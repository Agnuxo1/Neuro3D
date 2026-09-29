"""Tiny synthetic cross-occlusion checks; no Blender or external fixture."""

import copy
import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exp003_first_hit_preflight import check_fixture


def fixture():
    s = 1 / math.sqrt(2)
    def disk(position, normal):
        return {"position": position, "normal": normal, "radius": .2}
    a, b = (s, -s, 0.), (s, s, 0.)
    return {
        "source": {"position": (-1., 0., 0.), "direction": (1., 0., 0.)},
        "bs1": disk((0., 0., 0.), a), "r1": disk((2., 0., 0.), a),
        "r2": disk((2., .5, 0.), b), "f1": disk((1., .5, 0.), b),
        "m2": disk((0., 2., 0.), a), "bs2": disk((1., 2., 0.), a),
        "delay_pair": ("r1", "r2"),
        "interventions": {"delay_d": (0., .0025, .005),
                          "sham_z": .01, "ablate": "r2"},
    }


class FirstHitPreflightTests(unittest.TestCase):
    def test_expected_routes_and_controls(self):
        result = check_fixture(fixture())
        self.assertEqual(result["arm1"]["hits"], ("r1", "r2", "f1", "bs2"))
        self.assertEqual(result["arm2"]["hits"], ("m2", "bs2"))
        self.assertLess(result["max_delay_error_bu"], 1e-10)

    def test_cross_occluder_is_not_ignored(self):
        changed = copy.deepcopy(fixture())
        changed["m2"]["position"] = (1., 0., 0.)
        with self.assertRaises(AssertionError):
            check_fixture(changed)


if __name__ == "__main__":
    unittest.main()
