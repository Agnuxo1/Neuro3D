"""Independent receipt/budget oracle, stdlib only, no production imports or numeric replay."""
import base64,hashlib,json,math,sys,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT='coordinacion/respuestas/AXIAL-SOURCE-BUDGET-GATE-HOST-001-CODEX.json'
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
def main():
    report=json.loads((ROOT/REPORT).read_bytes())
    assert report['inherited_pin_source']=={'path':PREVIOUS,'sha256':PREVIOUS_SHA}
    pins=pins_from(report)
    for p,h in pins.items():
        assert sha((ROOT/p).read_bytes())==h,p
    assert len(pins)==217 and pins[PRODUCT]==PRODUCT_SHA
    product=payload(read(PRODUCT,PRODUCT_SHA))['cases']
    previous=payload(read(PREVIOUS,PREVIOUS_SHA))
    packets=payload(read('coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json',pins['coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json']))['packets']
    presence='coordinacion/respuestas/AXIAL-NATIVE-PRESENCE-STOPS-001-CODEX.json'
    packets.update({n:v['parent'] for n,v in payload(read(presence,pins[presence]))['synthetic_controls'].items()})
    data=payload(report);assert data['PASS'] is True and data['tests']==6
    results=data['results'];assert set(results['missing']['cases'])==set(packets) and len(packets)==17
    assert set(results['controls'])=={'positive','two_sources','explicit_zero_caps'}
    comparisons=0;old_stops=0;missing=0
    for label,result in [('missing',results['missing']),*results['controls'].items()]:
        assert result['model']==MODEL and result['units']==UNITS and result['inherited_pins_verified']==213
        assert result['allocation_report_sha256']==PREVIOUS_SHA and result['product_report_sha256']==PRODUCT_SHA
        assert result['new_numeric_products']==result['new_trigonometry_evaluations']==0
        assert all(result[k] is False for k in FALSE)
        names=list(packets) if label=='missing' else ['two_sources' if label=='two_sources' else 'positive']
        assert result['case_order']==names and list(result['cases'])==sorted(names) # JSON sorted capture
        for name,v in result['cases'].items():
            c=context(packets[name]);assert v['context']==c
            p=None if label=='missing' else previous['plans'][label]
            valid,caps,groups=validate_plan(c,p);a=v['allocation_result']
            assert a['allocation_INPUT_valid'] is valid and a['context_sha256']==digest(c)
            assert a['source_order']==c['source_order']
            if valid:
                assert a['allocation_sha256']==digest(p) and a['source_caps_L1']=={s:pair(x) for s,x in caps.items()}
                assert a['groups']==groups and a['unchanged_limits']==c['unchanged_limits']
            else:
                assert a['reason']=='missing explicit per-source L1 allocation INPUT; no default split/zero'
            assert v['numerical_evidence']=='retained_no_numerical_reexecution'
            assert v['product_report_sha256']==PRODUCT_SHA and v['HOST_only'] is True
            assert all(v[k] is False for k in FALSE)
            prior=product[name]
            for k in ('case_name','input_packet_sha256','scene_binding_sha256','word_ABI_sha256','source_order'):
                assert prior[k]==c[k]
            assert len(v['sources'])==len(prior['sources'])
            for s,old,assignment in zip(v['sources'],prior['sources'],c['assignments']):
                assert s['source_id']==old['source_id']==assignment['source_id']
                assert s['retained_source_row_sha256']==digest(old)
                assert s['phase_reference_id']==old['phase_reference_id']==assignment['source_phase_reference_id']
                assert s['terminal_reference_id']==old['terminal_reference_id']==assignment['terminal_reference_id']
                assert s['source_product_evaluated'] is old['source_product_evaluated']
                assert all(s[k] is False for k in FALSE)
                if not old['source_product_evaluated']:
                    assert s['status']=='STOP' and s['reason']==old['reason']
                    assert s['reason_provenance']=='unchanged_retained_numerical_STOP'
                    assert s['source_budget_evaluated'] is False and s[FLAG] is False
                    assert 'source_cap_L1' not in s and 'product_error_L1_to_ORIGINAL_bound' not in s
                    if label=='missing':old_stops+=1
                else:
                    assert s['product_error_L1_to_ORIGINAL_bound']==old['product_error_L1_to_ORIGINAL_bound']
                    for k in ('unchanged_original_phase_cap_rad','upstream_unit_phase_bound_rad'):
                        assert s[k]==old[k]
                    if not valid:
                        assert s['status']=='STOP' and s['reason']==a['reason']
                        assert s['reason_provenance']=='missing_static_INPUT_allocation'
                        assert s['source_budget_evaluated'] is False and s[FLAG] is False and 'source_cap_L1' not in s
                        missing+=1
                    else:
                        comparisons+=1;ok=rat(old['product_error_L1_to_ORIGINAL_bound'])<=caps[s['source_id']]
                        assert s['source_cap_L1']==pair(caps[s['source_id']])
                        assert s['source_budget_evaluated'] is True and s[FLAG] is ok
                        assert s['status']==('PASS_PARTIAL' if ok else 'FAIL')
                        assert s['reason']==('retained bare-product bound fits explicit source cap' if ok else
                                             'retained bare-product bound exceeds explicit source cap')
                        assert s['reason_provenance']=='exact_retained_L1_bound_vs_INPUT_cap'
            assert v[FLAG] is all(s[FLAG] for s in v['sources'])
            assert len(v['groups'])==len(groups)
            for actual,g in zip(v['groups'],groups):
                assert actual=={**g,FLAG:all(s[FLAG] for s in v['sources'] if s['source_id'] in g['source_order']),
                                'remaining_stages_error_proved':False,'accepted_full_field_pipeline':False}
    assert (comparisons,old_stops,missing)==(3,14,5)
    assert len(results['rejections'])==11
    for rej in results['rejections']:
        try:
            names=rej['names'];plans=rej['plans']
            assert rej['model']==MODEL and type(names) is list and 1<=len(names)<=64
            assert all(type(n) is str and n for n in names) and len(set(names))==len(names)
            assert type(plans) is dict and set(plans)==set(names) and set(names)<=set(packets)
            for n in names:
                validate_plan(context(packets[n]),plans[n])
        except (AssertionError,KeyError,TypeError):
            pass
        else:
            raise AssertionError('invalid rejection: '+rej['label'])
    print(json.dumps({'PASS':True,'pins_verified':len(pins),'retained_cases':17,'retained_sources':19,
                      'unchanged_numerical_STOPs':14,'missing_allocation_STOPs':5,
                      'comparisons':3,'partial_PASS':2,'explicit_zero_FAIL':1,'rejections':11,
                      'new_numeric_products':0,'new_trigonometry_evaluations':0,'full_field_accepted':False},sort_keys=True))
if __name__=='__main__':
    main()
