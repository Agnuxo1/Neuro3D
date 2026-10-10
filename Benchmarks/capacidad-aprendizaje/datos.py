"""Datos, particiones y preprocesado de F4 (solo lectura de entradas existentes).

Iris y Wine: particiones de P0-4 (Benchmarks/lineas-base/resultados/splits.json).
Breast Cancer y Digits: StratifiedShuffleSplit 80/20, semillas 20261009+k, como en P1-5.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from sklearn.decomposition import PCA

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
IRIS_CSV = REPO / "Blender/demo_lattice_iris/iris.csv"
WINE = REPO / "Docs/data/uci-wine/wine.data"
SPLITS_P04 = REPO / "Benchmarks/lineas-base/resultados/splits.json"
SPLITS_P210 = REPO / "Benchmarks/escala-modos/resultados/splits.json"
SPECIES = ["setosa", "versicolor", "virginica"]
SEED0 = 20261009
NPART = 10
# conjunto -> (modos N de la malla, K detectores)
CONFIG = {"iris": (8, 3), "wine": (8, 3), "breast_cancer": (8, 2), "digits": (16, 10)}
NAMES = list(CONFIG)


def sha_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def sha_xy(x, y):
    return {"X": hashlib.sha256(np.ascontiguousarray(x, dtype=np.float64).tobytes()).hexdigest(),
            "y": hashlib.sha256(np.ascontiguousarray(y, dtype=np.int64).tobytes()).hexdigest(),
            "X_shape": list(x.shape), "y_shape": list(y.shape)}


def split_hash(tr, te):
    return hashlib.sha256(json.dumps({"train": tr, "test": te}).encode()).hexdigest()


def load_datasets():
    from sklearn.datasets import load_breast_cancer, load_digits
    rows = [l.strip().split(",") for l in IRIS_CSV.read_text(encoding="utf-8").splitlines()[1:]]
    xi = np.array([[float(v) for v in r[:4]] for r in rows])
    yi = np.array([SPECIES.index(r[4]) for r in rows])
    raw = np.loadtxt(WINE, delimiter=",")
    assert raw.shape == (178, 14)
    xw, yw = raw[:, 1:5], raw[:, 0].astype(np.int64) - 1   # 4 atributos como en P0-4
    bc, dg = load_breast_cancer(), load_digits()
    return {"iris": (xi, yi), "wine": (xw, yw),
            "breast_cancer": (np.asarray(bc.data, dtype=np.float64), np.asarray(bc.target, dtype=np.int64)),
            "digits": (np.asarray(dg.data, dtype=np.float64), np.asarray(dg.target, dtype=np.int64))}


def make_splits_new(x, y):
    from sklearn.model_selection import StratifiedShuffleSplit
    out = []
    for k in range(NPART):
        seed = SEED0 + k
        tr, te = next(StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=seed).split(x, y))
        tr, te = sorted(int(i) for i in tr), sorted(int(i) for i in te)
        out.append({"k": k, "seed": seed, "train": tr, "test": te, "sha256_indices": split_hash(tr, te)})
    return out


def get_splits(data):
    p04 = json.loads(SPLITS_P04.read_text())
    sp = {}
    for name in ("iris", "wine"):
        for s in p04[name]:
            assert split_hash(s["train"], s["test"]) == s["sha256_indices"], (name, s["k"])
        sp[name] = p04[name]
    for name in ("breast_cancer", "digits"):
        sp[name] = make_splits_new(*data[name])
    return sp


def compare_with_p210(sp):
    """Compara las particiones de Digits con las de escala-modos (si existe)."""
    if not SPLITS_P210.exists():
        return {"existe": False}
    d = json.loads(SPLITS_P210.read_text())
    res = []
    for s, o in zip(sp["digits"], d["splits"]):
        res.append(bool(s["train"] == o["train"] and s["test"] == o["test"]))
    return {"existe": True, "coinciden_por_particion": res, "coinciden_todas": all(res),
            "nota": "P2-10 usa train_test_split; F4 usa StratifiedShuffleSplit como P1-5"}


def unit_power(Z):
    nrm = np.linalg.norm(Z, axis=1, keepdims=True)
    return Z / np.where(nrm > 0, nrm, 1.0)


def minmax_fit(Xtr):
    lo, hi = Xtr.min(axis=0), Xtr.max(axis=0)
    return lo, np.where(hi - lo > 0, hi - lo, 1.0)


def encode(name, X, tr, te):
    """Devuelve (Ztr, Zte) a la entrada de la malla (potencia unitaria por muestra) y
    (Atr) las caracteristicas escaladas previas a la normalizacion (para referencia)."""
    N = CONFIG[name][0]
    Xtr, Xte = X[tr], X[te]
    lo, rng = minmax_fit(Xtr)
    A, B = (Xtr - lo) / rng, (Xte - lo) / rng
    if name in ("iris", "wine"):
        pad = lambda M: np.hstack([M, np.zeros((M.shape[0], N - M.shape[1]))])   # modos 4..7 a cero
        A, B = pad(A), pad(B)
    else:
        pca = PCA(n_components=N, random_state=0).fit(A)
        A, B = pca.transform(A), pca.transform(B)
    return unit_power(A), unit_power(B)
