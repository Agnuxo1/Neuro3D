"""Exact represented-input geometry and rational optical interval references.

This module proves inclusion for its explicit scalar input model. It does not
certify missing paths, native Blender transforms, fabrication, or Maxwell error.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from math import factorial, isfinite, isqrt
from typing import Iterable, Sequence


def rational(value: int | float | str | Fraction) -> Fraction:
    """Decode a rational or an exact finite binary64 value without decimal loss."""
    if isinstance(value, bool):
        raise TypeError("Boolean coordinates are not accepted")
    if isinstance(value, Fraction):
        return value
    if isinstance(value, float):
        if not isfinite(value):
            raise ValueError("All values must be finite")
        return Fraction.from_float(value)
    if isinstance(value, str) and value.lower().lstrip("+-").startswith("0x"):
        return rational(float.fromhex(value))
    return Fraction(value)


@dataclass(frozen=True)
class Interval:
    """Closed interval with exact rational endpoints and inclusion arithmetic."""
    lo: Fraction
    hi: Fraction

    def __post_init__(self) -> None:
        object.__setattr__(self, "lo", rational(self.lo))
        object.__setattr__(self, "hi", rational(self.hi))
        if self.lo > self.hi:
            raise ValueError("Interval endpoints are reversed")

    @staticmethod
    def point(value: int | float | str | Fraction) -> Interval:
        v = rational(value)
        return Interval(v, v)

    def __add__(self, other: Interval | Fraction | int) -> Interval:
        b = interval(other)
        return Interval(self.lo + b.lo, self.hi + b.hi)

    __radd__ = __add__

    def __neg__(self) -> Interval:
        return Interval(-self.hi, -self.lo)

    def __sub__(self, other: Interval | Fraction | int) -> Interval:
        return self + (-interval(other))

    def __rsub__(self, other: Interval | Fraction | int) -> Interval:
        return interval(other) - self

    def __mul__(self, other: Interval | Fraction | int) -> Interval:
        b = interval(other)
        v = (self.lo*b.lo, self.lo*b.hi, self.hi*b.lo, self.hi*b.hi)
        return Interval(min(v), max(v))

    __rmul__ = __mul__

    def __truediv__(self, other: Interval | Fraction | int) -> Interval:
        b = interval(other)
        if b.lo <= 0 <= b.hi:
            raise ValueError("Division by an interval containing zero")
        return self * Interval(1/b.hi, 1/b.lo)

    def square(self) -> Interval:
        lo = Fraction(0) if self.lo <= 0 <= self.hi else min(self.lo**2, self.hi**2)
        return Interval(lo, max(self.lo**2, self.hi**2))

    def contains(self, value: int | float | str | Fraction) -> bool:
        return self.lo <= rational(value) <= self.hi

    def outward_wire(self, bits: int = 128) -> list[str]:
        """Serialize bounded-size dyadic endpoints, widening rather than truncating."""
        if not 8 <= bits <= 512:
            raise ValueError("8..512 serialization bits are required")
        scale = 1 << bits
        lower = (self.lo*scale).numerator//(self.lo*scale).denominator
        negative_upper = -self.hi*scale
        upper = -(negative_upper.numerator//negative_upper.denominator)
        return [str(Fraction(lower, scale)), str(Fraction(upper, scale))]

    @property
    def midpoint(self) -> Fraction:
        return (self.lo + self.hi)/2

    @property
    def radius(self) -> Fraction:
        return (self.hi - self.lo)/2


def interval(value: Interval | int | float | str | Fraction) -> Interval:
    """Promote an exact scalar to a singleton interval."""
    return value if isinstance(value, Interval) else Interval.point(value)


def sqrt_interval(value: Interval, bits: int = 128) -> Interval:
    """Enclose square roots with integer arithmetic on a binary rational grid."""
    if value.lo < 0 or not 8 <= bits <= 512:
        raise ValueError("Nonnegative radicand and 8..512 bits are required")
    scale = 1 << bits

    def bounds(x: Fraction) -> tuple[Fraction, Fraction]:
        k = isqrt((x.numerator * scale * scale)//x.denominator)
        lo = Fraction(k, scale)
        hi = lo if k*k*x.denominator == x.numerator*scale*scale else Fraction(k+1, scale)
        return lo, hi

    return Interval(bounds(value.lo)[0], bounds(value.hi)[1])


def segment_length(a: Sequence, b: Sequence, bits: int = 128) -> Interval:
    """Enclose a 3D segment length, including supplied coordinate intervals."""
    if len(a) != 3 or len(b) != 3:
        raise ValueError("Three coordinates per endpoint are required")
    squared = sum(((interval(x)-interval(y)).square() for x, y in zip(a, b)), Interval.point(0))
    return sqrt_interval(squared, bits)


def _atan_inverse(n: int, bits: int) -> Interval:
    """Use the alternating arctangent series and its exact next-term remainder."""
    x = Fraction(1, n)
    total, power, k = Fraction(0), x, 0
    threshold = Fraction(1, 1 << bits)
    while True:
        total += (-1 if k % 2 else 1)*power/(2*k+1)
        next_power = power*x*x
        next_term = (-1 if (k+1) % 2 else 1)*next_power/(2*k+3)
        if abs(next_term) <= threshold:
            return Interval(min(total, total+next_term), max(total, total+next_term))
        power, k = next_power, k+1


@lru_cache(maxsize=8)
def pi_interval(bits: int = 128) -> Interval:
    """Enclose pi by Machin's identity; no floating-point pi is assumed exact."""
    if not 8 <= bits <= 512:
        raise ValueError("8..512 bits are required")
    return 16*_atan_inverse(5, bits+8)-4*_atan_inverse(239, bits+8)


