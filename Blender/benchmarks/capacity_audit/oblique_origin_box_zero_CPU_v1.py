"""Sufficient ideal CPU affine-box zero-contact property; not a launch credential."""
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



def box_vector(value):
    require(type(value) is tuple and len(value) == 3, "STOP_BOX_VECTOR_SHAPE")
    for pair in value:
        require(type(pair) is tuple and len(pair) == 2 and all(type(x) is F for x in pair),
                "STOP_BOX_PAIR_TYPE")
        require(all(x.numerator.bit_length() <= 4096 and x.denominator.bit_length() <= 4096
                    for x in pair), "STOP_BOX_CAPACITY")
        require(pair[0] <= pair[1], "STOP_BOX_REVERSED")
        require(all(round_out(x, False) == x == round_out(x, True) for x in pair),
                "STOP_BOX_NOT_FINITE_BINARY64")
    return value


def scalar32(word):
    require(type(word) is int and 0 <= word < 2**32, "STOP_RAW_WORD_TYPE_RANGE")
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


def affine_range(coefficients, box, constant=F(0)):
    """Exact support of one affine form, not an independent interval graph."""
    lows = [c * (p[0] if c >= 0 else p[1]) for c, p in zip(coefficients, box)]
    highs = [c * (p[1] if c >= 0 else p[0]) for c, p in zip(coefficients, box)]
    return (constant + sum(lows, F(0)), constant + sum(highs, F(0)))


def pairs(interval):
    return [[x.numerator, x.denominator] for x in interval]


def prove_previous_zero(point_bounds, direction_bounds, triangle_words):
    """Sufficient ideal CPU box property ONLY. Never issues a launch credential."""
    point, direction = box_vector(point_bounds), box_vector(direction_bounds)
    require(not all(lo <= 0 <= hi for lo, hi in direction), "STOP_DIRECTION_ZERO_POSSIBLE")
    require(type(triangle_words) is tuple and len(triangle_words) == 3, "STOP_TRIANGLE_SHAPE")
    vertices = []
    for v in triangle_words:
        require(type(v) is tuple and len(v) == 3, "STOP_VERTEX_SHAPE")
        vertices.append(tuple(scalar32(w) for w in v))
    a, b, c = vertices
    e, f = sub(b, a), sub(c, a)
    normal = cross(e, f)
    out = dict(status="STOP_DEGENERATE_TRIANGLE", CPU_box_zero_contact_proved=False,
               parameter_zero_range=None, launch_exclusion_allowed=False,
               GPU_used=False, GPU_launch_allowed=False, native_precision_certified=False,
               upstream_binding_authenticated=False, nearest_hit_certified=False,
               full_path_visibility_certified=False, phase_certified=False,
               phase_error_bound=None, origin_offset_applied=False,
               ignored_primitive_ids=[], SOURCE_shared_token=False,
               full_costs="UNKNOWN_NOT_ZERO", old_producer_replays=0,
               scope="IDEAL_CPU_AFFINE_BOX_PROPERTY_NOT_NATIVE_OR_LAUNCH_CREDENTIAL")
    if normal == (F(0), F(0), F(0)):
        return out
    residual = affine_range(normal, point, -dot(normal, a))
    departure = affine_range(normal, direction)
    ee, ef, ff = dot(e, e), dot(e, f), dot(f, f)
    gram = ee*ff-ef*ef
    require(gram > 0, "STOP_GRAM_NOT_POSITIVE")
    cu = tuple((ff*x-ef*y)/gram for x, y in zip(e, f))
    cv = tuple((ee*y-ef*x)/gram for x, y in zip(e, f))
    cuv = tuple(x+y for x, y in zip(cu, cv))
    u = affine_range(cu, point, -dot(cu, a))
    v = affine_range(cv, point, -dot(cv, a))
    uv = affine_range(cuv, point, -dot(cuv, a))
    out.update(plane_affine_residual_range=pairs(residual),
               normal_dot_direction_range=pairs(departure),
               u_range=pairs(u), v_range=pairs(v), uv_range=pairs(uv))
    if residual != (F(0), F(0)):
        out["status"] = "STOP_ORIGIN_BOX_NOT_IDENTICALLY_ON_PLANE"
    elif departure[0] <= 0 <= departure[1]:
        out["status"] = "STOP_DIRECTION_POSSIBLE_PARALLEL_OR_COPLANAR"
    elif not (u[0] > 0 and v[0] > 0 and uv[1] < 1):
        out["status"] = "STOP_ORIGIN_BOX_NOT_STRICT_TRIANGLE_INTERIOR"
    else:
        out.update(status="CPU_DECLARED_ALL_BOX_ZERO_CONTACT_PROPERTY_ONLY",
                   CPU_box_zero_contact_proved=True, parameter_zero_range=[[0, 1], [0, 1]])
    return out
