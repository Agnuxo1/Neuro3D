"""Independent static INPUT budget oracle; stdlib, no production imports."""
import base64,hashlib,json,math,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT='coordinacion/respuestas/AXIAL-STAGE-ALLOCATION-HOST-001-CODEX.json'
PREVIOUS='coordinacion/respuestas/AXIAL-IDEAL-REFLECTION-STAGE-CPU-001-CODEX.json'
PREVIOUS_SHA='a336c4c8defd4deb1330e33cae46f4180e84a48dc7e227adea49e85061aaa8bc'
MODEL='axial-static-seven-stage-L1-allocation-HOST-v1'
BASE_MODEL='axial-static-amplitude-L1-allocation-HOST-v1'
UNITS='ORIGINAL-source-field-amplitude-L1'
STAGES=('source_encoding_L1','source_decode_RN64_L1','source_Horner_L1','source_decoded_argument_L1','source_geometry_reference_wavelength_L1','source_product_RN64_L1','ideal_material_L1')
RESERVES=('reduction_L1','terminal_projection_L1')
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
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
def q(v):
    assert type(v) is list and len(v)==2 and all(type(x) is int for x in v)
    assert v[0]>=0 and v[1]>0 and math.gcd(*v)==1;return F(*v)
def pair(v):return [v.numerator,v.denominator]
def allfalse(v):
    for k in FALSE:assert v[k] is False,k
def context(packet):
    bs={k:base64.b64decode(v,validate=True) for k,v in packet['buffers_base64'].items()}
    assert set(bs)=={'triangles','sources','wavelength','reference','original_scene_json','input_metadata_json'}
    for k,b in bs.items():assert packet['manifest']['buffers'][k]=={'bytes':len(b),'sha256':sha(b)}
    meta=json.loads(bs['input_metadata_json']);snap=json.loads(bs['original_scene_json']);g=meta['explicit_group_contract']
    assert meta['original_snapshot_sha256']==sha(bs['original_scene_json'])
    ids=meta['source_order'];ass=g['assignments'];assert ids==[s['id'] for s in snap['sources']]==[s['source_id'] for s in ass]
    assert len(ids)==len(set(ids)) and g['scene_binding_sha256']==meta['scene_binding_sha256']
    groups=[]
    for a in ass:
        assert a['source_phase_reference_id']=='original-source-zero:'+meta['scene_binding_sha256']+':'+a['source_id']
        key=[a['port'],a['coherence_group']]
        if key not in groups:groups.append(key)
    return {'model':BASE_MODEL,'units':UNITS,'case_name':meta['case_name'],'input_packet_sha256':digest(packet),
        'scene_binding_sha256':meta['scene_binding_sha256'],'word_ABI_sha256':meta['word_ABI_sha256'],
        'original_snapshot_sha256':meta['original_snapshot_sha256'],'original_group_contract_sha256':digest(g),
        'source_order':ids,'assignments':ass,'groups':groups,'unchanged_field_L1_cap':pair(q(g['limits']['field_L1'])),
        'unchanged_limits':g['limits'],'grouping_provenance':g['grouping_provenance'],
        'execution_authenticated':False,'coherence_authenticated':False}
