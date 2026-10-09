"""EXPLORATORIO post hoc (decision JEV 2026-10-09): Wine con semillas 1049, 1050, 1051 promediadas por particion.

Reutiliza las funciones de analisis.py (sin modificarlo). El analisis primario (semilla 1049) no cambia.
Salida: resultados/RESULTADOS_EXTENSION.json y .md
"""
import json, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import analisis as A  # noqa: E402

RES = A.RES
TAG = "EXPLORATORIO post hoc (decisión JEV 2026-10-09)"
SEEDS = (1049, 1050, 1051)


def load():
    base = json.loads((RES / "baselines.json").read_text())["wine"]
    base = sorted(base, key=lambda r: r["k"])
    acc = {s: [] for s in SEEDS}
    for k in range(10):
        prim = json.loads((RES / ("optical_wine_k%d.json" % k)).read_text())
        acc[1049].append([r for r in prim["runs"] if r["seed"] == 1049][0]["test_accuracy"])
        for s in (1050, 1051):
            e = json.loads((RES / "extension" / ("optical_wine_ext_k%d_s%d.json" % (k, s))).read_text())
            assert e["k"] == k and e["seed"] == s and e["sha256_indices"] == prim["sha256_indices"]
            acc[s].append(e["run"]["test_accuracy"])
    lin = [b["linear"]["test_accuracy"] for b in base]
    quad = [b["quadratic"]["test_accuracy"] for b in base]
    return acc, lin, quad


def compare(opt, ref):
    d = np.asarray(opt) - np.asarray(ref)
    p, meth = A.wilcoxon_p(d)
    return d, p, meth


def analyse():
    acc, lin, quad = load()
    mat = np.array([acc[s] for s in SEEDS])           # semillas x particiones
    avg = mat.mean(axis=0)
    out = {"schema": "p0-4.resultados_extension", "etiqueta": TAG, "seeds": list(SEEDS),
           "nota": "Analisis exploratorio decidido tras observar el split k=0; no sustituye al analisis primario (semilla 1049)."}
    comps, raw = {}, {}
    for name, ref in (("linear", lin), ("quadratic", quad)):
        d, p, meth = compare(avg, ref)
        raw[name] = p
        comps[name] = {"paired_diff_mean_of_3_seeds_minus_baseline": d.tolist(), "mean_diff": float(d.mean()), "ci95_bootstrap": A.bootstrap_ci(d),
                       "wilcoxon_p_raw": p, "wilcoxon_method": meth}
    adj = A.holm([raw["linear"], raw["quadratic"]])
    for name, ph in zip(("linear", "quadratic"), adj):
        comps[name]["wilcoxon_p_holm"] = ph
        comps[name]["classification"] = A.classify(comps[name]["ci95_bootstrap"], ph)
    labels = [comps[k]["classification"] for k in comps]
    out["wine_mean_of_3_seeds"] = {"test_accuracy_per_partition": avg.tolist(), "descriptives": A.describe(avg),
                                   "descriptives_linear": A.describe(lin), "descriptives_quadratic": A.describe(quad), "comparisons": comps,
                                   "dataset_classification": "superior" if all(l == "superior" for l in labels) else
                                   "equivalente" if all(l == "equivalente" for l in labels) else "inferior_o_inconcluso"}
    per_seed = {}
    for s in SEEDS:
        a = np.asarray(acc[s])
        per_seed[str(s)] = {"mean_accuracy": float(a.mean()), "std": float(a.std(ddof=1)),
                            "mean_diff_vs_linear": float((a - lin).mean()), "partitions_beating_linear": int(np.sum(a > lin)),
                            "partitions_tying_linear": int(np.sum(a == lin)), "partitions_losing_to_linear": int(np.sum(a < lin)),
                            "mean_diff_vs_quadratic": float((a - quad).mean()), "partitions_beating_quadratic": int(np.sum(a > quad)),
                            "test_accuracy_per_partition": a.tolist()}
    out["per_seed"] = per_seed
    sd = mat.std(axis=0, ddof=1)
    out["seed_std_per_partition"] = sd.tolist()
    out["seed_std_mean_over_partitions"] = float(sd.mean())
    out["seed_spread_per_partition_max_minus_min"] = (mat.max(axis=0) - mat.min(axis=0)).tolist()
    return out


def md(r):
    w = r["wine_mean_of_3_seeds"]
    L = ["# Resultados de la extension - Wine, 3 semillas (%s)" % TAG, "",
         "**%s.** Decidido despues de observar el split k=0. El analisis primario (semilla 1049, `RESULTADOS.md`) no cambia." % TAG, "",
         "Promedio de las semillas 1049, 1050 y 1051 por particion; IC95 bootstrap por particion (10000, semilla 0); Wilcoxon bilateral; Holm sobre las dos lineas base.", "",
         "| Modelo | media | desv. | min | max |", "|---|---|---|---|---|"]
    for n, d in (("optico (media 3 semillas)", w["descriptives"]), ("lineal", w["descriptives_linear"]), ("cuadratico", w["descriptives_quadratic"])):
        L.append("| %s | %.4f | %.4f | %.4f | %.4f |" % (n, d["mean"], d["std"], d["min"], d["max"]))
    L += ["", "| Optico vs | dif. media | IC95 | p Wilcoxon | p Holm | clasificacion |", "|---|---|---|---|---|---|"]
    for k, c in w["comparisons"].items():
        L.append("| %s | %+.4f | [%+.4f, %+.4f] | %.4f | %.4f | %s |" % (k, c["mean_diff"], c["ci95_bootstrap"][0], c["ci95_bootstrap"][1],
                                                                      c["wilcoxon_p_raw"], c["wilcoxon_p_holm"], c["classification"]))
    L += ["", "Clasificacion del conjunto: **%s**" % w["dataset_classification"], "", "## Por semilla", "",
          "| Semilla | exactitud media | dif. vs lineal | particiones que superan a lineal (empatan/pierden) | dif. vs cuadratico | superan a cuadratico |", "|---|---|---|---|---|---|"]
    for s, d in r["per_seed"].items():
        L.append("| %s | %.4f | %+.4f | %d (%d/%d) | %+.4f | %d |" % (s, d["mean_accuracy"], d["mean_diff_vs_linear"], d["partitions_beating_linear"],
                                                                  d["partitions_tying_linear"], d["partitions_losing_to_linear"], d["mean_diff_vs_quadratic"], d["partitions_beating_quadratic"]))
    L += ["", "Desviacion tipica entre semillas por particion: " + ", ".join("%.3f" % v for v in r["seed_std_per_partition"]) +
          " (media %.4f)." % r["seed_std_mean_over_partitions"], ""]
    return "\n".join(L)


if __name__ == "__main__":
    r = analyse()
    (RES / "RESULTADOS_EXTENSION.json").write_text(json.dumps(r, indent=1), encoding="utf-8")
    (RES / "RESULTADOS_EXTENSION.md").write_text(md(r), encoding="utf-8")
    print(md(r))
