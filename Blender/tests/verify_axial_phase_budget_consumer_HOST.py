"""Independent immutable receipt join oracle; no production imports or suite replay."""
import base64,hashlib,json,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT='coordinacion/respuestas/AXIAL-PHASE-BUDGET-CONSUMER-HOST-001-CODEX.json'
PARENT='coordinacion/respuestas/AXIAL-REFLECTED-SOURCE-PHASE-HOST-001-CODEX.json'
PARENT_SHA='07ba59c6be5378d6692ef1dad39866a3fd3a0e94353994080fe32421e8032df5'
BUDGET='coordinacion/respuestas/AXIAL-REFLECTED-SOURCE-BUDGET-BRIDGE-HOST-001-CODEX.json'
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(x):return sha(json.dumps(x,sort_keys=True,separators=(',',':')).encode())
def read(p,h):
    b=(ROOT/p).read_bytes();assert sha(b)==h,p
    return json.loads(b)
def payload(r):
    t=r['test_run'];s=''.join(t['stdout_zlib_base64_chunks']) if 'stdout_zlib_base64_chunks' in t else t['stdout_zlib_base64']
    b=zlib.decompress(base64.b64decode(s));assert sha(b)==t['stdout_sha256'] and len(b)==t['stdout_bytes']
    return json.loads(b)
