import unittest
from fractions import Fraction as F
from exp005_phase_reduction_cpu_audit import case,phase_proxy,FIELD_TOL


class PhaseReductionCPU(unittest.TestCase):
    def test_small_integer_and_quarter_controls(self):
        for reference in (2.,2.03125):
            row=case('control',.125,reference)
            self.assertLess(row['phase_first_CPU_unit_field_error'],FIELD_TOL)
            self.assertLess(row['cycles_first_CPU_unit_field_error'],FIELD_TOL)

    def test_exact_lambda_and_reference_transport_still_have_phase_first_error(self):
        for exponent in (20,30):
            row=case('large',2**-exponent,999999.875+2**-(exponent+2))
            self.assertTrue(row['lambda_transport_exact'])
            self.assertEqual(row['non_wavelength_raw_transport_changes'],{'geometry':0,'sources':0,'optics':0})
            self.assertEqual(F(*row['exact_reduced_turns']),F(1,4))
            self.assertGreater(row['phase_first_CPU_unit_field_error'],FIELD_TOL)
            self.assertLess(row['cycles_first_CPU_unit_field_error'],FIELD_TOL)
            self.assertEqual(row['generated_records'],13)

    def test_quotient_first_is_not_a_general_fix_even_vs_exact_decoded_lambda(self):
        row=case('counterexample',1.00416693877201e-12,999999.875+2**-22)
        self.assertTrue(row['reference_uses_decoded_lambda_not_original'])
        self.assertGreater(row['cycles_first_CPU_unit_field_error'],FIELD_TOL)

    def test_half_turn_boundary_is_retained_as_negative_half(self):
        row=phase_proxy(.0625,.125)
        self.assertEqual(F(*row['exact_reduced_turns']),F(-1,2))
        self.assertLess(row['cycles_first_CPU_unit_field_error'],FIELD_TOL)


if __name__=='__main__':unittest.main()
