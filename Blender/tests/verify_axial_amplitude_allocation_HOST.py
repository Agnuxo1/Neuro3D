"""Read-only independent allocation verifier; stdlib, no production imports."""
import base64
from collections import Counter
from fractions import Fraction as F
import hashlib,json,math,sys,time,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT='coordinacion/respuestas/AXIAL-AMPLITUDE-ALLOCATION-CONTRACT-001-CODEX.json'
PREVIOUS='coordinacion/respuestas/AXIAL-SOURCE-PRODUCT-HOST-001-CODEX.json'
SHA='04390dac11ab3d7b2a785542bc9b7c94a0f447686b777def0cdeb0a3dceca1b3'
MODEL='axial-static-amplitude-L1-allocation-HOST-v1'
UNITS='ORIGINAL-source-field-amplitude-L1'
def canon(v):
    return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def digest(v):
    return hashlib.sha256(canon(v)).hexdigest()
def read(p):
    return json.loads((ROOT/p).read_bytes())
def payload(r):
    t=r['test_run'];b=zlib.decompress(base64.b64decode(t.get('stdout_zlib_base64') or ''.join(t['stdout_zlib_base64_chunks']),validate=True))
    assert t['rc']==0 and len(b)==t['stdout_bytes'] and hashlib.sha256(b).hexdigest()==t['stdout_sha256']
    return json.loads(b)
def pins(r):
    if 'code_doc_sha256' in r:
        return dict(r['code_doc_sha256'])
    d=r['inherited_pin_source']
    assert hashlib.sha256((ROOT/d['path']).read_bytes()).hexdigest()==d['sha256']
    p=pins(read(d['path']));p[d['path']]=d['sha256'];p.update(r['own_code_doc_sha256']);return p
def q(v):
    assert type(v) is list and len(v)==2 and all(type(n) is int for n in v)
    assert v[0]>=0 and v[1]>0 and math.gcd(v[0],v[1])==1
    return F(*v)
def derive(packet):
    buffers={k:base64.b64decode(v,validate=True) for k,v in packet['buffers_base64'].items()}
    for k,v in buffers.items():
        assert packet['manifest']['buffers'][k]=={'bytes':len(v),'sha256':hashlib.sha256(v).hexdigest()}
    m=json.loads(buffers['input_metadata_json']);s=json.loads(buffers['original_scene_json']);g=m['explicit_group_contract']
    assert [v['id'] for v in s['sources']]==m['source_order']
    assert g['scene_binding_sha256']==m['scene_binding_sha256']
    assert m['original_snapshot_sha256']==hashlib.sha256(buffers['original_scene_json']).hexdigest()
    assert [a['source_id'] for a in g['assignments']]==m['source_order']
    groups=[]
    for a in g['assignments']:
        assert a['source_phase_reference_id']=='original-source-zero:'+m['scene_binding_sha256']+':'+a['source_id']
        k=[a['port'],a['coherence_group']]
        if k not in groups:
            groups.append(k)
    q(g['limits']['field_L1'])
    return {'model':MODEL,'units':UNITS,'case_name':m['case_name'],'input_packet_sha256':digest(packet),
            'scene_binding_sha256':m['scene_binding_sha256'],'word_ABI_sha256':m['word_ABI_sha256'],
            'original_snapshot_sha256':m['original_snapshot_sha256'],'original_group_contract_sha256':digest(g),
            'source_order':m['source_order'],'assignments':g['assignments'],'groups':groups,
            'unchanged_field_L1_cap':g['limits']['field_L1'],'unchanged_limits':g['limits'],
            'grouping_provenance':g['grouping_provenance'],'execution_authenticated':False,'coherence_authenticated':False}
def accounting(ctx,a):
    assert type(a) is dict and set(a)=={'model','units','context_sha256','sources','groups'}
    assert a['model']==MODEL and a['units']==UNITS and a['context_sha256']==digest(ctx)
    src=a['sources'];res=a['groups']
    assert type(src) is list and len(src)==len(ctx['source_order'])
    assert all(type(v) is dict and set(v)=={'source_id','cap_L1'} for v in src)
    assert [v['source_id'] for v in src]==ctx['source_order']
    caps={v['source_id']:q(v['cap_L1']) for v in src}
    assert type(res) is list and len(res)==len(ctx['groups'])
    assert all(type(v) is dict and set(v)=={'port','coherence_group','remaining_stages_reserved_L1'} for v in res)
    assert [[v['port'],v['coherence_group']] for v in res]==ctx['groups']
    limit=q(ctx['unchanged_field_L1_cap']);rows=[]
    for g in res:
        members=[v['source_id'] for v in ctx['assignments'] if v['port']==g['port'] and v['coherence_group']==g['coherence_group']]
        total=sum((caps[s] for s in members),F(0));reserve=q(g['remaining_stages_reserved_L1'])
        assert total+reserve<=limit
        rows.append({'port':g['port'],'coherence_group':g['coherence_group'],'source_order':members,
                     'source_caps_sum_L1':[total.numerator,total.denominator],
                     'remaining_stages_reserved_L1':[reserve.numerator,reserve.denominator],
                     'unchanged_group_field_L1_cap':[limit.numerator,limit.denominator],
                     'unallocated_L1':[(limit-total-reserve).numerator,(limit-total-reserve).denominator]})
    return caps,rows
