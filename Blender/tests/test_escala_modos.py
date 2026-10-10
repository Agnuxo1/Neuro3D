"""Pruebas rapidas de P2-10 (escala-modos). Solo numpy/sklearn, sin Blender ni GPU.

Ejecutar: python -m unittest Blender/tests/test_escala_modos.py
"""
import sys
import unittest
from pathlib import Path

import numpy as np

_DIR = Path(__file__).resolve().parents[2] / "Benchmarks" / "escala-modos"
sys.path.insert(0, str(_DIR))

import datos  # noqa: E402
from gradiente import finite_diff, loss_and_grad, loss_and_grad_ref  # noqa: E402
from malla import Mesh, apply_layers, dense_matrix, layer_coeffs  # noqa: E402


class TestMalla(unittest.TestCase):
    def _check(self, n):
        mesh = Mesh(n)
        self.assertEqual(mesh.n_mzi, n * (n - 1) // 2)
        self.assertEqual(mesh.n_params, n * (n - 1))
        rng = np.random.default_rng(n)
        p = rng.uniform(0, 2 * np.pi, mesh.n_params)
        X = rng.normal(size=(n, 4)) + 1j * rng.normal(size=(n, 4))
        U = dense_matrix(mesh, p)
        self.assertLess(np.max(np.abs(U.conj().T @ U - np.eye(n))), 1e-12)
        y = apply_layers(mesh, layer_coeffs(mesh, p), X)
        self.assertLess(np.max(np.abs(y - U @ X)), 1e-12)

    def test_capas_vs_densa_n4(self):
        self._check(4)

    def test_capas_vs_densa_n8(self):
        self._check(8)

    def test_tamano_n64(self):
        mesh = Mesh(64)
        self.assertEqual((mesh.n_mzi, mesh.n_params), (2016, 4032))


class TestGradiente(unittest.TestCase):
    def test_gradiente_vs_diferencias_finitas_n4(self):
        n, K = 4, 4
        rng = np.random.default_rng(3)
        mesh = Mesh(n)
        p = rng.uniform(0, 2 * np.pi, mesh.n_params)
        X = rng.uniform(size=(9, n))
        X /= np.linalg.norm(X, axis=1, keepdims=True)
        y = rng.integers(0, K, 9)
        _, g = loss_and_grad(mesh, p, X, y, K, 0.05)
        _, gref = loss_and_grad_ref(mesh, p, X, y, K, 0.05)
        fd = finite_diff(mesh, p, X, y, K, 0.05, np.arange(mesh.n_params))
        self.assertLess(np.linalg.norm(g - fd) / np.linalg.norm(fd), 1e-6)
        self.assertLess(np.max(np.abs(g - gref)), 1e-12)


class TestDatos(unittest.TestCase):
    def test_particiones_estratificadas(self):
        X, y = datos.load()
        self.assertEqual(X.shape, (1797, 64))
        for k in (0, 1):
            tr, te = datos.split_indices(y, k)
            self.assertEqual((len(tr), len(te)), (1437, 360))
            self.assertEqual(len(set(tr) & set(te)), 0)
            for c in range(10):
                frac = np.mean(y == c)
                self.assertLessEqual(abs(np.sum(y[te] == c) - frac * 360), 1.0)
                self.assertLessEqual(abs(np.sum(y[tr] == c) - frac * 1437), 1.0)

    def test_codificacion_ajustada_con_entrenamiento(self):
        X, y = datos.load()
        tr, te = datos.split_indices(y, 0)
        Ztr, Zte = datos.encode(X[tr], X[te])
        np.testing.assert_allclose(np.linalg.norm(Ztr, axis=1), 1.0, atol=1e-12)
        np.testing.assert_allclose(np.linalg.norm(Zte, axis=1), 1.0, atol=1e-12)


if __name__ == "__main__":
    unittest.main()
