import struct
"""Independent integer IEEE RN64 oracle; no production imports or float arithmetic replay."""
import base64,hashlib,json,math,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT='coordinacion/respuestas/AXIAL-ORIGINAL-ARGUMENT-CPU-001-CODEX.json'
PREVIOUS='coordinacion/respuestas/AXIAL-UNIT-FLOAT64-STAGE-CPU-001-CODEX.json'
PREVIOUS_SHA='9b25175d86ac779714d66063fd3ed837bc44dd1cf986931f98c3c510454a450e'
FLAG='ORIGINAL_scene_selector_argument_CPU_executed'
SOURCE_FLAG='restricted_nonzero_bare_source_error_to_fixed_ORIGINAL_bound_proved'
MODEL='axial-ORIGINAL-exact-scene-selector-RN64-argument-CPU-v1'
LABELS=['decode0','decode1','ac','bd','ad','bc','real','imag']
SIGN=2**63
def sha(raw):return hashlib.sha256(raw).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def read(path,h):
    raw=(ROOT/path).read_bytes();assert sha(raw)==h,path;return json.loads(raw)
def pins_from(r):
    if 'code_doc_sha256' in r:return dict(r['code_doc_sha256'])
    d=r['inherited_pin_source'];p=pins_from(read(d['path'],d['sha256']))
    p[d['path']]=d['sha256'];p.update(r['own_code_doc_sha256']);return p
def payload(r):
    t=r['test_run'];assert t['rc']==0
    b=zlib.decompress(base64.b64decode(t.get('stdout_zlib_base64') or ''.join(t['stdout_zlib_base64_chunks']),validate=True))
    assert len(b)==t['stdout_bytes'] and sha(b)==t['stdout_sha256'];return json.loads(b)
def pair(q):return [q.numerator,q.denominator]
def rational(v):
    assert type(v) is list and len(v)==2 and all(type(x) is int for x in v)
    assert v[1]>0 and math.gcd(*v)==1;return F(*v)
def bits(w):
    assert type(w) is int and 0<=w<2**64
    e=(w>>52)%2048;m=w%2**52;assert e<2047
    return (-1 if w&SIGN else 1)*F(m if e==0 else m+2**52)*F(2)**((1 if e==0 else e)-1075)
def lift32(w):
    assert type(w) is int and 0<=w<2**32
    sign=(w>>31)<<63;e=(w>>23)%256;m=w%2**23
    assert e<255 and (e or m==0)
    return sign if e==0 else sign|((e+896)<<52)|(m<<29)
def round64(q,zero_sign):
    if q==0:return zero_sign
    sign=SIGN if q<0 else 0;n,d=abs(q.numerator),q.denominator
    e=n.bit_length()-d.bit_length()
    if (n<d<<e if e>=0 else n<<-e<d):e-=1
    assert e<=1023
    grid=max(e,-1022)-52
    nn,dd=(n,d<<grid) if grid>=0 else (n<<-grid,d)
    m,rem=divmod(nn,dd);m+=int(2*rem>dd or (2*rem==dd and m&1))
    if m==0:return sign
    if e<-1022:
        assert m<=2**52
        return sign|m  # m==2^52 correctly reaches smallest normal
    if m==2**53:m>>=1;e+=1
    assert e<=1023 and 2**52<=m<2**53
    return sign|((e+1023)<<52)|(m-2**52)
def operation(x,y,kind):
    a,b=bits(x),bits(y);q=a*b if kind=='mul' else a+b
    if kind=='mul':zs=(x^y)&SIGN
    else:zs=SIGN if a==b==0 and x&SIGN and y&SIGN else 0
    return round64(q,zs),q

PI_LO=F('3.14159265358979323846264338327950288419716939937510')
PI_HI=F('3.14159265358979323846264338327950288419716939937511')
TWO_PI=0x401921fb54442d18
def original(v):
    assert type(v) is float
    word=struct.unpack('<Q',struct.pack('<d',v))[0]
    return bits(word)

