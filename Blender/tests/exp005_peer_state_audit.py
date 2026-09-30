"""Bounded CPU-only audit of retained peer state tracer, never peer writers.

Invokes Batch(dev='cpu') and trace on four triangles/two scenes. Matrix U here
is an explicitly compiled peer output; not a Blender/GPU inference claim.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from exp005_peer_ambiguity_audit import plane
from exp005_triangle_oracle import trace_scene

FIELD_TOL = 1e-4


def fixture(wavelength):
    return {'schema': 'exp005-readback-v2', 'lambda_BU': wavelength,
            'objects': {'M': plane(1., 'mirror'), 'D': plane(-1., 'det')},
            'undeclared_meshes': [], 'sources': [{'id': 's', 'position_BU': [0., 0., 0.],
                'direction': [1., 0., 0.], 'field_reim': [1., 0.]}]}


def evaluate_fields(scenes, fields):
    if len(scenes) != len(fields):
        raise ValueError('one complex field per retained scene required')
    rows = []
    for scene, pair in zip(scenes, fields):
        if len(pair) != 2 or not all(isinstance(x, (int, float)) and math.isfinite(x) for x in pair):
            raise ValueError('finite complete complex readback required')
        reference = trace_scene(scene, max_rays=4)['fields']['D']
        observed = complex(*pair)
        rows.append({'lambda_BU': scene['lambda_BU'], 'field_reim': pair,
                     'reference_reim': [reference.real, reference.imag],
                     'complex_error': abs(observed-reference),
                     'power_error': abs(abs(observed)**2-abs(reference)**2)})
    return rows


def audit(peer_path):
    import torch
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    before = hashlib.sha256(peer_path.read_bytes()).hexdigest()
    spec = importlib.util.spec_from_file_location('retained_state_peer', peer_path)
    peer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(peer)
    rows = []
    for label, wavelengths in (('uniform_control', (.125, .125)),
                               ('mixed_forward', (.125, .14)), ('mixed_reverse', (.14, .125))):
        scenes = [fixture(w) for w in wavelengths]
        preserved = copy.deepcopy(scenes)
        try:
            batch = peer.Batch(scenes, dev='cpu')
            result = peer.trace(batch, max_levels=8)
        except (ValueError, peer.TraceError) as exc:
            row = {'case': label, 'rejected': True, 'error': str(exc), 'inputs': scenes}
        else:
            fields = [[float(x.real), float(x.imag)] for x in result['U'][:, 0, 0].tolist()]
            comparisons = evaluate_fields(scenes, fields)
            row = {'case': label, 'rejected': False, 'inputs': scenes, 'comparisons': comparisons,
                   'stored_lambda_BU': getattr(batch, 'lam', None),
                   'wave_numbers': batch.k.tolist() if isinstance(batch.k, torch.Tensor) else batch.k,
                   'states': result['states'],
                   'max_complex_error': max(r['complex_error'] for r in comparisons)}
        if scenes != preserved:
            raise ValueError('peer changed caller inputs')
        rows.append(row)
    if rows[0]['rejected'] or rows[0]['max_complex_error'] > FIELD_TOL:
        raise ValueError('same-wavelength positive control failed')
    sc = torch.tensor([0, 0], dtype=torch.int64)
    points = torch.tensor([[5., 0., 0.], [5.+.4e-9, 0., 0.]], dtype=torch.float64)
    directions = torch.tensor([[1., 0., 0.], [1., 0., 0.]], dtype=torch.float64)
    exact_quantized_keys = hasattr(peer, '_qkey')
    keys = (peer._hash(peer._qkey(sc, points, directions, 1e-9, 1e-9))
            if exact_quantized_keys else peer._hash(sc, points, directions, 1e-9, 1e-9)).tolist()
    collision_control = {'available': exact_quantized_keys, 'rejected': False}
    if exact_quantized_keys:
        original_hash = peer._hash
        # Mutant only in this imported module/process, never peer source files.
        peer._hash = lambda qk: torch.zeros(qk.shape[0], dtype=torch.int64, device=qk.device)
        try:
            peer.trace(peer.Batch([fixture(.125), fixture(.14)], dev='cpu'), max_levels=8)
        except peer.TraceError as exc:
            collision_control.update(rejected='colision' in str(exc), error=str(exc))
        finally:
            peer._hash = original_hash
        if not collision_control['rejected']:
            raise ValueError('different quantized keys sharing hash were not rejected')
    delta = float(points[1, 0]-points[0, 0])
    # Analytic future segment to a common phase reference, NOT a full trace:
    # distinct origins imply a different path phase at equal local amplitude.
    phase_delta = 2*math.pi*delta/1e-6
    field_delta = 2*abs(math.sin(phase_delta/2))
    after = hashlib.sha256(peer_path.read_bytes()).hexdigest()
    if before != after or torch.cuda.is_initialized():
        raise ValueError('peer source changed or CUDA initialized during CPU audit')
    return {'scope': 'CPU execution of retained peer torch code plus independent triangular oracle; no GPU/Blender',
        'peer_sha256': before, 'field_threshold': FIELD_TOL, 'torch_version': torch.__version__,
        'cpu_threads': 1, 'cuda_initialized': False, 'cases': rows,
        'forced_hash_collision_control': collision_control,
        'mixed_lambda_unsafe': any(not r['rejected'] and r['max_complex_error'] > FIELD_TOL for r in rows[1:]),
        'quantization_alias': {'keys': keys, 'same_key': keys[0] == keys[1],
            'distinct_positions': bool(delta != 0), 'position_delta_BU': delta,
            'illustrative_lambda_BU': 1e-6, 'analytic_future_field_delta': field_delta,
            'scope': 'direct key collision from quantization; analytic phase example, NOT full-network error'},
        'required': 'uniform lambda rejection or per-scene k; exact full-state equality, no hash-only fusion'}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--peer', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    if a.output.exists():
        raise ValueError('new own evidence required')
    result = audit(a.peer)
    result['auditor_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    a.output.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k != 'cases'}, indent=2))
    for row in result['cases']:
        print(json.dumps({k: v for k, v in row.items() if k not in ('inputs', 'comparisons')}))


if __name__ == '__main__': main()
