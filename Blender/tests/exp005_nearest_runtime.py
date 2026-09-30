"""Frozen nearest V2 GPU gate: synthetic raw triangles + real reopened scenes.

Synthetic 1e-9-scale planes are NOT claimed to survive Blender mesh float32.
No CPU impacts/rays/frontier supplied; native shaders discover raw-scene paths.
"""
import argparse
import copy
import hashlib
import itertools
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parents[1]/'benchmarks'/'capacity_audit'))
import nearest_hit_v2 as variant
import shared_frontier_gpu as legacy
from exp005_peer_ambiguity_audit import plane
from exp005_chain_runtime import readback, source_fields, serialize, validate_roundtrip
from exp005_chain_fixture import chain_fixture, set_fields
from exp005_shared_runtime import INPUT_REPORT_SHA, shared_parity
from exp005_paired_cost import plan, check
from exp005_resident_v2 import configure_private_exit


def scene(objects):
    return {'schema': 'exp005-readback-v2', 'lambda_BU': .125,
        'objects': {**objects, 'D': plane(-1., 'det')}, 'undeclared_meshes': [],
        'sources': [{'id': 's', 'position_BU': [0., 0., 0.], 'direction': [1., 0., 0.],
                     'field_reim': [1., 0.]}]}


def raw_cases():
    for order in itertools.permutations('ABC'):
        offset = {'A': 0., 'B': -.9e-9, 'C': -1.8e-9}
        yield 'CE3_'+''.join(order), scene({n: plane(5.+offset[n], 'mirror') for n in order}), 2
    for order in itertools.permutations('ABC'):
        x = {'A': 5., 'B': 5.+.5e-9, 'C': 4.}
        yield 'far_tie_'+''.join(order), scene({n: plane(x[n], 'mirror') for n in order}), 0
    for reverse in (False, True):
        record = plane(5., 'mirror')
        if reverse: record['faces'] = [tuple(reversed(f)) for f in record['faces']]
        yield 'coplanar_'+str(reverse), scene({'M': record}), 0
    yield 'miss', scene({}), 1
    for order in itertools.permutations((0., -4e-5, 4e-5)):
        vertices, faces = [], []
        for slope in order:
            obj = plane(5., 'mirror'); start = len(vertices)
            vertices.extend((x+slope*y, y, z) for x, y, z in obj['vertices_world_BU'])
            faces.extend(tuple(start+i for i in face) for face in obj['faces'])
        yield 'normal_tie_'+str(order), scene({'M': {'kind': 'mirror', 'phase_rad': 0.,
            'vertices_world_BU': vertices, 'faces': faces}}), 2


def require_status(native, expected):
    if native['work']['status'] != expected:
        raise ValueError('specific nearest GPU status missing')
    if expected:
        if native['valid'] or native['ports'] or native['errors'] != {'D': legacy.ERRORS[expected]}:
            raise ValueError('all partial fields must fail closed')
        if native['work']['total_casts'] != 1 or native['work']['total_terminal_paths'] != 0:
            raise ValueError('expected abort on first geometric query')
    elif not native['valid']:
        raise ValueError('valid geometry falsely rejected')


