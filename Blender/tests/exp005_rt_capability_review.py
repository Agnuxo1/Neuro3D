"""Pinned CPU review of RT-CAP-002, with no peer imports/writers or launches.

Only two inspected pure functions are replayed via AST in a restricted
namespace. Telemetry is synthetic. This is not Blender/RT runtime evidence.
"""
import argparse
import ast
import copy
import hashlib
import json
import math
import os
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parents[2]
NEURO3D_COGNITION = Path(os.environ.get("NEURO3D_COGNITION_DIR", REPO_ROOT / ".cognition"))

ROOT = Path(__file__).parents[2]
PEER = NEURO3D_COGNITION / 'neuro3d/rt_cap002'
EXPECTED = {
    'rtcap.py': '86479f750963e2201f3283808eab25535192274ad27769c899e246bf25c26145',
    'test_rtcap.py': 'd1039895bc80e29a9dd2531353d3ed0bb9e641ce49c6510a983cd99e2fcf9562',
    'blender_capture.py': '4db3326fbf96d47429b23f23213e39a47121ce87f31968007a81c6edf0b3b8c1',
    'guard.py': 'b0245f0b274d91e4f302adb8dfde3bab01f36cad00f9a74c05776795a0c1bcf6',
    'manifest_T2.json': '5bdff7c492686ef8d0aef9fe16f36a74cb4a6216fcfb9d8fe50405fdf3ef09b6',
    'manifest_T32.json': '722751c0793a376c3be8fd58bea37132a12ea1c0879d671128cd74bfe2271a56',
    'guard_selftest.json': '999dddb531f4bcbfd7d470b1ee7b73c4ae881a43d9783a54b486d898903200dc',
    'guard_block_test.json': 'e21bd125658fa33a686f6e4b38ded39406c614664993ff4aebe6d1dca44fcdc9',
}


def pinned_inputs():
    result = {}
    for name, expected in EXPECTED.items():
        raw = (PEER / name).read_bytes()
        if hashlib.sha256(raw).hexdigest() != expected:
            raise ValueError('peer changed: ' + name)
        result[name] = raw.decode('utf-8-sig')
    return result


def pure_function(source, name, namespace):
    """No imports/main/I/O executed; forbid calls except inspected pure allowlist."""
    tree = ast.parse(source)
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
    allowed = {'telemetry', 'centre', 'abs', 'round', 'range', 'list', 'len', 'math.hypot'}
    for item in ast.walk(node):
        if isinstance(item, (ast.Import, ast.ImportFrom, ast.Global, ast.Nonlocal)):
            raise ValueError('unexpected side effect in selected function')
        if isinstance(item, ast.Call):
            target = ast.unparse(item.func)
            if target not in allowed and not target.endswith('.append'):
                raise ValueError('unreviewed call: ' + target)
    safe_builtins = {k: __builtins__[k] for k in ('abs', 'round', 'range', 'list', 'len')} if isinstance(__builtins__, dict) else {
        k: getattr(__builtins__, k) for k in ('abs', 'round', 'range', 'list', 'len')}
    ns = {'__builtins__': safe_builtins, **namespace}
    exec(compile(ast.Module(body=[node], type_ignores=[]), '<pinned pure ' + name + '>', 'exec'), ns)
    return ns[name], [node.lineno, node.end_lineno]


def literal_assignment(source, name):
    for node in ast.parse(source).body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return ast.literal_eval(node.value)
    raise ValueError('literal not found: ' + name)


def perfect_capture(m):
    n = m['res']; ids = m['expected_id_grid_row0_bottom']; ts = m['expected_t_grid']
    aov = [[0.0 if ids[r][c] < 0 else ids[r][c] + 1.0 for c in range(n)] for r in range(n)]
    z = [[1e10 if ids[r][c] < 0 else ts[r][c] for c in range(n)] for r in range(n)]
    pos = [[[(c + .5) / n, (r + .5) / n, 0.0 if ids[r][c] < 0 else 2.0 - ts[r][c]] for c in range(n)] for r in range(n)]
    return aov, z, pos


