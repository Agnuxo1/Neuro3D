"""New opt-in guarded scene-to-bare-source CPU prefix; no material/full-field admission."""
import base64,struct
from copy import deepcopy
from fractions import Fraction as F
import axial_geometry_decode_guard_CPU_v1 as guard
geo=guard.prior
source_stage=geo.prior
unit_stage=source_stage.unit
original=guard.original
io=guard.io
allocation=guard.allocation
require=guard.require
digest=guard.digest
pair=guard.pair
FALSE=guard.FALSE
MODEL='axial-fresh-scene-hilo-guard-RN64-unit-bare-source-prefix-CPU-v1'
FLAG='fresh_guarded_scene_bare_source_prefix_CPU_executed'
PREVIOUS='coordinacion/respuestas/AXIAL-GEOMETRY-DECODE-GUARD-CPU-001-CODEX.json'
PREVIOUS_SHA='6fb3d9660bb4e737d73e0d4e7bd1612811cf54cef3a888faf3f02bf051dcbf48'
SOURCE_REPORT='coordinacion/respuestas/AXIAL-ORIGINAL-SOURCE-CPU-001-CODEX.json'

def load_retained():
    r=allocation.parse(io.read(PREVIOUS,PREVIOUS_SHA))
    require(r['task_id']=='AXIAL-GEOMETRY-DECODE-GUARD-CPU-001','predecessor identity')
    pins=io.pins_from(r);pins[PREVIOUS]=PREVIOUS_SHA
    for p,h in pins.items():io.read(p,h)
    def data(p):return io.payload(allocation.parse(io.read(p,pins[p])))
    old=io.payload(r)['data']['audit'];src=data(SOURCE_REPORT)['data']['audit']
    require(src['previous_SOURCE_eight_bit_FAILs_preserved'] and src['previous_SOURCE_twelve_zero_sign_mismatches_preserved'],'retained SOURCE FAILs')
    packets=data(io.INGRESS)['packets']
    packets.update({n:v['parent'] for n,v in data(io.PRESENCE)['synthetic_controls'].items()})
    require(set(packets)==set(old['cases'])==set(src['cases']),'complete cases')
    return packets,old,src,pins

def compose(geom,arg,unit,cap):
    require(cap==[1,10**12] and all(type(x) is int for x in cap),'unchanged cap')
    G=guard.rational(geom['geometry_reference_wavelength_phase_bound_rad'])
    A=guard.rational(arg['phase_error_bound_rad'])
    B=guard.rational(unit['point_polynomial_L1_to_ideal_represented_angle_bound'])
    require(G>=0 and A>=0 and 0<B<F(1,2),'small nonnegative point charges')
    require(A==sum((guard.rational(v) for v in arg['phase_error_charges_rad'].values()),F(0)),'separate decoded argument charges')
    require(geom['decoded_argument_RN64_bound_rad']==arg['phase_error_bound_rad']
        and guard.rational(geom['point_argument_to_fixed_ORIGINAL_phase_bound_rad'])==G+A,'geometry argument binding')
    require(guard.rational(unit['point_polynomial_phase_bound_rad'])==B/(1-B),'polynomial phase identity')
    require(unit['argument_uint64']==arg['argument_uint64'],'fresh argument to unit binding')
    l1={'Horner_L1':B,'decoded_argument_L1':2*A,'geometry_reference_wavelength_L1':2*G}
    phase=B/(1-B)+A+G
    return {'unit_L1_charges_to_fixed_ORIGINAL':{k:pair(v) for k,v in l1.items()},
        'point_unit_L1_to_fixed_ORIGINAL_bound':pair(sum(l1.values(),F(0))),
        'point_unit_phase_to_fixed_ORIGINAL_bound_rad':pair(phase),
        'unchanged_phase_cap_rad':deepcopy(cap),'phase_charge_fits_unchanged_cap':phase<=F(*cap),
        'source_amplitude_budget_admitted':False,
        'rule':'L1 <= B_Horner+2*A_decoded_argument+2*G_geometry; phase <= B/(1-B)+A+G',
        'scope':'point unit toward fixed ORIGINAL; no source amplitude allowance/material/uniform/physical field claim'}

def execute_prefix(snapshot,index,profile,cap):
    # No previous numerical capsule supplies arguments/units/source limbs.
    geometry=geo.encode_geometry(snapshot,index)
    decoded,admission=guard.decode_guarded(snapshot,index,geometry)
    fixed_trace=original.trace_original(snapshot,index)
    trace=original.trace_original(decoded,index)
    trace['scope']='new exact rational traversal/selector of guarded CPU-decoded scene, not native ray arithmetic; legacy ORIGINAL keys refer to decoded inputs here'
    arg=original.argument_from_trace(trace)
    charges=geo.compose(fixed_trace,trace,arg,int(decoded['sources'][index]['direction'][0]),cap)
    unit=unit_stage.execute_unit(arg['argument_uint64'],trace['quadrant_mod4'],profile)
    comp=compose(charges,arg,unit,cap)
    source=source_stage.encode_source(snapshot['sources'][index]['field_reim'])
    product=source_stage.product_prefix(source,unit['unit_uint64'],comp['point_unit_L1_to_fixed_ORIGINAL_bound'])
    S=F(*product['ORIGINAL_source_norm_L1'])
    detailed={'source_encoding_L1':F(*product['bare_source_error_charges_L1']['source_encoding_L1']),
        'source_decode_RN64_L1':F(*product['bare_source_error_charges_L1']['source_decode_RN64_L1']),
        **{'source_'+k:S*F(*v) for k,v in comp['unit_L1_charges_to_fixed_ORIGINAL'].items()},
        'source_product_RN64_L1':F(*product['bare_source_error_charges_L1']['product_RN64_L1'])}
    require(sum(detailed.values(),F(0))==F(*product['point_bare_source_to_ORIGINAL_bound_L1']),'six separate source-prefix charges')
    return {'geometry_encoder':geometry,'guarded_decode':admission,'fixed_ORIGINAL_trace':fixed_trace,
        'decoded_trace':trace,'decoded_argument':arg,'geometry_composition':charges,'unit':unit,
        'unit_composition':comp,'source_encoder':source,'bare_source_prefix':product,
        'detailed_source_charges_L1':{k:pair(v) for k,v in detailed.items()},
        'point_bare_source_to_fixed_ORIGINAL_bound_L1':product['point_bare_source_to_ORIGINAL_bound_L1'],
        'new_CPU_decode_adds_encoding_and_guard':2*len(geometry['records']),
        'new_exact_root_records':len(fixed_trace['root_projection_records'])+len(trace['root_projection_records']),
        'source_amplitude_budget_admitted':False,'material_reflection_coefficient_applied':False,
        'old_numerical_capsule_used_as_argument_unit_source_input':False}

