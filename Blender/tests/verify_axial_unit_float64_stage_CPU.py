"""Independent integer IEEE RN64 oracle; no production imports or float arithmetic replay."""
import base64,hashlib,json,math,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT='coordinacion/respuestas/AXIAL-UNIT-FLOAT64-STAGE-CPU-001-CODEX.json'
PREVIOUS='coordinacion/respuestas/AXIAL-SOURCE-FLOAT64-STAGE-CPU-001-CODEX.json'
PREVIOUS_SHA='3075e1141e201cc773e88ab985b5f4da0f35da8f8ff86721dffd78db859c83b1'
FLAG='CPU_float64_Horner26_fixture_executed'
UNIT_FLAG='restricted_nonzero_unit_error_to_ORIGINAL_bound_proved'
MODEL='axial-pinned-Horner26-stage-CPU-float64-noFMA-v1'
LABELS=['square']+[n+'.'+op+str(j) for n in ('cos','sin') for j in range(5,-1,-1) for op in ('mul','add')]+['sin.final']
SIGN=2**63
def sha(raw):return hashlib.sha256(raw).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def read(path,h):
    raw=(ROOT/path).read_bytes();assert sha(raw)==h,path;return json.loads(raw)
def pins_from(r):
    if 'code_doc_sha256' in r:return dict(r['code_doc_sha256'])
    d=r['inherited_pin_source'];p=pins_from(read(d['path'],d['sha256']))
    p[d['path']]=d['sha256'];p.update(r['own_code_doc_sha256']);return p
def payload(r):
    t=r['test_run'];assert t['rc']==0
    b=zlib.decompress(base64.b64decode(t.get('stdout_zlib_base64') or ''.join(t['stdout_zlib_base64_chunks']),validate=True))
    assert len(b)==t['stdout_bytes'] and sha(b)==t['stdout_sha256'];return json.loads(b)
def pair(q):return [q.numerator,q.denominator]
def rational(v):
    assert type(v) is list and len(v)==2 and all(type(x) is int for x in v)
    assert v[1]>0 and math.gcd(*v)==1;return F(*v)
def bits(w):
    assert type(w) is int and 0<=w<2**64
    e=(w>>52)%2048;m=w%2**52;assert e<2047
    return (-1 if w&SIGN else 1)*F(m if e==0 else m+2**52)*F(2)**((1 if e==0 else e)-1075)
def lift32(w):
    assert type(w) is int and 0<=w<2**32
    sign=(w>>31)<<63;e=(w>>23)%256;m=w%2**23
    assert e<255 and (e or m==0)
    return sign if e==0 else sign|((e+896)<<52)|(m<<29)
def round64(q,zero_sign):
    if q==0:return zero_sign
    sign=SIGN if q<0 else 0;n,d=abs(q.numerator),q.denominator
    e=n.bit_length()-d.bit_length()
    if (n<d<<e if e>=0 else n<<-e<d):e-=1
    assert e<=1023
    grid=max(e,-1022)-52
    nn,dd=(n,d<<grid) if grid>=0 else (n<<-grid,d)
    m,rem=divmod(nn,dd);m+=int(2*rem>dd or (2*rem==dd and m&1))
    if m==0:return sign
    if e<-1022:
        assert m<=2**52
        return sign|m  # m==2^52 correctly reaches smallest normal
    if m==2**53:m>>=1;e+=1
    assert e<=1023 and 2**52<=m<2**53
    return sign|((e+1023)<<52)|(m-2**52)
def operation(x,y,kind):
    a,b=bits(x),bits(y);q=a*b if kind=='mul' else a+b
    if kind=='mul':zs=(x^y)&SIGN
    else:zs=SIGN if a==b==0 and x&SIGN and y&SIGN else 0
    return round64(q,zs),q