def main():
    import bpy
    import gpu
    from exp005_blender_gpu import schedule_exit
    p = argparse.ArgumentParser()
    p.add_argument('--evidence', type=Path, required=True)
    p.add_argument('--report', type=Path, required=True)
    p.add_argument('--authorized-by-user', action='store_true')
    a = p.parse_args(sys.argv[sys.argv.index('--')+1:])
    if not a.authorized_by_user or a.report.exists(): raise ValueError('new authorized evidence required')
    root = Path(__file__).parents[2]; sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    manifest = a.evidence.with_suffix('.json')
    if sha(manifest) != INPUT_REPORT_SHA: raise ValueError('immutable input manifest changed')
    hashes = {row['file']: row['sha256'] for row in json.loads(manifest.read_text())['scenes']}
    if len(hashes) != 12 or any(sha(a.evidence/n) != h for n, h in hashes.items()):
        raise ValueError('frozen scene hashes changed')
    dependencies = [Path(__file__), Path(variant.__file__), variant.BASE, variant.PART,
        Path(legacy.__file__), Path(legacy.__file__).with_name('frontier_gpu.py'),
        Path(legacy.__file__).with_name('frontier_inputs.py'), Path(legacy.__file__).with_name('gpu_geometry_probe.py')]
    dependencies += [Path(__file__).with_name(n) for n in ('exp005_shared_runtime.py',
        'exp005_frontier_runtime.py', 'exp005_triangle_oracle.py', 'exp005_chain_runtime.py',
        'exp005_chain_fixture.py', 'exp005_paired_cost.py', 'exp005_scene_readback.py',
        'exp005_mode_gate.py', 'exp005_blender_gpu.py', 'exp005_resident_v2.py', 'exp005_resident_runtime.py',
        'exp005_peer_ambiguity_audit.py')]
    code = {str(path.relative_to(root)): sha(path) for path in dependencies}
    report = {'passed': False, 'scope': 'native scalar ALU GPU in Blender; NO RT/BVH/generalization/speed advantage',
        'raw_scope': 'synthetic float64 raw-scene adversaries, NOT Blender mesh readbacks',
        'real_scope': 'four evaluations of frozen K3/K4 Blender scenes reopened read-only',
        'settings': configure_private_exit(bpy), 'input_scene_sha256': hashes,
        'code_sha256': code, 'composed_shader_sha256': hashlib.sha256(variant.shader_source().encode()).hexdigest(),
        'blender_version': bpy.app.version_string, 'renderer': gpu.platform.renderer_get(),
        'backend': gpu.platform.backend_type_get(), 'raw_cases': [], 'legacy_CE3': [], 'real_cases': [],
        'thresholds': {'field_ledger': 1e-4, 'power_balance': 2e-4, 'length_BU': 1e-5}}
    shaders = {}
    try:
        if 'NVIDIA' not in gpu.platform.vendor_get().upper(): raise ValueError('NVIDIA context required')
        shaders = {'V2': variant.native_shader(gpu), 'V1': legacy.native_shader(gpu)}
        for label, snapshot, expected in raw_cases():
            native, elapsed = legacy.dispatch(gpu, shaders['V2'], snapshot)
            require_status(native, expected)
            row = {'label': label, 'snapshot': snapshot, 'expected_status': expected,
                   'gpu': native, 'dispatch_sync_readback_ms': elapsed}
            if not expected:
                row['metrics'], oracle = shared_parity(snapshot, native)
                row['oracle'] = serialize(oracle)
            report['raw_cases'].append(row)
            if label.startswith('CE3_'):
                old, old_ms = legacy.dispatch(gpu, shaders['V1'], snapshot)
                report['legacy_CE3'].append({'label': label, 'gpu': old, 'dispatch_sync_readback_ms': old_ms})
        # Historical bug must be observed, not inferred from a shader screenshot.
        if sum(row['gpu']['valid'] for row in report['legacy_CE3']) != 1:
            raise ValueError('frozen legacy CE3 runtime counterexample did not reproduce exactly')
        for cells, label, amps in plan():
            bpy.ops.wm.open_mainfile(filepath=str(a.evidence/f'K{cells}_base.blend'))
            sc = bpy.context.scene
            original = readback(bpy, sc)
            retained = json.loads((a.evidence/f'K{cells}_base_snapshot.json').read_text())
            validate_roundtrip(chain_fixture(cells), retained, original)
            expected = copy.deepcopy(original); set_fields(expected, amps)
            source_fields(sc, amps); snapshot = readback(bpy, sc)
            if snapshot != expected: raise ValueError('evaluated raw scene differs from declared source change')
            native, elapsed = legacy.dispatch(gpu, shaders['V2'], snapshot, mode_cap=5)
            metrics, oracle = check(snapshot, native, 'shared', cells, amps)
            report['real_cases'].append({'cells': cells, 'input': label, 'snapshot': snapshot, 'gpu': native,
                'metrics': metrics, 'oracle': serialize(oracle), 'dispatch_sync_readback_ms': elapsed})
        if (len(report['raw_cases']), len(report['legacy_CE3']), len(report['real_cases'])) != (21, 6, 4):
            raise ValueError('frozen 31 dispatch count required')
        if any(sha(a.evidence/n) != h for n, h in hashes.items()): raise ValueError('frozen scenes changed')
        if any(sha(root/n) != h for n, h in code.items()): raise ValueError('code changed during run')
        report['passed'] = True
        print('EXP005_NEAREST_V2_NATIVE_PASS', flush=True)
    except Exception as exc:
        report['error'] = f'{type(exc).__name__}: {exc}'
        raise
    finally:
        a.report.write_text(json.dumps(report, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    shaders.clear()
    import gc
    gc.collect(); schedule_exit(bpy)


if __name__ == '__main__': main()
