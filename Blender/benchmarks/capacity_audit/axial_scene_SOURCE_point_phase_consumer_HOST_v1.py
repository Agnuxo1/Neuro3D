"""HOST rational point phase consumer of retained encoder receipts; no producer imports."""
import base64
import hashlib
import json
import math
import zlib
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
MODEL='axial-retained-synthetic-SOURCE-point-phase-consumer-HOST-v1'
FLAG='retained_SOURCE_point_phase_bound_computed_HOST'
SCOPE='principal point phase to ORIGINAL SOURCE field only; no path/unit/material/uniform quota'
PARENT='coordinacion/respuestas/AXIAL-SCENE-SOURCE-HILO-ENCODER-CPU-001-CODEX.json'
PARENT_SHA='bf911d4e21af25caf476bb80f13c3511df401e886595979382d336334277450b'
PARENT_MODEL='axial-retained-synthetic-scene-SOURCE-hilo-point-encoder-CPU-v1'
REQUEST_KEYS={'model','scope','SCENE_INPUT','encoder_receipt_sha256','SOURCE_point_records'}
def require(ok,message):
    if not ok:raise ValueError(message)
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def pair(q):return [q.numerator,q.denominator]
def rational(v):
    require(type(v) is list and len(v)==2 and all(type(n) is int for n in v),'strict typed rational')
    require(v[1]>0 and math.gcd(*v)==1,'canonical rational')
    return F(*v)
def word_value(w):
    require(type(w) is int and 0<=w<1<<64,'strict selected uint64')
    ex=(w>>52)&2047;ma=w&((1<<52)-1)
    require(ex<2047 and (ex>0 or ma==0),'finite normal-or-zero selected word')
    return (-1 if w>>63 else 1)*F(ma if ex==0 else ma+(1<<52))*F(2)**((ex or 1)-1023-52)
def payload(r):
    t=r['test_run'];encoded=t.get('stdout_zlib_base64')
    if encoded is None:encoded=''.join(t['stdout_zlib_base64_chunks'])
    b=zlib.decompress(base64.b64decode(encoded,validate=True))
    require(len(b)==t['stdout_bytes'] and sha(b)==t['stdout_sha256'],'lossless payload')
    return json.loads(b)
def load_retained():
    raw=(ROOT/PARENT).read_bytes();require(sha(raw)==PARENT_SHA,'parent receipt SHA')
    parent=json.loads(raw);require(parent['task_id']=='AXIAL-SCENE-SOURCE-HILO-ENCODER-CPU-001' and parent['model']==PARENT_MODEL,'parent ID/model')
    pins={**parent['code_doc_sha256'],PARENT:PARENT_SHA};require(len(pins)==513,'complete inherited pins')
    for path,h in pins.items():require(sha((ROOT/path).read_bytes())==h,'sealed '+path)
    data=payload(parent)['data'];false=parent['proof_scope']
    require(len(false)==38 and all(v is False for v in false.values()),'frozen general STOP scope')
    require(data['audit']['model']==PARENT_MODEL and data['audit']['group_admissions']==0,'retained point backend not box admission')
    return data,pins,false
def make_synthetic_request():
    data,_,_=load_retained()
    return {'model':MODEL,'scope':SCOPE,'SCENE_INPUT':deepcopy(data['request']),
            'encoder_receipt_sha256':PARENT_SHA,'SOURCE_point_records':deepcopy(data['audit']['sources'])}
def prepare_all(request,data):
    require(type(request) is dict and set(request)==REQUEST_KEYS,'exact point phase request schema')
    require(type(request['model']) is str and request['model']==MODEL and request['scope']==SCOPE,'explicit point phase scope/model')
    require(type(request['encoder_receipt_sha256']) is str and request['encoder_receipt_sha256']==PARENT_SHA,'same encoder receipt')
    require(type(request['SCENE_INPUT']) is dict and digest(request['SCENE_INPUT'])==digest(data['request']),'same full retained scene INPUT')
    rows=request['SOURCE_point_records'];expected=data['audit']['sources']
    require(type(rows) is list and len(rows)==4 and len(rows)==len(expected),'complete ordered point SOURCE records')
    staged=[]
    for row,baseline in zip(rows,expected):
        require(type(row) is dict and digest(row)==digest(baseline),'exact complete retained encoder SOURCE ledger')
        case=request['SCENE_INPUT']['cases'][row['case_name']]
        source=next(s for s in case['SOURCE_read_requests'] if s['source_id']==row['source_id'])
        require(row['context_sha256']==digest(case['context']) and row['GRID_INPUT_plan_sha256']==digest(case['GRID_INPUT']) and row['SOURCE_request_sha256']==digest(source),'scene/SOURCE/gauges/GRID bindings')
        scalars=row['scalars'];require(type(scalars) is list and len(scalars)==2,'two retained scalar records')
        original=[v['original_uint64'] for v in scalars];decoded=[v['decoded_uint64'] for v in scalars]
        require(digest(original)==digest(source['words']),'same ORIGINAL bits including zero sign')
        for w in original+decoded:word_value(w)
        require(all(type(v['ORIGINAL_zero_sign_preserved']) is bool for v in scalars),'typed zero-sign findings')
        eps=sum((rational(v['point_error_bound_abs']) for v in scalars),F(0))
        require(eps>=0 and rational(row['point_complex_error_L1_bound'])==eps,'same sum of point error cargos once')
        require(row['frozen_guard_admission_for_entire_box_proved'] is False and row['status']=='STOP','no box promotion')
        staged.append((deepcopy(row),original,decoded,pair(eps),all(v['ORIGINAL_zero_sign_preserved'] for v in scalars)))
    return staged
