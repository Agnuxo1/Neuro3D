"""Independent stdlib receipt/byte verifier. No imports from reader or frozen producers."""
import base64
import hashlib
import json
import struct
import zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT='coordinacion/respuestas/AXIAL-SCENE-SOURCE-SELECTED-WORD-READER-CPU-001-CODEX.json'
PARENT='coordinacion/respuestas/AXIAL-SOURCE-HELPER-ABI-BOUNDARY-HOST-001-CODEX.json'
PARENT_SHA='da7b75f85e9d258e9fc71a0967693ee744f388d9772ed3b421feb8fb4e9b91eb'
GRID='coordinacion/respuestas/AXIAL-SOURCE-BINARY64-GRID-INPUT-HOST-001-CODEX.json'
GC='coordinacion/respuestas/AXIAL-SOURCE-BINARY64-GRID-CONSUMER-HOST-001-CODEX.json'
MODEL='axial-retained-synthetic-scene-SOURCE-strict-selected-word-reader-CPU-v1'
SCOPE='ORIGINAL SOURCE words only; no hi-lo encoding/rounding/geometry/material/field'
FLAG='retained_synthetic_scene_SOURCE_words_decoded_CPU'
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def sealed(path,h):
    raw=(ROOT/path).read_bytes();assert sha(raw)==h,path;return json.loads(raw)
def payload(r):
    t=r['test_run'];encoded=t.get('stdout_zlib_base64')
    if encoded is None:encoded=''.join(t['stdout_zlib_base64_chunks'])
    raw=zlib.decompress(base64.b64decode(encoded,validate=True))
    assert len(raw)==t['stdout_bytes'] and sha(raw)==t['stdout_sha256']
    return json.loads(raw)
