"""Independent stdlib current-source ideal reflection oracle; NO production imports."""
import base64,hashlib,json,math,struct,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT='coordinacion/respuestas/AXIAL-CURRENT-SOURCE-IDEAL-REFLECTION-CPU-001-CODEX.json'
PARENT='coordinacion/respuestas/AXIAL-SOURCE-MATERIAL-ADMISSION-HOST-001-CODEX.json'
PARENT_SHA='9b081c137e0ec009e4d8c34aaf6c64bdf56da9b7d9dd66e32c07cdf947d02825'
ROOTS='coordinacion/respuestas/AXIAL-GUARDED-HILO-XROOT-RN64-CPU-001-CODEX.json'
SOURCE='coordinacion/respuestas/AXIAL-GUARDED-SOURCE-PRODUCT-RN64-CPU-001-CODEX.json'
MODEL='axial-current-guarded-source-new-ideal-minus-one-reflection-CPU-point-v1'
FLAG='current_guarded_source_ideal_reflection_CPU_executed'
TRUE=('reflection_coefficient_applied','reflection_coefficient_executed_new')
SIGN=1<<63
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
def main():
    receipt=json.loads((ROOT/REPORT).read_bytes())
    parent=read(PARENT,PARENT_SHA);inherited=dict(parent['code_doc_sha256']);inherited[PARENT]=PARENT_SHA
    own=receipt['own_code_doc_sha256'];pins={**inherited,**own}
    assert not (set(inherited)&set(own)) and receipt['code_doc_sha256']==pins
    assert receipt['inherited_pin_source']=={'path':PARENT,'sha256':PARENT_SHA}
    assert len(inherited)==398 and len(own)==4 and len(pins)==402
    for p,h in pins.items():assert sha((ROOT/p).read_bytes())==h,p
    previous=payload(parent)['data']['audit']
    source=payload(read(SOURCE,pins[SOURCE]))['data']['audit']
    roots=payload(read(ROOTS,pins[ROOTS]))['data']['audit']
    ip='coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json'
    pp='coordinacion/respuestas/AXIAL-NATIVE-PRESENCE-STOPS-001-CODEX.json'
    packets=payload(read(ip,pins[ip]))['packets'];presence=payload(read(pp,pins[pp]))
    packets.update({n:v['parent'] for n,v in presence['synthetic_controls'].items()})
    data=payload(receipt);assert data['tests']==4
    data=data['data'];audit=data['audit'];flags=tuple(k for k,v in parent['proof_scope'].items() if v is False and k not in TRUE)
    assert len(flags)==36 and all(receipt['proof_scope'][k] is False for k in flags)
    assert set(audit['cases'])==set(previous['cases'])==set(packets) and audit['model']==MODEL
    admitted=stopped=0;main_nodes=0
    for name,c in audit['cases'].items():
        old=previous['cases'][name];ctx,s,m,bs=context(packets[name])
        assert c['context']==ctx==old['context'] and c['status']=='STOP'
        assert all(c[n] is False for n in flags+TRUE)
        assert [r['source_id'] for r in c['sources']]==ctx['source_order']
        for i,(row,prev) in enumerate(zip(c['sources'],old['sources'])):
            assert row['source_id']==prev['source_id'] and row['status']=='STOP' and all(row[n] is False for n in flags)
            assert row['executed_material_quota_fits'] is None
            if prev['source_profile_admitted_HOST_only']:
                admitted+=1;v=row['result'];rr=roots['cases'][name]['sources'][i];rs=rr['result']
                p=profile(s,m,prev['source_id'],rs['fixed_ORIGINAL_reference'],rs['new_decoded_Xroot_result']['fixed_ORIGINAL_reference'])
                assert p==prev['material_profile']==v['material_profile']
                assert v['retained_material_admission_row_sha256']==digest(prev)
                assert v['retained_source_row_sha256']==prev['retained_source_row_sha256']
                assert v['retained_root_row_sha256']==digest(rr)==prev['retained_root_row_sha256']
                assert v['input_uint64']==prev['current_bare_source_uint64']==source['cases'][name]['sources'][i]['result']['product_uint64']
                assert len(v['input_uint64'])==len(v['reflected_uint64'])==len(v['material_nodes'])==2
                for w,out,node in zip(v['input_uint64'],v['reflected_uint64'],v['material_nodes']):
                    assert type(w) is type(out) is int and out==w^SIGN and bits(out)==-bits(w)
                    assert node=={'operation':'CPU_unary_minus_binary64','input_uint64':w,'output_uint64':out,'exact_material_rounding_error_L1':[0,1]}
                    main_nodes+=1
                assert v['fourteen_source_charges_L1']==prev['fourteen_source_charges_L1']
                expected={**prev['fourteen_source_charges_L1'],'ideal_material_L1':[0,1]}
                assert v['fifteen_source_material_charges_L1']==expected and len(expected)==15
                total=sum(map(q,expected.values()),F(0));assert all(q(x)>=0 for x in expected.values())
                assert total==q(v['point_reflected_source_bound_to_FIXED_ORIGINAL_L1'])==q(prev['partial_bare_source_bound_L1'])==q(v['partial_bare_source_bound_L1'])
                assert v['phase_reference_id']==prev['phase_reference_id']==ctx['assignments'][i]['source_phase_reference_id']
                assert v['terminal_reference_id']==prev['terminal_reference_id']==ctx['assignments'][i]['terminal_reference_id']
                assert all(row[n] is v[n] is True for n in TRUE+(FLAG,'material_executed'))
                assert all(v[n] is False for n in flags)
                assert v['executed_material_charge_L1']==row['executed_material_charge_L1']==[0,1]
                assert v['executed_material_quota_fits'] is None and v['new_main_CPU_unary_negations']==2
                assert v['source_phase_bound_proved'] is v['zero_canonicalization_performed'] is False
                assert len(v['fifteen_source_material_charges_L1'])==15
            else:
                stopped+=1;assert all(row[n] is False for n in TRUE+(FLAG,'material_executed'))
                assert row['executed_material_charge_L1'] is None and 'result' not in row
                assert row['reason']==prev['reason']
    assert (admitted,stopped,main_nodes,len(audit['cases']))==(2,17,4,17)
    probe=audit['runtime_probe'];pw=[0,SIGN,0x3ff0000000000000,0xbff0000000000000]
    assert probe=={'input_uint64':pw,'output_uint64':[w^SIGN for w in pw],'PASS':True,'new_probe_CPU_unary_negations':4,'zero_canonicalization_performed':False}
    assert audit['new_main_CPU_unary_negations']==main_nodes and audit['new_probe_CPU_unary_negations']==4
    assert audit['new_ideal_reflected_sources']==2 and audit['retained_sources_not_executed']==17 and audit['inherited_pins_verified']==398
    assert audit['old_native_stages_suites_reexecuted']==audit['new_source_geometry_argument_Horner_reduction_power_readout_operations']==0
    assert audit['allocation_policy_adopted'] is False and all(audit[n] is False for n in flags+TRUE)
    ctr=data['scalar_controls'];assert len(ctr['input_uint64'])==8 and ctr['new_test_CPU_unary_negations']==8
    assert ctr['output_uint64']==[w^SIGN for w in ctr['input_uint64']]
    for w,out in zip(ctr['input_uint64'],ctr['output_uint64']):assert bits(out)==-bits(w)
    atom=data['atomic_rejections'];assert len(atom['rows'])==13 and atom['native_calls']==0
    assert len({r['label'] for r in atom['rows']})==13
    assert len(data['typed_rejections'])==7
    fail=data['native_FAILURE_controls'];assert len(fail['rejections'])==6 and fail['main_calls_after_probe_FAIL']==0 and fail['probe_FAIL_native_calls']==4
    assert {'runtime_probe_identity_FAIL','wrong_main_unary_minus','bool_native_word','subnormal_input','nonfinite_input','bool_input'}=={r['label'] for r in fail['rejections']}
    # Independent wrong-output checks: zeros' signs count even though rational value is zero.
    rejected=0
    for w in (0,SIGN,0x3fb999999999999a):
        try:assert w==w^SIGN
        except AssertionError:rejected+=1
        else:raise AssertionError('identity is not unary minus')
    assert rejected==3
    print(json.dumps({'PASS':True,'pins':len(pins),'new_reflected_sources':admitted,'retained_STOP_sources':stopped,
        'main_unary_minus_nodes':main_nodes,'probe_nodes':4,'upstream_charges':14,'new_exact_material_charge':[0,1],
        'wrong_sign_controls_rejected':rejected,'quota_fit':'None; absent INPUT not invented',
        'scope':'CPU ideal point reflection ONLY; no fullfield/native-material-ABI/GPU/RT/physical admission'},sort_keys=True))
if __name__=='__main__':main()
