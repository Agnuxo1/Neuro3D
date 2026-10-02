"""Opt-in declarative HOST readout boundary; never a detector or execution admission."""
from copy import deepcopy
import axial_singleton_power_domain_HOST_v1 as power
import axial_source_budget_gate_HOST_v1 as io
import axial_amplitude_allocation_HOST_v1 as allocation
MODEL='axial-HOST-readout-retained-power-contract-v1'
PREVIOUS='coordinacion/respuestas/AXIAL-SINGLETON-POWER-DOMAIN-HOST-001-CODEX.json'
PREVIOUS_SHA='6fc6191ae3fed5ccaa52df1922df3c7947950b234d064f2c6ede1c39f6db96d2'
UNITS='ORIGINAL-source-field-amplitude-squared'
STAGES=('ORIGINAL_ingress','scene_transport','source_encoding','reflection','reduction',
        'power','readout','upload','execution','download','host_validation')
FALSE=power.FALSE+('readout_executed_new','readout_budget_accepted','physical_detector_calibrated',
                   'equal_work_comparison_admitted','complete_costs_measured')
require=io.require
digest=allocation.digest

def load_retained():
    r=allocation.parse(io.read(PREVIOUS,PREVIOUS_SHA))
    require(r['task_id']=='AXIAL-SINGLETON-POWER-DOMAIN-HOST-001','retained predecessor task identity')
    pins=io.pins_from(r);pins[PREVIOUS]=PREVIOUS_SHA
    for path,sha in pins.items():io.read(path,sha)
    data=io.payload(r)
    require(data['PASS'] is True,'successful captured predecessor, not scene admission')
    return data['data']['audit'],pins

def context_binding(ctx):
    keys=('input_packet_sha256','scene_binding_sha256','word_ABI_sha256',
          'original_snapshot_sha256','original_group_contract_sha256',
          'source_order','groups','assignments','unchanged_limits','unchanged_field_L1_cap')
    return {k:deepcopy(ctx[k]) for k in keys}

def make_proposed_contract(audit):
    """Return an explicitly SYNTHETIC proposal, not an existing scene INPUT receipt."""
    outputs=[]
    for n in audit['case_order']:
        c=audit['cases'][n];ctx=c['context']
        require([[g['port'],g['coherence_group']] for g in c['groups']]==ctx['groups'],'complete retained group partition')
        for gi,g in enumerate(c['groups']):
            assignments=[a for a in ctx['assignments']
                         if [a['port'],a['coherence_group']]==[g['port'],g['coherence_group']]]
            require([a['source_id'] for a in assignments]==g['source_order'],'complete source order without partial sum')
            outputs.append({'case_name':n,'group_index':gi,'port':g['port'],
                'coherence_group':g['coherence_group'],'complete_source_order':deepcopy(g['source_order']),
                'input_binding':context_binding(ctx),'retained_power_row_sha256':digest(g),
                'references':deepcopy(assignments),
                'observable':'HOST_squared_modulus_of_complete_coherent_group',
                'units':UNITS,'group_combination':'none; separate outputs, no detector integration',
                'readout_operation':'identity_uint64_receipt; no new rounding',
                'calibration':None,'area_integration':None,'exposure':None,'gain':None,
                'offset':None,'quantization':None,'budget_allocation_INPUT':None})
    return {'model':MODEL,'provenance':'SYNTHETIC proposed INPUT; absent from retained scene',
            'retained_power_report':{'path':PREVIOUS,'sha256':PREVIOUS_SHA},
            'case_order':deepcopy(audit['case_order']),'outputs':outputs,
            'cost_ledger':[{'stage':s,'status':'UNMEASURED','seconds':None,'bytes':None} for s in STAGES],
            'comparison_contract':{'status':'STOP','same_work_and_outputs_authenticated':False,
                                   'guard_and_exclusive_job_receipt':None},
            **dict.fromkeys(FALSE,False)}

def validate_contract(plan,*,model):
    """Accept only this declarative boundary; return STOP for every execution/scientific gate."""
    require(model==MODEL,'explicit HOST readout model')
    require(type(plan) is dict,'contract object required')
    audit,pins=load_retained();expected=make_proposed_contract(audit)
    # Strict schema and typed canonical equality: bool cannot masquerade as index 0 or vice versa.
    require(set(plan)==set(expected),'exact contract keys')
    require(type(plan['outputs']) is list and len(plan['outputs'])==len(expected['outputs']),
            'complete output partition, no dropped/duplicated/merged groups')
    require(type(plan['case_order']) is list and plan['case_order']==expected['case_order'],'complete case order')
    for i,(actual,wanted) in enumerate(zip(plan['outputs'],expected['outputs'])):
        require(type(actual) is dict and set(actual)==set(wanted),'exact output contract keys')
        require(type(actual['group_index']) is int,'group index is integer, not bool')
        require(digest(actual)==digest(wanted),'output identity/references/units/operations/budgets must match proposed HOST boundary')
    require(digest(plan)==digest(expected),'contract provenance, costs, safety or admission changed')
    rows=[];available=blocked=0
    for out in plan['outputs']:
        g=audit['cases'][out['case_name']]['groups'][out['group_index']]
        proved=g[power.FLAG] is True
        words=None
        if proved:
            checks=g['proof']['retained_corner_checks']
            words=[q['retained_power_uint64'] for q in checks]
            require(len(words)==4 and len(set(words))==1,'constant retained power receipt')
            available+=1
        else:blocked+=1
        rows.append({'case_name':out['case_name'],'group_index':out['group_index'],
                     'output_contract_sha256':digest(out),'retained_power_row_sha256':digest(g),
                     'restricted_power_proof_available':proved,
                     'retained_power_uint64_decimal':str(words[0]) if words else None,
                     'readout_status':'STOP','budget_allocation_INPUT_present':False,
                     'reason':'missing source/reduction/power/readout INPUT allocations and executed readout receipt'
                              if proved else g['reason'],
                     **dict.fromkeys(FALSE,False)})
    return {'model':MODEL,'contract_schema_valid':True,'contract_sha256':digest(plan),
            'contract_provenance':plan['provenance'],'outputs':rows,
            'restricted_power_receipts_available':available,'upstream_unproved_groups':blocked,
            'all_readouts_stopped':len(rows),'inherited_pins_verified':len(pins),
            'retained_unit_STOPs':audit['retained_unit_STOPs'],
            'nonzero_domains_not_refined':audit['nonzero_domains_not_refined'],
            'retained_zero_budget_FAIL_controls':deepcopy(audit['retained_zero_budget_FAIL_controls']),
            'unmeasured_cost_stages':list(STAGES),'new_RN_or_scene_producer_executions':0,
            **dict.fromkeys(FALSE,False)}
