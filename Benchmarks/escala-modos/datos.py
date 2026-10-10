"""Datos y particiones de P2-10: digits, 10 particiones estratificadas 80/20."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split

BASE_SEED = 20261009
N_SPLITS = 10
HERE = Path(__file__).parent


def load():
    d = load_digits()
    return d.data.astype(float), d.target.astype(int)


def split_indices(y, k):
    idx = np.arange(len(y))
    tr, te = train_test_split(idx, test_size=0.2, stratify=y, random_state=BASE_SEED + k)
    return np.sort(tr), np.sort(te)


def sha(idx):
    return hashlib.sha256(np.asarray(idx, dtype="<i8").tobytes()).hexdigest()


def write_splits(path=None):
    X, y = load()
    rec = []
    for k in range(N_SPLITS):
        tr, te = split_indices(y, k)
        rec.append({"k": k, "seed": BASE_SEED + k, "n_train": int(len(tr)), "n_test": int(len(te)),
                    "sha256_train": sha(tr), "sha256_test": sha(te),
                    "train": tr.tolist(), "test": te.tolist()})
    out = {"dataset": "sklearn.datasets.load_digits", "n": int(len(y)),
           "sha256_indices": "int64 little-endian, ordenados ascendentemente", "splits": rec}
    p = Path(path) if path else HERE / "resultados" / "splits.json"
    p.parent.mkdir(exist_ok=True)
    p.write_text(json.dumps(out), encoding="utf-8", newline="\n")
    return out


def minmax_fit(Xtr):
    lo, hi = Xtr.min(axis=0), Xtr.max(axis=0)
    rng = np.where(hi - lo > 0, hi - lo, 1.0)
    return lo, rng


def unit_power(Z):
    nrm = np.linalg.norm(Z, axis=1, keepdims=True)
    return Z / np.where(nrm > 0, nrm, 1.0)


def encode(Xtr, Xte):
    """Min-max (ajustado con entrenamiento) y norma unitaria. Devuelve (Ztr, Zte)."""
    lo, rng = minmax_fit(Xtr)
    return unit_power((Xtr - lo) / rng), unit_power((Xte - lo) / rng)


def encode_pca(Xtr, Xte, n_comp):
    """Min-max, PCA(n_comp) ajustada con entrenamiento, norma unitaria."""
    lo, rng = minmax_fit(Xtr)
    A, B = (Xtr - lo) / rng, (Xte - lo) / rng
    pca = PCA(n_components=n_comp, random_state=0).fit(A)
    return unit_power(pca.transform(A)), unit_power(pca.transform(B))
