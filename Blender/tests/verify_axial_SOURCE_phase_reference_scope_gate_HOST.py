"""Independent stdlib reference-scope oracle; no production imports or old suites."""
import base64,hashlib,json,math,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT='coordinacion/respuestas/AXIAL-SOURCE-PHASE-REFERENCE-SCOPE-GATE-HOST-001-CODEX.json'
PARENT='coordinacion/respuestas/AXIAL-SOURCE-UNIFORM-IDEAL-REFLECTION-PHASE-HOST-001-CODEX.json'
PARENT_SHA='dbadfe64901a5608064f76de805d1f89aef5349404333998d2556e990fb484c0'
POINT='coordinacion/respuestas/AXIAL-SOURCE-PHASE-QUOTA-CONSUMER-HOST-001-CODEX.json'
INPUT='coordinacion/respuestas/AXIAL-SOURCE-PHASE-INPUT-HOST-001-CODEX.json'
AMP='coordinacion/respuestas/AXIAL-SOURCE-AMPLITUDE-DISK-BOX-HOST-001-CODEX.json'
MODEL='axial-SOURCE-phase-fixed-anchor-vs-variable-box-reference-scope-gate-HOST-v1'
FLAG='SOURCE_phase_reference_scope_assessed_HOST'
REFERENCE='fixed-ORIGINAL-A-exp-i-theta-times-ideal-minus-one'
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(x):return sha(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def rat(x):
    assert type(x) is list and len(x)==2 and all(type(n) is int and n.bit_length()<=4096 for n in x)
    assert x[1]>0 and math.gcd(*x)==1;return F(*x)
def payload(r):
    t=r['test_run'];b=zlib.decompress(base64.b64decode(''.join(t['stdout_zlib_base64_chunks'])))
    assert len(b)==t['stdout_bytes'] and sha(b)==t['stdout_sha256'];return json.loads(b)
def main():
    r=json.loads((ROOT/REPORT).read_bytes());b=(ROOT/PARENT).read_bytes();assert sha(b)==PARENT_SHA;p=json.loads(b)
    inherited={**p['code_doc_sha256'],PARENT:PARENT_SHA};own=r['own_code_doc_sha256'];pins={**inherited,**own}
    assert len(inherited)==463 and len(own)==4 and len(pins)==467 and r['code_doc_sha256']==pins and not set(inherited)&set(own)
    for path,h in pins.items():assert sha((ROOT/path).read_bytes())==h,path
    assert r['task_id']=='AXIAL-SOURCE-PHASE-REFERENCE-SCOPE-GATE-HOST-001' and r['model']==MODEL and r['base_commit']=='5342795f3f2fa856f1eddbddfdbffa9fcd8bf4a2'
    run=payload(r);certs=payload(p)['data']
    assert len(r['failed_test_runs'])==1
    failed=r['failed_test_runs'][0];failed_payload=payload({'test_run':failed})
    assert failed['rc']==1 and failed['timed_out'] is False and failed_payload['tests']==5 and failed_payload['PASS'] is False
    assert 'FAILED (failures=2)' in failed['stderr']
    for snapshot in r['initial_source_snapshots'].values():assert sha(snapshot['utf8_source'].encode())==snapshot['sha256']
    def data(path):return payload(json.loads((ROOT/path).read_bytes()))['data']
    point,inputs,amp=data(POINT),data(INPUT),data(AMP)
    assert run['tests']==5 and run['PASS'] is True
    t=r['test_run'];assert t['rc']==0 and not t['timed_out'] and t['threads']==t['affinity_mask']==1 and t['hard_child_timeout_seconds']==60
    flags=tuple(r['proof_scope']);assert len(flags)==38 and all(v is False for v in r['proof_scope'].values())
    def nf(x):assert all(x[k] is False for k in flags)
    def scope(x,src,plan):
        intervals=[(rat(lo),rat(hi)) for lo,hi in src['box_reim']];anchor=list(map(rat,src['ORIGINAL_anchor_reim']))
        assert len(anchor)==2 and all(lo<=a<=hi for a,(lo,hi) in zip(anchor,intervals))
        singleton=all(lo==a==hi for a,(lo,hi) in zip(anchor,intervals))
        assert x['model']==MODEL and x[FLAG] is True and x['source_id']==src['source_id']==plan['source_id']
        assert x['domain_source_sha256']==digest(src) and x['phase_INPUT_source_sha256']==digest(plan)
        assert x['retained_reference_model']==plan['reference_model']==REFERENCE
        assert x['box_is_exact_ORIGINAL_anchor_singleton'] is singleton and x['uniform_reference_scope_supported_by_retained_INPUT'] is singleton
        assert x['anchor_quota_retained_cap_rad']==plan['cap_rad'] and rat(plan['cap_rad'])>=0
        assert x['comparison_performed'] is x['SOURCE_phase_policy_adopted'] is False and x['uniform_phase_INPUT_quota_fits'] is None
        assert x['status']=='STOP';nf(x)
    for variant in ('real_missing','explicit_None_missing','synthetic_retained','phase_zero_FAIL','Horner_zero_FAIL','source_zero_FAIL'):
        a=run['data'][variant];old=point[variant];absent=variant in ('real_missing','explicit_None_missing')
        assert a['model']==MODEL and a['variant']==variant and a['case_order']==old['case_order'] and a['inherited_pins_verified']==463
        expected=0 if absent else (2 if variant in ('synthetic_retained','phase_zero_FAIL') else 1)
        assert a['reference_scope_assessments']==a['blocked_variable_box_quota_scopes']==expected
        assert a['new_numeric_phase_comparisons']==a['new_native_operations']==a['old_suites_producers_reexecuted']==a['group_admissions']==0 and a['SOURCE_phase_policy_adopted'] is False;nf(a)
        failed_stage=failed_point_phase=0
        for name in a['case_order']:
            c=a['cases'][name];oc=old['cases'][name]
            assert c['context']==oc['context'] and digest(c['phase_INPUT'])==digest(oc['phase_INPUT'])
            assert c['retained_point_consumer_case_sha256']==digest(oc) and c['status']=='STOP'
            assert c['group_phase_bound_rad'] is c['group_field_bound_L1'] is None;nf(c)
            if absent:assert c['sources'] is None;continue
            assert len(c['sources'])==len(oc['sources'])
            for x,o in zip(c['sources'],oc['sources']):
                assert x['source_id']==o['source_id'] and x['retained_point_consumer_source_sha256']==digest(o) and digest(x['retained_point_consumer'])==digest(o)
                assert x['uniform_phase_comparison'] is x['uniform_phase_INPUT_quota_fits'] is None and x['status']=='STOP';nf(x)
                failed_point_phase+=int(o['phase_INPUT_quota_fits'] is False)
                failed_stage+=int(o['budget'] is not None and o['budget']['partial_seven_stage_comparison_fits'] is False)
                if x['scope'] is None:assert x['conditional_phase_SOURCE_sha256'] is None;continue
                src=next(s for s in amp['synthetic_scene_domains']['cases'][name]['domain_INPUT']['sources'] if s['source_id']==x['source_id'])
                cert=next(s for s in certs['synthetic_domains']['cases'][name]['sources'] if s['source_id']==x['source_id'])
                plan=next(s for s in c['phase_INPUT']['sources'] if s['source_id']==x['source_id'])
                assert x['conditional_phase_SOURCE_sha256']==digest(cert)
                scope(x['scope'],src,plan);assert x['scope']['uniform_reference_scope_supported_by_retained_INPUT'] is False
        if variant in ('Horner_zero_FAIL','source_zero_FAIL'):assert failed_stage>0
        if variant=='phase_zero_FAIL':assert failed_point_phase>0
    controls=run['data']['scope_controls'];sources=run['data']['scope_control_sources'];plan=run['data']['scope_control_phase_INPUT']
    assert len(controls)==3 and controls['singleton']['uniform_reference_scope_supported_by_retained_INPUT'] is True
    for n,x in controls.items():scope(x,sources[n],plan)
    assert len(run['data']['typed_reference_rejections'])==6 and len(run['data']['INPUT_SHA_rejections'])==6
    print(json.dumps({'PASS':True,'pins':len(pins),'blocked_box_scopes_CONTROL_orders':[2,2,1,1],'new_phase_comparisons':0,'historical_POINT_and_stage_FAILs_unchanged':True,'group_admissions':0},sort_keys=True))
if __name__=='__main__':main()
