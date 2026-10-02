"""Independent receipt/budget oracle, stdlib only, no production imports or numeric replay."""
import base64,hashlib,json,math,sys,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT='coordinacion/respuestas/AXIAL-MIRROR-ZERO-HOST-001-CODEX.json'
PREVIOUS='coordinacion/respuestas/AXIAL-AMPLITUDE-ALLOCATION-CONTRACT-001-CODEX.json'
PREVIOUS_SHA='f8432ef9d18b27eb1b64d61a87320ecb2a380b4a68b85438f6cde6b590b970f4'
PRODUCT='coordinacion/respuestas/AXIAL-SOURCE-PRODUCT-HOST-001-CODEX.json'
PRODUCT_SHA='04390dac11ab3d7b2a785542bc9b7c94a0f447686b777def0cdeb0a3dceca1b3'
MODEL='axial-retained-bare-source-product-budget-HOST-v1'
AMODEL='axial-static-amplitude-L1-allocation-HOST-v1'
UNITS='ORIGINAL-source-field-amplitude-L1'
FLAG='accepted_retained_bare_source_product_budget_CPU_only'
FALSE=('amplitude_budget_accepted','remaining_stages_error_proved','reflection_coefficient_applied',
       'field_values_computed','field_sum_computed','detector_evaluated','native_kernel_implemented',
       'GPU_executed','GPU_job_admission','execution_authenticated','coherence_authenticated','accepted_full_field_pipeline')
def canon(v):
    return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def sha(v):
    return hashlib.sha256(v).hexdigest()
def digest(v):
    return sha(canon(v))
def read(p,h):
    b=(ROOT/p).read_bytes();assert sha(b)==h,p;return json.loads(b)
def payload(r):
    t=r['test_run'];assert t['rc']==0
    b=zlib.decompress(base64.b64decode(t.get('stdout_zlib_base64') or ''.join(t['stdout_zlib_base64_chunks']),validate=True))
    assert len(b)==t['stdout_bytes'] and sha(b)==t['stdout_sha256']
    return json.loads(b)
def pins_from(r):
    if 'code_doc_sha256' in r:
        return dict(r['code_doc_sha256'])
    d=r['inherited_pin_source'];p=pins_from(read(d['path'],d['sha256']))
    p[d['path']]=d['sha256'];p.update(r['own_code_doc_sha256']);return p
def rat(v):
    assert type(v) is list and len(v)==2 and all(type(n) is int for n in v)
    assert v[0]>=0 and v[1]>0 and math.gcd(*v)==1
    return F(*v)
def pair(v):
    return [v.numerator,v.denominator]
def context(packet):
    roles={'triangles','sources','wavelength','reference','original_scene_json','input_metadata_json'}
    assert set(packet['buffers_base64'])==set(packet['manifest']['buffers'])==roles
    b={k:base64.b64decode(v,validate=True) for k,v in packet['buffers_base64'].items()}
    for k,v in b.items():
        assert packet['manifest']['buffers'][k]=={'bytes':len(v),'sha256':sha(v)}
    m=json.loads(b['input_metadata_json']);snap=json.loads(b['original_scene_json']);g=m['explicit_group_contract']
    assert m['original_snapshot_sha256']==sha(b['original_scene_json'])
    assert m['source_order']==[s['id'] for s in snap['sources']]
    assert m['case_name']==packet['manifest']['case_name']
    assert g['scene_binding_sha256']==m['scene_binding_sha256']
    assert [a['source_id'] for a in g['assignments']]==m['source_order']
    groups=[]
    for a in g['assignments']:
        assert a['source_phase_reference_id']=='original-source-zero:'+m['scene_binding_sha256']+':'+a['source_id']
        key=[a['port'],a['coherence_group']]
        if key not in groups:
            groups.append(key)
    cap=rat(g['limits']['field_L1'])
    return {'model':AMODEL,'units':UNITS,'case_name':m['case_name'],'input_packet_sha256':digest(packet),
            'scene_binding_sha256':m['scene_binding_sha256'],'word_ABI_sha256':m['word_ABI_sha256'],
            'original_snapshot_sha256':m['original_snapshot_sha256'],'original_group_contract_sha256':digest(g),
            'source_order':m['source_order'],'assignments':g['assignments'],'groups':groups,
            'unchanged_field_L1_cap':pair(cap),'unchanged_limits':g['limits'],
            'grouping_provenance':g['grouping_provenance'],'execution_authenticated':False,'coherence_authenticated':False}
