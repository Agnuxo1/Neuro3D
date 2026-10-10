"""F4: analisis de resultados parciales, integridad y SHA256SUMS. Solo CPU."""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"
import hashlib, json, platform, sys
from pathlib import Path
import numpy as np
import scipy
import sklearn
from scipy.stats import wilcoxon

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import datos as D  # noqa: E402

RES = HERE / "resultados"
PART = RES / "parciales"
SIGMAS = ["0.0", "0.01", "0.03", "0.1", "0.3"]
NBOOT = 10000


def boot_ci(v, rng):
    v = np.asarray(v, float)
    idx = rng.integers(0, len(v), size=(NBOOT, len(v)))
    m = v[idx].mean(axis=1)
    return [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


def fin(x):
    return None if x == float("inf") else x


def main():
    recs = {nm: [json.loads((PART / f"{nm}_k{k}.json").read_text()) for k in range(D.NPART)] for nm in D.NAMES}
    out = {"versiones": {"python": sys.version.split()[0], "numpy": np.__version__, "scipy": scipy.__version__,
                         "scikit_learn": sklearn.__version__, "plataforma": platform.platform()}}
    # C1
    c1 = {}
    for nm, rs in recs.items():
        errs = [r_["unitarity_err"] for r in rs for r_ in r["runs"]]
        kps = [r_["kappa_U"] for r in rs for r_ in r["runs"]]
        c1[nm] = {"configuraciones": len(errs), "max_error_unitariedad": float(max(errs)),
                  "kappa_min": float(min(kps)), "kappa_max": float(max(kps)), "max_abs_kappa_menos_1": float(max(abs(k - 1) for k in kps))}
    c1["pasa_todo"] = bool(all(v["max_error_unitariedad"] < 1e-12 for v in c1.values() if isinstance(v, dict)))
    out["C1"] = c1
    # C2
    c2 = {}
    for nm, rs in recs.items():
        k_ = [r["c2"]["kappa_G_N_entradas"] for r in rs]
        d = {"kappa_G_N_entradas_por_particion": [fin(x) for x in k_]}
        if all(np.isfinite(k_)):
            d.update(media=float(np.mean(k_)), mediana=float(np.median(k_)))
        else:
            d.update(media=None, mediana=None, nota="Gram singular (modos de entrada a cero): kappa infinito")
        if nm in ("iris", "wine"):
            k4 = [r["c2"]["kappa_G_4_activas"] for r in rs]
            d["kappa_G_4_activas"] = {"media": float(np.mean(k4)), "mediana": float(np.median(k4))}
        c2[nm] = d
    out["C2"] = c2
    # control sigma = 0
    out["control_sigma0_exacto"] = {nm: bool(all(r["c3_control_sigma0_exacto"] for r in rs)) for nm, rs in recs.items()}
    # C3
    rng = np.random.default_rng(0)
    c3, h3a, h3b = {}, {}, {}
    for nm, rs in recs.items():
        acc = {s: np.array([np.mean(r["c3_test_acc"][s]) for r in rs]) for s in SIGMAS}   # por particion
        base = acc["0.0"]
        d = {"exactitud_media": {s: float(acc[s].mean()) for s in SIGMAS},
             "exactitud_sd_entre_particiones": {s: float(acc[s].std(ddof=1)) for s in SIGMAS},
             "perdida": {}}
        for s in SIGMAS[1:]:
            loss = base - acc[s]
            d["perdida"][s] = {"media": float(loss.mean()), "ic95_bootstrap": boot_ci(loss, rng)}
        c3[nm] = d
        h3a[nm] = {"perdida_media_sigma_0.03": d["perdida"]["0.03"]["media"], "ic95": d["perdida"]["0.03"]["ic95_bootstrap"],
                   "cumple": bool(d["perdida"]["0.03"]["media"] < 0.01)}
        pares = []
        for a, b in zip(SIGMAS[:-1], SIGMAS[1:]):
            pares.append({"de": a, "a": b, "acc_prev": float(acc[a].mean()), "acc_sig": float(acc[b].mean()),
                          "incremento": float(acc[b].mean() - acc[a].mean()), "cumple": bool(acc[b].mean() <= acc[a].mean() + 0.005)})
        h3b[nm] = {"pares": pares, "cumple": bool(all(p["cumple"] for p in pares))}
    out["C3"] = c3
    out["H3a"] = {"por_conjunto": h3a, "cumple": bool(all(v["cumple"] for v in h3a.values()))}
    out["H3b"] = {"por_conjunto": h3b, "cumple": bool(all(v["cumple"] for v in h3b.values()))}
    # C4
    c4, h4 = {}, {}
    for nm, rs in recs.items():
        best = np.array([r["runs"][r["best_seed"]]["test_acc"] for r in rs])
        med = np.array([np.median([x["test_acc"] for x in r["runs"]]) for r in rs])
        diff = best - med
        try:
            w = wilcoxon(best, med, alternative="two-sided")
            wp = float(w.pvalue)
            wnote = None
        except ValueError as e:
            wp, wnote = None, str(e)
        rng_c4 = np.random.default_rng(0)
        ci = boot_ci(diff, rng_c4)
        allacc = [x["test_acc"] for r in rs for x in r["runs"]]
        c4[nm] = {"mejor_media": float(best.mean()), "mediana_reinicios_media": float(med.mean()),
                  "diferencia_por_particion": [float(x) for x in diff], "diferencia_media": float(diff.mean()),
                  "ic95_bootstrap": ci, "wilcoxon_p": wp, "wilcoxon_nota": wnote,
                  "sd_entre_reinicios_media": float(np.mean([np.std([x["test_acc"] for x in r["runs"]], ddof=1) for r in rs])),
                  "rango_acc_prueba_reinicios": [float(min(allacc)), float(max(allacc))],
                  "semillas_mejor": [r["best_seed"] for r in rs]}
        h4[nm] = {"diferencia_media_signo": float(diff.mean()), "abs": float(abs(diff.mean())), "cumple": bool(abs(diff.mean()) < 0.01)}
    out["C4"] = c4
    out["H4"] = {"por_conjunto": h4, "cumple_todos": bool(all(v["cumple"] for v in h4.values())),
                 "interpretacion": "|media sobre particiones de (mejor - mediana)| < 0,01; mejor = menor perdida de entrenamiento"}
    # tiempos
    tm = {}
    for nm, rs in recs.items():
        t = [x["cpu_seconds"] for r in rs for x in r["runs"]]
        tm[nm] = {"n": len(t), "media_s": float(np.mean(t)), "mediana_s": float(np.median(t)), "total_s": float(np.sum(t))}
    out["tiempos_cpu_entrenamiento"] = tm
    # particiones e integridad
    data = D.load_datasets()
    sp = D.get_splits(data)
    out["particiones"] = {nm: {"n_particiones": len(sp[nm]), "sha256_indices": [s["sha256_indices"] for s in sp[nm]]} for nm in D.NAMES}
    out["particiones"]["digits_vs_escala_modos"] = D.compare_with_p210(sp)
    for nm in D.NAMES:
        for r, s in zip(recs[nm], sp[nm]):
            assert r["split_sha256"] == s["sha256_indices"]
    (RES / "splits_f4.json").write_text(json.dumps({nm: sp[nm] for nm in ("breast_cancer", "digits")}), encoding="utf-8", newline="\n")
    out["integridad"] = {
        "scripts_sha256": {f: D.sha_file(HERE / f) for f in ("familia.py", "datos.py", "entrenar.py", "ensayos_f4.py", "analisis_f4.py")},
        "entradas_sha256": {"splits_P0-4": D.sha_file(D.SPLITS_P04), "iris.csv": D.sha_file(D.IRIS_CSV), "wine.data": D.sha_file(D.WINE),
                            "splits_f4.json": D.sha_file(RES / "splits_f4.json")},
        "datos_cargados_sha256": {nm: D.sha_xy(*data[nm]) for nm in D.NAMES}}
    (RES / "RESULTADOS_F4.json").write_text(json.dumps(out, indent=1), encoding="utf-8", newline="\n")
    # SHA256SUMS (LF, rutas relativas a resultados/)
    lines = []
    for p in sorted(RES.rglob("*")):
        if p.is_file() and p.name not in ("SHA256SUMS.txt",) and not p.name.endswith(".flag"):
            lines.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(RES).as_posix()}")
    (RES / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"C1": c1["pasa_todo"], "H3a": out["H3a"]["cumple"], "H3b": out["H3b"]["cumple"], "H4": out["H4"]["cumple_todos"]}))


if __name__ == "__main__":
    main()
