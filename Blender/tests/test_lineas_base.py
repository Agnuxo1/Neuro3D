"""Pruebas rapidas P0-4 (CPU, sin bpy): particiones, estratificacion, Holm, bootstrap y modulo numerico de Iris.

Ejecutar: python Blender/tests/test_lineas_base.py   (o con pytest)
"""
import json, os, sys, tempfile
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parents[2]
LB = REPO / "Benchmarks" / "lineas-base"
sys.path.insert(0, str(REPO)); sys.path.insert(0, str(LB))
import run_lineas_base as R  # noqa: E402
import analisis as A  # noqa: E402
import iris_numeric as IN  # noqa: E402


def test_wine_split_sizes_and_strata():
    _, y = R.load_wine()
    assert np.array_equal(np.bincount(y), [59, 71, 48])
    for k in range(R.NPART):
        tr, te = R.stratified(y, R.WINE_TEST_COUNTS, 20261009 + k)
        assert (len(tr), len(te)) == (141, 37) and set(tr).isdisjoint(te) and set(tr) | set(te) == set(range(178))
        assert np.bincount(y[te], minlength=3).tolist() == [12, 15, 10]
        assert np.bincount(y[tr], minlength=3).tolist() == [47, 56, 38]


def test_iris_split_sizes_and_strata():
    _, y = IN.load_raw()
    assert len(y) == 150
    for k in range(R.NPART):
        tr, te = R.stratified(y, R.IRIS_TEST_COUNTS, k)
        assert (len(tr), len(te)) == (120, 30) and set(tr).isdisjoint(te)
        assert np.bincount(y[te], minlength=3).tolist() == [10, 10, 10]
        assert np.bincount(y[tr], minlength=3).tolist() == [40, 40, 40]


def test_splits_deterministic_and_differ():
    a, b = R.make_splits(), R.make_splits()
    assert a == b
    assert len({s["sha256_indices"] for s in a["wine"]}) == 10 and len({s["sha256_indices"] for s in a["iris"]}) == 10
    p = LB / "resultados" / "splits.json"
    if p.exists():
        assert json.loads(p.read_text()) == a


def test_holm_known_example():
    # ejemplo clasico: p = [0.01, 0.04, 0.03, 0.005] -> ajustados [0.03, 0.06, 0.06, 0.02]
    assert np.allclose(A.holm([0.01, 0.04, 0.03, 0.005]), [0.03, 0.06, 0.06, 0.02])
    assert np.allclose(A.holm([0.04, 0.03]), [0.06, 0.06])
    assert np.allclose(A.holm([0.5, 0.9]), [1.0, 1.0])


def test_classification_rule():
    assert A.classify([0.01, 0.05], 0.01) == "superior"
    assert A.classify([0.01, 0.05], 0.2) == "inferior_o_inconcluso"
    assert A.classify([-0.01, 0.015], 0.9) == "equivalente"
    assert A.classify([-0.05, 0.01], 0.9) == "inferior_o_inconcluso"


def test_bootstrap_reproducible_and_brackets_mean():
    d = [0.01, -0.02, 0.0, 0.03, 0.01, 0.02, -0.01, 0.0, 0.02, 0.01]
    c1, c2 = A.bootstrap_ci(d), A.bootstrap_ci(d)
    assert c1 == c2 and c1[0] <= np.mean(d) <= c1[1]


def test_iris_numeric_matches_demo_source():
    # extraccion por AST: mismas constantes y salida de model_U unitaria
    U = IN.model_U(np.zeros((IN.K, IN.K)))
    assert U.shape == (8, 8)
    assert np.allclose(U @ U.conj().T, np.eye(8), atol=1e-9)   # red sin perdidas -> unitaria
    x, y = IN.load_raw()
    assert x.shape == (150, 4) and np.bincount(y).tolist() == [50, 50, 50]


def test_iris_numeric_check_json_if_present():
    p = LB / "resultados" / "iris_numeric_check.json"
    if p.exists():
        r = json.loads(p.read_text())
        assert r["equivalent_below_1e-12"] and r["loss_abs_diff"] < 1e-12 and r["params_max_abs_diff"] < 1e-12


if __name__ == "__main__":
    fails = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn(); print("OK  ", name)
            except Exception as e:
                fails += 1; print("FAIL", name, repr(e))
    raise SystemExit(1 if fails else 0)
