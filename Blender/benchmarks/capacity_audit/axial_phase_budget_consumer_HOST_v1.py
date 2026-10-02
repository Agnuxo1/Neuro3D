"""Opt-in HOST joins current SOURCE phase proof to unchanged retained INPUT quotas."""
from copy import deepcopy
import axial_reflected_source_phase_HOST_v1 as phase
import axial_group_prerequisites_HOST_v1 as groups
budget=phase.prior
io,allocation,quotas=phase.io,phase.allocation,budget.quotas
require,digest=phase.require,phase.digest
FALSE=phase.FALSE
MODEL='axial-current-SOURCE-phase-retained-seven-quota-consumer-HOST-v1'
FLAG='point_SOURCE_phase_certificate_consumed_HOST'
PARENT='coordinacion/respuestas/AXIAL-REFLECTED-SOURCE-PHASE-HOST-001-CODEX.json'
PARENT_SHA='07ba59c6be5378d6692ef1dad39866a3fd3a0e94353994080fe32421e8032df5'
BUDGET='coordinacion/respuestas/AXIAL-REFLECTED-SOURCE-BUDGET-BRIDGE-HOST-001-CODEX.json'

def load_retained():
    r=allocation.parse(io.read(PARENT,PARENT_SHA))
    require(r['task_id']=='AXIAL-REFLECTED-SOURCE-PHASE-HOST-001','current SOURCE phase parent task')
    pins=io.pins_from(r);pins[PARENT]=PARENT_SHA
    for p,h in pins.items():io.read(p,h)
    loaded,oldpins=phase.load_retained()
    require(all(pins.get(p)==h for p,h in oldpins.items()),'same current phase proof branches')
    br=allocation.parse(io.read(BUDGET,pins[BUDGET]))
    return loaded,io.payload(r)['data']['audit'],io.payload(br)['data'],pins

def inspect_certificate(packet,ctx,index,cert,loaded):
    retained,reflection,material,_=loaded
    expected=phase.admit_phase(packet,ctx,index,reflection['cases'][ctx['case_name']]['sources'][index],
        material['cases'][ctx['case_name']]['sources'][index],retained)
    require(cert==expected,'complete current SOURCE phase certificate binding')
    require(cert[phase.FLAG] is True and cert['proof']['phase_INPUT_quota_fits'] is None,'point proof, no phase INPUT quota')
    return {'source_id':cert['source_id'],'retained_reflection_row_sha256':cert['retained_reflection_row_sha256'],
        'fifteen_charges_L1':deepcopy(cert['fifteen_reflected_charges_L1']),
        'point_reflected_source_bound_L1':deepcopy(cert['proof']['point_reflected_error_L1']),
        'retained_reflection_executed_CPU':True,'new_material_operations':0}

def group_summary(ctx,valid,rows):
    indexed={r['source_id']:r for r in rows};out=[]
    for port,gid in ctx['groups']:
        aa=[a for a in ctx['assignments'] if (a['port'],a['coherence_group'])==(port,gid)]
        members=[a['source_id'] for a in aa]
        require(members and all(a['terminal_reference_id']==a['common_terminal_reference_id']==aa[0]['common_terminal_reference_id'] for a in aa),'same complete group gauge')
        available=[s for s in members if indexed[s][FLAG]]
        missing=[s for s in members if not indexed[s][FLAG]]
        failing=[s for s in members if indexed[s][FLAG] and not indexed[s]['budget']['partial_seven_stage_comparison_fits']]
        reserves=None;blocked=[]
        if not valid['allocation_INPUT_valid']:blocked.append('missing_source_stage_INPUT')
        else:reserves=deepcopy(next(g['reserves_L1'] for g in valid['groups'] if (g['port'],g['coherence_group'])==(port,gid)))
        if missing:blocked.append('incomplete_source_phase_and_point_stages')
        if failing:blocked.append('source_point_stage_quota_FAIL')
        blocked+=['missing_explicit_SOURCE_phase_INPUT','reduction_error_unproved','terminal_projection_error_unproved']
        out.append({'port':port,'coherence_group':gid,'source_order':members,
            'common_terminal_reference_id':aa[0]['common_terminal_reference_id'],
            'phase_certificate_sources':available,'missing_source_certificates':missing,'failed_point_source_quotas':failing,
            'INPUT_reserves_L1':reserves,'phase_INPUT_quota_fits':None,
            'group_phase_bound_rad':None,'group_field_bound_L1':None,'group_field_uint64':None,
            'executed_reduction_charge_L1':None,'executed_projection_charge_L1':None,
            'blockers':blocked,'status':'STOP',**dict.fromkeys(FALSE,False)})
    require(sorted(s for g in out for s in g['source_order'])==sorted(ctx['source_order']),'no partial group/duplicate source')
    return out

