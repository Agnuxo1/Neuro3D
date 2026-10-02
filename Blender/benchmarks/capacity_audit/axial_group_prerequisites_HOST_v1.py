"""Opt-in HOST prerequisite report; no group sum or future proof admission."""
from copy import deepcopy
import axial_reflected_source_budget_bridge_HOST_v1 as prior
io,allocation,quotas=prior.io,prior.allocation,prior.quotas
require,digest=prior.require,prior.digest
FALSE=prior.FALSE
MODEL='axial-current-reflected-group-prerequisites-HOST-v1'
PARENT='coordinacion/respuestas/AXIAL-REFLECTED-SOURCE-BUDGET-BRIDGE-HOST-001-CODEX.json'
PARENT_SHA='06d974cf7d7ab792377aef9d67d6ca2fcaf301a8932237a05eab5277018cd384'
VARIANTS=('real_missing','synthetic_partial','Horner_zero_FAIL','source_zero_FAIL','explicit_None_missing')

def load_retained():
    r=allocation.parse(io.read(PARENT,PARENT_SHA))
    require(r['task_id']=='AXIAL-REFLECTED-SOURCE-BUDGET-BRIDGE-HOST-001','parent task')
    pins=io.pins_from(r);pins[PARENT]=PARENT_SHA
    for p,h in pins.items():io.read(p,h)
    retained,reflection,material,oldpins=prior.load_retained()
    require(all(pins.get(p)==h for p,h in oldpins.items()),'same reflected current source branch')
    return retained[0],io.payload(r)['data'],retained[-1],pins

def select(data,plan_data,variant):
    require(type(variant) is str and variant in VARIANTS,'explicit retained variant')
    if variant=='real_missing':return data[variant],{}
    if variant=='synthetic_partial':
        require(data['retained_synthetic_INPUT_plans']==plan_data['synthetic_INPUT_plans'],'unchanged retained CONTROL INPUT')
        return data[variant],plan_data['synthetic_INPUT_plans']
    if variant=='explicit_None_missing':return data[variant],{'thin_resolved':None}
    name,key=('nonexact_geometry_phase_PASS','stage_overspend_control') if variant=='Horner_zero_FAIL' else ('thin_resolved','explicit_zero_FAIL')
    require(data[variant]['retained_INPUT_plan']==plan_data[key]['INPUT_plan'],'unchanged retained FAIL INPUT')
    return data[variant]['audit'],{name:plan_data[key]['INPUT_plan']}

def validate_case(packet,case,plan):
    ctx,valid=quotas.validate_plan(packet,digest(packet),plan,model=quotas.MODEL)
    require(case['context']==ctx and case['allocation_INPUT']==valid,'same complete ORIGINAL INPUT context and plan')
    require(case['status']=='STOP' and all(case[n] is False for n in FALSE),'retained case scope STOP')
    require(type(case['sources']) is list and [r['source_id'] for r in case['sources']]==ctx['source_order'],'complete ordered sources')
    for row in case['sources']:
        require(all(row[n] is False for n in FALSE),'typed false source scope')
        require(type(row['partial_seven_stage_comparison_fits']) is bool,'typed point fit')
        if row['stage_comparisons'] is None:
            require(row['partial_seven_stage_comparison_fits'] is False,'missing point stages cannot fit')
        else:
            require(valid['allocation_INPUT_valid'] is True and row['retained_reflection_executed_CPU'] is True,'executed retained stages require INPUT')
            require(type(row['new_material_operations']) is int and row['new_material_operations']==0,'no new material execution')
            require(set(row['stage_comparisons'])==set(quotas.STAGES),'all seven stage comparisons')
            require(all(type(v['fits']) is bool for v in row['stage_comparisons'].values()),'typed stage fits')
            require(type(row['partial_total_fits_source_cap']) is bool and
                row['partial_seven_stage_comparison_fits']==(row['partial_total_fits_source_cap'] and all(v['fits'] for v in row['stage_comparisons'].values())),'point fit not group admission')
    return ctx,valid

