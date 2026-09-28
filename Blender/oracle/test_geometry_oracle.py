"""Self-checks of the OPT-009 geometric reference. CPU only: python -m unittest."""

import math
import unittest

from geometry_oracle import (
    Arm, NonRectMZ, combiner_hit_separation, delay_line, falsifiable_square_case,
    manhattan_equal_arms, mz_ledger, naive_hit_delta, square_single_mirror,
    wavefront_delta,
)
from mz_oracle import mz_closed_form

TOL = 1e-12
S2 = math.sqrt(2.0)


def square_arms(d):
    """Hand-derived square MZ (default_scene layout), mirror2 moved by d along -n.

    Arm lengths are counted from BS1 to each arm's own hit on BS2 (plane x = y).
    arm1: (0,0) -> (2,0) -> (2,2), arrives along +y.
    arm2: (0,0) -> (0, 2 + s) -> (2 + s, 2 + s) with s = sqrt(2) d, arrives along +x.
    """

    s = S2 * d
    arm1 = (4.0, (2.0, 2.0, 0.0), (0.0, 1.0, 0.0))
    arm2 = (2.0 + s + 2.0 + s, (2.0 + s, 2.0 + s, 0.0), (1.0, 0.0, 0.0))
    return arm1, arm2


class Wavefront(unittest.TestCase):
    def test_square_mirror_shift_gives_textbook_delta(self):
        for d in (0.001, 0.0177, 0.2):
            arm1, arm2 = square_arms(d)
            got = wavefront_delta(arm1, arm2, arm1[1])
            self.assertAlmostEqual(got, square_single_mirror(d)["delta_L_wavefront"], places=12)
            self.assertAlmostEqual(arm2[0] - arm1[0], naive_hit_delta(d), places=12)

    def test_reference_point_independence(self):
        arm1, arm2 = square_arms(0.05)
        refs = [(2.0 + t, 2.0 + t, 0.0) for t in (-1.0, 0.0, 0.3, 5.0)]  # points on plane x = y
        vals = [wavefront_delta(arm1, arm2, r) for r in refs]
        self.assertLess(max(vals) - min(vals), TOL)

    def test_hit_separation(self):
        d = 0.0177
        s = square_single_mirror(d)["lateral_shift"]
        arm1, arm2 = square_arms(d)
        self.assertAlmostEqual(combiner_hit_separation(s), math.dist(arm1[1], arm2[1]), places=12)


class Geometry(unittest.TestCase):
    def test_square_is_manhattan(self):
        l1, l2 = manhattan_equal_arms(2.3, 1.7)
        self.assertEqual(l1, l2)
        sq = NonRectMZ(90.0, 2.3, 2.3).scene()
        self.assertAlmostEqual(sq["L1_from_bs1"], sq["L2_from_bs1"], places=12)

    def test_nonrect_delta_matches_segments(self):
        checked = 0
        for beta in (50.0, 60.0, 75.0):
            for X, Y in ((2.0, 2.0), (2.5, 2.0), (2.2, 2.6)):
                m = NonRectMZ(beta, X, Y)
                try:
                    sc = m.scene()
                except ValueError:  # P unreachable with positive segments (e.g. beta=50, P=(2.5,2))
                    continue
                checked += 1
                self.assertAlmostEqual(sc["L1_from_bs1"] - sc["L2_from_bs1"], m.delta_L(), places=12)
        self.assertGreaterEqual(checked, 7)
        with self.assertRaises(ValueError):
            NonRectMZ(50.0, 2.5, 2.0).scene()

    def test_nonrect_mirrors_send_rays_to_P(self):
        m = NonRectMZ(60.0, 2.5, 2.0)
        sc = m.scene()
        for mk, u, vdir in (("mirror1", (1.0, 0.0, 0.0), sc["port_a_direction"]),
                            ("mirror2", (0.0, 1.0, 0.0), sc["port_b_direction"])):
            n = sc[mk]["normal"]
            dn = sum(a * b for a, b in zip(u, n))
            r = tuple(a - 2 * dn * b for a, b in zip(u, n))
            for a, b in zip(r, vdir):
                self.assertAlmostEqual(a, b, places=12)
            # ray from mirror along r reaches P
            p = sc[mk]["position"]
            t = math.dist(p, sc["bs2"]["position"])
            end = tuple(a + t * b for a, b in zip(p, r))
            for a, b in zip(end, sc["bs2"]["position"]):
                self.assertAlmostEqual(a, b, places=12)

    def test_delay_line(self):
        self.assertEqual(delay_line(0.25), {"delta_L": 0.5, "lateral_shift": 0.0})


class Ledger(unittest.TestCase):
    def test_matches_phase_oracle_without_losses(self):
        for tau1 in (0.5, 0.8):
            for k in range(8):
                dphi = 2 * math.pi * k / 8
                led = mz_ledger(1.0, tau1, 0.5, Arm(), Arm(), dphi)
                ref = mz_closed_form(1.0, tau1, 0.5, 1, 1, dphi, 0.0)
                self.assertAlmostEqual(led["port_a"], ref.port_a, places=12)
                self.assertAlmostEqual(led["port_b"], ref.port_b, places=12)

    def test_broken_arm_is_escaped_not_loss(self):
        led = mz_ledger(1.0, 0.5, 0.5, Arm(), Arm(escaped=True), 1.234)
        self.assertAlmostEqual(led["escaped"], 0.5, places=12)
        self.assertEqual(led["absorbed"], 0.0)
        self.assertEqual(led["mirror_loss"], 0.0)
        self.assertAlmostEqual(led["port_a"], 0.25, places=12)
        self.assertAlmostEqual(led["port_b"], 0.25, places=12)
        self.assertLess(abs(led["residual"]), TOL)

    def test_lossy_broken_arm_categories(self):
        led = mz_ledger(1.0, 0.5, 0.5, Arm(0.9, 0.8), Arm(0.9, 0.8, escaped=True), 0.0)
        self.assertAlmostEqual(led["absorbed"], 2 * 0.5 * 0.1, places=12)
        self.assertAlmostEqual(led["mirror_loss"], 2 * 0.5 * 0.9 * 0.2, places=12)
        self.assertAlmostEqual(led["escaped"], 0.5 * 0.9 * 0.8, places=12)
        self.assertLess(abs(led["residual"]), TOL)

    def test_partial_overlap_conserves(self):
        for ov in (0.0, 0.3, 1.0):
            for k in range(8):
                led = mz_ledger(1.0, 0.7, 0.4, Arm(0.95, 0.9), Arm(0.8, 1.0), k * 0.8, 1.0, ov)
                self.assertLess(abs(led["residual"]), TOL)


class Falsifiable(unittest.TestCase):
    def test_square_case(self):
        c = falsifiable_square_case()
        self.assertAlmostEqual(c["expected_delta_L_wavefront"], c["wavelength"] / 2, places=12)
        self.assertAlmostEqual(c["naive_hit_delta_L"], c["wavelength"], places=12)
        self.assertLess(c["combiner_hit_separation"], 0.02)
        self.assertAlmostEqual(c["expected_delta_phi"], math.pi, places=12)


if __name__ == "__main__":
    unittest.main()
