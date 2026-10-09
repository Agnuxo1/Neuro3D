"""Calibracion del divisor (P1-7): pelicula dielectrica con |r|^2 = |t|^2 = 0,5.

1) Matriz de transferencia 1D (incidencia normal, vacio a ambos lados, caras como planos de
   referencia): r, t complejos de una lamina de indice n y espesor d.
2) Verificacion en el solver 2D (onda plana, incidencia normal, periodico en y): diferencias
   de |r|^2 y |t|^2 frente a la solucion 1D < 0,005. Si no se cumple se ajusta n (espesor fijo en
   nodos) hasta cumplir |r|^2 = 0,5 en el solver, se registra el ajuste y se repite la verificacion.
Uso: python calibracion.py [--ppl 16 24 32] [--salida calibracion.json]"""
from __future__ import annotations

import argparse
import json
import os
import time

import numpy as np
from scipy.optimize import brentq

import solver2d as s

TOL = 0.005
D_NOMINAL = 0.25  # espesor de la pelicula en lambdas (multiplo de h: 4, 6 y 8 nodos a lambda/16, /24, /32)


def rt_1d(n: float, d: float, k: float = s.K0, theta_deg: float = 0.0):
    """r, t complejos (convencion exp(-i w t), campo escalar E continuo con dE/dz continuo = modo TM
    de esta memoria) de una lamina n, espesor d (medido en la normal) en vacio. Planos de
    referencia en las caras. theta_deg: angulo de incidencia respecto a la normal."""
    st = np.sin(np.deg2rad(theta_deg))
    kz0 = k * np.cos(np.deg2rad(theta_deg))
    kz1 = k * np.sqrt(n ** 2 - st ** 2 + 0j)
    r12 = (kz0 - kz1) / (kz0 + kz1)
    r23 = -r12
    t12 = 2.0 * kz0 / (kz0 + kz1)
    t23 = 2.0 * kz1 / (kz0 + kz1)
    e = np.exp(2j * kz1 * d)
    den = 1.0 + r12 * r23 * e
    return (r12 + r23 * e) / den, t12 * t23 * np.exp(1j * kz1 * d) / den


def a_plano_medio(r_cara: complex, t_cara: complex, d: float, kz: float):
    """Coeficientes de un divisor ideal situado en el plano medio de la pelicula: r_c, t_c tales
    que reproducen el campo reflejado/transmitido referido a ese plano (lamina simetrica)."""
    return r_cara * np.exp(-1j * kz * d), t_cara * np.exp(-1j * kz * d)


def indice_nominal(d: float = D_NOMINAL, theta_deg: float = 0.0) -> float:
    """n > 1 con |r|^2 = 0,5 para el espesor d (primera raiz, la de menor indice)."""
    f = lambda n: abs(rt_1d(n, d, theta_deg=theta_deg)[0]) ** 2 - 0.5
    xs = np.linspace(1.2, 6.0, 8000)
    v = np.array([f(x) for x in xs])
    for a, b, fa, fb in zip(xs[:-1], xs[1:], v[:-1], v[1:]):
        if fa * fb < 0:
            return brentq(f, a, b, xtol=1e-14)
    raise RuntimeError("sin solucion |r|^2 = 0,5 para ese espesor")


def rt_solver(ppl: int, n: float, d_nodos: int, theta_deg: float = 0.0, pml: float = 3.0,
              ancho: float = 12.0):
    """r, t (complejos, planos de referencia en las caras) medidos en el solver 2D con onda plana
    de incidencia normal (theta=0) o a 45 grados (theta=45; ky = kx discretos). Periodico (Bloch) en y.
    Devuelve tambien r_c, t_c referidos al plano medio de la pelicula."""
    h = 1.0 / ppl
    m = s.construir_malla(ancho, 4 * h, h, pml, periodico_y=True)
    ky = s.k_diagonal(h) if theta_deg == 45.0 else 0.0
    m.bloch_ky = ky
    i0 = m.pml_x + int(round(2.0 / h))
    i_f = i0 + int(round(3.0 / h))
    n2 = np.ones((m.nx, m.ny))
    n2[i_f:i_f + d_nodos, :] = n ** 2
    x_front, x_back = (i_f - 0.5) * h, (i_f + d_nodos - 0.5) * h
    inc = s.onda_plana(m, x0=m.x()[i0], ky=ky)
    b = s.fuente_unidireccional(m, inc, i0)
    A = s.construir_operador(m, n2=n2)
    t0 = time.process_time()
    E = s.resolver(s.factorizar(A), b, m)[:, 0]
    t_cpu = time.process_time() - t0
    kd = float(s.kx_discreto(np.array([ky]), h)[0])
    x = m.x()
    a_front = np.exp(1j * kd * (x_front - x[i0]))
    cols_r = np.arange(m.pml_x + 4, i0 - 2)                 # detras de la fuente: solo reflejada
    r_est = E[cols_r] * np.exp(1j * kd * (x[cols_r] - x_front)) / a_front
    cols_t = np.arange(i_f + d_nodos + 4, m.nx - m.pml_x - 4)
    t_est = E[cols_t] * np.exp(-1j * kd * (x[cols_t] - x_back)) / a_front
    r, t = complex(r_est.mean()), complex(t_est.mean())
    rc, tc = a_plano_medio(r, t, d_nodos * h, kd)
    return dict(r=r, t=t, r_c=complex(rc), t_c=complex(tc),
                dispersion_r=float(np.std(r_est)), dispersion_t=float(np.std(t_est)),
                t_cpu_s=t_cpu, incognitas=m.nx * m.ny)


