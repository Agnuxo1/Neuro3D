import unittest
from exp005_cutoff_audit import fixture, compare, audit
from exp005_geometric_return_audit import geometric_candidates
from primitive_tie_guard_v1 import resolve_candidates


class CutoffTests(unittest.TestCase):
    def test_subthreshold_and_inclusive_boundary_skip_near_surface(self):
        for gap in (5e-10, 1e-9):
            result = compare(gap)
            self.assertEqual(result['selected_object'], 'far')
            self.assertEqual(result['arbitration']['minimum_distance_BU'], 1.)
            self.assertFalse(result['matches_analytic_reference'])
            self.assertEqual(result['arbitration']['action'], 'continue')

    def test_above_cutoff_controls_select_actual_nearest(self):
        for gap in (2e-9, 1e-8):
            result = compare(gap)
            self.assertEqual(result['selected_object'], 'near')
            self.assertTrue(result['matches_analytic_reference'])

    def test_order_cannot_restore_filtered_hits(self):
        record = fixture(5e-10)
        # All six primitives tested; six cyclic query orders (not 720 permutations).
        for shift in range(6):
            order = list(range(shift, 6))+list(range(shift))
            result = geometric_candidates(record, triangle_order=order)
            self.assertEqual({c['primitive_id'] for c in result['candidates']}, {4, 5})
            state = {'snapshot_sha256': result['geometry_sha256'],
                     'primitive_id': 0, 'departure_event': 't'}
            rule = resolve_candidates(snapshot_sha256=result['geometry_sha256'],
                manifest=result['manifest'], candidates=result['candidates'], previous=state)
            self.assertEqual(rule['selected_primitive'], 4)
            self.assertEqual(rule['action'], 'continue')

    def test_retained_audit_keeps_failures_separate_from_controls(self):
        result = audit()
        self.assertEqual(result['wrong_nearest_count'], 2)
        self.assertEqual(result['positive_control_count'], 2)

    def test_invalid_gap_fails_closed(self):
        for gap in (0., -1., 1., True, float('nan'), float('inf')):
            with self.assertRaises(ValueError): fixture(gap)


if __name__ == '__main__': unittest.main()
