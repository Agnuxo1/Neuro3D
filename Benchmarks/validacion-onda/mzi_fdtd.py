"""Mach-Zehnder a 45 grados con FDTD (P1-7, Enmiendas 1 y 2) frente al modelo de caminos.

Geometria (lambda = 1, origen en el centro de S1; todos los elementos son segmentos VERTICALES
alineados con la malla y los haces viajan a +-45 grados): el haz de entrada (w = 8) viaja en (1,1)
hacia S1; transmitido -> brazo A (1,1) -> M_A (x = +a) -> (-1,1) -> S2; reflejado -> brazo B (-1,1) ->
M_B (x = -a - delta) -> (1,1) -> S2. Salidas: P1 en direccion (1,1) (linea vertical x = +25) y P2 en
(-1,1) (x = -25). Brazos de ~30 lambda (tramo divisor-espejo), elementos de 40 lambda de longitud.
Barrido: M_B se desplaza delta = k h (k celdas), lo que cambia el camino 2 sqrt2 delta y desplaza el
haz B en S2 (0, 2 delta). Diferencia de camino efectiva = sqrt2 delta.
Potencias: P = |<E,g>|^2 / <g,g>^2 con g el modo gaussiano (misma definicion en solver y modelo).
Uso: python mzi_fdtd.py --ppl 16 [--ks 0 1 ...] [--procesos 3]
"""
from __future__ import annotations

import argparse
import json
import os
import time
from multiprocessing import Pool

import numpy as np

import fdtd2d as f

K_IDEAL = 2.0 * np.pi
W = 8.0
L_BRAZO = 30.0
H_ELEM = 20.0           # semilongitud de divisores y espejos (lambdas)
D_PELICULA = 0.25
X_PUERTO = 25.0
X0_FUENTE = 8.0         # distancia de la fuente de inyeccion a S1 (en x)
PERIODOS = 190
VENTANA = 10
SALIDA = "resultados"


def geometria(ppl: int, k: int, n_film: float) -> dict:
    h = 1.0 / ppl
    npml = 3 * ppl
    m = int(round(D_PELICULA * ppl))
    a_cells = int(round(L_BRAZO / np.sqrt(2) * ppl))
    Hc = int(round(H_ELEM * ppl))
    nx = 2 * npml + 64 * ppl
    ny = 2 * npml + 124 * ppl
    i_f = npml + 32 * ppl - m // 2
    c = i_f + (m - 1) / 2.0 + 0.5                    # entero: xS/h = c - 0.5
    xS = (c - 0.5) * h
    j_S1 = npml + 32 * ppl
    i_MA = int(c) + a_cells
    i_MB = int(c) - 1 - a_cells - k
    j_MA = j_S1 + a_cells
    j_S2 = j_S1 + 2 * a_cells + 1
    eps = np.ones((nx, ny))
    pec = np.zeros((nx, ny), bool)
    for jc in (j_S1, j_S2):
        eps[i_f:i_f + m, jc - Hc:jc + Hc + 1] = n_film ** 2
    pec[i_MA:i_MA + 2, j_MA - Hc:j_MA + Hc + 1] = True        # M_A: cara frontal en la columna i_MA
    pec[i_MB - 1:i_MB + 1, j_MA - Hc:j_MA + Hc + 1] = True    # M_B: cara frontal en i_MB (cara derecha)
    i0 = i_f - int(X0_FUENTE * ppl)
    yS1 = j_S1 * h
    yS2 = j_S2 * h
    x0 = i0 * h
    i_p1 = int(round((xS + X_PUERTO) / h))
    i_p2 = int(round((xS - X_PUERTO) / h))
    return dict(ppl=ppl, h=h, k=k, nx=nx, ny=ny, npml=npml, m=m, i_f=i_f, xS=xS, yS1=yS1, yS2=yS2,
                a_A=i_MA * h - xS, a_B=xS - i_MB * h, i_MA=i_MA, i_MB=i_MB, i0=i0, x0=x0,
                yc=yS1 - (xS - x0), i_p1=i_p1, i_p2=i_p2, x_p1=i_p1 * h, x_p2=i_p2 * h,
                eps=eps, pec=pec)


def modo(ny: int, h: float, yb: float, ky0: float) -> np.ndarray:
    """Modo gaussiano de la linea vertical (haz a 45 grados de radio W perpendicular)."""
    y = np.arange(ny) * h
    wy = W * np.sqrt(2.0)
    return np.exp(-((y - yb) / wy) ** 2) * np.exp(1j * ky0 * (y - yb))


