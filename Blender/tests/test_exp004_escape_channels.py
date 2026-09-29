"""Adversarial light-CPU checks of proposed coherent escape grouping."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exp004_escape_channels import group_raw_escapes


def ray(point=(0., 0., 0.), direction=(1., 0., 0.), last="r2", field=(1., 0.)):
    return {"last": last, "point": point, "dir": direction,
            "L": 5., "field": field}


class EscapeGroupingTests(unittest.TestCase):
    def test_same_line_coherent_even_with_longitudinal_offset(self):
        grouped = group_raw_escapes([ray(), ray(point=(.5, .0002, 0.),
                                              field=(-1., 0.))])
        self.assertEqual(len(grouped), 1)
        self.assertEqual(grouped[0][2], 2)
        self.assertAlmostEqual(abs(grouped[0][1]), 0)

    def test_parallel_but_laterally_separate_must_not_merge(self):
        grouped = group_raw_escapes([ray(), ray(point=(0., .02, 0.))])
        self.assertEqual(len(grouped), 2)

    def test_grey_zone_and_non_transitive_chain_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "Ambiguous"):
            group_raw_escapes([ray(), ray(point=(0., .005, 0.))])
        with self.assertRaisesRegex(ValueError, "Ambiguous"):
            group_raw_escapes([ray(), ray(point=(0., .0008, 0.)),
                               ray(point=(0., .0016, 0.))])

    def test_angular_boundary_is_not_silently_rounded(self):
        close = group_raw_escapes([ray(), ray(direction=(1., 5e-5, 0.))])
        self.assertEqual(len(close), 1)
        with self.assertRaisesRegex(ValueError, "Ambiguous"):
            group_raw_escapes([ray(), ray(direction=(1., 5e-4, 0.))])
        far = group_raw_escapes([ray(), ray(direction=(1., 2e-3, 0.))])
        self.assertEqual(len(far), 2)

    def test_different_last_objects_remain_separate(self):
        grouped = group_raw_escapes([ray(), ray(last="f1")])
        self.assertEqual(len(grouped), 2)


if __name__ == "__main__":
    unittest.main()
