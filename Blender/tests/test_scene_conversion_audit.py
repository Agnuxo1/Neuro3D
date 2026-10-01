"""Focused regressions for exact scene-linked conversion loss, CPU only."""
from fractions import Fraction as F
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).parent))
from exp005_scene_conversion_audit import audit_conversion


class ConversionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evidence = audit_conversion()  # Each of the three scenes generated once.
        cls.cases = {c['name']:c for c in cls.evidence['cases']}

    def test_ordinary_control_passes_absolute_gates(self):
        case = self.cases['ordinary']
        self.assertTrue(case['field_gate_satisfied'])
        self.assertTrue(case['intensity_gate_satisfied'])
        self.assertGreater(F(*case['exact_field_error_L1_rational']),0)
        self.assertEqual(case['producer']['generated_record_count'],2)
        self.assertEqual(len(case['producer']['rows']),1)

    def test_high_amplitude_loss_is_before_reduction_not_only_bound_rejection(self):
        case = self.cases['high_amplitude_CPU_only']
        self.assertFalse(case['field_gate_satisfied'])
        self.assertFalse(case['intensity_gate_satisfied'])
        self.assertGreater(F(*case['exact_field_error_L1_rational']),F(1,10000))
        self.assertGreater(F(*case['exact_intensity_error_rational']),F(1,5000))
        reduction = case['producer']['composition']['represented_reduction']['ports']['D']['groups']['g']
        self.assertEqual(reduction['field_error_L1_rational'],[0,1])
        self.assertEqual(reduction['intensity_error_rational'],[0,1])
        self.assertFalse(case['producer']['accepted_ideal_scene_CPU_only'])
        self.assertFalse(case['producer']['GPU_executed'])

    def test_dark_port_absolute_pass_does_not_establish_relative_accuracy(self):
        case = self.cases['near_dark_absolute_not_relative']
        self.assertEqual(case['ideal_field_rational'],[[1,2**30],[0,1]])
        self.assertEqual(case['modeled_field_rational'],[[0,1],[0,1]])
        self.assertEqual(case['relative_field_error_rational'],[1,1])
        self.assertTrue(case['field_gate_satisfied'])
        self.assertTrue(case['intensity_gate_satisfied'])
        self.assertEqual(case['producer']['generated_record_count'],4)
        self.assertEqual(len(case['producer']['rows']),2)


if __name__ == '__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(ConversionTests)
    result=unittest.TextTestRunner().run(suite)
    if hasattr(ConversionTests,'evidence'):
        print(json.dumps(ConversionTests.evidence,sort_keys=True,allow_nan=False))
    sys.exit(0 if result.wasSuccessful() else 1)
