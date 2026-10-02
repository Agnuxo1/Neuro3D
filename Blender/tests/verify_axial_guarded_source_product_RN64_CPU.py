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


SOURCE_REPORT='coordinacion/respuestas/AXIAL-GUARDED-SOURCE-PRODUCT-RN64-CPU-001-CODEX.json'
UNIT_REPORT='coordinacion/respuestas/AXIAL-GUARDED-ARGUMENT-UNIT-RN64-CPU-001-CODEX.json'
UNIT_SHA='e6d311ab43e94b1d94630873e80ade501379e78b13a5a753cb9e29be2f6f3424'
ARG_REPORT='coordinacion/respuestas/AXIAL-GUARDED-RESIDUAL-ARGUMENT-RN64-CPU-001-CODEX.json'
r=read(UNIT_REPORT,UNIT_SHA);assert r['task_id']=='AXIAL-GUARDED-ARGUMENT-UNIT-RN64-CPU-001'
pins=pins_from(r)
for p,h in pins.items():assert sha((ROOT/p).read_bytes())==h,p
assert len(pins)==372
old=payload(read(ARG_REPORT,pins[ARG_REPORT]))['data']['audit']
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

unit_a=a
nr=json.loads((ROOT/SOURCE_REPORT).read_bytes());assert nr['task_id']=='AXIAL-GUARDED-SOURCE-PRODUCT-RN64-CPU-001'
npins=pins_from(nr);assert len(npins)==377
for p,h in npins.items():assert sha((ROOT/p).read_bytes())==h,p
nraw=payload(nr);assert nraw['PASS'] is True and nraw['tests']==4
na=nraw['data']['audit'];allfalse(na)
assert tuple(nr['proof_scope'])==FALSE and all(t is False for t in nr['proof_scope'].values())
def bits32(w):
    assert type(w) is int and 0<=w<2**32
    exp=(w>>23)&255;mant=w&((1<<23)-1);assert exp!=255 and (exp!=0 or mant==0)
    return (-1 if w>>31 else 1)*F(mant if exp==0 else mant+(1<<23))*F(2)**((1 if exp==0 else exp)-150)
