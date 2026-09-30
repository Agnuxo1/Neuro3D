"""Bounded rational CPU reference for a PROSPECTIVE near-origin rejection gate.

Exact intersection parameters for represented binary64 inputs, not GPU error
enclosures or physical geometry. No renderer, fields or native integration.
"""
import argparse
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
from exp005_cutoff_audit import fixture, GAPS
from exp005_triangle_oracle import scalar
from exp005_self_hit_audit import T_MIN_BU
from exp005_geometric_return_audit import folded_geometric_control


def sub(a, b): return tuple(x-y for x, y in zip(a, b))
def dot(a, b): return sum(x*y for x, y in zip(a, b))
def cross(a, b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def vector(value):
    if len(value) != 3: raise ValueError('three components required')
    values = tuple(scalar(x) for x in value)
    if any(abs(x) > 1e6 for x in values): raise ValueError('bounded CPU reference domain exceeded')
    return tuple(Fraction(x) for x in values)


def signed_hits(record):
    vertices = [vector(v) for v in record['vertices']]
    faces = record['faces']
    if not 1 <= len(vertices) <= 64 or not 1 <= len(faces) <= 8:
        raise ValueError('reference requires <=64 vertices and <=8 triangles')
    origin, direction = vector(record['origin_BU']), vector(record['direction'])
    if abs(math.hypot(*(float(x) for x in direction))-1.) > 1e-12:
        raise ValueError('supplied unit direction required')
    hits = []
    for pid, face in enumerate(faces):
        if (len(face) != 3 or len(set(face)) != 3 or any(isinstance(i, bool) or
                not isinstance(i, int) or not 0 <= i < len(vertices) for i in face)):
            raise ValueError('valid triangular face required')
        a, b, c = (vertices[i] for i in face)
        e1, e2 = sub(b, a), sub(c, a)
        normal = cross(e1, e2)
        if normal == (0, 0, 0): raise ValueError('degenerate triangle')
        h = cross(direction, e2); det = dot(e1, h); rel = sub(origin, a)
        if det == 0:
            if dot(normal, rel) == 0: raise ValueError('coplanar ray requires another contract')
            continue
        u = dot(rel, h)/det; q = cross(rel, e1); v = dot(direction, q)/det
        if u < 0 or v < 0 or u+v > 1: continue  # Strict exact barycentrics.
        t = dot(e2, q)/det  # No sign/cutoff filter: retain zero and negative t.
        hits.append((pid, t))
    return hits


def near_origin_interval(t, *, distance_error_BU):
    if not isinstance(t, Fraction): raise ValueError('exact reference parameter required')
    error = scalar(distance_error_BU)
    if error < 0: raise ValueError('explicit nonnegative distance uncertainty required')
    e = Fraction(error); low, high = t-e, t+e
    # Any overlap with the excluded FORWARD interval (0,t_min] aborts.
    reject = high > 0 and low <= Fraction(T_MIN_BU)
    return {'low_exact': [low.numerator, low.denominator],
            'high_exact': [high.numerator, high.denominator],
            'action': 'abort' if reject else 'continue_close_gate_only'}


def diagnose(record, *, distance_error_BU):
    # Validate the explicit error even if no triangle yields a finite hit.
    near_origin_interval(Fraction(0), distance_error_BU=distance_error_BU)
    rows = [{'primitive_id': pid, 't_exact': [t.numerator, t.denominator],
             'interval': near_origin_interval(t, distance_error_BU=distance_error_BU)}
            for pid, t in signed_hits(record)]
    return {'action': 'abort' if any(r['interval']['action'] == 'abort' for r in rows)
            else 'continue_close_gate_only', 'signed_candidates': rows,
            'triangle_tests': len(record['faces']), 'distance_error_BU': float(distance_error_BU)}


def audit():
    rows = [{'gap_BU': gap, 'record': fixture(gap),
             'diagnostic': diagnose(fixture(gap), distance_error_BU=0.)} for gap in GAPS]
    if [r['diagnostic']['action'] for r in rows] != ['abort', 'abort',
            'continue_close_gate_only', 'continue_close_gate_only']:
        raise ValueError('near-origin contract reference failed')
    uncertainty = diagnose(fixture(2e-9), distance_error_BU=1.1e-9)
    if uncertainty['action'] != 'abort': raise ValueError('uncertain-origin sample must abort')
    folded = [{'record': row['record'],
               'diagnostic': diagnose(row['record'], distance_error_BU=0.)}
              for row in folded_geometric_control()]
    if any(row['diagnostic']['action'] != 'continue_close_gate_only' for row in folded):
        raise ValueError('represented-input folded control rejected')
    return {'scope': 'CPU rational reference + prospective close gate ONLY; not native repair',
            'fixed_t_min_BU': T_MIN_BU, 'cases': rows,
            'uncertainty_case': uncertainty,
            'folded_controls': folded,
            'limitations': ['Error zero means represented-input mathematical model ONLY',
                'No proven GPU/Bpy/transport or barycentric error enclosure',
                'Nonzero uncertainty also rejects departure t=0: conservative false aborts possible',
                'Strict barycentrics differ from native tolerance; no runtime equivalence',
                'Zero/negative reference t not near-positive, but other identity/mode gates still required']}


def main():
    p = argparse.ArgumentParser(); p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    if a.output.exists(): raise ValueError('new artifact required')
    r = audit(); root = Path(__file__).parents[1]
    files = [Path(__file__), Path(__file__).with_name('test_exp005_near_origin.py')]
    files += [Path(__file__).with_name(n) for n in ('exp005_cutoff_audit.py',
        'exp005_geometric_return_audit.py', 'exp005_self_hit_audit.py',
        'exp005_triangle_oracle.py', 'exp005_primitive_return_audit.py', 'exp005_precision_fixture.py')]
    files += [root/'benchmarks/capacity_audit'/n for n in ('primitive_tie_guard_v1.py',
        'primitive_return_guard_v1.py', 'frontier_inputs.py', 'gpu_geometry_probe.py')]
    files += [root/'shaders'/n for n in ('exp005_shared_frontier.glsl', 'exp005_nearest_v2.glsl')]
    r['code_sha256'] = {str(f): hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
    a.output.write_text(json.dumps(r, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps({'close_hits_abort': 2, 'above_cutoff_controls': 2,
        'uncertainty_aborts': 1, 'folded_controls': len(r['folded_controls']),
        'sha256': hashlib.sha256(a.output.read_bytes()).hexdigest()}))


if __name__ == '__main__': main()
