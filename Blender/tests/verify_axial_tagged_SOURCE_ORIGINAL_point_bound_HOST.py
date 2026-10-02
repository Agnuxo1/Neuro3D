"""Independent rational/word/wire proof verifier; no production imports."""
import base64
import hashlib
import json
import zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PATH='coordinacion/respuestas/AXIAL-TAGGED-SOURCE-ORIGINAL-POINT-BOUND-HOST-001-CODEX.json'
PARENT='coordinacion/respuestas/AXIAL-SOURCE-HILO-DECODER-TAGGED-TRANSPORT-CPU-001-CODEX.json'
DECODER='Blender/benchmarks/capacity_audit/axial_SOURCE_hilo_zero_aware_decoder_CPU_v1.py'
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def payload(r):
    t=r['test_run'];v=t.get('stdout_zlib_base64') or ''.join(t['stdout_zlib_base64_chunks'])
    b=zlib.decompress(base64.b64decode(v,validate=True))
    assert len(b)==t['stdout_bytes'] and sha(b)==t['stdout_sha256'];return json.loads(b)
def q(v):
    assert type(v) is list and len(v)==2 and all(type(n) is int for n in v) and v[1]>0
    f=F(*v);assert [f.numerator,f.denominator]==v;return f
def value(w):
    assert type(w) is int and 0<=w<1<<64
    exponent=(w>>52)&2047;mantissa=w&((1<<52)-1)
    assert exponent<2047 and (exponent or mantissa==0)
    return (-1 if w>>63 else 1)*F(mantissa if exponent==0 else mantissa+(1<<52))*F(2)**((exponent or 1)-1075)
def verify_proof(p):
    assert p['reference_scope']=='ORIGINAL fixed SOURCE A only; not A-exp-i-theta-reflection, UNIT, geometry or uniform domain'
    a,b=list(map(value,p['ORIGINAL_uint64'])),list(map(value,p['decoded_uint64']))
    eps=q(p['point_error_L1_bound']);assert eps>=0
    error=sum((abs(x-y) for x,y in zip(a,b)),F(0));assert error<=eps and q(p['measured_point_error_L1'])==error
    norm=sum(map(abs,a),F(0));lower=max(map(abs,a));margin=lower-eps
    assert (q(p['ORIGINAL_norm_L1']),q(p['ORIGINAL_norm_L2_lower']),q(p['strict_origin_margin']))==(norm,lower,margin)
    signs=all(x!=0 or y==0 and (ow>>63)==(dw>>63) for x,y,ow,dw in zip(a,b,p['ORIGINAL_uint64'],p['decoded_uint64']))
    assert p['ORIGINAL_zero_components_and_signs_preserved'] is signs
    if norm==0:assert p['point_relative_L1_bound'] is None
    else:assert q(p['point_relative_L1_bound'])==eps/norm
    if signs and margin>0:assert q(p['point_principal_phase_bound_rad'])==eps/margin
    else:assert p['point_principal_phase_bound_rad'] is None
    assert p['phase_quota_fits'] is None and p['uniform_SOURCE_error_L1'] is None and p['status']=='STOP'
r=json.loads((ROOT/PATH).read_bytes());assert r['task_id']=='AXIAL-TAGGED-SOURCE-ORIGINAL-POINT-BOUND-HOST-001'
pins=r['code_doc_sha256'];assert len(pins)==532
for path,h in pins.items():assert sha((ROOT/path).read_bytes())==h,path
t=payload(r);assert (t['tests_run'],t['errors'],t['failures'])==(4,0,0)
d=t['data'];a=d['audit'];req=d['request'];parent=payload(json.loads((ROOT/PARENT).read_bytes()))['data']
assert req['transport_receipt_sha256']==pins[PARENT]
assert digest(req['transport_INPUT'])==digest(parent['request'])
assert digest(req['transport_OUTPUT'])==digest(parent['audit'])
assert a['request_sha256']==digest(req) and a['point_bound_calls']==4
records=parent['request']['decoder_INPUT']['SOURCE_limb_records'];frames=parent['request']['frames'];outputs=parent['audit']['sources']
assert len(a['sources'])==len(records)==4
for new,row,frame,out in zip(a['sources'],records,frames,outputs):
    assert (new['case_name'],new['source_id'])==(row['case_name'],row['source_id'])==(out['case_name'],out['source_id'])
    wire=base64.b64decode(frame['frame_base64'],validate=True)
    assert wire==b'N3DZAD01'+bytes.fromhex(pins[DECODER])+bytes.fromhex(row['context_sha256'])+bytes.fromhex(digest(row))+base64.b64decode(row['hilo_le_base64'])
    assert sha(wire)==out['frame_sha256']==new['frame_sha256']
    assert new['encoder_row_sha256']==digest(row) and new['transport_OUTPUT_row_sha256']==digest(out)
    assert new['retained_whole_box_guard_admission_disproved'] is out['retained_whole_box_guard_admission_disproved']
    assert new['frozen_guard_admission_for_entire_box_proved'] is False and new['status']=='STOP'
    p=new['proof'];verify_proof(p)
    assert p['ORIGINAL_uint64']==[s['original_uint64'] for s in row['scalars']]
    assert p['decoded_uint64']==out['decoded_SOURCE_uint64']
    assert q(p['point_error_L1_bound'])==sum((q(old['encoding_error_abs'])+q(decoded['decode_error_abs']) for old,decoded in zip(row['scalars'],out['decoded_scalars'])),F(0))
assert len(d['new_POINT_controls'])==8
for control in d['new_POINT_controls']:verify_proof(control['proof'])
nonzero=d['new_POINT_controls'][4]['proof']
assert (nonzero['ORIGINAL_uint64'][0]>>63)==(nonzero['decoded_uint64'][0]>>63)==0
assert nonzero['ORIGINAL_zero_components_and_signs_preserved'] is False and nonzero['point_principal_phase_bound_rad'] is None
restored=d['new_POINT_controls'][2]['proof'];assert restored['ORIGINAL_zero_components_and_signs_preserved'] is True and restored['point_relative_L1_bound'] is None and restored['point_principal_phase_bound_rad'] is None
assert (len(d['batch_rejections']),len(d['typed_rejections']),len(d['model_rejections']))==(16,17,1)
m=d['missing'];assert (m['missing_cases'],m['missing_sources'],m['point_bound_calls'])==(17,19,0)
assert a['group_admissions']==a['decoder_calls']==a['native_RN_nodes']==a['old_numeric_suites_producers_reexecuted']==0
assert a['phase_quota_fits'] is None and a['uniform_SOURCE_error_L1'] is None and a['actual_scene_authenticated'] is False and a['full_SOURCE_reflected_reference_proved'] is False
assert len(a['proof_scope'])==38 and all(v is False for v in a['proof_scope'].values())
print(json.dumps({'status':'PASS','pins_verified':len(pins),'new_POINT_SOURCE_proofs':4,'new_rational_controls':8,
                  'same_sign_zero_to_nonzero_not_preserved':True,'origin_relative_and_phase':None,'SOURCE_full_quota_uniform_status':'STOP',
                  'decoder_and_native_calls':0},sort_keys=True))
