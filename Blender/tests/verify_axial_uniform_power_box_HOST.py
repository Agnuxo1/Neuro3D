"""Independent stdlib Fraction/integer oracle, no production imports or old scene replay."""
import base64,hashlib,json,math,sys,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT='coordinacion/respuestas/AXIAL-UNIFORM-POWER-BOX-HOST-001-CODEX.json'
AMODEL='axial-static-amplitude-L1-allocation-HOST-v1'
UNITS='ORIGINAL-source-field-amplitude-L1'
MODEL='axial-uniform-power-encoded-box-RN64-HOST-v1'
FALSE=('stage_closure_proved','remaining_stages_error_proved','accepted_full_field_pipeline','detector_evaluated',
       'execution_authenticated','coherence_authenticated','native_kernel_implemented','GPU_executed','GPU_job_admission',
       'scene_image_enclosed','uniform_source_error_proved','ORIGINAL_global_reference_proved')
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

SIGN=1<<63
def decode(w):
    assert type(w) is int and 0<=w<2**64
    e=(w>>52)&2047;assert e<2047
    n=w&((1<<52)-1)
    if e:n+=1<<52
    return (-1 if w>>63 else 1)*F(n)*F(2)**(e-1075 if e else -1074)

def round_even_ratio(v):
    q,r=divmod(v.numerator,v.denominator)
    return q+(2*r>v.denominator or (2*r==v.denominator and q%2==1))

def round_word(v,left,right):
    # Independent integer-only RN-even; no float/struct conversion or production import.
    if not v:return SIGN if left==right==SIGN else 0
    negative=v<0;x=abs(v)
    e=x.numerator.bit_length()-x.denominator.bit_length()
    if x<F(2)**e:e-=1
    if e < -1022:
        n=round_even_ratio(x/F(2)**-1074)
        w=n # zero/subnormal or smallest normal, including rounded tiny zero.
    else:
        n=round_even_ratio(x/F(2)**(e-52))
        if n==2**53:n//=2;e+=1
        assert e<=1023,'integer oracle overflow'
        w=((e+1023)<<52)+(n-2**52)
    return w|(SIGN if negative else 0)


def number(v):
    assert type(v) is list and len(v)==2 and all(type(n) is int for n in v)
    assert v[1]>0 and max(abs(v[0]).bit_length(),v[1].bit_length())<=4096
    assert math.gcd(*v)==1
    return F(*v)
MAX=decode(0x7fefffffffffffff)
def charge(m):
    assert 0<=m<=MAX
    # Absolute RN error <= half spacing for every binade, plus half subnormal spacing.
    return m/F(2**53)+F(1,2**1075) if m else F(0)
def verify_theorem(t):
    assert t['model']==MODEL and t['uniform_RN_bound_for_declared_box_proved'] is True
    intervals=[list(map(number,q)) for q in t['box']]
    assert len(intervals)==2
    for a,b in intervals:assert -MAX<=a<=b<=MAX
    high=[max(abs(a),abs(b)) for a,b in intervals]
    low=[F(0) if a<=0<=b else min(abs(a),abs(b)) for a,b in intervals]
    squares=[v**2 for v in high];errors=[charge(v) for v in squares]
    s=sum(squares)+sum(errors);add=charge(s);total=sum(errors)+add
    assert t['max_abs_components']==list(map(pair,high))
    assert t['min_abs_components']==list(map(pair,low))
    assert t['exact_square_max']==list(map(pair,squares))
    assert t['square_RN64_uniform_charges']==list(map(pair,errors))
    assert t['exact_add_input_max']==pair(s) and t['add_RN64_uniform_charge']==pair(add)
    assert t['power_RN64_uniform_charge']==pair(total)
    assert t['RN_graph']==['RN64(real*real)','RN64(imag*imag)','RN64(square_real+square_imag)']
    for flag in FALSE:assert t[flag] is False
    b=t['uniform_field_error_L1_hypothesis']
    keys=('ORIGINAL_field_L1_global_lower','ORIGINAL_power_global_lower','field_to_power_uniform_charge',
          'relative_field_global_upper','relative_power_global_upper')
    if b is None:
        assert all(t[k] is None for k in keys) and t['status']=='STOP'
    else:
        b=number(b);assert b>=0
        lf=max(F(0),sum(low)-b);lp=max(F(0),max(low)-b)**2
        prop=2*max(high)*b+b*b
        expected=[pair(lf),pair(lp),pair(prop),pair(b/lf) if lf else None,pair((prop+total)/lp) if lp else None]
        assert [t[k] for k in keys]==expected
        assert t['status']==('CONDITIONAL_SYNTHETIC_ONLY' if lf and lp else 'STOP')
    return total

