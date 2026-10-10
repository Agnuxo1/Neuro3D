"""Analisis y decision de P2-10 segun la seccion 7 del preregistro."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy import stats

HERE = Path(__file__).parent
RES = HERE / "resultados"


def boot_ci(d, n=10000, seed=0):
    rng = np.random.default_rng(seed)
    d = np.asarray(d, float)
    means = rng.choice(d, size=(n, len(d)), replace=True).mean(axis=1)
    return [float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))]


def wilcoxon(d):
    d = np.asarray(d, float)
    if np.all(d == 0):
        return {"estadistico": None, "p": 1.0, "nota": "todas las diferencias son cero"}
    r = stats.wilcoxon(d, alternative="two-sided")
    return {"estadistico": float(r.statistic), "p": float(r.pvalue),
            "nota": "exacto, n=10" if np.all(d != 0) else "con ceros (zero_method=wilcox)"}


def loglog(N, y):
    lx, ly = np.log(np.asarray(N, float)), np.log(np.asarray(y, float))
    r = stats.linregress(lx, ly)
    tcrit = stats.t.ppf(0.975, len(lx) - 2)
    return {"pendiente": float(r.slope), "error_estandar": float(r.stderr),
            "ic95": [float(r.slope - tcrit * r.stderr), float(r.slope + tcrit * r.stderr)],
            "gl": int(len(lx) - 2), "r2": float(r.rvalue ** 2)}


def main():
    raw = json.loads((RES / "resultados_raw.json").read_text(encoding="utf-8"))
    nk = 10
    mesh_sel = []
    for k in range(nk):
        rs = [r for r in raw["malla"] if r["k"] == k]
        best = min(rs, key=lambda r: r["train_loss"])  # seleccion por perdida de entrenamiento
        mesh_sel.append(best)
    acc_mesh = np.array([r["test_acc"] for r in mesh_sel])
    base = {b["k"]: b for b in raw["lineas_base"]}
    acc_lg = np.array([base[k]["logistica"]["test_acc"] for k in range(nk)])
    acc_ml = np.array([base[k]["mlp"]["test_acc"] for k in range(nk)])
    d_lg, d_ml = acc_mesh - acc_lg, acc_mesh - acc_ml
    mean_lg, ci_lg = float(d_lg.mean()), boot_ci(d_lg)
    mean_ml, ci_ml = float(d_ml.mean()), boot_ci(d_ml)
    soportado = bool(mean_lg >= -0.01 and ci_lg[0] >= -0.03)
    cpu = [r["cpu_seconds"] for r in raw["malla"]]

    sc = raw["escala"]
    N = [r["N"] for r in sc]
    h2 = {
        "criterio": "pendiente p del tiempo por entrada entre 1,8 y 2,2 (ajuste log-log, N=8,16,32,64)",
        "tiempo_por_entrada": loglog(N, [r["t_entrada_s"] for r in sc]),
        "exploratorio_tiempo_por_entrada_en_lote_1000": loglog(N, [r["t_entrada_lote_s"] for r in sc]),
        "memoria_coeficientes": loglog(N, [r["bytes_coeficientes"] for r in sc]),
        "memoria_matriz_densa": loglog(N, [r["bytes_matriz_densa"] for r in sc]),
        "puntos": [{"N": r["N"], "t_entrada_us": r["t_entrada_s"] * 1e6,
                    "t_entrada_lote_us": r["t_entrada_lote_s"] * 1e6,
                    "bytes_coeficientes": r["bytes_coeficientes"],
                    "bytes_matriz_densa": r["bytes_matriz_densa"]} for r in sc],
    }
    t = h2["tiempo_por_entrada"]
    h2["p_en_rango_estimacion_puntual"] = bool(1.8 <= t["pendiente"] <= 2.2)
    h2["ic95_dentro_del_rango"] = bool(t["ic95"][0] >= 1.8 and t["ic95"][1] <= 2.2)
    tl = h2["exploratorio_tiempo_por_entrada_en_lote_1000"]
    h2["lote_p_en_rango_estimacion_puntual"] = bool(1.8 <= tl["pendiente"] <= 2.2)

    out = {
        "versiones": raw["versiones"], "config": raw["config"],
        "exactitud_prueba_por_particion": {
            "malla_N64": acc_mesh.tolist(), "logistica": acc_lg.tolist(), "mlp48": acc_ml.tolist(),
            "malla_semilla_elegida": [r["phase_seed"] for r in mesh_sel]},
        "medias": {"malla_N64": float(acc_mesh.mean()), "logistica": float(acc_lg.mean()),
                   "mlp48": float(acc_ml.mean()),
                   "sd_malla": float(acc_mesh.std(ddof=1)), "sd_logistica": float(acc_lg.std(ddof=1)),
                   "sd_mlp48": float(acc_ml.std(ddof=1))},
        "H3": {"criterio": "diferencia media malla-logistica >= -0,01 y IC95 inferior >= -0,03 => soportado",
               "diferencia_media": mean_lg, "ic95_bootstrap": ci_lg, "bootstrap": "10000 remuestreos, semilla 0",
               "wilcoxon_bilateral": wilcoxon(d_lg),
               "diferencias_por_particion": d_lg.tolist(),
               "decision": "soportado" if soportado else "no soportado"},
        "control_MLP": {"nota": "sin criterio de decision", "diferencia_media": mean_ml,
                        "ic95_bootstrap": ci_ml, "wilcoxon_bilateral": wilcoxon(d_ml),
                        "diferencias_por_particion": d_ml.tolist()},
        "H2": h2,
        "cpu_entrenamiento_malla_s": {"n": len(cpu), "min": float(min(cpu)), "mediana": float(np.median(cpu)),
                                      "media": float(np.mean(cpu)), "max": float(max(cpu)),
                                      "total": float(sum(cpu))},
        "avisos_convergencia": {
            "logistica": int(sum(len(b["logistica"]["avisos"]) for b in raw["lineas_base"])),
            "mlp_particiones_con_aviso": [b["k"] for b in raw["lineas_base"] if b["mlp"]["avisos"]]},
        "entrenamiento_malla_train_acc_media_elegida": float(np.mean([r["train_acc"] for r in mesh_sel])),
        "limites": ["CPU sin GPU; no se afirma nada sobre la geometria de Neuro3D ni hardware fotonico.",
                    "Cuatro puntos para H2: el IC95 (t con 2 gl) es amplio.",
                    "N<64 solo mide tiempo y memoria; con 10 detectores N=8 no admite clasificacion."],
    }
    (RES / "RESULTADOS_ESCALA.json").write_text(json.dumps(out, indent=1), encoding="utf-8", newline="\n")

    f = lambda x: f"{x:.4f}"
    md = ["# Resultados P2-10 (escala a 64 modos)", "",
          "Generado por `analisis.py` a partir de `resultados_raw.json`. CPU, sin GPU.", "",
          "## H3 (digits, N = 64)", "",
          "| Modelo | Exactitud media | DE |", "|---|---|---|",
          f"| Malla N=64 | {f(acc_mesh.mean())} | {f(acc_mesh.std(ddof=1))} |",
          f"| Logistica (L2=0,001) | {f(acc_lg.mean())} | {f(acc_lg.std(ddof=1))} |",
          f"| MLP 48 | {f(acc_ml.mean())} | {f(acc_ml.std(ddof=1))} |", "",
          f"- Malla - logistica: {mean_lg:+.4f}, IC95 bootstrap [{ci_lg[0]:+.4f}, {ci_lg[1]:+.4f}], "
          f"Wilcoxon p = {out['H3']['wilcoxon_bilateral']['p']:.4f}.",
          f"- **Decision H3: {out['H3']['decision']}** (criterio: diferencia >= -0,01 e IC95 inferior >= -0,03).",
          f"- Control malla - MLP (sin criterio): {mean_ml:+.4f}, IC95 [{ci_ml[0]:+.4f}, {ci_ml[1]:+.4f}], "
          f"Wilcoxon p = {out['control_MLP']['wilcoxon_bilateral']['p']:.4f}.", "",
          "## H2 (escala)", "",
          "| N | t por entrada (us) | t en lote, por entrada (us) | bytes coeficientes | bytes matriz densa |",
          "|---|---|---|---|---|"]
    for q in h2["puntos"]:
        md.append(f"| {q['N']} | {q['t_entrada_us']:.2f} | {q['t_entrada_lote_us']:.2f} | "
                  f"{q['bytes_coeficientes']} | {q['bytes_matriz_densa']} |")
    md += ["",
           f"- Pendiente log-log (tiempo por entrada, evaluacion individual): {t['pendiente']:.3f}, "
           f"IC95 [{t['ic95'][0]:.3f}, {t['ic95'][1]:.3f}] (t, {t['gl']} gl). "
           f"p en [1,8; 2,2]: {h2['p_en_rango_estimacion_puntual']}; IC95 dentro: {h2['ic95_dentro_del_rango']}.",
           f"- Exploratorio (lote de 1000, tiempo por entrada): {tl['pendiente']:.3f}, "
           f"IC95 [{tl['ic95'][0]:.3f}, {tl['ic95'][1]:.3f}].",
           f"- Memoria de coeficientes: pendiente {h2['memoria_coeficientes']['pendiente']:.3f} "
           f"IC95 [{h2['memoria_coeficientes']['ic95'][0]:.3f}, {h2['memoria_coeficientes']['ic95'][1]:.3f}]; "
           f"matriz densa: {h2['memoria_matriz_densa']['pendiente']:.3f}.", "",
           "## CPU de entrenamiento (malla N=64, 2000 pasos)", "",
           f"- {len(cpu)} entrenamientos; mediana {np.median(cpu):.1f} s, min {min(cpu):.1f} s, "
           f"max {max(cpu):.1f} s, total {sum(cpu):.0f} s.", ""]
    (RES / "RESULTADOS_ESCALA.md").write_text("\n".join(md), encoding="utf-8", newline="\n")
    print(json.dumps({"H3": out["H3"]["decision"], "dif": mean_lg, "ic": ci_lg, "p_H2": t["pendiente"],
                      "ic_H2": t["ic95"]}))


if __name__ == "__main__":
    main()
