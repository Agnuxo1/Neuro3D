"""Mesh-free 2D scalar (Ez) angular-spectrum reference solver for planar optical elements.

Scope. Exact plane-wave propagation in vacuum and exact operators of INFINITE planar
elements whose normal is the x axis: a lossless dielectric slab (Airy coefficients,
s-polarization, Ez out of plane) and a perfect electric conductor (r = -1). Beams are
followed sequentially through a declared element order, so finite-element truncation
and edge diffraction are NOT represented; that is the solver's only idealization in
addition to the scalar 2D TM model. Conventions: lambda = 1, exp(-i w t), exp(+i k.r).

The solver shares no code with the P1-7 FDTD. Path models (M0 without and M1 with free
Gaussian diffraction) reproduce the P1-7 formula of mzi_fdtd.haz_ideal; a regression
test checks the equality against the frozen original.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

K = 2.0 * math.pi
SQ2 = math.sqrt(2.0)


class Grid:
    """Uniform periodic sampling of the y axis shared by every beam in one solve."""

    def __init__(self, y_min: float, length: float, n: int):
        if n < 64 or length <= 0 or not math.isfinite(y_min) or not math.isfinite(length):
            raise ValueError("A finite window and at least 64 samples are required")
        self.n, self.length, self.dy = n, float(length), float(length) / n
        if math.pi / self.dy <= K:
            raise ValueError("Sampling must resolve every propagating wavenumber")
        self.y = y_min + np.arange(n) * self.dy
        self.ky = 2.0 * math.pi * np.fft.fftfreq(n, d=self.dy)
        self.propagating = np.abs(self.ky) < K
        self.kx = np.sqrt((K * K - self.ky ** 2).astype(np.complex128))


@dataclass
class Beam:
    """Spectrum (FFT of the field on the line x = x_ref) travelling in x direction +1 or -1."""
    grid: Grid
    spectrum: np.ndarray
    x_ref: float
    direction: int

    def at(self, x: float) -> "Beam":
        distance = (x - self.x_ref) * self.direction
        if distance < -1e-12:
            raise ValueError("A beam can only be propagated forward along its direction")
        phase = np.exp(1j * self.grid.kx * max(distance, 0.0))
        return Beam(self.grid, np.where(self.grid.propagating, self.spectrum * phase, 0.0), x, self.direction)

    def field(self) -> np.ndarray:
        return np.fft.ifft(self.spectrum)

    def flux(self) -> float:
        """x-directed power flux; a unit plane wave at normal incidence carries 1 per unit length."""
        g = self.grid
        weight = np.where(g.propagating, g.kx.real / K, 0.0)
        return float(np.sum(np.abs(self.spectrum) ** 2 * weight) * g.dy / g.n)

    def __add__(self, other: "Beam") -> "Beam":
        if other.grid is not self.grid or other.direction != self.direction or abs(other.x_ref - self.x_ref) > 1e-12:
            raise ValueError("Only co-referenced beams with the same direction can be superposed")
        return Beam(self.grid, self.spectrum + other.spectrum, self.x_ref, self.direction)


def discarded_evanescent(grid: Grid, spectrum: np.ndarray) -> float:
    """Largest spectral magnitude that a propagation step sets to zero, relative to the peak."""
    peak = float(np.max(np.abs(spectrum)))
    return float(np.max(np.abs(spectrum[~grid.propagating]), initial=0.0)) / peak if peak else 0.0


def slab_coefficients(ky: np.ndarray, n: float, d: float) -> tuple[np.ndarray, np.ndarray]:
    """Center-plane referenced r, t of a lossless symmetric slab for Ez (s) polarization.

    r_c, t_c multiply the incident spectrum referenced at the slab's center plane; the
    reflected and transmitted spectra are referenced at the same plane (free-space
    extrapolation). The interface-referenced values equal the project's 1D TMM
    (calibracion.rt_1d) and are converted with the same exp(-i kx0 d) factor.
    """
    if not (n >= 1 and d >= 0 and math.isfinite(n) and math.isfinite(d)):
        raise ValueError("A finite index n >= 1 and thickness d >= 0 are required")
    ky = np.asarray(ky, dtype=float)
    r_c = np.zeros(ky.shape, dtype=np.complex128)
    t_c = np.zeros(ky.shape, dtype=np.complex128)
    ok = np.abs(ky) < K          # evanescent vacuum components are discarded by the solver
    kx0 = np.sqrt(K * K - ky[ok] ** 2)
    kx1 = np.sqrt(n * n * K * K - ky[ok] ** 2)
    r01 = (kx0 - kx1) / (kx0 + kx1)
    e2 = np.exp(2j * kx1 * d)
    denominator = 1.0 - r01 ** 2 * e2
    shift = np.exp(-1j * kx0 * d)
    r_c[ok] = r01 * (1.0 - e2) / denominator * shift
    t_c[ok] = (1.0 - r01 ** 2) * np.exp(1j * kx1 * d) / denominator * shift
    return r_c, t_c


class Splitter:
    """Planar splitter at x = x_c: a physical slab or a declared ideal constant-coefficient element."""

    def __init__(self, grid: Grid, x_c: float, *, n: float | None = None, d: float = 0.25,
                 r: complex | None = None, t: complex | None = None):
        self.x_c = float(x_c)
        if n is not None:
            self.r, self.t = slab_coefficients(grid.ky, n, d)
            self.kind = {"kind": "slab", "n": n, "d": d}
        else:
            if r is None or t is None:
                raise ValueError("Either a slab index or ideal r and t are required")
            self.r = np.full(grid.n, complex(r))
            self.t = np.full(grid.n, complex(t))
            self.kind = {"kind": "ideal", "r": [complex(r).real, complex(r).imag], "t": [complex(t).real, complex(t).imag]}

    def split(self, beam: Beam) -> tuple[Beam, Beam]:
        """Return (reflected, transmitted) beams referenced at the splitter plane."""
        incident = beam.at(self.x_c)
        reflected = Beam(beam.grid, self.r * incident.spectrum, self.x_c, -beam.direction)
        transmitted = Beam(beam.grid, self.t * incident.spectrum, self.x_c, beam.direction)
        return reflected, transmitted


def mirror(beam: Beam, x_m: float) -> Beam:
    """Perfect electric conductor face at x = x_m: tangential Ez vanishes, r = -1."""
    incident = beam.at(x_m)
    return Beam(beam.grid, -incident.spectrum, x_m, -beam.direction)


def gaussian_waist_beam(grid: Grid, x_w: float, y_w: float, w: float, angle_deg: float = 45.0) -> Beam:
    """Exact Helmholtz beam whose field on its waist line through (x_w, y_w) is exp(-s^2/w^2).

    The beam-frame spectrum A(kappa) = w/(2 sqrt(pi)) exp(-kappa^2 w^2/4) is mapped to the
    global tangential wavenumber ky = K sin(alpha0 + beta), kappa = K sin(beta), with the
    exact Jacobian cos(beta)/cos(alpha). Only waves travelling in +x are generated.
    """
    if not (w > 0 and abs(angle_deg) < 90):
        raise ValueError("A positive waist and a forward beam angle are required")
    alpha0 = math.radians(angle_deg)
    ky = grid.ky
    s = np.zeros(grid.n, dtype=np.complex128)
    ok = grid.propagating
    alpha = np.arcsin(np.clip(ky[ok] / K, -1.0, 1.0))
    beta = alpha - alpha0
    forward = np.abs(beta) < math.pi / 2
    kappa = K * np.sin(beta)
    density = w / (2.0 * math.sqrt(math.pi)) * np.exp(-(kappa * w) ** 2 / 4.0) * np.cos(beta) / np.cos(alpha)
    values = np.where(forward, density, 0.0)
    dky = 2.0 * math.pi / (grid.n * grid.dy)
    s[ok] = grid.n * dky * values * np.exp(1j * ky[ok] * (grid.y[0] - y_w))
    return Beam(grid, s, x_w, +1)


def paraxial_source_beam(grid: Grid, x0: float, yc: float, w: float, u_c: float) -> Beam:
    """The P1-7 source profile on the line x = x0 (fdtd2d.preparar_haz) with continuum ky0 = K/sqrt2."""
    y = grid.y
    s = (y - yc) / SQ2
    u = u_c + (y - yc) / SQ2
    q = 1.0 + 1j * 2.0 * u / (K * w * w)
    field = q ** -0.5 * np.exp(-s ** 2 / (w * w * q)) * np.exp(1j * (K / SQ2) * (y - yc))
    spectrum = np.fft.fft(field)
    return Beam(grid, np.where(grid.propagating, spectrum, 0.0), x0, +1)


def port_mode(grid: Grid, yb: float, w: float) -> np.ndarray:
    """P1-7 port mode on a vertical line for a 45-degree beam: waist profile and continuum carrier."""
    return np.exp(-((grid.y - yb) / (w * SQ2)) ** 2) * np.exp(1j * (K / SQ2) * (grid.y - yb))


def modal_amplitude(field: np.ndarray, mode: np.ndarray, dy: float) -> complex:
    """Complex modal amplitude c with P = |c|^2 equal to the P1-7 overlap power."""
    return complex(np.sum(field * np.conj(mode)) * dy / (np.sum(np.abs(mode) ** 2) * dy))


def path_field(x_p: float, y: np.ndarray, q_point, direction, length: float, coefficient: complex,
               w: float, diffraction: bool) -> np.ndarray:
    """P1-7 path-model field on x = x_p (identical formula to mzi_fdtd.haz_ideal).

    diffraction=False is the preregistered P1-7 model M0 (constant width, no curvature);
    diffraction=True is model M1 with free paraxial 1-transverse-dimension diffraction.
    `length` is the path length from the waist to q_point.
    """
    dx, dy = x_p - q_point[0], y - q_point[1]
    s = dx * direction[1] - dy * direction[0]
    u = dx * direction[0] + dy * direction[1]
    if not diffraction:
        return coefficient * np.exp(1j * K * (length + u)) * np.exp(-(s / w) ** 2)
    q = 1.0 + 1j * 2.0 * (length + u) / (K * w * w)
    return coefficient * np.exp(1j * K * (length + u)) * q ** -0.5 * np.exp(-s ** 2 / (w * w * q))


@dataclass(frozen=True)
class MZIGeometry:
    """45-degree Mach-Zehnder with vertical elements: splitter plane x_s, mirrors at x_s + a_a and x_s - a_b."""
    x_s: float
    y_s1: float
    a_a: float
    a_b: float
    x_p1: float
    x_p2: float
    yb1: float
    yb2: float


def solve_mzi(beam_in: Beam, splitter: Splitter, g: MZIGeometry) -> dict:
    """Propagate one input beam through the MZI and return output beams and port amplitudes."""
    if abs(splitter.x_c - g.x_s) > 1e-12:
        raise ValueError("Splitter plane and geometry disagree")
    r1, t1 = splitter.split(beam_in)
    arm_a = mirror(t1, g.x_s + g.a_a)          # transmitted arm travels +x, returns -x
    arm_b = mirror(r1, g.x_s - g.a_b)          # reflected arm travels -x, returns +x
    ra, ta = splitter.split(arm_a)              # arm A at S2 from the right
    rb, tb = splitter.split(arm_b)              # arm B at S2 from the left
    out_plus, out_minus = ra + tb, ta + rb
    e1, e2 = out_plus.at(g.x_p1).field(), out_minus.at(g.x_p2).field()
    return {"out_plus": out_plus, "out_minus": out_minus, "field_p1": e1, "field_p2": e2,
            "flux_in": beam_in.flux(), "flux_out": out_plus.flux() + out_minus.flux()}


def port_amplitudes(result: dict, grid: Grid, g: MZIGeometry, w: float) -> tuple[complex, complex]:
    return (modal_amplitude(result["field_p1"], port_mode(grid, g.yb1, w), grid.dy),
            modal_amplitude(result["field_p2"], port_mode(grid, g.yb2, w), grid.dy))


def mzi_model(g: MZIGeometry, r: complex, t: complex, grid: Grid, w: float, diffraction: bool) -> tuple[complex, complex]:
    """P1-7 path model with waist at (x_s, y_s1), mirrors -1, and the splitter's center coefficients."""
    la, lb = 2 * SQ2 * g.a_a, 2 * SQ2 * g.a_b
    qa, qb = (g.x_s, g.y_s1 + 2 * g.a_a), (g.x_s, g.y_s1 + 2 * g.a_b)
    d1, d2 = (1 / SQ2, 1 / SQ2), (-1 / SQ2, 1 / SQ2)
    y, mir = grid.y, -1.0
    e1 = (path_field(g.x_p1, y, qa, d1, la, mir * t * r, w, diffraction)
          + path_field(g.x_p1, y, qb, d1, lb, mir * r * t, w, diffraction))
    e2 = (path_field(g.x_p2, y, qa, d2, la, mir * t * t, w, diffraction)
          + path_field(g.x_p2, y, qb, d2, lb, mir * r * r, w, diffraction))
    return (modal_amplitude(e1, port_mode(grid, g.yb1, w), grid.dy),
            modal_amplitude(e2, port_mode(grid, g.yb2, w), grid.dy))


