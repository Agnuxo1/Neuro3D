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

    def test_gaussian_overlap_uses_transverse_output_separation(self):
        """OPT-002: independent oracle expects s=0.01, not BS2 hit gap 0.01414."""
        baseline = default_scene()
        case = falsifiable_square_case()
        normal = unit(baseline.mirror2.normal)
        d = case["mirror2_shift_along_minus_normal"]
        shifted = tuple(p - d * n for p, n in zip(baseline.mirror2.position, normal))
        # Reference values from Claude's expected_overlap_coherence.json.
        expected = (
            (0.2, 0.9987507809245809, 0.9993753904622904),
            (0.05, 0.9801986733067553, 0.9900993366533777),
            (0.01, 0.6065306597126334, 0.8032653298563167),
        )
        for waist, overlap, port_a in expected:
            scene = replace(baseline,
                            source=replace(baseline.source, frequency=500.0,
                                           beam_waist=waist),
                            mirror2=replace(baseline.mirror2, position=shifted))
            result = trace_mz(scene)
            self.assertEqual(result.status, "ok")
            self.assertTrue(result.interference_valid)
            self.assertAlmostEqual(result.transverse_separation, 0.01, places=12)
            self.assertAlmostEqual(result.mode_overlap, overlap, places=12)
            self.assertAlmostEqual(result.effective_coherence, overlap, places=12)
            self.assertAlmostEqual(total(result.optical_a), port_a, places=12)
            self.assertAlmostEqual(total(result.optical_b), 1 - port_a, places=12)
            self.assert_balanced(result)

    def test_zero_mutual_coherence_is_phase_independent(self):
        baseline = default_scene()
        baseline = replace(baseline, source=replace(baseline.source,
                                                    beam_waist=0.2,
                                                    mutual_coherence=0.0))
        for phase in (0.0, math.pi / 3, math.pi, 5 * math.pi / 3):
            scene = replace(baseline,
                            mirror2=replace(baseline.mirror2, phase_shift=phase))
            result = trace_mz(scene)
            self.assertEqual(result.status, "ok")
            self.assertEqual(result.effective_coherence, 0.0)
            self.assertAlmostEqual(total(result.optical_a), 0.5, places=12)
            self.assertAlmostEqual(total(result.optical_b), 0.5, places=12)
            self.assert_balanced(result)

    def test_incoherent_geometry_sweep_matches_nine_oracle_cases(self):
        baseline = default_scene()
        normal = unit(baseline.mirror2.normal)
        half_cycle_shift = 0.02 / (2 * math.sqrt(2))
        for k in range(9):
            d = half_cycle_shift * k / 4
            shifted = tuple(p - d * n for p, n in zip(baseline.mirror2.position, normal))
            scene = replace(baseline,
                            source=replace(baseline.source, frequency=500.0,
                                           mutual_coherence=0.0),
                            mirror2=replace(baseline.mirror2, position=shifted),
                            overlap_tolerance=0.03)
            result = trace_mz(scene)
            self.assertEqual(result.status, "ok")
            self.assertEqual(result.effective_coherence, 0.0)
            self.assertAlmostEqual(total(result.optical_a), 0.5, places=12)
            self.assertAlmostEqual(total(result.optical_b), 0.5, places=12)
            self.assert_balanced(result)

    def test_partial_mutual_coherence_reduces_visibility(self):
        baseline = default_scene()
        scene = replace(baseline, source=replace(baseline.source,
                                                beam_waist=0.2,
                                                mutual_coherence=0.4))
        bright = trace_mz(scene)
        dark = trace_mz(replace(scene,
                                mirror2=replace(scene.mirror2, phase_shift=math.pi)))
        self.assertAlmostEqual(bright.effective_coherence, 0.4, places=12)
        self.assertAlmostEqual(total(bright.optical_a), 0.3, places=12)
        self.assertAlmostEqual(total(bright.optical_b), 0.7, places=12)
        self.assertAlmostEqual(total(dark.optical_a), 0.7, places=12)
        self.assertAlmostEqual(total(dark.optical_b), 0.3, places=12)
        self.assert_balanced(bright)
        self.assert_balanced(dark)

    def test_partial_coherence_keeps_per_channel_ledger_balanced(self):
        baseline = default_scene()
        scene = replace(
            baseline,
            source=replace(baseline.source, rgb=(1.0, 2.0, 3.0),
                           beam_waist=0.01, mutual_coherence=0.4),
            bs1=replace(baseline.bs1, transmission=0.8),
            mirror1=replace(baseline.mirror1, reflectance=(0.8, 0.9, 1.0)),
            absorption=0.05,
        )
        result = trace_mz(scene)
        self.assertEqual(result.status, "ok")
        self.assertAlmostEqual(result.effective_coherence, 0.4, places=12)
        self.assert_balanced(result)

    def test_asymmetric_partial_coherence_matches_independent_ledger(self):
        baseline = default_scene()
        reflectance = (0.8, 0.9, 1.0)
        scene = replace(
            baseline,
            source=replace(baseline.source, rgb=(1.0, 2.0, 3.0),
                           beam_waist=0.2, mutual_coherence=0.4),
            bs1=replace(baseline.bs1, transmission=0.8),
            mirror1=replace(baseline.mirror1, reflectance=reflectance),
        )
        result = trace_mz(scene)
        self.assertEqual(result.status, "ok")
        for channel, (weight, mirror_r) in enumerate(zip((1, 2, 3), reflectance)):
            oracle = mz_ledger(weight / 6, 0.8, 0.5,
                               Arm(mirror_reflectance=mirror_r), Arm(),
                               0.0, gamma=0.4, overlap=1.0)
            self.assertAlmostEqual(result.optical_a[channel], oracle["port_a"], places=12)
            self.assertAlmostEqual(result.optical_b[channel], oracle["port_b"], places=12)
            self.assertAlmostEqual(result.mirror_loss_rgb[channel], oracle["mirror_loss"], places=12)
        self.assert_balanced(result)

    def test_legacy_ideal_mode_keeps_conservative_centroid_gate(self):
        baseline = default_scene()
        scene = replace(baseline,
                        mirror2=replace(baseline.mirror2, position=(0.0, 2.05, 0.0)))
        result = trace_mz(scene)
        self.assertEqual(result.status, "unresolved_mode_overlap")
        self.assertFalse(result.interference_valid)
        self.assertAlmostEqual(total(result.unresolved_rgb), 1.0, places=12)
        self.assert_balanced(result)

    def test_detector_occlusion_does_not_credit_wrong_port(self):
        baseline = default_scene()
        scene = replace(baseline,
                        mirror2=replace(baseline.mirror2, phase_shift=math.pi),
                        detector_a=Detector((2.0, 3.5, 0.0)),
                        detector_b=Detector((2.4, 2.4, 0.0), radius=0.5))
        result = trace_mz(scene)
        self.assertEqual(result.status, "unresolved_detector_occlusion")
        self.assertFalse(result.interference_valid)
        self.assertAlmostEqual(total(result.unresolved_rgb), 1.0, places=12)
        self.assertAlmostEqual(total(result.optical_a) + total(result.optical_b), 0.0, places=12)
        self.assert_balanced(result)

    def test_detector_behind_combiner_enclosing_origin_is_rejected(self):
        baseline = default_scene()
        scene = replace(baseline,
                        mirror2=replace(baseline.mirror2, phase_shift=math.pi),
                        detector_a=Detector((2.0, 1.9, 0.0), radius=0.15))
        result = trace_mz(scene)
        self.assertEqual(result.status, "unresolved_detector_geometry")
        self.assertFalse(result.interference_valid)
        self.assertAlmostEqual(total(result.unresolved_rgb), 1.0, places=12)
        self.assert_balanced(result)

    def test_two_detectors_enclosing_combiner_are_rejected(self):
        baseline = default_scene()
        shared = Detector((2.0, 2.0, 0.0), radius=0.1)
        scene = replace(baseline, detector_a=shared, detector_b=shared)
        result = trace_mz(scene)
        self.assertEqual(result.status, "unresolved_detector_geometry")
        self.assertFalse(result.interference_valid)
        self.assertAlmostEqual(total(result.unresolved_rgb), 1.0, places=12)
        self.assert_balanced(result)

    def test_finite_wide_beam_uses_gaussian_overlap_threshold(self):
        baseline = default_scene()
        normal = unit(baseline.mirror2.normal)
        d = 0.0125
        shifted = tuple(p - d * n for p, n in zip(baseline.mirror2.position, normal))
        scene = replace(baseline,
                        source=replace(baseline.source, beam_waist=1.0),
                        mirror2=replace(baseline.mirror2, position=shifted))
        result = trace_mz(scene)
        self.assertEqual(result.status, "ok")
        self.assertTrue(result.interference_valid)
        self.assertAlmostEqual(result.mode_overlap, 0.9998437622063955, places=12)
        self.assert_balanced(result)

    def test_finite_narrow_beam_with_negligible_overlap_is_unresolved(self):
        baseline = default_scene()
        normal = unit(baseline.mirror2.normal)
        d = 0.0125
        shifted = tuple(p - d * n for p, n in zip(baseline.mirror2.position, normal))
        scene = replace(baseline,
                        source=replace(baseline.source, beam_waist=0.001),
                        mirror2=replace(baseline.mirror2, position=shifted))
        result = trace_mz(scene)
        self.assertEqual(result.status, "unresolved_mode_overlap")
        self.assertFalse(result.interference_valid)
        self.assertAlmostEqual(total(result.unresolved_rgb), 1.0, places=12)
        self.assert_balanced(result)

    def test_partial_overlap_requires_both_rays_to_reach_each_detector(self):
        baseline = default_scene()
        case = falsifiable_square_case()
        normal = unit(baseline.mirror2.normal)
        d = case["mirror2_shift_along_minus_normal"]
        shifted = tuple(p - d * n for p, n in zip(baseline.mirror2.position, normal))
        scene = replace(baseline,
                        source=replace(baseline.source, frequency=500.0, beam_waist=0.2),
                        mirror2=replace(baseline.mirror2, position=shifted),
                        detector_a=replace(baseline.detector_a, radius=0.003),
                        detector_b=replace(baseline.detector_b, radius=0.003))
        result = trace_mz(scene)
        self.assertEqual(result.status, "unresolved_detector_overlap")
        self.assertFalse(result.interference_valid)
        self.assertAlmostEqual(total(result.unresolved_rgb), 1.0, places=12)
        self.assert_balanced(result)

    def test_invalid_overlap_parameters_are_rejected(self):
        baseline = default_scene()
        for waist in (0.0, -0.1, float("nan"), float("inf")):
            with self.subTest(waist=waist), self.assertRaises(ValueError):
                trace_mz(replace(baseline, source=replace(baseline.source,
                                                         beam_waist=waist)))
        for coherence in (-0.1, 1.1, float("nan"), float("inf")):
            with self.subTest(coherence=coherence), self.assertRaises(ValueError):
                trace_mz(replace(baseline, source=replace(baseline.source,
                                                         mutual_coherence=coherence)))

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
