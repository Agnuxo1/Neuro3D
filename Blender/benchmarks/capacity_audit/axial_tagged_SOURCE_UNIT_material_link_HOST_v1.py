"""Retained tagged A -> fixed ORIGINAL UNIT and ideal material. HOST only."""
import base64, hashlib, json, zlib
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
MODEL='axial-tagged-SOURCE-UNIT-material-retained-link-HOST-v1'
PARENT='coordinacion/respuestas/AXIAL-TAGGED-SOURCE-ORIGINAL-POINT-BOUND-HOST-001-CODEX.json'
PARENT_SHA='fa2873f797fadd9fbe416c2cd2bfe24db4e0148159583595d50cff0fc6450355'
BARE='coordinacion/respuestas/AXIAL-GUARDED-SOURCE-PRODUCT-RN64-CPU-001-CODEX.json'
MATERIAL='coordinacion/respuestas/AXIAL-CURRENT-SOURCE-IDEAL-REFLECTION-CPU-001-CODEX.json'
REFERENCE='fixed ORIGINAL A * exact exp(i ORIGINAL path phase) * ideal minus one'
def require(ok,msg):
    if not ok: raise ValueError(msg)
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def pair(q):return [q.numerator,q.denominator]
def q(v):
    require(type(v) is list and len(v)==2 and all(type(x) is int and x.bit_length()<=4096 for x in v) and v[1]>0,'strict bounded rational')
    r=F(*v);require(r>=0 and pair(r)==v,'canonical nonnegative rational');return r
def value(w):
    require(type(w) is int and 0<=w<1<<64,'strict uint64')
    e=(w>>52)&2047;m=w&((1<<52)-1)
    require(e<2047 and (e>0 or m==0),'normal or zero')
    return (-1 if w>>63 else 1)*F(m if e==0 else m+(1<<52))*F(2)**((e or 1)-1023-52)
def payload(r):
    t=r['test_run'];s=t.get('stdout_zlib_base64') or ''.join(t['stdout_zlib_base64_chunks'])
    b=zlib.decompress(base64.b64decode(s,validate=True))
    require(len(b)==t['stdout_bytes'] and sha(b)==t['stdout_sha256'],'lossless payload')
    return json.loads(b)['data']
def load_retained():
    raw=(ROOT/PARENT).read_bytes();require(sha(raw)==PARENT_SHA,'parent SHA')
    r=json.loads(raw);pins={**r['code_doc_sha256'],PARENT:PARENT_SHA}
    require(len(pins)==533,'full lineage')
    for path,h in pins.items():require(sha((ROOT/path).read_bytes())==h,'sealed '+path)
    require(BARE in pins and MATERIAL in pins,'retained downstream branches')
    a=payload(r);b=payload(json.loads((ROOT/BARE).read_bytes()))['audit']
    m=payload(json.loads((ROOT/MATERIAL).read_bytes()))['audit']
    require(len(r['proof_scope'])==38 and all(v is False for v in r['proof_scope'].values()),'general STOP')
    return a,b,m,pins,r['proof_scope']
def make_request():
    a,b,m,_,_=load_retained()
    return {'model':MODEL,'reference':REFERENCE,'parent_sha256':PARENT_SHA,
            'A_POINT_INPUT':deepcopy(a['request']),'A_POINT_OUTPUT':deepcopy(a['audit']),
            'bare_OUTPUT':deepcopy(b),'material_OUTPUT':deepcopy(m)}
