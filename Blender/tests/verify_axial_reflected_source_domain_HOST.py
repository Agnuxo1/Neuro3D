"""Independent stdlib verification of restricted ideal-mirror/source domain linkage."""
import base64,hashlib,json,math,struct,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT='coordinacion/respuestas/AXIAL-REFLECTED-SOURCE-DOMAIN-HOST-001-CODEX.json'
MIRROR='coordinacion/respuestas/AXIAL-MIRROR-ZERO-HOST-001-CODEX.json'
EVENTS='coordinacion/respuestas/AXIAL-NATIVE-EVENTS-001-CODEX.json'
ZERO='coordinacion/respuestas/AXIAL-ZERO-SINGLETON-UNIT-HOST-001-CODEX.json'
DOMAIN='coordinacion/respuestas/AXIAL-SCENE-PARAMETER-DOMAIN-HOST-001-CODEX.json'
FALSE=('scene_argument_enclosed','uniform_unit_error_to_ORIGINAL_proved','uniform_source_error_proved',
       'accepted_full_field_pipeline','remaining_stages_error_proved','execution_authenticated','coherence_authenticated',
       'native_kernel_implemented','GPU_executed','GPU_job_admission','whole_scene_parameter_enclosure_proved',
       'native_argument_implemented','general_3D_geometry_proved','physical_scene_uncertainty_certified',
       'native_signed_zero_graph_equivalence_proved','amplitude_budget_accepted','reflection_coefficient_applied',
       'field_values_computed','field_sum_computed','detector_evaluated','source_amplitude_uncertainty_enclosed',
       'native_material_transport_implemented','physical_mirror_model_validated','mirror_phase_uncertainty_enclosed',
       'reflection_coefficient_executed_new')
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
    e=w//2**52%2048;m=w%2**52;assert e<2047 and (e!=0 or m==0)
    return (-1 if w>=2**63 else 1)*F(m+(2**52 if e else 0))*F(2)**(e-1075)
def false(v):
    for k in FALSE:assert v[k] is False,k
def profile(snap,meta,event,domain,reported):
    assert meta['object_ids']==['M','D'] and meta['kinds']==['mirror','det']
    assert set(snap['objects'])=={'M','D'} and not snap['undeclared_meshes']
    m=snap['objects']['M'];assert m['kind']=='mirror' and snap['objects']['D']['kind']=='det'
    assert type(m['phase_rad']) is float
    bits=struct.unpack('<Q',struct.pack('<d',m['phase_rad']))[0];assert bits in (0,2**63)
    assert reported['fixed_ORIGINAL_mirror_phase_uint64']==bits and reported['ideal_coefficient_exact_reim']==[[-1,1],[0,1]]
    assert reported['coefficient_error_L1']==[0,1]
    assert reported['retained_event_row_sha256']==digest(event) and reported['retained_scene_domain_row_sha256']==digest(domain)
    dp=domain['restricted_domain_proof'];s=dp['uniform_affine_selector_proof']
    assert domain['restricted_coordinate_box_to_parameter_rectangle_proved'] is True
    assert dp['ORIGINAL_inside_coordinate_box'] is True and dp['all_shared_plane_X_within_box_selector_proved'] is True
    for k in ('restricted_shared_plane_selector_proved','strict_positive_first_and_reflected_second',
              'mirror_first_uniform_clearance','skip_previous_owner_permitted_only_after_first_root'):assert s[k] is True
    assert event['accepted_axial_two_event_geometry_CPU_only'] is True
    assert event['mirror_owner']==0 and event['terminal_owner']==1 and len(event['segments'])==2
    interior=[v for v in dp['fixed_YZ_projection_checks'] if v['classification']=='strict_interior']
    assert len(interior)==2 and [v['owner'] for v in interior]==[v['owner'] for v in event['segments']]==[0,1]
    assert [v['primitive_id'] for v in interior]==[v['primitive_id'] for v in event['segments']]
    departure=event['departure_certificate']
    assert departure['owner']==0 and departure['primitive_id']==event['segments'][0]['primitive_id']
    assert departure['source_id']==event['source_id'] and departure['origin']=='derived-from-accepted-first-event-not-caller-previous-id'
    assert reported['restricted_entire_domain_event_chain_proved'] is True
