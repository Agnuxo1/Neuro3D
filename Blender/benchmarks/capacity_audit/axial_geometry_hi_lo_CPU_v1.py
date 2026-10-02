"""Opt-in CPU hi-lo32 geometry transport; rational traversal of decoded coordinates."""
import base64,hashlib,math,struct
from copy import deepcopy
from fractions import Fraction as F
import axial_ORIGINAL_source_CPU_v1 as prior
io=prior.io
allocation=prior.allocation
require=prior.require
digest=prior.digest
pair=prior.pair
original=prior.original
source=prior.source
FALSE=prior.FALSE
MODEL='axial-geometry-hilo32-RN64-decode-rational-traversal-CPU-v1'
FLAG='decoded_geometry_point_CPU_executed'
PREVIOUS='coordinacion/respuestas/AXIAL-ORIGINAL-SOURCE-CPU-001-CODEX.json'
PREVIOUS_SHA='a9a894bc3f2749f750aba78714ec31d1bb2cbd6a77c2bf862dfedfd565ccf162'

def load_retained():
    receipt=allocation.parse(io.read(PREVIOUS,PREVIOUS_SHA))
    require(receipt['task_id']=='AXIAL-ORIGINAL-SOURCE-CPU-001','predecessor identity')
    pins=io.pins_from(receipt);pins[PREVIOUS]=PREVIOUS_SHA
    for path,h in pins.items():io.read(path,h)
    old=io.payload(receipt)['data']['audit']
    require(old['previous_SOURCE_eight_bit_FAILs_preserved'] and old['previous_SOURCE_twelve_zero_sign_mismatches_preserved'],'historical FAILs retained')
    def data(p):return io.payload(allocation.parse(io.read(p,pins[p])))
    packets=data(io.INGRESS)['packets']
    packets.update({n:v['parent'] for n,v in data(io.PRESENCE)['synthetic_controls'].items()})
    require(set(packets)==set(old['cases']),'complete retained cases')
    return packets,old,pins

def paths(snapshot,index):
    require(type(index) is int and 0<=index<len(snapshot['sources']),'source index')
    out=[]
    for name in ('M','D'):
        vertices=snapshot['objects'][name]['vertices_world_BU']
        require(type(vertices) is list and 3<=len(vertices)<=192,'bounded vertices')
        for j,v in enumerate(vertices):
            require(type(v) is list and len(v)==3,'three coordinate vertex')
            out.extend([['objects',name,'vertices_world_BU',j,k] for k in range(3)])
    for key in ('position_BU','direction'):out.extend([['sources',index,key,k] for k in range(3)])
    for key in ('mode_origin_BU','mode_direction'):out.extend([['objects','D',key,k] for k in range(3)])
    out.extend([['lambda_BU'],['objects','M','phase_rad']])
    return out

def get(obj,path):
    for k in path:obj=obj[k]
    return obj
def put(obj,path,v):
    for k in path[:-1]:obj=obj[k]
    obj[path[-1]]=v

def scalar(x):
    q=original.number(x);hi,hw=prior.cast32(x);source.value(hw,32)
    residual=x-hi;original.number(residual)
    lo,lw=prior.cast32(residual);source.value(lw,32)
    decoded=hi+lo;original.number(decoded)
    exact_sum=F.from_float(hi)+F.from_float(lo)
    return {'original_uint64':source.word(x),'high_uint32':hw,'residual_uint64':source.word(residual),
        'low_uint32':lw,'decoded_uint64':source.word(decoded),
        'residual_RN64_delta':pair(F.from_float(residual)-(q-F.from_float(hi))),
        'represented_exact_sum':pair(exact_sum),'encoding_error_abs':pair(abs(exact_sum-q)),
        'decode_RN64_delta':pair(F.from_float(decoded)-exact_sum),'decoded_coordinate_error_abs':pair(abs(F.from_float(decoded)-q))}

def encode_geometry(snapshot,index):
    ps=paths(snapshot,index);records=[{'path':p,**scalar(get(snapshot,p))} for p in ps]
    raw=b''.join(struct.pack('<II',r['high_uint32'],r['low_uint32']) for r in records)
    return {'source_index':index,'original_snapshot_digest':digest(snapshot),'records':records,
        'ordered_paths_sha256':digest(ps),'transport_le_base64':base64.b64encode(raw).decode(),
        'transport_le_sha256':hashlib.sha256(raw).hexdigest(),'transport_bytes':len(raw),
        'transport_contract':'opt-in ordered scalar pairs LE; not a replacement for frozen INPUT/shader ABI',
        'new_RN32_casts':2*len(ps),'new_RN64_subtractions':len(ps),'new_RN64_decode_adds':len(ps)}

