"""Independent stdlib-only singleton oracle; exact identities, no production imports."""
import base64,hashlib,json,math,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT='coordinacion/respuestas/AXIAL-ZERO-SINGLETON-UNIT-HOST-001-CODEX.json'
ONE=0x3ff0000000000000
FALSE=('scene_argument_enclosed','uniform_unit_error_to_ORIGINAL_proved','uniform_source_error_proved',
       'accepted_full_field_pipeline','remaining_stages_error_proved','execution_authenticated',
       'coherence_authenticated','native_kernel_implemented','GPU_executed','GPU_job_admission',
       'whole_scene_parameter_enclosure_proved','native_argument_implemented','general_3D_geometry_proved',
       'physical_scene_uncertainty_certified','native_signed_zero_graph_equivalence_proved')
def sha(v):return hashlib.sha256(v).hexdigest()
def canon(v):return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
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
def rat(v):
    assert type(v) is list and len(v)==2 and all(type(x) is int for x in v)
    assert v[1]>0 and math.gcd(*v)==1;return F(*v)
def binary(w):
    assert type(w) is int and 0<=w<2**64
    e=w//2**52%2048;f=w%2**52
    assert e!=2047 and (e!=0 or f==0)
    return (-1 if w>=2**63 else 1)*F(f+(2**52 if e else 0))*F(2)**(e-1075)
def false(v):
    for k in FALSE:assert v[k] is False,k
