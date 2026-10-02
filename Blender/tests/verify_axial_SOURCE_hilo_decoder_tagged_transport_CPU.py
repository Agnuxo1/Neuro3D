"""Independent wire and retained-output verification; no production imports."""
import base64
import hashlib
import json
import zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PATH='coordinacion/respuestas/AXIAL-SOURCE-HILO-DECODER-TAGGED-TRANSPORT-CPU-001-CODEX.json'
PARENT='coordinacion/respuestas/AXIAL-SOURCE-HILO-ZERO-AWARE-DECODER-CPU-001-CODEX.json'
CODE='Blender/benchmarks/capacity_audit/axial_SOURCE_hilo_zero_aware_decoder_CPU_v1.py'
MAGIC=b'N3DZAD01'
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def payload(r):
    t=r['test_run'];v=t.get('stdout_zlib_base64') or ''.join(t['stdout_zlib_base64_chunks'])
    b=zlib.decompress(base64.b64decode(v,validate=True))
    assert len(b)==t['stdout_bytes'] and sha(b)==t['stdout_sha256'];return json.loads(b)
def raw(v):
    assert type(v) is str
    b=base64.b64decode(v,validate=True);assert base64.b64encode(b).decode()==v;return b
r=json.loads((ROOT/PATH).read_bytes());assert r['task_id']=='AXIAL-SOURCE-HILO-DECODER-TAGGED-TRANSPORT-CPU-001'
pins=r['code_doc_sha256'];assert len(pins)==527
for p,h in pins.items():assert sha((ROOT/p).read_bytes())==h,p
result=payload(r);assert (result['tests_run'],result['errors'],result['failures'])==(4,0,0)
d=result['data'];req=d['request'];a=d['audit'];parent=payload(json.loads((ROOT/PARENT).read_bytes()))['data']
assert digest(req['decoder_INPUT'])==digest(parent['request'])
selector={'model':'axial-SOURCE-hilo-high-zero-sign-decoder-CPU-v1','implementation_sha256':pins[CODE],
          'parent_receipt_sha256':pins[PARENT],'payload_layout':'LE-u32-realhigh-reallow-imaghigh-imaglow',
          'envelope_magic_hex':MAGIC.hex()}
assert digest(a['decoder_selection'])==digest(selector)==digest(req['program_INPUT']['decoder_selection'])
assert req['program_INPUT']['decoder_INPUT_sha256']==digest(req['decoder_INPUT'])
assert a['request_sha256']==digest(req) and a['program_INPUT_sha256']==digest(req['program_INPUT'])
oldrows=parent['request']['SOURCE_limb_records'];outrows=parent['audit']['sources']
assert len(req['frames'])==len(oldrows)==len(a['sources'])==4
for frame,old,source,prior in zip(req['frames'],oldrows,a['sources'],outrows):
    b=raw(frame['frame_base64'])
    expected=MAGIC+bytes.fromhex(pins[CODE])+bytes.fromhex(old['context_sha256'])+bytes.fromhex(digest(old))+raw(old['hilo_le_base64'])
    assert b==expected and len(b)==120
    assert (frame['case_name'],frame['source_id'])==(old['case_name'],old['source_id'])==(source['case_name'],source['source_id'])
    assert source['frame_sha256']==sha(b) and source['encoder_row_sha256']==digest(old)
    assert source['payload_sha256']==sha(b[104:])==old['hilo_le_sha256']
    assert source['retained_whole_box_guard_admission_disproved'] is old['retained_whole_box_guard_admission_disproved']
    assert source['frozen_guard_admission_for_entire_box_proved'] is False and source['status']=='STOP'
    assert len(source['decoded_scalars'])==2
    for s,retained in zip(source['decoded_scalars'],prior['scalars']):
        assert digest(s)==digest({k:retained[k] for k in s})
    assert source['decoded_SOURCE_uint64']==[s['decoded_uint64'] for s in prior['scalars']]
assert (a['payload_bytes'],a['header_bytes'],a['wire_bytes'],a['native_RN64_adds'],a['zero_selections'])==(64,416,480,4,4)
assert a['encoder_calls']==a['old_suites_or_producers_reexecuted']==a['group_admissions']==0
assert a['phase_quota_fits'] is None and a['uniform_executed_SOURCE_error_L1'] is None
assert a['actual_scene_authenticated'] is False and a['frozen_GRID_program_changed'] is False and a['legacy_decoder_equivalence_proved'] is False
assert len(a['proof_scope'])==38 and all(x is False for x in a['proof_scope'].values())
m=d['missing'];assert (m['missing_cases'],m['missing_sources'],m['frames_received'],m['native_RN64_adds'])==(17,19,0,0)
assert (len(d['atomic_rejections']),len(d['model_rejections']),len(d['frame_construction_rejections']))==(22,4,6)
z=d['isolated_zero_frame'];b=raw(z['frame_base64']);old=parent['retained_negative_zero']['old']
assert z['old_scalar_sha256']==digest(old) and old['ORIGINAL_zero_sign_preserved'] is False and old['decoded_uint64']==0
assert b==MAGIC+bytes.fromhex(pins[CODE])+bytes.fromhex(z['context_sha256'])+bytes.fromhex(z['source_row_sha256'])+bytes.fromhex(old['hilo_le_hex'])+bytes(8)
assert sha(b[104:])==z['payload_sha256'] and z['scene_authenticated'] is False and z['old_failure_preserved'] is True
assert [s['decoded_uint64'] for s in z['decoded_scalars']]==[1<<63,0]
assert all(s['new_native_RN64_adds']==0 and s['new_zero_branch_selections']==1 for s in z['decoded_scalars'])
print(json.dumps({'status':'PASS','pins_verified':len(pins),'scene_frames':4,'payload_bytes':64,'header_bytes':416,'wire_bytes':480,
                  'native_scene_adds':4,'scene_zero_selections':4,'late_corruption_controls':22,'OLDminuszeroFAIL_preserved':True,
                  'transport_integrity_NOT_scene_or_GPU_admission':True},sort_keys=True))
