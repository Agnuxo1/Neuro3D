"""FDTD escalar 2D (modo TM: Ez, Hx, Hy) de referencia para P1-7 (Enmienda 2). CPU, numpy, float32.

Unidades: lambda = 1, c = 1, epsilon0 = mu0 = 1 (periodo T = 1). Malla de Yee: Ez en nodos (i, j),
Hy en (i+1/2, j), Hx en (i, j+1/2). Paso temporal dt = 1/N_p (N_p pasos por periodo, entero, para que
la DFT sobre un numero entero de periodos sea exacta). PML convolucional (CPML, kappa = 1) en los
cuatro bordes (o periodicidad en y). Fuente: haz inyectado por una linea vertical x = x0 con la
tecnica campo total/campo disperso, que lo emite solo hacia +x; el campo del haz sale de la relacion
de dispersion de la propia malla FDTD. Onda continua con encendido suave (rampa de coseno elevado).
El fasor (convencion exp(-i w t)) se extrae acumulando una DFT sobre la ultima ventana (periodos enteros).
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

import numpy as np

OMEGA = 2.0 * np.pi


def pasos_por_periodo(ppl: int) -> int:
    """Menor N_p entero con Courant dt/h = ppl/N_p <= 0,68 (estable en 2D: 1/sqrt2 = 0,707)."""
    return int(np.ceil(ppl / 0.68))


def ky_diagonal(ppl: int, n_p: int) -> float:
    """ky = kx de la onda plana FDTD a 45 grados (relacion de dispersion discreta)."""
    h, dt = 1.0 / ppl, 1.0 / n_p
    s2 = 0.5 * ((h / dt) * np.sin(OMEGA * dt / 2.0)) ** 2
    return float(2.0 / h * np.arcsin(np.sqrt(s2)))


def kx_fdtd(ky, ppl: int, n_p: int):
    """kx(ky) de la ecuacion discreta FDTD (NaN si evanescente)."""
    h, dt = 1.0 / ppl, 1.0 / n_p
    # sin^2(kx h/2) = (h/dt)^2 sin^2(w dt/2) - sin^2(ky h/2)
    v = ((h / dt) * np.sin(OMEGA * dt / 2.0)) ** 2 - np.sin(np.asarray(ky) * h / 2.0) ** 2
    out = np.full(np.shape(v), np.nan)
    ok = (v >= 0) & (v <= 1)
    out[ok] = 2.0 / h * np.arcsin(np.sqrt(v[ok]))
    return out


@dataclass
class Haz:
    """Haz gaussiano inyectado en la columna i0 (perfil de Ez en y, centrado en yc)."""
    w: float                 # radio 1/e de amplitud, perpendicular a la propagacion
    yc: float                # centro del haz en la columna de inyeccion (lambdas, coordenada y de la malla)
    angulo_deg: float = 45.0  # 45 -> diagonal FDTD exacta; 0 -> normal
    i0: int = 0


class FDTD:
    def __init__(self, nx: int, ny: int, ppl: int, eps: np.ndarray | None = None,
                 pec: np.ndarray | None = None, npml: int = 0, periodico_y: bool = False,
                 n_p: int | None = None, m_pml: int = 3, alfa_max: float = 0.24):
        self.nx, self.ny, self.ppl = nx, ny, ppl
        self.h = 1.0 / ppl
        self.n_p = n_p or pasos_por_periodo(ppl)
        self.dt = 1.0 / self.n_p
        self.S = self.dt / self.h
        assert self.S < 1 / np.sqrt(2)
        self.periodico = periodico_y
        f32 = np.float32
        self.Ez = np.zeros((nx, ny), f32)
        self.Hy = np.zeros((nx - 1, ny), f32)
        self.Hx = np.zeros((nx, ny if periodico_y else ny - 1), f32)
        e = np.ones((nx, ny)) if eps is None else eps
        cE = self.S / e
        if pec is not None:
            cE = np.where(pec, 0.0, cE)
        self.cE = cE.astype(f32)
        self.S32 = f32(self.S)
        self.npml = npml
        self._cpml(m_pml, alfa_max)
        self.lineas: dict[str, list] = {}
        self.t_paso = 0.0

    # ------------------------------------------------------------------ CPML
    def _perfil(self, n: int, npml: int, medio: bool, m: int, alfa_max: float):
        """sigma, alfa por posicion (medio=True: posiciones i+1/2, n-1 puntos)."""
        pos = np.arange(n - 1) + 0.5 if medio else np.arange(n, dtype=float)
        prof = np.zeros_like(pos)
        izq = pos < npml
        der = pos > (n - 1 - npml)
        prof[izq] = (npml - pos[izq]) / npml
        prof[der] = (pos[der] - (n - 1 - npml)) / npml
        sig = 0.8 * (m + 1) / self.h * prof ** m
        alf = alfa_max * (1.0 - prof) * (prof > 0)
        b = np.exp(-(sig + alf) * self.dt)
        a = np.where(sig + alf > 0, sig / np.maximum(sig + alf, 1e-30) * (b - 1.0), 0.0)
        return b.astype(np.float32), a.astype(np.float32)

    def _cpml(self, m, alfa_max):
        n = self.npml
        nx, ny = self.nx, self.ny
        f32 = np.float32
        if n == 0:
            self.sl = None
            return
        # x: Hy (posiciones i+1/2) y Ez (nodos)
        bh, ah = self._perfil(nx, n, True, m, alfa_max)
        be, ae = self._perfil(nx, n, False, m, alfa_max)
        self.xH = dict(b=bh, a=ah, lo=slice(0, n), hi=slice(nx - 1 - n, nx - 1))
        self.xE = dict(b=be, a=ae, lo=slice(0, n + 1), hi=slice(nx - 1 - n, nx))
        self.psi_hy_lo = np.zeros((n, ny), f32); self.psi_hy_hi = np.zeros((n, ny), f32)
        self.psi_ezx_lo = np.zeros((n + 1, ny), f32); self.psi_ezx_hi = np.zeros((n + 1, ny), f32)
        self.sl = True
        if not self.periodico:
            bh, ah = self._perfil(ny, n, True, m, alfa_max)
            be, ae = self._perfil(ny, n, False, m, alfa_max)
            self.yH = dict(b=bh, a=ah, lo=slice(0, n), hi=slice(ny - 1 - n, ny - 1))
            self.yE = dict(b=be, a=ae, lo=slice(0, n + 1), hi=slice(ny - 1 - n, ny))
            self.psi_hx_lo = np.zeros((nx, n), f32); self.psi_hx_hi = np.zeros((nx, n), f32)
            self.psi_ezy_lo = np.zeros((nx, n + 1), f32); self.psi_ezy_hi = np.zeros((nx, n + 1), f32)

    # ------------------------------------------------------------------ fuente
    def preparar_haz(self, haz: Haz, u_c: float = 0.0):
        """Fasores de Ez en la columna i0 y de Hy en i0-1/2 para un haz gaussiano unidireccional.
        u_c: distancia, medida a lo largo del haz, desde la cintura hasta el punto central (x0, yc) de
        la columna (negativa si la cintura esta aguas abajo). Perfil gaussiano de ancho w en la cintura
        (formula de haz gaussiano 2D, ver INFORME)."""
        ppl, n_p, h = self.ppl, self.n_p, self.h
        y = np.arange(self.ny) * h
        if haz.angulo_deg == 45.0:
            ky0 = ky_diagonal(ppl, n_p)
            ang = np.pi / 4
        else:
            ang = np.deg2rad(haz.angulo_deg)
            ky0 = OMEGA * np.sin(ang)
        kp = ky0 / np.sin(ang) if np.sin(ang) > 1e-9 else OMEGA   # numero de onda a lo largo del haz
        s = (y - haz.yc) * np.cos(ang)
        u = u_c + (y - haz.yc) * np.sin(ang)
        zeta = 2.0 * u / (kp * haz.w ** 2)
        q = 1.0 + 1j * zeta
        E = q ** -0.5 * np.exp(-s ** 2 / (haz.w ** 2 * q)) * np.exp(1j * ky0 * (y - haz.yc))
        # Hy por componentes: G(ky) = i S (1 - exp(-i kx h)) / (2 sin(w dt/2))
        pad = 4
        nf = int(2 ** np.ceil(np.log2(self.ny * pad)))
        F = np.fft.fft(E, nf)
        ky = 2 * np.pi * np.fft.fftfreq(nf, d=h)
        kx = kx_fdtd(ky, ppl, n_p)
        G = np.zeros(nf, complex)
        ok = np.isfinite(kx)
        G[ok] = 1j * self.S * (1 - np.exp(-1j * kx[ok] * h)) / (2 * np.sin(OMEGA * self.dt / 2))
        Hf = np.fft.ifft(F * G)[: self.ny]
        self.haz = haz
        self.E_ph, self.H_ph = E, Hf

    def preparar_plana(self, ky: float, i0: int):
        """Onda plana de amplitud 1 (kx de la dispersion FDTD) inyectada en la columna i0 (periodico en y)."""
        h = self.h
        y = np.arange(self.ny) * h
        kx = float(kx_fdtd(np.array([ky]), self.ppl, self.n_p)[0])
        self.E_ph = np.exp(1j * ky * y)
        self.H_ph = self.E_ph * 1j * self.S * (1 - np.exp(-1j * kx * h)) / (2 * np.sin(OMEGA * self.dt / 2))
        self.haz = Haz(w=0.0, yc=0.0, i0=i0)

    def _fuente_Ez(self, n: int) -> np.ndarray:
        t = n * self.dt
        return (self.E_ph * np.exp(-1j * OMEGA * t)).real * self._rampa(t)

    def _fuente_Hy(self, n: int) -> np.ndarray:
        t = (n + 0.5) * self.dt
        return (self.H_ph * np.exp(-1j * OMEGA * t)).real * self._rampa(t)

    def _rampa(self, t: float) -> float:
        tr = self.t_rampa
        return 1.0 if t >= tr else 0.5 * (1.0 - np.cos(np.pi * t / tr))

    # ------------------------------------------------------------------ paso
    def _paso(self, n: int):
        Ez, Hx, Hy, S = self.Ez, self.Hx, self.Hy, self.S32
        dt = np.float32(self.dt)
        nx, ny, npml = self.nx, self.ny, self.npml
        # --- Hy y Hx
        dEx = Ez[1:, :] - Ez[:-1, :]
        Hy += S * dEx
        if self.sl:
            for lado, psi in (("lo", self.psi_hy_lo), ("hi", self.psi_hy_hi)):
                sl = self.xH[lado]
                psi *= self.xH["b"][sl, None]
                psi += self.xH["a"][sl, None] * (dEx[sl, :] / np.float32(self.h))
                Hy[sl, :] += dt * psi
        if self.periodico:
            dEy = np.roll(Ez, -1, axis=1) - Ez
            Hx -= S * dEy
        else:
            dEy = Ez[:, 1:] - Ez[:, :-1]
            Hx -= S * dEy
            if self.sl:
                for lado, psi in (("lo", self.psi_hx_lo), ("hi", self.psi_hx_hi)):
                    sl = self.yH[lado]
                    psi *= self.yH["b"][None, sl]
                    psi += self.yH["a"][None, sl] * (dEy[:, sl] / np.float32(self.h))
                    Hx[:, sl] -= dt * psi
        # --- correccion campo total/disperso en Hy(i0-1/2)
        if hasattr(self, "haz"):
            i0 = self.haz.i0
            Hy[i0 - 1, :] -= S * self._fuente_Ez(n).astype(np.float32)
        # --- Ez
        dHy = Hy[1:, :] - Hy[:-1, :]          # (nx-2, ny): nodos 1..nx-2
        if self.periodico:
            dHx = Hx - np.roll(Hx, 1, axis=1)
            Ez[1:-1, :] += self.cE[1:-1, :] * (dHy - dHx[1:-1, :])
        else:
            Ez[1:-1, 1:-1] += self.cE[1:-1, 1:-1] * (dHy[:, 1:-1] - (Hx[1:-1, 1:] - Hx[1:-1, :-1]))
            if self.sl:
                # correccion CPML en Ez: (psi_x - psi_y) con derivadas de H
                self._cpml_ez(dHy, Hx)
        if self.periodico and self.sl:
            self._cpml_ez(dHy, None)
        if hasattr(self, "haz"):
            i0 = self.haz.i0
            Ez[i0, :] -= self.cE[i0, :] * self._fuente_Hy(n).astype(np.float32)

    def _cpml_ez(self, dHy, Hx):
        """Terminos psi de la PML sobre Ez (derivadas de Hy en x y de Hx en y)."""
        Ez, h, dt = self.Ez, np.float32(self.h), np.float32(self.dt)
        nx, ny = self.nx, self.ny
        # x: derivada en nodos 1..nx-2 (dHy[k] corresponde al nodo k+1)
        for lado, psi in (("lo", self.psi_ezx_lo), ("hi", self.psi_ezx_hi)):
            sl = self.xE[lado]
            lo, hi = sl.start, sl.stop
            # nodos en [lo, hi) con derivada disponible solo en 1..nx-2
            a0, a1 = max(lo, 1), min(hi, nx - 1)
            if a1 <= a0:
                continue
            b = self.xE["b"][a0:a1, None]
            a = self.xE["a"][a0:a1, None]
            p = psi[a0 - lo:a1 - lo, :]
            p *= b
            p += a * (dHy[a0 - 1:a1 - 1, :] / h)
            j0, j1 = (0, ny) if self.periodico else (1, ny - 1)
            Ez[a0:a1, j0:j1] += self.cE[a0:a1, j0:j1] * h * p[:, j0:j1]
        if Hx is not None:
            for lado, psi in (("lo", self.psi_ezy_lo), ("hi", self.psi_ezy_hi)):
                sl = self.yE[lado]
                lo, hi = sl.start, sl.stop
                a0, a1 = max(lo, 1), min(hi, ny - 1)
                if a1 <= a0:
                    continue
                dHx = Hx[:, a0:a1] - Hx[:, a0 - 1:a1 - 1]
                b = self.yE["b"][None, a0:a1]
                a = self.yE["a"][None, a0:a1]
                p = psi[:, a0 - lo:a1 - lo]
                p *= b
                p += a * (dHx / h)
                Ez[1:-1, a0:a1] -= self.cE[1:-1, a0:a1] * h * p[1:-1, :]
        return

    # ------------------------------------------------------------------ ejecucion
    def ejecutar(self, periodos: int, ventana: int, lineas: dict[str, int] | None = None,
                 t_rampa: float = 6.0, filas: dict[str, int] | None = None) -> dict:
        """Avanza `periodos` periodos y acumula la DFT de Ez en las columnas `lineas` {nombre: i}
        durante los ultimos `ventana` periodos. Devuelve fasores y tiempos."""
        self.t_rampa = t_rampa
        total = periodos * self.n_p
        n_ini = (periodos - ventana) * self.n_p
        acum = {k: np.zeros(self.ny, complex) for k in (lineas or {})}
        acum_prev = {k: np.zeros(self.ny, complex) for k in (lineas or {})}   # ventana anterior (control de regimen)
        n_prev = n_ini - ventana * self.n_p
        tiempos = []
        t0 = time.perf_counter()
        c0 = time.process_time()
        for n in range(total):
            tp = time.perf_counter()
            self._paso(n)
            if lineas and n >= max(n_prev, 0):
                fase = np.exp(1j * OMEGA * (n + 1) * self.dt)
                destino = acum if n >= n_ini else acum_prev
                for k, i in lineas.items():
                    destino[k] += self.Ez[i, :] * fase
            if n < 40:
                tiempos.append(time.perf_counter() - tp)
        wall = time.perf_counter() - t0
        cpu = time.process_time() - c0
        N = ventana * self.n_p
        return dict(fasores={k: v * (2.0 / N) for k, v in acum.items()},
                    fasores_prev={k: v * (2.0 / N) for k, v in acum_prev.items()}, t_wall_s=wall, t_cpu_s=cpu,
                    t_por_paso_s=wall / total, pasos=total)
