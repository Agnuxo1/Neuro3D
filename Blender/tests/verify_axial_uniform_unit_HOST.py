"""Independent rational interval oracle: no production imports or old point RN execution."""
import base64,hashlib,json,math,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT='coordinacion/respuestas/AXIAL-UNIFORM-UNIT-HOST-001-CODEX.json'
AMODEL='axial-static-amplitude-L1-allocation-HOST-v1'
UNITS='ORIGINAL-source-field-amplitude-L1'
MODEL='axial-uniform-Horner26-declared-angle-HOST-v1'
FALSE=('scene_argument_enclosed','uniform_unit_error_to_ORIGINAL_proved','uniform_source_error_proved',
       'accepted_full_field_pipeline','remaining_stages_error_proved','execution_authenticated',
       'coherence_authenticated','native_kernel_implemented','GPU_executed','GPU_job_admission')
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


def compact(v):
    if type(v) is dict:
        return {('node_intervals_sha256' if k=='node_intervals' else k):
                (digest(x) if k=='node_intervals' else compact(x)) for k,x in v.items()}
    if type(v) is list:
        if len(v)==2 and all(type(x) is int for x in v) and max(abs(x).bit_length() for x in v)>256:
            return {'exact_rational_sha256':digest(v),'numerator_bits':abs(v[0]).bit_length(),
                    'denominator_bits':v[1].bit_length()}
        return [compact(x) for x in v]
    return v
def charge(v):
    assert 0<=v<=decode(0x7fefffffffffffff)
    return v/F(2**53)+F(1,2**1075) if v else F(0)
def reconstruct(t,profile):
    lo,hi=map(lambda v:F(*v),t['declared_angle_interval'])
    assert -1<=lo<=hi<=1
    X=max(abs(lo),abs(hi));m=F(0) if lo<=0<=hi else min(abs(lo),abs(hi))
    ez=charge(X**2);z=[max(F(0),m*m-ez),X**2+ez];Z=max(map(abs,z));trace=[]
    trace.append({'label':'square','op':'correlated_square','input_intervals':[[pair(lo),pair(hi)]],
                  'exact_interval':[pair(m*m),pair(X**2)],'rounding_charge_abs':pair(ez),
                  'output_interval':list(map(pair,z))})
    def node(a,b,op,label):
        if op=='mul':
            possibilities=[a[0]*b[0],a[0]*b[1],a[1]*b[0],a[1]*b[1]]
            lower=min(possibilities);upper=max(possibilities)
        else:lower=a[0]+b[0];upper=a[1]+b[1]
        error=charge(max(abs(lower),abs(upper)))
        result=[lower-error,upper+error]
        trace.append({'label':label,'op':op,'input_intervals':[[pair(v) for v in a],[pair(v) for v in b]],
                      'exact_interval':[pair(lower),pair(upper)],'rounding_charge_abs':pair(error),
                      'output_interval':list(map(pair,result))})
        return result,error
    terms={}
    for name,odd in [('cos',0),('sin',1)]:
        exact=[F((-1)**j,math.factorial(2*j+odd)) for j in range(7)]
        encoded=[decode(q['uint64']) for q in profile[name]]
        h=[encoded[6],encoded[6]];I=abs(exact[6]);ec=abs(encoded[6]-exact[6]);es=er=F(0)
        for j in range(5,-1,-1):
            p,em=node(h,z,'mul',name+'.mul'+str(j))
            h,ea=node(p,[encoded[j],encoded[j]],'add',name+'.add'+str(j))
            ec=Z*ec+abs(encoded[j]-exact[j])
            es=Z*es+I*ez;er=Z*er+em+ea;I=I*X**2+abs(exact[j])
        if odd:
            h,ef=node(h,[lo,hi],'mul','sin.final');ec*=X;es*=X;er=er*X+ef;I*=X
        terms[name]={'output_interval':list(map(pair,h)),
                     'error_charges':{'coefficients':pair(ec),'square':pair(es),'RN_nodes':pair(er)},
                     'polynomial_error_uniform_bound':pair(ec+es+er),
                     'Taylor_uniform_remainder':pair(X**(14+odd)/math.factorial(14+odd)),
                     'ideal_polynomial_abs_upper':pair(I)}
    total=sum(F(*a['polynomial_error_uniform_bound'])+F(*a['Taylor_uniform_remainder']) for a in terms.values())
    phase=total/(1-total) if total<F(1,2) else None
    assert t['model']==MODEL and t['coefficient_profile_sha256']==digest(profile)
    assert t['x_abs_upper']==compact(pair(X)) and t['square_RN_uniform_error']==compact(pair(ez))
    assert t['terms']==compact(terms) and t['node_intervals_sha256']==digest(trace)
    assert t['unit_L1_error_to_ideal_at_represented_angle_uniform_bound']==compact(pair(total))
    assert t['additional_phase_uniform_bound_rad']==compact(pair(phase)) if phase is not None else t['additional_phase_uniform_bound_rad'] is None
    assert t['bounded_RN_nodes']==26 and t['uniform_theorem_for_declared_angle_interval_proved'] is True
    assert t['inherited_runner_accepts_entire_interval'] is False
    for k in FALSE:assert t[k] is False
    return trace,terms,phase

