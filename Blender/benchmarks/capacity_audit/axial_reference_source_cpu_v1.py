"""Original source/mirror product from referenced unit; opt-in CPU only."""
from copy import deepcopy
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
from axial_reference_argument_cpu_v1 import require, digest, pair, rat, nonnegative, payload
from axial_hilo_terminal_cpu_v1 import encode_hilo
from axial_hilo_ops_cpu_v1 import component
from axial_unit_rn64_cpu_v1 import component64
from axial_source_product_rn64_cpu_v1 import product_words, MODEL as PRODUCT

ROOT=Path(__file__).resolve().parents[3]
MODEL='scene-fixed-original-reference-source-mirror-product-RN64-cache-CPU-v1'
UNIT='scene-fixed-original-reference-unit-Horner26-RN64-cache-CPU-v1'
REPORT='coordinacion/respuestas/AXIAL-REFERENCE-UNIT-001-CODEX.json'
SHA='555348ada0093f288e075f8428246ed1a406a7666fd3a8102d3ccb14c1cd1591'
CACHE_REPORT='coordinacion/respuestas/AXIAL-GEOMETRY-SOURCE-001-CODEX.json'
CACHE_SHA='75b6c5dd33596707875e228acd032997c15b7045c9eac5bde8237831207e8d5e'
GEOMETRY='coordinacion/respuestas/AXIAL-GEOMETRY-WORDS-001-CODEX.json'
QUOTIENT='coordinacion/respuestas/AXIAL-REFERENCE-QUOTIENT-001-CODEX.json'
CAP=[1,1000000000000]


class SourceCache:
    """Only encoding/product mathematical outputs, never old field gates."""
    def __init__(self,pins,old):
        self.codes={n:pins[n] for n in (
            'Blender/benchmarks/capacity_audit/axial_hilo_terminal_cpu_v1.py',
            'Blender/benchmarks/capacity_audit/axial_hilo_ops_cpu_v1.py',
            'Blender/benchmarks/capacity_audit/axial_source_product_rn64_cpu_v1.py',
            'Blender/benchmarks/capacity_audit/axial_unit_rn64_cpu_v1.py')}
        self.bank={'encoding':{},'product':{}}
        for c in old.values():
            for p in c['paths']:
                if 'measurement' not in p:
                    continue
                a=p['source_ABI'];sig=p['cache_signature'];m=p['measurement']
                require(sig['model']==PRODUCT and sig['code_sha256']==self.codes[
                    'Blender/benchmarks/capacity_audit/axial_source_product_rn64_cpu_v1.py'],'source origin code/model')
                self.add('encoding',a['source_original_rational'],{'source_limb_uint32':a['source_limb_uint32']})
                self.add('product',[m['source_limb_uint32'],m['unit_uint64']],m)

    def key(self,kind,inputs):
        return {'kind':kind,'inputs':inputs,'model':'HOST-exact-RN32-hilo' if kind=='encoding' else PRODUCT,
                'code_sha256':self.codes,'origin_report_sha256':CACHE_SHA}

    def add(self,kind,inputs,output):
        key=self.key(kind,inputs);k=digest(key)
        item={'key':key,'output':deepcopy(output),'output_sha256':digest(output)}
        require(k not in self.bank[kind] or self.bank[kind][k]['output_sha256']==item['output_sha256'],'conflicting source pure cache')
        self.bank[kind][k]=item

    def find(self,kind,inputs):
        key=self.key(kind,inputs);item=self.bank[kind].get(digest(key))
        if item is None:return None,{'cache_hit':False,'key':key}
        require(item['key']==key and digest(item['output'])==item['output_sha256'],'corrupt pure source cache')
        return deepcopy(item['output']),{'cache_hit':True,'key':key,'output_sha256':item['output_sha256'],
            'not_reused':['sourceID/scene/gauge','field cap/bounds/admission','execution authentication','cost comparison']}


def load_retained():
    b=(ROOT/REPORT).read_bytes()
    require(hashlib.sha256(b).hexdigest()==SHA,'reference unit report SHA')
    r=json.loads(b)
    require(r['id']=='AXIAL-REFERENCE-UNIT-001' and r['model']==UNIT and
        r['test_run']['rc']==r['independent_validation']['rc']==0,'unit identity/model/verification')
    pins=dict(r['code_doc_sha256'],**{REPORT:SHA})
    require(pins[CACHE_REPORT]==CACHE_SHA,'source arithmetic origin pin')
    for name,h in pins.items():
        require(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h,'changed frozen input '+name)
    old=payload(json.loads((ROOT/CACHE_REPORT).read_bytes()))['audit']['cases']
    return pins,payload(r)['audit'],payload(json.loads((ROOT/GEOMETRY).read_bytes()))['cases'],SourceCache(pins,old)


def empty_cost():
    return {'new_source_HOST_RN32':0,'cached_source_HOST_RN32_NOT_executed':0,
            'new_source_exact_residual_subtractions':0,'cached_source_residual_subtractions_NOT_executed':0,
            'new_product_RN64':0,'cached_product_RN64_NOT_executed':0,'mirror_signbit_toggles_new':0}


