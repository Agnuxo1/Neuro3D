"""Independent stdlib receipt oracle; no imports or old native suites."""
import base64,hashlib,json,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT='coordinacion/respuestas/AXIAL-GROUP-PREREQUISITES-HOST-001-CODEX.json'
PARENT='coordinacion/respuestas/AXIAL-REFLECTED-SOURCE-BUDGET-BRIDGE-HOST-001-CODEX.json'
PARENT_SHA='06d974cf7d7ab792377aef9d67d6ca2fcaf301a8932237a05eab5277018cd384'
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(x):return sha(json.dumps(x,sort_keys=True,separators=(',',':')).encode())
def read(p,h):
    b=(ROOT/p).read_bytes();assert sha(b)==h,p
    return json.loads(b)
def payload(r):
    t=r['test_run'];chunks=t.get('stdout_zlib_base64_chunks')
    b=zlib.decompress(base64.b64decode(''.join(chunks) if chunks else t['stdout_zlib_base64']))
    assert sha(b)==t['stdout_sha256'] and len(b)==t['stdout_bytes']
    return json.loads(b)
def main():
    r=json.loads((ROOT/REPORT).read_bytes());pr=read(PARENT,PARENT_SHA)
    inherited={**pr['code_doc_sha256'],PARENT:PARENT_SHA};own=r['own_code_doc_sha256']
    assert len(inherited)==408 and len(own)==4 and not set(own)&set(inherited)
    pins={**inherited,**own};assert pins==r['code_doc_sha256'] and len(pins)==412
    for p,h in pins.items():assert sha((ROOT/p).read_bytes())==h,p
    flags=tuple(r['proof_scope']);assert len(flags)==38 and all(x is False for x in r['proof_scope'].values())
    def allfalse(x):assert all(x[k] is False for k in flags)
    parent=payload(pr)['data'];run=payload(r);assert run['PASS'] is True and run['tests']==4
    data=run['data'];groups=points=0
    for variant in ('real_missing','synthetic_partial','Horner_zero_FAIL','source_zero_FAIL','explicit_None_missing'):
        old=parent[variant]['audit'] if variant in ('Horner_zero_FAIL','source_zero_FAIL') else parent[variant]
        a=data[variant];assert a['model']=='axial-current-reflected-group-prerequisites-HOST-v1'
        assert a['variant']==variant and a['inherited_pins_verified']==408
        assert a['ready_groups']==a['new_native_operations']==a['old_producers_suites_reexecuted']==0;allfalse(a)
        assert set(a['cases'])==set(old['cases'])
        for name,c in a['cases'].items():
            oc=old['cases'][name];ctx=oc['context'];valid=oc['allocation_INPUT']
            assert c['context_sha256']==digest(ctx) and c['retained_case_sha256']==digest(oc)
            assert c['allocation_INPUT_valid'] is valid['allocation_INPUT_valid'] and c['status']=='STOP';allfalse(c)
            assert len(c['groups'])==len(ctx['groups'])
            seen=[]
            for (port,gid),g in zip(ctx['groups'],c['groups']):
                groups+=1;members=[x for x in ctx['assignments'] if (x['port'],x['coherence_group'])==(port,gid)]
                ss=[x['source_id'] for x in members];seen+=ss
                assert members and len(ss)==len(set(ss))
                assert all(x['common_terminal_reference_id']==x['terminal_reference_id']==members[0]['common_terminal_reference_id'] for x in members)
                assert g['source_order']==ss and g['port']==port and g['coherence_group']==gid
                assert g['common_terminal_reference_id']==members[0]['common_terminal_reference_id']
                rows={x['source_id']:x for x in oc['sources']};assert set(rows)==set(ctx['source_order'])
                missing=[s for s in ss if rows[s]['stage_comparisons'] is None]
                failing=[s for s in ss if rows[s]['stage_comparisons'] is not None and not rows[s]['partial_seven_stage_comparison_fits']]
                fits=[s for s in ss if rows[s]['partial_seven_stage_comparison_fits']]
                points+=len(fits);assert g['missing_point_sources']==missing and g['failed_point_sources']==failing and g['point_fit_sources']==fits
                reserve=None;blockers=[]
                if valid['allocation_INPUT_valid']:
                    reserve=next(x['reserves_L1'] for x in valid['groups'] if (x['port'],x['coherence_group'])==(port,gid))
                else:blockers.append('missing_explicit_source_and_stage_INPUT')
                if missing:blockers.append('incomplete_retained_reflected_point_stages')
                if failing:blockers.append('retained_point_stage_quota_FAIL')
                blockers+=['source_phase_proof_absent','reduction_error_unproved','terminal_projection_error_unproved']
                assert g['INPUT_reserves_L1']==reserve and g['blockers']==blockers and g['source_phase_missing']==ss
                assert g['readiness']=='STOP';allfalse(g)
                for k in ('executed_reduction_charge_L1','executed_terminal_projection_charge_L1','group_field_L1_bound','group_field_uint64'):assert g[k] is None
            assert sorted(seen)==sorted(ctx['source_order'])
    assert len(data['real_missing']['cases'])==17
    assert sum(len(g['source_order']) for c in data['real_missing']['cases'].values() for g in c['groups'])==19
    assert points==2
    assert len(data['atomic_rejections']['rows'])==11 and data['atomic_rejections']['group_report_calls']==0
    assert len(data['identity_rejections'])==5
    initial=r['initial_failure'];assert initial['rc']==1 and 'same retained budget audit' in initial['stderr']
    b=zlib.decompress(base64.b64decode(initial['stdout_zlib_base64']))
    assert sha(b)==initial['stdout_sha256'] and len(b)==initial['stdout_bytes']
    assert json.loads(b)['PASS'] is False
    assert r['failure_repair']=='Use explicit unique complete case_order; JSON key ordering is not semantic ordering. No quota or acceptance threshold change.'
    print(json.dumps({'PASS':True,'pins':len(pins),'groups_checked':groups,'partial_point_fits':points,
        'ready_groups':0,'real_missing_cases':17,'real_missing_sources':19,'atomic_rejections':11,'identity_rejections':5,
        'scope':'HOST prerequisites only; SOURCE phase and reduction/projection absent; no group bound/field/native/GPU/physical claim'},sort_keys=True))
if __name__=='__main__':main()
