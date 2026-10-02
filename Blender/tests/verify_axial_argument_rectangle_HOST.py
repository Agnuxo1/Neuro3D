"""Independent receipt/rational oracle for declared parameter rectangles; no producer imports."""
import base64,hashlib,json,math,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT='coordinacion/respuestas/AXIAL-ARGUMENT-RECTANGLE-HOST-001-CODEX.json'
MODEL='axial-parameter-rectangle-quarter-RN-monotone-HOST-v1'
FALSE=('scene_argument_enclosed','uniform_unit_error_to_ORIGINAL_proved','uniform_source_error_proved',
       'accepted_full_field_pipeline','remaining_stages_error_proved','execution_authenticated',
       'coherence_authenticated','native_kernel_implemented','GPU_executed','GPU_job_admission',
       'whole_scene_parameter_enclosure_proved','native_argument_implemented')
SIGN=1<<63
def canon(v):
    return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def sha(v):
    return hashlib.sha256(v).hexdigest()
def digest(v):
    return sha(canon(v))
def read(p,h):
    raw=(ROOT/p).read_bytes();assert sha(raw)==h,p;return json.loads(raw)
def payload(r):
    t=r['test_run'];assert t['rc']==0
    raw=zlib.decompress(base64.b64decode(t.get('stdout_zlib_base64') or ''.join(t['stdout_zlib_base64_chunks']),validate=True))
    assert len(raw)==t['stdout_bytes'] and sha(raw)==t['stdout_sha256']
    return json.loads(raw)
def pins_from(r):
    if 'code_doc_sha256' in r:return dict(r['code_doc_sha256'])
    d=r['inherited_pin_source'];p=pins_from(read(d['path'],d['sha256']))
    p[d['path']]=d['sha256'];p.update(r['own_code_doc_sha256']);return p
def pair(v):
    return [v.numerator,v.denominator]
def rational(v):
    assert type(v) is list and len(v)==2 and all(type(n) is int for n in v)
    assert v[1]>0 and math.gcd(*v)==1
    return F(*v)
def signed(words):
    assert type(words) is list and len(words)==16
    assert all(type(w) is int and 0<=w<2**32 for w in words)
    n=sum(w<<(32*i) for i,w in enumerate(words))
    return n-2**512 if words[-1]>>31 else n
def decode(w):
    assert type(w) is int and 0<=w<2**64
    e=(w>>52)&2047;assert e<2047
    n=w&((1<<52)-1)
    if e:n+=1<<52
    return (-1 if w>>63 else 1)*F(n)*F(2)**(e-1075 if e else -1074)
def charge(x):
    assert 0<=x<=decode(0x7fefffffffffffff)
    return x/F(2**53)+F(1,2**1075) if x else F(0)
def context(packet):
    roles={'triangles','sources','wavelength','reference','original_scene_json','input_metadata_json'}
    assert set(packet['buffers_base64'])==set(packet['manifest']['buffers'])==roles
    b={k:base64.b64decode(v,validate=True) for k,v in packet['buffers_base64'].items()}
    for k,v in b.items():assert packet['manifest']['buffers'][k]=={'bytes':len(v),'sha256':sha(v)}
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
        if key not in groups:groups.append(key)
    return {'model':'axial-static-amplitude-L1-allocation-HOST-v1','units':'ORIGINAL-source-field-amplitude-L1',
            'case_name':m['case_name'],'input_packet_sha256':digest(packet),
            'scene_binding_sha256':m['scene_binding_sha256'],'word_ABI_sha256':m['word_ABI_sha256'],
            'original_snapshot_sha256':m['original_snapshot_sha256'],'original_group_contract_sha256':digest(g),
            'source_order':m['source_order'],'assignments':g['assignments'],'groups':groups,
            'unchanged_field_L1_cap':pair(rational(g['limits']['field_L1'])),'unchanged_limits':g['limits'],
            'grouping_provenance':g['grouping_provenance'],'execution_authenticated':False,'coherence_authenticated':False}
def false_flags(v):
    for k in FALSE:assert v[k] is False,k
