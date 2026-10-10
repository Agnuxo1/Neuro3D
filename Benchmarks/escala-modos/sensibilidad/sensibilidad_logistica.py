"""Sensibilidad de H3 (P2-10) a la regularizacion de la logistica.
(a) C=1.0 (defecto sklearn). (b) C elegido por validacion cruzada interna (5 pliegues
estratificados, semilla 0) dentro del entrenamiento de cada particion; la prueba no interviene.
Empates en validacion -> menor C (mas regularizado). Codificacion (min-max + norma unitaria)
reajustada en cada pliegue interno solo con sus datos de entrenamiento. Mismos solver/tol que
la linea base original (max_iter=5000, tol=1e-8). Malla: exactitudes ya guardadas (no se reentrena)."""
import json, sys
from pathlib import Path
import numpy as np
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold

HERE = Path(__file__).resolve().parent
ESC = HERE.parent
sys.path.insert(0, str(ESC))
sys.dont_write_bytecode = True
import datos  # noqa: E402

GRID = [0.001, 0.01, 0.1, 1.0, 10.0, 100.0, 1000.0]


def fit_lr(Ztr, ytr, C):
    return LogisticRegression(C=C, max_iter=5000, tol=1e-8).fit(Ztr, ytr)


def boot_ci(d, n=10000, seed=0):
    rng = np.random.default_rng(seed)
    d = np.asarray(d, float)
    m = rng.choice(d, size=(n, len(d)), replace=True).mean(axis=1)
    return [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


def summarize(mesh, lg):
    d = np.asarray(mesh) - np.asarray(lg)
    w = stats.wilcoxon(d, alternative="two-sided") if np.any(d != 0) else None
    return {"logistica_media": float(np.mean(lg)), "malla_media": float(np.mean(mesh)),
            "diferencia_media": float(d.mean()), "ic95_bootstrap": boot_ci(d),
            "wilcoxon_estadistico": None if w is None else float(w.statistic),
            "wilcoxon_p": 1.0 if w is None else float(w.pvalue),
            "victorias_malla": int((d > 0).sum()), "empates": int((d == 0).sum()),
            "derrotas_malla": int((d < 0).sum()),
            "diferencias_por_particion": d.tolist(), "exactitud_logistica": list(map(float, lg)),
            "criterio_H3_soportado": bool(d.mean() >= -0.01 and boot_ci(d)[0] >= -0.03)}


def main():
    X, y = datos.load()
    splits = json.loads((ESC / "resultados" / "splits.json").read_text(encoding="utf-8"))["splits"]
    res = json.loads((ESC / "resultados" / "RESULTADOS_ESCALA.json").read_text(encoding="utf-8"))
    mesh = res["exactitud_prueba_por_particion"]["malla_N64"]
    orig = res["exactitud_prueba_por_particion"]["logistica"]
    acc_a, acc_b, chosen, valtab = [], [], [], []
    for s in splits:
        k = s["k"]; tr = np.array(s["train"]); te = np.array(s["test"])
        Ztr, Zte = datos.encode(X[tr], X[te])
        acc_a.append(float(fit_lr(Ztr, y[tr], 1.0).score(Zte, y[te])))
        skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)
        val = np.zeros(len(GRID))
        for itr, iva in skf.split(tr, y[tr]):
            A, B = datos.encode(X[tr][itr], X[tr][iva])
            for j, C in enumerate(GRID):
                val[j] += fit_lr(A, y[tr][itr], C).score(B, y[tr][iva]) / 5
        j = int(np.argmax(val))  # argmax devuelve el primero = menor C en empate
        chosen.append(GRID[j]); valtab.append(val.tolist())
        acc_b.append(float(fit_lr(Ztr, y[tr], GRID[j]).score(Zte, y[te])))
        print(k, acc_a[-1], GRID[j], acc_b[-1], flush=True)
    out = {"nota": "malla: exactitudes de resultados/RESULTADOS_ESCALA.json (no reentrenada)",
           "rejilla_C": GRID, "validacion": "5 pliegues estratificados internos, semilla 0, empate -> menor C",
           "original_lambda0.001": summarize(mesh, orig),
           "a_C1.0_defecto": summarize(mesh, acc_a),
           "b_C_por_validacion_interna": dict(summarize(mesh, acc_b), C_elegido_por_particion=chosen,
                                              exactitud_validacion_por_C=valtab),
           "comprobacion_original": "C=1/(0.001*n_train)=%.3f" % (1 / (0.001 * len(splits[0]["train"])))}
    (HERE / "resultados_sensibilidad.json").write_text(json.dumps(out, indent=1), encoding="utf-8", newline="\n")
    L = ["# Sensibilidad de H3 a la regularizacion de la logistica (P2-10)", "",
         "Malla N=64: exactitudes guardadas. Diferencia = malla - logistica. IC95 bootstrap (10000, semilla 0). Wilcoxon bilateral.", "",
         "| Variante | Logistica media | Malla media | Dif. media | IC95 | Wilcoxon p | Victorias malla | H3 |", "|---|---|---|---|---|---|---|---|"]
    for name, key in [("Original (L2=0,001, C~0,696)", "original_lambda0.001"), ("(a) C=1,0", "a_C1.0_defecto"), ("(b) C por validacion interna", "b_C_por_validacion_interna")]:
        r = out[key]
        L.append(f"| {name} | {r['logistica_media']:.4f} | {r['malla_media']:.4f} | {r['diferencia_media']:+.4f} | [{r['ic95_bootstrap'][0]:+.4f}, {r['ic95_bootstrap'][1]:+.4f}] | {r['wilcoxon_p']:.4f} | {r['victorias_malla']}/10 (empates {r['empates']}) | {'soportado' if r['criterio_H3_soportado'] else 'no soportado'} |")
    L += ["", "C elegido por particion (b): " + ", ".join(str(c) for c in chosen), "",
          "Metodo: validacion cruzada interna de 5 pliegues sobre el entrenamiento, codificacion reajustada por pliegue, empate -> menor C; prueba no interviene. max_iter=5000, tol=1e-8 en todas."]
    (HERE / "resultados_sensibilidad.md").write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
