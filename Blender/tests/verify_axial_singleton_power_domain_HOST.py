"""Independent stdlib audit of restricted uniform retained power; no production imports."""
import base64,hashlib,json,math,struct,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT='coordinacion/respuestas/AXIAL-SINGLETON-POWER-DOMAIN-HOST-001-CODEX.json'
POWER='coordinacion/respuestas/AXIAL-GROUP-POWER-HOST-001-CODEX.json'
RED='coordinacion/respuestas/AXIAL-GROUP-REDUCTION-HOST-001-CODEX.json'
REFLECTED='coordinacion/respuestas/AXIAL-REFLECTED-SOURCE-DOMAIN-HOST-001-CODEX.json'
GF='restricted_complete_singleton_group_error_to_ORIGINAL_proved'
PF='restricted_complete_singleton_power_error_to_ORIGINAL_proved'
FALSE=('scene_argument_enclosed','uniform_unit_error_to_ORIGINAL_proved','uniform_source_error_proved',
       'accepted_full_field_pipeline','remaining_stages_error_proved','execution_authenticated','coherence_authenticated',
       'native_kernel_implemented','GPU_executed','GPU_job_admission','whole_scene_parameter_enclosure_proved',
       'native_argument_implemented','general_3D_geometry_proved','physical_scene_uncertainty_certified',
       'native_signed_zero_graph_equivalence_proved','amplitude_budget_accepted','reflection_coefficient_applied',
       'field_values_computed','field_sum_computed','detector_evaluated','source_amplitude_uncertainty_enclosed',
       'native_material_transport_implemented','physical_mirror_model_validated','mirror_phase_uncertainty_enclosed',
       'reflection_coefficient_executed_new','uniform_group_error_proved','group_budget_accepted',
       'native_reduction_implemented','group_copy_executed_new','uniform_power_error_proved',
       'power_budget_accepted','native_power_implemented','power_executed_new')
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
def b64(w):
    assert type(w) is int and 0<=w<2**64
    e=w//2**52%2048;m=w%2**52;assert e<2047 and (e!=0 or m==0)
    return (-1 if w>=2**63 else 1)*F(m+(2**52 if e else 0))*F(2)**(e-1075)
def false(v):
    for k in FALSE:assert v[k] is False,k
