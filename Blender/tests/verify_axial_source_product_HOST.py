"""Read-only independent source-product verifier: stdlib, NO production imports."""
import base64
from collections import Counter
from fractions import Fraction as F
import hashlib, json, math, struct, sys, time, zlib
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
REPORT = 'coordinacion/respuestas/AXIAL-SOURCE-PRODUCT-HOST-001-CODEX.json'
PREVIOUS = 'coordinacion/respuestas/AXIAL-QUARTER-UNIT-HOST-001-CODEX.json'
SHA = '9391669247fa4b6b3576ac640174f1cd853535c78591d67ae27adc72f19beaba'
def digest(v):
    return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def read(path):
    return json.loads((ROOT/path).read_bytes())
def payload(r):
    t=r['test_run']
    raw=zlib.decompress(base64.b64decode(t.get('stdout_zlib_base64') or ''.join(t['stdout_zlib_base64_chunks']),validate=True))
    assert t['rc']==0 and len(raw)==t['stdout_bytes'] and hashlib.sha256(raw).hexdigest()==t['stdout_sha256']
    return json.loads(raw)
def pins(r):
    if 'code_doc_sha256' in r:
        return dict(r['code_doc_sha256'])
    dep=r['inherited_pin_source']
    assert hashlib.sha256((ROOT/dep['path']).read_bytes()).hexdigest()==dep['sha256']
    p=pins(read(dep['path']));p[dep['path']]=dep['sha256'];p.update(r['own_code_doc_sha256'])
    return p
def decode(w,bits):
    assert type(w) is int and 0<=w<2**bits
    mb,eb,bias=(23,8,127) if bits==32 else (52,11,1023)
    e=(w>>mb)&(2**eb-1);m=w&(2**mb-1)
    assert e!=(2**eb-1)
    power=(e if e else 1)-bias-mb
    n=m+(2**mb if e else 0)
    v=F(n*2**power) if power>=0 else F(n,2**-power)
    return -v if w>>(bits-1) else v
def nearest(q,bits):
    if not q:
        return 0
    q=F(q);sgn=(q<0)<<(bits-1);a=abs(q)
    fmt,typ=('f','I') if bits==32 else ('d','Q')
    initial=struct.unpack('<'+typ,struct.pack('<'+fmt,float(a)))[0]
    candidates=[w for w in range(max(0,initial-2),initial+3) if w<((255<<23) if bits==32 else (2047<<52))]
    best=min(candidates,key=lambda w:(abs(decode(w,bits)-a),w&1))
    if best==0:
        return sgn
    mb=23 if bits==32 else 52
    assert best>>mb, 'selected subnormal'
    return best|sgn
