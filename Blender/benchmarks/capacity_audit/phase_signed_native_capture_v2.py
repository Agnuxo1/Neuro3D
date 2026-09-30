"""Opt-in durable signed capture records; NOT GPU admission/authentication.

Never overwrite a record. Initial/receipt/final are separate, fsynced files.
A hard exit leaves a nonterminal initial record, never an accepted completion.
fsync does not certify survival of device failure or a Windows power loss.
"""
import json
import os
from pathlib import Path

import phase_signed_native_capture_v1 as V1
from phase_signed_native_probe_v1 import dispatch_signed_probe, scalar

V1_SHA = 'be70ede6795913a5a820cce0519e46c8c5e94f4dbda54946536ac739a0099796'
sha = V1.sha
fresh_deadline = V1.fresh_deadline
reject_admission = V1.reject_admission


def manifest():
    if sha(V1.__file__) != V1_SHA:
        raise ValueError('frozen V1 capture changed')
    plan = V1.manifest()
    plan['version'] = 'phase-signed-native-capture-v2'
    plan['code_sha256'][str(Path(__file__).resolve())] = sha(__file__)
    plan['persistence'] = 'exclusive initial result.json + raw receipt + terminal final.json'
    return plan


def validate_manifest(plan):
    if json.dumps(plan, sort_keys=True, allow_nan=False) != json.dumps(
            manifest(), sort_keys=True, allow_nan=False):
        raise ValueError('V2 manifest differs from preregistration/current pins')
    return [(scalar(c['input_uint32'][:2]), scalar(c['input_uint32'][2:]))
            for c in plan['cases']], [c['expected_status'] for c in plan['cases']]


def write_once(path, value):
    # Serialize BEFORE open: non-finite decoded data cannot leave an empty record.
    text = json.dumps(value, indent=2, allow_nan=False)+'\n'
    with Path(path).open('x', encoding='utf-8') as out:
        out.write(text); out.flush(); os.fsync(out.fileno())


def run_private_capture(gpu, plan, evidence, check, *, admit=reject_admission):
    if not callable(check) or not callable(admit):
        raise ValueError('mandatory external deadline/admission adapters')
    check(); samples, statuses = validate_manifest(plan)
    folder = Path(evidence)
    folder.mkdir(exist_ok=False)
    write_once(folder/'manifest.json', plan)
    base = {'runtime_execution_authenticated': False, 'native_promotion_allowed': False,
            'operational_gate_passed': False, 'geometry_or_scene_inference': False,
            'no_jev_aval': True, 'manifest_sha256': sha(folder/'manifest.json'),
            'scope': 'private scalar capture V2; external supervisor/authentication separate'}
    write_once(folder/'result.json', dict(base, status='in_progress'))
    result = dict(base, status='failed', readback_retained=False,
                  initial_sha256=sha(folder/'result.json'))
    try:
        check(); admit(); validate_manifest(plan); check()

        def retain(output):
            write_once(folder/'raw_uint32.json', output)
            raw_sha = sha(folder/'raw_uint32.json')
            write_once(folder/'raw_receipt.json', {'raw_sha256': raw_sha,
                       'manifest_sha256': base['manifest_sha256'],
                       'initial_sha256': result['initial_sha256']})
            result.update(readback_retained=True, raw_sha256=raw_sha,
                          receipt_sha256=sha(folder/'raw_receipt.json'))

        decoded = dispatch_signed_probe(gpu, samples, statuses, check, retain)
        json.dumps(decoded, allow_nan=False)  # Fail before attaching invalid payload.
        if not result['readback_retained']:
            raise ValueError('dispatcher returned without mandatory raw capture')
        check(); validate_manifest(plan)
        result['decoded'] = decoded
        result['status'] = 'scalar_gates_passed_pending_outer_authentication'
        return result
    except BaseException as error:
        result['error_type'] = type(error).__name__
        raise
    finally:
        write_once(folder/'final.json', result)


def inspect_capture(evidence):
    """Content consistency only. No missing/nonterminal record may pass completion."""
    folder = Path(evidence)
    read = lambda name: json.loads((folder/name).read_text(encoding='utf-8'))
    plan = read('manifest.json'); validate_manifest(plan)
    initial = read('result.json')
    ms, ins = sha(folder/'manifest.json'), sha(folder/'result.json')
    if initial.get('status') != 'in_progress' or initial.get('manifest_sha256') != ms:
        raise ValueError('initial record mismatch')
    raw_ok = False
    if (folder/'raw_receipt.json').exists():
        receipt = read('raw_receipt.json')
        if receipt != {'raw_sha256': sha(folder/'raw_uint32.json'),
                       'manifest_sha256': ms, 'initial_sha256': ins}:
            raise ValueError('raw receipt mismatch')
        raw_ok = True
    summary = {'status': 'incomplete', 'raw_receipt_verified': raw_ok,
               'completion_content_verified': False, 'runtime_execution_authenticated': False,
               'native_promotion_allowed': False, 'operational_gate_passed': False}
    if not (folder/'final.json').exists():
        return summary
    final = read('final.json')
    if final.get('manifest_sha256') != ms or final.get('initial_sha256') != ins:
        raise ValueError('terminal lineage mismatch')
    if final.get('readback_retained') is True:
        if not raw_ok or final.get('raw_sha256') != sha(folder/'raw_uint32.json') or \
                final.get('receipt_sha256') != sha(folder/'raw_receipt.json'):
            raise ValueError('terminal raw lineage mismatch')
    elif raw_ok:
        raise ValueError('terminal contradicts durable raw receipt')
    if final.get('status') == 'scalar_gates_passed_pending_outer_authentication':
        if not raw_ok or final.get('readback_retained') is not True or 'decoded' not in final:
            raise ValueError('scalar completion without raw/decoded evidence')
        summary.update(status='scalar_pending_authentication', completion_content_verified=True)
    elif final.get('status') == 'failed':
        summary['status'] = 'failed'
    else:
        raise ValueError('unknown terminal status')
    return summary
