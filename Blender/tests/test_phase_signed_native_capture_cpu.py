"""CPU persistence adapters ONLY: no Blender/GPU admission or runtime evidence."""
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
import phase_signed_native_capture_v1 as capture


class CaptureTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT/'Blender/tests')
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)/'capture'
        self.plan = capture.manifest()

    def run_capture(self, dispatch, check=lambda: None):
        with patch.object(capture, 'dispatch_signed_probe', dispatch):
            return capture.run_private_capture(None, self.plan, self.folder, check,
                                               admit=lambda: None)

    def report(self):
        return json.loads((self.folder/'result.json').read_text())

    def test_exact_manifest_cases(self):
        samples, statuses = capture.validate_manifest(self.plan)
        self.assertEqual(len(samples), 12)
        self.assertEqual(statuses, [0]*8+[2, 1, 1, 1])
        self.assertLess(samples[0][0], 0)
        json.dumps(self.plan, allow_nan=False)

    def test_tampered_manifest_rejected_before_evidence(self):
        for kind in ('case', 'policy', 'pin'):
            p = copy.deepcopy(self.plan)
            if kind == 'case': p['cases'][0]['expected_status'] = True
            elif kind == 'policy': p['policy']['ram_free_after_budget_min_GiB'] = 3
            else: p['code_sha256'][str(capture.PREP)] = '0'*64
            with self.assertRaises(ValueError):
                capture.run_private_capture(None, p, self.folder, lambda: None)
            self.assertFalse(self.folder.exists())

    def test_default_admission_rejects_and_retains_failure(self):
        with patch.object(capture, 'dispatch_signed_probe') as dispatch:
            with self.assertRaises(ValueError):
                capture.run_private_capture(None, self.plan, self.folder, lambda: None)
            dispatch.assert_not_called()
        self.assertEqual(self.report()['status'], 'failed')
        self.assertFalse(self.report()['readback_retained'])

    def test_raw_retained_before_decoder_failure(self):
        def dispatch(gpu, samples, statuses, check, retain):
            retain([17, 29]); raise ValueError('synthetic decoder failure')
        with self.assertRaises(ValueError): self.run_capture(dispatch)
        r = self.report()
        self.assertTrue(r['readback_retained'])
        self.assertEqual(r['raw_sha256'], capture.sha(self.folder/'raw_uint32.json'))
        self.assertEqual(r['error_type'], 'ValueError')

    def test_raw_retained_before_post_readback_deadline(self):
        state = {'expired': False}
        def check():
            if state['expired']: raise ValueError('synthetic exhausted deadline')
        def dispatch(gpu, samples, statuses, check, retain):
            retain([31]); state['expired'] = True; check()
        with self.assertRaises(ValueError): self.run_capture(dispatch, check)
        self.assertTrue(self.report()['readback_retained'])
        self.assertEqual(self.report()['status'], 'failed')

    def test_success_remains_unauthenticated_and_no_overwrite(self):
        def dispatch(gpu, samples, statuses, check, retain):
            retain([37]); return {'adapter': 'CPU persistence test, NOT numerical gate'}
        r = self.run_capture(dispatch)
        self.assertEqual(r['status'], 'scalar_gates_passed_pending_outer_authentication')
        for k in ('native_promotion_allowed', 'runtime_execution_authenticated',
                  'operational_gate_passed', 'geometry_or_scene_inference'):
            self.assertFalse(r[k])
        before = capture.sha(self.folder/'result.json')
        with self.assertRaises(FileExistsError): self.run_capture(dispatch)
        self.assertEqual(before, capture.sha(self.folder/'result.json'))

    def test_fresh_deadline_independent_monotonic_cutoff(self):
        now = datetime(2026, 9, 30, tzinfo=timezone.utc)
        tick = [0.0]
        check = capture.fresh_deadline(now+timedelta(seconds=90), now=lambda: now,
                                       monotonic=lambda: tick[0])
        check(); tick[0] = 90
        with self.assertRaises(ValueError): check()
        with self.assertRaises(ValueError):
            capture.fresh_deadline(now+timedelta(seconds=91), now=lambda: now)


if __name__ == '__main__': unittest.main()