def verify_source(ad,v):
    originals=ad['ORIGINAL_source_uint64'];sq=list(map(bits,originals));Uwords=ad['unit_uint64'];uv=list(map(bits,Uwords))
    unit_c={n:q(t) for n,t in ad['unit_L1_charges'].items()};U=sum(unit_c.values(),F(0))
    assert len(unit_c)==11 and all(t>=0 for t in unit_c.values()) and q(ad['unit_L1_bound'])==U<1
    enc=v['source_encoder'];ls=[];sums=[];E=F(0);records=[]
    for w,x in zip(originals,sq):
        hw=RN(x,32,w>>63);h=bits32(hw)
        exact=x-h;zs=int(x==h==0 and w>>63==1 and hw>>31==0);rw=RN(exact,64,zs);res=bits(rw)
        lw=RN(res,32,rw>>63);low=bits32(lw);represented=h+low;e=abs(represented-x);E+=e;sums.append(represented);ls.extend([hw,lw])
        records.append({'original_uint64':w,'high_uint32':hw,'residual_uint64':rw,'low_uint32':lw,
          'exact_residual':pair(exact),'signed_residual_RN64_delta':pair(res-exact),
          'signed_low_RN32_delta':pair(low-res),'represented_sum':pair(represented),'encoding_error_L1':pair(e)})
    rawbytes=struct.pack('<IIII',*ls)
    assert enc=={'ORIGINAL_source_uint64':originals,'limb_uint32':ls,'records':records,
      'hilo_le_base64':base64.b64encode(rawbytes).decode(),'hilo_le_sha256':sha(rawbytes),
      'exact_limb_sums':list(map(pair,sums)),'source_encoding_error_L1':pair(E),
      'new_RN32_casts':4,'new_RN64_subtractions':2,'zero_canonicalization_performed':False}
    nodes=[];given=v['nodes']
    def node(a,b,op,label):
        aq,bq=bits(a),bits(b);exact=aq*bq if op=='mul' else aq+bq
        zs=(a>>63)^(b>>63) if op=='mul' else int(aq==bq==0 and a>>63==b>>63==1)
        w=RN(exact,64,zs);val=bits(w);delta=val-exact
        expected={'label':label,'op':op,'input_uint64':[a,b],'output_uint64':w,'exact_operation':pair(exact),'signed_RN64_delta':pair(delta)}
        assert given[len(nodes)]==expected;nodes.append(expected);return w
    ws=[RN(bits32(w),64,w>>31) for w in ls]
    aa=node(ws[0],ws[1],'add','decode0');bb=node(ws[2],ws[3],'add','decode1')
    ac=node(aa,Uwords[0],'mul','ac');bd=node(bb,Uwords[1],'mul','bd')
    adw=node(aa,Uwords[1],'mul','ad');bc=node(bb,Uwords[0],'mul','bc')
    re=node(ac,bd^SIGN,'add','real');im=node(adw,bc,'add','imag');assert len(given)==len(nodes)==8
    D=sum((abs(q(t['signed_RN64_delta'])) for t in nodes[:2]),F(0));N=sum((abs(q(t['signed_RN64_delta'])) for t in nodes[2:]),F(0))
    S=sum(map(abs,sq),F(0));L=sum(map(abs,uv),F(0))
    charges={'source_encoding_L1':E*L,'source_decode_RN64_L1':D*L,**{'source_unit_'+n:S*t for n,t in unit_c.items()},'source_product_RN64_L1':N}
    B=sum(charges.values(),F(0));assert B==(E+D)*L+S*U+N and len(charges)==14
    reference=[sq[0]*uv[0]-sq[1]*uv[1],sq[0]*uv[1]+sq[1]*uv[0]]
    obs=abs(bits(re)-reference[0])+abs(bits(im)-reference[1]);assert obs<=(E+D)*L+N
    assert v['unit_uint64']==Uwords and v['decoded_source_uint64']==[aa,bb] and v['product_uint64']==[re,im]
    assert q(v['ORIGINAL_source_norm_L1'])==S and q(v['represented_unit_norm_L1'])==L
    assert q(v['observed_error_to_ORIGINAL_times_represented_unit_L1'])==obs
    assert v['detailed_source_charges_L1']=={n:pair(t) for n,t in charges.items()} and q(v['point_bare_source_bound_to_FIXED_ORIGINAL_L1'])==B
    assert v['new_decode_product_RN64_nodes']==8
    for key in ('source_amplitude_budget_admitted','source_phase_bound_proved','material_applied','zero_canonicalization_performed'):assert v[key] is False
    return B,ls,[re,im],nodes
executed=stopped=0;bounds={};products={}
assert na['case_order']==unit_a['case_order'] and na['inherited_pins_verified']==373
for name,c in na['cases'].items():
    uc=unit_a['cases'][name];ctx,snap=context(packets[name]);assert c['context']==uc['context']==ctx;allfalse(c)
    assert [t['source_id'] for t in c['sources']]==ctx['source_order']
    source_bytes=base64.b64decode(packets[name]['buffers_base64']['sources'],validate=True)
    assert packets[name]['manifest']['layout']['sources']['stride_words']==32 and len(source_bytes)==128*len(c['sources'])
    for i,row in enumerate(c['sources']):
        ur=uc['sources'][i];assert row['retained_row_sha256']==digest(ur) and row['source_id']==ur['source_id'] and row['status']=='STOP';allfalse(row)
        assert row['guarded_source_product_RN64_CPU_executed'] is ur['guarded_argument_unit_RN64_CPU_executed']
        if not row['guarded_source_product_RN64_CPU_executed']:
            stopped+=1;assert 'result' not in row and row['reason']==ur['reason'];continue
        executed+=1;uv=ur['result'];source_words=[word(x) for x in snap['sources'][i]['field_reim']]
        assert source_bytes[128*i+112:128*i+128]==struct.pack('<QQ',*source_words)
        expected={'source_id':row['source_id'],'ORIGINAL_source_uint64':source_words,'unit_uint64':uv['unit_uint64'],
          'unit_L1_charges':uv['unit_L1_charges_to_FIXED_ORIGINAL'],'unit_L1_bound':uv['point_unit_L1_bound_to_FIXED_ORIGINAL'],
          'retained_unit_row_sha256':digest(ur),'phase_reference_id':ur['phase_reference_id'],'terminal_reference_id':ur['terminal_reference_id']}
        assert row['admission']==expected and row['phase_reference_id']==ctx['assignments'][i]['source_phase_reference_id']
        assert row['terminal_reference_id']==ctx['assignments'][i]['terminal_reference_id']
        B,_,prod,_=verify_source(expected,row['result']);bounds[name]=float(B);products[name]=[float(bits(w)) for w in prod]
