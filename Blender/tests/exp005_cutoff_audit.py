"""CPU reproducer for F5: a filtered hit cannot be rescued by tie arbitration.

Analytic parallel-plane reference, no field inference, Blender or GPU. Existing
t_min stays unchanged. Numeric fixtures are small and exactly axis aligned.
"""
import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from exp005_geometric_return_audit import geometric_candidates
from primitive_tie_guard_v1 import resolve_candidates
from exp005_triangle_oracle import scalar
from exp005_self_hit_audit import T_MIN_BU

GAPS = (5e-10, 1e-9, 2e-9, 1e-8)


def fixture(gap):
    gap = scalar(gap)
    if not 0 < gap < 1:
        raise ValueError('positive gap below the distant plane required')
    vertices, faces, objects = [], [], []
    for x, name in ((0., 'departure'), (gap, 'near'), (1., 'far')):
        base = len(vertices)
        vertices.extend([[x, -1., -1.], [x, 1., -1.], [x, 1., 1.], [x, -1., 1.]])
        faces.extend([[base, base+1, base+2], [base, base+2, base+3]])
        objects.extend([name, name])
    return {'vertices': vertices, 'faces': faces, 'object_ids': objects,
            'origin_BU': [0., 0., 0.], 'direction': [1., 0., 0.]}


def compare(gap):
    record = fixture(gap)
    result = geometric_candidates(record)
    state = {'snapshot_sha256': result['geometry_sha256'],
             'primitive_id': 0, 'departure_event': 't'}
    rule = resolve_candidates(snapshot_sha256=result['geometry_sha256'],
        manifest=result['manifest'], candidates=result['candidates'], previous=state)
    selected = rule['selected_primitive']
    if selected is None: raise ValueError('distant control plane must be hit')
    selected_object = record['object_ids'][selected]
    # Independent analytic reference: x=t for ray (t,0,0), near plane x=gap.
    # Fraction is exact for the supplied binary64 input, not its decimal label.
    exact = Fraction(float(gap))
    expected = {'object_id': 'near', 'distance_BU': float(exact),
                'distance_exact_binary64_input': [exact.numerator, exact.denominator]}
    correct = selected_object == expected['object_id'] and rule['minimum_distance_BU'] == float(exact)
    return {'gap_BU': float(exact), 'record': record, 'candidate_query': result,
            'previous': state, 'arbitration': rule, 'selected_object': selected_object,
            'analytic_reference': expected, 'matches_analytic_reference': correct}


def audit():
    rows = [compare(gap) for gap in GAPS]
    if [r['matches_analytic_reference'] for r in rows] != [False, False, True, True]:
        raise ValueError('cutoff reproduction or positive controls changed')
    if any(r['arbitration']['action'] != 'continue' for r in rows):
        raise ValueError('expected component policy to continue after filtered hits')
    return {'scope': 'CPU geometry with zero origin bias; no native V3/GPU/Bpy/fields',
            'fixed_t_min_BU': T_MIN_BU, 'cases': rows,
            'wrong_nearest_count': 2, 'positive_control_count': 2,
            'limitations': ['Component continue is NOT a valid full-scene optical output',
                'Does not certify native runtime or actual Blender float32 geometry',
                'Previous-primitive tie rule cannot see hits removed by t_min',
                'No fix by shrinking epsilon, skipping primitives or relabeling the oracle']}


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--output', type=Path, required=True)
    a = parser.parse_args()
    if a.output.exists(): raise ValueError('new artifact required')
    result = audit()
    root = Path(__file__).parents[1]
    files = [Path(__file__), Path(__file__).with_name('test_exp005_cutoff.py')]
    files += [Path(__file__).with_name(name) for name in
              ('exp005_geometric_return_audit.py', 'exp005_self_hit_audit.py',
               'exp005_primitive_return_audit.py', 'exp005_precision_fixture.py',
               'exp005_triangle_oracle.py')]
    files += [root/'benchmarks/capacity_audit'/name for name in
              ('primitive_tie_guard_v1.py', 'primitive_return_guard_v1.py',
               'frontier_inputs.py', 'gpu_geometry_probe.py')]
    files += [root/'shaders'/name for name in ('exp005_shared_frontier.glsl', 'exp005_nearest_v2.glsl')]
    files += [root.parent/'coordinacion/respuestas/PRECISION-004-CLAUDE.json']
    result['input_code_sha256'] = {str(f): hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
    a.output.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps({'wrong_nearest': 2, 'controls_correct': 2,
        'sha256': hashlib.sha256(a.output.read_bytes()).hexdigest()}))


if __name__ == '__main__': main()
