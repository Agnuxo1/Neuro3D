"""Opt-in HOST disk-to-principal-phase bound for actual retained reflected SOURCE."""
import struct
from copy import deepcopy
from fractions import Fraction as F
import axial_reflected_source_budget_bridge_HOST_v1 as prior
io,allocation,original,guard=prior.io,prior.allocation,prior.material.original,prior.guard
require,digest,pair=prior.require,prior.digest,prior.pair
FALSE=prior.FALSE
MODEL='axial-current-reflected-source-disk-principal-phase-HOST-v1'
FLAG='point_reflected_source_phase_bound_HOST_proved'
PARENT='coordinacion/respuestas/AXIAL-GROUP-PREREQUISITES-HOST-001-CODEX.json'
PARENT_SHA='82f01820c150602bab94f03f0611424a14f87849c2b4c1938393665223bb86a2'

def load_retained():
    r=allocation.parse(io.read(PARENT,PARENT_SHA))
    require(r['task_id']=='AXIAL-GROUP-PREREQUISITES-HOST-001','parent task identity')
    pins=io.pins_from(r);pins[PARENT]=PARENT_SHA
    for p,h in pins.items():io.read(p,h)
    loaded=prior.load_retained()
    require(all(pins.get(p)==h for p,h in loaded[-1].items()),'same current source proof branches')
    return loaded,pins

def disk_phase_bound_HOST(original_words,reflected_words,error_L1):
    require(type(original_words) is list and len(original_words)==2 and
        type(reflected_words) is list and len(reflected_words)==2,'two ORIGINAL/reflected components')
    a=[guard.bits(w,64) for w in original_words]
    z=[guard.bits(w,64) for w in reflected_words]
    eps=guard.rational(error_L1)
    lo=max(map(abs,a));require(eps>=0 and lo>0 and eps<lo,'positive ORIGINAL amplitude and strict error disk away from zero')
    require(any(z),'retained reflected output cannot be zero inside this disk')
    gap=lo-eps;phase=eps/gap
    return {'ORIGINAL_source_uint64':deepcopy(original_words),'reflected_source_uint64':deepcopy(reflected_words),
        'ORIGINAL_amplitude_lower_bound':pair(lo),'point_reflected_error_L1':pair(eps),
        'positive_radial_projection_lower_bound':pair(gap),'point_principal_phase_distance_bound_rad':pair(phase),
        'bound_rule':'Euclidean error <= L1 epsilon; fixed ideal reference magnitude R>=max(abs(Are),abs(Aim))=m; positive radial projection >=m-epsilon; abs(principal phase distance)<=atan(epsilon/(m-epsilon))<=epsilon/(m-epsilon)',
        'fixed_reference_modulus_model':'ORIGINAL A times exact unit exp(i ORIGINAL path phase) times fixed ideal -1',
        'units':'radians for principal phase distance; ORIGINAL-source-field-amplitude for m/epsilon',
        'unwrapped_phase_proved':False,'native_atan_or_arg_executed':False,
        'phase_INPUT_quota_fits':None,'zero_canonicalization_performed':False}

def admit_phase(packet,ctx,index,row,matrow,retained):
    ev=prior.admit_reflection(packet,ctx,index,row,matrow,retained)
    snap,meta=original.snapshot_from_packet(packet,ctx);sid=ctx['source_order'][index]
    field=snap['sources'][index]['field_reim']
    require(type(field) is list and len(field)==2 and all(type(x) is float for x in field),'binary64 ORIGINAL field')
    words=[struct.unpack('<Q',struct.pack('<d',x))[0] for x in field]
    bare=retained[1]['cases'][ctx['case_name']]['sources'][index]
    require(words==bare['result']['source_encoder']['ORIGINAL_source_uint64'],'same SOURCE/ORIGINAL amplitude words')
    out=row['result']['reflected_uint64']
    proof=disk_phase_bound_HOST(words,out,ev['point_reflected_source_bound_L1'])
    assign=ctx['assignments'][index]
    require(row['result']['phase_reference_id']==assign['source_phase_reference_id'] and
        row['result']['terminal_reference_id']==assign['terminal_reference_id']==assign['common_terminal_reference_id'],'same fixed source and terminal gauges')
    return {'source_id':sid,'retained_reflection_row_sha256':digest(row),
        'retained_bare_source_row_sha256':digest(bare),'retained_material_admission_row_sha256':digest(matrow),
        'context_sha256':digest(ctx),'original_snapshot_sha256':ctx['original_snapshot_sha256'],
        'phase_reference_id':assign['source_phase_reference_id'],'terminal_reference_id':assign['terminal_reference_id'],
        'fifteen_reflected_charges_L1':deepcopy(ev['fifteen_charges_L1']),'proof':proof,FLAG:True,
        'reason':'HOST point principal SOURCE phase certificate ONLY; no INPUT phase allocation, uniform enclosure/group/reduction/readout admission',
        'status':'STOP',**dict.fromkeys(FALSE,False)}

def audit_source_phase_HOST(case_names,*,model):
    require(model==MODEL,'explicit SOURCE phase HOST model')
    require(type(case_names) is list and 1<=len(case_names)<=64 and
        all(type(n) is str and n for n in case_names) and len(set(case_names))==len(case_names),'bounded unique cases')
    (retained,old,mat,_),pins=load_retained();packets=retained[0]
    require(set(case_names)<=set(packets),'known cases')
    contexts={}
    # ALL ORIGINAL contexts and complete source orders before ANY phase proof.
    for name in case_names:
        ctx=allocation.context_from_packet(packets[name],digest(packets[name]),model=allocation.MODEL)
        require(ctx==old['cases'][name]['context']==mat['cases'][name]['context'],'same ORIGINAL context')
        for c in (old['cases'][name],mat['cases'][name]):
            require([r['source_id'] for r in c['sources']]==ctx['source_order'] and all(c[n] is False for n in FALSE),'complete ordered sources and no group promotion')
        contexts[name]=ctx
    admitted={}
    # All selected eligible SOURCE proofs before any returned certificate.
    for name,ctx in contexts.items():
        for i,row in enumerate(old['cases'][name]['sources']):
            require(type(row[prior.prior.FLAG]) is bool,'typed retained executed eligibility')
            if row[prior.prior.FLAG]:
                admitted[name,i]=admit_phase(packets[name],ctx,i,row,mat['cases'][name]['sources'][i],retained)
    cases={}
    for name,ctx in contexts.items():
        rows=[]
        for i,row in enumerate(old['cases'][name]['sources']):
            rows.append(admitted[name,i] if (name,i) in admitted else
                {'source_id':row['source_id'],'retained_reflection_row_sha256':digest(row),FLAG:False,
                 'proof':None,'status':'STOP','reason':row['reason'],**dict.fromkeys(FALSE,False)})
        cases[name]={'context':deepcopy(ctx),'sources':rows,'status':'STOP',**dict.fromkeys(FALSE,False)}
    return {'model':MODEL,'case_order':deepcopy(case_names),'cases':cases,'inherited_pins_verified':len(pins),
        'point_source_phase_certificates':len(admitted),'retained_sources_STOP':sum(len(c['sources']) for c in cases.values())-len(admitted),
        'new_native_operations':0,'old_producers_suites_reexecuted':0,'new_group_admission':False,
        'phase_INPUT_policy_adopted':False,'cost_scope':'HOST rational point certificate; IO/pins/upstream/rest unmeasured NOT zero',
        **dict.fromkeys(FALSE,False)}
