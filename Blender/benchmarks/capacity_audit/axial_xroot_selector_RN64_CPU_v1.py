"""Opt-in ORIGINAL-point X roots/lengths RN64; HOST rational YZ and interval selector."""
import math
from copy import deepcopy
from fractions import Fraction as F
import axial_ideal_reflection_stage_CPU_v1 as retained
guard=retained.prior.guard
original=guard.original
source=guard.source
io=guard.io
allocation=guard.allocation
require=guard.require
digest=guard.digest
pair=guard.pair
FALSE=guard.FALSE
MODEL='axial-ORIGINAL-point-Xroot-RN64-HOST-selector-v1'
FLAG='ORIGINAL_point_Xroot_RN64_CPU_executed'
PREVIOUS=retained.PREVIOUS
PREVIOUS_SHA=retained.PREVIOUS_SHA
load_retained=retained.load_retained
SIGN=1<<63

def native_sub(a,b):
    return a-b

def native_add(a,b):
    return a+b

def native_negate(a):
    return -a

def node(op,a,b=None):
    """Observe a new CPU operation and independently validate unique RN-even."""
    aw=source.word(a); aq=guard.bits(aw,64)
    if op=='negate':
        out=native_negate(a); exact=-aq; zero_sign=1-(aw>>63)
        inputs=[aw]
    else:
        bw=source.word(b); bq=guard.bits(bw,64); inputs=[aw,bw]
        require(op in ('subtract','add'),'node operation whitelist')
        out=native_sub(a,b) if op=='subtract' else native_add(a,b)
        exact=aq-bq if op=='subtract' else aq+bq
        zero_sign=int(aq==bq==0 and aw>>63==1 and (bw>>63)==(0 if op=='subtract' else 1))
    ow=source.word(out); value=guard.check_RN(exact,ow,64,zero_sign)
    require(exact==0 or value!=0,'nonzero rounded to zero STOP')
    mag=ow%(1<<63)
    if mag==0:
        lo,hi=-F(1,2**1075),F(1,2**1075)
    else:
        current=abs(value); lower=abs(guard.bits(mag-1,64,normal=False))
        require(mag<0x7fefffffffffffff,'finite upper neighbor required')
        upper=abs(guard.bits(mag+1,64,normal=False))
        left,right=(lower+current)/2,(current+upper)/2
        lo,hi=(-right,-left) if value<0 else (left,right)
    require(lo<=exact<=hi,'exact point enclosed')
    radius=max(value-lo,hi-value)
    return out,{'operation':op,'input_uint64':inputs,'output_uint64':ow,
        'exact_operation_BU':pair(exact),'signed_rounding_delta_BU':pair(value-exact),
        'rounding_cell_BU':[pair(lo),pair(hi)],'radius_BU':pair(radius)}

def root(plane,origin,sign):
    require(type(sign) is int and sign in (-1,1),'typed axial sign')
    v,n=node('subtract',plane,origin); nodes=[n]
    interval=[F(*q) for q in n['rounding_cell_BU']]
    if sign<0:
        v,m=node('negate',v); nodes.append(m)
        # Unary sign is exact: do not add its midpoint radius as new error.
        require(m['signed_rounding_delta_BU']==[0,1],'exact sign reflection')
        interval=[-interval[1],-interval[0]]
    q=(original.number(plane)-original.number(origin))*sign
    return {'plane_uint64':source.word(plane),'origin_uint64':source.word(origin),'direction':sign,
        'root_uint64':source.word(v),'exact_root_BU':pair(q),'root_interval_BU':[pair(x) for x in interval],
        'rounding_radius_BU':n['radius_BU'],'nodes':nodes}

def select(records,expected_owner):
    """Pure HOST conservative interval decision; no exact-root fallback/tie breaker."""
    candidates=[]
    for r in records:
        kind=r['classification']
        if kind in ('miss','previous_owner_zero_root_excluded'):continue
        require(kind=='strict_interior','boundary/unknown projection STOP')
        lo,hi=[guard.rational(x) for x in r['root']['root_interval_BU']]
        require(lo<=hi,'ordered root interval')
        if hi<0:continue
        require(lo>0,'root interval touches zero STOP')
        candidates.append(r)
    require(candidates,'no certified forward hit')
    winner=min(candidates,key=lambda r:guard.rational(r['root']['root_interval_BU'][1]))
    whi=guard.rational(winner['root']['root_interval_BU'][1])
    require(all(r is winner or whi<guard.rational(r['root']['root_interval_BU'][0]) for r in candidates),'overlapping nearest intervals STOP')
    require(winner['owner']==expected_owner,'unexpected nearest owner STOP')
    return winner