def validate_plan(c,p):
    if p is None:
        return False,{},[]
    assert type(p) is dict and set(p)=={'model','units','context_sha256','sources','groups'}
    assert p['model']==AMODEL and p['units']==UNITS and p['context_sha256']==digest(c)
    assert type(p['sources']) is list and len(p['sources'])==len(c['source_order'])
    assert all(type(s) is dict and set(s)=={'source_id','cap_L1'} for s in p['sources'])
    assert [s['source_id'] for s in p['sources']]==c['source_order']
    caps={s['source_id']:rat(s['cap_L1']) for s in p['sources']}
    assert type(p['groups']) is list and len(p['groups'])==len(c['groups'])
    assert all(type(g) is dict and set(g)=={'port','coherence_group','remaining_stages_reserved_L1'} for g in p['groups'])
    assert [[g['port'],g['coherence_group']] for g in p['groups']]==c['groups']
    rows=[];cap=rat(c['unchanged_field_L1_cap'])
    for g in p['groups']:
        ids=[a['source_id'] for a in c['assignments'] if [a['port'],a['coherence_group']]==[g['port'],g['coherence_group']]]
        total=sum((caps[s] for s in ids),F(0));reserve=rat(g['remaining_stages_reserved_L1'])
        assert total+reserve<=cap
        rows.append({'port':g['port'],'coherence_group':g['coherence_group'],'source_order':ids,
                     'source_caps_sum_L1':pair(total),'remaining_stages_reserved_L1':pair(reserve),
                     'unchanged_group_field_L1_cap':pair(cap),'unallocated_L1':pair(cap-total-reserve)})
    return True,caps,rows
import struct
MIRROR_MODEL='axial-original-mirror-zero-exact-sign-HOST-v1'
BUDGET='coordinacion/respuestas/AXIAL-SOURCE-BUDGET-GATE-HOST-001-CODEX.json'
BUDGET_SHA='4b46ea8d88bde3dd38a1e71e786c79318b92daa1edf81a1b3123874f2c5f19f2'
MFLAG='accepted_reflected_source_product_budget_CPU_only'
MFALSE=('amplitude_budget_accepted','remaining_stages_error_proved','field_sum_computed','detector_evaluated',
        'execution_authenticated','coherence_authenticated','accepted_full_field_pipeline',
        'native_kernel_implemented','GPU_executed','GPU_job_admission')
SIGN=1<<63
def word(w):
    assert type(w) is int and 0<=w<2**64
    e=(w>>52)&2047;m=w&((1<<52)-1);assert e!=2047
    power=-1074 if e==0 else e-1075
    if e:m+=1<<52
    return (-1 if w&SIGN else 1)*F(m)*F(2)**power
def exact_product(v,words):
    assert type(words) is list and len(words)==2
    a=[word(w) for w in words];out=[w^SIGN for w in words]
    assert v['input_uint64']==words and v['reflected_uint64']==out
    assert v['input_rational']==[pair(x) for x in a] and v['reflected_rational']==[pair(-x) for x in a]
    assert [word(w) for w in out]==[-x for x in a]
    assert v['additional_rounding_error_L1']==[0,1] and v['HOST_signbit_XORs']==2 and v['new_RN64_operations']==0
    assert v['scope']=='bit primitive only; not scene evidence'
