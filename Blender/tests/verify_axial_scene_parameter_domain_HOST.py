"""Independent restricted-domain oracle: stdlib only, no production imports or RN replay."""
import base64,hashlib,itertools,json,math,struct,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT='coordinacion/respuestas/AXIAL-SCENE-PARAMETER-DOMAIN-HOST-001-CODEX.json'
MODEL='axial-shared-plane-exactYZ-coordinate-domain-HOST-v1'
SCALE=2**149
FALSE=('scene_argument_enclosed','uniform_unit_error_to_ORIGINAL_proved','uniform_source_error_proved',
       'accepted_full_field_pipeline','remaining_stages_error_proved','execution_authenticated',
       'coherence_authenticated','native_kernel_implemented','GPU_executed','GPU_job_admission',
       'whole_scene_parameter_enclosure_proved','native_argument_implemented','general_3D_geometry_proved',
       'physical_scene_uncertainty_certified')
def canon(v):return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def sha(v):return hashlib.sha256(v).hexdigest()
def digest(v):return sha(canon(v))
def read(p,h):
    raw=(ROOT/p).read_bytes();assert sha(raw)==h,p;return json.loads(raw)
def payload(r):
    t=r['test_run'];assert t['rc']==0
    raw=zlib.decompress(base64.b64decode(t.get('stdout_zlib_base64') or ''.join(t['stdout_zlib_base64_chunks']),validate=True))
    assert len(raw)==t['stdout_bytes'] and sha(raw)==t['stdout_sha256'];return json.loads(raw)
def pins_from(r):
    if 'code_doc_sha256' in r:return dict(r['code_doc_sha256'])
    d=r['inherited_pin_source'];p=pins_from(read(d['path'],d['sha256']))
    p[d['path']]=d['sha256'];p.update(r['own_code_doc_sha256']);return p
def pair(v):return [v.numerator,v.denominator]
def rat(v):
    assert type(v) is list and len(v)==2 and all(type(n) is int for n in v)
    assert v[1]>0 and math.gcd(*v)==1;return F(*v)
def signed(w):
    assert type(w) is list and len(w)==16 and all(type(x) is int and 0<=x<2**32 for x in w)
    x=sum(t*2**(32*i) for i,t in enumerate(w));return x-2**512 if x>=2**511 else x
def binary(word,bits):
    assert type(word) is int and 0<=word<2**bits
    fraction_bits,bias=(23,127) if bits==32 else (52,1023)
    exponent_bits=bits-fraction_bits-1;e=(word>>fraction_bits)&(2**exponent_bits-1)
    m=word%(2**fraction_bits);assert e<2**exponent_bits-1
    if bits==32:assert e!=0 or m==0
    x=F(m+(2**fraction_bits if e else 0))*F(2)**((e if e else 1)-bias-fraction_bits)
    return -x if word>>(bits-1) else x
def hilo(w):
    x=sum(binary(v,32) for v in w)*SCALE;assert x.denominator==1;return x.numerator
def interval(w,r):
    center=hilo(w);radius=signed(r);assert radius>=0;return [center-radius,center+radius]
def original(v):
    assert type(v) is float and math.isfinite(v)
    x=F.from_float(v)*SCALE;assert x.denominator==1;return x.numerator
def false(v):
    for k in FALSE:assert v[k] is False,k
def context(packet):
    roles={'triangles','sources','wavelength','reference','original_scene_json','input_metadata_json'}
    assert set(packet['buffers_base64'])==set(packet['manifest']['buffers'])==roles
    b={k:base64.b64decode(v,validate=True) for k,v in packet['buffers_base64'].items()}
    for k,v in b.items():assert packet['manifest']['buffers'][k]=={'bytes':len(v),'sha256':sha(v)}
    m=json.loads(b['input_metadata_json']);s=json.loads(b['original_scene_json']);g=m['explicit_group_contract']
    assert m['original_snapshot_sha256']==sha(b['original_scene_json'])
    assert m['source_order']==[v['id'] for v in s['sources']]
    assert m['case_name']==packet['manifest']['case_name'] and g['scene_binding_sha256']==m['scene_binding_sha256']
    assert [v['source_id'] for v in g['assignments']]==m['source_order']
    groups=[]
    for v in g['assignments']:
        assert v['source_phase_reference_id']=='original-source-zero:'+m['scene_binding_sha256']+':'+v['source_id']
        assert v['terminal_reference_id']==v['common_terminal_reference_id']=='fixed-original-plane-mode:'+m['scene_binding_sha256']+':D'
        assert v['rebase_cycles']==[0,1]
        key=[v['port'],v['coherence_group']]
        if key not in groups:groups.append(key)
    return {'model':'axial-static-amplitude-L1-allocation-HOST-v1','units':'ORIGINAL-source-field-amplitude-L1',
            'case_name':m['case_name'],'input_packet_sha256':digest(packet),'scene_binding_sha256':m['scene_binding_sha256'],
            'word_ABI_sha256':m['word_ABI_sha256'],'original_snapshot_sha256':m['original_snapshot_sha256'],
            'original_group_contract_sha256':digest(g),'source_order':m['source_order'],'assignments':g['assignments'],
            'groups':groups,'unchanged_field_L1_cap':g['limits']['field_L1'],'unchanged_limits':g['limits'],
            'grouping_provenance':g['grouping_provenance'],'execution_authenticated':False,'coherence_authenticated':False},b,m,s
