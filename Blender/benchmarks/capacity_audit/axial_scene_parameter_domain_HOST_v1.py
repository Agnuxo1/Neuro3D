"""Restricted axial shared-plane coordinate box -> retained parameter rectangle; HOST only."""
import base64,hashlib,math,struct
from fractions import Fraction as F
from copy import deepcopy
import axial_argument_rectangle_HOST_v1 as previous
import axial_source_budget_gate_HOST_v1 as io
import axial_amplitude_allocation_HOST_v1 as allocation
MODEL='axial-shared-plane-exactYZ-coordinate-domain-HOST-v1'
PREVIOUS='coordinacion/respuestas/AXIAL-ARGUMENT-RECTANGLE-HOST-001-CODEX.json'
PREVIOUS_SHA='b69da9b5a2e3492465edfcb8b8357647763afe90bae2af30fd514b424c946cf8'
FALSE=previous.FALSE+('general_3D_geometry_proved','physical_scene_uncertainty_certified')
SCALE=2**149
require=previous.require
pair=previous.pair
signed=previous.signed512

def decode32(w):
    require(type(w) is int and 0<=w<2**32,'strict uint32')
    e=(w>>23)&255;m=w&0x7fffff
    require(e<255 and (e!=0 or m==0),'normal-or-zero finite word; no FTZ')
    return (-1 if w>>31 else 1)*((m|0x800000)<<(e-1)) if e else 0

def hilo(words):
    require(type(words) is list and len(words)==2,'two hi-lo INPUT words')
    return sum(map(decode32,words))

def interval(words,radius):
    c=hilo(words);r=signed(radius);require(r>=0,'nonnegative frozen radius')
    return [c-r,c+r]

def scaled_original(value):
    require(type(value) is float and math.isfinite(value),'finite ORIGINAL binary64 float')
    x=F(*value.as_integer_ratio())*SCALE
    require(x.denominator==1,'ORIGINAL coordinate on retained grid')
    return x.numerator

def rational_interval(v):
    require(type(v) is list and len(v)==2,'two rational endpoints')
    out=[previous.fraction(x) for x in v];require(out[0]<=out[1],'ordered rational interval')
    return out

def domain_image(m,s,d,r,wavelength,*,direction_sign,model):
    """Mathematical shared-plane box; NOT caller-supplied scene evidence."""
    require(model==MODEL and type(direction_sign) is int and direction_sign in (-1,1),'explicit axial domain model/sign')
    m,s,d,r,w=map(rational_interval,(m,s,d,r,wavelength));require(w[0]>0,'strict positive wavelength')
    sign=direction_sign
    def linear(coeffs,intervals):
        ends=[sum(c*(a if c>=0 else b) for c,(a,b) in zip(coeffs,intervals)),
              sum(c*(b if c>=0 else a) for c,(a,b) in zip(coeffs,intervals))]
        return list(map(pair,ends))
    first=linear([sign,-sign],[m,s])
    other=linear([sign,-sign],[d,s])
    second=linear([sign,-sign],[m,d])
    plane_gap=linear([sign,-sign],[d,m])
    strict=F(*first[0])>0 and F(*second[0])>0
    nearest=(F(*other[1])<0 or F(*plane_gap[0])>0)
    return {'model':MODEL,'direction_sign':sign,'first_segment_interval':first,
            'initial_other_owner_interval':other,'second_segment_interval':second,
            'initial_competitor_minus_mirror_interval':plane_gap,
            'strict_positive_first_and_reflected_second':strict,
            'mirror_first_uniform_clearance':nearest,
            'restricted_shared_plane_selector_proved':strict and nearest,
            'geometric_length_interval':linear([2*sign,-sign,-sign],[m,s,d]),
            'reference_correction_interval':linear([sign,-sign],[d,r]),
            'effective_reference_length_interval':linear([2*sign,-sign,-sign],[m,s,r]),
            'wavelength_interval':list(map(pair,w)),
            'same_D_coefficient_in_total_reference':sign-sign,
            'skip_previous_owner_permitted_only_after_first_root':strict and nearest,
            'status':'PROVED_SHARED_PLANE_BOX_ONLY' if strict and nearest else 'STOP',
            'parameter_domain_only':True,**dict.fromkeys(FALSE,False)}

