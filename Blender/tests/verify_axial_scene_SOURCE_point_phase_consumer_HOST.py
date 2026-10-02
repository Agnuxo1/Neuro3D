"""Independent receipt/point disk phase verifier; no consumer/encoder imports or replay."""
import base64
import hashlib
import json
import math
import zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
ID='AXIAL-SCENE-SOURCE-POINT-PHASE-CONSUMER-HOST-001'
REPORT='coordinacion/respuestas/'+ID+'-CODEX.json'
PARENT='coordinacion/respuestas/AXIAL-SCENE-SOURCE-HILO-ENCODER-CPU-001-CODEX.json'
PARENT_SHA='bf911d4e21af25caf476bb80f13c3511df401e886595979382d336334277450b'
MODEL='axial-retained-synthetic-SOURCE-point-phase-consumer-HOST-v1'
FLAG='retained_SOURCE_point_phase_bound_computed_HOST'
SCOPE='principal point phase to ORIGINAL SOURCE field only; no path/unit/material/uniform quota'
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def payload(r):
    t=r['test_run'];v=t.get('stdout_zlib_base64')
    if v is None:v=''.join(t['stdout_zlib_base64_chunks'])
    b=zlib.decompress(base64.b64decode(v,validate=True));assert len(b)==t['stdout_bytes'] and sha(b)==t['stdout_sha256']
    return json.loads(b)
def rational(v):
    assert type(v) is list and len(v)==2 and all(type(n) is int for n in v) and v[1]>0 and math.gcd(*v)==1
    return F(*v)
def word(w):
    assert type(w) is int and 0<=w<1<<64
    ex=(w>>52)&2047;ma=w&((1<<52)-1);assert ex<2047 and (ex or ma==0)
    return (-1 if w>>63 else 1)*F(ma+(1<<52) if ex else ma)*F(2)**((ex or 1)-1075)
def input_math(a,b,epsilon,signs):
    assert type(signs) is bool and type(a) is list and type(b) is list and len(a)==len(b)==2
    av,bv=list(map(word,a)),list(map(word,b));eps=rational(epsilon);assert eps>=0
    actual_signs=all(x!=0 or (aw>>63)==(bw>>63) for x,aw,bw in zip(av,a,b));assert signs is actual_signs
    measured=sum((abs(y-x) for x,y in zip(av,bv)),F(0));assert measured<=eps
    lower=max(map(abs,av));margin=lower-eps
    return eps,measured,lower,margin,actual_signs
def verify_proof(p,a,b,epsilon,signs):
    eps,measured,lower,margin,actual_signs=input_math(a,b,epsilon,signs)
    assert digest(p['ORIGINAL_uint64'])==digest(a) and digest(p['decoded_uint64'])==digest(b)
    assert rational(p['point_error_L1_radius'])==eps and rational(p['measured_point_error_L1'])==measured
    assert rational(p['ORIGINAL_norm_lower_bound'])==lower and rational(p['strict_origin_margin'])==margin
    assert p['ORIGINAL_zero_signs_preserved'] is actual_signs and p['scope']==SCOPE
    enclosed=actual_signs and margin>0;assert p['point_phase_enclosed'] is enclosed
    if enclosed:
        assert rational(p['point_principal_phase_bound_rad'])==eps/margin
        assert p['reason']=='point-only angle <= atan(eps/margin) <= eps/margin; no phase INPUT quota admission'
    else:
        assert p['point_principal_phase_bound_rad'] is None
        assert p['reason']==('retained ORIGINAL zero-sign FAIL STOP' if not actual_signs else 'no strict point disk margin to origin STOP')
    assert p['uniform_phase_bound_rad'] is p['phase_quota_fits'] is None and p['status']=='STOP'
