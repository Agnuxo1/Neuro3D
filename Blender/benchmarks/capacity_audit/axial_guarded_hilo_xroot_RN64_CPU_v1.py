"""Opt-in retained hi-lo ingress -> NEW guarded decode and Xroot RN64 point contrast."""
from copy import deepcopy
from fractions import Fraction as F
import axial_xroot_selector_RN64_CPU_v1 as prior
guard=prior.guard
original=prior.original
source=prior.source
io=prior.io
allocation=prior.allocation
require=prior.require
digest=prior.digest
pair=prior.pair
FALSE=prior.FALSE
MODEL='axial-retained-hilo-guard-new-Xroot-RN64-CPU-point-v1'
FLAG='guarded_hilo_Xroot_RN64_CPU_executed'
PREVIOUS='coordinacion/respuestas/AXIAL-XROOT-SELECTOR-RN64-CPU-001-CODEX.json'
PREVIOUS_SHA='3174f3d340f0e06692430e619dccc9852189f001221061b73bec2733bdcb7d4b'

def load_retained():
    r=allocation.parse(io.read(PREVIOUS,PREVIOUS_SHA))
    require(r['task_id']=='AXIAL-XROOT-SELECTOR-RN64-CPU-001','predecessor identity')
    pins=io.pins_from(r);pins[PREVIOUS]=PREVIOUS_SHA
    for p,h in pins.items():io.read(p,h)
    def data(p):return io.payload(allocation.parse(io.read(p,pins[p])))
    old=io.payload(r)['data']['audit'];chain=data(prior.PREVIOUS)['data']['audit']
    packets=data(io.INGRESS)['packets']
    packets.update({n:v['parent'] for n,v in data(io.PRESENCE)['synthetic_controls'].items()})
    require(set(packets)==set(old['cases'])==set(chain['cases']),'complete cases')
    return packets,old,chain,pins