r=json.loads((ROOT/REPORT).read_bytes());assert r['task_id']=='AXIAL-UNIFORM-POWER-BOX-HOST-001'
pins=pins_from(r);assert len(pins)==252
for p,h in pins.items():assert sha((ROOT/p).read_bytes())==h,p
source=r['inherited_pin_source'];old=read(source['path'],source['sha256']);cd=payload(old)['data']
d=payload(r);assert d['PASS'] is True and d['tests']==6;d=d['data']
rd=payload(read('coordinacion/respuestas/AXIAL-GROUP-RELATIVE-HOST-001-CODEX.json',
                pins['coordinacion/respuestas/AXIAL-GROUP-RELATIVE-HOST-001-CODEX.json']))['data']
fd=payload(read('coordinacion/respuestas/AXIAL-GROUP-REDUCTION-HOST-001-CODEX.json',
                pins['coordinacion/respuestas/AXIAL-GROUP-REDUCTION-HOST-001-CODEX.json']))['data']
pd=payload(read('coordinacion/respuestas/AXIAL-GROUP-POWER-HOST-001-CODEX.json',
                pins['coordinacion/respuestas/AXIAL-GROUP-POWER-HOST-001-CODEX.json']))['data']
packets=payload(read('coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json',
                    pins['coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json']))['packets']
presence='coordinacion/respuestas/AXIAL-NATIVE-PRESENCE-STOPS-001-CODEX.json'
controls=payload(read(presence,pins[presence]))['synthetic_controls']
packets.update({n:c['parent'] for n,c in controls.items()})
groups=boxes=0
for variant in ('missing','explicit_synthetic_INPUT_controls','zero_absolute','zero_relative'):
    a=d[variant];assert a['model']==MODEL and a['retained_variant']==variant
    assert a['inherited_pins_verified']==248
    assert a['case_order']==list(a['cases']) or set(a['case_order'])==set(a['cases']) # canonical JSON sorts maps
    expected_names=set(packets) if variant in ('missing','explicit_synthetic_INPUT_controls') else {'positive'}
    assert set(a['cases'])==expected_names and len(a['case_order'])==len(expected_names)
    assert a['new_scene_RN_nodes']==a['new_scene_geometry_phase_field_power_computations']==0
    for flag in FALSE:assert a[flag] is False
    count=0
    for name,c in a['cases'].items():
        oc=cd[variant]['cases'][name];rr=rd[variant]['cases'][name];pp=pd[variant]['cases'][name]
        ff=fd[pp['retained_variant']]['cases'][name];ctx=context(packets[name])
        assert ctx==c['context']==oc['context']==rr['context']==pp['context']==ff['context']
        assert c['retained_closure_case_sha256']==digest(oc)
        assert c['retained_source_STOP_FAILs']==oc['retained_source_STOP_FAILs']
        assert len(c['groups'])==len(ctx['groups'])
        for flag in FALSE:assert c[flag] is False
        for i,(g,og,rg,pg,fg) in enumerate(zip(c['groups'],oc['groups'],rr['groups'],pp['groups'],ff['groups'])):
            groups+=1
            assert [g['port'],g['coherence_group']]==ctx['groups'][i]
            assert g['source_order']==og['source_order']==rg['source_order']==pg['source_order']==fg['source_order']
            assert g['retained_closure_group_sha256']==digest(og)
            assert g['retained_field_group_sha256']==digest(fg) and g['retained_power_group_sha256']==digest(pg)
            assert g['retained_corner_limits_pass']==og['retained_corner_limits_pass']
            assert (g['retained_group_status'],g['retained_group_reason'])==(og['status'],og['reason'])
            assert g['remaining_missing_stage_ids']==og['missing_stage_ids']
            for flag in FALSE:assert g[flag] is False
            assert g['box_computed']==fg['accepted_retained_corner_group_reduction_CPU_only']
            if not g['box_computed']:
                assert (g['status'],g['reason'])==(og['status'],og['reason'])
                assert 'box' not in g
            else:
                count+=1;boxes+=1
                corners=fg['corner_sums'];assert len(corners)==4**len(g['source_order'])
                values=[list(map(decode,q['sum_uint64'])) for q in corners]
                box=[[pair(min(v[j] for v in values)),pair(max(v[j] for v in values))] for j in (0,1)]
                assert g['box']==g['box_theorem']['box']==box
                assert g['retained_field_corner_sha256']==[digest(q) for q in corners]
                assert g['retained_corner_error_NOT_uniform_B']==fg['error_L1_to_ORIGINAL_group_corner_sum_bound']
                total=verify_theorem(g['box_theorem'])
                assert g['box_theorem']['uniform_field_error_L1_hypothesis'] is None
                plan=pp['power_plan_result']
                cap=plan['groups'][i]['power_RN64_cap_abs'] if plan['power_INPUT_valid'] else None
                assert g['unchanged_power_RN64_cap_abs']==cap
                assert g['declared_box_RN_budget_evaluated']==(cap is not None)
                assert g['declared_box_RN_budget_fits']==(total<=number(cap) if cap is not None else False)
                if og['status']=='FAIL':assert (g['status'],g['reason'])==(og['status'],og['reason'])
                else:assert g['status']=='STOP'
    assert a['boxes_computed']==count
