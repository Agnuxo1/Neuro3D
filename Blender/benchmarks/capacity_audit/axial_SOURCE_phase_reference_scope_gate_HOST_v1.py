"""Fail-closed HOST gate: fixed ORIGINAL-A phase INPUT is not variable-A box policy."""
from copy import deepcopy
from fractions import Fraction as F
import axial_SOURCE_uniform_ideal_reflection_phase_HOST_v1 as prior
import axial_SOURCE_phase_INPUT_HOST_v1 as schema
io,allocation,require,digest,pair=prior.io,prior.allocation,prior.require,prior.digest,prior.pair
domain,FALSE=prior.domain,prior.FALSE
MODEL='axial-SOURCE-phase-fixed-anchor-vs-variable-box-reference-scope-gate-HOST-v1'
FLAG='SOURCE_phase_reference_scope_assessed_HOST'
PARENT='coordinacion/respuestas/AXIAL-SOURCE-UNIFORM-IDEAL-REFLECTION-PHASE-HOST-001-CODEX.json'
PARENT_SHA='dbadfe64901a5608064f76de805d1f89aef5349404333998d2556e990fb484c0'
INPUT='coordinacion/respuestas/AXIAL-SOURCE-PHASE-INPUT-HOST-001-CODEX.json'
POINT='coordinacion/respuestas/AXIAL-SOURCE-PHASE-QUOTA-CONSUMER-HOST-001-CODEX.json'
VARIANTS=('real_missing','explicit_None_missing','synthetic_retained','phase_zero_FAIL','Horner_zero_FAIL','source_zero_FAIL')

def load_retained():
    r=allocation.parse(io.read(PARENT,PARENT_SHA));require(r['task_id']=='AXIAL-SOURCE-UNIFORM-IDEAL-REFLECTION-PHASE-HOST-001','parent identity')
    pins=io.pins_from(r);pins[PARENT]=PARENT_SHA
    for p,h in pins.items():io.read(p,h)
    loaded=prior.load_retained();require(all(pins.get(p)==h for p,h in loaded[-1].items()),'same SOURCE domain/material lineage')
    def data(p):return io.payload(allocation.parse(io.read(p,pins[p])))['data']
    return loaded[0],loaded[1],io.payload(r)['data'],data(INPUT),data(POINT),pins

def assess_scope_HOST(source,phase_input,*,model):
    require(type(model) is str and model==MODEL,'explicit reference scope model')
    require(type(phase_input) is dict and set(phase_input)==schema.SOURCE_KEYS,'complete existing fixed-A phase INPUT row')
    require(phase_input['reference_model']==schema.REFERENCE,'unchanged fixed ORIGINAL-A reference; not substituted')
    for k in ('source_id','source_phase_reference_id','terminal_reference_id','common_terminal_reference_id'):
        require(type(phase_input[k]) is str and phase_input[k]==source[k],'same SOURCE/terminal gauge')
    allocation.rational(phase_input['cap_rad']) # INPUT syntax only, no numeric cap comparison
    intervals=domain.box_values(source['box_reim']);anchor=[domain.rational(v) for v in source['ORIGINAL_anchor_reim']]
    require(len(anchor)==2 and type(source['ORIGINAL_source_uint64']) is list and len(source['ORIGINAL_source_uint64'])==2 and
        anchor==[prior.prior.guard.bits(w,64) for w in source['ORIGINAL_source_uint64']] and
        all(lo<=a<=hi for a,(lo,hi) in zip(anchor,intervals)),'exact ORIGINAL bit anchor in box')
    singleton=all(lo==a==hi for a,(lo,hi) in zip(anchor,intervals))
    return {'model':MODEL,FLAG:True,'source_id':source['source_id'],'domain_source_sha256':digest(source),
        'phase_INPUT_source_sha256':digest(phase_input),'retained_reference_model':schema.REFERENCE,
        'uniform_target_reference':'variable ORIGINAL A times exp(i fixed ORIGINAL theta) times exact ideal -1',
        'box_is_exact_ORIGINAL_anchor_singleton':singleton,'uniform_reference_scope_supported_by_retained_INPUT':singleton,
        'anchor_quota_retained_cap_rad':deepcopy(phase_input['cap_rad']),
        'reason':'degenerate box equals retained fixed ORIGINAL-A scope ONLY' if singleton else 'fixed ORIGINAL-A INPUT does not declare variable-A box quota policy; no implicit scope expansion',
        'comparison_performed':False,'uniform_phase_INPUT_quota_fits':None,'SOURCE_phase_policy_adopted':False,
        'status':'STOP',**dict.fromkeys(FALSE,False)}

