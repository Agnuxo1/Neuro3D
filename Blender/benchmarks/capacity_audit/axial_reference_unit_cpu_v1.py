"""Referenced argument -> charged RN64 unit; opt-in CPU, no source fields."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from fractions import Fraction as F
from axial_reference_argument_cpu_v1 import require, digest, pair, rat, nonnegative, payload
from axial_unit_rn64_cpu_v1 import component64, rotation64, permute64, MODEL as HORNER

ROOT=Path(__file__).resolve().parents[3]
MODEL='scene-fixed-original-reference-unit-Horner26-RN64-cache-CPU-v1'
ARGUMENT='scene-fixed-original-reference-argument-RN64-cache-CPU-v1'
REPORT='coordinacion/respuestas/AXIAL-REFERENCE-ARGUMENT-001-CODEX.json'
SHA='7a7e71ac61ffde8a3253a9b5b6880243020d886046a3fd56262992de4174c201'
CACHE_REPORT='coordinacion/respuestas/AXIAL-GEOMETRY-UNIT-001-CODEX.json'
CACHE_SHA='525e7dc3fe7ffb2971390a0cc4034dafe07fd585d64f040223ac8b4ede5ef1cb'
CODE='Blender/benchmarks/capacity_audit/axial_unit_rn64_cpu_v1.py'


class UnitCache:
    """Pure polynomial graph identity, never old geometry/unit acceptance."""
    def __init__(self,pins,old):
        self.codes={n:pins[n] for n in (CODE,
            'Blender/benchmarks/capacity_audit/axial_relative_gate_cpu_v1.py',
            'Blender/benchmarks/capacity_audit/scene_field_producer_cpu_v1.py')}
        self.bank={}
        for c in old.values():
            for p in c['paths']:
                if 'unit_measurement' not in p:
                    continue
                m=p['unit_measurement'];sig=p['unit_cache_signature']
                require(sig['model']==HORNER and sig['code_sha256']==pins[CODE],'unit origin code/model')
                key=self.key(m['angle_uint64']);k=digest(key)
                item={'key':key,'output':deepcopy(m),'output_sha256':digest(m)}
                require(k not in self.bank or self.bank[k]['output_sha256']==item['output_sha256'],'conflicting pure unit cache')
                self.bank[k]=item

    def key(self,word):
        require(abs(component64(word))<=1,'unit argument normal-or-zero domain')
        return {'angle_uint64':word,'model':HORNER,'code_sha256':self.codes,'origin_report_sha256':CACHE_SHA}

    def find(self,word):
        key=self.key(word);item=self.bank.get(digest(key))
        if item is None:
            return None,{'cache_hit':False,'key':key}
        require(item['key']==key and item['output_sha256']==digest(item['output']),'corrupt pure unit cache')
        return deepcopy(item['output']),{'cache_hit':True,'key':key,'output_sha256':item['output_sha256'],
            'not_reused':['scene binding/source-terminal gauges','phase/L1 bounds and caps/admission','execution authentication','cost comparison']}


def load_retained():
    data=(ROOT/REPORT).read_bytes()
    require(hashlib.sha256(data).hexdigest()==SHA,'reference argument report SHA')
    r=json.loads(data)
    require(r['id']=='AXIAL-REFERENCE-ARGUMENT-001' and r['model']==ARGUMENT
        and r['test_run']['rc']==r['independent_validation']['rc']==0,'argument identity/model/verification')
    pins=dict(r['code_doc_sha256'],**{REPORT:SHA})
    require(pins[CACHE_REPORT]==CACHE_SHA,'unit origin report pin')
    for name,sha in pins.items():
        require(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==sha,'changed frozen input '+name)
    old=json.loads((ROOT/CACHE_REPORT).read_bytes())
    return pins,payload(r),UnitCache(pins,payload(old)['audit']['cases'])


def measure(word,cache):
    m,info=cache.find(word)
    if m is None:
        m=rotation64(word,rotation_model=HORNER)
    require(m['angle_uint64']==word and m['RN64_operations']==26 and len(m['operations'])==26,'matching Horner word/graph')
    require(set(m['terms'])=={'cos','sin'} and set(m['coefficients'])=={'cos','sin'}
        and all(len(v)==7 for v in m['coefficients'].values()),'complete two component polynomial contract')
    charges={k:sum((nonnegative(t[k]) for t in m['terms'].values()),F(0))
        for k in ('polynomial_error_upper_rational','Taylor_remainder_upper_rational')}
    pure=sum(charges.values(),F(0))
    require(pair(pure)==m['unit_error_L1_upper_rational'],'pure polynomial and Taylor composition')
    return m,info,charges,pure


def apply_quarter(words,k):
    require(type(k) is int and -2<=k<=2,'signed quarter context')
    out=permute64(words,k)
    return out,{'bit_sign_toggles':2 if k%4==2 else int(k%4 in (1,3)),
                'word_swaps':int(k%4 in (1,3))}


def cost_empty():
    return {'new_Horner_RN64':0,'cached_Horner_RN64_NOT_executed':0,
            'new_coefficient_HOST_RN64':0,'cached_coefficient_HOST_RN64_NOT_executed':0,
            'quarter_bit_sign_toggles_new':0,'quarter_word_swaps_new':0}


def cost_add(costs,info,qcost):
    hit=info['cache_hit']
    costs['cached_Horner_RN64_NOT_executed' if hit else 'new_Horner_RN64']+=26
    costs['cached_coefficient_HOST_RN64_NOT_executed' if hit else 'new_coefficient_HOST_RN64']+=14
    costs['quarter_bit_sign_toggles_new']+=qcost['bit_sign_toggles']
    costs['quarter_word_swaps_new']+=qcost['word_swaps']


def integrate(c,cache,*,model,expected_case_sha256):
    require(model==MODEL,'explicit referenced CPU unit model')
    require(c['model']==ARGUMENT and digest(c)==expected_case_sha256,'referenced argument case digest/model')
    ids=c['source_order'];binding=c['scene_binding_sha256']
    require(type(ids) is list and ids and all(type(n) is str for n in ids)
        and len(set(ids))==len(ids) and ids==[p['source_id'] for p in c['paths']],'ordered full source coverage')
    costs=cost_empty()
    out={'model':MODEL,'argument_case_sha256':expected_case_sha256,'scene_binding_sha256':binding,
         'word_ABI_sha256':c['word_ABI_sha256'],'source_order':ids,'paths':[],'costs':costs,
         'accepted_unit_CPU_only':False,'source_fields_computed':False,'mirror_phase_computed':False,
         'accepted_full_field_pipeline':False,'execution_authenticated':False}
    for p in c['paths']:
        require(all(type(p[k]) is bool for k in ('argument_available','accepted_argument_CPU_only','previous_reference_quotient_accepted')),'strict argument gates')
        row={'source_id':p['source_id'],'previous_argument_accepted':p['accepted_argument_CPU_only'],
             'unit_available':False,'accepted_unit_CPU_only':False}
        out['paths'].append(row)
        if not p['accepted_argument_CPU_only']:
            row['reason']='retained argument/upstream rejection; no unit'
            continue
        require(p['argument_available'] and p['previous_reference_quotient_accepted'],'full referenced argument provenance gates')
        source='original-source-zero:'+binding+':'+p['source_id']
        terminal='fixed-original-plane-mode:'+binding+':D'
        require(p['source_phase_reference_id']==source and p['terminal_reference_id']==terminal,'original source/terminal gauge')
        turn=p['integer_turn'];quarter=p['quarter_index']
        require(type(turn) is int and type(quarter) is int and -2<=quarter<=2,'signed turn/quarter')
        require(rat(p['original_reference_cycles'])-turn-F(quarter,4)==rat(p['original_reduced_reference_cycles']),'original referenced reduced phase')
        upstream=nonnegative(p['composed_argument_phase_bound_rad']);cap=nonnegative(p['phase_budget_rad'])
        require(upstream==nonnegative(p['upstream_reference_phase_bound_rad'])+
            sum((nonnegative(v) for v in p['new_argument_error_charges_rad'].values()),F(0)) and upstream<=cap,'new argument bound and unchanged cap')
        word=p['measurement']['argument_uint64']
        m,info,charges,pure=measure(word,cache)
        total=2*upstream+pure;budget=2*cap
        words,qcost=apply_quarter([m['terms'][n]['output_uint64'] for n in ('cos','sin')],quarter)
        cost_add(costs,info,qcost)
        row.update(unit_available=True,unit_evaluated=not info['cache_hit'],unit_cache=info,unit_measurement=m,
            source_phase_reference_id=source,terminal_reference_id=terminal,integer_turn=turn,quarter_index=quarter,
            original_reference_cycles=p['original_reference_cycles'],original_reduced_reference_cycles=p['original_reduced_reference_cycles'],
            argument_phase_bound_rad=pair(upstream),phase_budget_rad=pair(cap),
            new_unit_error_charges_L1={'reference_phase_Lipschitz':pair(2*upstream),
                'polynomial_RN_and_coefficient':pair(charges['polynomial_error_upper_rational']),
                'Taylor_remainder':pair(charges['Taylor_remainder_upper_rational'])},
            pure_unit_error_L1_upper=pair(pure),composed_unit_error_L1_upper=pair(total),
            derived_unit_L1_budget=pair(budget),unit_uint64=words,
            observed_unit_rational=[pair(component64(w)) for w in words],
            quarter_bit_operations=qcost,accepted_unit_CPU_only=total<=budget)
    out['accepted_unit_CPU_only']=all(p['accepted_unit_CPU_only'] for p in out['paths'])
    if 'retained_closure_gates_UNCHANGED' in c:
        out['retained_closure_gates_UNCHANGED']=deepcopy(c['retained_closure_gates_UNCHANGED'])
    return out


def audit(*,model):
    require(model==MODEL,'explicit referenced CPU unit model')
    pins,data,cache=load_retained()
    cases={n:integrate(c,cache,model=model,expected_case_sha256=digest(c)) for n,c in data['audit']['cases'].items()}
    controls={n:integrate(c,cache,model=model,expected_case_sha256=digest(c)) for n,c in data['audit']['controls'].items()}
    numeric=[];ncost=cost_empty()
    for i,p in enumerate(data['numeric_controls']):
        word=p['measurement']['argument_uint64'];quarter=(-2,-1,0,1,2,0)[i]
        m,info,charges,pure=measure(word,cache)
        words,qcost=apply_quarter([m['terms'][n]['output_uint64'] for n in ('cos','sin')],quarter)
        cost_add(ncost,info,qcost)
        numeric.append({'input_argument_uint64':word,'retained_argument_control_sha256':digest(p),
            'quarter_index':quarter,'unit_measurement':m,'unit_cache':info,'unit_uint64':words,
            'pure_unit_error_L1_upper':pair(pure),'quarter_bit_operations':qcost,
            'scope':'NEW unit graph for retained synthetic ABI argument only; no scene/phase budget/physical optics'})
    def sumcost(items):
        return {k:sum(c['costs'][k] for c in items.values()) for k in cost_empty()}
    return {'model':MODEL,'pins':pins,'cases':cases,'controls':controls,'numeric_unit_controls':numeric,
        'costs':sumcost(cases),'control_costs_separate':sumcost(controls),'numeric_unit_control_costs_separate':ncost,
        'counts':{'cases':len(cases),'sources':sum(len(c['paths']) for c in cases.values()),
                  'units':sum(p['unit_available'] for c in cases.values() for p in c['paths']),
                  'accepted_cases_CPU_only':sum(c['accepted_unit_CPU_only'] for c in cases.values())},
        'GPU_executed':False,'ALU_executed':False,'Bpy_executed':False,'execution_authenticated':False,
        'physical_coherence_verified':False,'native_promotion_allowed':False,'accepted_full_field_pipeline':False,
        'source_fields_computed':False,'mirror_phase_computed':False,'old_upstream_producer_rerun':False,
        'scope':'referenced propagation unit only; not mirror/source multiplication/group/reduction/native/full costs',
        'pending':['original source/mirror product from THIS referenced unit with new charges','native authentication/equal-work fullcosts']}
