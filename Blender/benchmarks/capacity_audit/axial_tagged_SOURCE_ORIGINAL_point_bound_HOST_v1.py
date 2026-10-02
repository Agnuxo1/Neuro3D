"""Point ORIGINAL bounds from retained tagged transport OUTPUT. No decoder/native imports."""
import base64
import hashlib
import json
import zlib
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
MODEL='axial-tagged-SOURCE-ORIGINAL-point-bounds-HOST-v1'
SCOPE='ORIGINAL fixed SOURCE A only; not A-exp-i-theta-reflection, UNIT, geometry or uniform domain'
PARENT='coordinacion/respuestas/AXIAL-SOURCE-HILO-DECODER-TAGGED-TRANSPORT-CPU-001-CODEX.json'
PARENT_SHA='e27054d5e4985f07fb6217bfd30bdff6514a77919512579e217c9e12222f8146'
DECODER='Blender/benchmarks/capacity_audit/axial_SOURCE_hilo_zero_aware_decoder_CPU_v1.py'
FLAG='tagged_OUTPUT_ORIGINAL_POINT_bounds_computed_HOST'
def require(ok,message):
    if not ok:raise ValueError(message)
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def pair(q):return [q.numerator,q.denominator]
def rational(v):
    require(type(v) is list and len(v)==2 and all(type(x) is int for x in v) and v[1]>0,'strict rational')
    require(all(x.bit_length()<=4096 for x in v),'bounded radius integer components')
    q=F(*v);require(pair(q)==v and q>=0,'canonical nonnegative radius');return q
def value(w):
    require(type(w) is int and 0<=w<1<<64,'strict uint64')
    e=(w>>52)&2047;m=w&((1<<52)-1)
    require(e<2047 and (e>0 or m==0),'finite normal-or-zero word')
    return (-1 if w>>63 else 1)*F(m if e==0 else m+(1<<52))*F(2)**((e or 1)-1023-52)
def payload(r):
    t=r['test_run'];v=t.get('stdout_zlib_base64')
    if v is None:v=''.join(t['stdout_zlib_base64_chunks'])
    b=zlib.decompress(base64.b64decode(v,validate=True))
    require(len(b)==t['stdout_bytes'] and sha(b)==t['stdout_sha256'],'lossless retained payload')
    return json.loads(b)
def load_retained():
    b=(ROOT/PARENT).read_bytes();require(sha(b)==PARENT_SHA,'parent receipt SHA')
    r=json.loads(b);require(r['task_id']=='AXIAL-SOURCE-HILO-DECODER-TAGGED-TRANSPORT-CPU-001','parent ID')
    pins={**r['code_doc_sha256'],PARENT:PARENT_SHA}
    require(len(pins)==528,'all inherited pins')
    for path,h in pins.items():require(sha((ROOT/path).read_bytes())==h,'sealed '+path)
    false=r['proof_scope'];require(len(false)==38 and all(x is False for x in false.values()),'general STOP preserved')
    data=payload(r)['data'];require(data['audit']['group_admissions']==0,'no transport admission')
    return data,pins,false
def bound_POINT(original,decoded,radius):
    require(type(original) is list and type(decoded) is list and len(original)==len(decoded)==2,'two typed complex words')
    a,b=list(map(value,original)),list(map(value,decoded));eps=rational(radius)
    measured=sum((abs(x-y) for x,y in zip(a,b)),F(0))
    require(measured<=eps,'actual ORIGINAL point error enclosed')
    # A zero component must remain a ZERO, with matching sign, not merely same sign bit.
    signs=all(x!=0 or (y==0 and (ow>>63)==(dw>>63)) for x,y,ow,dw in zip(a,b,original,decoded))
    norm_L1=sum(map(abs,a),F(0));lower=max(map(abs,a));margin=lower-eps
    relative=eps/norm_L1 if norm_L1>0 else None
    phase=eps/margin if signs and margin>0 else None
    return {'ORIGINAL_uint64':deepcopy(original),'decoded_uint64':deepcopy(decoded),'point_error_L1_bound':pair(eps),
            'measured_point_error_L1':pair(measured),'ORIGINAL_norm_L1':pair(norm_L1),
            'ORIGINAL_norm_L2_lower':pair(lower),'strict_origin_margin':pair(margin),
            'ORIGINAL_zero_components_and_signs_preserved':signs,
            'point_relative_L1_bound':pair(relative) if relative is not None else None,
            'point_principal_phase_bound_rad':pair(phase) if phase is not None else None,
            'reference_scope':SCOPE,'phase_quota_fits':None,'uniform_SOURCE_error_L1':None,'status':'STOP'}
