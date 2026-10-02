import struct
"""Independent integer IEEE RN64 oracle; no production imports or float arithmetic replay."""
import base64,hashlib,json,math,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT='coordinacion/respuestas/AXIAL-GEOMETRY-HILO-CPU-001-CODEX.json'
PREVIOUS='coordinacion/respuestas/AXIAL-ORIGINAL-SOURCE-CPU-001-CODEX.json'
PREVIOUS_SHA='a9a894bc3f2749f750aba78714ec31d1bb2cbd6a77c2bf862dfedfd565ccf162'
FLAG='decoded_geometry_point_CPU_executed'
SOURCE_FLAG='restricted_nonzero_bare_source_error_to_fixed_ORIGINAL_bound_proved'
MODEL='axial-geometry-hilo32-RN64-decode-rational-traversal-CPU-v1'
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

def round32(q,zero_sign):
    if q==0:return zero_sign
    sign=(1<<31) if q<0 else 0;n,d=abs(q.numerator),q.denominator
    e=n.bit_length()-d.bit_length()
    if (n<d<<e if e>=0 else n<<-e<d):e-=1
    assert e<=127
    grid=max(e,-126)-23
    nn,dd=(n,d<<grid) if grid>=0 else (n<<-grid,d)
    m,rem=divmod(nn,dd);m+=int(2*rem>dd or (2*rem==dd and m&1))
    if m==0:return sign
    if e<-126:
        assert m<=2**23;return sign|m
    if m==2**24:m>>=1;e+=1
    assert e<=127 and 2**23<=m<2**24
    return sign|((e+127)<<23)|(m-2**23)


def word(v):return struct.unpack('<Q',struct.pack('<d',v))[0]
def verify_scalar(t,w):
    q=bits(w);hw=round32(q,(w>>32)&(1<<31))
    residual,rexact=operation(w,lift32(hw)^SIGN,'add')
    lw=round32(bits(residual),(residual>>32)&(1<<31))
    dec,decexact=operation(lift32(hw),lift32(lw),'add')
    expected={'original_uint64':w,'high_uint32':hw,'residual_uint64':residual,'low_uint32':lw,'decoded_uint64':dec,
        'residual_RN64_delta':pair(bits(residual)-rexact),'represented_exact_sum':pair(decexact),
        'encoding_error_abs':pair(abs(decexact-q)),'decode_RN64_delta':pair(bits(dec)-decexact),
        'decoded_coordinate_error_abs':pair(abs(bits(dec)-q))}
    assert t==expected
    return dec,hw,lw

def get(obj,path):
    for k in path:obj=obj[k]
    return obj
def put(obj,path,value):
    for k in path[:-1]:obj=obj[k]
    obj[path[-1]]=value
def expected_paths(snapshot,index):
    ps=[]
    for name in ('M','D'):
        ps.extend([['objects',name,'vertices_world_BU',j,k] for j in range(len(snapshot['objects'][name]['vertices_world_BU'])) for k in range(3)])
    ps.extend([['sources',index,key,k] for key in ('position_BU','direction') for k in range(3)])
    ps.extend([['objects','D',key,k] for key in ('mode_origin_BU','mode_direction') for k in range(3)])
    return ps+[['lambda_BU'],['objects','M','phase_rad']]
def decode(snapshot,index,enc):
    ps=expected_paths(snapshot,index);assert len(ps)==38
    assert enc['source_index']==index and enc['original_snapshot_digest']==digest(snapshot)
    assert enc['ordered_paths_sha256']==digest(ps) and [t['path'] for t in enc['records']]==ps
    dec=json.loads(json.dumps(snapshot));limbs=[]
    for p,t in zip(ps,enc['records']):
        s={k:v for k,v in t.items() if k!='path'}
        w,h,l=verify_scalar(s,word(get(snapshot,p)));limbs.extend((h,l))
        put(dec,p,struct.unpack('<d',struct.pack('<Q',w))[0])
    raw=struct.pack('<'+'I'*len(limbs),*limbs)
    assert enc['transport_bytes']==len(raw)==304
    assert enc['transport_le_sha256']==sha(raw) and enc['transport_le_base64']==base64.b64encode(raw).decode()
    assert enc['new_RN32_casts']==76 and enc['new_RN64_subtractions']==enc['new_RN64_decode_adds']==38
    return dec
