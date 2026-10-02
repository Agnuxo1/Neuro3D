"""Independent stdlib proof checker for fixed-source, zero-unit restricted HOST domain."""
import base64,hashlib,json,math,struct,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT='coordinacion/respuestas/AXIAL-ZERO-SOURCE-DOMAIN-HOST-001-CODEX.json'
PRODUCT='coordinacion/respuestas/AXIAL-SOURCE-PRODUCT-HOST-001-CODEX.json'
FALSE=('scene_argument_enclosed','uniform_unit_error_to_ORIGINAL_proved','uniform_source_error_proved',
       'accepted_full_field_pipeline','remaining_stages_error_proved','execution_authenticated',
       'coherence_authenticated','native_kernel_implemented','GPU_executed','GPU_job_admission',
       'whole_scene_parameter_enclosure_proved','native_argument_implemented','general_3D_geometry_proved',
       'physical_scene_uncertainty_certified','native_signed_zero_graph_equivalence_proved',
       'amplitude_budget_accepted','reflection_coefficient_applied','field_values_computed','field_sum_computed',
       'detector_evaluated','source_amplitude_uncertainty_enclosed')
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
def binary(w,bits):
    assert type(w) is int and 0<=w<2**bits
    f,bias=(23,127) if bits==32 else (52,1023)
    e=w//2**f%(2**(bits-f-1));m=w%2**f
    assert e<2**(bits-f-1)-1 and (e!=0 or m==0)
    return (-1 if w>=2**(bits-1) else 1)*F(m+(2**f if e else 0))*F(2)**(e-bias-f)
def false(v):
    for k in FALSE:assert v[k] is False,k
def graph(product,words):
    original=[binary(w,64) for w in words];enc=product['source_encoder']
    assert enc['original_source_uint64']==words
    limbs=enc['source_limb_uint32'];assert len(limbs)==4
    vals=[binary(w,32) for w in limbs];source=[sum(vals[:2]),sum(vals[2:])]
    raw=struct.pack('<4I',*limbs)
    assert raw==base64.b64decode(enc['source_hilo_le_base64'],validate=True) and sha(raw)==enc['source_hilo_le_sha256']
    assert list(map(rat,enc['source_exact_limb_sum_rational']))==source
    error=sum(abs(a-b) for a,b in zip(source,original));assert error==F(1,2**55)
    assert rat(enc['source_encoding_error_L1'])==error
    for i,t in enumerate(enc['HOST_trace']):
        assert rat(t['original'])==original[i] and rat(t['high'])==vals[2*i]
        assert t['high_uint32']==limbs[2*i] and t['low_uint32']==limbs[2*i+1]
        assert rat(t['HOST_exact_residual'])==original[i]-vals[2*i]
        assert rat(t['represented'])==source[i] and rat(t['encoding_error'])==abs(source[i]-original[i])
    assert rat(enc['source_norm_L1'])==sum(map(abs,original))
    assert product['unit_uint64']==[0x3ff0000000000000,0] and rat(product['unit_error_L1_to_ORIGINAL_bound'])==0
    ops=product['operations'];assert len(ops)==8
    outputs=[]
    for op in ops:
        a,b=map(rat,op['inputs']);v=binary(op['output_uint64'],64)
        assert op['op'] in ('add','mul') and rat(op['delta'])==0
        assert v==(a+b if op['op']=='add' else a*b)
        assert v!=0 or op['output_uint64']==0
        outputs.append(v)
    assert [op['label'] for op in ops]==['decode0','decode1','ac','bd','ad','bc','real','imag']
    assert list(map(rat,ops[0]['inputs']))==vals[:2] and list(map(rat,ops[1]['inputs']))==vals[2:]
    assert [op['op'] for op in ops]==['add','add','mul','mul','mul','mul','add','add']
    expected=[(source[0],F(1)),(source[1],F(0)),(source[0],F(0)),(source[1],F(1)),
              (outputs[2],-outputs[3]),(outputs[4],outputs[5])]
    for op,(x,y) in zip(ops[2:],expected):assert list(map(rat,op['inputs']))==[x,y]
    assert outputs[:2]==outputs[-2:]==source
    assert product['product_uint64']==[ops[-2]['output_uint64'],ops[-1]['output_uint64']]
    assert list(map(rat,product['product_rational']))==source
    assert list(map(rat,product['source_decoded_RN64']))==source
    assert list(map(rat,product['exact_decoded_product']))==source
    assert list(map(rat,product['exact_original_times_represented_unit']))==original
    assert rat(product['observed_error_to_original_times_represented_unit_L1'])==error
    assert product['charges_L1']=={'source_encoding':[1,2**55],'source_decode_RN64':[0,1],
                                  'unit_to_ORIGINAL':[0,1],'product_RN64':[0,1]}
    assert rat(product['error_L1_to_original_source_times_ideal_unit_bound'])==error
    return error,source