def compose(fixed,root_result,sign,cap):
    require(type(sign) is int and sign in (-1,1),'typed axial sign')
    require(type(cap) is list and cap==[1,10**12] and all(type(x) is int for x in cap),'unchanged phase cap')
    decoded=root_result['fixed_ORIGINAL_reference']
    require([(h['primitive_id'],h['owner']) for h in fixed['hits']]==[(h['primitive_id'],h['owner']) for h in decoded['hits']],'same fixed/decoded primitive owners')
    require(fixed['quarter_index']==decoded['quarter_index'],'same fixed/decoded quarter')
    c={k:guard.rational(v) for k,v in fixed['ORIGINAL_coordinates_BU'].items()}
    d={k:guard.rational(v) for k,v in decoded['ORIGINAL_coordinates_BU'].items()}
    require(c.keys()==d.keys()=={'M','S','D','R','wavelength'},'complete coordinates')
    for t,v in ((fixed,c),(decoded,d)):
        require(v['wavelength']>0,'positive wavelength')
        require(guard.rational(t['geometric_length_BU'])==sign*(2*v['M']-v['S']-v['D'])
            and guard.rational(t['reference_correction_BU'])==sign*(v['D']-v['R'])
            and guard.rational(t['effective_reference_length_BU'])==sign*(2*v['M']-v['S']-v['R']),'explicit geometry/reference cancellation identities')
    e={k:abs(d[k]-c[k]) for k in c}
    Egeo=2*e['M']+e['S']+e['D'];Eref=e['D']+e['R'];Eeff=2*e['M']+e['S']+e['R']
    round_charges={k:guard.rational(v) for k,v in root_result['length_rounding_charges_BU'].items()}
    require(set(round_charges)=={'selected_Xroot_rounding_BU','geometric_accumulation_rounding_BU','reference_subtraction_rounding_BU','effective_add_rounding_BU'}
        and all(v>=0 for v in round_charges.values()),'four separate nonnegative rounding charges')
    R=sum(round_charges.values(),F(0));require(R==guard.rational(root_result['length_to_fixed_ORIGINAL_bound_BU']),'rounding bound recomposition')
    actual=guard.bits(root_result['effective_reference_length_uint64'],64)
    L0=guard.rational(fixed['effective_reference_length_BU']);Ld=guard.rational(decoded['effective_reference_length_BU'])
    require(abs(Ld-L0)<=Eeff and abs(actual-Ld)<=R,'fixed ORIGINAL representation and rounding bounds')
    cycle_charges={'geometry_representation_cycles':Eeff/d['wavelength'],'Xroot_length_rounding_cycles':R/d['wavelength'],
        'wavelength_representation_cycles':abs(L0)*e['wavelength']/(d['wavelength']*c['wavelength'])}
    E=sum(cycle_charges.values(),F(0));observed=abs(actual/d['wavelength']-L0/c['wavelength'])
    require(observed<=E,'combined cycles toward fixed ORIGINAL')
    phase_charges={k.replace('_cycles','_rad'):2*original.PI_UPPER*v for k,v in cycle_charges.items()}
    phase=sum(phase_charges.values(),F(0))
    quarter=F(fixed['quarter_index'],4)
    margin=F(1,8)-abs(L0/c['wavelength']-quarter)-E
    return {'coordinate_errors_BU':{k:pair(v) for k,v in e.items()},
        'geometry_representation_length_bound_BU':pair(Egeo),'reference_representation_bound_BU':pair(Eref),
        'uncorrelated_geometry_plus_reference_bound_BU':pair(Egeo+Eref),
        'effective_representation_bound_shared_D_cancelled_BU':pair(Eeff),
        'Xroot_length_rounding_charges_BU':{k:pair(v) for k,v in round_charges.items()},
        'Xroot_length_rounding_bound_BU':pair(R),'combined_effective_length_bound_BU':pair(Eeff+R),
        'actual_length_to_FIXED_ORIGINAL_error_BU':pair(abs(actual-L0)),
        'cycle_charges_to_fixed_ORIGINAL':{k:pair(v) for k,v in cycle_charges.items()},
        'cycles_to_fixed_ORIGINAL_bound':pair(E),'observed_host_exact_cycles_error':pair(observed),
        'phase_length_wavelength_charges_rad':{k:pair(v) for k,v in phase_charges.items()},
        'phase_length_wavelength_only_bound_rad':pair(phase),'unchanged_phase_cap_rad':deepcopy(cap),
        'length_wavelength_only_phase_charge_fits_cap':phase<=F(*cap),
        'quarter_margin_with_combined_error_cycles':pair(margin),'quarter_point_interval_certified':margin>0,
        'RN64_quotient_argument_not_executed':True,'scope':'point ORIGINAL fixed vs guarded hi-lo coordinates plus RN64 Xroot lengths; no quotient rounding/argument/unit/source/full field/uniform/physical'}

def execute(snapshot,index,encoder,cap):
    require(type(cap) is list and cap==[1,10**12] and all(type(x) is int for x in cap),'unchanged phase cap before decode')
    decoded,proof=guard.decode_guarded(snapshot,index,encoder)
    fixed=original.trace_original(snapshot,index)
    result=prior.execute(decoded,index,cap)
    composition=compose(fixed,result,int(snapshot['sources'][index]['direction'][0]),cap)
    return {'retained_geometry_encoder':deepcopy(encoder),'retained_transport_sha256':encoder['transport_le_sha256'],
        'guarded_decode':proof,'decoded_snapshot':decoded,'fixed_ORIGINAL_reference':fixed,
        'new_decoded_Xroot_result':result,'composition':composition,
        'new_native_decode_adds':len(proof['native_decode_nodes']),
        'new_fixed_and_decoded_rational_root_records':len(fixed['root_projection_records'])+result['new_rational_reference_root_records'],
        'new_encoder_operations':0,'new_Horner_source_material_reduction_power_readout':0,
        'scope':'retained INPUT hi-lo limbs consumed by NEW guard decode and Xroot RN64; not fresh encoder or complete fresh scene-to-field'}

