"""Solver verification for WAVE-C1. None of these cases is the preregistered confirmation configuration."""
from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path
import unittest

import numpy as np

from angular_spectrum_wave import (K, SQ2, Beam, Grid, MZIGeometry, Splitter, cascade_model,
    gaussian_waist_beam, mirror, modal_amplitude, mzi_model, path_field, port_amplitudes,
    port_mode, slab_coefficients, solve_cascade, solve_mzi)

HERE = Path(__file__).resolve().parent
WAVE = HERE.parent / "validacion-onda"


def frozen_mzi_module():
    """Load the frozen P1-7 module by path without changing sys.path or the working directory."""
    import sys
    sys.path.insert(0, str(WAVE))
    try:
        spec = importlib.util.spec_from_file_location("p17_mzi_fdtd", WAVE / "mzi_fdtd.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.remove(str(WAVE))


def synthesize(beam: Beam, points) -> np.ndarray:
    """Evaluate a beam at arbitrary (x, y) points by direct plane-wave summation."""
    g = beam.grid
    out = []
    for x, y in points:
        distance = (x - beam.x_ref) * beam.direction
        phase = np.exp(1j * (g.kx * distance + g.ky * (y - g.y[0])))
        out.append(np.sum(np.where(g.propagating, beam.spectrum * phase, 0.0)) / g.n)
    return np.asarray(out)


def direct_quadrature(x, y, x_w, y_w, w, angle_deg=45.0, samples=6001):
    """Independent exact plane-wave integral of the waist-defined Gaussian beam (no FFT)."""
    kappa = np.linspace(-3.0, 3.0, samples)
    dk = kappa[1] - kappa[0]
    a = w / (2 * math.sqrt(math.pi)) * np.exp(-(kappa * w) ** 2 / 4)
    beta = np.arcsin(kappa / K)
    alpha = math.radians(angle_deg) + beta
    kx, ky = K * np.cos(alpha), K * np.sin(alpha)
    return np.array([np.sum(a * np.exp(1j * (kx * (xi - x_w) + ky * (yi - y_w)))) * dk for xi, yi in zip(x, y)])


class SlabTests(unittest.TestCase):
    def test_interface_reference_equals_project_tmm(self):
        cal = json.loads((WAVE / "calibracion_45.json").read_text(encoding="utf-8"))
        n, d = cal["n_nominal"], cal["d_nominal_lambda"]
        ky = np.array([K / SQ2])
        rc, tc = slab_coefficients(ky, n, d)
        kx0 = K / SQ2
        r_face, t_face = rc[0] * np.exp(1j * kx0 * d), tc[0] * np.exp(1j * kx0 * d)
        self.assertLess(abs(r_face - complex(*cal["rt_1d_nominal"]["r"])), 1e-14)
        self.assertLess(abs(t_face - complex(*cal["rt_1d_nominal"]["t"])), 1e-14)
        self.assertAlmostEqual(abs(rc[0]) ** 2, 0.5, places=12)

    def test_lossless_symmetric_slab_energy_and_quadrature(self):
        ky = np.linspace(-0.999 * K, 0.999 * K, 501)
        for n in (1.0, 1.5, 2.427, 2.537):
            r, t = slab_coefficients(ky, n, 0.25)
            np.testing.assert_allclose(np.abs(r) ** 2 + np.abs(t) ** 2, 1.0, atol=1e-13)
            np.testing.assert_allclose((r * np.conj(t)).real, 0.0, atol=1e-13)
        r, t = slab_coefficients(ky, 1.0, 0.25)
        np.testing.assert_allclose(r, 0.0, atol=1e-15)
        np.testing.assert_allclose(t, 1.0, atol=1e-15)


class BeamTests(unittest.TestCase):
    grid = Grid(-200.0, 512.0, 4096)

    def test_waist_line_profile_is_exact(self):
        beam = gaussian_waist_beam(self.grid, 0.0, 0.0, 8.0)
        s = np.linspace(-24, 24, 13)
        points = [(-si / SQ2, si / SQ2) for si in s]
        np.testing.assert_allclose(synthesize(beam, points), np.exp(-(s / 8.0) ** 2), atol=1e-10)

    def test_propagated_field_matches_independent_quadrature(self):
        beam = gaussian_waist_beam(self.grid, 0.0, 0.0, 8.0)
        far = beam.at(67.0)
        idx = np.argmin(np.abs(self.grid.y - 67.0))
        sel = slice(idx - 160, idx + 160, 8)
        expected = direct_quadrature(np.full(40, 67.0), self.grid.y[sel], 0.0, 0.0, 8.0)
        np.testing.assert_allclose(far.field()[sel], expected, atol=1e-9)

    def test_flux_is_conserved_by_propagation_and_mirror(self):
        beam = gaussian_waist_beam(self.grid, 0.0, 0.0, 8.0)
        reflected = mirror(beam, 20.0)
        self.assertAlmostEqual(beam.flux(), reflected.flux(), places=12)
        kappa = np.linspace(-3.0, 3.0, 60001)
        density = (8.0 / (2 * math.sqrt(math.pi)) * np.exp(-(kappa * 8.0) ** 2 / 4)) ** 2
        exact = 2 * math.pi * np.sum(density * np.sqrt(1 - (kappa / K) ** 2)) * (kappa[1] - kappa[0])
        self.assertAlmostEqual(beam.flux() / exact, 1.0, places=9)
        self.assertAlmostEqual(beam.flux() / (8.0 * math.sqrt(math.pi / 2)), 1 - 1 / (2 * (8.0 * K) ** 2), places=6)

    def test_two_mirrors_equal_unfolded_free_propagation(self):
        beam = gaussian_waist_beam(self.grid, 0.0, 0.0, 8.0)
        twice = mirror(mirror(beam, 15.0), -5.0).at(10.0)
        unfolded = beam.at(15.0 + 20.0 + 15.0)
        np.testing.assert_allclose(twice.field(), unfolded.field(), atol=1e-12)


class ModelEquivalenceTests(unittest.TestCase):
    def test_path_field_equals_frozen_p17_formula(self):
        frozen = frozen_mzi_module()
        y = np.linspace(-50, 150, 2001)
        rng = np.random.default_rng(7)
        for _ in range(20):
            q = tuple(rng.uniform(-10, 60, 2))
            d = (1 / SQ2, 1 / SQ2) if rng.random() < 0.5 else (-1 / SQ2, 1 / SQ2)
            length, coefficient, x_p = rng.uniform(0, 120), complex(*rng.normal(size=2)), rng.uniform(-30, 30)
            for diffraction in (False, True):
                np.testing.assert_allclose(path_field(x_p, y, q, d, length, coefficient, 8.0, diffraction),
                                           frozen.haz_ideal(x_p, y, q, d, length, coefficient, diffraction), atol=1e-13)

    def test_single_stage_cascade_model_equals_mzi_model(self):
        grid = Grid(-186.0, 512.0, 4096)
        g = MZIGeometry(0.0, 0.0, 21.2, 21.5, 25.0, -25.0, 67.4, 67.4)
        r, t = 0.1 + 0.7j, -0.7 + 0.1j
        for diffraction in (False, True):
            a = mzi_model(g, r, t, grid, 8.0, diffraction)
            b = cascade_model([g], r, t, grid, 8.0, diffraction)
            self.assertLess(max(abs(a[0] - b[0]), abs(a[1] - b[1])), 1e-14)


class CompositionTests(unittest.TestCase):
    """Wide beams make diffraction negligible, so solver and path model must agree closely."""
    grid = Grid(-186.0, 512.0, 4096)
    r, t = 1j / SQ2, 1 / SQ2

    def geometry(self, a_b):
        a = 30 / SQ2
        return MZIGeometry(0.0, 0.0, a, a_b, 25.0, -25.0, 2 * a + 25, 2 * a + 25)

    def test_ideal_wide_beam_mzi_matches_path_model(self):
        for delta in (0.0, 0.1, 0.25):
            g = self.geometry(30 / SQ2 + delta)
            beam = gaussian_waist_beam(self.grid, 0.0, 0.0, 60.0)
            res = solve_mzi(beam, Splitter(self.grid, 0.0, r=self.r, t=self.t), g)
            c = port_amplitudes(res, self.grid, g, 60.0)
            m = mzi_model(g, self.r, self.t, self.grid, 60.0, True)
            self.assertLess(max(abs(abs(c[0]) ** 2 - abs(m[0]) ** 2), abs(abs(c[1]) ** 2 - abs(m[1]) ** 2)), 2e-4)
            self.assertAlmostEqual(res["flux_out"] / res["flux_in"], 1.0, places=12)

    def test_slab_mzi_conserves_flux(self):
        g = self.geometry(30 / SQ2 + 0.13)
        beam = gaussian_waist_beam(self.grid, 0.0, 0.0, 12.0)
        res = solve_mzi(beam, Splitter(self.grid, 0.0, n=2.0, d=0.25), g)
        self.assertAlmostEqual(res["flux_out"] / res["flux_in"], 1.0, places=11)

    def test_two_stage_cascade_wide_beam_matches_model(self):
        a = 30 / SQ2
        g1 = MZIGeometry(0.0, 0.0, a, a + 0.1, 25.0, -25.0, 2 * a + 25, 2 * a + 25)
        y2 = 2 * a + 30 + 2 * a + 25
        g2 = MZIGeometry(30.0, 2 * a + 30, a, a + 0.2, 55.0, 5.0, y2, y2)
        beam = gaussian_waist_beam(self.grid, 0.0, 0.0, 60.0)
        res = solve_cascade(beam, [g1, g2], lambda x: Splitter(self.grid, x, r=self.r, t=self.t))
        c = port_amplitudes(res, self.grid, g2, 60.0)
        m = cascade_model([g1, g2], self.r, self.t, self.grid, 60.0, True)
        self.assertLess(max(abs(abs(c[0]) ** 2 - abs(m[0]) ** 2), abs(abs(c[1]) ** 2 - abs(m[1]) ** 2)), 4e-4)


if __name__ == "__main__":
    unittest.main()
