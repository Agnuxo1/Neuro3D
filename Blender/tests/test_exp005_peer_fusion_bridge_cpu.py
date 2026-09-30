"""New bridge adversary, not a repeat of peer scene sweeps or GPU evidence."""
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'Blender/benchmarks/capacity_audit'))
from exp005_peer_fusion_bridge_cpu import audit


class FusionBridgeCPU(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.result = audit()

    def case(self, name): return next(c for c in self.result['cases'] if c['label'] == name)

    def test_independent_unfused_and_scaled_controls(self):
        for case in self.result['cases']:
            self.assertEqual(len(case['records']), 13)
            self.assertEqual(len(case['independent_reference']['ledger']), 4)
            for name in ('unfused', 'CPU_auto', 'torch_CPU_scaled_diagnostic'):
                self.assertLess(case['backends'][name]['field_error_vs_independent_CPU'], 1e-8,
                                msg=case['label']+'/'+name)

    def test_new_dyadic_alias_accepted_with_bad_field(self):
        case = self.case('subquant_dyadic')
        for name in ('CPU_default', 'torch_CPU_default'):
            self.assertFalse(case['backends'][name]['field_gate_1e4_passed'])
            self.assertLess(case['backends'][name]['states'], case['backends']['unfused']['states'])

    def test_exact_control_sham_and_longer_lambda(self):
        for name in ('exact_control', 'above_quant_sham', 'same_shift_long_lambda', 'same_shift_larger_lambda'):
            case = self.case(name)
            self.assertTrue(case['backends']['torch_CPU_default']['field_gate_1e4_passed'])
        case = self.case('above_quant_sham')
        self.assertEqual(case['backends']['torch_CPU_default']['states'], case['backends']['unfused']['states'])

    def test_CPU_only_not_native_promotion(self):
        self.assertEqual(self.result['threads'], 1)
        for key in ('CUDA_initialized', 'GPU_executed', 'Bpy_executed', 'native_promotion_allowed'):
            self.assertFalse(self.result[key])


def run():
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(FusionBridgeCPU))
    data = FusionBridgeCPU.result
    data['tests'] = result.testsRun; data['test_output'] = stream.getvalue()
    data['tests_successful'] = result.wasSuccessful()
    data['test_failures'] = len(result.failures); data['test_errors'] = len(result.errors)
    data['code_sha256'][str(Path(__file__))] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    data['finalized_utc'] = datetime.now(timezone.utc).isoformat()
    return data


if __name__ == '__main__':
    result = run()
    print(json.dumps(result, indent=2, allow_nan=False))
    sys.exit(0 if result['tests_successful'] else 1)
