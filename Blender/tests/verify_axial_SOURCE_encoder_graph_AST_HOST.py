"""Independent stdlib receipt/hash and AST extraction; no production imports/exec."""
import ast
import base64
import hashlib
import json
import zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT='coordinacion/respuestas/AXIAL-SOURCE-ENCODER-GRAPH-AST-HOST-001-CODEX.json'
PARENT='coordinacion/respuestas/AXIAL-SOURCE-BINARY64-GRID-CONSUMER-HOST-001-CODEX.json'
PARENT_SHA='131e1611ecb1c463b912db1f1905241b6e4efd89abb38a166b48c16289857d4a'
GRID='coordinacion/respuestas/AXIAL-SOURCE-BINARY64-GRID-INPUT-HOST-001-CODEX.json'
PROGRAM='Blender/benchmarks/capacity_audit/axial_guarded_source_product_RN64_CPU_v1.py'
PROGRAM_SHA='611b9f628c0599278938657a5154615bb22fe998ebd62f45e3a1dbad9c154bdc'
AST_SHA='7333f1e7f3e1db6ca352db1aa40014deece3879e23e7172bd3ae24b4925343ee'
MODEL='axial-SOURCE-encoder-decode-declared-GRID-static-AST-HOST-v1'
FLAG='declared_encoder_decode_AST_shape_matched_HOST'

def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def dump(n):return ast.dump(n,include_attributes=False)
def payload(r):
    t=r['test_run']
    v=t.get('stdout_zlib_base64')
    if v is None:v=''.join(t['stdout_zlib_base64_chunks'])
    b=zlib.decompress(base64.b64decode(v,validate=True))
    assert len(b)==t['stdout_bytes'] and sha(b)==t['stdout_sha256']
    return json.loads(b)
def assigned(body,name):
    rows=[(i,s) for i,s in enumerate(body) if isinstance(s,ast.Assign)
          and any(isinstance(t,ast.Name) and t.id==name for t in s.targets)]
    assert len(rows)==1,name
    return rows[0]
def expression(code):return dump(ast.parse(code,mode='eval').body)

