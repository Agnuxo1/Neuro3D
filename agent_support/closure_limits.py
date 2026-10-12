"""Physical reference scales and function-class baselines for the frontier fronts.

Nothing here measures hardware. Photon budgets assume ideal Poisson detection
with a declared efficiency and are design scales, not bounds on any device.
The trainer is a digital comparator for the nested-class ablation
(free complex W, passive W, geometry-realizable W); it is not Neuro3D.
"""
from __future__ import annotations

import math
from typing import Callable

import numpy as np

PLANCK = 6.62607015e-34       # J s, exact in the 2019 SI
LIGHT_SPEED = 299792458.0     # m/s, exact in the SI
BOLTZMANN = 1.380649e-23      # J/K, exact in the 2019 SI


def photon_energy(wavelength_m: float) -> float:
    """Energy of one photon in joules."""
    if not math.isfinite(wavelength_m) or wavelength_m <= 0:
        raise ValueError("A positive finite wavelength is required")
    return PLANCK*LIGHT_SPEED/wavelength_m


def shot_noise_photons(bits: int, separation_sigmas: float = 2.0) -> float:
    """Full-scale photon count so adjacent levels sit k Poisson sigmas apart.

    With 2**bits levels spaced N/2**bits and full-scale std sqrt(N), the
    requirement N/2**bits >= k*sqrt(N) gives N >= k**2 * 4**bits. With a
    midpoint threshold the adjacent-level error is about Phi(-k/2).
    """
    if not 1 <= bits <= 24 or not math.isfinite(separation_sigmas) or separation_sigmas <= 0:
        raise ValueError("1..24 bits and a positive separation are required")
    return separation_sigmas**2*4.0**bits


def detection_energy_per_mac(bits: int, wavelength_m: float, fan_in: int,
                             efficiency: float = 1.0, separation_sigmas: float = 2.0) -> float:
    """Optical detection energy per multiply-accumulate under the stated model.

    One detected output aggregates fan_in products, so its photon budget is
    shared among them. Lasers, modulators, DAC/ADC and electronics are excluded
    and must be measured separately before any efficiency claim.
    """
    if fan_in < 1 or not 0 < efficiency <= 1:
        raise ValueError("fan_in >= 1 and 0 < efficiency <= 1 are required")
    return shot_noise_photons(bits, separation_sigmas)*photon_energy(wavelength_m)/(efficiency*fan_in)


def landauer_energy(temperature_k: float = 300.0) -> float:
    """kT ln 2: a reference scale for irreversible bit erasure, not an optical bound."""
    if not math.isfinite(temperature_k) or temperature_k <= 0:
        raise ValueError("A positive finite temperature is required")
    return BOLTZMANN*temperature_k*math.log(2)


def spectral_norm(matrix: np.ndarray) -> float:
    """Largest singular value; a passive linear optical operator has value <= 1."""
    m = np.asarray(matrix, dtype=np.complex128)
    if m.ndim != 2 or not np.isfinite(m).all():
        raise ValueError("A finite matrix is required")
    return float(np.linalg.norm(m, 2))


def is_passive(matrix: np.ndarray, tolerance: float = 1e-12) -> bool:
    """True when the represented operator cannot amplify total modal power."""
    return spectral_norm(matrix) <= 1+tolerance


def project_passive(matrix: np.ndarray) -> np.ndarray:
    """Nearest contraction in Frobenius norm: clip singular values at one."""
    m = np.asarray(matrix, dtype=np.complex128)
    if m.ndim != 2 or not np.isfinite(m).all():
        raise ValueError("A finite matrix is required")
    u, s, vh = np.linalg.svd(m, full_matrices=False)
    return (u*np.minimum(s, 1.0))@vh


def numerical_jacobian(function: Callable[[np.ndarray], np.ndarray], theta, step: float = 1e-6) -> np.ndarray:
    """Central-difference Jacobian of a complex array map, flattened as [Re, Im]."""
    x = np.asarray(theta, dtype=float)
    if x.ndim != 1 or not np.isfinite(x).all() or not 0 < step < 1:
        raise ValueError("A finite parameter vector and 0 < step < 1 are required")
    def flat(v):
        y = np.asarray(function(v), dtype=np.complex128).ravel()
        if not np.isfinite(y).all():
            raise ValueError("The map returned non-finite values")
        return np.concatenate([y.real, y.imag])
    columns = []
    for j in range(len(x)):
        e = np.zeros_like(x)
        e[j] = step
        columns.append((flat(x+e)-flat(x-e))/(2*step))
    return np.column_stack(columns)


