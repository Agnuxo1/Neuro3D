"""Extension post hoc (decision JEV 2026-10-09): semillas 1050 y 1051 en las 10 particiones de Wine.

Uso: python run_extension.py all [--jobs 3]   |   python run_extension.py one K SEED
k=0 se reutiliza de resultados/optical_wine_k0.json (misma ejecucion que la primaria; se verifica hash de particion y perfil).
"""
import os
for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_k] = "1"
import json, shutil, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_lineas_base as R  # noqa: E402

EXT = R.RES / "extension"
SEEDS = (1050, 1051)


def out_path(k, seed):
    return EXT / ("optical_wine_ext_k%d_s%d.json" % (k, seed))


def record(k, seed, run, s, pp, cpu, res, reused):
    return {"schema": "p0-4.optical_wine_extension", "exploratorio": "post hoc (decision JEV 2026-10-09)", "k": k, "seed": seed,
            "reused_from_primary_process": reused, "sha256_indices": s["sha256_indices"], "profile_copy_sha256": R.sha(pp),
            "worker_status": res["status"], "run": run, "process_cpu_seconds": cpu["process_cpu_seconds"], "wall_seconds": cpu["wall_seconds"],
            "input_sha256": {"wine": R.sha(R.WINE), "profile_original": R.sha(R.PROFILE)}, "code_version": R.code_version()}


def reuse_k0():
    prim = json.loads((R.RES / "optical_wine_k0.json").read_text())
    s = R.get_splits()["wine"][0]
    pp = R.RES / "perfiles" / "wine_profile_k0.json"
    prof = json.loads(pp.read_text())
    assert prim["sha256_indices"] == s["sha256_indices"] and prim["profile_copy_sha256"] == R.sha(pp)
    assert prof["train_indices"] == s["train"] and prof["test_indices"] == s["test"]
    assert prim["input_sha256"]["wine"] == R.sha(R.WINE)
    for seed in SEEDS:
        run = [r for r in prim["runs"] if r["seed"] == seed][0]
        cpu = {"process_cpu_seconds": run["cpu_seconds_seed_training_plus_rebuild"], "wall_seconds": run["cpu_seconds_seed_training_plus_rebuild"]}
        rec = record(0, seed, run, s, pp, cpu, {"status": run["status"]}, True)
        rec["note"] = "tiempo = coste de semilla (entrenamiento+reconstruccion) del worker; el proceso k=0 de 3 semillas costo %.1f s" % prim["process_cpu_seconds"]
        out_path(0, seed).write_text(json.dumps(rec, indent=1), encoding="utf-8")


def one(k, seed):
    s = R.get_splits()["wine"][k]
    prof = json.loads(R.PROFILE.read_text())
    keep = [i for i in prof["initializations"] if i["seed"] == seed]
    assert len(keep) == 1
    p = dict(prof)
    p["train_indices"], p["test_indices"], p["initializations"] = s["train"], s["test"], keep
    (EXT / "perfiles").mkdir(parents=True, exist_ok=True)
    (EXT / "trabajo").mkdir(parents=True, exist_ok=True)
    pp = EXT / "perfiles" / ("wine_profile_k%d_s%d.json" % (k, seed))
    pp.write_text(json.dumps(p, indent=2), encoding="utf-8")
    work = EXT / "trabajo" / ("k%d_s%d" % (k, seed))
    if work.exists():
        shutil.rmtree(work)
    cpuj = EXT / "trabajo" / ("cpu_k%d_s%d.json" % (k, seed))
    r = subprocess.run([sys.executable, str(HERE / "wine_worker_runner.py"), str(cpuj), str(R.WORKER), "--profile", str(pp), "--out", str(work)],
                       cwd=str(R.REPO), capture_output=True, text=True)
    (EXT / "trabajo" / ("log_k%d_s%d.txt" % (k, seed))).write_text(r.stdout[-2000:] + "\n--stderr--\n" + r.stderr[-2000:], encoding="utf-8")
    res = json.loads((work / "result.json").read_text())
    cpu = json.loads(cpuj.read_text())
    q = res["runs"][0]
    run = {"seed": q["seed"], "status": q["status"], "test_accuracy": q["heldout"]["accuracy"], "train_accuracy": q["train"]["accuracy"],
           "initial_train_loss": q["initial_train_loss"], "final_train_loss": q["final_train_loss"],
           "cpu_seconds_seed_training_plus_rebuild": q["cost_seconds"]["seed_training_plus_rebuild"],
           "cpu_seconds_geometry_audits": q["cost_seconds"]["all_geometry_audits"]}
    out_path(k, seed).write_text(json.dumps(record(k, seed, run, s, pp, cpu, res, False), indent=1), encoding="utf-8")
    for f in list(work.rglob("final_virtual_*.json")):
        f.unlink()
    print("ext k=%d seed=%d status=%s acc=%.4f cpu=%.1fs" % (k, seed, q["status"], run["test_accuracy"], cpu["process_cpu_seconds"]), flush=True)


def all_jobs(jobs):
    EXT.mkdir(parents=True, exist_ok=True)
    reuse_k0()
    todo = [(k, sd) for k in range(1, 10) for sd in SEEDS if not out_path(k, sd).exists()]
    running = []
    while todo or running:
        running = [p for p in running if p.poll() is None]
        while todo and len(running) < jobs:
            k, sd = todo.pop(0)
            running.append(subprocess.Popen([sys.executable, str(Path(__file__)), "one", str(k), str(sd)]))
        time.sleep(5)


if __name__ == "__main__":
    if sys.argv[1] == "one":
        one(int(sys.argv[2]), int(sys.argv[3]))
    else:
        all_jobs(int(sys.argv[sys.argv.index("--jobs") + 1]) if "--jobs" in sys.argv else 3)
