"""Opt-in separate OpenGL consumer of frozen real Blender hit records.

No Blender/RT intersection dispatch: geometry remains prior CPU raycasts.
CPU oracle below is validation only; shader computes all deployed fields/powers.
"""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import struct
import time

from exp005_cascade_runtime import CASES, probes
from exp005_gpu_pack import pack_paths
from exp005_triangle_oracle import trace_scene

FIELD_TOL = 1e-4
POWER_TOL = 2e-4
SHADER = Path(__file__).parents[1]/'shaders'/'exp005_path_fields.glsl'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(folder):
    """Read frozen fixtures, pack raw inputs; independent CPU expected is validation."""
    manifest = json.loads((folder/'cascade_runtime.json').read_text(encoding='utf-8'))
    if not manifest['passed'] or set(manifest['cases']) != set(CASES):
        raise ValueError('complete passing frozen cascade required')
    jobs, hashes = [], {}
    for case in CASES:
        blend, snapshot_file = folder/f'{case}.blend', folder/f'{case}_snapshot.json'
        if sha(blend) != manifest['cases'][case]['blend_sha256']:
            raise ValueError('frozen blend hash mismatch')
        hashes[blend.name], hashes[snapshot_file.name] = sha(blend), sha(snapshot_file)
        snapshot = json.loads(snapshot_file.read_text(encoding='utf-8'))
        if len(snapshot['sources']) != 3:
            raise ValueError('three explicit source modes required')
        for label, amplitudes in probes():
            path_file = folder/f'{case}_{label}_paths.json'
            record = json.loads(path_file.read_text(encoding='utf-8'))
            hashes[path_file.name] = sha(path_file)
            scene = copy.deepcopy(snapshot)
            for source, amp in zip(scene['sources'], amplitudes):
                source['field_reim'] = [amp.real, amp.imag]
            packed = pack_paths(scene, record['bpy'])
            oracle = trace_scene(scene)['fields']
            retained = {p: complex(*v) for p, v in record['report']['fields'].items()}
            if set(packed.ports) != set(oracle) or set(oracle) != set(retained):
                raise ValueError('all declared complex ports required')
            jobs.append((case, label, amplitudes, packed, oracle, retained))
    return jobs, hashes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--authorized-by-user', action='store_true')
    args = parser.parse_args()
    if not args.authorized_by_user:
        raise SystemExit('Explicit GPU authorization required')
    if args.report.exists() or not args.report.parent.is_dir():
        raise SystemExit('Fresh report and existing parent required')
    report = {'passed': False, 'scope': 'raw Blender CPU paths -> separate OpenGL complex-field GPU consumer; not RT',
              'thresholds': {'complex': FIELD_TOL, 'power_balance': POWER_TOL, 'sham': 1e-12},
              'precision': 'FP64 products/sums/reduced phase; FP32 sin/cos', 'cases': []}
    ctx = window = None
    glfw = None
    try:
        jobs, hashes = prepare(args.evidence)
        report['input_sha256'] = hashes
        report['code_sha256'] = {p.name: sha(p) for p in
            (Path(__file__), Path(__file__).with_name('exp005_gpu_pack.py'), SHADER)}
        import glfw as glfw_module
        import moderngl
        glfw = glfw_module
        if not glfw.init():
            raise RuntimeError('GLFW initialization failed')
        glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        window = glfw.create_window(64, 64, 'Neuro3D raw path consumer', None, None)
        if window is None:
            raise RuntimeError('OpenGL context unavailable')
        glfw.make_context_current(window)
        ctx = moderngl.create_context(require=430)
        report['vendor'] = ctx.info.get('GL_VENDOR', 'unknown')
        report['renderer'] = ctx.info.get('GL_RENDERER', 'unknown')
        report['version'] = ctx.info.get('GL_VERSION', 'unknown')
        if 'NVIDIA' not in (report['vendor']+report['renderer']).upper():
            raise RuntimeError('Not NVIDIA context')
        shader = ctx.compute_shader(SHADER.read_text(encoding='utf-8'))
        actual_cases = {}
        for case, label, amps, packed, oracle, retained in jobs:
            raw_paths, raw_hits = packed.buffers()
            source, hits = ctx.buffer(raw_paths), ctx.buffer(raw_hits)
            target = ctx.buffer(reserve=len(packed.ports)*4*8)
            try:
                source.bind_to_storage_buffer(0)
                hits.bind_to_storage_buffer(1)
                target.bind_to_storage_buffer(2)
                shader['path_count'].value = packed.path_count
                shader['port_count'].value = len(packed.ports)
                shader['wavelength_BU'].value = packed.wavelength
                start = time.perf_counter()
                shader.run(group_x=math.ceil(len(packed.ports)/8))
                ctx.memory_barrier()
                values = struct.unpack(f'<{len(packed.ports)*4}d', target.read())
                elapsed_ms = (time.perf_counter()-start)*1000
            finally:
                source.release(); hits.release(); target.release()
            if not all(math.isfinite(v) for v in values):
                raise ValueError('nonfinite GPU readback')
            fields = {p: complex(values[4*i], values[4*i+1]) for i,p in enumerate(packed.ports)}
            powers = {p: values[4*i+2] for i,p in enumerate(packed.ports)}
            error = max(abs(fields[p]-oracle[p]) for p in fields)
            retained_error = max(abs(fields[p]-retained[p]) for p in fields)
            power_error = max(abs(powers[p]-abs(oracle[p])**2) for p in fields)
            balance = abs(sum(powers.values())-sum(abs(a)**2 for a in amps))
            internal = max(abs(powers[p]-abs(fields[p])**2) for p in fields)
            report['cases'].append({'case': case, 'probe': label, 'fields': {p:[v.real,v.imag] for p,v in fields.items()},
                'powers': powers, 'paths': packed.path_count, 'oracle_complex_error': error,
                'retained_cpu_complex_error': retained_error, 'oracle_power_error': power_error,
                'balance_error': balance, 'readback_internal_power_error': internal,
                'dispatch_sync_readback_ms': elapsed_ms})
            actual_cases[(case,label)] = fields, powers
            if max(error, retained_error)>FIELD_TOL or max(power_error,balance)>POWER_TOL or internal>1e-10:
                raise ValueError('frozen GPU consumer numerical gate failed')
        report['sham_complex_error'] = max(abs(actual_cases[('base',label)][0][p]-actual_cases[('sham',label)][0][p])
            for label,_ in probes() for p in actual_cases[('base',label)][0])
        report['causal_power_effects'] = {case: max(abs(actual_cases[(case,'basis0')][1][p]-actual_cases[('base','basis0')][1][p])
            for p in actual_cases[('base','basis0')][1]) for case in ('phase_a','phase_b','roof','lambda')}
        if report['sham_complex_error']>1e-12 or any(v<=1e-3 for v in report['causal_power_effects'].values()):
            raise ValueError('frozen GPU sham/causal gate failed')
        report['passed'] = True
        print('EXP005_GPU_CONSUMER_PASS', flush=True)
    except Exception as exc:
        report['error'] = f'{type(exc).__name__}: {exc}'
        raise
    finally:
        if ctx is not None: ctx.release()
        if window is not None: glfw.destroy_window(window)
        if glfw is not None: glfw.terminate()
        args.report.write_text(json.dumps(report, indent=2, allow_nan=False)+'\n', encoding='utf-8')


if __name__ == '__main__': main()
