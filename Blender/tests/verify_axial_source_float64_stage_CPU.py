"""Independent integer IEEE RN64 oracle; no production imports or float arithmetic replay."""
import base64,hashlib,json,math,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT='coordinacion/respuestas/AXIAL-SOURCE-FLOAT64-STAGE-CPU-001-CODEX.json'
PREVIOUS='coordinacion/respuestas/AXIAL-NONZERO-SOURCE-DOMAIN-HOST-001-CODEX.json'
PREVIOUS_SHA='d0157a47b48bf999a80aecefecef10600a1193a5374845c61088ec2382dfe9ad'
FLAG='CPU_float64_SOURCE_stage_fixture_executed'
SOURCE_FLAG='restricted_nonzero_bare_source_error_to_fixed_ORIGINAL_bound_proved'
MODEL='axial-pinned-SOURCE-stage-CPU-float64-noFMA-v1'
LABELS=['decode0','decode1','ac','bd','ad','bc','real','imag']
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
def verify_graph(point,limbs,units,ops):
    assert len(point['nodes'])==len(ops)==8 and [v['label'] for v in ops]==LABELS
    assert point['zero_canonicalization_performed'] is False and point['new_CPU_float64_RN_nodes_executed']==8
    assert point['old_numeric_producers_reexecuted']==0
    high,low,ih,il=map(lift32,limbs);c,d=units;generated=[];bad=[];signed=0
    def node(x,y,kind,label):
        expected,q=operation(x,y,kind);i=len(generated);actual=point['nodes'][i];ref=ops[i]
        assert ref['label']==label and ref['op']==kind and ref['inputs']==[pair(bits(x)),pair(bits(y))]
        assert actual['label']==label and actual['op']==kind and actual['input_uint64']==[x,y]
        assert actual['output_uint64']==expected and actual['reference_output_uint64']==ref['output_uint64']
        assert rational(actual['observed_delta_rational'])==bits(expected)-q
        match=expected==ref['output_uint64'];zero=not match and expected%SIGN==ref['output_uint64']%SIGN==0
        assert actual['word_match'] is match and actual['zero_sign_only_mismatch'] is zero
        if not match:bad.append(label)
        generated.append(expected);return expected
    a=node(high,low,'add','decode0');b=node(ih,il,'add','decode1')
    ac=node(a,c,'mul','ac');bd=node(b,d,'mul','bd')
    ad=node(a,d,'mul','ad');bc=node(b,c,'mul','bc')
    real=node(ac,bd^SIGN,'add','real');imag=node(ad,bc,'add','imag')
    assert point['product_uint64']==[real,imag] and point['node_word_mismatches']==bad
    assert point['exact_retained_node_bits_match'] is (not bad)
    assert point['status']==('FAIL_RETAINED_NODE_BITS' if bad else 'POINT_BITS_MATCH')
    return len(bad),sum(v['zero_sign_only_mismatch'] for v in point['nodes'])
def allfalse(v):
    for k in false:assert v[k] is False,k

r=json.loads((ROOT/REPORT).read_bytes());assert r['task_id']=='AXIAL-SOURCE-FLOAT64-STAGE-CPU-001'
assert r['inherited_pin_source']=={'path':PREVIOUS,'sha256':PREVIOUS_SHA}
pins=pins_from(r)
for path,h in pins.items():assert sha((ROOT/path).read_bytes())==h,path
assert len(pins)==312 and len(r['own_code_doc_sha256'])==4
prior=read(PREVIOUS,PREVIOUS_SHA);false=tuple(prior['proof_scope']);allfalse(r['proof_scope'])
old=payload(prior)['data']['audit'];raw=payload(r);assert raw['PASS'] is True and raw['tests']==4
t=r['test_run'];assert t['threads']==t['affinity_mask']==1 and t['hard_child_timeout_seconds']==60 and t['elapsed_seconds']<60 and not t['timed_out']
a=raw['data']['audit'];allfalse(a);assert a['model']==MODEL and a['case_order']==old['case_order'] and len(a['cases'])==17
probe=a['runtime_probe'];assert probe['PASS'] is True and probe['new_CPU_float64_probe_operations']==6
expected_probes=[('tie_even_one',0x3ff0000000000000),('tie_even_odd',0x3ff0000000000002),('gradual_product',1<<51),('gradual_add',2),('negative_zero_product',SIGN),('opposite_zeros_add',0)]
assert len(probe['checks'])==6
for v,(label,w) in zip(probe['checks'],expected_probes):
    assert v=={'label':label,'actual_uint64':w,'expected_uint64':w,'PASS':True}
