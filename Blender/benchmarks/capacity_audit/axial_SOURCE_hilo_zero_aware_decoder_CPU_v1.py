"""Explicit zero-aware SOURCE hi-lo decoder. A new graph, not old RN-add equivalence."""
import base64
import hashlib
import json
import struct
import zlib
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
MODEL='axial-SOURCE-hilo-high-zero-sign-decoder-CPU-v1'
SCOPE='POINT SOURCE limbs; both-zero selects HIGH sign; otherwise guarded binary64 RN-even sum'
FLAG='new_zero_aware_SOURCE_point_decoder_CPU_executed'
PARENT='coordinacion/respuestas/AXIAL-SCENE-SOURCE-POINT-PHASE-CONSUMER-HOST-001-CODEX.json'
PARENT_SHA='e80b81c1c76f38ddd3243790f7ec63fbd8d0dd4412a40aaa0b12ddcc96a71e9d'
ENCODER='coordinacion/respuestas/AXIAL-SCENE-SOURCE-HILO-ENCODER-CPU-001-CODEX.json'
ENCODER_SHA='bf911d4e21af25caf476bb80f13c3511df401e886595979382d336334277450b'
def require(ok,message):
    if not ok:raise ValueError(message)
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def pair(q):return [q.numerator,q.denominator]
def rational(v):
    require(type(v) is list and len(v)==2 and all(type(n) is int for n in v),'typed rational')
    require(v[1]>0 and v[0]>=0,'nonnegative rational')
    q=F(*v);require(pair(q)==v,'canonical rational');return q
def word_value(w,width,*,selected=True):
    require(type(width) is int and width in (32,64) and type(w) is int and 0<=w<1<<width,'typed IEEE word')
    mb,eb,bias=(23,8,127) if width==32 else (52,11,1023)
    e=(w>>mb)&((1<<eb)-1);m=w&((1<<mb)-1)
    require(e<(1<<eb)-1 and (not selected or e>0 or m==0),'finite normal-or-zero selected word')
    return (-1 if w>>(width-1) else 1)*F(m if e==0 else m+(1<<mb))*F(2)**((e or 1)-bias-mb)
def guard_sum(exact,w):
    value=word_value(w,64);mag=w&((1<<63)-1)
    if exact==0:require(w==0,'RN cancellation must yield plus zero');return value
    require(w>>63==int(exact<0),'RN sign')
    require(mag>0,'nonzero binary32 sum cannot underflow binary64')
    left=(abs(word_value(mag-1,64,selected=False))+abs(value))/2
    right=(abs(word_value(mag+1,64,selected=False))+abs(value))/2
    a=abs(exact);even=(mag&1)==0
    require((a>left or a==left and even) and (a<right or a==right and even),'RN-even midpoint')
    return value
def as_float32(w):return struct.unpack('<f',w.to_bytes(4,'little'))[0]
def native_add64(high,low):
    return int.from_bytes(struct.pack('<d',as_float32(high)+as_float32(low)),'little')
def decode_scalar(high,low):
    # Reject BOTH inputs before a native operation. No ORIGINAL-dependent sign patch.
    h,l=word_value(high,32),word_value(low,32);exact=h+l
    if h==l==0:
        w=(high>>31)<<63;value=word_value(w,64);branch='BOTH_ZERO_HIGH_SIGN'
        require((w>>63)==(high>>31) and value==exact,'explicit zero selection')
        adds=0
    else:
        w=native_add64(high,low);value=guard_sum(exact,w);branch='RN64_ADD';adds=1
    raw=struct.pack('<II',high,low)
    return {'high_uint32':high,'low_uint32':low,'hilo_le_hex':raw.hex(),'hilo_le_sha256':sha(raw),
            'decoded_uint64':w,'exact_limb_sum':pair(exact),'decoded_value':pair(value),
            'decode_error_abs':pair(abs(value-exact)),'branch':branch,'new_native_RN64_adds':adds,
            'new_zero_branch_selections':1-adds,'old_RN_add_graph_equivalence_proved':False}
def payload(r):
    t=r['test_run'];v=t.get('stdout_zlib_base64')
    if v is None:v=''.join(t['stdout_zlib_base64_chunks'])
    b=zlib.decompress(base64.b64decode(v,validate=True))
    require(len(b)==t['stdout_bytes'] and sha(b)==t['stdout_sha256'],'lossless retained payload')
    return json.loads(b)
def load_retained():
    raw=(ROOT/PARENT).read_bytes();require(sha(raw)==PARENT_SHA,'parent receipt SHA')
    parent=json.loads(raw);require(parent['task_id']=='AXIAL-SCENE-SOURCE-POINT-PHASE-CONSUMER-HOST-001','parent ID')
    pins={**parent['code_doc_sha256'],PARENT:PARENT_SHA};require(len(pins)==518,'complete inherited pins')
    for p,h in pins.items():require(sha((ROOT/p).read_bytes())==h,'sealed '+p)
    require(pins[ENCODER]==ENCODER_SHA,'same frozen encoder')
    enc=json.loads((ROOT/ENCODER).read_bytes());data=payload(enc)['data'];false=parent['proof_scope']
    require(len(false)==38 and all(v is False for v in false.values()),'general proof scope remains STOP')
    require(data['audit']['group_admissions']==0,'point encoder not admission')
    return data,pins,false