def potencia(E: np.ndarray, g: np.ndarray, h: float) -> float:
    c = np.sum(E * np.conj(g)) * h
    return float(abs(c) ** 2 / (np.sum(np.abs(g) ** 2) * h) ** 2)


def haz_ideal(x_p: float, y: np.ndarray, Q, d, L_Q: float, coef: complex, difraccion: bool = False) -> np.ndarray:
    """Campo en la linea x = x_p del haz que parte del punto Q en direccion d, tras un camino L_Q desde
    la cintura (S1). difraccion=False: modelo preregistrado (anchura w constante, sin curvatura).
    difraccion=True: DIAGNOSTICO exploratorio (no preregistrado) con la propagacion gaussiana libre."""
    dx, dy = x_p - Q[0], y - Q[1]
    s = dx * d[1] - dy * d[0]                       # distancia perpendicular con signo
    u = dx * d[0] + dy * d[1]                       # coordenada a lo largo del haz
    if not difraccion:
        return coef * np.exp(1j * K_IDEAL * (L_Q + u)) * np.exp(-(s / W) ** 2)
    q = 1.0 + 1j * 2.0 * (L_Q + u) / (K_IDEAL * W ** 2)
    return coef * np.exp(1j * K_IDEAL * (L_Q + u)) * q ** -0.5 * np.exp(-s ** 2 / (W ** 2 * q))


def modelo(g: dict, r: complex, t: complex, ky0: float) -> dict:
    """Modelo de caminos con r, t calibrados (referidos al plano medio), espejos -1, sin difraccion
    de camino; la potencia es el solapamiento del haz gaussiano (desplazado) con el modo de cada puerto."""
    h, ny = g["h"], g["ny"]
    y = np.arange(ny) * h
    s2 = np.sqrt(2.0)
    aA, aB = g["a_A"], g["a_B"]
    LA, LB = 2 * s2 * aA, 2 * s2 * aB
    QA = (g["xS"], g["yS1"] + 2 * aA)
    QB = (g["xS"], g["yS1"] + 2 * aB)
    d1, d2 = (1 / s2, 1 / s2), (-1 / s2, 1 / s2)
    mir = -1.0
    # P1 = r (A) + t (B); P2 = t (A) + r (B)  (mismo orden que el modelo de caminos escalar)
    yb1 = g["yS2"] + (g["x_p1"] - g["xS"])
    yb2 = g["yS2"] + (g["xS"] - g["x_p2"])
    g1, g2 = modo(ny, h, yb1, ky0), modo(ny, h, yb2, ky0)
    res = {}
    for nom, dif in (("", False), ("_dif", True)):
        E1 = (haz_ideal(g["x_p1"], y, QA, d1, LA, mir * t * r, dif)
              + haz_ideal(g["x_p1"], y, QB, d1, LB, mir * r * t, dif))
        E2 = (haz_ideal(g["x_p2"], y, QA, d2, LA, mir * t * t, dif)
              + haz_ideal(g["x_p2"], y, QB, d2, LB, mir * r * r, dif))
        res["P1" + nom], res["P2" + nom] = potencia(E1, g1, h), potencia(E2, g2, h)
    return dict(P1=res["P1"], P2=res["P2"], P1_dif=res["P1_dif"], P2_dif=res["P2_dif"],
                dL_geom=float(2 * s2 * (aB - aA)), dL_eff=float(s2 * (aB - aA)), desplaz_haz_B=float(2 * (aB - aA)))


