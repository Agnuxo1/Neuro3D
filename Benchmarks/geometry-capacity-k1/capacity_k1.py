"""Execute the HA-K1 protocol exactly as committed; refuse to overwrite an earlier run."""
from __future__ import annotations

import os
for _name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_name] = "1"
import argparse
import hashlib
import json
from pathlib import Path
import platform
import sys
import time

import numpy as np
import scipy
from scipy.stats import wilcoxon
import sklearn
from sklearn.linear_model import LogisticRegression

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "agent_support"))
from Tools.audit_captured_pilot_result_v1 import decode  # noqa: E402
from Tools.train_captured_geometry_v1 import parameters_and_bases  # noqa: E402
from Blender.blender_lab.affine_geometry_network_v1 import AffineGeometryNetwork  # noqa: E402
from Blender.blender_lab.coherent_state_graph_v1 import build_graph  # noqa: E402
from closure_limits import train_detector_classifier  # noqa: E402
from closure_statistics import holm_adjust, paired_bootstrap  # noqa: E402

CAPTURE = ROOT / "Docs/validation/native-deferred-training-2026-10-09/attempt01/worker"
DETECTORS = ("det.R0", "det.R1", "det.R2")
BOX, TEMPERATURE, N_TRAIN, N_TEST, SEEDS, RESTARTS = 0.035, 0.05, 400, 2000, 10, 3
GEOM_STEPS, GEOM_LR, LIN_STEPS, LIN_LR, LIN_SCALE, QUAD_C = 400, 0.002, 600, 0.05, 20.0, 100.0
WALL_LIMIT_S = 7200.0
IU = np.triu_indices(5)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_network():
    scene = decode(json.loads((CAPTURE / "initial_native_scene.json").read_bytes()))
    graph = decode(json.loads((CAPTURE / "initial_native_graph.json").read_bytes()))
    parameters, _ = parameters_and_bases(scene)
    return AffineGeometryNetwork(scene, graph, parameters), graph


def topology(graph) -> list:
    return [(n["hit_object"], tuple(sorted(e["target"] for e in n["edges"]))) for n in graph["nodes"]]


def topology_ok(net, base, theta) -> bool:
    scene, _ = net.materialize(theta)
    fresh = build_graph(scene)
    return fresh["status"] == "COMPLETE" and topology(fresh) == base


def encode(f: np.ndarray) -> np.ndarray:
    x = np.column_stack([f, np.ones(len(f))])
    return x / np.linalg.norm(x, axis=1, keepdims=True)


def geom_powers(net, x, theta, columns) -> np.ndarray:
    return net.forward(x.astype(np.complex128), theta, gradients=False)["powers"][:, columns]


def qvec(rows):
    return np.concatenate([np.real(np.conj(u)[:, None] * u[None, :])[IU] for u in rows])


def dq(rows, drows):
    return np.concatenate([np.real(np.conj(du)[:, None] * u[None, :] + np.conj(u)[:, None] * du[None, :])[IU]
                           for u, du in zip(rows, drows)])


def decision_rank(jac, q, tol=1e-9):
    basis = [np.concatenate([np.eye(15)[k]] * 3) for k in range(15)] + [q]
    b = np.array(basis).T
    rb = np.linalg.matrix_rank(b, tol=tol * np.linalg.norm(b))
    s = np.linalg.svd(np.hstack([jac, b]), compute_uv=False)
    return int((s > tol * s[0]).sum()) - int(rb)


def dimension_report(net, columns) -> dict:
    rng = np.random.default_rng(1)
    geom, inert = [], None
    for _ in range(20):
        theta = rng.uniform(-BOX, BOX, net.count)
        r = net.forward(np.eye(5, dtype=np.complex128), theta)
        rows = r["fields"].T[columns]
        drows = np.transpose(r["field_jacobian"], (2, 1, 0))[:, columns, :]
        jac = np.array([dq(rows, drows[p]) for p in range(net.count)]).T
        s = np.linalg.svd(jac, compute_uv=False)
        geom.append({"jacobian_rank": int((s > 1e-9 * s[0]).sum()), "decision_rank": decision_rank(jac, qvec(rows))})
        norms = np.linalg.norm(r["field_jacobian"][:, columns, :], axis=(0, 1))
        zero = {net.parameter_ids[k] for k in range(net.count) if norms[k] == 0.0}
        inert = zero if inert is None else inert & zero
    lin = []
    for _ in range(20):
        w = rng.normal(size=(3, 5)) + 1j * rng.normal(size=(3, 5))
        cols = []
        for j in range(3):
            for k in range(5):
                for z in (1, 1j):
                    d = np.zeros((3, 5), complex)
                    d[j, k] = z
                    cols.append(dq(w, d))
        lin.append(decision_rank(np.array(cols).T, qvec(w)))
    quad = decision_rank(np.eye(45), rng.normal(size=45))
    return {"geom": geom, "lin_decision_ranks": sorted(set(lin)), "quad_decision_rank": quad,
            "inert_parameters_for_decision_detectors": sorted(inert)}