assert groups==36 and boxes==10
assert sum(len(c['retained_source_STOP_FAILs']) for c in d['explicit_synthetic_INPUT_controls']['cases'].values())==14
assert all(g['declared_box_RN_budget_fits'] for c in d['explicit_synthetic_INPUT_controls']['cases'].values()
           for g in c['groups'] if g['box_computed'])
for t in d['primitives']:verify_theorem(t)
assert len(d['primitives'])==6 and d['primitives'][1]['ORIGINAL_power_global_lower']==[0,1]
assert d['witnesses_reused']==cd['counterexamples']
for k in ('sum','square'):
    assert 0<number(d['witnesses_reused'][k]['interior']['RN_error_abs'])<=charge(F(4))
assert d['samples']['new_synthetic_RN_nodes']==36 and d['samples']['new_scene_RN_nodes']==0
nodes=0
for sample in d['samples']['samples']:
    assert sample['label']=='SYNTHETIC_NOT_SCENE'
    a,b=sample['input_uint64'];x,y=decode(a),decode(b);t=sample['box_theorem'];bound=verify_theorem(t)
    assert t['box']==[[pair(x),pair(x)],[pair(y),pair(y)]]
    trace=sample['trace'];assert len(trace)==3
    assert [(v['op'],v['left_uint64'],v['right_uint64']) for v in trace[:2]]==[('mul',a,a),('mul',b,b)]
    assert (trace[2]['op'],trace[2]['left_uint64'],trace[2]['right_uint64'])==('add',trace[0]['output_uint64'],trace[1]['output_uint64'])
    for v in trace:
        l,rr=v['left_uint64'],v['right_uint64']
        exact=decode(l)*decode(rr) if v['op']=='mul' else decode(l)+decode(rr)
        # Exact multiply-zero sign is XOR; the reused helper's zero rule is for addition.
        word=((l^rr)&SIGN) if not exact and v['op']=='mul' else round_word(exact,l,rr)
        assert v['output_uint64']==word
        assert v['exact_rational']==pair(exact)
        assert v['RN_error_abs']==pair(abs(decode(word)-exact));nodes+=1
    err=abs(decode(trace[-1]['output_uint64'])-(x*x+y*y))
    assert sample['actual_power_error_abs']==pair(err) and err<=bound
assert nodes==36 and len(d['rejections'])==25
labels=[q['label'] for q in d['rejections']];assert len(labels)==len(set(labels))
assert r['proof_scope']['scene_wide_closure'] is False and r['proof_scope']['device_authenticated'] is False
print(json.dumps({'PASS':True,'pins':len(pins),'groups_checked':groups,'declared_boxes_checked':boxes,
                  'synthetic_new_nodes_integer_checked':nodes,'old_scene_RN_replayed':0,
                  'rejections_retained':len(labels),'scene_wide_closure':False},sort_keys=True))
