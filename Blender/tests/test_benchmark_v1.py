"""P1-5: pruebas rapidas del benchmark v1 (solo CPU, sin bpy). Ejecutar: python -m unittest Blender.tests.test_benchmark_v1 (desde la raiz del repo)."""
import json
import sys
import unittest
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parents[2]
BV1 = REPO / "Benchmarks" / "benchmark-v1"
sys.path.insert(0, str(REPO)); sys.path.insert(0, str(BV1))
import multiclass_softmax as MS  # noqa: E402
import run_benchmark_v1 as R  # noqa: E402
from Blender.blender_lab.classifier_comparison_v1 import encode_real_features, fit_baseline  # noqa: E402

DATA = R.load_datasets()


class Partitions(unittest.TestCase):
    def test_sizes_and_stratification_new_datasets(self):
        for name, (ntr, nte) in (("breast_cancer", (455, 114)), ("digits", (1437, 360))):
            x, y = DATA[name]
            sp = R.make_splits_new(x, y)
            self.assertEqual(len(sp), 10)
            overall = np.bincount(y) / len(y)
            for s in sp:
                self.assertEqual((len(s["train"]), len(s["test"])), (ntr, nte))
                self.assertFalse(set(s["train"]) & set(s["test"]))
                self.assertEqual(sorted(s["train"] + s["test"]), list(range(len(y))))
                self.assertEqual(s["seed"], R.SEED0 + s["k"])
                # estratificacion: proporcion de cada clase en prueba a menos de 1 muestra de la esperada
                self.assertTrue(np.all(np.abs(np.bincount(y[s["test"]], minlength=len(overall)) - overall * nte) <= 1.0 + 1e-9))

    def test_p04_partitions_sizes_and_hashes(self):
        sp = R.get_splits(DATA)   # verifica internamente los SHA-256 de Iris y Wine contra splits.json
        for name, (ntr, nte) in (("iris", (120, 30)), ("wine", (141, 37))):
            y = DATA[name][1]
            self.assertEqual(len(sp[name]), 10)
            for s in sp[name]:
                self.assertEqual((len(s["train"]), len(s["test"])), (ntr, nte))
                self.assertEqual(R.split_hash(s["train"], s["test"]), s["sha256_indices"])
                self.assertEqual(np.bincount(y[s["test"]]).tolist(), [10, 10, 10] if name == "iris" else [12, 15, 10])

    def test_hashes_deterministic(self):
        for name in ("breast_cancer", "digits"):
            x, y = DATA[name]
            a = [s["sha256_indices"] for s in R.make_splits_new(x, y)]
            b = [s["sha256_indices"] for s in R.make_splits_new(x, y)]
            self.assertEqual(a, b)
            self.assertEqual(len(set(a)), 10)
        self.assertEqual(R.sha_xy(*DATA["digits"]), R.sha_xy(*R.load_datasets()["digits"]))
        raw_path = BV1 / "resultados" / "benchmark_v1_raw.json"
        if raw_path.exists():   # los hashes guardados deben coincidir con los recalculados
            raw = json.loads(raw_path.read_text())
            for name in ("breast_cancer", "digits"):
                self.assertEqual([s["sha256_indices"] for s in raw["datasets"][name]["splits"]],
                                 [s["sha256_indices"] for s in R.make_splits_new(*DATA[name])])
                self.assertEqual(raw["datasets"][name]["data_sha256"], R.sha_xy(*DATA[name]))


class GenericMatchesFitBaseline(unittest.TestCase):
    def test_probabilities_match_iris_wine(self):
        sp = R.get_splits(DATA)
        cfg = dict(MS.CONFIG)
        for name in ("iris", "wine"):
            x, y = DATA[name]
            for k in (0, 5):
                tr = np.array(sp[name][k]["train"])
                enc, _ = encode_real_features(x, tr, R.SOURCE_IDS)
                for kind in ("linear", "quadratic"):
                    ref = fit_baseline(enc[tr], y[tr], kind, cfg)
                    sc = MS.design_matrix(enc, kind) @ np.asarray(ref["weights"]).T
                    e = np.exp(sc - sc.max(axis=1, keepdims=True)); pref = e / e.sum(axis=1, keepdims=True)
                    m = MS.fit_generic(x[tr], y[tr], 3, kind, cfg)
                    self.assertLess(np.max(np.abs(MS.probabilities(m, MS.encode_generic(m, x)) - pref)), 1e-6)

    def test_constant_column_does_not_break_and_no_test_clipping(self):
        x = np.column_stack([np.arange(10.0), np.ones(10)])
        lo, hi = MS.minmax_fit(x[:5])
        s = MS.minmax_apply(x, lo, hi)
        self.assertTrue(np.all(s[:, 1] == 0))
        self.assertGreater(s[9, 0], 1.0)   # sin recorte en prueba
        np.testing.assert_allclose(np.sum(MS.coherent_encode(s) ** 2, axis=1), 1.0)


if __name__ == "__main__":
    unittest.main()
