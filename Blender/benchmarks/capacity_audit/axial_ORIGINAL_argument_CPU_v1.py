"""Opt-in fresh ORIGINAL axial scene reference/selector/argument CPU; not native."""
import base64,hashlib,math
from copy import deepcopy
from fractions import Fraction as F
import axial_unit_float64_stage_CPU_v1 as prior
from scene_field_producer_cpu_v1 import PI_LOWER,PI_UPPER
io=prior.io
allocation=prior.allocation
require=prior.require
digest=prior.digest
MODEL='axial-ORIGINAL-exact-scene-selector-RN64-argument-CPU-v1'
PREVIOUS='coordinacion/respuestas/AXIAL-UNIT-FLOAT64-STAGE-CPU-001-CODEX.json'
PREVIOUS_SHA='9b25175d86ac779714d66063fd3ed837bc44dd1cf986931f98c3c510454a450e'
DOMAIN='coordinacion/respuestas/AXIAL-SCENE-PARAMETER-DOMAIN-HOST-001-CODEX.json'
FALSE=prior.FALSE
FLAG='ORIGINAL_scene_selector_argument_CPU_executed'
TWO_PI=0x401921fb54442d18
pair=lambda q:[q.numerator,q.denominator]

def load_retained():
    receipt=allocation.parse(io.read(PREVIOUS,PREVIOUS_SHA))
    require(receipt['task_id']=='AXIAL-UNIT-FLOAT64-STAGE-CPU-001','previous task identity')
    pins=io.pins_from(receipt);pins[PREVIOUS]=PREVIOUS_SHA
    for path,h in pins.items():io.read(path,h)
    def data(path):return io.payload(allocation.parse(io.read(path,pins[path])))
    previous=io.payload(receipt)['data']['audit'];domain=data(DOMAIN)['data']['audit']
    packets=data(io.INGRESS)['packets']
    packets.update({n:v['parent'] for n,v in data(io.PRESENCE)['synthetic_controls'].items()})
    require(set(packets)==set(previous['cases'])==set(domain['cases']),'complete cases')
    return packets,previous,domain,pins

def number(v):
    require(type(v) is float and math.isfinite(v),'finite ORIGINAL binary64 float')
    q=F.from_float(v);require(q==0 or F(1,2**1022)<=abs(q)<=F(2**1023),'bounded normal-or-zero ORIGINAL')
    return q

def snapshot_from_packet(packet,ctx):
    require(ctx==allocation.context_from_packet(packet,digest(packet),model=allocation.MODEL),'fresh complete INPUT context')
    buffers={k:base64.b64decode(v,validate=True) for k,v in packet['buffers_base64'].items()}
    for key,raw in buffers.items():require(packet['manifest']['buffers'][key]=={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()},'buffer receipt')
    require(hashlib.sha256(buffers['original_scene_json']).hexdigest()==ctx['original_snapshot_sha256'],'ORIGINAL snapshot SHA')
    snap=allocation.parse(buffers['original_scene_json']);meta=allocation.parse(buffers['input_metadata_json'])
    require([s['id'] for s in snap['sources']]==ctx['source_order'],'complete original source order')
    require(meta['explicit_group_contract']['assignments']==ctx['assignments'],'complete assignments')
    return snap,meta

