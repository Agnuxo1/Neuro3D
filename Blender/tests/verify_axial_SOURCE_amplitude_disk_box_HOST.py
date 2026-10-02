"""Independent stdlib oracle: analytic interval geometry, exact binary64 anchors, immutable receipts."""
import base64,hashlib,json,math,struct,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT='coordinacion/respuestas/AXIAL-SOURCE-AMPLITUDE-DISK-BOX-HOST-001-CODEX.json'
PARENT='coordinacion/respuestas/AXIAL-SOURCE-PHASE-QUOTA-CONSUMER-HOST-001-CODEX.json'
PARENT_SHA='7acd92eb57129f998f2eb8b3ab8a315f43118c18ca77682bea0f48ed7eca43c3'
PHASE='coordinacion/respuestas/AXIAL-REFLECTED-SOURCE-PHASE-HOST-001-CODEX.json'
MODEL='axial-ORIGINAL-SOURCE-amplitude-box-conditional-disk-HOST-v1'
FLAG='conditional_amplitude_box_phase_lemma_HOST_proved'
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(x):return sha(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def read(p,h):
    b=(ROOT/p).read_bytes();assert sha(b)==h,p
    return json.loads(b)
def payload(r):
    t=r['test_run'];s=''.join(t['stdout_zlib_base64_chunks']) if 'stdout_zlib_base64_chunks' in t else t['stdout_zlib_base64']
    b=zlib.decompress(base64.b64decode(s));assert sha(b)==t['stdout_sha256'] and len(b)==t['stdout_bytes']
    return json.loads(b)
def pair(x):return [x.numerator,x.denominator]
def rat(x):
    assert type(x) is list and len(x)==2 and all(type(n) is int and n.bit_length()<=4096 for n in x)
    assert x[1]>0 and math.gcd(*x)==1
    return F(*x)
def main():
    r=json.loads((ROOT/REPORT).read_bytes());p=read(PARENT,PARENT_SHA)
    inherited={**p['code_doc_sha256'],PARENT:PARENT_SHA};own=r['own_code_doc_sha256'];pins={**inherited,**own}
    assert len(inherited)==433 and len(own)==4 and len(pins)==437 and not set(inherited)&set(own) and r['code_doc_sha256']==pins
    for path,h in pins.items():assert sha((ROOT/path).read_bytes())==h,path
    run=payload(r);old=payload(p)['data'];phases=payload(read(PHASE,pins[PHASE]))['data']['audit']
    assert run['PASS'] is True and run['tests']==5
    assert r['test_run']['rc']==0 and r['test_run']['timed_out'] is False and r['test_run']['threads']==1 and r['test_run']['hard_child_timeout_seconds']==60
    flags=tuple(r['proof_scope']);assert len(flags)==38 and all(v is False for v in r['proof_scope'].values())
    def allfalse(v):assert all(v[k] is False for k in flags)
    def lemma(v,expected_eps):
        assert v['model']==MODEL and v['uniform_error_hypothesis_L1']==expected_eps
        assert v['uniform_executed_SOURCE_error_L1'] is None and v['uniform_SOURCE_enclosure_proved'] is False
        assert v['group_phase_bound_rad'] is None and v['status']=='STOP';allfalse(v)
        dd=[]
        for endpoints in v['box_reim']:
            lo,hi=map(rat,endpoints);assert lo<=hi
            # Independent piecewise distance-to-origin expression, no production import.
            dd.append(lo if lo>0 else (-hi if hi<0 else F(0)))
        m=max(dd);assert v['component_min_abs']==list(map(pair,dd)) and v['amplitude_lower_bound']==pair(m)
        assert m*m<=dd[0]*dd[0]+dd[1]*dd[1] # Analytic minimum squared modulus is sum of squared coordinate distances.
        if expected_eps is None:
            assert v[FLAG] is False and v['positive_radial_lower_bound'] is v['conditional_phase_bound_rad'] is None
        else:
            eps=rat(expected_eps);assert 0<=eps<m
            assert v[FLAG] is True and v['positive_radial_lower_bound']==pair(m-eps) and v['conditional_phase_bound_rad']==pair(eps/(m-eps))
    d=run['data'];real=d['real_missing'];assert set(real['cases'])==set(old['real_missing']['cases']) and len(real['cases'])==17
    assert sum(len(c['context']['source_order']) for c in real['cases'].values())==19
    synthetic=d['synthetic_scene_domains'];assert synthetic['case_order']==['nonexact_geometry_phase_PASS','thin_resolved']
    for audit,valid in ((real,False),(synthetic,True)):
        assert audit['model']==MODEL and audit['inherited_pins_verified']==433 and audit['point_error_reused_as_uniform'] is False
        assert audit['uniform_SOURCE_enclosure_proved'] is False and audit['domain_INPUT_valid_cases']==(2 if valid else 0)
        assert all(audit[k]==0 for k in ('group_admissions','new_native_operations','old_suites_producers_reexecuted'));allfalse(audit)
        assert len(audit['case_order'])==len(set(audit['case_order'])) and set(audit['case_order'])==set(audit['cases'])
        for name,c in audit['cases'].items():
            ctx=old['synthetic_retained' if valid else 'real_missing']['cases'][name]['context']
            assert c['context']==ctx and c['status']=='STOP' and c['uniform_SOURCE_enclosure_proved'] is False
            assert c['uniform_executed_SOURCE_error_L1'] is c['group_field_bound_L1'] is c['group_phase_bound_rad'] is None;allfalse(c)
            domain=c['domain_INPUT'];assert domain['domain_INPUT_valid'] is valid;allfalse(domain)
            if not valid:assert domain['sources'] is None;continue
            plan=d['synthetic_domain_INPUT_plans'][name]
            assert plan['model']==MODEL and plan['units']=='ORIGINAL-SOURCE-field-amplitude' and plan['scope']==domain['scope']
            assert plan['context_sha256']==domain['context_sha256']==digest(ctx) and domain['domain_sha256']==digest(plan)
            assert [s['source_id'] for s in domain['sources']]==ctx['source_order']
            for i,(row,source,a) in enumerate(zip(domain['sources'],plan['sources'],ctx['assignments'])):
                assert all(source[k]==a[k]==row[k] for k in ('source_id','source_phase_reference_id','terminal_reference_id','common_terminal_reference_id'))
                assert row['terminal_reference_id']==row['common_terminal_reference_id']
                words=phases['cases'][name]['sources'][i]['proof']['ORIGINAL_source_uint64']
                center=[F.from_float(struct.unpack('<d',struct.pack('<Q',w))[0]) for w in words]
                assert row['ORIGINAL_source_uint64']==words and row['ORIGINAL_anchor_reim']==list(map(pair,center))
                expected_box=[[pair(x-F(1,1000000)),pair(x+F(1,1000000))] for x in center]
                assert row['box_reim']==source['box_reim']==expected_box
                assert row['uniform_executed_SOURCE_error_L1'] is None and row['uniform_SOURCE_enclosure_proved'] is row['domain_authentication'] is False
                assert row['status']=='STOP';allfalse(row);lemma(row['conditional_geometry'],None)
    controls=d['conditional_controls'];assert len(controls)==4
    for name,v in controls.items():
        eps=[1,10000000000000000] if name in synthetic['cases'] else ([1,10] if name=='negative_components' else [0,1])
        lemma(v,eps)
        if name in synthetic['cases']:assert v['box_reim']==d['synthetic_domain_INPUT_plans'][name]['sources'][0]['box_reim']
    assert controls['negative_components']['amplitude_lower_bound']==[2,1]
    assert controls['axis_zero_component']['conditional_phase_bound_rad']==[0,1]
    lemma(d['origin_box_missing_error'],None);assert d['origin_box_missing_error']['amplitude_lower_bound']==[0,1]
    assert len(d['lemma_rejections'])==11 and len(d['domain_rejections'])==10
    assert r['synthetic_controls_are_real_INPUT'] is False and r['output_fitted_INPUT'] is False and r['JEV_provenance']=='LOCAL'
    print(json.dumps({'PASS':True,'pins':437,'tests':5,'conditional_lemmas':4,'lemma_rejections':11,'domain_rejections':10,
        'anchored_synthetic_domains':2,'REAL_missing_cases':17,'REAL_missing_sources':19,'uniform_SOURCE_error':None,'group_admissions':0,
        'scope':'conditional SOURCE amplitude-box geometry only; no executed uniform error/scene/GPU/RT/physical admission'},sort_keys=True))
if __name__=='__main__':main()
