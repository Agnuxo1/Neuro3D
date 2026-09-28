"""Independent analytic oracle for Neuro3D two-path tests (OPT-006, Claude).

Closed-form expectations for a Mach-Zehnder (MZ) circuit, written separately
from the scene engine so both can be compared. Pure standard library, CPU only.

Units: lengths in Blender units (BU), frequency in cycles per simulated second,
speed in BU per simulated second, phase in radians, power in simulated power
units (Ps). This is scalar ray optics: no polarisation or diffraction, and no
claim about physical photons.

Beam-splitter convention (lossless, symmetric):
    U(tau) = [[sqrt(tau),          i*sqrt(1 - tau)],
              [i*sqrt(1 - tau),    sqrt(tau)      ]]
tau is the power transmission. Light enters BS1 on input port 0. Arm 1 is the
transmitted beam and arm 2 the reflected one (phase factor i). BS2 recombines:
arm 1 enters BS2 port 0 and arm 2 enters port 1. Output port A = row 0 and
output port B = row 1. With equal arms and a 50/50 split, all power leaves
port B (constructive) and port A is dark.
"""

from __future__ import annotations

from dataclasses import dataclass
import cmath
import math

TWO_PI = 2.0 * math.pi


# ---------------------------------------------------------------- baseline
def single_path_baseline(
    intensity: float = 1.0,
    color: tuple[float, float, float] = (1.0, 0.5, 0.2),
    reflectance: tuple[float, float, float] = (0.8, 0.9, 1.0),
    responsivity: tuple[float, float, float] = (1.0, 1.0, 1.0),
    path_length: float = 3.8,
    absorption: float = 0.05,
    threshold: float = 0.25,
    gain: float = 1.0,
    frequency: float = 1.0,
    speed: float = 10.0,
    phase0: float = 0.0,
    phase_shift: float = 0.25,
) -> dict:
    """Reproduce EXP-000 (three-object circuit) from its equations only."""

    total = sum(color)
    transmission = math.exp(-absorption * path_length)
    power = sum(intensity * c / total * r * s * transmission
                for c, r, s in zip(color, reflectance, responsivity))
    activation = 1.0 - math.exp(-gain * max(0.0, power - threshold))
    phase = math.remainder(phase0 + phase_shift + TWO_PI * frequency * path_length / speed, TWO_PI)
    return {"power": power, "activation": activation, "phase": phase}


# ---------------------------------------------------------------- phases
def path_phase(path_length: float, frequency: float, speed: float, extra: float = 0.0) -> float:
    """Propagation phase 2*pi*f*L/v plus explicit shifts (rad), not wrapped."""

    return TWO_PI * frequency * path_length / speed + extra


def cross_term_average(delta_phi: float, delta_f: float, t_int: float) -> float:
    """Time average of cos(2*pi*delta_f*t + delta_phi) over [0, t_int].

    Returns the factor that multiplies 2*sqrt(P1*P2) in the detected power.
    Equal frequencies give cos(delta_phi). |delta_f|*t_int >> 1 tends to 0,
    which is the incoherent limit. Values in between are beating and must be
    flagged, never silently treated as coherent.
    """

    if t_int <= 0:
        raise ValueError("t_int must be positive")
    x = math.pi * delta_f * t_int
    if abs(x) < 1e-12:
        return math.cos(delta_phi)
    return math.sin(x) / x * math.cos(delta_phi + x)


# ---------------------------------------------------------------- MZ closed form
@dataclass(frozen=True)
class MZResult:
    port_a: float
    port_b: float
    loss_arm1: float
    loss_arm2: float
    residual: float  # p_in - (outputs + losses); 0 for exact bookkeeping
    visibility: float


