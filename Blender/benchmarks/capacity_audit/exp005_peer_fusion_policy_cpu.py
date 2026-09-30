"""Read-only peer V2 policy audit against regenerated rational scene fields.

Two sources, mixed wavelengths in both orders, explicit whole-batch rejection.
CPU synthetic only; no CUDA, peer writers, compilation, timing benchmark or
promotion. Numerical failures are retained independently of regression tests.
"""
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import time

from exp005_peer_fusion_bridge_cpu import ROOT, PEER, digest, snapshot
from history_trace_cpu_v1 import trace_scene
from history_fields_cpu_v1 import ideal_fields

VARIANT_SHA = '506b13c9c6bb442d16d9be07b8508a79b01ded9dd4c87c261ac1af83849b426e'
REPLY_SHA = '8114905b9cc501494bd41ca64e79fce3c89d6859598054046465d82ed00771e6'
SMALL = 2.**-17


def scene(lam):
    out = snapshot(lam, 2.**-31)
    out['sources'].append({'id': 's2', 'position_BU': [0., -1., 0.],
                           'direction': [0., 1., 0.], 'field_reim': [.6, .8]})
    return out


def audit():
    start = time.monotonic()
    import torch
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    if torch.cuda.is_initialized(): raise ValueError('CUDA must remain uninitialized')
    reply_path = ROOT/'coordinacion/respuestas/P0-FUSION-BRIDGE-002-CLAUDE.json'
    if digest(reply_path) != REPLY_SHA: raise ValueError('review changed reply before import')
    reply = json.loads(reply_path.read_text(encoding='utf-8'))
    pins = {str(reply_path): REPLY_SHA, str(PEER/'gpu_states_v2.py'): VARIANT_SHA}
    pins.update({str(PEER/k): v for k, v in reply['ack']['libraries_reviewed_unchanged'].items()})
    for key, sha in reply['artifact_sha256'].items():
        pins[str(PEER.parent/key)] = sha
    prior = ROOT/reply['ack']['codex_response']
    task = ROOT/'coordinacion/tareas/P0-FUSION-BRIDGE-002-CLAUDE.md'
    pins[str(prior)] = reply['ack']['sha256']
    pins[str(task)] = reply['ack']['task_input_sha256']
    own = [Path(__file__), ROOT/'Docs/EXP-005-FUSION-POLICY-CPU-2026-09-30.md',
           ROOT/'Blender/tests/test_exp005_peer_fusion_policy_cpu.py',
           ROOT/'Blender/tests/exp005_history_mzi_audit.py']
    own += [ROOT/'Blender/benchmarks/capacity_audit'/n for n in (
        'exp005_peer_fusion_bridge_cpu.py', 'history_trace_cpu_v1.py',
        'history_fields_cpu_v1.py', 'history_lengths_cpu_v1.py',
        'history_lineage_cpu_v2.py', 'history_completeness_cpu_v1.py',
        'frontier_inputs.py', 'gpu_geometry_probe.py')]
    pins.update({str(p): digest(p) for p in own})
    if any(digest(p) != s for p, s in pins.items()): raise ValueError('input SHA mismatch')
    spec = importlib.util.spec_from_file_location('audited_gpu_states_v2', PEER/'gpu_states_v2.py')
    gs = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gs)  # Reviewed pure library only, never p02_bridge writer.
    refs = {}
    for lam in (SMALL, .125):
        sn = scene(lam)
        traversed = trace_scene(sn)
        reference = ideal_fields(sn, traversed['records'], coherence_groups={'s': 's', 's2': 's2'})
        refs[lam] = {'snapshot': sn, 'records': traversed['records'], 'reference': reference}
    cases = []
    # Explicit policies; legacy default remains a failing diagnostic control.
    for lams in ([SMALL, .125], [.125, SMALL], [.125]):
        for policy in ('fixed', 'auto_per_scene', 'auto_strict_per_scene'):
            batch = gs.Batch([refs[l]['snapshot'] for l in lams], dev='cpu')
            calls = [0]
            nearest = batch.nearest
            def counted(*args):
                calls[0] += 1
                return nearest(*args)
            batch.nearest = counted
            row = {'lambdas_BU': lams, 'policy_name': policy}
            try:
                run = gs.trace(batch, max_levels=16, policy=policy)
            except gs.TraceError as exc:
                row.update(status='rejected', reason=str(exc), nearest_calls=calls[0], fields_emitted=False)
                cases.append(row)
                continue
            ports = [p for p, ob in refs[lams[0]]['snapshot']['objects'].items()
                     if ob['kind'] in ('det', 'escape')]
            errors = []
            for index, lam in enumerate(lams):
                ref = refs[lam]
                per_port = {}
                for pi, p in enumerate(ports):
                    values = []
                    source_errors = []
                    expected_values = []
                    for si, src in enumerate(ref['snapshot']['sources']):
                        value = complex(run['U'][index, pi, si])*complex(*src['field_reim'])
                        expected = complex(*ref['reference']['ports'][p]['groups'][src['id']]['field_reim'])
                        values.append(value); expected_values.append(expected)
                        source_errors.append(abs(value-expected))
                    per_port[p] = {'per_source_field_error': source_errors,
                                   'fields_reim': [[z.real, z.imag] for z in values],
                                   'coherent_total_field_error': abs(sum(values)-sum(expected_values)),
                                   'incoherent_power_error': abs(sum(abs(z)**2 for z in values)-
                                                                sum(abs(z)**2 for z in expected_values))}
                maximum = max(e for data in per_port.values() for e in data['per_source_field_error'])
                errors.append({'lambda_BU': lam, 'ports': per_port, 'max_source_field_error': maximum,
                               'global_gate_1e4': maximum <= 1e-4, 'strict_gate_1e8': maximum <= 1e-8})
            row.update(status='accepted', nearest_calls=calls[0], fields_emitted=True,
                       policy=run['policy'], states=run['states'], casts=run['casts'], errors=errors)
            cases.append(row)
    if torch.cuda.is_initialized(): raise ValueError('CUDA unexpectedly initialized')
    if any(digest(p) != s for p, s in pins.items()): raise ValueError('input changed during audit')
    return {'task_id': 'P0-FUSION-POLICY-003-CODEX',
            'timestamp_utc': datetime.now(timezone.utc).isoformat(), 'seconds': time.monotonic()-start,
            'threads': torch.get_num_threads(), 'device': 'cpu', 'torch': torch.__version__,
            'code_sha256': pins, 'references': list(refs.values()), 'cases': cases,
            'CUDA_initialized': False, 'GPU_executed': False, 'Bpy_executed': False,
            'native_promotion_allowed': False, 'JEV_provenance_verified': False, 'no_jev_aval': True,
            'scope': 'two synthetic represented CPU MZIs, two sources, nine explicit policy/batch controls; no CUDA/RT/general bound/speed claim'}


if __name__ == '__main__': print(json.dumps(audit(), indent=2, allow_nan=False))
