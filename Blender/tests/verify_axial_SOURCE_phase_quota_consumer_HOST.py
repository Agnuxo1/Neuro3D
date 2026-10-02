"""Independent SOURCE quota receipt oracle: stdlib exact rational comparison, no production imports."""
import base64,hashlib,json,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT='coordinacion/respuestas/AXIAL-SOURCE-PHASE-QUOTA-CONSUMER-HOST-001-CODEX.json'
PARENT='coordinacion/respuestas/AXIAL-SOURCE-PHASE-INPUT-HOST-001-CODEX.json'
PARENT_SHA='be9f748d4128174357284a1123d89c662c208392ba4d9dfa650f50fe580946f3'
CONSUMER='coordinacion/respuestas/AXIAL-PHASE-BUDGET-CONSUMER-HOST-001-CODEX.json'
PHASE='coordinacion/respuestas/AXIAL-REFLECTED-SOURCE-PHASE-HOST-001-CODEX.json'
BUDGET='coordinacion/respuestas/AXIAL-REFLECTED-SOURCE-BUDGET-BRIDGE-HOST-001-CODEX.json'
MODEL='axial-current-SOURCE-principal-phase-quota-consumer-HOST-v1'
FLAG='point_SOURCE_phase_quota_compared_HOST'
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(x):return sha(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def read(p,h):
    b=(ROOT/p).read_bytes();assert sha(b)==h,p
    return json.loads(b)
def payload(r):
    t=r['test_run'];s=''.join(t['stdout_zlib_base64_chunks']) if 'stdout_zlib_base64_chunks' in t else t['stdout_zlib_base64']
    b=zlib.decompress(base64.b64decode(s));assert sha(b)==t['stdout_sha256'] and len(b)==t['stdout_bytes']
    return json.loads(b)
def main():
    r=json.loads((ROOT/REPORT).read_bytes());p=read(PARENT,PARENT_SHA)
    inherited={**p['code_doc_sha256'],PARENT:PARENT_SHA};own=r['own_code_doc_sha256'];pins={**inherited,**own}
    assert len(inherited)==428 and len(own)==4 and len(pins)==432 and not set(inherited)&set(own) and r['code_doc_sha256']==pins
    for path,h in pins.items():assert sha((ROOT/path).read_bytes())==h,path
    inputs=payload(p)['data'];old=payload(read(CONSUMER,pins[CONSUMER]))['data']
    certs=payload(read(PHASE,pins[PHASE]))['data']['audit'];stage=payload(read(BUDGET,pins[BUDGET]))['data']
    flags=tuple(r['proof_scope']);assert len(flags)==38 and all(v is False for v in r['proof_scope'].values())
    def allfalse(v):assert all(v[k] is False for k in flags)
    run=payload(r);assert run['PASS'] is True and run['tests']==5
    assert r['test_run']['rc']==0 and r['test_run']['threads']==1 and r['test_run']['hard_child_timeout_seconds']==60 and r['test_run']['timed_out'] is False
    d=run['data'];group_count=0
    for v in ('real_missing','explicit_None_missing','synthetic_retained','phase_zero_FAIL','Horner_zero_FAIL','source_zero_FAIL'):
        cv='synthetic_partial' if v in ('synthetic_retained','phase_zero_FAIL') else v
        a=d[v];oc=old[cv];sv=stage[cv]['audit'] if cv in ('Horner_zero_FAIL','source_zero_FAIL') else stage[cv]
        names=sv['case_order'];assert a['case_order']==names and len(names)==len(set(names)) and set(names)==set(a['cases'])==set(oc['cases'])
        assert a['model']==MODEL and a['variant']==v and a['inherited_pins_verified']==428
        assert a['SOURCE_phase_policy_adopted'] is False and all(a[k]==0 for k in ('group_admissions','new_native_operations','old_suites_producers_reexecuted'));allfalse(a)
        comparisons=fits=0
        for name in names:
            c=a['cases'][name];ctx=sv['cases'][name]['context'];pc=certs['cases'][name];prior=oc['cases'][name]
            phasevalid=v not in ('real_missing','explicit_None_missing');stagevalid=sv['cases'][name]['allocation_INPUT']['allocation_INPUT_valid']
            assert c['context']==ctx==pc['context']==prior['context'] and c['stage_INPUT_valid'] is stagevalid and c['status']=='STOP';allfalse(c)
            pv=c['phase_INPUT'];assert pv['SOURCE_phase_INPUT_valid'] is phasevalid and pv['phase_INPUT_quota_fits'] is None and pv['status']=='STOP';allfalse(pv)
            plan=None
            if phasevalid:
                key='synthetic_zero_INPUT_plans' if v=='phase_zero_FAIL' else 'synthetic_control_INPUT_plans'
                plan=inputs[key][name]
                assert pv['plan_sha256']==digest(plan) and pv['context_sha256']==digest(ctx) and pv['sources']==plan['sources'] and pv['units']==plan['units']
                assert plan['model']=='axial-static-SOURCE-principal-phase-INPUT-HOST-v1' and plan['units']=='SOURCE-principal-phase-distance-rad'
                assert [s['source_id'] for s in plan['sources']]==ctx['source_order']
                for s,aa in zip(plan['sources'],ctx['assignments']):
                    assert all(s[k]==aa[k] for k in ('source_id','source_phase_reference_id','terminal_reference_id','common_terminal_reference_id'))
                    assert s['reference_model']=='fixed-ORIGINAL-A-exp-i-theta-times-ideal-minus-one'
                    assert s['cap_rad']==([0,1] if v=='phase_zero_FAIL' else [1,1000000000000])
            else:assert pv['sources'] is None
            assert [s['source_id'] for s in c['sources']]==ctx['source_order']
            for i,s in enumerate(c['sources']):
                cert=pc['sources'][i];available=phasevalid and stagevalid and cert['point_reflected_source_phase_bound_HOST_proved']
                assert s[FLAG] is available and s['status']=='STOP';allfalse(s)
                if available:
                    comparisons+=1;cmp=s['phase_comparison'];bound=cert['proof']['point_principal_phase_distance_bound_rad'];cap=plan['sources'][i]['cap_rad']
                    expected=F(*bound)<=F(*cap);fits+=int(expected)
                    assert cmp['bound_rad']==bound and cmp['cap_rad']==cap and cmp['fits'] is expected and s['phase_INPUT_quota_fits'] is expected
                    assert s['phase_certificate_sha256']==digest(cert) and s['budget']==prior['sources'][i]['budget']
                    assert s['budget']['fifteen_charges_L1']==cert['fifteen_reflected_charges_L1']
                    assert s['budget']['retained_reflection_row_sha256']==cert['retained_reflection_row_sha256']
                else:assert s['phase_certificate_sha256'] is s['phase_comparison'] is s['phase_INPUT_quota_fits'] is s['budget'] is None
            assert len(c['groups'])==len(ctx['groups']);indexed={s['source_id']:s for s in c['sources']};seen=[]
            for (port,gid),g in zip(ctx['groups'],c['groups']):
                group_count+=1;aa=[x for x in ctx['assignments'] if (x['port'],x['coherence_group'])==(port,gid)]
                ss=[x['source_id'] for x in aa];seen+=ss
                assert g['port']==port and g['coherence_group']==gid and g['source_order']==ss and g['SOURCE_phase_INPUT_complete'] is phasevalid
                assert all(x['terminal_reference_id']==x['common_terminal_reference_id']==aa[0]['common_terminal_reference_id'] for x in aa)
                assert g['common_terminal_reference_id']==aa[0]['common_terminal_reference_id']
                unavailable=[s for s in ss if indexed[s]['phase_INPUT_quota_fits'] is None]
                phasefail=[s for s in ss if indexed[s]['phase_INPUT_quota_fits'] is False]
                stagefail=[s for s in ss if indexed[s]['budget'] is not None and not indexed[s]['budget']['partial_seven_stage_comparison_fits']]
                blocks=[]
                if not stagevalid:blocks.append('missing_seven_stage_INPUT')
                if not phasevalid:blocks.append('missing_SOURCE_phase_INPUT')
                if unavailable:blocks.append('incomplete_point_SOURCE_certificates_or_INPUT')
                if phasefail:blocks.append('point_SOURCE_phase_quota_FAIL')
                if stagefail:blocks.append('point_SOURCE_stage_quota_FAIL')
                blocks+=['uniform_SOURCE_enclosure_unproved','reduction_error_unproved','terminal_projection_error_unproved']
                assert g['unavailable_phase_comparison_sources']==unavailable and g['failed_phase_quota_sources']==phasefail and g['failed_stage_quota_sources']==stagefail
                assert g['blockers']==blocks and g['status']=='STOP';allfalse(g)
                reserves=next(x['reserves_L1'] for x in sv['cases'][name]['allocation_INPUT']['groups'] if (x['port'],x['coherence_group'])==(port,gid)) if stagevalid else None
                assert g['INPUT_reserves_L1']==reserves
                for k in ('group_phase_bound_rad','group_field_bound_L1','group_field_uint64','executed_reduction_charge_L1','executed_projection_charge_L1'):assert g[k] is None
            assert sorted(seen)==sorted(ctx['source_order'])
        assert (comparisons,fits)==(a['point_phase_comparisons'],a['point_phase_quota_fits'])
    assert (d['synthetic_retained']['point_phase_comparisons'],d['synthetic_retained']['point_phase_quota_fits'])==(2,2)
    assert (d['phase_zero_FAIL']['point_phase_comparisons'],d['phase_zero_FAIL']['point_phase_quota_fits'])==(2,0)
    assert len(d['real_missing']['cases'])==17 and sum(len(c['sources']) for c in d['real_missing']['cases'].values())==19
    assert all(s['phase_INPUT_quota_fits'] is None for s in d['synthetic_retained']['cases']['two_sources']['sources'])
    for v in ('Horner_zero_FAIL','source_zero_FAIL'):
        row=next(iter(d[v]['cases'].values()))['sources'][0];assert row['phase_INPUT_quota_fits'] is True and row['budget']['partial_seven_stage_comparison_fits'] is False
    assert len(d['INPUT_rejections']['rows'])==8 and d['INPUT_rejections']['certificate_inspections']==d['INPUT_rejections']['numeric_phase_comparisons']==0
    assert len(d['certificate_rejections']['rows'])==10 and d['certificate_rejections']['numeric_phase_comparisons']==0 and len(d['boundary_rejections'])==3
    assert r['synthetic_controls_are_real_INPUT'] is False and r['output_fitted_INPUT'] is False and r['JEV_provenance']=='LOCAL'
    print(json.dumps({'PASS':True,'pins':432,'tests':5,'INPUT_rejections':8,'certificate_rejections':10,'boundary_rejections':3,
        'CONTROL_point_phase_fits':2,'zero_quota_FAIL':2,'REAL_missing_cases':17,'REAL_missing_sources':19,
        'groups_checked':group_count,'group_admissions':0,'old_Horner_sourcecap_FAIL_preserved':True,
        'scope':'HOST immutable SOURCE phase quota join; no uniform/group/GPU/RT/physical admission'},sort_keys=True))
if __name__=='__main__':main()
