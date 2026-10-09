"""Opt-in HOST necessary scene invariants; never certifies native equivalence.
No foreign imports, tracing, normalization, casts, interpolation or GPU work.
"""
from collections import Counter
from fractions import Fraction as F
import math

MODEL = "scene-necessary-invariants-HOST-v1"


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def rational(value):
    need(type(value) is list and len(value) == 2
         and all(type(v) is int for v in value), "typed rational")
    n, d = value
    need(d > 0 and max(abs(n).bit_length(), d.bit_length()) <= 128,
         "bounded rational")
    q = F(n, d)
    need([q.numerator, q.denominator] == value and abs(q) <= 10**6,
         "canonical rational")
    return q


def binary64_input(value):
    need(type(value) in (int, float), "typed snapshot scalar")
    if type(value) is int:
        need(abs(value) <= 10**6, "bounded snapshot integer")
        return F(value)
    need(math.isfinite(value) and abs(value) <= 10**6, "finite snapshot scalar")
    return F.from_float(value)  # Exact input word value, NOT decimal idealization.


def vector(value, decode):
    need(type(value) is list and len(value) == 3, "vector3")
    return tuple(decode(v) for v in value)


def ray_key(source, decode):
    p = vector(source["position_BU"], decode)
    d = vector(source["direction"], decode)
    pivot = next((abs(v) for v in d if v), None)
    need(pivot is not None, "zero source direction")
    # Same ideal oriented ray under positive scale; no sqrt/RN64 execution claim.
    return p, tuple(v / pivot for v in d)


def extent(triangles):
    points = []
    for tri in triangles:
        a, b, c = tri
        u, v = tuple(b[i]-a[i] for i in range(3)), tuple(c[i]-a[i] for i in range(3))
        cross = (u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2],
                 u[0]*v[1]-u[1]*v[0])
        if any(cross):
            points.extend(tri)
    need(bool(points), "no nondegenerate triangle surface")
    return tuple((min(p[i] for p in points), max(p[i] for p in points))
                 for i in range(3))


def original_invariants(scene, request):
    need(scene["schema"] == "precision-oblique-declared-scene-v1"
         and scene["units"] == "BU", "original BU frame")
    need(type(scene["sources"]) is list and 1 <= len(scene["sources"]) <= 64,
         "bounded original sources")
    need(type(scene["triangles"]) is list and 1 <= len(scene["triangles"]) <= 512,
         "bounded original triangles")
    triangles = []
    for t in scene["triangles"]:
        need(type(t["vertices_BU"]) is list and len(t["vertices_BU"]) == 3,
             "original triangle3")
        triangles.append(tuple(vector(v, rational) for v in t["vertices_BU"]))
    lam = rational(request["lambda_BU"])
    need(lam > 0, "positive original wavelength")
    return extent(triangles), Counter(ray_key(s, rational) for s in scene["sources"]), lam


def snapshot_invariants(snapshot):
    need(snapshot["schema"] == "exp005-readback-v2", "snapshot schema BU convention")
    objects, sources = snapshot["objects"], snapshot["sources"]
    need(type(objects) is dict and 1 <= len(objects) <= 128, "bounded objects")
    need(type(sources) is list and 1 <= len(sources) <= 64, "bounded snapshot sources")
    triangles = []
    for obj in objects.values():
        vertices, faces = obj["vertices_world_BU"], obj["faces"]
        need(type(vertices) is list and 1 <= len(vertices) <= 2048, "bounded vertices")
        need(type(faces) is list and len(faces) <= 512, "bounded faces")
        points = [vector(v, binary64_input) for v in vertices]
        for face in faces:
            need(type(face) is list and len(face) == 3
                 and all(type(i) is int and 0 <= i < len(points) for i in face),
                 "triangle face indices")
            triangles.append(tuple(points[i] for i in face))
            need(len(triangles) <= 512, "bounded total triangles")
    lam = binary64_input(snapshot["lambda_BU"])
    need(lam > 0, "positive snapshot wavelength")
    return extent(triangles), Counter(ray_key(s, binary64_input) for s in sources), lam


def compare(scene, request, snapshot):
    """Necessary invariants ONLY in the same declared BU coordinates.
    Ignores identifiers, order, winding and positive SOURCE direction scaling.
    A mismatch refutes whole-scene identity in this frame. Equal invariants
    are NOT sufficient: material, topology, detector/query and ALU remain open.
    """
    result = dict(model=MODEL, status="STOP_INPUT", reasons=[],
                  equivalence_proved=False, native_precision_certified=False,
                  phase_bound_rad=None, current_GPU_admission=False,
                  coordinate_transform_checked=False, sources_merged=False)
    try:
        a, b = original_invariants(scene, request), snapshot_invariants(snapshot)
        names = ("surface_extent_BU", "oriented_SOURCE_multiset", "lambda_BU")
        result["invariant_equal"] = {k: x == y for k, x, y in zip(names, a, b, strict=True)}
        result["reasons"] = [k for k in names if not result["invariant_equal"][k]]
        result["status"] = ("DIFFERENT_DECLARED_SCENE_SAME_BU_FRAME" if result["reasons"]
                            else "STOP_EQUAL_NECESSARY_INVARIANTS_NOT_EQUIVALENCE")
    except (ValueError, KeyError, TypeError, IndexError, OverflowError) as ex:
        result["reasons"] = [str(ex)]
    return result