def mz_closed_form(
    p_in: float = 1.0,
    tau1: float = 0.5,
    tau2: float = 0.5,
    t_arm1: float = 1.0,
    t_arm2: float = 1.0,
    phi1: float = 0.0,
    phi2: float = 0.0,
    gamma: float = 1.0,
) -> MZResult:
    """Output powers of a MZ from closed-form algebra.

    t_arm1 and t_arm2 are power transmissions of each arm (mirror reflectance x
    absorption exp(-alpha*L)); 0 means a broken arm. gamma in [0, 1] is the
    mutual coherence of the two arms.
        A = tau1*tau2*T1          B = (1-tau1)(1-tau2)*T2
        C = tau1*(1-tau2)*T1      D = (1-tau1)*tau2*T2
        P_A = A + B - 2*gamma*sqrt(A*B)*cos(phi1 - phi2)
        P_B = C + D + 2*gamma*sqrt(C*D)*cos(phi1 - phi2)
    Because A*B = C*D, the cross terms cancel in P_A + P_B, so conservation
    holds for every gamma and phase.
    """

    for name, v in (("tau1", tau1), ("tau2", tau2), ("t_arm1", t_arm1), ("t_arm2", t_arm2), ("gamma", gamma)):
        if not (0.0 <= v <= 1.0) or not math.isfinite(v):
            raise ValueError(f"{name} must lie in [0, 1]")
    if p_in < 0 or not math.isfinite(p_in):
        raise ValueError("p_in must be finite and nonnegative")
    dphi = phi1 - phi2
    a, b = tau1 * tau2 * t_arm1, (1 - tau1) * (1 - tau2) * t_arm2
    c, d = tau1 * (1 - tau2) * t_arm1, (1 - tau1) * tau2 * t_arm2
    port_a = p_in * (a + b - 2 * gamma * math.sqrt(a * b) * math.cos(dphi))
    port_b = p_in * (c + d + 2 * gamma * math.sqrt(c * d) * math.cos(dphi))
    loss1 = p_in * tau1 * (1 - t_arm1)
    loss2 = p_in * (1 - tau1) * (1 - t_arm2)
    residual = p_in - (port_a + port_b + loss1 + loss2)
    vis = 2 * gamma * math.sqrt(c * d) / (c + d) if c + d > 0 else 0.0
    return MZResult(port_a, port_b, loss1, loss2, residual, vis)


# ---------------------------------------------------------------- MZ by matrices
def _bs(tau: float) -> tuple[tuple[complex, complex], tuple[complex, complex]]:
    t, r = math.sqrt(tau), 1j * math.sqrt(1 - tau)
    return ((t, r), (r, t))


def _apply(m, v):
    return (m[0][0] * v[0] + m[0][1] * v[1], m[1][0] * v[0] + m[1][1] * v[1])


def mz_matrix(
    p_in: float = 1.0, tau1: float = 0.5, tau2: float = 0.5,
    t_arm1: float = 1.0, t_arm2: float = 1.0,
    phi1: float = 0.0, phi2: float = 0.0, gamma: float = 1.0,
) -> tuple[float, float]:
    """Second, independent derivation: complex field through 2x2 matrices.

    Coherent part: propagate the field vector. Incoherent part: propagate each
    arm alone and add powers. Partial coherence is the mixture
    gamma*coherent + (1-gamma)*incoherent, valid for a real mutual coherence.
    """

    e = _apply(_bs(tau1), (math.sqrt(p_in), 0.0))
    arm = (e[0] * math.sqrt(t_arm1) * cmath.exp(1j * phi1),
           e[1] * math.sqrt(t_arm2) * cmath.exp(1j * phi2))
    coh = _apply(_bs(tau2), arm)
    only1 = _apply(_bs(tau2), (arm[0], 0.0))
    only2 = _apply(_bs(tau2), (0.0, arm[1]))
    inc = [abs(only1[k]) ** 2 + abs(only2[k]) ** 2 for k in range(2)]
    return tuple(gamma * abs(coh[k]) ** 2 + (1 - gamma) * inc[k] for k in range(2))  # type: ignore[return-value]


# ---------------------------------------------------------------- geometry
def mirror_translation(d: float, incidence_deg: float) -> dict:
    """Translate a plane mirror by d along its normal (away from the beam).

    Extra path length: 2*d*cos(theta). Lateral shift of the reflected ray:
    2*d*sin(theta). Hence shift = delta_L * tan(theta).
    """

    th = math.radians(incidence_deg)
    return {"delta_L": 2 * d * math.cos(th), "lateral_shift": 2 * d * math.sin(th)}


def gaussian_overlap(shift: float, waist: float) -> float:
    """Normalised field overlap of two equal Gaussian beams offset by `shift`.

    The field is proportional to exp(-r^2/w^2) (w = 1/e^2 intensity radius).
    The overlap is exp(-s^2/(2 w^2)), and it multiplies the interference term
    as an effective gamma.
    """

    if waist <= 0:
        raise ValueError("waist must be positive")
    return math.exp(-shift * shift / (2 * waist * waist))


def destructive_by_single_mirror(wavelength: float, incidence_deg: float = 45.0, waist: float | None = None) -> dict:
    """Design check: move ONE mirror to add lambda/2 of path length.

    Reports the mirror displacement, the lateral ray shift it causes and, if a
    waist is given, the overlap left for interference.
    """

    th = math.radians(incidence_deg)
    d = wavelength / (4 * math.cos(th))
    geo = mirror_translation(d, incidence_deg)
    out = {"wavelength": wavelength, "mirror_shift": d, **geo}
    if waist is not None:
        out["overlap_gamma"] = gaussian_overlap(geo["lateral_shift"], waist)
    return out


def delay_line_shift(delta_l: float) -> dict:
    """Rigid retro pair (two mirrors at 90 deg) moved by d: delta_L = 2d, no lateral shift."""

    return {"stage_shift": delta_l / 2.0, "lateral_shift": 0.0}