r=json.loads((ROOT/REPORT).read_bytes());assert r['task_id']=='AXIAL-UNIFORM-UNIT-HOST-001'
pins=pins_from(r);assert len(pins)==257
for p,h in pins.items():assert sha((ROOT/p).read_bytes())==h,p
d=payload(r);assert d['PASS'] is True and d['tests']==6;d=d['data'];a=d['audit']
unit='coordinacion/respuestas/AXIAL-QUARTER-UNIT-HOST-001-CODEX.json'
old=payload(read(unit,pins[unit]))['cases']
ingress='coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json'
presence='coordinacion/respuestas/AXIAL-NATIVE-PRESENCE-STOPS-001-CODEX.json'
packets=payload(read(ingress,pins[ingress]))['packets']
controls=payload(read(presence,pins[presence]))['synthetic_controls']
packets.update({n:v['parent'] for n,v in controls.items()})
profile=old['positive']['sources'][0]['encoded_corner_units_HOST'][0]['rotation_RN64']['coefficients']
assert a['coefficient_profile']==profile
for name,odd in [('cos',0),('sin',1)]:
    assert len(profile[name])==7
    for j,c in enumerate(profile[name]):
        exact=F((-1)**j,math.factorial(2*j+odd))
        assert c['exact_rational']==pair(exact) and c['error_rational']==pair(abs(decode(c['uint64'])-exact))
assert a['inherited_pins_verified']==253 and set(a['cases'])==set(packets)==set(old)
assert len(a['case_order'])==17 and len(set(a['case_order']))==17 and set(a['case_order'])==set(old)
assert a['new_RN_casts_or_polynomial_evaluations']==a['new_scene_numeric_operations']==0
for k in FALSE:assert a[k] is False
count=stops=pointchecks=unfit=0;metadata=[]
for n,c in a['cases'].items():
    ctx=context(packets[n]);oc=old[n];assert ctx==c['context']
    for k in ('case_name','input_packet_sha256','scene_binding_sha256','word_ABI_sha256','source_order'):
        assert oc[k]==ctx[k]
    assert len(c['sources'])==len(ctx['source_order'])
    for k in FALSE:assert c[k] is False
    for s,o,assignment in zip(c['sources'],oc['sources'],ctx['assignments']):
        assert s['source_id']==o['source_id']==assignment['source_id']
        assert s['phase_reference_id']==o['phase_reference_id']==assignment['source_phase_reference_id']
        assert s['terminal_reference_id']==o['terminal_reference_id']==assignment['terminal_reference_id']
        assert s['retained_unit_source_sha256']==digest(o)
        assert s['retained_partial_unit_phase_pass']==s['theorem_computed']==o['accepted_unit_phase_bound_CPU_only']
        assert s['status']=='STOP'
        for k in FALSE:assert s[k] is False
        if not s['theorem_computed']:
            stops+=1;assert s['reason']==o['reason'];assert 'interval_theorem' not in s
            continue
        count+=1;corners=o['encoded_corner_units_HOST'];assert len(corners)==4
        xs=[decode(v['quarter_argument']['HOST_argument_uint64']) for v in corners]
        t=s['interval_theorem'];assert t['declared_angle_interval']==[pair(min(xs)),pair(max(xs))]
        trace,terms,phase=reconstruct(t,profile)
        cap=o['unchanged_original_phase_cap_rad'];assert s['unchanged_original_phase_cap_rad']==cap
        fits=phase<=F(*cap) if phase is not None else False
        assert s['polynomial_charge_alone_fits_unchanged_phase_cap']==fits;unfit+=not fits
        assert s['inherited_quarter_bound_NOT_uniform']==o['inherited_quarter_phase_bound_rad']
        assert s['composed_ORIGINAL_uniform_error'] is None
        metadata.append({'case':n,'source':s['source_id'],'polynomial_charge_alone_fits':fits})
        assert s['retained_angle_corner_sha256']==[digest(v) for v in corners]
        for i,corner in enumerate(corners):
            rot=corner['rotation_RN64'];assert rot['coefficients']==profile and len(rot['operations'])==26
            for op,ob in zip(rot['operations'],trace):
                assert op['label']==ob['label']
                assert abs(F(*op['rounding_delta_rational']))<=F(*ob['rounding_charge_abs'])
                low,high=map(lambda v:F(*v),ob['output_interval']);y=decode(op['output_uint64'])
                assert low<=y<=high;pointchecks+=1
            for name,v in rot['terms'].items():
                assert F(*v['actual_polynomial_error_rational'])<=F(*terms[name]['polynomial_error_uniform_bound'])
            assert {'case':n,'source_id':s['source_id'],'corner_index':i,'corner_sha256':digest(corner),
                    'nodes_checked':26,'old_RN_reexecuted':0} in d['retained_point_checks']
assert count==5 and stops==14 and pointchecks==520 and len(d['retained_point_checks'])==20
assert a['uniform_intervals_computed']==count and a['retained_unit_STOPs']==stops
assert len(d['primitives'])==6
for t in d['primitives']:reconstruct(t,profile)
assert len(d['rejections'])==19 and len({v['label'] for v in d['rejections']})==19
assert len(r['failures_preserved'])>=1 and r['failures_preserved'][0]['rc']==1
assert r['proof_scope']['full_scene_enclosure'] is False
print(json.dumps({'PASS':True,'pins':len(pins),'uniform_source_intervals':count,'retained_unit_STOPs':stops,
                  'retained_node_containment_checks':pointchecks,'old_RN_reexecuted':0,
                  'new_point_RN':0,'analytical_interval_nodes':26*(count+6),
                  'phase_charge_not_fitting_unchanged_caps':unfit,'phase_budget_details':metadata,
                  'full_scene_enclosure':False},sort_keys=True))
