"""Opt-in HOST comparison of retained conditional box phase against explicit domain INPUT."""
from copy import deepcopy
from fractions import Fraction as F
import axial_SOURCE_domain_phase_INPUT_HOST_v1 as schema
import axial_SOURCE_uniform_ideal_reflection_phase_HOST_v1 as phase
io,allocation,require,digest=schema.io,schema.allocation,schema.require,schema.digest
domain,FALSE,pair=schema.domain,schema.FALSE,phase.pair
MODEL='axial-variable-A-domain-SOURCE-phase-quota-conditional-consumer-HOST-v1'
FLAG='conditional_SOURCE_domain_phase_quota_compared_HOST'
REFERENCE='variable ORIGINAL A times exp(i fixed ORIGINAL theta) times exact ideal -1'
PARENT='coordinacion/respuestas/AXIAL-SOURCE-DOMAIN-PHASE-INPUT-HOST-001-CODEX.json'
PARENT_SHA='e23030aab9ff6eff0391424a97acd3f74a868dbce12698b43cb73a8f40c854db'
CERTIFICATE='coordinacion/respuestas/AXIAL-SOURCE-UNIFORM-IDEAL-REFLECTION-PHASE-HOST-001-CODEX.json'
VARIANTS=('real_missing','explicit_None_missing','domain_present_phase_missing','synthetic_valid','synthetic_zero_valid')
CERT_KEYS={'source_id','domain_source_sha256','retained_UNIT_link_SOURCE_sha256',
           'retained_material_admission_SOURCE_sha256','proof','whole_box_guard_admission_disproved'}

def load_retained():
    r=allocation.parse(io.read(PARENT,PARENT_SHA));require(r['task_id']=='AXIAL-SOURCE-DOMAIN-PHASE-INPUT-HOST-001','parent identity')
    pins=io.pins_from(r);pins[PARENT]=PARENT_SHA
    for p,h in pins.items():io.read(p,h)
    loaded=schema.load_retained()
    require(all(pins.get(p)==h for p,h in loaded[-1].items()),'same immutable INPUT/domain lineage')
    cert=allocation.parse(io.read(CERTIFICATE,pins[CERTIFICATE]))
    require(cert['task_id']=='AXIAL-SOURCE-UNIFORM-IDEAL-REFLECTION-PHASE-HOST-001' and cert['model']==phase.MODEL,'conditional phase certificate identity')
    return loaded[0],io.payload(r)['data'],io.payload(cert)['data'],pins

def inspect_certificate_HOST(source,phase_input,cert,*,model):
    require(type(model) is str and model==MODEL,'explicit conditional consumer model')
    require(type(phase_input) is dict and set(phase_input)==schema.SOURCE_KEYS and
            phase_input['reference_model']==schema.REFERENCE and
            phase_input['domain_source_sha256']==digest(source),'exact typed variable-domain INPUT SOURCE')
    for k in schema.GAUGES:require(type(phase_input[k]) is str and phase_input[k]==source[k],'same SOURCE/terminal gauges')
    require(source['terminal_reference_id']==source['common_terminal_reference_id'],'same common terminal reference')
    require(type(cert) is dict and set(cert)==CERT_KEYS and cert['source_id']==source['source_id']
            and cert['domain_source_sha256']==digest(source),'exact complete SOURCE domain certificate binding')
    for key in ('retained_UNIT_link_SOURCE_sha256','retained_material_admission_SOURCE_sha256'):
        h=cert[key];require(type(h) is str and len(h)==64 and all(x in '0123456789abcdef' for x in h),'retained dependency SHA')
    require(cert['whole_box_guard_admission_disproved'] is True,'retained whole-box guard rejection MUST remain')
    p=cert['proof']
    require(type(p) is dict and p['model']==phase.MODEL and p['material_model']==phase.MATERIAL_MODEL and
            p['reference']==REFERENCE and p['box_reim']==source['box_reim'],'same variable-A box/ideal-minus-one conditional reference')
    require(p[phase.FLAG] is True and p['material_executed'] is p['physical_material_authenticated'] is
            p['unwrapped_phase_proved'] is p['frozen_guard_admission_for_entire_box_proved'] is False and
            p['uniform_executed_SOURCE_error_L1'] is p['executed_material_charge_L1'] is p['phase_INPUT_quota_fits'] is None
            and p['status']=='STOP' and all(p[k] is False for k in FALSE),'conditional math only; NOT actual error/material/policy/guard')
    charges=p['fifteen_conditional_reflected_charges_L1']
    require(type(charges) is dict and set(charges)==set(phase.CHARGES)|{'ideal_material_exact_model_L1'} and
            charges['ideal_material_exact_model_L1']==[0,1],'fifteen separate charges ONCE; ideal-zero algebraic only')
    values=[domain.rational(v) for v in charges.values()]
    require(all(v>=0 for v in values),'nonnegative conditional charges')
    eps=sum(values,F(0));intervals=domain.box_values(source['box_reim'])
    distances=[domain.distance_zero(i) for i in intervals];m=max(distances)
    require(p['component_min_abs']==list(map(pair,distances)) and p['amplitude_modulus_lower_bound']==pair(m)
            and p['conditional_reflected_RN_model_error_L1']==pair(eps) and m>eps>=0
            and p['positive_radial_projection_lower_bound']==pair(m-eps)
            and p['conditional_principal_phase_bound_rad']==pair(eps/(m-eps)),
            'exact conditional charge/radial/phase equations on ENTIRE box')
    # Strictly validate canonical phase rational and cap; never inspect decoded point output.
    require(domain.rational(p['conditional_principal_phase_bound_rad'])>=0 and domain.rational(phase_input['cap_rad'])>=0,'typed nonnegative bound/cap')
    return {'retained_conditional_SOURCE_sha256':digest(cert),'retained_conditional_proof_sha256':digest(p),
            'domain_source_sha256':digest(source),'phase_INPUT_source_sha256':digest(phase_input),
            'conditional_principal_phase_bound_rad':deepcopy(p['conditional_principal_phase_bound_rad']),
            'whole_box_guard_admission_disproved':True}