def audit_phase_budget_consumer_HOST(variant,*,model):
    require(model==MODEL and type(variant) is str and variant in groups.VARIANTS,'explicit retained variant/model')
    loaded,certificates,data,pins=load_retained();retained,reflection,material,_=loaded
    old,plans=groups.select(data,retained[-1],variant);packets=retained[0]
    checked={}
    # ALL INPUT cases validated BEFORE ANY certificate inspection.
    for name in old['case_order']:
        c=old['cases'][name];ctx,valid=groups.validate_case(packets[name],c,plans.get(name))
        pc=certificates['cases'][name]
        require(pc['context']==ctx and [r['source_id'] for r in pc['sources']]==ctx['source_order'] and
            pc['status']=='STOP' and all(pc[n] is False for n in FALSE),'complete same phase SOURCE context')
        checked[name]=(ctx,valid)
    evidence={}
    # ALL requested eligible certificates BEFORE ANY numerical budget comparison.
    for name,(ctx,valid) in checked.items():
        if not valid['allocation_INPUT_valid']:continue
        for i,cert in enumerate(certificates['cases'][name]['sources']):
            require(type(cert[phase.FLAG]) is bool,'typed phase certificate eligibility')
            if cert[phase.FLAG]:
                evidence[name,i]=inspect_certificate(packets[name],ctx,i,cert,loaded)
    cases={};count=fits=0
    for name,(ctx,valid) in checked.items():
        rows=[]
        for i,cert in enumerate(certificates['cases'][name]['sources']):
            if (name,i) in evidence:
                b=budget.compare_source(evidence[name,i],valid['sources'][i]);count+=1;fits+=int(b['partial_seven_stage_comparison_fits'])
                row={'source_id':cert['source_id'],'phase_certificate_sha256':digest(cert),FLAG:True,
                    'point_principal_phase_bound_rad':deepcopy(cert['proof']['point_principal_phase_distance_bound_rad']),
                    'budget':b,'phase_INPUT_quota_fits':None,'status':'STOP',**dict.fromkeys(FALSE,False)}
            else:
                row={'source_id':cert['source_id'],'phase_certificate_sha256':digest(cert),FLAG:False,
                    'point_principal_phase_bound_rad':None,'budget':None,'phase_INPUT_quota_fits':None,
                    'reason':'missing source INPUT or no current point SOURCE phase certificate','status':'STOP',**dict.fromkeys(FALSE,False)}
            rows.append(row)
        cases[name]={'context':ctx,'allocation_INPUT_valid':valid['allocation_INPUT_valid'],'sources':rows,
            'groups':group_summary(ctx,valid,rows),'status':'STOP',**dict.fromkeys(FALSE,False)}
    return {'model':MODEL,'variant':variant,'cases':cases,'inherited_pins_verified':len(pins),
        'certificates_consumed':count,'partial_seven_stage_fits':fits,'group_admissions':0,
        'new_native_operations':0,'old_suites_producers_reexecuted':0,'phase_INPUT_policy_adopted':False,
        'cost_scope':'HOST INPUT/proof/partial comparison only; IO/pins/setup/upstream/rest UNMEASURED NOT zero',
        **dict.fromkeys(FALSE,False)}