def make_synthetic_request():
    data,_,_=load_retained()
    return {'model':MODEL,'reference_scope':SCOPE,'transport_receipt_sha256':PARENT_SHA,
            'transport_INPUT':deepcopy(data['request']),'transport_OUTPUT':deepcopy(data['audit'])}
def prepare_all(request,data,pins):
    require(type(request) is dict and set(request)=={'model','reference_scope','transport_receipt_sha256','transport_INPUT','transport_OUTPUT'},'exact point consumer INPUT; no phase cap alias')
    require(type(request['model']) is str and request['model']==MODEL and request['reference_scope']==SCOPE,'explicit A point reference')
    require(request['transport_receipt_sha256']==PARENT_SHA,'same transport receipt')
    inp,out=request['transport_INPUT'],request['transport_OUTPUT']
    require(type(inp) is dict and type(out) is dict and digest(inp)==digest(data['request']) and digest(out)==digest(data['audit']),'same COMPLETE scene-ORIGINAL-program-selection-INPUT and actual OUTPUT')
    rows=inp['decoder_INPUT']['SOURCE_limb_records'];frames=inp['frames'];results=out['sources']
    require(len(rows)==len(frames)==len(results)==4,'complete ordered frame/source coverage')
    staged=[]
    for row,frame,result in zip(rows,frames,results):
        require((row['case_name'],row['source_id'])==(frame['case_name'],frame['source_id'])==(result['case_name'],result['source_id']),'same ordered SOURCE')
        raw=base64.b64decode(frame['frame_base64'],validate=True)
        require(base64.b64encode(raw).decode()==frame['frame_base64'],'canonical frame')
        expected=b'N3DZAD01'+bytes.fromhex(pins[DECODER])+bytes.fromhex(row['context_sha256'])+bytes.fromhex(digest(row))+base64.b64decode(row['hilo_le_base64'],validate=True)
        require(raw==expected and len(raw)==120 and sha(raw)==result['frame_sha256'],'exact bound decoder/context/SOURCE/payload frame')
        require(result['encoder_row_sha256']==digest(row) and result['payload_sha256']==sha(raw[104:])==row['hilo_le_sha256'],'exact SOURCE ORIGINAL ledger/payload')
        original=[s['original_uint64'] for s in row['scalars']]
        decoded=result['decoded_SOURCE_uint64']
        require(digest(decoded)==digest([s['decoded_uint64'] for s in result['decoded_scalars']]),'actual decoded bits')
        for w in original+decoded:value(w)
        eps=sum((rational(old['encoding_error_abs'])+rational(new['decode_error_abs'])
                 for old,new in zip(row['scalars'],result['decoded_scalars'])),F(0))
        staged.append((deepcopy(row),deepcopy(result),original,decoded,pair(eps)))
    return staged
def audit_POINT_HOST(request,*,model):
    require(type(model) is str and model==MODEL,'explicit opt-in HOST point consumer')
    data,pins,false=load_retained()
    if request is None:
        m=data['missing']
        return {'model':MODEL,FLAG:False,'missing_cases':m['missing_cases'],'missing_sources':m['missing_sources'],
                'point_bound_calls':0,'group_admissions':0,'phase_quota_fits':None,'uniform_SOURCE_error_L1':None,
                'proof_scope':deepcopy(false),'status':'STOP'}
    staged=prepare_all(request,data,pins) # ALL byte/INPUT/OUTPUT/reference checks BEFORE ANY new bound.
    rows=[]
    for original_record,out,a,b,eps in staged:
        rows.append({'case_name':original_record['case_name'],'source_id':original_record['source_id'],
                     'encoder_row_sha256':digest(original_record),'transport_OUTPUT_row_sha256':digest(out),
                     'frame_sha256':out['frame_sha256'],'proof':bound_POINT(a,b,eps),
                     'retained_whole_box_guard_admission_disproved':out['retained_whole_box_guard_admission_disproved'],
                     'frozen_guard_admission_for_entire_box_proved':False,'status':'STOP'})
    return {'model':MODEL,FLAG:True,'request_sha256':digest(request),'sources':rows,'point_bound_calls':len(rows),
            'inherited_pins_verified':len(pins),'decoder_calls':0,'native_RN_nodes':0,'old_numeric_suites_producers_reexecuted':0,
            'group_admissions':0,'phase_quota_fits':None,'uniform_SOURCE_error_L1':None,
            'actual_scene_authenticated':False,'full_SOURCE_reflected_reference_proved':False,'proof_scope':deepcopy(false),'status':'STOP'}
