"""Independent stdlib IEEE/YZ/root interval/length oracle; no production imports."""
import base64,hashlib,json,math,struct,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT='coordinacion/respuestas/AXIAL-GUARDED-HILO-XROOT-RN64-CPU-001-CODEX.json'
PREVIOUS='coordinacion/respuestas/AXIAL-XROOT-SELECTOR-RN64-CPU-001-CODEX.json'
PREVIOUS_SHA='3174f3d340f0e06692430e619dccc9852189f001221061b73bec2733bdcb7d4b'
PIHI=F(314159265358979323846264338327950288419716939937511,10**50)
SIGN=1<<63
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(x):return sha(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def read(p,h):
    b=(ROOT/p).read_bytes();assert sha(b)==h,p;return json.loads(b)
def pins_from(r):
    if 'code_doc_sha256' in r:return dict(r['code_doc_sha256'])
    d=r['inherited_pin_source'];p=pins_from(read(d['path'],d['sha256']))
    p[d['path']]=d['sha256'];p.update(r['own_code_doc_sha256']);return p
def payload(r):
    t=r['test_run'];assert t['rc']==0
    if 'timed_out' in t:assert t['timed_out'] is False
    b=zlib.decompress(base64.b64decode(t.get('stdout_zlib_base64') or ''.join(t['stdout_zlib_base64_chunks']),validate=True))
    assert len(b)==t['stdout_bytes'] and sha(b)==t['stdout_sha256'];return json.loads(b)
def q(x):
    assert type(x) is list and len(x)==2 and all(type(a) is int for a in x)
    assert x[1]>0 and math.gcd(*x)==1;return F(*x)
def pair(x):return [x.numerator,x.denominator]
def word(v):return struct.unpack('<Q',struct.pack('<d',v))[0]
def bits(w,normal=True):
    assert type(w) is int and 0<=w<2**64
    sign=-1 if w&SIGN else 1;exp=(w>>52)&2047;mant=w&((1<<52)-1)
    assert exp!=2047 and (not normal or exp!=0 or mant==0)
    return sign*F(mant if exp==0 else mant+(1<<52))*F(2)**((1 if exp==0 else exp)-1075)
def cell(w):
    v=bits(w);mag=w%SIGN
    if mag==0:return [-F(1,2**1075),F(1,2**1075)]
    assert mag<0x7fefffffffffffff
    left=(bits(mag-1,False)+abs(v))/2;right=(abs(v)+bits(mag+1,False))/2
    return [-right,-left] if v<0 else [left,right]
def check_node(n):
    ins=n['input_uint64'];op=n['operation'];a=bits(ins[0]);aw=ins[0]
    if op=='negate':
        assert len(ins)==1;exact=-a;sign=1-(aw>>63)
        assert n['output_uint64']==(aw^SIGN)
    else:
        assert len(ins)==2 and op in ('subtract','add');b=bits(ins[1])
        exact=a-b if op=='subtract' else a+b
        sign=int(a==b==0 and aw>>63==1 and ins[1]>>63==(0 if op=='subtract' else 1))
    ow=n['output_uint64'];v=bits(ow);lo,hi=cell(ow)
    if exact==0:assert ow==sign*SIGN
    else:
        assert v!=0 and ((ow>>63)==int(exact<0))
        assert lo<exact<hi or (ow%2==0 and exact in (lo,hi))
    assert q(n['exact_operation_BU'])==exact and q(n['signed_rounding_delta_BU'])==v-exact
    assert n['rounding_cell_BU']==[pair(lo),pair(hi)]
    radius=max(v-lo,hi-v);assert q(n['radius_BU'])==radius
    return radius
def check_root(r):
    assert type(r['direction']) is int and r['direction'] in (-1,1)
    p,o=r['plane_uint64'],r['origin_uint64'];ns=r['nodes'];s=r['direction']
    assert ns[0]['operation']=='subtract' and ns[0]['input_uint64']==[p,o];rad=check_node(ns[0])
    interval=[q(x) for x in ns[0]['rounding_cell_BU']]
    if s<0:
        assert len(ns)==2 and ns[1]['operation']=='negate' and ns[1]['input_uint64']==[ns[0]['output_uint64']]
        check_node(ns[1]);interval=[-interval[1],-interval[0]]
    else:assert len(ns)==1
    assert r['root_uint64']==ns[-1]['output_uint64']
    assert q(r['exact_root_BU'])==(bits(p)-bits(o))*s
    assert r['root_interval_BU']==[pair(x) for x in interval] and q(r['rounding_radius_BU'])==rad
    return rad
def choose(rs,owner):
    hits=[]
    for r in rs:
        if r['classification'] in ('miss','previous_owner_zero_root_excluded'):continue
        assert r['classification']=='strict_interior'
        lo,hi=map(q,r['root']['root_interval_BU']);assert lo<=hi
        if hi<0:continue
        assert lo>0;hits.append(r)
    assert hits
    win=min(hits,key=lambda r:q(r['root']['root_interval_BU'][1]))
    assert all(r is win or q(win['root']['root_interval_BU'][1])<q(r['root']['root_interval_BU'][0]) for r in hits)
    assert win['owner']==owner;return win
def cross(u,v):return u[0]*v[1]-u[1]*v[0]
def minus(u,v):return [u[0]-v[0],u[1]-v[1]]
def verify_scene(res,snap,i):
    src=snap['sources'][i];sign=int(src['direction'][0]);position=src['position_BU'];point=[bits(word(v)) for v in position[1:]]
    assert src['direction']==[float(sign),0.0,0.0] and sign in (-1,1)
    planes=[snap['objects'][n]['vertices_world_BU'][0][0] for n in ('M','D')]
    origin=position[0];prev=None;chosen=[];nodes=[];counts=0
    ref=res['fixed_ORIGINAL_reference'];exact_length=F(0)
    for step,rs in enumerate(res['steps']):
        pid=0;expected=[]
        for owner,name in enumerate(('M','D')):
            obj=snap['objects'][name];assert obj['kind']==('mirror' if owner==0 else 'det')
            verts=[[bits(word(v)) for v in t] for t in obj['vertices_world_BU']]
            assert all(v[0]==bits(word(planes[owner])) for v in verts)
            for face in obj['faces']:
                assert len(face)==len(set(face))==3;vs=[verts[j] for j in face]
                r=rs[pid];assert [r['step'],r['primitive_id'],r['owner']]==[step,pid,owner]
                rr=r['root'];check_root(rr);nodes+=rr['nodes']
                assert rr['plane_uint64']==word(planes[owner]) and rr['origin_uint64']==word(origin) and rr['direction']==sign
                er=(bits(word(planes[owner]))-bits(word(origin)))*sign
                if owner==prev:
                    assert step==1 and er==0 and bits(rr['root_uint64'])==0
                    assert r['classification']=='previous_owner_zero_root_excluded';counts+=1
                else:
                    a,b,c=[v[1:] for v in vs];u,v,p=minus(b,a),minus(c,a),minus(point,a)
                    det=cross(u,v);U,V=cross(p,v),cross(u,p);assert det!=0
                    if det<0:det,U,V=-det,-U,-V
                    W=det-U-V;kind='miss' if min(U,V,W)<0 else ('boundary_FAIL' if min(U,V,W)==0 else 'strict_interior')
                    assert r['classification']==kind and r['det_U_V_W']==[pair(qv) for qv in (det,U,V,W)]
                pid+=1
        assert len(rs)==pid
        win=choose(rs,step);chosen.append(win);er=q(win['root']['exact_root_BU']);assert er>0;exact_length+=er
        assert ref['hits'][step]=={'primitive_id':win['primitive_id'],'owner':step,'segment_BU':pair(er)}
        origin=planes[step];prev=step;sign=-sign
    assert counts==res['previous_owner_exact_zero_exclusions']==2
    assert res['selected_identity']==[[r['primitive_id'],r['owner']] for r in chosen]
    assert res['selected_root_uint64']==[r['root']['root_uint64'] for r in chosen]
    current=0;acc=F(0)
    for n,w in zip(res['accumulation_nodes'],res['selected_root_uint64']):
        assert n['operation']=='add' and n['input_uint64']==[current,w]
        acc+=check_node(n);nodes.append(n);current=n['output_uint64']
    assert len(res['accumulation_nodes'])==2 and current==res['geometric_length_uint64']
    rs=res['reference_nodes'];assert rs[0]['operation']=='subtract' and rs[0]['input_uint64']==[word(planes[1]),word(snap['objects']['D']['mode_origin_BU'][0])]
    referr=check_node(rs[0]);nodes.append(rs[0]);cw=rs[0]['output_uint64']
    if src['direction'][0]<0:
        assert len(rs)==2 and rs[1]['input_uint64']==[cw] and rs[1]['operation']=='negate'
        check_node(rs[1]);nodes.append(rs[1]);cw=rs[1]['output_uint64']
    else:assert len(rs)==1
    assert cw==res['reference_correction_uint64']
    eff=res['effective_node'];assert eff['operation']=='add' and eff['input_uint64']==[current,cw]
    efferr=check_node(eff);nodes.append(eff);assert eff['output_uint64']==res['effective_reference_length_uint64']
    correction=int(src['direction'][0])*(bits(word(planes[1]))-bits(word(snap['objects']['D']['mode_origin_BU'][0])))
    effective=exact_length+correction;wave=bits(word(snap['lambda_BU']));assert wave>0
    assert q(ref['geometric_length_BU'])==exact_length and q(ref['reference_correction_BU'])==correction
    assert q(ref['effective_reference_length_BU'])==effective and q(ref['wavelength_BU'])==wave
    cycles=effective/wave;k=(4*cycles+F(1,2))//1;assert ref['quarter_index']==k and ref['quadrant_mod4']==k%4
    assert q(ref['exact_ORIGINAL_cycles'])==cycles and q(ref['residual_cycles'])==cycles-F(k,4)
    charges={'selected_Xroot_rounding_BU':sum((q(r['root']['rounding_radius_BU']) for r in chosen),F(0)),
        'geometric_accumulation_rounding_BU':acc,'reference_subtraction_rounding_BU':referr,'effective_add_rounding_BU':efferr}
    assert res['length_rounding_charges_BU']=={key:pair(v) for key,v in charges.items()}
    bound=sum(charges.values(),F(0));observed=abs(bits(eff['output_uint64'])-effective)
    assert observed<=bound and q(res['observed_length_error_BU'])==observed and q(res['length_to_fixed_ORIGINAL_bound_BU'])==bound
    phase=2*PIHI*bound/wave;assert q(res['phase_from_length_only_bound_rad'])==phase
    assert res['unchanged_phase_cap_rad']==[1,10**12] and res['length_only_phase_charge_fits_cap']==(phase<=F(1,10**12))
    assert res['new_RN64_operation_counts']=={key:sum(n['operation']==key for n in nodes) for key in ('subtract','add','negate')}
    assert res['native_YZ_projection_executed'] is res['full_native_ray_selector_implemented'] is res['hi_lo_geometry_replayed'] is False
    assert res['remaining_argument_unit_source_material_reduction_power_readout_executions']==0
    return float(phase)
def context(packet):
    bs={k:base64.b64decode(v,validate=True) for k,v in packet['buffers_base64'].items()}
    assert set(bs)=={'triangles','sources','wavelength','reference','original_scene_json','input_metadata_json'}
    for k,b in bs.items():assert packet['manifest']['buffers'][k]=={'bytes':len(b),'sha256':sha(b)}
    m=json.loads(bs['input_metadata_json']);s=json.loads(bs['original_scene_json']);g=m['explicit_group_contract']
    assert m['original_snapshot_sha256']==sha(bs['original_scene_json']);ids=m['source_order'];ass=g['assignments']
    assert ids==[x['id'] for x in s['sources']]==[x['source_id'] for x in ass]
    groups=[]
    for t in ass:
        assert t['source_phase_reference_id']=='original-source-zero:'+m['scene_binding_sha256']+':'+t['source_id']
        key=[t['port'],t['coherence_group']]
        if key not in groups:groups.append(key)
    c={'model':'axial-static-amplitude-L1-allocation-HOST-v1','units':'ORIGINAL-source-field-amplitude-L1','case_name':m['case_name'],
       'input_packet_sha256':digest(packet),'scene_binding_sha256':m['scene_binding_sha256'],'word_ABI_sha256':m['word_ABI_sha256'],
       'original_snapshot_sha256':m['original_snapshot_sha256'],'original_group_contract_sha256':digest(g),
       'source_order':ids,'assignments':ass,'groups':groups,'unchanged_field_L1_cap':pair(q(g['limits']['field_L1'])),
       'unchanged_limits':g['limits'],'grouping_provenance':g['grouping_provenance'],'execution_authenticated':False,'coherence_authenticated':False}
    return c,s

def get(obj,path):
    for k in path:obj=obj[k]
    return obj
def put(obj,path,value):
    for k in path[:-1]:obj=obj[k]
    obj[path[-1]]=value
def lift32(w):
    assert type(w) is int and 0<=w<2**32
    e=(w>>23)&255;m=w&((1<<23)-1);assert e<255 and (e or m==0)
    return ((w>>31)<<63) if e==0 else ((w>>31)<<63)|((e+896)<<52)|(m<<29)
def RN(x,width,zs):
    assert type(width) is int and width in (32,64)
    if x==0:return zs<<(width-1)
    frac,bias,emin,emax=(23,127,-126,127) if width==32 else (52,1023,-1022,1023)
    sign=(1<<(width-1)) if x<0 else 0;n,d=abs(x.numerator),x.denominator
    e=n.bit_length()-d.bit_length()
    if (n<d<<e if e>=0 else n<<-e<d):e-=1
    assert e<=emax
    grid=max(e,emin)-frac;nn,dd=(n,d<<grid) if grid>=0 else (n<<-grid,d)
    m,rem=divmod(nn,dd);m+=int(2*rem>dd or (2*rem==dd and m&1))
    if m==0:return sign
    if e<emin:
        assert m<=2**frac;return sign|m
    if m==2**(frac+1):m>>=1;e+=1
    assert e<=emax and 2**frac<=m<2**(frac+1)
    return sign|((e+bias)<<frac)|(m-2**frac)
def scalar(record,ow):
    original=bits(ow);hw=RN(original,32,ow>>63);h=bits(lift32(hw))
    rz=int(original==h==0 and ow>>63==1 and hw>>31==0)
    residual=RN(original-h,64,rz);rq=bits(residual);lw=RN(rq,32,residual>>63);l=bits(lift32(lw))
    dz=int(h==l==0 and hw>>31==1 and lw>>31==1);dw=RN(h+l,64,dz);dq=bits(dw)
    expected={'original_uint64':ow,'high_uint32':hw,'residual_uint64':residual,'low_uint32':lw,'decoded_uint64':dw,
       'residual_RN64_delta':pair(rq-(original-h)),'represented_exact_sum':pair(h+l),
       'encoding_error_abs':pair(abs(h+l-original)),'decode_RN64_delta':pair(dq-(h+l)),
       'decoded_coordinate_error_abs':pair(abs(dq-original))}
    assert {k:v for k,v in record.items() if k!='path'}==expected
    return hw,lw,dw
def verify_transport(result,snap,i):
    encoder=result['retained_geometry_encoder'];ps=[]
    for name in ('M','D'):
        ps.extend([['objects',name,'vertices_world_BU',j,k] for j in range(len(snap['objects'][name]['vertices_world_BU'])) for k in range(3)])
    for key in ('position_BU','direction'):ps.extend([['sources',i,key,k] for k in range(3)])
    for key in ('mode_origin_BU','mode_direction'):ps.extend([['objects','D',key,k] for k in range(3)])
    ps.extend([['lambda_BU'],['objects','M','phase_rad']])
    assert encoder['source_index']==i and encoder['original_snapshot_digest']==digest(snap)
    assert len(ps)==38 and encoder['ordered_paths_sha256']==digest(ps)
    assert [r['path'] for r in encoder['records']]==ps
    raw=base64.b64decode(encoder['transport_le_base64'],validate=True)
    assert len(raw)==encoder['transport_bytes']==304 and sha(raw)==encoder['transport_le_sha256']==result['retained_transport_sha256']
    expected=json.loads(json.dumps(snap));proof=result['guarded_decode'];nodes=proof['native_decode_nodes'];checks=proof['record_admission']
    assert len(nodes)==len(checks)==38
    for j,(path,rec,n,c) in enumerate(zip(ps,encoder['records'],nodes,checks)):
        ow=word(get(snap,path));h,l,d=scalar(rec,ow);assert struct.unpack_from('<II',raw,j*8)==(h,l)
        assert n=={'path':path,'input_uint32':[h,l],'output_uint64':d}
        assert c['original_uint64']==ow and c['high_uint32']==h and c['low_uint32']==l and c['decoded_uint64']==d
        assert c['residual_uint64']==rec['residual_uint64'] and c['RN_chain_midpoints_checked']==4
        put(expected,path,struct.unpack('<d',struct.pack('<Q',d))[0])
    assert result['decoded_snapshot']==expected and proof['decoded_snapshot_digest']==digest(expected)
    assert proof['all_records_admitted_before_first_native_add'] is True
    assert proof['new_native_RN64_decode_adds']==result['new_native_decode_adds']==38 and proof['new_encoding_casts_subtractions']==0
    assert result['new_encoder_operations']==result['new_Horner_source_material_reduction_power_readout']==0
    return expected
def verify_composition(comp,fixed,res,sign):
    dec=res['fixed_ORIGINAL_reference'];c={k:q(v) for k,v in fixed['ORIGINAL_coordinates_BU'].items()};d={k:q(v) for k,v in dec['ORIGINAL_coordinates_BU'].items()}
    assert [h['primitive_id'] for h in fixed['hits']]==[h['primitive_id'] for h in dec['hits']]
    assert [h['owner'] for h in fixed['hits']]==[h['owner'] for h in dec['hits']]==[0,1]
    assert fixed['quarter_index']==dec['quarter_index']
    for t,v in ((fixed,c),(dec,d)):
        assert v['wavelength']>0 and q(t['geometric_length_BU'])==sign*(2*v['M']-v['S']-v['D'])
        assert q(t['reference_correction_BU'])==sign*(v['D']-v['R']) and q(t['effective_reference_length_BU'])==sign*(2*v['M']-v['S']-v['R'])
    e={k:abs(d[k]-c[k]) for k in c};assert comp['coordinate_errors_BU']=={k:pair(v) for k,v in e.items()}
    geom=2*e['M']+e['S']+e['D'];ref=e['D']+e['R'];eff=2*e['M']+e['S']+e['R']
    assert q(comp['geometry_representation_length_bound_BU'])==geom and q(comp['reference_representation_bound_BU'])==ref
    assert q(comp['uncorrelated_geometry_plus_reference_bound_BU'])==geom+ref
    assert q(comp['effective_representation_bound_shared_D_cancelled_BU'])==eff
    rc={k:q(v) for k,v in res['length_rounding_charges_BU'].items()};assert all(v>=0 for v in rc.values())
    R=sum(rc.values(),F(0));assert comp['Xroot_length_rounding_charges_BU']==res['length_rounding_charges_BU']
    assert q(comp['Xroot_length_rounding_bound_BU'])==q(res['length_to_fixed_ORIGINAL_bound_BU'])==R
    assert q(comp['combined_effective_length_bound_BU'])==eff+R
    actual=bits(res['effective_reference_length_uint64']);L0=q(fixed['effective_reference_length_BU']);Ld=q(dec['effective_reference_length_BU'])
    assert abs(Ld-L0)<=eff and abs(actual-Ld)<=R and abs(actual-L0)<=eff+R
    assert q(comp['actual_length_to_FIXED_ORIGINAL_error_BU'])==abs(actual-L0)
    charges={'geometry_representation_cycles':eff/d['wavelength'],'Xroot_length_rounding_cycles':R/d['wavelength'],
        'wavelength_representation_cycles':abs(L0)*e['wavelength']/(d['wavelength']*c['wavelength'])}
    E=sum(charges.values(),F(0));assert comp['cycle_charges_to_fixed_ORIGINAL']=={k:pair(v) for k,v in charges.items()}
    assert q(comp['cycles_to_fixed_ORIGINAL_bound'])==E
    observed=abs(actual/d['wavelength']-L0/c['wavelength']);assert observed<=E and q(comp['observed_host_exact_cycles_error'])==observed
    phases={k.replace('_cycles','_rad'):2*PIHI*v for k,v in charges.items()};P=sum(phases.values(),F(0))
    assert comp['phase_length_wavelength_charges_rad']=={k:pair(v) for k,v in phases.items()} and q(comp['phase_length_wavelength_only_bound_rad'])==P
    assert comp['unchanged_phase_cap_rad']==[1,10**12] and comp['length_wavelength_only_phase_charge_fits_cap']==(P<=F(1,10**12))
    margin=F(1,8)-abs(L0/c['wavelength']-F(fixed['quarter_index'],4))-E
    assert q(comp['quarter_margin_with_combined_error_cycles'])==margin and comp['quarter_point_interval_certified']==(margin>0)
    assert comp['RN64_quotient_argument_not_executed'] is True
    return P,margin

r=json.loads((ROOT/REPORT).read_bytes());assert r['task_id']=='AXIAL-GUARDED-HILO-XROOT-RN64-CPU-001'
pins=pins_from(r)
for p,h in pins.items():assert sha((ROOT/p).read_bytes())==h,p
assert len(pins)==357
old=payload(read(PREVIOUS,PREVIOUS_SHA))['data']['audit']
def data(p):return payload(read(p,pins[p]))
chain=data('coordinacion/respuestas/AXIAL-GUARDED-SCENE-SOURCE-CPU-001-CODEX.json')['data']['audit']
packets=data('coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json')['packets']
packets.update({n:v['parent'] for n,v in data('coordinacion/respuestas/AXIAL-NATIVE-PRESENCE-STOPS-001-CODEX.json')['synthetic_controls'].items()})
raw=payload(r);assert raw['PASS'] is True and raw['tests']==4
a=raw['data']['audit'];assert a['case_order']==old['case_order'] and a['inherited_pins_verified']==353
FALSE=tuple(r['proof_scope']);assert len(FALSE)==38 and all(x is False for x in r['proof_scope'].values())
def allfalse(x):
    for k in FALSE:assert x[k] is False,k
allfalse(a);executed=stopped=0;phases={};margins={}
for name,c in a['cases'].items():
    ctx,snap=context(packets[name]);assert c['context']==old['cases'][name]['context']==chain['cases'][name]['context']==ctx;allfalse(c)
    for i,row in enumerate(c['sources']):
        prior=old['cases'][name]['sources'][i];assert row['source_id']==prior['source_id'] and row['retained_Xroot_row_sha256']==digest(prior)
        assert row['status']=='STOP';allfalse(row)
        assert row['guarded_hilo_Xroot_RN64_CPU_executed'] is prior['ORIGINAL_point_Xroot_RN64_CPU_executed']
        if not row['guarded_hilo_Xroot_RN64_CPU_executed']:
            stopped+=1;assert 'result' not in row and row['reason']==prior['reason'];continue
        executed+=1;res=row['result'];assert res['retained_geometry_encoder']==chain['cases'][name]['sources'][i]['result']['geometry_encoder']
        decoded=verify_transport(res,snap,i);rr=res['new_decoded_Xroot_result'];verify_scene(rr,decoded,i)
        assert res['fixed_ORIGINAL_reference']==prior['result']['fixed_ORIGINAL_reference']
        P,M=verify_composition(res['composition'],res['fixed_ORIGINAL_reference'],rr,int(snap['sources'][i]['direction'][0]))
        assert P<=F(1,10**12) and M>0;phases[name]=float(P);margins[name]=float(M)
        assert res['new_fixed_and_decoded_rational_root_records']==16
        assert row['phase_reference_id']==ctx['assignments'][i]['source_phase_reference_id'] and row['terminal_reference_id']==ctx['assignments'][i]['terminal_reference_id']
assert (executed,stopped)==(2,17) and a['new_point_sources_executed']==2 and a['retained_sources_not_executed']==17
assert a['new_guard_decode_adds']==76 and a['new_Xroot_RN64_operation_counts']=={'subtract':18,'add':6,'negate':8}
assert a['new_fixed_and_decoded_rational_root_records']==32 and a['new_encoder_operations']==a['old_audits_suites_reexecuted']==a['new_Horner_source_material_reduction_power_readout']==0
assert a['native_YZ_projection_selector_implemented'] is a['RN64_quotient_argument_executed'] is False
assert a['all_eligible_transports_admitted_before_new_operations'] is True
forg=raw['data']['forgery_rejection'];enc=forg['encoder'];honest=chain['cases']['thin_resolved']['sources'][0]['result']['geometry_encoder']
expected=json.loads(json.dumps(honest));t=expected['records'][-1];t['decoded_uint64']=word(1.0)
t['decode_RN64_delta']=pair(bits(t['decoded_uint64'])-q(t['represented_exact_sum']))
t['decoded_coordinate_error_abs']=pair(abs(bits(t['decoded_uint64'])-bits(t['original_uint64'])))
assert enc==expected and t['original_uint64']==0
try:scalar(t,t['original_uint64'])
except AssertionError:pass
else:raise AssertionError('forgery must fail RN chain')
assert forg['decode_adds']==forg['Xroot_subs']==forg['rational_reference_records']==0 and forg['prior_case_also_not_executed'] is True
runtime=raw['data']['runtime_decode_FAIL'];assert runtime['new_decode_adds_attempted']==1 and runtime['new_Xroot_ops']==runtime['reference_records']==0
assert len(runtime['attempts'])==1
t=runtime['attempts'][0];h,l=t['input_uint32'];exact=bits(lift32(h))+bits(lift32(l));z=int(bits(lift32(h))==bits(lift32(l))==0 and h>>31==l>>31==1)
assert t['correct_uint64']==RN(exact,64,z) and t['forged_uint64']==t['correct_uint64']+1
rejects=raw['data']['admission_rejections'];assert len(rejects)==len({x['label'] for x in rejects})==13
assert all(x['reason'] for x in rejects)
control=raw['data']['conservative_cap_FAIL'];rr=control['root_result_majorant'];assert rr['length_rounding_charges_BU']['selected_Xroot_rounding_BU']==[1,100]
fixed=a['cases']['thin_resolved']['sources'][0]['result']['fixed_ORIGINAL_reference']
P,M=verify_composition(control['composition'],fixed,rr,1);assert P>F(1,10**12) and M<0 and control['native_operations']==0
initial=r['retained_initial_failure'];initial_raw=payload_failure=None
t=initial['test_run'];assert t['rc']==1 and t['timed_out'] is False
b=zlib.decompress(base64.b64decode(''.join(t['stdout_zlib_base64_chunks']),validate=True))
assert sha(b)==t['stdout_sha256'] and len(b)==t['stdout_bytes'] and json.loads(b)['PASS'] is False
assert 'normal-or-zero selected word' in t['stderr'] and initial['repair_scope']=='ONLY synthetic forged last zero record changed from +1 subnormal to finite-normal 1.0; no production/cap changes'
assert initial['code_doc_sha256']['Blender/benchmarks/capacity_audit/axial_guarded_hilo_xroot_RN64_CPU_v1.py']==r['own_code_doc_sha256']['Blender/benchmarks/capacity_audit/axial_guarded_hilo_xroot_RN64_CPU_v1.py']
print(json.dumps({'PASS':True,'pins':len(pins),'sources':2,'retained_STOP':17,'guard_decode_adds':76,
 'Xroot_ops':a['new_Xroot_RN64_operation_counts'],'phase_length_wave_only_rad':phases,'quarter_margins_cycles':margins,
 'forgery_before_ALL_decode_roots':True,'native_decode_FAIL_before_roots':True,'cap_FAIL_preserved':True,
 'initial_test_failure_preserved':True,'rejections':13,'GPU_full_native_ray_full_field_admitted':False},sort_keys=True))
