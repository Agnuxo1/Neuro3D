"""P1-5: analisis segun secciones 7 y 8 de PREREGISTRO-P1-5.md. No ejecuta ningun modelo nuevo (solo lee resultados guardados).

Entradas: resultados/benchmark_v1_raw.json y, para el claim optico, los resultados ya guardados de P0-4
(Benchmarks/lineas-base/resultados: sensibilidad_iris_reinicios.json, optical_iris.json, optical_wine_k*.json, extension/).
Salidas: resultados/RESULTADOS_BENCHMARK_V1.json, .md y SHA256SUMS.txt
"""
import hashlib, json, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
RES = HERE / "resultados"
P04 = REPO / "Benchmarks/lineas-base"
sys.path.insert(0, str(P04))
import analisis as A            # noqa: E402  (helpers de P0-4: holm, bootstrap_ci, wilcoxon_p, classify, describe)
import analisis_extension as AE  # noqa: E402  (carga de las tres semillas de Wine)

DATASETS = ["iris", "wine", "breast_cancer", "digits"]
NAMES = {"iris": "Iris", "wine": "Wine", "breast_cancer": "Breast Cancer", "digits": "Digits"}
DESC = {"B1": "softmax lineal L2=0.001", "B2": "SVM RBF C=1 gamma=scale", "B3": "random forest 200 arboles", "B4": "MLP (32,)",
        "B5": "softmax lineal P0-4", "B6": "softmax cuadratico P0-4"}


def sha_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def optical_series():
    """Iris: media de los 4 reinicios por particion (P0-4 seccion 7; el optico de Iris no tiene semillas 1049-1051).
    Wine: media de las semillas 1049, 1050 y 1051 por particion (extension de P0-4)."""
    reinicios = json.loads((P04 / "resultados/sensibilidad_iris_reinicios.json").read_text())
    iris_mean = [float(np.mean([r["test_accuracy"] for r in reinicios[str(k)]])) for k in range(10)]
    iris_best = [p["test_accuracy"] for p in sorted(json.loads((P04 / "resultados/optical_iris.json").read_text())["partitions"], key=lambda r: r["k"])]
    acc, _, _ = AE.load()
    wine_mean = np.mean([acc[s] for s in AE.SEEDS], axis=0).tolist()
    return {"iris": {"mean": iris_mean, "primary_best_restart": iris_best, "n_per_partition": 4, "unit": "reinicios"},
            "wine": {"mean": wine_mean, "n_per_partition": 3, "unit": "semillas 1049,1050,1051",
                     "per_seed": {str(s): acc[s] for s in AE.SEEDS}}}


def claim(opt, b5, b6):
    comps, raw = {}, {}
    for tag, ref in (("B5", b5), ("B6", b6)):
        d = np.asarray(opt) - np.asarray(ref)
        p, meth = A.wilcoxon_p(d)
        raw[tag] = p
        comps[tag] = {"paired_diff_optical_minus_baseline": d.tolist(), "mean_diff": float(d.mean()), "ci95_bootstrap": A.bootstrap_ci(d),
                      "wilcoxon_p_raw": p, "wilcoxon_method": meth}
    adj = A.holm([raw["B5"], raw["B6"]])
    for tag, ph in zip(("B5", "B6"), adj):
        comps[tag]["wilcoxon_p_holm"] = ph
        comps[tag]["classification"] = A.classify(comps[tag]["ci95_bootstrap"], ph)
    labels = [comps[t]["classification"] for t in ("B5", "B6")]
    cls = "superior" if all(l == "superior" for l in labels) else "equivalente" if all(l == "equivalente" for l in labels) else "inferior_o_inconcluso"
    return comps, cls


