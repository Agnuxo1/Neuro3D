"""CPU-only outward binary64 interval model for triangle parameters t/u/v.

Fixed expression tree, represented inputs, no FMA/fast-math/FTZ equivalence
claim. Exact rational comparisons are tests, NOT a GPU error certificate.
"""
import argparse
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
import random
from exp005_triangle_oracle import scalar
from exp005_cutoff_audit import fixture, GAPS
from exp005_near_origin_audit import vector as rational_vector, sub, dot, cross
from exp005_self_hit_audit import T_MIN_BU


class Interval:
    def __init__(self, low, high):
        self.low, self.high = scalar(low), scalar(high)
        if self.low > self.high: raise ValueError('ordered finite endpoints required')

    @classmethod
    def point(cls, x): return cls(x, x)

    @classmethod
    def outward(cls, low, high):
        return cls(math.nextafter(low, -math.inf), math.nextafter(high, math.inf))

    def __add__(self, other):
        return self.outward(self.low+other.low, self.high+other.high)

    def __sub__(self, other):
        return self.outward(self.low-other.high, self.high-other.low)

    def __mul__(self, other):
        values = [a*b for a in (self.low, self.high) for b in (other.low, other.high)]
        return self.outward(min(values), max(values))

    def __truediv__(self, other):
        if other.low <= 0 <= other.high: raise ValueError('denominator contains zero')
        values = [a/b for a in (self.low, self.high) for b in (other.low, other.high)]
        return self.outward(min(values), max(values))

    def pair(self): return [self.low, self.high]

    def contains(self, exact):
        return Fraction(self.low) <= exact <= Fraction(self.high)


def interval_vector(value):
    if len(value) != 3: raise ValueError('three components required')
    values = tuple(scalar(x) for x in value)
    if any(abs(x) > 1e6 for x in values): raise ValueError('CPU pilot bounds exceeded')
    return tuple(Interval.point(x) for x in values)


def interval_dot(a, b):
    # Explicit left-associated expression; NOT Python sum starting at int zero.
    return (a[0]*b[0]+a[1]*b[1])+a[2]*b[2]


def parameters(origin, direction, triangle):
    if len(triangle) != 3: raise ValueError('triangle required')
    a, b, c = (interval_vector(v) for v in triangle)
    o, d = interval_vector(origin), interval_vector(direction)
    e1, e2 = sub(b, a), sub(c, a); h = cross(d, e2)
    det = interval_dot(e1, h)
    if det.low <= 0 <= det.high:
        return {'status': 'uncertain_determinant', 'bounds': {'det': det.pair()}}
    rel = sub(o, a); q = cross(rel, e1)
    u = interval_dot(rel, h)/det; v = interval_dot(d, q)/det; t = interval_dot(e2, q)/det
    uv = u+v
    if u.high < 0 or v.high < 0 or uv.low > 1:
        status = 'outside_in_CPU_model'
    elif t.high <= 0:
        status = 'non_forward_in_CPU_model'
    elif t.low <= T_MIN_BU:
        status = 'possible_near_origin'
    elif u.low >= 0 and v.low >= 0 and uv.high <= 1:
        status = 'forward_inside_in_CPU_model'
    else:
        status = 'uncertain_barycentric_edge'
    return {'status': status, 'bounds': {name: value.pair() for name, value in
            (('det', det), ('u', u), ('v', v), ('t', t), ('u_plus_v', uv))}}


def exact_parameters(origin, direction, triangle):
    a, b, c = (rational_vector(v) for v in triangle)
    o, d = rational_vector(origin), rational_vector(direction)
    e1, e2 = sub(b, a), sub(c, a); h = cross(d, e2); det = dot(e1, h)
    if det == 0: return None
    rel = sub(o, a); q = cross(rel, e1)
    u, v, t = dot(rel, h)/det, dot(d, q)/det, dot(e2, q)/det
    return {'det': det, 'u': u, 'v': v, 't': t, 'u_plus_v': u+v}


