"""Opt-in bounded next-plane parameter CPU graph; no producer/I/O/GPU."""
from fractions import Fraction as F

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


def sub(a, b):
    return tuple(x-y for x, y in zip(a, b))


def cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def dot(a, b):
    return (a[0]*b[0]+a[1]*b[1])+a[2]*b[2]


def raw_vector(words):
    require(type(words) is tuple and len(words) == 3, "STOP_RAW_VECTOR_SHAPE")
    require(all(type(w) is int and 0 <= w < 2**32 for w in words), "STOP_RAW_WORD_TYPE_RANGE")
    return tuple(Interval(scalar32(w)) for w in words)


def box_vector(bounds):
    require(type(bounds) is tuple and len(bounds) == 3, "STOP_BOX_VECTOR_SHAPE")
    result = []
    for pair in bounds:
        require(type(pair) is tuple and len(pair) == 2 and all(type(x) is F for x in pair), "STOP_BOX_PAIR_TYPE")
        require(all(x.numerator.bit_length() <= 4096 and x.denominator.bit_length() <= 4096 for x in pair), "STOP_BOX_CAPACITY")
        v = Interval(*pair)
        require(all(round_out(x, False) == x == round_out(x, True) for x in pair), "STOP_BOX_NOT_BINARY64_ENDPOINT")
        result.append(v)
    return tuple(result)


def enclose_plane(point_bounds, direction_bounds, triangle_words):
    """Conditional plane-only query: never authorizes launch exclusion or a hit."""
    require(type(triangle_words) is tuple and len(triangle_words) == 3, "STOP_TRIANGLE_SHAPE")
    point, direction = box_vector(point_bounds), box_vector(direction_bounds)
    require(not all(x.lo <= 0 <= x.hi for x in direction), "STOP_DIRECTION_ZERO_POSSIBLE")
    a, b, c = [raw_vector(words) for words in triangle_words]
    normal = cross(sub(b, a), sub(c, a))
    squared = dot(normal, normal)
    out = dict(plane_only=True, triangle_hit_certified=False, nearest_hit_certified=False,
               exact_contact_allowed=False, launch_exclusion_allowed=False,
               ignored_primitive_ids=[], origin_offset_applied=False,
               upstream_binding_authenticated=False, native_precision_certified=False,
               full_path_visibility_certified=False, phase_certified=False,
               GPU_used=False, GPU_launch_allowed=False, phase_error_bound=None,
               parameter_units="unnormalized_reflected_direction_parameter_NOT_BU_length",
               full_costs="UNKNOWN_NOT_ZERO",
               assumptions=["correctly_rounded_binary64", "no_FMA_or_reassociation", "gradual_underflow"])
    out["normal_squared_interval"] = squared.json()
    if squared.lo <= 0:
        out.update(status="STOP_NORMAL_SQUARED_ZERO_POSSIBLE")
        return out
    numerator = dot(normal, sub(a, point))
    denominator = dot(normal, direction)
    out.update(numerator_interval=numerator.json(), denominator_interval=denominator.json())
    if denominator.lo <= 0 <= denominator.hi:
        out.update(status="STOP_PLANE_DENOMINATOR_ZERO_POSSIBLE")
        return out
    parameter = numerator/denominator
    if parameter.lo <= 0 <= parameter.hi:
        status = "STOP_LAUNCH_OR_CONTACT_ZERO_POSSIBLE"
    elif parameter.hi < 0:
        status = "CONDITIONAL_NEGATIVE_PLANE_PARAMETER_NOT_FORWARD"
    else:
        status = "CONDITIONAL_POSITIVE_PLANE_PARAMETER_CONTACT_UNCLASSIFIED"
    out.update(status=status, parameter_interval=parameter.json())
    return out
