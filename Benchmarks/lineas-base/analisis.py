"""P0-4: analisis exactamente segun la seccion 7 del preregistro (y regla de decision de la seccion 2).

Entradas: resultados/baselines.json, optical_iris.json, optical_wine_k*.json, splits.json
Salidas:  resultados/RESULTADOS.json y RESULTADOS.md
"""
import hashlib, json, sys
from pathlib import Path
import numpy as np
from scipy.stats import wilcoxon

HERE = Path(__file__).resolve().parent
RES = HERE / "resultados"
N_BOOT = 10000
BOOT_SEED = 0
EQUIV = 0.02
ALPHA = 0.05


def holm(pvals):
    """Correccion de Holm-Bonferroni (p ajustados, monotonos, recortados a 1), en el orden original."""
    p = np.asarray(pvals, dtype=float)
    m = len(p)
    order = np.argsort(p)
    adj = np.empty(m)
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, (m - rank) * p[i])
        adj[i] = min(1.0, running)
    return adj.tolist()


def bootstrap_ci(diffs, n_boot=N_BOOT, seed=BOOT_SEED):
    """IC95 percentil del promedio de diferencias, remuestreando particiones con reemplazo."""
    d = np.asarray(diffs, dtype=float)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(d), size=(n_boot, len(d)))
    means = d[idx].mean(axis=1)
    return [float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))]


def wilcoxon_p(diffs):
    d = np.asarray(diffs, dtype=float)
    if np.all(d == 0):
        return 1.0, "todas las diferencias son cero"
    r = wilcoxon(d, alternative="two-sided")   # zero_method='wilcox', method='auto'
    return float(r.pvalue), "scipy.stats.wilcoxon bilateral, zero_method=wilcox, method=auto"


def classify(ci, p_holm):
    if ci[0] > 0 and p_holm < ALPHA:
        return "superior"
    if ci[0] >= -EQUIV and ci[1] <= EQUIV:
        return "equivalente"
    return "inferior_o_inconcluso"


def describe(a):
    a = np.asarray(a, dtype=float)
    return {"mean": float(a.mean()), "std": float(a.std(ddof=1)), "min": float(a.min()), "max": float(a.max()), "n": int(len(a))}


def collect():
    base = json.loads((RES / "baselines.json").read_text())
    iris = json.loads((RES / "optical_iris.json").read_text())
    acc = {"iris": {}, "wine": {}}
    acc["iris"]["optico"] = [p["test_accuracy"] for p in sorted(iris["partitions"], key=lambda r: r["k"])]
    wine_files = sorted(RES.glob("optical_wine_k*.json"), key=lambda f: int(f.stem.split("k")[-1]))
    wine = [json.loads(f.read_text()) for f in wine_files]
    assert [w["k"] for w in wine] == list(range(len(wine)))
    # Semillas comunes a todas las particiones (plan de respaldo: solo 1049; k=0 conserva 1050/1051 como dato extra)
    common = set.intersection(*[{r["seed"] for r in w["runs"]} for w in wine])
    acc["wine"]["optico"] = [float(np.mean([r["test_accuracy"] for r in w["runs"] if r["seed"] in common])) for w in wine]
    acc["wine"]["_seeds_used"] = sorted(common)
    for ds in ("iris", "wine"):
        for kind in ("linear", "quadratic"):
            acc[ds][kind] = [r[kind]["test_accuracy"] for r in sorted(base[ds], key=lambda r: r["k"])]
    return acc, wine, iris, base