def prepare_all(request,a,b,m):
    require(type(request) is dict and set(request)=={'model','reference','parent_sha256','A_POINT_INPUT','A_POINT_OUTPUT','bare_OUTPUT','material_OUTPUT'},'exact opt-in INPUT; no quotas')
    require(request['model']==MODEL and type(request['model']) is str and request['reference']==REFERENCE and request['parent_sha256']==PARENT_SHA,'explicit model/reference/parent')
    for k,v in [('A_POINT_INPUT',a['request']),('A_POINT_OUTPUT',a['audit']),('bare_OUTPUT',b),('material_OUTPUT',m)]:
        require(digest(request[k])==digest(v),'COMPLETE sealed '+k)
    rows=a['request']['transport_INPUT']['decoder_INPUT']['SOURCE_limb_records'];out=a['audit']['sources']
    require(len(rows)==len(out)==4,'complete SOURCE order')
    staged=[]
    for row,point in zip(rows,out):
        name,sid=row['case_name'],row['source_id'];bc=b['cases'][name];mc=m['cases'][name]
        require((name,sid)==(point['case_name'],point['source_id']),'ordered point identity')
        ctx=bc['context'];require(digest(ctx)==row['context_sha256'] and digest(ctx)==digest(mc['context']),'same scene ORIGINAL ABI and gauges')
        i=ctx['source_order'].index(sid);br=bc['sources'][i];mr=mc['sources'][i]
        require(br['source_id']==mr['source_id']==sid,'same downstream source')
        p=point['proof'];original=[s['original_uint64'] for s in row['scalars']]
        require(p['ORIGINAL_uint64']==original and point['encoder_row_sha256']==digest(row),'same ORIGINAL ledger')
        for w in original+p['decoded_uint64']:value(w)
        eps=q(p['point_error_L1_bound'])
        require(sum((abs(value(x)-value(y)) for x,y in zip(original,p['decoded_uint64'])),F(0))<=eps,'A enclosure')
        E=sum((q(s['encoding_error_abs']) for s in row['scalars']),F(0))
        transport=a['request']['transport_OUTPUT']['sources'][len(staged)]
        D=sum((q(s['decode_error_abs']) for s in transport['decoded_scalars']),F(0))
        require(E+D==eps,'encoding/decode ONCE')
        if br.get('result') is None or mr.get('result') is None:
            require(br.get('result') is None and mr.get('result') is None,'no partial branch')
            staged.append((name,sid,None,point));continue
        v=br['result'];ad=br['admission'];mat=mr['result'];assign=ctx['assignments'][i]
        require(digest(p['decoded_uint64'])==digest(v['decoded_source_uint64']),'BITWISE equal retained product operands including zeros')
        require(original==ad['ORIGINAL_source_uint64'] and ad['unit_uint64']==v['unit_uint64'],'same ORIGINAL and UNIT')
        require(ad['phase_reference_id']==mat['phase_reference_id']==assign['source_phase_reference_id'] and ad['terminal_reference_id']==mat['terminal_reference_id']==assign['terminal_reference_id'],'same gauges')
        S=sum((abs(value(w)) for w in original),F(0));L=sum((abs(value(w)) for w in v['unit_uint64']),F(0))
        require(q(v['represented_unit_norm_L1'])==L and q(v['ORIGINAL_source_norm_L1'])==S,'same norms')
        unit=ad['unit_L1_charges'];require(len(unit)==11 and sum(map(q,unit.values()),F(0))==q(ad['unit_L1_bound']),'eleven ORIGINAL UNIT charges')
        old=v['detailed_source_charges_L1'];require(len(old)==14,'old fourteen')
        charges={'source_encoding_L1':pair(E*L),'source_decode_RN64_L1':pair(D*L),
                 **{'source_unit_'+k:pair(S*q(t)) for k,t in unit.items()},
                 'source_product_RN64_L1':deepcopy(old['source_product_RN64_L1']),'ideal_material_L1':[0,1]}
        require(set(charges)==set(mat['fifteen_source_material_charges_L1']),'exact fifteen names')
        # Equality is checked, never assumed from equal numerics or equal payload bytes.
        require(all(q(charges[k])==q(mat['fifteen_source_material_charges_L1'][k]) for k in charges),'retained downstream charge equivalence')
        require(mat['input_uint64']==v['product_uint64'] and mat['material_executed'] is True and mr['material_executed'] is True,'retained product->material')
        require(mat['material_profile']['ideal_coefficient_exact_reim']==[[-1,1],[0,1]],'only fixed ideal minus one')
        require(len(mat['material_nodes'])==2,'two material nodes')
        for w,z,n in zip(v['product_uint64'],mat['reflected_uint64'],mat['material_nodes']):
            require(type(z) is int and z==w^(1<<63) and n=={'operation':'CPU_unary_minus_binary64','input_uint64':w,'output_uint64':z,'exact_material_rounding_error_L1':[0,1]},'exact retained sign isometry')
        total=sum(map(q,charges.values()),F(0))
        require(total==q(mat['point_reflected_source_bound_to_FIXED_ORIGINAL_L1']),'conservation toward fixed ORIGINAL')
        staged.append((name,sid,{'charges':charges,'total':pair(total),'bare_row_sha256':digest(br),'material_row_sha256':digest(mr),
                              'context_sha256':digest(ctx),'retained_reflected_uint64':deepcopy(mat['reflected_uint64'])},point))
    return staged
def emit_link(name,sid,ledger,point):
    return {'case_name':name,'source_id':sid,'reference':REFERENCE,'A_point_row_sha256':digest(point),
            'retained_operand_link_proved':ledger is not None,'ledger':ledger,'new_product_or_material_executed':False,
            'phase_quota_fits':None,'phase_bound_rad':None,'uniform_SOURCE_error_L1':None,
            'whole_box_guard_admission_disproved':point['retained_whole_box_guard_admission_disproved'],'status':'STOP'}
def audit(request,*,model):
    require(type(model) is str and model==MODEL,'explicit HOST opt-in')
    a,b,m,pins,false=load_retained()
    if request is None:
        return {'model':MODEL,'sources':[],'missing_cases':17,'missing_sources':19,'links':0,'group_admissions':0,'proof_scope':deepcopy(false),'status':'STOP'}
    staged=prepare_all(request,a,b,m) # ALL records, operands, material and ledgers before ANY emission.
    rows=[emit_link(*v) for v in staged]
    return {'model':MODEL,'sources':rows,'links':sum(r['retained_operand_link_proved'] for r in rows),'inherited_pins_verified':len(pins),
            'new_native_operations':0,'old_producers_suites_reexecuted':0,'group_admissions':0,'actual_scene_authenticated':False,
            'execution_of_new_backend_proved':False,'proof_scope':deepcopy(false),'phase_quota_fits':None,'status':'STOP'}
