"""Ejecuta P1-8 completo segun PREREGISTRO-P1-8.md. CPU, un proceso. Uso: python analisis.py"""
import hashlib, json, platform, sys, time
from pathlib import Path
import numpy as np
import scipy
from scipy.stats import wilcoxon

import generadores as g
import modelos as m

HERE = Path(__file__).resolve().parent
OUT = HERE / "resultados"
OUT.mkdir(exist_ok=True)


def run_set(tasks, label):
    rows = []
    for t in tasks:
        t0 = time.time()
        Qs = m.qda_fit(t['Xtr'], t['ytr'])
        accQ = float((m.qda_predict(Qs, t['Xte']) == t['yte']).mean())
        mod = m.optical_fit(t['Xtr'], t['ytr'])
        accO = float((m.optical_predict(mod, t['Xte']) == t['yte']).mean())
        Mo = m.optical_Q(mod['U'], mod['V'])
        rows.append(dict(
            conjunto=label, semilla=t['seed'], acc_Q=accQ, acc_O=accO, diff=accQ - accO,
            O_semilla_elegida=mod['seed'], O_perdida_entren=mod['loss'], O_perdidas_5=mod['losses'],
            rangos_detector_O=[m.num_rank(M) for M in Mo],
            rangos_dif_O=m.pair_ranks(Mo), rangos_dif_QDA=m.pair_ranks(Qs),
            seg=time.time() - t0))
    return rows


def boot_ci(d, B=10000, seed=0):
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(d), size=(B, len(d)))
    means = d[idx].mean(1)
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def summarize(rows):
    d = np.array([r['diff'] for r in rows])
    lo, hi = boot_ci(d)
    try:
        w = wilcoxon(d, alternative='two-sided')
        wp, ws = float(w.pvalue), float(w.statistic)
    except ValueError as e:
        wp, ws = None, str(e)
    return dict(n=len(d), media_Q=float(np.mean([r['acc_Q'] for r in rows])),
                media_O=float(np.mean([r['acc_O'] for r in rows])),
                media_dif=float(d.mean()), mediana_dif=float(np.median(d)),
                IC95_bootstrap=[lo, hi], wilcoxon_p_bilateral=wp, wilcoxon_estadistico=ws,
                tareas_dif_mayor_0_02=int((d > 0.02).sum()))