def verify_plan(plan,ctx,p):
    assert set(plan)=={'model','units','context_sha256','sources','groups'}
    assert plan['model']==MODEL and plan['units']==UNITS and plan['context_sha256']==digest(ctx)
    ss=plan['sources'];gs=plan['groups'];cap=q(ctx['unchanged_field_L1_cap'])
    assert [s['source_id'] for s in ss]==ctx['source_order'] and [[g['port'],g['coherence_group']] for g in gs]==ctx['groups']
    assert p['allocation_INPUT_valid'] is True and p['context_sha256']==digest(ctx) and p['plan_sha256']==digest(plan)
    assert p['groups']==gs and p['unchanged_limits']==ctx['unchanged_limits'];allfalse(p)
    for s,row in zip(ss,p['sources']):
        assert set(s)=={'source_id','cap_L1','stages_L1'} and set(s['stages_L1'])==set(STAGES)
        spent=sum((q(s['stages_L1'][k]) for k in STAGES),F(0));c=q(s['cap_L1']);assert spent<=c
        assert row=={'source_id':s['source_id'],'cap_L1':s['cap_L1'],'stages_L1':s['stages_L1'],
            'stage_caps_sum_L1':pair(spent),'unallocated_source_L1':pair(c-spent)}
    old=p['projected_legacy_input_accounting'];assert old['allocation_INPUT_valid'] is True
    assert old['context_sha256']==digest(ctx) and old['source_order']==ctx['source_order']
    assert old['source_caps_L1']=={s['source_id']:s['cap_L1'] for s in ss}
    projected={'model':BASE_MODEL,'units':UNITS,'context_sha256':digest(ctx),
        'sources':[{'source_id':s['source_id'],'cap_L1':s['cap_L1']} for s in ss],'groups':[]}
    for g,row in zip(gs,old['groups']):
        assert set(g)=={'port','coherence_group','reserves_L1'} and set(g['reserves_L1'])==set(RESERVES)
        members=[a['source_id'] for a in ctx['assignments'] if a['port']==g['port'] and a['coherence_group']==g['coherence_group']]
        total=sum((q(s['cap_L1']) for s in ss if s['source_id'] in members),F(0))
        reserve=sum((q(g['reserves_L1'][k]) for k in RESERVES),F(0));assert total+reserve<=cap
        assert row=={'port':g['port'],'coherence_group':g['coherence_group'],'source_order':members,
            'source_caps_sum_L1':pair(total),'remaining_stages_reserved_L1':pair(reserve),
            'unchanged_group_field_L1_cap':pair(cap),'unallocated_L1':pair(cap-total-reserve)}
        projected['groups'].append({'port':g['port'],'coherence_group':g['coherence_group'],'remaining_stages_reserved_L1':pair(reserve)})
    assert old['allocation_sha256']==digest(projected) and old['unchanged_limits']==ctx['unchanged_limits']
    for k in ('amplitude_budget_accepted','source_product_gate_evaluated','remaining_stages_error_proved','field_values_computed',
            'detector_evaluated','coherence_authenticated','execution_authenticated','accepted_full_field_pipeline','GPU_executed'):assert old[k] is False
def verify_audit(a,plans):
    assert a['model']==MODEL and a['inherited_pins_verified']==353
    valid=missing=fit=0;allfalse(a)
    for n in a['case_order']:
        ctx=context(packets[n]);c=a['cases'][n];assert c['context']==old['cases'][n]['context']==ctx and c['status']=='STOP';allfalse(c)
        p=c['allocation_INPUT'];allfalse(p)
        if n not in plans:
            missing+=1;assert p['allocation_INPUT_valid'] is False and 'missing' in p['reason']
            for row,sid in zip(c['sources'],ctx['source_order']):
                assert row['source_id']==sid and row['stage_comparisons'] is None and row['retained_point_stage_budget_fits'] is False;allfalse(row)
            continue
        plan=plans[n];verify_plan(plan,ctx,p);valid+=1
        for row,prev,sp in zip(c['sources'],old['cases'][n]['sources'],plan['sources']):
            allfalse(row);assert row['source_id']==prev['source_id']==sp['source_id'] and row['retained_source_row_sha256']==digest(prev)
            if not prev['ideal_reflection_CPU_executed']:
                assert row['stage_comparisons'] is None and row['retained_point_stage_budget_fits'] is False and row['reason']==prev['reason'];continue
            r=prev['result'];charges={k:q(v) for k,v in r['charges_L1'].items()}
            assert r['profile']['ideal_coefficient_exact_reim']==[[-1,1],[0,1]]
            material=q(r['profile']['new_coefficient_error_L1'])+q(r['additional_reflection_rounding_error_L1']);assert material==0
            charges['ideal_material_L1']=material;assert set(charges)==set(STAGES)
            total=sum(charges.values(),F(0));assert pair(total)==r['point_reflected_source_to_fixed_ORIGINAL_bound_L1']
            checks={k:{'charge_L1':pair(charges[k]),'quota_L1':sp['stages_L1'][k],'fits':charges[k]<=q(sp['stages_L1'][k])} for k in STAGES}
            tf=total<=q(sp['cap_L1']);good=tf and all(v['fits'] for v in checks.values())
            assert row['stage_comparisons']==checks and row['sum_charges_L1']==pair(total) and row['source_cap_L1']==sp['cap_L1']
            assert row['total_charge_fits_source_cap'] is tf and row['retained_point_stage_budget_fits'] is good
            fit+=int(good)
    assert (a['explicit_INPUT_plans_valid'],a['missing_INPUT_plans_STOP'],a['retained_point_source_stage_comparisons_fit'])==(valid,missing,fit)
    assert a['new_numeric_scene_source_material_reduction_power_readout_executions']==a['old_suites_producers_reexecuted']==0 and a['allocation_policy_adopted'] is False
    return valid,missing,fit
