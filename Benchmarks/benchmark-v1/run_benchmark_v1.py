"""P1-5: ejecuta las lineas base B1-B6 segun PREREGISTRO-P1-5.md (con Enmienda 1). Solo CPU, un proceso, sin descargas.

Salida: resultados/benchmark_v1_raw.json. Uso: python run_benchmark_v1.py
"""
import os
for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_k] = "1"
import hashlib, json, sys, time, warnings
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
RES = HERE / "resultados"
sys.path.insert(0, str(REPO)); sys.path.insert(0, str(HERE))
import multiclass_softmax as MS  # noqa: E402
from Blender.blender_lab.classifier_comparison_v1 import encode_real_features, fit_baseline, baseline_scores  # noqa: E402

IRIS_CSV = REPO / "Blender/demo_lattice_iris/iris.csv"
WINE = REPO / "Docs/data/uci-wine/wine.data"
SPLITS_P04 = REPO / "Benchmarks/lineas-base/resultados/splits.json"
BASE_P04 = REPO / "Benchmarks/lineas-base/resultados/baselines.json"
SOURCE_IDS = ["r0", "r1", "c0", "c1", "c2"]
SPECIES = ["setosa", "versicolor", "virginica"]
SEED0 = 20261009
NPART = 10
VERIFY_TOL = 1e-6
CODE_FILES = ["Benchmarks/benchmark-v1/multiclass_softmax.py", "Benchmarks/benchmark-v1/run_benchmark_v1.py",
              "Blender/blender_lab/classifier_comparison_v1.py"]


def sha_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def sha_xy(x, y):
    return {"X": hashlib.sha256(np.ascontiguousarray(x, dtype=np.float64).tobytes()).hexdigest(),
            "y": hashlib.sha256(np.ascontiguousarray(y, dtype=np.int64).tobytes()).hexdigest(),
            "X_shape": list(x.shape), "y_shape": list(y.shape)}


def load_datasets():
    from sklearn.datasets import load_breast_cancer, load_digits
    rows = [l.strip().split(",") for l in IRIS_CSV.read_text(encoding="utf-8").splitlines()[1:]]
    xi = np.array([[float(v) for v in r[:4]] for r in rows]); yi = np.array([SPECIES.index(r[4]) for r in rows])
    raw = np.loadtxt(WINE, delimiter=","); assert raw.shape == (178, 14)
    xw, yw = raw[:, 1:5], raw[:, 0].astype(np.int64) - 1
    bc = load_breast_cancer(); dg = load_digits()
    return {"iris": (xi, yi), "wine": (xw, yw),
            "breast_cancer": (np.asarray(bc.data, dtype=np.float64), np.asarray(bc.target, dtype=np.int64)),
            "digits": (np.asarray(dg.data, dtype=np.float64), np.asarray(dg.target, dtype=np.int64))}


def split_hash(tr, te):
    return hashlib.sha256(json.dumps({"train": tr, "test": te}).encode()).hexdigest()


def make_splits_new(x, y):
    """Breast Cancer y Digits: StratifiedShuffleSplit 80/20, semillas 20261009+k, indices ordenados."""
    from sklearn.model_selection import StratifiedShuffleSplit
    out = []
    for k in range(NPART):
        seed = SEED0 + k
        tr, te = next(StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=seed).split(x, y))
        tr, te = sorted(int(i) for i in tr), sorted(int(i) for i in te)
        out.append({"k": k, "seed": seed, "n_train": len(tr), "n_test": len(te), "train": tr, "test": te,
                    "sha256_indices": split_hash(tr, te), "test_class_counts": np.bincount(y[te]).tolist(),
                    "train_class_counts": np.bincount(y[tr]).tolist()})
    return out


def get_splits(data):
    p04 = json.loads(SPLITS_P04.read_text())
    sp = {}
    for name in ("iris", "wine"):
        for s in p04[name]:   # verificar que los indices coinciden con los hashes registrados en P0-4
            assert split_hash(s["train"], s["test"]) == s["sha256_indices"], (name, s["k"])
        sp[name] = p04[name]
    for name in ("breast_cancer", "digits"):
        sp[name] = make_splits_new(*data[name])
    return sp


