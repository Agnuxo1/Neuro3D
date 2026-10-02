"""Opt-in HOST seven-quota bridge for the NEW current-source material ledger."""
from copy import deepcopy
from fractions import Fraction as F
import axial_current_source_ideal_reflection_CPU_v1 as prior
material=prior.prior
bridge=material.bridge
quotas=bridge.quotas
io=prior.io
allocation=prior.allocation
require=prior.require
digest=prior.digest
guard=prior.guard
pair=bridge.pair
FALSE=material.FALSE
MODEL='axial-current-reflected-source-fifteen-to-seven-stage-L1-HOST-v1'
PREVIOUS='coordinacion/respuestas/AXIAL-CURRENT-SOURCE-IDEAL-REFLECTION-CPU-001-CODEX.json'
PREVIOUS_SHA='474304cf3366616beb1f725e2e3e1e8bbf8735bf34f8d5b55bd11ddbd4f2965d'
MAPPING={**bridge.MAPPING,'ideal_material_L1':('ideal_material_L1',)}

def load_retained():
    r=allocation.parse(io.read(PREVIOUS,PREVIOUS_SHA))
    require(r['task_id']=='AXIAL-CURRENT-SOURCE-IDEAL-REFLECTION-CPU-001','current reflection task identity')
    pins=io.pins_from(r);pins[PREVIOUS]=PREVIOUS_SHA
    for p,h in pins.items():io.read(p,h)
    loaded,mat,p=prior.load_retained()
    require(all(k in pins and pins[k]==h for k,h in p.items()),'same current reflection branches')
    retained=loaded[0];old=io.payload(r)['data']['audit']
    require(set(old['cases'])==set(mat['cases'])==set(retained[0]),'complete current cases')
    return retained,old,mat,pins

def admit_reflection(packet,ctx,index,row,matrow,retained):
    sid=ctx['source_order'][index]
    require(row['source_id']==sid and row[prior.FLAG] is True and row['material_executed'] is True,'same executed reflection source')
    require(row['status']=='STOP' and all(row[n] is False for n in prior.FALSE) and all(row[n] is True for n in prior.TRUE),'same reflection scope')
    snap,meta=material.original.snapshot_from_packet(packet,ctx)
    root=retained[5]['cases'][ctx['case_name']]['sources'][index]
    rr=root['result']
    profile=material.material_profile(snap,meta,sid,rr['fixed_ORIGINAL_reference'],rr['new_decoded_Xroot_result']['fixed_ORIGINAL_reference'])
    def old(k):return retained[k]['cases'][ctx['case_name']]['sources'][index]
    expected_mat=material.admit_current_source(packet,ctx,index,old(1),old(2),old(3),old(4),root,retained[6],profile)
    require(matrow==expected_mat,'current material admission binding')
    a=prior.admit(expected_mat);v=row['result']
    require(v['material_executed'] is True and v[prior.FLAG] is True and v['zero_canonicalization_performed'] is False and v['source_phase_bound_proved'] is False,'typed reflected scope')
    require(all(v[n] is False for n in prior.FALSE) and all(v[n] is True for n in prior.TRUE),'no reflected-source promotion')
    require(type(v['new_main_CPU_unary_negations']) is int and v['new_main_CPU_unary_negations']==2,'typed retained node count')
    out=v['reflected_uint64'];nodes=v['material_nodes']
    require(type(out) is list and len(out)==2 and type(nodes) is list and len(nodes)==2,'two retained reflection nodes')
    expected_nodes=[]
    for w,o,n in zip(a['input_uint64'],out,nodes):
        x,y=guard.bits(w,64),guard.bits(o,64)
        require(o==w^prior.SIGN and y==-x,'retained unary-minus exact sign and rational value')
        require(guard.rational(n['exact_material_rounding_error_L1'])==0,'typed canonical executed material node zero')
        expected_nodes.append({'operation':'CPU_unary_minus_binary64','input_uint64':w,'output_uint64':o,'exact_material_rounding_error_L1':[0,1]})
    detail={**deepcopy(a['fourteen_source_charges_L1']),'ideal_material_L1':[0,1]}
    require(set(v['fifteen_source_material_charges_L1'])==set(detail) and
        all(guard.rational(v['fifteen_source_material_charges_L1'][k])==guard.rational(t) for k,t in detail.items()),'all fifteen charges exact and typed')
    require(guard.rational(v['executed_material_charge_L1'])==guard.rational(row['executed_material_charge_L1'])==0,'executed material exact zero, not default')
    require(guard.rational(v['point_reflected_source_bound_to_FIXED_ORIGINAL_L1'])==guard.rational(a['partial_bare_source_bound_L1']),'unchanged reflected point bound')
    expected={**deepcopy(a),'reflected_uint64':deepcopy(out),'material_nodes':expected_nodes,
        'fifteen_source_material_charges_L1':detail,
        'point_reflected_source_bound_to_FIXED_ORIGINAL_L1':deepcopy(a['partial_bare_source_bound_L1']),
        'new_main_CPU_unary_negations':2,'executed_material_charge_L1':[0,1],
        'executed_material_quota_fits':None,'material_executed':True,
        'error_rule':'Exact unary minus is an L1 isometry toward the fixed ORIGINAL ideal reflected source; all fourteen upstream charges retained',
        'zero_canonicalization_performed':False,'source_phase_bound_proved':False,
        prior.FLAG:True,**dict.fromkeys(prior.TRUE,True),**dict.fromkeys(prior.FALSE,False)}
    require(v==expected and row['executed_material_quota_fits'] is None,'complete retained reflection ledger; no quota invention')
    return {'source_id':sid,'retained_reflection_row_sha256':digest(row),'fifteen_charges_L1':detail,
        'point_reflected_source_bound_L1':deepcopy(a['partial_bare_source_bound_L1']),
        'retained_reflection_executed_CPU':True,'new_material_operations':0}