r=json.loads((ROOT/REPORT).read_bytes());assert r['task_id']==ID and r['model']==MODEL and r['parent_receipt_sha256']==PARENT_SHA
raw=(ROOT/PARENT).read_bytes();assert sha(raw)==PARENT_SHA;parent=json.loads(raw)
pins={**parent['code_doc_sha256'],PARENT:PARENT_SHA};assert len(pins)==513 and len(r['code_doc_sha256'])==517
assert all(r['code_doc_sha256'].get(p)==h for p,h in pins.items()) and REPORT not in r['code_doc_sha256']
for p,h in r['code_doc_sha256'].items():assert sha((ROOT/p).read_bytes())==h,p
t=r['test_run'];assert t['rc']==0 and t['timed_out'] is False and t['threads']==t['affinity_mask']==1 and t['hard_child_timeout_seconds']==60 and t['elapsed_seconds']<60
o=payload(r);assert (o['tests_run'],o['failures'],o['errors'])==(4,0,0);d=o['data'];old=payload(parent)['data']
req={'model':MODEL,'scope':SCOPE,'SCENE_INPUT':old['request'],'encoder_receipt_sha256':PARENT_SHA,'SOURCE_point_records':old['audit']['sources']}
assert digest(d['request'])==digest(req)
a,m=d['audit'],d['missing'];assert a[FLAG] is True and m[FLAG] is False and a['model']==m['model']==MODEL
assert a['request_sha256']==digest(req) and (a['point_phase_computations'],a['point_phase_enclosed_count'],a['inherited_pins_verified'])==(4,4,513)
assert (m['missing_cases'],m['missing_sources'],m['point_phase_computations'])==(17,19,0)
assert a['encoder_calls']==a['native_RN_nodes']==a['old_numeric_controls_reexecuted']==0
assert len(a['sources'])==len(old['audit']['sources'])==4
for out,record in zip(a['sources'],old['audit']['sources']):
    assert (out['case_name'],out['source_id'])==(record['case_name'],record['source_id']) and out['SOURCE_encoder_row_sha256']==digest(record)
    src=record['scalars'];orig=[v['original_uint64'] for v in src];dec=[v['decoded_uint64'] for v in src]
    eps=sum((rational(v['point_error_bound_abs']) for v in src),F(0));assert eps==rational(record['point_complex_error_L1_bound'])
    verify_proof(out['proof'],orig,dec,[eps.numerator,eps.denominator],all(v['ORIGINAL_zero_sign_preserved'] for v in src))
    assert out['retained_whole_box_guard_admission_disproved'] is record['retained_whole_box_guard_admission_disproved']
    assert out['frozen_guard_admission_for_entire_box_proved'] is False and out['status']=='STOP'
assert sum(x['retained_whole_box_guard_admission_disproved'] is True for x in a['sources'])==2
for out in (a,m,r):
    assert out['proof_scope']==parent['proof_scope'] and len(out['proof_scope'])==38 and all(v is False for v in out['proof_scope'].values())
    assert out['group_admissions']==0 and out['uniform_executed_SOURCE_error_L1'] is out['uniform_phase_bound_rad'] is out['phase_quota_fits'] is None
assert a['actual_scene_authenticated'] is a['signed_zero_equivalence_proved'] is False
assert len(d['rational_controls'])==5
for row in d['rational_controls']:
    p=row['proof'];verify_proof(p,p['ORIGINAL_uint64'],p['decoded_uint64'],p['point_error_L1_radius'],p['ORIGINAL_zero_signs_preserved'])
assert d['rational_controls'][0]['proof']['point_principal_phase_bound_rad']==[0,1]
assert d['rational_controls'][1]['proof']['point_principal_phase_bound_rad']==[1,7]
assert all(x['proof']['point_principal_phase_bound_rad'] is None for x in d['rational_controls'][2:])
assert len(d['batch_stops'])==8
for bad in d['batch_stops']:
    q=bad['request'];assert bad['bound_calls']==0 and bad['reason']
    admissible=type(q) is dict and set(q)==set(req) and q['model']==MODEL and q['scope']==SCOPE and q['encoder_receipt_sha256']==PARENT_SHA and digest(q['SCENE_INPUT'])==digest(req['SCENE_INPUT']) and digest(q['SOURCE_point_records'])==digest(req['SOURCE_point_records'])
    assert not admissible
assert len(d['type_stops'])==8
for bad in d['type_stops']:
    failed=False
    try:input_math(bad['original_words'],bad['decoded_words'],bad['error_L1'],bad['sign_gate'])
    except AssertionError:failed=True
    assert failed and bad['reason']
assert len(d['optin_stops'])==3 and all(x['reason']=='explicit opt-in point phase model' and x['loader_calls']==0 for x in d['optin_stops'])
assert r['gpu_jobs']==r['blender_jobs']==r['encoder_calls']==r['native_RN_nodes']==0
assert r['JEV']=='LOCAL fallback; security blocked; no retry or remote endorsement'
print(json.dumps({'status':'PASS','sha_pins_verified':517,'tests':4,'point_bounds':4,'rational_controls':5,'negative_contract_controls':19,'encoder_calls':0,'native_RN_nodes':0,'origin_zero_sign_controls_STOP':3,'admissions':0,'uniform_phase':None,'scope':'principal SOURCE point only'},sort_keys=True))
