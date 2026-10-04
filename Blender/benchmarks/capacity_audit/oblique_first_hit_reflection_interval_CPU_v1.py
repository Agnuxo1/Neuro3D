"""New point/reflection interval graph; no producers, file writes or GPU.
Pure arithmetic copied as nine AST subtrees from sealed own first-hit library.
No first-hit evaluator/intersection is imported or executed.
"""
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


def enclose(origin_words, direction_words, triangle_words, t_bounds):
    """New analytical point/reflection graph, not authenticated scene admission."""
    require(type(triangle_words) is tuple and len(triangle_words) == 3, "STOP_TRIANGLE_SHAPE")
    require(type(t_bounds) is tuple and len(t_bounds) == 2 and all(type(x) is F for x in t_bounds), "STOP_T_SHAPE_TYPE")
    require(all(x.numerator.bit_length() <= 4096 and x.denominator.bit_length() <= 4096 for x in t_bounds), "STOP_T_CAPACITY")
    require(0 < t_bounds[0] <= t_bounds[1], "STOP_T_CONTACT_OR_ORDER")
    t = Interval(*t_bounds)
    origin, direction = raw_vector(origin_words), raw_vector(direction_words)
    require(any(x.lo != 0 for x in direction), "STOP_ZERO_DIRECTION")
    a, b, c = [raw_vector(words) for words in triangle_words]
    normal = cross(sub(b, a), sub(c, a))
    norm_squared = dot(normal, normal)
    if norm_squared.lo <= 0:
        return dict(status="STOP_NORMAL_SQUARED_ZERO_POSSIBLE", native_precision_certified=False,
                    GPU_launch_allowed=False, phase_error_bound=None)
    factor = (Interval(F(2))*dot(direction, normal))/norm_squared
    reflected = tuple(d-factor*n for d, n in zip(direction, normal))
    point = tuple(o+t*d for o, d in zip(origin, direction))
    residual = dot(sub(point, a), normal)
    return dict(status="CONDITIONAL_POINT_REFLECTION_ENCLOSURE",
                point_interval=[x.json() for x in point], point_units="declared_scene_BU_NOT_meters",
                normal_interval=[x.json() for x in normal], normal_squared_interval=norm_squared.json(),
                reflection_factor_interval=factor.json(), reflected_direction_interval=[x.json() for x in reflected],
                direction_units="original_unnormalized_direction_units", normalized=False,
                plane_residual_interval=residual.json(),
                contact_status="STOP_PLANE_CONTACT_ZERO_POSSIBLE" if residual.lo <= 0 <= residual.hi else "STOP_UPSTREAM_SURFACE_INCONSISTENT",
                t_interval=t.json(), upstream_t_authenticated=False, source_binding_authenticated=False,
                assumptions=["correctly_rounded_binary64", "no_FMA_or_reassociation", "gradual_underflow"],
                ignored_primitive_ids=[], origin_offset_applied=False, exact_contact_allowed=False,
                full_path_visibility_certified=False, complete_trace_output=False, native_precision_certified=False,
                GPU_used=False, GPU_launch_allowed=False, phase_certified=False, phase_error_bound=None,
                full_costs="UNKNOWN_NOT_ZERO")