def verify_generic(data, splits, cfg):
    """La version generica debe reproducir fit_baseline (probabilidades, lineal y cuadratica) en Iris y Wine, tolerancia 1e-6."""
    rep = {"tolerance": VERIFY_TOL, "max_abs_probability_difference": {}, "pass": True}
    for name in ("iris", "wine"):
        x, y = data[name]
        for kind in ("linear", "quadratic"):
            worst = 0.0
            for s in splits[name]:
                tr = np.array(s["train"])
                enc, _ = encode_real_features(x, tr, SOURCE_IDS)
                ref = fit_baseline(enc[tr], y[tr], kind, cfg)
                zr = MS.design_matrix(enc, kind)
                sc = zr @ np.asarray(ref["weights"]).T
                e = np.exp(sc - sc.max(axis=1, keepdims=True)); pref = e / e.sum(axis=1, keepdims=True)
                m = MS.fit_generic(x[tr], y[tr], 3, kind, cfg)
                pg = MS.probabilities(m, MS.encode_generic(m, x))
                worst = max(worst, float(np.max(np.abs(pg - pref))))
            rep["max_abs_probability_difference"]["%s_%s" % (name, kind)] = worst
            rep["pass"] = rep["pass"] and worst < VERIFY_TOL
    return rep


def metrics(pred, y):
    from sklearn.metrics import balanced_accuracy_score
    return {"test_accuracy": float(np.mean(pred == y)), "balanced_accuracy": float(balanced_accuracy_score(y, pred))}


def run_dataset(name, x, y, splits, cfg, with_b56):
    from sklearn.svm import SVC
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.neural_network import MLPClassifier
    nc = int(len(np.unique(y)))
    res = {m: [] for m in ("B1", "B2", "B3", "B4") + (("B5", "B6") if with_b56 else ())}
    for s in splits[name]:
        tr, te, k, seed = np.array(s["train"]), np.array(s["test"]), s["k"], s["seed"]
        h = s["sha256_indices"]
        lo, hi = MS.minmax_fit(x[tr]); xs = MS.minmax_apply(x, lo, hi)
        # B1: softmax lineal generico (CPU = escalado + ajuste + prediccion)
        t = time.process_time()
        m = MS.fit_generic(x[tr], y[tr], nc, "linear", cfg); pred = MS.predict_generic(m, x[te])
        cpu = time.process_time() - t
        res["B1"].append(dict(k=k, sha256_indices=h, cpu_seconds=cpu, converged=m["converged"], iterations=m["iterations"],
                              max_gradient_abs=m["max_gradient_abs"], nominal_parameters=m["nominal_parameters"], **metrics(pred, y[te])))
        # B2
        t = time.process_time(); clf = SVC(kernel="rbf", C=1, gamma="scale").fit(xs[tr], y[tr]); pred = clf.predict(xs[te]); cpu = time.process_time() - t
        res["B2"].append(dict(k=k, sha256_indices=h, cpu_seconds=cpu, **metrics(pred, y[te])))
        # B3
        t = time.process_time(); clf = RandomForestClassifier(n_estimators=200, random_state=seed).fit(xs[tr], y[tr]); pred = clf.predict(xs[te]); cpu = time.process_time() - t
        res["B3"].append(dict(k=k, sha256_indices=h, cpu_seconds=cpu, random_state=seed, **metrics(pred, y[te])))
        # B4
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            t = time.process_time()
            clf = MLPClassifier(hidden_layer_sizes=(32,), max_iter=500, early_stopping=False, random_state=seed).fit(xs[tr], y[tr])
            pred = clf.predict(xs[te]); cpu = time.process_time() - t
        res["B4"].append(dict(k=k, sha256_indices=h, cpu_seconds=cpu, random_state=seed, n_iter=int(clf.n_iter_),
                              convergence_warning=any("onverge" in str(q.message) for q in w), **metrics(pred, y[te])))
        if with_b56:   # B5/B6: fit_baseline original (P0-4) con la codificacion de encode_real_features
            for tag, kind in (("B5", "linear"), ("B6", "quadratic")):
                t = time.process_time()
                enc, _ = encode_real_features(x, tr, SOURCE_IDS)
                bm = fit_baseline(enc[tr], y[tr], kind, cfg); pred = np.argmax(baseline_scores(bm, enc), axis=1)
                cpu = time.process_time() - t
                res[tag].append(dict(k=k, sha256_indices=h, cpu_seconds=cpu, iterations=bm["iterations"],
                                     max_gradient_abs=bm["max_gradient_abs"], nominal_parameters=bm["nominal_parameters"],
                                     test_predictions=pred[te].tolist(), **metrics(pred[te], y[te])))
    return res