def decode_geometry(snapshot,index,encoder):
    ps=paths(snapshot,index)
    require(encoder['source_index']==index and encoder['original_snapshot_digest']==digest(snapshot),'same original snapshot/index')
    require([r['path'] for r in encoder['records']]==ps and encoder['ordered_paths_sha256']==digest(ps),'complete ordered coordinate paths')
    raw=base64.b64decode(encoder['transport_le_base64'],validate=True)
    require(len(raw)==encoder['transport_bytes']==8*len(ps) and hashlib.sha256(raw).hexdigest()==encoder['transport_le_sha256'],'transport bytes/SHA')
    out=deepcopy(snapshot)
    for j,r in enumerate(encoder['records']):
        require(r['original_uint64']==source.word(get(snapshot,r['path'])),'same original coordinate bits')
        hw,lw=struct.unpack_from('<II',raw,8*j)
        require([hw,lw]==[r['high_uint32'],r['low_uint32']],'same serialized limbs')
        hi,lo=source.value(hw,32),source.value(lw,32)
        # Decode has already executed once in scalar(); deserialize the observed word,
        # then check its exact rational ledger without a second floating-point add.
        v=source.value(r['decoded_uint64'],64);q=F.from_float(get(snapshot,r['path']))
        exact_sum=F.from_float(hi)+F.from_float(lo)
        require(r['represented_exact_sum']==pair(exact_sum) and r['encoding_error_abs']==pair(abs(exact_sum-q))
            and r['decode_RN64_delta']==pair(F.from_float(v)-exact_sum)
            and r['decoded_coordinate_error_abs']==pair(abs(F.from_float(v)-q)),'coordinate error ledger')
        put(out,r['path'],v)
    return out

def compose(original_trace,decoded_trace,arg,sign,cap):
    require(type(sign) is int and sign in (-1,1),'axial sign')
    require(type(cap) is list and len(cap)==2 and all(type(x) is int for x in cap) and cap==[1,10**12],'unchanged fixture phase cap')
    require([(h['primitive_id'],h['owner']) for h in original_trace['hits']]==[(h['primitive_id'],h['owner']) for h in decoded_trace['hits']],'same nearest primitive/owner')
    require(original_trace['quarter_index']==decoded_trace['quarter_index'],'same quarter branch')
    c={k:F(*v) for k,v in original_trace['ORIGINAL_coordinates_BU'].items()}
    d={k:F(*v) for k,v in decoded_trace['ORIGINAL_coordinates_BU'].items()}
    for t,v in ((original_trace,c),(decoded_trace,d)):
        require(v['wavelength']>0,'positive wavelength')
        require(F(*t['geometric_length_BU'])==sign*(2*v['M']-v['S']-v['D'])
            and F(*t['reference_correction_BU'])==sign*(v['D']-v['R'])
            and F(*t['effective_reference_length_BU'])==sign*(2*v['M']-v['S']-v['R']),'axial length/reference identities')
    e={k:abs(d[k]-c[k]) for k in c};geo=2*e['M']+e['S']+e['D'];ref=e['D']+e['R']
    effective=2*e['M']+e['S']+e['R']
    delta_geo=abs(F(*decoded_trace['geometric_length_BU'])-F(*original_trace['geometric_length_BU']))
    delta_ref=abs(F(*decoded_trace['reference_correction_BU'])-F(*original_trace['reference_correction_BU']))
    delta_eff=abs(F(*decoded_trace['effective_reference_length_BU'])-F(*original_trace['effective_reference_length_BU']))
    require(delta_geo<=geo and delta_ref<=ref and delta_eff<=effective,'geometry/reference bounds')
    length=F(*original_trace['effective_reference_length_BU'])
    cycles=effective/d['wavelength']+abs(length)*e['wavelength']/(d['wavelength']*c['wavelength'])
    observed=abs(F(*decoded_trace['exact_ORIGINAL_cycles'])-F(*original_trace['exact_ORIGINAL_cycles']))
    require(observed<=cycles,'wavelength quotient bound')
    phase=2*original.PI_UPPER*cycles;total=phase+F(*arg['phase_error_bound_rad'])
    return {'coordinate_errors_BU':{k:pair(v) for k,v in e.items()},'geometry_length_bound_BU':pair(geo),
        'reference_correction_bound_BU':pair(ref),'uncorrelated_effective_bound_BU':pair(geo+ref),
        'correlated_effective_bound_BU':pair(effective),'observed_geometry_delta_BU':pair(delta_geo),
        'observed_reference_delta_BU':pair(delta_ref),'observed_effective_delta_BU':pair(delta_eff),
        'wavelength_error_BU':pair(e['wavelength']),'cycles_bound':pair(cycles),'observed_cycles_delta':pair(observed),
        'geometry_reference_wavelength_phase_bound_rad':pair(phase),'decoded_argument_RN64_bound_rad':arg['phase_error_bound_rad'],
        'point_argument_to_fixed_ORIGINAL_phase_bound_rad':pair(total),'unchanged_phase_cap_rad':deepcopy(cap),
        'point_charge_fits_unchanged_cap':total<=F(*cap),'shared_D_cancellation_identity_checked':True,
        'first_root_BU':deepcopy(decoded_trace['hits'][0]['segment_BU']),
        'first_root_positive':F(*decoded_trace['hits'][0]['segment_BU'])>0,
        'scope':'point-only geometry/reference/wavelength plus argument; excludes source amplitude/material/Horner/full pipeline'}