def verify_word(row):
    w=row['word'];width=row['width']
    assert type(w) is int and type(width) is int and width in (32,64) and 0<=w<1<<width
    mb,eb=(23,8) if width==32 else (52,11)
    exponent=(w>>mb)&((1<<eb)-1);mantissa=w&((1<<mb)-1)
    assert exponent<(1<<eb)-1 and (exponent>0 or mantissa==0)
    assert row['class']==('normal' if exponent else 'zero') and row['sign']==w>>(width-1)
    raw=w.to_bytes(width//8,'little')
    assert row['little_endian_hex']==raw.hex() and type(row['roundtrip_uint']) is int and row['roundtrip_uint']==w
    # Receipt identity check from exact hex representation; not backend/probe/encoder replay.
    assert struct.pack('<f' if width==32 else '<d',float.fromhex(row['float_hex']))==raw
    assert row['new_word_reinterpretations']==1 and row['new_arithmetic_or_RN_casts']==0
r=json.loads((ROOT/REPORT).read_bytes());assert r['task_id']=='AXIAL-SCENE-SOURCE-SELECTED-WORD-READER-CPU-001'
assert r['model']==MODEL and r['parent_receipt_sha256']==PARENT_SHA
parent=sealed(PARENT,PARENT_SHA);inherited={**parent['code_doc_sha256'],PARENT:PARENT_SHA}
assert len(inherited)==503 and len(r['code_doc_sha256'])==507
assert all(r['code_doc_sha256'].get(p)==h for p,h in inherited.items())
for path,h in r['code_doc_sha256'].items():
    assert sha((ROOT/path).read_bytes())==h,path
assert REPORT not in r['code_doc_sha256']
t=r['test_run'];assert t['rc']==0 and t['timed_out'] is False and t['threads']==1 and t['affinity_mask']==1 and t['hard_child_timeout_seconds']==60 and t['elapsed_seconds']<60
out=payload(r);assert (out['tests_run'],out['failures'],out['errors'])==(4,0,0)
d=out['data'];plans=payload(sealed(GRID,inherited[GRID]))['data']['synthetic_grid_INPUT_plans']
gc=payload(sealed(GC,inherited[GC]))['data'];expected={'model':MODEL,'scope':SCOPE,'case_order':list(plans),'cases':{}}
for name,plan in plans.items():
    sources=[]
    for source in plan['sources']:
        sources.append({k:source[k] for k in ('source_id','source_phase_reference_id','terminal_reference_id','common_terminal_reference_id','domain_source_sha256')}|
                       {'width':64,'words':source['ORIGINAL_source_uint64']})
    expected['cases'][name]={'context':gc['synthetic_valid']['cases'][name]['context'],'GRID_INPUT':plan,'SOURCE_read_requests':sources}
assert digest(d['request'])==digest(expected)
a=d['scene'];assert a['request_sha256']==digest(expected) and a[FLAG] is True
assert (a['source_count'],a['new_word_reinterpretations'],a['inherited_pins_verified'])==(4,8,503)
assert a['new_source_arithmetic_or_RN_casts']==a['old_producers_or_numeric_controls_reexecuted']==0
assert len(a['sources'])==4
expected_sources=[(name,s) for name in expected['case_order'] for s in expected['cases'][name]['SOURCE_read_requests']]
for row,(name,src) in zip(a['sources'],expected_sources):
    assert row['case_name']==name and row['source_id']==src['source_id']
    assert row['context_sha256']==digest(expected['cases'][name]['context']) and row['GRID_INPUT_plan_sha256']==digest(plans[name])
    assert row['SOURCE_request_sha256']==digest(src) and len(row['words'])==2
    for word,value in zip(row['words'],src['words']):assert word['word']==value and word['width']==64;verify_word(word)
    old=next(s for s in gc['synthetic_valid']['cases'][name]['sources'] if s['source_id']==src['source_id'])
    assert row['retained_whole_box_guard_admission_disproved'] is old['retained_whole_box_guard_admission_disproved']
    assert row['frozen_guard_admission_for_entire_box_proved'] is False and row['status']=='STOP'
assert sum(row['retained_whole_box_guard_admission_disproved'] is True for row in a['sources'])==2
assert sum(row['retained_whole_box_guard_admission_disproved'] is None for row in a['sources'])==2
m=d['missing'];assert m[FLAG] is False and m['new_word_reinterpretations']==0
assert (m['retained_missing_cases'],m['retained_missing_sources'])==(17,19)
assert len(gc['real_missing']['cases'])==17 and sum(len(c['context']['source_order']) for c in gc['real_missing']['cases'].values())==19
for result in (a,m):
    assert result['model']==MODEL and result['group_admissions']==0 and result['status']=='STOP'
    assert result['uniform_executed_SOURCE_error_L1'] is None
    assert result['proof_scope']==parent['proof_scope'] and len(result['proof_scope'])==38 and all(v is False for v in result['proof_scope'].values())
    assert result['actual_scene_domain_grid_authenticated'] is False and result['encoder_graph_execution_authenticated'] is False
assert a['phase_INPUT_quota_fits'] is None and a['signed_zero_encoder_graph_equivalence_proved'] is False and a['retained_synthetic_control_is_real_scene_INPUT'] is False
assert len(d['primitive_valid'])==16 and len({(x['width'],x['name']) for x in d['primitive_valid']})==16
for x in d['primitive_valid']:verify_word(x)
assert {x['name'] for x in d['primitive_valid']}=={'positive_zero','negative_zero','positive_one','negative_one','positive_min_normal','negative_min_normal','positive_max_finite','negative_max_finite'}
def primitive_admissible(word,width):
    if type(width) is not int or width not in (32,64) or type(word) is not int or not 0<=word<1<<width:return False
    mb,eb=(23,8) if width==32 else (52,11)
    exponent=(word>>mb)&((1<<eb)-1);mantissa=word&((1<<mb)-1)
    return exponent<(1<<eb)-1 and (exponent>0 or mantissa==0)
assert len(d['primitive_rejections'])==32 and all(x['reason'] and x['pack_calls']==0 and not primitive_admissible(x['word'],x['width']) for x in d['primitive_rejections'])
def request_admissible(q):
    if type(q) is not dict or set(q)!=set(expected) or q['model']!=MODEL or q['scope']!=SCOPE:return False
    order=q['case_order']
    if type(order) is not list or any(type(n) is not str for n in order) or len(order)!=3 or len(set(order))!=3 or set(order)!=set(plans):return False
    if type(q['cases']) is not dict or set(q['cases'])!=set(plans):return False
    for name in order:
        case=q['cases'][name];baseline=expected['cases'][name]
        if type(case) is not dict or set(case)!=set(baseline) or digest(case['context'])!=digest(baseline['context']) or digest(case['GRID_INPUT'])!=digest(baseline['GRID_INPUT']):return False
        sources=case['SOURCE_read_requests']
        if type(sources) is not list or len(sources)!=len(baseline['SOURCE_read_requests']):return False
        for source,old in zip(sources,baseline['SOURCE_read_requests']):
            if type(source) is not dict or set(source)!=set(old) or type(source['width']) is not int or source['width']!=64:return False
            if type(source['words']) is not list or len(source['words'])!=2 or not all(primitive_admissible(w,64) for w in source['words']):return False
            if digest(source)!=digest(old):return False
    return True
assert request_admissible(expected)
assert all(not request_admissible(x['request']) for x in d['batch_rejections'])
assert len(d['batch_rejections'])==16 and len({x['name'] for x in d['batch_rejections']})==16
assert all(x['reason'] and x['reader_calls']==0 and digest(x['request'])!=digest(expected) for x in d['batch_rejections'])
assert len(d['optin_rejections'])==3 and all(x['reason']=='explicit opt-in reader model' and x['loader_calls']==0 for x in d['optin_rejections'])
assert d['roundtrip_failure']=={'word':1<<63,'width':64,'reason':'CPU selected-word bit roundtrip incl signed zero'}
assert r['proof_scope']==parent['proof_scope'] and r['group_admissions']==0 and r['uniform_executed_SOURCE_error_L1'] is None
assert r['gpu_jobs']==r['blender_jobs']==r['encoder_calls']==0 and r['JEV']=='LOCAL fallback; security blocked; no retry or remote endorsement'
print(json.dumps({'status':'PASS','sha_pins_verified':507,'tests':4,'new_reader_words':24,'negative_contract_controls':52,'admissions':0,'all_general_proof_flags':False,'scope':'CPU selected words only; whole box remains STOP'},sort_keys=True))
