"""Opt-in static per-stage L1 INPUT accounting against retained ideal prefix evidence."""
from copy import deepcopy
from fractions import Fraction as F
import axial_ideal_reflection_stage_CPU_v1 as prior
io=prior.io
allocation=prior.allocation
require=prior.require
digest=prior.digest
pair=prior.pair
MODEL='axial-static-seven-stage-L1-allocation-HOST-v1'
UNITS=allocation.UNITS
PREVIOUS='coordinacion/respuestas/AXIAL-IDEAL-REFLECTION-STAGE-CPU-001-CODEX.json'
PREVIOUS_SHA='a336c4c8defd4deb1330e33cae46f4180e84a48dc7e227adea49e85061aaa8bc'
STAGES=('source_encoding_L1','source_decode_RN64_L1','source_Horner_L1','source_decoded_argument_L1',
        'source_geometry_reference_wavelength_L1','source_product_RN64_L1','ideal_material_L1')
RESERVES=('reduction_L1','terminal_projection_L1')
FALSE=prior.FALSE+('reflection_coefficient_applied','reflection_coefficient_executed_new')

def load_retained():
    r=allocation.parse(io.read(PREVIOUS,PREVIOUS_SHA))
    require(r['task_id']=='AXIAL-IDEAL-REFLECTION-STAGE-CPU-001','previous task identity')
    pins=io.pins_from(r);pins[PREVIOUS]=PREVIOUS_SHA
    for p,h in pins.items():io.read(p,h)
    def data(p):return io.payload(allocation.parse(io.read(p,pins[p])))
    old=io.payload(r)['data']['audit'];packets=data(io.INGRESS)['packets']
    packets.update({n:v['parent'] for n,v in data(io.PRESENCE)['synthetic_controls'].items()})
    require(set(packets)==set(old['cases']),'complete retained cases')
    return packets,old,pins

def validate_plan(packet,expected_sha,plan,*,model):
    require(model==MODEL,'explicit per-stage HOST model')
    ctx=allocation.context_from_packet(packet,expected_sha,model=allocation.MODEL)
    if plan is None:return ctx,{'allocation_INPUT_valid':False,'reason':'missing explicit per-source AND per-stage INPUT; no default split/zero',**dict.fromkeys(FALSE,False)}
    require(type(plan) is dict and set(plan)=={'model','units','context_sha256','sources','groups'},'plan whitelist, no outputs or authority flags')
    require(plan['model']==MODEL and plan['units']==UNITS and plan['context_sha256']==digest(ctx),'model units context binding')
    ss=plan['sources'];gs=plan['groups']
    require(type(ss) is list and len(ss)==len(ctx['source_order']),'complete source allocations')
    require(all(type(s) is dict and set(s)=={'source_id','cap_L1','stages_L1'} for s in ss),'source plan whitelist')
    require([s['source_id'] for s in ss]==ctx['source_order'],'complete ordered unique sources')
    rows=[]
    for s in ss:
        require(type(s['stages_L1']) is dict and set(s['stages_L1'])==set(STAGES),'all seven stage quotas, no aliases')
        caps={k:allocation.rational(s['stages_L1'][k]) for k in STAGES};cap=allocation.rational(s['cap_L1'])
        spent=sum(caps.values(),F(0));require(spent<=cap,'stage quotas exceed explicit source cap')
        rows.append({'source_id':s['source_id'],'cap_L1':pair(cap),'stages_L1':deepcopy(s['stages_L1']),
            'stage_caps_sum_L1':pair(spent),'unallocated_source_L1':pair(cap-spent)})
    require(type(gs) is list and len(gs)==len(ctx['groups']),'complete group reservations')
    require(all(type(g) is dict and set(g)=={'port','coherence_group','reserves_L1'} for g in gs),'group plan whitelist')
    require([[g['port'],g['coherence_group']] for g in gs]==ctx['groups'],'ordered port/coherence groups')
    groups=[]
    for g in gs:
        require(type(g['reserves_L1']) is dict and set(g['reserves_L1'])==set(RESERVES),'explicit field-L1 remaining-stage reserves; power is NOT L1')
        rs={k:allocation.rational(g['reserves_L1'][k]) for k in RESERVES}
        groups.append({'port':g['port'],'coherence_group':g['coherence_group'],'remaining_stages_reserved_L1':pair(sum(rs.values(),F(0)))})
    projected={'model':allocation.MODEL,'units':UNITS,'context_sha256':digest(ctx),
        'sources':[{'source_id':s['source_id'],'cap_L1':s['cap_L1']} for s in ss],'groups':groups}
    old=allocation.audit_allocation_HOST(packet,expected_sha,projected,model=allocation.MODEL)['result']
    require(old['allocation_INPUT_valid'] is True,'projected source/group INPUT accounting')
    return ctx,{'allocation_INPUT_valid':True,'context_sha256':digest(ctx),'plan_sha256':digest(plan),
        'sources':rows,'groups':deepcopy(gs),'projected_legacy_input_accounting':old,
        'unchanged_limits':deepcopy(ctx['unchanged_limits']),**dict.fromkeys(FALSE,False)}

