"""Opt-in HOST ideal-material profile bound to the current guarded SOURCE proof."""
import base64,struct
from copy import deepcopy
import axial_guarded_source_budget_bridge_HOST_v1 as bridge
io=bridge.io
allocation=bridge.allocation
original=bridge.original
require=bridge.require
digest=bridge.digest
FALSE=bridge.FALSE
MODEL='axial-current-guarded-source-owner-hit-zero-phase-material-admission-HOST-v1'
PREVIOUS='coordinacion/respuestas/AXIAL-GUARDED-SOURCE-BUDGET-BRIDGE-HOST-001-CODEX.json'
PREVIOUS_SHA='a68927d3657469345fb330a81653483d2d15d433d1df8d1a88a9660257a88794'
SIGN=1<<63

def load_retained():
    r=allocation.parse(io.read(PREVIOUS,PREVIOUS_SHA))
    require(r['task_id']=='AXIAL-GUARDED-SOURCE-BUDGET-BRIDGE-HOST-001','parent task identity')
    pins=io.pins_from(r);pins[PREVIOUS]=PREVIOUS_SHA
    for p,h in pins.items():io.read(p,h)
    retained=bridge.load_retained()
    require(all(p in pins and pins[p]==h for p,h in retained[-2].items()),'same guarded-source branches')
    return retained,pins

def material_profile(snapshot,metadata,source_id,fixed,decoded):
    """Only HOST conditional mathematical coefficient, NEVER an executed material charge."""
    require(type(source_id) is str and source_id in metadata['source_order'],'declared source')
    require(set(snapshot['objects'])=={'M','D'} and snapshot['undeclared_meshes']==[],'declared M/D only')
    require(metadata['object_ids']==['M','D'] and metadata['kinds']==['mirror','det'],'ordered owner map')
    owners=[];pid=0
    for owner,name,kind in ((0,'M','mirror'),(1,'D','det')):
        obj=snapshot['objects'][name];require(obj['kind']==kind,'same ORIGINAL owner kind')
        vertices=obj['vertices_world_BU'];faces=obj['faces']
        require(type(vertices) is list and 3<=len(vertices)<=192,'bounded vertices')
        require(all(type(v) is list and len(v)==3 and all(type(a) is float for a in v) for v in vertices),'binary64 vertex layout')
        require(type(faces) is list and 1<=len(faces)<=64,'bounded faces')
        for face in faces:
            require(type(face) is list and len(face)==3 and len(set(face))==3 and
                all(type(i) is int and 0<=i<len(vertices) for i in face),'typed triangular topology')
            owners.append({'primitive_id':pid,'owner':owner,'object_id':name,'kind':kind,'face':deepcopy(face)})
            pid+=1
    require(pid<=64,'bounded total primitive map')
    phase=snapshot['objects']['M']['phase_rad']
    require(type(phase) is float,'binary64 ORIGINAL material phase')
    phase_word=struct.unpack('<Q',struct.pack('<d',phase))[0]
    require(phase_word in (0,SIGN),'exact ORIGINAL +/-0 only; nonzero/subnormal/nonfinite phase STOP, no FTZ')
    hit_chains=[]
    for trace in (fixed,decoded):
        require(trace['source_id']==source_id,'same source trace')
        hs=trace['hits'];require(type(hs) is list and len(hs)==2,'two retained hits')
        chain=[]
        for step,h in enumerate(hs):
            p=h['primitive_id'];o=h['owner']
            require(type(p) is int and type(o) is int and 0<=p<len(owners) and o==step,'typed M then D hits')
            require(owners[p]['owner']==o,'hit primitive belongs to ORIGINAL owner')
            require(bridge.guard.rational(h['segment_BU'])>0,'strictly positive hit segment, no self/contact root')
            chain.append({'primitive_id':p,'owner':o,'object_id':owners[p]['object_id'],'kind':owners[p]['kind']})
        hit_chains.append(chain)
    require(hit_chains[0]==hit_chains[1],'same ORIGINAL/decoded hit owner primitive chain')
    return {'source_id':source_id,'mirror_phase_ORIGINAL_uint64':phase_word,
        'primitive_owner_map':owners,'selected_hit_chain':hit_chains[0],
        'fixed_trace_sha256':digest(fixed),'decoded_trace_sha256':digest(decoded),
        'ideal_coefficient_exact_reim':[[-1,1],[0,1]],
        'coefficient_model':'conditional fixed ideal -exp(i*ORIGINAL phase) at exact +/-0; NOT Fresnel/physical material',
        'profile_admitted_HOST_only':True,'material_executed':False,
        'executed_material_charge_L1':None,'executed_material_quota_fits':None,
        'native_material_ABI_implemented':False,'zero_canonicalization_performed':False}

