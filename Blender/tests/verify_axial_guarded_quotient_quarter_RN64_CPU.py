"""Independent stdlib IEEE/YZ/root interval/length oracle; no production imports."""
import base64,hashlib,json,math,struct,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT='coordinacion/respuestas/AXIAL-GUARDED-QUOTIENT-QUARTER-RN64-CPU-001-CODEX.json'
PREVIOUS='coordinacion/respuestas/AXIAL-GUARDED-HILO-XROOT-RN64-CPU-001-CODEX.json'
PREVIOUS_SHA='9e8166babef7b1ba22a2d0b492a3950cf31127bfa2cfecbe35bb81b3be7f5e52'
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

r=json.loads((ROOT/REPORT).read_bytes());assert r['task_id']=='AXIAL-GUARDED-QUOTIENT-QUARTER-RN64-CPU-001'
pins=pins_from(r)
for p,h in pins.items():assert sha((ROOT/p).read_bytes())==h,p
assert len(pins)==362
old=payload(read(PREVIOUS,PREVIOUS_SHA))['data']['audit']
def data(p):return payload(read(p,pins[p]))
packets=data('coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json')['packets']
packets.update({n:v['parent'] for n,v in data('coordinacion/respuestas/AXIAL-NATIVE-PRESENCE-STOPS-001-CODEX.json')['synthetic_controls'].items()})
raw=payload(r);assert raw['PASS'] is True and raw['tests']==4
a=raw['data']['audit'];assert a['case_order']==old['case_order'] and set(a['cases'])==set(old['cases'])
assert a['inherited_pins_verified']==358
FALSE=tuple(r['proof_scope']);assert len(FALSE)==38 and all(v is False for v in r['proof_scope'].values())
def allfalse(x):
    for k in FALSE:assert x[k] is False,k
allfalse(a);executed=stopped=0;phases={};margins={};quotients={};residuals={}
for name,c in a['cases'].items():
    ctx,snap=context(packets[name]);assert c['context']==old['cases'][name]['context']==ctx;allfalse(c)
    assert [v['source_id'] for v in c['sources']]==ctx['source_order']
    for i,row in enumerate(c['sources']):
        prior=old['cases'][name]['sources'][i]
        assert row['source_id']==prior['source_id'] and row['retained_row_sha256']==digest(prior)
        assert row['status']=='STOP';allfalse(row)
        assert row['guarded_quotient_quarter_RN64_CPU_executed'] is prior['guarded_hilo_Xroot_RN64_CPU_executed']
        if not row['guarded_quotient_quarter_RN64_CPU_executed']:
            stopped+=1;assert 'result' not in row and row['reason']==prior['reason'];continue
        executed+=1;oldres=prior['result'];ad=row['admission'];v=row['result'];root=oldres['new_decoded_Xroot_result']
        fixed=oldres['fixed_ORIGINAL_reference'];Q0=q(fixed['exact_ORIGINAL_cycles']);sign=int(snap['sources'][i]['direction'][0])
        coords={'M':snap['objects']['M']['vertices_world_BU'][0][0],'S':snap['sources'][i]['position_BU'][0],
          'D':snap['objects']['D']['vertices_world_BU'][0][0],'R':snap['objects']['D']['mode_origin_BU'][0],'wavelength':snap['lambda_BU']}
        assert fixed['ORIGINAL_coordinates_BU']=={k:pair(bits(word(x))) for k,x in coords.items()}
        assert Q0==sign*(2*bits(word(coords['M']))-bits(word(coords['S']))-bits(word(coords['R'])))/bits(word(coords['wavelength']))
        verify_composition(oldres['composition'],fixed,root,sign)
        adexpected={'source_id':fixed['source_id'],'length_uint64':root['effective_reference_length_uint64'],
          'wavelength_uint64':word(oldres['decoded_snapshot']['lambda_BU']),'exact_retained_length_over_decoded_wave':
          pair(bits(root['effective_reference_length_uint64'])/bits(word(oldres['decoded_snapshot']['lambda_BU']))),
          'fixed_ORIGINAL_cycles':pair(Q0),'fixed_quarter_index':fixed['quarter_index'],
          'upstream_cycle_charges':oldres['composition']['cycle_charges_to_fixed_ORIGINAL'],
          'upstream_cycles_bound':oldres['composition']['cycles_to_fixed_ORIGINAL_bound'],
          'unchanged_phase_cap_rad':[1,10**12],'retained_result_sha256':digest(oldres)}
        assert ad==adexpected
        Lw,Ww=ad['length_uint64'],ad['wavelength_uint64'];L,W=bits(Lw),bits(Ww);assert L>0 and W>0
        exact=L/W;qw=RN(exact,64,0);Q=bits(qw);k=(4*Q+F(1,2))//1
        assert k==fixed['quarter_index'] and type(k) is int and abs(k)<2**51
        kw=RN(F(k,4),64,0 if k>=0 else 1);K=bits(kw);assert K==F(k,4)
        rw=RN(Q-K,64,0);R=bits(rw);assert abs(R)<F(1,8)
        assert v['division_node']=={'input_uint64':[Lw,Ww],'output_uint64':qw,'exact_quotient':pair(exact),'signed_RN64_delta_cycles':pair(Q-exact)}
        assert v['quarter_cast_node']=={'input_exact_rational':pair(F(k,4)),'output_uint64':kw,'RN64_delta_cycles':[0,1]}
        assert v['residual_subtraction_node']=={'input_uint64':[qw,kw],'output_uint64':rw,'exact_subtraction_cycles':pair(Q-K),'signed_RN64_delta_cycles':pair(R-(Q-K))}
        assert v['quotient_uint64']==qw and v['HOST_quarter_index']==k and v['residual_uint64']==rw
        charges={n:q(x) for n,x in ad['upstream_cycle_charges'].items()}
        charges.update(quotient_RN64_cycles=abs(Q-exact),quarter_subtraction_RN64_cycles=abs(R-(Q-K)))
        assert len(charges)==5 and all(x>=0 for x in charges.values())
        assert v['cycle_charges_to_fixed_ORIGINAL']=={n:pair(x) for n,x in charges.items()}
        E=sum(charges.values(),F(0));margin=F(1,8)-abs(Q0-F(k,4))-(E-charges['quarter_subtraction_RN64_cycles'])
        assert margin>0 and q(v['quarter_margin_with_quotient_error_cycles'])==margin
        assert v['fixed_ORIGINAL_residual_cycles']==pair(Q0-F(k,4))
        assert q(v['residual_to_fixed_ORIGINAL_bound_cycles'])==E and q(v['observed_residual_error_cycles'])==abs(R-(Q0-F(k,4)))<=E
        ps={n.replace('_cycles','_rad'):2*PIHI*x for n,x in charges.items()};P=sum(ps.values(),F(0))
        assert v['phase_charges_rad']=={n:pair(x) for n,x in ps.items()}
        assert q(v['phase_quotient_residual_only_bound_rad'])==P and v['partial_phase_charge_fits_cap'] is (P<=F(1,10**12))
        assert v['unchanged_phase_cap_rad']==[1,10**12]
        assert v['new_RN64_divisions']==v['new_exact_quarter_RN64_casts']==v['new_RN64_subtractions']==1
        assert row['phase_reference_id']==ctx['assignments'][i]['source_phase_reference_id']
        assert row['terminal_reference_id']==ctx['assignments'][i]['terminal_reference_id']
        phases[name]=float(P);margins[name]=float(margin);quotients[name]=float(Q);residuals[name]=float(R)
