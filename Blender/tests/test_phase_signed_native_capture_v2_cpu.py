"""CPU-only crash/persistence adapters, not shader or numerical GPU testing."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'Blender/benchmarks/capacity_audit'))
import phase_signed_native_capture_v2 as C


class CaptureV2Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT/'Blender/tests')
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)/'v2'
        self.plan = C.manifest()

    def run_capture(self, dispatch):
        with patch.object(C, 'dispatch_signed_probe', dispatch):
            return C.run_private_capture(None, self.plan, self.folder, lambda: None,
                                         admit=lambda: None)

    @staticmethod
    def success(gpu, samples, statuses, check, retain):
        retain([17, 29]); return {'adapter': 'CPU persistence test only'}

    def test_hard_exit_reproduces_V1_empty_record_and_V2_incomplete(self):
        observations = []
        for version in (1, 2):
            folder = Path(self.tmp.name)/('crash'+str(version))
            code = '''import os,sys
from unittest.mock import patch
sys.path.insert(0, sys.argv[1])
import importlib
C=importlib.import_module('phase_signed_native_capture_v'+sys.argv[3])
def dispatch(gpu,samples,statuses,check,retain):
 retain([17,29]); os._exit(23)
with patch.object(C,'dispatch_signed_probe',dispatch):
 C.run_private_capture(None,C.manifest(),sys.argv[2],lambda:None,admit=lambda:None)
'''
            r = subprocess.run([sys.executable, '-B', '-c', code,
                 str(ROOT/'Blender/benchmarks/capacity_audit'), str(folder), str(version)],
                 capture_output=True, text=True, timeout=20)
            self.assertEqual(r.returncode, 23, r.stderr)
            size = (folder/'result.json').stat().st_size
            raw_sha = hashlib.sha256((folder/'raw_uint32.json').read_bytes()).hexdigest()
            if version == 1: self.assertEqual(size, 0)
            else:
                self.assertGreater(size, 0)
                self.assertFalse((folder/'final.json').exists())
                inspected = C.inspect_capture(folder)
                self.assertEqual(inspected['status'], 'incomplete')
                self.assertTrue(inspected['raw_receipt_verified'])
                self.assertFalse(inspected['completion_content_verified'])
            observations.append({'version': version, 'child_rc': r.returncode,
                                 'initial_bytes': size, 'raw_sha256': raw_sha})
        print('hard_exit_observations='+json.dumps(observations))

    def test_nonfinite_decoded_payload_fails_with_nonempty_terminal(self):
        def dispatch(gpu, samples, statuses, check, retain):
            retain([31]); return {'unexpected': float('nan')}
        with self.assertRaises(ValueError): self.run_capture(dispatch)
        final = json.loads((self.folder/'final.json').read_text())
        self.assertEqual(final['status'], 'failed')
        self.assertNotIn('decoded', final)
        self.assertTrue(final['readback_retained'])
        self.assertEqual(C.inspect_capture(self.folder)['status'], 'failed')

    def test_decoder_exception_retains_verified_raw(self):
        def dispatch(gpu, samples, statuses, check, retain):
            retain([37]); raise ValueError('synthetic decoder exception')
        with self.assertRaises(ValueError): self.run_capture(dispatch)
        check = C.inspect_capture(self.folder)
        self.assertTrue(check['raw_receipt_verified'])
        self.assertEqual(check['status'], 'failed')

    def test_default_admission_rejects_before_dispatch(self):
        with patch.object(C, 'dispatch_signed_probe') as dispatch:
            with self.assertRaises(ValueError):
                C.run_private_capture(None, self.plan, self.folder, lambda: None)
            dispatch.assert_not_called()
        self.assertEqual(C.inspect_capture(self.folder)['status'], 'failed')

    def test_success_pending_auth_and_no_overwrite(self):
        self.run_capture(self.success)
        result = C.inspect_capture(self.folder)
        self.assertEqual(result['status'], 'scalar_pending_authentication')
        for flag in ('operational_gate_passed', 'runtime_execution_authenticated',
                     'native_promotion_allowed'): self.assertFalse(result[flag])
        before = C.sha(self.folder/'final.json')
        with self.assertRaises(FileExistsError): self.run_capture(self.success)
        self.assertEqual(before, C.sha(self.folder/'final.json'))

    def test_missing_readback_never_completes(self):
        with self.assertRaises(ValueError):
            self.run_capture(lambda *args: {'adapter': 'invalid missing retention'})
        self.assertEqual(C.inspect_capture(self.folder)['status'], 'failed')

    def test_raw_tamper_fails_receipt_check(self):
        self.run_capture(self.success)
        # Test-only mutation of OWN temporary evidence, never historic fixtures.
        (self.folder/'raw_uint32.json').write_text('[999]\n')
        with self.assertRaises(ValueError): C.inspect_capture(self.folder)


if __name__ == '__main__': unittest.main()
