"""New-argument source product: changed words only, pinned exact product cache."""
from copy import deepcopy
import hashlib
import json
from fractions import Fraction as F
from pathlib import Path
from axial_source_product_rn64_cpu_v1 import product_words,payload,ZERO_PROFILE_REASON,MODEL as PRODUCT_MODEL
from axial_hilo_ops_cpu_v1 import component
from axial_unit_rn64_cpu_v1 import component64
from axial_relative_gate_cpu_v1 import ratio,bound

ROOT=Path(__file__).resolve().parents[3]
REPORT='coordinacion/respuestas/AXIAL-UNIT-ARGUMENT-RN64-001-CODEX.json'
SHA='dbcd557575616af8882c4fbf924c91c42db607e777c8bc43309099f336a32c17'
PRODUCT_REPORT='coordinacion/respuestas/AXIAL-SOURCE-PRODUCT-RN64-001-CODEX.json'
PRODUCT_SHA='6be20bac7ddf52a4c8d167b92db2c576c03a81c45428d5fa7b95ac4577d1d9a8'
SOURCE_REPORT='coordinacion/respuestas/AXIAL-QUARTER-SOURCE-OPS-001-CODEX.json'
SOURCE_SHA='c3a54d51c47f901d4c0520216499c027a24c9579742e9b28a57073c72053d2a0'
PRODUCT_CODE='Blender/benchmarks/capacity_audit/axial_source_product_rn64_cpu_v1.py'
MODEL='axial-new-argument-source-product-RN64-cached-words-CPU-v1'


def load_retained():
    raw=(ROOT/REPORT).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SHA:raise ValueError('new unit SHA mismatch')
    r=json.loads(raw)
    if r['id']!='AXIAL-UNIT-ARGUMENT-RN64-001-CODEX' or r['run']['rc']!=0:raise ValueError('new unit identity/status mismatch')
    for n,h in r['code_doc_sha256'].items():
        if hashlib.sha256((ROOT/n).read_bytes()).hexdigest()!=h:raise ValueError('changed frozen input '+n)
    raw=(ROOT/PRODUCT_REPORT).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=PRODUCT_SHA:raise ValueError('cached product SHA mismatch')
    old=json.loads(raw)
    if old['id']!='AXIAL-SOURCE-PRODUCT-RN64-001-CODEX' or old['run']['rc']!=0 or old['product_model']!=PRODUCT_MODEL:
        raise ValueError('cached product identity/status/model mismatch')
    if old['code_doc_sha256'][PRODUCT_CODE]!=r['code_doc_sha256'][PRODUCT_CODE]:raise ValueError('cached product code mismatch')
    raw=(ROOT/SOURCE_REPORT).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA:raise ValueError('source ABI SHA mismatch')
    src=json.loads(raw)
    return r,payload(r)['audit']['cases'],payload(src)['cases'],payload(old)['audit']['cases']


def _case(newunit,source,old,product_code_sha):
    for key in ('original_scene_binding_sha256','decoded_scene_binding_sha256'):
        if newunit[key]!=old[key]:raise ValueError('cached product scene binding mismatch')
    if newunit['previous_full_case_accepted']!=old['previous_full_case_accepted']:raise ValueError('previous full flag changed')
    # Interface adaptation only; no selector, geometry, unit or old-product replay.
    unit=deepcopy(newunit)
    unit['accepted_propagation_unit_CPU_only']=newunit['accepted_unit_CPU_only']
    for p in unit['paths']:
        p['accepted_propagation_unit_CPU_only']=p['accepted_unit_CPU_only']
        if 'unit_uint64' in p:p['propagation_unit_uint64']=p['unit_uint64']
    return _compose(unit,source,old,product_code_sha)