def execute(snapshot,index,cap):
    require(type(cap) is list and cap==[1,10**12] and all(type(x) is int for x in cap),'unchanged fixture phase cap')
    # Fresh rational ORIGINAL reference validates this restricted geometry/YZ.
    # It is not the selector's input root value nor a native YZ implementation.
    reference=original.trace_original(snapshot,index)
    planes=[snapshot['objects'][n]['vertices_world_BU'][0][0] for n in ('M','D')]
    origin=snapshot['sources'][index]['position_BU'][0]
    sign=int(snapshot['sources'][index]['direction'][0])
    previous=None; steps=[]; allnodes=[]; selected=[]; previous_count=0
    for step,expected in enumerate((0,1)):
        rows=[]
        for p in reference['root_projection_records']:
            if p['step']!=step:continue
            owner=p['owner']; rr=root(planes[owner],origin,sign); allnodes.extend(rr['nodes'])
            row={'step':step,'primitive_id':p['primitive_id'],'owner':owner,'classification':p['classification'],'root':rr}
            if 'det_U_V_W' in p:row['det_U_V_W']=deepcopy(p['det_U_V_W'])
            if owner==previous:
                require(step==1 and planes[owner]==origin and p['classification']=='previous_owner_zero_root_excluded'
                    and guard.bits(rr['root_uint64'],64)==0,'previous owner exact zero only')
                previous_count+=1
            else:require(p['classification']!='previous_owner_zero_root_excluded','no initial contact exemption')
            rows.append(row)
        winner=select(rows,expected); selected.append(winner); steps.append(rows)
        # Reference identity is only a check AFTER interval selection.
        require((winner['primitive_id'],winner['owner'])==(reference['hits'][step]['primitive_id'],reference['hits'][step]['owner']),'ORIGINAL hit crosscheck after selection')
        origin=planes[winner['owner']]; previous=winner['owner']; sign=-sign
    roots=[source.value(r['root']['root_uint64'],64) for r in selected]
    geom=0.0; accumulation=[]
    for v in roots:
        geom,n=node('add',geom,v); accumulation.append(n)
    srcsign=int(snapshot['sources'][index]['direction'][0])
    ref_origin=snapshot['objects']['D']['mode_origin_BU'][0]
    correction,n=node('subtract',planes[1],ref_origin); corrnodes=[n]
    if srcsign<0:
        correction,n=node('negate',correction); corrnodes.append(n)
    effective,n=node('add',geom,correction); effnode=n
    root_error=sum((guard.rational(r['root']['rounding_radius_BU']) for r in selected),F(0))
    accumulation_error=sum((guard.rational(n['radius_BU']) for n in accumulation),F(0))
    reference_error=guard.rational(corrnodes[0]['radius_BU'])
    final_error=guard.rational(effnode['radius_BU'])
    charges={'selected_Xroot_rounding_BU':root_error,'geometric_accumulation_rounding_BU':accumulation_error,
        'reference_subtraction_rounding_BU':reference_error,'effective_add_rounding_BU':final_error}
    bound=sum(charges.values(),F(0))
    observed=abs(guard.bits(source.word(effective),64)-guard.rational(reference['effective_reference_length_BU']))
    require(observed<=bound,'length error toward fixed ORIGINAL bounded')
    phase=2*original.PI_UPPER*bound/guard.rational(reference['wavelength_BU'])
    allnodes+=accumulation+corrnodes+[effnode]
    return {'scope':'new CPU RN64 X roots and lengths from ORIGINAL point; YZ/proofs/selector HOST rational; NOT hi-lo decoded input/general3D/native full ray/full field',
        'fixed_ORIGINAL_reference':reference,'steps':steps,'selected_identity':[[r['primitive_id'],r['owner']] for r in selected],
        'selected_root_uint64':[r['root']['root_uint64'] for r in selected],
        'geometric_length_uint64':source.word(geom),'reference_correction_uint64':source.word(correction),
        'effective_reference_length_uint64':source.word(effective),'accumulation_nodes':accumulation,
        'reference_nodes':corrnodes,'effective_node':effnode,'length_rounding_charges_BU':{k:pair(v) for k,v in charges.items()},
        'length_to_fixed_ORIGINAL_bound_BU':pair(bound),'observed_length_error_BU':pair(observed),
        'phase_from_length_only_bound_rad':pair(phase),'unchanged_phase_cap_rad':deepcopy(cap),
        'length_only_phase_charge_fits_cap':phase<=F(*cap),'new_RN64_operation_counts':{k:sum(n['operation']==k for n in allnodes) for k in ('subtract','add','negate')},
        'new_rational_reference_root_records':len(reference['root_projection_records']),
        'previous_owner_exact_zero_exclusions':previous_count,'native_YZ_projection_executed':False,
        'full_native_ray_selector_implemented':False,'hi_lo_geometry_replayed':False,
        'remaining_argument_unit_source_material_reduction_power_readout_executions':0}

