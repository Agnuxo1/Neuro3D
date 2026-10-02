"""Independent stdlib IEEE/pi/scene-bound argument oracle; no production imports."""
import base64,hashlib,json,math,struct,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT='coordinacion/respuestas/AXIAL-GUARDED-ARGUMENT-UNIT-RN64-CPU-001-CODEX.json'
PREVIOUS='coordinacion/respuestas/AXIAL-GUARDED-RESIDUAL-ARGUMENT-RN64-CPU-001-CODEX.json'
PREVIOUS_SHA='06a224643cc77a1e78f8526b719d5e208624b9aca81c901014f81cdb9f208679'
PIHI=F(314159265358979323846264338327950288419716939937511,10**50)
SIGN=1<<63
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(x):return sha(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def read(p,h):
    b=(ROOT/p).read_bytes();assert sha(b)==h,p;return json.loads(b)
def pins_from(r):
    if 'code_doc_sha256' in r:return dict(r['code_doc_sha256'])
    d=r['inherited_pin_source'];p=pins_from(read(d['path'],d['sha256']))
    p[d['path']]=d['sha256'];p.update(r['own_code_doc_sha256']);return p
def payload(r):
    t=r['test_run'];assert t['rc']==0
    if 'timed_out' in t:assert t['timed_out'] is False
    b=zlib.decompress(base64.b64decode(t.get('stdout_zlib_base64') or ''.join(t['stdout_zlib_base64_chunks']),validate=True))
    assert len(b)==t['stdout_bytes'] and sha(b)==t['stdout_sha256'];return json.loads(b)
def q(x):
    assert type(x) is list and len(x)==2 and all(type(a) is int for a in x)
    assert x[1]>0 and math.gcd(*x)==1;return F(*x)
def pair(x):return [x.numerator,x.denominator]
def word(v):return struct.unpack('<Q',struct.pack('<d',v))[0]
def bits(w,normal=True):
    assert type(w) is int and 0<=w<2**64
    sign=-1 if w&SIGN else 1;exp=(w>>52)&2047;mant=w&((1<<52)-1)
    assert exp!=2047 and (not normal or exp!=0 or mant==0)
    return sign*F(mant if exp==0 else mant+(1<<52))*F(2)**((1 if exp==0 else exp)-1075)
def context(packet):
    bs={k:base64.b64decode(v,validate=True) for k,v in packet['buffers_base64'].items()}
    assert set(bs)=={'triangles','sources','wavelength','reference','original_scene_json','input_metadata_json'}
    for k,b in bs.items():assert packet['manifest']['buffers'][k]=={'bytes':len(b),'sha256':sha(b)}
    m=json.loads(bs['input_metadata_json']);s=json.loads(bs['original_scene_json']);g=m['explicit_group_contract']
    assert m['original_snapshot_sha256']==sha(bs['original_scene_json']);ids=m['source_order'];ass=g['assignments']
    assert ids==[x['id'] for x in s['sources']]==[x['source_id'] for x in ass]
    groups=[]
    for t in ass:
        assert t['source_phase_reference_id']=='original-source-zero:'+m['scene_binding_sha256']+':'+t['source_id']
        key=[t['port'],t['coherence_group']]
        if key not in groups:groups.append(key)
    c={'model':'axial-static-amplitude-L1-allocation-HOST-v1','units':'ORIGINAL-source-field-amplitude-L1','case_name':m['case_name'],
       'input_packet_sha256':digest(packet),'scene_binding_sha256':m['scene_binding_sha256'],'word_ABI_sha256':m['word_ABI_sha256'],
       'original_snapshot_sha256':m['original_snapshot_sha256'],'original_group_contract_sha256':digest(g),
       'source_order':ids,'assignments':ass,'groups':groups,'unchanged_field_L1_cap':pair(q(g['limits']['field_L1'])),
       'unchanged_limits':g['limits'],'grouping_provenance':g['grouping_provenance'],'execution_authenticated':False,'coherence_authenticated':False}
    return c,s
def RN(x,width,zs):
    assert type(width) is int and width in (32,64)
    if x==0:return zs<<(width-1)
    frac,bias,emin,emax=(23,127,-126,127) if width==32 else (52,1023,-1022,1023)
    sign=(1<<(width-1)) if x<0 else 0;n,d=abs(x.numerator),x.denominator
    e=n.bit_length()-d.bit_length()
    if (n<d<<e if e>=0 else n<<-e<d):e-=1
    assert e<=emax
    grid=max(e,emin)-frac;nn,dd=(n,d<<grid) if grid>=0 else (n<<-grid,d)
    m,rem=divmod(nn,dd);m+=int(2*rem>dd or (2*rem==dd and m&1))
    if m==0:return sign
    if e<emin:
        assert m<=2**frac;return sign|m
    if m==2**(frac+1):m>>=1;e+=1
    assert e<=emax and 2**frac<=m<2**(frac+1)
    return sign|((e+bias)<<frac)|(m-2**frac)

def verify_composition(comp,fixed,res,sign):
    dec=res['fixed_ORIGINAL_reference'];c={k:q(v) for k,v in fixed['ORIGINAL_coordinates_BU'].items()};d={k:q(v) for k,v in dec['ORIGINAL_coordinates_BU'].items()}
    assert [h['primitive_id'] for h in fixed['hits']]==[h['primitive_id'] for h in dec['hits']]
    assert [h['owner'] for h in fixed['hits']]==[h['owner'] for h in dec['hits']]==[0,1]
    assert fixed['quarter_index']==dec['quarter_index']
    for t,v in ((fixed,c),(dec,d)):
        assert v['wavelength']>0 and q(t['geometric_length_BU'])==sign*(2*v['M']-v['S']-v['D'])
        assert q(t['reference_correction_BU'])==sign*(v['D']-v['R']) and q(t['effective_reference_length_BU'])==sign*(2*v['M']-v['S']-v['R'])
    e={k:abs(d[k]-c[k]) for k in c};assert comp['coordinate_errors_BU']=={k:pair(v) for k,v in e.items()}
    geom=2*e['M']+e['S']+e['D'];ref=e['D']+e['R'];eff=2*e['M']+e['S']+e['R']
    assert q(comp['geometry_representation_length_bound_BU'])==geom and q(comp['reference_representation_bound_BU'])==ref
    assert q(comp['uncorrelated_geometry_plus_reference_bound_BU'])==geom+ref
    assert q(comp['effective_representation_bound_shared_D_cancelled_BU'])==eff
    rc={k:q(v) for k,v in res['length_rounding_charges_BU'].items()};assert all(v>=0 for v in rc.values())
    R=sum(rc.values(),F(0));assert comp['Xroot_length_rounding_charges_BU']==res['length_rounding_charges_BU']
    assert q(comp['Xroot_length_rounding_bound_BU'])==q(res['length_to_fixed_ORIGINAL_bound_BU'])==R
    assert q(comp['combined_effective_length_bound_BU'])==eff+R
    actual=bits(res['effective_reference_length_uint64']);L0=q(fixed['effective_reference_length_BU']);Ld=q(dec['effective_reference_length_BU'])
    assert abs(Ld-L0)<=eff and abs(actual-Ld)<=R and abs(actual-L0)<=eff+R
    assert q(comp['actual_length_to_FIXED_ORIGINAL_error_BU'])==abs(actual-L0)
    charges={'geometry_representation_cycles':eff/d['wavelength'],'Xroot_length_rounding_cycles':R/d['wavelength'],
        'wavelength_representation_cycles':abs(L0)*e['wavelength']/(d['wavelength']*c['wavelength'])}
    E=sum(charges.values(),F(0));assert comp['cycle_charges_to_fixed_ORIGINAL']=={k:pair(v) for k,v in charges.items()}
    assert q(comp['cycles_to_fixed_ORIGINAL_bound'])==E
    observed=abs(actual/d['wavelength']-L0/c['wavelength']);assert observed<=E and q(comp['observed_host_exact_cycles_error'])==observed
    phases={k.replace('_cycles','_rad'):2*PIHI*v for k,v in charges.items()};P=sum(phases.values(),F(0))
    assert comp['phase_length_wavelength_charges_rad']=={k:pair(v) for k,v in phases.items()} and q(comp['phase_length_wavelength_only_bound_rad'])==P
    assert comp['unchanged_phase_cap_rad']==[1,10**12] and comp['length_wavelength_only_phase_charge_fits_cap']==(P<=F(1,10**12))
    margin=F(1,8)-abs(L0/c['wavelength']-F(fixed['quarter_index'],4))-E
    assert q(comp['quarter_margin_with_combined_error_cycles'])==margin and comp['quarter_point_interval_certified']==(margin>0)
    assert comp['RN64_quotient_argument_not_executed'] is True
    return P,margin

PILO=PIHI-F(1,10**50)
CW=0x401921fb54442d18
C=bits(CW);lo,hi=2*PILO,2*PIHI
assert RN(lo,64,0)==RN(hi,64,0)==CW
EC=max(abs(C-lo),abs(C-hi))
def verify_argument(ad,v):
    assert ad['TWO_PI_uint64']==CW and ad['unchanged_phase_cap_rad']==[1,10**12]
    rw=ad['residual_uint64'];R=bits(rw);R0=q(ad['fixed_ORIGINAL_residual_cycles'])
    assert abs(R)<F(1,8) and abs(R0)<F(1,8)
    uc={n:q(t) for n,t in ad['upstream_cycle_charges'].items()}
    assert set(uc)=={'geometry_representation_cycles','Xroot_length_rounding_cycles','wavelength_representation_cycles','quotient_RN64_cycles','quarter_subtraction_RN64_cycles'}
    E=sum(uc.values(),F(0));assert all(t>=0 for t in uc.values()) and q(ad['upstream_cycles_bound'])==E and abs(R-R0)<=E
    exact=C*R;ow=RN(exact,64,rw>>63);T=bits(ow);em=abs(T-exact)
    phases={n.replace('_cycles','_rad'):hi*t for n,t in uc.items()}
    phases.update(constant_2pi_rad=abs(R)*EC,argument_multiply_RN64_rad=em);P=sum(phases.values(),F(0))
    interval=sorted([lo*R0,hi*R0]);observed=max(abs(T-t) for t in interval)
    assert observed<=P and abs(T)+P<1
    assert v['TWO_PI_uint64']==CW and v['pi_enclosure_rad_per_cycle']==[pair(lo),pair(hi)]
    assert q(v['constant_2pi_error_bound_rad_per_cycle'])==EC
    assert v['multiply_node']=={'input_uint64':[rw,CW],'output_uint64':ow,'exact_product_rad':pair(exact),'signed_RN64_delta_rad':pair(T-exact)}
    assert v['argument_uint64']==ow and v['fixed_ORIGINAL_argument_interval_rad']==[pair(t) for t in interval]
    assert v['phase_charges_rad']=={n:pair(t) for n,t in phases.items()} and q(v['argument_to_fixed_ORIGINAL_bound_rad'])==P
    assert q(v['observed_argument_error_upper_rad'])==observed and v['unchanged_phase_cap_rad']==[1,10**12]
    assert v['point_argument_phase_charge_fits_cap'] is (P<=F(1,10**12)) and v['new_RN64_multiplies']==1
    return T,P,phases

def verify_unit(ad,v,profile):
    assert ad['coefficient_profile_sha256']==digest(profile) and ad['unchanged_phase_cap_rad']==[1,10**12]
    aw=ad['argument_uint64'];x=bits(aw);X=abs(x);k=ad['quadrant_mod4'];assert type(k) is int and 0<=k<4
    up={n:q(t) for n,t in ad['upstream_phase_charges_rad'].items()};A=sum(up.values(),F(0))
    assert len(up)==7 and all(t>=0 for t in up.values()) and q(ad['upstream_phase_bound_rad'])==A and X+A<1
    nodes=[];given=v['nodes']
    def node(a,b,op,label):
        aq,bq=bits(a),bits(b);exact=aq*bq if op=='mul' else aq+bq
        zs=(a>>63)^(b>>63) if op=='mul' else int(aq==bq==0 and a>>63==b>>63==1)
        w=RN(exact,64,zs);val=bits(w);delta=val-exact
        expected={'label':label,'op':op,'input_uint64':[a,b],'output_uint64':w,'exact_operation':pair(exact),'signed_RN64_delta':pair(delta)}
        assert given[len(nodes)]==expected;nodes.append(expected);return w,abs(delta)
    zw,ez=node(aw,aw,'mul','square');Z=abs(bits(zw));terms={};words=[]
    for name,odd in (('cos',0),('sin',1)):
        cs=[F((-1)**j,math.factorial(2*j+odd)) for j in range(7)]
        for c,exact in zip(profile[name],cs):
            assert c['uint64']==RN(exact,64,int(exact<0)) and q(c['exact_rational'])==exact and q(c['error_rational'])==abs(bits(c['uint64'])-exact)
        hw=profile[name][6]['uint64'];ideal=cs[6];ec=abs(bits(hw)-ideal);es=er=F(0)
        for j in range(5,-1,-1):
            pw,em=node(hw,zw,'mul',name+'.mul'+str(j));hw,ea=node(pw,profile[name][j]['uint64'],'add',name+'.add'+str(j))
            ec=Z*ec+abs(bits(profile[name][j]['uint64'])-cs[j]);es=Z*es+abs(ideal)*ez;er=Z*er+em+ea
            ideal=ideal*x*x+cs[j]
        if odd:
            hw,ef=node(hw,aw,'mul','sin.final');ec*=X;es*=X;er=er*X+ef;ideal*=x
        assert ideal==sum((c*x**(2*j+odd) for j,c in enumerate(cs)),F(0))
        obs=abs(bits(hw)-ideal);assert obs<=ec+es+er;rem=X**(14+odd)/math.factorial(14+odd)
        terms[name]={'coefficient_L1':pair(ec),'square_L1':pair(es),'RN_nodes_L1':pair(er),'Taylor_L1':pair(rem),
            'ideal_polynomial':pair(ideal),'observed_polynomial_error_L1':pair(obs),'term_total_L1':pair(ec+es+er+rem)}
        words.append(hw)
    poly={n:sum((q(t[n]) for t in terms.values()),F(0)) for n in ('coefficient_L1','square_L1','RN_nodes_L1','Taylor_L1')}
    B=sum(poly.values(),F(0));assert 0<=B<F(1,2) and len(nodes)==len(given)==26
    c,s=words;unit=[c,s] if k==0 else ([s^SIGN,c] if k==1 else ([c^SIGN,s^SIGN] if k==2 else [s,c^SIGN]))
    l1={**poly,**{n.replace('_rad','_L1'):2*t for n,t in up.items()}}
    phase={**up,**{n.replace('_L1','_phase_rad'):t/(1-B) for n,t in poly.items()}}
    P=sum(phase.values(),F(0));L=sum(l1.values(),F(0));assert P==B/(1-B)+A and L==B+2*A and len(l1)==len(phase)==11
    assert v['argument_uint64']==aw and v['quadrant_mod4']==k and v['coefficient_profile_sha256']==digest(profile)
    assert v['unpermuted_unit_uint64']==words and v['unit_uint64']==unit and v['terms']==terms
    assert v['polynomial_charges_L1']=={n:pair(t) for n,t in poly.items()} and q(v['point_polynomial_L1_bound'])==B
    assert q(v['point_polynomial_phase_bound_rad'])==B/(1-B)
    assert v['unit_L1_charges_to_FIXED_ORIGINAL']=={n:pair(t) for n,t in l1.items()} and q(v['point_unit_L1_bound_to_FIXED_ORIGINAL'])==L
    assert v['phase_charges_to_FIXED_ORIGINAL_rad']=={n:pair(t) for n,t in phase.items()} and q(v['point_unit_phase_bound_to_FIXED_ORIGINAL_rad'])==P
    assert v['unchanged_phase_cap_rad']==[1,10**12] and v['point_unit_phase_charge_fits_cap'] is (P<=F(1,10**12))
    assert v['new_RN64_horner_nodes']==26 and v['quarter_bit_permutation_executed'] is True and v['zero_canonicalization_performed'] is False
    return B,L,P,unit

r=json.loads((ROOT/REPORT).read_bytes());assert r['task_id']=='AXIAL-GUARDED-ARGUMENT-UNIT-RN64-CPU-001'
pins=pins_from(r)
for p,h in pins.items():assert sha((ROOT/p).read_bytes())==h,p
assert len(pins)==372
old=payload(read(PREVIOUS,PREVIOUS_SHA))['data']['audit']
def data(p):return payload(read(p,pins[p]))
quot=data('coordinacion/respuestas/AXIAL-GUARDED-QUOTIENT-QUARTER-RN64-CPU-001-CODEX.json')['data']['audit']
roots=data('coordinacion/respuestas/AXIAL-GUARDED-HILO-XROOT-RN64-CPU-001-CODEX.json')['data']['audit']
profile=data('coordinacion/respuestas/AXIAL-UNIFORM-UNIT-HOST-001-CODEX.json')['data']['audit']['coefficient_profile']
packets=data('coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json')['packets']
packets.update({n:v['parent'] for n,v in data('coordinacion/respuestas/AXIAL-NATIVE-PRESENCE-STOPS-001-CODEX.json')['synthetic_controls'].items()})
raw=payload(r);assert raw['PASS'] is True and raw['tests']==4
a=raw['data']['audit'];assert a['case_order']==old['case_order'] and set(a['cases'])==set(old['cases'])
assert a['coefficient_profile']==profile and a['inherited_pins_verified']==368
FALSE=tuple(r['proof_scope']);assert len(FALSE)==38 and all(t is False for t in r['proof_scope'].values())
def allfalse(obj):
    for n in FALSE:assert obj[n] is False,n
allfalse(a);executed=stopped=0;Bs={};Ls={};Ps={};units={}
for name,c in a['cases'].items():
    ctx,snap=context(packets[name]);assert c['context']==old['cases'][name]['context']==quot['cases'][name]['context']==roots['cases'][name]['context']==ctx;allfalse(c)
    assert [t['source_id'] for t in c['sources']]==ctx['source_order']
    for i,row in enumerate(c['sources']):
        oldrow=old['cases'][name]['sources'][i];qr=quot['cases'][name]['sources'][i];rr=roots['cases'][name]['sources'][i]
        assert row['source_id']==oldrow['source_id']==qr['source_id']==rr['source_id'] and row['retained_row_sha256']==digest(oldrow)
        assert row['status']=='STOP';allfalse(row)
        assert row['guarded_argument_unit_RN64_CPU_executed'] is oldrow['guarded_residual_argument_RN64_CPU_executed']
        if not row['guarded_argument_unit_RN64_CPU_executed']:
            stopped+=1;assert 'result' not in row and row['reason']==oldrow['reason'];continue
        executed+=1;root=rr['result'];fixed=root['fixed_ORIGINAL_reference'];dec=root['new_decoded_Xroot_result'];sign=int(snap['sources'][i]['direction'][0])
        coords={'M':snap['objects']['M']['vertices_world_BU'][0][0],'S':snap['sources'][i]['position_BU'][0],
          'D':snap['objects']['D']['vertices_world_BU'][0][0],'R':snap['objects']['D']['mode_origin_BU'][0],'wavelength':snap['lambda_BU']}
        assert fixed['ORIGINAL_coordinates_BU']=={n:pair(bits(word(t))) for n,t in coords.items()}
        verify_composition(root['composition'],fixed,dec,sign)
        L=bits(dec['effective_reference_length_uint64']);W=bits(word(root['decoded_snapshot']['lambda_BU']));qw=RN(L/W,64,0);Q=bits(qw)
        k=(4*Q+F(1,2))//1;kw=RN(F(k,4),64,0);rw=RN(Q-bits(kw),64,0);R=bits(rw)
        Q0=sign*(2*bits(word(coords['M']))-bits(word(coords['S']))-bits(word(coords['R'])))/bits(word(coords['wavelength']))
        assert q(fixed['exact_ORIGINAL_cycles'])==Q0 and k==fixed['quarter_index']==qr['result']['HOST_quarter_index']
        uc={n:q(t) for n,t in root['composition']['cycle_charges_to_fixed_ORIGINAL'].items()}
        uc.update(quotient_RN64_cycles=abs(Q-L/W),quarter_subtraction_RN64_cycles=abs(R-(Q-bits(kw))))
        E=sum(uc.values(),F(0));assert F(1,8)-abs(Q0-F(k,4))-(E-uc['quarter_subtraction_RN64_cycles'])>0
        expectedA={'source_id':fixed['source_id'],'residual_uint64':rw,'fixed_ORIGINAL_residual_cycles':pair(Q0-F(k,4)),
            'upstream_cycle_charges':{n:pair(t) for n,t in uc.items()},'upstream_cycles_bound':pair(E),'unchanged_phase_cap_rad':[1,10**12],
            'TWO_PI_uint64':CW,'retained_quotient_row_sha256':digest(qr)}
        assert oldrow['admission']==expectedA
        T,A,phase=verify_argument(oldrow['admission'],oldrow['result'])
        expected={'source_id':fixed['source_id'],'argument_uint64':oldrow['result']['argument_uint64'],'quadrant_mod4':k%4,
            'upstream_phase_charges_rad':{n:pair(t) for n,t in phase.items()},'upstream_phase_bound_rad':pair(A),'unchanged_phase_cap_rad':[1,10**12],
            'coefficient_profile_sha256':digest(profile),'retained_argument_row_sha256':digest(oldrow)}
        assert row['admission']==expected
        assert row['phase_reference_id']==oldrow['phase_reference_id']==ctx['assignments'][i]['source_phase_reference_id']
        assert row['terminal_reference_id']==oldrow['terminal_reference_id']==ctx['assignments'][i]['terminal_reference_id']
        B,L,P,U=verify_unit(row['admission'],row['result'],profile);assert P<=F(1,10**12)
        Bs[name]=float(B);Ls[name]=float(L);Ps[name]=float(P);units[name]=[float(bits(w)) for w in U]
assert (executed,stopped)==(2,17) and a['new_point_sources_executed']==a['new_quarter_bit_permutations']==2 and a['retained_sources_not_executed']==17
assert a['new_RN64_horner_nodes']==52 and a['old_native_stages_suites_reexecuted']==0
pre=raw['data']['preflight_rejections'];assert pre['new_CPU_nodes']==0 and pre['prior_case_also_not_executed'] is True
assert {t['label'] for t in pre['rejections']}=={'second_context','foreign_gauge','argument_word','argument_charge','promotion','coefficient_RN','predecessor_SHA'}
typed=raw['data']['typed_rejections'];assert typed['new_CPU_nodes']==0 and len(typed['rejections'])==len({t['label'] for t in typed['rejections']})==15
assert all(t['reason'] for t in pre['rejections']+typed['rejections'])
fails=raw['data']['runtime_FAILs'];assert len(fails)==2
for t in fails:
    aw=t['admission']['argument_uint64'];x=bits(aw);zw=RN(x*x,64,0)
    if t['label']=='wrong_square_RN':correct=zw;assert t['CPU_nodes_attempted']==1
    else:
        pw=RN(bits(profile['cos'][6]['uint64'])*bits(zw),64,int(bits(profile['cos'][6]['uint64'])*bits(zw)<0))
        exact=bits(pw)+bits(profile['cos'][5]['uint64']);correct=RN(exact,64,int(exact<0));assert t['CPU_nodes_attempted']==3
    assert t['reason'] and t['attempts']==[{'correct_uint64':correct,'forged_uint64':correct+1}]
controls=raw['data']['scalar_controls'];assert len(controls)==10
zero_cases=set()
for t in controls:
    B,L,P,U=verify_unit(t['admission'],t['result'],profile)
    if t['label']=='signed_zero':
        w=t['admission']['argument_uint64'];k=t['admission']['quadrant_mod4'];zero_cases.add((w>>63,k));assert B==L==P==0
        assert t['result']['unpermuted_unit_uint64']==[word(1.0),w]
    elif t['label']=='Taylor_cap_FAIL':assert P>F(1,10**12) and t['result']['point_unit_phase_charge_fits_cap'] is False
    else:assert bits(t['result']['unpermuted_unit_uint64'][1])<0
assert zero_cases=={(s,k) for s in (0,1) for k in range(4)}
print(json.dumps({'PASS':True,'pins':len(pins),'sources':2,'retained_STOP':17,'new_main_RN64_nodes':52,'main_quarter_bit_permutations':2,
 'polynomial_L1_bounds':Bs,'unit_L1_to_FIXED_ORIGINAL_bounds':Ls,'unit_phase_to_FIXED_ORIGINAL_rad':Ps,'unit_reim':units,
 'preflight_rejections':7,'typed_rejections':15,'signed_zero_quadrant_controls':8,'Taylor_cap_FAIL_preserved':True,
 'wrong_square_add_RN_STOP':True,'old_stages_suites_reexecuted':0,'GPU_native_backend_uniform_full_field_admitted':False},sort_keys=True))