def audit_chain_CPU(case_names,*,model):
    require(model==MODEL,'explicit new guarded CPU chain model')
    require(type(case_names) is list and 1<=len(case_names)<=64 and all(type(n) is str and n for n in case_names) and len(set(case_names))==len(case_names),'bounded unique cases')
    packets,old,oldsrc,pins=load_retained();require(set(case_names)<=set(packets),'known cases')
    probe=source_stage.runtime_probe();require(probe['PASS'] is True,'runtime FAIL before encoder/guard/traversal')
    profile=oldsrc['coefficient_profile'];unit_stage.validate_profile(profile)
    cases={};executed=stopped=scalars=roots=0
    for name in case_names:
        packet=packets[name];ctx=allocation.context_from_packet(packet,digest(packet),model=allocation.MODEL)
        require(ctx==old['cases'][name]['context']==oldsrc['cases'][name]['context'],'same complete INPUT')
        snap,meta=original.snapshot_from_packet(packet,ctx);rows=[]
        require([r['source_id'] for r in old['cases'][name]['sources']]==[r['source_id'] for r in oldsrc['cases'][name]['sources']]==ctx['source_order'],'complete source order')
        for i,(r,s) in enumerate(zip(old['cases'][name]['sources'],oldsrc['cases'][name]['sources'])):
            require(r[guard.FLAG] is s[source_stage.FLAG],'same eligible sources')
            row={'source_id':r['source_id'],'status':'STOP',FLAG:False,'retained_guard_row_sha256':digest(r),**dict.fromkeys(FALSE,False)}
            if not r[guard.FLAG]:
                stopped+=1;row.update(reason=r['reason'],reason_provenance='unchanged_retained_STOP')
            else:
                raw=base64.b64decode(packet['buffers_base64']['sources'],validate=True)
                require(packet['manifest']['layout']['sources']['stride_words']==32 and len(raw)==128*len(ctx['source_order'])
                    and raw[128*i+112:128*i+128]==struct.pack('<dd',*snap['sources'][i]['field_reim']),'same ORIGINAL source complex words')
                result=execute_prefix(snap,i,profile,meta['original_path_phase_caps'][r['source_id']])
                require(result['fixed_ORIGINAL_trace']==s['trace'],'fixed ORIGINAL reference crosscheck AFTER fresh execution')
                row.update(result=result,**{FLAG:True},phase_reference_id=ctx['assignments'][i]['source_phase_reference_id'],
                    terminal_reference_id=ctx['assignments'][i]['terminal_reference_id'],
                    reason='new guarded scene-to-source bare PREFIX point; no material/allocations/reduction/detector/native ray/uniform/full field admission')
                executed+=1;scalars+=len(result['geometry_encoder']['records']);roots+=result['new_exact_root_records']
            rows.append(row)
        cases[name]={'context':ctx,'sources':rows,**dict.fromkeys(FALSE,False)}
    return {'model':MODEL,'case_order':deepcopy(case_names),'cases':cases,'runtime_probe':probe,'coefficient_profile':profile,
        'inherited_pins_verified':len(pins),'fresh_guarded_prefix_sources_executed':executed,'retained_sources_not_executed':stopped,
        'new_geometry_RN32_casts':2*scalars,'new_geometry_RN64_subtractions':scalars,
        'new_geometry_encoder_decode_adds':scalars,'new_geometry_guard_native_decode_adds':scalars,
        'new_exact_fixed_and_decoded_root_records':roots,'new_decoded_argument_casts':executed,'new_decoded_argument_multiplies':executed,
        'new_Horner_RN64_nodes':26*executed,'new_source_RN32_casts':4*executed,'new_source_RN64_subtractions':2*executed,
        'new_source_decode_product_nodes':8*executed,'new_material_reduction_power_readout_executions':0,
        'old_numeric_audits_suites_reexecuted':0,'previous_SOURCE_eight_bit_FAILs_preserved':True,'previous_SOURCE_twelve_zero_sign_mismatches_preserved':True,
        'native_ray_arithmetic_executed':False,'uniform_backend_domain_admitted':False,
        'cost_scope':'fresh geometry encode includes one decode add/scalar, guarded consumer executes SECOND decode add/scalar, both counted; fixed/decoded rational reference/selector, new argument/Horner/source/product; main probes6ops64+4casts32; IO/pins/setup/rational and remaining costs UNMEASURED never zero',
        **dict.fromkeys(FALSE,False)}