def main():
    t_all = time.time()
    info = dict(python=sys.version, numpy=np.__version__, scipy=scipy.__version__,
                plataforma=platform.platform(), dispositivo="CPU",
                semillas_cuadratica=g.QUAD_SEEDS, semillas_lineal=g.LIN_SEEDS,
                semillas_init_O=list(m.INIT_SEEDS), T=m.T, lr=m.LR, pasos=m.STEPS)
    grad = m.check_gradient()
    print("gradiente (max rel. dif. finitas):", grad, flush=True)
    quad = run_set(g.quad_tasks(), "cuadratica"); print("cuadratica hecha", flush=True)
    lin = run_set(g.lin_tasks(), "lineal"); print("lineal hecha", flush=True)
    sq, sl = summarize(quad), summarize(lin)

    # verificacion de rango
    allO = [r for r in quad + lin]
    maxrank_O = max(max(r['rangos_dif_O'].values()) for r in allO)
    maxrank_det = max(max(r['rangos_detector_O']) for r in allO)
    qda_q = [r for r in quad]
    n_pairs_r5 = sum(v == 5 for r in qda_q for v in r['rangos_dif_QDA'].values())
    n_tasks_r5 = sum(any(v == 5 for v in r['rangos_dif_QDA'].values()) for r in qda_q)
    n_tasks_all5 = sum(all(v == 5 for v in r['rangos_dif_QDA'].values()) for r in qda_q)
    rank_ver = dict(max_rango_dif_O=maxrank_O, max_rango_detector_O=maxrank_det,
                    teoria_O_cumplida=bool(maxrank_O <= 4 and maxrank_det <= 2),
                    QDA_cuadratica_pares_rango5=n_pairs_r5, QDA_pares_total=3 * len(qda_q),
                    QDA_tareas_con_algun_par_rango5=n_tasks_r5,
                    QDA_tareas_con_todos_pares_rango5=n_tasks_all5, QDA_tareas=len(qda_q),
                    QDA_rango5_mayoria=bool(n_tasks_all5 > len(qda_q) / 2))

    # decision (seccion 6)
    control_ok = bool(sl['media_dif'] < 0.01)
    h1 = bool(sq['IC95_bootstrap'][0] > 0.02 and sq['media_dif'] > 0.02)
    if not control_ok:
        decision = "prueba invalida"
    elif h1:
        decision = "limite demostrado"
    else:
        decision = "sin limite practico demostrado"
    res = dict(info=info, verificacion_gradiente=grad, verificacion_rango=rank_ver,
               frontera_cuadratica=sq, control_lineal=sl,
               control_cordura_cumplido=control_ok, H1_cumplida=h1, decision=decision,
               segundos_totales=time.time() - t_all)
    (OUT / "resultados_raw.json").write_text(json.dumps(dict(info=info, tareas=quad + lin), indent=1), encoding="utf-8", newline="\n")
    (OUT / "RESULTADOS_LIMITE.json").write_text(json.dumps(res, indent=1), encoding="utf-8", newline="\n")
    md = f"""# Resultados P1-8

Decision: **{decision}**

| Conjunto | n | acc Q | acc O | media Q-O | IC95 bootstrap | Wilcoxon p | tareas Q-O>0,02 |
|---|---|---|---|---|---|---|---|
| Cuadratica | {sq['n']} | {sq['media_Q']:.4f} | {sq['media_O']:.4f} | {sq['media_dif']:.4f} | [{sq['IC95_bootstrap'][0]:.4f}, {sq['IC95_bootstrap'][1]:.4f}] | {sq['wilcoxon_p_bilateral']} | {sq['tareas_dif_mayor_0_02']} |
| Lineal (control) | {sl['n']} | {sl['media_Q']:.4f} | {sl['media_O']:.4f} | {sl['media_dif']:.4f} | [{sl['IC95_bootstrap'][0]:.4f}, {sl['IC95_bootstrap'][1]:.4f}] | {sl['wilcoxon_p_bilateral']} | {sl['tareas_dif_mayor_0_02']} |

Control de cordura (media Q-O lineal < 0,01): {'cumplido' if control_ok else 'NO cumplido'}. H1 (IC95 inf > 0,02 en cuadratica): {'cumplida' if h1 else 'no cumplida'}.

Verificacion de rango: max rango de P_k = {maxrank_det} (teoria <= 2); max rango de Q_i-Q_j en O = {maxrank_O} (teoria <= 4); QDA con los 3 pares de rango 5 en {n_tasks_all5}/{len(qda_q)} tareas cuadraticas ({n_pairs_r5}/{3*len(qda_q)} pares).

Gradiente analitico vs diferencias finitas (max error relativo): {grad}.

Python {sys.version.split()[0]}, numpy {np.__version__}, scipy {scipy.__version__}; CPU. Tiempo total {res['segundos_totales']:.1f} s.
"""
    (OUT / "RESULTADOS_LIMITE.md").write_text(md, encoding="utf-8", newline="\n")
    # SHA256SUMS: rutas relativas a limite-lectura, LF
    files = ["generadores.py", "modelos.py", "analisis.py", "resultados/resultados_raw.json",
             "resultados/RESULTADOS_LIMITE.json", "resultados/RESULTADOS_LIMITE.md"]
    lines = [f"{hashlib.sha256((HERE / f).read_bytes()).hexdigest()}  {f}" for f in files]
    (OUT / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(md)


if __name__ == "__main__":
    main()
