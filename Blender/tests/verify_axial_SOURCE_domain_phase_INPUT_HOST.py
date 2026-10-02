"""Independent stdlib INPUT/domain-binding receipt oracle; no production imports."""
import base64,hashlib,json,math,struct,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT='coordinacion/respuestas/AXIAL-SOURCE-DOMAIN-PHASE-INPUT-HOST-001-CODEX.json'
PARENT='coordinacion/respuestas/AXIAL-SOURCE-PHASE-REFERENCE-SCOPE-GATE-HOST-001-CODEX.json'
PARENT_SHA='a3d8a1d5d4a9b59f8c5d38a265f965576afb14d84d5f5f2dd0e8fd669eabf34e'
AMP='coordinacion/respuestas/AXIAL-SOURCE-AMPLITUDE-DISK-BOX-HOST-001-CODEX.json'
INPUT='coordinacion/respuestas/AXIAL-SOURCE-PHASE-INPUT-HOST-001-CODEX.json'
MODEL='axial-variable-A-domain-SOURCE-principal-phase-INPUT-HOST-v1'
DOMAIN_MODEL='axial-ORIGINAL-SOURCE-amplitude-box-conditional-disk-HOST-v1'
UNITS='SOURCE-principal-phase-distance-rad'
REFERENCE='variable-ORIGINAL-A-in-declared-box-exp-i-fixed-ORIGINAL-theta-times-ideal-minus-one'
SCOPE='SOURCE_field_reim_only; fixed ORIGINAL geometry/wavelength/path/material/gauges'
FLAG='SOURCE_domain_phase_INPUT_valid_HOST'
GAUGES=('source_id','source_phase_reference_id','terminal_reference_id','common_terminal_reference_id')
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def pair(x):return [x.numerator,x.denominator]
def rat(x):
    assert type(x) is list and len(x)==2 and all(type(n) is int and n.bit_length()<=4096 for n in x)
    assert x[1]>0 and math.gcd(*x)==1;return F(*x)
def bits(w):
    assert type(w) is int and 0<=w<2**64
    x=struct.unpack('<d',struct.pack('<Q',w))[0];assert math.isfinite(x);return F.from_float(x)
def payload(r):
    t=r['test_run'];b=zlib.decompress(base64.b64decode(''.join(t['stdout_zlib_base64_chunks'])))
    assert len(b)==t['stdout_bytes'] and sha(b)==t['stdout_sha256'];return json.loads(b)
