"""Independent stdlib verifier: analytical intervals/ORIGINAL composition, not execution."""
import base64,hashlib,json,math,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT='coordinacion/respuestas/AXIAL-NONZERO-UNIT-DOMAIN-HOST-001-CODEX.json'
MODEL='axial-nonzero-domain-Horner26-ORIGINAL-bound-HOST-v1'
FLAG='restricted_nonzero_unit_error_to_ORIGINAL_bound_proved'
def sha(x):return hashlib.sha256(x).hexdigest()
def digest(x):return sha(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def read(p,h):
    raw=(ROOT/p).read_bytes();assert sha(raw)==h,p;return json.loads(raw)
def payload(r):
    t=r['test_run'];assert t['rc']==0
    raw=zlib.decompress(base64.b64decode(t.get('stdout_zlib_base64') or ''.join(t['stdout_zlib_base64_chunks']),validate=True))
    assert len(raw)==t['stdout_bytes'] and sha(raw)==t['stdout_sha256'];return json.loads(raw)
def pins_from(r):
    if 'code_doc_sha256' in r:return dict(r['code_doc_sha256'])
    v=r['inherited_pin_source'];p=pins_from(read(v['path'],v['sha256']))
    p[v['path']]=v['sha256'];p.update(r['own_code_doc_sha256']);return p
def pair(x):return [x.numerator,x.denominator]
def rat(x):
    assert type(x) is list and len(x)==2 and all(type(v) is int for v in x)
    assert x[1]>0 and math.gcd(*x)==1;return F(*x)
def bits(w):
    assert type(w) is int and 0<=w<2**64
    sign=-1 if w>>63 else 1;e=(w>>52)&2047;m=w%2**52
    assert e<2047 and (e or m==0)
    return sign*F((2**52+m) if e else 0)*F(2)**(e-1075)
def compact(x):
    if type(x) is dict:
        return {('node_intervals_sha256' if k=='node_intervals' else k):(digest(v) if k=='node_intervals' else compact(v)) for k,v in x.items()}
    if type(x) is list:
        if len(x)==2 and all(type(v) is int for v in x) and max(abs(v).bit_length() for v in x)>256:
            return {'exact_rational_sha256':digest(x),'numerator_bits':abs(x[0]).bit_length(),'denominator_bits':x[1].bit_length()}
        return [compact(v) for v in x]
    return x

def reconstruct(t,profile):
    lower,upper=map(rat,t['declared_angle_interval'])
    assert -1<=lower<=upper<=1 and (lower>0 or upper<0)
    x=max(abs(lower),abs(upper));near=min(abs(lower),abs(upper));nodes=[]
    def E(m):
        assert 0<=m<=bits(0x7fefffffffffffff)
        return m*F(1,2**53)+F(1,2**1075) if m else F(0)
    ez=E(x*x);z=[max(F(0),near*near-ez),x*x+ez]
    nodes.append({'label':'square','op':'correlated_square','input_intervals':[t['declared_angle_interval']],
        'exact_interval':[pair(near*near),pair(x*x)],'rounding_charge_abs':pair(ez),'output_interval':list(map(pair,z))})
    def op(a,b,name,label):
        if name=='mul':values=[a[0]*b[0],a[0]*b[1],a[1]*b[0],a[1]*b[1]]
        else:values=[a[0]+b[0],a[1]+b[1]]
        l,h=min(values),max(values);err=E(max(abs(l),abs(h)));out=[l-err,h+err]
        nodes.append({'label':label,'op':name,'input_intervals':[list(map(pair,a)),list(map(pair,b))],
            'exact_interval':[pair(l),pair(h)],'rounding_charge_abs':pair(err),'output_interval':list(map(pair,out))})
        return out,err
    parts={}
    for name,odd in [('cos',0),('sin',1)]:
        assert len(profile[name])==7
        ideal=[F((-1)**i,math.factorial(2*i+odd)) for i in range(7)]
        stored=[bits(c['uint64']) for c in profile[name]]
        for c,y,v in zip(profile[name],stored,ideal):
            assert rat(c['exact_rational'])==v and rat(c['error_rational'])==abs(y-v)
        h=[stored[-1],stored[-1]];I=abs(ideal[-1])
        errors={'coefficients':abs(stored[-1]-ideal[-1]),'square':F(0),'RN_nodes':F(0)}
        for j in reversed(range(6)):
            prod,em=op(h,z,'mul',name+'.mul'+str(j))
            h,ea=op(prod,[stored[j],stored[j]],'add',name+'.add'+str(j))
            errors={k:max(map(abs,z))*v for k,v in errors.items()}
            errors['coefficients']+=abs(stored[j]-ideal[j])
            errors['square']+=I*ez;errors['RN_nodes']+=em+ea
            I=I*x*x+abs(ideal[j])
        if odd:
            h,ef=op(h,[lower,upper],'mul','sin.final')
            errors={k:x*v for k,v in errors.items()};errors['RN_nodes']+=ef;I*=x
        parts[name]={'output_interval':list(map(pair,h)),
            'error_charges':{k:pair(v) for k,v in errors.items()},
            'polynomial_error_uniform_bound':pair(sum(errors.values())),
            'Taylor_uniform_remainder':pair(x**(14+odd)/math.factorial(14+odd)),
            'ideal_polynomial_abs_upper':pair(I)}
    B=sum(rat(v['polynomial_error_uniform_bound'])+rat(v['Taylor_uniform_remainder']) for v in parts.values())
    assert 0<B<F(1,2) and len(nodes)==26
    assert t['terms']==compact(parts) and t['node_intervals_sha256']==digest(nodes)
    assert t['unit_L1_error_to_ideal_at_represented_angle_uniform_bound']==compact(pair(B))
    assert t['additional_phase_uniform_bound_rad']==compact(pair(B/(1-B)))
    assert t['coefficient_profile_sha256']==digest(profile)
    normal=[]
    for node in nodes:
        l,h=map(rat,node['output_interval'])
        assert l<=h and (F(1,2**1022)<=l<=h<=bits(0x7fefffffffffffff)
                        or -bits(0x7fefffffffffffff)<=l<=h<=-F(1,2**1022))
        normal.append(node['label'])
    return B,nodes,normal

r=json.loads((ROOT/REPORT).read_bytes());assert r['task_id']=='AXIAL-NONZERO-UNIT-DOMAIN-HOST-001'
pins=pins_from(r)
for p,h in pins.items():assert sha((ROOT/p).read_bytes())==h,p
assert len(pins)==302 and len(r['own_code_doc_sha256'])==4
prior=read(r['inherited_pin_source']['path'],r['inherited_pin_source']['sha256'])
assert prior['task_id']=='AXIAL-HOST-READOUT-CONTRACT-001'
false=tuple(prior['proof_scope'])
def allfalse(v):
    for k in false:assert v[k] is False,k
allfalse(r['proof_scope'])
raw=payload(r);assert raw['PASS'] is True and raw['tests']==4
t=r['test_run'];assert t['threads']==1 and t['affinity_mask']==1 and t['hard_child_timeout_seconds']==60 and t['elapsed_seconds']<60 and not t['timed_out']
a=raw['data']['audit'];allfalse(a);assert a['model']==MODEL
def audit(path):return payload(read(path,pins[path]))['data']['audit']
domain=audit('coordinacion/respuestas/AXIAL-SCENE-PARAMETER-DOMAIN-HOST-001-CODEX.json')
rect=audit('coordinacion/respuestas/AXIAL-ARGUMENT-RECTANGLE-HOST-001-CODEX.json')
uniform=audit('coordinacion/respuestas/AXIAL-UNIFORM-UNIT-HOST-001-CODEX.json')
packets=payload(read('coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json',pins['coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json']))['packets']
presence='coordinacion/respuestas/AXIAL-NATIVE-PRESENCE-STOPS-001-CODEX.json'
packets.update({n:v['parent'] for n,v in payload(read(presence,pins[presence]))['synthetic_controls'].items()})
assert a['case_order']==domain['case_order'] and len(a['cases'])==17
proved=stopped=zeros=nodes_checked=0;values={}
for n in a['case_order']:
    c=a['cases'][n];ctx=c['context'];allfalse(c)
    assert ctx==domain['cases'][n]['context']==rect['cases'][n]['context']==uniform['cases'][n]['context']
    packet=packets[n];assert digest(packet)==ctx['input_packet_sha256']
    bufs={k:base64.b64decode(v,validate=True) for k,v in packet['buffers_base64'].items()}
    for k,v in bufs.items():assert packet['manifest']['buffers'][k]=={'bytes':len(v),'sha256':sha(v)}
    meta=json.loads(bufs['input_metadata_json'])
    assert ctx['assignments']==meta['explicit_group_contract']['assignments']
    assert ctx['original_snapshot_sha256']==sha(bufs['original_scene_json'])
    ds=domain['cases'][n]['sources'];rs=rect['cases'][n]['sources'];us=uniform['cases'][n]['sources']
    assert [s['source_id'] for s in c['sources']]==[s['source_id'] for s in ds]==ctx['source_order']
    for s,d,rr,u in zip(c['sources'],ds,rs,us):
        allfalse(s);assert s['status']=='STOP' and s['retained_domain_row_sha256']==digest(d)
        if not d['restricted_coordinate_box_to_parameter_rectangle_proved']:
            stopped+=1;assert not s[FLAG] and 'proof' not in s and s['reason']==d['reason'];continue
        if rr['argument_image']['argument_interval']==[[0,1],[0,1]]:
            zeros+=1;assert not s[FLAG] and 'proof' not in s and s['reason_provenance']=='outside_nonzero_scope';continue
        proved+=1;p=s['proof'];allfalse(p);assert s[FLAG] is p[FLAG] is True
        assert p['model']==MODEL and p['source_id']==d['source_id']
        assert p['retained_domain_row_sha256']==digest(d)
        assert p['retained_rectangle_row_sha256']==d['retained_argument_rectangle_source_sha256']==digest(rr)
        assert p['retained_uniform_unit_row_sha256']==rr['retained_uniform_unit_source_sha256']==digest(u)
        assign=next(v for v in ctx['assignments'] if v['source_id']==s['source_id'])
        assert p['ORIGINAL_assignment_sha256']==digest(assign)
        assert u['phase_reference_id']==assign['source_phase_reference_id'] and u['terminal_reference_id']==assign['terminal_reference_id']
        sel=d['restricted_domain_proof']['uniform_affine_selector_proof'];branch=rr['parameter_branch'];im=rr['argument_image']
        assert d['restricted_domain_proof']['ORIGINAL_inside_coordinate_box'] is True
        assert sel['mirror_first_uniform_clearance'] is True and sel['strict_positive_first_and_reflected_second'] is True
        assert sel['effective_reference_length_interval']==branch['length_interval'] and sel['wavelength_interval']==branch['wavelength_interval']
        assert branch['quarter_turn_endpoint_integers']==[branch['ORIGINAL_quarter_turn']]*2 and branch['quarter_branch_over_rectangle_proved'] is True
        assert im['argument_image_over_declared_rectangle_enclosed'] is True and im['old_argument_RN_graph_defined_over_declared_rectangle'] is True
        lo,hi=map(rat,u['interval_theorem']['declared_angle_interval']);al,ah=map(rat,im['argument_interval'])
        assert lo<=al<=ah<=hi and (al>0 or ah<0) and p['represented_argument_interval']==im['argument_interval']
        B,nodes,normal=reconstruct(u['interval_theorem'],uniform['coefficient_profile']);nodes_checked+=len(nodes)
        up=rat(branch['uniform_upstream_phase_to_fixed_ORIGINAL_rad']);arg=rat(im['uniform_argument_error_bound_rad'])
        delta=rat(im['uniform_composed_parameter_phase_to_fixed_ORIGINAL_rad']);assert up>=0 and arg>=0 and delta==up+arg
        assert p['parameter_phase_bound_rad']==pair(up) and p['argument_phase_bound_rad']==pair(arg)
        assert p['composed_parameter_argument_phase_bound_rad']==pair(delta)
        l1=B+2*delta;phase=B/(1-B)+delta;cap=meta['original_path_phase_caps'][s['source_id']]
        assert F(*map(int,p['polynomial_unit_L1_bound_decimal']))==B
        assert F(*map(int,p['uniform_unit_L1_to_fixed_ORIGINAL_bound_decimal']))==l1
        assert F(*map(int,p['uniform_phase_to_fixed_ORIGINAL_bound_decimal']))==phase
        assert cap==p['unchanged_original_phase_cap_rad']==d['unchanged_original_phase_cap_rad']==rr['unchanged_original_phase_cap_rad']==u['unchanged_original_phase_cap_rad']==[1,10**12]
        assert phase<=rat(cap) and p['phase_charge_fits_unchanged_cap'] is True
        assert p['normal_node_labels']==normal and p['restricted_Horner26_nodes_normal_proved'] is True
        assert p['retained_analytic_trace_sha256']==digest(nodes) and p['coefficient_profile_sha256']==digest(uniform['coefficient_profile'])
        assert p['arithmetic_hypothesis']==u['interval_theorem']['arithmetic_hypothesis']
        assert u['interval_theorem']['inherited_runner_accepts_entire_interval'] is False
        assert p['status']=='STOP' and p['new_RN_or_scene_producer_executions']==0
        values[n]={'unit_L1_bound_approx':float(l1),'phase_bound_rad_approx':float(phase)}
assert (proved,stopped,zeros,nodes_checked)==(2,14,3,52)
assert set(values)=={'nonexact_geometry_phase_PASS','thin_resolved'}
assert a['inherited_pins_verified']==298 and a['new_RN_or_scene_producer_executions']==0
assert (a['restricted_nonzero_source_unit_bounds_proved'],a['retained_unit_STOPs'],a['zero_domains_outside_scope'])==(2,14,3)
rejections=raw['data']['rejections'];assert len(rejections)==len({v['label'] for v in rejections})==37
assert all(type(v['reason']) is str and v['reason'] for v in rejections)
print(json.dumps({'PASS':True,'pins':len(pins),'restricted_nonzero_unit_bounds':2,'normal_analytical_nodes':52,
 'retained_unit_STOPs':14,'zero_domains_not_recomputed':3,'rejections':37,'approximate_summary_only':values,
 'new_RN_or_scene_producer_executions':0,'native_or_fullpipeline_admission':False},sort_keys=True))
