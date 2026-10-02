"""Independent static INPUT budget oracle; stdlib, no production imports."""
import base64,hashlib,json,math,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT='coordinacion/respuestas/AXIAL-STAGE-SIDECAR-INGRESS-HOST-001-CODEX.json'
PREVIOUS='coordinacion/respuestas/AXIAL-STAGE-ALLOCATION-HOST-001-CODEX.json'
PREVIOUS_SHA='686e7c67ba7f2115de70443f38e13a5c306a70416193a91817fee3595a9eb7a8'
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
WIRE_MODEL='axial-seven-stage-sidecar-UTF8-SHA-bounded-HOST-v1'
SCHEMA='axial-seven-stage-allocation-sidecar-v1'
LIMITS={'max_bytes':65536,'max_depth':12,'max_containers':2048,'max_integer_digits':96,'max_string_UTF8_bytes':256}
def uniq(pairs):
    d={}
    for k,v in pairs:
        assert k not in d,'duplicate decoded key'
        d[k]=v
    return d
def int_token(t):
    assert len(t.lstrip('-'))<=96;return int(t)
def invalid(t):raise ValueError('noninteger token')
def lexical(raw):
    assert type(raw) is bytes and 0<len(raw)<=65536 and not raw.startswith(b'\xef\xbb\xbf')
    text=raw.decode('utf-8','strict');decoder=json.JSONDecoder(parse_int=int_token,parse_float=invalid,parse_constant=invalid)
    # Independent scanner delegates scalar token decoding to stdlib; production uses regex.
    i=0;stack=[];count=depth=ints=strings=0
    while i<len(text):
        c=text[i]
        if c in ' \t\r\n':i+=1;continue
        if c in '{[':
            stack.append(c);count+=1;depth=max(depth,len(stack));assert depth<=12 and count<=2048;i+=1
        elif c in '}]':
            assert stack and stack.pop()==('{' if c=='}' else '[');i+=1
        elif c in ',:':i+=1
        else:
            value,end=decoder.raw_decode(text,i)
            if c=='"':
                assert type(value) is str and end-i<=1538 and len(value.encode('utf-8','strict'))<=256;strings+=1
            elif type(value) is int:
                assert len(text[i:end].lstrip('-'))<=96;ints+=1
            else:assert value is None or type(value) is bool
            i=end
    assert not stack
    return text,{'bytes':len(raw),'maximum_depth':depth,'containers':count,'integer_tokens':ints,'string_tokens':strings}
def validate_plan_input(plan,ctx):
    assert type(plan) is dict and set(plan)=={'model','units','context_sha256','sources','groups'}
    assert plan['model']==MODEL and plan['units']==UNITS and plan['context_sha256']==digest(ctx)
    ss=plan['sources'];gs=plan['groups'];assert type(ss) is list and type(gs) is list
    assert [s['source_id'] for s in ss]==ctx['source_order'] and [[g['port'],g['coherence_group']] for g in gs]==ctx['groups']
    cap=q(ctx['unchanged_field_L1_cap'])
    for s in ss:
        assert set(s)=={'source_id','cap_L1','stages_L1'} and set(s['stages_L1'])==set(STAGES)
        assert sum((q(v) for v in s['stages_L1'].values()),F(0))<=q(s['cap_L1'])
    for g in gs:
        assert set(g)=={'port','coherence_group','reserves_L1'} and set(g['reserves_L1'])==set(RESERVES)
        members={a['source_id'] for a in ctx['assignments'] if a['port']==g['port'] and a['coherence_group']==g['coherence_group']}
        spent=sum((q(s['cap_L1']) for s in ss if s['source_id'] in members),F(0))
        assert spent+sum((q(v) for v in g['reserves_L1'].values()),F(0))<=cap
def receive(raw,rec,packet):
    assert type(rec) is dict and set(rec)=={'bytes','sha256'} and type(rec['bytes']) is int and 0<rec['bytes']<=65536
    h=rec['sha256'];assert type(h) is str and len(h)==64 and all(c in '0123456789abcdef' for c in h)
    assert len(raw)==rec['bytes'] and sha(raw)==h
    text,stats=lexical(raw)
    env=json.loads(text,object_pairs_hook=uniq,parse_int=int_token,parse_float=invalid,parse_constant=invalid)
    assert type(env) is dict and set(env)=={'schema','input_packet_sha256','plan'}
    assert env['schema']==SCHEMA and env['input_packet_sha256']==digest(packet)
    ctx=context(packet);validate_plan_input(env['plan'],ctx)
    return ctx,env,stats
def wire_bytes(w):
    b=base64.b64decode(w['raw_base64'],validate=True)
    assert w['receipt']=={'bytes':len(b),'sha256':sha(b)};return b
def verify_result(out,raw,rec,packet):
    ctx,env,stats=receive(raw,rec,packet);allfalse(out)
    assert out['schema']==SCHEMA and out['raw_wire_receipt']==rec and out['wire_preflight']==stats and out['limits']==LIMITS
    assert out['context']==ctx and out['canonical_envelope_sha256']==digest(env)
    assert out['status']=='STOP' and out['numerical_charge_comparisons']==0 and out['allocation_policy_adopted'] is False
    verify_plan(env['plan'],ctx,out['allocation_INPUT'])
    return env
