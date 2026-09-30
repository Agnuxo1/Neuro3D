"""Exact departure witness over bounded CPU fixture inputs, NOT native history.

No projection/snapping, tolerance relaxation, whole-object veto or GPU use.
The caller supplies prior-hit identity; hashing proves binding, not provenance.
"""
import argparse
import hashlib
import json
from pathlib import Path
from exp005_geometric_return_audit import canonical, geometric_candidates, folded_geometric_control
from exp005_interval_audit import exact_parameters, parameters
from exp005_near_origin_audit import vector, sub, dot, cross
from exp005_cutoff_audit import fixture, GAPS
from primitive_return_guard_v1 import primitive_id


def fingerprint(value):
    return hashlib.sha256(canonical(value).encode('utf-8')).hexdigest()


def triangle(record, pid):
    return [record['vertices'][i] for i in record['faces'][pid]]


def witness(record, *, previous_pid, expected_geometry_sha256, event='mirror'):
    if not 1 <= len(record['faces']) <= 8 or len(record['vertices']) > 64:
        raise ValueError('bounded CPU fixture required')
    if 'object_ids' not in record:
        raise ValueError('explicit owners required')
    for value in record['vertices']:
        vector(value)
    vector(record['origin_BU']); vector(record['direction'])
    previous_pid = primitive_id(previous_pid)
    if previous_pid >= len(record['faces']) or event not in ('mirror', 't', 'r'):
        raise ValueError('valid previous primitive and departure event required')
    geometry_sha = geometric_candidates(record)['geometry_sha256']
    if geometry_sha != expected_geometry_sha256:
        raise ValueError('stale fixture geometry')
    base = triangle(record, previous_pid)
    exact = exact_parameters(record['origin_BU'], record['direction'], base)
    if exact is None or exact['t'] != 0 or exact['u'] < 0 or exact['v'] < 0 or exact['u_plus_v'] > 1:
        raise ValueError('exact on-triangle nonparallel departure required; no snapping')
    a, b, c = map(vector, base)
    normal = cross(sub(b, a), sub(c, a))
    owner = record['object_ids'][previous_pid]
    zero_ids = []
    for pid in range(len(record['faces'])):
        tri = triangle(record, pid)
        if record['object_ids'][pid] != owner:
            continue
        if any(dot(normal, sub(vector(v), a)) != 0 for v in tri):
            continue
        value = exact_parameters(record['origin_BU'], record['direction'], tri)
        if value is not None and value['t'] == 0 and value['u'] >= 0 and value['v'] >= 0 and value['u_plus_v'] <= 1:
            zero_ids.append(pid)
    return {'schema': 'exp005-departure-CPU-witness-v1', 'geometry_sha256': geometry_sha,
        'ray_sha256': fingerprint({'origin': record['origin_BU'], 'direction': record['direction']}),
        'previous_pid': previous_pid, 'event': event, 'exact_zero_coplanar_same_owner_ids': zero_ids,
        'scope': 'represented CPU fixture only; caller history NOT authenticated'}


def diagnose(record, certificate):
    required = ('previous_pid', 'geometry_sha256', 'event')
    if not isinstance(certificate, dict) or any(k not in certificate for k in required):
        raise ValueError('complete witness required')
    recomputed = witness(record, previous_pid=certificate['previous_pid'],
        expected_geometry_sha256=certificate['geometry_sha256'], event=certificate['event'])
    if canonical(recomputed) != canonical(certificate):
        raise ValueError('witness binding/proof mismatch')
    rows = []
    for pid in range(len(record['faces'])):
        result = parameters(record['origin_BU'], record['direction'], triangle(record, pid))
        label = result['status']
        if pid in certificate['exact_zero_coplanar_same_owner_ids']:
            label = 'exact_departure_zero_CPU_witness'
        rows.append({'primitive_id': pid, 'interval_result': result, 'diagnostic': label})
    return rows


def audit():
    rows = []
    for gap in GAPS:
        record = fixture(gap)
        cert = witness(record, previous_pid=0,
            expected_geometry_sha256=geometric_candidates(record)['geometry_sha256'])
        labels = diagnose(record, cert)
        if cert['exact_zero_coplanar_same_owner_ids'] != [0, 1]:
            raise ValueError('departure seam not preserved')
        if any(labels[i]['diagnostic'] != labels[i]['interval_result']['status'] for i in (2, 3, 4, 5)):
            raise ValueError('nondeparture uncertainty hidden')
        rows.append({'gap_BU': gap, 'record': record, 'witness': cert, 'diagnostics': labels})
    folded = []
    for row in folded_geometric_control()[1:]:
        record = row['record']; previous = row['arbitration']['previous']['primitive_id']
        try:
            cert = witness(record, previous_pid=previous,
                expected_geometry_sha256=geometric_candidates(record)['geometry_sha256'])
            folded.append({'record': record, 'previous_pid': previous, 'witness': cert,
                'diagnostics': diagnose(record, cert)})
        except ValueError as exc:
            folded.append({'record': record, 'previous_pid': previous, 'rejected': str(exc)})
    return {'scope': 'CPU-only exact departure witness, NOT native propagation repair',
        'gap_cases': rows, 'folded_saved_rays': folded,
        'limitations': ['Geometry SHA is not full optical snapshot or prior-hit authentication',
            'Exact represented coordinates only; rounded off-plane departures reject rather than snap',
            'Interval/native FMA/transport/barycentric/phase bounds remain unresolved',
            'Other objects at t=0 and all positive hits retain original diagnostics',
            'No fields, Bpy readback, GPU, RT, generalization or performance claim']}


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists(): raise ValueError('new artifact required')
    result = audit()
    names = ('exp005_departure_audit.py', 'test_exp005_departure.py', 'exp005_interval_audit.py',
        'exp005_geometric_return_audit.py', 'exp005_cutoff_audit.py', 'exp005_near_origin_audit.py',
        'exp005_primitive_return_audit.py', 'exp005_self_hit_audit.py', 'exp005_precision_fixture.py',
        'exp005_triangle_oracle.py')
    files = [Path(__file__).with_name(name) for name in names]
    root = Path(__file__).parents[1]
    files += [root/'benchmarks/capacity_audit'/n for n in ('primitive_return_guard_v1.py', 'primitive_tie_guard_v1.py')]
    files += [root/'shaders'/n for n in ('exp005_shared_frontier.glsl', 'exp005_nearest_v2.glsl')]
    result['code_sha256'] = {str(f): hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
    with args.output.open('x', encoding='utf-8') as output:
        output.write(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps({'gap_cases': len(result['gap_cases']), 'folded_rejected':
        sum('rejected' in r for r in result['folded_saved_rays']),
        'sha256': hashlib.sha256(args.output.read_bytes()).hexdigest()}))


if __name__ == '__main__': main()
