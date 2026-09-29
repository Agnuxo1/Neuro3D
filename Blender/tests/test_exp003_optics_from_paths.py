"""Independent arithmetic gates for the explicitly hybrid field combiner."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exp003_optics_from_paths import combine_measured_paths


def paths(length1=5., length2=3., status1="reached_bs2"):
    return {"arm1": {"status": status1, "length": length1},
            "arm2": {"status": "reached_bs2", "length": length2}}


class OpticalCombinationTests(unittest.TestCase):
    def test_dark_half_and_bright_ports(self):
        for length, target in ((5., 0.), (5.025, .5), (5.05, 1.)):
            with self.subTest(length=length):
                result = combine_measured_paths(paths(length1=length), .1)
                self.assertAlmostEqual(result["P_A"], target, places=10)
                self.assertLess(result["balance_error"], 1e-12)

    def test_lost_arm_is_escape_not_phase_fallback(self):
        result = combine_measured_paths(paths(length1=None, status1="lost"), .1)
        self.assertAlmostEqual(result["P_A"], .25)
        self.assertAlmostEqual(result["P_B"], .25)
        self.assertAlmostEqual(result["escape"], .5)
        self.assertLess(result["balance_error"], 1e-12)

    def test_invalid_scene_status_cannot_be_treated_as_lost(self):
        with self.assertRaisesRegex(ValueError, "Invalid"):
            combine_measured_paths(paths(length1=None, status1="unexpected_route"), .1)


if __name__ == "__main__":
    unittest.main()
