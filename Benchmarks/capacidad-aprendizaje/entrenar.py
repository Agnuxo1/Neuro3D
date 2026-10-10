"""Entrenamiento de F4: Adam (tasa 0,01, 2000 pasos), gradiente analitico, perdida softmax P_k/T."""
from __future__ import annotations

import time

import numpy as np

from familia import Mesh, loss_and_grad, predict

LR, STEPS, T_TEMP = 0.01, 2000, 0.05


def train(Ztr, ytr, n, K, seed):
    """Devuelve (fases, perdida final de entrenamiento, segundos de CPU)."""
    mesh = Mesh(n)
    p = np.random.default_rng(seed).uniform(0, 2 * np.pi, mesh.n_params)
    m, v = np.zeros_like(p), np.zeros_like(p)
    b1, b2, eps = 0.9, 0.999, 1e-8
    t0 = time.process_time()
    for t in range(1, STEPS + 1):
        _, g = loss_and_grad(mesh, p, Ztr, ytr, K, T_TEMP)
        m = b1 * m + (1 - b1) * g
        v = b2 * v + (1 - b2) * g * g
        p -= LR * (m / (1 - b1 ** t)) / (np.sqrt(v / (1 - b2 ** t)) + eps)
    cpu = time.process_time() - t0
    final, _ = loss_and_grad(mesh, p, Ztr, ytr, K, T_TEMP, want_grad=False)
    return p, float(final), cpu


def accuracy(mesh, p, Z, y, K):
    return float(np.mean(predict(mesh, p, Z, K) == y))
