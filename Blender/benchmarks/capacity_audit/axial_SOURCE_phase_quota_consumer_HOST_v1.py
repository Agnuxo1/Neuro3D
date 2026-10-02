"""Opt-in immutable SOURCE phase INPUT/certificate quota join; no group admission."""
from copy import deepcopy
import axial_SOURCE_phase_INPUT_HOST_v1 as schema
prior=schema.prior
phase,budget,groups=prior.phase,prior.budget,prior.groups
io,allocation,require,digest=schema.io,schema.allocation,schema.require,schema.digest
FALSE=schema.FALSE
MODEL='axial-current-SOURCE-principal-phase-quota-consumer-HOST-v1'
FLAG='point_SOURCE_phase_quota_compared_HOST'
PARENT='coordinacion/respuestas/AXIAL-SOURCE-PHASE-INPUT-HOST-001-CODEX.json'
PARENT_SHA='be9f748d4128174357284a1123d89c662c208392ba4d9dfa650f50fe580946f3'
VARIANTS=('real_missing','explicit_None_missing','synthetic_retained','phase_zero_FAIL','Horner_zero_FAIL','source_zero_FAIL')

def load_retained():
    r=allocation.parse(io.read(PARENT,PARENT_SHA))
    require(r['task_id']=='AXIAL-SOURCE-PHASE-INPUT-HOST-001','phase INPUT parent identity')
    pins=io.pins_from(r);pins[PARENT]=PARENT_SHA
    for p,h in pins.items():io.read(p,h)
    loaded,certificates,stage_data,oldpins=prior.load_retained()
    require(all(pins.get(p)==h for p,h in oldpins.items()),'same SOURCE proof branches')
    consumer=io.payload(allocation.parse(io.read(schema.PARENT,pins[schema.PARENT])))['data']
    inputs=io.payload(r)['data']
    return loaded,certificates,stage_data,consumer,inputs,pins

def select(retained,stage_data,inputs,variant):
    stage_variant='synthetic_partial' if variant in ('synthetic_retained','phase_zero_FAIL') else variant
    old,stage_plans=groups.select(stage_data,retained[-1],stage_variant)
    names=old['case_order']
    if variant=='real_missing':phase_plans={}
    elif variant=='explicit_None_missing':phase_plans={n:None for n in names}
    else:
        key='synthetic_zero_INPUT_plans' if variant=='phase_zero_FAIL' else 'synthetic_control_INPUT_plans'
        phase_plans={n:deepcopy(inputs[key][n]) for n in names}
    consumer_variant='synthetic_partial' if variant in ('synthetic_retained','phase_zero_FAIL') else variant
    return old,stage_plans,phase_plans,consumer_variant

def inspect_certificate(packet,ctx,index,cert,loaded):
    retained,reflection,material,_=loaded
    expected=phase.admit_phase(packet,ctx,index,reflection['cases'][ctx['case_name']]['sources'][index],
        material['cases'][ctx['case_name']]['sources'][index],retained)
    # Canonical hash equality is stricter than Python == (which treats bool as int).
    require(digest(cert)==digest(expected),'complete typed current SOURCE phase certificate')
    require(cert[phase.FLAG] is True and cert['proof']['phase_INPUT_quota_fits'] is None,'point certificate not prior INPUT approval')
    a=ctx['assignments'][index]
    require(cert['phase_reference_id']==a['source_phase_reference_id'] and
        cert['terminal_reference_id']==a['terminal_reference_id']==a['common_terminal_reference_id'],'same ORIGINAL gauges')
    allocation.rational(cert['proof']['point_principal_phase_distance_bound_rad'])
    return deepcopy(cert)

def compare_phase(cert,phase_plan):
    require(cert['source_id']==phase_plan['source_id'],'same SOURCE phase INPUT')
    bound=allocation.rational(cert['proof']['point_principal_phase_distance_bound_rad'])
    cap=allocation.rational(phase_plan['cap_rad'])
    return {'bound_rad':deepcopy(cert['proof']['point_principal_phase_distance_bound_rad']),
            'cap_rad':deepcopy(phase_plan['cap_rad']),'fits':bound<=cap,
            'comparison_scope':'point principal SOURCE phase only; not uniform or group'}

def summarize_groups(ctx,stage_valid,phase_valid,rows):
    indexed={r['source_id']:r for r in rows};out=[];seen=[]
    for port,gid in ctx['groups']:
        aa=[a for a in ctx['assignments'] if (a['port'],a['coherence_group'])==(port,gid)]
        ss=[a['source_id'] for a in aa];seen+=ss
        require(ss and all(a['terminal_reference_id']==a['common_terminal_reference_id']==aa[0]['common_terminal_reference_id'] for a in aa),'complete common terminal gauge')
        unavailable=[s for s in ss if indexed[s]['phase_INPUT_quota_fits'] is None]
        phase_fail=[s for s in ss if indexed[s]['phase_INPUT_quota_fits'] is False]
        stage_fail=[s for s in ss if indexed[s]['budget'] is not None and not indexed[s]['budget']['partial_seven_stage_comparison_fits']]
        blocks=[]
        if not stage_valid['allocation_INPUT_valid']:blocks.append('missing_seven_stage_INPUT')
        if not phase_valid['SOURCE_phase_INPUT_valid']:blocks.append('missing_SOURCE_phase_INPUT')
        if unavailable:blocks.append('incomplete_point_SOURCE_certificates_or_INPUT')
        if phase_fail:blocks.append('point_SOURCE_phase_quota_FAIL')
        if stage_fail:blocks.append('point_SOURCE_stage_quota_FAIL')
        blocks+=['uniform_SOURCE_enclosure_unproved','reduction_error_unproved','terminal_projection_error_unproved']
        reserves=None
        if stage_valid['allocation_INPUT_valid']:
            reserves=deepcopy(next(g['reserves_L1'] for g in stage_valid['groups'] if (g['port'],g['coherence_group'])==(port,gid)))
        out.append({'port':port,'coherence_group':gid,'source_order':ss,'common_terminal_reference_id':aa[0]['common_terminal_reference_id'],
            'SOURCE_phase_INPUT_complete':phase_valid['SOURCE_phase_INPUT_valid'],'unavailable_phase_comparison_sources':unavailable,
            'failed_phase_quota_sources':phase_fail,'failed_stage_quota_sources':stage_fail,'INPUT_reserves_L1':reserves,
            'group_phase_bound_rad':None,'group_field_bound_L1':None,'group_field_uint64':None,
            'executed_reduction_charge_L1':None,'executed_projection_charge_L1':None,'blockers':blocks,
            'status':'STOP',**dict.fromkeys(FALSE,False)})
    require(sorted(seen)==sorted(ctx['source_order']),'all group members once')
    return out

