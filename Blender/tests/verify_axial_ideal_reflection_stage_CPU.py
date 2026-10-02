"""Independent retained-input/sign-isometry checker; stdlib only, no production imports."""
import base64,hashlib,json,math,struct,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT='coordinacion/respuestas/AXIAL-IDEAL-REFLECTION-STAGE-CPU-001-CODEX.json'
PREVIOUS='coordinacion/respuestas/AXIAL-GUARDED-SCENE-SOURCE-CPU-001-CODEX.json'
PREVIOUS_SHA='8f4ea4cc5d35cb3f56d800837ff553c438f4e635d7e482b2a197a45651e59da8'
FLAG='ideal_reflection_CPU_executed'
OLD_FLAG='fresh_guarded_scene_bare_source_prefix_CPU_executed'
SIGN=1<<63
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def read(p,h):
    raw=(ROOT/p).read_bytes();assert sha(raw)==h,p;return json.loads(raw)
def pins_from(r):
    if 'code_doc_sha256' in r:return dict(r['code_doc_sha256'])
    d=r['inherited_pin_source'];p=pins_from(read(d['path'],d['sha256']))
    p[d['path']]=d['sha256'];p.update(r['own_code_doc_sha256']);return p
def payload(r):
    t=r['test_run'];assert t['rc']==0
    if 'timed_out' in t:assert t['timed_out'] is False
    raw=zlib.decompress(base64.b64decode(t.get('stdout_zlib_base64') or ''.join(t['stdout_zlib_base64_chunks']),validate=True))
    assert len(raw)==t['stdout_bytes'] and sha(raw)==t['stdout_sha256']
    return json.loads(raw)
def rational(v):
    assert type(v) is list and len(v)==2 and all(type(x) is int for x in v)
    assert v[0]>=0 and v[1]>0 and math.gcd(*v)==1
    return F(*v)
def bits(w):
    assert type(w) is int and 0<=w<2**64
    e=(w>>52)&2047;m=w&((1<<52)-1);assert e<2047 and (e or m==0)
    return (-1 if w&SIGN else 1)*F(m+(1<<52) if e else 0)*F(2)**(e-1075 if e else -1074)
def pair(q):return [q.numerator,q.denominator]
def word(x):
    assert type(x) is float and math.isfinite(x)
    return int.from_bytes(struct.pack('<d',x),'little')
r=json.loads((ROOT/REPORT).read_bytes())
assert r['task_id']=='AXIAL-IDEAL-REFLECTION-STAGE-CPU-001' and r['base_commit']=='32c1768347531bb209983e350cd1d702ae357e7f'
assert r['inherited_pin_source']=={'path':PREVIOUS,'sha256':PREVIOUS_SHA}
pins=pins_from(r)
for p,h in pins.items():assert sha((ROOT/p).read_bytes())==h,p
assert len(pins)==352
old=payload(read(PREVIOUS,PREVIOUS_SHA))['data']['audit']
raw=payload(r);assert raw['PASS'] is True and raw['tests']==4
a=raw['data']['audit'];assert a['case_order']==old['case_order'] and a['inherited_pins_verified']==348
packets=payload(read('coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json',pins['coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json']))['packets']
controls=payload(read('coordinacion/respuestas/AXIAL-NATIVE-PRESENCE-STOPS-001-CODEX.json',pins['coordinacion/respuestas/AXIAL-NATIVE-PRESENCE-STOPS-001-CODEX.json']))['synthetic_controls']
packets.update({n:v['parent'] for n,v in controls.items()})
false=set(r['proof_scope'])
assert len(false)==36 and all(v is False for v in r['proof_scope'].values())
assert 'reflection_coefficient_applied' not in false and 'reflection_coefficient_executed_new' not in false
ex=stop=nodes=0;bounds={}
for n in a['case_order']:
    c=a['cases'][n];oc=old['cases'][n];assert c['context']==oc['context']
    for k in false:assert c[k] is False
    for i,(row,prev) in enumerate(zip(c['sources'],oc['sources'])):
        assert row['source_id']==prev['source_id']==c['context']['source_order'][i] and row['status']=='STOP'
        for k in false:assert row[k] is False
        if not prev[OLD_FLAG]:
            assert row[FLAG] is row['reflection_coefficient_applied'] is row['reflection_coefficient_executed_new'] is False
            assert row['reason']==prev['reason'] and 'result' not in row;stop+=1;continue
        assert row[FLAG] is row['reflection_coefficient_applied'] is row['reflection_coefficient_executed_new'] is True
        packet=packets[n];ctx=c['context'];assert digest(packet)==ctx['input_packet_sha256']
        buffers={k:base64.b64decode(v,validate=True) for k,v in packet['buffers_base64'].items()}
        for k,b in buffers.items():assert packet['manifest']['buffers'][k]=={'bytes':len(b),'sha256':sha(b)}
        snap=json.loads(buffers['original_scene_json']);meta=json.loads(buffers['input_metadata_json'])
        assert sha(buffers['original_scene_json'])==ctx['original_snapshot_sha256']==meta['original_snapshot_sha256']
        assert meta['scene_binding_sha256']==ctx['scene_binding_sha256'] and meta['word_ABI_sha256']==ctx['word_ABI_sha256']
        assert digest(meta['explicit_group_contract'])==ctx['original_group_contract_sha256']
        assert ctx['unchanged_limits']==meta['explicit_group_contract']['limits']
        assert meta['source_order']==[s['id'] for s in snap['sources']]==ctx['source_order']
        assert meta['explicit_group_contract']['assignments']==ctx['assignments'] and 'source_amplitude_allocation' not in meta
        res=row['result'];rr=prev['result']
        assert res['retained_prefix_row_sha256']==digest(prev) and res['context_sha256']==digest(ctx)
        assert set(snap['objects'])=={'M','D'} and snap['undeclared_meshes']==[]
        assert meta['object_ids']==['M','D'] and meta['kinds']==['mirror','det']
        assert [snap['objects'][s]['kind'] for s in ('M','D')]==['mirror','det']
        w=word(snap['objects']['M']['phase_rad']);assert w in (0,SIGN)
        profile=res['profile'];assert profile['mirror_phase_ORIGINAL_uint64']==w and profile['ideal_coefficient_exact_reim']==[[-1,1],[0,1]]
        assert profile['new_coefficient_error_L1']==[0,1]
        first=None
        for key in ('fixed_ORIGINAL_trace','decoded_trace'):
            t=rr[key];assert t['source_id']==row['source_id']
            hits=t['hits'];assert len(hits)==2 and [h['owner'] for h in hits]==[0,1]
            for h in hits:
                assert type(h['owner']) is int and type(h['primitive_id']) is int and rational(h['segment_BU'])>0
            ids=[(h['owner'],h['primitive_id']) for h in hits]
            if first is None:first=ids
            else:assert first==ids
        field=snap['sources'][i]['field_reim'];assert buffers['sources'][128*i+112:128*i+128]==struct.pack('<dd',*field)
        ass=ctx['assignments'][i]
        assert res['source_phase_reference_id']==prev['phase_reference_id']==ass['source_phase_reference_id']
        assert res['terminal_reference_id']==prev['terminal_reference_id']==ass['terminal_reference_id']
        assert res['input_uint64']==rr['bare_source_prefix']['product_uint64']
        assert res['reflected_uint64']==[v^SIGN for v in res['input_uint64']] and len(res['nodes'])==2
        for inp,out,node in zip(res['input_uint64'],res['reflected_uint64'],res['nodes']):
            assert node=={'operation':'unary_minus_binary64','input_uint64':inp,'output_uint64':out}
            assert bits(out)==-bits(inp);nodes+=1
        charges=res['charges_L1'];assert charges==rr['detailed_source_charges_L1'] and len(charges)==6
        bound=sum((rational(v) for v in charges.values()),F(0))
        assert pair(bound)==res['point_reflected_source_to_fixed_ORIGINAL_bound_L1']==rr['point_bare_source_to_fixed_ORIGINAL_bound_L1']
        assert bound>0 and res['additional_reflection_rounding_error_L1']==[0,1] and res['new_CPU_unary_negations']==2
        assert res[FLAG] is res['reflection_coefficient_applied'] is res['reflection_coefficient_executed_new'] is True
        for k in false:assert res[k] is False
        assert res['zero_canonicalization_performed'] is False
        gate=res['allocation_gate'];assert gate['allocation_INPUT_valid'] is False and gate['context_sha256']==digest(ctx)
        assert gate['source_order']==ctx['source_order'] and gate['amplitude_budget_accepted'] is gate['accepted_full_field_pipeline'] is False
        # Isometry for any ideal reference z: (-p)-(-z)=-(p-z).
        # No assertion that retained prefix equals a completed terminal field.
        bounds[n]=float(bound);ex+=1