r=json.loads((ROOT/REPORT).read_bytes());pins=pins_from(r)
for p,h in pins.items():assert sha((ROOT/p).read_bytes())==h,p
data=payload(r);assert data['PASS'] is True and data['tests']==4
a=data['data']['audit'];false(a);assert a['inherited_pins_verified']==273 and len(pins)==277
prev=read(r['inherited_pin_source']['path'],r['inherited_pin_source']['sha256']);old=payload(prev)['data']['audit']
products=payload(read(PRODUCT,pins[PRODUCT]))['cases']
ingress='coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json';presence='coordinacion/respuestas/AXIAL-NATIVE-PRESENCE-STOPS-001-CODEX.json'
packets=payload(read(ingress,pins[ingress]))['packets'];controls=payload(read(presence,pins[presence]))['synthetic_controls']
packets.update({n:v['parent'] for n,v in controls.items()})
assert a['case_order']==old['case_order'] and len(a['case_order'])==17
count=stops=nonzero=nodes=0
for n in a['case_order']:
    c=a['cases'][n];ctx=c['context'];false(c);assert ctx==old['cases'][n]['context']
    packet=packets[n];assert digest(packet)==ctx['input_packet_sha256']==products[n]['input_packet_sha256']
    buffers={k:base64.b64decode(v,validate=True) for k,v in packet['buffers_base64'].items()}
    assert set(buffers)==set(packet['manifest']['buffers'])
    for role,raw in buffers.items():assert packet['manifest']['buffers'][role]=={'bytes':len(raw),'sha256':sha(raw)}
    meta=json.loads(buffers['input_metadata_json']);snapshot=json.loads(buffers['original_scene_json'])
    assert ctx['original_snapshot_sha256']==meta['original_snapshot_sha256']==sha(buffers['original_scene_json'])
    assert ctx['source_order']==meta['source_order']==[s['id'] for s in snapshot['sources']]
    assert ctx['assignments']==meta['explicit_group_contract']['assignments']
    assert ctx['unchanged_field_L1_cap']==meta['explicit_group_contract']['limits']['field_L1']
    for k in ('scene_binding_sha256','word_ABI_sha256','source_order','case_name'):assert products[n][k]==ctx[k]==meta[k]
    assert [s['source_id'] for s in c['sources']]==ctx['source_order']
    for i,s in enumerate(c['sources']):
        u=old['cases'][n]['sources'][i];p=products[n]['sources'][i];false(s)
        assert s['status']=='STOP' and s['retained_zero_unit_row_sha256']==digest(u)
        assert s['retained_unit_polynomial_charge_fits']==u['retained_unit_polynomial_charge_fits']
        if not u['restricted_exact_unit_error_to_ORIGINAL_proved']:
            if u['reason_provenance']=='unchanged_retained_unit_STOP':stops+=1
            else:nonzero+=1
            assert s['reason']==u['reason'] and s['reason_provenance']==u['reason_provenance']
            assert s['restricted_fixed_source_bare_product_error_to_ORIGINAL_proved'] is False and 'proof' not in s
        else:
            count+=1;q=s['proof'];false(q)
            assert s['restricted_fixed_source_bare_product_error_to_ORIGINAL_proved'] is True
            assert q['retained_zero_unit_row_sha256']==digest(u) and q['retained_source_product_row_sha256']==digest(p)
            assert q['restricted_fixed_source_bare_product_error_to_ORIGINAL_proved'] is True
            assert u['proof']['unit_L1_error_to_ORIGINAL_bound']==[0,1] and u['proof']['quarter_turn']==0
            raw=buffers['sources'][128*i+112:128*i+128];assert raw==struct.pack('<dd',*snapshot['sources'][i]['field_reim'])
            words=list(struct.unpack('<QQ',raw));assert words==p['original_source_uint64']
            assert len(q['graph_checks'])==len(p['encoded_corner_products'])==4
            reference=None
            for j,(point,g) in enumerate(zip(p['encoded_corner_products'],q['graph_checks'])):
                error,source=graph(point,words);nodes+=8
                assert point['unit_uint64']==u['proof']['graph_checks'][j+1]['exact_unit_uint64']
                assert g['retained_product_sha256']==digest(point) and g['retained_encoder_sha256']==digest(point['source_encoder'])
                assert g['retained_node_identities_checked']==8 and g['new_RN_or_encoder_operations']==0
                assert g['fixed_original_source_uint64']==words
                assert list(map(rat,g['fixed_original_source_rational']))==[binary(w,64) for w in words]
                assert list(map(rat,g['represented_source_rational']))==source
                assert g['charges_L1']==point['charges_L1'] and g['bare_product_error_to_ORIGINAL_L1']==[1,2**55]
                assert reference is None or digest(point)==reference;reference=digest(point)
            assert q['uniform_bare_product_L1_error_to_fixed_ORIGINAL_bound']==p['product_error_L1_to_ORIGINAL_bound']==[1,2**55]
            assert q['nonzero_encoding_error_preserved'] is True
            assert q['unchanged_original_phase_cap_rad']==u['proof']['unchanged_original_phase_cap_rad']==[0,1]
            assert q['unchanged_global_field_L1_cap_NOT_a_source_allocation']==ctx['unchanged_field_L1_cap']
            assert q['phase_cap_NOT_compared_to_amplitude'] is True and q['new_RN_or_old_producers_reexecuted']==0
            assignment=ctx['assignments'][i]
            assert q['source_phase_reference_id']==p['phase_reference_id']==assignment['source_phase_reference_id']
            assert q['terminal_reference_id']==p['terminal_reference_id']==assignment['terminal_reference_id']
assert (count,stops,nonzero,nodes)==(3,14,2,96)
assert (a['restricted_fixed_source_domains_proved'],a['retained_unit_STOPs'],a['nonzero_domains_not_refined'])==(count,stops,nonzero)
assert len(data['data']['rejections'])==41 and len({v['label'] for v in data['data']['rejections']})==41
assert len(data['data']['source_word_checks'])==3 and len(data['data']['binary_controls'])==4
false(r['proof_scope'])
print(json.dumps({'PASS':True,'pins':len(pins),'restricted_fixed_source_domains':count,'retained_STOPs':stops,
                  'nonzero_domains_not_refined':nonzero,'retained_decode_product_identities':nodes,
                  'source_encoding_error_L1':[1,2**55],'rejections':41,'new_RN_or_encoder_reexecution':0,
                  'reflection_reduction_full_pipeline_proved':False},sort_keys=True))
