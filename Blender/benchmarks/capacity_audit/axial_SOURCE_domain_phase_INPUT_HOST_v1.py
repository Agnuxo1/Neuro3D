"""Opt-in variable-A-domain SOURCE phase INPUT. Syntax binding, never phase policy."""
from copy import deepcopy
import axial_SOURCE_phase_reference_scope_gate_HOST_v1 as prior
io,allocation,require,digest=prior.io,prior.allocation,prior.require,prior.digest
domain,FALSE=prior.domain,prior.FALSE
MODEL='axial-variable-A-domain-SOURCE-principal-phase-INPUT-HOST-v1'
UNITS='SOURCE-principal-phase-distance-rad'
REFERENCE='variable-ORIGINAL-A-in-declared-box-exp-i-fixed-ORIGINAL-theta-times-ideal-minus-one'
SCOPE=domain.SCOPE
FLAG='SOURCE_domain_phase_INPUT_valid_HOST'
PARENT='coordinacion/respuestas/AXIAL-SOURCE-PHASE-REFERENCE-SCOPE-GATE-HOST-001-CODEX.json'
PARENT_SHA='a3d8a1d5d4a9b59f8c5d38a265f965576afb14d84d5f5f2dd0e8fd669eabf34e'
SOURCE_KEYS=prior.schema.SOURCE_KEYS|{'domain_source_sha256'}
PLAN_KEYS={'model','units','context_sha256','domain_sha256','scope','sources'}
GAUGES=('source_id','source_phase_reference_id','terminal_reference_id','common_terminal_reference_id')

def load_retained():
    r=allocation.parse(io.read(PARENT,PARENT_SHA))
    require(r['task_id']=='AXIAL-SOURCE-PHASE-REFERENCE-SCOPE-GATE-HOST-001','parent identity')
    pins=io.pins_from(r);pins[PARENT]=PARENT_SHA
    for p,h in pins.items():io.read(p,h)
    loaded=prior.load_retained()
    require(all(pins.get(p)==h for p,h in loaded[-1].items()),'same pinned lineage')
    return loaded[0],loaded[1],loaded[3],pins # packets, amplitude domains, old point INPUT, pins

def validate_plan(packet,expected_packet_sha256,domain_plan,plan,*,model):
    require(type(model) is str and model==MODEL,'explicit new variable-A-domain phase INPUT model')
    ctx=allocation.context_from_packet(packet,expected_packet_sha256,model=allocation.MODEL)
    dom=domain.validate_domain(packet,ctx,domain_plan)
    base={FLAG:False,'sources':None,'context_sha256':digest(ctx),
          'domain_sha256':dom.get('domain_sha256'),'domain_INPUT_valid':dom['domain_INPUT_valid'],
          'uniform_phase_INPUT_quota_fits':None,'uniform_executed_SOURCE_error_L1':None,
          'SOURCE_phase_policy_adopted':False,'frozen_guard_admission_for_entire_box_proved':False,
          'status':'STOP',**dict.fromkeys(FALSE,False)}
    if plan is None:
        return ctx,{**base,'reason':'missing explicit variable-domain SOURCE phase INPUT; absent is not zero'}
    require(dom['domain_INPUT_valid'] is True,'phase INPUT requires complete explicit domain, never anchor fallback')
    require(type(plan) is dict and set(plan)==PLAN_KEYS,'new INPUT exact keys, no legacy scope adapter/output/authority')
    for k,v in (('model',MODEL),('units',UNITS),('context_sha256',digest(ctx)),
                ('domain_sha256',dom['domain_sha256']),('scope',SCOPE)):
        require(type(plan[k]) is str and plan[k]==v,'exact variable-domain INPUT model/units/context/domain/scope')
    rows=plan['sources']
    require(type(rows) is list and len(rows)==len(ctx['source_order']) and
            all(type(s) is dict and set(s)==SOURCE_KEYS for s in rows),'complete SOURCE row whitelist')
    require([s['source_id'] for s in rows]==ctx['source_order']==[a['source_id'] for a in ctx['assignments']]
            ==[s['source_id'] for s in dom['sources']],'complete ordered source/domain coverage')
    for row,a,src in zip(rows,ctx['assignments'],dom['sources']):
        for k in GAUGES:
            require(type(row[k]) is str and row[k]==a[k]==src[k],'exact ORIGINAL SOURCE/terminal gauges')
        require(a['terminal_reference_id']==a['common_terminal_reference_id'],'fixed common terminal gauge')
        require(type(row['reference_model']) is str and row['reference_model']==REFERENCE,
                'variable ORIGINAL A reference explicitly required; point/UNIT/unwrapped not substituted')
        require(type(row['domain_source_sha256']) is str and row['domain_source_sha256']==digest(src),
                'exact entire validated SOURCE domain binding')
        cap=domain.rational(row['cap_rad']) # NEW schema bound: <=4096 bits; frozen point parser unchanged.
        require(cap>=0,'nonnegative SOURCE phase INPUT cap; syntax only')
    return ctx,{**base,FLAG:True,'units':UNITS,'scope':SCOPE,'reference_model':REFERENCE,
                'plan_sha256':digest(plan),'sources':deepcopy(rows),
                'reason':'schema binding only; cap syntax is not real policy, certificate comparison or guard admission'}

def audit_INPUT_HOST(case_order,domain_plans,plans,packets,*,model):
    require(type(model) is str and model==MODEL,'explicit new INPUT model')
    require(type(case_order) is list and 1<=len(case_order)<=64 and
            all(type(n) is str and n for n in case_order) and len(set(case_order))==len(case_order),
            'bounded unique case order')
    require(type(plans) is dict and set(plans)<=set(case_order) and
            type(domain_plans) is dict and set(domain_plans)<=set(case_order),'selected INPUT/domain keys only')
    require(type(packets) is dict and set(case_order)<=set(packets),'complete packet coverage')
    checked={}
    for name in case_order:
        ctx,v=validate_plan(packets[name],digest(packets[name]),domain_plans.get(name),plans.get(name),model=model)
        checked[name]={'context':ctx,'INPUT':v,'status':'STOP',**dict.fromkeys(FALSE,False)}
    return {'model':MODEL,'case_order':deepcopy(case_order),'cases':checked,
            'valid_INPUT_cases':sum(c['INPUT'][FLAG] for c in checked.values()),
            'missing_INPUT_cases':sum(not c['INPUT'][FLAG] for c in checked.values()),
            'certificate_inspections':0,'numeric_phase_comparisons':0,'group_admissions':0,
            'new_native_operations':0,'old_suites_producers_reexecuted':0,'SOURCE_phase_policy_adopted':False,
            'cost_scope':'HOST syntax binding only; IO/context/domain/setup/upstream/full costs UNMEASURED NOT zero',
            **dict.fromkeys(FALSE,False)}
