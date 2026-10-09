"""Pruebas rapidas P1-8 (numpy, sin Blender ni bpy). Ejecutar: python -m pytest test_limite_lectura.py"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Benchmarks" / "limite-lectura"))
import generadores as g  # noqa: E402
import modelos as m  # noqa: E402


def test_rango_un_detector_es_2():
    rng = np.random.default_rng(0)
    for _ in range(20):
        U = rng.standard_normal((3, 5)); V = rng.standard_normal((3, 5))
        for M in m.optical_Q(U, V):
            assert m.num_rank(M) == 2


def test_frontera_dos_detectores_rango_max_4():
    rng = np.random.default_rng(1)
    for _ in range(20):
        Q = m.optical_Q(rng.standard_normal((3, 5)), rng.standard_normal((3, 5)))
        assert max(m.pair_ranks(Q).values()) <= 4
    # forma cuadratica == |a^T x|^2
    a = rng.standard_normal(5) + 1j * rng.standard_normal(5)
    x = rng.standard_normal(5)
    M = m.optical_Q(a.real[None], a.imag[None])[0]
    assert np.isclose(x @ M @ x, abs(a @ x) ** 2)


def test_qda_frontera_cuadratica_exacta_juguete():
    # dos clases con covarianzas distintas y gran muestra: QDA debe recuperar la frontera teorica
    rng = np.random.default_rng(2)
    n = 200000
    m0, m1 = np.zeros(4), np.ones(4)
    S0, S1 = np.eye(4), 2.0 * np.eye(4)
    X = np.vstack([rng.multivariate_normal(m0, S0, n), rng.multivariate_normal(m1, S1, n)])
    y = np.r_[np.zeros(n, int), np.ones(n, int)]
    Qs = m.qda_fit(X, y, K=2)
    # frontera teorica: log N(x;m0,S0) = log N(x;m1,S1)
    def theo(x):
        d0 = -0.5 * (x - m0) @ np.linalg.inv(S0) @ (x - m0) - 0.5 * np.linalg.slogdet(S0)[1]
        d1 = -0.5 * (x - m1) @ np.linalg.inv(S1) @ (x - m1) - 0.5 * np.linalg.slogdet(S1)[1]
        return d0 - d1
    xt_pts = rng.standard_normal((300, 4)) * 1.5
    est = m.quad_scores(Qs, xt_pts)
    est = est[:, 0] - est[:, 1]
    ref = np.array([theo(x) for x in xt_pts])
    assert np.mean(np.sign(est) == np.sign(ref)) > 0.99
    assert np.max(np.abs(est - ref)) < 0.1


def test_gradientes_vs_diferencias_finitas():
    r = m.check_gradient()
    assert r["T=1"] < 1e-5 and r["T=0.05"] < 1e-5


def test_generadores_deterministas_y_tamano():
    a, b = g.make_task(3), g.make_task(3)
    assert np.array_equal(a["Xtr"], b["Xtr"])
    assert len(a["ytr"]) == 400 and len(a["yte"]) == 200
    assert np.bincount(a["ytr"]).tolist() == [133, 133, 134]