def bound_POINT_phase(original_words,decoded_words,error_L1,*,original_zero_signs_preserved):
    require(type(original_zero_signs_preserved) is bool,'typed zero-sign gate')
    require(type(original_words) is list and type(decoded_words) is list and len(original_words)==len(decoded_words)==2,'two typed complex words')
    a=list(map(word_value,original_words));b=list(map(word_value,decoded_words));eps=rational(error_L1)
    observed_signs=all(x!=0 or (ow>>63)==(dw>>63) for x,ow,dw in zip(a,original_words,decoded_words))
    require(original_zero_signs_preserved is observed_signs,'zero-sign finding bound to actual words')
    require(eps>=0,'nonnegative point radius')
    measured=sum((abs(y-x) for x,y in zip(a,b)),F(0));require(measured<=eps,'point radius encloses measured ORIGINAL error')
    # max(|real|,|imag|) <= Euclidean ORIGINAL norm; L1 error upper-bounds L2 disk radius.
    lower=max(map(abs,a));margin=lower-eps
    out={'ORIGINAL_uint64':deepcopy(original_words),'decoded_uint64':deepcopy(decoded_words),
         'point_error_L1_radius':pair(eps),'measured_point_error_L1':pair(measured),
         'ORIGINAL_norm_lower_bound':pair(lower),'strict_origin_margin':pair(margin),
         'ORIGINAL_zero_signs_preserved':original_zero_signs_preserved,'point_principal_phase_bound_rad':None,
         'point_phase_enclosed':False,'scope':SCOPE,'uniform_phase_bound_rad':None,'phase_quota_fits':None,'status':'STOP'}
    if not original_zero_signs_preserved:out['reason']='retained ORIGINAL zero-sign FAIL STOP'
    elif margin<=0:out['reason']='no strict point disk margin to origin STOP'
    else:
        out.update(point_principal_phase_bound_rad=pair(eps/margin),point_phase_enclosed=True,
                   reason='point-only angle <= atan(eps/margin) <= eps/margin; no phase INPUT quota admission')
    return out
def audit_point_phase_HOST(request,*,model):
    require(type(model) is str and model==MODEL,'explicit opt-in point phase model')
    data,pins,false=load_retained()
    if request is None:
        missing=data['missing']
        return {'model':MODEL,FLAG:False,'missing_cases':missing['missing_cases'],'missing_sources':missing['missing_sources'],
                'point_phase_computations':0,'group_admissions':0,'uniform_executed_SOURCE_error_L1':None,
                'uniform_phase_bound_rad':None,'phase_quota_fits':None,'proof_scope':deepcopy(false),'status':'STOP'}
    staged=prepare_all(request,data) # ALL ledger/INPUT checks before ANY new point bound
    rows=[]
    for record,original,decoded,eps,signs in staged:
        proof=bound_POINT_phase(original,decoded,eps,original_zero_signs_preserved=signs)
        rows.append({'case_name':record['case_name'],'source_id':record['source_id'],'SOURCE_encoder_row_sha256':digest(record),
                     'proof':proof,'retained_whole_box_guard_admission_disproved':record['retained_whole_box_guard_admission_disproved'],
                     'frozen_guard_admission_for_entire_box_proved':False,'status':'STOP'})
    return {'model':MODEL,FLAG:True,'request_sha256':digest(request),'sources':rows,'point_phase_computations':len(rows),
            'point_phase_enclosed_count':sum(r['proof']['point_phase_enclosed'] for r in rows),'inherited_pins_verified':len(pins),
            'encoder_calls':0,'native_RN_nodes':0,'old_numeric_controls_reexecuted':0,'group_admissions':0,
            'uniform_executed_SOURCE_error_L1':None,'uniform_phase_bound_rad':None,'phase_quota_fits':None,
            'actual_scene_authenticated':False,'signed_zero_equivalence_proved':False,'proof_scope':deepcopy(false),'status':'STOP'}