def train_geom(net, x, y, columns, seed) -> dict:
    rng = np.random.default_rng(seed)
    theta = rng.uniform(-BOX, BOX, net.count)
    m, v = np.zeros(net.count), np.zeros(net.count)
    xc = x.astype(np.complex128)
    for t in range(1, GEOM_STEPS + 1):
        _, grad, _ = net.cross_entropy(xc, y, theta, list(DETECTORS), TEMPERATURE)
        m = 0.9 * m + 0.1 * grad
        v = 0.999 * v + 0.001 * grad * grad
        theta = np.clip(theta - GEOM_LR * (m / (1 - 0.9 ** t)) / (np.sqrt(v / (1 - 0.999 ** t)) + 1e-12), -BOX, BOX)
    loss = net.cross_entropy(xc, y, theta, list(DETECTORS), TEMPERATURE)[0]
    return {"theta": theta, "loss": float(loss), "seed": seed}


def accuracy(pred, y) -> float:
    return float(np.mean(np.asarray(pred) == np.asarray(y)))


def run_seed(net, base, columns, s) -> dict:
    data = np.random.default_rng(1000 + s)
    x_train, x_test = encode(data.random((N_TRAIN, 4))), encode(data.random((N_TEST, 4)))
    teacher = np.random.default_rng(2000 + s)
    w = (teacher.normal(size=(3, 5)) + 1j * teacher.normal(size=(3, 5))) / np.sqrt(2)
    a = teacher.normal(size=(3, 5, 5))
    q = (a + np.transpose(a, (0, 2, 1))) / 2
    theta_star = teacher.uniform(-BOX, BOX, net.count)
    labelers = {
        "T_lin": lambda x: np.argmax(np.abs(x @ w.T) ** 2, axis=1),
        "T_quad": lambda x: np.argmax(np.einsum("nk,jkl,nl->nj", x, q, x), axis=1),
        "T_geom": lambda x: np.argmax(geom_powers(net, x, theta_star, columns), axis=1),
    }
    out = {"seed": s, "teacher_geom_topology_ok": topology_ok(net, base, theta_star), "teachers": {}}
    quad_features = lambda x: np.column_stack([x[:, i] * x[:, j] for i, j in zip(*IU)])
    for name, label in labelers.items():
        y_train, y_test = label(x_train), label(x_test)
        row = {"majority_test_rate": float(np.max(np.bincount(y_test, minlength=3)) / N_TEST),
               "train_class_counts": np.bincount(y_train, minlength=3).tolist()}
        if len(set(y_train.tolist())) > 1:
            lr = LogisticRegression(C=QUAD_C, max_iter=5000).fit(quad_features(x_train), y_train)
            row["S_quad"] = {"test": accuracy(lr.predict(quad_features(x_test)), y_test),
                             "train": accuracy(lr.predict(quad_features(x_train)), y_train)}
        else:
            row["S_quad"] = {"test": accuracy(np.full(N_TEST, y_train[0]), y_test), "train": 1.0, "note": "single training class"}
        fits = [train_detector_classifier(x_train, y_train, 3, passive=False, steps=LIN_STEPS, learning_rate=LIN_LR,
                                          scale=LIN_SCALE, seed=3000 + 10 * s + k) for k in range(RESTARTS)]
        best = min(fits, key=lambda f: f["loss_history"][-1])
        row["S_lin"] = {"test": accuracy(np.argmax(np.abs(x_test @ best["W"].T) ** 2, axis=1), y_test),
                        "train": best["train_accuracy"], "final_loss": best["loss_history"][-1]}
        runs = sorted((train_geom(net, x_train, y_train, columns, 3000 + 10 * s + k) for k in range(RESTARTS)),
                      key=lambda r: r["loss"])
        chosen, checks = None, []
        for run in runs:
            ok = topology_ok(net, base, run["theta"])
            checks.append({"seed": run["seed"], "loss": run["loss"], "topology_ok": ok})
            if ok:
                chosen = run
                break
        if chosen is None:
            row["S_geom"] = {"test": None, "train": None, "checks": checks, "status": "NULL_NO_VALID_TOPOLOGY"}
        else:
            row["S_geom"] = {"test": accuracy(np.argmax(geom_powers(net, x_test, chosen["theta"], columns), axis=1), y_test),
                             "train": accuracy(np.argmax(geom_powers(net, x_train, chosen["theta"], columns), axis=1), y_train),
                             "final_loss": chosen["loss"], "theta": chosen["theta"].tolist(), "checks": checks}
        out["teachers"][name] = row
    return out


