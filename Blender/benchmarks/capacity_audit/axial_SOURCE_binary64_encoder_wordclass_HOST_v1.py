"""HOST sufficient encoder word-class theorem under EXPLICIT binary64-grid assumption."""
from copy import deepcopy
from fractions import Fraction as F
import axial_SOURCE_domain_phase_consumer_HOST_v1 as prior
io,allocation,require,digest=prior.io,prior.allocation,prior.require,prior.digest
domain,FALSE,pair=prior.domain,prior.FALSE,prior.pair
MODEL='axial-SOURCE-binary64-grid-encoder-normal-or-zero-sufficient-HOST-v1'
GRID='finite ORIGINAL binary64 values in declared intervals ONLY; not arbitrary real continuum'
ARITH='RN-even binary32/binary64; exact widening; gradual underflow; no FTZ/FMA'
FLAG='sufficient_numeric_encoder_wordclasses_under_explicit_binary64_grid_HOST'
PARENT='coordinacion/respuestas/AXIAL-SOURCE-DOMAIN-PHASE-CONSUMER-HOST-001-CODEX.json'
PARENT_SHA='7ac15550539842bcd45aa9a61fad3d95fcc47b4ba846cfae5bfd362c2ba919ce'
VARIANTS=('real_missing','explicit_None_missing','synthetic_valid')
def pow2(e):
    require(type(e) is int and -4096<=e<=4096,'bounded exact binary exponent')
    return F(1<<e) if e>=0 else F(1,1<<(-e))
def floor_log2(q):
    require(type(q) is F and q>0,'positive exact rational for binade floor')
    e=q.numerator.bit_length()-q.denominator.bit_length()
    return e-1 if q<pow2(e) else e

def component_wordclasses_HOST(interval,*,model,grid,arithmetic_model):
    require(type(model) is str and model==MODEL and type(grid) is str and grid==GRID and
            type(arithmetic_model) is str and arithmetic_model==ARITH,'explicit binary64 subset/model/arithmetic; no implicit continuum admission')
    require(type(interval) is list and len(interval)==2,'closed component interval')
    lo,hi=map(domain.rational,interval);require(lo<=hi,'ordered interval')
    m=domain.distance_zero((lo,hi));M=max(abs(lo),abs(hi))
    out={'model':MODEL,'explicit_grid_assumption':GRID,'arithmetic_model':ARITH,'interval':deepcopy(interval),
         'min_abs':pair(m),'max_abs':pair(M),FLAG:False,'proof':None,
         'actual_scene_domain_grid_authenticated':False,'all_real_continuum_wordclasses_proved':False,
         'frozen_guard_admission_for_entire_box_proved':False,'frozen_guard_verdict':None,
         'signed_zero_execution_policy_proved':False,'SOURCE_graph_executed':False,
         'uniform_executed_SOURCE_error_L1':None,'status':'STOP',**dict.fromkeys(FALSE,False)}
    if lo==hi==0:
        out.update({FLAG:True,'proof':{'case':'exact-zero numeric magnitudes ONLY','numeric_magnitudes_zero':True},
                    'reason':'normal-or-zero numeric class under ideal rounding; +/-zero bits/execution NOT authenticated'})
        return out
    if m<pow2(-74) or M>pow2(127):
        out['reason']='outside conservative sufficient criterion; UNKNOWN, not proof of rejection and no box clipping'
        return out
    e=floor_log2(m);q=pow2(e-52);hg=pow2(e-24);u32=pow2(-24);u64=pow2(-53)
    hmin=(1-u32)*m;hmax=(1+u32)*M;rmax=u32*M;lmax=(1+u32)*rmax
    dmin=(1-u64)*(1-u32*u32)*m;dmax=(1+u64)*(1+u32*u32)*M
    min32=pow2(-126);max32=(pow2(24)-1)*pow2(104)
    min64=pow2(-1022);max64=(pow2(53)-1)*pow2(971)
    require(q>=min32 and hg/q==pow2(28) and hmin>min32 and hmax<max32 and
            rmax<max32 and lmax<max32 and dmin>min64 and dmax<max64,'all conservative ranges and normal-class margins')
    out.update({FLAG:True,'proof':{'case':'nonzero binary64 lattice + Sterbenz conditional arithmetic',
        'binary64_binade_floor':e,'binary64_grid_quantum_lower_bound':pair(q),
        'binary32_high_grid_quantum_lower_bound':pair(hg),'high_grid_multiple':pair(hg/q),
        'u32':pair(u32),'u64':pair(u64),'high_abs_lower_bound':pair(hmin),'high_abs_upper_bound':pair(hmax),
        'exact_residual_abs_upper_bound':pair(rmax),'nonzero_exact_residual_abs_lower_bound':pair(q),
        'low_abs_upper_bound':pair(lmax),'decoded_abs_lower_bound':pair(dmin),'decoded_abs_upper_bound':pair(dmax),
        'sterbenz_same_sign_ratio_in_half_to_two':True,'residual_RN64_exact_under_grid_model':True,
        'SOURCE_product_UNIT_material_nodes_covered':False},
        'reason':'sufficient ONLY for explicit finite binary64 grid: original/high/residual/low/decode numeric classes; NOT bits/device/full SOURCE/guard admission'})
    return out

