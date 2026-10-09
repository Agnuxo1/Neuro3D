"""P0-4: ejecuta particiones, lineas base y opticos segun PREREGISTRO-P0-4.md (solo CPU, sin bpy).

Subcomandos: splits | baselines | iris | wine [--k K ...] [--seeds 1049,1050,1051] | all
Un proceso a la vez. Cada resultado es resultados/*.json con tiempo de CPU, hash de entrada y version del codigo.
"""
import os
for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_k] = "1"
import argparse, hashlib, json, shutil, subprocess, sys, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
RES = HERE / "resultados"
sys.path.insert(0, str(REPO)); sys.path.insert(0, str(HERE))
from Blender.blender_lab.classifier_comparison_v1 import encode_real_features, fit_baseline, baseline_scores  # noqa: E402
import iris_numeric as IN  # noqa: E402

PROFILE = REPO / "Docs/research/wine_comparison_profile_2026-10-09.json"
WINE = REPO / "Docs/data/uci-wine/wine.data"
WORKER = REPO / "Tools/train_wine_comparison_v1.py"
SOURCE_IDS = ["r0", "r1", "c0", "c1", "c2"]
NPART = 10
WINE_TEST_COUNTS = [12, 15, 10]   # asignacion estratificada fija (coincide con la particion congelada del perfil)
IRIS_TEST_COUNTS = [10, 10, 10]
CODE_FILES = ["Blender/blender_lab/classifier_comparison_v1.py", "Tools/train_wine_comparison_v1.py", "Tools/audit_captured_pilot_result_v1.py",
              "Tools/trace_indexed_scene_v1.py", "Tools/train_captured_geometry_v1.py", "Blender/blender_lab/affine_geometry_network_v1.py",
              "Blender/blender_lab/coherent_state_graph_v1.py", "Blender/demo_lattice_iris/neuro3d_iris_demo.py",
              "Docs/research/wine_comparison_profile_2026-10-09.json"]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def code_version():
    files = {f: sha(REPO / f) for f in CODE_FILES}
    for own in ("run_lineas_base.py", "iris_numeric.py", "wine_worker_runner.py"):
        files["Benchmarks/lineas-base/" + own] = sha(HERE / own)
    return {"files": files, "combined_sha256": hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()}


def load_wine():
    raw = np.loadtxt(WINE, delimiter=",")
    assert raw.shape == (178, 14)
    return raw[:, 1:5], raw[:, 0].astype(np.int64) - 1


def stratified(y, test_counts, seed):
    rng = np.random.default_rng(seed)
    test = []
    for c, n in enumerate(test_counts):
        idx = np.flatnonzero(y == c)
        test += rng.permutation(idx)[:n].tolist()
    test = sorted(test)
    train = sorted(set(range(len(y))) - set(test))
    return train, test


def make_splits():
    _, yw = load_wine()
    _, yi = IN.load_raw()
    out = {"wine": [], "iris": []}
    for k in range(NPART):
        for name, y, counts, seed in (("wine", yw, WINE_TEST_COUNTS, 20261009 + k), ("iris", yi, IRIS_TEST_COUNTS, k)):
            tr, te = stratified(y, counts, seed)
            h = hashlib.sha256(json.dumps({"train": tr, "test": te}).encode()).hexdigest()
            out[name].append({"k": k, "seed": seed, "n_train": len(tr), "n_test": len(te), "train": tr, "test": te, "sha256_indices": h,
                              "test_class_counts": np.bincount(y[te], minlength=3).tolist()})
    out["method"] = "por clase: default_rng(seed).permutation(indices_de_clase)[:n_test_clase]; test fijo Wine [12,15,10], Iris [10,10,10]"
    out["wine_data_sha256"] = sha(WINE)
    out["iris_csv_sha256"] = sha(IN.CSV)
    return out


def get_splits():
    p = RES / "splits.json"
    if not p.exists():
        RES.mkdir(exist_ok=True)
        p.write_text(json.dumps(make_splits(), indent=1), encoding="utf-8")
    return json.loads(p.read_text())


def run_baselines(name, x_raw, y, splits, cfg):
    out = []
    for s in splits[name]:
        tr, te = np.array(s["train"]), np.array(s["test"])
        t = time.process_time()
        x, _ = encode_real_features(x_raw, tr, SOURCE_IDS)
        row = {"k": s["k"], "sha256_indices": s["sha256_indices"]}
        for kind in ("linear", "quadratic"):
            m = fit_baseline(x[tr], y[tr], kind, cfg)
            pred = np.argmax(baseline_scores(m, x), axis=1)
            row[kind] = {"test_accuracy": float(np.mean(pred[te] == y[te])), "train_accuracy": float(np.mean(pred[tr] == y[tr])),
                         "iterations": m["iterations"], "max_gradient_abs": m["max_gradient_abs"], "objective": m["objective"],
                         "nominal_parameters": m["nominal_parameters"], "test_predictions": pred[te].tolist()}
        row["cpu_seconds"] = time.process_time() - t
        out.append(row)
    return out


def cmd_baselines():
    splits = get_splits()
    cfg = json.loads(PROFILE.read_text())["baseline_optimizer"]
    xw, yw = load_wine()
    xi, yi = IN.load_raw()
    res = {"schema": "p0-4.baselines", "config": cfg, "code_version": code_version(),
           "input_sha256": {"wine": sha(WINE), "iris": sha(IN.CSV), "splits": sha(RES / "splits.json")},
           "wine": run_baselines("wine", xw, yw, splits, cfg), "iris": run_baselines("iris", xi, yi, splits, cfg)}
    (RES / "baselines.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    print("baselines: wine lin %.3f quad %.3f | iris lin %.3f quad %.3f" % tuple(
        np.mean([r[kind]["test_accuracy"] for r in res[ds]]) for ds in ("wine", "iris") for kind in ("linear", "quadratic")))