def encode_source(original,cache,costs):
    require(type(original) is list and len(original)==2,'two original source fields')
    inputs=[pair(v) for v in original];e,info=cache.find('encoding',inputs);hit=info['cache_hit']
    if e is None:
        e={'source_limb_uint32':[w for v in original for w in encode_hilo(v)[0]]}
    costs['cached_source_HOST_RN32_NOT_executed' if hit else 'new_source_HOST_RN32']+=4
    costs['cached_source_residual_subtractions_NOT_executed' if hit else 'new_source_exact_residual_subtractions']+=2
    words=e['source_limb_uint32'];require(type(words) is list and len(words)==4,'four source encoding limbs')
    sums=[component(words[j])+component(words[j+1]) for j in (0,2)]
    error=sum((abs(a-b) for a,b in zip(original,sums)),F(0))
    return words,sums,error,info


def multiply(words,unit,cache,costs):
    reflected=[w^(1<<63) for w in unit]
    list(map(component64,reflected));costs['mirror_signbit_toggles_new']+=2
    m,info=cache.find('product',[words,reflected]);hit=info['cache_hit']
    if m is None:m=product_words(words,reflected,product_model=PRODUCT)
    costs['cached_product_RN64_NOT_executed' if hit else 'new_product_RN64']+=8
    require(m['source_limb_uint32']==words and m['unit_uint64']==reflected
        and m['RN64_operations']==8 and len(m['operations'])==8,'matching pure product inputs')
    return m,reflected,info


def compose(u,g,caps,cache,*,model,expected_unit_sha256):
    require(model==MODEL,'explicit referenced source CPU model')
    require(u['model']==UNIT and digest(u)==expected_unit_sha256,'referenced unit digest/model')
    scene=g['scene_snapshot'];abi=g['word_ABI'];ids=abi['source_order']
    binding=digest({'snapshot':scene,'object_order':abi['object_ids'],'source_order':ids})
    require(binding==abi['original_scene_binding_sha256']==u['scene_binding_sha256']
        and digest(abi)==g['word_ABI_sha256']==u['word_ABI_sha256'],'original source/unit scene ABI binding')
    require(ids and len(set(ids))==len(ids) and ids==u['source_order']
        ==[p['source_id'] for p in u['paths']]==[p['source_id'] for p in g['sources']]
        ==[p['id'] for p in scene['sources']],'complete ordered source coverage')
    require(type(caps) is dict and set(caps)==set(ids),'explicit full per-source caps no default')
    limits={sid:nonnegative(caps[sid]) for sid in ids}
    costs=empty_cost();out={'model':MODEL,'scene_binding_sha256':binding,
        'word_ABI_sha256':g['word_ABI_sha256'],'unit_case_sha256':expected_unit_sha256,
        'source_order':ids,'paths':[],'costs':costs,'accepted_source_absolute_CPU_only':False,
        'scene_field_reduced':False,'detector_evaluated':False,'coherent_group_budget_certified':False,
        'accepted_full_field_pipeline':False,'execution_authenticated':False}
    for src,up,gp in zip(scene['sources'],u['paths'],g['sources']):
        sid=src['id']
        require(type(up['accepted_unit_CPU_only']) is bool and type(up['unit_available']) is bool,'strict unit gates')
        row={'source_id':sid,'previous_unit_accepted':up['accepted_unit_CPU_only'],
             'product_available':False,'accepted_source_absolute_CPU_only':False,'field_L1_budget':pair(limits[sid])}
        out['paths'].append(row)
        if not up['accepted_unit_CPU_only']:
            row['reason']='retained unit/upstream rejection; no source encode/product'
            continue
        require(up['unit_available'] is True,'available referenced unit')
        source='original-source-zero:'+binding+':'+sid
        terminal='fixed-original-plane-mode:'+binding+':D'
        require(up['source_phase_reference_id']==gp['phase_reference_id']==source
            and up['terminal_reference_id']==terminal,'original source/terminal gauges')
        mirror=abi['object_ids'][gp['mirror_owner']];port=abi['object_ids'][gp['terminal_owner']]
        require(mirror=='M' and port=='D' and scene['objects'][mirror]['kind']=='mirror'
            and F(scene['objects'][mirror]['phase_rad'])==0,'original mirror-zero coefficient -1 profile')
        original=[F(v) for v in src['field_reim']]
        require(len(original)==2,'two original source components')
        words,sums,encoding,einfo=encode_source(original,cache,costs)
        m,reflected,minfo=multiply(words,up['unit_uint64'],cache,costs)
        unorm=sum((abs(component64(w)) for w in reflected),F(0));anorm=sum(map(abs,original),F(0))
        eu=nonnegative(up['composed_unit_error_L1_upper'])
        charges={'source_encoding':encoding*unorm,
                 'source_decode':nonnegative(m['source_decode_error_L1_upper_rational'])*unorm,
                 'original_source_norm_times_referenced_unit_error':anorm*eu,
                 'product_RN64':nonnegative(m['product_error_L1_upper_rational'])}
        total=sum(charges.values(),F(0))
        row.update(product_available=True,product_evaluated=not minfo['cache_hit'],source_encoding_cache=einfo,
            product_cache=minfo,source_phase_reference_id=source,terminal_reference_id=terminal,port=port,
            source_original_rational=[pair(v) for v in original],source_limb_uint32=words,
            source_exact_limb_sum_rational=[pair(v) for v in sums],source_encoding_error_L1=pair(encoding),
            source_norm_L1=pair(anorm),observed_unit_norm_L1=pair(unorm),
            referenced_unit_error_L1=pair(eu),mirror_coefficient_exact_reim=[[-1,1],[0,1]],
            measurement=m,error_charges_L1={k:pair(v) for k,v in charges.items()},
            composed_path_field_error_L1=pair(total),accepted_source_absolute_CPU_only=total<=limits[sid])
    out['accepted_source_absolute_CPU_only']=all(p['accepted_source_absolute_CPU_only'] for p in out['paths'])
    if 'retained_closure_gates_UNCHANGED' in u:
        out['retained_closure_gates_UNCHANGED']=deepcopy(u['retained_closure_gates_UNCHANGED'])
    return out


