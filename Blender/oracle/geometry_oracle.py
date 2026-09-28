"""Independent geometric reference for Neuro3D MZ phases (OPT-009, Claude).

Closed-form geometry, not a ray tracer: it does not duplicate the scene engine.
It answers three questions with standard optics:
  1. Wavefront phase reference at a combiner: how to compare two arms whose
     rays hit the splitter surface at different points.
  2. Which scene edits change the relative path length while the output rays
     still coincide (square vs non-rectangular MZ, delay line).
  3. Power ledger with separate categories: ports, absorption, mirror loss,
     escaped and unresolved (partial overlap).

Units: BU, rad, simulated power (Ps). Scalar plane-wave optics; no diffraction.
Splitter convention as in mz_oracle.py.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

Vec = tuple[float, float, float]


def _dot(a: Vec, b: Vec) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _sub(a: Vec, b: Vec) -> Vec:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _unit(a: Vec) -> Vec:
    n = math.sqrt(_dot(a, a))
    return (a[0] / n, a[1] / n, a[2] / n)


# ------------------------------------------------------------- 1. wavefront
def wavefront_length(length_to_hit: float, hit: Vec, arrival_dir: Vec, ref: Vec) -> float:
    """Optical length of an arm referred to point `ref` on the combiner surface.

    A plane wave travelling along the unit vector v has phase k*(L + v.(ref - hit))
    at `ref`. Reflection at the surface keeps the tangential phase (phase
    matching), so both arms can be compared at any common point of the surface:
        L_ref = L_hit + v . (ref - hit)
    """

    return length_to_hit + _dot(_unit(arrival_dir), _sub(ref, hit))


def wavefront_delta(arm1: tuple[float, Vec, Vec], arm2: tuple[float, Vec, Vec], ref: Vec) -> float:
    """L2 - L1 on the common wavefront. arm = (length_to_hit, hit, arrival_dir).

    If the combiner normal is parallel to v2 - v1 (which is true for a correctly
    oriented MZ splitter) and both hits and `ref` lie on the surface, the result
    does not depend on `ref`. This is itself a testable property.
    """

    return wavefront_length(*arm2, ref) - wavefront_length(*arm1, ref)


# ------------------------------------------------------------- 2. geometry cases
def square_single_mirror(d: float, incidence_deg: float = 45.0) -> dict:
    """Move ONE mirror of a square MZ by d along its normal (away from the beam).

    Standard result: delta_L = 2 d cos(theta) on the common wavefront, and the
    ray is displaced laterally by 2 d sin(theta). On a 45 deg combiner, the
    two hit points are separated by that lateral shift times sqrt(2)/... see
    `combiner_hit_separation`.
    """

    th = math.radians(incidence_deg)
    return {"delta_L_wavefront": 2 * d * math.cos(th), "lateral_shift": 2 * d * math.sin(th)}


def combiner_hit_separation(lateral_shift: float, combiner_incidence_deg: float = 45.0) -> float:
    """Distance between the two hit points on a tilted combiner for a given lateral ray shift."""

    return lateral_shift / math.cos(math.radians(combiner_incidence_deg))


def naive_hit_delta(d: float) -> float:
    """What a model gets if it compares lengths at the two hit points (square MZ, 45 deg).

    The extra arm length up to its own hit point is 2*sqrt(2)*d = 2 * wavefront.
    This is the value that OPT-008 found in mz_scene.py. Only a diagnostic: it
    must NOT be the expected value.
    """

    return 2 * math.sqrt(2) * d


def manhattan_equal_arms(x: float, y: float) -> tuple[float, float]:
    """Square MZ (arms leave at 0/90 deg, return at 90/0 deg), shared hit P=(x, y) from BS1.

    Both arms measure x + y: with exact overlap, geometry cannot create a phase.
    """

    return x + y, x + y


@dataclass(frozen=True)
class NonRectMZ:
    """Planar MZ: BS1 at the origin, input along +x, BS normals parallel to (1,-1,0).

    Arm 1 leaves along u1 = +x and arm 2 along u2 = +y. After one mirror each,
    they return along v1 = (cos b, sin b) and v2 = (sin b, cos b), which meet at
    the combiner point P = (X, Y). beta = 90 deg is the square MZ.
    """

    beta_deg: float
    X: float
    Y: float

    def _solve(self, u, v):
        det = u[0] * v[1] - u[1] * v[0]
        a = (self.X * v[1] - self.Y * v[0]) / det
        b = (u[0] * self.Y - u[1] * self.X) / det
        return a, b

    def scene(self) -> dict:
        b = math.radians(self.beta_deg)
        u1, u2 = (1.0, 0.0), (0.0, 1.0)
        v1, v2 = (math.cos(b), math.sin(b)), (math.sin(b), math.cos(b))
        a1, b1 = self._solve(u1, v1)
        a2, b2 = self._solve(u2, v2)
        if min(a1, b1, a2, b2) <= 0:
            raise ValueError("P is not reachable with positive segment lengths for this beta")
        m1 = (a1 * u1[0], a1 * u1[1], 0.0)
        m2 = (a2 * u2[0], a2 * u2[1], 0.0)
        n1 = _unit((u1[0] - v1[0], u1[1] - v1[1], 0.0))  # mirror normal: bisector of u and -v
        n2 = _unit((u2[0] - v2[0], u2[1] - v2[1], 0.0))
        return {
            "bs1": {"position": (0.0, 0.0, 0.0), "normal": _unit((1.0, -1.0, 0.0))},
            "mirror1": {"position": m1, "normal": n1},
            "mirror2": {"position": m2, "normal": n2},
            "bs2": {"position": (self.X, self.Y, 0.0), "normal": _unit((1.0, -1.0, 0.0))},
            "port_a_direction": (v1[0], v1[1], 0.0),  # arm1 transmitted + arm2 reflected
            "port_b_direction": (v2[0], v2[1], 0.0),
            "L1_from_bs1": a1 + b1,
            "L2_from_bs1": a2 + b2,
        }

    def delta_L(self) -> float:
        """L1 - L2 = (X - Y)(1 - tan(beta/2))."""

        return (self.X - self.Y) * (1 - math.tan(math.radians(self.beta_deg) / 2))


def delay_line(d: float) -> dict:
    """Rigid pair of mirrors at 90 deg (roof/retro) moved by d along the beam axis.

    The output ray is unchanged (no lateral shift), so the overlap is preserved;
    delta_L = 2 d. Costs two extra objects.
    """

    return {"delta_L": 2 * d, "lateral_shift": 0.0}


# ------------------------------------------------------------- 3. ledger
@dataclass(frozen=True)
class Arm:
    """Power bookkeeping of one arm between BS1 and BS2.

    transmission: exp(-alpha*L) (absorption along the path).
    mirror_reflectance: power reflectance of the arm mirror.
    escaped: True if the arm geometrically misses an aperture (broken path).
    Absorption and mirror loss are applied before the miss is detected, in
    that order.
    """

    transmission: float = 1.0
    mirror_reflectance: float = 1.0
    escaped: bool = False


def mz_ledger(p_in: float, tau1: float, tau2: float, arm1: Arm, arm2: Arm,
              delta_phi: float, gamma: float = 1.0, overlap: float = 1.0) -> dict:
    """Separate categories: port_a, port_b, absorbed, mirror_loss, escaped.

    The effective coherence is gamma * overlap. Partial overlap is the mixture
    coherent*g + incoherent*(1 - g), which conserves power exactly, so nothing
    is left 'unresolved'. Use a model that reports 'unresolved' only if it
    refuses to combine; then its port powers are zero and unresolved = sum of
    arm powers at BS2.
    Port convention: equal phases send all power to port B (see mz_oracle.py).
    """

    out = {"absorbed": 0.0, "mirror_loss": 0.0, "escaped": 0.0}
    powers = []
    for arm, frac in ((arm1, tau1), (arm2, 1 - tau1)):
        p = p_in * frac
        absorbed = p * (1 - arm.transmission)
        p -= absorbed
        mloss = p * (1 - arm.mirror_reflectance)
        p -= mloss
        out["absorbed"] += absorbed
        out["mirror_loss"] += mloss
        if arm.escaped:
            out["escaped"] += p
            p = 0.0
        powers.append(p)
    p1, p2 = powers
    g = gamma * overlap
    a, b = tau2 * p1, (1 - tau2) * p2          # port A contributions
    c, d = (1 - tau2) * p1, tau2 * p2          # port B contributions
    cos = math.cos(delta_phi)
    out["port_a"] = a + b - 2 * g * math.sqrt(a * b) * cos
    out["port_b"] = c + d + 2 * g * math.sqrt(c * d) * cos
    out["residual"] = p_in - sum(out[k] for k in ("port_a", "port_b", "absorbed", "mirror_loss", "escaped"))
    return out


# ------------------------------------------------------------- falsifiable case
def falsifiable_square_case(speed: float = 10.0, frequency: float = 500.0) -> dict:
    """Square MZ as in mz_scene.default_scene, move mirror2 so that the WAVEFRONT delta is lambda/2.

    Expected (standard optics): destructive, i.e. all power at port A.
    A model that compares lengths at the hit points gets delta = lambda and
    predicts port B instead. Separation of the hits on BS2 is reported so the
    case stays inside a 0.02 BU overlap tolerance.
    """

    lam = speed / frequency
    d = lam / (4 * math.cos(math.radians(45)))
    sq = square_single_mirror(d)
    return {
        "wavelength": lam,
        "mirror2_shift_along_minus_normal": d,
        "expected_delta_L_wavefront": sq["delta_L_wavefront"],
        "expected_delta_phi": 2 * math.pi * sq["delta_L_wavefront"] / lam,
        "naive_hit_delta_L": naive_hit_delta(d),
        "combiner_hit_separation": combiner_hit_separation(sq["lateral_shift"]),
        "expected_port_a": 1.0,
        "expected_port_b": 0.0,
    }
