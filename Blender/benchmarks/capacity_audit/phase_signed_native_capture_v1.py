"""Private signed scalar evidence capture; no launcher or admission authority.

CPU adapters test persistence only. Native authenticity and hard process timeout
remain the responsibility of a separate exclusive outer supervisor.
"""
import hashlib
import json
from pathlib import Path

from phase_native_capture_v1 import fresh_deadline, reject_admission
from phase_signed_native_probe_v1 import dispatch_signed_probe, pilot_cases, scalar

ROOT = Path(__file__).resolve().parents[3]
PREP = ROOT/'coordinacion/respuestas/PHASE-SIGNED-NATIVE-PREP-001-CODEX.json'
PREP_SHA = '3cc971e17a9f6267cb4da15707f51a2c47d8a72982a12f2f048f3771bbc907e4'
DEADLINE_HELPER = Path(__file__).with_name('phase_native_capture_v1.py')
DEADLINE_HELPER_SHA = 'bea2803eef83d66ac9e9b097137c67a270d8516764b9b01a94943c9c4602f1dc'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def manifest():
    if sha(DEADLINE_HELPER) != DEADLINE_HELPER_SHA:
        raise ValueError('frozen deadline helper changed')
    if sha(PREP) != PREP_SHA:
        raise ValueError('signed preparation changed')
    prep = json.loads(PREP.read_text(encoding='utf-8'))
    pins = dict(prep['code_sha256'])
    if any(sha(p) != value for p, value in pins.items()):
        raise ValueError('frozen signed preparation inputs changed')
    if pilot_cases() != prep['pilot_cases_exact_uint32']:
        raise ValueError('signed cases differ from preregistration')
    pins[str(PREP)] = PREP_SHA
    pins[str(DEADLINE_HELPER)] = DEADLINE_HELPER_SHA
    pins[str(Path(__file__).resolve())] = sha(__file__)
    return {'version': 'phase-signed-native-capture-v1', 'code_sha256': pins,
            'cases': pilot_cases(),
            'policy': {'child_deadline_max_seconds': 90, 'ram_budget_GiB': 2,
                       'ram_free_after_budget_min_GiB': 4, 'vram_total_max_GiB': 18,
                       'temperature_max_C': 80, 'scalar_field_gate': 1e-4},
            'operational_admission_granted': False, 'native_promotion_allowed': False}


def validate_manifest(plan):
    if json.dumps(plan, sort_keys=True, allow_nan=False) != json.dumps(
            manifest(), sort_keys=True, allow_nan=False):
        raise ValueError('signed manifest differs from frozen inputs or current pins')
    return [(scalar(c['input_uint32'][:2]), scalar(c['input_uint32'][2:]))
            for c in plan['cases']], [c['expected_status'] for c in plan['cases']]


def run_private_capture(gpu, plan, evidence, check, *, admit=reject_admission):
    """No GPU admission by default; raw readback precedes decoder/deadline gates."""
    if not callable(check) or not callable(admit):
        raise ValueError('explicit external deadline/admission adapters required')
    check(); samples, statuses = validate_manifest(plan)
    folder = Path(evidence)
    folder.mkdir(exist_ok=False)
    with (folder/'manifest.json').open('x', encoding='utf-8') as out:
        out.write(json.dumps(plan, indent=2, allow_nan=False)+'\n')
    result = {'status': 'failed', 'readback_retained': False,
              'runtime_execution_authenticated': False, 'native_promotion_allowed': False,
              'operational_gate_passed': False, 'geometry_or_scene_inference': False,
              'no_jev_aval': True,
              'scope': 'private signed scalar capture; outer guard/authentication separate'}
    with (folder/'result.json').open('x', encoding='utf-8') as report:
        try:
            check(); admit(); validate_manifest(plan); check()

            def retain(output):
                with (folder/'raw_uint32.json').open('x', encoding='utf-8') as raw:
                    raw.write(json.dumps(output, allow_nan=False)+'\n')
                result['readback_retained'] = True
                result['raw_sha256'] = sha(folder/'raw_uint32.json')

            result['decoded'] = dispatch_signed_probe(gpu, samples, statuses, check, retain)
            check(); validate_manifest(plan)
            result['status'] = 'scalar_gates_passed_pending_outer_authentication'
            return result
        except BaseException as error:
            result['error_type'] = type(error).__name__
            raise
        finally:
            report.write(json.dumps(result, indent=2, allow_nan=False)+'\n')
            report.flush()