def group_report(case,ctx,valid):
    rows={r['source_id']:r for r in case['sources']};out=[]
    for port,group in ctx['groups']:
        assignments=[a for a in ctx['assignments'] if (a['port'],a['coherence_group'])==(port,group)]
        members=[a['source_id'] for a in assignments]
        require(members and len(members)==len(set(members)),'nonempty complete group')
        require(all(a['terminal_reference_id']==a['common_terminal_reference_id']==assignments[0]['common_terminal_reference_id'] for a in assignments),'same common terminal reference')
        missing=[s for s in members if rows[s]['stage_comparisons'] is None]
        failing=[s for s in members if rows[s]['stage_comparisons'] is not None and not rows[s]['partial_seven_stage_comparison_fits']]
        reserved=None
        blockers=[]
        if not valid['allocation_INPUT_valid']:blockers.append('missing_explicit_source_and_stage_INPUT')
        else:
            g=next(g for g in valid['groups'] if (g['port'],g['coherence_group'])==(port,group))
            reserved=deepcopy(g['reserves_L1'])
        if missing:blockers.append('incomplete_retained_reflected_point_stages')
        if failing:blockers.append('retained_point_stage_quota_FAIL')
        # Neither a point L1 fit nor a unit phase ledger proves SOURCE phase.
        blockers+=['source_phase_proof_absent','reduction_error_unproved','terminal_projection_error_unproved']
        out.append({'port':port,'coherence_group':group,'source_order':members,
            'common_terminal_reference_id':assignments[0]['common_terminal_reference_id'],
            'missing_point_sources':missing,'failed_point_sources':failing,
            'point_fit_sources':[s for s in members if rows[s]['partial_seven_stage_comparison_fits']],
            'source_phase_missing':deepcopy(members),'INPUT_reserves_L1':reserved,
            'executed_reduction_charge_L1':None,'executed_terminal_projection_charge_L1':None,
            'group_field_L1_bound':None,'group_field_uint64':None,'readiness':'STOP',
            'blockers':blockers,'scope':'explicit CPU grouping hypothesis, not authenticated native/physical coherence',
            **dict.fromkeys(FALSE,False)})
    require([s for g in out for s in g['source_order']] and
        sorted(s for g in out for s in g['source_order'])==sorted(ctx['source_order']),'every source belongs to exactly one group')
    return out

def audit_group_prerequisites_HOST(variant,*,model):
    require(model==MODEL,'explicit group prerequisites HOST model')
    require(type(variant) is str and variant in VARIANTS,'bounded retained variant')
    packets,data,plans,pins=load_retained();old,input_plans=select(data,plans,variant)
    require(old['model']==prior.MODEL and type(old['case_order']) is list and len(old['case_order'])==len(set(old['case_order']))==len(old['cases']) and set(old['case_order'])==set(old['cases']) and all(old[n] is False for n in FALSE),'same retained budget audit')
    checked={}
    # ALL complete INPUT/source cases before ANY group report.
    for name in old['case_order']:
        case=old['cases'][name]
        require(name in packets,'known retained case')
        checked[name]=validate_case(packets[name],case,input_plans.get(name))
    cases={n:{'context_sha256':digest(ctx),'retained_case_sha256':digest(old['cases'][n]),
        'allocation_INPUT_valid':valid['allocation_INPUT_valid'],'groups':group_report(old['cases'][n],ctx,valid),
        'status':'STOP',**dict.fromkeys(FALSE,False)} for n,(ctx,valid) in checked.items()}
    return {'model':MODEL,'variant':variant,'cases':cases,'inherited_pins_verified':len(pins),
        'ready_groups':0,'new_native_operations':0,'old_producers_suites_reexecuted':0,
        'cost_scope':'HOST prerequisite reporting ONLY; IO/pins/upstream/full pipeline costs unmeasured, NOT zero',
        **dict.fromkeys(FALSE,False)}
