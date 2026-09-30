import copy
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1]/'benchmarks'/'capacity_audit'))
from local_frame_v1 import local_frame
from exp005_precision_transport_audit import audit as world_audit, transform, transported
from exp005_local_frame_audit import audit as local_audit
from exp005_precision_fixture import direct, reflected
from exp005_triangle_oracle import trace_scene
from exp005_modal_coverage_audit import audit as modal_audit


class PrecisionTransportTests(unittest.TestCase):
    def test_modal_mutants_survive_old_gate_but_not_supplement(self):
        result = modal_audit()
        rows = {r['dot_tolerance']: r for r in result['rows']}
        for mutant in (4e-10, 1e-8):
            self.assertTrue(rows[mutant]['old_four_pass'])
            self.assertFalse(rows[mutant]['new_two_pass'])
        self.assertTrue(rows[1e-9]['old_four_pass'])
        self.assertTrue(rows[1e-9]['new_two_pass'])

    def test_modal_supplement_matches_independent_scene_oracle(self):
        result = modal_audit()
        self.assertEqual(len(result['oracle_controls']), 2)
        for row in result['oracle_controls']:
            self.assertEqual(row['v3_accept'], row['oracle_accept'])

    def test_world_transport_failures_are_visible_not_discarded(self):
        result = world_audit()
        self.assertEqual(len(result['rows']), 64)
        self.assertEqual(len(result['transport_failures']), 2)
        self.assertFalse(result['trace_rejections'])
        self.assertGreater(result['max_transport_field_error'], 1e-3)
        for row in result['transport_failures']:
            self.assertEqual(row['lambda_BU'], 1e-6)
            self.assertFalse(row['transport_pass'])
            self.assertEqual(row['original_casts'], row['transported_casts'])

    def test_local_frame_controls_both_transport_and_invariance(self):
        result = local_audit()
        self.assertEqual(len(result['rows']), 64)
        self.assertFalse(result['local_transport_failures'])
        self.assertFalse(result['world_vs_local_failures'])
        self.assertFalse(result['rejections'])
        self.assertLessEqual(result['max_local_transport_error'], 1e-12)
        self.assertLessEqual(result['max_frame_drift'], 1e-12)

    def test_conversion_does_not_mutate_scene_or_optics(self):
        world = transform(reflected(), 65536.987654321, 16., 1e-6)
        before = copy.deepcopy(world)
        local, metadata = local_frame(world)
        self.assertEqual(world, before)
        self.assertEqual(metadata['origin_BU'], world['sources'][0]['position_BU'])
        self.assertEqual(local['sources'][0]['position_BU'], [0., 0., 0.])
        self.assertEqual(local['sources'][0]['direction'], world['sources'][0]['direction'])
        self.assertEqual(local['sources'][0]['field_reim'], world['sources'][0]['field_reim'])
        self.assertEqual(local['lambda_BU'], world['lambda_BU'])
        self.assertEqual(local['objects']['M']['phase_rad'], world['objects']['M']['phase_rad'])
        self.assertEqual(local['objects']['D']['mode_direction'], world['objects']['D']['mode_direction'])
        self.assertEqual(local['objects']['M']['faces'], world['objects']['M']['faces'])

    def test_relative_frame_does_not_recover_already_lost_scene_precision(self):
        world = transform(direct(), 999900.321987654, 1., 1e-6)
        local, _ = local_frame(world)
        intended_gap = 1e-8
        self.assertNotEqual(local['objects']['D']['mode_origin_BU'][0], intended_gap)
        original = trace_scene(world, max_rays=4)
        decoded, _ = transported(local)
        result = trace_scene(decoded, max_rays=4)
        self.assertLessEqual(abs(original['fields']['D']-result['fields']['D']), 1e-12)

    def test_frame_preflight_does_not_expand_old_abi_bounds(self):
        outside = transform(direct(2.), 1e6, 1., .125)
        with self.assertRaisesRegex(ValueError, 'bounded'): local_frame(outside)
        # Original positions fit, but the two distant groups exceed local bounds.
        inside = direct(2.); inside['sources'][0]['position_BU'] = [-999999., 0., 0.]
        for obj in inside['objects'].values():
            obj['vertices_world_BU'] = [[999999., y, z] for _, y, z in obj['vertices_world_BU']]
            obj['mode_origin_BU'] = [999999., 0., 0.]
        with self.assertRaisesRegex(ValueError, 'bounded'): local_frame(inside)

    def test_roundtrip_retains_ids_fields_and_triangle_counts(self):
        world = reflected(2.)
        recovered, error = transported(world)
        self.assertEqual(list(world['objects']), list(recovered['objects']))
        self.assertEqual(world['sources'], recovered['sources'])
        self.assertEqual(error, 0.)
        self.assertEqual(sum(len(o['faces']) for o in world['objects'].values()),
                         sum(len(o['faces']) for o in recovered['objects'].values()))


if __name__ == '__main__': unittest.main()