assert (executed,stopped)==(2,17) and a['new_point_sources_executed']==2 and a['retained_sources_not_executed']==17
assert a['new_RN64_divisions']==a['new_exact_quarter_RN64_casts']==a['new_RN64_subtractions']==2
assert a['new_encoder_guard_decode_Xroot_reference_Horner_source_material_reduction_power_readout']==a['old_audits_suites_reexecuted']==0
assert a['native_quarter_selector_implemented'] is False
pre=raw['data']['whole_request_preflight_rejections'];assert pre['new_CPU_operations']==0 and pre['prior_case_also_not_executed'] is True
assert {x['label'] for x in pre['rejections']}=={'second_case_stale_context','decoded_wavelength_changed','predecessor_SHA'}
typed=raw['data']['typed_admission_rejections'];assert typed['new_CPU_operations']==0
assert len(typed['rejections'])==len({x['label'] for x in typed['rejections']})==14
assert all(x['reason'] for x in pre['rejections']+typed['rejections'])
controls=raw['data']['STOP_controls'];assert len(controls)==5
base=a['cases']['thin_resolved']['sources'][0]['admission']
for t in controls:
    label=t['label'];ad=t['admission'];assert t['reason'] and ad['unchanged_phase_cap_rad']==[1,10**12]
    x=bits(ad['length_uint64'])/bits(ad['wavelength_uint64']);qw=RN(x,64,0);Q=bits(qw);k=(4*Q+F(1,2))//1
    kw=RN(F(k,4),64,0);K=bits(kw);rw=RN(Q-K,64,0)
    if label in ('larger_majorant_no_cap_change','exact_quarter_boundary'):
        E=sum((q(v) for v in ad['upstream_cycle_charges'].values()),F(0))+abs(Q-x)
        M=F(1,8)-abs(q(ad['fixed_ORIGINAL_cycles'])-F(k,4))-E
        assert M<=0 and t['division_attempts']==1 and t['quarter_casts']==t['residual_subtractions']==0
        if label=='exact_quarter_boundary':assert Q==F(1,8) and k==1 and M==0
        else:assert ad['upstream_cycle_charges']['geometry_representation_cycles']==[1,8]
    else:
        assert ad==base and len(t['attempts'])==1
        correct={'wrong_division_RN':qw,'wrong_quarter_cast_RN':kw,'wrong_residual_RN':rw}[label]
        assert t['attempts'][0]=={'correct_uint64':correct,'forged_uint64':correct+1}
print(json.dumps({'PASS':True,'pins':len(pins),'new_CPU_divisions':2,'new_exact_quarter_casts':2,'new_CPU_subtractions':2,
 'sources':2,'retained_STOP':17,'phase_quotient_residual_only_rad':phases,'quarter_margins_cycles':margins,
 'quotients':quotients,'residuals':residuals,'preflight_rejections':3,'typed_rejections':14,'STOP_controls':5,
 'old_stages_suites_reexecuted':0,'native_quarter_argument_full_field_GPU':False},sort_keys=True))
