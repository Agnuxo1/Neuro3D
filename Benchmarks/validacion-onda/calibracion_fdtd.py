"""Calibracion del divisor a 45 grados (TM) con el solver FDTD (P1-7, Enmienda 2, paso 3).
Onda plana a 45 grados (periodico en y, ky cuantizado) sobre la pelicula de d = 0,25 lambda y
medida de |r|^2 y |t|^2 por fasores. Punto de partida: n de calibracion_45.json (Helmholtz).
Si |R-0,5| o |T-0,5| >= 0,005 se ajusta n (secante) y se repite; el ajuste queda registrado.
Uso: python calibracion_fdtd.py [--ppl 16 24] -> calibracion_fdtd_45.json"""
from __future__ import annotations

import argparse
import json
import time

import numpy as np

import calibracion as cal
import fdtd2d as f

TOL = 0.005


def ky_cuantizado(ppl, n_p, ny_max=700):
    """(ny, ky) con ky = 2 pi m /(ny h) lo mas cercano a la diagonal FDTD."""
    h = 1.0 / ppl
    k0 = f.ky_diagonal(ppl, n_p)
    mejor = None
    for ny in range(60, ny_max):
        m = round(k0 * ny * h / (2 * np.pi))
        if m == 0:
            continue
        ky = 2 * np.pi * m / (ny * h)
        err = abs(ky - k0) / k0
        if mejor is None or err < mejor[0]:
            mejor = (err, ny, ky)
    return mejor[1], mejor[2], mejor[0]


def rt_fdtd(ppl, n, d_nodos, periodos=70, ventana=10):
    h = 1.0 / ppl
    n_p = f.pasos_por_periodo(ppl)
    ny, ky, err_ang = ky_cuantizado(ppl, n_p)
    npml = 3 * ppl
    i0 = npml + 2 * ppl
    i_f = i0 + 3 * ppl
    nx = i_f + d_nodos + 8 * ppl + npml
    eps = np.ones((nx, ny))
    eps[i_f:i_f + d_nodos, :] = n ** 2
    sim = f.FDTD(nx, ny, ppl, eps=eps, npml=npml, periodico_y=True, n_p=n_p)
    sim.preparar_plana(ky, i0)
    cols = {"r": np.arange(npml + 4 * ppl // 4, i0 - 4), "t": np.arange(i_f + d_nodos + 4, nx - npml - 4)}
    lineas = {f"c{i}": i for i in np.concatenate([cols["r"], cols["t"]])}
    t0 = time.process_time()
    res = sim.ejecutar(periodos, ventana, lineas)
    t_cpu = time.process_time() - t0
    y = np.arange(ny) * h
    kx = float(f.kx_fdtd(np.array([ky]), ppl, n_p)[0])
    x = np.arange(nx) * h
    x_front, x_back = (i_f - 0.5) * h, (i_f + d_nodos - 0.5) * h
    a_front = np.exp(1j * kx * (x_front - x[i0]))
    def perfil(i):
        return np.mean(res["fasores"][f"c{i}"] * np.exp(-1j * ky * y))
    r_est = np.array([perfil(i) * np.exp(1j * kx * (x[i] - x_front)) / a_front for i in cols["r"]])
    t_est = np.array([perfil(i) * np.exp(-1j * kx * (x[i] - x_back)) / a_front for i in cols["t"]])
    r, t = complex(r_est.mean()), complex(t_est.mean())
    rc, tc = cal.a_plano_medio(r, t, d_nodos * h, kx)
    return dict(r=r, t=t, r_c=complex(rc), t_c=complex(tc), disp_r=float(np.std(r_est)),
                disp_t=float(np.std(t_est)), t_cpu_s=t_cpu, ny=ny, ky=ky, err_angulo_rel=err_ang)


def calibrar_fdtd(ppl, n_ini):
    d_nodos = int(round(cal.D_NOMINAL * ppl))
    n, n_ant, R_ant = n_ini, None, None
    pasos = []
    for _ in range(10):
        res = rt_fdtd(ppl, n, d_nodos)
        R, T = abs(res["r"]) ** 2, abs(res["t"]) ** 2
        dR, dT = R - 0.5, T - 0.5
        pasos.append(dict(n=n, R=float(R), T=float(T), dif_R=float(dR), dif_T=float(dT), disp_r=res["disp_r"], disp_t=res["disp_t"]))
        if abs(dR) < TOL and abs(dT) < TOL:
            break
        n_prev = n
        n = n + dR * 2.0 if n_ant is None else n - dR * (n - n_ant) / (R - R_ant)
        n_ant, R_ant = n_prev, R
        pasos[-1]["ajuste"] = f"n {n_prev:.6f} -> {n:.6f}"
    else:
        raise RuntimeError("no converge")
    nf = pasos[-1]["n"]
    return dict(ppl=ppl, d_nodos=d_nodos, d_lambda=d_nodos / ppl, n_inicial_helmholtz=n_ini, n_usado=nf,
                ajustado=bool(abs(nf - n_ini) > 1e-9), pasos=pasos, cumple=True,
                solver=dict(r_re=res["r"].real, r_im=res["r"].imag, t_re=res["t"].real, t_im=res["t"].imag, R=float(R), T=float(T)),
                plano_medio=dict(r_re=res["r_c"].real, r_im=res["r_c"].imag, t_re=res["t_c"].real, t_im=res["t_c"].imag),
                dif_R=float(dR), dif_T=float(dT), t_cpu_s=res["t_cpu_s"], ny=res["ny"], err_angulo_rel=res["err_angulo_rel"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ppl", type=int, nargs="+", default=[16, 24])
    ap.add_argument("--salida", default="calibracion_fdtd_45.json")
    a = ap.parse_args()
    ini = json.load(open("calibracion_45.json"))["mallas"]
    out = dict(angulo_deg=45.0, d_nominal_lambda=cal.D_NOMINAL, tolerancia=TOL, solver="FDTD", mallas={})
    for p in a.ppl:
        c = calibrar_fdtd(p, ini[str(p)]["n_usado"])
        out["mallas"][str(p)] = c
        print(f"ppl={p}: n {c['n_inicial_helmholtz']:.5f} -> {c['n_usado']:.5f}  R={c['solver']['R']:.5f} T={c['solver']['T']:.5f} "
              f"primer dif_R={c['pasos'][0]['dif_R']:+.4f} pasos={len(c['pasos'])}", flush=True)
    json.dump(out, open(a.salida, "w"), indent=1)


if __name__ == "__main__":
    main()