def verify_graph(point,corner):
    rotation=corner['rotation_RN64'];ops=rotation['operations'];coeff=rotation['coefficients']
    assert len(point['nodes'])==len(ops)==26 and [v['label'] for v in ops]==LABELS
    assert point['zero_canonicalization_performed'] is False
    assert point['new_CPU_float64_RN_nodes_executed']==26 and point['old_numeric_producers_reexecuted']==0
    assert point['quarter_bit_permutation_executed'] is True
    x=rotation['angle_uint64'];assert abs(bits(x))<=1 and point['angle_uint64']==x
    k=corner['quarter_argument']['quadrant_mod4'];assert type(k) is int and 0<=k<4 and point['quarter_index']==k
    generated=[];bad=[]
    def node(a,b,kind,label):
        result,q=operation(a,b,kind);i=len(generated);actual=point['nodes'][i];ref=ops[i]
        assert ref['label']==label and ref['op']==kind and ref['inputs_rational']==[pair(bits(a)),pair(bits(b))]
        assert actual['label']==label and actual['op']==kind and actual['input_uint64']==[a,b]
        assert actual['output_uint64']==result and actual['reference_output_uint64']==ref['output_uint64']
        assert rational(actual['observed_delta_rational'])==bits(result)-q
        match=result==ref['output_uint64'];assert actual['word_match'] is match
        if not match:bad.append(label)
        generated.append(result);return result
    z=node(x,x,'mul','square');output=[]
    for name,odd in [('cos',0),('sin',1)]:
        assert len(coeff[name])==7
        for j,c in enumerate(coeff[name]):
            exact=F((-1)**j,math.factorial(2*j+odd))
            assert rational(c['exact_rational'])==exact and rational(c['error_rational'])==abs(bits(c['uint64'])-exact)
            assert c['uint64']==round64(exact,0)
        h=coeff[name][6]['uint64']
        for j in range(5,-1,-1):
            p=node(h,z,'mul',name+'.mul'+str(j));h=node(p,coeff[name][j]['uint64'],'add',name+'.add'+str(j))
        if name=='sin':h=node(h,x,'mul','sin.final')
        output.append(h)
    c,s=output
    unit=[c,s] if k==0 else ([s^SIGN,c] if k==1 else ([c^SIGN,s^SIGN] if k==2 else [s,c^SIGN]))
    assert point['unpermuted_unit_uint64']==output and point['unit_uint64']==unit
    final=unit==corner['unit_uint64']
    assert point['node_word_mismatches']==bad and point['exact_retained_node_bits_match'] is (not bad)
    assert point['retained_final_unit_bits_match'] is final
    assert point['status']==('POINT_BITS_MATCH' if not bad and final else 'FAIL_RETAINED_NODE_BITS')
    return len(bad),final

def allfalse(obj):
    for key in false:assert obj[key] is False,key

