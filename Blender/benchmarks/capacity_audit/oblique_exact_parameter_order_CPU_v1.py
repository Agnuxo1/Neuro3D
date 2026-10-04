"""Opt-in exact CPU audit for two raw32 triangles; never a native hit credential."""
from fractions import Fraction as F
import hashlib
import struct

WORD_COUNT = 24
COORDINATE_LIMIT = 1000000


def decode32(word):
    if type(word) is not int or not 0 <= word <= 0xffffffff:
        raise ValueError("raw32 requires uint32, not bool/float")
    sign, exponent, mantissa = word >> 31, (word >> 23) & 255, word & 0x7fffff
    if exponent == 255 or (exponent == 0 and (mantissa or sign)):
        raise ValueError("nonfinite, subnormal and negative zero are outside this contract")
    if not exponent:
        return F(0)
    power = exponent - 150
    value = F(((-1) ** sign) * ((1 << 23) + mantissa))
    value = value * (1 << power) if power >= 0 else value / (1 << -power)
    if abs(value) > COORDINATE_LIMIT:
        raise ValueError("raw coordinate outside declared audit domain")
    return value


def sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def dot(a, b):
    return sum((x*y for x, y in zip(a, b)), F(0))


def pair(value):
    return [value.numerator, value.denominator]


def compare_quotients(a, b):
    """Compare exact rational quotients through integer cross-products, no rounded t."""
    left = a.numerator * b.denominator
    right = b.numerator * a.denominator
    return (left > right) - (left < right)


def triangle(origin, direction, vertices):
    a, b, c = vertices
    e1, e2 = sub(b, a), sub(c, a)
    p = cross(direction, e2)
    det = dot(e1, p)
    if not det:
        return {"state": "STOP_ZERO_DETERMINANT"}
    s = sub(origin, a)
    q = cross(s, e1)
    un, vn, tn = dot(s, p), dot(direction, q), dot(e2, q)
    if det < 0:
        det, un, vn, tn = -det, -un, -vn, -tn
    t, u, v = tn/det, un/det, vn/det
    evidence = {"det": pair(det), "t_numerator": pair(tn), "t": pair(t),
                "u": pair(u), "v": pair(v)}
    if tn == 0:
        return dict(evidence, state="STOP_CONTACT")
    if tn < 0 or un < 0 or vn < 0 or un+vn > det:
        return dict(evidence, state="MISS_EXACT")
    if un == 0 or vn == 0 or un+vn == det:
        return dict(evidence, state="STOP_BOUNDARY")
    point = tuple(origin[i] + t*direction[i] for i in range(3))
    bary_point = tuple(a[i] + u*e1[i] + v*e2[i] for i in range(3))
    if point != bary_point or dot(cross(e1, e2), sub(point, a)) != 0:
        raise ArithmeticError("exact incidence invariant broken")
    return dict(evidence, state="INTERIOR_EXACT_CPU_ONLY", point=[pair(x) for x in point])


def audit_raw_stage(words):
    """24 uint32 = o3,d3,triangleA9,triangleB9. Not N3DG32V1.
    Exceptions and STOPs are fail-closed. No IDs, epsilon, native admission or I/O.
    """
    if type(words) not in (list, tuple) or len(words) != WORD_COUNT:
        raise ValueError("exactly two triangles and one ray required")
    values = tuple(decode32(w) for w in words)
    origin, direction = values[:3], values[3:6]
    if direction == (0, 0, 0):
        raise ValueError("zero direction")
    vertices = [tuple(values[j:j+3] for j in range(base, base+9, 3)) for base in (6, 15)]
    hits = [triangle(origin, direction, v) for v in vertices]
    stops = [i for i, h in enumerate(hits) if h["state"].startswith("STOP")]
    candidates = [i for i, h in enumerate(hits) if h["state"] == "INTERIOR_EXACT_CPU_ONLY"]
    chosen, comparison = None, None
    if stops:
        status = "STOP_UNRESOLVED_TRIANGLE"
    elif not candidates:
        status = "MISS_TWO_TRIANGLES_CPU_ONLY"
    elif len(candidates) == 1:
        chosen, status = candidates[0], "UNIQUE_TWO_TRIANGLES_CPU_ONLY"
    else:
        comparison = compare_quotients(F(*hits[0]["t"]), F(*hits[1]["t"]))
        if not comparison:
            status = "STOP_EXACT_TIE"
        else:
            chosen = 0 if comparison < 0 else 1
            status = "UNIQUE_TWO_TRIANGLES_CPU_ONLY"
    bundle = struct.pack("<24I", *words)
    return {"schema": "RAW_TWO_TRIANGLES_EXACT_CPU_AUDIT_V1", "status": status,
            "raw_stage_sha256": hashlib.sha256(bundle).hexdigest(), "raw_stage_bytes": 96,
            "scope": "TWO_TRIANGLES_ONLY_NOT_AUTHENTICATED_SCENE_OR_NATIVE_OUTPUT",
            "triangles": hits, "quotient_comparison": comparison,
            "candidate_index": chosen, "stop_triangle_indices": stops,
            "exact_candidate_point": None if chosen is None else hits[chosen]["point"],
            "GPU_launch_allowed": False, "launch_exclusion_allowed": False,
            "native_precision_certified": False, "nearest_hit_certified": False,
            "full_path_visibility_certified": False, "phase_certified": False,
            "phase_error_bound": None, "native_origin_box_bound": None,
            "transport_hilo_implemented": False, "full_costs": "UNKNOWN_NOT_ZERO"}
