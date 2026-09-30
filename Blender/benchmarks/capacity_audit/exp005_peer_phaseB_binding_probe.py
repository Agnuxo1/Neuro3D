"""Narrow read-only acknowledgement of policy008 repair, no peer writers/GPU."""
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PEER = Path('D:/PROJECTS/.cognition/neuro3d/p0_scene_gpu')
REPLY = ROOT/'coordinacion/respuestas/P0-FUSION-POLICY-008-CLAUDE.json'
REPLY_SHA = 'f3cbb04d7e8dfc4810ed61414e3718a113a627e5b90989ae5d9164f0e031380e'


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def audit():
    if sha(REPLY) != REPLY_SHA: raise ValueError('review new peer reply first')
    reply = json.loads(REPLY.read_text(encoding='utf-8'))
    pins = {str(PEER/k): v for k, v in reply['artifacts_sha256'].items()}
    pins[str(REPLY)] = REPLY_SHA
    for label in ('P0-FUSION-POLICY-007-CODEX', 'task_input'):
        entry = reply['ack'][label]; pins[str(ROOT/entry['path'])] = entry['sha256']
    pins[str(Path(__file__).resolve())] = sha(__file__)
    if any(sha(p) != v for p, v in pins.items()): raise ValueError('retained SHA mismatch')
    spec = importlib.util.spec_from_file_location('audited_peer_binding_checker',
                                                 PEER/'p03_checker_v2.py')
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)  # Reviewed pure library, no CLI/test writers.
    mp = PEER/'p03_manifest.json'
    man = json.loads(mp.read_text())
    valid = json.loads((PEER/'p03_v4_cpu.json').read_text())
    failures, warnings = checker.check(valid, man, mp)
    altered = deepcopy(valid)
    entry = altered['groups'][0]['policy_per_scene']['per_scene'][0]
    original = entry['quant']; entry['quant'] *= 1e6
    tamper_failures, _ = checker.check(altered, man, mp)
    if failures or warnings or not any('politica quant' in f for f in tamper_failures):
        raise AssertionError('narrow control/quant repair not confirmed')
    if any(sha(p) != v for p, v in pins.items()): raise ValueError('input changed during audit')
    return {'task_id': 'P0-FUSION-POLICY-009-CODEX', 'code_sha256': pins,
            'peer_ack_ID_and_SHA_verified': True, 'valid_v4_control_failures': failures,
            'valid_v4_control_warnings': warnings,
            'tamper': {'original_quant': original, 'altered_quant': entry['quant'],
                       'checker_failures': tamper_failures},
            'quant_result_data_repair_confirmed': True,
            'scope': 'two retained-data CPU checker calls only, not 104 scene replay or GPU authentication',
            'not_verified': ['runtime use of dquant', 'native GPU execution',
                             'angular/accumulation bounds', 'general malformed-data coverage'],
            'native_promotion_allowed': False, 'no_jev_aval': True}


if __name__ == '__main__': print(json.dumps(audit(), indent=2, allow_nan=False))