def phase_from_length(length: Interval, wavelength: Interval, bits: int = 128) -> Interval:
    """Reduce exact length/wavelength cycles before multiplying by enclosed pi."""
    if length.lo < 0 or wavelength.lo <= 0:
        raise ValueError("Nonnegative lengths and strictly positive wavelengths are required")
    cycles = length/wavelength
    turns = round(cycles.midpoint)
    return 2*pi_interval(bits)*(cycles-turns)


def _trig_at_rational(x: Fraction, terms: int) -> tuple[Interval, Interval]:
    """Enclose cosine and sine using real Taylor remainder bounds."""
    if not 8 <= terms <= 64 or abs(x) > 4:
        raise ValueError("Taylor reduction requires |x| <= 4 and 8..64 terms")
    cosine = sum(((-1)**k*x**(2*k)/factorial(2*k) for k in range(terms+1)), Fraction(0))
    sine = sum(((-1)**k*x**(2*k+1)/factorial(2*k+1) for k in range(terms+1)), Fraction(0))
    ec = abs(x)**(2*terms+1)/factorial(2*terms+1)
    es = abs(x)**(2*terms+2)/factorial(2*terms+2)
    return Interval(cosine-ec, cosine+ec), Interval(sine-es, sine+es)


def unit_phasor(phase: Interval, bits: int = 128, terms: int = 24) -> tuple[Interval, Interval]:
    """Enclose exp(i*phase), preserving pi uncertainty during range reduction."""
    period = 2*pi_interval(bits)
    turns = round(phase.midpoint/period.midpoint)
    reduced = phase-turns*period
    if reduced.radius >= 2 or abs(reduced.midpoint) > 4:
        return Interval(-1, 1), Interval(-1, 1)
    c, s = _trig_at_rational(reduced.midpoint, terms)
    e = reduced.radius  # Both sin and cos are globally 1-Lipschitz.
    return (Interval(max(Fraction(-1), c.lo-e), min(Fraction(1), c.hi+e)),
            Interval(max(Fraction(-1), s.lo-e), min(Fraction(1), s.hi+e)))


def complex_product(a: tuple[Interval, Interval], b: tuple[Interval, Interval]) -> tuple[Interval, Interval]:
    """Multiply rectangular complex enclosures without dropping cross terms."""
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def coherent_field(paths: Iterable[tuple[tuple[Interval, Interval], Interval]]) -> tuple[Interval, Interval]:
    """Sum every supplied complex amplitude times its enclosed phase factor."""
    real, imag = Interval.point(0), Interval.point(0)
    for amplitude, phase in paths:
        r, i = complex_product(amplitude, unit_phasor(phase))
        real, imag = real+r, imag+i
    return real, imag