def verify_fresh_scene(snapshot,index,trace,arg):
    source=snapshot['sources'][index];sxyz=list(map(original,source['position_BU']))
    dxyz=list(map(original,source['direction']));sign=int(dxyz[0])
    assert dxyz==[sign,0,0] and sign in (-1,1)
    assert set(snapshot['objects'])=={'M','D'} and snapshot['undeclared_meshes']==[]
    planes={};triangles=[];pid=0
    for owner,name in enumerate(('M','D')):
        obj=snapshot['objects'][name];assert obj['kind']==('mirror' if owner==0 else 'det')
        vertices=[list(map(original,v)) for v in obj['vertices_world_BU']]
        assert len({v[0] for v in vertices})==1;planes[name]=vertices[0][0]
        for face in obj['faces']:
            triangles.append((pid,owner,[vertices[j] for j in face]));pid+=1
    assert original(snapshot['objects']['M']['phase_rad'])==0
    ref=list(map(original,snapshot['objects']['D']['mode_origin_BU']))
    assert list(map(original,snapshot['objects']['D']['mode_direction']))==[-sign,0,0]
    wavelength=original(snapshot['lambda_BU']);assert wavelength>0
    records=trace['root_projection_records'];assert len(records)==2*len(triangles)
    hits=[];origin=sxyz[0];direction=sign
    for step in (0,1):
        forward=[]
        for j,(primitive,owner,xyz) in enumerate(triangles):
            row=records[step*len(triangles)+j]
            root=direction*(xyz[0][0]-origin)
            assert row['step']==step and row['primitive_id']==primitive and row['owner']==owner
            assert rational(row['root_BU'])==root
            if step==1 and owner==0:
                assert root==0 and row['classification']=='previous_owner_zero_root_excluded'
                continue
            ay,az=xyz[0][1:];by,bz=xyz[1][1:];cy,cz=xyz[2][1:];py,pz=sxyz[1:]
            uy,uz=by-ay,bz-az;vy,vz=cy-ay,cz-az;dy,dz=py-ay,pz-az
            determinant=uy*vz-uz*vy
            assert determinant!=0
            bary1=(dy*vz-dz*vy)/determinant
            bary2=(uy*dz-uz*dy)/determinant
            bary3=1-bary1-bary2
            det=abs(determinant);ds=[det,det*bary1,det*bary2,det*bary3]
            assert row['det_U_V_W']==list(map(pair,ds))
            kind='miss' if min(bary1,bary2,bary3)<0 else ('boundary_FAIL' if min(bary1,bary2,bary3)==0 else 'strict_interior')
            assert row['classification']==kind and kind!='boundary_FAIL'
            if kind=='strict_interior':
                assert root!=0
                if root>0:forward.append((root,primitive,owner))
        assert forward;nearest=min(forward)
        assert sum(v[0]==nearest[0] for v in forward)==1 and nearest[2]==step
        root,primitive,owner=nearest
        expected={'primitive_id':primitive,'owner':owner,'segment_BU':pair(root)}
        assert trace['hits'][step]==expected;hits.append(root)
        origin=planes['M' if step==0 else 'D'];direction=-direction
    expected_coords={'M':planes['M'],'S':sxyz[0],'D':planes['D'],'R':ref[0],'wavelength':wavelength}
    assert trace['ORIGINAL_coordinates_BU']=={key:pair(v) for key,v in expected_coords.items()}
    length=sum(hits,F(0));correction=sign*(planes['D']-ref[0])
    effective=sign*(2*planes['M']-sxyz[0]-ref[0])
    assert effective==length+correction>0
    assert trace['geometric_length_BU']==pair(length) and trace['reference_correction_BU']==pair(correction)
    assert trace['effective_reference_length_BU']==pair(effective) and trace['wavelength_BU']==pair(wavelength)
    q=effective/wavelength
    k=(8*q.numerator+q.denominator)//(2*q.denominator)
    r=F(4*q.numerator-k*q.denominator,4*q.denominator)
    assert abs(r)<F(1,8)
    assert trace['exact_ORIGINAL_cycles']==pair(q) and trace['quarter_index']==k
    assert trace['quadrant_mod4']==k%4 and trace['residual_cycles']==pair(r)
    assert trace['geometry_reference_rounding_error_BU']==[0,1]
    residual=round64(r,0);argument,exact=operation(residual,TWO_PI,'mul')
    assert arg['residual_uint64']==residual and arg['TWO_PI_uint64']==TWO_PI and arg['argument_uint64']==argument
    assert arg['multiply_input_uint64']==[residual,TWO_PI]
    assert rational(arg['multiply_rounding_delta_rad'])==bits(argument)-exact
    charges={'residual_conversion_rad':2*PI_HI*abs(bits(residual)-r),
       'constant_2pi_rad':abs(r)*max(abs(bits(TWO_PI)-2*PI_LO),abs(bits(TWO_PI)-2*PI_HI)),
       'multiply_RN64_rad':abs(bits(argument)-exact)}
    assert arg['phase_error_charges_rad']=={key:pair(v) for key,v in charges.items()}
    assert rational(arg['phase_error_bound_rad'])==sum(charges.values(),F(0))
    assert arg['new_CPU_float64_casts']==arg['new_CPU_float64_multiplies']==1
    assert arg['retained_argument_or_result_substitution'] is False
    return hits[0],sum(charges.values(),F(0))