r=json.loads((ROOT/REPORT).read_bytes());assert r['task_id']=='AXIAL-STAGE-ALLOCATION-HOST-001'
assert r['base_commit']=='471534cbcde4eb2f3f3c92dc33f96413c7c52f56' and r['inherited_pin_source']=={'path':PREVIOUS,'sha256':PREVIOUS_SHA}
pins=pins_from(r)
for p,h in pins.items():assert sha((ROOT/p).read_bytes())==h,p
assert len(pins)==357
FALSE=tuple(r['proof_scope']);assert len(FALSE)==38 and all(v is False for v in r['proof_scope'].values())
old=payload(read(PREVIOUS,PREVIOUS_SHA))['data']['audit']
ip='coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json';pp='coordinacion/respuestas/AXIAL-NATIVE-PRESENCE-STOPS-001-CODEX.json'
packets=payload(read(ip,pins[ip]))['packets']
packets.update({n:v['parent'] for n,v in payload(read(pp,pins[pp]))['synthetic_controls'].items()})
raw=payload(r);assert raw['PASS'] is True and raw['tests']==4;d=raw['data']
real=verify_audit(d['real_absent'],{});assert real==(0,17,0)
assert sum(len(c['sources']) for c in d['real_absent']['cases'].values())==19
plans=d['synthetic_INPUT_plans']
# Verify quotas are fixed INPUT-only control policy, not fitted to retained charges.
for n,p in plans.items():
    ctx=context(packets[n]);cap=q(ctx['unchanged_field_L1_cap'])
    for s in p['sources']:
        assert s['cap_L1']==pair(cap/4) and s['stages_L1']==dict.fromkeys(STAGES,[1,10**14])
    for g in p['groups']:
        members=sum(a['port']==g['port'] and a['coherence_group']==g['coherence_group'] for a in ctx['assignments'])
        assert g['reserves_L1']==dict.fromkeys(RESERVES,pair((cap-members*cap/4)/2))
assert verify_audit(d['synthetic_comparisons'],plans)==(3,0,2)
c=d['stage_overspend_control'];n='nonexact_geometry_phase_PASS'
assert verify_audit(c['audit'],{n:c['INPUT_plan']})==(1,0,0)
row=c['audit']['cases'][n]['sources'][0]
assert row['total_charge_fits_source_cap'] is True and row['stage_comparisons']['source_Horner_L1']['fits'] is False
assert c['INPUT_plan']['sources'][0]['stages_L1']['source_Horner_L1']==[0,1]
z=d['explicit_zero_FAIL'];assert verify_audit(z['audit'],{'thin_resolved':z['INPUT_plan']})==(1,0,0)
assert z['INPUT_plan']['sources'][0]['cap_L1']==[0,1] and all(q(v)==0 for v in z['INPUT_plan']['sources'][0]['stages_L1'].values())
rejects=d['rejections'];assert len(rejects)==len({v['label'] for v in rejects})==25 and d['atomic_comparison_calls']==0
print(json.dumps({'PASS':True,'pins':len(pins),'real_missing_plans_STOP':17,'real_sources_STOP':19,
 'synthetic_plans_valid':3,'partial_point_comparisons_fit':2,'total_fit_stage_overspend_FAIL_preserved':True,
 'explicit_zero_FAIL_preserved':True,'atomic_comparisons_before_all_plans_valid':0,'rejections':25,
 'numeric_producers_executed':0,'allocation_policy_adopted':False,'fullpipeline_GPU_admitted':False},sort_keys=True))