def check_product(p):
    enc=p['source_encoder']
    s=[decode(w,64) for w in enc['original_source_uint64']]
    sh=[];expected=[]
    for q in s:
        h=nearest(q,32);hq=decode(h,32);l=nearest(q-hq,32)
        expected += [h,l];sh.append(hq+decode(l,32))
    assert enc['source_limb_uint32']==expected
    assert [F(*v) for v in enc['source_exact_limb_sum_rational']]==sh
    es=sum((abs(x-y) for x,y in zip(s,sh)),F(0))
    assert F(*enc['source_encoding_error_L1'])==es
    raw=struct.pack('<4I',*expected)
    assert base64.b64decode(enc['source_hilo_le_base64'])==raw and hashlib.sha256(raw).hexdigest()==enc['source_hilo_le_sha256']
    sd=[];edges=[]
    for i in range(2):
        a,b=map(lambda w:decode(w,32),expected[2*i:2*i+2])
        w=nearest(a+b,64);sd.append(decode(w,64));edges.append(('decode'+str(i),'add',a,b))
    u=[decode(w,64) for w in p['unit_uint64']]
    a,b=sd;c,d=u
    mul=[]
    for label,x,y in [('ac',a,c),('bd',b,d),('ad',a,d),('bc',b,c)]:
        mul.append(decode(nearest(x*y,64),64));edges.append((label,'mul',x,y))
    ac,bd,ad,bc=mul
    edges += [('real','add',ac,-bd),('imag','add',ad,bc)]
    assert len(p['operations'])==8
    for node,(label,op,x,y) in zip(p['operations'],edges):
        assert node['label']==label and node['op']==op
        assert [F(*v) for v in node['inputs']]==[x,y]
        exact=x*y if op=='mul' else x+y
        w=nearest(exact,64);v=decode(w,64)
        assert node['output_uint64']==w and F(*node['delta'])==v-exact
    outs=[p['operations'][-2]['output_uint64'],p['operations'][-1]['output_uint64']]
    values=[decode(w,64) for w in outs]
    assert outs==p['product_uint64'] and values==[F(*v) for v in p['product_rational']]
    assert sd==[F(*v) for v in p['source_decoded_RN64']]
    ed=sum((abs(x-y) for x,y in zip(sd,sh)),F(0))
    er=sum((abs(F(*v['delta'])) for v in p['operations'][2:]),F(0))
    nu=sum(map(abs,u),F(0));ns=sum(map(abs,s),F(0));bu=F(*p['unit_error_L1_to_ORIGINAL_bound'])
    charges={'source_encoding':es*nu,'source_decode_RN64':ed*nu,'unit_to_ORIGINAL':ns*bu,'product_RN64':er}
    assert charges=={k:F(*v) for k,v in p['charges_L1'].items()}
    assert F(*p['error_L1_to_original_source_times_ideal_unit_bound'])==sum(charges.values(),F(0))
    exact=[a*c-b*d,a*d+b*c];original=[s[0]*c-s[1]*d,s[0]*d+s[1]*c]
    assert exact==[F(*v) for v in p['exact_decoded_product']]
    assert original==[F(*v) for v in p['exact_original_times_represented_unit']]
    obs=sum((abs(x-y) for x,y in zip(values,original)),F(0))
    assert F(*p['observed_error_to_original_times_represented_unit_L1'])==obs<=es*nu+ed*nu+er
    assert p['costs_partial']=={'HOST_encoder_RN32_casts':4,'HOST_exact_residual_subtractions':2,'HOST_decode_RN64_adds':2,'modeled_product_RN64_muls':4,'modeled_product_RN64_adds':2}
    for k in ('amplitude_budget_accepted','accepted_full_field_pipeline','field_sum_computed','reflection_coefficient_applied','GPU_executed'):
        assert p[k] is False
    return values,s
def ideal_reference(prior):
    # The same pinned PI enclosure; no implementation functions imported or executed.
    lo=F('3.14159265358979323846264338327950288419716939937510')
    hi=F('3.14159265358979323846264338327950288419716939937511')
    arg=prior['ideal_ORIGINAL_unit_HOST']['quarter_argument']
    t=F(*arg['quarter_residual_HOST_rational']);k=arg['quarter_turns_HOST']%4
    x=(lo+hi)*t
    c=sum((F((-1)**j,math.factorial(2*j))*x**(2*j) for j in range(40)),F(0))
    s=sum((F((-1)**j,math.factorial(2*j+1))*x**(2*j+1) for j in range(40)),F(0))
    uncertainty=abs(x)**80/math.factorial(80)+abs(x)**81/math.factorial(81)+2*abs(t)*(hi-lo)
    return [(c,s),(-s,c),(-c,-s),(s,-c)][k],uncertainty