def analyse():
    acc, wine, iris, base = collect()
    out = {"schema": "p0-4.resultados", "preregistro": "PREREGISTRO-P0-4.md", "bootstrap": {"n": N_BOOT, "seed": BOOT_SEED, "unit": "particion"},
           "decision_rule": {"superior": "IC95 inferior > 0 y p Wilcoxon (Holm sobre 2 lineas base) < 0.05, frente a ambas lineas base",
                             "equivalente": "IC95 contenido en [-0.02, +0.02]", "otro": "inferior_o_inconcluso"},
           "wine_seeds_per_partition": sorted({len(w["runs"]) for w in wine}),
           "wine_seeds_used_in_analysis": acc["wine"]["_seeds_used"],
           "wine_k0_extra_seeds_test_accuracy": {str(r["seed"]): r["test_accuracy"] for r in wine[0]["runs"]}, "datasets": {}}
    for ds in ("iris", "wine"):
        a = acc[ds]
        n = len(a["optico"])
        entry = {"n_partitions": n, "test_accuracy_per_partition": {m: a[m] for m in ("optico", "linear", "quadratic")},
                 "descriptives": {m: describe(a[m]) for m in ("optico", "linear", "quadratic")}, "comparisons": {}}
        raw_p = {}
        for kind in ("linear", "quadratic"):
            d = np.asarray(a["optico"]) - np.asarray(a[kind])
            p, pmeth = wilcoxon_p(d)
            raw_p[kind] = p
            entry["comparisons"][kind] = {"paired_diff_optical_minus_baseline": d.tolist(), "mean_diff": float(d.mean()), "ci95_bootstrap": bootstrap_ci(d),
                                          "wilcoxon_p_raw": p, "wilcoxon_method": pmeth}
        adj = holm([raw_p["linear"], raw_p["quadratic"]])
        for kind, ph in zip(("linear", "quadratic"), adj):
            c = entry["comparisons"][kind]
            c["wilcoxon_p_holm"] = ph
            c["classification"] = classify(c["ci95_bootstrap"], ph)
        labels = [entry["comparisons"][k]["classification"] for k in ("linear", "quadratic")]
        entry["dataset_classification"] = "superior" if all(l == "superior" for l in labels) else \
            "equivalente" if all(l == "equivalente" for l in labels) else "inferior_o_inconcluso"
        entry["dataset_classification_note"] = "superior/equivalente solo si se cumple frente a las dos lineas base; el detalle por linea base esta en comparisons"
        out["datasets"][ds] = entry
    out["cpu_seconds"] = {"iris_optical_total": float(sum(p["cpu_seconds"] for p in iris["partitions"])),
                          "wine_optical_total_process": float(sum(w["process_cpu_seconds"] for w in wine)),
                          "wine_seed_training_cpu_per_run": [r["cpu_seconds_seed_training_plus_rebuild"] for w in wine for r in w["runs"]]}
    out["wine_worker_status"] = [w["worker_status"] for w in wine]
    out["wine_runs_not_pass"] = [{"k": w["k"], "seed": r["seed"], "status": r["status"]} for w in wine for r in w["runs"] if r["status"] != "PASS"]
    # equivalencia worker vs. lineas base propias (verificacion de reimplementacion en Wine)
    chk = []
    for w in wine:
        for kind in ("linear", "quadratic"):
            own = base["wine"][w["k"]][kind]["test_predictions"]
            chk.append(own == w["worker_baseline_test_predictions"][kind])
    out["wine_baseline_predictions_identical_to_worker"] = bool(all(chk))
    return out


def md(r):
    L = ["# Resultados P0-4 (lineas base con igual numero de parametros)", "",
         "Generado por `analisis.py` segun la seccion 7 del preregistro. Exactitud de prueba; diferencia = optico menos linea base; "
         "IC95 bootstrap por particion (10000 remuestreos, semilla 0); Wilcoxon bilateral con Holm sobre las dos lineas base.", ""]
    for ds, e in r["datasets"].items():
        L += ["## %s (%d particiones)" % (ds.capitalize(), e["n_partitions"]), "", "| Modelo | media | desv. | min | max |", "|---|---|---|---|---|"]
        for m, d in e["descriptives"].items():
            L.append("| %s | %.4f | %.4f | %.4f | %.4f |" % (m, d["mean"], d["std"], d["min"], d["max"]))
        L += ["", "| Optico vs | diferencia media | IC95 | p Wilcoxon | p Holm | clasificacion |", "|---|---|---|---|---|---|"]
        for kind, c in e["comparisons"].items():
            L.append("| %s | %+.4f | [%+.4f, %+.4f] | %.4f | %.4f | %s |" % (kind, c["mean_diff"], c["ci95_bootstrap"][0], c["ci95_bootstrap"][1],
                                                                          c["wilcoxon_p_raw"], c["wilcoxon_p_holm"], c["classification"]))
        L += ["", "Clasificacion del conjunto: **%s**" % e["dataset_classification"], ""]
    L += ["Wilcoxon con 10 particiones tiene poca potencia: ausencia de diferencia no prueba equivalencia (preregistro, seccion 9).", ""]
    return "\n".join(L)


if __name__ == "__main__":
    r = analyse()
    body = json.dumps(r, indent=1)
    (RES / "RESULTADOS.json").write_text(body, encoding="utf-8")
    (RES / "RESULTADOS.md").write_text(md(r), encoding="utf-8")
    print(md(r))
    print("sha256 RESULTADOS.json:", hashlib.sha256(body.encode()).hexdigest())
