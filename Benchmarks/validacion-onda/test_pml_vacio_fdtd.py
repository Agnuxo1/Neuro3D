"""Prueba de dominio vacio del FDTD (P1-7, Enmienda 2): un haz gaussiano inyectado hacia +x con la
tecnica campo total/disperso debe ser absorbido por la CPML sin reflejar. Reflexion = energia
(integral de |Ez|^2 dy) en columnas situadas por detras de la fuente / energia inyectada.
Criterio: reflexion < 1e-3. Tambien se comprueba la fidelidad del haz aguas abajo (solapamiento).
Uso: python test_pml_vacio_fdtd.py [--ppl 16] [--w 8]"""
from __future__ import annotations

import argparse
import json
import os

import numpy as np
import psutil

import fdtd2d as f


def pico_gb() -> float:
    try:
        return psutil.Process().memory_info().peak_wset / 2 ** 30
    except Exception:
        return float("nan")


def solapamiento(Ecol, ppl, w, yb, ky0, ang_deg):
    """P = |<E,g>|^2 / <g,g>^2 con g el modo gaussiano de la linea vertical (misma definicion que el MZI)."""
    h = 1.0 / ppl
    y = np.arange(len(Ecol)) * h
    wy = w / np.cos(np.deg2rad(ang_deg))
    g = np.exp(-((y - yb) / wy) ** 2) * np.exp(1j * ky0 * (y - yb))
    c = np.sum(Ecol * np.conj(g)) * h
    return float(abs(c) ** 2 / (np.sum(np.abs(g) ** 2) * h) ** 2)


def reflexion_fdtd(ppl=16, w=8.0, ang=45.0, lx=50.0, ly=70.0, pml=3.0, periodos=80, ventana=10):
    npml = int(round(pml * ppl))
    nx = int(round(lx * ppl)) + 2 * npml
    ny = int(round(ly * ppl)) + 2 * npml
    sim = f.FDTD(nx, ny, ppl, npml=npml)
    i0 = npml + 2 * ppl
    h = 1.0 / ppl
    # el haz inclinado sube: centro en el primer tercio vertical para que salga por arriba/derecha
    yc = (npml * h) + (0.45 if ang == 45.0 else 0.5) * ly
    sim.preparar_haz(f.Haz(w=w, yc=yc, angulo_deg=ang, i0=i0))
    sim.haz.i0 = i0
    columnas = {"atras1": i0 - ppl, "atras2": i0 - 2 * ppl, "ref": i0 + 1}
    dx_abajo = int(round(15 * ppl))
    columnas["abajo"] = i0 + dx_abajo
    res = sim.ejecutar(periodos, ventana, columnas)
    e_in = float(np.sum(np.abs(sim.E_ph) ** 2) * h)
    fs = res["fasores"]
    r_atras = max(float(np.sum(np.abs(fs[k]) ** 2) * h) for k in ("atras1", "atras2")) / e_in
    ky0 = f.ky_diagonal(ppl, sim.n_p) if ang == 45.0 else 0.0
    desplaz = np.tan(np.deg2rad(ang)) * dx_abajo * h
    p_abajo = solapamiento(fs["abajo"], ppl, w, yc + desplaz, ky0, ang)
    return dict(ppl=ppl, w=w, angulo=ang, nx=nx, ny=ny, celdas=nx * ny, n_p=sim.n_p,
                reflexion_potencia=r_atras, reflexion_amplitud=float(np.sqrt(r_atras)),
                solapamiento_abajo=p_abajo, t_por_paso_s=res["t_por_paso_s"], t_cpu_s=res["t_cpu_s"],
                pasos=res["pasos"], pico_memoria_gb=pico_gb())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ppl", type=int, default=16)
    ap.add_argument("--w", type=float, default=8.0)
    ap.add_argument("--salida", default=os.path.join("resultados", "pml_vacio_fdtd.json"))
    a = ap.parse_args()
    res = [reflexion_fdtd(a.ppl, a.w, 45.0), reflexion_fdtd(a.ppl, a.w, 0.0, lx=40.0, ly=50.0)]
    for r in res:
        print(json.dumps(r))
    peor = max(r["reflexion_potencia"] for r in res)
    ok = peor < 1e-3
    print(f"FDTD dominio vacio: reflexion potencia max = {peor:.3e}; criterio < 1e-3 -> {'CUMPLE' if ok else 'FALLA'}")
    os.makedirs(os.path.dirname(a.salida), exist_ok=True)
    json.dump(dict(casos=res, criterio=1e-3, cumple=bool(ok)), open(a.salida, "w"), indent=1)
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
