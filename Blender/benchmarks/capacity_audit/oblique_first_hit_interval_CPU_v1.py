"""Opt-in CPU rational enclosures; no GPU, I/O, producer import or admission.

Intervals include exact real and operation-rounded first-hit graphs, conditional
on binary64 correctly rounded operations, no FMA/reassociation, gradual underflow.
These assumptions are NOT established for a device by this implementation.
"""
from fractions import Fraction as F
import hashlib
import struct


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def power2(exponent):
    return F(2**exponent) if exponent >= 0 else F(1, 2**(-exponent))


MAX64 = (2 - power2(-52)) * power2(1023)


def round_out(value, upper):
    """Directed finite binary64 value, derived with integers, not host floats."""
    require(type(value) is F and type(upper) is bool, "round_type")
    if value == 0:
        return F(0)
    require(abs(value) <= MAX64, "STOP_OVERFLOW")
    magnitude = abs(value)
    exponent = magnitude.numerator.bit_length() - magnitude.denominator.bit_length()
    if magnitude < power2(exponent):
        exponent -= 1
    step = power2(max(exponent - 52, -1074))
    scaled = value / step
    q, remainder = divmod(scaled.numerator, scaled.denominator)
    result = (q + int(upper and remainder != 0)) * step
    require(abs(result) <= MAX64, "STOP_OVERFLOW")
    return result


class Interval:
    """Closed rational endpoints; outward rounding at every scalar operation."""
    __slots__ = ("lo", "hi")

    def __init__(self, lo, hi=None):
        require(type(lo) is F and (hi is None or type(hi) is F), "interval_type")
        hi = lo if hi is None else hi
        require(lo <= hi and max(abs(lo), abs(hi)) <= MAX64, "interval_domain")
        self.lo, self.hi = lo, hi

    @classmethod
    def outward(cls, lo, hi):
        return cls(round_out(lo, False), round_out(hi, True))

    def __add__(self, other):
        return self.outward(self.lo + other.lo, self.hi + other.hi)

    def __sub__(self, other):
        return self.outward(self.lo - other.hi, self.hi - other.lo)

    def __mul__(self, other):
        products = [a*b for a in (self.lo, self.hi) for b in (other.lo, other.hi)]
        return self.outward(min(products), max(products))

    def __truediv__(self, other):
        require(not other.lo <= 0 <= other.hi, "STOP_DENOMINATOR_CONTAINS_ZERO")
        quotients = [a/b for a in (self.lo, self.hi) for b in (other.lo, other.hi)]
        return self.outward(min(quotients), max(quotients))

    def json(self):
        return [[self.lo.numerator, self.lo.denominator], [self.hi.numerator, self.hi.denominator]]


def scalar32(word):
    exponent, mantissa = (word >> 23) & 255, word & 0x7fffff
    require(exponent != 255 and not (exponent == 0 and mantissa) and word != 0x80000000,
            "STOP_ORIGINAL_WORD_DOMAIN")
    result = F(0) if exponent == 0 else (2**23 + mantissa) * power2(exponent - 150)
    result = -result if word >> 31 else result
    require(abs(result) <= 1000000, "STOP_ORIGINAL_SCALAR_DOMAIN")
    return result


