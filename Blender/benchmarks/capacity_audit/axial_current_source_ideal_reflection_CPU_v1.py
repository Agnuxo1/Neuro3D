"""NEW CPU ideal -1 reflection of the current guarded source, never old-prefix substitution."""
import struct
from copy import deepcopy
from fractions import Fraction as F
import axial_source_material_admission_HOST_v1 as prior
io=prior.io
allocation=prior.allocation
require=prior.require
digest=prior.digest
guard=prior.bridge.guard
SIGN=1<<63
MODEL='axial-current-guarded-source-new-ideal-minus-one-reflection-CPU-point-v1'
FLAG='current_guarded_source_ideal_reflection_CPU_executed'
TRUE=('reflection_coefficient_applied','reflection_coefficient_executed_new')
FALSE=tuple(n for n in prior.FALSE if n not in TRUE)
PREVIOUS='coordinacion/respuestas/AXIAL-SOURCE-MATERIAL-ADMISSION-HOST-001-CODEX.json'
PREVIOUS_SHA='9b081c137e0ec009e4d8c34aaf6c64bdf56da9b7d9dd66e32c07cdf947d02825'

def load_retained():
    receipt=allocation.parse(io.read(PREVIOUS,PREVIOUS_SHA))
    require(receipt['task_id']=='AXIAL-SOURCE-MATERIAL-ADMISSION-HOST-001','parent task identity')
    pins=io.pins_from(receipt);pins[PREVIOUS]=PREVIOUS_SHA
    for p,h in pins.items():io.read(p,h)
    loaded=prior.load_retained()
    require(all(p in pins and pins[p]==h for p,h in loaded[1].items()),'same source material branches')
    audit=io.payload(receipt)['data']['audit']
    return loaded,audit,pins

def admit(row):
    require(row['source_profile_admitted_HOST_only'] is True and row['status']=='STOP','HOST source profile required')
    require(all(row[n] is False for n in prior.FALSE),'no inherited material/field promotion')
    require(row['material_executed'] is False and row['executed_material_charge_L1'] is None and row['executed_material_quota_fits'] is None,'material NOT previously executed')
    p=row['material_profile']
    require(p['profile_admitted_HOST_only'] is True and p['material_executed'] is False and
        p['native_material_ABI_implemented'] is False and p['zero_canonicalization_performed'] is False,'typed HOST-only material profile')
    require(type(p['mirror_phase_ORIGINAL_uint64']) is int and p['mirror_phase_ORIGINAL_uint64'] in (0,SIGN)
        and p['ideal_coefficient_exact_reim']==[[-1,1],[0,1]],'exact ORIGINAL zero-phase ideal coefficient')
    require(p['executed_material_charge_L1'] is None and p['executed_material_quota_fits'] is None,'unknown prior material charge')
    words=row['current_bare_source_uint64'];require(type(words) is list and len(words)==2,'two current source words')
    for w in words:guard.bits(w,64)
    charges={n:guard.rational(v) for n,v in row['fourteen_source_charges_L1'].items()}
    expected=set(n for ns in prior.bridge.MAPPING.values() for n in ns)
    require(set(charges)==expected and len(charges)==14 and all(v>=0 for v in charges.values()),'fourteen unchanged separate source charges')
    total=guard.rational(row['partial_bare_source_bound_L1'])
    require(sum(charges.values(),F(0))==total,'unchanged source bound conservation')
    require(p['source_id']==row['source_id'],'profile source identity')
    return {'source_id':row['source_id'],'input_uint64':deepcopy(words),
        'fourteen_source_charges_L1':deepcopy(row['fourteen_source_charges_L1']),
        'partial_bare_source_bound_L1':deepcopy(row['partial_bare_source_bound_L1']),
        'material_profile':deepcopy(p),'retained_material_admission_row_sha256':digest(row),
        'retained_source_row_sha256':row['retained_source_row_sha256'],
        'retained_root_row_sha256':row['retained_root_row_sha256'],
        'phase_reference_id':row['phase_reference_id'],'terminal_reference_id':row['terminal_reference_id']}

def native_negate(word):
    guard.bits(word,64) # bounded normal-or-zero; no subnormal FTZ
    value=struct.unpack('<d',struct.pack('<Q',word))[0]
    result=-value # actual CPU unary minus, not synthesized XOR output
    return struct.unpack('<Q',struct.pack('<d',result))[0]

