"""Independent receipt/budget oracle, stdlib only, no production imports or numeric replay."""
import base64,hashlib,json,math,sys,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT='coordinacion/respuestas/AXIAL-GROUP-RELATIVE-HOST-001-CODEX.json'
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

PREV='coordinacion/respuestas/AXIAL-GROUP-POWER-HOST-001-CODEX.json'
PREV_SHA='d6510bb52617324272bc47b45b2b2c09ecc4578e865b06f0fc1d332a51998763'
FIELD='coordinacion/respuestas/AXIAL-GROUP-REDUCTION-HOST-001-CODEX.json'
FIELD_SHA='44e1af7a17f3fdb9577d274dc001212f9cefe7ea17af7548c9ba5f7f113a942d'
RMODEL='axial-retained-corner-relative-L1-ORIGINAL-HOST-v1'
RFLAG='accepted_retained_corner_field_power_limits_CPU_only'
PFLAG='accepted_retained_corner_group_power_CPU_only'
FFLAG='accepted_retained_corner_group_reduction_CPU_only'
RFALSE=('accepted_full_field_pipeline','remaining_stages_error_proved','detector_evaluated',
        'execution_authenticated','coherence_authenticated','native_kernel_implemented','GPU_executed','GPU_job_admission')
VARIANTS=('missing','explicit_synthetic_INPUT_controls','zero_absolute','zero_relative')
def decode(w):
    assert type(w) is int and 0<=w<2**64
    exponent=(w>>52)&2047;assert exponent<2047
    mantissa=w&((1<<52)-1)
    if exponent:mantissa+=1<<52
    return (-1 if w>>63 else 1)*F(mantissa)*F(2)**(exponent-1075 if exponent else -1074)
def number(row):
    words=row['input_uint64'];assert type(words) is list and len(words)==2
    x,y=map(decode,words)
    norm=abs(x)+abs(y);bound=rat(row['field_error_L1_to_ORIGINAL_bound'])
    lower=max(F(0),norm-bound);cap=rat(row['unchanged_relative_field_cap'])
    relative=bound/lower if lower else None;fits=relative is not None and relative<=cap
    assert row['observed_field_L1_exact']==pair(norm)
    assert row['ORIGINAL_field_L1_lower_bound']==pair(lower)
    assert row['relative_field_L1_upper_bound']==(pair(relative) if relative is not None else None)
    assert row['relative_field_gate_satisfied'] is fits
    assert row['status']==('STOP' if relative is None else ('PASS_PARTIAL' if fits else 'FAIL'))
    assert row['reason']==('no positive ORIGINAL L1 lower bound; no epsilon' if relative is None else
                          ('relative field L1 bound fits cap' if fits else 'relative field L1 bound exceeds cap'))
    assert row['new_RN_operations']==0
    assert row['metric']=='relative complex L1 per group; ORIGINAL ideal L1 denominator'
    assert row['scope']=='rational primitive only; not caller scene evidence'
    for dx,dy in ((F(0),F(0)),(bound,F(0)),(-bound,F(0)),(F(0),bound),(F(0),-bound)):
        original=abs(x+dx)+abs(y+dy);actual=abs(dx)+abs(dy)
        assert actual<=bound and original>=lower
        if relative is not None and original:assert actual/original<=relative
    return fits
def false_flags(row):
    for flag in RFALSE:assert row[flag] is False
