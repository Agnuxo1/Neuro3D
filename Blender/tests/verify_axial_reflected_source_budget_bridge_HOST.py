"""Independent stdlib reflected-source seven-quota oracle. No production imports."""
import base64,hashlib,json,math,struct,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT='coordinacion/respuestas/AXIAL-REFLECTED-SOURCE-BUDGET-BRIDGE-HOST-001-CODEX.json'
PARENT='coordinacion/respuestas/AXIAL-CURRENT-SOURCE-IDEAL-REFLECTION-CPU-001-CODEX.json'
PARENT_SHA='474304cf3366616beb1f725e2e3e1e8bbf8735bf34f8d5b55bd11ddbd4f2965d'
MAT='coordinacion/respuestas/AXIAL-SOURCE-MATERIAL-ADMISSION-HOST-001-CODEX.json'
ROOTS='coordinacion/respuestas/AXIAL-GUARDED-HILO-XROOT-RN64-CPU-001-CODEX.json'
SOURCE='coordinacion/respuestas/AXIAL-GUARDED-SOURCE-PRODUCT-RN64-CPU-001-CODEX.json'
PLAN='coordinacion/respuestas/AXIAL-STAGE-ALLOCATION-HOST-001-CODEX.json'
OWN_MODEL='axial-current-reflected-source-fifteen-to-seven-stage-L1-HOST-v1'
MODEL='axial-static-seven-stage-L1-allocation-HOST-v1'
BASE_MODEL='axial-static-amplitude-L1-allocation-HOST-v1'
UNITS='ORIGINAL-source-field-amplitude-L1'
SIGN=1<<63
STAGES=('source_encoding_L1','source_decode_RN64_L1','source_Horner_L1','source_decoded_argument_L1','source_geometry_reference_wavelength_L1','source_product_RN64_L1','ideal_material_L1')
RESERVES=('reduction_L1','terminal_projection_L1')
MAPPING={
 'source_encoding_L1':['source_encoding_L1'],
 'source_decode_RN64_L1':['source_decode_RN64_L1'],
 'source_Horner_L1':['source_unit_coefficient_L1','source_unit_square_L1','source_unit_RN_nodes_L1','source_unit_Taylor_L1'],
 'source_decoded_argument_L1':['source_unit_quotient_RN64_L1','source_unit_quarter_subtraction_RN64_L1','source_unit_constant_2pi_L1','source_unit_argument_multiply_RN64_L1'],
 'source_geometry_reference_wavelength_L1':['source_unit_geometry_representation_L1','source_unit_Xroot_length_rounding_L1','source_unit_wavelength_representation_L1'],
 'source_product_RN64_L1':['source_product_RN64_L1'],'ideal_material_L1':['ideal_material_L1']}
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(x):return sha(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def read(p,h):
    b=(ROOT/p).read_bytes();assert sha(b)==h,p;return json.loads(b)
def payload(r):
    t=r['test_run'];assert t['rc']==0 and t.get('timed_out',False) is False
    b=zlib.decompress(base64.b64decode(t.get('stdout_zlib_base64') or ''.join(t['stdout_zlib_base64_chunks']),validate=True))
    assert len(b)==t['stdout_bytes'] and sha(b)==t['stdout_sha256']
    v=json.loads(b);assert v['PASS'] is True;return v
def q(x):
    assert type(x) is list and len(x)==2 and all(type(a) is int for a in x)
    assert x[1]>0 and math.gcd(*x)==1;return F(*x)
def context(packet):
    bs={k:base64.b64decode(v,validate=True) for k,v in packet['buffers_base64'].items()}
    assert set(bs)=={'triangles','sources','wavelength','reference','original_scene_json','input_metadata_json'}
    for k,b in bs.items():assert packet['manifest']['buffers'][k]=={'bytes':len(b),'sha256':sha(b)}
    m=json.loads(bs['input_metadata_json']);s=json.loads(bs['original_scene_json']);g=m['explicit_group_contract']
    assert m['original_snapshot_sha256']==sha(bs['original_scene_json'])
    ids=m['source_order'];ass=g['assignments'];assert ids==[x['id'] for x in s['sources']]==[x['source_id'] for x in ass]
    groups=[]
    for t in ass:
        assert t['source_phase_reference_id']=='original-source-zero:'+m['scene_binding_sha256']+':'+t['source_id']
        key=[t['port'],t['coherence_group']]
        if key not in groups:groups.append(key)
    c={'model':'axial-static-amplitude-L1-allocation-HOST-v1','units':'ORIGINAL-source-field-amplitude-L1','case_name':m['case_name'],
       'input_packet_sha256':digest(packet),'scene_binding_sha256':m['scene_binding_sha256'],'word_ABI_sha256':m['word_ABI_sha256'],
       'original_snapshot_sha256':m['original_snapshot_sha256'],'original_group_contract_sha256':digest(g),
       'source_order':ids,'assignments':ass,'groups':groups,'unchanged_field_L1_cap':[q(g['limits']['field_L1']).numerator,q(g['limits']['field_L1']).denominator],
       'unchanged_limits':g['limits'],'grouping_provenance':g['grouping_provenance'],'execution_authenticated':False,'coherence_authenticated':False}
    return c,s,m,bs
def profile(s,m,sid,fixed,decoded):
    assert set(s['objects'])=={'M','D'} and s['undeclared_meshes']==[]
    assert m['object_ids']==['M','D'] and m['kinds']==['mirror','det'] and sid in m['source_order']
    owners=[]
    for o,name,kind in ((0,'M','mirror'),(1,'D','det')):
        ob=s['objects'][name];assert ob['kind']==kind
        v,faces=ob['vertices_world_BU'],ob['faces']
        assert type(v) is list and 3<=len(v)<=192 and all(type(t) is list and len(t)==3 and all(type(a) is float for a in t) for t in v)
        assert type(faces) is list and 1<=len(faces)<=64
        for face in faces:
            assert type(face) is list and len(face)==3 and len(set(face))==3
            assert all(type(i) is int and 0<=i<len(v) for i in face)
            owners.append({'primitive_id':len(owners),'owner':o,'object_id':name,'kind':kind,'face':face})
    assert len(owners)<=64
    assert type(s['objects']['M']['phase_rad']) is float
    w=struct.unpack('<Q',struct.pack('<d',s['objects']['M']['phase_rad']))[0];assert w in (0,SIGN)
    chains=[]
    for t in (fixed,decoded):
        assert t['source_id']==sid and type(t['hits']) is list and len(t['hits'])==2
        chain=[]
        for step,h in enumerate(t['hits']):
            p,o=h['primitive_id'],h['owner']
            assert type(p) is int and type(o) is int and 0<=p<len(owners) and o==step==owners[p]['owner']
            assert q(h['segment_BU'])>0
            chain.append({k:owners[p][k] for k in ('primitive_id','owner','object_id','kind')})
        chains.append(chain)
    assert chains[0]==chains[1]
    return {'source_id':sid,'mirror_phase_ORIGINAL_uint64':w,
        'primitive_owner_map':owners,'selected_hit_chain':chains[0],
        'fixed_trace_sha256':digest(fixed),'decoded_trace_sha256':digest(decoded),
        'ideal_coefficient_exact_reim':[[-1,1],[0,1]],
        'coefficient_model':'conditional fixed ideal -exp(i*ORIGINAL phase) at exact +/-0; NOT Fresnel/physical material',
        'profile_admitted_HOST_only':True,'material_executed':False,
        'executed_material_charge_L1':None,'executed_material_quota_fits':None,
        'native_material_ABI_implemented':False,'zero_canonicalization_performed':False}
def bits(w):
    assert type(w) is int and 0<=w<2**64
    e=(w>>52)&2047;m=w&((1<<52)-1)
    assert e!=2047 and (e!=0 or m==0)
    return (-1 if w&SIGN else 1)*F(m if e==0 else m+(1<<52))*F(2)**((1 if e==0 else e)-1075)
def pair(v):return [v.numerator,v.denominator]
def allfalse(o):assert all(o[n] is False for n in FALSE)
def pq(v):
    t=q(v);assert t>=0;return t
def verify_plan(plan,ctx,p):
    assert set(plan)=={'model','units','context_sha256','sources','groups'}
    assert plan['model']==MODEL and plan['units']==UNITS and plan['context_sha256']==digest(ctx)
    ss=plan['sources'];gs=plan['groups'];cap=pq(ctx['unchanged_field_L1_cap'])
    assert [s['source_id'] for s in ss]==ctx['source_order'] and [[g['port'],g['coherence_group']] for g in gs]==ctx['groups']
    assert p['allocation_INPUT_valid'] is True and p['context_sha256']==digest(ctx) and p['plan_sha256']==digest(plan)
    assert p['groups']==gs and p['unchanged_limits']==ctx['unchanged_limits'];allfalse(p)
    for s,row in zip(ss,p['sources']):
        assert set(s)=={'source_id','cap_L1','stages_L1'} and set(s['stages_L1'])==set(STAGES)
        spent=sum((pq(s['stages_L1'][k]) for k in STAGES),F(0));c=pq(s['cap_L1']);assert spent<=c
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
        total=sum((pq(s['cap_L1']) for s in ss if s['source_id'] in members),F(0))
        reserve=sum((pq(g['reserves_L1'][k]) for k in RESERVES),F(0));assert total+reserve<=cap
        assert row=={'port':g['port'],'coherence_group':g['coherence_group'],'source_order':members,
            'source_caps_sum_L1':pair(total),'remaining_stages_reserved_L1':pair(reserve),
            'unchanged_group_field_L1_cap':pair(cap),'unallocated_L1':pair(cap-total-reserve)}
        projected['groups'].append({'port':g['port'],'coherence_group':g['coherence_group'],'remaining_stages_reserved_L1':pair(reserve)})
    assert old['allocation_sha256']==digest(projected) and old['unchanged_limits']==ctx['unchanged_limits']
    for k in ('amplitude_budget_accepted','source_product_gate_evaluated','remaining_stages_error_proved','field_values_computed',
            'detector_evaluated','coherence_authenticated','execution_authenticated','accepted_full_field_pipeline','GPU_executed'):assert old[k] is False
def verify_retained(name,index,ctx,s,m,old,mat,source,roots):
    row=old['cases'][name]['sources'][index];v=row['result'];mr=mat['cases'][name]['sources'][index]
    sr=source['cases'][name]['sources'][index];rr=roots['cases'][name]['sources'][index];rs=rr['result']
    assert row['current_guarded_source_ideal_reflection_CPU_executed'] is True and row['material_executed'] is True
    assert v['retained_material_admission_row_sha256']==digest(mr)
    assert v['retained_source_row_sha256']==digest(sr)==mr['retained_source_row_sha256']
    assert v['retained_root_row_sha256']==digest(rr)==mr['retained_root_row_sha256']
    p=profile(s,m,row['source_id'],rs['fixed_ORIGINAL_reference'],rs['new_decoded_Xroot_result']['fixed_ORIGINAL_reference'])
    assert p==mr['material_profile']==v['material_profile']
    assert v['input_uint64']==mr['current_bare_source_uint64']==sr['result']['product_uint64']
    assert len(v['material_nodes'])==len(v['reflected_uint64'])==len(v['input_uint64'])==2
    for w,o,n in zip(v['input_uint64'],v['reflected_uint64'],v['material_nodes']):
        assert type(w) is type(o) is int and o==w^SIGN and bits(o)==-bits(w)
        assert n=={'operation':'CPU_unary_minus_binary64','input_uint64':w,'output_uint64':o,'exact_material_rounding_error_L1':[0,1]} and q(n['exact_material_rounding_error_L1'])==0
    detail={**sr['result']['detailed_source_charges_L1'],'ideal_material_L1':[0,1]}
    assert detail==v['fifteen_source_material_charges_L1'] and q(v['executed_material_charge_L1'])==0
    assert v['executed_material_quota_fits'] is None
    assert v['phase_reference_id']==mr['phase_reference_id']==ctx['assignments'][index]['source_phase_reference_id']
    assert v['terminal_reference_id']==mr['terminal_reference_id']==ctx['assignments'][index]['terminal_reference_id']
    assert type(v['new_main_CPU_unary_negations']) is int and v['new_main_CPU_unary_negations']==2
    assert v['zero_canonicalization_performed'] is v['source_phase_bound_proved'] is False
    total=sum(map(pq,detail.values()),F(0))
    assert total==q(v['point_reflected_source_bound_to_FIXED_ORIGINAL_L1'])==q(sr['result']['point_bare_source_bound_to_FIXED_ORIGINAL_L1'])
    return row,detail,total
def verify_bridge(a,plans,packets,old,mat,source,roots):
    assert a['model']==OWN_MODEL and a['charge_mapping']==MAPPING
    assert a['inherited_pins_verified']==403 and a['new_native_operations']==a['old_native_stages_suites_reexecuted']==0
    assert a['allocation_policy_adopted'] is False;allfalse(a)
    valid=missing=count=fits=0
    for name,c in a['cases'].items():
        ctx,s,m,bs=context(packets[name]);assert c['context']==ctx==old['cases'][name]['context']
        assert c['status']=='STOP';allfalse(c)
        assert [r['source_id'] for r in c['sources']]==ctx['source_order']
        plan=plans.get(name);p=c['allocation_INPUT']
        if plan is None:
            missing+=1;assert p['allocation_INPUT_valid'] is False;allfalse(p)
            assert all(r['stage_comparisons'] is None and r['partial_seven_stage_comparison_fits'] is False for r in c['sources'])
        else:
            valid+=1;verify_plan(plan,ctx,p)
        for i,(out,oldrow) in enumerate(zip(c['sources'],old['cases'][name]['sources'])):
            allfalse(out);assert out['retained_reflection_row_sha256']==digest(oldrow)
            if plan is None or not oldrow['current_guarded_source_ideal_reflection_CPU_executed']:
                assert out['stage_comparisons'] is None and out['partial_seven_stage_comparison_fits'] is False
                assert 'fifteen_charges_L1' not in out and 'retained_reflection_executed_CPU' not in out
                continue
            count+=1;row,detail,total=verify_retained(name,i,ctx,s,m,old,mat,source,roots)
            assert out['fifteen_charges_L1']==detail and len(detail)==15
            mapped={k:pair(sum((pq(detail[n]) for n in ns),F(0))) for k,ns in MAPPING.items()}
            assert out['seven_stage_charges_L1']==mapped and set(mapped)==set(STAGES)
            assert sum(map(q,mapped.values()),F(0))==total==q(out['point_reflected_source_bound_L1'])
            sp=plan['sources'][i];expected={k:{'charge_L1':mapped[k],'quota_L1':sp['stages_L1'][k],'fits':q(mapped[k])<=pq(sp['stages_L1'][k])} for k in STAGES}
            assert out['stage_comparisons']==expected and out['source_cap_L1']==sp['cap_L1']
            tf=total<=pq(sp['cap_L1']);fit=tf and all(v['fits'] for v in expected.values())
            assert out['partial_total_fits_source_cap'] is tf and out['partial_seven_stage_comparison_fits'] is fit
            assert out['retained_reflection_executed_CPU'] is True and out['new_material_operations']==0
            fits+=int(fit)
    assert (a['explicit_INPUT_plans_valid'],a['missing_INPUT_plans_STOP'],a['partial_source_comparisons'],a['partial_seven_stage_comparisons_fit'])==(valid,missing,count,fits)
    return valid,missing,count,fits
def main():
    global FALSE
    r=json.loads((ROOT/REPORT).read_bytes());pr=read(PARENT,PARENT_SHA)
    inherited=dict(pr['code_doc_sha256']);inherited[PARENT]=PARENT_SHA
    own=r['own_code_doc_sha256'];pins={**inherited,**own}
    assert not set(own)&set(inherited) and r['code_doc_sha256']==pins
    assert r['inherited_pin_source']=={'path':PARENT,'sha256':PARENT_SHA}
    assert (len(inherited),len(own),len(pins))==(403,4,407)
    for path,h in pins.items():assert sha((ROOT/path).read_bytes())==h,path
    FALSE=tuple(r['proof_scope']);assert len(FALSE)==38 and all(v is False for v in r['proof_scope'].values())
    old=payload(pr)['data']['audit'];mat=payload(read(MAT,pins[MAT]))['data']['audit']
    source=payload(read(SOURCE,pins[SOURCE]))['data']['audit'];roots=payload(read(ROOTS,pins[ROOTS]))['data']['audit']
    ip='coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json';pp='coordinacion/respuestas/AXIAL-NATIVE-PRESENCE-STOPS-001-CODEX.json'
    packets=payload(read(ip,pins[ip]))['packets'];pres=payload(read(pp,pins[pp]))
    packets.update({n:v['parent'] for n,v in pres['synthetic_controls'].items()})
    plan_data=payload(read(PLAN,pins[PLAN]))['data'];run=payload(r)
    assert run['tests']==4;d=run['data'];plans=plan_data['synthetic_INPUT_plans']
    assert d['retained_synthetic_INPUT_plans']==plans
    flat=[n for ns in MAPPING.values() for n in ns];assert len(flat)==len(set(flat))==15
    assert verify_bridge(d['real_missing'],{},packets,old,mat,source,roots)==(0,17,0,0)
    assert sum(len(c['sources']) for c in d['real_missing']['cases'].values())==19
    assert verify_bridge(d['synthetic_partial'],plans,packets,old,mat,source,roots)==(3,0,2,2)
    for label,key,name in [('Horner_zero_FAIL','stage_overspend_control','nonexact_geometry_phase_PASS'),('source_zero_FAIL','explicit_zero_FAIL','thin_resolved')]:
        ctrl=d[label];assert ctrl['retained_INPUT_plan']==plan_data[key]['INPUT_plan']
        assert verify_bridge(ctrl['audit'],{name:ctrl['retained_INPUT_plan']},packets,old,mat,source,roots)==(1,0,1,0)
        out=ctrl['audit']['cases'][name]['sources'][0]
        if label=='Horner_zero_FAIL':assert out['partial_total_fits_source_cap'] is True and out['stage_comparisons']['source_Horner_L1']['fits'] is False
        else:assert out['partial_total_fits_source_cap'] is False
    assert verify_bridge(d['explicit_None_missing'],{'thin_resolved':None},packets,old,mat,source,roots)==(0,1,0,0)
    assert len(d['proof_rejections']['rows'])==12 and d['proof_rejections']['comparison_calls']==0
    assert len(d['INPUT_mapping_rejections']['rows'])==15 and d['INPUT_mapping_rejections']['proof_inspection_calls']==0
    assert r['technical_capture_recovery']['exit_code']==0 and 'Warning: truncated output' in r['technical_capture_recovery']['partial_tool_output']
    assert 'scientific parameters' in r['technical_capture_recovery']['recovery'] or 'scientific parameter' in r['technical_capture_recovery']['recovery']
    print(json.dumps({'PASS':True,'pins':len(pins),'real_missing_cases':17,'real_STOP_sources':19,
        'retained_CONTROL_plans':3,'partial_seven_stage_fits':2,'old_Horner_zero_FAIL_retained':True,'old_source_zero_FAIL_retained':True,
        'material_zero':'executed bitproof, NOT absent default','mapping':'15 charges ONCE -> 7 frozen quotas',
        'native_operations':0,'scope':'HOST retained point comparison ONLY; no source phase/group/fullfield/GPU/RT/physical admission'},sort_keys=True))
if __name__=='__main__':main()
