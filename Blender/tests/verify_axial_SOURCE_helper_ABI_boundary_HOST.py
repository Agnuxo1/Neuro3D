"""Independent stdlib binding-receipt extraction; never import production."""
import ast
import base64
import hashlib
import json
import zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT='coordinacion/respuestas/AXIAL-SOURCE-HELPER-ABI-BOUNDARY-HOST-001-CODEX.json'
PARENT='coordinacion/respuestas/AXIAL-SOURCE-ENCODER-GRAPH-AST-HOST-001-CODEX.json'
PARENT_SHA='7f1006dfe09052b924dc7074f61933c5608711ece54210eab05044f581fa5b68'
PROBE='coordinacion/respuestas/AXIAL-ORIGINAL-SOURCE-CPU-001-CODEX.json'
PROBE_SHA='a9a894bc3f2749f750aba78714ec31d1bb2cbd6a77c2bf862dfedfd565ccf162'
PD='22360581828da0509dcc4a9bb1862a7cbbe914692172f0f693c997bbea0b6244'
DIR='Blender/benchmarks/capacity_audit/'
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def dump(n):return ast.dump(n,include_attributes=False)
def payload(r):
    t=r['test_run'];v=t.get('stdout_zlib_base64')
    if v is None:v=''.join(t['stdout_zlib_base64_chunks'])
    b=zlib.decompress(base64.b64decode(v,validate=True))
    assert len(b)==t['stdout_bytes'] and sha(b)==t['stdout_sha256'];return json.loads(b)