def _compose(unit,source,old,product_code_sha):
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
         'new_RN64_operations':0,'cached_RN64_operations':0,'RN64_operations':0,'paths':[],'field_absolute_L1_budget_rational':trans['field_absolute_L1_budget']}
    # Frozen code tests original/decoded mirror==0 before the nonquarter branch.
    zero=source['field_values_computed'] or source.get('reason')==ZERO_PROFILE_REASON
    if not zero:return {**out,'reason':'original+decoded mirror-zero profile not proven; no product'}
    if not trans['accepted_CPU_transport_budget_only'] or not unit['accepted_propagation_unit_CPU_only']:
        return {**out,'reason':'retained scene/source/phase/unit certification rejected; no product'}
    fb=bound(trans['field_absolute_L1_budget'])
    out['mirror_zero_provenance']='SHA-pinned quarter producer passed original+decoded phase==0 before fieldgeneration or nonquarter rejection; no replay'
    oldpaths={p['source_id']:p for p in old['paths']}
    if list(oldpaths)!=ids:raise ValueError('cached product complete source coverage required')
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
        cached=oldpaths[src['source_id']]['measurement']
        reused=cached['source_limb_uint32']==words and cached['unit_uint64']==reflected
        model=deepcopy(cached) if reused else product_words(words,reflected,product_model=PRODUCT_MODEL)
        if model['source_limb_uint32']!=words or model['unit_uint64']!=reflected or model['RN64_operations']!=8:
            raise ValueError('product words/node contract mismatch')
        out['cached_RN64_operations' if reused else 'new_RN64_operations']+=8
        ed=F(*model['source_decode_error_L1_upper_rational']);ep=F(*model['product_error_L1_upper_rational'])
        eu=bound(up['composed_unit_error_L1_upper_rational'])
        unorm=sum((abs(component64(w)) for w in reflected),F(0));anorm=sum(map(abs,source_original),F(0))
        if anorm!=F(*tr['original_amplitude_L1_upper_rational']):
            raise ValueError('original source norm mismatch')
        charges={'source_encoding':es*unorm,'source_decode':ed*unorm,'unit_phase_numeric':anorm*eu,'product_RN':ep}
        total=sum(charges.values(),F(0))
        out['paths'].append({'source_id':src['source_id'],'port':tr['port'],'coherence_group':src['coherence_group'],
            'phase_reference_id':reference,'path_phase_reference_id':up['phase_reference_id'],
            'product_cache_reused':reused,'product_evaluated':not reused,
            'cache_signature':{'model':PRODUCT_MODEL,'product_code_sha256':product_code_sha,
                'source_limb_uint32':words,'unit_uint64':reflected,'report_sha256':PRODUCT_SHA if reused else None},
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



def audit_retained_new_argument_products(*,case_names,product_model):
    if product_model!=MODEL:raise ValueError('explicit new-argument source product CPU contract required')
    if not isinstance(case_names,list) or not case_names or any(type(n) is not str for n in case_names) or len(set(case_names))!=len(case_names):
        raise ValueError('explicit unique retained case selection required')
    r,units,sources,old=load_retained()
    if any(n not in units for n in case_names):raise ValueError('unknown retained case')
    cases={n:_case(units[n],sources[n],old[n],r['code_doc_sha256'][PRODUCT_CODE]) for n in case_names}
    return {'product_model':MODEL,'cases':cases,'pins_verified':r['code_doc_sha256'],
            'retained_report_sha256':SHA,'product_report_sha256':PRODUCT_SHA,'source_report_sha256':SOURCE_SHA,
            'RN64_operations':sum(c['RN64_operations'] for c in cases.values()),
            'new_RN64_operations':sum(c['new_RN64_operations'] for c in cases.values()),
            'cached_RN64_operations':sum(c['cached_RN64_operations'] for c in cases.values()),
            'GPU_executed':False,'ALU_executed':False,'accepted_full_field_pipeline':False,
            'native_promotion_allowed':False,'scene_field_reduced':False,'detector_evaluated':False,
            'cost_scope':'8 new modeled RN64 per changed product input; same-code/model/words product cache not executed; upstream/IO/RAM/energy/guard/reduction/detector/full costs excluded'}
