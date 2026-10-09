"""Sensibilidad de Iris: optico = MEDIA de los 4 reinicios por particion (seccion 7 del preregistro), en vez del mejor por perdida de train.

Cada reinicio r se entrena con train(x, y, steps=500, seed=r, restarts=1) (identico al reinicio r del original: rng(seed+r)).
Verifica que el mejor reinicio por perdida de train reproduce los parametros de optical_iris.json.
Salida: resultados/SENSIBILIDAD_IRIS.json y .md. Guarda progreso en resultados/sensibilidad_iris_reinicios.json.
"""
import json, sys, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import iris_numeric as IN  # noqa: E402
import analisis as A  # noqa: E402

RES = A.RES
CACHE = RES / "sensibilidad_iris_reinicios.json"


def restarts():
    splits = json.loads((RES / "splits.json").read_text())["iris"]
    orig = json.loads((RES / "optical_iris.json").read_text())["partitions"]
    x, y = IN.load_raw()
    data = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    for s in splits:
        k = str(s["k"])
        if k in data:
            continue
        tr, te = np.array(s["train"]), np.array(s["test"])
        lo, hi = x[tr].min(0), x[tr].max(0)
        xs = (x - lo) / (hi - lo)
        rows = []
        for r in range(4):
            t = time.process_time()
            p = IN.train(xs[tr], y[tr], steps=500, seed=r, restarts=1, log=lambda *_: None)
            l_tr, a_tr = IN.loss_acc(p, xs[tr], y[tr])
            l_te, a_te = IN.loss_acc(p, xs[te], y[te])
            rows.append({"restart": r, "train_loss": float(l_tr), "train_accuracy": float(a_tr), "test_accuracy": float(a_te),
                         "params": p.tolist(), "cpu_seconds": time.process_time() - t})
        data[k] = rows
        CACHE.write_text(json.dumps(data, indent=1), encoding="utf-8")
        print("iris k=%s reinicios test_acc=%s" % (k, [round(q["test_accuracy"], 3) for q in rows]), flush=True)
    return splits, orig, data


def main():
    splits, orig, data = restarts()
    base = json.loads((RES / "baselines.json").read_text())["iris"]
    lin = [b["linear"]["test_accuracy"] for b in sorted(base, key=lambda r: r["k"])]
    quad = [b["quadratic"]["test_accuracy"] for b in sorted(base, key=lambda r: r["k"])]
    maxdiff, best_acc = 0.0, []
    for o in sorted(orig, key=lambda r: r["k"]):
        rows = data[str(o["k"])]
        b = min(rows, key=lambda q: q["train_loss"])   # mismo criterio que train(): primera con menor perdida
        maxdiff = max(maxdiff, float(np.max(np.abs(np.array(b["params"]) - np.array(o["params"])))))
        best_acc.append(b["test_accuracy"])
    assert maxdiff < 1e-12, "no reproduce el mejor reinicio original: %g" % maxdiff
    mean_acc = [float(np.mean([q["test_accuracy"] for q in data[str(k)]])) for k in range(10)]
    out = {"schema": "p0-4.sensibilidad_iris", "etiqueta": "SENSIBILIDAD: optico = media de 4 reinicios (preregistro seccion 7)",
           "best_restart_reproduces_original_max_param_diff": maxdiff,
           "test_accuracy_per_partition": {"optico_media_reinicios": mean_acc, "optico_mejor_reinicio_primario": best_acc, "linear": lin, "quadratic": quad},
           "descriptives": {"optico_media_reinicios": A.describe(mean_acc), "linear": A.describe(lin), "quadratic": A.describe(quad)},
           "restart_test_accuracy": {k: [q["test_accuracy"] for q in v] for k, v in data.items()},
           "restart_cpu_seconds_total": float(sum(q["cpu_seconds"] for v in data.values() for q in v)), "comparisons": {}}
    raw = {}
    for name, ref in (("linear", lin), ("quadratic", quad)):
        d = np.asarray(mean_acc) - np.asarray(ref)
        p, meth = A.wilcoxon_p(d)
        raw[name] = p
        out["comparisons"][name] = {"paired_diff": d.tolist(), "mean_diff": float(d.mean()), "ci95_bootstrap": A.bootstrap_ci(d),
                                    "wilcoxon_p_raw": p, "wilcoxon_method": meth}
    adj = A.holm([raw["linear"], raw["quadratic"]])
    for name, ph in zip(("linear", "quadratic"), adj):
        c = out["comparisons"][name]
        c["wilcoxon_p_holm"] = ph
        c["classification"] = A.classify(c["ci95_bootstrap"], ph)
    labs = [c["classification"] for c in out["comparisons"].values()]
    out["dataset_classification"] = "superior" if all(l == "superior" for l in labs) else "equivalente" if all(l == "equivalente" for l in labs) else "inferior_o_inconcluso"
    prim = json.loads((RES / "RESULTADOS.json").read_text())["datasets"]["iris"]["dataset_classification"]
    out["primary_dataset_classification"] = prim
    out["classification_changes_vs_primary"] = prim != out["dataset_classification"]
    (RES / "SENSIBILIDAD_IRIS.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    L = ["# Sensibilidad de Iris: optico = media de los 4 reinicios", "",
         "Preregistro seccion 7: para el optico se usa la media de reinicios por particion; el analisis primario uso el mejor reinicio por perdida de train. "
         "El mejor reinicio reproduce el original (diferencia maxima de parametros %.1e)." % maxdiff, "",
         "| Modelo | media | desv. | min | max |", "|---|---|---|---|---|"]
    for n, d in out["descriptives"].items():
        L.append("| %s | %.4f | %.4f | %.4f | %.4f |" % (n, d["mean"], d["std"], d["min"], d["max"]))
    L += ["", "| Optico vs | dif. media | IC95 | p Wilcoxon | p Holm | clasificacion |", "|---|---|---|---|---|---|"]
    for k, c in out["comparisons"].items():
        L.append("| %s | %+.4f | [%+.4f, %+.4f] | %.4f | %.4f | %s |" % (k, c["mean_diff"], c["ci95_bootstrap"][0], c["ci95_bootstrap"][1], c["wilcoxon_p_raw"], c["wilcoxon_p_holm"], c["classification"]))
    L += ["", "Clasificacion del conjunto: **%s** (primaria: %s; cambia: %s)" % (out["dataset_classification"], prim, out["classification_changes_vs_primary"]), ""]
    (RES / "SENSIBILIDAD_IRIS.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