def cmd_iris():
    splits = get_splits()
    x, y = IN.load_raw()
    path = RES / "optical_iris.json"
    if path.exists():
        out = json.loads(path.read_text())
    else:
        out = {"schema": "p0-4.optical_iris", "code_version": code_version(), "demo_sha256": IN.demo_sha256(),
               "input_sha256": {"iris": sha(IN.CSV), "splits": sha(RES / "splits.json")}, "steps": 500, "restarts": 4,
               "seed": 0, "partitions": []}
    done = {p["k"] for p in out["partitions"]}
    for s in splits["iris"]:
        if s["k"] in done:
            continue
        tr, te = np.array(s["train"]), np.array(s["test"])
        lo, hi = x[tr].min(0), x[tr].max(0)
        xs = (x - lo) / (hi - lo)
        t = time.process_time()
        p = IN.train(xs[tr], y[tr], steps=500, seed=0, restarts=4, log=lambda *_: None)
        cpu = time.process_time() - t
        l_tr, a_tr = IN.loss_acc(p, xs[tr], y[tr])
        l_te, a_te = IN.loss_acc(p, xs[te], y[te])
        out["partitions"].append({"k": s["k"], "sha256_indices": s["sha256_indices"], "train_loss": float(l_tr), "train_accuracy": float(a_tr),
                                  "test_accuracy": float(a_te), "test_loss": float(l_te), "params": p.tolist(), "cpu_seconds": cpu})
        out["partitions"].sort(key=lambda r: r["k"])
        path.write_text(json.dumps(out, indent=1), encoding="utf-8")
        print("iris k=%d test_acc=%.4f cpu=%.1fs" % (s["k"], a_te, cpu), flush=True)


def cmd_wine(ks, seeds):
    splits = get_splits()
    prof = json.loads(PROFILE.read_text())
    (RES / "perfiles").mkdir(exist_ok=True)
    (RES / "wine_trabajo").mkdir(exist_ok=True)
    keep = [i for i in prof["initializations"] if i["seed"] in seeds]
    assert len(keep) == len(seeds), "semillas no halladas en el perfil"
    for k in ks:
        final = RES / ("optical_wine_k%d.json" % k)
        if final.exists():
            print("wine k=%d ya hecho" % k)
            continue
        s = splits["wine"][k]
        p = dict(prof)
        p["train_indices"] = s["train"]
        p["test_indices"] = s["test"]
        p["initializations"] = keep
        pp = RES / "perfiles" / ("wine_profile_k%d.json" % k)
        pp.write_text(json.dumps(p, indent=2), encoding="utf-8")
        work = RES / "wine_trabajo" / ("k%d" % k)
        if work.exists():
            shutil.rmtree(work)
        cpuj = RES / "wine_trabajo" / ("cpu_k%d.json" % k)
        r = subprocess.run([sys.executable, str(HERE / "wine_worker_runner.py"), str(cpuj), str(WORKER), "--profile", str(pp), "--out", str(work)],
                           cwd=str(REPO), capture_output=True, text=True)
        (RES / "wine_trabajo" / ("log_k%d.txt" % k)).write_text(r.stdout[-4000:] + "\n--stderr--\n" + r.stderr[-4000:], encoding="utf-8")
        res = json.loads((work / "result.json").read_text())
        cpu = json.loads(cpuj.read_text())
        runs = [{"seed": q["seed"], "status": q["status"], "test_accuracy": q["heldout"]["accuracy"], "train_accuracy": q["train"]["accuracy"],
                 "initial_train_loss": q["initial_train_loss"], "final_train_loss": q["final_train_loss"],
                 "cpu_seconds_seed_training_plus_rebuild": q["cost_seconds"]["seed_training_plus_rebuild"],
                 "cpu_seconds_geometry_audits": q["cost_seconds"]["all_geometry_audits"]} for q in res["runs"]]
        out = {"schema": "p0-4.optical_wine", "k": k, "sha256_indices": s["sha256_indices"], "worker_exit_code": cpu["exit_code"], "worker_status": res["status"],
               "profile_copy_sha256": sha(pp), "seeds": seeds, "runs": runs, "process_cpu_seconds": cpu["process_cpu_seconds"], "wall_seconds": cpu["wall_seconds"],
               "worker_baselines_test_accuracy": {b["kind"]: b["heldout"]["accuracy"] for b in res["baselines"]},
               "worker_baseline_test_predictions": {b["kind"]: [b["predictions"][i] for i in s["test"]] for b in res["baselines"]},
               "input_sha256": {"wine": sha(WINE), "profile_original": sha(PROFILE)}, "code_version": code_version()}
        final.write_text(json.dumps(out, indent=1), encoding="utf-8")
        print("wine k=%d status=%s test_acc=%s cpu=%.1fs" % (k, res["status"], [round(q["test_accuracy"], 4) for q in runs], cpu["process_cpu_seconds"]), flush=True)
        for f in list(work.rglob("final_virtual_*.json")):
            f.unlink()   # artefactos pesados; el resultado queda en result.json


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["splits", "baselines", "iris", "wine", "all"])
    ap.add_argument("--k", type=int, nargs="*")
    ap.add_argument("--seeds", default="1049,1050,1051")
    a = ap.parse_args()
    RES.mkdir(exist_ok=True)
    seeds = [int(v) for v in a.seeds.split(",")]
    if a.cmd == "splits":
        get_splits()
        print("splits ok")
    if a.cmd in ("baselines", "all"):
        cmd_baselines()
    if a.cmd in ("iris", "all"):
        cmd_iris()
    if a.cmd in ("wine", "all"):
        cmd_wine(a.k if a.k else range(NPART), seeds)
