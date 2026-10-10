"""Ejecucion de P2-10: entrenamiento de la malla, lineas base y escala (CPU)."""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_v] = "1"

import json
import platform
import sys
import time
import warnings
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import scipy
import sklearn
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier

import datos
from gradiente import loss_and_grad
from malla import Mesh, apply_layers, dense_matrix, layer_coeffs

HERE = Path(__file__).parent
RES = HERE / "resultados"
PART = RES / "parciales"
N_MODES, K_DET, T_TEMP, LR, STEPS = 64, 10, 0.05, 0.01, 2000
PHASE_SEEDS = (0, 1, 2)


def train_mesh(task):
    k, s = task
    f = PART / f"malla_k{k}_s{s}.json"
    if f.exists():
        return json.loads(f.read_text())
    X, y = datos.load()
    tr, te = datos.split_indices(y, k)
    Ztr, Zte = datos.encode(X[tr], X[te])
    ytr, yte = y[tr], y[te]
    mesh = Mesh(N_MODES)
    p = np.random.default_rng(s).uniform(0, 2 * np.pi, mesh.n_params)
    m, v = np.zeros_like(p), np.zeros_like(p)
    b1, b2, eps = 0.9, 0.999, 1e-8
    curve = []
    t0 = time.process_time()
    w0 = time.perf_counter()
    for t in range(1, STEPS + 1):
        loss, g = loss_and_grad(mesh, p, Ztr, ytr, K_DET, T_TEMP)
        if t == 1 or t % 100 == 0:
            curve.append([t, float(loss)])
        m = b1 * m + (1 - b1) * g
        v = b2 * v + (1 - b2) * g * g
        p -= LR * (m / (1 - b1 ** t)) / (np.sqrt(v / (1 - b2 ** t)) + eps)
    cpu = time.process_time() - t0
    wall = time.perf_counter() - w0
    final_loss, _ = loss_and_grad(mesh, p, Ztr, ytr, K_DET, T_TEMP, want_grad=False)

    def acc(Z, yy):
        out = apply_layers(mesh, layer_coeffs(mesh, p), Z.T)
        return float(np.mean(np.argmax(np.abs(out[:K_DET]) ** 2, axis=0) == yy))
    rec = {"k": k, "phase_seed": s, "train_loss": float(final_loss), "train_acc": acc(Ztr, ytr),
           "test_acc": acc(Zte, yte), "cpu_seconds": cpu, "wall_seconds": wall,
           "loss_curve": curve, "phases_sha_note": "no guardadas (reproducibles por semilla)"}
    PART.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(rec), encoding="utf-8", newline="\n")
    return rec


def baselines(k):
    X, y = datos.load()
    tr, te = datos.split_indices(y, k)
    Ztr, Zte = datos.encode(X[tr], X[te])
    out = {"k": k}
    lam = 0.001  # objetivo: CE media + (lam/2)||W||^2  ->  C = 1/(lam * n_train)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        t0 = time.process_time()
        lg = LogisticRegression(C=1.0 / (lam * len(tr)), max_iter=5000, tol=1e-8).fit(Ztr, y[tr])
        out["logistica"] = {"test_acc": float(lg.score(Zte, y[te])), "train_acc": float(lg.score(Ztr, y[tr])),
                            "n_iter": int(np.max(lg.n_iter_)), "cpu_seconds": time.process_time() - t0,
                            "n_params": int(lg.coef_.size + lg.intercept_.size),
                            "avisos": [str(x.message) for x in w]}
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        t0 = time.process_time()
        mlp = MLPClassifier(hidden_layer_sizes=(48,), max_iter=500, early_stopping=False,
                            random_state=datos.BASE_SEED + k).fit(Ztr, y[tr])
        out["mlp"] = {"test_acc": float(mlp.score(Zte, y[te])), "train_acc": float(mlp.score(Ztr, y[tr])),
                      "n_iter": int(mlp.n_iter_), "cpu_seconds": time.process_time() - t0,
                      "n_params": int(sum(c.size for c in mlp.coefs_) + sum(b.size for b in mlp.intercepts_)),
                      "convergio": bool(mlp.n_iter_ < 500),
                      "avisos": [str(x.message) for x in w if issubclass(x.category, ConvergenceWarning)]}
    return out


def scale():
    X, y = datos.load()
    tr, te = datos.split_indices(y, 0)
    rows = []
    for n in (8, 16, 32, 64):
        Zte = datos.encode(X[tr], X[te])[1] if n == 64 else datos.encode_pca(X[tr], X[te], n)[1]
        mesh = Mesh(n)
        p = np.random.default_rng(0).uniform(0, 2 * np.pi, mesh.n_params)
        co = layer_coeffs(mesh, p)
        xs = [Zte[i % len(Zte)] for i in range(1000)]
        for x in xs[:100]:  # calentamiento
            apply_layers(mesh, co, x)
        reps = []
        for _ in range(7):
            t0 = time.perf_counter()
            for x in xs:
                apply_layers(mesh, co, x)
            reps.append((time.perf_counter() - t0) / 1000)
        # exploratorio: lote de 1000 entradas, tiempo por entrada
        Xb = np.array(xs).T
        apply_layers(mesh, co, Xb)
        breps = []
        for _ in range(7):
            t0 = time.perf_counter()
            apply_layers(mesh, co, Xb)
            breps.append((time.perf_counter() - t0) / 1000)
        coef_bytes = int(sum(c.nbytes for tup in co for c in tup)) // 1  # elementos del MZI almacenados
        mzi_bytes = mesh.n_mzi * 4 * 16  # 4 elementos complejos por MZI (referencia teorica)
        dense_bytes = int(dense_matrix(mesh, p).nbytes)
        rows.append({"N": n, "t_entrada_s": float(np.median(reps)), "t_entrada_reps": reps,
                     "t_entrada_lote_s": float(np.median(breps)), "t_entrada_lote_reps": breps,
                     "bytes_coeficientes": coef_bytes, "bytes_mzi_teorico": mzi_bytes,
                     "bytes_matriz_densa": dense_bytes, "n_mzi": mesh.n_mzi, "n_fases": mesh.n_params,
                     "entrada": "digits crudo (64 modos)" if n == 64 else f"PCA({n}) ajustada con entrenamiento"})
    return rows


def main():
    stage = sys.argv[1] if len(sys.argv) > 1 else "all"
    RES.mkdir(exist_ok=True)
    if stage in ("all", "splits"):
        datos.write_splits()
    if stage in ("all", "malla"):
        tasks = [(k, s) for k in range(10) for s in PHASE_SEEDS]
        with ProcessPoolExecutor(max_workers=3) as ex:
            done = list(ex.map(train_mesh, tasks))
        print("mallas listas", len(done))
    if stage in ("all", "resto"):
        mesh_recs = [train_mesh((k, s)) for k in range(10) for s in PHASE_SEEDS]  # lee parciales
        base = [baselines(k) for k in range(10)]
        sc = scale()
        raw = {"versiones": {"python": sys.version, "numpy": np.__version__, "scipy": scipy.__version__,
                             "sklearn": sklearn.__version__, "plataforma": platform.platform()},
               "config": {"N": N_MODES, "K": K_DET, "T": T_TEMP, "lr": LR, "pasos": STEPS,
                          "semillas_fases": list(PHASE_SEEDS), "hilos_max": 3,
                          "trabajadores_entrenamiento": 3},
               "malla": mesh_recs, "lineas_base": base, "escala": sc}
        (RES / "resultados_raw.json").write_text(json.dumps(raw, indent=1), encoding="utf-8", newline="\n")
        print("raw escrito")


if __name__ == "__main__":
    main()
