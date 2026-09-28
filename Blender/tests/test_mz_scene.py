"""Fast CPU checks of the scene-defined two-port MZ prototype; no Blender/GPU."""

import math
import pathlib
import sys
import unittest
from dataclasses import replace

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.mz_scene import default_scene, trace_mz


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
