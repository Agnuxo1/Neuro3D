"""Scene-readback guards against a wrong but internally consistent fixture."""

import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exp003_fixture_guard import validate_baseline_paths, validate_observed_disks
from test_exp003_first_hit_preflight import fixture


def observed_for(data):
    return {role: {"position": data[role]["position"],
                   "normal": data[role]["normal"],
                   "radius": data[role]["radius"],
                   "faces": 1, "vertices": 32, "modifiers": False,
                   "scale": (1., 1., 1.)}
            for role in ("bs1", "r1", "r2", "f1", "m2", "bs2")}


class FixtureGuardTests(unittest.TestCase):
    def test_frozen_geometry_is_accepted(self):
        data = fixture()
        self.assertTrue(validate_observed_disks(data, observed_for(data)))

    def test_shifted_pair_is_rejected_even_if_relative_delay_survives(self):
        data = fixture()
        obs = observed_for(data)
        for role in ("r1", "r2"):
            x, y, z = obs[role]["position"]
            obs[role]["position"] = (x + .3, y, z)
        with self.assertRaisesRegex(ValueError, "World position"):
            validate_observed_disks(data, obs)

    def test_solidify_or_short_polygon_is_rejected(self):
        data = fixture()
        obs = observed_for(data)
        obs["r1"]["modifiers"] = True
        with self.assertRaisesRegex(ValueError, "Modified disk"):
            validate_observed_disks(data, obs)
        obs["r1"]["modifiers"] = False
        obs["r1"]["vertices"] = 16
        with self.assertRaisesRegex(ValueError, "topology"):
            validate_observed_disks(data, obs)

    def test_absolute_paths_reject_wrong_dark_port_geometry(self):
        base = {"arm1": {"status": "reached_bs2", "length": 5.0},
                "arm2": {"status": "reached_bs2", "length": 3.0}}
        self.assertTrue(validate_baseline_paths(base))
        base["arm1"]["length"] = 5.6
        with self.assertRaisesRegex(ValueError, "length differs"):
            validate_baseline_paths(base)


if __name__ == "__main__":
    unittest.main()