r=json.loads((ROOT/REPORT).read_bytes())
assert r['task_id']=='AXIAL-STAGE-SIDECAR-INGRESS-HOST-001' and r['base_commit']=='9798032a8ea3ac2d8e7454d144d82c23838cf2a6'
assert r['inherited_pin_source']=={'path':PREVIOUS,'sha256':PREVIOUS_SHA}
pins=pins_from(r)
for p,h in pins.items():assert sha((ROOT/p).read_bytes())==h,p
assert len(pins)==362
FALSE=tuple(r['proof_scope']);assert len(FALSE)==38 and all(v is False for v in r['proof_scope'].values())
old=payload(read(PREVIOUS,PREVIOUS_SHA))['data']['real_absent']
ip='coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json';pp='coordinacion/respuestas/AXIAL-NATIVE-PRESENCE-STOPS-001-CODEX.json'
packets=payload(read(ip,pins[ip]))['packets']
packets.update({n:v['parent'] for n,v in payload(read(pp,pins[pp]))['synthetic_controls'].items()})
raw=payload(r);assert raw['PASS'] is True and raw['tests']==4;d=raw['data']
a=d['real_missing'];allfalse(a)
assert a['model']==WIRE_MODEL and a['case_order']==old['case_order'] and a['inherited_pins_verified']==358
assert a['missing_sidecars_STOP']==17 and a['sidecar_INPUT_admitted']==0 and a['limits']==LIMITS
sources=0
for n,c in a['cases'].items():
    allfalse(c);assert c['context']==context(packets[n])==old['cases'][n]['context'] and c['status']=='STOP'
    assert c['allocation_INPUT']['allocation_INPUT_valid'] is False and c['numerical_charge_comparisons']==0
    sources+=len(c['context']['source_order'])
assert sources==19
s=d['synthetic_ingress'];allfalse(s)
assert s['sidecar_INPUT_admitted']==3 and s['missing_sidecars_STOP']==0 and s['numerical_charge_comparisons']==0
for n,w in d['synthetic_wires'].items():
    b=wire_bytes(w);env=verify_result(s['cases'][n],b,w['receipt'],packets[n])
    assert env['plan']==d['synthetic_INPUT_plans'][n]
    assert b==json.dumps(env,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
    ctx=context(packets[n]);cap=q(ctx['unchanged_field_L1_cap'])
    for src in env['plan']['sources']:assert src['cap_L1']==pair(cap/4) and src['stages_L1']==dict.fromkeys(STAGES,[1,10**14])
space=d['whitespace_wire'];b=wire_bytes(space['wire'])
env=verify_result(space['result'],b,space['wire']['receipt'],packets['thin_resolved'])
assert sha(b)!=digest(env)
rejects=d['wire_rejections'];assert len(rejects)==23 and len({v['label'] for v in rejects})==23
for rec in rejects:
    b=wire_bytes(rec['wire'])
    try:receive(b,rec['submitted_receipt'],packets['thin_resolved'])
    except (AssertionError,ValueError,TypeError,KeyError,UnicodeError):pass
    else:raise AssertionError('independent expected rejection '+rec['label'])
resources=d['resource_rejections'];assert len(resources)==6
for rec in resources:
    assert rec['global_parse_calls']==0
    b=b' '*65537 if rec['label']=='oversize' else wire_bytes(rec['wire'])
    rc=rec['receipt'] if rec['label']=='oversize' else rec['wire']['receipt']
    assert rc=={'bytes':len(b),'sha256':sha(b)}
    try:receive(b,rc,packets['thin_resolved'])
    except (AssertionError,ValueError,TypeError,KeyError,UnicodeError):pass
    else:raise AssertionError('expected resource rejection')
bound=d['byte_limit_boundary'];b=wire_bytes(bound['base_wire'])+b' '*bound['padding_spaces'];assert len(b)==65536
verify_result(bound['result'],b,bound['receipt'],packets['thin_resolved'])
for name,v in d['preflight_boundary_controls'].items():
    b=wire_bytes(v['wire']);_,stats=lexical(b);assert stats==v['stats']
assert d['preflight_boundary_controls']['depth12']['stats']['maximum_depth']==12
assert d['atomic_rejection']['partial_results_returned'] is False and d['atomic_rejection']['numeric_comparisons']==0
assert 'receipt' in d['atomic_rejection']['reason'] and 'missing/invalid' in d['serialize_absent_rejection']
for x in (a,s):
    assert x['new_numeric_producers_executed']==x['old_suites_producers_reexecuted']==x['numerical_charge_comparisons']==0
    assert x['allocation_policy_adopted'] is False
print(json.dumps({'PASS':True,'pins':len(pins),'real_absent_sidecars_STOP':17,'real_sources_STOP':19,
 'synthetic_wire_INPUT_admitted':3,'whitespace_raw_SHA_distinct':True,'invalid_wires_rejected':23,
 'resource_rejections_before_global_parse':6,'byte_limit_boundary':65536,'atomic_no_partial_result':True,
 'numerical_charge_comparisons':0,'numeric_producers_executed':0,'fullpipeline_GPU_admitted':False},sort_keys=True))