r=json.loads((ROOT/REPORT).read_bytes());assert r['task_id']=='AXIAL-UNIT-FLOAT64-STAGE-CPU-001'
assert r['inherited_pin_source']=={'path':PREVIOUS,'sha256':PREVIOUS_SHA}
pins=pins_from(r);assert len(pins)==317 and len(r['own_code_doc_sha256'])==4
for path,h in pins.items():assert sha((ROOT/path).read_bytes())==h,path
prior=read(PREVIOUS,PREVIOUS_SHA);false=tuple(prior['proof_scope']);allfalse(r['proof_scope'])
prior_a=payload(prior)['data']['audit']
assert prior_a['point_graphs_bits_FAIL']==8 and prior_a['point_graphs_bits_MATCH']==0
assert sum(n['zero_sign_only_mismatch'] for c in prior_a['cases'].values() for s in c['sources'] for p in s.get('points',[]) for n in p['nodes'])==12
def data(path):return payload(read(path,pins[path]))
old=data('coordinacion/respuestas/AXIAL-NONZERO-UNIT-DOMAIN-HOST-001-CODEX.json')['data']['audit']
uniform=data('coordinacion/respuestas/AXIAL-UNIFORM-UNIT-HOST-001-CODEX.json')['data']['audit']
units=data('coordinacion/respuestas/AXIAL-QUARTER-UNIT-HOST-001-CODEX.json')['cases']
packets=data('coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json')['packets']
packets.update({n:v['parent'] for n,v in data('coordinacion/respuestas/AXIAL-NATIVE-PRESENCE-STOPS-001-CODEX.json')['synthetic_controls'].items()})
raw=payload(r);assert raw['PASS'] is True and raw['tests']==4
t=r['test_run'];assert t['threads']==t['affinity_mask']==1 and t['hard_child_timeout_seconds']==60 and t['elapsed_seconds']<60 and not t['timed_out']
a=raw['data']['audit'];allfalse(a)
assert a['model']==MODEL and a['case_order']==old['case_order']==prior_a['case_order'] and len(a['cases'])==17
assert a['runtime_probe']==prior_a['runtime_probe']
# Runtime strings need not authenticate hardware; retained exact six probe bits only.
assert a['runtime_probe']['PASS'] is True and a['runtime_probe']['new_CPU_float64_probe_operations']==6
expected=[0x3ff0000000000000,0x3ff0000000000002,1<<51,2,SIGN,0]
assert [p['actual_uint64'] for p in a['runtime_probe']['checks']]==expected
assert all(p['PASS'] is True and p['expected_uint64']==w for p,w in zip(a['runtime_probe']['checks'],expected))
executed=stopped=matched=failed=nodes=0;found=[]
for name in a['case_order']:
    case=a['cases'][name];allfalse(case);ctx=case['context'];packet=packets[name]
    assert ctx==old['cases'][name]['context']==uniform['cases'][name]['context']==prior_a['cases'][name]['context']
    assert digest(packet)==ctx['input_packet_sha256']
    buffers={k:base64.b64decode(v,validate=True) for k,v in packet['buffers_base64'].items()}
    for key,b in buffers.items():assert packet['manifest']['buffers'][key]=={'bytes':len(b),'sha256':sha(b)}
    meta=json.loads(buffers['input_metadata_json']);assert meta['explicit_group_contract']['assignments']==ctx['assignments']
    assert sha(buffers['original_scene_json'])==ctx['original_snapshot_sha256']
    quarter=units[name]
    for key in ('case_name','input_packet_sha256','scene_binding_sha256','word_ABI_sha256','source_order'):assert quarter[key]==ctx[key]
    cs=old['cases'][name]['sources'];us=uniform['cases'][name]['sources'];qs=quarter['sources']
    assert [s['source_id'] for s in case['sources']]==[s['source_id'] for s in cs]==[s['source_id'] for s in us]==[s['source_id'] for s in qs]==ctx['source_order']
    for i,(row,certificate,u,q) in enumerate(zip(case['sources'],cs,us,qs)):
        allfalse(row);assert row['status']=='STOP' and row['retained_unit_certificate_sha256']==digest(certificate)
        if not certificate[UNIT_FLAG]:
            stopped+=1;assert row[FLAG] is False and 'points' not in row
            assert row['reason']==certificate['reason'] and row['reason_provenance']==certificate['reason_provenance'];continue
        executed+=1;found.append(name);assert row[FLAG] is True
        proof=certificate['proof'];allfalse(proof);assert proof[UNIT_FLAG] is True
        assert proof['ORIGINAL_assignment_sha256']==digest(ctx['assignments'][i])
        assert proof['retained_uniform_unit_row_sha256']==digest(u) and u['retained_unit_source_sha256']==digest(q)
        assert proof['coefficient_profile_sha256']==digest(uniform['coefficient_profile'])
        assert q['phase_reference_id']==ctx['assignments'][i]['source_phase_reference_id']
        assert q['terminal_reference_id']==ctx['assignments'][i]['terminal_reference_id']
        assert q['unchanged_original_phase_cap_rad']==proof['unchanged_original_phase_cap_rad']
        corners=q['encoded_corner_units_HOST'];assert len(corners)==len(row['points'])==4
        assert [digest(c) for c in corners]==u['retained_angle_corner_sha256']
        lo,hi=map(rational,u['interval_theorem']['declared_angle_interval'])
        for j,(point,corner) in enumerate(zip(row['points'],corners)):
            assert point['witness_index']==j and point['retained_unit_corner_sha256']==digest(corner)
            assert corner['rotation_RN64']['coefficients']==uniform['coefficient_profile']
            angle=corner['rotation_RN64']['angle_uint64'];assert angle==corner['quarter_argument']['HOST_argument_uint64']
            assert lo<=bits(angle)<=hi
            nbad,final=verify_graph(point,corner);good=nbad==0 and final
            nodes+=26;matched+=int(good);failed+=int(not good)
assert (executed,stopped,nodes,matched,failed)==(2,17,208,8,0)
assert set(found)=={'nonexact_geometry_phase_PASS','thin_resolved'}
assert a['inherited_pins_verified']==313 and a['executed_source_fixture_sets']==executed
assert a['retained_sources_not_executed']==stopped and a['new_CPU_float64_RN_nodes_executed']==nodes
assert a['point_graphs_bits_MATCH']==matched and a['point_graphs_bits_FAIL']==failed
assert a['previous_SOURCE_eight_bit_FAILs_preserved'] is True and a['backend_domain_admitted'] is False
assert a['new_scene_selector_argument_encoder_executions']==a['old_numeric_producers_reexecuted']==0
mutation=raw['data']['last_node_mutation']
nbad,final=verify_graph(mutation['actual'],mutation['corner']);assert nbad==1 and final
assert mutation['actual']['node_word_mismatches']==['sin.final']
rejects=raw['data']['rejections'];assert len(rejects)==len({v['label'] for v in rejects})==27
print(json.dumps({'PASS':True,'pins':len(pins),'CPU_Horner_nodes_checked_by_integer_IEEE':nodes,
 'point_graph_bits_MATCH':matched,'point_graph_bits_FAIL':failed,'retained_sources_not_executed':stopped,
 'synthetic_mutation_nodes_checked':26,'synthetic_reference_FAIL_preserved':True,
 'previous_SOURCE_8_bit_FAILs_12_signed_zero_mismatches_preserved':True,'rejections':len(rejects),
 'fresh_scene_selector_argument_executed':False,'backend_domain_admission':'STOP','GPU_executed':False},sort_keys=True))
