"""Static checks of frozen EXP-001 edits; no bpy, Blender, or GPU."""

import math
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "tests"), str(ROOT / "oracle")]

from mz_exp001_plan import controls
from geometry_oracle import NonRectMZ


class EXP001PlanTests(unittest.TestCase):
    def test_control_names_and_port_expectations_are_frozen(self):
        cases = controls()
        self.assertEqual([case.name for case in cases],
                         ["A", "B-geo", "B-mat", "C-A", "C-B-geo", "C-B-mat", "D"])
        self.assertEqual([(case.expected_a, case.expected_b, case.expected_escape)
                          for case in cases],
                         [(0, 1, 0), (1, 0, 0), (1, 0, 0),
                          (0.5, 0.5, 0), (0.5, 0.5, 0), (0.5, 0.5, 0),
                          (0.25, 0.25, 0.5)])
        self.assertEqual(cases[-1].expected_status, "missed_bs2")

    def test_geometry_edit_matches_independent_nonrect_reference(self):
        base = NonRectMZ(60.0, 2.0, 2.0).scene()
        edit = controls()[1]
        moved = NonRectMZ(60.0, 2.0 + edit.group_delta[0],
                          2.0 + edit.group_delta[1]).scene()
        for got, expected in zip(edit.group_delta,
                                 tuple(a - b for a, b in zip(moved["bs2"]["position"],
                                                              base["bs2"]["position"]))):
            self.assertAlmostEqual(got, expected, places=12)
        for got, expected in zip(edit.mirror1_delta,
                                 tuple(a - b for a, b in zip(moved["mirror1"]["position"],
                                                              base["mirror1"]["position"]))):
            self.assertAlmostEqual(got, expected, places=12)
        self.assertAlmostEqual(edit.group_delta[0], 0.27990381056766, places=10)
        self.assertAlmostEqual(edit.group_delta[1], 0.16160254037844, places=10)
        self.assertAlmostEqual(edit.mirror1_delta[0], 0.18660254037844, places=10)
        self.assertAlmostEqual(math.hypot(*edit.group_delta[:2]), 0.32320508075689,
                               places=10)


if __name__ == "__main__":
    unittest.main()
