"""Six retained peer scalars, own frozen proxy; no scene/GPU certificate.

Never import or execute the peer writer, NumPy or scene runners. Extract
only two reviewed pure functions from the pinned OWN arithmetic proxy.
"""
import ast
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path
import struct
import time

ROOT = Path(__file__).resolve().parents[2]
RESPONSE = ROOT / 'coordinacion/respuestas/PRECISION-006-REDUCTION-CLAUDE.json'
PINS = {
    RESPONSE: '0d1a1eaa981f2cb60261e3563c85a8721d499fd6967605025684c3b9903e9609',
    ROOT / 'Docs/EXP-005-PHASE-REDUCTION-CPU-2026-09-30.md': '4daa4f6dc33e83dbae475da359e7161b7b2402259121a791a388f11ab58c9a22',
    ROOT / 'Blender/tests/exp005_phase_reduction_cpu_audit.py': '3569f1a95966dcdfe272f52007a1cc97fd548ae32132b39472e5b906b3d9e09e',
    Path('D:/PROJECTS/.cognition/neuro3d/precision006_claude/b_reduction.py'): '9ce55ccb3fab0bc434635424a4f9f5e912ca141282454422a97390fdd7203952',
    Path('D:/PROJECTS/.cognition/neuro3d/precision006_claude/b_reduction.json'): '524405afc15861cacd44604346cec9b2e84ccfc7a31516c46348a1446e47d31f',
    ROOT / 'Blender/shaders/exp005_shared_frontier.glsl': '914bf2962ead3c6a7b721a8dc2aa6c1e796af4bde1892db1802c3ca93ebdfcd1',
}


def check_pins():
    for path, expected in PINS.items():
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError('changed input: ' + str(path))


def probe():
    start = time.monotonic()
    check_pins()
    peer = json.loads(RESPONSE.read_text(encoding='utf-8'))
    artifact = json.loads(Path(peer['artifacts']['b_reduction.json']).read_text())
    if peer['cases'] != artifact['cases'] or len(peer['cases']) != 6:
        raise ValueError('peer scalar cases inconsistent')
    source = ROOT / 'Blender/tests/exp005_phase_reduction_cpu_audit.py'
    tree = ast.parse(source.read_text())
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef)
             and n.name in ('float32', 'phase_proxy')]
    if len(nodes) != 2 or any(n.decorator_list or n.args.defaults for n in nodes):
        raise ValueError('reviewed pure definitions changed')
    namespace = {'struct': struct, 'math': math, 'F': F}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(source), 'exec'), namespace)
    rows = []
    for item in peer['cases']:
        length, wavelength = item['L_BU'], item['lambda']
        f32 = namespace['float32'](wavelength)
        if f32 != wavelength:
            raise ValueError('this scoped comparison requires exact float32 lambda')
        result = namespace['phase_proxy'](length, wavelength)
        exact_q = F(length) / F(wavelength)
        row = {'label': item['label'], 'L_BU': length, 'lambda_BU': wavelength,
               'lambda_exact_float32': True,
               'binary64_quotient_exact': F(length / wavelength) == exact_q,
               'exact_reduced_turns': result['exact_reduced_turns']}
        for own_key, peer_key in (
            ('phase_first_CPU_unit_field_error', 'phase_first_unit_err'),
            ('cycles_first_CPU_unit_field_error', 'cycles_first_unit_err'),
        ):
            row[peer_key] = result[own_key]
            row[peer_key + '_peer_delta'] = abs(result[own_key] - item[peer_key])
            if row[peer_key + '_peer_delta'] > 1e-13:
                raise ValueError('scalar disagreement')
        rows.append(row)
    adversary = rows[3]
    if not (adversary['phase_first_unit_err'] < 1e-4
            < adversary['cycles_first_unit_err']):
        raise ValueError('F1 crossover not reproduced')
    if not (rows[1]['binary64_quotient_exact'] and rows[2]['binary64_quotient_exact']
            and not adversary['binary64_quotient_exact']):
        raise ValueError('F2 exact-quotient distinction not reproduced')
    check_pins()
    return {'task_id': 'PRECISION-006-REDUCTION-CODEX',
            'timestamp_utc': datetime.now(timezone.utc).isoformat(),
            'status': 'six_scalar_CPU_cases_reproduced', 'cases': rows,
            'input_sha256': {str(p): s for p, s in PINS.items()},
            'probe_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'seconds': time.monotonic() - start, 'complex_field_gate': 1e-4,
            'diagnostic_peer_agreement_only': 1e-13,
            'peer_writer_executed': False, 'peer_sweep_replayed': False,
            'scene_retraced': False, 'GPU_or_Bpy_executed': False,
            'native_promotion_allowed': False, 'no_jev_aval': True,
            'limits': ['F4 empirical N_max is not a proved admission bound',
                       'F6 compensated proposal not implemented or certified',
                       'CPU libm and binary64 proxy, not GPU driver/FMA/RT']}


if __name__ == '__main__':
    print(json.dumps(probe(), indent=2))