def admit_current_source(packet,ctx,index,row,unitrow,argrow,qr,rr,polynomial_profile,mat):
    require(type(index) is int and 0<=index<len(ctx['source_order']),'source index')
    sid=ctx['source_order'][index]
    ev=bridge.admit_source(packet,ctx,index,row,unitrow,argrow,qr,rr,polynomial_profile)
    require(ev['source_id']==mat['source_id']==sid,'source profile proof identity')
    words=row['result']['product_uint64']
    require(type(words) is list and len(words)==2,'two current source output words')
    for w in words:bridge.guard.bits(w,64)
    return {'source_id':sid,'retained_source_row_sha256':digest(row),
        'retained_root_row_sha256':digest(rr),'current_bare_source_uint64':deepcopy(words),
        'phase_reference_id':row['phase_reference_id'],'terminal_reference_id':row['terminal_reference_id'],
        'fourteen_source_charges_L1':deepcopy(ev['charges_L1']),
        'partial_bare_source_bound_L1':deepcopy(ev['partial_bare_source_bound_L1']),
        'material_profile':deepcopy(mat),'source_profile_admitted_HOST_only':True,
        'material_executed':False,'executed_material_charge_L1':None,'executed_material_quota_fits':None,
        'status':'STOP','reason':'HOST source/material preflight ONLY; no new material execution, missing real INPUT allocations, no full field',
        **dict.fromkeys(FALSE,False)}

def audit_material_admission_HOST(case_names,*,model):
    require(model==MODEL,'explicit source-bound HOST material model')
    require(type(case_names) is list and 1<=len(case_names)<=64 and
        all(type(n) is str and n for n in case_names) and len(set(case_names))==len(case_names),'bounded unique cases')
    retained,pins=load_retained()
    packets,old,unit,arg,quot,roots,polynomial_profile,_,_=retained
    require(set(case_names)<=set(packets),'known cases')
    profiles={}
    # ALL contexts and material guards BEFORE ANY retained numerical proof admission.
    for name in case_names:
        ctx=old['cases'][name]['context']
        snap,meta=original.snapshot_from_packet(packets[name],ctx)
        for parent in (old,unit,arg,quot,roots):
            c=parent['cases'][name]
            require(c['context']==ctx and [r['source_id'] for r in c['sources']]==ctx['source_order'],'same complete contexts/source order')
            require(all(c[n] is False for n in FALSE),'no inherited promotion')
        for i,row in enumerate(old['cases'][name]['sources']):
            require(type(row[bridge.prior.FLAG]) is bool and row['status']=='STOP' and all(row[n] is False for n in FALSE),'typed source eligibility/nonpromotion')
            if row[bridge.prior.FLAG]:
                rr=roots['cases'][name]['sources'][i]['result']
                profiles[name,i]=material_profile(snap,meta,row['source_id'],
                    rr['fixed_ORIGINAL_reference'],rr['new_decoded_Xroot_result']['fixed_ORIGINAL_reference'])
    admitted={}
    # ALL requested proofs admitted before exposing ANY output admission row.
    for (name,i),mat in profiles.items():
        ctx=old['cases'][name]['context']
        admitted[name,i]=admit_current_source(packets[name],ctx,i,old['cases'][name]['sources'][i],
            unit['cases'][name]['sources'][i],arg['cases'][name]['sources'][i],
            quot['cases'][name]['sources'][i],roots['cases'][name]['sources'][i],polynomial_profile,mat)
    cases={}
    for name in case_names:
        rows=[]
        for i,row in enumerate(old['cases'][name]['sources']):
            if (name,i) in admitted:rows.append(admitted[name,i])
            else:rows.append({'source_id':row['source_id'],'retained_source_row_sha256':digest(row),
                'source_profile_admitted_HOST_only':False,'material_executed':False,
                'executed_material_charge_L1':None,'executed_material_quota_fits':None,
                'status':'STOP','reason':row['reason'],'reason_provenance':'unchanged retained upstream STOP',
                **dict.fromkeys(FALSE,False)})
        cases[name]={'context':deepcopy(old['cases'][name]['context']),'sources':rows,'status':'STOP',**dict.fromkeys(FALSE,False)}
    return {'model':MODEL,'case_order':deepcopy(case_names),'cases':cases,'inherited_pins_verified':len(pins),
        'source_material_profiles_admitted_HOST_only':len(admitted),
        'retained_sources_STOP':sum(len(v['sources']) for v in cases.values())-len(admitted),
        'new_native_operations':0,'old_native_stages_suites_reexecuted':0,
        'material_charge_invented_as_zero':False,'allocation_policy_adopted':False,
        'cost_scope':'HOST retained proof/preflight only; IO/pins/setup/upstream/remaining costs UNMEASURED NOT zero',
        **dict.fromkeys(FALSE,False)}
