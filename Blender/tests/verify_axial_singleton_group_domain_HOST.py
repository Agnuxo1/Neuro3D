"""Independent stdlib singleton group/receipt verification; no production imports."""
import base64,hashlib,json,math,zlib,struct
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT='coordinacion/respuestas/AXIAL-SINGLETON-GROUP-DOMAIN-HOST-001-CODEX.json'
REDUCTION='coordinacion/respuestas/AXIAL-GROUP-REDUCTION-HOST-001-CODEX.json'
TREE='coordinacion/respuestas/AXIAL-TREE-LINEAGE-HOST-001-CODEX.json'
MIRROR='coordinacion/respuestas/AXIAL-MIRROR-ZERO-HOST-001-CODEX.json'
FLAG='restricted_complete_singleton_group_error_to_ORIGINAL_proved'
FALSE=('scene_argument_enclosed','uniform_unit_error_to_ORIGINAL_proved','uniform_source_error_proved',
       'accepted_full_field_pipeline','remaining_stages_error_proved','execution_authenticated','coherence_authenticated',
       'native_kernel_implemented','GPU_executed','GPU_job_admission','whole_scene_parameter_enclosure_proved',
       'native_argument_implemented','general_3D_geometry_proved','physical_scene_uncertainty_certified',
       'native_signed_zero_graph_equivalence_proved','amplitude_budget_accepted','reflection_coefficient_applied',
       'field_values_computed','field_sum_computed','detector_evaluated','source_amplitude_uncertainty_enclosed',
       'native_material_transport_implemented','physical_mirror_model_validated','mirror_phase_uncertainty_enclosed',
       'reflection_coefficient_executed_new','uniform_group_error_proved','group_budget_accepted',
       'native_reduction_implemented','group_copy_executed_new')
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
r=json.loads((ROOT/REPORT).read_bytes());pins=pins_from(r)
for p,h in pins.items():assert sha((ROOT/p).read_bytes())==h,p
data=payload(r);assert data['PASS'] is True and data['tests']==4
a=data['data']['audit'];false(a);assert len(pins)==287 and a['inherited_pins_verified']==283
pr=read(r['inherited_pin_source']['path'],r['inherited_pin_source']['sha256'])
old=payload(pr)['data']['audit']
red=payload(read(REDUCTION,pins[REDUCTION]))['data']
tree=payload(read(TREE,pins[TREE]))['data']['audit']['cases']
mirror=payload(read(MIRROR,pins[MIRROR]))['data']['missing']['cases']
ingress='coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json'
presence='coordinacion/respuestas/AXIAL-NATIVE-PRESENCE-STOPS-001-CODEX.json'
packets=payload(read(ingress,pins[ingress]))['packets']
packets.update({n:v['parent'] for n,v in payload(read(presence,pins[presence]))['synthetic_controls'].items()})
assert a['case_order']==old['case_order'] and len(a['case_order'])==len(a['cases'])==17
proved=blocked=identities=0
for n in a['case_order']:
    c=a['cases'][n];ctx=c['context'];false(c)
    prior=old['cases'][n];assert ctx==prior['context'] and c['sources']==prior['sources']
    assert c['retained_source_domain_case_sha256']==digest(prior)
    missing=red['missing']['cases'][n];synthetic=red['explicit_synthetic_INPUT_controls']['cases'][n]
    assert ctx==missing['context']==synthetic['context']
    assert c['retained_missing_budget_case_sha256']==digest(missing)
    assert missing['allocation_result']['allocation_INPUT_valid'] is False and missing['stage_result']['stage_INPUT_valid'] is False
    assert all(g['accepted_retained_corner_group_reduction_CPU_only'] is False for g in missing['groups'])
    packet=packets[n];assert digest(packet)==ctx['input_packet_sha256']
    buffers={k:base64.b64decode(v,validate=True) for k,v in packet['buffers_base64'].items()}
    for role,raw in buffers.items():assert packet['manifest']['buffers'][role]=={'bytes':len(raw),'sha256':sha(raw)}
    meta=json.loads(buffers['input_metadata_json']);snap=json.loads(buffers['original_scene_json'])
    assert sha(buffers['original_scene_json'])==ctx['original_snapshot_sha256']==meta['original_snapshot_sha256']
    assert ctx['assignments']==meta['explicit_group_contract']['assignments']
    assert ctx['source_order']==meta['source_order']==[v['id'] for v in snap['sources']]
    assert [s['source_id'] for s in c['sources']]==[v['source_id'] for v in ctx['assignments']]==ctx['source_order']
    assert [[g['port'],g['coherence_group']] for g in c['groups']]==ctx['groups']
    for groupindex,(g,key) in enumerate(zip(c['groups'],ctx['groups'])):
        false(g);assert g['status']=='STOP' and g['group_budget_evaluated'] is False
        members=[(i,v,c['sources'][i]) for i,v in enumerate(ctx['assignments']) if [v['port'],v['coherence_group']]==key]
        assert members and g['source_order']==[v['source_id'] for i,v,s in members]
        unavailable=[s['source_id'] for i,v,s in members if s['restricted_ideal_reflected_fixed_source_error_to_ORIGINAL_proved'] is not True]
        if unavailable:
            blocked+=1;assert g[FLAG] is False and g['blocked_source_ids']==unavailable and 'proof' not in g and 'sum_uint64' not in g
            assert g['reason_provenance']=='unchanged_source_domain_blockers'
            continue
        assert len(members)==1 and n in ('positive','negative')
        proved+=1;i,assignment,src=members[0];p=g['proof'];false(p);assert g[FLAG] is True and p[FLAG] is True
        assert src['status']=='STOP' and src['reason_provenance']=='missing_static_INPUT_allocation'
        assert g['reason_provenance']=='missing_static_INPUT_allocation'
        assert p['complete_source_order']==g['source_order']
        sp=src['proof'];m=mirror[n]['sources'][i];tr=tree[n];rg=synthetic['groups'][groupindex]
        assert ctx==mirror[n]['context']==tr['context']
        assert p['retained_reflected_source_row_sha256']==digest(src) and sp['retained_mirror_source_row_sha256']==digest(m)
        assert p['retained_reduction_group_sha256']==digest(rg) and p['retained_tree_row_sha256']==digest(tr)==synthetic['retained_tree_row_sha256']
        assert tr['tree_lineage_matches_restricted_CPU_only'] is True and tr['input_packet_sha256']==ctx['input_packet_sha256']
        assert tr['sources'][i]['native_event_row_sha256']==m['retained_event_row_sha256']
        assert tr['retained_source_product_row_sha256s'][i]==m['retained_product_row_sha256']
        assert p['certificate_sha256']==rg['certificate_sha256']==tr['certificate_sha256']
        assert p['terminal_reference_id']==assignment['terminal_reference_id']==assignment['common_terminal_reference_id'] and rat(assignment['rebase_cycles'])==0
        assert p['grouping_provenance']==ctx['grouping_provenance']
        assert p['missing_source_and_stage_allocation_NOT_promoted'] is True and p['synthetic_budget_admission_NOT_inherited'] is True
        assert sp['missing_source_allocation_NOT_promoted'] is True and sp['profile']['restricted_entire_domain_event_chain_proved'] is True
        assert len(p['retained_copy_identities'])==len(sp['retained_corner_identities'])==len(rg['corner_sums'])==4
        originalwords=list(struct.unpack('<QQ',buffers['sources'][128*i+112:128*i+128]))
        assert buffers['sources'][128*i+112:128*i+128]==struct.pack('<dd',*snap['sources'][i]['field_reim'])
        original=[-binary(w) for w in originalwords];constant=None
        for cornerindex,(q,su,rc) in enumerate(zip(p['retained_copy_identities'],sp['retained_corner_identities'],rg['corner_sums'])):
            assert q['source_identity_sha256']==digest(su) and q['reduction_corner_sha256']==digest(rc)
            w=su['reflected_uint64'];v=list(map(binary,w))
            assert constant is None or w==constant;constant=w
            assert q['retained_copy_uint64']==rc['sum_uint64']==w and rc['source_uint64']==[w]
            assert rc['corner_indices']==[cornerindex] and w[1]==2**63
            assert list(map(rat,su['negated_fixed_ORIGINAL_source_rational']))==original
            assert sum(abs(x-y) for x,y in zip(v,original))==rat(su['uniform_reflected_source_error_L1'])==F(1,2**55)
            assert list(map(rat,rc['sum_rational']))==list(map(rat,rc['exact_represented_sources_sum']))==v
            assert type(rc['RN64_additions']) is int and rc['RN64_additions']==0 and rc['trace']==[]
            assert rat(rc['rounding_error_L1_bound'])==rat(rc['actual_error_L1_to_represented_sum'])==0
            assert q['bit_copy_identities_checked']==2 and q['new_RN_or_copy_executions']==0;identities+=2
        assert rat(p['uniform_group_L1_error_to_fixed_ORIGINAL_bound'])==rat(rg['source_errors_L1_sum'])==rat(rg['error_L1_to_ORIGINAL_group_corner_sum_bound'])==F(1,2**55)
        assert p['reduction_rounding_error_L1']==rg['reduction_RN64_error_L1_bound']==[0,1]
        assert p['new_RN_or_copy_or_scene_producer_executions']==0
