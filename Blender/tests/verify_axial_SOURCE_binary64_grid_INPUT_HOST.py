"""Independent stdlib grid INPUT/snapshot/ABI binding oracle; no production imports."""
import base64,hashlib,json,math,struct,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT='coordinacion/respuestas/AXIAL-SOURCE-BINARY64-GRID-INPUT-HOST-001-CODEX.json'
PARENT='coordinacion/respuestas/AXIAL-SOURCE-BINARY64-ENCODER-WORDCLASS-HOST-001-CODEX.json'
PARENT_SHA='78249147dca45e62cf0ae1e4e9a87cb774f3e000a07da5d6ec81d47d8cb5f748'
DOMAIN='coordinacion/respuestas/AXIAL-SOURCE-DOMAIN-PHASE-INPUT-HOST-001-CODEX.json'
INGRESS='coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json'
PRESENCE='coordinacion/respuestas/AXIAL-NATIVE-PRESENCE-STOPS-001-CODEX.json'
MODEL='axial-SOURCE-binary64-grid-snapshot-encoder-INPUT-HOST-v1'
FLAG='SOURCE_binary64_grid_INPUT_bound_HOST'
GRID='finite ORIGINAL binary64 values in declared intervals ONLY; not arbitrary real continuum'
ARITH='RN-even binary32/binary64; exact widening; gradual underflow; no FTZ/FMA'
SCOPE='SOURCE_field_reim_only; fixed ORIGINAL geometry/wavelength/path/material/gauges'
PROGRAM='Blender/benchmarks/capacity_audit/axial_guarded_source_product_RN64_CPU_v1.py'
PROGRAM_SHA='611b9f628c0599278938657a5154615bb22fe998ebd62f45e3a1dbad9c154bdc'
GRAPH={'limb_wire_abi':'4x uint32 little-endian; real.high real.low imag.high imag.low',
       'component_order':['real','imag'],'limb_order':['real.high','real.low','imag.high','imag.low'],
       'nodes_per_component':[['high','RN32','ORIGINAL'],['residual','RN64-sub','ORIGINAL','widen64(high)'],
          ['low','RN32','residual'],['decode','RN64-add','widen64(high)','widen64(low)']],
       'widening':'exact binary32 to binary64','signed_zero':'IEEE node signs; no canonicalization',
       'covered':'encoder/decode only; no UNIT product/material/transport/field'}
GAUGES=('source_id','source_phase_reference_id','terminal_reference_id','common_terminal_reference_id')
PLAN_KEYS={'model','grid','arithmetic_model','packet_sha256','context_sha256','original_snapshot_sha256',
           'domain_sha256','scope','encoder_program_path','encoder_program_sha256','encoder_graph','sources'}
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def payload(r):
    t=r['test_run'];enc=t.get('stdout_zlib_base64') or ''.join(t['stdout_zlib_base64_chunks'])
    b=zlib.decompress(base64.b64decode(enc,validate=True))
    assert len(b)==t['stdout_bytes'] and sha(b)==t['stdout_sha256'];return json.loads(b)
