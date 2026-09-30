"""Pinned recipe + scalar capture/supervisor content join, NOT a launcher.

Re-decodes raw words rather than trusting a stored 'decoded' or rc0 label.
Metadata/SHA consistency never authenticates native GPU execution.
"""
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path

import phase_signed_native_capture_v2 as C
from phase_signed_native_probe_v1 import decode
import scalar_job_supervisor_v1 as S

ROOT = Path(__file__).resolve().parents[3]
SUPERVISOR_REPORT = ROOT/'coordinacion/respuestas/PHASE-SCALAR-SUPERVISOR-001-CODEX.json'
SUPERVISOR_SHA = 'bb280b865f8635493cbcb75ba0b084a6a7007f3a6b21c3a47cd5993565713913'


def canonical(v): return json.dumps(v, sort_keys=True, allow_nan=False)


def contract():
    if C.sha(SUPERVISOR_REPORT) != SUPERVISOR_SHA:
        raise ValueError('frozen supervisor preparation changed')
    report = json.loads(SUPERVISOR_REPORT.read_text(encoding='utf-8'))
    plan = C.manifest()
    pins = dict(plan['code_sha256']); pins.update(report['code_sha256'])
    pins[str(SUPERVISOR_REPORT)] = SUPERVISOR_SHA
    pins[str(Path(__file__).resolve())] = C.sha(__file__)
    if any(C.sha(p) != v for p, v in pins.items()):
        raise ValueError('frozen bundle dependency changed')
    return {'version': 'scalar-job-bundle-v1', 'code_sha256': pins,
            'capture_manifest': plan, 'runtime_execution_authenticated': False,
            'native_promotion_allowed': False, 'operational_gate_passed': False,
            'scope': 'content join only; no acquisition/launcher/OS or driver authentication'}


def paths(capture, supervisor):
    values = [Path(v).resolve() for v in (capture, supervisor)]
    if any(not Path(v).is_absolute() for v in (capture, supervisor)) or \
            any(not p.is_relative_to(ROOT) or p == ROOT for p in values) or \
            values[0].is_relative_to(values[1]) or values[1].is_relative_to(values[0]):
        raise ValueError('distinct nonnested private absolute evidence paths inside project required')
    return [str(v) for v in values]


def recipe(command, capture, supervisor, *, deadline, now, queue_name, timeout=60):
    # Caller must build this INSIDE an acquired turn; this function acquires none.
    S.validate_policy(deadline, timeout, now)
    if not isinstance(command, list) or not command or \
            any(type(v) is not str or not v for v in command):
        raise ValueError('explicit argv required')
    if not isinstance(queue_name, str) or not queue_name:
        raise ValueError('explicit queue job name required')
    cpath, spath = paths(capture, supervisor)
    return {'contract': contract(), 'command': command,
            'command_sha256': hashlib.sha256(json.dumps(command).encode()).hexdigest(),
            'capture_path': cpath, 'supervisor_path': spath,
            'deadline_utc': deadline.isoformat(), 'timeout_s': timeout, 'queue_name': queue_name}


def validate_recipe(value):
    expected_keys = {'contract', 'command', 'command_sha256', 'capture_path',
                     'supervisor_path', 'deadline_utc', 'timeout_s', 'queue_name'}
    if not isinstance(value, dict) or set(value) != expected_keys:
        raise ValueError('exact recipe schema required')
    if canonical(value['contract']) != canonical(contract()):
        raise ValueError('recipe contract differs from frozen/current pins')
    paths(value['capture_path'], value['supervisor_path'])
    deadline = datetime.fromisoformat(value['deadline_utc'])
    if deadline.tzinfo is None or deadline.utcoffset().total_seconds() != 0:
        raise ValueError('explicit UTC recipe deadline required')
    t = value['timeout_s']
    if isinstance(t, bool) or not isinstance(t, (int, float)) or not math.isfinite(t) or not 0<t<=70:
        raise ValueError('bounded scalar timeout required')
    cmd = value['command']
    if not isinstance(cmd, list) or not cmd or any(type(v) is not str or not v for v in cmd):
        raise ValueError('explicit argv required')
    if value['command_sha256'] != hashlib.sha256(json.dumps(cmd).encode()).hexdigest():
        raise ValueError('command SHA mismatch')
    if type(value['queue_name']) is not str or not value['queue_name']:
        raise ValueError('queue name required')


def inspect_bundle(value):
    """No promotion. Re-evaluate raw scalar gates with CPU decoder/oracle."""
    validate_recipe(value)
    cdir, sdir = Path(value['capture_path']), Path(value['supervisor_path'])
    read = lambda p: json.loads(p.read_text(encoding='utf-8'))
    initial, final = read(sdir/'initial.json'), read(sdir/'final.json')
    if initial.get('status') != 'in_progress' or final.get('status') != 'completed' or \
            type(final.get('exit_code')) is not int or final['exit_code'] != 0 or \
            final.get('cleanup_completed') is not True or final.get('reasons') != []:
        raise ValueError('supervisor did not complete cleanly')
    for envelope in (initial, final):
        for key in ('command_sha256', 'deadline_utc', 'timeout_s'):
            if canonical(envelope.get(key)) != canonical(value[key]):
                raise ValueError('supervisor/recipe '+key+' mismatch')
        if envelope.get('runtime_execution_authenticated') is not False or \
                envelope.get('native_promotion_allowed') is not False:
            raise ValueError('envelope contradicts unauthenticated preparation')
    if (final.get('reservation') or {}).get('name') != value['queue_name']:
        raise ValueError('named reservation metadata mismatch')
    elapsed = final.get('elapsed_s')
    if isinstance(elapsed, bool) or not isinstance(elapsed, (int, float)) or \
            not math.isfinite(elapsed) or not 0 <= elapsed < value['timeout_s']:
        raise ValueError('late/invalid supervisor completion')
    samples = final.get('samples')
    if not isinstance(samples, list) or not samples:
        raise ValueError('missing resource samples')
    for i, sample in enumerate(samples):
        if S.resource_reasons(sample, before_launch=i==0):
            raise ValueError('resource sample violates frozen scalar budget')
    capture = C.inspect_capture(cdir)
    if capture['status'] != 'scalar_pending_authentication' or not capture['completion_content_verified']:
        raise ValueError('capture is incomplete/failed')
    plan = read(cdir/'manifest.json')
    if canonical(plan) != canonical(value['contract']['capture_manifest']):
        raise ValueError('capture/recipe manifest mismatch')
    pairs, statuses = C.validate_manifest(plan)
    decoded = decode(pairs, read(cdir/'raw_uint32.json'), expected_statuses=statuses)
    if canonical(decoded) != canonical(read(cdir/'final.json').get('decoded')):
        raise ValueError('stored decoded data differs from raw re-decoding')
    validate_recipe(value)
    return {'job_content_consistency_verified': True, 'scalar_redecode_verified': True,
            'valid_cases': sum(c['status']==0 for c in decoded['cases']),
            'abort_cases': sum(c['status']!=0 for c in decoded['cases']),
            'injected_test_adapters': final.get('injected_test_adapters'),
            'runtime_execution_authenticated': False, 'native_promotion_allowed': False,
            'operational_gate_passed': False, 'geometry_or_scene_inference': False,
            'scope': 'CPU content consistency only; recipe/rc/SHA cannot authenticate a GPU run',
            'no_jev_aval': True}
