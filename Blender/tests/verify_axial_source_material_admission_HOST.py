"""Independent stdlib material/owner/context receipt oracle; no production imports."""
import base64,hashlib,json,math,struct,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT='coordinacion/respuestas/AXIAL-SOURCE-MATERIAL-ADMISSION-HOST-001-CODEX.json'
PARENT='coordinacion/respuestas/AXIAL-GUARDED-SOURCE-BUDGET-BRIDGE-HOST-001-CODEX.json'
PARENT_SHA='a68927d3657469345fb330a81653483d2d15d433d1df8d1a88a9660257a88794'
SOURCE='coordinacion/respuestas/AXIAL-GUARDED-SOURCE-PRODUCT-RN64-CPU-001-CODEX.json'
ROOTS='coordinacion/respuestas/AXIAL-GUARDED-HILO-XROOT-RN64-CPU-001-CODEX.json'
SIGN=1<<63
MODEL='axial-current-guarded-source-owner-hit-zero-phase-material-admission-HOST-v1'
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
def main():
    receipt=json.loads((ROOT/REPORT).read_bytes())
    parent=read(PARENT,PARENT_SHA);inherited=dict(parent['code_doc_sha256']);inherited[PARENT]=PARENT_SHA
    own=receipt['own_code_doc_sha256'];pins={**inherited,**own}
    assert not (set(inherited)&set(own)) and receipt['code_doc_sha256']==pins
    assert receipt['inherited_pin_source']=={'path':PARENT,'sha256':PARENT_SHA}
    assert len(inherited)==393 and len(own)==4 and len(pins)==397
    for p,h in pins.items():assert sha((ROOT/p).read_bytes())==h,p
    source=payload(read(SOURCE,pins[SOURCE]))['data']['audit']
    roots=payload(read(ROOTS,pins[ROOTS]))['data']['audit']
    packets=payload(read('coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json',pins['coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json']))['packets']
    presence=payload(read('coordinacion/respuestas/AXIAL-NATIVE-PRESENCE-STOPS-001-CODEX.json',pins['coordinacion/respuestas/AXIAL-NATIVE-PRESENCE-STOPS-001-CODEX.json']))
    packets.update({n:v['parent'] for n,v in presence['synthetic_controls'].items()})
    run=payload(receipt);assert run['tests']==3;data=run['data'];audit=data['audit']
    assert audit['model']==MODEL and set(audit['cases'])==set(source['cases'])==set(packets)
    flags=tuple(k for k,v in source.items() if v is False)
    assert len(flags)==38
    admitted=stopped=0
    for name,c in audit['cases'].items():
        old=source['cases'][name];ctx,s,m,bs=context(packets[name])
        assert c['context']==ctx==old['context']==roots['cases'][name]['context']
        assert c['status']=='STOP' and all(c[n] is False for n in flags)
        assert [r['source_id'] for r in c['sources']]==ctx['source_order']
        for i,(row,prev) in enumerate(zip(c['sources'],old['sources'])):
            assert row['status']=='STOP' and row['retained_source_row_sha256']==digest(prev) and all(row[n] is False for n in flags)
            assert row['material_executed'] is False and row['executed_material_charge_L1'] is None and row['executed_material_quota_fits'] is None
            if prev['guarded_source_product_RN64_CPU_executed']:
                admitted+=1;rr=roots['cases'][name]['sources'][i];rs=rr['result']
                expected=profile(s,m,row['source_id'],rs['fixed_ORIGINAL_reference'],rs['new_decoded_Xroot_result']['fixed_ORIGINAL_reference'])
                assert row['source_profile_admitted_HOST_only'] is True and row['material_profile']==expected
                assert row['retained_root_row_sha256']==digest(rr)
                res=prev['result'];assert row['current_bare_source_uint64']==res['product_uint64']
                assert all(type(w) is int and 0<=w<2**64 and (w>>52)&2047!=2047 for w in row['current_bare_source_uint64'])
                assert row['phase_reference_id']==prev['phase_reference_id']==ctx['assignments'][i]['source_phase_reference_id']
                assert row['terminal_reference_id']==prev['terminal_reference_id']==ctx['assignments'][i]['terminal_reference_id']
                words=[struct.unpack('<Q',struct.pack('<d',v))[0] for v in s['sources'][i]['field_reim']]
                assert prev['admission']['ORIGINAL_source_uint64']==words
                assert bs['sources'][128*i+112:128*i+128]==struct.pack('<QQ',*words)
                assert row['fourteen_source_charges_L1']==res['detailed_source_charges_L1']
                charges=list(map(q,row['fourteen_source_charges_L1'].values()))
                assert len(charges)==14 and all(v>=0 for v in charges)
                assert sum(charges,F(0))==q(row['partial_bare_source_bound_L1'])==q(res['point_bare_source_bound_to_FIXED_ORIGINAL_L1'])
            else:
                stopped+=1;assert row['source_profile_admitted_HOST_only'] is False and row['reason']==prev['reason']
                assert 'material_profile' not in row and 'current_bare_source_uint64' not in row
    assert (admitted,stopped,len(audit['cases']))==(2,17,17)
    assert audit['source_material_profiles_admitted_HOST_only']==2 and audit['retained_sources_STOP']==17 and audit['inherited_pins_verified']==393
    assert audit['new_native_operations']==audit['old_native_stages_suites_reexecuted']==0
    assert audit['material_charge_invented_as_zero'] is audit['allocation_policy_adopted'] is False
    assert all(audit[n] is False for n in flags)
    assert len(data['profile_rejections'])==22 and len(data['atomic_rejections']['rows'])==12
    assert data['atomic_rejections']['profile_guard_before_proof_calls']==0
    assert [p['mirror_phase_ORIGINAL_uint64'] for p in data['signed_zero_profile_controls']]==[0,SIGN]
    for p in data['signed_zero_profile_controls']:
        assert p['material_executed'] is False and p['executed_material_charge_L1'] is None and p['zero_canonicalization_performed'] is False
    # Independent controls execute oracle checks, not trust production rejection labels.
    s0=context(packets['thin_resolved'])[1];m0=context(packets['thin_resolved'])[2]
    rr=roots['cases']['thin_resolved']['sources'][0]['result'];fixed=rr['fixed_ORIGINAL_reference'];decoded=rr['new_decoded_Xroot_result']['fixed_ORIGINAL_reference']
    import copy
    rejected=0
    for w in (1,SIGN|1,1<<52,0x3ff0000000000000,0xbff0000000000000,0x7ff0000000000000,0x7ff8000000000000):
        s=copy.deepcopy(s0);s['objects']['M']['phase_rad']=struct.unpack('<d',struct.pack('<Q',w))[0]
        try:profile(s,m0,'s',fixed,decoded)
        except AssertionError:rejected+=1
        else:raise AssertionError('nonzero phase admitted by oracle')
    bad=copy.deepcopy(fixed);bad['hits'][0]['primitive_id']=2
    try:profile(s0,m0,'s',bad,decoded)
    except AssertionError:rejected+=1
    else:raise AssertionError('cross-owner primitive admitted by oracle')
    assert rejected==8
    print(json.dumps({'PASS':True,'pins':len(pins),'admitted_HOST_profiles':admitted,'retained_STOP_sources':stopped,
        'independent_phase_owner_rejects':rejected,'native_operations':0,'material_charge':'None NOT zero',
        'source_proof':'immutable SHA pinned prior proof; no old producer/suite replay',
        'scope':'source-bound HOST preflight ONLY, NO material/fullfield/GPU/RT/physical admission'},sort_keys=True))
if __name__=='__main__':main()
