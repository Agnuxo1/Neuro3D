"""Pruebas rapidas de la validacion de onda P1-7 (FDTD, Enmiendas 1 y 2). Solo CPU, sin Blender ni bpy.
Ejecutar: python test_validacion_onda.py   (o pytest)."""
import os
import sys

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "Benchmarks", "validacion-onda"))
sys.path.insert(0, RAIZ)
os.chdir(RAIZ)

import numpy as np  # noqa: E402

import calibracion as cal  # noqa: E402
import calibracion_fdtd as cf  # noqa: E402
import mzi  # noqa: E402
import mzi_fdtd as mf  # noqa: E402
import test_pml_vacio_fdtd as tp  # noqa: E402


def test_dominio_vacio_fdtd():
    for ang, lx, ly in ((45.0, 22.0, 50.0), (0.0, 20.0, 24.0)):
        r = tp.reflexion_fdtd(ppl=16, w=3.0, ang=ang, lx=lx, ly=ly, pml=2.0, periodos=50, ventana=8)
        assert r["reflexion_potencia"] < 1e-3, r


def test_matriz_transferencia_1d_45():
    n = cal.indice_nominal(cal.D_NOMINAL, 45.0)
    r, t = cal.rt_1d(n, cal.D_NOMINAL, theta_deg=45.0)
    assert abs(abs(r) ** 2 - 0.5) < 1e-12 and abs(abs(t) ** 2 - 0.5) < 1e-12
    assert abs(abs(r) ** 2 + abs(t) ** 2 - 1.0) < 1e-12


def test_calibracion_fdtd_45_lambda16():
    # n ajustado en calibracion_fdtd_45.json (ppl=16)
    res = cf.rt_fdtd(16, 2.426975, 4, periodos=60)
    assert abs(abs(res["r"]) ** 2 - 0.5) < cf.TOL
    assert abs(abs(res["t"]) ** 2 - 0.5) < cf.TOL
    assert abs(abs(res["r"]) ** 2 + abs(res["t"]) ** 2 - 1.0) < 2e-3      # sin perdidas


def test_modelo_r1_t0_geometria_mzi():
    g = mf.geometria(16, 0, 2.43)
    ky0 = mf.f.ky_diagonal(16, mf.f.pasos_por_periodo(16))
    m = mf.modelo(g, 1.0, 0.0, ky0)
    assert m["P1"] < 1e-12 and abs(m["P2"] - 1.0) < 1e-3   # el modo usa el ky de la malla FDTD (0,04 % del ideal)


def test_modelo_de_caminos_escalar():
    dl = np.linspace(0, 1, 21)
    p1, p2 = mzi.modelo_caminos(1.0, 0.0, dl)          # r=1, t=0: todo por el puerto (-1,1)
    assert np.allclose(p1, 0) and np.allclose(p2, 1)
    r, t = 1 / np.sqrt(2), 1j / np.sqrt(2)
    p1, p2 = mzi.modelo_caminos(r, t, dl)
    assert np.allclose(p1 + p2, 1.0) and abs(p1.max() - 1) < 1e-12 and abs(p1.min()) < 1e-12


if __name__ == "__main__":
    for nombre, f in list(globals().items()):
        if nombre.startswith("test_") and callable(f):
            f()
            print("OK", nombre)