def audit_Xroot_CPU(case_names,*,model):
    require(model==MODEL,'explicit Xroot RN64 point model')
    require(type(case_names) is list and 1<=len(case_names)<=64 and all(type(n) is str and n for n in case_names)
        and len(set(case_names))==len(case_names),'bounded unique cases')
    packets,old,pins=load_retained();require(set(case_names)<=set(packets),'known cases')
    admitted=[]
    for name in case_names:
        ctx=allocation.context_from_packet(packets[name],digest(packets[name]),model=allocation.MODEL)
        require(ctx==old['cases'][name]['context'],'same fresh complete INPUT')
        snap,meta=original.snapshot_from_packet(packets[name],ctx)
        require(ctx['source_order']==[r['source_id'] for r in old['cases'][name]['sources']],'ordered complete sources')
        admitted.append((name,ctx,snap,meta))
    # All contexts admitted before any new numeric operation.
    cases={}; executed=stopped=0; counts=dict.fromkeys(('subtract','add','negate'),0)
    for name,ctx,snap,meta in admitted:
        rows=[]
        for i,prior in enumerate(old['cases'][name]['sources']):
            row={'source_id':prior['source_id'],'status':'STOP',FLAG:False,'retained_row_sha256':digest(prior),**dict.fromkeys(FALSE,False)}
            if not prior[retained.prior.FLAG]:
                stopped+=1;row['reason']=prior['reason'];row['reason_provenance']='unchanged_retained_STOP'
            else:
                result=execute(snap,i,meta['original_path_phase_caps'][prior['source_id']])
                require(result['fixed_ORIGINAL_reference']==prior['result']['fixed_ORIGINAL_trace'],'retained ORIGINAL crosscheck after fresh execution')
                executed+=1
                for k,v in result['new_RN64_operation_counts'].items():counts[k]+=v
                row.update(result=result,**{FLAG:True},phase_reference_id=ctx['assignments'][i]['source_phase_reference_id'],
                    terminal_reference_id=ctx['assignments'][i]['terminal_reference_id'],
                    reason='point Xroot/length CPU contrast only; no full-ray/hi-lo/error-budget/field promotion')
            rows.append(row)
        cases[name]={'context':ctx,'sources':rows,**dict.fromkeys(FALSE,False)}
    return {'model':MODEL,'case_order':deepcopy(case_names),'cases':cases,'new_point_sources_executed':executed,
        'retained_sources_not_executed':stopped,'inherited_pins_verified':len(pins),'new_RN64_operation_counts':counts,
        'new_rational_reference_root_records':sum(r.get('result',{}).get('new_rational_reference_root_records',0) for c in cases.values() for r in c['sources']),
        'old_audits_suites_reexecuted':0,'full_native_ray_selector_implemented':False,
        'cost_scope':'CPU subtract/add/unary sign counted; reference/YZ/interval HOST/pins/IO/setup UNMEASURED not zero; upstream hi-lo and remaining stages not executed; suite wall not comparable performance',
        **dict.fromkeys(FALSE,False)}
