"""Artificial envelopes + CPU-generated raw words; no GPU or subprocess launch."""
from datetime import datetime, timedelta, timezone
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'Blender/benchmarks/capacity_audit'))
sys.path.insert(0, str(ROOT/'Blender/tests'))
import scalar_job_bundle_v1 as B
import phase_signed_native_capture_v2 as C
import scalar_job_supervisor_v1 as S
from phase_signed_native_probe_v1 import decode
from test_phase_signed_native_probe_cpu import synthetic  # Pure helper; no old suite executed.


class BundleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT/'Blender/tests')
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name)
        now = datetime.now(timezone.utc)
        self.recipe = B.recipe(['CPU-synthetic-not-executed', '--fixture'], base/'capture',
                               base/'supervisor', deadline=now+timedelta(seconds=90),
                               now=now, queue_name='CPU-bundle', timeout=60)
        self.cdir, self.sdir = base/'capture', base/'supervisor'

    def build(self):
        def dispatch(gpu, pairs, statuses, check, retain):
            output = synthetic(); retain(output)
            return decode(pairs, output, expected_statuses=statuses)
        with patch.object(C, 'dispatch_signed_probe', dispatch):
            C.run_private_capture(None, self.recipe['contract']['capture_manifest'],
                                  self.cdir, lambda: None, admit=lambda: None)
        self.sdir.mkdir()
        base = {k: self.recipe[k] for k in ('command_sha256', 'deadline_utc', 'timeout_s')}
        base.update(runtime_execution_authenticated=False, native_promotion_allowed=False)
        S.write_once(self.sdir/'initial.json', dict(base, status='in_progress'))
        self.final = dict(base, status='completed', exit_code=0, cleanup_completed=True,
            reasons=[], elapsed_s=.1, injected_test_adapters=True,
            reservation={'name': 'CPU-bundle'}, samples=[{'ram_available_bytes': 7*S.GIB,
            'device_used_bytes': S.GIB, 'temperature_c': 40}])
        S.write_once(self.sdir/'final.json', self.final)

    @staticmethod
    def overwrite_test_fixture(path, data):
        # Mutations affect only OWN disposable synthetic fixtures.
        path.write_text(json.dumps(data, allow_nan=False), encoding='utf-8')

    def test_exact_recipe_and_raw_redecode_never_GPU_authenticate(self):
        self.build(); r = B.inspect_bundle(self.recipe)
        self.assertEqual((r['valid_cases'], r['abort_cases']), (8, 4))
        self.assertTrue(r['scalar_redecode_verified'])
        for key in ('runtime_execution_authenticated', 'native_promotion_allowed',
                    'operational_gate_passed', 'geometry_or_scene_inference'):
            self.assertFalse(r[key])

    def test_command_or_deadline_lineage_mismatch_rejects(self):
        self.build()
        for key, value in [('command_sha256', '0'*64), ('deadline_utc', '2026-09-30T06:00:00+00:00')]:
            f = dict(self.final); f[key] = value
            self.overwrite_test_fixture(self.sdir/'final.json', f)
            with self.assertRaises(ValueError): B.inspect_bundle(self.recipe)

    def test_late_cleanup_or_failed_child_never_passes(self):
        self.build()
        for change in ({'elapsed_s': 60}, {'cleanup_completed': False}, {'exit_code': 15}):
            self.overwrite_test_fixture(self.sdir/'final.json', dict(self.final, **change))
            with self.assertRaises(ValueError): B.inspect_bundle(self.recipe)

    def test_altered_decoded_data_rejects_even_if_raw_receipt_matches(self):
        self.build(); f = json.loads((self.cdir/'final.json').read_text())
        f['decoded']['cases'][0]['signed_trace']['phase_sign'] = 1
        self.overwrite_test_fixture(self.cdir/'final.json', f)
        with self.assertRaises(ValueError): B.inspect_bundle(self.recipe)

    def test_bad_raw_identity_with_recomputed_hashes_still_rejects(self):
        self.build(); raw = json.loads((self.cdir/'raw_uint32.json').read_text())
        raw[25] = 99
        self.overwrite_test_fixture(self.cdir/'raw_uint32.json', raw)
        receipt = json.loads((self.cdir/'raw_receipt.json').read_text())
        receipt['raw_sha256'] = C.sha(self.cdir/'raw_uint32.json')
        self.overwrite_test_fixture(self.cdir/'raw_receipt.json', receipt)
        f = json.loads((self.cdir/'final.json').read_text())
        f.update(raw_sha256=receipt['raw_sha256'], receipt_sha256=C.sha(self.cdir/'raw_receipt.json'))
        self.overwrite_test_fixture(self.cdir/'final.json', f)
        with self.assertRaises(ValueError): B.inspect_bundle(self.recipe)

    def test_missing_terminal_does_not_complete(self):
        self.build()
        alternate = self.sdir.with_name('unfinished'); alternate.mkdir()
        S.write_once(alternate/'initial.json', {'status': 'in_progress'})
        value = copy.deepcopy(self.recipe); value['supervisor_path'] = str(alternate)
        with self.assertRaises(FileNotFoundError): B.inspect_bundle(value)

    def test_outside_or_nested_evidence_paths_reject(self):
        with self.assertRaises(ValueError): B.paths(ROOT.parent/'elsewhere', self.sdir)
        with self.assertRaises(ValueError): B.paths(self.cdir, self.cdir/'nested')

    def test_recipe_manifest_or_unknown_key_tamper_rejects(self):
        for key in ('manifest', 'extra'):
            value = copy.deepcopy(self.recipe)
            if key == 'manifest': value['contract']['capture_manifest']['cases'][0]['expected_status'] = True
            else: value['force_native_promotion'] = True
            with self.assertRaises(ValueError): B.validate_recipe(value)


if __name__ == '__main__': unittest.main()
