"""Self-checks of the OPT-006 oracle. CPU only: python -m unittest (from this folder)."""

import math
import unittest

from mz_oracle import (
    cross_term_average, delay_line_shift, destructive_by_single_mirror,
    gaussian_overlap, mirror_translation, mz_closed_form, mz_matrix,
    path_phase, single_path_baseline,
)

TOL = 1e-12


class Baseline(unittest.TestCase):
    def test_reproduces_exp000(self):
        b = single_path_baseline()
        self.assertAlmostEqual(b["power"], 0.7053474966, places=10)
        self.assertAlmostEqual(b["activation"], 0.3657724623, places=10)
        self.assertAlmostEqual(b["phase"], 0.25 + 2 * math.pi * 3.8 / 10, places=12)


class TwoDerivationsAgree(unittest.TestCase):
    def test_closed_form_equals_matrices_on_grid(self):
        for tau1 in (0.5, 0.8, 0.1):
            for tau2 in (0.5, 0.3):
                for t1, t2 in ((1, 1), (0.9, 0.7), (1, 0)):
                    for gamma in (1.0, 0.4, 0.0):
                        for k in range(16):
                            dphi = 2 * math.pi * k / 16
                            cf = mz_closed_form(1.0, tau1, tau2, t1, t2, dphi, 0.0, gamma)
                            pa, pb = mz_matrix(1.0, tau1, tau2, t1, t2, dphi, 0.0, gamma)
                            self.assertLess(abs(cf.port_a - pa), TOL)
                            self.assertLess(abs(cf.port_b - pb), TOL)
                            self.assertLess(abs(cf.residual), TOL)


class Controls(unittest.TestCase):
    def test_constructive_and_destructive(self):
        c = mz_closed_form(phi1=0.0, phi2=0.0)
        self.assertLess(abs(c.port_a), TOL)
        self.assertLess(abs(c.port_b - 1.0), TOL)
        d = mz_closed_form(phi1=math.pi, phi2=0.0)
        self.assertLess(abs(d.port_a - 1.0), TOL)
        self.assertLess(abs(d.port_b), TOL)

    def test_unbalanced_visibility(self):
        vals = [mz_closed_form(tau1=0.8, phi1=2 * math.pi * k / 64).port_b for k in range(64)]
        v = (max(vals) - min(vals)) / (max(vals) + min(vals))
        self.assertAlmostEqual(v, 2 * math.sqrt(0.8 * 0.2), places=12)

    def test_incoherent_is_phase_independent(self):
        vals = [mz_closed_form(gamma=0.0, phi1=2 * math.pi * k / 32) for k in range(32)]
        for r in vals:
            self.assertLess(abs(r.port_a - 0.5), TOL)
            self.assertLess(abs(r.port_b - 0.5), TOL)

    def test_uniform_phase_average_equals_incoherent(self):
        n = 8
        pa = sum(mz_closed_form(tau1=0.7, phi1=2 * math.pi * k / n).port_a for k in range(n)) / n
        self.assertLess(abs(pa - mz_closed_form(tau1=0.7, gamma=0.0).port_a), TOL)

    def test_broken_arm(self):
        r = mz_closed_form(t_arm2=0.0, phi1=1.234)
        self.assertLess(abs(r.port_a - 0.25), TOL)
        self.assertLess(abs(r.port_b - 0.25), TOL)
        self.assertLess(abs(r.loss_arm2 - 0.5), TOL)
        self.assertLess(abs(r.residual), TOL)

    def test_single_receiver_can_exceed_input(self):
        # Two coherent 50/50 paths summed at ONE point: |sqrt(.5)+sqrt(.5)|^2 = 2.
        self.assertAlmostEqual(abs(math.sqrt(0.5) + math.sqrt(0.5)) ** 2, 2.0, places=12)


class FrequencyAndGeometry(unittest.TestCase):
    def test_cross_term_limits(self):
        self.assertAlmostEqual(cross_term_average(0.3, 0.0, 1.0), math.cos(0.3), places=12)
        self.assertLess(abs(cross_term_average(0.3, 1e6, 1.0)), 1e-6)
        self.assertLess(abs(cross_term_average(0.0, 1.0, 1.0)), 1e-12)  # full beat period

    def test_phase(self):
        self.assertAlmostEqual(path_phase(0.5, 10.0, 10.0), math.pi, places=12)

    def test_mirror_shift_equals_tan(self):
        g = mirror_translation(0.1, 45.0)
        self.assertAlmostEqual(g["lateral_shift"], g["delta_L"], places=12)

    def test_destructive_mirror_at_lambda_1(self):
        d = destructive_by_single_mirror(1.0, 45.0, waist=0.2)
        self.assertAlmostEqual(d["delta_L"], 0.5, places=12)
        self.assertAlmostEqual(d["lateral_shift"], 0.5, places=12)
        self.assertLess(d["overlap_gamma"], 0.05)  # beams no longer overlap

    def test_delay_line(self):
        self.assertEqual(delay_line_shift(0.5)["lateral_shift"], 0.0)

    def test_overlap(self):
        self.assertEqual(gaussian_overlap(0.0, 1.0), 1.0)


if __name__ == "__main__":
    unittest.main()
