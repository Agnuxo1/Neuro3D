"""Opt-in CPU selected-word reader bound to SHA-retained synthetic scene INPUT."""
import base64
import hashlib
import json
import struct
import zlib
from copy import deepcopy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
MODEL='axial-retained-synthetic-scene-SOURCE-strict-selected-word-reader-CPU-v1'
FLAG='retained_synthetic_scene_SOURCE_words_decoded_CPU'
SCOPE='ORIGINAL SOURCE words only; no hi-lo encoding/rounding/geometry/material/field'
PARENT='coordinacion/respuestas/AXIAL-SOURCE-HELPER-ABI-BOUNDARY-HOST-001-CODEX.json'
PARENT_SHA='da7b75f85e9d258e9fc71a0967693ee744f388d9772ed3b421feb8fb4e9b91eb'
GRID='coordinacion/respuestas/AXIAL-SOURCE-BINARY64-GRID-INPUT-HOST-001-CODEX.json'
CONSUMER='coordinacion/respuestas/AXIAL-SOURCE-BINARY64-GRID-CONSUMER-HOST-001-CODEX.json'
REQUEST_KEYS={'model','scope','case_order','cases'}
CASE_KEYS={'context','GRID_INPUT','SOURCE_read_requests'}
SOURCE_KEYS={'source_id','source_phase_reference_id','terminal_reference_id','common_terminal_reference_id',
             'domain_source_sha256','width','words'}

def require(ok: bool,message: str) -> None:
    if not ok:raise ValueError(message)