def map_charges(evidence):
    detailed={k:guard.rational(v) for k,v in evidence['fifteen_charges_L1'].items()}
    names=[n for ns in MAPPING.values() for n in ns]
    require(len(names)==len(set(names))==15 and set(names)==set(detailed) and all(v>=0 for v in detailed.values()),'fifteen charges mapped ONCE')
    totals={k:sum((detailed[n] for n in ns),F(0)) for k,ns in MAPPING.items()}
    require(sum(totals.values(),F(0))==sum(detailed.values(),F(0))==guard.rational(evidence['point_reflected_source_bound_L1']),'seven-stage exact conservation')
    return {k:pair(v) for k,v in totals.items()}

def compare_source(evidence,plan):
    require(evidence['source_id']==plan['source_id'],'same source plan')
    mapped=map_charges(evidence);require(set(mapped)==set(quotas.STAGES),'all seven frozen stage quotas')
    comps={k:{'charge_L1':v,'quota_L1':deepcopy(plan['stages_L1'][k]),'fits':guard.rational(v)<=allocation.rational(plan['stages_L1'][k])} for k,v in mapped.items()}
    total=guard.rational(evidence['point_reflected_source_bound_L1']);fit=total<=allocation.rational(plan['cap_L1'])
    return {'source_id':evidence['source_id'],'retained_reflection_row_sha256':evidence['retained_reflection_row_sha256'],
        'fifteen_charges_L1':deepcopy(evidence['fifteen_charges_L1']),'seven_stage_charges_L1':mapped,'stage_comparisons':comps,
        'point_reflected_source_bound_L1':pair(total),'source_cap_L1':deepcopy(plan['cap_L1']),
        'partial_total_fits_source_cap':fit,'partial_seven_stage_comparison_fits':fit and all(v['fits'] for v in comps.values()),
        'retained_reflection_executed_CPU':True,'new_material_operations':0,
        'reason':'seven retained point-stage comparisons ONLY; no source phase/group/reduction/projection/power/readout/fullfield admission',
        **dict.fromkeys(FALSE,False)}

def audit_reflected_budget_HOST(case_names,plans_by_case,*,model):
    require(model==MODEL,'explicit reflected-source budget HOST model')
    require(type(case_names) is list and 1<=len(case_names)<=64 and all(type(n) is str and n for n in case_names) and len(set(case_names))==len(case_names),'bounded unique cases')
    require(type(plans_by_case) is dict and set(plans_by_case)<=set(case_names),'selected static INPUT plans only')
    retained,old,mat,pins=load_retained();packets=retained[0]
    require(set(case_names)<=set(packets),'known cases')
    admitted={}
    # ALL INPUT plans BEFORE ANY retained numerical/material proof inspection.
    for name in case_names:
        ctx,plan=quotas.validate_plan(packets[name],digest(packets[name]),plans_by_case.get(name),model=quotas.MODEL)
        require(ctx==old['cases'][name]['context']==mat['cases'][name]['context'],'same complete INPUT context')
        for c in (old['cases'][name],mat['cases'][name]):
            require([r['source_id'] for r in c['sources']]==ctx['source_order'] and all(c[n] is False for n in FALSE),'complete order/no group promotion')
        admitted[name]=(ctx,plan)
    evidence={}
    # ALL available proofs BEFORE ANY budget comparison: no partial comparison output.
    for name,(ctx,plan) in admitted.items():
        ev={}
        if plan['allocation_INPUT_valid']:
            for i,row in enumerate(old['cases'][name]['sources']):
                require(type(row[prior.FLAG]) is bool,'typed reflection eligibility')
                if row[prior.FLAG]:ev[i]=admit_reflection(packets[name],ctx,i,row,mat['cases'][name]['sources'][i],retained)
        evidence[name]=ev
    cases={};valid=missing=count=fits=0
    for name,(ctx,plan) in admitted.items():
        valid+=int(plan['allocation_INPUT_valid']);missing+=int(not plan['allocation_INPUT_valid']);rows=[]
        for i,row in enumerate(old['cases'][name]['sources']):
            if i in evidence[name]:
                v=compare_source(evidence[name][i],plan['sources'][i]);count+=1;fits+=int(v['partial_seven_stage_comparison_fits'])
            else:
                v={'source_id':row['source_id'],'partial_seven_stage_comparison_fits':False,'stage_comparisons':None,
                    'retained_reflection_row_sha256':digest(row),'reason':plan['reason'] if not plan['allocation_INPUT_valid'] else row['reason'],
                    **dict.fromkeys(FALSE,False)}
            rows.append(v)
        cases[name]={'context':ctx,'allocation_INPUT':plan,'sources':rows,'status':'STOP',**dict.fromkeys(FALSE,False)}
    return {'model':MODEL,'case_order':deepcopy(case_names),'cases':cases,'charge_mapping':deepcopy(MAPPING),
        'inherited_pins_verified':len(pins),'explicit_INPUT_plans_valid':valid,'missing_INPUT_plans_STOP':missing,
        'partial_source_comparisons':count,'partial_seven_stage_comparisons_fit':fits,
        'new_native_operations':0,'old_native_stages_suites_reexecuted':0,'allocation_policy_adopted':False,
        'cost_scope':'HOST retained proof/INPUT comparison only; IO/pins/setup/upstream/remaining costs UNMEASURED NOT zero',
        **dict.fromkeys(FALSE,False)}