def trace_original(snapshot,index):
    """New exact rational CPU reference from ORIGINAL bits, not encoded geometry replay."""
    require(type(index) is int and 0<=index<len(snapshot['sources']),'source index')
    require(set(snapshot['objects'])=={'M','D'} and snapshot['undeclared_meshes']==[],'two-owner declared scene only')
    src=snapshot['sources'][index];position=list(map(number,src['position_BU']))
    direction=list(map(number,src['direction']))
    require(len(position)==len(direction)==3 and direction[0] in (-1,1) and direction[1:]==[0,0],'exact axial unit direction')
    sign=int(direction[0]);triangles=[];planes={};pid=0
    for owner,name in enumerate(('M','D')):
        obj=snapshot['objects'][name];require(obj['kind']==('mirror' if owner==0 else 'det'),'owner kind')
        vertices=obj['vertices_world_BU']
        require(type(vertices) is list and 3<=len(vertices)<=192 and all(type(v) is list and len(v)==3 for v in vertices),'bounded vertex layout')
        vertices=[list(map(number,v)) for v in vertices]
        require(all(v[0]==vertices[0][0] for v in vertices),'shared axial plane')
        planes[name]=vertices[0][0]
        require(type(obj['faces']) is list and 1<=len(obj['faces'])<=64,'bounded faces')
        for face in obj['faces']:
            require(type(face) is list and len(face)==3 and len(set(face))==3
                    and all(type(i) is int and 0<=i<len(vertices) for i in face),'triangle topology')
            triangles.append((pid,owner,[vertices[i] for i in face]));pid+=1
    require(len(triangles)<=64,'bounded total primitives')
    require(number(snapshot['objects']['M']['phase_rad'])==0,'mirror phase zero; material not evaluated')
    detector=snapshot['objects']['D'];ref=list(map(number,detector['mode_origin_BU']))
    require(len(ref)==3 and list(map(number,detector['mode_direction']))==[-sign,0,0],'same reflected fixed reference direction')
    wavelength=number(snapshot['lambda_BU']);require(wavelength>0,'positive wavelength')
    records=[];hits=[];length=F(0);origin=position[0];direction=sign;previous_owner=None
    for step,expected_owner in enumerate((0,1)):
        candidates=[]
        for primitive,owner,vertices in triangles:
            root=(vertices[0][0]-origin)*direction
            if previous_owner==owner:
                require(step==1 and root==0,'skip previous owner only at reflected zero root')
                records.append({'step':step,'primitive_id':primitive,'owner':owner,'root_BU':pair(root),'classification':'previous_owner_zero_root_excluded'});continue
            a,b,c=[[v[1],v[2]] for v in vertices];point=position[1:]
            cross=lambda p,q:p[0]*q[1]-p[1]*q[0]
            sub=lambda p,q:[p[0]-q[0],p[1]-q[1]]
            u,v,p=sub(b,a),sub(c,a),sub(point,a)
            det=cross(u,v);require(det!=0,'degenerate projection STOP')
            U,V=cross(p,v),cross(u,p)
            if det<0:det,U,V=-det,-U,-V
            W=det-U-V
            kind='miss' if min(U,V,W)<0 else ('boundary_FAIL' if min(U,V,W)==0 else 'strict_interior')
            records.append({'step':step,'primitive_id':primitive,'owner':owner,'root_BU':pair(root),
                'classification':kind,'det_U_V_W':[pair(q) for q in (det,U,V,W)]})
            if kind=='miss':continue
            require(kind!='boundary_FAIL','boundary contact STOP')
            require(root!=0,'self/contact root zero STOP')
            if root>0:candidates.append((root,primitive,owner))
        require(candidates,'no forward interior hit')
        candidates.sort();first=candidates[0]
        require(sum(c[0]==first[0] for c in candidates)==1,'nearest tie STOP')
        root,primitive,owner=first;require(owner==expected_owner,'unexpected nearest owner STOP')
        hits.append({'primitive_id':primitive,'owner':owner,'segment_BU':pair(root)})
        length+=root;origin=planes['M' if owner==0 else 'D'];previous_owner=owner;direction=-direction
    correction=sign*(planes['D']-ref[0]);effective=length+correction
    require(effective>0,'positive effective length')
    q=effective/wavelength;k=(4*q+F(1,2))//1;r=q-F(k,4)
    require(abs(r)<F(1,8),'quarter branch boundary STOP')
    return {'source_id':src['id'],'hits':hits,'root_projection_records':records,
       'ORIGINAL_coordinates_BU':{name:pair(v) for name,v in {'M':planes['M'],'S':position[0],'D':planes['D'],'R':ref[0],'wavelength':wavelength}.items()},
       'geometric_length_BU':pair(length),'reference_correction_BU':pair(correction),
       'effective_reference_length_BU':pair(effective),'wavelength_BU':pair(wavelength),
       'exact_ORIGINAL_cycles':pair(q),'quarter_index':k,'quadrant_mod4':k%4,'residual_cycles':pair(r),
       'geometry_reference_rounding_error_BU':[0,1],'scope':'new exact rational CPU ORIGINAL reference, not decoded hi-lo or native ray traversal'}

def argument_from_trace(trace):
    r=F(*trace['residual_cycles']);require(abs(r)<F(1,8),'strict quarter residual')
    x=float(r);require(math.isfinite(x),'finite conversion')
    encoded=prior.source.word(x);require(x==0 or abs(x)>=math.ldexp(1.0,-1022),'selected subnormal conversion STOP')
    pi=prior.source.value(TWO_PI,64);angle=x*pi
    require(math.isfinite(angle) and (angle==0 or abs(angle)>=math.ldexp(1.0,-1022)),'selected nonnormal argument STOP')
    out=prior.source.word(angle);represented=F.from_float(x);constant=F.from_float(pi);actual=F.from_float(angle)
    charges={'residual_conversion_rad':2*PI_UPPER*abs(represented-r),
             'constant_2pi_rad':abs(r)*max(abs(constant-2*PI_LOWER),abs(constant-2*PI_UPPER)),
             'multiply_RN64_rad':abs(actual-represented*constant)}
    error=sum(charges.values(),F(0))
    return {'residual_uint64':encoded,'TWO_PI_uint64':TWO_PI,'argument_uint64':out,
       'multiply_input_uint64':[encoded,TWO_PI],'multiply_rounding_delta_rad':pair(actual-represented*constant),
       'phase_error_charges_rad':{name:pair(q) for name,q in charges.items()},
       'phase_error_bound_rad':pair(error),'new_CPU_float64_casts':1,'new_CPU_float64_multiplies':1,
       'retained_argument_or_result_substitution':False}

