"""Independent stdlib482pin encoder word-class oracle; no production imports."""
import base64,hashlib,json,math,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT='coordinacion/respuestas/AXIAL-SOURCE-BINARY64-ENCODER-WORDCLASS-HOST-001-CODEX.json'
PARENT='coordinacion/respuestas/AXIAL-SOURCE-DOMAIN-PHASE-CONSUMER-HOST-001-CODEX.json'
PARENT_SHA='7ac15550539842bcd45aa9a61fad3d95fcc47b4ba846cfae5bfd362c2ba919ce'
INPUT='coordinacion/respuestas/AXIAL-SOURCE-DOMAIN-PHASE-INPUT-HOST-001-CODEX.json'
MODEL='axial-SOURCE-binary64-grid-encoder-normal-or-zero-sufficient-HOST-v1'
GRID='finite ORIGINAL binary64 values in declared intervals ONLY; not arbitrary real continuum'
ARITH='RN-even binary32/binary64; exact widening; gradual underflow; no FTZ/FMA'
FLAG='sufficient_numeric_encoder_wordclasses_under_explicit_binary64_grid_HOST'
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def rat(x):
    assert type(x) is list and len(x)==2 and all(type(n) is int and n.bit_length()<=4096 for n in x)
    assert x[1]>0 and math.gcd(*x)==1;return F(*x)
def pair(x):return [x.numerator,x.denominator]
def two(e):return F(2**e) if e>=0 else F(1,2**(-e))
def payload(r):
    t=r['test_run'];b=zlib.decompress(base64.b64decode(''.join(t['stdout_zlib_base64_chunks'])))
    assert len(b)==t['stdout_bytes'] and sha(b)==t['stdout_sha256'];return json.loads(b)
def bits(w,n,allow_zero=False,allow_subnormal=False):
    p,bias,emin=(23,127,-126) if n==32 else (52,1023,-1022)
    ebits=8 if n==32 else 11
    assert type(w) is int and 0<=w<2**n
    exp=(w>>p)&(2**ebits-1);frac=w&(2**p-1);sign=w>>(n-1)
    if exp==0:
        if frac==0:
            assert allow_zero;return F(0)
        assert allow_subnormal
        return (-1 if sign else 1)*F(frac)*two(emin-p)
    assert exp<2**ebits-1
    return (-1 if sign else 1)*F(2**p+frac)*two(exp-bias-p)
def rn_neighbor_check(target,w,n):
    actual=bits(w,n,allow_zero=True)
    if target==0:assert actual==0;return actual
    p=23 if n==32 else 52
    assert actual!=0 and (target>0)==(actual>0)
    # Numeric adjacent normal magnitudes at either side; no native casts.
    aw=w&((1<<(n-1))-1);sign=-1 if target<0 else 1
    prev=sign*bits(aw-1,n,allow_subnormal=True);nxt=sign*bits(aw+1,n,allow_subnormal=True)
    da=abs(target-actual)
    assert da<=abs(target-prev) and da<=abs(target-nxt)
    if da==abs(target-prev) or da==abs(target-nxt):assert aw%2==0
    return actual