def main():
    r=json.loads((ROOT/REPORT).read_bytes())
    pb=(ROOT/PARENT).read_bytes();assert sha(pb)==PARENT_SHA
    p=json.loads(pb);old={**p['code_doc_sha256'],PARENT:PARENT_SHA}
    own=r['own_code_doc_sha256'];pins={**old,**own}
    assert len(old)==493 and len(own)==4 and len(pins)==497 and not set(old)&set(own)
    assert pins==r['code_doc_sha256']
    for path,h in pins.items():assert sha((ROOT/path).read_bytes())==h,path
    assert r['task_id']=='AXIAL-SOURCE-ENCODER-GRAPH-AST-HOST-001' and r['model']==MODEL
    assert r['base_commit']=='97fe1fcf293388a6474a60766f3699e2de97e6d5'
    t=r['test_run'];assert t['rc']==0 and t['timed_out'] is False
    assert t['threads']==t['affinity_mask']==1 and t['hard_child_timeout_seconds']==60
    run=payload(r);assert run['tests']==5 and run['PASS'] is True
    d=run['data'];a=d['audit']
    assert a['model']==MODEL and a['proof_scope']==p['proof_scope']
    assert len(a['proof_scope'])==38 and all(v is False for v in a['proof_scope'].values())
    assert a['status']=='STOP' and a['group_admissions']==a['native_calls']==0
    assert a['uniform_executed_SOURCE_error_L1'] is None
    for k in ('synthetic_controls_are_real_INPUT','actual_scene_domain_grid_authenticated',
              'encoder_graph_execution_authenticated','RN_model_runtime_verified','helper_semantics_certified',
              'signed_zero_execution_proved','frozen_guard_admission_for_entire_box_proved'):
        assert a[k] is False,k
    assert a['inherited_pins_verified']==493 and a['static_source_inspections']==1
    text=(ROOT/PROGRAM).read_bytes();assert sha(text)==PROGRAM_SHA
    tree=ast.parse(text);assert sha(dump(tree).encode())==AST_SHA
    fs={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
    for name,ex in [('native_cast32','transport.cast32(v)'),('native_subtract','a-b'),
                    ('native_add','a+b'),('native_multiply','a*b')]:
        f=fs[name];assert len(f.body)==1 and isinstance(f.body[0],ast.Return)
        assert dump(f.body[0].value)==expression(ex)
    enc=fs['encode_source'];idx,originals=assigned(enc.body,'originals')
    assert dump(originals.value)==expression('[guard.bits(w,64) for w in words]')
    loops=[(i,n) for i,n in enumerate(enc.body) if isinstance(n,ast.For)]
    assert len(loops)==1 and idx<loops[0][0];loop=loops[0][1]
    assert dump(loop.iter)==expression('zip(words,originals)')
    # Independent ordered node expressions, rather than importing core templates.
    rn=[n for n in ast.walk(loop) if isinstance(n,ast.Call) and
        isinstance(n.func,ast.Attribute) and n.func.attr=='check_RN']
    assert len(rn)==3
    for name,ex in [
        ('h','guard.check_RN(x,hw,32,w>>63)'),
        ('rw','source.word(native_subtract(source.value(w,64),source.value(hw,32)))'),
        ('res','guard.check_RN(exact,rw,64,zs)'),
        ('low','guard.check_RN(res,lw,32,rw>>63)'),
        ('zs','int(x==h==0 and w>>63==1 and hw>>31==0)')]:
        _,n=assigned(loop.body,name);assert dump(n.value)==expression(ex),name
    calls=[n for n in ast.walk(loop) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='native_cast32']
    assert len(calls)==2 and {dump(n) for n in calls}=={
        expression('native_cast32(source.value(w,64))'),expression('native_cast32(source.value(rw,64))')}
    limb_calls=[n for n in ast.walk(loop) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)
                and isinstance(n.func.value,ast.Name) and n.func.value.id=='limbs']
    assert len(limb_calls)==1 and dump(limb_calls[0])==expression('limbs.extend([hw,lw])')
    _,raw=assigned(enc.body,'raw');assert dump(raw.value)==expression("struct.pack('<IIII',*limbs)")
    fn=fs['execute'];nodes=[n for n in fn.body if isinstance(n,ast.FunctionDef) and n.name=='node']
    assert len(nodes)==1;nd=nodes[0]
    _,v=assigned(nd.body,'v')
    assert dump(v.value)==expression("(native_multiply if op=='mul' else native_add)(source.value(a,64),source.value(b,64))")
    _,q=assigned(nd.body,'q');assert dump(q.value)==expression('guard.check_RN(exact,w,64,zs)')
    wi,w=assigned(fn.body,'lw');assert dump(w.value)==expression('[source.word(source.value(w,32)) for w in limbs]')
    ai,va=assigned(fn.body,'a');bi,vb=assigned(fn.body,'b')
    assert ai==wi+1 and bi==ai+1
    assert dump(va.value)==expression("node(lw[0],lw[1],'add','decode0')")
    assert dump(vb.value)==expression("node(lw[2],lw[3],'add','decode1')")
    regions=[]
    for name in ('native_cast32','native_subtract','native_add','native_multiply','encode_source'):
        n=fs[name];regions.append({'region':name,'first_line':n.lineno,'last_line':n.end_lineno,
                                  'AST_sha256':sha(dump(n).encode())})
    regions.append({'region':'execute.through_decode1','first_line':fn.lineno,'last_line':vb.end_lineno,
                    'AST_sha256':sha(dump(ast.Module(body=fn.body[:bi+1],type_ignores=[])).encode())})
    match=a['match']
    assert match['regions']==regions and match['module_AST_sha256']==AST_SHA
    assert match['source_text_sha256']==PROGRAM_SHA and match[FLAG] is True
    assert match['status']=='STOP' and match['native_calls']==match['frozen_target_executions']==0
    fmt=d['formatting_only_control']
    assert fmt[FLAG] is True and fmt['module_AST_sha256']==AST_SHA and fmt['source_text_sha256']!=PROGRAM_SHA
    plans=payload(json.loads((ROOT/GRID).read_bytes()))['data']['synthetic_grid_INPUT_plans']
    assert a['retained_synthetic_plans_matched']==3 and set(a['synthetic_plan_graphs'])==set(plans)
    for name,plan in plans.items():
        assert plan['encoder_program_path']==PROGRAM and plan['encoder_program_sha256']==PROGRAM_SHA
        assert a['synthetic_plan_graphs'][name]=={'GRID_INPUT_plan_sha256':digest(plan),
          'declared_graph_sha256':digest(plan['encoder_graph']),'program_sha256':PROGRAM_SHA,FLAG:True,'status':'STOP'}
    controls=d['AST_rejection_controls'];assert len(controls)==20 and len({c['label'] for c in controls})==20
    for c in controls:
        assert c['rejection'] and sha(c['candidate_text'].encode())==c['candidate_sha256']
        ct=ast.parse(c['candidate_text'])
        assert sha(dump(ct).encode())!=AST_SHA # No execution of any mutant.
    graphs=d['graph_rejection_controls'];assert len(graphs)==7
    g=plans['two_sources']['encoder_graph']
    for c in graphs:
        assert c['rejection'] and c['AST_inspections']==0
        assert digest(c['plans']['two_sources']['encoder_graph'])!=digest(g)
    assert len(d['type_model_rejections'])==8 and all(c['rejection'] for c in d['type_model_rejections'])
    assert len(d['batch_binding_rejections'])==3 and all(c['rejection'] and c['AST_inspections']==0 for c in d['batch_binding_rejections'])
    assert r['proof_scope']==a['proof_scope'] and r['group_admissions']==0
    assert r['actual_scene_domain_grid_authenticated'] is r['encoder_graph_execution_authenticated'] is False
    assert r['uniform_executed_SOURCE_error_L1'] is None and r['JEV_provenance']=='LOCAL_fallback'
    print(json.dumps({'PASS':True,'pins':len(pins),'tests':5,'static_regions':6,'synthetic_plan_graphs':3,
      'AST_rejections':20,'graph_rejections':7,'type_model_rejections':8,'batch_binding_rejections':3,
      'native_calls':0,'frozen_target_imports':0,'group_admissions':0,'status':'STOP'},sort_keys=True,separators=(',',':')))

if __name__=='__main__':main()
