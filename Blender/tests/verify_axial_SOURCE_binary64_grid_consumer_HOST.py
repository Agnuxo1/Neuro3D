"""Independent stdlib492pin INPUT/sealed-certificate consumer audit; no production imports."""
import base64,hashlib,json,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT='coordinacion/respuestas/AXIAL-SOURCE-BINARY64-GRID-CONSUMER-HOST-001-CODEX.json'
PARENT='coordinacion/respuestas/AXIAL-SOURCE-BINARY64-GRID-INPUT-HOST-001-CODEX.json'
PARENT_SHA='3eb8e18e7740f7448d92a9e459427ad3a2dd28e58d73c7f950c75417a3db94ff'
CERT='coordinacion/respuestas/AXIAL-SOURCE-BINARY64-ENCODER-WORDCLASS-HOST-001-CODEX.json'
CERT_SHA='78249147dca45e62cf0ae1e4e9a87cb774f3e000a07da5d6ec81d47d8cb5f748'
DOMAIN='coordinacion/respuestas/AXIAL-SOURCE-DOMAIN-PHASE-INPUT-HOST-001-CODEX.json'
MODEL='axial-SOURCE-binary64-grid-INPUT-retained-wordclass-consumer-HOST-v1'
BOUND='retained_wordclass_certificate_bound_to_GRID_INPUT_HOST'
SUFFICIENT='conditional_encoder_numeric_wordclasses_sufficient_HOST'
OLD_FLAG='sufficient_numeric_encoder_wordclasses_under_explicit_binary64_grid_HOST'
INPUT_FLAG='SOURCE_binary64_grid_INPUT_bound_HOST'
INSPECT_KEYS={'source_id','domain_source_sha256','GRID_INPUT_source_sha256','retained_SOURCE_certificate_sha256',
              'retained_component_certificate_sha256','component_sufficient_flags',SUFFICIENT,
              'retained_whole_box_guard_admission_disproved','scope'}
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def payload(r):
    t=r['test_run'];b=zlib.decompress(base64.b64decode(''.join(t['stdout_zlib_base64_chunks']),validate=True))
    assert len(b)==t['stdout_bytes'] and sha(b)==t['stdout_sha256'];return json.loads(b)
