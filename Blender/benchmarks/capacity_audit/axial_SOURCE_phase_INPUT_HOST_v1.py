"""Opt-in SOURCE principal-phase INPUT syntax; no certificate consumption or policy."""
from copy import deepcopy
import axial_phase_budget_consumer_HOST_v1 as prior
allocation,io=prior.allocation,prior.io
require,digest=prior.require,prior.digest
FALSE=prior.FALSE
MODEL='axial-static-SOURCE-principal-phase-INPUT-HOST-v1'
UNITS='SOURCE-principal-phase-distance-rad'
REFERENCE='fixed-ORIGINAL-A-exp-i-theta-times-ideal-minus-one'
PARENT='coordinacion/respuestas/AXIAL-PHASE-BUDGET-CONSUMER-HOST-001-CODEX.json'
PARENT_SHA='d5f7bf9ec0f9b724ef1ea65810903312e7cd790900ec5aa92fdfa737fe70af9f'
SOURCE_KEYS={'source_id','source_phase_reference_id','terminal_reference_id',
             'common_terminal_reference_id','reference_model','cap_rad'}

def load_retained():
    r=allocation.parse(io.read(PARENT,PARENT_SHA))
    require(r['task_id']=='AXIAL-PHASE-BUDGET-CONSUMER-HOST-001','parent identity')
    pins=io.pins_from(r);pins[PARENT]=PARENT_SHA
    for p,h in pins.items():io.read(p,h)
    loaded,certificates,data,oldpins=prior.load_retained()
    require(all(pins.get(p)==h for p,h in oldpins.items()),'same pinned branches')
    # Only context/packet branches returned. No certificate or numerical proof inspected.
    return loaded[0][0],data,pins

def validate_plan(packet,expected_packet_sha256,plan,*,model):
    require(type(model) is str and model==MODEL,'explicit SOURCE phase INPUT model')
    ctx=allocation.context_from_packet(packet,expected_packet_sha256,model=allocation.MODEL)
    if plan is None:
        return ctx,{'SOURCE_phase_INPUT_valid':False,'reason':'missing explicit SOURCE phase INPUT; absent is not zero',
                    'sources':None,'phase_INPUT_quota_fits':None,'status':'STOP',**dict.fromkeys(FALSE,False)}
    require(type(plan) is dict and set(plan)=={'model','units','context_sha256','sources'},'INPUT exact keys, no UNIT/output/authority aliases')
    for k,v in (('model',MODEL),('units',UNITS),('context_sha256',digest(ctx))):
        require(type(plan[k]) is str and plan[k]==v,'SOURCE phase model/units/context')
    rows=plan['sources'];require(type(rows) is list and len(rows)==len(ctx['source_order']),'complete ordered SOURCE phase INPUT')
    require(all(type(r) is dict and set(r)==SOURCE_KEYS for r in rows),'SOURCE phase INPUT row whitelist')
    require([r['source_id'] for r in rows]==ctx['source_order'],'SOURCE identity/order, no omissions/duplicates')
    require([a['source_id'] for a in ctx['assignments']]==ctx['source_order'],'context complete assignment order')
    for row,a in zip(rows,ctx['assignments']):
        for k in ('source_id','source_phase_reference_id','terminal_reference_id','common_terminal_reference_id'):
            require(type(row[k]) is str and row[k]==a[k],'exact ORIGINAL source and terminal gauge')
        require(a['terminal_reference_id']==a['common_terminal_reference_id'],'fixed common terminal gauge')
        require(type(row['reference_model']) is str and row['reference_model']==REFERENCE,'fixed ORIGINAL ideal reflected SOURCE reference, not UNIT or unwrapped phase')
        allocation.rational(row['cap_rad']) # Strict canonical nonnegative integer pair; bool is not int.
    # Copy only after every source has passed. Zero is valid INPUT, never zero error.
    return ctx,{'SOURCE_phase_INPUT_valid':True,'context_sha256':digest(ctx),'plan_sha256':digest(plan),
                'units':UNITS,'sources':deepcopy(rows),'phase_INPUT_quota_fits':None,
                'status':'STOP',**dict.fromkeys(FALSE,False)}

def audit_INPUT_HOST(case_order,plans,packets,*,model):
    require(type(model) is str and model==MODEL,'explicit SOURCE phase INPUT model')
    require(type(case_order) is list and 1<=len(case_order)<=64 and
            all(type(n) is str and n for n in case_order) and len(set(case_order))==len(case_order),'bounded unique case order')
    require(type(plans) is dict and set(plans)<=set(case_order),'INPUT selected case keys only')
    require(type(packets) is dict and set(case_order)<=set(packets),'complete selected packet coverage')
    checked={}
    for n in case_order:
        ctx,result=validate_plan(packets[n],digest(packets[n]),plans.get(n),model=model)
        checked[n]={'context':ctx,'INPUT':result,'status':'STOP',**dict.fromkeys(FALSE,False)}
    return {'model':MODEL,'case_order':deepcopy(case_order),'cases':checked,
            'valid_INPUT_cases':sum(c['INPUT']['SOURCE_phase_INPUT_valid'] for c in checked.values()),
            'missing_INPUT_cases':sum(not c['INPUT']['SOURCE_phase_INPUT_valid'] for c in checked.values()),
            'certificate_inspections':0,'numeric_phase_comparisons':0,'group_admissions':0,
            'new_native_operations':0,'old_suites_producers_reexecuted':0,'SOURCE_phase_policy_adopted':False,
            'cost_scope':'HOST schema only; IO/context/setup/upstream/full costs UNMEASURED, NOT zero',
            **dict.fromkeys(FALSE,False)}