def allfalse(v):
    for key in false:assert v[key] is False,key

r=json.loads((ROOT/REPORT).read_bytes());assert r['task_id']=='AXIAL-ORIGINAL-ARGUMENT-CPU-001'
assert r['inherited_pin_source']=={'path':PREVIOUS,'sha256':PREVIOUS_SHA}
pins=pins_from(r);assert len(pins)==322 and len(r['own_code_doc_sha256'])==4
for path,h in pins.items():assert sha((ROOT/path).read_bytes())==h,path
previous=read(PREVIOUS,PREVIOUS_SHA);false=tuple(previous['proof_scope']);allfalse(r['proof_scope'])
old=payload(previous)['data']['audit']
def data(path):return payload(read(path,pins[path]))
source_prior=data('coordinacion/respuestas/AXIAL-SOURCE-FLOAT64-STAGE-CPU-001-CODEX.json')['data']['audit']
assert source_prior['point_graphs_bits_FAIL']==8 and source_prior['point_graphs_bits_MATCH']==0
assert sum(n['zero_sign_only_mismatch'] for c in source_prior['cases'].values() for s in c['sources'] for p in s.get('points',[]) for n in p['nodes'])==12
domain=data('coordinacion/respuestas/AXIAL-SCENE-PARAMETER-DOMAIN-HOST-001-CODEX.json')['data']['audit']
packets=data('coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json')['packets']
packets.update({n:v['parent'] for n,v in data('coordinacion/respuestas/AXIAL-NATIVE-PRESENCE-STOPS-001-CODEX.json')['synthetic_controls'].items()})
raw=payload(r);assert raw['PASS'] is True and raw['tests']==4
t=r['test_run'];assert t['threads']==t['affinity_mask']==1 and t['hard_child_timeout_seconds']==60 and t['elapsed_seconds']<60 and not t['timed_out']
a=raw['data']['audit'];allfalse(a)
assert a['model']==MODEL and a['case_order']==old['case_order'] and len(a['cases'])==17
assert a['runtime_probe']==old['runtime_probe'] and a['runtime_probe']['PASS'] is True
executed=stopped=records=0;found=[]
for name in a['case_order']:
    case=a['cases'][name];allfalse(case);ctx=case['context'];packet=packets[name]
    assert ctx==old['cases'][name]['context']==domain['cases'][name]['context']
    assert digest(packet)==ctx['input_packet_sha256']
    buffers={key:base64.b64decode(v,validate=True) for key,v in packet['buffers_base64'].items()}
    for key,b in buffers.items():assert packet['manifest']['buffers'][key]=={'bytes':len(b),'sha256':sha(b)}
    assert sha(buffers['original_scene_json'])==ctx['original_snapshot_sha256']
    snapshot=json.loads(buffers['original_scene_json']);meta=json.loads(buffers['input_metadata_json'])
    assert meta['explicit_group_contract']['assignments']==ctx['assignments']
    assert [s['id'] for s in snapshot['sources']]==ctx['source_order']==[s['source_id'] for s in case['sources']]
    olds=old['cases'][name]['sources'];ds=domain['cases'][name]['sources']
    for i,(row,prior,d) in enumerate(zip(case['sources'],olds,ds)):
        allfalse(row);assert row['status']=='STOP' and row['retained_domain_row_sha256']==digest(d)
        if not prior['CPU_float64_Horner26_fixture_executed']:
            stopped+=1;assert row[FLAG] is False and 'trace' not in row
            assert row['reason']==prior['reason'] and row['reason_provenance']=='unchanged_retained_stage_STOP';continue
        assert row[FLAG] is True and d['restricted_coordinate_box_to_parameter_rectangle_proved'] is True
        gap,bound=verify_fresh_scene(snapshot,i,row['trace'],row['argument'])
        proof=d['restricted_domain_proof']
        assert {key:rational(v)*2**149 for key,v in row['trace']['ORIGINAL_coordinates_BU'].items()}==proof['ORIGINAL_coordinates_scaled_BU']
        assert [h['primitive_id'] for h in row['trace']['hits']]==[v['primitive_id'] for v in proof['fixed_YZ_projection_checks'] if v['classification']=='strict_interior']
        cap=meta['original_path_phase_caps'][row['source_id']]
        assert row['unchanged_phase_cap_rad']==d['unchanged_original_phase_cap_rad']==cap==[1,10**12]
        assert row['point_reference_argument_charge_fits_unchanged_cap'] is (bound<=rational(cap))
        assert bound<=rational(cap) and gap>0
        assert row['phase_reference_id']==ctx['assignments'][i]['source_phase_reference_id']
        assert row['terminal_reference_id']==ctx['assignments'][i]['terminal_reference_id']
        executed+=1;records+=len(row['trace']['root_projection_records']);found.append(name)