def cases():
    rows = []
    for gap in GAPS:
        record = fixture(gap)
        for pid, face in enumerate(record['faces']):
            rows.append({'id': f'gap_{gap}_primitive_{pid}', 'origin': record['origin_BU'],
                'direction': record['direction'], 'triangle': [record['vertices'][i] for i in face],
                'group': 'departure' if pid < 2 else 'near' if pid < 4 else 'far'})
    rng = random.Random(202609300911)
    for i in range(24):
        base = (0., 100., 1e4)[i % 3]; gap = rng.uniform(.125, 2.)
        u, v = rng.uniform(.1, .3), rng.uniform(.1, .3)
        x = base+gap
        rows.append({'id': f'interior_{i}', 'origin': [base, -1+2*(u+v), -1+2*v],
            'direction': [1., 0., 0.], 'triangle': [[x, -1., -1.], [x, 1., -1.], [x, 1., 1.]],
            'group': 'interior'})
    for z in (0., 1.):
        rows.append({'id': f'parallel_{z}', 'origin': [0., 0., z],
            'direction': [1., 0., 0.], 'triangle': [[0., 0., 0.], [1., 0., 0.], [0., 1., 0.]],
            'group': 'parallel'})
    return rows


def audit():
    rows = []; counts = {}
    for case in cases():
        result = parameters(case['origin'], case['direction'], case['triangle'])
        exact = exact_parameters(case['origin'], case['direction'], case['triangle'])
        if exact is None:
            if result['status'] != 'uncertain_determinant': raise ValueError('parallel ray silently accepted')
        elif result['status'] != 'uncertain_determinant':
            for name, value in exact.items():
                if not Interval(*result['bounds'][name]).contains(value):
                    raise ValueError('exact rational value escaped interval')
        counts[result['status']] = counts.get(result['status'], 0)+1
        rows.append({'case': case, 'result': result,
            'exact': None if exact is None else {n: [v.numerator, v.denominator] for n, v in exact.items()}})
    # Departure t=0 widens across zero: a blanket near-origin gate would reject
    # valid departure. Retain that cost; NEVER force zero uncertainty for PASS.
    departure = [r for r in rows if r['case']['group'] == 'departure']
    if any(r['result']['status'] != 'possible_near_origin' for r in departure):
        raise ValueError('expected conservative departure uncertainty')
    return {'scope': 'CPU fixed-expression interval reference ONLY; no GPU/Bpy bound or repair',
        'cases': rows, 'counts': counts, 'departure_uncertainties': len(departure),
        'limitations': ['Represented binary64 inputs, no pre-export/transport error included',
            'No native FMA/reassociation/fast-math/FTZ expression equivalence demonstrated',
            'Det/barycentric uncertainty is NOT a miss; no fields/phase/runtime inference',
            'Origin departure certificate still required; blanket gate can reject valid rays']}


def main():
    p = argparse.ArgumentParser(); p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    if a.output.exists(): raise ValueError('new artifact required')
    r = audit(); root = Path(__file__).parents[1]
    files = [Path(__file__), Path(__file__).with_name('test_exp005_interval.py')]
    files += [Path(__file__).with_name(n) for n in ('exp005_near_origin_audit.py',
        'exp005_cutoff_audit.py', 'exp005_geometric_return_audit.py', 'exp005_self_hit_audit.py',
        'exp005_triangle_oracle.py', 'exp005_primitive_return_audit.py', 'exp005_precision_fixture.py')]
    files += [root/'benchmarks/capacity_audit'/n for n in ('primitive_tie_guard_v1.py',
        'primitive_return_guard_v1.py', 'frontier_inputs.py', 'gpu_geometry_probe.py')]
    files += [root/'shaders'/n for n in ('exp005_shared_frontier.glsl', 'exp005_nearest_v2.glsl')]
    r['code_sha256'] = {str(f): hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
    a.output.write_text(json.dumps(r, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps({'cases': len(r['cases']), 'counts': r['counts'],
        'departure_uncertainties': r['departure_uncertainties'],
        'sha256': hashlib.sha256(a.output.read_bytes()).hexdigest()}))


if __name__ == '__main__': main()
