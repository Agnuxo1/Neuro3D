"""Independent stdlib verification of new uniform SOURCE ledger; no production imports."""
import base64,hashlib,json,math,struct,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT='coordinacion/respuestas/AXIAL-NONZERO-SOURCE-DOMAIN-HOST-001-CODEX.json'
PREVIOUS='coordinacion/respuestas/AXIAL-NONZERO-UNIT-DOMAIN-HOST-001-CODEX.json'
PREVIOUS_SHA='c48285861cbfffbc191e4c52796c60b7879e0cced34e15272b2c264aa75572b2'
FLAG='restricted_nonzero_bare_source_error_to_fixed_ORIGINAL_bound_proved'
UFLAG='restricted_nonzero_unit_error_to_ORIGINAL_bound_proved'
MODEL='axial-nonzero-fixed-source-uniform-product-HOST-v1'
HYP='binary64 nearest-even gradual underflow; fixed retained coefficients, Horner26, no FMA'
def sha(x):return hashlib.sha256(x).hexdigest()
def digest(x):return sha(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def read(p,h):
    raw=(ROOT/p).read_bytes();assert sha(raw)==h,p;return json.loads(raw)
def pins_from(r):
    if 'code_doc_sha256' in r:return dict(r['code_doc_sha256'])
    v=r['inherited_pin_source'];p=pins_from(read(v['path'],v['sha256']))
    p[v['path']]=v['sha256'];p.update(r['own_code_doc_sha256']);return p
def payload(r):
    t=r['test_run'];assert t['rc']==0
    raw=zlib.decompress(base64.b64decode(t.get('stdout_zlib_base64') or ''.join(t['stdout_zlib_base64_chunks']),validate=True))
    assert len(raw)==t['stdout_bytes'] and sha(raw)==t['stdout_sha256'];return json.loads(raw)
def rat(x):
    assert type(x) is list and len(x)==2 and all(type(v) is int for v in x)
    assert x[1]>0 and math.gcd(*x)==1;return F(*x)
def big(x):
    assert type(x) is list and len(x)==2 and all(type(v) is str and v==str(int(v)) for v in x)
    n,d=map(int,x);assert d>0 and math.gcd(n,d)==1;return F(n,d)
def pair(x):return [x.numerator,x.denominator]
def dec(x):return list(map(str,pair(x)))
def bits(w,width):
    assert type(w) is int and 0<=w<2**width
    mb,eb,bias=(52,11,1023) if width==64 else (23,8,127)
    e=(w>>mb)%2**eb;m=w%2**mb
    assert e!=2**eb-1 and (e!=0 or m==0)
    return (-1 if w>>(width-1) else 1)*F((2**mb+m) if e else 0)*F(2)**(e-bias-mb)
def check_false(x):
    for k in false:assert x[k] is False,k
def E(m):
    assert 0<=m<=bits(0x7fefffffffffffff,64)/2
    return F(m,2**53)+F(1,2**1075) if m else F(0)

r=json.loads((ROOT/REPORT).read_bytes());assert r['task_id']=='AXIAL-NONZERO-SOURCE-DOMAIN-HOST-001'
assert r['inherited_pin_source']=={'path':PREVIOUS,'sha256':PREVIOUS_SHA}
pins=pins_from(r)
for p,h in pins.items():assert sha((ROOT/p).read_bytes())==h,p
assert len(pins)==307 and len(r['own_code_doc_sha256'])==4
prior=read(PREVIOUS,PREVIOUS_SHA);false=tuple(prior['proof_scope']);check_false(r['proof_scope'])
old=payload(prior)['data']['audit'];raw=payload(r)
assert raw['PASS'] is True and raw['tests']==4
t=r['test_run'];assert t['threads']==1 and t['affinity_mask']==1 and t['hard_child_timeout_seconds']==60 and t['elapsed_seconds']<60 and not t['timed_out']
a=raw['data']['audit'];check_false(a);assert a['model']==MODEL and a['case_order']==old['case_order']
assert len(a['cases'])==17 and a['inherited_pins_verified']==303 and a['new_RN_or_old_producer_executions']==0
prodpath='coordinacion/respuestas/AXIAL-SOURCE-PRODUCT-HOST-001-CODEX.json'
products=payload(read(prodpath,pins[prodpath]))['cases']
ingress='coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json'
packets=payload(read(ingress,pins[ingress]))['packets']
presence='coordinacion/respuestas/AXIAL-NATIVE-PRESENCE-STOPS-001-CODEX.json'
packets.update({n:v['parent'] for n,v in payload(read(presence,pins[presence]))['synthetic_controls'].items()})
proved=stops=zeros=nodes_checked=0;values={}
for n in a['case_order']:
    c=a['cases'][n];ctx=c['context'];check_false(c)
    assert ctx==old['cases'][n]['context']
    packet=packets[n];assert digest(packet)==ctx['input_packet_sha256']
    bufs={k:base64.b64decode(v,validate=True) for k,v in packet['buffers_base64'].items()}
    for k,v in bufs.items():assert packet['manifest']['buffers'][k]=={'bytes':len(v),'sha256':sha(v)}
    meta=json.loads(bufs['input_metadata_json']);snapshot=json.loads(bufs['original_scene_json'])
    assert ctx['assignments']==meta['explicit_group_contract']['assignments'] and ctx['original_snapshot_sha256']==sha(bufs['original_scene_json'])
    pp=products[n]
    for k in ('case_name','input_packet_sha256','scene_binding_sha256','word_ABI_sha256','source_order'):assert pp[k]==ctx[k]
    us=old['cases'][n]['sources'];ps=pp['sources']
    assert [s['source_id'] for s in c['sources']]==[s['source_id'] for s in us]==[s['source_id'] for s in ps]==ctx['source_order']
    for i,(s,u,pr) in enumerate(zip(c['sources'],us,ps)):
        check_false(s);assert s['status']=='STOP' and s['retained_unit_row_sha256']==digest(u)
        if not u[UFLAG]:
            assert not s[FLAG] and 'proof' not in s and s['reason']==u['reason'] and s['reason_provenance']==u['reason_provenance']
            if s['reason_provenance']=='unchanged_retained_unit_STOP':stops+=1
            else:assert s['reason_provenance']=='outside_nonzero_scope';zeros+=1
            continue
        proved+=1;p=s['proof'];check_false(p);assert p[FLAG] is s[FLAG] is True and p['model']==MODEL
        up=u['proof'];assert up[UFLAG] is True and up['arithmetic_hypothesis']==HYP
        B=big(up['polynomial_unit_L1_bound_decimal']);d=rat(up['composed_parameter_argument_phase_bound_rad'])
        U=big(up['uniform_unit_L1_to_fixed_ORIGINAL_bound_decimal'])
        assert 0<B<F(1,2) and d>=0 and U==B+2*d and U==big(p['unit_L1_error_to_fixed_ORIGINAL_decimal'])
        assert d==rat(up['parameter_phase_bound_rad'])+rat(up['argument_phase_bound_rad'])
        assert big(up['uniform_phase_to_fixed_ORIGINAL_bound_decimal'])==B/(1-B)+d<=F(1,10**12)
        assignment=ctx['assignments'][i];sid=s['source_id']
        assert p['source_id']==sid and p['original_input_packet_sha256']==digest(packet)
        assert p['ORIGINAL_assignment_sha256']==up['ORIGINAL_assignment_sha256']==digest(assignment)
        assert pr['source_product_evaluated'] is True and pr['phase_reference_id']==assignment['source_phase_reference_id'] and pr['terminal_reference_id']==assignment['terminal_reference_id']
        assert packet['manifest']['layout']['sources']['stride_words']==32 and len(bufs['sources'])==128*len(ctx['source_order'])
        fieldbytes=bufs['sources'][128*i+112:128*i+128]
        assert fieldbytes==struct.pack('<dd',*snapshot['sources'][i]['field_reim']) and snapshot['sources'][i]['id']==sid
        words=list(struct.unpack('<QQ',fieldbytes));original=[bits(w,64) for w in words]
        assert words==p['fixed_original_source_uint64']==pr['original_source_uint64']
        assert p['fixed_original_source_rational']==list(map(pair,original))
        corners=pr['encoded_corner_products'];assert len(corners)==4;enc=corners[0]['source_encoder']
        assert all(v['source_encoder']==enc for v in corners) and enc['original_source_uint64']==words
        limbs=enc['source_limb_uint32'];assert len(limbs)==4 and p['source_hilo_uint32']==limbs
        limbvals=[bits(w,32) for w in limbs];decoded=[sum(limbvals[:2]),sum(limbvals[2:])]
        assert p['decoded_source_rational']==enc['source_exact_limb_sum_rational']==list(map(pair,decoded))
        transport=struct.pack('<IIII',*limbs)
        assert base64.b64decode(enc['source_hilo_le_base64'],validate=True)==transport and enc['source_hilo_le_sha256']==sha(transport)
        err=sum(abs(x-y) for x,y in zip(original,decoded));assert err==rat(p['nonzero_encoding_error_L1'])==rat(enc['source_encoding_error_L1'])==F(1,2**55)
        assert rat(enc['source_norm_L1'])==sum(map(abs,original))
        for j,trace in enumerate(enc['HOST_trace']):
            assert trace['original']==pair(original[j]) and trace['high']==pair(limbvals[2*j])
            assert trace['HOST_exact_residual']==pair(original[j]-limbvals[2*j]) and trace['represented']==pair(decoded[j])
            assert trace['encoding_error']==pair(abs(original[j]-decoded[j]))
        for corner in corners:
            assert corner['model']=='axial-source-hilo32-decode-RN64-product-HOST-v1'
            ops=corner['operations'];assert len(ops)==8 and [v['label'] for v in ops]==['decode0','decode1','ac','bd','ad','bc','real','imag']
            assert [v['op'] for v in ops]==['add','add','mul','mul','mul','mul','add','add']
            for j,op in enumerate(ops[:2]):
                assert op['inputs']==[pair(limbvals[2*j]),pair(limbvals[2*j+1])] and bits(op['output_uint64'],64)==decoded[j] and rat(op['delta'])==0
        M,L=1+U,2+U;assert p['represented_unit_component_abs_upper_decimal']==dec(M) and p['represented_unit_norm_L1_upper_decimal']==dec(L)
        ma,mb=abs(decoded[0])*M,abs(decoded[1])*M;ea,eb=E(ma),E(mb)
        addition=ma+mb+ea+eb;ead=E(addition)
        expected=[('ac',ma,ea),('bd',mb,eb),('ad',ma,ea),('bc',mb,eb),('real',addition,ead),('imag',addition,ead)]
        for node,(label,m,e) in zip(p['product_RN_nodes'],expected):
            assert node=={'label':label,'exact_abs_upper_decimal':dec(m),'RN_error_abs_decimal':dec(e)};nodes_checked+=1
        assert len(p['product_RN_nodes'])==6
        RN=2*(ea+eb+ead)
        charges={'source_encoding':dec(err*L),'source_decode_RN64':dec(F(0)),
                 'unit_to_fixed_ORIGINAL':dec(sum(map(abs,original))*U),'product_RN64':dec(RN)}
        assert p['charges_L1_decimal']==charges
        total=sum(map(big,charges.values()));assert big(p['uniform_bare_source_L1_error_to_fixed_ORIGINAL_bound_decimal'])==total
        assert p['retained_unit_row_sha256']==digest(u) and p['retained_product_row_sha256']==digest(pr) and p['retained_encoder_sha256']==digest(enc)
        assert p['unchanged_original_phase_cap_rad']==up['unchanged_original_phase_cap_rad']==meta['original_path_phase_caps'][sid]==[1,10**12]
        assert p['unchanged_global_field_L1_cap_NOT_source_allocation']==ctx['unchanged_field_L1_cap']
        assert p['units']=='ORIGINAL-source-field-amplitude-L1' and p['arithmetic_hypothesis']==HYP+'; decode2/product6 RN64, no FMA'
        assert p['material_reflection_charge_included'] is False and p['new_RN_or_old_producer_executions']==0 and p['status']=='STOP'
        values[n]={'bare_source_L1_bound_approx':float(total),'encoding_charge_approx':float(err*L),'product_RN_charge_approx':float(RN)}
assert (proved,stops,zeros,nodes_checked)==(2,14,3,12)
assert set(values)=={'nonexact_geometry_phase_PASS','thin_resolved'}
assert (a['restricted_nonzero_bare_source_bounds_proved'],a['retained_unit_STOPs'],a['zero_domains_outside_scope'])==(2,14,3)
rejections=raw['data']['rejections'];assert len(rejections)==len({v['label'] for v in rejections})==30
g=raw['data']['generic_complex_control'];ga,gb,gm=map(rat,[g['a'],g['b'],g['M']])
ge=E(abs(ga)*gm)+E(abs(gb)*gm)
assert big(g['bound_decimal'])==2*ge+2*E((abs(ga)+abs(gb))*gm+ge)
print(json.dumps({'PASS':True,'pins':len(pins),'restricted_nonzero_bare_source_bounds':proved,
    'new_product_nodes_checked':nodes_checked,'retained_STOPs':stops,'zero_domains_outside_scope':zeros,
    'reject_controls':len(rejections),'approximate_display_only':values,'new_RN_executions':0,'full_pipeline':'STOP'},sort_keys=True))
