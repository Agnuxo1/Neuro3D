"""CPU-only checks of EXP-002 procedure; synthetic optics are not evidence."""

import math
from pathlib import Path
from types import SimpleNamespace
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "core"))
from mz_geometry_optimizer import fit_port_a


def fake_result(power_a, *, overlap=1.0, status="ok", residual=0.0):
    a = (power_a / 3,) * 3
    b = ((1.0 - power_a) / 3,) * 3
    return SimpleNamespace(
        status=status, interference_valid=(status == "ok"),
        optical_a=a, optical_b=b, escape_rgb=(0.0,) * 3,
        unresolved_rgb=(0.0,) * 3, residual_rgb=(residual,) * 3,
        mode_overlap=overlap,
    )


class GeometryOptimizerProcedureTests(unittest.TestCase):
    def test_two_targets_on_synthetic_ideal_curve(self):
        def ideal(u):
            return fake_result(math.sin(math.pi * u / 2) ** 2)
        for target, start, expected_u in ((.75, .1, 2 / 3), (.25, .9, 1 / 3)):
            with self.subTest(target=target):
                run = fit_port_a(ideal, target, start)
                self.assertTrue(run.converged)
                self.assertLessEqual(run.updates, 50)
                self.assertLessEqual(abs(run.observations[-1].power_a - target), 1e-4)
                self.assertAlmostEqual(run.final_u, expected_u, delta=1e-3)
                self.assertEqual(len(run.observations), 3 * run.updates + 1)

    def test_frozen_geometry_cannot_reach_target(self):
        positions = []
        def frozen(u):
            positions.append(u)
            return fake_result(.0244717418524232)
        run = fit_port_a(frozen, .75, .1)
        self.assertFalse(run.converged)
        self.assertEqual(run.stop_reason, "zero_gradient")
        self.assertEqual(positions[-1], run.final_u)

    def test_incoherent_control_cannot_reach_target(self):
        run = fit_port_a(lambda _u: fake_result(.5), .75, .1)
        self.assertFalse(run.converged)
        self.assertEqual(run.stop_reason, "zero_gradient")

    def test_rejects_optical_gate_failure_even_at_gradient_probe(self):
        def misaligned(u):
            return fake_result(.1, overlap=.5 if u > .1 else 1.0)
        with self.assertRaisesRegex(ValueError, "overlap"):
            fit_port_a(misaligned, .75, .1)

    def test_rejects_energy_imbalance_and_bad_input(self):
        with self.assertRaisesRegex(ValueError, "imbalance"):
            fit_port_a(lambda _u: fake_result(.2, residual=1e-8), .75, .1)
        with self.assertRaisesRegex(ValueError, "fractions"):
            fit_port_a(lambda _u: fake_result(.2), float("nan"), .1)


if __name__ == "__main__":
    unittest.main()