def main():
    r=json.loads((ROOT/REPORT).read_bytes());b=(ROOT/PARENT).read_bytes();assert sha(b)==PARENT_SHA
    p=json.loads(b);inherited={**p['code_doc_sha256'],PARENT:PARENT_SHA};own=r['own_code_doc_sha256']
    assert len(inherited)==468 and len(own)==4 and not set(inherited)&set(own)
    pins={**inherited,**own};assert len(pins)==472 and r['code_doc_sha256']==pins
    for path,h in pins.items():assert sha((ROOT/path).read_bytes())==h,path
    assert r['task_id']=='AXIAL-SOURCE-DOMAIN-PHASE-INPUT-HOST-001' and r['model']==MODEL
    assert r['base_commit']=='228f4ab899e6808e6fbe93ee655ea1a62d7b2430'
    run=payload(r);assert run['tests']==5 and run['PASS'] is True
    assert len(r['failed_test_runs'])==1
    failed=r['failed_test_runs'][0];f=payload({'test_run':failed})
    assert failed['rc']==1 and failed['timed_out'] is False and f['tests']==5 and f['PASS'] is False
    assert 'expected rejection oversized' in failed['stderr'] and 'FAILED (failures=1)' in failed['stderr']
    for s in r['initial_source_snapshots'].values():assert sha(s['utf8_source'].encode())==s['sha256']
    t=r['test_run'];assert t['rc']==0 and t['timed_out'] is False and t['threads']==t['affinity_mask']==1 and t['hard_child_timeout_seconds']==60
    flags=tuple(r['proof_scope']);assert len(flags)==38 and all(v is False for v in r['proof_scope'].values())
    def nf(x):assert all(x[k] is False for k in flags)
    def data(path):return payload(json.loads((ROOT/path).read_bytes()))['data']
    amp,old=data(AMP),data(INPUT);d=run['data']
    names=list(amp['synthetic_domain_INPUT_plans'])+['two_sources']
    assert list(d['synthetic_domain_INPUT_plans'])==sorted(names) # serialized JSON sorted, not audit case order
    for n in names[:2]:
        assert d['synthetic_domain_INPUT_plans'][n]==amp['synthetic_domain_INPUT_plans'][n]
        assert d['synthetic_validated_domains'][n]==amp['synthetic_scene_domains']['cases'][n]['domain_INPUT']
    multi=d['synthetic_domain_INPUT_plans']['two_sources'];mv=d['synthetic_validated_domains']['two_sources']
    assert len(multi['sources'])==len(mv['sources'])==2
    snap_bytes=base64.b64decode(d['synthetic_multisource_ORIGINAL_snapshot_base64'],validate=True)
    assert sha(snap_bytes)==old['synthetic_valid']['cases']['two_sources']['context']['original_snapshot_sha256']
    snap=json.loads(snap_bytes)
    assert [s['id'] for s in snap['sources']]==[s['source_id'] for s in mv['sources']]
    for s,v in zip(snap['sources'],mv['sources']):
        assert all(type(x) is float and math.isfinite(x) for x in s['field_reim'])
        assert [struct.unpack('<Q',struct.pack('<d',x))[0] for x in s['field_reim']]==v['ORIGINAL_source_uint64']
    assert d['synthetic_multisource_domain_provenance'].startswith('NEW INPUT syntax control')
    # Independently reconstruct domain rows and exact anchor/box/conditional-geometry fields.
    for n in names:
        dp=d['synthetic_domain_INPUT_plans'][n];dv=d['synthetic_validated_domains'][n]
        ctx=old['synthetic_valid']['cases'][n]['context']
        assert set(dp)=={'model','units','context_sha256','scope','sources'}
        assert dp['model']==DOMAIN_MODEL and dp['units']=='ORIGINAL-SOURCE-field-amplitude'
        assert dp['context_sha256']==digest(ctx) and dp['scope']==SCOPE
        assert dv['domain_INPUT_valid'] is True and dv['domain_sha256']==digest(dp) and dv['context_sha256']==digest(ctx)
        assert [s['source_id'] for s in dp['sources']]==[s['source_id'] for s in dv['sources']]==ctx['source_order']
        for raw,src,a in zip(dp['sources'],dv['sources'],ctx['assignments']):
            assert set(raw)==set(GAUGES)|{'box_reim'}
            assert all(type(raw[k]) is str and raw[k]==src[k]==a[k] for k in GAUGES)
            assert raw['terminal_reference_id']==raw['common_terminal_reference_id']
            box=[tuple(map(rat,i)) for i in raw['box_reim']];anchors=list(map(rat,src['ORIGINAL_anchor_reim']))
            assert anchors==list(map(bits,src['ORIGINAL_source_uint64'])) and all(lo<=x<=hi for x,(lo,hi) in zip(anchors,box))
            if n=='two_sources':assert all(lo==x==hi for x,(lo,hi) in zip(anchors,box))
            distances=[F(0) if lo<=0<=hi else min(abs(lo),abs(hi)) for lo,hi in box];lower=max(distances)
            geometry={'model':DOMAIN_MODEL,'box_reim':raw['box_reim'],'component_min_abs':list(map(pair,distances)),
                'amplitude_lower_bound':pair(lower),'uniform_error_hypothesis_L1':None,
                'uniform_executed_SOURCE_error_L1':None,'uniform_SOURCE_enclosure_proved':False,
                'conditional_phase_bound_rad':None,'positive_radial_lower_bound':None,
                'conditional_amplitude_box_phase_lemma_HOST_proved':False,
                'group_phase_bound_rad':None,'status':'STOP',**dict.fromkeys(flags,False),
                'reason':'missing uniform SOURCE error proof; point error is not a uniform enclosure'}
            expected={**raw,'ORIGINAL_source_uint64':src['ORIGINAL_source_uint64'],
                'ORIGINAL_anchor_reim':src['ORIGINAL_anchor_reim'],'conditional_geometry':geometry,
                'uniform_executed_SOURCE_error_L1':None,'uniform_SOURCE_enclosure_proved':False,
                'domain_authentication':False,'status':'STOP',**dict.fromkeys(flags,False)}
            assert src==expected
    count=0
    for variant,valid,cap,domains_present in (
        ('real_missing',False,None,False),('explicit_None_missing',False,None,False),
        ('domain_present_phase_missing',False,None,True),
        ('synthetic_valid',True,[1,1000000000000],True),('synthetic_zero_valid',True,[0,1],True)):
        audit=d[variant];nf(audit);assert audit['model']==MODEL and audit['SOURCE_phase_policy_adopted'] is False
        expected_order=names if domains_present else amp['real_missing']['case_order']
        assert audit['case_order']==expected_order and set(audit['cases'])==set(expected_order)
        assert audit['valid_INPUT_cases']==(3 if valid else 0) and audit['missing_INPUT_cases']==(0 if valid else len(expected_order))
        assert all(audit[k]==0 for k in ('certificate_inspections','numeric_phase_comparisons','group_admissions','new_native_operations','old_suites_producers_reexecuted'))
        if not domains_present:assert len(expected_order)==17 and sum(len(c['context']['source_order']) for c in audit['cases'].values())==19
        for n in expected_order:
            case=audit['cases'][n];v=case['INPUT'];nf(case);nf(v)
            ctx=old['synthetic_valid' if domains_present else 'real_missing']['cases'][n]['context']
            assert case['context']==ctx and v['context_sha256']==digest(ctx)
            assert case['status']==v['status']=='STOP' and v[FLAG] is valid and v['domain_INPUT_valid'] is domains_present
            assert v['SOURCE_phase_policy_adopted'] is False and v['frozen_guard_admission_for_entire_box_proved'] is False
            assert v['uniform_phase_INPUT_quota_fits'] is v['uniform_executed_SOURCE_error_L1'] is None
            assert v['domain_sha256']==(digest(d['synthetic_domain_INPUT_plans'][n]) if domains_present else None)
            if not valid:assert v['sources'] is None;continue
            plan=d['synthetic_control_INPUT_plans' if cap[0] else 'synthetic_zero_INPUT_plans'][n]
            assert set(plan)=={'model','units','context_sha256','domain_sha256','scope','sources'}
            assert plan['model']==MODEL and plan['units']==UNITS and plan['scope']==SCOPE
            assert plan['context_sha256']==v['context_sha256'] and plan['domain_sha256']==v['domain_sha256']
            assert v['plan_sha256']==digest(plan) and v['sources']==plan['sources'] and v['reference_model']==REFERENCE
            assert [s['source_id'] for s in plan['sources']]==ctx['source_order']
            for s,src,a in zip(plan['sources'],d['synthetic_validated_domains'][n]['sources'],ctx['assignments']):
                count+=1;assert set(s)==set(GAUGES)|{'reference_model','cap_rad','domain_source_sha256'}
                assert all(type(s[k]) is str and s[k]==src[k]==a[k] for k in GAUGES)
                assert s['domain_source_sha256']==digest(src) and s['reference_model']==REFERENCE and s['cap_rad']==cap and rat(s['cap_rad'])>=0
    assert d['real_missing']==d['explicit_None_missing'] and count==8
    assert len(d['typed_cap_rejections'])==12 and len(d['binding_rejections'])==19 and len(d['boundary_rejections'])==8
    assert r['synthetic_controls_are_real_INPUT'] is r['output_fitted_INPUT'] is r['SOURCE_phase_policy_adopted'] is False
    assert r['JEV_provenance']=='LOCAL' and r['group_admissions']==0 and r['phase_INPUT_quota_fits'] is None
    # Prior scope gate and all point FAIL variants remain immutable; never replayed.
    retained=payload(p)['data']
    assert retained['real_missing']['case_order']!=retained['explicit_None_missing']['case_order']
    assert retained['phase_zero_FAIL']['blocked_variable_box_quota_scopes']==2
    print(json.dumps({'PASS':True,'pins':472,'tests':5,'schema_source_rows_checked':count,
        'REAL_missing_cases':17,'REAL_missing_sources':19,'invalid_INPUT_rejections':39,
        'uniform_phase_comparison':None,'group_admissions':0,'scope':'new explicit domain INPUT syntax ONLY; policy/guard/execution STOP'},sort_keys=True))
if __name__=='__main__':main()