def audit():
    inputs = pinned_inputs(); policy = literal_assignment(inputs['guard.py'], 'POLICY')
    thresholds = literal_assignment(inputs['rtcap.py'], 'THRESHOLDS')
    check, check_lines = pure_function(inputs['rtcap.py'], 'check_capture', {
        'THRESHOLDS': thresholds, 'math': math, 'centre': lambda r, c: ((c + .5) / 8, (r + .5) / 8)})
    valid = []
    for size in (2, 32):
        m = json.loads(inputs[f'manifest_T{size}.json'])
        body = {k: v for k, v in m.items() if k != 'manifest_sha256_body'}
        sha = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        if sha != m['manifest_sha256_body']: raise ValueError('manifest body changed')
        if not check(m, *perfect_capture(m))['pass']: raise ValueError('perfect control failed')
        valid.append({'T': size, 'perfect_capture_pass': True, 'manifest_body_sha_verified': True})
    m = json.loads(inputs['manifest_T32.json']); checker_bad = []
    for name, slot in (('depth_nan', 'z'), ('position_z_nan', 2), ('position_x_nan', 0)):
        a, z, p = copy.deepcopy(perfect_capture(m))
        if slot == 'z': z[0][0] = float('nan')
        else: p[0][0][slot] = float('nan')
        checker_bad.append({'case': name, 'pixel_rc': [0, 0], 'injected': 'NaN', 'peer_pass': check(m, a, z, p)['pass']})
    a, z, p = perfect_capture(m); z[0][0] += 2e-6
    numeric_bad_rejected = not check(m, a, z, p)['pass']

    telemetry = {'ram_free_gib': 8.0, 'vram_used_gib': 1.0, 'vram_total_gib': 24.0, 'temp_c': 30.0}
    run, guard_lines = pure_function(inputs['guard.py'], 'preflight', {'POLICY': policy, 'telemetry': lambda: dict(telemetry)})
    if run(1.5, 1.0)[1]: raise ValueError('valid budget control blocked')
    guard_bad = []
    for key in ('ram_free_gib', 'vram_used_gib', 'temp_c'):
        previous = telemetry[key]; telemetry[key] = float('nan')
        _, why = run(1.5, 1.0)
        guard_bad.append({'case': key + '_nan', 'injected': 'NaN', 'peer_blocked': bool(why)})
        telemetry[key] = previous
    for name, ram, vram in (('ram_budget_nan', float('nan'), 1.0), ('vram_budget_nan', 1.5, float('nan'))):
        guard_bad.append({'case': name, 'injected': 'NaN', 'peer_blocked': bool(run(ram, vram)[1])})
    telemetry['ram_free_gib'] = 3.0
    guard_bad.append({'case': 'negative_ram_budget_with_3GiB_free', 'budget_gib': -2.0, 'peer_blocked': bool(run(-2.0, 1.0)[1])})
    positive_low_ram_rejected = bool(run(1.5, 1.0)[1])
    telemetry['ram_free_gib'] = 8.0; telemetry['vram_used_gib'] = 19.0
    guard_bad.append({'case': 'negative_vram_budget_with_19GiB_used', 'budget_gib': -2.0, 'peer_blocked': bool(run(1.5, -2.0)[1])})
    return {'schema': 'exp005-rt-capability-review-cpu-v1',
        'scope': 'Pinned pure checker/preflight functions with synthetic data only; no peer imports/main/writers, no telemetry/GPU/Blender execution',
        'input_sha256': {str(PEER / k): v for k, v in EXPECTED.items()},
        'valid_controls': valid, 'numeric_bad_depth_rejected': numeric_bad_rejected,
        'positive_low_ram_rejected': positive_low_ram_rejected,
        'nonfinite_checker_cases': checker_bad, 'unsafe_guard_cases': guard_bad,
        'source_lines': {'check_capture': check_lines, 'preflight': guard_lines},
        'static_findings': [
            'guard.main: no absolute UTC deadline argument/check; only relative subprocess timeout',
            'guard.main: no in-flight RAM/VRAM/temperature polling while child runs',
            'guard.main: postflight telemetry error is stored as text without changing OK status/exit',
            'blender_capture: false check.pass is printed/saved but does not cause nonzero exit',
            'blender_capture: no selected-device inventory retained; requesting OPTIX alone is not hardware-counter proof'],
        'launch_approved': False, 'native_or_rt_certified': False, 'no_jev_aval': True}


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); result = audit()
    result['code_sha256'] = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in (
        Path(__file__), Path(__file__).with_name('test_exp005_rt_capability_review.py'))}
    with args.output.open('x', encoding='utf-8') as f:
        f.write(json.dumps(result, indent=2, allow_nan=False) + '\n')
    print(json.dumps({'checker_invalid_accepted': sum(c['peer_pass'] for c in result['nonfinite_checker_cases']),
        'guard_unsafe_accepted': sum(not c['peer_blocked'] for c in result['unsafe_guard_cases']),
        'report_sha256': hashlib.sha256(args.output.read_bytes()).hexdigest()}))


if __name__ == '__main__': main()