r=json.loads((ROOT/REPORT).read_bytes());pins=pins_from(r)
for p,h in pins.items():assert sha((ROOT/p).read_bytes())==h,p
data=payload(r);assert data['PASS'] is True and data['tests']==4
a=data['data']['audit'];false(a);assert len(pins)==292 and a['inherited_pins_verified']==288
pr=read(r['inherited_pin_source']['path'],r['inherited_pin_source']['sha256']);old=payload(pr)['data']['audit']
power=payload(read(POWER,pins[POWER]))['data']
red=payload(read(RED,pins[RED]))['data']['explicit_synthetic_INPUT_controls']['cases']
ref=payload(read(REFLECTED,pins[REFLECTED]))['data']['audit']['cases']
ingress='coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json'
presence='coordinacion/respuestas/AXIAL-NATIVE-PRESENCE-STOPS-001-CODEX.json'
packets=payload(read(ingress,pins[ingress]))['packets']
packets.update({n:v['parent'] for n,v in payload(read(presence,pins[presence]))['synthetic_controls'].items()})
assert a['case_order']==old['case_order'] and len(a['cases'])==17
proved=blocked=cells=zero_cells=0;uniform_absolute=None;uniform_relative=None
for n in a['case_order']:
    c=a['cases'][n];ctx=c['context'];prior=old['cases'][n];false(c)
    assert ctx==prior['context'] and c['retained_sources_sha256']==digest(prior['sources'])
    packet=packets[n];assert digest(packet)==ctx['input_packet_sha256']
    buffers={k:base64.b64decode(v,validate=True) for k,v in packet['buffers_base64'].items()}
    for role,raw in buffers.items():assert packet['manifest']['buffers'][role]=={'bytes':len(raw),'sha256':sha(raw)}
    meta=json.loads(buffers['input_metadata_json']);snap=json.loads(buffers['original_scene_json'])
    assert sha(buffers['original_scene_json'])==ctx['original_snapshot_sha256']==meta['original_snapshot_sha256']
    assert ctx['assignments']==meta['explicit_group_contract']['assignments']
    assert ctx['source_order']==meta['source_order']==[s['id'] for s in snap['sources']]
    assert [[g['port'],g['coherence_group']] for g in c['groups']]==ctx['groups']
    for gi,(g,og) in enumerate(zip(c['groups'],prior['groups'])):
        false(g);assert g['retained_complete_group_row_sha256']==digest(og)
        assert g['status']=='STOP' and g['power_budget_evaluated'] is False and g['source_order']==og['source_order']
        if og[GF] is not True:
            blocked+=1;assert g[PF] is False and 'proof' not in g and g['reason']==og['reason']
            assert g['reason_provenance']=='unchanged_complete_group_domain_STOP'
            if 'blocked_source_ids' in og:assert g['blocked_source_ids']==og['blocked_source_ids']
            continue
        proved+=1;p=g['proof'];false(p);assert g[PF] is True and p[PF] is True
        assert n in ('positive','negative') and p['complete_source_order']==og['source_order']==['s']
        gp=og['proof'];pc=power['explicit_synthetic_INPUT_controls']['cases'][n]
        assert ctx==pc['context']==red[n]['context']==ref[n]['context']
        pg=pc['groups'][gi];rg=red[n]['groups'][gi]
        assert p['retained_uniform_group_row_sha256']==digest(og) and p['retained_power_group_sha256']==digest(pg)
        assert pg['retained_group_row_sha256']==digest(rg)==gp['retained_reduction_group_sha256']
        assert pg['source_order']==rg['source_order']==p['complete_source_order']
        assert pg['unchanged_original_limits']==ctx['unchanged_limits']
        sourceindex=ctx['source_order'].index('s');src=ref[n]['sources'][sourceindex]
        assert gp['retained_reflected_source_row_sha256']==digest(src) and src['restricted_ideal_reflected_fixed_source_error_to_ORIGINAL_proved'] is True
        ow=list(struct.unpack('<QQ',buffers['sources'][128*sourceindex+112:128*sourceindex+128]))
        assert buffers['sources'][128*sourceindex+112:128*sourceindex+128]==struct.pack('<dd',*snap['sources'][sourceindex]['field_reim'])
        original=[-b64(w) for w in ow];op=sum(v*v for v in original)
        assert op>0 and rat(p['fixed_ORIGINAL_power_exact'])==op
        assert len(p['retained_corner_checks'])==len(pg['power_corners'])==len(gp['retained_copy_identities'])==len(rg['corner_sums'])==4
        wordconstant=None;groupabs=None;grouprel=None;envelope=None;roundingconstant=None
        for i,(q,c,copy,rd,sc) in enumerate(zip(p['retained_corner_checks'],pg['power_corners'],gp['retained_copy_identities'],rg['corner_sums'],src['proof']['retained_corner_identities'])):
            assert q['retained_power_corner_sha256']==digest(c) and q['retained_copy_identity_sha256']==digest(copy)
            assert copy['reduction_corner_sha256']==digest(rd)==c['retained_field_corner_sha256']
            assert copy['source_identity_sha256']==digest(sc)
            words=copy['retained_copy_uint64'];assert words==c['input_uint64']==rd['sum_uint64']==sc['reflected_uint64']
            assert list(map(rat,sc['negated_fixed_ORIGINAL_source_rational']))==original
            assert wordconstant is None or words==wordconstant;wordconstant=words
            values=list(map(b64,words));assert c['corner_indices']==[i] and len(c['trace'])==len(q['RN_cell_checks'])==3
            assert type(c['RN64_operations']) is int and c['RN64_operations']==3
            t=c['trace'];ops=[('mul',words[0],words[0]),('mul',words[1],words[1]),('add',t[0]['output_uint64'],t[1]['output_uint64'])]
            rounding=F(0)
            for node,cell,(operation,left,right) in zip(t,q['RN_cell_checks'],ops):
                assert node['op']==operation and node['left_uint64']==left and node['right_uint64']==right
                exact=b64(left)*b64(right) if operation=='mul' else b64(left)+b64(right)
                assert rat(node['exact_rational'])==exact>=0
                w=node['output_uint64'];value=b64(w);assert 0<=w<2**63
                assert cell['recorded_uint64']==w and cell['new_RN_executions']==0
                if w==0:
                    assert exact==0 and cell['exact_zero_identity'] is True;zero_cells+=1
                else:
                    low=(b64(w-1)+value)/2;high=(value+b64(w+1))/2;even=w%2==0
                    assert low<exact<high or (even and exact in (low,high))
                    assert rat(cell['lower_midpoint'])==low and rat(cell['upper_midpoint'])==high
                    assert cell['ties_included'] is even and cell['exact_zero_identity'] is False
                err=abs(value-exact);assert rat(node['rounding_error_abs'])==err;rounding+=err;cells+=1
            observed=b64(t[-1]['output_uint64']);represented=sum(v*v for v in values)
            assert q['retained_power_uint64']==c['observed_power_uint64']==t[-1]['output_uint64']
            assert rat(c['observed_power_rational'])==observed and rat(c['represented_input_power_exact'])==represented
            B=rat(gp['uniform_group_L1_error_to_fixed_ORIGINAL_bound']);assert B==rat(c['input_field_L1_error_bound'])==F(1,2**55)
            M=max(map(abs,values));propagation=2*M*B+B*B;combined=propagation+rounding;lower=(M-B)**2
            assert M>B and rat(c['ORIGINAL_power_lower_bound'])==lower
            assert rat(c['actual_error_abs_to_represented_power'])==abs(observed-represented)
            assert rat(c['field_to_power_error_abs_bound'])==propagation and rat(c['power_RN64_error_abs_bound'])==rounding
            assert rat(c['combined_error_abs_to_ORIGINAL_power_bound'])==combined and rat(c['relative_power_error_bound'])==combined/lower
            absolute=abs(observed-op);relative=absolute/op
            assert absolute>0 and rat(q['exact_absolute_error_to_fixed_ORIGINAL_power'])==absolute<=combined
            assert rat(q['exact_relative_error_to_fixed_ORIGINAL_power'])==relative<=combined/lower
            assert groupabs is None or (absolute,relative,combined,rounding)==(groupabs,grouprel,envelope,roundingconstant)
            groupabs,grouprel,envelope,roundingconstant=absolute,relative,combined,rounding
            assert q['new_RN_or_producer_executions']==0
        assert rat(p['uniform_exact_absolute_power_error'])==groupabs and rat(p['uniform_exact_relative_power_error'])==grouprel
        assert rat(p['retained_conservative_absolute_power_bound'])==rat(pg['combined_error_abs_to_ORIGINAL_power_bound'])==envelope
        assert rat(p['retained_power_RN64_error_abs_bound'])==rat(pg['power_RN64_error_abs_bound'])==roundingconstant
        assert p['synthetic_power_budget_admission_NOT_inherited'] is True and p['missing_allocation_NOT_promoted'] is True
        assert p['new_RN_or_copy_or_scene_producer_executions']==0
        assert uniform_absolute is None or (uniform_absolute,uniform_relative)==(groupabs,grouprel)
        uniform_absolute,uniform_relative=groupabs,grouprel
