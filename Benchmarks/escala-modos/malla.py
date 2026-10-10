"""Malla de Clements de N modos con capas de acopladores 2x2 (P2-10).

Representacion compacta: N capas; la capa l actua sobre los pares (j, j+1) con
j = l%2, l%2+2, ...  Para N par hay N(N-1)/2 interferometros Mach-Zehnder,
cada uno con dos fases (theta interna, phi externa).

MZI: T(theta, phi) = B diag(e^{i theta}, 1) B diag(e^{i phi}, 1),
con B = (1/sqrt 2) [[1, i], [i, 1]].

Se ofrecen dos rutas independientes:
  * apply_layers: aplicacion por capas, coste O(N^2) por entrada.
  * dense_matrix: matriz densa N x N construida embebiendo cada elemento 2x2
    y multiplicando las matrices (referencia de la verificacion V).
Solo numpy. Sin GPU.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

_B = np.array([[1, 1j], [1j, 1]], dtype=complex) / np.sqrt(2.0)


class Mesh:
    """Geometria de la malla: numero de pares por capa y desplazamientos."""

    def __init__(self, n: int):
        if n < 2:
            raise ValueError("n >= 2")
        self.n = n
        self.off = [l % 2 for l in range(n)]
        self.cnt = [(n - o) // 2 for o in self.off]
        self.start = np.concatenate([[0], np.cumsum(self.cnt)]).astype(int)
        self.n_mzi = int(self.start[-1])  # interferometros
        self.n_params = 2 * self.n_mzi  # dos fases por interferometro

    def split(self, p: np.ndarray):
        """p = [theta (n_mzi), phi (n_mzi)] -> listas por capa."""
        th = p[: self.n_mzi]
        ph = p[self.n_mzi:]
        return ([th[self.start[l]:self.start[l + 1]] for l in range(self.n)],
                [ph[self.start[l]:self.start[l + 1]] for l in range(self.n)])


def mzi_elements(theta: np.ndarray, phi: np.ndarray):
    """Elementos (t00, t01, t10, t11) del MZI, vectorizado."""
    d = np.exp(1j * np.asarray(theta))
    e = np.exp(1j * np.asarray(phi))
    m00 = 0.5 * (d - 1.0)
    m01 = 0.5j * (d + 1.0)
    m10 = m01
    m11 = 0.5 * (1.0 - d)
    return m00 * e, m01, m10 * e, m11


def mzi_derivatives(theta, phi):
    """Derivadas de los elementos respecto a theta y a phi."""
    d = np.exp(1j * np.asarray(theta))
    e = np.exp(1j * np.asarray(phi))
    dm00 = 0.5j * d
    dm01 = -0.5 * d
    dm10 = dm01
    dm11 = -0.5j * d
    m00, m01, m10, m11 = mzi_elements(theta, phi)
    d_th = (dm00 * e, dm01, dm10 * e, dm11)
    d_ph = (1j * m00, 0.0 * m01, 1j * m10, 0.0 * m11)
    return d_th, d_ph


def layer_coeffs(mesh: Mesh, p: np.ndarray):
    """Coeficientes por capa (lista de tuplas t00,t01,t10,t11), forma (m,1)."""
    ths, phs = mesh.split(p)
    out = []
    for l in range(mesh.n):
        t = mzi_elements(ths[l], phs[l])
        out.append(tuple(c[:, None] for c in t))
    return out


def apply_layers(mesh: Mesh, coeffs, x: np.ndarray) -> np.ndarray:
    """Aplica la malla por capas. x: (n,) o (n, B) (modos en el eje 0)."""
    squeeze = x.ndim == 1
    a = x.astype(complex)[:, None] if squeeze else x.astype(complex)
    for l in range(mesh.n):
        o, m = mesh.off[l], mesh.cnt[l]
        if m == 0:
            continue
        t00, t01, t10, t11 = coeffs[l]
        a0 = a[o:o + 2 * m:2]
        a1 = a[o + 1:o + 2 * m:2]
        n0 = t00 * a0 + t01 * a1
        n1 = t10 * a0 + t11 * a1
        a = a.copy()
        a[o:o + 2 * m:2] = n0
        a[o + 1:o + 2 * m:2] = n1
    return a[:, 0] if squeeze else a


def dense_matrix(mesh: Mesh, p: np.ndarray) -> np.ndarray:
    """Matriz de transferencia densa a partir de los elementos (referencia)."""
    n = mesh.n
    ths, phs = mesh.split(p)
    U = np.eye(n, dtype=complex)
    for l in range(n):
        o = mesh.off[l]
        L = np.eye(n, dtype=complex)
        for k in range(mesh.cnt[l]):
            j = o + 2 * k
            d = np.exp(1j * ths[l][k])
            e = np.exp(1j * phs[l][k])
            M = _B @ np.diag([d, 1.0]) @ _B @ np.diag([e, 1.0])
            L[j:j + 2, j:j + 2] = M
        U = L @ U
    return U


def verify(ns=(2, 3, 4, 5, 6, 7, 8), seeds=(0, 1, 2, 3, 4)):
    rows = []
    worst = 0.0
    worst_unit = 0.0
    for n in ns:
        mesh = Mesh(n)
        for s in seeds:
            rng = np.random.default_rng(1000 * n + s)
            p = rng.uniform(0, 2 * np.pi, mesh.n_params)
            U = dense_matrix(mesh, p)
            X = rng.normal(size=(n, 5)) + 1j * rng.normal(size=(n, 5))
            y_l = apply_layers(mesh, layer_coeffs(mesh, p), X)
            diff = float(np.max(np.abs(y_l - U @ X)))
            unit = float(np.max(np.abs(U.conj().T @ U - np.eye(n))))
            worst = max(worst, diff)
            worst_unit = max(worst_unit, unit)
            rows.append({"n": n, "seed": s, "n_mzi": mesh.n_mzi,
                         "max_abs_diff": diff, "unitarity_err": unit})
    count_ok = all(Mesh(n).n_mzi == n * (n - 1) // 2 for n in (2, 4, 8, 16, 32, 64))
    m64 = Mesh(64)
    return {
        "criterio": "diferencia maxima < 1e-12 (N <= 8)",
        "max_abs_diff": worst,
        "max_unitarity_err": worst_unit,
        "pasa": bool(worst < 1e-12),
        "n_mzi_correcto_N_par": bool(count_ok),
        "n64": {"mzi": m64.n_mzi, "fases": m64.n_params},
        "casos": rows,
    }


if __name__ == "__main__":
    res = verify()
    out = Path(__file__).parent / "resultados"
    out.mkdir(exist_ok=True)
    (out / "verificacion.json").write_text(json.dumps(res, indent=1), encoding="utf-8", newline="\n")
    print("max_abs_diff", res["max_abs_diff"], "unit", res["max_unitarity_err"],
          "pasa", res["pasa"], "mzi64", res["n64"])
    sys.exit(0 if res["pasa"] else 1)
