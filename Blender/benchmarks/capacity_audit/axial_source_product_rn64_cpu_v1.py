"""Scene ABI sources times retained unit: explicit synthetic CPU RN64 only."""
import base64
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import zlib

from axial_hilo_ops_cpu_v1 import component
from axial_unit_rn64_cpu_v1 import component64,round64
from axial_relative_gate_cpu_v1 import ratio,bound

ROOT=Path(__file__).resolve().parents[3]
REPORT='coordinacion/respuestas/AXIAL-UNIT-RN64-001-CODEX.json'
SHA='e920ad271b1d00ada8c9d85a496556d5ac78644bc146a885a0ee4962a75e4609'
SOURCE_REPORT='coordinacion/respuestas/AXIAL-QUARTER-SOURCE-OPS-001-CODEX.json'
SOURCE_SHA='c3a54d51c47f901d4c0520216499c027a24c9579742e9b28a57073c72053d2a0'
MODEL='axial-source-limbs-unit-eight-RN64-CPU-v1'
ZERO_PROFILE_REASON='decoded phase is not an exact quarter cycle; no approximation/fallback'


def product_words(source_words,unit_words,*,product_model):
    """Two source decode-adds, four multiplies, two combine nodes; no FMA."""
    if product_model!=MODEL:raise ValueError('explicit synthetic CPU RN64 product required')
    if not isinstance(source_words,list) or len(source_words)!=4 or not isinstance(unit_words,list) or len(unit_words)!=2:
        raise ValueError('four source uint32 limbs and two unit uint64 words required')
    sh=list(map(component,source_words));u,v=map(component64,unit_words)
    trace=[]
    def rn(a,b,op,label):
        exact=a+b if op=='add' else (a-b if op=='sub' else a*b)
        w,value=round64(exact);delta=value-exact
        trace.append({'label':label,'op':op,'inputs_rational':[ratio(a),ratio(b)],
                      'output_uint64':w,'rounding_delta_rational':ratio(delta)})
        return value,delta,w
    ar,dr,_=rn(sh[0],sh[1],'add','decode.real')
    ai,di,_=rn(sh[2],sh[3],'add','decode.imag')
    ac,dac,_=rn(ar,u,'mul','mul.ac');bd,dbd,_=rn(ai,v,'mul','mul.bd')
    ad,dad,_=rn(ar,v,'mul','mul.ad');bc,dbc,_=rn(ai,u,'mul','mul.bc')
    re,dre,wr=rn(ac,bd,'sub','combine.real');im,dim,wi=rn(ad,bc,'add','combine.imag')
    exact=[ar*u-ai*v,ar*v+ai*u];actual=[re-exact[0],im-exact[1]]
    assert actual==[dac-dbd+dre,dad+dbc+dim]
    product_bound=sum(map(abs,(dac,dbd,dad,dbc,dre,dim)),F(0))
    return {'source_limb_uint32':source_words,'unit_uint64':unit_words,
            'decoded_source_rational':[ratio(ar),ratio(ai)],
            'source_exact_limb_sum_rational':[ratio(sh[0]+sh[1]),ratio(sh[2]+sh[3])],
            'source_decode_error_L1_upper_rational':ratio(abs(dr)+abs(di)),
            'output_uint64':[wr,wi],'observed_path_field_rational':[ratio(re),ratio(im)],
            'product_error_L1_upper_rational':ratio(product_bound),
            'actual_product_error_L1_rational':ratio(sum(map(abs,actual),F(0))),
            'operations':trace,'RN64_operations':8,'GPU_executed':False,'ALU_executed':False}


def payload(report):
    run=report['run'];raw=zlib.decompress(base64.b64decode(run['stdout_zlib_base64'],validate=True))
    if len(raw)!=run['stdout_bytes'] or hashlib.sha256(raw).hexdigest()!=run['stdout_sha256']:
        raise ValueError('retained exact payload SHA mismatch')
    return json.loads(raw)


