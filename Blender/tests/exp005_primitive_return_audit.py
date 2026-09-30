"""Read retained CPU queries and test actual folded-object return controls."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parents[1]/'benchmarks'/'capacity_audit'))
from primitive_return_guard_v1 import classify_return
from exp005_self_hit_audit import query
from exp005_precision_fixture import reflected


def folded_record():
    scene = reflected(.5)
    first, second = scene['objects']['M'], scene['objects']['D']
    return {'vertices': first['vertices_world_BU']+second['vertices_world_BU'],
        'faces': first['faces']+[[i+4 for i in f] for f in second['faces']],
        'object_ids': ['folded_object']*4,
        'origin_BU': [0., 0., 0.], 'direction': [1., 0., 0.]}


def folded_control():
    record = folded_record()
    previous = None
    rows = []
    for step in range(3):
        hit = query(record)
        if hit['missed_initial']: raise ValueError('folded control missed a surface')
        triangle = hit['first_triangle']
        rule = classify_return(previous_primitive=previous, candidate_primitive=triangle,
            departure_event=None if previous is None else 'mirror',
            distance_BU=hit['first_distance_BU'])
        rows.append({'step': step, 'previous_triangle': previous,
                     'query': hit, 'guard': rule})
        previous = triangle
        record['origin_BU'], record['direction'] = hit['point_BU'], hit['reflected_direction']
    if [r['query']['first_triangle']//2 for r in rows] != [0, 1, 0]:
        raise ValueError('folded return sequence must visit face0, face1, face0')
    if any(r['guard']['action'] != 'continue' for r in rows):
        raise ValueError('legitimate folded-object return was excluded')
    return {'initial_record': folded_record(), 'steps': rows}


def audit(retained):
    rows = []
    for index, case in enumerate(retained['retained_same_triangle_adversaries']):
        q = query(case['record'])
        if (json.dumps(q, sort_keys=True, allow_nan=False) !=
                json.dumps(case['world_query'], sort_keys=True, allow_nan=False)):
            raise ValueError('retained query replay mismatch')
        rule = classify_return(previous_primitive=q['first_triangle'],
            candidate_primitive=q['first_triangle'], departure_event='mirror',
            distance_BU=q['same_triangle_self_hit_BU'])
        if rule['action'] != 'abort': raise ValueError('explicit same-triangle candidate not rejected')
        rows.append({'case_index': index, 'primitive': q['first_triangle'],
                     'candidate_distance_BU': q['same_triangle_self_hit_BU'], 'guard': rule})
    if len(rows) != 12: raise ValueError('all twelve retained candidates required')
    return {'scope': 'CPU rule applied to explicit candidates, NOT native propagation or nearest arbitration',
        'explicit_same_triangle_candidates': rows, 'folded_control': folded_control(),
        'limitations': ['No GPU previous-primitive ABI implemented',
                       'Other-triangle numerical returns remain unresolved',
                       'Rule cannot see candidates discarded by existing t_min filter',
                       'Local/raw Blender precision and modal/phase gates still separate']}


def main():
    p = argparse.ArgumentParser(); p.add_argument('--input', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True); a = p.parse_args()
    if a.output.exists(): raise ValueError('new artifact required')
    raw = a.input.read_bytes()
    expected = '534d2c14b5ab1738f00192068c70600ae94f60b3d601eda60ddb557206eedd71'
    if hashlib.sha256(raw).hexdigest() != expected: raise ValueError('frozen self-hit evidence changed')
    r = audit(json.loads(raw))
    r['input_sha256'] = expected
    paths = (Path(__file__), Path(__file__).with_name('exp005_self_hit_audit.py'),
        Path(__file__).with_name('exp005_triangle_oracle.py'),
        Path(__file__).with_name('exp005_precision_fixture.py'),
        Path(__file__).with_name('exp005_peer_ambiguity_audit.py'),
        Path(__file__).parents[1]/'benchmarks'/'capacity_audit'/'primitive_return_guard_v1.py',
        Path(__file__).parents[1]/'benchmarks'/'capacity_audit'/'frontier_inputs.py',
        Path(__file__).parents[1]/'benchmarks'/'capacity_audit'/'gpu_geometry_probe.py')
    r['code_sha256'] = {str(x): hashlib.sha256(x.read_bytes()).hexdigest() for x in paths}
    a.output.write_text(json.dumps(r, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps({'explicit_candidates_aborted': len(r['explicit_same_triangle_candidates']),
        'folded_control_steps_accepted': len(r['folded_control']['steps']),
        'sha256': hashlib.sha256(a.output.read_bytes()).hexdigest()}))


if __name__ == '__main__': main()