def audit_reference_scope_HOST(variant,*,model):
    require(type(model) is str and model==MODEL and type(variant) is str and variant in VARIANTS,'explicit pinned variant/model')
    packets,amp,certs,inputs,point,pins=load_retained();old=point[variant]
    absent=variant in ('real_missing','explicit_None_missing')
    key='synthetic_zero_INPUT_plans' if variant=='phase_zero_FAIL' else 'synthetic_control_INPUT_plans'
    plans={} if absent else inputs[key]
    domains={} if absent else amp['synthetic_domain_INPUT_plans']
    checked={}
    # ALL INPUT/domain/context/order/gauges before ANY scope assessment.
    for name in old['case_order']:
        ctx,pv=schema.validate_plan(packets[name],digest(packets[name]),plans.get(name),model=schema.MODEL)
        cc=certs['real_missing']['cases'][name] if absent else certs['synthetic_domains']['cases'].get(name,certs['real_missing']['cases'][name])
        require(ctx==old['cases'][name]['context']==cc['context'],'same complete ORIGINAL context')
        require(digest(pv)==digest(old['cases'][name]['phase_INPUT']),'exact unchanged retained phase INPUT')
        dom=domain.validate_domain(packets[name],ctx,domains.get(name))
        baseline=old['cases'][name]['sources'];require(type(baseline) is list and [s['source_id'] for s in baseline]==ctx['source_order'],'complete retained point rows')
        require(type(pv['SOURCE_phase_INPUT_valid']) is bool,'typed INPUT state')
        rows=None
        if dom['domain_INPUT_valid'] and pv['SOURCE_phase_INPUT_valid']:
            require(type(cc['sources']) is list and [s['source_id'] for s in cc['sources']]==ctx['source_order'],'complete conditional box certificates')
            rows=[]
            for src,c,p,b in zip(dom['sources'],cc['sources'],pv['sources'],baseline):
                proof=c['proof']
                require(src['source_id']==c['source_id']==p['source_id']==b['source_id'] and c['domain_source_sha256']==digest(src),'same ordered SOURCE domain certificate')
                require(proof[prior.FLAG] is True and c['whole_box_guard_admission_disproved'] is True and
                    proof['box_reim']==src['box_reim'] and proof['material_executed'] is False and
                    proof['uniform_executed_SOURCE_error_L1'] is None and all(proof[k] is False for k in FALSE),'conditional math only, guard STILL STOP')
                charges=proof['fifteen_conditional_reflected_charges_L1'];require(type(charges) is dict and len(charges)==15,'complete fifteen conditional charges')
                eps=sum((domain.rational(v) for v in charges.values()),F(0));m=domain.rational(proof['amplitude_modulus_lower_bound'])
                require(eps>=0 and m>eps and proof['conditional_reflected_RN_model_error_L1']==pair(eps) and
                    proof['conditional_principal_phase_bound_rad']==pair(eps/(m-eps)),'exact retained conditional phase equation; not an execution certificate')
                rows.append((src,c,p,b))
        checked[name]=(ctx,pv,dom,cc,baseline,rows)
    cases={};assessed=blocked=0
    for name,(ctx,pv,dom,cc,baseline,rows) in checked.items():
        indexed={}
        if rows is not None:
            for src,c,p,b in rows:
                scope=assess_scope_HOST(src,p,model=model);assessed+=1;blocked+=int(not scope['uniform_reference_scope_supported_by_retained_INPUT'])
                indexed[src['source_id']]={'source_id':src['source_id'],'conditional_phase_SOURCE_sha256':digest(c),'scope':scope}
        out=None if absent else []
        if out is not None:
            for b in baseline:
                row=indexed.get(b['source_id'],{'source_id':b['source_id'],'conditional_phase_SOURCE_sha256':None,'scope':None})
                row.update({'retained_point_consumer_source_sha256':digest(b),'retained_point_consumer':deepcopy(b),
                    'uniform_phase_comparison':None,'uniform_phase_INPUT_quota_fits':None,'status':'STOP',**dict.fromkeys(FALSE,False)})
                out.append(row)
        cases[name]={'context':ctx,'phase_INPUT':pv,'domain_INPUT_valid':dom['domain_INPUT_valid'],'sources':out,
            'retained_point_consumer_case_sha256':digest(old['cases'][name]),
            'group_phase_bound_rad':None,'group_field_bound_L1':None,'status':'STOP',**dict.fromkeys(FALSE,False)}
    return {'model':MODEL,'variant':variant,'case_order':deepcopy(old['case_order']),'cases':cases,
        'inherited_pins_verified':len(pins),'reference_scope_assessments':assessed,'blocked_variable_box_quota_scopes':blocked,
        'new_numeric_phase_comparisons':0,'new_native_operations':0,'old_suites_producers_reexecuted':0,
        'SOURCE_phase_policy_adopted':False,'group_admissions':0,
        'cost_scope':'HOST reference-scope compatibility only; full costs UNMEASURED NOT zero',**dict.fromkeys(FALSE,False)}