assert (proved,blocked,cells,zero_cells)==(2,15,24,8)
assert (a['restricted_complete_singleton_power_groups_proved'],a['blocked_complete_groups'],a['retained_RN_cell_checks'])==(proved,blocked,cells)
assert (a['retained_unit_STOPs'],a['nonzero_domains_not_refined'])==(14,2)
for variant,controls in a['retained_zero_budget_FAIL_controls'].items():
    for n,v in controls.items():
        retained=power[variant]['cases'][n]
        assert v['retained_case_sha256']==digest(retained) and v['group_statuses']==['FAIL'] and v['accepted_groups']==[False]
assert len(data['data']['rejections'])==len({v['label'] for v in data['data']['rejections']})==40
assert len(data['data']['SYNTHETIC_cell_controls'])==4
false(r['proof_scope'])
bound=r['evidence']['exact_bounds_decimal']
assert F(*map(int,bound['uniform_exact_absolute_power_error']))==uniform_absolute
assert F(*map(int,bound['uniform_exact_relative_power_error']))==uniform_relative
print(json.dumps({'PASS':True,'pins':len(pins),'restricted_uniform_power_groups':proved,'blocked_complete_groups':blocked,
 'retained_RN_cell_checks':cells,'retained_exact_zero_nodes':zero_cells,'rejections':40,
 'exact_absolute_power_error_decimal':[str(uniform_absolute.numerator),str(uniform_absolute.denominator)],
 'new_RN_or_scene_producer_executions':0,'power_budget_promoted':False,'physical_detector_or_fullpipeline_proved':False},sort_keys=True))