def projection(vertices,point):
    a,b,c=vertices
    cross=lambda x,y:x[0]*y[1]-x[1]*y[0]
    sub=lambda x,y:[x[0]-y[0],x[1]-y[1]]
    v,u,p=sub(b,a),sub(c,a),sub(point,a)
    det=cross(v,u)
    if det==0:return {'classification':'degenerate_FAIL','det_u_v_w_scaled':None}
    U,V=cross(p,u),cross(v,p)
    if det<0:det,U,V=-det,-U,-V
    W=det-U-V
    kind='miss' if min(U,V,W)<0 else ('boundary_FAIL' if min(U,V,W)==0 else 'strict_interior')
    return {'classification':kind,'det_u_v_w_scaled':[det,U,V,W]}

def derive_restricted_domain(packet,ctx,index,ref,b,geometry):
    """Internal pinned inputs only; fresh rational proof, no old selector/encoder run."""
    require(allocation.digest(packet)==ctx['input_packet_sha256'],'same INPUT packet')
    buffers={k:base64.b64decode(v,validate=True) for k,v in packet['buffers_base64'].items()}
    for k,raw in buffers.items():require(packet['manifest']['buffers'][k]=={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()},'buffer receipt')
    meta=allocation.parse(buffers['input_metadata_json']);snap=allocation.parse(buffers['original_scene_json'])
    require(meta['original_snapshot_sha256']==hashlib.sha256(buffers['original_scene_json']).hexdigest(),'ORIGINAL snapshot receipt')
    require(set(snap['objects'])=={'M','D'} and snap['undeclared_meshes']==[],'exact two-owner scene')
    require(meta['object_ids']==['M','D'] and meta['kinds']==['mirror','det'],'two-owner INPUT profile')
    require([s['id'] for s in snap['sources']]==ctx['source_order'],'same ordered ORIGINAL sources')
    def words(k):
        raw=buffers[k];require(len(raw)%4==0,'word alignment')
        return list(struct.unpack('<'+'I'*(len(raw)//4),raw))
    tw,sw,ww,rw=map(words,('triangles','sources','wavelength','reference'))
    require(len(tw)%35==0 and 1<=len(tw)//35<=64 and len(sw)==32*len(snap['sources'])
            and len(ww)==18 and len(rw)==31 and rw[0]==1,'frozen strides/reference present')
    expected=[]
    for owner,name in enumerate(('M','D')):
        obj=snap['objects'][name];require(obj['kind']==('mirror' if owner==0 else 'det'),'original owner kind')
        vertices=obj['vertices_world_BU']
        require(type(vertices) is list and 3<=len(vertices)<=192 and all(type(v) is list and len(v)==3 for v in vertices),'bounded ORIGINAL vertices')
        require(all(scaled_original(v[0])==scaled_original(vertices[0][0]) for v in vertices),'one shared ORIGINAL X variable across ALL owner faces')
        for face in obj['faces']:
            require(type(face) is list and len(face)==3 and len(set(face))==3
                    and all(type(j) is int and 0<=j<len(vertices) for j in face),'triangle topology')
            expected.append((owner,[vertices[j] for j in face]))
    require(len(expected)==len(tw)//35,'all original triangles represented')
    planes={};records=[];src=snap['sources'][index];source=sw[32*index:32*(index+1)]
    point=[hilo(source[j:j+2]) for j in (2,4)]
    require(point==[scaled_original(src['position_BU'][j]) for j in (1,2)],'exact ORIGINAL source YZ, not radius surrogate')
    dirs=[hilo(source[j:j+2]) for j in (6,8,10)]
    require(dirs[0] in (-SCALE,SCALE) and dirs[1:]==[0,0],'exact encoded axial unit direction')
    sign=1 if dirs[0]>0 else -1
    require([scaled_original(x) for x in src['direction']]==[sign*SCALE,0,0],'same ORIGINAL axial direction')
    for pid,(owner,vertices) in enumerate(expected):
        row=tw[35*pid:35*(pid+1)];require(row[0]==owner,'triangle owner/order')
        xs=[hilo(row[j:j+2]) for j in (1,7,13)]
        p=interval(row[1:3],row[19:35]);require(xs==[xs[0]]*3,'same X across triangle')
        require(owner not in planes or planes[owner]==p,'single shared X variable per owner')
        planes[owner]=p;yz=[]
        for j,v in zip((1,7,13),vertices):
            original=[scaled_original(x) for x in v]
            require(p[0]<=original[0]<=p[1],'ORIGINAL plane X inside unchanged radius')
            require(original[0]==scaled_original(vertices[0][0]),'shared ORIGINAL plane')
            encoded=[hilo(row[j+2:j+4]),hilo(row[j+4:j+6])]
            require(encoded==original[1:],'exact ORIGINAL triangle YZ')
            yz.append(encoded)
        records.append({'primitive_id':pid,'owner':owner,**projection(yz,point)})
    require(set(planes)=={0,1},'both complete planes')
    require(all(v['classification'] in ('miss','strict_interior') for v in records),'no boundary/degenerate projection')
    interior=[v for v in records if v['classification']=='strict_interior']
    require([v['owner'] for v in interior]==[0,1],'unique strictly interior triangle per owner')
    source_interval=interval(source[:2],source[12:28])
    original_s=scaled_original(src['position_BU'][0])
    require(source_interval[0]<=original_s<=source_interval[1],'ORIGINAL source X inside unchanged radius')
    reference_interval=interval(rw[13:15],rw[15:31]);wave=interval(ww[:2],ww[2:])
    original_r=scaled_original(snap['objects']['D']['mode_origin_BU'][0])
    original_w=scaled_original(snap['lambda_BU'])
    require(reference_interval[0]<=original_r<=reference_interval[1] and wave[0]<=original_w<=wave[1] and wave[0]>0,'ORIGINAL reference/wavelength inside frozen intervals')
    require([scaled_original(x) for x in snap['objects']['D']['mode_direction']]==[-sign*SCALE,0,0],'ORIGINAL reflected mode')
    require(meta['reference']['frame']=='fixed original world point; ideal unit-X plane-wave mode','fixed reference frame')
    require([previous.decode((rw[j+1]<<32)|rw[j])*SCALE for j in (7,9,11)]==[-sign*SCALE,0,0],'transported ORIGINAL mode bits')
    require([previous.decode((rw[j+1]<<32)|rw[j])*SCALE for j in (1,3,5)]
            ==[scaled_original(x) for x in snap['objects']['D']['mode_origin_BU']],'transported ORIGINAL reference point bits')
    domain={'M':planes[0],'S':source_interval,'D':planes[1],'R':reference_interval,'wavelength':wave}
    original={'M':scaled_original(snap['objects']['M']['vertices_world_BU'][0][0]),
              'S':original_s,'D':scaled_original(snap['objects']['D']['vertices_world_BU'][0][0]),
              'R':original_r,'wavelength':original_w}
    proof=domain_image(*[[pair(F(v)) for v in domain[k]] for k in ('M','S','D','R','wavelength')],direction_sign=sign,model=MODEL)
    require(proof['restricted_shared_plane_selector_proved'],'uniform first/reflected roots with strictly positive clearance')
    require(geometry['direction_sign']==sign,'same retained incident direction')
    require([v['primitive_id'] for v in interior]==[v['primitive_id'] for v in geometry['segments']],'same retained two hits')
    require(proof['first_segment_interval']==[pair(F(signed(x))) for x in geometry['segments'][0]['segment_interval_words']]
            and proof['second_segment_interval']==[pair(F(signed(x))) for x in geometry['segments'][1]['segment_interval_words']],'same retained segment bounds')
    for key in ('geometric_length_interval','reference_correction_interval','effective_reference_length_interval','wavelength_interval'):
        require(proof[key]==[pair(F(signed(x))) for x in ref[key+'_words']],'same retained interval '+key)
    require(proof['effective_reference_length_interval']==b['length_interval'] and proof['wavelength_interval']==b['wavelength_interval'],'exact parameter rectangle target')
    OL=sign*(2*original['M']-original['S']-original['R'])
    require(b['ORIGINAL_length']==pair(F(OL)) and b['ORIGINAL_wavelength']==pair(F(original_w)),'same fixed ORIGINAL reference length and wavelength')
    return {'coordinate_intervals_scaled_BU':domain,'ORIGINAL_coordinates_scaled_BU':original,
            'fixed_YZ_projection_checks':records,'uniform_affine_selector_proof':proof,
            'coordinate_domain':'shared owner X translations within INPUT radii; source/reference/wavelength intervals; fixed EXACT original YZ; axial directions',
            'ORIGINAL_inside_coordinate_box':True,'restricted_coordinate_box_to_parameter_rectangle_proved':True,
            'all_shared_plane_X_within_box_selector_proved':True,'radii_enlarged':False,
            'new_RN_encodings_or_old_producers_reexecuted':0,**dict.fromkeys(FALSE,False)}

def load_retained():
    r=allocation.parse(io.read(PREVIOUS,PREVIOUS_SHA));require(r['task_id']=='AXIAL-ARGUMENT-RECTANGLE-HOST-001','previous task')
    pins=io.pins_from(r);pins[PREVIOUS]=PREVIOUS_SHA
    for p,h in pins.items():io.read(p,h)
    old=io.payload(r)['data']['audit']
    argument=io.payload(allocation.parse(io.read(previous.ARGUMENT,pins[previous.ARGUMENT])))['cases']
    packets=io.payload(allocation.parse(io.read(io.INGRESS,pins[io.INGRESS])))['packets']
    controls=io.payload(allocation.parse(io.read(io.PRESENCE,pins[io.PRESENCE])))['synthetic_controls']
    packets.update({n:c['parent'] for n,c in controls.items()})
    return packets,old,argument,pins

def audit_scene_parameter_domain_HOST(case_names,*,model):
    require(model==MODEL,'explicit restricted scene domain model')
    require(type(case_names) is list and 1<=len(case_names)<=64 and all(type(n) is str and n for n in case_names)
            and len(set(case_names))==len(case_names),'bounded unique cases')
    packets,old,argument,pins=load_retained();require(set(case_names)<=set(packets),'known cases')
    out={};proved=stops=0
    for n in case_names:
        ctx=allocation.context_from_packet(packets[n],allocation.digest(packets[n]),model=allocation.MODEL)
        require(ctx==old['cases'][n]['context'],'same fresh ORIGINAL INPUT context')
        rows=[]
        for i,s in enumerate(old['cases'][n]['sources']):
            row={'source_id':s['source_id'],'retained_argument_rectangle_source_sha256':allocation.digest(s),
                 'retained_rectangle_evaluated':s['rectangle_evaluated'],
                 'retained_partial_unit_phase_pass':s['retained_partial_unit_phase_pass'],
                 'retained_unit_polynomial_charge_fits':s['retained_unit_polynomial_charge_fits'],
                 'restricted_coordinate_box_to_parameter_rectangle_proved':False,**dict.fromkeys(FALSE,False)}
            if not s['rectangle_evaluated']:
                row.update(status='STOP',reason=s['reason'],reason_provenance='unchanged_retained_unit_STOP');stops+=1
            else:
                ref=argument[n]['upstream']['upstream']['sources'][i]['reference']
                proof=derive_restricted_domain(packets[n],ctx,i,ref,s['parameter_branch'],ref['geometry'])
                row.update(restricted_domain_proof=proof,restricted_coordinate_box_to_parameter_rectangle_proved=True,
                           unchanged_original_phase_cap_rad=deepcopy(s['unchanged_original_phase_cap_rad']),
                           retained_parameter_phase_fits_unchanged_cap=s['uniform_parameter_phase_alone_fits_unchanged_cap'],
                           status='STOP',reason='restricted coordinate domain and ORIGINAL linked; source/reduction/full pipeline not proved',
                           reason_provenance='restricted_domain_only_not_full_pipeline');proved+=1
            rows.append(row)
        require([s['source_id'] for s in rows]==ctx['source_order'],'complete ordered sources')
        out[n]={'context':ctx,'sources':rows,**dict.fromkeys(FALSE,False)}
    return {'model':MODEL,'case_order':list(case_names),'cases':out,'inherited_pins_verified':len(pins),
            'restricted_coordinate_domains_proved':proved,'retained_unit_STOPs':stops,
            'new_RN_encodings_or_old_producers_reexecuted':0,**dict.fromkeys(FALSE,False)}
