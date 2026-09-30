import copy
import itertools
import unittest
from exp005_geometric_return_audit import geometric_candidates, resolve_query, folded_geometric_control
from exp005_primitive_return_audit import folded_record
from primitive_tie_guard_v1 import resolve_candidates


class GeometricReturnTests(unittest.TestCase):
    def test_three_folded_geometric_steps_continue_without_object_veto(self):
        rows = folded_geometric_control()
        self.assertEqual([r['arbitration']['rule']['selected_primitive']//2 for r in rows], [0, 1, 0])
        self.assertEqual(len({r['arbitration']['geometry_sha256'] for r in rows}), 1)

    def test_every_triangle_query_order_stable_on_folded_geometry(self):
        record = folded_record(); expected = resolve_query(record)
        for order in itertools.permutations(range(4)):
            result = resolve_query(record, triangle_order=order)
            self.assertEqual(result['rule'], expected['rule'])
            self.assertEqual(result['geometry_sha256'], expected['geometry_sha256'])
            self.assertEqual(result['triangle_tests'], 4)

    def test_ray_change_preserves_geometry_fingerprint_but_vertex_change_invalidates_state(self):
        record = folded_record(); initial = resolve_query(record)
        state = {'snapshot_sha256': initial['geometry_sha256'],
                 'primitive_id': initial['rule']['selected_primitive'], 'departure_event': 'mirror'}
        changed = copy.deepcopy(record); changed['origin_BU'][2] += 1e-3
        self.assertEqual(geometric_candidates(changed)['geometry_sha256'], state['snapshot_sha256'])
        vertex = list(changed['vertices'][0]); vertex[0] += 1e-3
        changed['vertices'][0] = vertex
        geometry = geometric_candidates(changed)
        with self.assertRaisesRegex(ValueError, 'another snapshot'):
            resolve_candidates(snapshot_sha256=geometry['geometry_sha256'],
                manifest=geometry['manifest'], candidates=geometry['candidates'], previous=state)

    def test_no_partial_or_duplicate_triangle_query_allowed(self):
        for order in ((0, 1), (0, 1, 2, 2), (0, 1, 2, True), (0, 1, 2, 4)):
            with self.assertRaises(ValueError): geometric_candidates(folded_record(), triangle_order=order)

    def test_mesh_and_ray_corruption_fail_closed(self):
        for target, key, value in (('face', None, [0, 0, 2]), ('ray', 'direction', [2., 0., 0.]),
                                  ('vertex', None, [float('nan'), 0., 0.])):
            record = folded_record()
            if target == 'face': record['faces'][0] = value
            elif target == 'vertex': record['vertices'][0] = value
            else: record[key] = value
            with self.assertRaises(ValueError): geometric_candidates(record)

    def test_candidates_do_not_mutate_input(self):
        record = folded_record(); before = copy.deepcopy(record)
        geometric_candidates(record)
        self.assertEqual(record, before)


if __name__ == '__main__': unittest.main()
