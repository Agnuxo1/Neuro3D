"""Independent stdlib477pin conditional-consumer oracle; no production imports."""
import base64,hashlib,json,math,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT='coordinacion/respuestas/AXIAL-SOURCE-DOMAIN-PHASE-CONSUMER-HOST-001-CODEX.json'
PARENT='coordinacion/respuestas/AXIAL-SOURCE-DOMAIN-PHASE-INPUT-HOST-001-CODEX.json'
PARENT_SHA='e23030aab9ff6eff0391424a97acd3f74a868dbce12698b43cb73a8f40c854db'
CERTIFICATE='coordinacion/respuestas/AXIAL-SOURCE-UNIFORM-IDEAL-REFLECTION-PHASE-HOST-001-CODEX.json'
CERT_SHA='dbadfe64901a5608064f76de805d1f89aef5349404333998d2556e990fb484c0'
MODEL='axial-variable-A-domain-SOURCE-phase-quota-conditional-consumer-HOST-v1'
FLAG='conditional_SOURCE_domain_phase_quota_compared_HOST'
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def pair(x):return [x.numerator,x.denominator]
def rat(x):
    assert type(x) is list and len(x)==2 and all(type(n) is int and n.bit_length()<=4096 for n in x)
    assert x[1]>0 and math.gcd(*x)==1;return F(*x)
def payload(r):
    t=r['test_run'];b=zlib.decompress(base64.b64decode(''.join(t['stdout_zlib_base64_chunks'])))
    assert len(b)==t['stdout_bytes'] and sha(b)==t['stdout_sha256'];return json.loads(b)