def modal_power(field: tuple[Interval, Interval]) -> Interval:
    """Enclose normalized modal power; this quantity is not calibrated watts."""
    return field[0].square()+field[1].square()


def certified_argmax(powers: Sequence[Interval]) -> int | None:
    """Return a class only when its lower power exceeds every other upper power."""
    if len(powers) < 2 or any(p.lo < 0 for p in powers):
        raise ValueError("At least two nonnegative power intervals are required")
    for i, p in enumerate(powers):
        if all(p.lo > q.hi for j, q in enumerate(powers) if i != j):
            return i
    return None


def field_to_power_error(observed_abs_upper: Fraction, field_error: Fraction) -> Fraction:
    """Bound |P_true-P_observed| from a supplied upper bound on |E_observed|."""
    a, e = rational(observed_abs_upper), rational(field_error)
    if a < 0 or e < 0:
        raise ValueError("Error and magnitude bounds must be nonnegative")
    return 2*a*e+e*e


def _vector(v: Sequence) -> tuple[Fraction, Fraction, Fraction]:
    if len(v) != 3:
        raise ValueError("Three-dimensional vectors are required")
    return tuple(rational(x) for x in v)


def _sub(a, b):
    return tuple(x-y for x, y in zip(a, b))


def _dot(a, b):
    return sum((x*y for x, y in zip(a, b)), Fraction(0))


def _cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def exact_first_hit(origin: Sequence, direction: Sequence, triangles: Sequence[dict]) -> dict:
    """Find a first hit in exact represented coordinates; retain contacts and ties.

    Each triangle needs primitive_id, object_id, and vertices (three 3D vectors).
    Coplanar support and degenerate triangles deliberately return UNKNOWN.
    A shared triangle seam is merged only within one object and one exact plane.
    """
    o, d = _vector(origin), _vector(direction)
    if _dot(d, d) == 0:
        raise ValueError("A nonzero direction is required")
    hits, ids = [], set()
    for triangle in triangles:
        pid = str(triangle["primitive_id"])
        if pid in ids:
            raise ValueError("Primitive identifiers must be unique")
        ids.add(pid)
        vertices = triangle["vertices"]
        if len(vertices) != 3:
            raise ValueError("Three vertices per triangle are required")
        a, b, c = (_vector(x) for x in vertices)
        e1, e2 = _sub(b, a), _sub(c, a)
        normal = _cross(e1, e2)
        if _dot(normal, normal) == 0:
            return {"status": "UNKNOWN", "reason": "DEGENERATE_TRIANGLE", "primitive_id": pid}
        p = _cross(d, e2)
        determinant = _dot(e1, p)
        if determinant == 0:
            if _dot(normal, _sub(o, a)) == 0:
                return {"status": "UNKNOWN", "reason": "COPLANAR_QUERY", "primitive_id": pid}
            continue
        delta = _sub(o, a)
        u = _dot(delta, p)/determinant
        q = _cross(delta, e1)
        v = _dot(d, q)/determinant
        t = _dot(e2, q)/determinant
        if t >= 0 and u >= 0 and v >= 0 and u+v <= 1:
            hits.append((t, pid, str(triangle["object_id"]), a, normal))
    if not hits:
        return {"status": "MISS"}
    first_t = min(h[0] for h in hits)
    tied = [h for h in hits if h[0] == first_t]
    if first_t == 0:
        return {"status": "UNKNOWN", "reason": "LAUNCH_CONTACT", "primitive_ids": [h[1] for h in tied]}
    reference = tied[0]
    same_surface = all(h[2] == reference[2] and _cross(h[4], reference[4]) == (0, 0, 0)
                       and _dot(reference[4], _sub(h[3], reference[3])) == 0 for h in tied)
    if not same_surface:
        return {"status": "UNKNOWN", "reason": "DISTINCT_SURFACE_TIE", "primitive_ids": [h[1] for h in tied]}
    return {"status": "HIT", "parameter": first_t, "object_id": reference[2],
            "primitive_ids": sorted(h[1] for h in tied),
            "point": tuple(o[j]+first_t*d[j] for j in range(3))}