def mode_geometry(g,new_x):
    """Only reconstruct the already-retained mode control binding; no geometry replay."""
    g=deepcopy(g);g['scene_snapshot']['objects']['D']['mode_origin_BU'][0]=new_x
    abi=g['word_ABI'];b=digest({'snapshot':g['scene_snapshot'],'object_order':abi['object_ids'],'source_order':abi['source_order']})
    abi['original_scene_binding_sha256']=b;g['word_ABI_sha256']=digest(abi)
    for p in g['sources']:
        if 'phase_reference_id' in p:p['phase_reference_id']='original-source-zero:'+b+':'+p['source_id']
    return g


def audit(*,model,field_caps):
    require(model==MODEL,'explicit referenced source CPU model')
    pins,units,geometry,cache=load_retained()
    require(type(field_caps) is dict and set(field_caps)==set(units['cases']),'explicit full case caps')
    cases={n:compose(c,geometry[n],field_caps[n],cache,model=model,expected_unit_sha256=digest(c)) for n,c in units['cases'].items()}
    q=payload(json.loads((ROOT/QUOTIENT).read_bytes()))
    controls={}
    for n,c in units['controls'].items():
        g=mode_geometry(geometry['positive'],q['control_inputs'][n]['new_original_modepoint_X'])
        controls[n]=compose(c,g,{sid:CAP for sid in c['source_order']},cache,model=model,expected_unit_sha256=digest(c))
    strict=compose(units['cases']['nonexact_geometry_phase_PASS'],geometry['nonexact_geometry_phase_PASS'],
        {'s':[0,1]},cache,model=model,expected_unit_sha256=digest(units['cases']['nonexact_geometry_phase_PASS']))
    # One NEW pure complex ABI input, not a changed original scene or admission.
    costs=empty_cost();original=[F(0.2),F(-0.15)]
    words,sums,err,einfo=encode_source(original,cache,costs)
    unit=units['numeric_unit_controls'][0]
    measured,reflected,minfo=multiply(words,unit['unit_uint64'],cache,costs)
    numeric={'original_source_rational':[pair(v) for v in original],'retained_numeric_unit_control_sha256':digest(unit),
        'source_encoding_cache':einfo,'source_limb_uint32':words,'source_encoding_error_L1':pair(err),
        'product_cache':minfo,'measurement':measured,'costs':costs,
        'scope':'NEW complex source/product ABI only; retained numeric unit, not scene/field cap/group/GPU evidence'}
    def sumcost(items):
        return {k:sum(c['costs'][k] for c in items.values()) for k in empty_cost()}
    return {'model':MODEL,'pins':pins,'cases':cases,'controls':controls,'strict_field_cap_zero_control':strict,
        'numeric_source_product_control':numeric,'costs':sumcost(cases),'control_costs_separate':sumcost(controls),
        'strict_control_costs_separate':strict['costs'],
        'counts':{'cases':len(cases),'sources':sum(len(c['paths']) for c in cases.values()),
            'products':sum(p['product_available'] for c in cases.values() for p in c['paths']),
            'accepted_cases_CPU_only':sum(c['accepted_source_absolute_CPU_only'] for c in cases.values())},
        'field_cap_scope':'explicit per-source L1 only; same prior source contract cap1e-12 for audit, NOTconf1/phase/group/relative',
        'GPU_executed':False,'ALU_executed':False,'Bpy_executed':False,'execution_authenticated':False,
        'physical_coherence_verified':False,'native_promotion_allowed':False,'accepted_full_field_pipeline':False,
        'scene_field_reduced':False,'detector_evaluated':False,'coherent_group_budget_certified':False,
        'old_upstream_producer_rerun':False,'pending':['reduce THESE referenced source terminals with group/field/power/relative bounds','native/equal-work fullcosts']}