assert (executed,stopped)==(2,17) and na['new_point_sources_executed']==2 and na['retained_sources_not_executed']==17
assert (na['new_source_RN32_casts'],na['new_source_RN64_subtractions'],na['new_decode_product_RN64_nodes'])==(8,4,16)
assert na['old_native_stages_suites_reexecuted']==na['new_material_group_power_readout_executions']==0
pre=nraw['data']['preflight_rejections'];assert pre['new_CPU_ops']==0 and pre['prior_case_also_not_executed'] is True
assert {t['label'] for t in pre['rejections']}=={'second_context','foreign_gauge','unit_word','unit_node','unit_charge','phase_cap','boolean_cap','integer_bit_policy','promotion','source_order','predecessor_SHA'}
typed=nraw['data']['typed_rejections'];assert typed['new_CPU_ops']==0 and len(typed['rejections'])==14
assert all(t['reason'] for t in pre['rejections']+typed['rejections'])
controls=nraw['data']['scalar_controls'];assert len(controls)==7
zero_cases=set()
for t in controls:
    B,ls,prod,nodes=verify_source(t['admission'],t['result'])
    if t['label'] in ('scalar_0','scalar_1','scalar_2','scalar_3'):
        ow=t['admission']['ORIGINAL_source_uint64'];zero_cases.add(tuple(w>>63 for w in ow))
        assert ls==[ow[0]>>32,0,ow[1]>>32,0] and B==0 # IEEE -0 minus -0 -> +0 low
    if t['label']=='scalar_4':assert ls[0]==0x3f800000 and ls[2]==0xbf800002
assert zero_cases=={(a,b) for a in (0,1) for b in (0,1)}
fails=nraw['data']['runtime_FAILs'];assert len(fails)==4
for t in fails:
    base=t['admission'];w=base['ORIGINAL_source_uint64'][0];x=bits(w);hw=RN(x,32,w>>63);h=bits32(hw)
    rw=RN(x-h,64,int(x==h==0 and w>>63==1 and hw>>31==0));lw=RN(bits(rw),32,rw>>63)
    label=t['label']
    if label=='wrong_high_RN32':expected=hw;width=32
    elif label=='wrong_residual_RN64':expected=rw;width=64
    else:
        aa=RN(h+bits32(lw),64,int(h==bits32(lw)==0 and hw>>31==lw>>31==1));width=64
        expected=aa if label=='wrong_decode_RN64' else RN(bits(aa)*bits(base['unit_uint64'][0]),64,(aa>>63)^(base['unit_uint64'][0]>>63))
    assert t['reason'] and t['attempts']==[{'correct_word':expected,'forged_word':expected+1,'width':width}]
edges=nraw['data']['encoding_edge_STOPs'];assert {t['label'] for t in edges}=={'cast_overflow','selected_binary32_subnormal'}
assert all(t['reason'] for t in edges)
print(json.dumps({'PASS':True,'pins':len(npins),'sources':2,'retained_STOP':17,'main_new_RN32_casts':8,'main_new_RN64_subtractions':4,
 'main_new_decode_product_nodes':16,'source_prefix_L1_bounds':bounds,'source_product_reim':products,'separate_charges_per_source':14,
 'preflight_rejections':11,'typed_rejections':14,'synthetic_scalar_controls':7,'signed_zero_component_controls':4,
 'RN32_RN64_runtime_STOP_controls':4,'encoding_overflow_subnormal_STOPs':2,'old_native_stages_suites_reexecuted':0,
 'source_phase_allocation_full_field_GPU_RT_physical_admitted':False},sort_keys=True))