def verify_charges(c,ot,dt,arg,sign,cap):
    o={k:rational(v) for k,v in ot['ORIGINAL_coordinates_BU'].items()}
    d={k:rational(v) for k,v in dt['ORIGINAL_coordinates_BU'].items()}
    e={k:abs(d[k]-o[k]) for k in o}
    geo=2*e['M']+e['S']+e['D'];ref=e['D']+e['R'];eff=2*e['M']+e['S']+e['R']
    assert c['coordinate_errors_BU']=={k:pair(v) for k,v in e.items()}
    assert c['geometry_length_bound_BU']==pair(geo) and c['reference_correction_bound_BU']==pair(ref)
    assert c['uncorrelated_effective_bound_BU']==pair(geo+ref) and c['correlated_effective_bound_BU']==pair(eff)
    assert c['wavelength_error_BU']==pair(e['wavelength'])
    for key,charge,limit in [('geometric_length_BU','observed_geometry_delta_BU',geo),('reference_correction_BU','observed_reference_delta_BU',ref),('effective_reference_length_BU','observed_effective_delta_BU',eff)]:
        observed=abs(rational(dt[key])-rational(ot[key]));assert c[charge]==pair(observed) and observed<=limit
    cycles=eff/d['wavelength']+abs(rational(ot['effective_reference_length_BU']))*e['wavelength']/(d['wavelength']*o['wavelength'])
    observed=abs(rational(dt['exact_ORIGINAL_cycles'])-rational(ot['exact_ORIGINAL_cycles']))
    assert c['cycles_bound']==pair(cycles) and c['observed_cycles_delta']==pair(observed) and observed<=cycles
    phase=2*PI_HI*cycles;total=phase+rational(arg['phase_error_bound_rad'])
    assert c['geometry_reference_wavelength_phase_bound_rad']==pair(phase)
    assert c['decoded_argument_RN64_bound_rad']==arg['phase_error_bound_rad']
    assert c['point_argument_to_fixed_ORIGINAL_phase_bound_rad']==pair(total)
    assert c['unchanged_phase_cap_rad']==cap==[1,10**12]
    assert c['point_charge_fits_unchanged_cap'] is (total<=rational(cap)) and 0<total<=rational(cap)
    assert c['shared_D_cancellation_identity_checked'] is True
    assert c['first_root_BU']==dt['hits'][0]['segment_BU'] and c['first_root_positive'] is True
    assert [(h['primitive_id'],h['owner']) for h in ot['hits']]==[(h['primitive_id'],h['owner']) for h in dt['hits']]
    assert ot['quarter_index']==dt['quarter_index']
    for trace,v in ((ot,o),(dt,d)):
        assert rational(trace['geometric_length_BU'])==sign*(2*v['M']-v['S']-v['D'])
        assert rational(trace['reference_correction_BU'])==sign*(v['D']-v['R'])
        assert rational(trace['effective_reference_length_BU'])==sign*(2*v['M']-v['S']-v['R'])
    return float(total)
def allfalse(v):
    for k in false:assert v[k] is False,k

