import unittest
from fractions import Fraction
from exp005_precision006_review_audit import audit


class Precision006ReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.report = audit()

    def test_eight_cases_match_peer_phase_display(self):
        self.assertEqual(len(self.report['rows']), 8)
        for row in self.report['rows']:
            self.assertLessEqual(row['peer_phase_display_delta'], 1e-15)

    def test_relative_gate_passes_all_but_length_budget_rejects_two(self):
        self.assertEqual(self.report['wavelength_budget_rejections'], 2)
        for row in self.report['rows']:
            self.assertLessEqual(row['transport']['relative_error'], 1e-12)
            expected_reject = abs(row['signed_phase_rad_display']) > 1e-4
            self.assertEqual(row['wavelength_only_budget']['accepted'], not expected_reject)

    def test_exact_controls_have_zero_cycle_delta_not_native_phase_claim(self):
        for row in self.report['rows']:
            if row['group'] == 'controls':
                self.assertEqual(Fraction(*row['delta_cycles_exact']), 0)
                self.assertEqual(row['unit_complex_delta_display'], 0)

    def test_two_unit_complex_errors_exceed_unchanged_field_budget(self):
        self.assertEqual(sum(r['unit_complex_delta_display'] > 1e-4 for r in self.report['rows']), 2)

    def test_half_ulp_label_is_factor_two_high(self):
        self.assertEqual(self.report['half_ulp_audit']['peer_to_actual_ratio'], 2.)
        self.assertEqual(self.report['half_ulp_audit']['actual_half_ulp_BU'], 2.**-34)


if __name__ == '__main__': unittest.main()