def audit_quota_consumer_HOST(variant,*,model):
    require(type(model) is str and model==MODEL and type(variant) is str and variant in VARIANTS,'explicit model/pinned variant')
    loaded,certificates,stage_data,consumers,inputs,pins=load_retained()
    retained=loaded[0];packets=retained[0]
    old,stage_plans,phase_plans,cv=select(retained,stage_data,inputs,variant)
    existing=consumers[cv]
    checked={}
    # ALL phase AND stage INPUTs, contexts and source orders BEFORE ANY certificate inspection.
    for name in old['case_order']:
        ctx,sv=groups.validate_case(packets[name],old['cases'][name],stage_plans.get(name))
        pc,pv=schema.validate_plan(packets[name],digest(packets[name]),phase_plans.get(name),model=schema.MODEL)
        cc=certificates['cases'][name];oc=existing['cases'][name]
        require(pc==ctx==cc['context']==oc['context'],'same complete ORIGINAL contexts')
        require(cc['status']==oc['status']=='STOP' and all(cc[k] is False and oc[k] is False for k in FALSE),'no retained group admission')
        for case in (cc,oc):
            require([s['source_id'] for s in case['sources']]==ctx['source_order'],'complete source evidence order')
        require(oc['allocation_INPUT_valid'] is sv['allocation_INPUT_valid'],'same retained stage INPUT validity')
        for cert,row in zip(cc['sources'],oc['sources']):
            require(type(cert[phase.FLAG]) is bool and type(row[prior.FLAG]) is bool,'strict certificate eligibility')
            require(row['phase_certificate_sha256']==digest(cert),'pinned stage consumer/certificate identity')
        checked[name]=(ctx,sv,pv)
    admitted={}
    # ALL requested eligible certificates BEFORE ANY phase quota comparison.
    for name,(ctx,sv,pv) in checked.items():
        if not (sv['allocation_INPUT_valid'] and pv['SOURCE_phase_INPUT_valid']):continue
        for i,cert in enumerate(certificates['cases'][name]['sources']):
            if cert[phase.FLAG]:
                admitted[name,i]=inspect_certificate(packets[name],ctx,i,cert,loaded)
                oldrow=existing['cases'][name]['sources'][i]
                require(oldrow[prior.FLAG] is True and oldrow['budget'] is not None,'current stage certificate consumed')
                require(oldrow['budget']['fifteen_charges_L1']==cert['fifteen_reflected_charges_L1'] and
                    oldrow['budget']['retained_reflection_row_sha256']==cert['retained_reflection_row_sha256'],'same fifteen-charge stage evidence')
    cases={};comparisons=fits=0
    for name,(ctx,sv,pv) in checked.items():
        rows=[]
        for i,sid in enumerate(ctx['source_order']):
            if (name,i) in admitted:
                cert=admitted[name,i];cmp=compare_phase(cert,pv['sources'][i]);comparisons+=1;fits+=int(cmp['fits'])
                row={'source_id':sid,FLAG:True,'phase_certificate_sha256':digest(cert),
                    'phase_comparison':cmp,'phase_INPUT_quota_fits':cmp['fits'],
                    'budget':deepcopy(existing['cases'][name]['sources'][i]['budget'])}
            else:
                row={'source_id':sid,FLAG:False,'phase_certificate_sha256':None,'phase_comparison':None,
                    'phase_INPUT_quota_fits':None,'budget':None,
                    'reason':'missing phase/stage INPUT or unavailable point SOURCE phase certificate'}
            row.update({'status':'STOP',**dict.fromkeys(FALSE,False)});rows.append(row)
        cases[name]={'context':ctx,'stage_INPUT_valid':sv['allocation_INPUT_valid'],'phase_INPUT':pv,
            'sources':rows,'groups':summarize_groups(ctx,sv,pv,rows),'status':'STOP',**dict.fromkeys(FALSE,False)}
    return {'model':MODEL,'variant':variant,'case_order':deepcopy(old['case_order']),'cases':cases,
        'inherited_pins_verified':len(pins),'point_phase_comparisons':comparisons,'point_phase_quota_fits':fits,
        'group_admissions':0,'SOURCE_phase_policy_adopted':False,'new_native_operations':0,'old_suites_producers_reexecuted':0,
        'cost_scope':'HOST retained INPUT/certificate/rational point comparisons only; IO/setup/upstream/rest UNMEASURED NOT zero',
        **dict.fromkeys(FALSE,False)}