def main():
    start=time.perf_counter();r=read(REPORT);data=payload(r)
    inherited=pins(read(PREVIOUS));inherited[PREVIOUS]=SHA
    assert hashlib.sha256((ROOT/PREVIOUS).read_bytes()).hexdigest()==SHA
    assert data['pins']==inherited
    allpins=dict(inherited);allpins.update(r['own_code_doc_sha256'])
    for p,h in allpins.items():
        assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    old=payload(read(PREVIOUS))['cases']
    packets=payload(read('coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json'))['packets']
    controls=payload(read('coordinacion/respuestas/AXIAL-NATIVE-PRESENCE-STOPS-001-CODEX.json'))['synthetic_controls']
    inputs={n:p for n,p in packets.items()};inputs.update({n:c['parent'] for n,c in controls.items()})
    assert data['PASS'] is True and data['tests']==7
    assert set(data['cases'])==set(old)==set(inputs) and len(old)==17
    evaluated=stops=rows=0;products=[]
    for name,case in data['cases'].items():
        prev=old[name];packet=inputs[name]
        for key in ('input_packet_sha256','overlay_sha256','scene_binding_sha256','word_ABI_sha256','source_order'):
            assert case[key]==prev[key]
        raw=base64.b64decode(packet['buffers_base64']['sources'])
        snapshot=json.loads(base64.b64decode(packet['buffers_base64']['original_scene_json']))
        assert len(case['sources'])==len(prev['sources'])==len(case['source_order'])
        for i,(row,prior) in enumerate(zip(case['sources'],prev['sources'])):
            rows+=1
            assert row['source_id']==prior['source_id']==snapshot['sources'][i]['id']
            for key in ('phase_reference_id','terminal_reference_id'):
                assert row[key]==prior[key]
            assert row['upstream_unit_row_sha256']==digest(prior)
            assert row['original_source_uint64']==list(struct.unpack('<QQ',raw[128*i+112:128*i+128]))
            assert struct.pack('<QQ',*row['original_source_uint64'])==struct.pack('<dd',*snapshot['sources'][i]['field_reim'])
            assert row['source_product_evaluated']==prior['accepted_unit_phase_bound_CPU_only']
            if not row['source_product_evaluated']:
                stops+=1;assert row['reason']==prior['reason'] and 'encoded_corner_products' not in row
                continue
            evaluated+=1
            assert row['unchanged_original_phase_cap_rad']==prior['unchanged_original_phase_cap_rad']
            assert row['upstream_unit_phase_bound_rad']==prior['composed_unit_phase_bound_rad']
            assert len(row['encoded_corner_products'])==4
            ideal,unc=ideal_reference(prior);bounds=[]
            for p,u in zip(row['encoded_corner_products'],prior['encoded_corner_units_HOST']):
                assert p['source_encoder']['original_source_uint64']==row['original_source_uint64']
                assert p['unit_uint64']==u['unit_uint64']
                assert p['unit_error_L1_to_ORIGINAL_bound']==prior['composed_unit_error_L1_to_ORIGINAL_bound']
                values,s=check_product(p);c,d=ideal
                target=[s[0]*c-s[1]*d,s[0]*d+s[1]*c]
                upper=sum((abs(x-y) for x,y in zip(values,target)),F(0))+sum(map(abs,s),F(0))*unc
                b=F(*p['error_L1_to_original_source_times_ideal_unit_bound'])
                assert upper<=b, 'independent ORIGINAL high-order product bound'
                bounds.append(b);products.append(p)
            assert F(*row['product_error_L1_to_ORIGINAL_bound'])==max(bounds)
        for key in ('amplitude_budget_accepted','field_values_computed','field_sum_computed','detector_evaluated','native_kernel_implemented','GPU_executed','GPU_job_admission','execution_authenticated','reflection_coefficient_applied','accepted_full_field_pipeline'):
            assert case[key] is False
    assert (rows,evaluated,stops)==(19,5,14)
    assert len(data['controls'])==6 and len(data['expected_rejections'])==11
    for p in data['controls']:
        check_product(p)
    products += data['controls']
    assert len(products)==26 and Counter(map(digest,products))==Counter(map(digest,data['calls']))
    assert all(v['type'] in ('ValueError','TypeError') for v in data['expected_rejections'])
    print(json.dumps({'PASS':True,'pins_verified':len(allpins),'inherited_pins':len(inherited),'tests':7,'cases':17,'source_rows':rows,'sources_evaluated':evaluated,'previous_STOP_preserved':stops,'scene_products':20,'primitive_products':6,'expected_primitive_rejections':11,'RN64_nodes_verified':208,'ORIGINAL_trig_products_verified':20,'GPU_executed':False,'amplitude_budget_accepted':False,'elapsed_seconds':time.perf_counter()-start},sort_keys=True))
if __name__=='__main__':
    main()
