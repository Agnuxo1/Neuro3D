import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1]/'benchmarks'/'capacity_audit'))
from wavelength_transport_v1 import checked_wavelength
from exp005_wavelength_transport_audit import audit


class WavelengthTransportTests(unittest.TestCase):
    def test_cpu_audit_retains_collapses_and_overflow(self):
        rows = {r['lambda_BU']: r for r in audit()['rows']}
        self.assertTrue(all(r['raw_preflight_accepted'] for r in rows.values()))
        for value in (1e-46, 1e-300):
            self.assertTrue(rows[value]['collapsed'])
            self.assertTrue(rows[value]['candidate_rejected'])
        self.assertEqual(rows[1e39]['legacy_split_error'], 'OverflowError')
        self.assertTrue(rows[1e39]['candidate_rejected'])
        self.assertGreater(rows[1e-40]['relative_error'], 1e-12)
        self.assertTrue(rows[1e-40]['candidate_rejected'])

    def test_exact_wavelength_and_zero_budget(self):
        result = checked_wavelength(.125, relative_budget=0.)
        self.assertEqual(result['decoded_BU'], .125)
        self.assertEqual(result['relative_error'], 0.)

    def test_normal_controls_remain_positive(self):
        for value in (1e-6, 1e-30, 1e30):
            result = checked_wavelength(value, relative_budget=1e-12)
            self.assertGreater(result['decoded_BU'], 0.)
            self.assertLessEqual(result['relative_error'], 1e-12)

    def test_invalid_input_fail_closed(self):
        for value in (0., -1., float('nan'), float('inf'), True):
            with self.assertRaises(ValueError):
                checked_wavelength(value, relative_budget=1e-12)

    def test_invalid_or_missing_budget_not_implicit(self):
        for budget in (-1., 1., float('nan'), float('inf'), True):
            with self.assertRaises(ValueError):
                checked_wavelength(.125, relative_budget=budget)
        with self.assertRaises(TypeError): checked_wavelength(.125)


if __name__ == '__main__': unittest.main()
