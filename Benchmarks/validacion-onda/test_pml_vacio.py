"""Prueba PML en vacio (P1-7): un haz gaussiano inyectado hacia +x debe ser absorbido sin
reflejar. Reflexion = energia que vuelve por detras de la fuente / energia inyectada.
Criterio del preregistro: reflexion < 1e-3. Se reportan potencia (energia) y amplitud.
Uso: python test_pml_vacio.py [--ppl 16] [--w 8] [--salida resultados/pml_vacio.json]"""
from __future__ import annotations

import argparse
import json
import os
import time

import numpy as np

import solver2d as s


def pico_memoria_gb() -> float:
    try:
        import psutil
        return psutil.Process().memory_info().peak_wset / 2 ** 30
    except Exception:
        return float("nan")


def reflexion_pml(ppl: int = 16, w: float = 8.0, angulo: float = 0.0, pml: float = 3.0,
                  largo: float = 14.0) -> dict:
    """Haz de anchura w (en lambdas) con inclinacion `angulo` (grados) hacia la PML derecha y
    las PML superior/inferior. ppl = puntos por longitud de onda (h = 1/ppl)."""
    h = 1.0 / ppl
    ly = 2 * 2.6 * w + 2.0                      # +-2.6 w: potencia del haz fuera < 1e-5
    m = s.construir_malla(largo, ly, h, pml)
    i0 = m.pml_x + int(round(2.0 / h))          # fuente a 2 lambdas de la PML izquierda
    yc = (m.ny - 1) * h / 2.0
    # el haz inclinado se desplaza hacia +y: se centra de modo que llegue al borde derecho en yc
    desplaz = np.tan(np.deg2rad(angulo)) * (m.x()[-1] - m.x()[i0]) / 2.0
    y0 = yc - desplaz
    inc = s.haz_gaussiano(m, w, m.x()[i0], y0, angulo)
    inc[:i0, :] = 0.0
    # el termino fuente usa el haz sin truncar; se rehace con el campo completo
    inc_full = s.haz_gaussiano(m, w, m.x()[i0], y0, angulo)
    b = s.fuente_unidireccional(m, inc_full, i0)
    A = s.construir_operador(m)
    t0 = time.process_time()
    f = s.factorizar(A)
    E = s.resolver(f, b, m)
    t_cpu = time.process_time() - t0
    # energia inyectada: plano justo despues de la fuente (la propagacion oblicua la conserva
    # para el flujo en x solo aproximadamente; se usa tambien el campo E de referencia)
    e_in = s.flujo_energia(E[i0 + 1, :], m)
    # plano posterior a la fuente, entre la PML izquierda y la fuente (debe ser ~0)
    i_m = m.pml_x + int(round(1.0 / h))
    e_back = s.flujo_energia(E[i_m, :], m)
    # error global respecto al haz exacto en la region fisica a la derecha de la fuente
    ix0, ix1 = i0 + 1, m.nx - m.pml_x
    iy0, iy1 = m.pml_y, m.ny - m.pml_y
    ref = inc_full[ix0:ix1, iy0:iy1]
    err = np.linalg.norm(E[ix0:ix1, iy0:iy1] - ref) / np.linalg.norm(ref)
    # reflejo en el semiespacio posterior a la fuente (todas las columnas fisicas a su izquierda)
    cols_atras = slice(m.pml_x, i0 - 1)
    e_back_max = float(np.max(np.sum(np.abs(E[cols_atras, :]) ** 2, axis=1) * m.h))
    r_pot = e_back_max / e_in
    return dict(ppl=ppl, w=w, angulo=angulo, nx=m.nx, ny=m.ny, incognitas=m.nx * m.ny,
                reflexion_potencia=r_pot, reflexion_amplitud=float(np.sqrt(r_pot)),
                reflexion_plano_1lambda=e_back / e_in,
                error_relativo_haz=float(err),
                t_factor_s=f.t_factor, t_cpu_total_s=t_cpu, nnz_lu=f.nnz_lu,
                pico_memoria_gb=pico_memoria_gb())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ppl", type=int, default=16)
    ap.add_argument("--w", type=float, default=8.0)
    ap.add_argument("--salida", default=os.path.join("resultados", "pml_vacio.json"))
    a = ap.parse_args()
    res = [reflexion_pml(a.ppl, a.w, ang) for ang in (0.0, 10.0)]
    for r in res:
        print(json.dumps(r))
    peor = max(r["reflexion_potencia"] for r in res)
    peor_amp = max(r["reflexion_amplitud"] for r in res)
    ok = peor < 1e-3
    print(f"PML vacio: reflexion potencia max = {peor:.3e}; amplitud max = {peor_amp:.3e}; "
          f"criterio < 1e-3 -> {'CUMPLE' if ok else 'FALLA'}")
    os.makedirs(os.path.dirname(a.salida), exist_ok=True)
    with open(a.salida, "w", encoding="utf8") as fh:
        json.dump(dict(casos=res, criterio=1e-3, cumple=bool(ok),
                       cumple_en_amplitud=bool(peor_amp < 1e-3)), fh, indent=1)
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
