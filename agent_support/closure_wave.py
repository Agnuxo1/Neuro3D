"""Paraxial controls and complex modal projection for a declared scalar regime.

These controls support a new wave-validation protocol. They do not implement
the complete Neuro3D device or establish vector electromagnetic fidelity.
"""
from __future__ import annotations

import math
import numpy as np


def gaussian_1d(y, distance: float, wavelength: float, waist: float) -> np.ndarray:
    """Propagate a 1-transverse-dimensional Gaussian with its phase and Gouy term.

    The convention is exp(-i*omega*t), exp(+i*k*z); waist field exp(-y^2/w0^2).
    The amplitude factor is sqrt(w0/w), appropriate for one transverse dimension.
    """
    y = np.asarray(y, dtype=float)
    if not np.isfinite(y).all() or not all(math.isfinite(x) for x in (distance, wavelength, waist)) or wavelength <= 0 or waist <= 0:
        raise ValueError("Finite coordinates and positive wavelength/waist are required")
    k = 2*math.pi/wavelength
    rayleigh = math.pi*waist*waist/wavelength
    ratio = distance/rayleigh
    width = waist*math.sqrt(1+ratio*ratio)
    inverse_radius = distance/(distance*distance+rayleigh*rayleigh)
    phase = k*distance + 0.5*k*inverse_radius*y*y - 0.5*math.atan(ratio)
    return math.sqrt(waist/width)*np.exp(-(y/width)**2)*np.exp(1j*phase)


def angular_spectrum_1d(field, spacing: float, distance: float, wavelength: float) -> np.ndarray:
    """Use an FFT outgoing Helmholtz propagator on a finite periodic 1D window."""
    e = np.asarray(field, dtype=np.complex128)
    if e.ndim != 1 or len(e) < 8 or not np.isfinite(e).all() or spacing <= 0 or wavelength <= 0 or distance < 0 or not all(math.isfinite(v) for v in (spacing, distance, wavelength)):
        raise ValueError("A finite 1D field, positive spacing/wavelength, and nonnegative distance are required")
    k = 2*math.pi/wavelength
    ky = 2*math.pi*np.fft.fftfreq(len(e), d=spacing)
    kz = np.sqrt((k*k-ky*ky).astype(np.complex128))
    return np.fft.ifft(np.fft.fft(e)*np.exp(1j*kz*distance))


def modal_amplitude(field, reference_mode, spacing: float) -> complex:
    """Project onto a declared mode; retain complex phase instead of only power."""
    e, g = np.asarray(field, dtype=np.complex128), np.asarray(reference_mode, dtype=np.complex128)
    if e.ndim != 1 or e.shape != g.shape or not np.isfinite(e).all() or not np.isfinite(g).all() or spacing <= 0 or not math.isfinite(spacing):
        raise ValueError("Matched finite 1D arrays and a positive spacing are required")
    norm = float(np.vdot(g, g).real*spacing)
    if norm <= 0:
        raise ValueError("A zero reference mode has no defined modal amplitude")
    return complex(np.vdot(g, e)*spacing/norm)


def circular_phase_difference(a: complex, b: complex, dark_floor: float = 1e-12) -> float | None:
    """Return a wrapped phase difference; a dark field has undefined phase."""
    a, b = complex(a), complex(b)
    if not all(math.isfinite(v) for v in (a.real, a.imag, b.real, b.imag, dark_floor)) or dark_floor <= 0:
        raise ValueError("Finite fields and a positive dark-field floor are required")
    if abs(a) <= dark_floor or abs(b) <= dark_floor:
        return None
    return float(np.angle(a*np.conjugate(b)))


def observed_order(coarse: complex, medium: complex, fine: complex, refinement_ratio: float) -> dict:
    """Estimate convergence order for three matched observables and fixed geometry."""
    values = [complex(v) for v in (coarse, medium, fine)]
    if not all(math.isfinite(x) for v in values for x in (v.real, v.imag)) or refinement_ratio <= 1 or not math.isfinite(refinement_ratio):
        raise ValueError("Finite observables and a refinement ratio greater than one are required")
    d1, d2 = abs(values[0]-values[1]), abs(values[1]-values[2])
    if d1 == 0 or d2 == 0:
        return {"status": "INCONCLUSIVE", "reason": "ZERO_DIFFERENCE", "coarse_medium": d1, "medium_fine": d2}
    p = math.log(d1/d2)/math.log(refinement_ratio)
    return {"status": "DIAGNOSTIC", "order": p, "coarse_medium": d1, "medium_fine": d2,
            "scope": "Observed asymptotic diagnostic; neither a rigorous error bound nor proof that the asymptotic regime has been reached"}
