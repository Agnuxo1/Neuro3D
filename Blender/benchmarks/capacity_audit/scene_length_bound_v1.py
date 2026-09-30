"""Prospective ideal-scene length bound; not a native geometric error bound.

No traversal or intermediate rays. Exact rational AABB bounds for represented
coordinates, convex triangle hits and unit directions; depth is explicit.
"""
from fractions import Fraction
import hashlib
import json
import math
from frontier_inputs import pack_frontier
from phase_transport_budget_v1 import wavelength_phase_budget


def pair(value):
    return [value.numerator, value.denominator]


def upward_float(value):
    result = float(value)
    if not math.isfinite(result):
        raise ValueError('finite length bound required')
    if Fraction(result) < value:
        result = math.nextafter(result, math.inf)
    return result


def scene_length_bound(snapshot, *, max_depth, mode_cap=3):
    if isinstance(max_depth, bool) or not isinstance(max_depth, int) or not 1 <= max_depth <= 32:
        raise ValueError('explicit depth in [1,32] required')
    pack_frontier(snapshot, mode_cap=mode_cap)  # Raw ABI validation, no traversal.
    points = [tuple(Fraction(float(v)) for v in source['position_BU']) for source in snapshot['sources']]
    points += [tuple(Fraction(float(v)) for v in vertex)
               for obj in snapshot['objects'].values() for vertex in obj['vertices_world_BU']]
    lo = tuple(min(p[i] for p in points) for i in range(3))
    hi = tuple(max(p[i] for p in points) for i in range(3))
    diameter_l1 = sum((b-a for a,b in zip(lo,hi)), Fraction(0))
    references = {}
    for name, obj in snapshot['objects'].items():
        if obj['kind'] in ('det', 'escape'):
            ref = tuple(Fraction(float(v)) for v in obj['mode_origin_BU'])
            references[name] = sum((max(abs(r-a), abs(r-b)) for r,a,b in zip(ref,lo,hi)), Fraction(0))
    reference_bound = max(references.values())
    total = max_depth*diameter_l1 + reference_bound
    canonical = json.dumps(snapshot, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()
    return {'scene_canonical_sha256': hashlib.sha256(canonical).hexdigest(),
        'max_depth': max_depth, 'mode_cap': mode_cap,
        'aabb_lower_BU_rational': [pair(v) for v in lo],
        'aabb_upper_BU_rational': [pair(v) for v in hi],
        'segment_diameter_L1_BU_rational': pair(diameter_l1),
        'reference_offset_L1_BU_rational': pair(reference_bound),
        'terminal_reference_bounds_BU_rational': {n:pair(v) for n,v in references.items()},
        'effective_length_abs_BU_rational': pair(total),
        'effective_length_abs_BU_upward_float': upward_float(total),
        'scope': 'ideal represented scene, convex hits + unit directions + at most max_depth segments',
        'native_certified': False,
        'excluded': ['GPU barycentric tolerance outside triangles', 'rounded origins/intersections/directions',
            'hi-lo geometry/reference decode error', 'length summation and phase reduction',
            'unexported geometry and many-path complex-field error']}


def scene_wavelength_budget(snapshot, *, max_depth, phase_budget_rad, relative_budget, mode_cap=3):
    bound = scene_length_bound(snapshot, max_depth=max_depth, mode_cap=mode_cap)
    phase = wavelength_phase_budget(snapshot['lambda_BU'],
        max_effective_length_BU=bound['effective_length_abs_BU_upward_float'],
        phase_budget_rad=phase_budget_rad, relative_budget=relative_budget)
    return {'scene_bound': bound, 'wavelength_only_budget': phase,
        'native_promotion_allowed': False}