def main():
    report=json.loads((ROOT/REPORT).read_bytes())
    assert report['task_id']=='AXIAL-GROUP-RELATIVE-HOST-001'
    assert report['model']==RMODEL
    assert report['inherited_pin_source']=={'path':PREV,'sha256':PREV_SHA}
    pins=pins_from(report);assert len(pins)==242 and pins[PREV]==PREV_SHA and pins[FIELD]==FIELD_SHA
    for p,h in pins.items():assert sha((ROOT/p).read_bytes())==h,p
    new=payload(report);assert new['PASS'] is True and new['tests']==6
    d=new['data']
    prev=payload(read(PREV,PREV_SHA))['data'];field=payload(read(FIELD,FIELD_SHA))['data']
    packets=payload(read('coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json',
                         pins['coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json']))['packets']
    controls=payload(read('coordinacion/respuestas/AXIAL-NATIVE-PRESENCE-STOPS-001-CODEX.json',
                          pins['coordinacion/respuestas/AXIAL-NATIVE-PRESENCE-STOPS-001-CODEX.json']))['synthetic_controls']
    packets.update({n:c['parent'] for n,c in controls.items()})
    assert len(packets)==17
    checks=0;total_groups=0;partial=0;stops=0;source_stops=0
    for variant in VARIANTS:
        audit=d[variant];expected=list(packets) if variant in VARIANTS[:2] else ['positive']
        assert audit['case_order']==expected and set(audit['cases'])==set(expected)
        assert audit['retained_variant']==variant and audit['model']==RMODEL
        assert audit['inherited_pins_verified']==238
        for k in ('new_RN_operations','new_field_products','new_field_reductions','new_power_operations','new_trigonometry','new_ray_traces'):
            assert audit[k]==0
        false_flags(audit);local=0
        for n in expected:
            c=audit['cases'][n];p=prev[variant]['cases'][n]
            f=field[p['retained_variant']]['cases'][n];ctx=context(packets[n])
            assert c['context']==ctx==p['context']==f['context']
            assert c['retained_variant']==variant
            assert c['retained_source_STOP_FAILs']==p['retained_source_STOP_FAILs']
            assert p['retained_source_rows_sha256']==[digest(s) for s in f['sources']]
            expected_STOPs=[{'source_id':s['source_id'],'status':s['status'],'reason':s['reason']}
                            for s in f['sources'] if s['status'] in ('STOP','FAIL')]
            assert c['retained_source_STOP_FAILs']==expected_STOPs
            if variant==VARIANTS[1]:source_stops+=len(expected_STOPs)
            assert [[g['port'],g['coherence_group']] for g in c['groups']]==ctx['groups']
            assert len(c['groups'])==len(f['groups'])==len(p['groups'])
            for row,fg,pg in zip(c['groups'],f['groups'],p['groups']):
                assert row['retained_field_group_sha256']==digest(fg)
                assert row['retained_power_group_sha256']==digest(pg)
                assert pg['retained_group_row_sha256']==digest(fg)
                assert row['source_order']==pg['source_order']==fg['source_order']
                false_flags(row);total_groups+=1
                if fg[FFLAG] is not True:
                    assert row['field_relative_gate_evaluated'] is False
                    assert row['field_relative_gates_satisfied'] is False and row[RFLAG] is False
                    assert (row['status'],row['reason'])==(pg['status'],pg['reason'])
                    assert row['reason_provenance']=='unchanged_retained_field_power_STOP'
                    assert 'field_relative_corners' not in row
                    if 'blocked_source_ids' in pg:assert row['blocked_source_ids']==pg['blocked_source_ids']
                else:
                    assert row['field_relative_gate_evaluated'] is True
                    assert len(row['field_relative_corners'])==len(fg['corner_sums'])
                    rel=[]
                    for v,fc in zip(row['field_relative_corners'],fg['corner_sums']):
                        assert v['retained_field_corner_sha256']==digest(fc)
                        assert v['corner_indices']==fc['corner_indices'] and v['input_uint64']==fc['sum_uint64']
                        assert v['field_error_L1_to_ORIGINAL_bound']==fg['error_L1_to_ORIGINAL_group_corner_sum_bound']
                        assert v['unchanged_relative_field_cap']==ctx['unchanged_limits']['relative_field']
                        rel.append(number(v));local+=1
                    rel_ok=all(rel)
                    absolute=rat(fg['error_L1_to_ORIGINAL_group_corner_sum_bound'])<=rat(ctx['unchanged_limits']['field_L1'])
                    power_ok=pg[PFLAG] is True
                    if power_ok:
                        assert pg['absolute_power_gate'] is True and pg['relative_power_gate'] is True
                        assert pg['unchanged_original_limits']==ctx['unchanged_limits']
                    assert row['field_relative_gates_satisfied'] is rel_ok
                    assert row['absolute_field_gate'] is absolute
                    assert row['retained_absolute_relative_power_gates'] is power_ok
                    assert row[RFLAG] is (rel_ok and absolute and power_ok)
                    assert row['unchanged_original_limits']==ctx['unchanged_limits']
                    if not power_ok:
                        assert (row['status'],row['reason'])==(pg['status'],pg['reason'])
                        assert row['reason_provenance']=='unchanged_retained_power_STOP_FAIL'
                    elif any(v['status']=='STOP' for v in row['field_relative_corners']):
                        assert row['status']=='STOP' and row[RFLAG] is False
                    else:assert row['status']==('PASS_PARTIAL' if row[RFLAG] else 'FAIL')
                if variant==VARIANTS[1]:
                    partial+=int(row[RFLAG]);stops+=int(row['status']=='STOP')
            assert c[RFLAG] is all(g[RFLAG] for g in c['groups'])
            false_flags(c)
        assert audit['new_exact_relative_denominator_checks']==local
        assert local==(16 if variant in VARIANTS[:2] else 4);checks+=local
        if variant!='explicit_synthetic_INPUT_controls':assert not any(c[RFLAG] for c in audit['cases'].values())
        if variant in VARIANTS[2:]:
            row=audit['cases']['positive']['groups'][0]
            assert row['status']=='FAIL' and row['field_relative_gates_satisfied'] is True and row[RFLAG] is False
    assert (partial,stops,source_stops,checks)==(4,13,14,40)
    assert len(d['primitives'])==9
    for row in d['primitives']:number(row)
    assert [r['status'] for r in d['primitives']]==['PASS_PARTIAL','FAIL','STOP','PASS_PARTIAL','STOP','PASS_PARTIAL','PASS_PARTIAL','STOP','STOP']
    assert d['primitives'][0]['observed_field_L1_exact']==[7,1]
    assert d['primitives'][0]['relative_field_L1_upper_bound']==[1,6]
    assert d['primitives'][6]['relative_field_L1_upper_bound']==[1,1]
    assert d['suite_diamond_reference_checks']==245
    assert len(d['rejections'])==22
    for row in d['rejections']:
        assert row['reason']
        if row['kind']=='primitive':
            try:
                assert type(row['words']) is list and len(row['words'])==2
                [decode(w) for w in row['words']];rat(row['bound']);rat(row['cap'])
            except (AssertionError,TypeError,ValueError,ZeroDivisionError):pass
            else:raise AssertionError('invalid primitive accepted '+row['label'])
        elif row['kind']=='selection':
            try:
                names=row['names'];v=row['variant']
                assert row['model']==RMODEL and v in VARIANTS and type(names) is list and 1<=len(names)<=64
                assert all(type(n) is str and n for n in names) and len(set(names))==len(names)
                assert set(names)<=set(prev[v]['cases'])
            except (AssertionError,TypeError,KeyError):pass
            else:raise AssertionError('invalid selection accepted '+row['label'])
        else:assert row['kind']=='caller_cap' and row['label']=='injection'
    assert report['failures_preserved']==[]
    return {'PASS':True,'pins_verified':242,'cases':17,'partial_groups':4,'groups_STOP':13,
            'preserved_source_STOPs':14,'new_scene_diagnostic_denominator_checks':40,
            'synthetic_denominator_checks':9,'diamond_reference_checks':245,'expected_rejections':22,
            'new_RN_operations':0,'production_imports':0,'field_power_replays':0,
            'accepted_full_field_pipeline':False}
if __name__=='__main__':print(json.dumps(main(),sort_keys=True))