def decode(raw):
    require(type(raw) is bytes and 40 <= len(raw) <= 2668 and len(raw) % 4 == 0, "STOP_INPUT_EXTENT")
    w = struct.unpack("<%dI" % (len(raw)//4), raw)
    require(w[:4] == (0x4744334e, 0x31563233, 1, 2) and w[9] == 0, "STOP_INPUT_HEADER")
    n = w[4]
    require(1 <= n <= 64 and w[5] == 17+9*n and w[6] == n and len(w) == 27+10*n, "STOP_INPUT_COUNTS")
    ids = w[10:10+n]
    require(len(set(ids)) == n and all(i < 2**31 for i in ids), "STOP_INPUT_IDS")
    require(w[7] != w[8] and w[7] in ids and w[8] in ids, "STOP_INPUT_QUERY_IDS")
    values = tuple(scalar32(x) for x in w[10+n:])
    require(values[15+9*n] > 0, "STOP_INPUT_LAMBDA")
    sources = [(values[6*i:6*i+3], values[6*i+3:6*i+6]) for i in (0, 1)]
    require(all(any(direction) for _, direction in sources), "STOP_INPUT_DIRECTION")
    triangles = [(ids[i], [values[12+9*i+j:15+9*i+j] for j in (0, 3, 6)]) for i in range(n)]
    return sources, triangles


def sub(a, b):
    return tuple(x-y for x, y in zip(a, b))


def cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def dot(a, b):
    return (a[0]*b[0]+a[1]*b[1])+a[2]*b[2]


def triangle_enclosure(origin, direction, vertices):
    origin, direction = [tuple(Interval(x) for x in v) for v in (origin, direction)]
    a, b, c = [tuple(Interval(x) for x in v) for v in vertices]
    e1, e2 = sub(b, a), sub(c, a)
    p = cross(direction, e2)
    determinant = dot(e1, p)
    if determinant.lo <= 0 <= determinant.hi:
        return dict(classification="STOP_DETERMINANT_ZERO_POSSIBLE", determinant=determinant.json())
    s = sub(origin, a)
    q = cross(s, e1)
    u, v, t = dot(s, p)/determinant, dot(direction, q)/determinant, dot(e2, q)/determinant
    uv = u+v
    classification = "STOP_BOUNDARY_OR_CONTACT_POSSIBLE"
    if u.hi < 0 or v.hi < 0 or uv.lo > 1 or t.hi < 0:
        classification = "CONDITIONAL_MISS"
    elif u.lo > 0 and v.lo > 0 and uv.hi < 1 and t.lo > 0:
        classification = "CONDITIONAL_INTERIOR_HIT"
    return dict(classification=classification, determinant=determinant.json(),
                t=t.json(), u=u.json(), v=v.json(), uv=uv.json())


def evaluate(raw):
    """Original INPUT -> CPU interval report. Not a native certificate/dispatcher."""
    sources, triangles = decode(raw)
    outputs = []
    for sid, (origin, direction) in enumerate(sources):
        rows = []
        for primitive, vertices in triangles:
            try:
                row = triangle_enclosure(origin, direction, vertices)
            except ValueError as error:
                row = dict(classification="STOP_ARITHMETIC", reason=str(error))
            rows.append(dict(primitive_id=primitive, **row))
        hits = [r for r in rows if r["classification"] == "CONDITIONAL_INTERIOR_HIT"]
        resolved = all(r["classification"] in ("CONDITIONAL_INTERIOR_HIT", "CONDITIONAL_MISS") for r in rows)
        winners = [r for r in hits if all(r is s or F(*r["t"][1]) < F(*s["t"][0]) for s in hits)] if resolved else []
        selection = "STOP_UNRESOLVED_COVERAGE_OR_ORDER"
        if resolved and not hits:
            selection = "CONDITIONAL_NO_HIT"
        elif len(winners) == 1:
            selection = "CONDITIONAL_UNIQUE_FIRST_HIT"
        outputs.append(dict(source_id="S"+str(sid), rows=rows, triangle_tests=len(rows), selection=selection,
                            chosen_primitive_id=winners[0]["primitive_id"] if len(winners) == 1 else None))
    return dict(input_sha256=hashlib.sha256(raw).hexdigest(), input_bytes=len(raw), sources=outputs,
                scope="CPU_RATIONAL_ENCLOSURE_CONDITIONAL_ON_UNVERIFIED_BINARY64_GRAPH",
                assumptions=["correctly_rounded_binary64", "no_FMA_or_reassociation", "gradual_underflow"],
                parameter_t_units="original_unnormalized_direction_parameter_NOT_BU_length",
                barycentric_units="dimensionless", GPU_used=False, GPU_launch_allowed=False,
                native_precision_certified=False, scene_authenticated=False, exact_contact_allowed=False,
                complete_trace_output=False, phase_certified=False, phase_error_bound=None,
                full_costs="UNKNOWN_NOT_ZERO")
