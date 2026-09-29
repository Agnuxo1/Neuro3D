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
                   "scale": (1., 1., 1.), "parented": False,
                   "world_axes": ((1., 0., 0.), (0., 1., 0.), (0., 0., 1.)),
                   "local_vertices": tuple((data[role]["radius"] * math.cos(2 * math.pi * i / 32),
                                            data[role]["radius"] * math.sin(2 * math.pi * i / 32),
                                            0.) for i in range(32))}
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

    def test_face_normal_and_parent_transform_are_checked(self):
        data = fixture()
        obs = observed_for(data)
        obs["r1"]["normal"] = (0., 0., 1.)
        with self.assertRaisesRegex(ValueError, "normal"):
            validate_observed_disks(data, obs)
        obs = observed_for(data)
        obs["r1"]["parented"] = True
        with self.assertRaisesRegex(ValueError, "Parented"):
            validate_observed_disks(data, obs)
        obs = observed_for(data)
        obs["r1"]["world_axes"] = ((1., 0., 0.), (.1, 1., 0.), (0., 0., 1.))
        with self.assertRaisesRegex(ValueError, "World"):
            validate_observed_disks(data, obs)

    def test_nonplanar_vertices_are_rejected_and_reversed_normal_is_recorded(self):
        data = fixture()
        obs = observed_for(data)
        vertices = list(obs["r1"]["local_vertices"])
        vertices[0] = (*vertices[0][:2], .001)
        obs["r1"]["local_vertices"] = vertices
        with self.assertRaisesRegex(ValueError, "vertices"):
            validate_observed_disks(data, obs)
        obs = observed_for(data)
        obs["r1"]["normal"] = tuple(-x for x in obs["r1"]["normal"])
        self.assertEqual(validate_observed_disks(data, obs)["normal_signs"]["r1"], -1)

    def test_nonfinite_readback_is_not_accepted(self):
        data = fixture()
        obs = observed_for(data)
        obs["r1"]["radius"] = float("nan")
        with self.assertRaisesRegex(ValueError, "Radius"):
            validate_observed_disks(data, obs)


if __name__ == "__main__":
    unittest.main()