def projection(vertices,p):
    a,b,c=vertices
    area=lambda u,v:u[0]*v[1]-u[1]*v[0]
    sub=lambda u,v:[u[0]-v[0],u[1]-v[1]]
    det=area(sub(b,a),sub(c,a))
    if det==0:return {'classification':'degenerate_FAIL','det_u_v_w_scaled':None}
    sg=1 if det>0 else -1
    A,B,C=[sub(v,p) for v in vertices]
    W,U,V=[sg*area(u,v) for u,v in ((B,C),(C,A),(A,B))]
    kind='miss' if min(U,V,W)<0 else ('boundary_FAIL' if min(U,V,W)==0 else 'strict_interior')
    assert U+V+W==abs(det)
    return {'classification':kind,'det_u_v_w_scaled':[abs(det),U,V,W]}
def affine(proof,inputs):
    false(proof);sg=inputs['sign'];assert type(sg) is int and sg in (-1,1)
    assert proof['model']==MODEL and proof['direction_sign']==sg and proof['parameter_domain_only'] is True
    domains={k:list(map(rat,inputs[k])) for k in ('M','S','D','R','wavelength')}
    assert all(len(v)==2 and v[0]<=v[1] for v in domains.values()) and domains['wavelength'][0]>0
    # Exact affine extrema: every coordinate endpoint combination; NOT RN-error sampling.
    corners=[]
    for M,S,D,R,W in itertools.product(*(domains[k] for k in ('M','S','D','R','wavelength'))):
        corners.append((sg*(M-S),sg*(D-S),sg*(M-D),sg*(D-M),sg*(2*M-S-D),sg*(D-R),sg*(2*M-S-R),W))
    keys=('first_segment_interval','initial_other_owner_interval','second_segment_interval',
          'initial_competitor_minus_mirror_interval','geometric_length_interval','reference_correction_interval',
          'effective_reference_length_interval','wavelength_interval')
    for i,key in enumerate(keys):
        assert proof[key]==[pair(min(v[i] for v in corners)),pair(max(v[i] for v in corners))]
    strict=min(v[0] for v in corners)>0 and min(v[2] for v in corners)>0
    nearest=max(v[1] for v in corners)<0 or min(v[3] for v in corners)>0
    assert proof['strict_positive_first_and_reflected_second']==strict
    assert proof['mirror_first_uniform_clearance']==nearest
    assert proof['restricted_shared_plane_selector_proved']==proof['skip_previous_owner_permitted_only_after_first_root']==(strict and nearest)
    assert proof['same_D_coefficient_in_total_reference']==0
    assert proof['status']==('PROVED_SHARED_PLANE_BOX_ONLY' if strict and nearest else 'STOP')
    return len(corners)