def audit_hilo_Xroot_CPU(case_names,*,model):
    require(model==MODEL,'explicit retained hi-lo consumer model')
    require(type(case_names) is list and 1<=len(case_names)<=64 and all(type(n) is str and n for n in case_names)
        and len(set(case_names))==len(case_names),'bounded unique cases')
    packets,old,chain,pins=load_retained();require(set(case_names)<=set(packets),'known cases')
    admitted=[]
    for name in case_names:
        ctx=allocation.context_from_packet(packets[name],digest(packets[name]),model=allocation.MODEL)
        require(ctx==old['cases'][name]['context']==chain['cases'][name]['context'],'same fresh complete INPUT')
        snap,meta=original.snapshot_from_packet(packets[name],ctx)
        rows=old['cases'][name]['sources'];cs=chain['cases'][name]['sources']
        require(ctx['source_order']==[r['source_id'] for r in rows]==[r['source_id'] for r in cs],'complete ordered sources')
        encoders={}
        for i,(r,c) in enumerate(zip(rows,cs)):
            require(r[prior.FLAG] is c[prior.retained.prior.FLAG],'same retained eligible sources')
            if r[prior.FLAG]:
                enc=c['result']['geometry_encoder'];guard.admit(snap,i,enc)
                encoders[i]=enc
        admitted.append((name,ctx,snap,meta,encoders))
    # ALL eligible records/context/limbs are checked before any new CPU decode/root.
    cases={};executed=stopped=adds=records=0;counts=dict.fromkeys(('subtract','add','negate'),0)
    for name,ctx,snap,meta,encoders in admitted:
        rows=[]
        for i,r in enumerate(old['cases'][name]['sources']):
            row={'source_id':r['source_id'],'status':'STOP',FLAG:False,'retained_Xroot_row_sha256':digest(r),**dict.fromkeys(FALSE,False)}
            if i not in encoders:
                stopped+=1;row.update(reason=r['reason'],reason_provenance='unchanged_retained_STOP')
            else:
                result=execute(snap,i,encoders[i],meta['original_path_phase_caps'][r['source_id']])
                require(result['fixed_ORIGINAL_reference']==r['result']['fixed_ORIGINAL_reference'],'fixed ORIGINAL crosscheck after execution')
                executed+=1;adds+=result['new_native_decode_adds'];records+=result['new_fixed_and_decoded_rational_root_records']
                for k,v in result['new_decoded_Xroot_result']['new_RN64_operation_counts'].items():counts[k]+=v
                row.update(result=result,**{FLAG:True},phase_reference_id=ctx['assignments'][i]['source_phase_reference_id'],
                    terminal_reference_id=ctx['assignments'][i]['terminal_reference_id'],
                    reason='point guarded hi-lo -> Xroot/length contrast only; missing quotient/argument/full domain/budgets/field stay STOP')
            rows.append(row)
        cases[name]={'context':ctx,'sources':rows,**dict.fromkeys(FALSE,False)}
    return {'model':MODEL,'case_order':deepcopy(case_names),'cases':cases,'inherited_pins_verified':len(pins),
        'new_point_sources_executed':executed,'retained_sources_not_executed':stopped,'new_guard_decode_adds':adds,
        'new_Xroot_RN64_operation_counts':counts,'new_fixed_and_decoded_rational_root_records':records,
        'new_encoder_operations':0,'old_audits_suites_reexecuted':0,'new_Horner_source_material_reduction_power_readout':0,
        'native_YZ_projection_selector_implemented':False,'RN64_quotient_argument_executed':False,
        'all_eligible_transports_admitted_before_new_operations':True,
        'cost_scope':'retained encoder not reexecuted but not zero upstream cost; decode and Xroot ops separate; pure admission/YZ/reference/HOST proofs/IO/pins/setup/remaining UNMEASURED never zero; wall not benchmark parity',
        **dict.fromkeys(FALSE,False)}
