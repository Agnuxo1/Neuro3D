"""Independent tiny CPU audit of peer fusion -> device-state bridge.

Read-only pure peer libraries, never their experiment writers. Five dyadic
synthetic MZIs, regenerated exact CPU histories and rational phase reference.
No CUDA/Blender/RT, no peer edits, no runtime promotion or speed benchmark.
"""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
PEER = Path('D:/PROJECTS/.cognition/neuro3d/nebulatrace')
sys.path.insert(0, str(ROOT/'Blender/tests'))
from exp005_history_mzi_audit import fixture
from history_trace_cpu_v1 import trace_scene
from history_fields_cpu_v1 import ideal_fields

PINS = {'statefuse.py': 'a5d40e68f56c654623d4dd58ea9d7cb86fb2f53cd61212a54f6569051d5256b0',
        'gpu_states.py': 'a39cc506dad29de8e87bc37e875504f5d0c6d5eff1ab228a48c83ac5bcf0a12f'}


def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def peer_module(name):
    path = PEER/name
    if digest(path) != PINS[name]: raise ValueError('peer input changed; review new SHA first')
    spec = importlib.util.spec_from_file_location('audited_'+path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # Reviewed import-only library, no writer/main harness.
    return module


def snapshot(wavelength, displacement):
    scene, _ = fixture(0., 0.)
    scene = deepcopy(scene); scene['lambda_BU'] = wavelength
    vertices = scene['objects']['MB']['vertices_world_BU']
    for vertex in vertices: vertex[1] += displacement
    return scene


def cases():
    return [('exact_control', 2.**-17, 0.),
            ('subquant_dyadic', 2.**-17, 2.**-31),
            ('same_shift_long_lambda', .125, 2.**-31),
            ('above_quant_sham', 2.**-17, 2.**-27),
            ('same_shift_larger_lambda', 2.**-10, 2.**-31)]


def audit():
    start = time.monotonic()
    import torch
    torch.set_num_threads(1); torch.set_num_interop_threads(1)
    if torch.cuda.is_initialized(): raise ValueError('CPU-only audit requires uninitialized CUDA')
    sf = peer_module('statefuse.py'); gs = peer_module('gpu_states.py')
    own_paths = [Path(__file__), ROOT/'Docs/EXP-005-FUSION-BRIDGE-CPU-2026-09-30.md']
    own_paths += [ROOT/'Blender/tests/exp005_history_mzi_audit.py']
    own_paths += [ROOT/'Blender/benchmarks/capacity_audit'/name for name in (
        'history_trace_cpu_v1.py', 'history_fields_cpu_v1.py', 'history_lengths_cpu_v1.py',
        'history_lineage_cpu_v2.py', 'history_completeness_cpu_v1.py', 'frontier_inputs.py',
        'gpu_geometry_probe.py')]
    own_pins = {str(p): digest(p) for p in own_paths}
    reports = {}; peer_pins = {str(PEER/k): v for k, v in PINS.items()}
    for name in ('P0-1-FUSION-CLAUDE.json', 'P0-3-SCENE-STATES-CLAUDE.json', 'P0-4-RT-EQUAL-CLAUDE.json'):
        path = ROOT/'coordinacion/respuestas'/name; d = json.loads(path.read_text(encoding='utf-8'))
        peer_pins[str(path)] = digest(path)
        for key, value in d['artifact_sha256'].items():
            artifact = Path(d['artifacts'][key])
            if digest(artifact) != value: raise ValueError('retained peer artifact changed')
            peer_pins[str(artifact)] = value
        reports[d['task_id']] = {'status': d['status'], 'timestamp_utc': d['timestamp_utc'],
                                'GPU_replayed': False, 'JEV_provenance_verified': False}
    outputs = []
    for label, lam, shift in cases():
        scene = snapshot(lam, shift)
        traversed = trace_scene(scene)
        oracle = ideal_fields(scene, traversed['records'], coherence_groups={'s': 'g'})
        expected = {port: complex(*data['groups']['g']['field_reim'])
                    for port, data in oracle['ports'].items()}
        unfused = sf.transfer(scene, fuse=False, max_states=64)
        default = sf.transfer(scene, max_states=64)
        automatic = sf.transfer(scene, quant='auto', max_states=64)
        device_cpu = gs.trace(gs.Batch([scene], dev='cpu'), max_levels=16)
        # Diagnostic scalar override ONLY: not an implementation of per-scene
        # adaptive quantization for a mixed-wavelength GPU batch.
        q = min(1e-9, 1e-6*lam/(math.tau*4))
        device_scaled = gs.trace(gs.Batch([scene], dev='cpu'), quant=q, dquant=q, max_levels=16)
        entries = {}
        for name, run in (('unfused', unfused), ('CPU_default', default),
                          ('CPU_auto', automatic), ('torch_CPU_default', device_cpu),
                          ('torch_CPU_scaled_diagnostic', device_scaled)):
            U = run['U'][0] if name.startswith('torch') else run['U']
            values = {p: complex(U[i, 0]) for i, p in enumerate(unfused['ports'])}
            error = max(abs(values[p]-expected[p]) for p in expected)
            entries[name] = {'states': run['states'], 'casts': run['casts'],
                             'field_error_vs_independent_CPU': error,
                             'field_gate_1e4_passed': error <= 1e-4,
                             'fields_reim': {p: [z.real, z.imag] for p, z in values.items()}}
        outputs.append({'label': label, 'wavelength_BU': lam, 'mirror_shift_BU': shift,
                        'snapshot': scene, 'records': traversed['records'],
                        'independent_reference': oracle, 'scaled_quant': q, 'backends': entries})
    if torch.cuda.is_initialized(): raise ValueError('CUDA unexpectedly initialized')
    all_pins = {**own_pins, **peer_pins}
    if any(digest(p) != v for p, v in all_pins.items()): raise ValueError('input changed during audit')
    return {'task_id': 'P0-FUSION-BRIDGE-001-CODEX', 'timestamp_utc': datetime.now(timezone.utc).isoformat(),
            'seconds': time.monotonic()-start, 'torch': torch.__version__,
            'threads': torch.get_num_threads(), 'device': 'cpu', 'CUDA_initialized': False,
            'code_sha256': all_pins, 'received_peer_reports': reports, 'cases': outputs,
            'native_promotion_allowed': False, 'GPU_executed': False, 'Bpy_executed': False,
            'JEV_provenance_verified': False, 'no_jev_aval': True,
            'scope': 'five dyadic CPU synthetic MZIs; independent regenerated histories/ideal fields, no CUDA/RT/speed claim'}


if __name__ == '__main__': print(json.dumps(audit(), indent=2, allow_nan=False))
