"""Read-only retained-data checker audit; no peer harness/test writers or GPU."""
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PEER = Path('D:/PROJECTS/.cognition/neuro3d/p0_scene_gpu')
REPLY = ROOT/'coordinacion/respuestas/P0-FUSION-POLICY-006-CLAUDE.json'
REPLY_SHA = '700c43aa38174af5d8ddbb7d070082268cbc7ee4c6a54508a5b88ea3df2a68b6'


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def audit():
    if sha(REPLY) != REPLY_SHA: raise ValueError('review changed reply first')
    reply = json.loads(REPLY.read_text(encoding='utf-8'))
    pins = {str(PEER/k): v for k, v in reply['artifacts_sha256'].items()}
    pins[str(REPLY)] = REPLY_SHA
    for label in ('P0-FUSION-POLICY-005-CODEX', 'task_input'):
        entry = reply['ack'][label]; pins[str(ROOT/entry['path'])] = entry['sha256']
    pins[str(Path(__file__))] = sha(__file__)
    if any(sha(p) != v for p, v in pins.items()): raise ValueError('retained SHA mismatch')
    spec = importlib.util.spec_from_file_location('audited_peer_phaseB_checker', PEER/'p03_checker.py')
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)  # Reviewed pure library; CLI writer not called.
    manifest_path = PEER/'p03_manifest.json'
    manifest = json.loads(manifest_path.read_text())
    valid = json.loads((PEER/'p03_v3_cpu.json').read_text())
    valid_failures = checker.check(valid, manifest, manifest_path)
    altered = deepcopy(valid)
    policy = altered['groups'][0]['policy_per_scene']['per_scene'][0]
    before = deepcopy(policy); policy['quant'] *= 1000000.
    altered_failures = checker.check(altered, manifest, manifest_path)
    if valid_failures or altered_failures: raise AssertionError('retained expected counterexample changed')
    if any(sha(p) != v for p, v in pins.items()): raise ValueError('input changed during audit')
    return {'task_id': 'P0-FUSION-POLICY-007-CODEX', 'code_sha256': pins,
            'peer_ack_ID_and_SHA_verified': True, 'valid_control_failures': valid_failures,
            'data_mutation': {'original_effective_policy': before, 'changed_effective_policy': policy},
            'changed_policy_checker_failures': altered_failures, 'changed_policy_still_accepted': True,
            'existing_peer_CPU_result_not_refuted': True, 'native_promotion_allowed': False,
            'scope': 'CPU checker only, retained result-data tamper; no actual wrong runtime quantization or GPU run',
            'pending': 'bind scene-indexed effective lambda/quant/dquant/floor to manifest, not just policy list length',
            'no_jev_aval': True}


if __name__ == '__main__': print(json.dumps(audit(), indent=2, allow_nan=False))
