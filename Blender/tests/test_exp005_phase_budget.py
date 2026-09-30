import unittest
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1]/'benchmarks'/'capacity_audit'))
from phase_transport_budget_v1 import wavelength_phase_budget, PI_UPPER
from exp005_phase_budget_audit import audit


class PhaseBudgetTests(unittest.TestCase):
    def result(self, wavelength=.123456789, length=2., budget=1e-4):
        return wavelength_phase_budget(wavelength, max_effective_length_BU=length,
            phase_budget_rad=budget, relative_budget=1e-12)

    def test_exact_wavelength_has_zero_encoding_phase(self):
        result = self.result(.125, 1e6, 0.)
        self.assertTrue(result['accepted'])
        self.assertEqual(Decimal(result['wavelength_phase_upper_rad_decimal']), 0)
        self.assertIn('GPU phase reduction', result['excluded'])

    def test_bound_monotonic_in_declared_length(self):
        short, long = self.result(length=2.), self.result(length=1e6)
        a = Decimal(short['wavelength_phase_upper_rad_decimal'])
        b = Decimal(long['wavelength_phase_upper_rad_decimal'])
        self.assertGreater(a, 0)
        self.assertGreater(b, a)

    def test_reported_decimal_is_not_below_rational_upper_bound(self):
        result = self.result()
        decoded = result['wavelength_transport']['decoded_BU']
        original = Fraction(.123456789)
        exact_upper = 2*PI_UPPER*Fraction(2.)*abs(Fraction(decoded)-original)/(original*Fraction(decoded))
        self.assertGreaterEqual(Fraction(Decimal(result['wavelength_phase_upper_rad_decimal'])), exact_upper)

    def test_explicit_zero_phase_budget_rejects_nonexact_encoding(self):
        result = self.result(budget=0.)
        self.assertFalse(result['accepted'])

    def test_length_and_budget_are_required_and_finite(self):
        for value in (-1., True, float('nan'), float('inf')):
            with self.assertRaises(ValueError): self.result(length=value)
            with self.assertRaises(ValueError): self.result(budget=value)
        with self.assertRaises(TypeError): wavelength_phase_budget(.125)

    def test_encoding_collapse_not_hidden_by_zero_length(self):
        with self.assertRaisesRegex(ValueError, 'collapsed'):
            self.result(1e-46, 0.)

    def test_twelve_cases_and_transport_budget_are_retained(self):
        rows = audit()['rows']
        self.assertEqual(len(rows), 12)
        self.assertTrue(all(x['wavelength_transport']['relative_error'] <= 1e-12 for x in rows))
        self.assertTrue(all(x['scope'].endswith('unverified') for x in rows))

    def test_small_relative_error_does_not_pass_long_path_phase_budget(self):
        short = self.result(1.11111111111111e-6, 2.)
        long = self.result(1.11111111111111e-6, 1e6)
        self.assertLess(long['wavelength_transport']['relative_error'], 1e-12)
        self.assertTrue(short['accepted'])
        self.assertFalse(long['accepted'])
        self.assertGreater(Decimal(long['wavelength_phase_upper_rad_decimal']), Decimal('0.004'))


if __name__ == '__main__': unittest.main()
