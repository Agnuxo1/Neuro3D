"""Opt-in exact CPU box membership; never authorizes native triangle exclusion."""
from fractions import Fraction as F
from Blender.benchmarks.capacity_audit import oblique_transport_contact_plane_CPU_v1 as plane

def affine_interval(coefficients, offset, box):
    lo = hi = offset
    for coefficient, (lower, upper) in zip(coefficients, box):
        endpoints = (coefficient * lower, coefficient * upper)
        lo += min(endpoints)
        hi += max(endpoints)
    return lo, hi

def audit_interior(point_words, triangle_words, direction_words, declared_errors=None):
    """Declared Cartesian box only; prerequisite is zero residual for the whole box."""
    result = plane.audit_plane(point_words, triangle_words, direction_words, declared_errors)
    result["plane_status"] = result["status"]
    result.update(scope="CPU_DECLARED_BOX_TRIANGLE_MEMBERSHIP_ONLY_NOT_NATIVE",
                  gram_determinant=None, barycentric_affine=None,
                  barycentric_intervals=None, affine_partition_identity=False,
                  strict_interior_condition_cpu=False, nearest_hit_certified=False)
    if result["plane_status"] != "CPU_ZERO_PLANE_CONTACT_ONLY":
        result["status"] = "STOP_PLANE_PREREQUISITE"
        return result
    vertices = [tuple(plane.decode(w) for w in triangle_words[i:i+3])
                for i in (0, 3, 6)]
    a, b, c = vertices
    e1, e2 = plane.sub(b, a), plane.sub(c, a)
    g11, g12, g22 = plane.dot(e1, e1), plane.dot(e1, e2), plane.dot(e2, e2)
    gram = g11 * g22 - g12 * g12
    result["gram_determinant"] = plane.pair(gram)
    if gram <= 0:
        result["status"] = "STOP_DEGENERATE_GRAM"
        return result
    u = tuple((g22*x-g12*y)/gram for x,y in zip(e1,e2))
    v = tuple((g11*y-g12*x)/gram for x,y in zip(e1,e2))
    ou, ov = -plane.dot(u,a), -plane.dot(v,a)
    w = tuple(-x-y for x,y in zip(u,v))
    ow = F(1)-ou-ov
    assert all(x+y+z == 0 for x,y,z in zip(u,v,w)) and ou+ov+ow == 1
    box = [(F(*lo), F(*hi)) for lo,hi in result["point_box"]]
    intervals = [affine_interval(coeff, offset, box)
                 for coeff,offset in ((u,ou),(v,ov),(w,ow))]
    result["barycentric_affine"] = [
        {"coefficients": [plane.pair(x) for x in coeff], "offset": plane.pair(offset)}
        for coeff,offset in ((u,ou),(v,ov),(w,ow))]
    result["affine_partition_identity"] = True
    result["barycentric_intervals"] = [[plane.pair(lo),plane.pair(hi)] for lo,hi in intervals]
    if all(lo > 0 for lo,hi in intervals):
        result["status"] = "CPU_ZERO_CONTACT_STRICT_INTERIOR_CONDITION_ONLY"
        result["strict_interior_condition_cpu"] = True
    elif any(hi < 0 for lo,hi in intervals):
        result["status"] = "CPU_BOX_OUTSIDE_TRIANGLE_ON_PLANE_ONLY"
    elif all(lo >= 0 for lo,hi in intervals):
        result["status"] = "STOP_TRIANGLE_BOUNDARY"
    else:
        result["status"] = "STOP_UNCERTAIN_TRIANGLE_MEMBERSHIP"
    return result
