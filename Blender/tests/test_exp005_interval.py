from fractions import Fraction
import random
import unittest
from exp005_interval_audit import Interval, parameters, exact_parameters, audit


class IntervalTests(unittest.TestCase):
    def test_operations_contain_exact_binary64_input_results(self):
        rng = random.Random(202609300912)
        for _ in range(32):
            a, b = rng.uniform(-1e4, 1e4), rng.uniform(.1, 10.)
            x, y = Interval.point(a), Interval.point(b)
            p, q = Fraction(a), Fraction(b)
            for interval, exact in ((x+y, p+q), (x-y, p-q), (x*y, p*q), (x/y, p/q)):
                self.assertTrue(interval.contains(exact))

    def test_full_parameters_enclosed_and_departure_uncertainty_not_hidden(self):
        r = audit()
        self.assertEqual(len(r['cases']), 50)
        self.assertEqual(r['departure_uncertainties'], 8)
        self.assertEqual(r['counts']['uncertain_determinant'], 2)

    def test_exact_zero_does_not_force_zero_interval(self):
        r = Interval.point(1.)-Interval.point(1.)
        self.assertLess(r.low, 0.)
        self.assertGreater(r.high, 0.)
        self.assertTrue(r.contains(Fraction(0)))

    def test_denominator_zero_and_invalid_inputs_fail_closed(self):
        for low, high in ((-1., 1.), (0., 1.), (-1., 0.), (0., 0.)):
            with self.assertRaises(ValueError): Interval.point(1.)/Interval(low, high)
        for low, high in ((2., 1.), (True, 1.), (0., float('inf')), (float('nan'), 1.)):
            with self.assertRaises(ValueError): Interval(low, high)
        with self.assertRaises(ValueError): Interval.point(1e308)*Interval.point(1e308)

    def test_outside_triangle_is_not_a_near_positive_hit(self):
        triangle = [[1., -1., -1.], [1., 1., -1.], [1., 1., 1.]]
        r = parameters([0., 10., 10.], [1., 0., 0.], triangle)
        self.assertEqual(r['status'], 'outside_in_CPU_model')

    def test_negative_t_is_not_silently_positive(self):
        triangle = [[-1., -1., -1.], [-1., 1., -1.], [-1., 1., 1.]]
        r = parameters([0., 0., 0.], [1., 0., 0.], triangle)
        self.assertEqual(r['status'], 'non_forward_in_CPU_model')
        self.assertTrue(Interval(*r['bounds']['t']).contains(Fraction(-1)))

    def test_reference_rejects_out_of_bounds(self):
        with self.assertRaises(ValueError):
            parameters([1e6+1, 0., 0.], [1., 0., 0.], [[0., 0., 0.]]*3)


if __name__ == '__main__': unittest.main()
