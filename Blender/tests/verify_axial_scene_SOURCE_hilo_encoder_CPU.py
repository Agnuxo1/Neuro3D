"""Independent exact rational + IEEE node/ABI/SHA receipt verification; no producer imports."""
import base64
import hashlib
import json
import struct
import zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
ID='AXIAL-SCENE-SOURCE-HILO-ENCODER-CPU-001'
REPORT='coordinacion/respuestas/'+ID+'-CODEX.json'
PARENT='coordinacion/respuestas/AXIAL-SCENE-SOURCE-SELECTED-WORD-READER-CPU-001-CODEX.json'
PARENT_SHA='fe4b52108413bb8f9e32b693f7691c9183f89d45b7ab2d838035d7d87a16cf54'
MODEL='axial-retained-synthetic-scene-SOURCE-hilo-point-encoder-CPU-v1'
FLAG='retained_synthetic_SOURCE_point_hilo_encoder_CPU_executed'
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def payload(r):
    t=r['test_run'];encoded=t.get('stdout_zlib_base64')
    if encoded is None:encoded=''.join(t['stdout_zlib_base64_chunks'])
    b=zlib.decompress(base64.b64decode(encoded,validate=True));assert len(b)==t['stdout_bytes'] and sha(b)==t['stdout_sha256']
    return json.loads(b)
def rational(v):
    assert type(v) is list and len(v)==2 and all(type(x) is int for x in v) and v[1]>0
    q=F(*v);assert [q.numerator,q.denominator]==v;return q
def bits(w,width,normal=True):
    assert type(width) is int and width in (32,64) and type(w) is int and 0<=w<1<<width
    m,e,b=(23,8,127) if width==32 else (52,11,1023)
    ex=(w>>m)&((1<<e)-1);ma=w&((1<<m)-1)
    assert ex<(1<<e)-1 and (not normal or ex or ma==0)
    return F((-1 if w>>(width-1) else 1)*(ma if ex==0 else ma+(1<<m)))*F(2)**((ex or 1)-b-m)
def midpoint(q,w,width,zs):
    v=bits(w,width);mag=w&((1<<(width-1))-1);sg=w>>(width-1)
    assert type(zs) is int and zs in (0,1)
    if q==0:assert mag==0 and sg==zs;return v
    assert sg==int(q<0)
    if mag==0:assert abs(q)<=F(2)**(-150 if width==32 else -1075);return v
    m,e=(23,8) if width==32 else (52,11)
    maximum=(((1<<e)-2)<<m)|((1<<m)-1)
    below=abs(bits(mag-1,width,False));now=abs(v)
    above=abs(bits(mag+1,width,False)) if mag<maximum else now+now-below
    lo,hi=(below+now)/2,(now+above)/2
    assert lo<=abs(q)<=hi and (abs(q) not in (lo,hi) or mag%2==0)
    return v
def scalar(r):
    w=r['original_uint64'];x=bits(w,64)
    hword,rword,lword,dword=[r[k] for k in ('high_uint32','residual_uint64','low_uint32','decoded_uint64')]
    h,rs,l,dec=bits(hword,32),bits(rword,64),bits(lword,32),bits(dword,64)
    expected=[('high_RN32',32,hword,x,w>>63),
              ('residual_RN64',64,rword,x-h,int(x==h==0 and w>>63==1 and hword>>31==0)),
              ('low_RN32',32,lword,rs,rword>>63),
              ('decode_RN64',64,dword,h+l,int(h==l==0 and hword>>31==lword>>31==1))]
    assert len(r['nodes'])==4
    for node,(name,width,word,exact,zs) in zip(r['nodes'],expected):
        assert (node['label'],node['width'],node['word'],node['zero_sign'])==(name,width,word,zs)
        assert rational(node['exact'])==exact and rational(node['value'])==midpoint(exact,word,width,zs)
        assert rational(node['delta'])==bits(word,width)-exact
    enc=abs(h+l-x);de=abs(dec-h-l);err=abs(dec-x)
    assert rational(r['encoding_error_abs'])==enc and rational(r['decode_error_abs'])==de and rational(r['decoded_error_abs'])==err
    assert rational(r['point_error_bound_abs'])==enc+de and err<=enc+de
    raw=struct.pack('<II',hword,lword);assert r['hilo_le_hex']==raw.hex() and r['hilo_le_sha256']==sha(raw)
    preserved=not (x==0 and (dword>>63)!=(w>>63))
    assert r['ORIGINAL_zero_sign_preserved'] is preserved and r['ORIGINAL_bitwise_roundtrip'] is (dword==w)
    assert (r['new_RN32_casts'],r['new_RN64_subtractions'],r['new_RN64_decode_adds'])==(2,1,1) and r['zero_canonicalization_performed'] is False
    assert r['status']==('POINT_EXECUTED_BOX_STOP' if preserved else 'ORIGINAL_ZERO_SIGN_FAIL_STOP')