def compare_source(row,source_plan):
    if row[prior.FLAG] is not True:
        return {'source_id':row['source_id'],'retained_point_stage_budget_fits':False,'reason':row['reason'],
            'retained_source_row_sha256':digest(row),'stage_comparisons':None,**dict.fromkeys(FALSE,False)}
    r=row['result'];require(r[prior.FLAG] is True,'retained ideal reflection execution')
    require(r['profile']['ideal_coefficient_exact_reim']==[[-1,1],[0,1]],'fixed ideal -1 profile')
    charges={k:allocation.rational(v) for k,v in r['charges_L1'].items()}
    require(set(charges)==set(STAGES)-{'ideal_material_L1'},'six prior charges exactly')
    material=allocation.rational(r['profile']['new_coefficient_error_L1'])+allocation.rational(r['additional_reflection_rounding_error_L1'])
    require(material==0,'only existing exact ideal material profile, no general coefficient proof')
    charges['ideal_material_L1']=material
    total=sum(charges.values(),F(0));require(total==allocation.rational(r['point_reflected_source_to_fixed_ORIGINAL_bound_L1']),'seven charge conservation')
    require(source_plan['source_id']==row['source_id'],'same source plan')
    comparisons={k:{'charge_L1':pair(charges[k]),'quota_L1':source_plan['stages_L1'][k],
        'fits':charges[k]<=allocation.rational(source_plan['stages_L1'][k])} for k in STAGES}
    total_fits=total<=allocation.rational(source_plan['cap_L1']);fits=total_fits and all(v['fits'] for v in comparisons.values())
    return {'source_id':row['source_id'],'retained_source_row_sha256':digest(row),'stage_comparisons':comparisons,
        'sum_charges_L1':pair(total),'source_cap_L1':source_plan['cap_L1'],'total_charge_fits_source_cap':total_fits,
        'retained_point_stage_budget_fits':fits,'reason':'partial retained point-stage comparison only; no group/reduction/power/readout proof',
        **dict.fromkeys(FALSE,False)}

def audit_stage_allocation_HOST(case_names,plans_by_case,*,model):
    require(model==MODEL,'explicit per-stage HOST model')
    require(type(case_names) is list and 1<=len(case_names)<=64 and all(type(n) is str and n for n in case_names)
            and len(set(case_names))==len(case_names),'bounded unique cases')
    require(type(plans_by_case) is dict and set(plans_by_case)<=set(case_names),'selected INPUT plans only')
    packets,old,pins=load_retained();require(set(case_names)<=set(packets),'known cases')
    # Validate every static INPUT plan before inspecting retained numerical charges.
    admitted={}
    for n in case_names:
        ctx,p=validate_plan(packets[n],digest(packets[n]),plans_by_case.get(n),model=model)
        require(ctx==old['cases'][n]['context'],'same complete retained INPUT context')
        admitted[n]=(ctx,p)
    cases={};valid=missing=fits=0
    for n in case_names:
        ctx,p=admitted[n];rows=[]
        require([r['source_id'] for r in old['cases'][n]['sources']]==ctx['source_order'],'complete source evidence order')
        if not p['allocation_INPUT_valid']:
            missing+=1
            rows=[{'source_id':s,'retained_point_stage_budget_fits':False,'reason':p['reason'],
                'stage_comparisons':None,**dict.fromkeys(FALSE,False)} for s in ctx['source_order']]
        else:
            valid+=1
            for r,s in zip(old['cases'][n]['sources'],p['sources']):
                out=compare_source(r,s);fits+=int(out['retained_point_stage_budget_fits']);rows.append(out)
        cases[n]={'context':ctx,'allocation_INPUT':p,'sources':rows,'status':'STOP',**dict.fromkeys(FALSE,False)}
    return {'model':MODEL,'case_order':deepcopy(case_names),'cases':cases,'inherited_pins_verified':len(pins),
        'explicit_INPUT_plans_valid':valid,'missing_INPUT_plans_STOP':missing,'retained_point_source_stage_comparisons_fit':fits,
        'new_numeric_scene_source_material_reduction_power_readout_executions':0,'old_suites_producers_reexecuted':0,
        'allocation_policy_adopted':False,'cost_scope':'static HOST INPUT/rational comparisons only; IO/pins/setup/retained upstream and remaining full costs UNMEASURED, never zero',**dict.fromkeys(FALSE,False)}
