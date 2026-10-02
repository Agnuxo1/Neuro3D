"""Opt-in point hi-lo encoder for SHA-retained synthetic SOURCE INPUT; not a box guard."""
import base64
import hashlib
import importlib.util
import json
import struct
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
MODEL='axial-retained-synthetic-scene-SOURCE-hilo-point-encoder-CPU-v1'
FLAG='retained_synthetic_SOURCE_point_hilo_encoder_CPU_executed'
PARENT='coordinacion/respuestas/AXIAL-SCENE-SOURCE-SELECTED-WORD-READER-CPU-001-CODEX.json'
PARENT_SHA='fe4b52108413bb8f9e32b693f7691c9183f89d45b7ab2d838035d7d87a16cf54'
READER='Blender/benchmarks/capacity_audit/axial_scene_SOURCE_selected_word_reader_CPU_v1.py'
READER_SHA='a08508d79d850f38a393c6f2923e01c188ba48dea558958e86658c24b221a3cf'
def require(ok,message):
    if not ok:raise ValueError(message)
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def pair(q):return [q.numerator,q.denominator]
def sealed(path,h):
    b=(ROOT/path).read_bytes();require(sha(b)==h,'sealed '+path);return b
# Our own passive reader only. No frozen encoder/guard/cast/writer imports.
sealed(READER,READER_SHA)
spec=importlib.util.spec_from_file_location('own_strict_scene_reader',ROOT/READER)
reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
def load_retained():
    parent=json.loads(sealed(PARENT,PARENT_SHA));require(parent['task_id']=='AXIAL-SCENE-SOURCE-SELECTED-WORD-READER-CPU-001','parent ID')
    pins={**parent['code_doc_sha256'],PARENT:PARENT_SHA};require(len(pins)==508,'complete inherited pins')
    for p,h in pins.items():sealed(p,h)
    plans=reader.payload(json.loads(sealed(reader.GRID,pins[reader.GRID])))['data']['synthetic_grid_INPUT_plans']
    cases=reader.payload(json.loads(sealed(reader.CONSUMER,pins[reader.CONSUMER])))['data']
    false=parent['proof_scope'];require(len(false)==38 and all(v is False for v in false.values()),'unchanged STOP scope')
    return plans,cases,pins,false
def ieee_rational(word,width,*,selected=True):
    require(type(width) is int and width in (32,64) and type(word) is int and 0<=word<1<<width,'typed unsigned IEEE word')
    mb,eb,bias=(23,8,127) if width==32 else (52,11,1023)
    e=(word>>mb)&((1<<eb)-1);m=word&((1<<mb)-1)
    require(e<(1<<eb)-1,'finite selected output')
    if selected:require(e>0 or m==0,'normal-or-zero selected output')
    return (-1 if word>>(width-1) else 1)*F(m if e==0 else m+(1<<mb))*F(2)**((1 if e==0 else e)-bias-mb)
def check_RN(exact,word,width,zero_sign):
    require(type(exact) is F and type(zero_sign) is int and zero_sign in (0,1),'typed rational and zero sign')
    value=ieee_rational(word,width);sign=word>>(width-1);magnitude=word&((1<<(width-1))-1)
    if exact==0:
        require(magnitude==0 and sign==zero_sign,'RN exact-zero sign');return value
    require(sign==int(exact<0),'RN sign')
    magnitude_value=abs(value);a=abs(exact)
    if magnitude==0:
        require(a<=F(2)**(-150 if width==32 else -1075),'RN zero midpoint');return value
    lower=abs(ieee_rational(magnitude-1,width,selected=False))
    mb,eb=(23,8) if width==32 else (52,11)
    maximum=(((1<<eb)-2)<<mb)|((1<<mb)-1)
    upper=abs(ieee_rational(magnitude+1,width,selected=False)) if magnitude<maximum else magnitude_value+(magnitude_value-lower)
    left,right=(lower+magnitude_value)/2,(magnitude_value+upper)/2;even=magnitude%2==0
    require((a>left or (a==left and even)) and (a<right or (a==right and even)),'RN-even midpoint failed')
    return value