r=json.loads((ROOT/REPORT).read_bytes());assert r['task_id']==ID and r['model']==MODEL and r['parent_receipt_sha256']==PARENT_SHA
praw=(ROOT/PARENT).read_bytes();assert sha(praw)==PARENT_SHA;p=json.loads(praw)
inherited={**p['code_doc_sha256'],PARENT:PARENT_SHA};assert len(inherited)==508 and len(r['code_doc_sha256'])==512
assert all(r['code_doc_sha256'].get(k)==h for k,h in inherited.items()) and REPORT not in r['code_doc_sha256']
for path,h in r['code_doc_sha256'].items():assert sha((ROOT/path).read_bytes())==h,path
t=r['test_run'];assert t['rc']==0 and t['timed_out'] is False and t['threads']==t['affinity_mask']==1 and t['hard_child_timeout_seconds']==60 and t['elapsed_seconds']<60
out=payload(r);assert (out['tests_run'],out['failures'],out['errors'])==(4,0,0);d=out['data']
parent_data=payload(p)['data'];req=parent_data['request'];assert digest(d['request'])==digest(req)
a=d['audit'];m=d['missing']
assert a['model']==m['model']==MODEL and a[FLAG] is True and m[FLAG] is False
assert a['request_sha256']==digest(req) and (a['source_count'],a['inherited_pins_verified'])==(4,508)
assert (a['new_RN32_casts'],a['new_RN64_subtractions'],a['new_RN64_decode_adds'])==(16,8,8)
assert (m['missing_cases'],m['missing_sources'],m['new_RN32_casts'],m['new_RN64_subtractions'],m['new_RN64_decode_adds'])==(17,19,0,0,0)
expected=[(name,s) for name in req['case_order'] for s in req['cases'][name]['SOURCE_read_requests']]
assert len(a['sources'])==4
for row,(name,source) in zip(a['sources'],expected):
    assert row['case_name']==name and row['source_id']==source['source_id']
    assert row['context_sha256']==digest(req['cases'][name]['context']) and row['GRID_INPUT_plan_sha256']==digest(req['cases'][name]['GRID_INPUT'])
    assert row['SOURCE_request_sha256']==digest(source) and len(row['scalars'])==2
    for record,w in zip(row['scalars'],source['words']):assert record['original_uint64']==w;scalar(record)
    limbs=[record[k] for record in row['scalars'] for k in ('high_uint32','low_uint32')]
    assert row['limb_uint32']==limbs
    raw=base64.b64decode(row['hilo_le_base64'],validate=True);assert raw==struct.pack('<IIII',*limbs) and len(raw)==16 and sha(raw)==row['hilo_le_sha256']
    assert rational(row['point_complex_error_L1_bound'])==sum((rational(v['point_error_bound_abs']) for v in row['scalars']),F(0))
    old=next(x for x in parent_data['scene']['sources'] if x['case_name']==name and x['source_id']==source['source_id'])
    assert row['retained_whole_box_guard_admission_disproved'] is old['retained_whole_box_guard_admission_disproved']
    assert row['frozen_guard_admission_for_entire_box_proved'] is False and row['status']=='STOP'
assert sum(row['retained_whole_box_guard_admission_disproved'] is True for row in a['sources'])==2
for result in (a,m,r):
    assert result['proof_scope']==p['proof_scope'] and len(result['proof_scope'])==38 and all(v is False for v in result['proof_scope'].values())
    assert result['group_admissions']==0 and result['uniform_executed_SOURCE_error_L1'] is None and result['phase_bound_rad'] is None
assert a['actual_scene_authenticated'] is a['GPU_runtime_authenticated'] is a['signed_zero_graph_equivalence_proved'] is False
assert a['old_producers_or_numeric_controls_reexecuted']==0
assert len(d['primitive_valid'])==2
for row in d['primitive_valid']:scalar(row)
tie,zero=d['primitive_valid'];assert tie['original_uint64']==0x3ff0000010000000 and tie['high_uint32']==0x3f800000
assert zero['original_uint64']==1<<63 and zero['decoded_uint64']==0 and zero['status']=='ORIGINAL_ZERO_SIGN_FAIL_STOP' and zero['decoded_error_abs']==[0,1]
stops=d['primitive_stops'];assert len(stops)==8
assert [(x['name'],x['reason']) for x in stops[:3]]==[('selected_subnormal_high','normal-or-zero selected output'),('high_overflow','native high_RN32 overflow STOP'),('wrong_tie_cast','RN-even midpoint failed')]
assert all(x['residual_calls']==0 for x in stops[:3]) and sum(x['native_high_attempts'] for x in stops[:3])==2
assert bits(stops[0]['original_uint64'],64)==F(2)**-127 and bits(stops[1]['original_uint64'],64)==F(2)**128
for bad in stops[3:]:
    w=bad['original_uint64'];assert type(w) is not int or not 0<=w<1<<64
    assert bad['cast_calls']==0 and bad['reason']=='typed unsigned IEEE word'
assert len(d['batch_stops'])==8 and all(x['encoder_calls']==0 and x['reason'] and digest(x['request'])!=digest(req) for x in d['batch_stops'])
assert len(d['optin_stops'])==3 and all(x['loader_calls']==0 and x['reason']=='explicit opt-in encoder model' for x in d['optin_stops'])
assert len(d['guard_stops'])==6
for bad in d['guard_stops']:
    failed=False
    try:midpoint(rational(bad['exact']),bad['word'],bad['width'],bad['zero_sign'])
    except AssertionError:failed=True
    assert failed and bad['reason']
assert r['gpu_jobs']==r['blender_jobs']==0 and r['old_numeric_producer_calls']==0
assert r['JEV']=='LOCAL fallback; security blocked; no retry or remote endorsement'
print(json.dumps({'status':'PASS','sha_pins_verified':512,'tests':4,'scene_RN_nodes':32,'primitive_successful_RN_nodes':8,'native_high_rejected_attempts':2,'negative_contract_controls':25,'ORIGINAL_negative_zero':'FAIL_STOP_preserved','admissions':0,'scope':'new CPU point encoder only; whole boxes STOP'},sort_keys=True))