def make_synthetic_request():
    data,_,_=load_retained()
    return {'model':MODEL,'scope':SCOPE,'encoder_receipt_sha256':ENCODER_SHA,
            'SCENE_INPUT':deepcopy(data['request']),'SOURCE_limb_records':deepcopy(data['audit']['sources'])}
def prepare_all(request,data):
    require(type(request) is dict and set(request)=={'model','scope','encoder_receipt_sha256','SCENE_INPUT','SOURCE_limb_records'},'exact decoder INPUT')
    require(type(request['model']) is str and request['model']==MODEL and request['scope']==SCOPE,'explicit changed graph')
    require(request['encoder_receipt_sha256']==ENCODER_SHA,'retained encoder ID')
    require(digest(request['SCENE_INPUT'])==digest(data['request']),'complete scene/GRID/context/gauges/ORIGINAL')
    rows=request['SOURCE_limb_records'];expected=data['audit']['sources']
    require(type(rows) is list and len(rows)==len(expected)==4,'complete ordered SOURCE limbs')
    staged=[]
    for row,old in zip(rows,expected):
        require(type(row) is dict and digest(row)==digest(old),'sealed complete SOURCE row')
        case=request['SCENE_INPUT']['cases'][row['case_name']]
        source=next(s for s in case['SOURCE_read_requests'] if s['source_id']==row['source_id'])
        scalars=row['scalars'];require(len(scalars)==2,'complex SOURCE scalar count')
        require(digest([v['original_uint64'] for v in scalars])==digest(source['words']),'same ORIGINAL bits')
        limbs=[v[k] for v in scalars for k in ('high_uint32','low_uint32')]
        require(digest(limbs)==digest(row['limb_uint32']),'same four-limb ABI')
        for w in limbs:word_value(w,32)
        raw=struct.pack('<IIII',*limbs)
        require(base64.b64encode(raw).decode()==row['hilo_le_base64'] and sha(raw)==row['hilo_le_sha256'],'unchanged sixteen-byte ABI')
        for v in scalars:
            original=word_value(v['original_uint64'],64)
            h,l=word_value(v['high_uint32'],32),word_value(v['low_uint32'],32)
            require(rational(v['encoding_error_abs'])==abs(h+l-original),'retained encoding cargo unchanged')
            require(type(v['ORIGINAL_zero_sign_preserved']) is bool,'retained typed sign finding')
        staged.append(deepcopy(row))
    return staged
def audit_decoder_CPU(request,*,model):
    require(type(model) is str and model==MODEL,'explicit opt-in decoder model')
    data,pins,false=load_retained()
    if request is None:
        return {'model':MODEL,FLAG:False,'missing_cases':data['missing']['missing_cases'],
                'missing_sources':data['missing']['missing_sources'],'new_native_RN64_adds':0,
                'new_zero_branch_selections':0,'group_admissions':0,'phase_quota_fits':None,
                'uniform_executed_SOURCE_error_L1':None,'proof_scope':deepcopy(false),'status':'STOP'}
    staged=prepare_all(request,data) # ALL scene/limb/byte checks BEFORE ANY decode.
    rows=[]
    for old in staged:
        scalars=[]
        for prior in old['scalars']:
            new=decode_scalar(prior['high_uint32'],prior['low_uint32'])
            original=word_value(prior['original_uint64'],64);decoded=word_value(new['decoded_uint64'],64)
            eps=rational(prior['encoding_error_abs'])+rational(new['decode_error_abs'])
            signs=original!=0 or prior['original_uint64']>>63==new['decoded_uint64']>>63
            require(abs(decoded-original)<=eps,'point ORIGINAL enclosure')
            new.update(original_uint64=prior['original_uint64'],retained_old_decoded_uint64=prior['decoded_uint64'],
                       retained_old_zero_sign_preserved=prior['ORIGINAL_zero_sign_preserved'],
                       ORIGINAL_zero_sign_preserved=signs,encoding_error_abs=deepcopy(prior['encoding_error_abs']),
                       point_error_bound_abs=pair(eps),ORIGINAL_bitwise_roundtrip=prior['original_uint64']==new['decoded_uint64'])
            scalars.append(new)
        rows.append({'case_name':old['case_name'],'source_id':old['source_id'],'encoder_row_sha256':digest(old),
                     'scalars':scalars,'hilo_le_sha256':old['hilo_le_sha256'],
                     'point_complex_error_L1_bound':pair(sum((F(*s['point_error_bound_abs']) for s in scalars),F(0))),
                     'retained_whole_box_guard_admission_disproved':old['retained_whole_box_guard_admission_disproved'],
                     'frozen_guard_admission_for_entire_box_proved':False,'status':'STOP'})
    return {'model':MODEL,FLAG:True,'request_sha256':digest(request),'sources':rows,
            'new_native_RN64_adds':sum(s['new_native_RN64_adds'] for r in rows for s in r['scalars']),
            'new_zero_branch_selections':sum(s['new_zero_branch_selections'] for r in rows for s in r['scalars']),
            'inherited_pins_verified':len(pins),'encoder_calls':0,'old_numeric_controls_reexecuted':0,
            'group_admissions':0,'uniform_executed_SOURCE_error_L1':None,'phase_quota_fits':None,
            'actual_scene_authenticated':False,'old_RN_add_graph_equivalence_proved':False,
            'proof_scope':deepcopy(false),'status':'STOP'}