def main():
    r=json.loads((ROOT/REPORT).read_bytes());b=(ROOT/PARENT).read_bytes();assert sha(b)==PARENT_SHA
    p=json.loads(b);inherited={**p['code_doc_sha256'],PARENT:PARENT_SHA};own=r['own_code_doc_sha256'];pins={**inherited,**own}
    assert len(inherited)==478 and len(own)==4 and len(pins)==482 and not set(inherited)&set(own) and r['code_doc_sha256']==pins
    for path,h in pins.items():assert sha((ROOT/path).read_bytes())==h,path
    assert r['task_id']=='AXIAL-SOURCE-BINARY64-ENCODER-WORDCLASS-HOST-001' and r['model']==MODEL
    assert r['base_commit']=='36b2f5109aab8064227604713d019cc92d2f7ba2'
    old=payload(p)['data'];inputs=payload(json.loads((ROOT/INPUT).read_bytes()))['data'];run=payload(r);d=run['data']
    assert run['tests']==5 and run['PASS'] is True
    t=r['test_run'];assert t['rc']==0 and t['timed_out'] is False and t['threads']==t['affinity_mask']==1 and t['hard_child_timeout_seconds']==60
    flags=tuple(r['proof_scope']);assert len(flags)==38 and all(v is False for v in r['proof_scope'].values())
    def nf(x):assert all(x[k] is False for k in flags)
    def component(x,interval):
        nf(x);assert x['model']==MODEL and x['explicit_grid_assumption']==GRID and x['arithmetic_model']==ARITH and x['interval']==interval
        for k in ('actual_scene_domain_grid_authenticated','all_real_continuum_wordclasses_proved','frozen_guard_admission_for_entire_box_proved','signed_zero_execution_policy_proved','SOURCE_graph_executed'):assert x[k] is False
        assert x['status']=='STOP' and x['frozen_guard_verdict'] is x['uniform_executed_SOURCE_error_L1'] is None
        a,b=map(rat,interval);assert a<=b
        m=F(0) if a<=0<=b else min(abs(a),abs(b));M=max(abs(a),abs(b))
        assert x['min_abs']==pair(m) and x['max_abs']==pair(M)
        sufficient=(a==b==0) or (m>=two(-74) and M<=two(127))
        assert x[FLAG] is sufficient
        if not sufficient:assert x['proof'] is None;return False
        v=x['proof']
        if a==b==0:
            assert v=={'case':'exact-zero numeric magnitudes ONLY','numeric_magnitudes_zero':True};return True
        e=m.numerator.bit_length()-m.denominator.bit_length()
        if two(e)>m:e-=1
        assert two(e)<=m<two(e+1)
        q=two(e-52);hg=two(e-24);u=two(-24);v64=two(-53)
        expected={'binary64_grid_quantum_lower_bound':q,'binary32_high_grid_quantum_lower_bound':hg,
            'high_grid_multiple':hg/q,'u32':u,'u64':v64,'high_abs_lower_bound':(1-u)*m,'high_abs_upper_bound':(1+u)*M,
            'exact_residual_abs_upper_bound':u*M,'nonzero_exact_residual_abs_lower_bound':q,
            'low_abs_upper_bound':(1+u)*u*M,'decoded_abs_lower_bound':(1-v64)*(1-u*u)*m,
            'decoded_abs_upper_bound':(1+v64)*(1+u*u)*M}
        assert v['binary64_binade_floor']==e and all(v[k]==pair(n) for k,n in expected.items())
        assert q>=two(-126) and hg/q==two(28)
        assert two(-126)<expected['high_abs_lower_bound']<=expected['high_abs_upper_bound']<(two(24)-1)*two(104)
        assert expected['low_abs_upper_bound']<(two(24)-1)*two(104)
        assert two(-1022)<expected['decoded_abs_lower_bound']<=expected['decoded_abs_upper_bound']<(two(53)-1)*two(971)
        assert 1-u>F(1,2) and 1+u<2
        assert v['sterbenz_same_sign_ratio_in_half_to_two'] is v['residual_RN64_exact_under_grid_model'] is True
        assert v['SOURCE_product_UNIT_material_nodes_covered'] is False
        return True
    for variant in ('real_missing','explicit_None_missing','synthetic_valid'):
        a=d[variant];base=inputs[variant]
        nf(a);assert a['model']==MODEL and a['explicit_grid_assumption']==GRID and a['arithmetic_model']==ARITH and a['variant']==variant
        assert a['inherited_pins_verified']==478 and a['case_order']==base['case_order'] and set(a['cases'])==set(base['cases'])
        assert a['actual_scene_domain_grid_authenticated'] is a['all_real_continuum_wordclasses_proved'] is a['uniform_SOURCE_enclosure_proved'] is False
        assert a['new_native_operations']==a['old_suites_producers_reexecuted']==a['old_counterexamples_reexecuted']==a['group_admissions']==0
        count=0
        for name in a['case_order']:
            case=a['cases'][name];ctx=base['cases'][name]['context']
            nf(case);assert case['context']==ctx==old[variant]['cases'][name]['context'] and case['status']=='STOP'
            assert case['group_field_bound_L1'] is case['group_phase_bound_rad'] is None
            if variant!='synthetic_valid':assert case['sources'] is None;continue
            dom=inputs['synthetic_validated_domains'][name];pr=old[variant]['cases'][name]['sources']
            assert [s['source_id'] for s in case['sources']]==ctx['source_order']==[s['source_id'] for s in dom['sources']]
            for s,src,prev in zip(case['sources'],dom['sources'],pr):
                nf(s);assert s['source_id']==src['source_id']==prev['source_id']
                assert s['domain_source_sha256']==prev['domain_source_sha256']==digest(src)
                assert s['retained_consumer_SOURCE_sha256']==digest(prev)
                assert s['retained_whole_box_guard_admission_disproved'] is prev['whole_box_guard_admission_disproved']
                assert s['actual_scene_domain_grid_authenticated'] is s['frozen_guard_admission_for_entire_box_proved'] is False
                assert s['status']=='STOP' and s['uniform_executed_SOURCE_error_L1'] is None
                assert len(s['components'])==2
                vals=[component(c,i) for c,i in zip(s['components'],src['box_reim'])]
                assert s[FLAG] is all(vals);count+=2
                if prev['whole_box_guard_admission_disproved'] is True:assert vals==[True,False] and s[FLAG] is False
        assert a['component_predicate_assessments']==count==(8 if variant=='synthetic_valid' else 0)
    assert d['real_missing']['cases']==d['explicit_None_missing']['cases']
    assert len(d['real_missing']['cases'])==17 and sum(len(x['context']['source_order']) for x in d['real_missing']['cases'].values())==19
    assert len(d['controls'])==len(d['control_intervals'])==7
    for k,x in d['controls'].items():component(x,d['control_intervals'][k])
    assert len(d['new_dyadic_RN_controls'])==16
    seen=set()
    for x in d['new_dyadic_RN_controls']:
        e,sign,offset=x['binade'],x['sign'],x['offset_binary64_ULP']
        assert e in (-74,-20,0,40) and sign in (0,1) and offset in (0,1);seen.add((e,sign,offset))
        value=bits(x['original_uint64'],64);h=rn_neighbor_check(value,x['high_uint32'],32)
        residual=value-h;assert bits(x['residual_uint64'],64,True)==residual
        low=rn_neighbor_check(residual,x['low_uint32'],32)
        dec=rn_neighbor_check(h+low,x['decoded_uint64'],64);assert dec==value
        assert x['original_uint64']==x['decoded_uint64']==(sign<<63)|((1023+e)<<52)|offset
        assert x['x']==pair(value) and x['high']==pair(h) and x['residual']==pair(residual) and x['low']==pair(low)
        assert value==(-1 if sign else 1)*(two(e)+offset*two(e-52))
    assert len(seen)==16 and len(d['type_rejections'])==10 and len(d['INPUT_rejections'])==6
    assert r['actual_scene_domain_grid_authenticated'] is r['all_real_continuum_wordclasses_proved'] is r['frozen_guard_admission_for_entire_box_proved'] is False
    assert r['group_admissions']==0 and r['uniform_executed_SOURCE_error_L1'] is r['phase_INPUT_quota_fits'] is None and r['JEV_provenance']=='LOCAL'
    print(json.dumps({'PASS':True,'pins':482,'tests':5,'components':8,'new_dyadic_RN_controls':16,'interval_controls':7,
        'typed_INPUT_rejections':16,'retained_negative_guard_boxes':2,'REAL_missing_cases':17,'REAL_missing_sources':19,
        'group_admissions':0,'scope':'sufficient wordclasses under EXPLICIT binary64 grid only; actual scene/guard/execution STOP'},sort_keys=True))
if __name__=='__main__':main()