def main():
    r=json.loads((ROOT/REPORT).read_bytes());p=read(PARENT,PARENT_SHA)
    inherited={**p['code_doc_sha256'],PARENT:PARENT_SHA};own=r['own_code_doc_sha256']
    pins={**inherited,**own};assert not set(inherited)&set(own)
    assert len(inherited)==418 and len(own)==4 and len(pins)==422 and r['code_doc_sha256']==pins
    for path,h in pins.items():assert sha((ROOT/path).read_bytes())==h,path
    flags=tuple(r['proof_scope']);assert len(flags)==38 and all(x is False for x in r['proof_scope'].values())
    def allfalse(v):assert all(v[k] is False for k in flags)
    phases=payload(p)['data']['audit'];budget=payload(read(BUDGET,pins[BUDGET]))['data']
    run=payload(r);assert run['PASS'] is True and run['tests']==4
    data=run['data'];consumed=fits=groups=0
    flag='point_SOURCE_phase_certificate_consumed_HOST'
    for variant in ('real_missing','synthetic_partial','Horner_zero_FAIL','source_zero_FAIL','explicit_None_missing'):
        old=budget[variant]['audit'] if variant in ('Horner_zero_FAIL','source_zero_FAIL') else budget[variant]
        a=data[variant];assert a['variant']==variant and a['model']=='axial-current-SOURCE-phase-retained-seven-quota-consumer-HOST-v1'
        assert a['inherited_pins_verified']==418 and a['group_admissions']==a['new_native_operations']==a['old_suites_producers_reexecuted']==0
        assert a['phase_INPUT_policy_adopted'] is False;allfalse(a)
        assert set(a['cases'])==set(old['cases'])
        count=fit=0
        for name,c in a['cases'].items():
            oc=old['cases'][name];ctx=oc['context'];valid=oc['allocation_INPUT'];pc=phases['cases'][name]
            assert c['context']==ctx==pc['context'] and c['allocation_INPUT_valid'] is valid['allocation_INPUT_valid']
            assert c['status']=='STOP';allfalse(c)
            assert [row['source_id'] for row in c['sources']]==ctx['source_order']
            for i,row in enumerate(c['sources']):
                cert=pc['sources'][i];allfalse(row)
                assert row['phase_certificate_sha256']==digest(cert) and row['phase_INPUT_quota_fits'] is None and row['status']=='STOP'
                available=valid['allocation_INPUT_valid'] and cert['point_reflected_source_phase_bound_HOST_proved']
                assert row[flag] is available
                if available:
                    count+=1
                    assert row['point_principal_phase_bound_rad']==cert['proof']['point_principal_phase_distance_bound_rad']
                    assert row['budget']==oc['sources'][i] # EXACT retained seven-quota comparison, no re-fit or fresh output-derived INPUT
                    assert row['budget']['retained_reflection_row_sha256']==cert['retained_reflection_row_sha256']
                    assert row['budget']['fifteen_charges_L1']==cert['fifteen_reflected_charges_L1']
                    fit+=int(row['budget']['partial_seven_stage_comparison_fits'])
                else:
                    assert row['budget'] is row['point_principal_phase_bound_rad'] is None
            assert len(c['groups'])==len(ctx['groups']);indexed={row['source_id']:row for row in c['sources']};seen=[]
            for (port,gid),g in zip(ctx['groups'],c['groups']):
                groups+=1
                aa=[x for x in ctx['assignments'] if (x['port'],x['coherence_group'])==(port,gid)]
                ss=[x['source_id'] for x in aa];seen+=ss
                assert g['port']==port and g['coherence_group']==gid and g['source_order']==ss
                assert all(x['terminal_reference_id']==x['common_terminal_reference_id']==aa[0]['common_terminal_reference_id'] for x in aa)
                assert g['common_terminal_reference_id']==aa[0]['common_terminal_reference_id']
                av=[s for s in ss if indexed[s][flag]];miss=[s for s in ss if not indexed[s][flag]]
                fail=[s for s in ss if indexed[s][flag] and not indexed[s]['budget']['partial_seven_stage_comparison_fits']]
                assert g['phase_certificate_sources']==av and g['missing_source_certificates']==miss and g['failed_point_source_quotas']==fail
                res=None;blocks=[]
                if valid['allocation_INPUT_valid']:
                    res=next(x['reserves_L1'] for x in valid['groups'] if (x['port'],x['coherence_group'])==(port,gid))
                else:blocks.append('missing_source_stage_INPUT')
                if miss:blocks.append('incomplete_source_phase_and_point_stages')
                if fail:blocks.append('source_point_stage_quota_FAIL')
                blocks+=['missing_explicit_SOURCE_phase_INPUT','reduction_error_unproved','terminal_projection_error_unproved']
                assert g['INPUT_reserves_L1']==res and g['blockers']==blocks and g['status']=='STOP';allfalse(g)
                for key in ('phase_INPUT_quota_fits','group_phase_bound_rad','group_field_bound_L1','group_field_uint64','executed_reduction_charge_L1','executed_projection_charge_L1'):assert g[key] is None
            assert sorted(seen)==sorted(ctx['source_order'])
        assert (count,fit)==(a['certificates_consumed'],a['partial_seven_stage_fits'])
        consumed+=count;fits+=fit
    assert len(data['real_missing']['cases'])==17 and sum(len(c['sources']) for c in data['real_missing']['cases'].values())==19
    assert (data['synthetic_partial']['certificates_consumed'],data['synthetic_partial']['partial_seven_stage_fits'])==(2,2)
    assert data['Horner_zero_FAIL']['partial_seven_stage_fits']==data['source_zero_FAIL']['partial_seven_stage_fits']==0
    assert len(data['INPUT_rejections']['rows'])==5 and data['INPUT_rejections']['certificate_inspection_calls']==0
    assert len(data['certificate_identity_rejections']['rows'])==10 and data['certificate_identity_rejections']['budget_compare_calls']==0
    print(json.dumps({'PASS':True,'pins':len(pins),'groups_checked':groups,'CONTROL_certificates_consumed':2,'CONTROL_partial_stage_fits':2,
        'REAL_INPUT_missing_cases':17,'REAL_STOP_sources':19,'old_Horner_sourcecap_FAILs_retained':True,
        'phase_INPUT_quota':None,'group_admissions':0,'scope':'HOST immutable point join; no phase INPUT/reduction/projection/fullfield/native/GPU/RT/physical admission'},sort_keys=True))
if __name__=='__main__':main()