def as_float(word,width):return struct.unpack('<f' if width==32 else '<d',word.to_bytes(width//8,'little'))[0]
def as_word(value,width):return int.from_bytes(struct.pack('<f' if width==32 else '<d',value),'little')
def native_cast32(value):return as_word(value,32)
def native_subtract(a,b):return as_word(a-b,64)
def native_add(a,b):return as_word(a+b,64)
def encode_scalar(original_word):
    # Typed normal-or-zero INPUT before first native op; every new selected output checked.
    x=ieee_rational(original_word,64);xf=as_float(original_word,64);nodes=[]
    def node(label,exact,width,zero_sign,operation):
        try:word=operation()
        except (OverflowError,struct.error) as e:raise ValueError('native '+label+' overflow STOP') from e
        q=check_RN(exact,word,width,zero_sign)
        nodes.append({'label':label,'width':width,'word':word,'exact':pair(exact),'value':pair(q),'delta':pair(q-exact),'zero_sign':zero_sign})
        return word,q
    high,h=node('high_RN32',x,32,original_word>>63,lambda:native_cast32(xf))
    residual,r=node('residual_RN64',x-h,64,int(x==h==0 and original_word>>63==1 and high>>31==0),
                    lambda:native_subtract(xf,as_float(high,32)))
    low,l=node('low_RN32',r,32,residual>>63,lambda:native_cast32(as_float(residual,64)))
    decoded,d=node('decode_RN64',h+l,64,int(h==l==0 and high>>31==low>>31==1),
                   lambda:native_add(as_float(high,32),as_float(low,32)))
    encoding=abs(h+l-x);decode=abs(d-h-l);observed=abs(d-x)
    require(observed<=encoding+decode,'point error enclosure')
    zero_preserved=not (x==0 and (decoded>>63)!=(original_word>>63))
    raw=struct.pack('<II',high,low)
    return {'original_uint64':original_word,'high_uint32':high,'residual_uint64':residual,'low_uint32':low,
            'decoded_uint64':decoded,'nodes':nodes,'hilo_le_hex':raw.hex(),'hilo_le_sha256':sha(raw),
            'encoding_error_abs':pair(encoding),'decode_error_abs':pair(decode),'decoded_error_abs':pair(observed),
            'point_error_bound_abs':pair(encoding+decode),'ORIGINAL_zero_sign_preserved':zero_preserved,
            'ORIGINAL_bitwise_roundtrip':decoded==original_word,
            'new_RN32_casts':2,'new_RN64_subtractions':1,'new_RN64_decode_adds':1,
            'zero_canonicalization_performed':False,'status':'POINT_EXECUTED_BOX_STOP' if zero_preserved else 'ORIGINAL_ZERO_SIGN_FAIL_STOP'}
def audit_scene_encoder_CPU(request,*,model):
    require(type(model) is str and model==MODEL,'explicit opt-in encoder model')
    plans,cases,pins,false=load_retained()
    if request is None:
        rows=cases['real_missing']['cases']
        return {'model':MODEL,FLAG:False,'missing_cases':len(rows),'missing_sources':sum(len(c['context']['source_order']) for c in rows.values()),
                'new_RN32_casts':0,'new_RN64_subtractions':0,'new_RN64_decode_adds':0,
                'group_admissions':0,'uniform_executed_SOURCE_error_L1':None,'phase_bound_rad':None,
                'proof_scope':deepcopy(false),'status':'STOP'}
    # Existing INPUT schema's reader model remains explicit; encoder model is independent opt-in.
    staged=reader.prepare_all_requests(request,plans,cases) # ALL INPUT before ANY encode
    results=[]
    for name,source,plan_sha,ctx_sha in staged:
        scalars=[encode_scalar(w) for w in source['words']]
        old=next(s for s in cases['synthetic_valid']['cases'][name]['sources'] if s['source_id']==source['source_id'])
        limbs=[v[k] for v in scalars for k in ('high_uint32','low_uint32')]
        raw=struct.pack('<IIII',*limbs)
        results.append({'case_name':name,'source_id':source['source_id'],'context_sha256':ctx_sha,
                        'GRID_INPUT_plan_sha256':plan_sha,'SOURCE_request_sha256':digest(source),'scalars':scalars,
                        'limb_uint32':limbs,'hilo_le_base64':base64.b64encode(raw).decode(),'hilo_le_sha256':sha(raw),
                        'point_complex_error_L1_bound':pair(sum((F(*v['point_error_bound_abs']) for v in scalars),F(0))),
                        'retained_whole_box_guard_admission_disproved':old['retained_whole_box_guard_admission_disproved'],
                        'frozen_guard_admission_for_entire_box_proved':False,'status':'STOP'})
    return {'model':MODEL,FLAG:True,'request_sha256':digest(request),'sources':results,'source_count':len(results),
            'new_RN32_casts':4*len(results),'new_RN64_subtractions':2*len(results),'new_RN64_decode_adds':2*len(results),
            'inherited_pins_verified':len(pins),'old_producers_or_numeric_controls_reexecuted':0,
            'group_admissions':0,'uniform_executed_SOURCE_error_L1':None,'phase_bound_rad':None,
            'actual_scene_authenticated':False,'GPU_runtime_authenticated':False,'signed_zero_graph_equivalence_proved':False,
            'proof_scope':deepcopy(false),'status':'STOP'}