def runtime_probe():
    words=[0,SIGN,0x3ff0000000000000,0xbff0000000000000]
    out=[native_negate(w) for w in words]
    return {'input_uint64':words,'output_uint64':out,'PASS':out==[w^SIGN for w in words],
        'new_probe_CPU_unary_negations':4,'zero_canonicalization_performed':False}

def execute(admission):
    nodes=[];out=[]
    for w in admission['input_uint64']:
        v=native_negate(w);require(type(v) is int and v==w^SIGN,'new unary-minus exact bit identity including signed zero')
        out.append(v);nodes.append({'operation':'CPU_unary_minus_binary64','input_uint64':w,
            'output_uint64':v,'exact_material_rounding_error_L1':[0,1]})
    charges={**deepcopy(admission['fourteen_source_charges_L1']),'ideal_material_L1':[0,1]}
    return {**deepcopy(admission),'reflected_uint64':out,'material_nodes':nodes,
        'fifteen_source_material_charges_L1':charges,
        'point_reflected_source_bound_to_FIXED_ORIGINAL_L1':deepcopy(admission['partial_bare_source_bound_L1']),
        'new_main_CPU_unary_negations':2,'executed_material_charge_L1':[0,1],
        'executed_material_quota_fits':None,'material_executed':True,
        'error_rule':'Exact unary minus is an L1 isometry toward the fixed ORIGINAL ideal reflected source; all fourteen upstream charges retained',
        'zero_canonicalization_performed':False,'source_phase_bound_proved':False,
        FLAG:True,**dict.fromkeys(TRUE,True),**dict.fromkeys(FALSE,False)}

def audit_reflection_CPU(case_names,*,model):
    require(model==MODEL,'explicit current-source ideal-reflection CPU model')
    require(type(case_names) is list and 1<=len(case_names)<=64 and all(type(n) is str and n for n in case_names)
        and len(set(case_names))==len(case_names),'bounded unique cases')
    loaded,old,pins=load_retained()
    require(set(case_names)<=set(old['cases']),'known cases')
    # Revalidate ONLY HOST evidence; no old numerical producer/stage/suite/ray trace.
    # All contexts/material/proofs and raw retained row bindings before ANY native probe/main.
    fresh=prior.audit_material_admission_HOST(case_names,model=prior.MODEL)
    plans={}
    for name in case_names:
        c=old['cases'][name]
        require(c==fresh['cases'][name],'same complete current material admission case')
        plans[name]=[]
        for row in c['sources']:
            require(type(row['source_profile_admitted_HOST_only']) is bool,'typed HOST eligibility')
            plans[name].append(admit(row) if row['source_profile_admitted_HOST_only'] else None)
    probe=runtime_probe();require(probe['PASS'] is True,'runtime probe FAIL before main material outputs')
    cases={};executed=stopped=0
    for name in case_names:
        rows=[]
        for row,a in zip(old['cases'][name]['sources'],plans[name]):
            v={'source_id':row['source_id'],'status':'STOP',FLAG:False,'material_executed':False,
                'executed_material_charge_L1':None,'executed_material_quota_fits':None,
                **dict.fromkeys(TRUE,False),**dict.fromkeys(FALSE,False)}
            if a is None:
                stopped+=1;v.update(reason=row['reason'],reason_provenance='unchanged retained upstream STOP')
            else:
                res=execute(a);executed+=1
                v.update(result=res,material_executed=True,executed_material_charge_L1=[0,1],
                    **{FLAG:True},**dict.fromkeys(TRUE,True),
                    reason='NEW CPU ideal reflection on current guarded source; missing real INPUT allocations, no reduction/power/readout/full field')
            rows.append(v)
        cases[name]={'context':deepcopy(old['cases'][name]['context']),'sources':rows,
            'status':'STOP',**dict.fromkeys(TRUE,False),**dict.fromkeys(FALSE,False)}
    return {'model':MODEL,'case_order':deepcopy(case_names),'cases':cases,'runtime_probe':probe,
        'inherited_pins_verified':len(pins),'new_ideal_reflected_sources':executed,'retained_sources_not_executed':stopped,
        'new_main_CPU_unary_negations':2*executed,'new_probe_CPU_unary_negations':4,
        'old_native_stages_suites_reexecuted':0,'new_source_geometry_argument_Horner_reduction_power_readout_operations':0,
        'allocation_policy_adopted':False,'material_input':'pinned ORIGINAL zero-phase HOST profile; NO native material ABI',
        'cost_scope':'main/probe negations counted separately; IO/pins/setup/HOST preflight/upstream/remaining costs UNMEASURED never zero',
        **dict.fromkeys(TRUE,False),**dict.fromkeys(FALSE,False)}
