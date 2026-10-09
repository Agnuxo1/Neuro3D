"""Self-checks for the OPT-007 mesh (CPU). python -m unittest (from this folder)."""

import math
import sys
import unittest
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "core"))
from mesh import K, LAMBDA, OpticalMesh, clements_pairs, encode  # noqa: E402


class Mesh(unittest.TestCase):
    def test_cell_count(self):
        for n in (2, 3, 4, 7, 16):
            self.assertEqual(sum(len(c) for c in clements_pairs(n)), n * (n - 1) // 2)

    def test_unitary_and_energy(self):
        m = OpticalMesh(8, 5, seed=3)
        U = m.unitary()
        err = (U.conj().T @ U - torch.eye(8, dtype=torch.complex128)).abs().max().item()
        self.assertLess(err, 1e-12)
        x = encode(torch.rand(32, 8, dtype=torch.float64))
        self.assertLess((m.powers(x).sum(1) - 1).abs().max().item(), 1e-12)

    def test_single_cell_matches_mz_engine_convention(self):
        """N=2 mesh with only the internal delay line = square MZ of mz_scene: equal arms -> port B."""
        from mz_scene import default_scene, trace_mz
        from dataclasses import replace
        m = OpticalMesh(2, 2, seed=0)
        with torch.no_grad():
            m.d_ext.zero_(); m.d_out.zero_()
        inp = torch.tensor([[1.0, 0.0]], dtype=torch.float64)
        for d in (0.0, LAMBDA / 8, LAMBDA / 4):
            with torch.no_grad():
                m.d_int.fill_(d)
            p = m.powers(inp)[0]
            # engine: same splitter convention, relative phase 2*K*d on arm 1 via phase_shift
            s0 = default_scene()
            r = trace_mz(replace(s0, mirror1=replace(s0.mirror1, phase_shift=2 * K * d)))
            self.assertAlmostEqual(p[0].item(), sum(r.optical_a), places=12)
            self.assertAlmostEqual(p[1].item(), sum(r.optical_b), places=12)

    def test_gradient_flows_to_geometry(self):
        m = OpticalMesh(4, 3, seed=1)
        x = encode(torch.rand(10, 4, dtype=torch.float64))
        m(x).sum().backward()
        self.assertGreater(m.d_int.grad.abs().sum().item(), 0)


if __name__ == "__main__":
    unittest.main()
