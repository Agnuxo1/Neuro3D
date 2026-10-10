"""Control P1-7 con dispositivo fijo: lambda/16 con n = 2,484992 (indice del solver fino), sin recalibrar.
Importa mzi_fdtd, fdtd2d y calibracion_fdtd sin modificarlos. r, t del modelo se recalculan con ese n
(rt_fdtd en lambda/16, a plano medio). Posiciones k y dL_eff tomadas de resultados/mzi_fdtd_16_k*.json.
Uso: python run_control.py [--procesos 2]"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
import time
from multiprocessing import Pool

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(AQUI)
sys.path.insert(0, BASE)
TMP = r"D:\PROJECTS\.cognition\neuro3d-audit\p1-7\control\tmp"
RES = os.path.join(AQUI, "resultados")
PPL = 16

import calibracion as cal  # noqa: E402
import calibracion_fdtd as cf  # noqa: E402
import mzi_fdtd as m  # noqa: E402


def n_fijo() -> float:
    return json.load(open(os.path.join(BASE, "calibracion_fdtd_45.json")))["mallas"]["24"]["n_usado"]


def trabajo(arg):
    k, n, r, t = arg
    m.SALIDA = TMP
    o = m.simular((PPL, k, n, r, t))
    return o


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--procesos", type=int, default=2)
    a = ap.parse_args()
    os.makedirs(RES, exist_ok=True)
    os.makedirs(TMP, exist_ok=True)
    n = n_fijo()
    orig = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(BASE, "resultados", f"mzi_fdtd_{PPL}_k*.json")))]
    ks = [d["k"] for d in orig]
    assert ks == list(range(12)), ks
    # Paso 3: calibracion sin ajuste con n fijo
    cj = os.path.join(RES, "calibracion_n_fijo_16.json")
    if os.path.exists(cj):
        cal16 = json.load(open(cj))
    else:
        rs = cf.rt_fdtd(PPL, n, int(round(cal.D_NOMINAL * PPL)))
        R, T = abs(rs["r"]) ** 2, abs(rs["t"]) ** 2
        cal16 = dict(ppl=PPL, n=n, R=float(R), T=float(T), dif_R=float(R - 0.5), dif_T=float(T - 0.5), tolerancia=cf.TOL,
                     no_calibrado_en_lambda16=bool(abs(R - 0.5) > cf.TOL or abs(T - 0.5) > cf.TOL),
                     solver=dict(r_re=rs["r"].real, r_im=rs["r"].imag, t_re=rs["t"].real, t_im=rs["t"].imag),
                     plano_medio=dict(r_re=rs["r_c"].real, r_im=rs["r_c"].imag, t_re=rs["t_c"].real, t_im=rs["t_c"].imag),
                     t_cpu_s=rs["t_cpu_s"])
        json.dump(cal16, open(cj, "w"), indent=1)
    pm = cal16["plano_medio"]
    r, t = complex(pm["r_re"], pm["r_im"]), complex(pm["t_re"], pm["t_im"])
    print("calibracion n fijo:", {x: cal16[x] for x in ("n", "R", "T", "dif_R", "dif_T", "no_calibrado_en_lambda16")}, flush=True)
    args = [(k, n, r, t) for k in ks]
    t0 = time.time()
    with Pool(a.procesos) as p:
        for o in p.imap_unordered(trabajo, args):
            print(f"k={o['k']:2d} err={max(o['err_P1'], o['err_P2']):.4f} cpu={o['t_cpu_s']:.0f}s", flush=True)
    for d in orig:
        o = json.load(open(os.path.join(TMP, f"mzi_fdtd_{PPL}_k{d['k']:02d}.json")))
        assert abs(o["dL_eff"] - d["dL_eff"]) < 1e-12 and o["pasos"] == d["pasos"] and o["celdas"] == d["celdas"]
        out = dict(ppl=PPL, k=o["k"], dL_eff=o["dL_eff"], n_film=o["n_film"], n_original_recalibrado=d["n_film"],
                   P1_solver=o["P1_solver"], P2_solver=o["P2_solver"], P1_modelo=o["P1_modelo"], P2_modelo=o["P2_modelo"],
                   err_P1=o["err_P1"], err_P2=o["err_P2"], err=max(o["err_P1"], o["err_P2"]),
                   err_original_n_recalibrado=max(d["err_P1"], d["err_P2"]), dif_regimen=o["dif_regimen"],
                   pasos=o["pasos"], celdas=o["celdas"], t_cpu_s=o["t_cpu_s"], t_wall_s=o["t_wall_s"])
        json.dump(out, open(os.path.join(RES, f"control_fijo_16_k{o['k']:02d}.json"), "w"), indent=1)
    sys.stdout.write("total s %.0f\n" % (time.time() - t0))
    open(os.path.join(TMP, "RUN_DONE"), "w").write("ok")


if __name__ == "__main__":
    main()