def load_retained():
    raw=(ROOT/REPORT).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SHA:raise ValueError('retained RN64 report SHA mismatch')
    r=json.loads(raw)
    if r['id']!='AXIAL-UNIT-RN64-001-CODEX' or r['run']['rc']!=0:
        raise ValueError('retained identity/status mismatch')
    for n,h in r['code_doc_sha256'].items():
        if hashlib.sha256((ROOT/n).read_bytes()).hexdigest()!=h:raise ValueError('changed frozen input '+n)
    if r['code_doc_sha256'].get(SOURCE_REPORT)!=SOURCE_SHA:
        raise ValueError('source report pin missing/mismatched')
    source=json.loads((ROOT/SOURCE_REPORT).read_bytes())
    return r,payload(r)['audit']['cases'],payload(source)['cases']


def _case(unit,source):
    trans=source['transport'];binding=trans['original_scene_binding_sha256']
    for key in ['original_scene_binding_sha256','decoded_scene_binding_sha256']:
        if unit[key]!=trans[key]:raise ValueError('source/unit scene binding mismatch')
    sources=trans['source_transport']['sources'];contrib=trans['contributions']
    paths=trans['path_certificate']['path_certificates'];ids=[p['source_id'] for p in unit['paths']]
    if not 1<=len(ids)<=16 or len(set(ids))!=len(ids) or any([p['source_id'] for p in seq]!=ids for seq in (sources,contrib,paths)):
        raise ValueError('complete ordered unique source/path/contribution coverage required')
    reference='ideal-scene-source-gauge:'+binding
    out={'previous_full_case_accepted':unit['previous_full_case_accepted'],
         'previous_unit_accepted':unit['accepted_propagation_unit_CPU_only'],
         'accepted_source_product_absolute_CPU_only':False,'accepted_full_field_pipeline':False,
         'path_field_values_computed':False,'scene_field_reduced':False,'detector_evaluated':False,
         'coherent_group_budget_certified':False,
         'case_gate_scope':'per-source path absolute budget cap only; no coherent-group/reduction/detector gate',
         'GPU_executed':False,'ALU_executed':False,'native_promotion_allowed':False,
         'execution_authenticated':False,'old_scene_unit_quotient_or_producer_rerun':False,
         'original_scene_binding_sha256':binding,'decoded_scene_binding_sha256':trans['decoded_scene_binding_sha256'],
         'RN64_operations':0,'paths':[],'field_absolute_L1_budget_rational':trans['field_absolute_L1_budget']}
    # Frozen code tests original/decoded mirror==0 before the nonquarter branch.
    zero=source['field_values_computed'] or source.get('reason')==ZERO_PROFILE_REASON
    if not zero:return {**out,'reason':'original+decoded mirror-zero profile not proven; no product'}
    if not trans['accepted_CPU_transport_budget_only'] or not unit['accepted_propagation_unit_CPU_only']:
        return {**out,'reason':'retained scene/source/phase/unit certification rejected; no product'}
    fb=bound(trans['field_absolute_L1_budget'])
    out['mirror_zero_provenance']='SHA-pinned quarter producer passed original+decoded phase==0 before fieldgeneration or nonquarter rejection; no replay'
    for src,tr,path,up in zip(sources,contrib,paths,unit['paths']):
        if src['scene_binding_sha256']!=binding or src['source_phase_reference_id']!=reference or tr['common_phase_reference_id']!=reference:
            raise ValueError('source gauge/binding mismatch')
        if up['phase_reference_id']!=path['phase_reference_id'] or up['phase_reference_id']!=tr['source_phase_reference_id'] or up['phase_reference_id']!='original-source-zero:'+binding+':'+src['source_id']:
            raise ValueError('unit/path original reference mismatch')
        if src['coherence_group']!=tr['coherence_group'] or path['terminal_object_id']!=tr['port']:
            raise ValueError('source port/coherence grouping mismatch')
        if not src['accepted_CPU_source_transport_budget_only'] or not tr['accepted_CPU_transport_contribution_only'] or not up['accepted_propagation_unit_CPU_only']:
            raise ValueError('complete source/path acceptance required')
        if len(src['components'])!=2:raise ValueError('two complex source components required')
        words=[w for c in src['components'] for w in c['limb_uint32']]
        source_original=[F(*c['input_binary64_rational']) for c in src['components']]
        limb_sums=[sum(map(component,words[i:i+2]),F(0)) for i in (0,2)]
        if [ratio(v) for v in limb_sums]!=[c['exact_limb_sum_rational'] for c in src['components']]:
            raise ValueError('source exact limb sum mismatch')
        es=sum((abs(a-b) for a,b in zip(source_original,limb_sums)),F(0))
        # Exact reflection coefficient -1 at the proven mirror-zero profile.
        reflected=[w^(1<<63) for w in up['propagation_unit_uint64']]
        model=product_words(words,reflected,product_model=MODEL)
        ed=F(*model['source_decode_error_L1_upper_rational']);ep=F(*model['product_error_L1_upper_rational'])
        eu=bound(up['composed_unit_error_L1_upper_rational'])
        unorm=sum((abs(component64(w)) for w in reflected),F(0));anorm=sum(map(abs,source_original),F(0))
        if anorm!=F(*tr['original_amplitude_L1_upper_rational']):
            raise ValueError('original source norm mismatch')
        charges={'source_encoding':es*unorm,'source_decode':ed*unorm,'unit_phase_numeric':anorm*eu,'product_RN':ep}
        total=sum(charges.values(),F(0))
        out['paths'].append({'source_id':src['source_id'],'port':tr['port'],'coherence_group':src['coherence_group'],
            'phase_reference_id':reference,'path_phase_reference_id':up['phase_reference_id'],
            'source_original_rational':[ratio(v) for v in source_original],
            'original_amplitude_L1_rational':ratio(anorm),'observed_unit_L1_rational':ratio(unorm),
            'source_encoding_error_L1_rational':ratio(es),'retained_unit_error_L1_upper_rational':ratio(eu),
            'mirror_coefficient_exact_reim_rational':[[-1,1],[0,1]],'measurement':model,
            'error_charges_L1_rational':{k:ratio(v) for k,v in charges.items()},
            'composed_path_field_error_L1_upper_rational':ratio(total),
            'field_absolute_L1_budget_rational':ratio(fb),
            'accepted_source_product_absolute_CPU_only':total<=fb})
        out['RN64_operations']+=8
    out['path_field_values_computed']=True
    out['accepted_source_product_absolute_CPU_only']=all(p['accepted_source_product_absolute_CPU_only'] for p in out['paths'])
    return out