def main():
    r=json.loads((ROOT/REPORT).read_bytes());b=(ROOT/PARENT).read_bytes();assert sha(b)==PARENT_SHA
    p=json.loads(b);inherited={**p['code_doc_sha256'],PARENT:PARENT_SHA};own=r['own_code_doc_sha256']
    pins={**inherited,**own};assert len(inherited)==483 and len(own)==4 and len(pins)==487
    assert not set(inherited)&set(own) and r['code_doc_sha256']==pins
    for path,h in pins.items():assert sha((ROOT/path).read_bytes())==h,path
    failed=r['failed_independent_oracle_runs'];assert len(failed)==1
    f=failed[0];assert f['rc']==1 and f['timed_out'] is False and f['stdout_bytes']==0
    assert "KeyError: 'cases'" in f['stderr']
    for snap in r['initial_source_snapshots'].values():assert sha(snap['utf8_source'].encode())==snap['sha256']
    assert r['initial_source_snapshots'][list(own)[0]]['sha256']==own[list(own)[0]]
    assert pins[PROGRAM]==PROGRAM_SHA
    assert r['task_id']=='AXIAL-SOURCE-BINARY64-GRID-INPUT-HOST-001' and r['model']==MODEL
    assert r['base_commit']=='54f16dd806dc3c00639bf53e20136d14528790b3'
    run=payload(r);d=run['data'];old=payload(p)['data']
    inputs=payload(json.loads((ROOT/DOMAIN).read_bytes()))['data']
    packets=payload(json.loads((ROOT/INGRESS).read_bytes()))['packets']
    presence=payload(json.loads((ROOT/PRESENCE).read_bytes()))['synthetic_controls']
    packets.update({n:v['parent'] for n,v in presence.items()})
    assert run['tests']==5 and run['PASS'] is True
    t=r['test_run'];assert t['rc']==0 and t['timed_out'] is False and t['threads']==t['affinity_mask']==1 and t['hard_child_timeout_seconds']==60
    flags=tuple(r['proof_scope']);assert len(flags)==38 and all(v is False for v in r['proof_scope'].values())
    def nf(x):assert all(x[k] is False for k in flags)
    def packet_context(name,ctx):
        packet=packets[name];assert digest(packet)==ctx['input_packet_sha256']
        buffers={k:base64.b64decode(v,validate=True) for k,v in packet['buffers_base64'].items()}
        assert set(buffers)=={'triangles','sources','wavelength','reference','original_scene_json','input_metadata_json'}
        for k,raw in buffers.items():assert packet['manifest']['buffers'][k]=={'bytes':len(raw),'sha256':sha(raw)}
        snap=json.loads(buffers['original_scene_json']);meta=json.loads(buffers['input_metadata_json'])
        assert sha(buffers['original_scene_json'])==meta['original_snapshot_sha256']==ctx['original_snapshot_sha256']
        assert [s['id'] for s in snap['sources']]==ctx['source_order']==meta['source_order']
        assert meta['explicit_group_contract']['assignments']==ctx['assignments']
        assert digest(meta['explicit_group_contract'])==ctx['original_group_contract_sha256']
        assert meta['scene_binding_sha256']==ctx['scene_binding_sha256']
        assert meta['word_ABI_sha256']==ctx['word_ABI_sha256']
        assert meta['explicit_group_contract']['limits']==ctx['unchanged_limits']
        assert ctx['execution_authenticated'] is ctx['coherence_authenticated'] is False
        return packet,snap
    negatives=0;wordpairs=0
    for variant in ('real_missing','explicit_None_missing','domain_present_grid_missing','synthetic_valid'):
        a=d[variant];present=variant=='synthetic_valid';withdom=variant in ('domain_present_grid_missing','synthetic_valid')
        base=inputs['synthetic_valid' if withdom else 'real_missing']
        nf(a);assert a['model']==MODEL and a['case_order']==base['case_order'] and set(a['cases'])==set(base['cases'])
        assert a['wordclass_predicate_assessments']==a['certificate_inspections']==a['new_native_operations']==a['old_suites_producers_reexecuted']==a['old_counterexamples_reexecuted']==a['group_admissions']==0
        assert a['actual_scene_domain_grid_authenticated'] is a['encoder_graph_execution_authenticated'] is False
        assert a['valid_INPUT_cases']==(3 if present else 0) and a['missing_INPUT_cases']==(0 if present else 3 if withdom else 17)
        for name in a['case_order']:
            case=a['cases'][name];ctx=case['context'];v=case['INPUT'];nf(case);nf(v)
            assert ctx==base['cases'][name]['context']==old['synthetic_valid' if withdom else 'real_missing']['cases'][name]['context']
            packet,snap=packet_context(name,ctx)
            assert case['status']==v['status']=='STOP' and v['context_sha256']==digest(ctx)
            assert v['domain_INPUT_valid'] is withdom and v[FLAG] is present
            for k in ('actual_scene_domain_grid_authenticated','encoder_graph_execution_authenticated','frozen_guard_admission_for_entire_box_proved'):assert v[k] is False
            assert v['uniform_executed_SOURCE_error_L1'] is v['phase_INPUT_quota_fits'] is None
            dom=inputs['synthetic_validated_domains'].get(name) if withdom else None
            assert v['domain_sha256']==(dom['domain_sha256'] if withdom else None)
            if not present:assert v['sources'] is None;continue
            plan=d['synthetic_grid_INPUT_plans'][name]
            assert set(plan)==PLAN_KEYS and plan['model']==v['model']==MODEL
            assert plan['grid']==v['grid']==GRID and plan['arithmetic_model']==v['arithmetic_model']==ARITH
            assert plan['scope']==v['scope']==SCOPE
            assert plan['context_sha256']==digest(ctx) and plan['packet_sha256']==v['packet_sha256']==digest(packet)
            assert plan['original_snapshot_sha256']==v['original_snapshot_sha256']==ctx['original_snapshot_sha256']
            assert plan['domain_sha256']==dom['domain_sha256']==digest(inputs['synthetic_domain_INPUT_plans'][name])
            assert plan['encoder_program_path']==v['encoder_program_path']==PROGRAM
            assert plan['encoder_program_sha256']==v['encoder_program_sha256']==PROGRAM_SHA
            assert plan['encoder_graph']==v['encoder_graph']==GRAPH
            assert v['plan_sha256']==digest(plan) and v['sources']==plan['sources']
            assert [s['source_id'] for s in v['sources']]==ctx['source_order']==[s['source_id'] for s in dom['sources']]
            assert len(v['sources'])==len(dom['sources'])==len(snap['sources'])
            for row,src,assignment,original,prior in zip(v['sources'],dom['sources'],ctx['assignments'],snap['sources'],old['synthetic_valid']['cases'][name]['sources']):
                assert set(row)==set(GAUGES)|{'domain_source_sha256','ORIGINAL_source_uint64'}
                assert all(type(row[k]) is str and row[k]==src[k]==assignment[k] for k in GAUGES)
                assert assignment['terminal_reference_id']==assignment['common_terminal_reference_id']
                assert row['source_id']==original['id']==prior['source_id'] and row['domain_source_sha256']==prior['domain_source_sha256']==digest(src)
                words=row['ORIGINAL_source_uint64'];assert type(words) is list and len(words)==2
                assert words==src['ORIGINAL_source_uint64']
                field=original['field_reim'];assert all(type(f) is float and math.isfinite(f) for f in field)
                assert words==[struct.unpack('<Q',struct.pack('<d',f))[0] for f in field]
                for w in words:
                    assert type(w) is int and 0<=w<2**64
                    exp=(w>>52)&2047;frac=w&((1<<52)-1);assert 0<exp<2047 or exp==frac==0
                wordpairs+=1
                if prior['retained_whole_box_guard_admission_disproved'] is True:
                    negatives+=1;assert name in ('nonexact_geometry_phase_PASS','thin_resolved')
                    assert prior['sufficient_numeric_encoder_wordclasses_under_explicit_binary64_grid_HOST'] is False
    assert negatives==2 and wordpairs==4
    assert d['real_missing']['cases']==d['explicit_None_missing']['cases']
    assert len(d['real_missing']['cases'])==17 and sum(len(x['context']['source_order']) for x in d['real_missing']['cases'].values())==19
    assert len(d['plan_graph_rejections'])==17 and len(d['source_rejections'])==14 and len(d['batch_lineage_rejections'])==6
    assert r['actual_scene_domain_grid_authenticated'] is r['encoder_graph_execution_authenticated'] is r['frozen_guard_admission_for_entire_box_proved'] is False
    assert r['group_admissions']==0 and r['uniform_executed_SOURCE_error_L1'] is r['phase_INPUT_quota_fits'] is None
    assert r['JEV_provenance']=='LOCAL' and r['synthetic_controls_are_real_INPUT'] is r['output_fitted_INPUT'] is False
    print(json.dumps({'PASS':True,'pins':487,'tests':5,'synthetic_INPUT_cases':3,'snapshot_SOURCE_word_pairs':4,
        'plan_graph_source_batch_rejections':37,'retained_negative_guard_boxes':2,
        'REAL_missing_cases':17,'REAL_missing_sources':19,'new_predicates':0,'group_admissions':0,
        'scope':'explicit GRID INPUT snapshot/domain/encoder binding ONLY; scene/guard/execution STOP'},sort_keys=True))
if __name__=='__main__':main()
