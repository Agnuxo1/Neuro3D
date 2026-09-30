import copy
from fractions import Fraction
import unittest
from exp005_near_origin_audit import signed_hits, near_origin_interval, diagnose, audit
from exp005_cutoff_audit import fixture


class NearOriginTests(unittest.TestCase):
    def test_exact_plane_reference_keeps_all_signed_hits(self):
        hits = signed_hits(fixture(5e-10))
        self.assertEqual(dict(hits), {0: Fraction(0), 1: Fraction(0),
            2: Fraction(5e-10), 3: Fraction(5e-10), 4: Fraction(1), 5: Fraction(1)})

    def test_subcutoff_rejects_without_changing_original_threshold(self):
        r = audit()
        self.assertEqual([x['diagnostic']['action'] for x in r['cases']],
            ['abort', 'abort', 'continue_close_gate_only', 'continue_close_gate_only'])

    def test_represented_input_folded_returns_not_globally_excluded(self):
        r = audit()
        self.assertEqual(len(r['folded_controls']), 3)
        self.assertTrue(all(x['diagnostic']['action'] == 'continue_close_gate_only'
                            for x in r['folded_controls']))

    def test_zero_negative_and_interval_boundaries(self):
        self.assertEqual(near_origin_interval(Fraction(0), distance_error_BU=0.)['action'],
                         'continue_close_gate_only')
        self.assertEqual(near_origin_interval(Fraction(-1), distance_error_BU=0.)['action'],
                         'continue_close_gate_only')
        self.assertEqual(near_origin_interval(Fraction(2e-9), distance_error_BU=1.1e-9)['action'], 'abort')
        self.assertEqual(near_origin_interval(Fraction(-1e-10), distance_error_BU=2e-10)['action'], 'abort')
        self.assertEqual(near_origin_interval(Fraction(0), distance_error_BU=1e-12)['action'], 'abort')

    def test_uncertainty_is_mandatory_and_not_silently_zeroed(self):
        with self.assertRaises(TypeError): diagnose(fixture(2e-9))
        for error in (-1., True, float('nan'), float('inf')):
            with self.assertRaises(ValueError): diagnose(fixture(2e-9), distance_error_BU=error)

    def test_parallel_miss_and_coplanar_ray_are_distinct(self):
        r = fixture(2e-9); r['direction'] = [0., 1., 0.]; r['origin_BU'] = [-1., 0., 0.]
        self.assertEqual(signed_hits(r), [])
        r['origin_BU'] = [0., 0., 0.]
        with self.assertRaisesRegex(ValueError, 'coplanar'): signed_hits(r)

    def test_invalid_degenerate_and_bounds_fail_closed(self):
        for change in ('degenerate', 'bounds', 'face', 'direction'):
            r = fixture(2e-9)
            if change == 'degenerate': r['vertices'][1] = list(r['vertices'][0])
            elif change == 'bounds': r['vertices'][0][0] = 1e6+1
            elif change == 'face': r['faces'][0] = [True, 1, 2]
            else: r['direction'] = [0., 0., 0.]
            with self.assertRaises(ValueError): signed_hits(r)

    def test_record_not_mutated(self):
        r = fixture(2e-9); before = copy.deepcopy(r)
        diagnose(r, distance_error_BU=0.)
        self.assertEqual(r, before)


if __name__ == '__main__': unittest.main()