def analyse():
    raw = json.loads((RES / "benchmark_v1_raw.json").read_text())
    opt = optical_series()
    out = {"schema": "p1-5.resultados", "preregistro": "PREREGISTRO-P1-5.md (+ Enmienda 1)",
           "bootstrap": {"n": A.N_BOOT, "seed": A.BOOT_SEED, "unit": "particion"},
           "versions": raw["versions"], "input_sha256": {"benchmark_v1_raw.json": sha_file(RES / "benchmark_v1_raw.json"), **raw["input_sha256"],
                                                          "p0_4_optical_inputs": {f: sha_file(P04 / "resultados" / f) for f in
                                                                                  ("sensibilidad_iris_reinicios.json", "optical_iris.json", "RESULTADOS.json", "RESULTADOS_EXTENSION.json")}},
           "code_sha256": {**raw["code_sha256"], "Benchmarks/benchmark-v1/analisis_benchmark_v1.py": sha_file(__file__),
                           "Benchmarks/lineas-base/analisis.py": sha_file(P04 / "analisis.py"),
                           "Benchmarks/lineas-base/analisis_extension.py": sha_file(P04 / "analisis_extension.py")},
           "verification_generic_vs_fit_baseline": raw["verification_generic_vs_fit_baseline"],
           "b5_b6_predictions_identical_to_p0_4": raw["b5_b6_predictions_identical_to_p0_4"],
           "datasets": {}}
    for ds in DATASETS:
        d = raw["datasets"][ds]
        models = d["models"]
        acc = {m: [r["test_accuracy"] for r in sorted(rs, key=lambda r: r["k"])] for m, rs in models.items()}
        bal = {m: [r["balanced_accuracy"] for r in sorted(rs, key=lambda r: r["k"])] for m, rs in models.items()}
        cpu = {m: [r["cpu_seconds"] for r in sorted(rs, key=lambda r: r["k"])] for m, rs in models.items()}
        e = {"n_partitions": 10, "data_sha256": d["data_sha256"], "n_classes": d["n_classes"], "n_features": d["n_features"],
             "partition_sha256": [s["sha256_indices"] for s in d["splits"]], "n_train": d["splits"][0]["n_train"], "n_test": d["splits"][0]["n_test"],
             "test_accuracy_per_partition": acc, "balanced_accuracy_per_partition": bal,
             "descriptives_accuracy": {m: A.describe(v) for m, v in acc.items()},
             "descriptives_balanced_accuracy": {m: A.describe(v) for m, v in bal.items()},
             "cpu_seconds": {m: {"mean_per_partition": float(np.mean(v)), "total": float(np.sum(v)), "max": float(np.max(v))} for m, v in cpu.items()},
             "b1_convergence": {"converged_partitions": int(sum(r["converged"] for r in models["B1"])), "max_gradient_abs_worst": float(max(r["max_gradient_abs"] for r in models["B1"]))},
             "b4_convergence_warnings": int(sum(r["convergence_warning"] for r in models["B4"]))}
        best = max(acc, key=lambda m: (np.mean(acc[m]), -list(acc).index(m)))
        e["best_baseline_by_mean_accuracy"] = best
        diffs = {}
        raw_p = []
        for m in acc:
            dd = np.asarray(acc[m]) - np.asarray(acc[best])
            p, meth = A.wilcoxon_p(dd)
            diffs[m] = {"paired_diff_vs_best": dd.tolist(), "mean_diff": float(dd.mean()), "ci95_bootstrap": A.bootstrap_ci(dd) if m != best else [0.0, 0.0],
                        "wilcoxon_p_raw_descriptive": p if m != best else None, "is_best": m == best}
        e["diff_vs_best_baseline"] = diffs
        if ds in opt:
            o = opt[ds]
            comps, cls = claim(o["mean"], acc["B5"], acc["B6"])
            e["optical"] = {"series_used": o["unit"] + " (media por particion)", "n_per_partition": o["n_per_partition"],
                            "test_accuracy_per_partition": o["mean"], "descriptives": A.describe(o["mean"]),
                            "comparisons_vs_B5_B6": comps, "dataset_classification": cls,
                            "descriptive_diff_vs_B1_B4": {m: {"mean_diff": float(np.mean(np.asarray(o["mean"]) - np.asarray(acc[m]))),
                                                              "ci95_bootstrap": A.bootstrap_ci(np.asarray(o["mean"]) - np.asarray(acc[m]))} for m in ("B1", "B2", "B3", "B4")}}
            if ds == "iris":
                e["optical"]["sensitivity_primary_best_restart"] = {"descriptives": A.describe(o["primary_best_restart"]),
                                                                    "claim_vs_B5_B6": claim(o["primary_best_restart"], acc["B5"], acc["B6"])[1]}
            if ds == "wine":
                e["optical"]["per_seed_mean_accuracy"] = {s: float(np.mean(v)) for s, v in o["per_seed"].items()}
        out["datasets"][ds] = e
    out["cpu_seconds_total_by_dataset"] = {ds: float(sum(v["total"] for v in out["datasets"][ds]["cpu_seconds"].values())) for ds in DATASETS}
    out["total_wall_seconds_run"] = raw["total_wall_seconds"]
    return out


