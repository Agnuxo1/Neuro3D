"""Fast CPU checks of the scene-defined two-port MZ prototype; no Blender/GPU."""

import math
import pathlib
import sys
import unittest
from dataclasses import replace

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.mz_scene import Detector, Mirror, Splitter, default_scene, trace_mz, unit
from oracle.geometry_oracle import NonRectMZ, falsifiable_square_case, mz_ledger, Arm


def total(rgb):
    return sum(rgb)


class MZSceneTests(unittest.TestCase):
    def assert_balanced(self, result):
        for residual in result.residual_rgb:
            self.assertLess(abs(residual), 1e-12)

    def test_equal_arms_route_power_to_port_b(self):
        result = trace_mz(default_scene())
        self.assertEqual(result.status, "ok")
        self.assertTrue(result.interference_valid)
        self.assertLess(total(result.optical_a), 1e-12)
        self.assertAlmostEqual(total(result.optical_b), 1.0, places=12)
        self.assert_balanced(result)

    def test_nonrectangular_scene_geometry_switches_ports(self):
        """Independent closed-form geometry supplies the scene and expected ports."""
        baseline = default_scene()
        beta = 60.0
        shift_x = 0.5 / (1 - math.tan(math.radians(beta / 2)))
        for x, expected_a in ((2.0, 0.0), (2.0 + shift_x, 1.0)):
            geometry = NonRectMZ(beta, x, 2.0)
            positions = geometry.scene()
            p = positions["bs2"]["position"]
            da = positions["port_a_direction"]
            db = positions["port_b_direction"]
            scene = replace(
                baseline,
                mirror1=Mirror(positions["mirror1"]["position"], positions["mirror1"]["normal"]),
                mirror2=Mirror(positions["mirror2"]["position"], positions["mirror2"]["normal"]),
                bs2=Splitter(p, positions["bs2"]["normal"]),
                detector_a=Detector(tuple(a + b for a, b in zip(p, da))),
                detector_b=Detector(tuple(a + b for a, b in zip(p, db))),
            )
            result = trace_mz(scene)
            oracle = mz_ledger(1.0, 0.5, 0.5, Arm(), Arm(),
                               2 * math.pi * geometry.delta_L())
            self.assertEqual(result.status, "ok")
            self.assertTrue(result.interference_valid)
            self.assertAlmostEqual(total(result.optical_a), expected_a, places=10)
            self.assertAlmostEqual(total(result.optical_a), oracle["port_a"], places=10)
            self.assertAlmostEqual(total(result.optical_b), oracle["port_b"], places=10)
            self.assert_balanced(result)

    def test_square_offset_hits_use_common_wavefront_phase(self):
        """The old engine reports B=1 here because it compares different hit points."""
        baseline = default_scene()
        case = falsifiable_square_case()
        normal = unit(baseline.mirror2.normal)
        d = case["mirror2_shift_along_minus_normal"]
        shifted = tuple(p - d * n for p, n in zip(baseline.mirror2.position, normal))
        scene = replace(baseline,
                        source=replace(baseline.source, frequency=500.0),
                        mirror2=replace(baseline.mirror2, position=shifted))
        result = trace_mz(scene)
        self.assertEqual(result.status, "ok")
        self.assertTrue(result.interference_valid)
        self.assertAlmostEqual(total(result.optical_a), case["expected_port_a"], places=9)
        self.assertAlmostEqual(total(result.optical_b), case["expected_port_b"], places=9)
        self.assert_balanced(result)

    def test_square_phase_is_invariant_to_reference_on_combiner_plane(self):
        baseline = default_scene()
        case = falsifiable_square_case()
        normal = unit(baseline.mirror2.normal)
        d = case["mirror2_shift_along_minus_normal"]
        shifted = tuple(p - d * n for p, n in zip(baseline.mirror2.position, normal))
        scene = replace(baseline,
                        source=replace(baseline.source, frequency=500.0),
                        mirror2=replace(baseline.mirror2, position=shifted))
        reference = trace_mz(scene)
        for displacement in (-0.1, 0.1):
            # This translates the finite disc *within its own plane* only.
            p = scene.bs2.position
            moved = (p[0] + displacement, p[1] + displacement, p[2])
            result = trace_mz(replace(scene, bs2=replace(scene.bs2, position=moved)))
            self.assertEqual(result.status, "ok")
            self.assertAlmostEqual(total(result.optical_a), total(reference.optical_a), places=9)
            self.assertAlmostEqual(total(result.optical_b), total(reference.optical_b), places=9)
            self.assert_balanced(result)

    def test_tiny_nonzero_splitter_branch_is_accounted(self):
        scene = default_scene()
        scene = replace(scene, bs1=replace(scene.bs1, transmission=1e-10))
        result = trace_mz(scene)
        self.assertEqual(result.status, "ok")
        self.assert_balanced(result)

    def test_mirror_phase_swaps_ports(self):
        scene = default_scene()
        shifted = replace(scene, mirror2=replace(scene.mirror2, phase_shift=math.pi))
        result = trace_mz(shifted)
        self.assertTrue(result.interference_valid)
        self.assertAlmostEqual(total(result.optical_a), 1.0, places=12)
        self.assertLess(total(result.optical_b), 1e-12)
        self.assert_balanced(result)

    def test_unbalanced_splitter_has_expected_visibility(self):
        scene = default_scene()
        scene = replace(scene, bs1=replace(scene.bs1, transmission=0.8))
        powers = []
        for k in range(32):
            shift = 2 * math.pi * k / 32
            variant = replace(scene, mirror2=replace(scene.mirror2, phase_shift=shift))
            result = trace_mz(variant)
            powers.append(total(result.optical_b))
            self.assert_balanced(result)
        visibility = (max(powers) - min(powers)) / (max(powers) + min(powers))
        self.assertAlmostEqual(visibility, 0.8, places=12)

    def test_material_and_path_absorption_are_in_ledger(self):
        scene = default_scene()
        scene = replace(scene, absorption=0.05,
                        mirror1=replace(scene.mirror1, reflectance=(0.8, 0.9, 1.0)),
                        mirror2=replace(scene.mirror2, reflectance=(0.8, 0.9, 1.0)))
        result = trace_mz(scene)
        self.assertEqual(result.status, "ok")
        self.assertGreater(total(result.absorption_rgb), 0)
        self.assertGreater(total(result.mirror_loss_rgb), 0)
        self.assertLess(total(result.optical_a) + total(result.optical_b), 1.0)
        self.assert_balanced(result)

    def test_turning_one_mirror_breaks_one_arm(self):
        scene = default_scene()
        scene = replace(scene, mirror2=replace(scene.mirror2, normal=(0.0, 1.0, 0.0)))
        result = trace_mz(scene)
        self.assertFalse(result.interference_valid)
        self.assertAlmostEqual(total(result.optical_a), 0.25, places=12)
        self.assertAlmostEqual(total(result.optical_b), 0.25, places=12)
        self.assertAlmostEqual(total(result.escape_rgb), 0.5, places=12)
        self.assert_balanced(result)

    def test_nonoverlapping_paths_are_not_called_interference(self):
        scene = default_scene()
        scene = replace(scene, mirror2=replace(scene.mirror2, position=(0.0, 2.05, 0.0)))
        result = trace_mz(scene)
        self.assertEqual(result.status, "unresolved_mode_overlap")
        self.assertFalse(result.interference_valid)
        self.assertEqual(total(result.optical_a) + total(result.optical_b), 0.0)
        self.assertAlmostEqual(total(result.unresolved_rgb), 1.0, places=12)
        self.assert_balanced(result)

    def test_detector_responsivity_does_not_change_optical_balance(self):
        scene = default_scene()
        scene = replace(scene, detector_b=replace(scene.detector_b,
                                                 responsivity=(0.0, 0.5, 1.0)))
        result = trace_mz(scene)
        self.assertAlmostEqual(total(result.optical_b), 1.0, places=12)
        self.assertLess(result.signal_b, total(result.optical_b))
        self.assert_balanced(result)

    def test_invalid_transmission_is_rejected(self):
        scene = default_scene()
        with self.assertRaises(ValueError):
            trace_mz(replace(scene, bs1=replace(scene.bs1, transmission=1.1)))

    def test_large_finite_phase_is_reduced_before_field_combination(self):
        scene = default_scene()
        scene = replace(scene, source=replace(scene.source, phase=1e308))
        result = trace_mz(scene)
        self.assertTrue(all(math.isfinite(x) for x in (*result.optical_a, *result.optical_b)))
        self.assert_balanced(result)

    def test_overflowing_phase_is_rejected(self):
        scene = default_scene()
        scene = replace(scene, source=replace(scene.source, frequency=1e308), speed=1e-8)
        with self.assertRaises(ValueError):
            trace_mz(scene)


if __name__ == "__main__":
    unittest.main()
