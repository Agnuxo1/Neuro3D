"""Apply prospective tie policy to ALL hits of retained CPU triangle queries.

No Bpy/GPU, no fields, no 192-trial regeneration, no peer writer execution.
Manifest fingerprint covers only this geometric fixture, not an optical scene.
"""
import argparse
import copy
import hashlib
import itertools
import json
import math
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1]/'benchmarks'/'capacity_audit'))
from primitive_tie_guard_v1 import resolve_candidates
from exp005_triangle_oracle import vec, sub, cross, unit, triangle_hit
from exp005_self_hit_audit import query, T_MIN_BU
from exp005_primitive_return_audit import folded_record

FROZEN_INPUT = '534d2c14b5ab1738f00192068c70600ae94f60b3d601eda60ddb557206eedd71'


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def geometric_candidates(record, *, triangle_order=None):
    vertices = [vec(v) for v in record['vertices']]
    faces = record['faces']
    if not 1 <= len(faces) <= 64:
        raise ValueError('pilot requires 1..64 faces')
    objects = record.get('object_ids', ['fixture_object']*len(faces))
    if len(objects) != len(faces) or any(not isinstance(o, str) or not o for o in objects):
        raise ValueError('explicit object IDs per primitive required')
    triangles = []
    for face in faces:
        if (len(face) != 3 or len(set(face)) != 3 or any(isinstance(i, bool) or
                not isinstance(i, int) or not 0 <= i < len(vertices) for i in face)):
            raise ValueError('valid pre-triangulated face required')
        tri = tuple(vertices[i] for i in face)
        unit(cross(sub(tri[1], tri[0]), sub(tri[2], tri[0])))
        triangles.append(tri)
    order = list(range(len(faces))) if triangle_order is None else list(triangle_order)
    if (any(isinstance(i, bool) or not isinstance(i, int) for i in order) or
            sorted(order) != list(range(len(faces)))):
        raise ValueError('query must cover every primitive exactly once')
    geometry = {'vertices': vertices, 'faces': faces, 'object_ids': objects}
    sha = hashlib.sha256(canonical(geometry).encode('utf-8')).hexdigest()
    manifest = [{'primitive_id': i, 'object_id': o} for i, o in enumerate(objects)]
    origin, direction = vec(record['origin_BU']), vec(record['direction'])
    # Validate, do NOT renormalize saved rays and change their arithmetic.
    if abs(math.hypot(*direction)-1.) > 1e-12:
        raise ValueError('retained unit direction required')
    hits = []
    for pid in order:
        h = triangle_hit(origin, direction, triangles[pid], T_MIN_BU)
        if h is not None:
            hits.append({'primitive_id': pid, 'distance_BU': h[0], 'normal': h[1]})
    return {'geometry_sha256': sha, 'manifest': manifest, 'candidates': hits,
            'triangle_order': order, 'triangle_tests': len(order)}


def resolve_query(record, previous_pid=None, *, triangle_order=None):
    result = geometric_candidates(record, triangle_order=triangle_order)
    state = None if previous_pid is None else {
        'snapshot_sha256': result['geometry_sha256'], 'primitive_id': previous_pid,
        'departure_event': 'mirror'}
    rule = resolve_candidates(snapshot_sha256=result['geometry_sha256'],
        manifest=result['manifest'], candidates=result['candidates'], previous=state)
    return dict(result, previous=state, rule=rule)


def folded_geometric_control():
    record = folded_record(); previous = None; rows = []
    for step in range(3):
        q = query(record)
        result = resolve_query(record, previous)
        if result['rule']['action'] != 'continue':
            raise ValueError('geometric folded control rejected')
        if result['rule']['minimum_distance_BU'] != q['first_distance_BU']:
            raise ValueError('folded minimum drift')
        rows.append({'record': copy.deepcopy(record), 'query': q, 'arbitration': result})
        previous = result['rule']['selected_primitive']
        record['origin_BU'], record['direction'] = q['point_BU'], q['reflected_direction']
    if [r['arbitration']['rule']['selected_primitive']//2 for r in rows] != [0, 1, 0]:
        raise ValueError('folded control must visit face0, face1, face0')
    return rows


def audit(retained):
    cases = retained['retained_same_triangle_adversaries']
    if len(cases) != 12: raise ValueError('twelve frozen fixtures required')
    rows = []
    for index, case in enumerate(cases):
        for local in (False, True):
            q = query(case['record'], local=local)
            if canonical(q) != canonical(case['local_query' if local else 'world_query']):
                raise ValueError('frozen numeric query replay mismatch')
            ray = copy.deepcopy(case['record'])
            ray['vertices'] = [sub(v, q['anchor_BU']) for v in ray['vertices']]
            ray['origin_BU'], ray['direction'] = q['point_BU'], q['reflected_direction']
            results = [resolve_query(ray, q['first_triangle'], triangle_order=order)
                       for order in itertools.permutations(range(len(ray['faces'])))]
            if any(r['rule'] != results[0]['rule'] for r in results):
                raise ValueError('geometric result depends on query order')
            own_hits = [h for h in results[0]['candidates'] if h['primitive_id'] == q['first_triangle']]
            expected = q['same_triangle_self_hit_BU']
            if ([h['distance_BU'] for h in own_hits] != ([] if expected is None else [expected])):
                raise ValueError('same-primitive candidate differs from retained query')
            rows.append({'case': index, 'frame': 'local' if local else 'world',
                'record_after_reflection': ray, 'previous_query': q, 'permutations': results})
    counts = {frame: {action: sum(r['frame'] == frame and
                  r['permutations'][0]['rule']['action'] == action for r in rows)
                  for action in ('abort', 'continue', 'miss')} for frame in ('world', 'local')}
    return {'scope': 'CPU synthetic geometric queries + prospective tie policy; NO Bpy/GPU/field network',
        'queries': rows, 'counts': counts, 'folded_geometric_control': folded_geometric_control(),
        'limitations': ['same scalar oracle as earlier reproduction, not independent Maxwell validation',
            'local/world fingerprint only fixture geometry, not exporter or full optical snapshot',
            't_min may discard positive returns; other-face numerical returns unresolved',
            'native per-branch IDs, fields/phase/ledger/guard and peer review pending']}


def main():
    p = argparse.ArgumentParser(); p.add_argument('--input', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True); a = p.parse_args()
    if a.output.exists(): raise ValueError('new artifact required')
    raw = a.input.read_bytes()
    if hashlib.sha256(raw).hexdigest() != FROZEN_INPUT:
        raise ValueError('frozen input changed')
    result = audit(json.loads(raw)); result['input_sha256'] = FROZEN_INPUT
    root = Path(__file__).parents[1]
    files = [Path(__file__), Path(__file__).with_name('test_exp005_geometric_return.py'),
        Path(__file__).with_name('exp005_self_hit_audit.py'),
        Path(__file__).with_name('exp005_primitive_return_audit.py'),
        Path(__file__).with_name('exp005_precision_fixture.py'),
        Path(__file__).with_name('exp005_triangle_oracle.py')]
    files += [root/'benchmarks/capacity_audit'/name for name in
              ('primitive_tie_guard_v1.py', 'primitive_return_guard_v1.py',
               'frontier_inputs.py', 'gpu_geometry_probe.py')]
    files += [root/'shaders'/name for name in ('exp005_shared_frontier.glsl', 'exp005_nearest_v2.glsl')]
    result['code_sha256'] = {str(f): hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
    a.output.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps({'queries': len(result['queries']), 'counts': result['counts'],
        'sha256': hashlib.sha256(a.output.read_bytes()).hexdigest()}))


if __name__ == '__main__': main()