prodpath='coordinacion/respuestas/AXIAL-SOURCE-PRODUCT-HOST-001-CODEX.json'
products=payload(read(prodpath,pins[prodpath]))['cases']
ingress='coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json'
packets=payload(read(ingress,pins[ingress]))['packets']
presence='coordinacion/respuestas/AXIAL-NATIVE-PRESENCE-STOPS-001-CODEX.json'
packets.update({n:v['parent'] for n,v in payload(read(presence,pins[presence]))['synthetic_controls'].items()})
executed=stopped=matched=failed=nodes=badnodes=signednodes=final_match=0
per_case={}
for name in a['case_order']:
    case=a['cases'][name];ctx=case['context'];allfalse(case)
    assert ctx==old['cases'][name]['context'];packet=packets[name];assert digest(packet)==ctx['input_packet_sha256']
    buf={k:base64.b64decode(v,validate=True) for k,v in packet['buffers_base64'].items()}
    for k,v in buf.items():assert packet['manifest']['buffers'][k]=={'bytes':len(v),'sha256':sha(v)}
    meta=json.loads(buf['input_metadata_json']);assert meta['explicit_group_contract']['assignments']==ctx['assignments']
    assert ctx['original_snapshot_sha256']==sha(buf['original_scene_json'])
    pp=products[name]
    for k in ('case_name','input_packet_sha256','scene_binding_sha256','word_ABI_sha256','source_order'):assert ctx[k]==pp[k]
    cs=old['cases'][name]['sources'];ps=pp['sources']
    assert [s['source_id'] for s in case['sources']]==[s['source_id'] for s in cs]==[s['source_id'] for s in ps]==ctx['source_order']
    for i,(s,certificate,pr) in enumerate(zip(case['sources'],cs,ps)):
        allfalse(s);assert s['status']=='STOP' and s['retained_source_certificate_sha256']==digest(certificate)
        if not certificate[SOURCE_FLAG]:
            stopped+=1;assert s[FLAG] is False and s['bare_source_values_computed_new'] is False and 'points' not in s
            assert s['reason']==certificate['reason'] and s['reason_provenance']==certificate['reason_provenance'];continue
        executed+=1;assert s[FLAG] is True and s['bare_source_values_computed_new'] is True
        p=certificate['proof'];assert p[SOURCE_FLAG] is True and p['original_input_packet_sha256']==digest(packet)
        assert p['retained_product_row_sha256']==digest(pr) and p['ORIGINAL_assignment_sha256']==digest(ctx['assignments'][i])
        assert pr['phase_reference_id']==ctx['assignments'][i]['source_phase_reference_id'] and pr['terminal_reference_id']==ctx['assignments'][i]['terminal_reference_id']
        assert p['fixed_original_source_uint64']==pr['original_source_uint64']
        sourcebytes=buf['sources'][128*i+112:128*i+128]
        assert list(int.from_bytes(sourcebytes[j:j+8],'little') for j in (0,8))==p['fixed_original_source_uint64']
        corners=pr['encoded_corner_products'];assert len(s['points'])==len(corners)==4
        labels=[]
        for j,(v,c) in enumerate(zip(s['points'],corners)):
            assert v['witness_index']==j and v['retained_corner_product_sha256']==digest(c)
            enc=c['source_encoder'];assert v['source_encoder_sha256']==p['retained_encoder_sha256']==digest(enc)
            assert v['unit_uint64']==c['unit_uint64'] and enc['source_limb_uint32']==p['source_hilo_uint32']
            blob=base64.b64decode(enc['source_hilo_le_base64'],validate=True)
            assert len(blob)==16 and sha(blob)==enc['source_hilo_le_sha256']
            assert [int.from_bytes(blob[k:k+4],'little') for k in range(0,16,4)]==enc['source_limb_uint32']
            nbad,nsigned=verify_graph(v,enc['source_limb_uint32'],c['unit_uint64'],c['operations'])
            nodes+=8;badnodes+=nbad;signednodes+=nsigned
            matched+=int(nbad==0);failed+=int(nbad!=0);final_match+=int(v['product_uint64']==c['product_uint64'])
            labels.append(v['node_word_mismatches'])
        per_case[name]=labels
        assert s['exact_all_fixture_node_bits_match'] is all(v['exact_retained_node_bits_match'] for v in s['points'])
assert (executed,stopped,nodes,matched,failed,badnodes,signednodes,final_match)==(2,17,64,0,8,12,12,8)
assert per_case=={'nonexact_geometry_phase_PASS':[['bd','bc']]*4,'thin_resolved':[['bd']]*4}
assert a['inherited_pins_verified']==308 and a['executed_source_fixture_sets']==executed and a['retained_sources_not_executed']==stopped
assert a['new_CPU_float64_RN_nodes_executed']==nodes and a['point_graphs_bits_MATCH']==matched and a['point_graphs_bits_FAIL']==failed
assert a['old_numeric_producers_reexecuted']==0 and a['source_encoder_executed_new'] is False and a['unit_or_scene_inference_executed_new'] is False
z=raw['data']['signed_zero_control'];assert z['FAIL_preserved'] is True and z['native_signed_zero_graph_equivalence_proved'] is False
nbad,nsigned=verify_graph(z['actual'],z['limbs_uint32'],z['unit_uint64'],z['reference_ops'])
assert nbad==nsigned==1 and z['actual']['node_word_mismatches']==['bc']
rejected=raw['data']['rejections'];assert len(rejected)==len({v['label'] for v in rejected})==29
print(json.dumps({'PASS':True,'pins':len(pins),'CPU_stage_nodes_checked_by_integer_IEEE':nodes,'synthetic_control_nodes':8,
    'retained_sources_not_executed':stopped,'point_graph_bits_MATCH':matched,'point_graph_bits_FAIL_preserved':failed,
    'signed_zero_node_mismatches_preserved':signednodes,'final_product_bits_match_NOT_graph_admission':final_match,
    'rejections':len(rejected),'fresh_scene_unit_inference_executed':False,'backend_admission':'STOP','GPU_executed':False},sort_keys=True))