assert (ex,stop,nodes)==(2,17,4)
assert set(bounds)=={'thin_resolved','nonexact_geometry_phase_PASS'}
for k,v in {'new_ideal_reflected_sources':2,'retained_sources_not_executed':17,'new_main_CPU_unary_negations':4,
 'new_probe_CPU_unary_negations':4,'new_geometry_argument_Horner_source_encoder_product_executions':0,
 'old_numeric_audits_suites_reexecuted':0,'new_reduction_power_readout_executions':0}.items():assert a[k]==v
assert a['fresh_scene_inference_executed'] is False
assert a['previous_SOURCE_eight_bit_FAILs_preserved'] is a['previous_SOURCE_twelve_zero_sign_mismatches_preserved'] is True
for k in false:assert a[k] is False
probe=a['runtime_probe'];ws=[0,SIGN,0x3ff0000000000000,0xbff0000000000000]
assert probe['input_uint64']==ws and probe['output_uint64']==[w^SIGN for w in ws] and probe['PASS'] is True
assert probe['new_CPU_unary_negations']==4 and probe['zero_canonicalization_performed'] is False
assert raw['data']['unary_controls']==[{'input_uint64':w,'output_uint64':w^SIGN} for w in ws]
assert raw['data']['negative_zero_profile']['mirror_phase_ORIGINAL_uint64']==SIGN
atomic=raw['data']['atomic_rejection'];assert atomic['new_CPU_unary_negations']==0 and atomic['partial_outputs_returned'] is False
assert 'gauges' in atomic['reason']
ext=raw['data']['unsupported_allocation_extension'];assert ext['source_budget_admitted'] is False and 'unsupported' in ext['reason']
rejects=raw['data']['rejections'];assert len(rejects)==len({v['label'] for v in rejects})==24
assert r['evidence']['main_CPU_unary_negations']==4 and r['evidence']['probe_CPU_unary_negations']==4 and r['evidence']['control_CPU_unary_negations']==4
print(json.dumps({'PASS':True,'pins':len(pins),'ideal_reflected_sources':ex,'not_executed':stop,
 'new_main_negations_checked':nodes,'point_reflected_bounds_L1':bounds,'missing_source_allocations_preserved':True,
 'signed_zero_preserved':True,'atomic_no_partial_outputs':True,'rejections':len(rejects),
 'upstream_numeric_producers_reexecuted':0,'GPU_physical_fullpipeline_admitted':False},sort_keys=True))