def main():
    r=json.loads((ROOT/REPORT).read_bytes());b=(ROOT/PARENT).read_bytes();assert sha(b)==PARENT_SHA
    p=json.loads(b);inherited={**p['code_doc_sha256'],PARENT:PARENT_SHA};own=r['own_code_doc_sha256'];pins={**inherited,**own}
    assert len(inherited)==473 and len(own)==4 and len(pins)==477 and not set(inherited)&set(own) and r['code_doc_sha256']==pins
    for path,h in pins.items():assert sha((ROOT/path).read_bytes())==h,path
    assert r['task_id']=='AXIAL-SOURCE-DOMAIN-PHASE-CONSUMER-HOST-001' and r['model']==MODEL
    assert r['base_commit']=='e9d1c283d25ccabe68438bb3138c1d0b73a9df91'
    cb=(ROOT/CERTIFICATE).read_bytes();assert sha(cb)==CERT_SHA
    certs=payload(json.loads(cb))['data'];inputs=payload(p)['data'];run=payload(r);d=run['data']
    assert run['tests']==5 and run['PASS'] is True
    t=r['test_run'];assert t['rc']==0 and t['timed_out'] is False and t['threads']==t['affinity_mask']==1 and t['hard_child_timeout_seconds']==60
    flags=tuple(r['proof_scope']);assert len(flags)==38 and all(v is False for v in r['proof_scope'].values())
    def nf(x):assert all(x[k] is False for k in flags)
    def comparison(x,bound,cap):
        assert x['model']==MODEL and x['conditional_principal_phase_bound_rad']==bound and x['synthetic_INPUT_cap_rad']==cap
        assert rat(cap)>=0 and x['uniform_phase_INPUT_quota_fits'] is x['uniform_executed_SOURCE_error_L1'] is None
        assert x['SOURCE_phase_policy_adopted'] is False and x['status']=='STOP';nf(x)
        if bound is None:assert x[FLAG] is False and x['conditional_phase_quota_fits'] is None;return None
        assert rat(bound)>=0 and x[FLAG] is True
        fit=rat(bound)<=rat(cap);assert x['conditional_phase_quota_fits'] is fit;return fit
    for variant in ('real_missing','explicit_None_missing','domain_present_phase_missing','synthetic_valid','synthetic_zero_valid'):
        a=d[variant];base=inputs[variant];present=variant in ('synthetic_valid','synthetic_zero_valid')
        assert a['model']==MODEL and a['variant']==variant and a['case_order']==base['case_order'] and set(a['cases'])==set(base['cases'])
        assert a['inherited_pins_verified']==473 and a['SOURCE_phase_policy_adopted'] is False and a['uniform_SOURCE_enclosure_proved'] is False;nf(a)
        assert a['new_native_operations']==a['old_suites_producers_reexecuted']==a['group_admissions']==0
        compared=fits=fails=missing=0
        for name in a['case_order']:
            out=a['cases'][name];ctx=base['cases'][name]['context'];pv=base['cases'][name]['INPUT']
            assert out['context']==ctx and out['phase_INPUT']==pv and out['status']=='STOP';nf(out)
            assert out['group_phase_bound_rad'] is out['group_field_bound_L1'] is None
            if not present:assert out['sources'] is None;continue
            dom=inputs['synthetic_validated_domains'][name]
            assert [s['source_id'] for s in out['sources']]==ctx['source_order']==[s['source_id'] for s in dom['sources']]
            cc=certs['synthetic_domains']['cases'].get(name,certs['real_missing']['cases'][name])
            assert cc['context']==ctx
            for i,(row,src,inp) in enumerate(zip(out['sources'],dom['sources'],pv['sources'])):
                assert row['source_id']==src['source_id']==inp['source_id'] and row['domain_source_sha256']==digest(src) and row['phase_INPUT_source_sha256']==digest(inp)
                assert inp['domain_source_sha256']==digest(src) and inp['reference_model']=='variable-ORIGINAL-A-in-declared-box-exp-i-fixed-ORIGINAL-theta-times-ideal-minus-one'
                assert all(inp[k]==src[k]==ctx['assignments'][i][k] for k in ('source_id','source_phase_reference_id','terminal_reference_id','common_terminal_reference_id'))
                assert row['uniform_phase_INPUT_quota_fits'] is None and row['status']=='STOP';nf(row)
                if cc['sources'] is None:
                    assert name=='two_sources' and row['conditional_certificate'] is row['whole_box_guard_admission_disproved'] is None
                    comparison(row['conditional_comparison'],None,inp['cap_rad']);missing+=1;continue
                cert=cc['sources'][i];proof=cert['proof'];bound=proof['conditional_principal_phase_bound_rad']
                assert cert['source_id']==src['source_id'] and cert['domain_source_sha256']==digest(src) and cert['whole_box_guard_admission_disproved'] is True
                assert proof['reference']=='variable ORIGINAL A times exp(i fixed ORIGINAL theta) times exact ideal -1'
                assert proof['model']=='axial-SOURCE-box-ideal-minus-one-principal-phase-conditional-HOST-v1'
                assert proof['material_model']=='exact ideal -1 sign reversal; L1 isometry; NOT physical material'
                assert proof['box_reim']==src['box_reim'] and proof['conditional_SOURCE_box_ideal_reflection_phase_HOST_proved'] is True and proof['status']=='STOP';nf(proof)
                for k in ('material_executed','physical_material_authenticated','unwrapped_phase_proved','frozen_guard_admission_for_entire_box_proved'):assert proof[k] is False
                assert proof['uniform_executed_SOURCE_error_L1'] is proof['executed_material_charge_L1'] is proof['phase_INPUT_quota_fits'] is None
                q=proof['fifteen_conditional_reflected_charges_L1'];assert len(q)==15 and q['ideal_material_exact_model_L1']==[0,1]
                vals=list(map(rat,q.values()));assert all(v>=0 for v in vals);eps=sum(vals,F(0))
                intervals=[tuple(map(rat,j)) for j in src['box_reim']]
                distances=[F(0) if lo<=0<=hi else min(abs(lo),abs(hi)) for lo,hi in intervals];m=max(distances)
                assert m>eps>=0 and proof['component_min_abs']==list(map(pair,distances)) and proof['amplitude_modulus_lower_bound']==pair(m)
                assert proof['conditional_reflected_RN_model_error_L1']==pair(eps) and proof['positive_radial_projection_lower_bound']==pair(m-eps) and bound==pair(eps/(m-eps))
                expected={'retained_conditional_SOURCE_sha256':digest(cert),'retained_conditional_proof_sha256':digest(proof),
                    'domain_source_sha256':digest(src),'phase_INPUT_source_sha256':digest(inp),
                    'conditional_principal_phase_bound_rad':bound,'whole_box_guard_admission_disproved':True}
                assert row['conditional_certificate']==expected and row['whole_box_guard_admission_disproved'] is True
                fit=comparison(row['conditional_comparison'],bound,inp['cap_rad']);compared+=1;fits+=int(fit);fails+=int(not fit)
                assert inp['cap_rad']==([0,1] if variant=='synthetic_zero_valid' else [1,1000000000000])
        assert a['conditional_certificate_inspections']==a['new_conditional_phase_comparisons']==compared==(2 if present else 0)
        assert a['missing_conditional_certificate_sources']==missing==(2 if present else 0)
        assert a['conditional_fit_count']==fits and a['conditional_fail_count']==fails
        assert (fits,fails)==((0,2) if variant=='synthetic_zero_valid' else (2,0) if present else (0,0))
    assert d['real_missing']['cases']==d['explicit_None_missing']['cases']
    assert len(d['real_missing']['cases'])==17 and sum(len(x['context']['source_order']) for x in d['real_missing']['cases'].values())==19
    for name,bound,cap in (('below',[1,3],[1,2]),('equal',[1,2],[1,2]),('above',[2,3],[1,2]),('zero_hypothesis',[0,1],[0,1]),('absent',None,[0,1])):
        comparison(d['boundary_controls'][name],bound,cap)
    assert len(d['typed_comparison_rejections'])==8 and len(d['INPUT_rejections'])==7 and len(d['certificate_rejections'])==17
    assert r['synthetic_controls_are_real_INPUT'] is r['output_fitted_INPUT'] is r['SOURCE_phase_policy_adopted'] is False
    assert r['group_admissions']==0 and r['uniform_executed_SOURCE_error_L1'] is r['phase_INPUT_quota_fits'] is None and r['JEV_provenance']=='LOCAL'
    print(json.dumps({'PASS':True,'pins':477,'tests':5,'control_conditional_fits':2,'zero_conditional_FAILs':2,
        'REAL_missing_cases':17,'REAL_missing_sources':19,'missing_multisource_certificates':2,
        'typed_INPUT_certificate_rejections':32,'group_admissions':0,'scope':'conditional mathematical comparison ONLY; policy/guard/execution STOP'},sort_keys=True))
if __name__=='__main__':main()
