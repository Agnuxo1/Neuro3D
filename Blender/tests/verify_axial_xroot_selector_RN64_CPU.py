"""Independent stdlib IEEE/YZ/root interval/length oracle; no production imports."""
import base64,hashlib,json,math,struct,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT='coordinacion/respuestas/AXIAL-XROOT-SELECTOR-RN64-CPU-001-CODEX.json'
PREVIOUS='coordinacion/respuestas/AXIAL-GUARDED-SCENE-SOURCE-CPU-001-CODEX.json'
PREVIOUS_SHA='8f4ea4cc5d35cb3f56d800837ff553c438f4e635d7e482b2a197a45651e59da8'
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
r=json.loads((ROOT/REPORT).read_bytes());assert r['task_id']=='AXIAL-XROOT-SELECTOR-RN64-CPU-001'
pins=pins_from(r)
for p,h in pins.items():assert sha((ROOT/p).read_bytes())==h,p
assert len(pins)==352
old=payload(read(PREVIOUS,PREVIOUS_SHA))['data']['audit']
def data(p):return payload(read(p,pins[p]))
packets=data('coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json')['packets']
packets.update({n:v['parent'] for n,v in data('coordinacion/respuestas/AXIAL-NATIVE-PRESENCE-STOPS-001-CODEX.json')['synthetic_controls'].items()})
raw=payload(r);assert raw['PASS'] is True and raw['tests']==4
a=raw['data']['audit'];assert a['case_order']==old['case_order'] and a['inherited_pins_verified']==348
FALSE=tuple(r['proof_scope']);assert len(FALSE)==38 and all(x is False for x in r['proof_scope'].values())
def allfalse(x):
    for k in FALSE:assert x[k] is False,k
allfalse(a);executed=stopped=0;phases={}
for name,c in a['cases'].items():
    ctx,snap=context(packets[name]);assert c['context']==old['cases'][name]['context']==ctx;allfalse(c)
    for i,row in enumerate(c['sources']):
        prior=old['cases'][name]['sources'][i];assert row['source_id']==prior['source_id'] and row['retained_row_sha256']==digest(prior)
        assert row['status']=='STOP';allfalse(row)
        assert row['ORIGINAL_point_Xroot_RN64_CPU_executed'] is prior['fresh_guarded_scene_bare_source_prefix_CPU_executed']
        if not row['ORIGINAL_point_Xroot_RN64_CPU_executed']:
            stopped+=1;assert 'result' not in row and row['reason']==prior['reason'];continue
        executed+=1;res=row['result'];assert res['fixed_ORIGINAL_reference']==prior['result']['fixed_ORIGINAL_trace']
        phases[name]=verify_scene(res,snap,i)
        assert row['phase_reference_id']==ctx['assignments'][i]['source_phase_reference_id'] and row['terminal_reference_id']==ctx['assignments'][i]['terminal_reference_id']
assert (executed,stopped)==(2,17) and a['new_point_sources_executed']==2 and a['retained_sources_not_executed']==17
assert a['new_RN64_operation_counts']=={'subtract':18,'add':6,'negate':8} and a['new_rational_reference_root_records']==16
assert a['old_audits_suites_reexecuted']==0 and a['full_native_ray_selector_implemented'] is False
for v in raw['data']['scalar_controls'].values():check_root(v)
assert raw['data']['scalar_controls']['halfway_even']['root_uint64']==word(1.0)
assert 'midpoint' in raw['data']['wrong_runtime_rejection']['reason']
controls=raw['data']['selector_controls'];assert len(controls)==5
for c in controls:
    try:choose(c['records'],c['expected_owner'])
    except AssertionError:pass
    else:raise AssertionError('control must reject '+c['label'])
contact=raw['data']['initial_contact_rejection'];s=contact['snapshot']
assert s['sources'][0]['position_BU'][0]==s['objects']['M']['vertices_world_BU'][0][0]
assert contact['new_native_operations']==0 and 'root zero' in contact['reason']
rejects=raw['data']['admission_rejections'];assert len(rejects)==len({x['label'] for x in rejects})==11
assert all(x['reason'] for x in rejects)
scope=raw['data']['scope'];assert scope['new_Horner_source_material_reduction_power_readout']==scope['new_hi_lo_encoder_guard']==scope['old_audits_suites']==0
assert scope['all_REAL_field_cases_STOP'] is scope['selector_controls_synthetic_NOT_fixture_changes'] is True
print(json.dumps({'PASS':True,'pins':len(pins),'new_point_sources':2,'retained_sources_not_executed':17,
 'operation_counts':a['new_RN64_operation_counts'],'phase_length_only_rad':phases,'selector_controls_rejected':5,
 'admission_rejections':11,'contact_before_native':True,'GPU_full_native_ray_full_field_admitted':False},sort_keys=True))
