"""Synthetic resources/reservations + real OWN lightweight CPU children only."""
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'Blender/benchmarks/capacity_audit'))
import psutil
import scalar_job_supervisor_v1 as S


class SupervisorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT/'Blender/tests')
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)/'job'
        self.safe = {'ram_available_bytes': 7*S.GIB, 'device_used_bytes': S.GIB,
                     'temperature_c': 40}

    def run_job(self, code='print(17)', **kw):
        return S.run_owned([sys.executable, '-B', '-c', code], self.folder,
            deadline=datetime.now(timezone.utc)+timedelta(seconds=30), queue_name='CPU-test',
            timeout=kw.pop('timeout', 3), sample=kw.pop('sample', lambda: self.safe),
            reservation=kw.pop('reservation', lambda name: {'synthetic': True}), **kw)

    def test_new_deadline_invalid_or_historical_rejected(self):
        now = datetime.now(timezone.utc)
        for deadline, timeout in [(now, 3), (now+timedelta(seconds=91), 3),
                                  (now+timedelta(seconds=90), True),
                                  (now.replace(tzinfo=None), 3)]:
            with self.assertRaises(ValueError): S.validate_policy(deadline, timeout, now)

    def test_projection_floors_and_invalid_telemetry(self):
        self.assertEqual(S.resource_reasons(self.safe, before_launch=True), [])
        for key, val, reason in [('ram_available_bytes', 5*S.GIB, 'ram_floor'),
                                ('device_used_bytes', 18*S.GIB, 'vram_cap'),
                                ('temperature_c', 81, 'temperature_cap')]:
            sample = dict(self.safe); sample[key] = val
            self.assertIn(reason, S.resource_reasons(sample, before_launch=True))
        for sample in ({}, dict(self.safe, temperature_c=float('nan')),
                       dict(self.safe, ram_available_bytes=True)):
            with self.assertRaises(ValueError): S.resource_reasons(sample, before_launch=True)

    def test_holder_identity_never_accepts_different_child(self):
        d = {'name': 'own', 'pid': 7, 'ctime': 10., 'child_pid': 8, 'child_ctime': 11.}
        S.verify_holder_record(d, 'own', 8, 11., 10.)
        for changed in (dict(d, name='peer'), dict(d, child_pid=9),
                        dict(d, child_ctime=12.), dict(d, pid=True)):
            with self.assertRaises(ValueError): S.verify_holder_record(changed, 'own', 8, 11., 10.)

    def test_bad_reservation_never_starts_child(self):
        def bad(name): raise ValueError('synthetic other holder')
        r = self.run_job(reservation=bad)
        self.assertNotIn('child_pid', r)
        self.assertEqual(r['status'], 'rejected_or_stopped')

    def test_low_ram_never_starts_child(self):
        r = self.run_job(sample=lambda: dict(self.safe, ram_available_bytes=5*S.GIB))
        self.assertNotIn('child_pid', r)
        self.assertEqual(r['reasons'], ['ram_floor'])

    def test_real_own_cpu_exit_logged_not_GPU_authenticated(self):
        r = self.run_job()
        self.assertEqual(r['status'], 'completed')
        self.assertEqual(r['exit_code'], 0)
        self.assertTrue(r['cleanup_completed'])
        self.assertTrue(r['injected_test_adapters'])
        self.assertFalse(r['runtime_execution_authenticated'])
        self.assertFalse(psutil.pid_exists(r['child_pid']))
        self.assertEqual(json.loads((self.folder/'final.json').read_text()), r)

    def test_own_sleeping_child_stopped_on_monotonic_timeout(self):
        r = self.run_job('import time;time.sleep(20)', timeout=.3)
        self.assertEqual(r['status'], 'stopped')
        self.assertIn('child_timeout', r['reasons'])
        self.assertTrue(r['cleanup_completed'])
        self.assertFalse(psutil.pid_exists(r['child_pid']))
        print('timeout_observation='+json.dumps({k: r[k] for k in
              ('status', 'reasons', 'exit_code', 'elapsed_s', 'cleanup_completed')}))

    def test_telemetry_failure_after_launch_stops_own_child(self):
        calls = [0]
        def sample():
            calls[0] += 1
            if calls[0] > 1: raise OSError('synthetic telemetry loss')
            return self.safe
        r = self.run_job('import time;time.sleep(20)', sample=sample)
        self.assertEqual(r['status'], 'rejected_or_stopped')
        self.assertTrue(r['cleanup_completed'])
        self.assertFalse(psutil.pid_exists(r['child_pid']))

    def test_nonfinite_telemetry_retains_serializable_failed_envelope(self):
        calls = [0]
        def sample():
            calls[0] += 1
            return self.safe if calls[0] == 1 else dict(self.safe, temperature_c=float('nan'))
        r = self.run_job('import time;time.sleep(20)', sample=sample)
        self.assertEqual(r['status'], 'rejected_or_stopped')
        self.assertTrue(r['cleanup_completed'])
        self.assertEqual(json.loads((self.folder/'final.json').read_text()), r)
        self.assertFalse(psutil.pid_exists(r['child_pid']))


if __name__ == '__main__': unittest.main()
