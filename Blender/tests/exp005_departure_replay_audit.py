"""Replay frozen rounded hit points against the exact CPU departure witness.

Tests applicability, not a new self-hit sampler or native/GPU repair.
"""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
from exp005_departure_audit import witness, triangle
from exp005_geometric_return_audit import canonical, geometric_candidates, FROZEN_INPUT
from exp005_self_hit_audit import query
from exp005_interval_audit import exact_parameters, parameters
from exp005_triangle_oracle import sub
REPO_ROOT = Path(__file__).resolve().parents[2]
NEURO3D_COGNITION = Path(os.environ.get("NEURO3D_COGNITION_DIR", REPO_ROOT / ".cognition"))


def load_frozen(path):
    raw = Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != FROZEN_INPUT:
        raise ValueError('frozen evidence changed')
    return json.loads(raw)


def replay(retained):
    cases = retained['retained_same_triangle_adversaries']
    if len(cases) != 12:
        raise ValueError('twelve frozen records required')
    rows = []
    counts = {frame: {'accepted': 0, 'rejected': 0, 'exact_positive_t': 0,
        'exact_negative_t': 0, 'exact_zero_t': 0, 'parallel': 0} for frame in ('world', 'local')}
    for index, case in enumerate(cases):
        for frame in ('world', 'local'):
            q = query(case['record'], local=frame == 'local')
            if canonical(q) != canonical(case[frame+'_query']):
                raise ValueError('frozen query drift')
            if q['missed_initial']:
                raise ValueError('expected retained first hit')
            ray = copy.deepcopy(case['record'])
            ray['vertices'] = [sub(v, q['anchor_BU']) for v in ray['vertices']]
            ray['origin_BU'], ray['direction'] = q['point_BU'], q['reflected_direction']
            # Explicit synthetic owner label, NOT recovered optical metadata.
            ray['object_ids'] = ['retained_fixture_object']*len(ray['faces'])
            pid = q['first_triangle']; tri = triangle(ray, pid)
            exact = exact_parameters(ray['origin_BU'], ray['direction'], tri)
            interval = parameters(ray['origin_BU'], ray['direction'], tri)
            if exact is None:
                sign = 'parallel'
            else:
                sign = 'exact_positive_t' if exact['t'] > 0 else 'exact_negative_t' if exact['t'] < 0 else 'exact_zero_t'
            counts[frame][sign] += 1
            try:
                cert = witness(ray, previous_pid=pid,
                    expected_geometry_sha256=geometric_candidates(ray)['geometry_sha256'])
            except ValueError as exc:
                outcome = 'rejected'; detail = {'reason': str(exc)}
            else:
                outcome = 'accepted'; detail = {'witness': cert}
            counts[frame][outcome] += 1
            rows.append({'case': index, 'frame': frame, 'ray_after_rounded_hit': ray,
                'first_query': q, 'previous_pid': pid, 'outcome': outcome, **detail,
                'exact_signed_parameters': None if exact is None else
                    {key: [value.numerator, value.denominator] for key, value in exact.items()},
                'interval_parameters': interval})
    return {'scope': 'CPU applicability audit of exact witness on frozen rounded departures',
        'input_sha256': FROZEN_INPUT, 'counts': counts, 'rows': rows,
        'limitations': ['Twelve records selected for world self-hits, NOT an unbiased rate estimate',
            'First intersection/reflection was binary64 CPU arithmetic, NOT physical ground truth',
            'Owner labels synthetic; no Blender exporter or optical-history authentication',
            'Rejected rounded points need bounded origin/history contract, NOT snapping or relaxed epsilon',
            'No certificate of native transport, fields, GPU, RT, phase or generality']}


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True); args = parser.parse_args()
    if args.output.exists(): raise ValueError('new evidence path required')
    report = replay(load_frozen(args.input))
    previous = NEURO3D_COGNITION / 'neuro3d/exp005_departure_cpu_20260930_0934.json'
    raw = previous.read_bytes()
    if hashlib.sha256(raw).hexdigest() != 'e358a954d96700e7b90788631028e853a32d67ea0bb91758222db132134323f5':
        raise ValueError('prior witness evidence changed')
    deps = json.loads(raw)['code_sha256']
    for name, sha in deps.items():
        if hashlib.sha256(Path(name).read_bytes()).hexdigest() != sha:
            raise ValueError('witness dependency changed: '+name)
    for name in ('exp005_departure_replay_audit.py', 'test_exp005_departure_replay.py'):
        path = Path(__file__).with_name(name); deps[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
    report['code_sha256'] = deps
    report['prior_report_sha256'] = hashlib.sha256(raw).hexdigest()
    with args.output.open('x', encoding='utf-8') as output:
        output.write(json.dumps(report, indent=2, allow_nan=False)+'\n')
    print(json.dumps({'counts': report['counts'], 'rows': len(report['rows']),
        'sha256': hashlib.sha256(args.output.read_bytes()).hexdigest()}))


if __name__ == '__main__': main()
