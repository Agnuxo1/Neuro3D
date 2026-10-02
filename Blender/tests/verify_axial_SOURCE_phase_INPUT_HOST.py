"""Independent receipt/schema oracle, stdlib only, no production imports."""
import base64,hashlib,json,math,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT='coordinacion/respuestas/AXIAL-SOURCE-PHASE-INPUT-HOST-001-CODEX.json'
PARENT='coordinacion/respuestas/AXIAL-PHASE-BUDGET-CONSUMER-HOST-001-CODEX.json'
PARENT_SHA='d5f7bf9ec0f9b724ef1ea65810903312e7cd790900ec5aa92fdfa737fe70af9f'
MODEL='axial-static-SOURCE-principal-phase-INPUT-HOST-v1'
UNITS='SOURCE-principal-phase-distance-rad'
REFERENCE='fixed-ORIGINAL-A-exp-i-theta-times-ideal-minus-one'
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def payload(r):
    t=r['test_run'];s=''.join(t['stdout_zlib_base64_chunks']) if 'stdout_zlib_base64_chunks' in t else t['stdout_zlib_base64']
    b=zlib.decompress(base64.b64decode(s))
    assert len(b)==t['stdout_bytes'] and sha(b)==t['stdout_sha256']
    return json.loads(b)
def main():
    r=json.loads((ROOT/REPORT).read_bytes());b=(ROOT/PARENT).read_bytes();assert sha(b)==PARENT_SHA
    p=json.loads(b);inherited={**p['code_doc_sha256'],PARENT:PARENT_SHA};own=r['own_code_doc_sha256']
    assert len(inherited)==423 and len(own)==4 and not set(inherited)&set(own)
    pins={**inherited,**own};assert len(pins)==427 and r['code_doc_sha256']==pins
    for path,h in pins.items():assert sha((ROOT/path).read_bytes())==h,path
    flags=tuple(r['proof_scope']);assert len(flags)==38 and all(v is False for v in r['proof_scope'].values())
    parent=payload(p)['data'];run=payload(r)
    assert run['PASS'] is True and run['tests']==5
    assert r['test_run']['rc']==0 and r['test_run']['timed_out'] is False and r['test_run']['threads']==1 and r['test_run']['hard_child_timeout_seconds']==60
    d=run['data'];count=0
    for variant,oldvariant,valid,cap in (
        ('real_missing','real_missing',False,None),('explicit_None_missing','real_missing',False,None),
        ('synthetic_valid','synthetic_partial',True,[1,1000000000000]),
        ('synthetic_zero_valid','synthetic_partial',True,[0,1])):
        a=d[variant];old=parent[oldvariant]
        assert a['model']==MODEL and set(a['cases'])==set(old['cases'])
        order=a['case_order'];assert len(order)==len(set(order)) and set(order)==set(a['cases'])
        assert a['SOURCE_phase_policy_adopted'] is False and all(a[k] is False for k in flags)
        assert all(a[k]==0 for k in ('certificate_inspections','numeric_phase_comparisons','group_admissions','new_native_operations','old_suites_producers_reexecuted'))
        assert a['valid_INPUT_cases']==(3 if valid else 0) and a['missing_INPUT_cases']==(0 if valid else 17)
        if not valid:assert sum(len(c['context']['source_order']) for c in a['cases'].values())==19
        for name in order:
            c=a['cases'][name];ctx=old['cases'][name]['context'];v=c['INPUT']
            assert c['context']==ctx and c['status']==v['status']=='STOP' and all(c[k] is False and v[k] is False for k in flags)
            assert v['SOURCE_phase_INPUT_valid'] is valid and v['phase_INPUT_quota_fits'] is None
            if not valid:
                assert v['sources'] is None and 'missing' in v['reason'];continue
            plan=d['synthetic_control_INPUT_plans' if cap[0] else 'synthetic_zero_INPUT_plans'][name]
            assert set(plan)=={'model','units','context_sha256','sources'}
            assert plan['model']==MODEL and plan['units']==UNITS and plan['context_sha256']==v['context_sha256']==digest(ctx)
            assert v['units']==UNITS and v['plan_sha256']==digest(plan) and v['sources']==plan['sources']
            assert [s['source_id'] for s in v['sources']]==ctx['source_order']==[x['source_id'] for x in ctx['assignments']]
            for s,x in zip(v['sources'],ctx['assignments']):
                count+=1
                assert set(s)=={'source_id','source_phase_reference_id','terminal_reference_id','common_terminal_reference_id','reference_model','cap_rad'}
                assert all(type(s[k]) is str and s[k]==x[k] for k in ('source_id','source_phase_reference_id','terminal_reference_id','common_terminal_reference_id'))
                assert s['terminal_reference_id']==s['common_terminal_reference_id'] and s['reference_model']==REFERENCE
                assert s['cap_rad']==cap and type(s['cap_rad']) is list
                assert all(type(n) is int for n in s['cap_rad']) and s['cap_rad'][0]>=0 and s['cap_rad'][1]>0 and math.gcd(*s['cap_rad'])==1
    assert d['real_missing']==d['explicit_None_missing']
    assert len(d['synthetic_valid']['cases']['two_sources']['INPUT']['sources'])==2
    assert len(d['rational_rejections'])==13 and len(d['identity_rejections']['rows'])==13 and len(d['boundary_rejections'])==7
    assert d['identity_rejections']['certificate_inspections']==d['identity_rejections']['numeric_phase_comparisons']==0
    assert r['synthetic_controls_are_real_INPUT'] is False and r['output_fitted_INPUT'] is False and r['JEV_provenance']=='LOCAL'
    print(json.dumps({'PASS':True,'pins':427,'tests':5,'synthetic_source_rows_checked':count,
        'REAL_missing_cases':17,'REAL_missing_sources':19,'invalid_INPUT_rejections':33,
        'SOURCE_phase_numeric_comparison':None,'group_admissions':0,
        'scope':'INPUT syntax/identity only; no real phase policy or certificate/GPU/fullfield admission'},sort_keys=True))
if __name__=='__main__':main()