def md(r):
    L = ["# Resultados P1-5 · benchmark v1", "",
         "Generado por `analisis_benchmark_v1.py` segun `PREREGISTRO-P1-5.md` (con Enmienda 1). Exactitud de prueba; 10 particiones por conjunto; "
         "IC95 bootstrap por particion (10000 remuestreos, semilla 0). Los resultados se publican tal cual.", "",
         "Entorno: " + ", ".join("%s %s" % (k, v.split()[0] if k == "python" else v) for k, v in r["versions"].items() if k != "platform"), "",
         "Verificacion de la version multiclase frente a `fit_baseline` (max. diferencia absoluta de probabilidades, tolerancia 1e-6): "
         + ", ".join("%s=%.1e" % (k, v) for k, v in r["verification_generic_vs_fit_baseline"]["max_abs_probability_difference"].items()), ""]
    for ds in DATASETS:
        e = r["datasets"][ds]
        L += ["## %s (%d atributos, %d clases, train/test %d/%d)" % (NAMES[ds], e["n_features"], e["n_classes"], e["n_train"], e["n_test"]), "",
              "| Modelo | exactitud media | desv. | min | max | exact. equilibrada media | CPU s/particion | dif. vs mejor | IC95 dif. |", "|---|---|---|---|---|---|---|---|---|"]
        for m, dsc in e["descriptives_accuracy"].items():
            df = e["diff_vs_best_baseline"][m]
            L.append("| %s %s | %.4f | %.4f | %.4f | %.4f | %.4f | %.3f | %s | %s |" % (
                m, DESC[m] + (" (mejor)" if df["is_best"] else ""), dsc["mean"], dsc["std"], dsc["min"], dsc["max"],
                e["descriptives_balanced_accuracy"][m]["mean"], e["cpu_seconds"][m]["mean_per_partition"],
                "-" if df["is_best"] else "%+.4f" % df["mean_diff"], "-" if df["is_best"] else "[%+.4f, %+.4f]" % tuple(df["ci95_bootstrap"])))
        L += ["", "Mejor linea base por exactitud media: **%s**. B1 convergio en %d/10 particiones (gradiente maximo peor %.1e); B4 con aviso de convergencia en %d/10."
              % (e["best_baseline_by_mean_accuracy"], e["b1_convergence"]["converged_partitions"], e["b1_convergence"]["max_gradient_abs_worst"], e["b4_convergence_warnings"]), ""]
        if "optical" in e:
            o = e["optical"]
            L += ["### Claim optico en %s (serie: %s)" % (NAMES[ds], o["series_used"]), "",
                  "Optico: media %.4f, desv. %.4f, min %.4f, max %.4f." % (o["descriptives"]["mean"], o["descriptives"]["std"], o["descriptives"]["min"], o["descriptives"]["max"]), "",
                  "| Optico vs | dif. media | IC95 | p Wilcoxon | p Holm | clasificacion |", "|---|---|---|---|---|---|"]
            for tag, c in o["comparisons_vs_B5_B6"].items():
                L.append("| %s | %+.4f | [%+.4f, %+.4f] | %.4f | %.4f | %s |" % (tag, c["mean_diff"], c["ci95_bootstrap"][0], c["ci95_bootstrap"][1], c["wilcoxon_p_raw"], c["wilcoxon_p_holm"], c["classification"]))
            L += ["", "Clasificacion del conjunto: **%s**." % o["dataset_classification"]]
            if "sensitivity_primary_best_restart" in o:
                s = o["sensitivity_primary_best_restart"]
                L += ["Sensibilidad (analisis primario de P0-4, mejor reinicio por perdida de entrenamiento): media %.4f, clasificacion %s." % (s["descriptives"]["mean"], s["claim_vs_B5_B6"])]
            if "per_seed_mean_accuracy" in o:
                L += ["Exactitud media por semilla: " + ", ".join("%s=%.4f" % kv for kv in o["per_seed_mean_accuracy"].items()) + "."]
            L += ["Diferencia descriptiva del optico frente a B1-B4 (no es criterio de decision): " +
                  "; ".join("%s %+.4f [%+.4f, %+.4f]" % (m, v["mean_diff"], v["ci95_bootstrap"][0], v["ci95_bootstrap"][1]) for m, v in o["descriptive_diff_vs_B1_B4"].items()) + ".", ""]
    L += ["## Notas", "",
          "- Breast Cancer y Digits: sin modelo optico (alcance del preregistro, seccion 2).",
          "- Las particiones se solapan: los IC subestiman la incertidumbre. Con 10 particiones Wilcoxon tiene poca potencia.",
          "- Iris y Wine ya se ejecutaron en P0-4; las predicciones de B5/B6 recalculadas son identicas a las de P0-4: %s." % r["b5_b6_predictions_identical_to_p0_4"],
          "- Tiempo de CPU total (s, suma de modelos y particiones): " + ", ".join("%s %.1f" % (NAMES[k], v) for k, v in r["cpu_seconds_total_by_dataset"].items()) + ".", ""]
    return "\n".join(L)


if __name__ == "__main__":
    r = analyse()
    (RES / "RESULTADOS_BENCHMARK_V1.json").write_text(json.dumps(r, indent=1), encoding="utf-8")
    (RES / "RESULTADOS_BENCHMARK_V1.md").write_text(md(r), encoding="utf-8")
    names = ["benchmark_v1_raw.json", "RESULTADOS_BENCHMARK_V1.json", "RESULTADOS_BENCHMARK_V1.md"]
    (RES / "SHA256SUMS.txt").write_text("".join("%s  %s\n" % (sha_file(RES / n), n) for n in names), encoding="utf-8")
    print(md(r))