r=json.loads((ROOT/REPORT).read_bytes());assert r['task_id']=='AXIAL-GEOMETRY-HILO-CPU-001'
assert r['inherited_pin_source']=={'path':PREVIOUS,'sha256':PREVIOUS_SHA}
pins=pins_from(r);assert len(pins)==337 and len(r['own_code_doc_sha256'])==4
for p,h in pins.items():assert sha((ROOT/p).read_bytes())==h,p
previous=read(PREVIOUS,PREVIOUS_SHA);false=tuple(previous['proof_scope']);allfalse(r['proof_scope'])
old=payload(previous)['data']['audit']
def data(p):return payload(read(p,pins[p]))
legacy=data('coordinacion/respuestas/AXIAL-SOURCE-FLOAT64-STAGE-CPU-001-CODEX.json')['data']['audit']
assert legacy['point_graphs_bits_FAIL']==8 and legacy['point_graphs_bits_MATCH']==0
assert sum(n['zero_sign_only_mismatch'] for c in legacy['cases'].values() for s in c['sources'] for p in s.get('points',[]) for n in p['nodes'])==12
packets=data('coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json')['packets']
packets.update({n:v['parent'] for n,v in data('coordinacion/respuestas/AXIAL-NATIVE-PRESENCE-STOPS-001-CODEX.json')['synthetic_controls'].items()})
raw=payload(r);assert raw['PASS'] is True and raw['tests']==4
t=r['test_run'];assert t['threads']==t['affinity_mask']==1 and t['hard_child_timeout_seconds']==60 and t['elapsed_seconds']<60 and not t['timed_out']
a=raw['data']['audit'];allfalse(a);assert a['model']==MODEL
assert a['case_order']==old['case_order'] and len(a['cases'])==17
assert a['runtime_probe']==old['runtime_probe'] and a['runtime_probe']['PASS'] is True
ex=stop=scalars=roots=0;bounds={}
for name in a['case_order']:
    c=a['cases'][name];allfalse(c);ctx=c['context'];p=packets[name]
    assert ctx==old['cases'][name]['context'] and digest(p)==ctx['input_packet_sha256']
    buffers={k:base64.b64decode(v,validate=True) for k,v in p['buffers_base64'].items()}
    for k,b in buffers.items():assert p['manifest']['buffers'][k]=={'bytes':len(b),'sha256':sha(b)}
    assert sha(buffers['original_scene_json'])==ctx['original_snapshot_sha256']
    snap=json.loads(buffers['original_scene_json']);meta=json.loads(buffers['input_metadata_json'])
    assert meta['explicit_group_contract']['assignments']==ctx['assignments']
    assert [s['id'] for s in snap['sources']]==ctx['source_order']==[s['source_id'] for s in c['sources']]
    for i,(row,prior) in enumerate(zip(c['sources'],old['cases'][name]['sources'])):
        allfalse(row);assert row['status']=='STOP' and row['retained_source_row_sha256']==digest(prior)
        if not prior['fresh_ORIGINAL_bare_source_prefix_CPU_executed']:
            stop+=1;assert row[FLAG] is False and 'encoder' not in row
            assert row['reason']==prior['reason'] and row['reason_provenance']=='unchanged_retained_STOP';continue
        assert row[FLAG] is True
        verify_fresh_scene(snap,i,prior['trace'],prior['argument'])
        dec=decode(snap,i,row['encoder']);assert digest(dec)==row['decoded_snapshot_digest']
        gap,_=verify_fresh_scene(dec,i,row['decoded_trace'],row['decoded_argument'])
        if name=='thin_resolved':assert gap==F(1,2**30)
        assert 'decoded' in row['decoded_trace']['scope'] and 'not fixed ORIGINAL' in row['decoded_trace']['scope']
        bounds[name]=verify_charges(row['composition'],prior['trace'],row['decoded_trace'],row['decoded_argument'],int(original(dec['sources'][i]['direction'][0])),meta['original_path_phase_caps'][row['source_id']])
        assert row['phase_reference_id']==ctx['assignments'][i]['source_phase_reference_id']
        assert row['terminal_reference_id']==ctx['assignments'][i]['terminal_reference_id']
        ex+=1;scalars+=len(row['encoder']['records']);roots+=len(row['decoded_trace']['root_projection_records'])
assert (ex,stop,scalars,roots)==(2,17,76,16)
assert set(bounds)=={'thin_resolved','nonexact_geometry_phase_PASS'}
assert a['inherited_pins_verified']==333 and a['decoded_geometry_sources_executed']==2
assert a['retained_sources_not_executed']==17 and a['coordinate_scalars_encoded']==76
assert a['new_RN32_casts']==152 and a['new_RN64_subtractions']==a['new_RN64_decode_adds']==76
assert a['new_decoded_argument_casts']==a['new_decoded_argument_multiplies']==2 and a['new_exact_decoded_root_records']==16
assert a['new_Horner_SOURCE_material_reduction_power_readout_executions']==a['old_numeric_producers_reexecuted']==0
assert a['previous_SOURCE_eight_bit_FAILs_preserved'] is a['previous_SOURCE_twelve_zero_sign_mismatches_preserved'] is True
assert a['native_ray_arithmetic_executed'] is a['uniform_geometry_backend_domain_admitted'] is False
for control in raw['data']['scalar_controls']:verify_scalar(control,control['original_uint64'])
assert len(raw['data']['scalar_controls'])==4
rejects=raw['data']['rejections'];assert len(rejects)==len({v['label'] for v in rejects})==27
print(json.dumps({'PASS':True,'pins':337,'decoded_sources':ex,'retained_sources_not_executed':stop,
    'geometry_scalars_checked':scalars,'RN32_casts_checked':152,'RN64_sub_decode_checked':152,
    'exact_decoded_root_records_checked':roots,'thin_gap_BU':[1,2**30],'point_phase_bounds_rad':bounds,
    'rejections':27,'scalar_controls_checked':4,'legacy_8_FAIL_12_signs_preserved':True,
    'native_ray_GPU_full_pipeline_admitted':False},sort_keys=True))