def cascade_model(stages: list[MZIGeometry], r: complex, t: complex, grid: Grid, w: float,
                  diffraction: bool) -> tuple[complex, complex]:
    """Path model for MZIs cascaded through their +x (P1) outputs; returns the last stage's ports.

    Every path's central ray is unfolded through the 45-degree planes: each arm of half-width
    a adds 2a in y and 2 sqrt2 a in length; the inter-stage segment from x_s(i) to x_s(i+1)
    adds its x distance in y and sqrt2 times it in length.
    """
    paths = [(stages[0].y_s1, 0.0, 1.0 + 0j)]
    mir = -1.0
    for index, g in enumerate(stages):
        if index:
            gap = g.x_s - stages[index - 1].x_s
            paths = [(y + gap, length + SQ2 * gap, c) for y, length, c in paths]
        last = index == len(stages) - 1
        new = []
        for y, length, c in paths:
            new.append((y + 2 * g.a_a, length + 2 * SQ2 * g.a_a, c * t * mir, "A"))
            new.append((y + 2 * g.a_b, length + 2 * SQ2 * g.a_b, c * r * mir, "B"))
        if not last:
            paths = [(y, length, c * (r if arm == "A" else t)) for y, length, c, arm in new]
        else:
            final = new
    gl = stages[-1]
    d1, d2 = (1 / SQ2, 1 / SQ2), (-1 / SQ2, 1 / SQ2)
    e1 = sum(path_field(gl.x_p1, grid.y, (gl.x_s, y), d1, length, c * (r if arm == "A" else t), w, diffraction)
             for y, length, c, arm in final)
    e2 = sum(path_field(gl.x_p2, grid.y, (gl.x_s, y), d2, length, c * (t if arm == "A" else r), w, diffraction)
             for y, length, c, arm in final)
    return (modal_amplitude(e1, port_mode(grid, gl.yb1, w), grid.dy),
            modal_amplitude(e2, port_mode(grid, gl.yb2, w), grid.dy))


def solve_cascade(beam_in: Beam, stages: list[MZIGeometry], splitter_factory) -> dict:
    """Feed the +x output of each MZI into the next one; return the last stage's solve.

    `discarded_flux` is the flux of the -x outputs of earlier stages, which leave the cascade,
    so flux_in = flux_out(last stage) + discarded_flux for a lossless cascade.
    """
    beam, result, discarded = beam_in, None, 0.0
    for index, g in enumerate(stages):
        result = solve_mzi(beam, splitter_factory(g.x_s), g)
        if index < len(stages) - 1:
            discarded += result["out_minus"].flux()
        beam = result["out_plus"]
    result["discarded_flux"] = discarded
    result["flux_in"] = beam_in.flux()
    return result


def circular_difference(a: complex, b: complex, dark_floor: float) -> float | None:
    """Wrapped phase of a relative to b; None when either amplitude is below the dark floor."""
    if abs(a) <= dark_floor or abs(b) <= dark_floor:
        return None
    return float(np.angle(a * np.conj(b)))