def profile(s,m,e):
    assert m['object_ids']==['M','D'] and m['kinds']==['mirror','det']
    assert set(s['objects'])=={'M','D'} and not s['undeclared_meshes']
    assert s['objects']['M']['kind']=='mirror' and s['objects']['D']['kind']=='det'
    p=s['objects']['M']['phase_rad'];assert type(p) is float
    w=struct.unpack('<Q',struct.pack('<d',p))[0];assert w in (0,SIGN)
    assert e['accepted_axial_two_event_geometry_CPU_only'] is True
    assert e['mirror_owner']==0 and e['terminal_owner']==1
    assert len(e['segments'])==2 and [v['owner'] for v in e['segments']]==[0,1]
    d=e['departure_certificate'];assert d['owner']==0 and d['source_id']==e['source_id']
    assert d['primitive_id']==e['segments'][0]['primitive_id']
    assert d['origin']=='derived-from-accepted-first-event-not-caller-previous-id'
    return {'mirror_object_id':'M','terminal_object_id':'D','mirror_phase_ORIGINAL_uint64':w,
            'mirror_coefficient_exact_reim':[[-1,1],[0,1]],'coefficient_error_L1':[0,1],
            'profile':'ORIGINAL binary64 +/-0 phase, ideal mirror -exp(i*phase)',
            'coefficient_transport':'HOST original_scene_json INPUT only; no native material buffer implementation'}
