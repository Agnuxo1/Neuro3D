"""Synthetic float64 close-gap/mode fixtures; NOT reopened Blender geometry."""
import math
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1]/'benchmarks'/'capacity_audit'))
from exp005_peer_ambiguity_audit import plane
from exp005_triangle_oracle import geometry, triangle_hit, add, scale, unit
from nearest_hit_v2 import Candidate, select


def direct(gap=1e-8, angle=0.):
    det = plane(gap, 'det')
    det.update(mode_origin_BU=[gap, 0., 0.], mode_direction=[math.cos(angle), math.sin(angle), 0.])
    return {'schema': 'exp005-readback-v2', 'lambda_BU': .125,
            'objects': {'D': det}, 'undeclared_meshes': [],
            'sources': [{'id': 's', 'position_BU': [0., 0., 0.],
                         'direction': [1., 0., 0.], 'field_reim': [1., 0.]}]}


def reflected(gap=1e-8):
    # Mirror x+y=1 redirects +x to -y; the detector is parallel to input,
    # so the close surface is only encountered AFTER the first reflection.
    result = direct()
    mirror = plane(1., 'mirror')
    mirror['vertices_world_BU'] = [(x-y, y, z) for x, y, z in mirror['vertices_world_BU']]
    det = plane(0., 'det')
    det.update(vertices_world_BU=[(1+y, -gap, z) for _, y, z in det['vertices_world_BU']],
               mode_origin_BU=[1., -gap, 0.], mode_direction=[0., -1., 0.])
    result['objects'] = {'M': mirror, 'D': det}
    return result


def cases():
    yield 'direct_gap', direct(), 0
    yield 'reflected_gap', reflected(), 0
    yield 'direct_far', direct(2.), 0
    yield 'reflected_far', reflected(2.), 0
    yield 'mode_match', direct(2.), 0
    yield 'mode_inside', direct(2., 2e-5), 0
    yield 'mode_mismatch', direct(2., 2e-4), 3
    yield 'mode_reverse', direct(2., math.pi), 3


def query(snapshot, origin, direction, *, bias=0.):
    """CPU specification of shifting semantics + global-minimum selection.

Uses independent triangle intersection; never passes these hits to GPU.
"""
    _, objects = geometry(snapshot); names = tuple(objects)
    direction = unit(direction); shifted = add(origin, scale(direction, bias))
    hits = []
    for index, obj in enumerate(objects.values()):
        for triangle in obj['triangles']:
            hit = triangle_hit(shifted, direction, triangle, 1e-9)
            if hit is not None: hits.append(Candidate(hit[0], index, hit[1]))
    winner, ambiguous = select(hits)
    return None if winner is None else {
        'object': names[winner.object_id], 'distance_BU': winner.distance_BU+bias,
        'normal': winner.normal, 'ambiguous': ambiguous}


def cpu_evidence():
    from exp005_triangle_oracle import trace_scene
    from precision_v3 import terminal_accept, shader_source
    import hashlib
    result = {'scope': 'CPU specification and independent triangle oracle; NO GPU runtime',
              'raw_scope': 'synthetic float64, NOT Blender float32 readback', 'cases': []}
    for label, snapshot, status in cases():
        row = {'label': label, 'snapshot': snapshot, 'expected_runtime_status': status}
        if status:
            try: trace_scene(snapshot, max_rays=4)
            except ValueError as exc:
                if 'arrival direction' not in str(exc): raise
                row['oracle_rejected_mode'] = True
            else: raise ValueError('oracle mode rejection missing')
        else:
            oracle = trace_scene(snapshot, max_rays=4)
            row['oracle'] = {'rays': oracle['rays'], 'length_BU': oracle['paths'][0]['length_BU'],
                             'field_reim': [oracle['fields']['D'].real, oracle['fields']['D'].imag],
                             'power': oracle['powers']['D']}
        if label in ('direct_gap', 'reflected_gap'):
            origin, direction = ((0., 0., 0.), (1., 0., 0.)) if label == 'direct_gap' else ((1., 0., 0.), (0., -1., 0.))
            row['legacy_query_emulated'] = query(snapshot, origin, direction, bias=1e-6)
            row['unshifted_query_spec'] = query(snapshot, origin, direction)
            if row['legacy_query_emulated'] is not None or row['unshifted_query_spec']['object'] != 'D':
                raise ValueError('close-gap adversary did not reproduce')
        if label.startswith('mode_'):
            axis = snapshot['objects']['D']['mode_direction']
            row['legacy_mode_accept_spec'] = terminal_accept((1., 0., 0.), axis, dot_tolerance=1e-6)
            row['strict_mode_accept_spec'] = terminal_accept((1., 0., 0.), axis)
            if row['strict_mode_accept_spec'] != (status == 0): raise ValueError('mode spec mismatch')
        result['cases'].append(row)
    result['composed_shader_sha256'] = hashlib.sha256(shader_source().encode()).hexdigest()
    return result


def main():
    import argparse
    import json
    import hashlib
    p = argparse.ArgumentParser(); p.add_argument('--output', type=Path, required=True); a = p.parse_args()
    if a.output.exists(): raise ValueError('new evidence path required')
    result = cpu_evidence()
    result['fixture_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    a.output.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps({'passed': True, 'cases': len(result['cases']), 'scope': result['scope'],
                      'sha256': hashlib.sha256(a.output.read_bytes()).hexdigest()}))


if __name__ == '__main__': main()