def main():
    import platform, scipy, sklearn
    t0 = time.perf_counter()
    cfg = dict(MS.CONFIG)
    data = load_datasets()
    splits = get_splits(data)
    ver = verify_generic(data, splits, cfg)
    print("verificacion generica vs fit_baseline:", ver, flush=True)
    RES.mkdir(exist_ok=True)
    if not ver["pass"]:
        (RES / "verificacion_fallida.json").write_text(json.dumps(ver, indent=1), encoding="utf-8")
        sys.exit("La version generica NO reproduce fit_baseline: no se continua")
    out = {"schema": "p1-5.benchmark_v1_raw", "preregistro": "Benchmarks/benchmark-v1/PREREGISTRO-P1-5.md (+ Enmienda 1)",
           "versions": {"python": sys.version, "numpy": np.__version__, "scipy": scipy.__version__, "scikit-learn": sklearn.__version__,
                        "platform": platform.platform()},
           "config_softmax": cfg, "threads": "OMP/OPENBLAS/MKL = 1",
           "code_sha256": {f: sha_file(REPO / f) for f in CODE_FILES},
           "input_sha256": {"iris_csv": sha_file(IRIS_CSV), "wine_data": sha_file(WINE), "splits_p0_4": sha_file(SPLITS_P04), "baselines_p0_4": sha_file(BASE_P04)},
           "datasets": {}, "verification_generic_vs_fit_baseline": ver,
           "split_source": {"iris": "P0-4 splits.json (Enmienda 1)", "wine": "P0-4 splits.json (Enmienda 1)",
                            "breast_cancer": "StratifiedShuffleSplit(test_size=0.2, random_state=20261009+k)",
                            "digits": "StratifiedShuffleSplit(test_size=0.2, random_state=20261009+k)"}}
    for name in ("iris", "wine", "breast_cancer", "digits"):
        x, y = data[name]
        t = time.perf_counter()
        models = run_dataset(name, x, y, splits, cfg, with_b56=name in ("iris", "wine"))
        out["datasets"][name] = {"data_sha256": sha_xy(x, y), "n_classes": int(len(np.unique(y))), "n_features": int(x.shape[1]),
                                 "splits": splits[name], "models": models, "wall_seconds": time.perf_counter() - t}
        print(name, {m: round(float(np.mean([r["test_accuracy"] for r in rs])), 4) for m, rs in models.items()}, "%.1fs" % (time.perf_counter() - t), flush=True)
    b04 = json.loads(BASE_P04.read_text())
    out["b5_b6_predictions_identical_to_p0_4"] = bool(all(
        out["datasets"][d]["models"][tag][k]["test_predictions"] == sorted(b04[d], key=lambda r: r["k"])[k][kind]["test_predictions"]
        for d in ("iris", "wine") for tag, kind in (("B5", "linear"), ("B6", "quadratic")) for k in range(NPART)))
    out["total_wall_seconds"] = time.perf_counter() - t0
    (RES / "benchmark_v1_raw.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print("raw ok; B5/B6 identicas a P0-4:", out["b5_b6_predictions_identical_to_p0_4"], "total %.1fs" % out["total_wall_seconds"])


if __name__ == "__main__":
    main()
