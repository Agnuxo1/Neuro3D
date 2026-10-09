"""Bound the represented CPU hit-point error; no native/GPU certificate."""
import argparse
import hashlib
import json
from fractions import Fraction
import os
from pathlib import Path
from exp005_departure_replay_audit import load_frozen
from exp005_departure_audit import triangle
from exp005_interval_audit import Interval, interval_vector, parameters, exact_parameters
from exp005_near_origin_audit import vector, sub, dot, cross
from exp005_triangle_oracle import sub as float_sub
from exp005_geometric_return_audit import canonical
REPO_ROOT = Path(__file__).resolve().parents[2]
NEURO3D_COGNITION = Path(os.environ.get("NEURO3D_COGNITION_DIR", REPO_ROOT / ".cognition"))

REPLAY_SHA = 'd7bb937fca9c70bb2c371a2e8259fa9f2d3efe5f8f096cc0562fc88354d4e34d'


def enclosure(record, pid, saved_point, outgoing_direction):
    if not 1 <= len(record['faces']) <= 8 or len(record['vertices']) > 64:
        raise ValueError('bounded CPU fixture required')
    if isinstance(pid, bool) or not isinstance(pid, int) or not 0 <= pid < len(record['faces']):
        raise ValueError('valid primitive required')
    tri = triangle(record, pid)
    exact = exact_parameters(record['origin_BU'], record['direction'], tri)
    bounds = parameters(record['origin_BU'], record['direction'], tri)
    if exact is None or bounds['status'] == 'uncertain_determinant':
        raise ValueError('unresolved determinant; no finite origin certificate')
    if exact['t'] <= 0 or exact['u'] < 0 or exact['v'] < 0 or exact['u_plus_v'] > 1:
        raise ValueError('represented first hit outside strict forward triangle')
    o, d = vector(record['origin_BU']), vector(record['direction'])
    exact_point = tuple(x+y*exact['t'] for x, y in zip(o, d))
    oi, di = interval_vector(record['origin_BU']), interval_vector(record['direction'])
    ti = Interval(*bounds['bounds']['t'])
    point_box = [x+y*ti for x, y in zip(oi, di)]
    saved, outgoing = vector(saved_point), vector(outgoing_direction)
    if any(not box.contains(value) for box, value in zip(point_box, exact_point)):
        raise ValueError('rational point escaped CPU interval tree')
    # Rational endpoints prevent round-down when reporting a conservative radius.
    radii = [max(abs(Fraction(box.low)-q), abs(Fraction(box.high)-q))
             for box, q in zip(point_box, saved)]
    a, b, c = map(vector, tri); normal = cross(sub(b, a), sub(c, a))
    denom = abs(dot(normal, outgoing))
    if denom == 0: raise ValueError('outgoing ray parallel; no finite projected bound')
    projected = sum(abs(n)*r for n, r in zip(normal, radii))/denom
    signed_plane_t = dot(normal, sub(exact_point, saved))/dot(normal, outgoing)
    if abs(signed_plane_t) > projected:
        raise ValueError('signed plane offset escaped origin-error projection')
    pair = lambda value: [value.numerator, value.denominator]
    return {'point_intervals_BU': [box.pair() for box in point_box],
        'exact_point_BU': [pair(x) for x in exact_point],
        'axis_radius_BU_exact': [pair(x) for x in radii],
        'projected_plane_t_radius_BU_exact': pair(projected),
        'signed_plane_t_BU_exact': pair(signed_plane_t),
        'first_hit_parameters': bounds,
        'scope': 'error against ideal first hit of represented inputs, not physical/native history'}


def audit(retained, replay):
    cases = retained['retained_same_triangle_adversaries']
    if len(cases) != 12 or len(replay['rows']) != 24:
        raise ValueError('frozen coverage required')
    if {(x['case'], x['frame']) for x in replay['rows']} != {(i, f) for i in range(12) for f in ('world', 'local')}:
        raise ValueError('complete unique replay keys required')
    rows = []
    for row in replay['rows']:
        source = cases[row['case']]; q = source[row['frame']+'_query']
        if canonical(q) != canonical(row['first_query']): raise ValueError('saved query binding mismatch')
        record = dict(source['record'])
        record['vertices'] = [float_sub(v, q['anchor_BU']) for v in record['vertices']]
        record['origin_BU'] = float_sub(record['origin_BU'], q['anchor_BU'])
        result = enclosure(record, q['first_triangle'], q['point_BU'], q['reflected_direction'])
        if result['signed_plane_t_BU_exact'] != row['exact_signed_parameters']['t']:
            raise ValueError('independent plane identity disagrees with retained Moller rational t')
        rows.append({'case': row['case'], 'frame': row['frame'], 'enclosure': result})
    return {'scope': 'CPU-only outward point enclosure and rational plane-offset bound',
        'rows': rows, 'limitations': ['Inputs already rounded/translated; no pre-export or frame-conversion error included',
            'No guarantee chosen first triangle was globally correct or optical history authenticated',
            'Outgoing direction treated as supplied represented value, not reflection error enclosure',
            'Uncorrelated coordinate boxes can be conservative, particularly at grazing incidence',
            'NO exemption/acceptance gate, phase bound, native expression/FMA/FTZ certificate or GPU test']}


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists(): raise ValueError('new output path required')
    input_path = NEURO3D_COGNITION / 'neuro3d/exp005_self_hit_cpu_20260930_0804.json'
    replay_path = NEURO3D_COGNITION / 'neuro3d/exp005_departure_replay_cpu_20260930_0942.json'
    raw = replay_path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != REPLAY_SHA: raise ValueError('frozen replay changed')
    replay = json.loads(raw); deps = dict(replay['code_sha256'])
    for name, sha in deps.items():
        if hashlib.sha256(Path(name).read_bytes()).hexdigest() != sha: raise ValueError('dependency changed: '+name)
    result = audit(load_frozen(input_path), replay)
    for name in ('exp005_origin_enclosure_audit.py', 'test_exp005_origin_enclosure.py'):
        path = Path(__file__).with_name(name); deps[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
    result['code_sha256'] = deps
    result['input_sha256'] = replay['input_sha256']; result['replay_sha256'] = REPLAY_SHA
    with args.output.open('x', encoding='utf-8') as output:
        output.write(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps({'rows': len(result['rows']), 'sha256': hashlib.sha256(args.output.read_bytes()).hexdigest()}))


if __name__ == '__main__': main()
