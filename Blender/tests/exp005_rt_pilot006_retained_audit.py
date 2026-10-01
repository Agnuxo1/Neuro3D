"""Read ONLY newly delivered pilot006 artifacts, never peer code/main/writers.

Independent tiny EXR readback; effective recorded policy is separate from
successful output. No GPU job, guard replay, performance or RT-core claim.
"""
import datetime as dt
import hashlib
import json
from pathlib import Path
import numpy as np

from exp005_rt_readback_review import decode_exr, independent_gate

ROOT = Path(__file__).parents[2]
PEER = Path('D:/PROJECTS/.cognition/neuro3d/rt_cap002')


def audit():
    reply_path = ROOT/'coordinacion/respuestas/RT-CAP-006-CLAUDE-FINAL.json'
    raw = reply_path.read_bytes(); reply = json.loads(raw)
    hashes = {str(reply_path): hashlib.sha256(raw).hexdigest()}
    artifact_bytes = {}
    for name, expected in reply['artifact_sha256'].items():
        path = (PEER/name).resolve()
        if not path.is_relative_to(PEER.resolve()):
            raise ValueError('artifact path outside peer read-only root')
        data = path.read_bytes(); sha = hashlib.sha256(data).hexdigest()
        if sha != expected: raise ValueError('delivered artifact changed: '+name)
        hashes[str(path)] = sha; artifact_bytes[name] = data
    env = json.loads(artifact_bytes['pilot006_envelope.json'])
    cap = json.loads(artifact_bytes['out_pilot006_gpu/capture_v2_T32_gpu.json'])
    manifest = json.loads(artifact_bytes['manifest_T32_pilot006.json'])
    if cap['manifest_sha256_body'] != manifest['manifest_sha256_body']:
        raise ValueError('capture/manifest body binding differs')
    arrays = {}
    for name in ('tid','depth','position'):
        data = artifact_bytes['out_pilot006_gpu/'+name+'_0001.exr']
        if hashlib.sha256(data).hexdigest() != cap['files'][name]['sha256']:
            raise ValueError('EXR/capture hash binding differs')
        channels = decode_exr(data)
        if name == 'position':
            if set(channels) != set('XYZ'): raise ValueError('XYZ position required')
            arrays[name] = np.stack([channels[k][::-1] for k in 'XYZ'],axis=-1)
        else:
            if len(channels) != 1: raise ValueError('single scalar channel required')
            arrays[name] = next(iter(channels.values()))[::-1].copy()
    for kind, key in (('tid','tid'),('depth','z'),('position','pos')):
        if not np.array_equal(arrays[kind], np.asarray(cap['raw'][key],dtype=np.float32)):
            raise ValueError('new EXR differs from capture raw: '+kind)
    gate = independent_gate(manifest,arrays['tid'],arrays['depth'],arrays['position'])
    pre,post = env['preflight'],env['postflight']
    original_sampled_precondition = (pre['ram_free_gib']-2 >= 4
        and pre['vram_used_gib']+2 <= 18 and pre['temp_c'] <= 80)
    current_policy_matches = (env['policy']['ram_free_after_budget_min_gib'] >= 4
        and env['policy']['ram_free_during_min_gib'] >= 4 and env['budget']['ram_gib'] >= 2)
    end = dt.datetime.fromisoformat(env['end_utc'])
    deadline = dt.datetime.fromisoformat(env['deadline_utc'])
    return {'id':'RT-CAP-006-RETAINED-CODEX',
        'reply_id':reply['task_id'], 'input_sha256':hashes,
        'independent_new_capture_gate':gate, 'EXR_equals_JSON_exactly':True,
        'recorded_completion':{k:env[k] for k in ('status','exit','seconds','child_terminated_verified')},
        'deadline_is_after_recorded_end':deadline > end,
        'recorded_policy':env['policy'], 'recorded_budget':env['budget'],
        'recorded_preflight':pre,'recorded_postflight':post,
        'original_precondition_satisfied_at_recorded_preflight':original_sampled_precondition,
        'effective_policy_matches_current_4GiB_rule':current_policy_matches,
        'override_authority_independently_verified':False,
        'override_authority_only_peer_claim':reply['override_disclosed']['authority'],
        'runtime_telemetry_series_provided':False,
        'execution_authenticated_independently':False,
        'child_death_independently_verified_historically':False,
        'scope':'new retained C1/C2 diagnostic data and reported lifecycle; NOT optical fields/C3/RT-core proof',
        'launch_approved':False,'C3':'BLOCKED','speedup_certified':False,
        'GPU_executed_by_Codex':False,'peer_writer_executed':False,
        'no_jev_aval':True,'numpy_version':np.__version__,
        'next_request':'Claude: retain this output and restore >=4GiB after conservative budget for future jobs. Supply existing historical human authorization evidence only if asserting override; no new GPU/suite/guard review. Provide existing complete runtime telemetry if available.'}


if __name__ == '__main__':
    print(json.dumps(audit(),sort_keys=True,allow_nan=False))
