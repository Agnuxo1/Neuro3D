"""Portable successor to the pinned P1-7 regression; importing never chdirs.

The pinned original remains unchanged for historical reproduction. Solver
modules are loaded only when a test explicitly runs. These checks do not
confirm the exploratory diffraction correction for the full device.
"""
import importlib
from pathlib import Path
import sys
import unittest

WAVE = Path(__file__).resolve().parents[2] / "Benchmarks/validacion-onda"


def wave_module(name):
    old = list(sys.path)
    try:
        sys.path.insert(0, str(WAVE))
        return importlib.import_module(name)
    finally:
        sys.path[:] = old


class PortableWaveTests(unittest.TestCase):
    def test_import_preserves_cwd_and_search_path(self):
        cwd, paths = Path.cwd(), list(sys.path)
        wave_module("mzi_fdtd")
        self.assertEqual(Path.cwd(), cwd)
        self.assertEqual(sys.path, paths)

    def test_transfer_matrix_45_degrees(self):
        cal = wave_module("calibracion")
        n = cal.indice_nominal(cal.D_NOMINAL, 45.0)
        r, t = cal.rt_1d(n, cal.D_NOMINAL, theta_deg=45.0)
        self.assertLess(abs(abs(r)**2-0.5), 1e-12)
        self.assertLess(abs(abs(t)**2-0.5), 1e-12)

    def test_represented_mzi_perfect_mirror(self):
        mf = wave_module("mzi_fdtd")
        result = mf.modelo(mf.geometria(16, 0, 2.43), 1.0, 0.0,
                           mf.f.ky_diagonal(16, mf.f.pasos_por_periodo(16)))
        self.assertLess(result["P1"], 1e-12)
        self.assertLess(abs(result["P2"]-1), 1e-3)

    def test_scalar_path_conservation(self):
        import numpy as np
        mzi = wave_module("mzi")
        p1, p2 = mzi.modelo_caminos(1/np.sqrt(2), 1j/np.sqrt(2), np.linspace(0, 1, 21))
        np.testing.assert_allclose(p1+p2, 1, atol=1e-12)

    def test_empty_domain_fdtd(self):
        tp = wave_module("test_pml_vacio_fdtd")
        for angle, lx, ly in ((45.0, 22.0, 50.0), (0.0, 20.0, 24.0)):
            result = tp.reflexion_fdtd(ppl=16, w=3.0, ang=angle, lx=lx, ly=ly,
                                      pml=2.0, periodos=50, ventana=8)
            self.assertLess(result["reflexion_potencia"], 1e-3)

    def test_calibration_fdtd_historical_index(self):
        cf = wave_module("calibracion_fdtd")
        result = cf.rt_fdtd(16, 2.426975, 4, periodos=60)
        self.assertLess(abs(abs(result["r"])**2-0.5), cf.TOL)
        self.assertLess(abs(abs(result["t"])**2-0.5), cf.TOL)


if __name__ == "__main__":
    unittest.main()