r=json.loads((ROOT/REPORT).read_bytes());pins=pins_from(r)
for p,h in pins.items():assert sha((ROOT/p).read_bytes())==h,p
data=payload(r);assert data['PASS'] is True and data['tests']==4
a=data['data']['audit'];false(a);assert len(pins)==282 and a['inherited_pins_verified']==278
old=payload(read(r['inherited_pin_source']['path'],r['inherited_pin_source']['sha256']))['data']['audit']
mirror=payload(read(MIRROR,pins[MIRROR]))['data']['missing']['cases']
events=payload(read(EVENTS,pins[EVENTS]))['cases']
zero=payload(read(ZERO,pins[ZERO]))['data']['audit']
domains=payload(read(DOMAIN,pins[DOMAIN]))['data']['audit']
ingress='coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json';presence='coordinacion/respuestas/AXIAL-NATIVE-PRESENCE-STOPS-001-CODEX.json'
packets=payload(read(ingress,pins[ingress]))['packets']
packets.update({n:v['parent'] for n,v in payload(read(presence,pins[presence]))['synthetic_controls'].items()})
assert a['case_order']==old['case_order'] and len(a['case_order'])==17
count=stops=nonzero=xors=0
for n in a['case_order']:
    c=a['cases'][n];ctx=c['context'];false(c)
    assert ctx==old['cases'][n]['context']==mirror[n]['context']==zero['cases'][n]['context']==domains['cases'][n]['context']
    packet=packets[n];assert digest(packet)==ctx['input_packet_sha256']
    buffers={k:base64.b64decode(v,validate=True) for k,v in packet['buffers_base64'].items()}
    for role,raw in buffers.items():assert packet['manifest']['buffers'][role]=={'bytes':len(raw),'sha256':sha(raw)}
    meta=json.loads(buffers['input_metadata_json']);snap=json.loads(buffers['original_scene_json'])
    assert sha(buffers['original_scene_json'])==ctx['original_snapshot_sha256']==meta['original_snapshot_sha256']
    assert ctx['assignments']==meta['explicit_group_contract']['assignments']
    assert ctx['source_order']==meta['source_order']==[v['id'] for v in snap['sources']]
    assert [v['source_id'] for v in c['sources']]==ctx['source_order']
    for i,row in enumerate(c['sources']):
        false(row);src=old['cases'][n]['sources'][i];m=mirror[n]['sources'][i]
        assert row['retained_fixed_source_domain_row_sha256']==digest(src)
        assert row['retained_unit_polynomial_charge_fits']==src['retained_unit_polynomial_charge_fits'] and row['status']=='STOP'
        if not src['restricted_fixed_source_bare_product_error_to_ORIGINAL_proved']:
            if src['reason_provenance']=='unchanged_retained_unit_STOP':stops+=1
            else:nonzero+=1
            assert row['reason']==src['reason'] and row['reason_provenance']==src['reason_provenance']
            assert row['restricted_ideal_reflected_fixed_source_error_to_ORIGINAL_proved'] is False and 'proof' not in row
        else:
            count+=1;p=row['proof'];false(p);assert row['restricted_ideal_reflected_fixed_source_error_to_ORIGINAL_proved'] is True
            assert p['retained_fixed_source_domain_row_sha256']==digest(src) and p['retained_mirror_source_row_sha256']==digest(m)
            z=zero['cases'][n]['sources'][i];d=domains['cases'][n]['sources'][i];e=events[n]['sources'][i]
            assert src['proof']['retained_zero_unit_row_sha256']==digest(z) and z['proof']['retained_scene_domain_source_sha256']==digest(d)
            for k in ('case_name','input_packet_sha256','scene_binding_sha256','word_ABI_sha256','source_order'):assert events[n][k]==ctx[k]
            assert e['departure_certificate']['input_packet_sha256']==digest(packet)
            profile(snap,meta,e,d,p['profile'])
            assert m['retained_event_row_sha256']==digest(e)
            assert m['retained_product_row_sha256']==src['proof']['retained_source_product_row_sha256']
            assert m['mirror_profile']['mirror_phase_ORIGINAL_uint64']==p['profile']['fixed_ORIGINAL_mirror_phase_uint64']
            assert m['mirror_profile']['mirror_coefficient_exact_reim']==p['profile']['ideal_coefficient_exact_reim']
            assert m['coefficient_error_L1']==m['additional_rounding_error_L1']==[0,1]
            assignment=ctx['assignments'][i]
            assert m['phase_reference_id']==assignment['source_phase_reference_id'] and m['terminal_reference_id']==assignment['terminal_reference_id']
            assert len(p['retained_corner_identities'])==len(m['reflected_corner_products_HOST'])==len(src['proof']['graph_checks'])==4
            fixedwords=list(struct.unpack('<QQ',buffers['sources'][128*i+112:128*i+128]))
            assert buffers['sources'][128*i+112:128*i+128]==struct.pack('<dd',*snap['sources'][i]['field_reim'])
            for q,corner,g in zip(p['retained_corner_identities'],m['reflected_corner_products_HOST'],src['proof']['graph_checks']):
                assert q['retained_reflection_corner_sha256']==digest(corner)
                assert q['retained_product_sha256']==g['retained_product_sha256']==corner['retained_corner_product_sha256']
                assert corner['input_uint64']==g['retained_product_uint64']
                assert q['reflected_uint64']==corner['reflected_uint64']==[w^2**63 for w in corner['input_uint64']]
                before=list(map(binary,corner['input_uint64']));after=list(map(binary,corner['reflected_uint64']))
                assert after==[-v for v in before] and list(map(rat,q['reflected_rational']))==after
                assert list(map(rat,corner['reflected_rational']))==after and list(map(rat,corner['input_rational']))==before
                original=list(map(binary,fixedwords));assert g['fixed_original_source_uint64']==fixedwords
                assert list(map(rat,q['negated_fixed_ORIGINAL_source_rational']))==[-v for v in original]
                assert sum(abs(v+o) for v,o in zip(after,original))==rat(q['uniform_reflected_source_error_L1'])==F(1,2**55)
                assert q['additional_rounding_error_L1']==corner['additional_rounding_error_L1']==[0,1]
                assert corner['charges_L1_unchanged']==g['charges_L1']
                assert corner['new_RN64_operations']==q['new_RN_or_producer_executions']==0
                assert q['retained_sign_XOR_identities_checked']==corner['HOST_signbit_XORs']==2;xors+=2
            assert p['uniform_ideal_reflected_source_L1_error_to_fixed_ORIGINAL_bound']==m['reflected_source_error_L1_to_ORIGINAL_bound']==[1,2**55]
            assert p['additional_coefficient_error_L1']==p['additional_reflection_rounding_error_L1']==[0,1]
            assert p['missing_source_allocation_NOT_promoted'] is True and m['source_budget_evaluated'] is False
            assert m['accepted_reflected_source_product_budget_CPU_only'] is False
            assert p['retained_mirror_source_status']==row['status']==m['status']=='STOP'
            assert p['retained_mirror_source_reason']==row['reason']==m['reason'] and row['reason_provenance']==m['reason_provenance']
            assert p['new_RN_or_scene_producer_executions']==0 and p['nonzero_encoding_error_preserved'] is True
assert (count,stops,nonzero,xors)==(3,14,2,24)
assert (a['restricted_ideal_reflected_source_domains_proved'],a['retained_unit_STOPs'],a['nonzero_domains_not_refined'])==(count,stops,nonzero)
assert len(data['data']['rejections'])==41 and len({v['label'] for v in data['data']['rejections']})==41
controls=data['data']['SYNTHETIC_fixed_phase_controls'];assert len(controls)==2
assert [v['fixed_ORIGINAL_mirror_phase_uint64'] for v in controls]==[0,2**63]
assert all(v['ideal_coefficient_exact_reim']==[[-1,1],[0,1]] for v in controls)
false(r['proof_scope'])
print(json.dumps({'PASS':True,'pins':len(pins),'restricted_ideal_reflected_sources':count,'retained_STOPs':stops,
                  'nonzero_not_refined':nonzero,'retained_sign_XOR_identities':xors,'rejections':41,
                  'reflected_source_L1_error':[1,2**55],'new_RN_or_scene_producer_executions':0,
                  'native_material_or_physical_mirror_proved':False,'source_budget_promoted':False},sort_keys=True))