assert (executed,stopped,records)==(2,17,16) and set(found)=={'thin_resolved','nonexact_geometry_phase_PASS'}
assert a['inherited_pins_verified']==318 and a['fresh_ORIGINAL_sources_executed']==executed
assert a['retained_sources_not_executed']==stopped and a['new_CPU_float64_casts']==a['new_CPU_float64_multiplies']==executed
assert a['new_exact_geometry_reference_selector_sources']==executed
assert a['new_Horner_SOURCE_material_reduction_executions']==a['old_numeric_producers_reexecuted']==0
assert a['encoded_hi_lo_backend_executed'] is False and a['uniform_backend_domain_admitted'] is False
assert a['previous_SOURCE_eight_bit_FAILs_preserved'] is True
control=raw['data']['thin_positive_root_control']
snap=json.loads(base64.b64decode(packets['thin_resolved']['buffers_base64']['original_scene_json']))
gap,bound=verify_fresh_scene(snap,0,control['trace'],control['argument'])
assert rational(control['exact_gap_BU'])==gap>0
rejects=raw['data']['rejections'];assert len(rejects)==len({v['label'] for v in rejects})==26
print(json.dumps({'PASS':True,'pins':len(pins),'fresh_ORIGINAL_sources':executed,
 'retained_sources_not_executed':stopped,'root_projection_records_checked':records,
 'RN64_casts_and_multiplies_checked':4,'thin_positive_ORIGINAL_root_preserved':True,
 'synthetic_control_root_records_checked':8,'phase_charge_fits_UNCHANGED_caps':True,
 'previous_SOURCE_8_bit_FAILs_preserved':True,'rejections':len(rejects),
 'encoded_hi_lo_backend_executed':False,'uniform_backend_domain_admission':'STOP','GPU_executed':False},sort_keys=True))
