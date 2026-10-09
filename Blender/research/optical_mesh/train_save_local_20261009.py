"""Train the digits mesh (seed 0, CPU) and save geometry + held-out split for the Blender scene.
Also provides a numpy forward (no torch) used inside Blender, checked against torch here."""

import json
from pathlib import Path

import numpy as np
import torch
from sklearn.model_selection import train_test_split

from mesh import K, clements_pairs, encode
from run_exp import load, scale_train_only, train_mesh

HERE = Path(__file__).parent


def numpy_forward(amp, d_int, d_ext, d_out, n):
    """Same optics as mesh.OpticalMesh.fields, in numpy (runs inside Blender)."""
    e = amp.astype(np.complex128).copy()
    s2 = 1 / np.sqrt(2)
    idx = 0
    for col in clements_pairs(n):
        a = np.array([p[0] for p in col]); b = np.array([p[1] for p in col]); nc = len(col)
        th = 2 * K * d_int[idx: idx + nc]; ph = 2 * K * d_ext[idx: idx + nc]; idx += nc
        x, y = e[:, a] * np.exp(1j * ph), e[:, b]
        u, v = s2 * (x + 1j * y), s2 * (1j * x + y)
        u = u * np.exp(1j * th)
        e[:, a], e[:, b] = s2 * (u + 1j * v), s2 * (1j * u + v)
    return np.abs(e * np.exp(1j * 2 * K * d_out)) ** 2


if __name__ == "__main__":
    X, y = load("digits")
    Xtr, Xva, ytr, yva = train_test_split(X, y, test_size=0.3, stratify=y, random_state=0)
    Xtr, Xva = scale_train_only(Xtr, Xva)
    m = train_mesh(Xtr, ytr, 16, 10, 0, "cpu", 1500)
    d = {k: getattr(m, k).detach().numpy().tolist() for k in ("d_int", "d_ext", "d_out")}
    amp_va = encode(torch.tensor(Xva)).numpy()
    p_np = numpy_forward(amp_va, *(np.array(d[k]) for k in ("d_int", "d_ext", "d_out")), 16)
    with torch.no_grad():
        p_t = m.powers(torch.tensor(amp_va)).numpy()
    acc = float((p_np[:, :10].argmax(1) == yva).mean())
    print("numpy vs torch max diff:", np.abs(p_np - p_t).max(), " val acc:", acc)
    (HERE / "digits_mesh_seed0.json").write_text(json.dumps({
        **d, "gain": float(m.gain), "n": 16, "classes": 10, "lambda": 0.1, "val_acc": acc,
        "Xva": Xva.tolist(), "yva": yva.tolist()}))