def sha(b: bytes) -> str:return hashlib.sha256(b).hexdigest()
def digest(v: object) -> str:return sha(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def sealed(path: str,h: str) -> bytes:
    b=(ROOT/path).read_bytes();require(sha(b)==h,'sealed '+path);return b
def payload(r: dict) -> dict:
    t=r['test_run'];v=t.get('stdout_zlib_base64')
    if v is None:v=''.join(t['stdout_zlib_base64_chunks'])
    b=zlib.decompress(base64.b64decode(v,validate=True))
    require(len(b)==t['stdout_bytes'] and sha(b)==t['stdout_sha256'],'lossless payload')
    return json.loads(b)

def validate_SELECTED_word(word: int,width: int) -> dict:
    """Integer-only guard BEFORE byte interpretation; strict bool/float rejection."""
    require(type(width) is int and width in (32,64),'strict width int32/64')
    require(type(word) is int and 0<=word<1<<width,'strict unsigned selected word')
    mb,eb=(23,8) if width==32 else (52,11)
    exponent=(word>>mb)&((1<<eb)-1);mantissa=word&((1<<mb)-1)
    require(exponent<(1<<eb)-1,'finite selected word')
    require(exponent>0 or mantissa==0,'normal-or-zero selected word')
    return {'width':width,'word':word,'class':'zero' if exponent==0 else 'normal','sign':word>>(width-1)}

def interpret_SELECTED_CPU(word: int,width: int) -> dict:
    selected=validate_SELECTED_word(word,width)
    int_format,float_format=('<I','<f') if width==32 else ('<Q','<d')
    raw=struct.pack(int_format,word);value=struct.unpack(float_format,raw)[0]
    require(struct.pack(float_format,value)==raw,'CPU selected-word bit roundtrip incl signed zero')
    return {**selected,'little_endian_hex':raw.hex(),'float_hex':value.hex(),
            'roundtrip_uint':struct.unpack(int_format,struct.pack(float_format,value))[0],
            'new_word_reinterpretations':1,'new_arithmetic_or_RN_casts':0}

def load_retained() -> tuple[dict,dict,dict,dict]:
    parent=json.loads(sealed(PARENT,PARENT_SHA))
    require(parent['task_id']=='AXIAL-SOURCE-HELPER-ABI-BOUNDARY-HOST-001','parent ID')
    pins={**parent['code_doc_sha256'],PARENT:PARENT_SHA}
    require(len(pins)==503 and GRID in pins and CONSUMER in pins,'complete retained lineage')
    for path,h in pins.items():sealed(path,h)
    plans=payload(json.loads(sealed(GRID,pins[GRID])))['data']['synthetic_grid_INPUT_plans']
    cases=payload(json.loads(sealed(CONSUMER,pins[CONSUMER])))['data']
    require(set(plans)==set(cases['synthetic_valid']['cases']) and len(plans)==3,'three exact retained synthetic plans')
    false=parent['proof_scope'];require(len(false)==38 and all(v is False for v in false.values()),'frozen STOP scope')
    return plans,cases,pins,false

def make_synthetic_request() -> dict:
    """Explicit test factory, NEVER inferred from missing real INPUT."""
    plans,cases,_,_=load_retained()
    rows={}
    for name,plan in plans.items():
        sources=[]
        for src in plan['sources']:
            row={k:deepcopy(src[k]) for k in SOURCE_KEYS-{'words','width'}}
            row.update(width=64,words=deepcopy(src['ORIGINAL_source_uint64']));sources.append(row)
        rows[name]={'context':deepcopy(cases['synthetic_valid']['cases'][name]['context']),
                    'GRID_INPUT':deepcopy(plan),'SOURCE_read_requests':sources}
    return {'model':MODEL,'scope':SCOPE,'case_order':list(plans),'cases':rows}

def prepare_all_requests(request: dict,plans: dict,cases: dict) -> list:
    require(type(request) is dict and set(request)==REQUEST_KEYS,'exact explicit request schema')
    require(type(request['model']) is str and request['model']==MODEL and request['scope']==SCOPE,'explicit request model/scope')
    order=request['case_order']
    require(type(order) is list and all(type(n) is str for n in order) and len(order)==3 and
            len(set(order))==3 and set(order)==set(plans),'complete unique case order')
    require(type(request['cases']) is dict and set(request['cases'])==set(order),'complete batch coverage')
    staged=[]
    for name in order:
        row=request['cases'][name];plan=plans[name];case=cases['synthetic_valid']['cases'][name]
        require(type(row) is dict and set(row)==CASE_KEYS,'exact case schema')
        require(digest(row['context'])==digest(case['context']),'exact context/caps/gauges lineage')
        require(type(row['GRID_INPUT']) is dict and digest(row['GRID_INPUT'])==digest(plan),'exact full GRID INPUT incl original snapshot/domain/graph')
        sources=row['SOURCE_read_requests']
        require(type(sources) is list and len(sources)==len(plan['sources']),'complete ordered SOURCE requests')
        for src,expected in zip(sources,plan['sources']):
            require(type(src) is dict and set(src)==SOURCE_KEYS,'exact SOURCE read schema')
            for key in SOURCE_KEYS-{'width','words'}:
                require(type(src[key]) is str and src[key]==expected[key],'same SOURCE/gauges/domain')
            require(type(src['width']) is int and src['width']==64,'scene SOURCE ORIGINAL width strictly64')
            words=src['words']
            require(type(words) is list and len(words)==2,'two real/imag ORIGINAL words')
            for word in words:validate_SELECTED_word(word,64)
            require(digest(words)==digest(expected['ORIGINAL_source_uint64']),'same ORIGINAL source bit words incl signed zero')
            staged.append((name,deepcopy(src),digest(plan),digest(case['context'])))
    return staged

def audit_scene_SOURCE_reader_CPU(request: dict|None,*,model: str) -> dict:
    require(type(model) is str and model==MODEL,'explicit opt-in reader model')
    plans,cases,pins,false=load_retained()
    if request is None:
        real=cases['real_missing'];count=sum(len(c['context']['source_order']) for c in real['cases'].values())
        return {'model':MODEL,'variant':'missing_explicit_request','retained_missing_cases':len(real['cases']),
                'retained_missing_sources':count,FLAG:False,'new_word_reinterpretations':0,
                'group_admissions':0,'uniform_executed_SOURCE_error_L1':None,
                'actual_scene_domain_grid_authenticated':False,'encoder_graph_execution_authenticated':False,
                'proof_scope':deepcopy(false),'status':'STOP'}
    staged=prepare_all_requests(request,plans,cases) # ALL inputs before ANY interpretation
    rows=[]
    for name,src,plan_sha,ctx_sha in staged:
        old=next(s for s in cases['synthetic_valid']['cases'][name]['sources'] if s['source_id']==src['source_id'])
        words=[interpret_SELECTED_CPU(w,64) for w in src['words']]
        rows.append({'case_name':name,'source_id':src['source_id'],'context_sha256':ctx_sha,
                     'GRID_INPUT_plan_sha256':plan_sha,'SOURCE_request_sha256':digest(src),'words':words,
                     'retained_whole_box_guard_admission_disproved':old['retained_whole_box_guard_admission_disproved'],
                     'frozen_guard_admission_for_entire_box_proved':False,'status':'STOP'})
    return {'model':MODEL,'variant':'explicit_retained_synthetic_request','request_sha256':digest(request),
            FLAG:True,'sources':rows,'source_count':len(rows),'new_word_reinterpretations':sum(len(r['words']) for r in rows),
            'new_source_arithmetic_or_RN_casts':0,'old_producers_or_numeric_controls_reexecuted':0,
            'inherited_pins_verified':len(pins),'proof_scope':deepcopy(false),'group_admissions':0,
            'uniform_executed_SOURCE_error_L1':None,'phase_INPUT_quota_fits':None,
            'actual_scene_domain_grid_authenticated':False,'encoder_graph_execution_authenticated':False,
            'signed_zero_encoder_graph_equivalence_proved':False,
            'retained_synthetic_control_is_real_scene_INPUT':False,'status':'STOP'}