def audit_retained_source_products(*,case_names,product_model):
    if product_model!=MODEL:raise ValueError('explicit synthetic CPU RN64 product required')
    if not isinstance(case_names,list) or not case_names or any(type(n) is not str for n in case_names) or len(set(case_names))!=len(case_names):
        raise ValueError('explicit unique nonempty retained selection required')
    r,units,sources=load_retained()
    if any(n not in units for n in case_names):raise ValueError('unknown retained case')
    cases={n:_case(units[n],sources[n]) for n in case_names}
    return {'schema':'exp005-source-product-synthetic-RN64-CPU-v1','product_model':MODEL,'cases':cases,
        'RN64_operations':sum(c['RN64_operations'] for c in cases.values()),'pins_verified':r['code_doc_sha256'],
        'retained_report_sha256':SHA,'source_report_sha256':SOURCE_SHA,'GPU_executed':False,
        'ALU_executed':False,'accepted_full_field_pipeline':False,'native_promotion_allowed':False,
        'scene_field_reduced':False,'detector_evaluated':False,
        'cost_scope':'8 modeled RN64/path +2exact reflection signbit XOR; source32->64 values exact, source decode included; excludes retained unit/geometry/selector/IO/memory/energy/reduction/detector/guard; no fullcost/equivalent-speed claim'}