def compare_conditional_HOST(bound,cap,*,model):
    require(type(model) is str and model==MODEL,'explicit conditional comparison model')
    q=domain.rational(cap);require(q>=0,'nonnegative explicit cap')
    out={'model':MODEL,FLAG:False,'conditional_principal_phase_bound_rad':deepcopy(bound),
         'synthetic_INPUT_cap_rad':deepcopy(cap),'conditional_phase_quota_fits':None,
         'uniform_phase_INPUT_quota_fits':None,'uniform_executed_SOURCE_error_L1':None,
         'SOURCE_phase_policy_adopted':False,'status':'STOP',**dict.fromkeys(FALSE,False)}
    if bound is None:out['reason']='missing conditional certificate is NOT zero bound';return out
    b=domain.rational(bound);require(b>=0,'nonnegative conditional bound')
    out.update({FLAG:True,'conditional_phase_quota_fits':b<=q,
                'reason':'conditional mathematical bound <= explicit synthetic INPUT cap ONLY; guard execution/policy STILL STOP'})
    return out

def audit_consumer_HOST(variant,*,model):
    require(type(variant) is str and variant in VARIANTS and type(model) is str and model==MODEL,'explicit pinned variant/model')
    packets,inputs,certs,pins=load_retained();baseline=inputs[variant];names=baseline['case_order']
    domains={} if variant in ('real_missing','explicit_None_missing') else inputs['synthetic_domain_INPUT_plans']
    plans=inputs['synthetic_control_INPUT_plans'] if variant=='synthetic_valid' else inputs['synthetic_zero_INPUT_plans'] if variant=='synthetic_zero_valid' else {}
    if variant=='explicit_None_missing':plans=dict.fromkeys(names)
    # Stage 1: ALL INPUT first, no conditional certificate inspection.
    checked=schema.audit_INPUT_HOST(names,domains,plans,packets,model=schema.MODEL)
    prepared={}
    for name in names:
        case=checked['cases'][name];ctx=case['context'];v=case['INPUT']
        require(ctx==baseline['cases'][name]['context'] and digest(v)==digest(baseline['cases'][name]['INPUT']),'same complete immutable typed INPUT/context')
        dom=domain.validate_domain(packets[name],ctx,domains.get(name))
        prepared[name]=(ctx,v,dom)
    # Stage 2: ALL retained certificate/context/coverage checks before ANY comparison.
    inspected={};count=missing=0
    for name,(ctx,v,dom) in prepared.items():
        rows=None
        if v[schema.FLAG]:
            cc=certs['synthetic_domains']['cases'].get(name,certs['real_missing']['cases'][name])
            require(ctx==cc['context'],'same complete ORIGINAL certificate context')
            rows=[]
            if cc['sources'] is None:
                for src,p in zip(dom['sources'],v['sources']):rows.append((src,p,None));missing+=1
            else:
                require(type(cc['sources']) is list and [x['source_id'] for x in cc['sources']]==ctx['source_order'],'complete ordered certificates; no partial SOURCE acceptance')
                for src,p,cert in zip(dom['sources'],v['sources'],cc['sources']):
                    rows.append((src,p,inspect_certificate_HOST(src,p,cert,model=model)));count+=1
        inspected[name]=(ctx,v,rows)
    # Stage 3: only new exact HOST conditional comparisons. No producer / old suite replay.
    cases={};compared=fits=fails=0
    for name,(ctx,v,rows) in inspected.items():
        out=None
        if rows is not None:
            out=[]
            for src,p,c in rows:
                comparison=compare_conditional_HOST(None if c is None else c['conditional_principal_phase_bound_rad'],p['cap_rad'],model=model)
                compared+=int(comparison[FLAG]);fits+=int(comparison['conditional_phase_quota_fits'] is True);fails+=int(comparison['conditional_phase_quota_fits'] is False)
                out.append({'source_id':src['source_id'],'domain_source_sha256':digest(src),
                            'phase_INPUT_source_sha256':digest(p),'conditional_certificate':c,'conditional_comparison':comparison,
                            'whole_box_guard_admission_disproved':None if c is None else True,
                            'uniform_phase_INPUT_quota_fits':None,'status':'STOP',**dict.fromkeys(FALSE,False)})
        cases[name]={'context':ctx,'phase_INPUT':v,'sources':out,'group_phase_bound_rad':None,'group_field_bound_L1':None,
                     'status':'STOP',**dict.fromkeys(FALSE,False)}
    return {'model':MODEL,'variant':variant,'case_order':deepcopy(names),'cases':cases,
            'inherited_pins_verified':len(pins),'conditional_certificate_inspections':count,'missing_conditional_certificate_sources':missing,
            'new_conditional_phase_comparisons':compared,'conditional_fit_count':fits,'conditional_fail_count':fails,
            'SOURCE_phase_policy_adopted':False,'group_admissions':0,'new_native_operations':0,
            'old_suites_producers_reexecuted':0,'uniform_SOURCE_enclosure_proved':False,
            'cost_scope':'HOST conditional comparison; IO/setup/domain/upstream/full costs UNMEASURED NOT zero',**dict.fromkeys(FALSE,False)}