def calibrar(ppl: int, d: float = D_NOMINAL, n_nominal: float | None = None, theta_deg: float = 0.0) -> dict:
    """Calibracion para una malla: verifica el nominal y, si falla, ajusta n y repite."""
    n_nom = n_nominal or indice_nominal(d, theta_deg)
    d_nodos = int(round(d * ppl))
    d_efectivo = d_nodos / ppl
    r1, t1 = rt_1d(n_nom, d_efectivo)
    pasos = []
    n = n_nom
    n_ant = R_ant = None
    for intento in range(10):
        res = rt_solver(ppl, n, d_nodos, theta_deg)
        R, T = abs(res["r"]) ** 2, abs(res["t"]) ** 2
        # criterio: diferencias del solver frente a la solucion 1D del diseno nominal (0,5 / 0,5)
        dR, dT = R - 0.5, T - 0.5
        pasos.append(dict(n=n, R_solver=float(R), T_solver=float(T), dif_R=float(dR), dif_T=float(dT)))
        if abs(dR) < TOL and abs(dT) < TOL:
            break
        n_prev = n
        n = n + dR * 2.0 if n_ant is None else n - dR * (n - n_ant) / (R - R_ant)
        n_ant, R_ant = n_prev, R
        pasos[-1]["ajuste"] = f"n {n_prev:.6f} -> {n:.6f}"
    else:
        raise RuntimeError("calibracion no converge")
    n_final = pasos[-1]["n"]
    r1, t1 = rt_1d(n_final, d_efectivo, theta_deg=theta_deg)
    ajustado = abs(n_final - n_nom) > 1e-12
    return dict(ppl=ppl, angulo_deg=theta_deg, d_lambda=d_efectivo, d_nodos=d_nodos, n_nominal=n_nom, n_usado=n_final,
                ajustado=bool(ajustado), pasos=pasos,
                solver=dict(r_re=res["r"].real, r_im=res["r"].imag, t_re=res["t"].real, t_im=res["t"].imag,
                            R=float(R), T=float(T)),
                plano_medio=dict(r_re=res["r_c"].real, r_im=res["r_c"].imag, t_re=res["t_c"].real,
                                 t_im=res["t_c"].imag),
                modelo_1d_n_usado=dict(r_re=float(r1.real), r_im=float(r1.imag), t_re=float(t1.real),
                                       t_im=float(t1.imag), R=float(abs(r1) ** 2), T=float(abs(t1) ** 2)),
                dif_R=float(dR), dif_T=float(dT), cumple=bool(abs(dR) < TOL and abs(dT) < TOL),
                t_cpu_s=res["t_cpu_s"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ppl", type=int, nargs="+", default=[16, 24])
    ap.add_argument("--angulo", type=float, default=45.0)
    ap.add_argument("--salida", default=None)
    a = ap.parse_args()
    salida = a.salida or ("calibracion_45.json" if a.angulo == 45.0 else "calibracion_incidencia_normal.json")
    n_nom = indice_nominal(D_NOMINAL, a.angulo)
    r1n, t1n = rt_1d(n_nom, D_NOMINAL, theta_deg=a.angulo)
    out = dict(angulo_deg=a.angulo, d_nominal_lambda=D_NOMINAL, n_nominal=n_nom, tolerancia=TOL,
               rt_1d_nominal={"r": [float(r1n.real), float(r1n.imag)], "t": [float(t1n.real), float(t1n.imag)]},
               mallas={})
    for p in a.ppl:
        c = calibrar(p, n_nominal=n_nom, theta_deg=a.angulo)
        out["mallas"][str(p)] = c
        print(f"ppl={p}: n_nominal={n_nom:.5f} n_usado={c['n_usado']:.5f} R_solver={c['solver']['R']:.5f} "
              f"T_solver={c['solver']['T']:.5f} dif_R={c['dif_R']:+.5f} dif_T={c['dif_T']:+.5f} cumple={c['cumple']} "
              f"pasos_primer_dif_R={c['pasos'][0]['dif_R']:+.4f}")
    with open(salida, "w", encoding="utf8") as fh:
        json.dump(out, fh, indent=1)


if __name__ == "__main__":
    main()