def main():
    r=json.loads((ROOT/REPORT).read_bytes())
    assert r['inherited_pin_source']=={'path':BUDGET,'sha256':BUDGET_SHA}
    pins=pins_from(r)
    for p,h in pins.items():assert sha((ROOT/p).read_bytes())==h,p
    assert len(pins)==222
    budgets=payload(read(BUDGET,BUDGET_SHA))['results']
    products=payload(read(PRODUCT,PRODUCT_SHA))['cases']
    plans=payload(read(PREVIOUS,PREVIOUS_SHA))['plans']
    ingress='coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json'
    presence='coordinacion/respuestas/AXIAL-NATIVE-PRESENCE-STOPS-001-CODEX.json'
    ep='coordinacion/respuestas/AXIAL-NATIVE-EVENTS-001-CODEX.json'
    packets=payload(read(ingress,pins[ingress]))['packets']
    packets.update({n:v['parent'] for n,v in payload(read(presence,pins[presence]))['synthetic_controls'].items()})
    events=payload(read(ep,pins[ep]))['cases']
    data=payload(r);assert data['PASS'] is True and data['tests']==6;data=data['data']
    assert set(data['missing']['cases'])==set(packets) and len(packets)==17
    assert set(data['controls'])=={'positive','two_sources','explicit_zero_caps'}
    reflected=0;old_stops=0;missing=0;counts=[]
    for label,result in [('missing',data['missing']),*data['controls'].items()]:
        prior=budgets['missing'] if label=='missing' else budgets['controls'][label]
        assert result['model']==MIRROR_MODEL and result['units']==UNITS
        assert result['budget_report_sha256']==BUDGET_SHA and result['inherited_pins_verified']==218
        assert result['case_order']==prior['case_order'] and set(result['cases'])==set(prior['cases'])
        assert result['new_RN64_operations']==result['new_products']==result['new_trigonometry_evaluations']==0
        assert result['geometry_reexecuted'] is False and result['coefficient_model_implemented_HOST_only'] is True
        assert all(result[k] is False for k in MFALSE)
        corners=0
        for n,v in result['cases'].items():
            c=context(packets[n]);assert v['context']==c
            bcase=prior['cases'][n];assert v['allocation_result']==bcase['allocation_result']
            p=None if label=='missing' else plans[label]
            valid,caps,groups=validate_plan(c,p)
            assert valid is v['allocation_result']['allocation_INPUT_valid']
            snap=json.loads(base64.b64decode(packets[n]['buffers_base64']['original_scene_json']))
            meta=json.loads(base64.b64decode(packets[n]['buffers_base64']['input_metadata_json']))
            assert len(v['sources'])==len(products[n]['sources'])
            for s,old,b in zip(v['sources'],products[n]['sources'],bcase['sources']):
                assert s['source_id']==old['source_id']==b['source_id']
                assert s['phase_reference_id']==old['phase_reference_id']
                assert s['terminal_reference_id']==old['terminal_reference_id']
                assert s['retained_product_row_sha256']==digest(old) and s['retained_budget_row_sha256']==digest(b)
                assert s['source_budget_evaluated'] is b['source_budget_evaluated']
                assert all(s[k] is False for k in MFALSE)
                if not old['source_product_evaluated']:
                    assert s['reflection_coefficient_applied_HOST'] is False and s[MFLAG] is False
                    assert s['status']=='STOP' and s['reason']==old['reason']
                    assert s['reason_provenance']=='unchanged_retained_numerical_STOP'
                    assert 'reflected_corner_products_HOST' not in s
                    if label=='missing':old_stops+=1
                    continue
                ecase=events[n]
                for k in ('case_name','input_packet_sha256','scene_binding_sha256','word_ABI_sha256','source_order'):
                    assert ecase[k]==products[n][k]
                e=ecase['sources'][products[n]['source_order'].index(s['source_id'])]
                assert e['departure_certificate']['input_packet_sha256']==digest(packets[n])
                assert s['mirror_profile']==profile(snap,meta,e) and s['retained_event_row_sha256']==digest(e)
                assert s['reflection_coefficient_applied_HOST'] is True
                assert s['coefficient_error_L1']==s['additional_rounding_error_L1']==[0,1]
                assert s['reflected_source_error_L1_to_ORIGINAL_bound']==old['product_error_L1_to_ORIGINAL_bound']
                assert s['unchanged_original_phase_cap_rad']==old['unchanged_original_phase_cap_rad']
                assert len(s['reflected_corner_products_HOST'])==len(old['encoded_corner_products'])==4
                for out,p in zip(s['reflected_corner_products_HOST'],old['encoded_corner_products']):
                    exact_product(out,p['product_uint64'])
                    assert out['retained_corner_product_sha256']==digest(p)
                    assert out['charges_L1_unchanged']==p['charges_L1']
                    assert out['error_L1_to_ORIGINAL_reflected_source_ideal_unit_bound']==p['error_L1_to_original_source_times_ideal_unit_bound']
                    assert out['ideal_reference_transform']=='negation of ORIGINAL source times ideal propagation unit; L1 isometry'
                    assert [F(*x) for x in out['reflected_rational']]==[-F(*x) for x in p['product_rational']]
                    assert sum(abs(word(x)) for x in p['product_uint64'])==sum(abs(word(x)) for x in out['reflected_uint64'])
                    corners+=1;reflected+=1
                assert s['status']==b['status'] and s['reason']==b['reason'] and s['reason_provenance']==b['reason_provenance']
                ok=valid and rat(old['product_error_L1_to_ORIGINAL_bound'])<=caps[s['source_id']]
                assert s[MFLAG] is ok and s[MFLAG] is b[FLAG]
                if valid:assert s['source_cap_L1']==pair(caps[s['source_id']])
                else:
                    assert 'source_cap_L1' not in s;missing+=1
            assert v[MFLAG] is all(s[MFLAG] for s in v['sources'])
            assert all(v[k] is False for k in MFALSE) and v['reflected_field_sum_computed'] is False
        assert result['HOST_corner_reflections']==corners and result['HOST_signbit_XORs']==2*corners
        counts.append(corners)
    assert counts==[20,4,4,4] and (reflected,old_stops,missing)==(32,14,5)
    assert len(data['primitive_controls'])==6
    for v in data['primitive_controls']:exact_product(v,v['input_uint64'])
    assert len(data['profile_controls'])==2
    for v in data['profile_controls']:assert v['profile']==profile(v['snapshot'],v['metadata'],v['event'])
    assert len(data['rejections'])==19
    for v in data['rejections']:
        try:
            if v['kind']=='primitive':
                assert v['model']==MIRROR_MODEL and type(v['words']) is list and len(v['words'])==2
                for w in v['words']:word(w)
            elif v['kind']=='profile':profile(v['snapshot'],v['metadata'],v['event'])
            else:
                assert v['model']==MIRROR_MODEL
                for n in v['names']:validate_plan(context(packets[n]),v['plans'][n])
        except (AssertionError,KeyError,TypeError):
            pass
        else:raise AssertionError('invalid rejection')
    print(json.dumps({'PASS':True,'pins_verified':222,'cases':17,'sources':19,'numeric_STOPs_preserved':14,
                      'missing_allocation_STOPs':5,'HOST_corner_reflections':32,'HOST_scene_XORs':64,
                      'primitive_controls':6,'signed_zero_profile_controls':2,'expected_rejections':19,
                      'new_RN64':0,'new_products':0,'new_trigonometry':0,'full_field_accepted':False},sort_keys=True))
if __name__=='__main__':main()
