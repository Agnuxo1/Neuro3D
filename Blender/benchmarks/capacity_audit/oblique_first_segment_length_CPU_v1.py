"""Opt-in ideal first-segment length enclosure, conditional on upstream t.

Pure CPU mathematical analysis, NOT a binary64 length graph or GPU dispatcher.
No imports/replay of retained producers, and no file writes.
"""
from fractions import Fraction as F
from math import isqrt

ROOT_BITS = 96
GRID = 1 << ROOT_BITS


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def rational(value):
    require(type(value) is F, "STOP_RATIONAL_TYPE")
    require(value.numerator.bit_length() <= 4096 and value.denominator.bit_length() <= 4096,
            "STOP_ANALYSIS_CAPACITY")
    return value


def root_interval(value):
    """Fixed dyadic96 absolute bracket; exact squares remain point intervals."""
    value = rational(value)
    require(value >= 0, "STOP_NEGATIVE_RADICAND")
    k = isqrt((value.numerator << (2*ROOT_BITS)) // value.denominator)
    lo = F(k, GRID)
    hi = lo if lo*lo == value else F(k+1, GRID)
    require(lo*lo <= value <= hi*hi and hi-lo <= F(1, GRID), "root_bracket")
    return lo, hi


def direction_scalar(word):
    require(type(word) is int and 0 <= word < 2**32, "STOP_WORD_TYPE_RANGE")
    exponent, mantissa = (word >> 23) & 255, word & 0x7fffff
    require(exponent != 255 and not (exponent == 0 and mantissa) and word != 0x80000000,
            "STOP_ORIGINAL_DIRECTION_WORD_DOMAIN")
    if exponent == 0:
        return F(0)
    shift = exponent-150
    value = F((2**23+mantissa) << shift) if shift >= 0 else F(2**23+mantissa, 2**(-shift))
    value = -value if word >> 31 else value
    require(abs(value) <= 1000000, "STOP_ORIGINAL_DIRECTION_BOUND")
    return value


def pair_json(lo, hi):
    return [[lo.numerator, lo.denominator], [hi.numerator, hi.denominator]]


def enclose(direction_words, t_bounds):
    """Analytical helper: caller's t interval is conditional, not authenticated.

    Direction words are original binary32. L is ideal geometric displacement
    t*sqrt(sum(direction**2)); no rounded point subtraction or GPU sqrt assumed.
    """
    require(type(direction_words) is tuple and len(direction_words) == 3, "STOP_DIRECTION_SHAPE")
    require(type(t_bounds) is tuple and len(t_bounds) == 2, "STOP_T_SHAPE")
    lo, hi = [rational(x) for x in t_bounds]
    require(0 < lo <= hi, "STOP_T_CONTACT_OR_ORDER")
    direction = tuple(direction_scalar(x) for x in direction_words)
    norm_squared = sum(x*x for x in direction)
    require(norm_squared > 0, "STOP_ZERO_DIRECTION")
    norm_lo, norm_hi = root_interval(norm_squared)
    length_lo, length_hi = lo*norm_lo, hi*norm_hi
    # Keep origin/rounding errors of a native point/norm implementation out of scope.
    return dict(status="CONDITIONAL_LENGTH_ENCLOSURE" if length_lo > 0 else "STOP_LENGTH_ZERO_POSSIBLE",
                scope="CPU_IDEAL_FIRST_SEGMENT_CONDITIONAL_ON_UPSTREAM_T",
                direction_original_words=list(direction_words), normalized=False,
                direction_norm_squared=[norm_squared.numerator, norm_squared.denominator],
                direction_norm_interval=pair_json(norm_lo, norm_hi), root_grid_bits=ROOT_BITS,
                t_interval=pair_json(lo, hi), t_units="original_unnormalized_ray_parameter",
                length_interval=pair_json(length_lo, length_hi),
                length_units="declared_scene_BU_NOT_meters_NOT_optical_path",
                length_width=[(length_hi-length_lo).numerator, (length_hi-length_lo).denominator],
                source_binding_authenticated=False, native_length_graph_certified=False,
                exact_contact_allowed=False, complete_path_visibility_certified=False,
                complete_trace_output=False, GPU_used=False, GPU_launch_allowed=False,
                phase_certified=False, phase_error_bound=None, full_costs="UNKNOWN_NOT_ZERO")