def simular(arg):
    ppl, k, n_film, r, t = arg
    import psutil
    nombre = os.path.join(SALIDA, f"mzi_fdtd_{ppl}_k{k:02d}.json")
    if os.path.exists(nombre):
        return json.load(open(nombre))
    g = geometria(ppl, k, n_film)
    n_p = f.pasos_por_periodo(ppl)
    ky0 = f.ky_diagonal(ppl, n_p)
    sim = f.FDTD(g["nx"], g["ny"], ppl, eps=g["eps"], pec=g["pec"], npml=g["npml"], n_p=n_p)
    sim.preparar_haz(f.Haz(w=W, yc=g["yc"], angulo_deg=45.0, i0=g["i0"]),
                     u_c=-np.sqrt(2.0) * (g["xS"] - g["x0"]))   # cintura del haz de entrada en S1
    sim.haz.i0 = g["i0"]
    res = sim.ejecutar(PERIODOS, VENTANA, {"p1": g["i_p1"], "p2": g["i_p2"]})
    h, ny = g["h"], g["ny"]
    yb1 = g["yS2"] + (g["x_p1"] - g["xS"])
    yb2 = g["yS2"] + (g["xS"] - g["x_p2"])
    g1, g2 = modo(ny, h, yb1, ky0), modo(ny, h, yb2, ky0)
    fs, fp = res["fasores"], res["fasores_prev"]
    P1, P2 = potencia(fs["p1"], g1, h), potencia(fs["p2"], g2, h)
    P1p, P2p = potencia(fp["p1"], g1, h), potencia(fp["p2"], g2, h)
    mod = modelo(g, r, t, ky0)
    out = dict(ppl=ppl, k=k, n_film=n_film, celdas=g["nx"] * g["ny"], n_p=n_p, pasos=res["pasos"],
               P1_solver=P1, P2_solver=P2, P1_ventana_previa=P1p, P2_ventana_previa=P2p,
               dif_regimen=max(abs(P1 - P1p), abs(P2 - P2p)),
               P1_modelo=mod["P1"], P2_modelo=mod["P2"], P1_modelo_dif=mod["P1_dif"], P2_modelo_dif=mod["P2_dif"], err_P1=abs(P1 - mod["P1"]), err_P2=abs(P2 - mod["P2"]),
               dL_geom=mod["dL_geom"], dL_eff=mod["dL_eff"], desplaz_haz_B=mod["desplaz_haz_B"],
               suma_solver=P1 + P2, t_cpu_s=res["t_cpu_s"], t_wall_s=res["t_wall_s"],
               t_por_paso_s=res["t_por_paso_s"], pico_memoria_gb=psutil.Process().memory_info().peak_wset / 2 ** 30)
    os.makedirs(SALIDA, exist_ok=True)
    json.dump(out, open(nombre, "w"), indent=1)
    return out


def ks_necesarios(ppl: int) -> list[int]:
    """Desplazamientos (celdas) que cubren los 21 objetivos dL_eff = j/20, j = 0..20."""
    h = 1.0 / ppl
    return sorted({int(round((j / 20.0) / (np.sqrt(2) * h))) for j in range(21)})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ppl", type=int, required=True)
    ap.add_argument("--ks", type=int, nargs="*")
    ap.add_argument("--procesos", type=int, default=3)
    a = ap.parse_args()
    cal = json.load(open("calibracion_fdtd_45.json"))["mallas"][str(a.ppl)]
    pm = cal["plano_medio"]
    r, t = complex(pm["r_re"], pm["r_im"]), complex(pm["t_re"], pm["t_im"])
    ks = a.ks if a.ks else ks_necesarios(a.ppl)
    args = [(a.ppl, k, cal["n_usado"], r, t) for k in ks]
    t0 = time.time()
    if a.procesos > 1 and len(args) > 1:
        with Pool(a.procesos) as p:
            for o in p.imap_unordered(simular, args):
                print(f"k={o['k']:2d} dL_eff={o['dL_eff']:.4f} P1 {o['P1_solver']:.4f}/{o['P1_modelo']:.4f} "
                      f"P2 {o['P2_solver']:.4f}/{o['P2_modelo']:.4f} err={max(o['err_P1'], o['err_P2']):.4f} "
                      f"[dif {o['P1_modelo_dif']:.4f}/{o['P2_modelo_dif']:.4f}] regimen={o['dif_regimen']:.1e} cpu={o['t_cpu_s']:.0f}s", flush=True)
    else:
        for ar in args:
            o = simular(ar)
            print(f"k={o['k']:2d} dL_eff={o['dL_eff']:.4f} P1 {o['P1_solver']:.4f}/{o['P1_modelo']:.4f} "
                  f"P2 {o['P2_solver']:.4f}/{o['P2_modelo']:.4f} err={max(o['err_P1'], o['err_P2']):.4f} "
                  f"[dif {o['P1_modelo_dif']:.4f}/{o['P2_modelo_dif']:.4f}] regimen={o['dif_regimen']:.1e} cpu={o['t_cpu_s']:.0f}s", flush=True)
    print("total s", time.time() - t0)


if __name__ == "__main__":
    main()