def graph(u,k):
    rot=u['rotation_RN64'];q=u['quarter_argument'];assert rot['angle_uint64']==q['HOST_argument_uint64']==0
    assert q['quarter_turns_HOST']==k and rat(q['quarter_residual_HOST_rational'])==rat(q['HOST_argument_rational'])==0
    cs=rot['coefficients'];assert set(cs)=={'cos','sin'}
    for name,odd in [('cos',0),('sin',1)]:
        assert len(cs[name])==7 and cs[name][0]['uint64']==ONE
        for j,c in enumerate(cs[name]):
            t=F((-1)**j,math.factorial(2*j+odd))
            assert rat(c['exact_rational'])==t and rat(c['error_rational'])==abs(binary(c['uint64'])-t)
    ops=rot['operations'];assert len(ops)==rot['RN64_operations']==26
    negative=[]
    # Every retained result is exactly representable. This is NOT RN evaluation.
    for op in ops:
        a,b=map(rat,op['inputs_rational']);out=binary(op['output_uint64'])
        assert rat(op['rounding_delta_rational'])==0
        assert out==(a*b if op['op']=='mul' else a+b)
        if op['op']=='mul':
            assert b==0 and op['output_uint64']==0
            if a<0:negative.append(op['label'])
    assert ops[0]['label']=='square' and ops[0]['inputs_rational']==[[0,1],[0,1]]
    for offset,name in [(1,'cos'),(13,'sin')]:
        for step,j in enumerate(range(5,-1,-1)):
            m,a=ops[offset+2*step:offset+2*step+2]
            assert m['label']==name+'.mul'+str(j) and m['op']=='mul'
            assert rat(m['inputs_rational'][0])==binary(cs[name][j+1]['uint64'])
            assert a['label']==name+'.add'+str(j) and a['op']=='add'
            assert a['inputs_rational'][0]==[0,1] and a['output_uint64']==cs[name][j]['uint64']
            assert rat(a['inputs_rational'][1])==binary(cs[name][j]['uint64'])
    assert ops[-1]['label']=='sin.final' and ops[-1]['inputs_rational']==[[1,1],[0,1]]
    expected={0:[ONE,0],1:[2**63,ONE],2:[ONE+2**63,2**63],3:[0,ONE+2**63]}[k%4]
    assert u['unit_uint64']==expected and u['unpermuted_unit_uint64']==[ONE,0]
    assert [rat(v) for v in u['unit_rational']]==list(map(binary,expected))
    assert u['unit_uint32_little_endian']==[[v%2**32,v//2**32] for v in expected]
    assert len(negative)==6
    return negative
r=json.loads((ROOT/REPORT).read_bytes());pins=pins_from(r)
for p,h in pins.items():assert sha((ROOT/p).read_bytes())==h,p
data=payload(r);assert data['PASS'] is True and data['tests']==4
a=data['data']['audit'];false(a)
old=payload(read(r['inherited_pin_source']['path'],r['inherited_pin_source']['sha256']))['data']['audit']
rect=payload(read('coordinacion/respuestas/AXIAL-ARGUMENT-RECTANGLE-HOST-001-CODEX.json',pins['coordinacion/respuestas/AXIAL-ARGUMENT-RECTANGLE-HOST-001-CODEX.json']))['data']['audit']
units=payload(read('coordinacion/respuestas/AXIAL-QUARTER-UNIT-HOST-001-CODEX.json',pins['coordinacion/respuestas/AXIAL-QUARTER-UNIT-HOST-001-CODEX.json']))['cases']
ingress='coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json';presence='coordinacion/respuestas/AXIAL-NATIVE-PRESENCE-STOPS-001-CODEX.json'
packets=payload(read(ingress,pins[ingress]))['packets']
controls=payload(read(presence,pins[presence]))['synthetic_controls']
packets.update({n:v['parent'] for n,v in controls.items()})
assert a['case_order']==old['case_order'] and len(a['case_order'])==17 and len(pins)==272
count=stops=nonzero=nodes=0
for n in a['case_order']:
    c=a['cases'][n];false(c);assert c['context']==old['cases'][n]['context']==rect['cases'][n]['context']
    packet=packets[n];ctx=c['context'];assert digest(packet)==ctx['input_packet_sha256']
    buffers={k:base64.b64decode(v,validate=True) for k,v in packet['buffers_base64'].items()}
    for role,raw in buffers.items():assert packet['manifest']['buffers'][role]=={'bytes':len(raw),'sha256':sha(raw)}
    meta=json.loads(buffers['input_metadata_json'])
    assert meta['original_snapshot_sha256']==sha(buffers['original_scene_json'])==ctx['original_snapshot_sha256']
    assert ctx['scene_binding_sha256']==meta['scene_binding_sha256'] and ctx['word_ABI_sha256']==meta['word_ABI_sha256']
    assert ctx['assignments']==meta['explicit_group_contract']['assignments'] and ctx['source_order']==meta['source_order']
    assert [s['source_id'] for s in c['sources']]==ctx['source_order']
    for i,s in enumerate(c['sources']):
        false(s);d=old['cases'][n]['sources'][i];rr=rect['cases'][n]['sources'][i];u=units[n]['sources'][i]
        assert s['retained_scene_domain_source_sha256']==digest(d)
        assert s['retained_unit_polynomial_charge_fits']==d['retained_unit_polynomial_charge_fits'] and s['status']=='STOP'
        if not d['restricted_coordinate_box_to_parameter_rectangle_proved']:
            stops+=1;assert s['reason']==d['reason'] and not s['restricted_exact_unit_error_to_ORIGINAL_proved']
        elif rr['argument_image']['argument_interval']!=[[0,1],[0,1]]:
            nonzero+=1;assert not s['restricted_exact_unit_error_to_ORIGINAL_proved'] and 'proof' not in s
        else:
            count+=1;p=s['proof'];false(p);assert s['restricted_exact_unit_error_to_ORIGINAL_proved'] is True
            assert p['retained_scene_domain_source_sha256']==digest(d) and p['retained_rectangle_source_sha256']==digest(rr)
            assert p['retained_unit_source_sha256']==digest(u)
            assert p['unchanged_original_phase_cap_rad']==d['unchanged_original_phase_cap_rad']==rr['unchanged_original_phase_cap_rad']==meta['original_path_phase_caps'][s['source_id']]==[0,1]
            assert d['retained_unit_polynomial_charge_fits'] is False and p['retained_generic_polynomial_NONfit_unchanged'] is True
            b=rr['parameter_branch'];im=rr['argument_image']
            assert b['quarter_residual_interval']==[[0,1],[0,1]] and b['ORIGINAL_quarter_residual']==[0,1]
            assert im['uniform_argument_error_bound_rad']==im['uniform_composed_parameter_phase_to_fixed_ORIGINAL_rad']==[0,1]
            assert b['quarter_turn_endpoint_integers']==[p['quarter_turn']]*2 and p['quarter_turn']==b['ORIGINAL_quarter_turn']
            assignment=ctx['assignments'][i]
            assert u['phase_reference_id']==assignment['source_phase_reference_id'] and u['terminal_reference_id']==assignment['terminal_reference_id']
            points=[u['ideal_ORIGINAL_unit_HOST']]+u['encoded_corner_units_HOST'];assert len(points)==len(p['graph_checks'])==5
            for point,g in zip(points,p['graph_checks']):
                assert g['retained_graph_sha256']==digest(point) and g['identities_checked']==26
                assert g['canonical_HOST_zero_not_IEEE_signed_zero_labels']==graph(point,p['quarter_turn'])
                assert p['coefficient_profile_sha256']==digest(point['rotation_RN64']['coefficients'])
                assert g['exact_unit_uint64']==point['unit_uint64'] and g['exact_unit_rational']==point['unit_rational']
                nodes+=26
            assert p['unit_L1_error_to_ORIGINAL_bound']==p['additional_phase_bound_rad']==[0,1]
            assert p['exact_charge_fits_unchanged_cap'] is True and p['new_RN_encodings_or_old_producers_reexecuted']==0
assert (count,stops,nonzero,nodes)==(3,14,2,390)
assert (a['restricted_zero_unit_proofs'],a['retained_unit_STOPs'],a['nonzero_domains_not_refined'])==(count,stops,nonzero)
assert len(data['data']['rejections'])==37 and len({v['label'] for v in data['data']['rejections']})==37
for p in data['data']['permutations']:
    k=p['quarter'];expected={0:[ONE,0],1:[2**63,ONE],2:[ONE+2**63,2**63],3:[0,ONE+2**63]}[k%4]
    assert p['words']==expected and list(map(rat,p['rational']))==list(map(binary,expected))
false(r['proof_scope'])
print(json.dumps({'PASS':True,'pins':len(pins),'restricted_zero_units':count,'retained_STOPs':stops,
                  'nonzero_not_refined':nonzero,'retained_exact_node_identities':nodes,'canonical_vs_native_sign_differences':90,
                  'new_RN_or_old_producer_reexecution':0,'rejections':37,'native_signed_zero_equivalence':False},sort_keys=True))