def branch(b):
    assert b['model']==MODEL and b['parameter_rectangle_only'] is True;false_flags(b)
    ll,lh=map(rational,b['length_interval']);wl,wh=map(rational,b['wavelength_interval'])
    L=rational(b['ORIGINAL_length']);W=rational(b['ORIGINAL_wavelength'])
    assert ll<=lh and 0<wl<=wh and W>0
    corners=[l/w for l in (ll,lh) for w in (wl,wh)]
    lo,hi=min(corners),max(corners);q=L/W
    assert b['quotient_corner_rationals']==list(map(pair,corners))
    assert b['quotient_interval']==list(map(pair,(lo,hi))) and b['ORIGINAL_quotient']==pair(q)
    centered=[(v+F(1,2)).numerator//(v+F(1,2)).denominator for v in (lo,hi,q)]
    assert b['centered_turn_endpoint_integers']==centered[:2] and b['ORIGINAL_centered_turn']==centered[2]
    if len(set(centered))!=1:
        assert b['status']=='STOP' and b['centered_branch_over_rectangle_proved'] is False
        assert b['quarter_branch_over_rectangle_proved'] is False and 'quarter_residual_interval' not in b
        return
    j=centered[0];r=[v-j for v in (lo,hi,q)]
    assert -F(1,2)<=r[0]<=r[1]<F(1,2)
    assert b['centered_branch_over_rectangle_proved'] is True
    assert b['centered_residual_interval']==list(map(pair,r[:2]))
    quarter=[(4*v+F(1,2)).numerator//(4*v+F(1,2)).denominator for v in r]
    assert b['quarter_turn_endpoint_integers']==quarter[:2] and b['ORIGINAL_quarter_turn']==quarter[2]
    if len(set(quarter))!=1:
        assert b['status']=='STOP' and b['quarter_branch_over_rectangle_proved'] is False
        assert 'quarter_residual_interval' not in b
        return
    t=[v-F(quarter[0],4) for v in r]
    assert -F(1,8)<=t[0]<=t[1]<F(1,8)
    assert b['quarter_residual_interval']==list(map(pair,t[:2]))
    assert b['ORIGINAL_quarter_residual']==pair(t[2])
    assert b['uniform_upstream_phase_to_fixed_ORIGINAL_rad']==pair(8*max(abs(lo-q),abs(hi-q)))
    assert b['quarter_branch_over_rectangle_proved'] is True and b['status']=='PROVED_PARAMETER_BRANCH_ONLY'
def cell(c,exact,w):
    assert c['output_uint64']==w and c['exact_input']==pair(exact)
    value=decode(w);assert abs(value)<decode(0x7fefffffffffffff)
    if value==0:
        assert w==0 and exact>=0 or w==SIGN and exact<0
        neighbors=(-F(1,2**1074),F(1,2**1074))
    else:
        step=1 if value>0 else -1
        neighbors=(decode(w-step),decode(w+step))
    bounds=[(v+value)/2 for v in neighbors];even=w%2==0
    assert c['cell_interval']==list(map(pair,bounds)) and c['ties_to_even_output']==even
    assert bounds[0]<exact<bounds[1] or even and exact in bounds
    assert c['rounding_cell_membership_proved'] is True and c['new_RN_executed']==0
def image(b,v,corners):
    branch(b);assert b['quarter_branch_over_rectangle_proved'] is True
    assert len(corners)==len(v['retained_endpoint_cell_certificates'])==4
    assert len({x['TWO_PI_uint64'] for x in corners})==1
    assert len({tuple(x['TWO_PI_error_bound_rad']) for x in corners})==1
    p=decode(corners[0]['TWO_PI_uint64']);bp=rational(corners[0]['TWO_PI_error_bound_rad']);assert p>0 and bp>=0
    assert v['TWO_PI_uint64']==corners[0]['TWO_PI_uint64'] and v['TWO_PI_error_bound_rad']==pair(bp)
    j=b['ORIGINAL_centered_turn'];k=b['ORIGINAL_quarter_turn']
    qs=list(map(rational,b['quotient_corner_rationals']));xs=[];ys=[]
    for q,c,cert in zip(qs,corners,v['retained_endpoint_cell_certificates']):
        r=q-j;t=r-F(k,4)
        assert c['original_residual_cycles_rational']==pair(r) and c['quarter_turns_HOST']==k
        assert c['quarter_residual_HOST_rational']==pair(t)
        assert F(signed(c['numerator_words']),signed(c['denominator_words']))==r
        x=decode(c['HOST_cast_uint64']);y=decode(c['HOST_argument_uint64'])
        assert c['HOST_cast_rational']==pair(x) and c['HOST_argument_rational']==pair(y)
        cell(cert['cast'],t,c['HOST_cast_uint64']);cell(cert['multiply'],p*x,c['HOST_argument_uint64'])
        xs.append(x);ys.append(y)
    indices=[qs.index(min(qs)),qs.index(max(qs))]
    assert v['retained_extrema_corner_indices']==indices
    assert [xs[i] for i in indices]==[min(xs),max(xs)] and [ys[i] for i in indices]==[min(ys),max(ys)]
    assert v['cast_interval']==list(map(pair,(min(xs),max(xs))))
    assert v['argument_interval']==list(map(pair,(min(ys),max(ys)))) and -1<=min(ys)<=max(ys)<=1
    normal=F(1,2**1022)
    defined=all(min(z)==max(z)==0 or min(z)>=normal or max(z)<=-normal for z in (xs,ys))
    assert v['old_argument_RN_graph_defined_over_declared_rectangle']==defined
    tmax=max(map(abs,map(rational,b['quarter_residual_interval'])))
    cast=p*charge(tmax);mul=charge(p*max(map(abs,xs)));const=tmax*bp
    assert v['uniform_argument_charges_rad']=={'cast':pair(cast),'multiply':pair(mul),'constant_2pi':pair(const)}
    extra=cast+mul+const
    assert v['uniform_argument_error_bound_rad']==pair(extra)
    assert v['uniform_composed_parameter_phase_to_fixed_ORIGINAL_rad']==pair(rational(b['uniform_upstream_phase_to_fixed_ORIGINAL_rad'])+extra)
    assert v['argument_image_over_declared_rectangle_enclosed'] is True and v['new_RN_casts_or_multiplies']==0
    false_flags(v)

r=json.loads((ROOT/REPORT).read_bytes());assert r['task_id']=='AXIAL-ARGUMENT-RECTANGLE-HOST-001'
pins=pins_from(r);assert len(pins)==262
for p,h in pins.items():assert sha((ROOT/p).read_bytes())==h,p
previous=read(r['inherited_pin_source']['path'],r['inherited_pin_source']['sha256'])
uniform=payload(previous)['data']['audit']
a_path='coordinacion/respuestas/AXIAL-NATIVE-ARGUMENT-HOST-001-CODEX.json'
q_path='coordinacion/respuestas/AXIAL-QUARTER-ARGUMENT-HOST-001-CODEX.json'
u_path='coordinacion/respuestas/AXIAL-QUARTER-UNIT-HOST-001-CODEX.json'
argument=payload(read(a_path,pins[a_path]))['cases']
quarter=payload(read(q_path,pins[q_path]))['cases']
units=payload(read(u_path,pins[u_path]))['cases']
ingress='coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json'
presence='coordinacion/respuestas/AXIAL-NATIVE-PRESENCE-STOPS-001-CODEX.json'
packets=payload(read(ingress,pins[ingress]))['packets']
packets.update({n:v['parent'] for n,v in payload(read(presence,pins[presence]))['synthetic_controls'].items()})
d=payload(r);assert d['PASS'] is True and d['tests']==6;d=d['data'];a=d['audit']
assert a['model']==MODEL and set(a['cases'])==set(packets)==set(uniform['cases'])
assert len(a['case_order'])==17 and len(set(a['case_order']))==17 and set(a['case_order'])==set(packets)
assert a['inherited_pins_verified']==258 and a['previous_producers_reexecuted'] is False
assert a['new_RN_casts_or_multiplies']==0;false_flags(a)
count=stops=checks=nonfit=0;details=[]
for n,c in a['cases'].items():
    ctx=context(packets[n]);assert ctx==c['context']==uniform['cases'][n]['context'];false_flags(c)
    aa=argument[n];qq=quarter[n];uu=units[n]
    for prior in (aa,qq,uu,aa['upstream'],aa['upstream']['upstream']):
        for key in ('case_name','input_packet_sha256','scene_binding_sha256','word_ABI_sha256','source_order'):
            assert prior[key]==ctx[key]
        assert len(prior['sources'])==len(ctx['source_order'])
        assert [s['source_id'] for s in prior['sources']]==ctx['source_order']
    assert len(c['sources'])==len(ctx['source_order'])
    for i,(s,old,qs,us,assignment) in enumerate(zip(c['sources'],uniform['cases'][n]['sources'],qq['sources'],uu['sources'],ctx['assignments'])):
        assert s['source_id']==old['source_id']==qs['source_id']==us['source_id']==assignment['source_id']
        assert us['phase_reference_id']==qs['phase_reference_id']==assignment['source_phase_reference_id']
        assert us['terminal_reference_id']==qs['terminal_reference_id']==assignment['terminal_reference_id']
        assert s['retained_uniform_unit_source_sha256']==digest(old)
        assert s['retained_partial_unit_phase_pass']==us['accepted_unit_phase_bound_CPU_only']
        assert s['rectangle_evaluated']==us['accepted_unit_phase_bound_CPU_only']
        assert s['retained_unit_polynomial_charge_fits']==old.get('polynomial_charge_alone_fits_unchanged_phase_cap')
        assert s['status']=='STOP';false_flags(s)
        if not s['rectangle_evaluated']:
            stops+=1;assert s['reason']==us['reason']==old['reason']
            assert s['reason_provenance']=='unchanged_retained_unit_STOP'
            assert s['argument_image_over_declared_rectangle_enclosed'] is False
            assert 'argument_image' not in s and 'parameter_branch' not in s
            continue
        count+=1;b=s['parameter_branch'];v=s['argument_image']
        cyc=aa['upstream']['sources'][i];ref=aa['upstream']['upstream']['sources'][i]['reference']
        assert s['retained_reference_sha256']==digest(ref) and s['retained_cycle_source_sha256']==digest(cyc)
        assert s['retained_quarter_source_sha256']==digest(qs) and qs==us['upstream_quarter_proof']
        corners=qs['encoded_corner_quarter_arguments'];assert len(corners)==len(us['encoded_corner_units_HOST'])==4
        assert [x['quarter_argument'] for x in us['encoded_corner_units_HOST']]==corners
        lw=ref['effective_reference_length_interval_words'];ww=ref['wavelength_interval_words']
        assert b['length_interval']==[pair(F(signed(w))) for w in lw]
        assert b['wavelength_interval']==[pair(F(signed(w))) for w in ww]
        assert [(x['length_words'],x['wavelength_words']) for x in cyc['encoded_enclosure_corner_cycles']]==[(l,w) for l in lw for w in ww]
        orig=cyc['original_ideal_cycles']
        assert b['ORIGINAL_length']==pair(F(signed(orig['length_words'])))
        assert b['ORIGINAL_wavelength']==pair(F(signed(orig['wavelength_words'])))
        image(b,v,corners);checks+=8
        ulo,uhi=map(rational,old['interval_theorem']['declared_angle_interval']);vlo,vhi=map(rational,v['argument_interval'])
        assert s['retained_uniform_unit_interval_covers_argument_image']==(ulo<=vlo<=vhi<=uhi) is True
        cap=us['unchanged_original_phase_cap_rad']
        assert cap==qs['unchanged_original_phase_cap_rad']==aa['sources'][i]['unchanged_original_phase_cap_rad']==s['unchanged_original_phase_cap_rad']
        fits=rational(v['uniform_composed_parameter_phase_to_fixed_ORIGINAL_rad'])<=rational(cap)
        assert s['uniform_parameter_phase_alone_fits_unchanged_cap']==fits
        nonfit+=s['retained_unit_polynomial_charge_fits'] is False
        details.append({'case':n,'source':s['source_id'],'parameter_phase_fits_unchanged_cap':fits,
                        'retained_polynomial_charge_fits':s['retained_unit_polynomial_charge_fits']})
        assert s['argument_image_over_declared_rectangle_enclosed'] is True
        assert s['reason_provenance']=='missing_whole_scene_parameter_certificate'
assert count==5 and stops==14 and checks==40 and nonfit==3
assert a['declared_rectangle_images_proved']==count and a['retained_unit_STOPs']==stops
assert len(d['primitives'])==8
for b in d['primitives']:branch(b)
assert d['primitives'][4]['quarter_residual_interval']==[[-1,8],[-1,8]]
assert len(d['RN_cells'])==6
for c in d['RN_cells']:cell(c,rational(c['exact_input']),c['output_uint64'])
assert len(d['rejections'])==23 and len({x['label'] for x in d['rejections']})==23
assert r['proof_scope']['whole_scene_parameter_enclosure_proved'] is False
assert r['test_capture_recovery']['rerun_required'] is False
print(json.dumps({'PASS':True,'pins':len(pins),'declared_rectangle_images':count,'retained_unit_STOPs':stops,
                  'retained_endpoint_cell_checks':checks,'synthetic_branch_controls':8,'synthetic_RN_cell_controls':6,
                  'rejections':23,'new_RN_or_prior_producer_reexecution':0,'whole_scene_parameter_enclosure_proved':False,
                  'budget_details':details},sort_keys=True))
