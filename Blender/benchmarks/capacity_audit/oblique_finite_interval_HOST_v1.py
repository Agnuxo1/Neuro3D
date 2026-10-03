"""Opt-in exact HOST predicate; NEW CPU synthetic controls, not physical visibility."""
from fractions import Fraction as F
from hashlib import sha256
import json
from math import gcd

MODEL = "oblique-finite-interval-HOST-v1"
LABEL = "NEW_CPU_SYNTHETIC_NOT_SEALED_PHYSICAL"
POINTS = ("origin", "detector", "A", "B", "C")
FLAGS = dict(physical_visibility_certified=False, phase_certified=False,
             native_backend_certified=False, GPU_used=False, scene_authenticated=False)

def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=True, allow_nan=False).encode()).hexdigest()

def rational(value):
    if type(value) is not list or len(value) != 2:
        raise ValueError("rational_pair_required")
    n, d = value
    if type(n) is not int or type(d) is not int or d <= 0:
        raise ValueError("typed_positive_denominator_required")
    if max(abs(n).bit_length(), d.bit_length()) > 128 or gcd(n, d) != 1:
        raise ValueError("canonical_128bit_rational_required")
    x = F(n, d)
    if abs(x) > 2**32:
        raise ValueError("coordinate_domain_exceeded")
    return x

def keys(value, expected):
    if type(value) is not dict or set(value) != set(expected):
        raise ValueError("exact_schema_required")

def validate(scene, query):
    keys(scene, ("label", "scene_id", "context", "units", "points", "SOURCE", "DETECTOR", "primitive"))
    if scene["label"] != LABEL or scene["units"] != "scene_length":
        raise ValueError("synthetic_label_and_units_required")
    if type(scene["scene_id"]) is not str or not scene["scene_id"].startswith("NEW-SYNTHETIC/"):
        raise ValueError("new_scene_id_required")
    if type(scene["context"]) is not str or not 1 <= len(scene["context"]) <= 128:
        raise ValueError("context_required")
    if scene["SOURCE"] != {"id": "SOURCE0", "point": "origin"}:
        raise ValueError("separate_SOURCE0_required")
    if scene["DETECTOR"] != {"id": "DETECTOR0", "point": "detector"}:
        raise ValueError("finite_detector_required")
    if scene["primitive"] != {"id": "TRIANGLE0", "vertices": ["A", "B", "C"]}:
        raise ValueError("single_primitive_binding_required")
    keys(scene["points"], POINTS)
    boxes = {}
    for name in POINTS:
        point = scene["points"][name]
        keys(point, ("nominal", "radius"))
        if any(type(point[k]) is not list or len(point[k]) != 3 for k in ("nominal", "radius")):
            raise ValueError("all15_coordinates_and_radii_required")
        nominal, radius = [[rational(v) for v in point[k]] for k in ("nominal", "radius")]
        if any(r < 0 for r in radius):
            raise ValueError("negative_radius")
        boxes[name] = [(x-r, x+r) for x, r in zip(nominal, radius)]
    keys(query, ("model", "snapshot_sha256", "context", "source", "detector", "primitive", "segment"))
    expected = dict(model=MODEL, snapshot_sha256=digest(scene), context=scene["context"],
                    source="SOURCE0", detector="DETECTOR0", primitive="TRIANGLE0",
                    segment="CLOSED_FINITE_0_1")
    if query != expected:
        raise ValueError("query_snapshot_binding_mismatch")
    return boxes

def classify(scene, query):
    """Sound only for the explicitly declared independent coordinate boxes."""
    try:
        boxes = validate(scene, query)
    except (ValueError, TypeError, OverflowError) as exc:
        return dict(status="STOP_INPUT", reason=str(exc), trace=None, **FLAGS)
    counts = dict(add=0, sub=0, mul=0, neg=0)
    def add(a,b):
        counts["add"] += 1
        return a[0]+b[0], a[1]+b[1]
    def sub(a,b):
        counts["sub"] += 1
        return a[0]-b[1], a[1]-b[0]
    def mul(a,b):
        counts["mul"] += 1
        products = [x*y for x in a for y in b]
        return min(products), max(products)
    def neg(a):
        counts["neg"] += 1
        return -a[1], -a[0]
    def vsub(a,b):
        return [sub(x,y) for x,y in zip(a,b)]
    def cross(a,b):
        return [sub(mul(a[j],b[k]),mul(a[k],b[j])) for j,k in ((1,2),(2,0),(0,1))]
    def dot(a,b):
        terms = [mul(x,y) for x,y in zip(a,b)]
        return add(add(terms[0],terms[1]),terms[2])
    o, end, a, b, c = [boxes[n] for n in POINTS]
    d, e1, e2, s = vsub(end,o), vsub(b,a), vsub(c,a), vsub(o,a)
    p, q = cross(d,e2), cross(s,e1)
    det, u, v, t = dot(e1,p), dot(s,p), dot(d,q), dot(e2,q)
    w, end_slack = sub(sub(det,u),v), sub(det,t)
    raw = dict(det=det, U=u, V=v, W=w, T=t, end_slack=end_slack)
    sign = 1 if det[0] > 0 else -1 if det[1] < 0 else 0
    oriented = {k: neg(x) if sign == -1 else x for k,x in raw.items()} if sign else None
    # Fixed order, strict inequalities only; no EPS, no owner/object exception.
    if not sign:
        status, reason = "STOP_UNRESOLVED", "determinant_includes_zero"
    elif any(oriented[k][1] < 0 for k in ("U","V","W","T","end_slack")):
        status, reason = "DECLARED_BOX_DISJOINT", "strict_negative_slack"
    elif all(oriented[k][0] > 0 for k in ("U","V","W","T","end_slack")):
        status, reason = "DECLARED_BOX_INTERIOR_CROSS", "all_five_slacks_strict_positive"
    else:
        status, reason = "STOP_UNRESOLVED", "boundary_or_interval_overlap"
    def wire(iv):
        return [[x.numerator,x.denominator] for x in iv]
    return dict(status=status, reason=reason, snapshot_sha256=digest(scene),
                query_sha256=digest(query), coordinate_boxes=15, radius_slots=15,
                sign=sign, trace={k:wire(v) for k,v in raw.items()},
                oriented=None if oriented is None else {k:wire(v) for k,v in oriented.items()},
                exact_interval_operations=counts, division_operations=0, EPS_used=False,
                segment="CLOSED_FINITE_0_1", costs="HOST_PARTIAL_ONLY_FULL_COSTS_UNKNOWN",
                promotion="STOP_PHYSICAL_NATIVE_GPU", **FLAGS)
