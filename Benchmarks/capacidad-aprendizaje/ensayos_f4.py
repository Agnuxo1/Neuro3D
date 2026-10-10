"""F4: verificacion previa y ensayos C1 a C4 (CPU, un hilo por proceso).

Uso: python ensayos_f4.py verificar | tiempo | ejecutar SHARD NSHARDS
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_v] = "1"
import json, sys, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import datos as D                      # noqa: E402
import familia as F                    # noqa: E402
from entrenar import train, accuracy   # noqa: E402

RES = HERE / "resultados"
PART = RES / "parciales"
ORIG_GRAD = D.REPO / "Benchmarks/escala-modos/resultados/verificacion_gradiente.json"
SIGMAS = [0.0, 0.01, 0.03, 0.1, 0.3]
NDRAW = 5
NRESTART = 10


def wjson(path, obj):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(obj, indent=1), encoding="utf-8", newline="\n")


def verificar():
    out = {}
    # (a) gradiente analitico contra diferencias finitas, 3 configuraciones aleatorias
    cfgs = [(8, 3, 11), (8, 2, 12), (16, 10, 13)]
    a = [F.check(n, K, B=12, T=0.05, seed=seed) for n, K, seed in cfgs]
    out["a_gradiente"] = {"criterio": "error relativo maximo < 1e-6", "casos": a,
                          "max_error_relativo": max(r["error_relativo_norma"] for r in a)}
    out["a_gradiente"]["pasa"] = bool(out["a_gradiente"]["max_error_relativo"] < 1e-6)
    # copia frente al original: mismas configuraciones que escala-modos/verificacion_gradiente.json
    orig = json.loads(ORIG_GRAD.read_text())
    cmp_ = {}
    for key, (n, K) in {"N8": (8, 8), "N8_K4": (8, 4), "N4": (4, 4)}.items():
        mine = F.check(n, K)
        cmp_[key] = {"error_relativo_copia": mine["error_relativo_norma"],
                     "error_relativo_original": orig[key]["error_relativo_norma"],
                     "norma_grad_copia": mine["norma_grad"], "norma_grad_original": orig[key]["norma_grad"],
                     "coincide": bool(abs(mine["error_relativo_norma"] - orig[key]["error_relativo_norma"]) < 1e-12
                                      and abs(mine["norma_grad"] - orig[key]["norma_grad"]) < 1e-12)}
    out["a_copia_vs_original"] = cmp_
    # (b) C1: unitariedad en 20 configuraciones aleatorias, N=8 y N=16; capas == densa
    b = {}
    for n in (8, 16):
        mesh = F.Mesh(n)
        worst, worst_k, worst_layers = 0.0, 0.0, 0.0
        for s in range(20):
            rng = np.random.default_rng(5000 + 100 * n + s)
            p = rng.uniform(0, 2 * np.pi, mesh.n_params)
            err, kap = F.unitarity(mesh, p)
            X = rng.normal(size=(n, 4)) + 1j * rng.normal(size=(n, 4))
            dl = float(np.max(np.abs(F.apply_layers(mesh, F.layer_coeffs(mesh, p), X) - F.dense_matrix(mesh, p) @ X)))
            worst, worst_k, worst_layers = max(worst, err), max(worst_k, abs(kap - 1)), max(worst_layers, dl)
        b[f"N{n}"] = {"configuraciones": 20, "max_error_unitariedad": worst, "max_abs_kappa_menos_1": worst_k,
                      "max_dif_capas_vs_densa": worst_layers, "pasa": bool(worst < 1e-12)}
    out["b_unitariedad"] = {"criterio": "error de unitariedad < 1e-12", **b,
                            "pasa": bool(all(v["pasa"] for v in b.values()))}
    out["pasa"] = bool(out["a_gradiente"]["pasa"] and out["b_unitariedad"]["pasa"])
    wjson(RES / "verificacion_f4.json", out)
    print(json.dumps({"a": out["a_gradiente"]["max_error_relativo"], "copia": {k: v["coincide"] for k, v in cmp_.items()},
                      "b": {k: v["max_error_unitariedad"] for k, v in b.items()}, "pasa": out["pasa"]}))
    return 0 if out["pasa"] else 1


def job(name, k, data, splits):
    X, y = data[name]
    n, K = D.CONFIG[name]
    s = splits[name][k]
    tr, te = np.array(s["train"]), np.array(s["test"])
    Ztr, Zte = D.encode(name, X, tr, te)
    ytr, yte = y[tr], y[te]
    mesh = F.Mesh(n)
    # C2
    G = Ztr.T @ Ztr / len(Ztr)
    ev = np.linalg.eigvalsh(G)

    def kap(ev_):
        return float(ev_[-1] / ev_[0]) if ev_[0] > 1e-12 * ev_[-1] else float("inf")
    c2 = {"kappa_G_N_entradas": kap(ev), "autovalor_min": float(ev[0]), "autovalor_max": float(ev[-1])}
    if name in ("iris", "wine"):
        c2["kappa_G_4_activas"] = kap(np.linalg.eigvalsh(G[:4, :4]))
    # C4 + C1 por reinicio
    runs, phases = [], []
    for seed in range(NRESTART):
        p, loss, cpu = train(Ztr, ytr, n, K, seed)
        err, kp = F.unitarity(mesh, p)
        runs.append({"seed": seed, "train_loss": loss, "train_acc": accuracy(mesh, p, Ztr, ytr, K),
                     "test_acc": accuracy(mesh, p, Zte, yte, K), "cpu_seconds": cpu,
                     "unitarity_err": err, "kappa_U": kp})
        phases.append(p)
    best = int(np.argmin([r["train_loss"] for r in runs]))   # por perdida de entrenamiento; empate: menor semilla
    pb = phases[best]
    # C3
    c3 = {}
    for si, sg in enumerate(SIGMAS):
        accs = []
        for d in range(NDRAW):
            rng = np.random.default_rng([20261009, D.NAMES.index(name), k, si, d])
            pp = pb + sg * rng.standard_normal(pb.shape)
            accs.append(accuracy(mesh, pp, Zte, yte, K))
        c3[str(sg)] = accs
    ctrl = bool(all(a == runs[best]["test_acc"] for a in c3["0.0"]))
    return {"dataset": name, "k": k, "n": n, "K": K, "n_train": int(len(tr)), "n_test": int(len(te)),
            "split_sha256": s["sha256_indices"], "runs": runs, "best_seed": best, "c2": c2,
            "c3_test_acc": c3, "c3_control_sigma0_exacto": ctrl}


def ejecutar(shard, nshards):
    data = D.load_datasets()
    splits = D.get_splits(data)
    jobs = [(nm, k) for nm in D.NAMES for k in range(D.NPART)]
    for i, (nm, k) in enumerate(jobs):
        if i % nshards != shard:
            continue
        f = PART / f"{nm}_k{k}.json"
        if f.exists():
            continue
        t0 = time.time()
        rec = job(nm, k, data, splits)
        wjson(f, rec)
        print(nm, k, "best", rec["best_seed"], "ctrl", rec["c3_control_sigma0_exacto"], "%.0fs" % (time.time() - t0), flush=True)
    (RES / f"hecho_shard{shard}.flag").write_text("ok")


def tiempo():
    data = D.load_datasets()
    splits = D.get_splits(data)
    out = {}
    for nm in ("iris", "digits"):
        X, y = data[nm]
        n, K = D.CONFIG[nm]
        s = splits[nm][0]
        tr, te = np.array(s["train"]), np.array(s["test"])
        Ztr, _ = D.encode(nm, X, tr, te)
        _, loss, cpu = train(Ztr, y[tr], n, K, 0)
        out[nm] = {"cpu_seconds_por_entrenamiento": cpu, "train_loss": loss, "n_train": int(len(tr))}
    est, tot = {}, 0.0
    for nm in D.NAMES:
        ref = out["digits"] if nm == "digits" else out["iris"]
        n_tr = {"iris": 120, "wine": 142, "breast_cancer": 455, "digits": 1437}[nm]
        est[nm] = ref["cpu_seconds_por_entrenamiento"] * (n_tr / ref["n_train"]) * 100   # cota lineal en B
        tot += est[nm]
    out["estimacion_cpu_s_total_conservadora"] = tot
    out["estimacion_por_conjunto_s"] = est
    out["estimacion_horas_con_2_procesos"] = tot / 2 / 3600
    wjson(RES / "tiempo_prueba.json", out)
    print(json.dumps(out))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "verificar":
        sys.exit(verificar())
    elif cmd == "tiempo":
        tiempo()
    elif cmd == "ejecutar":
        ejecutar(int(sys.argv[2]), int(sys.argv[3]))
