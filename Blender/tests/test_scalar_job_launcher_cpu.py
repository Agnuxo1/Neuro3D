"""New launcher orchestration with MOCK ancestry/resources/supervisor only."""
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'Blender/benchmarks/capacity_audit'))
sys.path.insert(0, str(ROOT/'Blender/tests'))
import scalar_job_launcher_v1 as L
from test_phase_signed_native_probe_cpu import synthetic
from phase_signed_native_probe_v1 import decode


class LauncherTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT/'Blender/tests')
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name); self.exe = self.base/'blender.exe'
        self.exe.write_bytes(b'Not an executable; CPU fixture only')
        self.job = self.base/'job'
        self.owner = {'guard_pid': 111, 'guard_birth': 1000., 'queue_pid': 99, 'queue_birth': 900.}
        self.resource = {'ram_available_bytes': 7*L.S.GIB, 'device_used_bytes': L.S.GIB, 'temperature_c': 40}
        self.addCleanup(patch.stopall)
        self.own = patch.object(L, 'owner_snapshot', return_value=self.owner).start()
        self.tel = patch.object(L.S, 'telemetry', return_value=self.resource).start()
        self.supervisor = patch.object(L.S, 'run_owned', side_effect=self.fake_supervisor).start()
        self.bad_sidecar = False

    def run_job(self): return L.run(self.exe, self.job, 'CPU-launcher-mock')
    def final(self): return json.loads((self.job/'launcher_final.json').read_text())

    def fake_supervisor(self, command, path, *, deadline, queue_name, timeout):
        recipe = json.loads((self.job/'recipe.json').read_text())
        def dispatch(gpu, pairs, statuses, check, retain):
            raw = synthetic(); retain(raw)
            return decode(pairs, raw, expected_statuses=statuses)
        with patch.object(L.C, 'dispatch_signed_probe', dispatch):
            L.C.run_private_capture(None, recipe['contract']['capture_manifest'],
                                   recipe['capture_path'], lambda: None, admit=lambda: None)
        folder = Path(path); folder.mkdir()
        base = {k: recipe[k] for k in ('command_sha256', 'deadline_utc', 'timeout_s')}
        base.update(runtime_execution_authenticated=False, native_promotion_allowed=False)
        L.C.write_once(folder/'initial.json', dict(base, status='in_progress'))
        env = dict(base, status='completed', exit_code=0, cleanup_completed=True,
            reasons=[], elapsed_s=.1, injected_test_adapters=True,
            child_pid=222, reservation={'name':queue_name}, samples=[self.resource])
        L.C.write_once(folder/'final.json', env)
        L.C.write_once(Path(recipe['capture_path']+'.child.json'), {
            'child_pid':222, 'guard_pid':111, 'queue_pid':99,
            'recipe_sha256': '0'*64 if self.bad_sidecar else L.C.sha(self.job/'recipe.json'),
            'binding_sha256':L.C.sha(self.job/'binding.json'), 'entrypoint_sha256':L.C.sha(L.E.SELF),
            'runtime_execution_authenticated':False, 'native_promotion_allowed':False})
        return env

    def test_mock_complete_recipe_capture_envelope_join_never_authenticates_GPU(self):
        result = self.run_job()
        self.assertEqual(result['status'], 'content_verified_pending_runtime_authentication')
        self.assertEqual((result['content']['valid_cases'], result['content']['abort_cases']), (8,4))
        self.assertFalse(result['operational_gate_passed']); self.assertFalse(result['runtime_execution_authenticated'])
        recipe = json.loads((self.job/'recipe.json').read_text())
        self.assertEqual(recipe['timeout_s'],60)
        self.assertEqual(json.loads((self.job/'binding.json').read_text())['guard_pid'],111)
        remaining = (datetime.fromisoformat(recipe['deadline_utc'])-datetime.now(timezone.utc)).total_seconds()
        self.assertTrue(80 < remaining <= 90)

    def test_reservation_missing_never_creates_folder_or_calls_telemetry(self):
        self.own.side_effect = ValueError('synthetic missing reservation')
        with self.assertRaises(ValueError): self.run_job()
        self.assertFalse(self.job.exists()); self.tel.assert_not_called(); self.supervisor.assert_not_called()

    def test_ram_after_budget_rejects_without_recipe_or_child(self):
        self.resource['ram_available_bytes']=5*L.S.GIB
        result = self.run_job()
        self.assertEqual(result['reasons'],['ram_floor'])
        self.assertEqual(self.final()['status'],'resource_rejected')
        self.assertFalse((self.job/'recipe.json').exists()); self.supervisor.assert_not_called()

    def test_telemetry_failure_leaves_failed_terminal_without_child(self):
        self.tel.side_effect = OSError('synthetic telemetry failure')
        with self.assertRaises(OSError): self.run_job()
        self.assertEqual(self.final()['status'],'failed'); self.supervisor.assert_not_called()

    def test_failed_supervisor_rejects_even_with_process_exit_metadata(self):
        self.supervisor.side_effect = None
        self.supervisor.return_value = {'status':'child_failed','child_pid':222,'exit_code':17}
        with self.assertRaises(ValueError): self.run_job()
        self.assertEqual(self.final()['supervisor_status'],'child_failed')

    def test_child_sidecar_changed_rejects_after_retaining_raw_and_envelope(self):
        self.bad_sidecar = True
        with self.assertRaises(ValueError): self.run_job()
        self.assertEqual(self.final()['status'],'failed')
        self.assertTrue((self.job/'capture/raw_uint32.json').is_file())
        self.assertTrue((self.job/'supervisor/final.json').is_file())

    def test_existing_folder_and_relative_executable_reject_before_admission(self):
        self.job.mkdir()
        with self.assertRaises(ValueError): self.run_job()
        with self.assertRaises(ValueError): L.run('blender.exe',self.base/'other','CPU-mock')
        self.own.assert_not_called(); self.supervisor.assert_not_called()

    def test_executable_change_after_binding_rejects_before_supervisor(self):
        def owner(name):
            if self.own.call_count == 2: self.exe.write_bytes(b'changed own fixture')
            return self.owner
        self.own.side_effect = owner
        with self.assertRaises(ValueError): self.run_job()
        self.assertEqual(self.final()['status'],'failed'); self.supervisor.assert_not_called()


if __name__ == '__main__': unittest.main()