def main():
    r=json.loads((ROOT/REPORT).read_bytes());pb=(ROOT/PARENT).read_bytes();assert sha(pb)==PARENT_SHA
    p=json.loads(pb);old={**p['code_doc_sha256'],PARENT:PARENT_SHA};own=r['own_code_doc_sha256']
    pins={**old,**own};assert len(old)==498 and len(own)==4 and len(pins)==502 and not set(old)&set(own)
    assert r['code_doc_sha256']==pins
    for path,h in pins.items():assert sha((ROOT/path).read_bytes())==h,path
    assert r['base_commit']=='79018f5e1bf615197b3910cd39ac11f0efb59c54'
    assert r['task_id']=='AXIAL-SOURCE-HELPER-ABI-BOUNDARY-HOST-001'
    run=payload(r);assert run['PASS'] is True and run['tests']==4
    t=r['test_run'];assert t['rc']==0 and t['timed_out'] is False
    assert t['threads']==t['affinity_mask']==1 and t['hard_child_timeout_seconds']==60
    d=run['data'];a=d['audit'];v=a['audit'];probe=a['probe']
    assert a['inherited_pins_verified']==498 and a['proof_scope']==p['proof_scope']==r['proof_scope']
    assert len(a['proof_scope'])==38 and all(x is False for x in a['proof_scope'].values())
    assert a['group_admissions']==0 and a['status']=='STOP' and a['uniform_executed_SOURCE_error_L1'] is None
    assert a['actual_scene_domain_grid_authenticated'] is a['encoder_graph_execution_authenticated'] is False
    assert a['historical_negative_markers_retained'] is True and a['old_producers_and_numerical_controls_reexecuted']==0
    assert v['helper_ABI_static_boundary_bound_HOST'] is True and v['status']=='STOP'
    assert v['native_calls']==v['target_imports']==0
    queries={'transport.cast32':('axial_ORIGINAL_source_CPU_v1','cast32'),
             'source.word':('axial_source_float64_stage_CPU_v1','word'),
             'source.value':('axial_source_float64_stage_CPU_v1','value'),
             'guard.bits':('axial_geometry_decode_guard_CPU_v1','bits'),
             'guard.check_RN':('axial_geometry_decode_guard_CPU_v1','check_RN')}
    assert set(v['bindings'])==set(queries)
    trees={}
    def tree(module):
        if module not in trees:trees[module]=ast.parse((ROOT/(DIR+module+'.py')).read_bytes())
        return trees[module]
    for query,(module,name) in queries.items():
        fn=[n for n in tree(module).body if isinstance(n,ast.FunctionDef) and n.name==name]
        assert len(fn)==1;n=fn[0]
        assert v['bindings'][query]=={'kind':'function','module':module,'name':name,'first_line':n.lineno,
             'last_line':n.end_lineno,'AST_sha256':sha(dump(n).encode())}
    # Independent symbolic replay of the recorded import/alias trace, NO Python
    # evaluation. Every node has to be sealed and reachable in AST name lookup.
    index={}
    for row in v['alias_trace']:
        body=tree(row['module']).body
        candidates=[n for n in body if n.lineno==row['first_line']]
        assert len(candidates)==1 and sha(dump(candidates[0]).encode())==row['AST_sha256']
        n=candidates[0];key=(row['module'],row['symbol'])
        if key in index:assert dump(index[key])==dump(n)
        index[key]=n
    def resolve(module,name,seen=()):
        key=(module,name);assert key not in seen and len(seen)<64 and key in index
        n=index[key]
        if isinstance(n,ast.Import):
            candidates=[x for x in n.names if (x.asname or x.name)==name]
            assert len(candidates)==1
            return ('module',candidates[0].name)
        if isinstance(n,ast.FunctionDef):return ('function',module,n.name)
        assert isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id==name for x in n.targets)
        return expr(module,n.value,seen+(key,))
    def expr(module,n,seen):
        if isinstance(n,ast.Name):return resolve(module,n.id,seen)
        assert isinstance(n,ast.Attribute)
        obj=expr(module,n.value,seen);assert obj[0]=='module'
        return resolve(obj[1],n.attr,seen)
    for query,(module,name) in queries.items():
        assert expr('axial_guarded_source_product_RN64_CPU_v1',ast.parse(query,mode='eval').body,())==('function',module,name)
    assert v['parsed_module_count']==len(trees)
    b=v['boundary']
    for key in ('cast32_requires_float_finite_input_in_text','cast32_output_finite_only_not_normal_guard_in_text',
                'source_value_rejects_subnormal_selected_words_in_text','guard_bits_width_type_strict_int_in_text',
                'check_RN_exact_zero_checks_word_sign_in_text','check_RN_neighbor_bits_allow_subnormal_for_midpoints_in_text'):
        assert b[key] is True,key
    for key in ('source_value_width_type_strict_int_in_text','word_has_standalone_finite_input_guard_in_text',
                'rational_value_alone_preserves_zero_sign','runtime_binding_authenticated','current_runtime_probe_executed',
                'whole_domain_RN_model_authenticated','signed_zero_execution_proved','selected_guard_accepts_cast_subnormals'):
        assert b[key] is False,key
    oldb=(ROOT/PROBE).read_bytes();assert sha(oldb)==PROBE_SHA
    olda=payload(json.loads(oldb))['data']['audit'];op=olda['runtime_probe'];assert digest(op)==PD
    assert olda['previous_SOURCE_eight_bit_FAILs_preserved'] is olda['previous_SOURCE_twelve_zero_sign_mismatches_preserved'] is True
    assert probe['retained_cast_checks']==op['binary32_cast_checks'] and probe['retained_binary64_checks']==op['binary64']['checks']
    assert probe['retained_probe_sha256']==PD and probe['retained_probe_observed_PASS'] is True
    assert len(probe['retained_cast_checks'])==4 and len(probe['retained_binary64_checks'])==6
    assert probe['new_probe_operations']==probe['new_probe_casts']==0
    assert probe['retained_is_current_runtime_authentication'] is probe['subnormal_word1_is_selected_guard_admission'] is False
    assert probe['retained_cast_checks'][2]['label']=='gradual_cast32' and probe['retained_cast_checks'][2]['actual_uint32']==1
    controls=d['static_rejections'];assert len(controls)==11
    for c in controls:
        assert c['rejection'] and sha(c['candidate_text'].encode())==c['candidate_sha256']
        ast.parse(c['candidate_text'])
        assert c['candidate_sha256']!=sha((ROOT/(DIR+c['module']+'.py')).read_bytes())
    assert len(d['probe_rejections'])==4
    for c in d['probe_rejections']:assert c['rejection'] and digest(c['probe'])!=PD
    assert len(d['type_form_rejections'])==8 and all(c['rejection'] for c in d['type_form_rejections'])
    assert r['JEV_provenance']=='LOCAL_fallback' and r['group_admissions']==0
    print(json.dumps({'PASS':True,'pins':502,'tests':4,'helper_endpoints':5,'modules':len(trees),
       'static_rejections':11,'probe_rejections':4,'type_form_rejections':8,
       'retained_probes':10,'new_probes':0,'target_imports':0,'native_calls':0,'status':'STOP'},
       sort_keys=True,separators=(',',':')))

if __name__=='__main__':main()