def decide(candidate, reference) -> dict:
    if len(candidate) < 2:
        return {"differences": [], "wilcoxon_one_sided_p": 1.0, "bootstrap": {"interval": [-1.0, 1.0]},
                "note": "fewer than two complete seeds"}
    a, b = np.asarray(candidate, float), np.asarray(reference, float)
    d = a - b
    p = 1.0 if np.all(d == 0) else float(wilcoxon(a, b, alternative="greater", zero_method="wilcox").pvalue)
    boot = paired_bootstrap(a.tolist(), b.tolist(), seed=0, draws=10000, alpha=0.05)
    return {"differences": d.tolist(), "mean_difference": float(d.mean()), "wilcoxon_one_sided_p": p, "bootstrap": boot}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=HERE / "results")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    start = time.perf_counter()
    net, graph = load_network()
    base = topology(graph)
    columns = [net.ports.index(p) for p in DETECTORS]
    report = {"schema": "neuro3d.ha_k1.v1", "protocol": "PROTOCOL-HA-K1.md",
              "environment": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
                              "sklearn": sklearn.__version__, "platform": platform.platform()},
              "dimension": dimension_report(net, columns), "seeds": []}
    print("dimension", json.dumps({k: v for k, v in report["dimension"].items() if k != "geom"}), flush=True)
    for s in range(SEEDS):
        if time.perf_counter() - start > WALL_LIMIT_S:
            report["seeds"].append({"seed": s, "status": "NULL_WALL_LIMIT"})
            continue
        t0 = time.perf_counter()
        row = run_seed(net, base, columns, s)
        row["seconds"] = time.perf_counter() - t0
        report["seeds"].append(row)
        print("seed", s, round(row["seconds"], 1), {t: {k: row["teachers"][t][k]["test"] for k in ("S_quad", "S_lin", "S_geom")}
                                                   for t in row["teachers"]}, flush=True)
    done = [r for r in report["seeds"] if "teachers" in r and all(r["teachers"][t]["S_geom"]["test"] is not None for t in r["teachers"])]
    acc = lambda t, s: [r["teachers"][t][s]["test"] for r in done]
    h1, h2 = decide(acc("T_lin", "S_lin"), acc("T_lin", "S_geom")), decide(acc("T_quad", "S_quad"), acc("T_quad", "S_lin"))
    holm = holm_adjust([h1["wilcoxon_one_sided_p"], h2["wilcoxon_one_sided_p"]])
    for h, p in zip((h1, h2), holm):
        h["holm_p"] = p
        lo, hi = h["bootstrap"]["interval"]
        h["decision"] = "SUPPORTED" if p < 0.05 and lo > 0 else ("OPPOSITE" if hi < 0 else "INCONCLUSIVE")
    control = float(np.mean(acc("T_geom", "S_geom"))) if done else None
    report.update({"complete_seeds": len(done), "H_A1": h1, "H_A2": h2,
                   "C_A3": {"mean_S_geom_on_T_geom": control, "met": control is not None and control >= 0.95},
                   "means": {t: {s: float(np.mean(acc(t, s))) for s in ("S_quad", "S_lin", "S_geom")} for t in ("T_lin", "T_quad", "T_geom")},
                   "seconds_total": time.perf_counter() - start})
    if not report["C_A3"]["met"]:
        h1["note"] = "C-A3 failed: H-A1 confounded by optimization"
    sources = [HERE / "PROTOCOL-HA-K1.md", HERE / "capacity_k1.py", CAPTURE / "initial_native_scene.json",
               CAPTURE / "initial_native_graph.json", ROOT / "agent_support/closure_limits.py",
               ROOT / "agent_support/closure_statistics.py", ROOT / "Blender/blender_lab/affine_geometry_network_v1.py",
               ROOT / "Blender/blender_lab/coherent_state_graph_v1.py", ROOT / "Tools/train_captured_geometry_v1.py"]
    report["sources_sha256"] = {str(p.relative_to(ROOT)).replace("\\", "/"): sha256(p) for p in sources}
    (args.out / "HA_K1_RESULTS.json").write_bytes((json.dumps(report, indent=1, allow_nan=False) + "\n").encode())
    print(json.dumps({"means": report["means"], "H_A1": h1["decision"], "H_A2": h2["decision"], "C_A3": report["C_A3"],
                      "complete_seeds": len(done)}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