def load_retained():
    r=allocation.parse(io.read(PARENT,PARENT_SHA));require(r['task_id']=='AXIAL-SOURCE-DOMAIN-PHASE-CONSUMER-HOST-001','parent identity')
    pins=io.pins_from(r);pins[PARENT]=PARENT_SHA
    for p,h in pins.items():io.read(p,h)
    loaded=prior.load_retained();require(all(pins.get(p)==h for p,h in loaded[-1].items()),'same immutable ORIGINAL/domain/guard lineage')
    return loaded[0],loaded[1],io.payload(r)['data'],pins

def audit_wordclasses_HOST(variant,*,model,grid,arithmetic_model):
    require(type(variant) is str and variant in VARIANTS and model==MODEL and grid==GRID and arithmetic_model==ARITH,'explicit retained variant/grid/model')
    packets,inputs,old,pins=load_retained();base=inputs[variant];names=base['case_order']
    plans=inputs['synthetic_domain_INPUT_plans'] if variant=='synthetic_valid' else {}
    prepared={}
    # ALL ORIGINAL INPUT/domain/context/gauges/retained negative evidence before new predicate.
    for name in names:
        ctx=allocation.context_from_packet(packets[name],digest(packets[name]),model=allocation.MODEL)
        require(ctx==base['cases'][name]['context']==old[variant]['cases'][name]['context'],'same complete ORIGINAL context')
        dom=domain.validate_domain(packets[name],ctx,plans.get(name))
        if dom['domain_INPUT_valid']:
            require(dom==inputs['synthetic_validated_domains'][name],'unchanged entire typed domain')
            previous=old[variant]['cases'][name]['sources']
            require(type(previous) is list and [s['source_id'] for s in previous]==ctx['source_order'],'complete previous SOURCE rows')
            for src,p in zip(dom['sources'],previous):
                require(p['domain_source_sha256']==digest(src) and (p['whole_box_guard_admission_disproved'] is None or p['whole_box_guard_admission_disproved'] is True),'same domain + retained rejection/UNKNOWN')
                require(p['uniform_phase_INPUT_quota_fits'] is None and p['status']=='STOP' and all(p[k] is False for k in FALSE),'prior conditional comparison not admission')
        else:require(old[variant]['cases'][name]['sources'] is None,'no numerical point inspection without domain')
        prepared[name]=(ctx,dom)
    cases={};assessed=0
    for name,(ctx,dom) in prepared.items():
        out=None
        if dom['domain_INPUT_valid']:
            out=[]
            for src,p in zip(dom['sources'],old[variant]['cases'][name]['sources']):
                comps=[component_wordclasses_HOST(i,model=model,grid=grid,arithmetic_model=arithmetic_model) for i in src['box_reim']]
                assessed+=2;sufficient=all(c[FLAG] for c in comps)
                if p['whole_box_guard_admission_disproved'] is True:require(not sufficient,'cannot contradict retained binary64 counterexample')
                out.append({'source_id':src['source_id'],'domain_source_sha256':digest(src),'components':comps,
                    FLAG:sufficient,'retained_consumer_SOURCE_sha256':digest(p),
                    'retained_whole_box_guard_admission_disproved':p['whole_box_guard_admission_disproved'],
                    'actual_scene_domain_grid_authenticated':False,'frozen_guard_admission_for_entire_box_proved':False,
                    'uniform_executed_SOURCE_error_L1':None,'status':'STOP',**dict.fromkeys(FALSE,False)})
        cases[name]={'context':ctx,'sources':out,'group_field_bound_L1':None,'group_phase_bound_rad':None,
                     'status':'STOP',**dict.fromkeys(FALSE,False)}
    return {'model':MODEL,'variant':variant,'explicit_grid_assumption':GRID,'arithmetic_model':ARITH,
        'case_order':deepcopy(names),'cases':cases,'inherited_pins_verified':len(pins),'component_predicate_assessments':assessed,
        'actual_scene_domain_grid_authenticated':False,'all_real_continuum_wordclasses_proved':False,
        'new_native_operations':0,'old_suites_producers_reexecuted':0,'old_counterexamples_reexecuted':0,'group_admissions':0,
        'uniform_SOURCE_enclosure_proved':False,'cost_scope':'HOST sufficient predicate; IO/setup/upstream/full UNMEASURED NOT zero',**dict.fromkeys(FALSE,False)}
