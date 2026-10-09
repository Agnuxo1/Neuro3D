"""MZI a 45 grados (Enmienda 1 del preregistro P1-7): geometria, modelo de caminos y estimacion
de dominio. ESTADO: la parte de ondas (barrido ΔL con el solver) NO se lanzo: la medicion de coste
(resultados/medicion_coste.json, INFORME-EJECUCION-P1-7.md) muestra que el dominio no cabe.

Geometria (lambda = 1): haz de entrada viaja en (1,1)/sqrt2 hacia S1 en el origen. Todos los
elementos (divisores y espejos) son segmentos VERTICALES (alineados con la malla; los haces van a
45 grados): S1 (0,0), M_A (a,a), M_B (-a,a), S2 (0,2a), con a = L/sqrt2 y L ~ 30 (brazo = tramo
divisor-espejo). Brazo A (transmitido en S1): (1,1) -> M_A -> (-1,1) -> S2. Brazo B (reflejado):
(-1,1) -> M_B -> (1,1) -> S2. Salidas: P1 en direccion (1,1) = t*B + r*A ; P2 en (-1,1) = t*A + r*B.
"""
from __future__ import annotations

import numpy as np

K0 = 2.0 * np.pi


def modelo_caminos(r: complex, t: complex, delta_L: np.ndarray | float, L: float = 60.0,
                   espejo: complex = -1.0, k: float = K0):
    """Potencias (P1, P2) del modelo escalar ideal sin difraccion. r, t: coeficientes (complejos)
    del divisor referidos a su plano medio. L: recorrido total del brazo B; el brazo A mide L + ΔL.
    Propagacion exp(i k L); espejos `espejo` (-1) en cada brazo; entrada de amplitud 1."""
    dL = np.asarray(delta_L, float)
    A = espejo * t * np.exp(1j * k * (L + dL))     # brazo A: transmitido en S1
    B = espejo * r * np.exp(1j * k * L)            # brazo B: reflejado en S1
    P1 = np.abs(t * B + r * A) ** 2                # direccion (1,1)
    P2 = np.abs(t * A + r * B) ** 2                # direccion (-1,1)
    return P1, P2


def dominio_estimado(w: float, ppl: int, L: float = 30.0, pml: float = 3.0) -> dict:
    """Numero de incognitas del dominio rectangular que contiene el interferometro y sus haces
    (semianchura del haz 2w, longitud de elementos 2*sqrt2*w, PML a cada lado)."""
    a = L / np.sqrt(2.0)
    b = 2.0 * w                                    # semianchura del haz (amplitud 1,8 %)
    lx = 2.0 * (a + b / np.sqrt(2.0) + 0.5 * b)    # cota conservadora en x
    ly = (2.0 * a) + 2.0 * (2.0 * np.sqrt(2.0) * w) # S1..S2 mas semilongitud de elementos arriba y abajo
    nx = int((lx + 2 * pml) * ppl)
    ny = int((ly + 2 * pml) * ppl)
    return dict(w=w, ppl=ppl, lx=lx, ly=ly, nx=nx, ny=ny, N=nx * ny)
