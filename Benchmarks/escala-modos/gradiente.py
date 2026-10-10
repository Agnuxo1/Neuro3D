"""Perdida softmax sobre P_c/T y su gradiente analitico respecto a las fases (P2-10).

Perdida: media de la entropia cruzada con logits P_c / T, P_c = |y_c|^2,
y = U x, detectores en los primeros K modos de salida.
Retropropagacion exacta por capas (calculo de Wirtinger); sin autograd.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

from malla import Mesh, mzi_derivatives, mzi_elements


def loss_and_grad_ref(mesh: Mesh, p: np.ndarray, X: np.ndarray, y: np.ndarray,
                  K: int = 10, T: float = 0.05, want_grad: bool = True):
    """X: (B, n) real; y: (B,) etiquetas en [0, K). Devuelve (perdida, grad|None)."""
    n, B = mesh.n, X.shape[0]
    ths, phs = mesh.split(p)
    coefs = [mzi_elements(ths[l], phs[l]) for l in range(n)]
    a = X.T.astype(complex)  # (n, B)
    acts = [a] if want_grad else None
    for l in range(n):
        o, m = mesh.off[l], mesh.cnt[l]
        if m:
            t00, t01, t10, t11 = (c[:, None] for c in coefs[l])
            a0, a1 = a[o:o + 2 * m:2], a[o + 1:o + 2 * m:2]
            nxt = a.copy()
            nxt[o:o + 2 * m:2] = t00 * a0 + t01 * a1
            nxt[o + 1:o + 2 * m:2] = t10 * a0 + t11 * a1
            a = nxt
        if want_grad:
            acts.append(a)
    yo = a[:K]  # (K, B)
    P = (yo.real ** 2 + yo.imag ** 2)
    z = P / T
    zmax = z.max(axis=0, keepdims=True)
    lse = zmax[0] + np.log(np.exp(z - zmax).sum(axis=0))
    idx = np.arange(B)
    loss = float(np.mean(lse - z[y, idx]))
    if not want_grad:
        return loss, None
    S = np.exp(z - lse[None, :])
    S[y, idx] -= 1.0  # dL/dz * B
    dP = S / (T * B)  # (K, B)
    g = np.zeros((n, B), dtype=complex)
    g[:K] = dP * yo  # dL/d conj(y)  (Wirtinger)
    gth = np.zeros(mesh.n_mzi)
    gph = np.zeros(mesh.n_mzi)
    for l in range(n - 1, -1, -1):
        o, m = mesh.off[l], mesh.cnt[l]
        if not m:
            continue
        ain = acts[l]
        a0, a1 = ain[o:o + 2 * m:2], ain[o + 1:o + 2 * m:2]
        g0, g1 = g[o:o + 2 * m:2], g[o + 1:o + 2 * m:2]
        d_th, d_ph = mzi_derivatives(ths[l], phs[l])
        for dT, out in ((d_th, gth), (d_ph, gph)):
            d00, d01, d10, d11 = (c[:, None] for c in dT)
            dy0 = d00 * a0 + d01 * a1
            dy1 = d10 * a0 + d11 * a1
            val = (g0.conj() * dy0 + g1.conj() * dy1).sum(axis=1)
            out[mesh.start[l]:mesh.start[l + 1]] = 2.0 * val.real
        t00, t01, t10, t11 = (c[:, None] for c in coefs[l])
        ng = g.copy()
        ng[o:o + 2 * m:2] = t00.conj() * g0 + t10.conj() * g1
        ng[o + 1:o + 2 * m:2] = t01.conj() * g0 + t11.conj() * g1
        g = ng
    return loss, np.concatenate([gth, gph])


_BUF = {}


def _buffers(n, B):
    key = (n, B)
    if key not in _BUF:
        _BUF.clear()
        _BUF[key] = (np.empty((n + 1, n, B), dtype=complex), np.empty((n, B), dtype=complex),
                     np.empty((n, B), dtype=complex), np.empty((n // 2 + 1, B), dtype=complex),
                     np.empty((n // 2 + 1, B), dtype=complex), np.empty((n // 2 + 1, B), dtype=complex))
    return _BUF[key]


def loss_and_grad(mesh: Mesh, p: np.ndarray, X: np.ndarray, y: np.ndarray,
                  K: int = 10, T: float = 0.05, want_grad: bool = True):
    """Version rapida (buffers preasignados, formulas reducidas). Mismo resultado que _ref.

    Con h = dL/dy (derivada de Wirtinger respecto a y):
      h_in = T^T h_out;  dL/dphi = -2 Im sum(a0 * h_in0);
      dL/dtheta = Re( e^{i theta} * sum[ h0 (i u0 - u1) - h1 (u0 + i u1) ] ),  u = D(phi) a.
    """
    n, B = mesh.n, X.shape[0]
    ths, phs = mesh.split(p)
    acts, h, h2, tA, tB, tC = _buffers(n, B)
    acts[0] = X.T
    coefs = []
    for l in range(n):
        o, m = mesh.off[l], mesh.cnt[l]
        src, dst = acts[l], acts[l + 1]
        if o == 1:
            dst[0] = src[0]
        if (n - o) % 2 == 1:
            dst[n - 1] = src[n - 1]
        if m:
            t00, t01, t10, t11 = (c[:, None] for c in mzi_elements(ths[l], phs[l]))
            coefs.append((t00, t01, t10, t11))
            a0, a1 = src[o:o + 2 * m:2], src[o + 1:o + 2 * m:2]
            d0, d1 = dst[o:o + 2 * m:2], dst[o + 1:o + 2 * m:2]
            np.multiply(t00, a0, out=d0)
            np.multiply(t01, a1, out=tA[:m])
            d0 += tA[:m]
            np.multiply(t10, a0, out=d1)
            np.multiply(t11, a1, out=tA[:m])
            d1 += tA[:m]
        else:
            coefs.append(None)
    yo = acts[n][:K]
    P = yo.real ** 2 + yo.imag ** 2
    z = P / T
    zmax = z.max(axis=0, keepdims=True)
    lse = zmax[0] + np.log(np.exp(z - zmax).sum(axis=0))
    idx = np.arange(B)
    loss = float(np.mean(lse - z[y, idx]))
    if not want_grad:
        return loss, None
    S = np.exp(z - lse[None, :])
    S[y, idx] -= 1.0
    h[:] = 0.0
    h[:K] = (S / (T * B)) * yo.conj()
    gth = np.zeros(mesh.n_mzi)
    gph = np.zeros(mesh.n_mzi)
    for l in range(n - 1, -1, -1):
        o, m = mesh.off[l], mesh.cnt[l]
        if not m:
            continue
        t00, t01, t10, t11 = coefs[l]
        a0, a1 = acts[l][o:o + 2 * m:2], acts[l][o + 1:o + 2 * m:2]
        h0, h1 = h[o:o + 2 * m:2], h[o + 1:o + 2 * m:2]
        e = np.exp(1j * phs[l])[:, None]
        dth = np.exp(1j * ths[l])
        u0 = np.multiply(e, a0, out=tB[:m])
        # Q = -(u0 + i u1);  P = i u0 - u1
        np.multiply(a1, 1j, out=tC[:m])
        tC[:m] += u0
        np.negative(tC[:m], out=tC[:m])  # Q
        np.multiply(u0, 1j, out=tA[:m])
        tA[:m] -= a1  # P
        Ssum = np.einsum('ij,ij->i', h0, tA[:m]) + np.einsum('ij,ij->i', h1, tC[:m])
        gth[mesh.start[l]:mesh.start[l + 1]] = (dth * Ssum).real
        # retropropagacion h_in = T^T h
        n0, n1 = h2[o:o + 2 * m:2], h2[o + 1:o + 2 * m:2]
        np.multiply(t00, h0, out=n0)
        np.multiply(t10, h1, out=tA[:m])
        n0 += tA[:m]
        np.multiply(t01, h0, out=n1)
        np.multiply(t11, h1, out=tA[:m])
        n1 += tA[:m]
        gph[mesh.start[l]:mesh.start[l + 1]] = -2.0 * np.einsum('ij,ij->i', a0, n0).imag
        if o == 1:
            h2[0] = h[0]
        if (n - o) % 2 == 1:
            h2[n - 1] = h[n - 1]
        h, h2 = h2, h
    return loss, np.concatenate([gth, gph])


def finite_diff(mesh, p, X, y, K, T, idxs, h=1e-6):
    out = np.zeros(len(idxs))
    for i, j in enumerate(idxs):
        pp, pm = p.copy(), p.copy()
        pp[j] += h
        pm[j] -= h
        out[i] = (loss_and_grad(mesh, pp, X, y, K, T, False)[0]
                  - loss_and_grad(mesh, pm, X, y, K, T, False)[0]) / (2 * h)
    return out


def check(n: int, K: int, B: int = 12, T: float = 0.05, seed: int = 7, subset=None):
    rng = np.random.default_rng(seed + n)
    mesh = Mesh(n)
    p = rng.uniform(0, 2 * np.pi, mesh.n_params)
    X = rng.uniform(size=(B, n))
    X /= np.linalg.norm(X, axis=1, keepdims=True)
    y = rng.integers(0, K, B)
    _, g = loss_and_grad(mesh, p, X, y, K, T)
    idxs = np.arange(mesh.n_params) if subset is None else rng.choice(mesh.n_params, subset, replace=False)
    fd = finite_diff(mesh, p, X, y, K, T, idxs)
    ga = g[idxs]
    rel = float(np.linalg.norm(ga - fd) / np.linalg.norm(fd))
    ref = loss_and_grad_ref(mesh, p, X, y, K, T)[1]
    return {"n": n, "K": K, "n_params_probados": int(len(idxs)),
            "dif_max_rapida_vs_referencia": float(np.max(np.abs(g - ref))),
            "error_relativo_norma": rel,
            "max_abs_diff": float(np.max(np.abs(ga - fd))), "norma_grad": float(np.linalg.norm(fd))}


if __name__ == "__main__":
    res = {"criterio": "error relativo < 1e-6 en N=8",
           "N8": check(8, 8), "N8_K4": check(8, 4), "N4": check(4, 4),
           "N64_subconjunto": check(64, 10, B=6, subset=60)}
    res["pasa"] = bool(res["N8"]["error_relativo_norma"] < 1e-6
                       and res["N8_K4"]["error_relativo_norma"] < 1e-6)
    out = Path(__file__).parent / "resultados"
    out.mkdir(exist_ok=True)
    (out / "verificacion_gradiente.json").write_text(json.dumps(res, indent=1), encoding="utf-8", newline="\n")
    print(json.dumps({k: (v if not isinstance(v, dict) else v["error_relativo_norma"]) for k, v in res.items()}))
    sys.exit(0 if res["pasa"] else 1)
