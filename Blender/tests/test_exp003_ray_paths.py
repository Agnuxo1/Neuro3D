"""CPU-light contract tests; Blender scene integration is still unrun."""

import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exp003_first_hit_preflight import first_hit
from exp003_ray_paths import trace_paths
from test_exp003_first_hit_preflight import fixture


def cast_for(fixture_data, removed=None, extra=None):
    disks = {}
    for name in ("bs1", "r1", "r2", "f1", "m2", "bs2"):
        if name == removed:
            continue
        item = fixture_data[name]
        disks[name] = (tuple(item["position"]), tuple(item["normal"]),
                       item["radius"])
    if extra is not None:
        disks["occluder"] = extra

    def cast(origin, direction):
        hit = first_hit(origin, direction, disks)
        return None if hit is None else (hit[1], hit[2], disks[hit[1]][1])

    return cast


class RayPathTests(unittest.TestCase):
    def test_scene_hits_control_lengths(self):
        data = fixture()
        result = trace_paths(cast_for(data), data["source"]["position"],
                             data["source"]["direction"])
        self.assertEqual(result["arm1"]["status"], "reached_bs2")
        self.assertEqual([h["object"] for h in result["arm1"]["hits"]],
                         ["r1", "r2", "f1", "bs2"])
        self.assertAlmostEqual(result["arm1"]["length"], 5)
        self.assertAlmostEqual(result["arm2"]["length"], 3)

    def test_missing_mirror_is_loss_not_analytic_fallback(self):
        data = fixture()
        result = trace_paths(cast_for(data, removed="r2"),
                             data["source"]["position"],
                             data["source"]["direction"])
        self.assertEqual(result["arm1"]["status"], "lost")
        self.assertIsNone(result["arm1"]["length"])
        self.assertEqual(result["arm2"]["status"], "reached_bs2")

    def test_cross_occluder_is_reported(self):
        data = fixture()
        s = 1 / math.sqrt(2)
        extra = ((1., 0., 0.), (s, -s, 0.), .2)
        result = trace_paths(cast_for(data, extra=extra),
                             data["source"]["position"],
                             data["source"]["direction"])
        self.assertEqual(result["arm1"]["hits"][0]["object"], "occluder")

    def test_self_hit_cannot_produce_a_usable_phase(self):
        data = fixture()
        base = cast_for(data)
        previous = [None]

        def self_hitting_cast(origin, direction):
            if previous[0] == "r1":
                previous[0] = None
                return "r1", (2., .0001, 0.), data["r1"]["normal"]
            hit = base(origin, direction)
            previous[0] = hit[0] if hit else None
            return hit

        result = trace_paths(self_hitting_cast, data["source"]["position"],
                             data["source"]["direction"])
        self.assertEqual(result["arm1"]["status"], "invalid_self_hit")
        self.assertIsNone(result["arm1"]["length"])

    def test_unexpected_route_is_not_relabelled_as_success(self):
        data = fixture()
        wrong = {"arm1": ("r1", "bs2"), "arm2": ("m2", "bs2")}
        result = trace_paths(cast_for(data), data["source"]["position"],
                             data["source"]["direction"], expected_routes=wrong)
        self.assertEqual(result["arm1"]["status"], "unexpected_route")
        self.assertIsNone(result["arm1"]["length"])


if __name__ == "__main__":
    unittest.main()
