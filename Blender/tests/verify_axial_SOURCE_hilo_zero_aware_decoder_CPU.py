"""Independent retained-byte and exact-rational verifier; no production imports."""
import base64
import hashlib
import json
import zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
RECEIPT=ROOT/'coordinacion/respuestas/AXIAL-SOURCE-HILO-ZERO-AWARE-DECODER-CPU-001-CODEX.json'
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(x):return sha(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def payload(r):
    t=r['test_run'];v=t.get('stdout_zlib_base64') or ''.join(t['stdout_zlib_base64_chunks'])
    b=zlib.decompress(base64.b64decode(v,validate=True))
    assert len(b)==t['stdout_bytes'] and sha(b)==t['stdout_sha256']
    return json.loads(b)
def value(w,width):
    assert type(w) is int and 0<=w<1<<width
    mb,eb,bias={32:(23,8,127),64:(52,11,1023)}[width]
    ex=(w>>mb)&((1<<eb)-1);ma=w&((1<<mb)-1)
    assert ex<(1<<eb)-1
    return (-1 if w>>(width-1) else 1)*F(ma if ex==0 else ma+(1<<mb))*F(2)**((ex or 1)-bias-mb)
def q(x):
    assert type(x) is list and len(x)==2 and all(type(v) is int for v in x) and x[1]>0
    f=F(*x);assert [f.numerator,f.denominator]==x;return f
def verify_scalar(s):
    high,low,w=s['high_uint32'],s['low_uint32'],s['decoded_uint64']
    h,l,d=value(high,32),value(low,32),value(w,64)
    for x in (high,low):
        assert ((x>>23)&255)>0 or (x&0x7fffffff)==0
    raw=high.to_bytes(4,'little')+low.to_bytes(4,'little')
    assert s['hilo_le_hex']==raw.hex() and s['hilo_le_sha256']==sha(raw)
    assert q(s['exact_limb_sum'])==h+l and q(s['decoded_value'])==d and q(s['decode_error_abs'])==abs(d-h-l)
    assert s['old_RN_add_graph_equivalence_proved'] is False
    if h==l==0:
        assert s['branch']=='BOTH_ZERO_HIGH_SIGN' and w==(high>>31)<<63
        assert s['new_native_RN64_adds']==0 and s['new_zero_branch_selections']==1
    else:
        assert s['branch']=='RN64_ADD' and s['new_native_RN64_adds']==1 and s['new_zero_branch_selections']==0
        target=h+l;mag=w&0x7fffffffffffffff
        if target==0:assert w==0
        else:
            assert (w>>63)==int(target<0) and mag>0
            left=(abs(value(mag-1,64))+abs(d))/2
            right=(abs(value(mag+1,64))+abs(d))/2
            assert left<=abs(target)<=right
            if abs(target) in (left,right):assert mag%2==0
    if 'original_uint64' in s:
        original=value(s['original_uint64'],64);eps=q(s['encoding_error_abs'])+q(s['decode_error_abs'])
        assert q(s['encoding_error_abs'])==abs(h+l-original)
        assert q(s['point_error_bound_abs'])==eps and abs(d-original)<=eps
        assert s['ORIGINAL_zero_sign_preserved'] is (original!=0 or (w>>63)==(s['original_uint64']>>63))
        assert s['ORIGINAL_bitwise_roundtrip'] is (w==s['original_uint64'])
r=json.loads(RECEIPT.read_bytes());assert r['task_id']=='AXIAL-SOURCE-HILO-ZERO-AWARE-DECODER-CPU-001'
pins=r['code_doc_sha256'];assert len(pins)==522
for path,h in pins.items():assert sha((ROOT/path).read_bytes())==h,path
p=payload(r);assert (p['tests_run'],p['errors'],p['failures'])==(4,0,0);data=p['data'];a=data['audit']
oldpath='coordinacion/respuestas/AXIAL-SCENE-SOURCE-HILO-ENCODER-CPU-001-CODEX.json'
old=payload(json.loads((ROOT/oldpath).read_bytes()))['data']
req=data['request']
assert digest(req['SCENE_INPUT'])==digest(old['request'])
assert digest(req['SOURCE_limb_records'])==digest(old['audit']['sources'])
assert req['encoder_receipt_sha256']==pins[oldpath]
assert a['request_sha256']==digest(req)
assert (a['new_native_RN64_adds'],a['new_zero_branch_selections'],a['encoder_calls'],a['old_numeric_controls_reexecuted'])==(4,4,0,0)
assert a['group_admissions']==0 and a['phase_quota_fits'] is None and a['uniform_executed_SOURCE_error_L1'] is None
assert a['actual_scene_authenticated'] is False and a['old_RN_add_graph_equivalence_proved'] is False
assert len(a['proof_scope'])==38 and all(x is False for x in a['proof_scope'].values())
assert len(a['sources'])==4
for new,prior in zip(a['sources'],old['audit']['sources']):
    assert (new['case_name'],new['source_id'])==(prior['case_name'],prior['source_id'])
    assert new['encoder_row_sha256']==digest(prior) and new['hilo_le_sha256']==prior['hilo_le_sha256']
    assert new['retained_whole_box_guard_admission_disproved'] is prior['retained_whole_box_guard_admission_disproved']
    assert new['frozen_guard_admission_for_entire_box_proved'] is False and new['status']=='STOP'
    for s,previous in zip(new['scalars'],prior['scalars']):
        verify_scalar(s)
        assert (s['original_uint64'],s['retained_old_decoded_uint64'])==(previous['original_uint64'],previous['decoded_uint64'])
        assert s['retained_old_zero_sign_preserved'] is previous['ORIGINAL_zero_sign_preserved']
    assert q(new['point_complex_error_L1_bound'])==sum((q(s['point_error_bound_abs']) for s in new['scalars']),F(0))
for s in data['controls']:verify_scalar(s)
assert len(data['controls'])==8
nz=data['retained_negative_zero'];assert digest(nz['old'])==digest(old['primitive_valid'][1]);verify_scalar(nz['new'])
assert nz['old']['ORIGINAL_zero_sign_preserved'] is False and nz['old']['status']=='ORIGINAL_ZERO_SIGN_FAIL_STOP'
assert nz['old']['decoded_uint64']==0 and nz['new']['decoded_uint64']==nz['old']['original_uint64']==1<<63
assert nz['new']['hilo_le_sha256']==nz['old']['hilo_le_sha256']
assert nz['phase_at_origin'] is None and nz['old_failure_preserved'] is True
missing=data['missing'];assert (missing['missing_cases'],missing['missing_sources'],missing['new_native_RN64_adds'])==(17,19,0)
assert (len(data['batch_rejections']),len(data['model_rejections']),len(data['primitive_rejections']),len(data['mock_output_rejections']))==(12,1,18,4)
print(json.dumps({'status':'PASS','pins_verified':len(pins),'scene_new_RN64_adds':4,'scene_zero_selections':4,
                  'new_controls':8,'retained_minus_zero_old_FAIL_preserved':True,'new_point_minus_zero_restored':True,
                  'whole_box_and_phase_quota_status':'STOP','old_graph_equivalence':False},sort_keys=True))