def audit_geometry_CPU(case_names,*,model):
    require(model==MODEL,'explicit opt-in geometry CPU model')
    require(type(case_names) is list and 1<=len(case_names)<=64 and all(type(n) is str and n for n in case_names) and len(set(case_names))==len(case_names),'bounded unique cases')
    packets,old,pins=load_retained();require(set(case_names)<=set(packets),'known cases')
    probe=prior.runtime_probe();require(probe['PASS'] is True,'runtime guard FAIL before geometry transport')
    cases={};executed=stopped=scalars=0
    for name in case_names:
        packet=packets[name];ctx=allocation.context_from_packet(packet,digest(packet),model=allocation.MODEL)
        require(ctx==old['cases'][name]['context'],'same complete INPUT')
        snapshot,meta=original.snapshot_from_packet(packet,ctx);rows=[]
        require([r['source_id'] for r in old['cases'][name]['sources']]==ctx['source_order'],'complete ordered source rows')
        for i,r in enumerate(old['cases'][name]['sources']):
            row={'source_id':r['source_id'],'status':'STOP',FLAG:False,'retained_source_row_sha256':digest(r),**dict.fromkeys(FALSE,False)}
            if not r[prior.FLAG]:
                stopped+=1;row.update(reason=r['reason'],reason_provenance='unchanged_retained_STOP')
            else:
                enc=encode_geometry(snapshot,i);decoded=decode_geometry(snapshot,i,enc)
                trace=original.trace_original(decoded,i)
                trace['scope']='exact rational traversal/selector of CPU RN64-decoded hi-lo geometry; legacy ORIGINAL keys name decoded inputs here, not fixed ORIGINAL or native ray arithmetic'
                arg=original.argument_from_trace(trace)
                charge=compose(r['trace'],trace,arg,int(decoded['sources'][i]['direction'][0]),meta['original_path_phase_caps'][r['source_id']])
                row.update(encoder=enc,decoded_snapshot_digest=digest(decoded),decoded_trace=trace,decoded_argument=arg,composition=charge,**{FLAG:True},
                    phase_reference_id=ctx['assignments'][i]['source_phase_reference_id'],terminal_reference_id=ctx['assignments'][i]['terminal_reference_id'],
                    reason='decoded geometry point only; native traversal/uniform domain/material/full field admission STOP')
                executed+=1;scalars+=len(enc['records'])
            rows.append(row)
        cases[name]={'context':ctx,'sources':rows,**dict.fromkeys(FALSE,False)}
    return {'model':MODEL,'case_order':deepcopy(case_names),'cases':cases,'runtime_probe':probe,'inherited_pins_verified':len(pins),
        'decoded_geometry_sources_executed':executed,'retained_sources_not_executed':stopped,'coordinate_scalars_encoded':scalars,
        'new_RN32_casts':2*scalars,'new_RN64_subtractions':scalars,'new_RN64_decode_adds':scalars,
        'new_decoded_argument_casts':executed,'new_decoded_argument_multiplies':executed,
        'new_exact_decoded_root_records':8*executed,'new_Horner_SOURCE_material_reduction_power_readout_executions':0,
        'old_numeric_producers_reexecuted':0,'previous_SOURCE_eight_bit_FAILs_preserved':True,'previous_SOURCE_twelve_zero_sign_mismatches_preserved':True,
        'native_ray_arithmetic_executed':False,'uniform_geometry_backend_domain_admitted':False,
        'cost_scope':'main transport 2casts32+1sub64+1add64 per scalar, argument 1cast64+1mul64 per source; probes6ops64+4casts32; exact rational roots/projection/selector/pins/IO/setup/remaining costs UNMEASURED never zero',
        **dict.fromkeys(FALSE,False)}