def scene(proof,packet,index,ref,b):
    ctx,buffers,meta,snap=context(packet)
    assert set(snap['objects'])=={'M','D'} and snap['undeclared_meshes']==[]
    assert meta['object_ids']==['M','D'] and meta['kinds']==['mirror','det']
    words=lambda k:list(struct.unpack('<'+'I'*(len(buffers[k])//4),buffers[k]))
    tw,sw,ww,rw=map(words,('triangles','sources','wavelength','reference'))
    assert len(tw)%35==0 and len(sw)==32*len(ctx['source_order']) and len(ww)==18 and len(rw)==31 and rw[0]==1
    faces=[]
    for owner,name in enumerate(('M','D')):
        o=snap['objects'][name];vs=o['vertices_world_BU'];assert o['kind']==('mirror' if owner==0 else 'det')
        assert all(original(v[0])==original(vs[0][0]) for v in vs)
        for face in o['faces']:
            assert len(face)==len(set(face))==3 and all(type(j) is int and 0<=j<len(vs) for j in face)
            faces.append((owner,[vs[j] for j in face]))
    assert len(faces)==len(tw)//35
    src=snap['sources'][index];sw=sw[32*index:32*(index+1)]
    sign=1 if hilo(sw[6:8])>0 else -1
    assert [hilo(sw[j:j+2]) for j in (6,8,10)]==[sign*SCALE,0,0]
    assert [original(v) for v in src['direction']]==[sign*SCALE,0,0]
    point=[hilo(sw[j:j+2]) for j in (2,4)];assert point==[original(v) for v in src['position_BU'][1:]]
    planes={};records=[];checks=0
    for pid,(owner,vertices) in enumerate(faces):
        row=tw[35*pid:35*(pid+1)];assert row[0]==owner
        xs=[hilo(row[j:j+2]) for j in (1,7,13)];assert xs==[xs[0]]*3
        iv=interval(row[1:3],row[19:35]);assert owner not in planes or planes[owner]==iv;planes[owner]=iv
        yz=[]
        for j,v in zip((1,7,13),vertices):
            v=list(map(original,v));assert iv[0]<=v[0]<=iv[1];checks+=1
            y=[hilo(row[j+2:j+4]),hilo(row[j+4:j+6])];assert y==v[1:];checks+=2;yz.append(y)
        records.append({'primitive_id':pid,'owner':owner,**projection(yz,point)})
    assert set(planes)=={0,1};assert all(v['classification'] in ('strict_interior','miss') for v in records)
    active=[v for v in records if v['classification']=='strict_interior'];assert [v['owner'] for v in active]==[0,1]
    assert proof['fixed_YZ_projection_checks']==records
    domain={'M':planes[0],'D':planes[1],'S':interval(sw[:2],sw[12:28]),'R':interval(rw[13:15],rw[15:]),'wavelength':interval(ww[:2],ww[2:])}
    O={'M':original(snap['objects']['M']['vertices_world_BU'][0][0]),'D':original(snap['objects']['D']['vertices_world_BU'][0][0]),
       'S':original(src['position_BU'][0]),'R':original(snap['objects']['D']['mode_origin_BU'][0]),'wavelength':original(snap['lambda_BU'])}
    assert all(domain[k][0]<=O[k]<=domain[k][1] for k in O);checks+=5
    assert proof['coordinate_intervals_scaled_BU']==domain and proof['ORIGINAL_coordinates_scaled_BU']==O
    assert [original(v) for v in snap['objects']['D']['mode_direction']]==[-sign*SCALE,0,0]
    assert [binary((rw[j+1]<<32)|rw[j],64)*SCALE for j in (7,9,11)]==[-sign*SCALE,0,0]
    assert [binary((rw[j+1]<<32)|rw[j],64)*SCALE for j in (1,3,5)]==[original(v) for v in snap['objects']['D']['mode_origin_BU']]
    assert meta['reference']['frame']=='fixed original world point; ideal unit-X plane-wave mode'
    p=proof['uniform_affine_selector_proof']
    corners=affine(p,{**{k:[pair(F(x)) for x in v] for k,v in domain.items()},'sign':sign})
    assert p['restricted_shared_plane_selector_proved'] is True
    geometry=ref['geometry'];assert geometry['direction_sign']==sign
    assert [v['primitive_id'] for v in active]==[v['primitive_id'] for v in geometry['segments']]
    for key in ('geometric_length_interval','reference_correction_interval','effective_reference_length_interval','wavelength_interval'):
        assert p[key]==[pair(F(signed(x))) for x in ref[key+'_words']]
    assert p['first_segment_interval']==[pair(F(signed(x))) for x in geometry['segments'][0]['segment_interval_words']]
    assert p['second_segment_interval']==[pair(F(signed(x))) for x in geometry['segments'][1]['segment_interval_words']]
    assert p['effective_reference_length_interval']==b['length_interval'] and p['wavelength_interval']==b['wavelength_interval']
    assert b['ORIGINAL_length']==pair(F(sign*(2*O['M']-O['S']-O['R'])))
    assert b['ORIGINAL_wavelength']==pair(F(O['wavelength']))
    assert proof['ORIGINAL_inside_coordinate_box'] is True and proof['restricted_coordinate_box_to_parameter_rectangle_proved'] is True
    assert proof['all_shared_plane_X_within_box_selector_proved'] is True and proof['radii_enlarged'] is False
    assert proof['new_RN_encodings_or_old_producers_reexecuted']==0;false(proof)
    return checks,len(records),corners

r=json.loads((ROOT/REPORT).read_bytes());assert r['task_id']=='AXIAL-SCENE-PARAMETER-DOMAIN-HOST-001'
pins=pins_from(r);assert len(pins)==267
for p,h in pins.items():assert sha((ROOT/p).read_bytes())==h,p
d=payload(r);assert d['PASS'] is True and d['tests']==6;d=d['data'];a=d['audit']
old=payload(read(r['inherited_pin_source']['path'],r['inherited_pin_source']['sha256']))['data']['audit']
arg='coordinacion/respuestas/AXIAL-NATIVE-ARGUMENT-HOST-001-CODEX.json'
argument=payload(read(arg,pins[arg]))['cases']
ingress='coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json'
presence='coordinacion/respuestas/AXIAL-NATIVE-PRESENCE-STOPS-001-CODEX.json'
packets=payload(read(ingress,pins[ingress]))['packets']
packets.update({n:v['parent'] for n,v in payload(read(presence,pins[presence]))['synthetic_controls'].items()})
assert a['model']==MODEL and a['inherited_pins_verified']==263 and set(a['cases'])==set(old['cases'])==set(packets)
assert len(a['case_order'])==len(set(a['case_order']))==17 and set(a['case_order'])==set(packets)
assert a['new_RN_encodings_or_old_producers_reexecuted']==0;false(a)
count=stops=checks=projections=corners=0
for n,c in a['cases'].items():
    ctx,_,meta,_=context(packets[n]);assert c['context']==old['cases'][n]['context']==ctx;false(c)
    assert len(c['sources'])==len(ctx['source_order'])
    for i,(s,o) in enumerate(zip(c['sources'],old['cases'][n]['sources'])):
        assert s['source_id']==o['source_id']==ctx['source_order'][i]
        assert s['retained_argument_rectangle_source_sha256']==digest(o)
        assert s['retained_rectangle_evaluated']==s['restricted_coordinate_box_to_parameter_rectangle_proved']==o['rectangle_evaluated']
        assert s['retained_unit_polynomial_charge_fits']==o['retained_unit_polynomial_charge_fits']
        assert s['retained_partial_unit_phase_pass']==o['retained_partial_unit_phase_pass']
        assert s['status']=='STOP';false(s)
        if not s['restricted_coordinate_box_to_parameter_rectangle_proved']:
            stops+=1;assert s['reason']==o['reason'] and 'restricted_domain_proof' not in s
        else:
            count+=1;ref=argument[n]['upstream']['upstream']['sources'][i]['reference']
            x,y,z=scene(s['restricted_domain_proof'],packets[n],i,ref,o['parameter_branch'])
            checks+=x;projections+=y;corners+=z
            assert s['unchanged_original_phase_cap_rad']==o['unchanged_original_phase_cap_rad']==meta['original_path_phase_caps'][s['source_id']]
            assert s['retained_parameter_phase_fits_unchanged_cap']==o['uniform_parameter_phase_alone_fits_unchanged_cap']
            assert s['reason_provenance']=='restricted_domain_only_not_full_pipeline'
assert count==a['restricted_coordinate_domains_proved']==5 and stops==a['retained_unit_STOPs']==14
assert len(d['primitives'])==7
for v in d['primitives']:corners+=affine(v['proof'],v['inputs'])
assert len(d['projection_controls'])==4
for v in d['projection_controls']:assert v['proof']==projection(v['vertices'],v['point'])
assert len(d['rejections'])==32 and len({v['label'] for v in d['rejections']})==32
assert any(v['label']=='mutated_ORIGINALnonshared_face' for v in d['rejections'])
assert r['proof_scope']['general_3D_geometry_proved'] is False and r['proof_scope']['physical_scene_uncertainty_certified'] is False
print(json.dumps({'PASS':True,'pins':len(pins),'restricted_coordinate_domains':count,'retained_unit_STOPs':stops,
                  'ORIGINAL_word_containment_and_exactYZ_checks':checks,'fresh_YZ_projection_checks':projections,
                  'affine_endpoint_combinations_not_RN_evaluations':corners,'synthetic_projection_controls':4,
                  'rejections':32,'old_producer_or_RN_reexecution':0,'general_3D_geometry_proved':False},sort_keys=True))