assert (proved,blocked,identities)==(2,15,16)
assert (a['restricted_complete_singleton_groups_proved'],a['blocked_complete_groups'],a['retained_bit_copy_identities'])==(proved,blocked,identities)
assert (a['retained_unit_STOPs'],a['nonzero_domains_not_refined'])==(14,2)
two=a['cases']['two_sources']['groups'][0]
assert two['source_order']==['s','other'] and two['blocked_source_ids']==['other'] and 'proof' not in two
d=a['predecessor_metadata_discrepancy'];assert d==data['data']['metadata_discrepancy']
assert d['recorded_rational']==pr['evidence']['unchanged_per_source_L1_error']==[1,36028797018963970]
assert d['captured_audit_rational']==[1,36028797018963968] and rat(d['recorded_rational'])!=rat(d['captured_audit_rational'])
assert d['metadata_matches_captured_audit'] is False and d['predecessor_modified'] is False
assert len(data['data']['rejections'])==len({v['label'] for v in data['data']['rejections']})==38
false(r['proof_scope'])
bound=r['evidence']['exact_uniform_group_L1_error_decimal_rational']
assert F(int(bound['numerator']),int(bound['denominator']))==F(1,2**55)
print(json.dumps({'PASS':True,'pins':len(pins),'restricted_complete_singleton_groups':proved,'blocked_complete_groups':blocked,
                  'retained_bit_copy_identities':identities,'rejections':38,'new_RN_or_scene_producer_executions':0,
                  'group_L1_error_decimal':'1/36028797018963968','predecessor_metadata_mismatch_preserved':True,
                  'source_or_group_budget_promoted':False,'full_pipeline_proved':False},sort_keys=True))
