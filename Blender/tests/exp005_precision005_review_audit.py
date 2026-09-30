"""Own CPU replay of PRECISION-005 evidence; never executes peer writers."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
from exp005_precision_fixture import direct
from exp005_precision_transport_audit import transported, FIELD_TOL
from local_frame_v1 import local_frame
from exp005_triangle_oracle import trace_scene
from exp005_self_hit_audit import query

ROOT = Path(__file__).parents[2]
RESPONSE = ROOT/'coordinacion/respuestas/PRECISION-005-CLAUDE.json'


def verified_peer():
    raw = RESPONSE.read_bytes(); peer = json.loads(raw)
    if peer['task_id'] != 'PRECISION-005' or peer['status'] != 'complete':
        raise ValueError('complete peer response required')
    hashes = {}
    for name, sha in peer['input_sha256'].items():
        path = ROOT/name
        if hashlib.sha256(path.read_bytes()).hexdigest() != sha: raise ValueError('peer input changed: '+name)
        hashes[str(path)] = sha
    for name, sha in peer['artifacts']['artifact_sha256'].items():
        path = Path(peer['artifacts'][name])
        if hashlib.sha256(path.read_bytes()).hexdigest() != sha: raise ValueError('peer artifact changed: '+name)
        hashes[str(path)] = sha
    return peer, hashes, hashlib.sha256(raw).hexdigest()


def clusters(separation, wavelength):
    scene = direct(.7123456789012345)
    detector = copy.deepcopy(scene['objects']['D'])
    def shifted(point): return [point[0]+separation, point[1], point[2]]
    detector['vertices_world_BU'] = [shifted(p) for p in detector['vertices_world_BU']]
    detector['mode_origin_BU'] = shifted(detector['mode_origin_BU'])
    source = copy.deepcopy(scene['sources'][0]); source['id'] = 's2'
    source['position_BU'] = shifted(source['position_BU'])
    scene['objects']['D2'] = detector; scene['sources'].append(source)
    scene['lambda_BU'] = wavelength
    return scene


def frame_result(scene, ideal):
    local, meta = local_frame(scene); decoded, input_error = transported(local)
    results = [trace_scene(s, max_rays=8)['fields'] for s in (scene, local, decoded)]
    return {'metadata': meta, 'input_error_BU': input_error,
        'fields_reim': [{k: [v.real, v.imag] for k, v in f.items()} for f in results],
        'world_vs_ideal': {k: abs(results[0][k]-ideal[k]) for k in ideal},
        'local_vs_ideal': {k: abs(results[1][k]-ideal[k]) for k in ideal},
        'abi_local_vs_ideal': {k: abs(results[2][k]-ideal[k]) for k in ideal},
        'abi_vs_raw_world': {k: abs(results[2][k]-results[0][k]) for k in ideal}}


def record(row):
    return {'vertices': row['vertices'], 'faces': row['triangles'],
        'origin_BU': row['source_origin'], 'direction': row['incident_direction']}


def audit():
    peer, hashes, sha = verified_peer()
    reference = json.loads(Path(peer['artifacts']['a_frames.json']).read_bytes())
    frames = []
    for saved in reference['rows']:
        wavelength, separation = saved['lambda_BU'], saved['sep_BU']
        scene = clusters(separation, wavelength)
        ideal = trace_scene(clusters(3., wavelength), max_rays=8)['fields']
        own = frame_result(scene, ideal)
        deltas = {n: {k: abs(own[n][k]-saved[n][k]) for k in saved[n]}
            for n in ('world_vs_ideal', 'local_vs_ideal', 'abi_local_vs_ideal')}
        frames.append({'lambda_BU': wavelength, 'separation_BU': separation,
            'scene': scene, 'own': own, 'peer_numeric_error_delta': deltas})
    selfhit = json.loads(Path(peer['artifacts']['b_selfhit_retained.json']).read_bytes())
    queries = []
    for label in ('failing', 'control'):
        source = selfhit[label]
        for local in (False, True):
            own = query(record(source), local=local)
            peer_row = source if not local else selfhit['failing_in_local_frame(source origin subtracted)' if label == 'failing' else 'control_in_local_frame']
            peer_same = next((h[1] for h in peer_row['self_hits'] if h[0] == source['hit_tri']), None)
            queries.append({'label': label, 'frame': 'local' if local else 'world',
                'record': record(source), 'own': own,
                'peer_first_t_delta_BU': abs(own['first_distance_BU']-source['t']),
                'peer_same_triangle_t_BU': peer_same,
                'peer_same_triangle_t_delta_BU': None if peer_same is None or own['same_triangle_self_hit_BU'] is None
                    else abs(peer_same-own['same_triangle_self_hit_BU'])})
    folded = json.loads(Path(peer['artifacts']['d_folded.json']).read_bytes())['folded_control']
    folded_query = query(record(folded))
    if folded_query['first_triangle'] != 0 or [x['triangle'] for x in folded_query['other_triangle_hits_not_classified']] != [1]:
        raise ValueError('folded other-face control drift')
    order_scene = clusters(999900.321987654, 1e-6)
    ideal = trace_scene(clusters(3., 1e-6), max_rays=8)['fields']
    forward = frame_result(order_scene, ideal)
    order_scene['sources'].reverse(); reverse = frame_result(order_scene, ideal)
    return {'scope': 'Own CPU synthetic replay, NO peer writers/GPU/Bpy/JEV',
        'response_sha256': sha, 'verified_peer_sha256': hashes, 'frames': frames,
        'selfhit_queries': queries, 'folded_query': folded_query,
        'source_order': {'forward': forward, 'reverse': reverse},
        'field_tolerance_unchanged': FIELD_TOL,
        'limitations': ['4 frame cases and 4 retained selfhit queries, NOT peer 400-sample rate validation',
            'Comparison with ideal unrounded construction is distinct from ABI-vs-raw error',
            'Source order tested CPU only; no native phase or performance certification',
            'Peer exclusion/domain proposals are NOT adopted or implemented',
            'NumPy dot/norm and own scalar sum/hypot expression trees differ; self-hit distance parity is NOT assumed',
            'Common scalar oracle used; not independent Maxwell or physical optics validation']}


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists(): raise ValueError('new evidence required')
    result = audit()
    files = [Path(__file__), Path(__file__).with_name('test_exp005_precision005_review.py')]
    files += [Path(__file__).with_name(n) for n in ('exp005_triangle_oracle.py', 'exp005_self_hit_audit.py',
        'exp005_precision_fixture.py', 'exp005_precision_transport_audit.py', 'exp005_blender_gpu.py')]
    files += [ROOT/'Blender/benchmarks/capacity_audit'/n for n in ('local_frame_v1.py', 'frontier_inputs.py')]
    result['own_code_sha256'] = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    with args.output.open('x', encoding='utf-8') as output:
        output.write(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps({'frames': len(result['frames']), 'selfhit_queries': len(result['selfhit_queries']),
        'peer_hashes': len(result['verified_peer_sha256']),
        'sha256': hashlib.sha256(args.output.read_bytes()).hexdigest()}))


if __name__ == '__main__': main()
