"""Solver de referencia P1-7: Helmholtz escalar 2D (TM), frecuencia, CPU.

Unidades: lambda = 1 (k = 2 pi). Convencion temporal exp(-i w t): ondas salientes exp(+i k x).
Esquema: diferencias finitas de 5 puntos, PML por estiramiento complejo de coordenadas
(s = 1 + i a (u/L)^m), resolucion directa dispersa (scipy splu).

Fuente (sin dispersion numerica espuria): inyeccion unidireccional. Se define el campo
incidente F = E_inc para x >= x0 y 0 para x < x0 (E_inc = solucion exacta de la ecuacion
discreta de vacio, por espectro angular con la relacion de dispersion discreta). El termino
fuente b = A_vac F solo es distinto de cero en las columnas i0-1 e i0, y el campo resuelto
es F en el vacio: la fuente es transparente a las ondas que vuelven hacia ella.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

K0 = 2.0 * np.pi  # numero de onda en vacio con lambda = 1


@dataclass
class Malla:
    """Malla uniforme (nx, ny) de paso h (en lambdas). Indice plano = i * ny + j."""

    nx: int
    ny: int
    h: float
    pml_x: int = 0          # celdas de PML en cada extremo de x
    pml_y: int = 0          # celdas de PML en cada extremo de y (0 con periodico_y)
    periodico_y: bool = False
    r0: float = 1e-8        # reflexion teorica objetivo de la PML continua (amplitud^2)
    orden: int = 2          # orden del perfil polinomico
    bloch_ky: float = 0.0   # fase de Bloch en y (periodico_y): E(y+Ly) = E(y) exp(i ky Ly)

    def x(self) -> np.ndarray:
        return np.arange(self.nx) * self.h

    def y(self) -> np.ndarray:
        return np.arange(self.ny) * self.h


def construir_malla(lx: float, ly: float, h: float, pml: float, periodico_y: bool = False,
                    pml_en_y: bool = True, r0: float = 1e-8) -> Malla:
    """Malla para un dominio fisico lx x ly (lambdas) mas una PML de grosor `pml` (lambdas)
    en cada borde. Devuelve la malla con nx, ny incluyendo la PML."""
    npml = int(round(pml / h))
    nx = int(round(lx / h)) + 1 + 2 * npml
    if periodico_y:
        ny = int(round(ly / h))
        return Malla(nx, ny, h, npml, 0, True, r0)
    py = npml if pml_en_y else 0
    ny = int(round(ly / h)) + 1 + 2 * py
    return Malla(nx, ny, h, npml, py, False, r0)


def _perfil_estiramiento(n: int, npml: int, h: float, k: float, r0: float, orden: int):
    """Factores de estiramiento s en nodos (n) y en semi-nodos (n-1, posicion i+1/2)."""
    if npml == 0:
        return np.ones(n, complex), np.ones(max(n - 1, 0), complex)
    grosor = npml * h
    a = (orden + 1) * np.log(1.0 / r0) / (2.0 * k * grosor)

    def s_en(pos):  # pos en unidades de celdas
        u = np.zeros_like(pos)
        izq = pos < npml
        der = pos > (n - 1 - npml)
        u[izq] = (npml - pos[izq]) * h
        u[der] = (pos[der] - (n - 1 - npml)) * h
        return 1.0 + 1j * a * (u / grosor) ** orden

    nodos = np.arange(n, dtype=float)
    semis = nodos[:-1] + 0.5
    return s_en(nodos), s_en(semis)


def construir_operador(m: Malla, n2: np.ndarray | None = None, pec: np.ndarray | None = None,
                       k: float = K0, vacio: bool = False) -> sp.csc_matrix:
    """Operador A = (1/sx) d/dx((1/sx) d/dx) + (1/sy) d/dy((1/sy) d/dy) + k^2 n^2.

    n2: indice al cuadrado por nodo, forma (nx, ny) (por defecto 1).
    pec: mascara booleana (nx, ny) de nodos conductores perfectos (E = 0): fila identidad.
    vacio=True construye el operador sin PML (para el termino fuente / comprobaciones).
    Contorno externo: Dirichlet (E=0) tras la PML; periodico en y si m.periodico_y.
    """
    nx, ny, h = m.nx, m.ny, m.h
    px, py = (0, 0) if vacio else (m.pml_x, 0 if m.periodico_y else m.pml_y)
    sxn, sxh = _perfil_estiramiento(nx, px, h, k, m.r0, m.orden)
    syn, syh = _perfil_estiramiento(ny, py, h, k, m.r0, m.orden)
    if n2 is None:
        n2 = np.ones((nx, ny))
    ih2 = 1.0 / h ** 2
    N = nx * ny
    idx = np.arange(N).reshape(nx, ny)

    # coeficientes de acoplamiento en x: hacia i+1 (usa semi-nodo i) y hacia i-1 (semi-nodo i-1)
    cxp = np.zeros((nx, ny), complex)
    cxm = np.zeros((nx, ny), complex)
    cxp[:-1, :] = ih2 / (sxn[:-1, None] * sxh[:, None])
    cxm[1:, :] = ih2 / (sxn[1:, None] * sxh[:, None])
    diag = -(cxp + cxm)
    # y
    cyp = np.zeros((nx, ny), complex)
    cym = np.zeros((nx, ny), complex)
    if m.periodico_y:
        cyp[:, :] = ih2
        cym[:, :] = ih2
    else:
        cyp[:, :-1] = ih2 / (syn[None, :-1] * syh[None, :])
        cym[:, 1:] = ih2 / (syn[None, 1:] * syh[None, :])
    diag = diag - (cyp + cym) + (k ** 2) * n2   # (cyp, cym sin fase de Bloch en este punto)

    filas, cols, vals = [], [], []

    # x
    filas.append(idx[:-1, :].ravel()); cols.append(idx[1:, :].ravel()); vals.append(cxp[:-1, :].ravel())
    filas.append(idx[1:, :].ravel()); cols.append(idx[:-1, :].ravel()); vals.append(cxm[1:, :].ravel())
    # y
    if m.periodico_y:
        jp = (np.arange(ny) + 1) % ny
        jm = (np.arange(ny) - 1) % ny
        fase = np.exp(1j * m.bloch_ky * ny * h)
        cyp[:, ny - 1] *= fase          # vecino j=ny esta en j=0 desplazado Ly
        cym[:, 0] /= fase
        filas.append(idx.ravel()); cols.append(idx[:, jp].ravel()); vals.append(cyp.ravel())
        filas.append(idx.ravel()); cols.append(idx[:, jm].ravel()); vals.append(cym.ravel())
    else:
        filas.append(idx[:, :-1].ravel()); cols.append(idx[:, 1:].ravel()); vals.append(cyp[:, :-1].ravel())
        filas.append(idx[:, 1:].ravel()); cols.append(idx[:, :-1].ravel()); vals.append(cym[:, 1:].ravel())
    filas.append(idx.ravel()); cols.append(idx.ravel()); vals.append(diag.ravel())

    A = sp.coo_matrix((np.concatenate(vals), (np.concatenate(filas), np.concatenate(cols))),
                      shape=(N, N)).tocsr()
    if pec is not None and pec.any():
        # fila identidad en nodos PEC; se anulan tambien las columnas hacia ellos? No: en las filas
        # vecinas el valor E_pec = 0 se impone por la propia fila identidad (E_pec = 0).
        d = np.ones(N)
        d[pec.ravel()] = 0.0
        A = sp.diags(d) @ A + sp.diags(1.0 - d)
    return A.tocsc()


# --------------------------------------------------------------------------- campo incidente
def kx_discreto(ky: np.ndarray, h: float, k: float = K0) -> np.ndarray:
    """Componente kx exacta de la ecuacion discreta de 5 puntos en vacio (NaN si evanescente)."""
    c = 2.0 - np.cos(ky * h) - (k * h) ** 2 / 2.0
    out = np.full(np.shape(ky), np.nan)
    ok = np.abs(c) <= 1.0
    out[ok] = np.arccos(c[ok]) / h
    return out


def haz_gaussiano(m: Malla, w: float, x_cintura: float, y_centro: float, angulo_deg: float = 0.0,
                  k: float = K0, n_espectro: int | None = None) -> np.ndarray:
    """Haz gaussiano E ~ exp(-(y'/w)^2) (w = radio 1/e de amplitud) como solucion exacta de la
    ecuacion discreta de vacio. Se obtiene por superposicion de ondas planas discretas con
    espectro gaussiano. angulo_deg: inclinacion respecto a +x (positivo hacia +y).
    Forma (nx, ny); amplitud 1 en el eje en la cintura."""
    x = m.x()[:, None, None]
    y = m.y()[None, :, None]
    ky0 = k * np.sin(np.deg2rad(angulo_deg))
    ancho_k = 2.0 / w                                   # a 1/e del espectro de amplitud
    n_espectro = n_espectro or 401
    kys = ky0 + np.linspace(-4.5 * ancho_k, 4.5 * ancho_k, n_espectro)
    kx = kx_discreto(kys, m.h, k)
    ok = np.isfinite(kx)
    kys, kx = kys[ok], kx[ok]
    amp = np.exp(-((kys - ky0) * w / 2.0) ** 2)
    amp = amp / amp.sum()                               # amplitud 1 en el eje de la cintura
    campo = np.zeros((m.nx, m.ny), complex)
    # sumar por bloques de k para acotar memoria
    for b0 in range(0, len(kys), 40):
        sl = slice(b0, b0 + 40)
        fase = (1j * kx[sl][None, None, :] * (x - x_cintura)
                + 1j * (kys[sl][None, None, :] - ky0) * (y - y_centro))
        campo += (amp[sl][None, None, :] * np.exp(fase)).sum(axis=2)
    # modulacion de la inclinacion (la portadora es exp(i ky0 y) con kx(ky) ya incluido)
    fase_portadora = np.exp(1j * ky0 * (m.y()[None, :] - y_centro))
    return campo * fase_portadora


def k_diagonal(h: float, k: float = K0) -> float:
    """Numero de onda kx = ky de la onda plana discreta exacta a 45 grados en la malla."""
    return float(np.arccos(1.0 - (k * h) ** 2 / 4.0) / h)


def onda_plana(m: Malla, x0: float = 0.0, k: float = K0, ky: float = 0.0) -> np.ndarray:
    """Onda plana discreta exacta, amplitud 1 en (x0, y=0). ky=0: incidencia normal; para 45 grados
    usar ky = k_diagonal(h) (kx se obtiene de la relacion de dispersion discreta)."""
    kx = float(kx_discreto(np.array([ky]), m.h, k)[0])
    return np.exp(1j * kx * (m.x()[:, None] - x0) + 1j * ky * m.y()[None, :])


def fuente_unidireccional(m: Malla, campo_inc: np.ndarray, i0: int, k: float = K0) -> np.ndarray:
    """Vector b (plano) que inyecta `campo_inc` hacia +x desde la columna i0 (transparente)."""
    b = np.zeros((m.nx, m.ny), complex)
    ih2 = 1.0 / m.h ** 2
    b[i0 - 1, :] = campo_inc[i0, :] * ih2
    b[i0, :] = -campo_inc[i0 - 1, :] * ih2
    return b.ravel()


# --------------------------------------------------------------------------- resolucion
@dataclass
class Factor:
    lu: object
    t_factor: float
    nnz_lu: int


def factorizar(A: sp.csc_matrix, permc: str = "MMD_AT_PLUS_A") -> Factor:
    t0 = time.process_time()
    lu = spla.splu(A, permc_spec=permc)
    return Factor(lu, time.process_time() - t0, lu.L.nnz + lu.U.nnz)


def resolver(f: Factor, b: np.ndarray, m: Malla) -> np.ndarray:
    return f.lu.solve(b).reshape(m.nx, m.ny)


# --------------------------------------------------------------------------- medidas
def potencia_solapamiento(E_col: np.ndarray, m: Malla, w: float, y_centro: float,
                          angulo_deg: float = 0.0, k: float = K0) -> float:
    """Potencia por solapamiento del campo en una columna (corte x = cte) con el modo gaussiano
    g(y) = exp(-((y-yc)/w)^2) exp(i k sin(a) (y - yc)):  P = |<g,E>|^2 / <g,g>  (unidades de
    amplitud^2 * longitud; dividir por la misma magnitud del haz de entrada para normalizar)."""
    y = m.y()
    g = np.exp(-((y - y_centro) / w) ** 2) * np.exp(1j * k * np.sin(np.deg2rad(angulo_deg)) * (y - y_centro))
    c = np.sum(np.conj(g) * E_col) * m.h
    return float(np.abs(c) ** 2 / (np.sum(np.abs(g) ** 2) * m.h))


def potencia_modo_entrada(m: Malla, w: float) -> float:
    """Potencia por solapamiento del propio haz de entrada (amplitud 1): = integral exp(-2y^2/w^2)."""
    return float(w * np.sqrt(np.pi / 2.0))


def flujo_energia(E_col: np.ndarray, m: Malla) -> float:
    """Integral de |E|^2 dy en una columna (referencia de energia, sin factor de velocidad)."""
    return float(np.sum(np.abs(E_col) ** 2) * m.h)
