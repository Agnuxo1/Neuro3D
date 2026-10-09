"""OPT-007 exploratory experiment (Claude). CPU by default; --device cuda via the GPU queue.

Tasks (fixed stratified 70/30 split, 5 seeds):
  iris   : 4 features  -> N=4 mesh, 3 classes
  digits : 8x8 digits averaged to 4x4 = 16 features -> N=16 mesh, 10 classes
Models:
  mesh          geometry-only optical mesh (delay-line displacements) + 1 gain
  controls      shuffled labels | random geometry (untrained) | frozen geometry (gain only)
  baselines     multinomial logistic regression (sklearn) | MLP with ~same #params (torch)
Writes results JSON next to this file. Exploratory, not preregistered.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import numpy as np
import torch
from sklearn.datasets import load_digits, load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

from mesh import OpticalMesh, encode


def load(task):
    if task == "iris":
        d = load_iris(); X, y = d.data, d.target
    else:
        d = load_digits(); X = d.images.reshape(-1, 4, 2, 4, 2).mean(axis=(2, 4)).reshape(-1, 16); y = d.target
    return X.astype(np.float64), y


def scale_train_only(Xtr, Xva):
    """Min-max fitted on the TRAIN split only (no validation leakage); val clipped to [0,1]."""
    lo, hi = Xtr.min(0), Xtr.max(0)
    f = lambda Z: np.clip((Z - lo) / (hi - lo + 1e-12), 0.0, 1.0)  # noqa: E731
    return f(Xtr), f(Xva)


def train_mesh(Xtr, ytr, n, c, seed, device, epochs, freeze_geometry=False, shuffle=False):
    torch.manual_seed(seed)
    m = OpticalMesh(n, c, seed=seed).to(device)
    xt = encode(torch.tensor(Xtr, device=device))
    yt = torch.tensor(np.random.default_rng(seed).permutation(ytr) if shuffle else ytr, device=device)
    geo = [] if freeze_geometry else [m.d_int, m.d_ext, m.d_out]
    # Adam step of 4e-4 BU = 0.05 rad of phase (2k*d); the gain has its own scale
    groups = [{"params": [m.gain], "lr": 0.05}] + ([{"params": geo, "lr": 4e-4}] if geo else [])
    opt = torch.optim.Adam(groups)
    for _ in range(epochs):
        opt.zero_grad()
        loss = torch.nn.functional.cross_entropy(m(xt), yt)
        loss.backward(); opt.step()
    return m


def acc_mesh(m, X, y, device):
    with torch.no_grad():
        p = m(encode(torch.tensor(X, device=device))).argmax(1).cpu().numpy()
    return float((p == y).mean())


class MLP(torch.nn.Module):
    def __init__(self, n, c, h):
        super().__init__(); self.a = torch.nn.Linear(n, h); self.b = torch.nn.Linear(h, c)
    def forward(self, x): return self.b(torch.relu(self.a(x)))


def train_mlp(Xtr, ytr, Xva, yva, n, c, h, seed, epochs):
    torch.manual_seed(seed)
    m = MLP(n, c, h).double(); opt = torch.optim.Adam(m.parameters(), lr=0.01)
    xt, yt = torch.tensor(Xtr), torch.tensor(ytr)
    for _ in range(epochs):
        opt.zero_grad(); torch.nn.functional.cross_entropy(m(xt), yt).backward(); opt.step()
    with torch.no_grad():
        return float((m(torch.tensor(Xva)).argmax(1).numpy() == yva).mean()), sum(p.numel() for p in m.parameters())


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--device", default="cpu"); ap.add_argument("--epochs", type=int, default=1500)
    ap.add_argument("--seeds", type=int, default=5); a = ap.parse_args()
    out = {"device": a.device, "epochs": a.epochs, "tasks": {}}
    for task in ("iris", "digits"):
        X, y = load(task); n, c = X.shape[1], int(y.max() + 1)
        rows = {k: [] for k in ("mesh", "shuffled", "random_geometry", "frozen_geometry", "logreg", "mlp")}
        t_train = []
        for s in range(a.seeds):
            Xtr, Xva, ytr, yva = train_test_split(X, y, test_size=0.3, stratify=y, random_state=s)
            Xtr, Xva = scale_train_only(Xtr, Xva)
            t0 = time.perf_counter(); m = train_mesh(Xtr, ytr, n, c, s, a.device, a.epochs); t_train.append(time.perf_counter() - t0)
            rows["mesh"].append(acc_mesh(m, Xva, yva, a.device))
            rows["shuffled"].append(acc_mesh(train_mesh(Xtr, ytr, n, c, s, a.device, a.epochs, shuffle=True), Xva, yva, a.device))
            rows["random_geometry"].append(acc_mesh(OpticalMesh(n, c, seed=s).to(a.device), Xva, yva, a.device))
            rows["frozen_geometry"].append(acc_mesh(train_mesh(Xtr, ytr, n, c, s, a.device, a.epochs, freeze_geometry=True), Xva, yva, a.device))
            rows["logreg"].append(float(LogisticRegression(max_iter=5000).fit(Xtr, ytr).score(Xva, yva)))
            geo = m.geometry_parameters()
            h = max(1, round((geo - c) / (n + 1 + c)))  # MLP hidden size giving ~same #params
            acc, mlp_params = train_mlp(Xtr, ytr, Xva, yva, n, c, h, s, a.epochs); rows["mlp"].append(acc)
        # inference cost (digital simulation) vs matrix baseline
        cells = n * (n - 1) // 2
        with torch.no_grad():
            xb = encode(torch.rand(4096, n, dtype=torch.float64, device=a.device)); m(xb)
            if a.device == "cuda": torch.cuda.synchronize()
            t0 = time.perf_counter()
            for _ in range(20): m(xb)
            if a.device == "cuda": torch.cuda.synchronize()
            lat = (time.perf_counter() - t0) / 20 / 4096
        out["tasks"][task] = {
            "n_modes": n, "classes": c,
            "val_acc": {k: {"mean": float(np.mean(v)), "sd": float(np.std(v)), "runs": v} for k, v in rows.items()},
            "geometry_params": m.geometry_parameters(), "mlp_params": mlp_params, "logreg_params": n * c + c,
            "optical_cells": cells, "delay_lines": 2 * cells + n,
            "digital_sim_real_flops_per_sample": cells * 2 * 40 + n * 8,  # ~2 BS (4 cmul+adds each) + phases, rough
            "logreg_macs_per_sample": n * c,
            "train_seconds_mean": float(np.mean(t_train)), "sim_latency_s_per_sample": lat,
        }
        print(task, json.dumps({k: round(v["mean"], 4) for k, v in out["tasks"][task]["val_acc"].items()}))
    Path(__file__).with_name(f"results_{a.device}_noleak.json").write_text(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
