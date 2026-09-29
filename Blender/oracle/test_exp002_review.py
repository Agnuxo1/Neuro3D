"""Locks the EXP-002 pre-run review findings (CPU only, no Blender)."""

import unittest

import exp002_review as rv


class Exp002Review(unittest.TestCase):
    def test_honest_scene_meets_frozen_criteria(self):
        c = rv.criteria(rv.scene_evaluator)
        self.assertTrue(c["both_targets_converged"])
        self.assertEqual(c["updates"], [20, 20])
        self.assertTrue(c["frozen_control_fails_as_required"])
        self.assertTrue(c["incoherent_control_holds"])

    def test_leaky_runner_is_indistinguishable_by_current_contract(self):
        self.assertEqual(rv.criteria(rv.leaky_evaluator)["both_targets_converged"], True)
        c = rv.criteria(rv.leaky_evaluator)
        self.assertTrue(c["frozen_control_fails_as_required"] and c["incoherent_control_holds"])

    def test_sham_control_separates_honest_from_leaky(self):
        self.assertFalse(any(rv.sham()["converged"]))
        self.assertTrue(all(rv.sham(rv.leaky_evaluator())["converged"]))

    def test_engine_equals_design_curve(self):
        worst = max(abs(sum(rv.scene_evaluator()(k / 50).optical_a)
                        - __import__("math").sin(__import__("math").pi * k / 100) ** 2)
                    for k in range(51))
        self.assertLess(worst, 1e-12)

    def test_final_error_margin_is_thin(self):
        errs = rv.criteria(rv.scene_evaluator)["final_error"]
        self.assertTrue(all(5e-5 < e < 1e-4 for e in errs))


if __name__ == "__main__":
    unittest.main()