def main():
    r=json.loads((ROOT/REPORT).read_bytes());b=(ROOT/PARENT).read_bytes();assert sha(b)==PARENT_SHA
    p=json.loads(b);inherited={**p['code_doc_sha256'],PARENT:PARENT_SHA};own=r['own_code_doc_sha256']
    pins={**inherited,**own};assert len(inherited)==488 and len(own)==4 and len(pins)==492 and not set(inherited)&set(own)
    assert r['code_doc_sha256']==pins
    for path,h in pins.items():assert sha((ROOT/path).read_bytes())==h,path
    assert r['task_id']=='AXIAL-SOURCE-BINARY64-GRID-CONSUMER-HOST-001' and r['model']==MODEL
    assert r['base_commit']=='79e6a201c3e71c55ea5cc560b4b1e44ae966832b'
    cb=(ROOT/CERT).read_bytes();assert sha(cb)==CERT_SHA
    certs=payload(json.loads(cb))['data'];grid=payload(p)['data'];inputs=payload(json.loads((ROOT/DOMAIN).read_bytes()))['data']
    run=payload(r);d=run['data'];assert run['tests']==5 and run['PASS'] is True
    t=r['test_run'];assert t['rc']==0 and t['timed_out'] is False and t['threads']==t['affinity_mask']==1 and t['hard_child_timeout_seconds']==60
    flags=tuple(r['proof_scope']);assert len(flags)==38 and all(v is False for v in r['proof_scope'].values())
    def nf(x):assert all(x[k] is False for k in flags)
    for variant in ('real_missing','explicit_None_missing','domain_present_grid_missing','synthetic_valid'):
        audit=d[variant];base=grid[variant];present=variant=='synthetic_valid'
        withdom=variant in ('domain_present_grid_missing','synthetic_valid')
        nf(audit);assert audit['model']==MODEL and audit['variant']==variant
        assert audit['case_order']==base['case_order'] and set(audit['cases'])==set(base['cases'])
        assert audit['inherited_pins_verified']==488
        assert audit['new_wordclass_predicates']==audit['new_native_operations']==audit['old_suites_producers_reexecuted']==audit['old_counterexamples_reexecuted']==audit['group_admissions']==0
        assert audit['actual_scene_domain_grid_authenticated'] is audit['encoder_graph_execution_authenticated'] is False
        count=sufficient=negative=0
        for name in audit['case_order']:
            case=audit['cases'][name];ctx=case['context'];v=case['GRID_INPUT']
            nf(case);nf(v)
            assert digest(ctx)==digest(base['cases'][name]['context'])==digest(certs['synthetic_valid' if withdom else 'real_missing']['cases'][name]['context'])
            assert digest(v)==digest(base['cases'][name]['INPUT']) and case['status']=='STOP'
            assert case['group_field_bound_L1'] is case['group_phase_bound_rad'] is None
            if not present:
                assert v[INPUT_FLAG] is False and case['sources'] is None;continue
            assert v[INPUT_FLAG] is True
            dom=inputs['synthetic_validated_domains'][name];original=certs['synthetic_valid']['cases'][name]['sources']
            assert [s['source_id'] for s in case['sources']]==ctx['source_order']
            assert len(case['sources'])==len(dom['sources'])==len(v['sources'])==len(original)
            for row,src,g,cert in zip(case['sources'],dom['sources'],v['sources'],original):
                nf(row)
                assert set(row)==INSPECT_KEYS|{BOUND,'model','actual_scene_domain_grid_authenticated','encoder_graph_execution_authenticated',
                     'frozen_guard_admission_for_entire_box_proved','uniform_executed_SOURCE_error_L1','phase_INPUT_quota_fits','status'}|set(flags)
                assert row['source_id']==src['source_id']==g['source_id']==cert['source_id']
                assert row['domain_source_sha256']==g['domain_source_sha256']==cert['domain_source_sha256']==digest(src)
                assert g['ORIGINAL_source_uint64']==src['ORIGINAL_source_uint64']
                assert row['GRID_INPUT_source_sha256']==digest(g)
                assert row['retained_SOURCE_certificate_sha256']==digest(cert)
                comps=cert['components'];assert len(comps)==2
                assert row['retained_component_certificate_sha256']==list(map(digest,comps))
                vals=[c[OLD_FLAG] for c in comps];assert all(type(f) is bool for f in vals)
                assert row['component_sufficient_flags']==vals and row[SUFFICIENT] is cert[OLD_FLAG] is all(vals)
                for comp,interval in zip(comps,src['box_reim']):
                    nf(comp);assert comp['interval']==interval
                    assert comp['model']=='axial-SOURCE-binary64-grid-encoder-normal-or-zero-sufficient-HOST-v1'
                    assert comp['explicit_grid_assumption']==v['grid'] and comp['arithmetic_model']==v['arithmetic_model']
                    assert (comp['proof'] is not None) is comp[OLD_FLAG]
                    # Proof rational content is SEALED by the entire component digest, not regenerated.
                    assert comp['actual_scene_domain_grid_authenticated'] is comp['all_real_continuum_wordclasses_proved'] is comp['frozen_guard_admission_for_entire_box_proved'] is comp['signed_zero_execution_policy_proved'] is comp['SOURCE_graph_executed'] is False
                    assert comp['frozen_guard_verdict'] is comp['uniform_executed_SOURCE_error_L1'] is None
                assert row['retained_whole_box_guard_admission_disproved'] is cert['retained_whole_box_guard_admission_disproved']
                if cert['retained_whole_box_guard_admission_disproved'] is True:
                    negative+=1;assert vals==[True,False] and row[SUFFICIENT] is False
                else:
                    assert cert['retained_whole_box_guard_admission_disproved'] is None and name=='two_sources'
                    assert row[SUFFICIENT] is True
                assert row[BOUND] is True and row['model']==MODEL and row['status']=='STOP'
                assert row['actual_scene_domain_grid_authenticated'] is row['encoder_graph_execution_authenticated'] is row['frozen_guard_admission_for_entire_box_proved'] is False
                assert row['uniform_executed_SOURCE_error_L1'] is row['phase_INPUT_quota_fits'] is None
                count+=1;sufficient+=int(row[SUFFICIENT])
        assert audit['retained_SOURCE_certificate_inspections']==audit['bound_SOURCE_certificates']==count==(4 if present else 0)
        assert audit['conditional_sufficient_SOURCE_count']==sufficient==(2 if present else 0)
        assert audit['retained_negative_guard_SOURCE_count']==negative==(2 if present else 0)
    assert d['real_missing']['cases']==d['explicit_None_missing']['cases']
    assert len(d['real_missing']['cases'])==17 and sum(len(x['context']['source_order']) for x in d['real_missing']['cases'].values())==19
    assert len(d['INPUT_rejections'])==6 and len(d['certificate_rejections'])==11 and len(d['model_lineage_rejections'])==3
    assert r['actual_scene_domain_grid_authenticated'] is r['encoder_graph_execution_authenticated'] is r['frozen_guard_admission_for_entire_box_proved'] is False
    assert r['group_admissions']==0 and r['uniform_executed_SOURCE_error_L1'] is r['phase_INPUT_quota_fits'] is None
    assert r['JEV_provenance']=='LOCAL' and r['synthetic_controls_are_real_INPUT'] is r['output_fitted_INPUT'] is False
    print(json.dumps({'PASS':True,'pins':492,'tests':5,'bound_SOURCE_certificates':4,'conditional_sufficient_SOURCE_count':2,
        'retained_negative_guard_SOURCE_count':2,'REAL_missing_cases':17,'REAL_missing_sources':19,
        'INPUT_cert_model_rejections':20,'new_predicates':0,'group_admissions':0,
        'scope':'sealed certificate + explicit GRID INPUT only; actual scene/guard/execution STOP'},sort_keys=True))
if __name__=='__main__':main()
