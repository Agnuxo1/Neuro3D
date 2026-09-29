"""Fixture-schema checks for the candidate lattice Blender bridge."""

import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exp004_scene_bridge import validate_lattice_fixture


def candidate(k=2):
    disks = []
    for i in range(k):
        for j in range(k):
            for role in ("bs1", "r1", "r2", "f1", "m2", "bs2"):
                disks.append({"id": f"c{i}{j}.{role}",
                              "kind": "bs" if role.startswith("bs") else "mirror",
                              "p": [float(i), float(j), 0.], "n": [0., 0., 1.], "r": .2})
    for axis in ("R", "C"):
        for mode in range(k):
            disks.append({"id": f"det.{axis}{mode}", "kind": "det",
                          "p": [float(mode), 10., 0.], "n": [0., 0., 1.], "r": .15})
    sources = [{"id": f"{axis}{mode}", "p": [0., float(mode), 0.],
                "d": [1., 0., 0.]}
               for axis in ("r", "c") for mode in range(k)]
    return {"K": k, "disks": disks, "sources": sources}


class LatticeFixtureTests(unittest.TestCase):
    def test_candidate_schema(self):
        value = candidate()
        self.assertIs(validate_lattice_fixture(value), value)

    def test_reject_missing_duplicate_and_wrong_kind(self):
        for mutation in ("missing", "duplicate", "kind"):
            with self.subTest(mutation=mutation):
                value = copy.deepcopy(candidate())
                if mutation == "missing":
                    value["disks"].pop()
                elif mutation == "duplicate":
                    value["disks"][1]["id"] = value["disks"][0]["id"]
                else:
                    value["disks"][0]["kind"] = "mirror"
                with self.assertRaises(ValueError):
                    validate_lattice_fixture(value)

    def test_reject_nonfinite_or_nonunit_geometry(self):
        for field, replacement in (("p", [float("nan"), 0., 0.]),
                                   ("n", [0., 0., 2.]), ("r", -1.)):
            with self.subTest(field=field):
                value = copy.deepcopy(candidate())
                value["disks"][0][field] = replacement
                with self.assertRaises(ValueError):
                    validate_lattice_fixture(value)


if __name__ == "__main__":
    unittest.main()
