"""Lightweight contract tests; no Blender, GPU or scientific runtime claim."""

import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exp004_measured_mesh import PAIRS, propagate_measured_mesh


def measured_cells(length1=5.0, length2=3.0):
    return {(col, lower): {
        "arm1": {"status": "reached_bs2", "length": length1},
        "arm2": {"status": "reached_bs2", "length": length2},
    } for col, pairs in enumerate(PAIRS) for lower, _ in pairs}


class MeasuredMeshTests(unittest.TestCase):
    def test_topology_has_six_cells(self):
        self.assertEqual([len(pairs) for pairs in PAIRS], [2, 1, 2, 1])
        self.assertEqual(sum(map(len, PAIRS)), 6)

    def test_one_cell_port_convention_and_four_basis_powers(self):
        paths = measured_cells()
        for mode in range(4):
            with self.subTest(mode=mode):
                result = propagate_measured_mesh(
                    paths, [float(i == mode) for i in range(4)], .1)
                self.assertAlmostEqual(sum(result["powers"]), 1, places=12)
                for out, power in enumerate(result["powers"]):
                    self.assertAlmostEqual(power, float(out == 3 - mode), places=12)
                self.assertLess(result["balance_error"], 1e-12)
        # In column 0 the equal-phase MZI swaps 0 -> 1, not 0 -> 0.
        paths[(0, 0)]["arm1"]["status"] = "lost"
        paths[(0, 0)]["arm1"]["length"] = None
        result = propagate_measured_mesh(paths, [1, 0, 0, 0], .1)
        self.assertAlmostEqual(result["escape"], .5, places=12)

    def test_interior_geometry_perturbation_changes_output(self):
        paths = measured_cells()
        inp = [1, 0, 0, 0]
        base = propagate_measured_mesh(paths, inp, .1)
        perturbed = copy.deepcopy(paths)
        perturbed[(1, 1)]["arm1"]["length"] += .025
        changed = propagate_measured_mesh(perturbed, inp, .1)
        self.assertGreater(sum(abs(a - b) for a, b in zip(
            base["fields"], changed["fields"])), .1)
        self.assertLess(changed["balance_error"], 1e-12)

    def test_loss_propagates_without_renormalization(self):
        paths = measured_cells()
        paths[(1, 1)]["arm1"] = {"status": "lost", "length": None}
        result = propagate_measured_mesh(paths, [1, 0, 0, 0], .1)
        self.assertGreater(result["escape"], 0)
        self.assertLess(sum(result["powers"]), 1)
        self.assertLess(result["balance_error"], 1e-12)

    def test_missing_cell_and_unresolved_status_fail_closed(self):
        paths = measured_cells()
        del paths[(3, 1)]
        with self.assertRaisesRegex(ValueError, "cell"):
            propagate_measured_mesh(paths, [1, 0, 0, 0], .1)
        paths = measured_cells()
        paths[(2, 0)]["arm1"] = {"status": "unexpected_route", "length": None}
        with self.assertRaisesRegex(ValueError, "Unresolved"):
            propagate_measured_mesh(paths, [1, 0, 0, 0], .1)


if __name__ == "__main__":
    unittest.main()
