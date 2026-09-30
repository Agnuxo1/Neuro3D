"""Prospective native GPU precision gate; CPU fixtures never become hit inputs."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parents[1]/'benchmarks'/'capacity_audit'))
import precision_v3 as variant
import nearest_hit_v2 as prior
import shared_frontier_gpu as shared
from exp005_precision_fixture import cases
from exp005_nearest_runtime import raw_cases, require_status
from exp005_chain_runtime import readback, source_fields, serialize, validate_roundtrip
from exp005_chain_fixture import chain_fixture, set_fields
from exp005_paired_cost import plan, check
from exp005_shared_runtime import INPUT_REPORT_SHA, shared_parity
from exp005_resident_v2 import configure_private_exit


def probes():
    for label, snapshot, status in raw_cases(): yield 'nearest/'+label, snapshot, status
    for label, snapshot, status in cases(): yield 'precision/'+label, snapshot, status


def check_precision(row):
    native, expected = row['gpu'], row['expected_status']
    require_status(native, expected)
    if expected: return None, None
    metrics, oracle = shared_parity(row['snapshot'], native)
    if row['label'] in ('precision/direct_gap', 'precision/reflected_gap'):
        expected_length = 1e-8 if row['label'].endswith('/direct_gap') else 1+1e-8
        ledger = native['ports']['D']['ledger']
        if len(ledger) != 1 or abs(ledger[0]['effective_length_BU']-expected_length) > 1e-7:
            raise ValueError('close-gap path count/length failed')
    return metrics, oracle


def main():
    import bpy
    import gpu
    from exp005_blender_gpu import schedule_exit
    p = argparse.ArgumentParser(); p.add_argument('--evidence', type=Path, required=True)
    p.add_argument('--report', type=Path, required=True); p.add_argument('--authorized-by-user', action='store_true')
    a = p.parse_args(sys.argv[sys.argv.index('--')+1:])
    if not a.authorized_by_user or a.report.exists(): raise ValueError('fresh authorized output required')
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    manifest = a.evidence.with_suffix('.json')
    if sha(manifest) != INPUT_REPORT_SHA: raise ValueError('immutable input manifest changed')
    hashes = {row['file']: row['sha256'] for row in json.loads(manifest.read_text())['scenes']}
    if len(hashes) != 12 or any(sha(a.evidence/n) != h for n, h in hashes.items()):
        raise ValueError('frozen scene hashes changed')
    root = Path(__file__).parents[2]
    # Include transitive numerical helpers explicitly; no historical consumer edits.
    deps = [Path(__file__), Path(variant.__file__), Path(prior.__file__), prior.BASE, prior.PART,
            Path(shared.__file__)]
    deps += [Path(shared.__file__).with_name(n) for n in ('frontier_gpu.py', 'frontier_inputs.py', 'gpu_geometry_probe.py')]
    deps += [Path(__file__).with_name(n) for n in ('exp005_precision_fixture.py', 'exp005_nearest_runtime.py',
        'exp005_chain_runtime.py', 'exp005_chain_fixture.py', 'exp005_paired_cost.py', 'exp005_shared_runtime.py',
        'exp005_frontier_runtime.py', 'exp005_triangle_oracle.py', 'exp005_scene_readback.py',
        'exp005_mode_gate.py', 'exp005_blender_gpu.py', 'exp005_resident_v2.py', 'exp005_resident_runtime.py',
        'exp005_peer_ambiguity_audit.py')]
    code = {str(path.relative_to(root)): sha(path) for path in deps}
    report = {'passed': False, 'scope': 'native scalar ALU raw-scene GPU; NOT RT/BVH/Maxwell/speedup',
        'raw_scope': '29 synthetic float64 triangle cases, NOT Blender float32 geometry',
        'real_scope': 'four frozen Blender K3/K4 evaluated readbacks',
        'settings': configure_private_exit(bpy), 'input_scene_sha256': hashes, 'code_sha256': code,
        'composed_shader_sha256': hashlib.sha256(variant.shader_source().encode()).hexdigest(),
        'prior_composed_shader_sha256': hashlib.sha256(prior.shader_source().encode()).hexdigest(),
        'blender_version': bpy.app.version_string, 'renderer': gpu.platform.renderer_get(),
        'backend': gpu.platform.backend_type_get(), 'raw_cases': [], 'legacy_precision': [], 'real_cases': [],
        'thresholds': {'field_ledger': 1e-4, 'power_balance': 2e-4, 'length_BU': 1e-5,
                       'gap_ledger_length_BU': 1e-7, 't_min_BU': 1e-9, 'terminal_dot_tolerance': 1e-9}}
    shaders = {}
    try:
        if 'NVIDIA' not in gpu.platform.vendor_get().upper(): raise ValueError('NVIDIA context required')
        shaders = {'V3': variant.native_shader(gpu), 'V2': prior.native_shader(gpu)}
        regressions = {'precision/direct_gap': 1, 'precision/reflected_gap': 1, 'precision/mode_mismatch': 0}
        for label, snapshot, expected in probes():
            native, elapsed = shared.dispatch(gpu, shaders['V3'], snapshot)
            row = {'label': label, 'snapshot': snapshot, 'expected_status': expected,
                   'gpu': native, 'dispatch_sync_readback_ms': elapsed}
            report['raw_cases'].append(row)  # Keep failing readback too.
            metrics, oracle = check_precision(row)
            if metrics is not None: row.update(metrics=metrics, oracle=serialize(oracle))
            if label in regressions:
                old, old_ms = shared.dispatch(gpu, shaders['V2'], snapshot)
                report['legacy_precision'].append({'label': label, 'gpu': old, 'dispatch_sync_readback_ms': old_ms})
                if old['work']['status'] != regressions[label]: raise ValueError('legacy precision failure not reproduced')
                if bool(old['valid']) != (regressions[label] == 0): raise ValueError('legacy flag mismatch')
        for cells, label, amps in plan():
            bpy.ops.wm.open_mainfile(filepath=str(a.evidence/f'K{cells}_base.blend'))
            sc = bpy.context.scene; original = readback(bpy, sc)
            retained = json.loads((a.evidence/f'K{cells}_base_snapshot.json').read_text())
            validate_roundtrip(chain_fixture(cells), retained, original)
            expected = copy.deepcopy(original); set_fields(expected, amps)
            source_fields(sc, amps); snapshot = readback(bpy, sc)
            if snapshot != expected: raise ValueError('evaluated scene differs from declared source change')
            native, elapsed = shared.dispatch(gpu, shaders['V3'], snapshot, mode_cap=5)
            row = {'cells': cells, 'input': label, 'snapshot': snapshot, 'gpu': native,
                   'dispatch_sync_readback_ms': elapsed}
            report['real_cases'].append(row)
            metrics, oracle = check(snapshot, native, 'shared', cells, amps)
            row.update(metrics=metrics, oracle=serialize(oracle))
        if (len(report['raw_cases']), len(report['legacy_precision']), len(report['real_cases'])) != (29, 3, 4):
            raise ValueError('all 36 preregistered dispatches required')
        if any(sha(a.evidence/n) != h for n, h in hashes.items()): raise ValueError('frozen scenes changed')
        if any(sha(root/n) != h for n, h in code.items()): raise ValueError('code changed during run')
        report['passed'] = True
        print('EXP005_PRECISION_V3_NATIVE_PASS', flush=True)
    except Exception as exc:
        report['error'] = f'{type(exc).__name__}: {exc}'
        raise
    finally:
        a.report.write_text(json.dumps(report, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    shaders.clear()
    import gc
    gc.collect(); schedule_exit(bpy)


if __name__ == '__main__': main()