def effective_rank(jacobian: np.ndarray, relative_tolerance: float = 1e-7) -> dict:
    """Numerical local dimension of a reachable set at one point.

    The count depends on the declared tolerance and finite-difference error;
    report the singular values, never the rank alone.
    """
    j = np.asarray(jacobian, dtype=float)
    if j.ndim != 2 or not np.isfinite(j).all() or not 0 < relative_tolerance < 1:
        raise ValueError("A finite 2D Jacobian and 0 < tolerance < 1 are required")
    s = np.linalg.svd(j, compute_uv=False)
    rank = 0 if not s.size or s[0] == 0 else int((s > relative_tolerance*s[0]).sum())
    return {"rank": rank, "singular_values": s.tolist(), "relative_tolerance": relative_tolerance}


def detector_loss(a: np.ndarray, b: np.ndarray, x: np.ndarray, y: np.ndarray, scale: float):
    """Softmax cross-entropy on scaled detector powers |(A+iB)x|^2 and its gradients."""
    e = x@(a+1j*b).T
    z = scale*np.abs(e)**2
    z -= z.max(axis=1, keepdims=True)
    p = np.exp(z)
    p /= p.sum(axis=1, keepdims=True)
    n = len(y)
    loss = float(-np.log(p[np.arange(n), y]).mean())
    g = p.copy()
    g[np.arange(n), y] -= 1.0
    g *= scale/n
    return loss, 2*(g*e.real).T@x, 2*(g*e.imag).T@x


def train_detector_classifier(x, y, modes: int, *, passive: bool = True, steps: int = 400,
                              learning_rate: float = 0.05, scale: float = 10.0, seed: int = 0) -> dict:
    """Fit argmax_j |W_j x|^2 by Adam, projecting onto contractions when passive.

    Inputs are real encodings (n, sources); labels are detector indices. This
    is the digital comparator for F1: it shows what a linear optical function
    class can do on the same encoding and data split. argmax decisions are
    invariant to positive scaling of W, so free and passive classes share
    their decision functions; passivity matters only under a fixed detection
    gain or photon budget, which `scale` models here.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y)
    if x.ndim != 2 or not np.isfinite(x).all() or y.shape != (len(x),) or modes < 2:
        raise ValueError("Finite (samples, sources) inputs, matched labels and >= 2 modes are required")
    if not np.issubdtype(y.dtype, np.integer) or y.min() < 0 or y.max() >= modes:
        raise ValueError("Labels must be integers in [0, modes)")
    if steps < 1 or not 0 < learning_rate < 1 or not math.isfinite(scale) or scale <= 0:
        raise ValueError("Positive steps, 0 < learning_rate < 1 and a positive scale are required")
    rng = np.random.default_rng(seed)
    sources = x.shape[1]
    a = rng.normal(0, 1/math.sqrt(2*sources), (modes, sources))
    b = rng.normal(0, 1/math.sqrt(2*sources), (modes, sources))
    if passive:
        w = project_passive(a+1j*b)
        a, b = w.real.copy(), w.imag.copy()
    moments = [np.zeros_like(a), np.zeros_like(b), np.zeros_like(a), np.zeros_like(b)]
    history = []
    for t in range(1, steps+1):
        loss, ga, gb = detector_loss(a, b, x, y, scale)
        history.append(loss)
        for k, (param, grad) in enumerate(((a, ga), (b, gb))):
            moments[k] = 0.9*moments[k]+0.1*grad
            moments[k+2] = 0.999*moments[k+2]+0.001*grad*grad
            mhat = moments[k]/(1-0.9**t)
            vhat = moments[k+2]/(1-0.999**t)
            param -= learning_rate*mhat/(np.sqrt(vhat)+1e-12)
        if passive:
            w = project_passive(a+1j*b)
            a, b = w.real.copy(), w.imag.copy()
    w = a+1j*b
    predictions = np.argmax(np.abs(x@w.T)**2, axis=1)
    return {"W": w, "loss_history": history, "train_accuracy": float((predictions == y).mean()),
            "spectral_norm": spectral_norm(w), "passive_constraint": passive, "seed": seed,
            "scope": "Digital comparator class; not a geometry-realizable Neuro3D network"}
