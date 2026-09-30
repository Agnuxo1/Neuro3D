import copy
from fractions import Fraction
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).parents[1]/'benchmarks/capacity_audit'))
from scene_length_bound_v1 import scene_length_bound, scene_wavelength_budget, upward_float
from exp005_escape_fixture import escape_fixture


class SceneLengthBoundTests(unittest.TestCase):
    def test_segment_depth_and_reference_formula_exact(self):
        result = scene_length_bound(escape_fixture(), max_depth=16)
        d = Fraction(*result['segment_diameter_L1_BU_rational'])
        r = Fraction(*result['reference_offset_L1_BU_rational'])
        self.assertEqual(Fraction(*result['effective_length_abs_BU_rational']), 16*d+r)
        self.assertFalse(result['native_certified'])

    def test_far_reference_increases_bound_and_changes_snapshot_identity(self):
        scene = escape_fixture(); original = scene_length_bound(scene, max_depth=16)
        scene['objects']['a.Y']['mode_origin_BU'] = [999., 999., 999.]
        changed = scene_length_bound(scene, max_depth=16)
        self.assertGreater(Fraction(*changed['effective_length_abs_BU_rational']),
                           Fraction(*original['effective_length_abs_BU_rational']))
        self.assertNotEqual(original['scene_canonical_sha256'], changed['scene_canonical_sha256'])

    def test_exact_translation_preserves_bound_not_snapshot_hash(self):
        scene = escape_fixture(); translated = copy.deepcopy(scene)
        for source in translated['sources']:
            source['position_BU'] = [v+32. for v in source['position_BU']]
        for obj in translated['objects'].values():
            obj['vertices_world_BU'] = [[v+32. for v in p] for p in obj['vertices_world_BU']]
            if obj['kind'] in ('det', 'escape'):
                obj['mode_origin_BU'] = [v+32. for v in obj['mode_origin_BU']]
        a = scene_length_bound(scene, max_depth=16)
        b = scene_length_bound(translated, max_depth=16)
        self.assertEqual(a['effective_length_abs_BU_rational'], b['effective_length_abs_BU_rational'])
        self.assertNotEqual(a['scene_canonical_sha256'], b['scene_canonical_sha256'])

    def test_bound_conversion_never_rounds_down(self):
        for q in (Fraction(1,3), Fraction(10,7), Fraction(2**53+1)):
            self.assertGreaterEqual(Fraction(upward_float(q)), q)

    def test_invalid_depth_incomplete_scene_and_no_native_promotion(self):
        for depth in (0, 33, True, 1.5):
            with self.assertRaises(ValueError): scene_length_bound(escape_fixture(), max_depth=depth)
        scene = escape_fixture(); scene['undeclared_meshes'] = ['hidden']
        with self.assertRaises(ValueError): scene_length_bound(scene, max_depth=16)
        result = scene_wavelength_budget(escape_fixture(), max_depth=16,
            phase_budget_rad=1e-4, relative_budget=1e-12)
        self.assertTrue(result['wavelength_only_budget']['accepted'])
        self.assertFalse(result['native_promotion_allowed'])


if __name__ == '__main__': unittest.main()