def audit_ORIGINAL_argument_CPU(case_names,*,model):
    require(model==MODEL,'explicit CPU ORIGINAL reference model')
    require(type(case_names) is list and 1<=len(case_names)<=64 and all(type(n) is str and n for n in case_names)
        and len(set(case_names))==len(case_names),'bounded unique cases')
    packets,previous,domain,pins=load_retained();require(set(case_names)<=set(packets),'known cases')
    probe=prior.source.runtime_probe();require(probe['PASS'] is True,'runtime probe FAIL; no argument execution')
    cases={};executed=stopped=0
    for name in case_names:
        ctx=allocation.context_from_packet(packets[name],digest(packets[name]),model=allocation.MODEL)
        require(ctx==previous['cases'][name]['context']==domain['cases'][name]['context'],'same fresh INPUT')
        snapshot,meta=snapshot_from_packet(packets[name],ctx)
        cs=previous['cases'][name]['sources'];ds=domain['cases'][name]['sources']
        require([s['source_id'] for s in cs]==[s['source_id'] for s in ds]==ctx['source_order'],'complete ordered sources')
        rows=[]
        for i,(old,d) in enumerate(zip(cs,ds)):
            row={'source_id':old['source_id'],'status':'STOP',FLAG:False,'retained_domain_row_sha256':digest(d),**dict.fromkeys(FALSE,False)}
            if not old[prior.FLAG]:
                stopped+=1;row.update(reason=old['reason'],reason_provenance='unchanged_retained_stage_STOP')
            else:
                require(d['restricted_coordinate_box_to_parameter_rectangle_proved'] is True,'retained stable original domain')
                result=trace_original(snapshot,i);arg=argument_from_trace(result)
                proof=d['restricted_domain_proof'];scale=2**149
                require({key:F(*v)*scale for key,v in result['ORIGINAL_coordinates_BU'].items()}==proof['ORIGINAL_coordinates_scaled_BU'],'same ORIGINAL coordinates, not nominal centers')
                require([v['primitive_id'] for v in result['hits']]==[v['primitive_id'] for v in proof['fixed_YZ_projection_checks'] if v['classification']=='strict_interior'],'same exact retained roots')
                cap=meta['original_path_phase_caps'][old['source_id']]
                require(cap==d['unchanged_original_phase_cap_rad'],'same source phase cap')
                fits=F(*arg['phase_error_bound_rad'])<=F(*cap);executed+=1
                row.update(trace=result,argument=arg,phase_reference_id=ctx['assignments'][i]['source_phase_reference_id'],
                    terminal_reference_id=ctx['assignments'][i]['terminal_reference_id'],unchanged_phase_cap_rad=cap,
                    point_reference_argument_charge_fits_unchanged_cap=fits,**{FLAG:True},
                    reason='fresh exact ORIGINAL reference/argument only; no encoded backend, Horner/source chain, material, allocations or full pipeline')
            rows.append(row)
        cases[name]={'context':ctx,'sources':rows,**dict.fromkeys(FALSE,False)}
    return {'model':MODEL,'case_order':deepcopy(case_names),'cases':cases,'runtime_probe':probe,
       'inherited_pins_verified':len(pins),'fresh_ORIGINAL_sources_executed':executed,'retained_sources_not_executed':stopped,
       'new_CPU_float64_casts':executed,'new_CPU_float64_multiplies':executed,
       'new_exact_geometry_reference_selector_sources':executed,'new_Horner_SOURCE_material_reduction_executions':0,
       'old_numeric_producers_reexecuted':0,'previous_SOURCE_eight_bit_FAILs_preserved':True,
       'encoded_hi_lo_backend_executed':False,'uniform_backend_domain_admitted':False,
       'cost_scope':'exact rational geometry/ref/quotient-selector CPU work present but unmeasured; one RN64 cast+mul per source, six probes; snapshot/pins/context/setup/remaining costs UNMEASURED never zero',
       **dict.fromkeys(FALSE,False)}