def main():
    start=time.perf_counter();r=read(REPORT);data=payload(r)
    assert hashlib.sha256((ROOT/PREVIOUS).read_bytes()).hexdigest()==SHA
    inherited=pins(read(PREVIOUS));inherited[PREVIOUS]=SHA
    assert data['pins']==inherited
    allpins=dict(inherited);allpins.update(r['own_code_doc_sha256'])
    for p,h in allpins.items():
        assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    packets=payload(read('coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json'))['packets']
    controls=payload(read('coordinacion/respuestas/AXIAL-NATIVE-PRESENCE-STOPS-001-CODEX.json'))['synthetic_controls']
    packets.update({n:v['parent'] for n,v in controls.items()})
    assert data['PASS'] is True and data['tests']==7
    assert set(data['contexts'])==set(data['missing'])==set(packets) and len(packets)==17
    for n,p in packets.items():
        ctx=derive(p);assert data['contexts'][n]==ctx
        v=data['missing'][n];assert v['context']==ctx
        z=v['result'];assert z['allocation_INPUT_valid'] is False and z['context_sha256']==digest(ctx)
        assert z['source_order']==ctx['source_order'] and 'no default split/zero' in z['reason']
        assert 'source_caps_L1' not in z
    synthetic=data['synthetic_packet'];base=packets['two_sources']
    # Only the explicitly labeled second coherence assignment is changed in this new synthetic INPUT.
    x={k:base64.b64decode(v) for k,v in synthetic['buffers_base64'].items()}
    y={k:base64.b64decode(v) for k,v in base['buffers_base64'].items()}
    assert all(x[k]==y[k] for k in x if k!='input_metadata_json')
    m=json.loads(x['input_metadata_json']);o=json.loads(y['input_metadata_json'])
    old_group=m['explicit_group_contract']['assignments'][1]['coherence_group']
    assert old_group=='g2';m['explicit_group_contract']['assignments'][1]['coherence_group']='g'
    assert m==o
    assert len(data['plans'])==len(data['valid'])==4
    for n,a in data['plans'].items():
        p=synthetic if n=='synthetic_two_groups' else packets['positive' if n=='explicit_zero_caps' else n]
        ctx=derive(p);v=data['valid'][n];z=v['result'];caps,rows=accounting(ctx,a)
        assert v['context']==ctx and z['allocation_INPUT_valid'] is True
        assert z['groups']==rows and z['source_caps_L1']=={s:[c.numerator,c.denominator] for s,c in caps.items()}
        assert z['unchanged_limits']==ctx['unchanged_limits'] and z['allocation_sha256']==digest(a)
        assert z['context_sha256']==digest(ctx)
    assert len(data['valid']['synthetic_two_groups']['result']['groups'])==2
    assert data['valid']['explicit_zero_caps']['result']['source_caps_L1']=={'s':[0,1]}
    assert len(data['rejections'])==18 and len({v['label'] for v in data['rejections']})==18
    for v in data['rejections']:
        assert v['packet'] in packets.values() and v['reason'] and v['type']=='ValueError'
        try:
            accounting(derive(v['packet']),v['allocation'])
        except (AssertionError,KeyError,TypeError,ValueError):
            pass
        else:
            raise AssertionError('independent invalid plan accepted '+v['label'])
    results=list(data['missing'].values())+list(data['valid'].values())
    assert Counter(map(digest,results))==Counter(map(digest,data['calls'])) and len(results)==21
    for v in results:
        for k in ('amplitude_budget_accepted','source_product_gate_evaluated','remaining_stages_error_proved','field_values_computed','detector_evaluated','coherence_authenticated','execution_authenticated','accepted_full_field_pipeline','GPU_executed'):
            assert v[k] is False
    products=payload(read(PREVIOUS))['cases']
    assert sum(not v['source_product_evaluated'] for c in products.values() for v in c['sources'])==14
    assert products['two_sources']['sources'][1]['source_product_evaluated'] is False
    print(json.dumps({'PASS':True,'pins_verified':len(allpins),'inherited_pins':len(inherited),'tests':7,
                      'retained_INPUTs_missing_allocation_STOP':17,'new_synthetic_INPUT_plans_valid':4,
                      'invalid_plans_rejected':18,'successful_contract_calls':21,'previous_numeric_STOP_preserved':14,
                      'original_caps_unchanged':True,'amplitude_budget_accepted':False,'GPU_executed':False,
                      'elapsed_seconds':time.perf_counter()-start},sort_keys=True))
if __name__=='__main__':
    main()
