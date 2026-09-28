"""Tiny CPU tests for geometry-controlled optical signal transport."""

import math
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.scene_optics import Emitter, Receiver, Reflector, trace_single_reflection


class SceneOpticsTests(unittest.TestCase):
    def setUp(self):
        self.source = Emitter((-2.0, 0.0, 0.0), (1.0, 0.0, 0.0), 1.0, (1.0, 0.5, 0.2), 1.0, 0.0)
        self.mirror = Reflector((0.0, 0.0, 0.0), (1.0, -1.0, 0.0), 0.5, (0.8, 0.9, 1.0), 0.25)
        self.receiver = Receiver((0.0, 2.0, 0.0), 0.2)

    def test_reflector_delivers_colored_power_and_phase(self):
        result = trace_single_reflection(self.source, self.mirror, self.receiver)
        self.assertTrue(result.hit)
        self.assertAlmostEqual(result.path_length, 3.8)
        self.assertGreater(result.intensity, 0.0)
        self.assertLessEqual(result.intensity, self.source.intensity)
        self.assertGreater(result.color_power[0], result.color_power[1])
        self.assertAlmostEqual(result.frequency, self.source.frequency)
        expected = math.remainder(0.25 + 2.0 * math.pi * 3.8 / 10.0, 2.0 * math.pi)
        self.assertAlmostEqual(result.phase, expected)

    def test_turning_mirror_breaks_path(self):
        turned = Reflector(self.mirror.position, (1.0, 0.0, 0.0), self.mirror.radius, self.mirror.reflectance)
        result = trace_single_reflection(self.source, turned, self.receiver)
        self.assertFalse(result.hit)
        self.assertEqual(result.intensity, 0.0)

    def test_moving_receiver_breaks_path(self):
        result = trace_single_reflection(self.source, self.mirror, Receiver((0.0, 2.0, 1.0), 0.2))
        self.assertFalse(result.hit)

    def test_material_filter_changes_received_color(self):
        blue_only = Reflector(self.mirror.position, self.mirror.normal, self.mirror.radius, (0.0, 0.0, 1.0))
        result = trace_single_reflection(self.source, blue_only, self.receiver)
        self.assertTrue(result.hit)
        self.assertEqual(result.color_power[0], 0.0)
        self.assertEqual(result.color_power[1], 0.0)
        self.assertGreater(result.color_power[2], 0.0)

    def test_absorption_reduces_received_power(self):
        low = trace_single_reflection(self.source, self.mirror, self.receiver, absorption_per_unit=0.01)
        high = trace_single_reflection(self.source, self.mirror, self.receiver, absorption_per_unit=0.5)
        self.assertLess(high.intensity, low.intensity)

    def test_receiver_threshold_controls_activation(self):
        active = trace_single_reflection(self.source, self.mirror, self.receiver)
        silent = trace_single_reflection(
            self.source, self.mirror,
            Receiver(self.receiver.position, self.receiver.radius, activation_threshold=10.0),
        )
        self.assertGreater(active.activation, 0.0)
        self.assertEqual(silent.activation, 0.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
