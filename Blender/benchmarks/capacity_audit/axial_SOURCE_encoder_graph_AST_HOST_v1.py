"""Opt-in static AST correspondence only. Never import or execute the frozen target."""
import ast
import base64
import hashlib
import json
import zlib
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MODEL = 'axial-SOURCE-encoder-decode-declared-GRID-static-AST-HOST-v1'
FLAG = 'declared_encoder_decode_AST_shape_matched_HOST'
PROGRAM = 'Blender/benchmarks/capacity_audit/axial_guarded_source_product_RN64_CPU_v1.py'
PROGRAM_SHA = '611b9f628c0599278938657a5154615bb22fe998ebd62f45e3a1dbad9c154bdc'
MODULE_AST_SHA = '7333f1e7f3e1db6ca352db1aa40014deece3879e23e7172bd3ae24b4925343ee'
PARENT = 'coordinacion/respuestas/AXIAL-SOURCE-BINARY64-GRID-CONSUMER-HOST-001-CODEX.json'
PARENT_SHA = '131e1611ecb1c463b912db1f1905241b6e4efd89abb38a166b48c16289857d4a'
GRID = 'coordinacion/respuestas/AXIAL-SOURCE-BINARY64-GRID-INPUT-HOST-001-CODEX.json'
GRID_SHA = '3eb8e18e7740f7448d92a9e459427ad3a2dd28e58d73c7f950c75417a3db94ff'
GRAPH = {
    'limb_wire_abi': '4x uint32 little-endian; real.high real.low imag.high imag.low',
    'component_order': ['real', 'imag'],
    'limb_order': ['real.high', 'real.low', 'imag.high', 'imag.low'],
    'nodes_per_component': [
        ['high','RN32','ORIGINAL'],
        ['residual','RN64-sub','ORIGINAL','widen64(high)'],
        ['low','RN32','residual'],
        ['decode','RN64-add','widen64(high)','widen64(low)']],
    'widening': 'exact binary32 to binary64',
    'signed_zero': 'IEEE node signs; no canonicalization',
    'covered': 'encoder/decode only; no UNIT product/material/transport/field'}
ENCODER_TEMPLATE = """
def encode_source(words):
    require(type(words) is list and len(words)==2,'two ORIGINAL source words')
    originals=[guard.bits(w,64) for w in words]
    limbs=[];records=[];sums=[];enc=F(0)
    for w,x in zip(words,originals):
        _,hw=native_cast32(source.value(w,64));h=guard.check_RN(x,hw,32,w>>63)
        rw=source.word(native_subtract(source.value(w,64),source.value(hw,32)))
        exact=x-h;zs=int(x==h==0 and w>>63==1 and hw>>31==0)
        res=guard.check_RN(exact,rw,64,zs)
        _,lw=native_cast32(source.value(rw,64));low=guard.check_RN(res,lw,32,rw>>63)
        represented=h+low;e=abs(represented-x);enc+=e;sums.append(represented);limbs.extend([hw,lw])
        records.append({'original_uint64':w,'high_uint32':hw,'residual_uint64':rw,'low_uint32':lw,
          'exact_residual':pair(exact),'signed_residual_RN64_delta':pair(res-exact),
          'signed_low_RN32_delta':pair(low-res),'represented_sum':pair(represented),'encoding_error_L1':pair(e)})
    raw=struct.pack('<IIII',*limbs)
    return {'ORIGINAL_source_uint64':deepcopy(words),'limb_uint32':limbs,'records':records,
      'hilo_le_base64':base64.b64encode(raw).decode(),'hilo_le_sha256':hashlib.sha256(raw).hexdigest(),
      'exact_limb_sums':list(map(pair,sums)),'source_encoding_error_L1':pair(enc),
      'new_RN32_casts':4,'new_RN64_subtractions':2,'zero_canonicalization_performed':False}
"""
DECODE_PREFIX_TEMPLATE = """
def execute(admission):
    words=admission['ORIGINAL_source_uint64'];require(type(words) is list and len(words)==2,'two source components')
    sq=[guard.bits(w,64) for w in words]
    uw=admission['unit_uint64'];require(type(uw) is list and len(uw)==2,'two retained unit words');u=[guard.bits(w,64) for w in uw]
    charges={n:guard.rational(v) for n,v in admission['unit_L1_charges'].items()};U=sum(charges.values(),F(0))
    require(set(charges)==set(UNIT_NAMES) and all(v>=0 for v in charges.values()) and U==guard.rational(admission['unit_L1_bound']) and U<1,'eleven nonnegative retained unit charges')
    encoder=encode_source(words);limbs=encoder['limb_uint32'];nodes=[]
    def node(a,b,op,label):
        aq,bq=guard.bits(a,64),guard.bits(b,64);exact=aq*bq if op=='mul' else aq+bq
        zs=(a>>63)^(b>>63) if op=='mul' else int(aq==bq==0 and a>>63==b>>63==1)
        v=(native_multiply if op=='mul' else native_add)(source.value(a,64),source.value(b,64))
        w=source.word(v);q=guard.check_RN(exact,w,64,zs)
        nodes.append({'label':label,'op':op,'input_uint64':[a,b],'output_uint64':w,'exact_operation':pair(exact),'signed_RN64_delta':pair(q-exact)})
        return w
    lw=[source.word(source.value(w,32)) for w in limbs]
    a=node(lw[0],lw[1],'add','decode0');b=node(lw[2],lw[3],'add','decode1')
"""
WRAPPERS_TEMPLATE = """
def native_cast32(v):return transport.cast32(v)
def native_subtract(a,b):return a-b
def native_add(a,b):return a+b
def native_multiply(a,b):return a*b
"""

def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)

def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()

def digest(value: object) -> str:
    return sha(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode())

def dump(node: ast.AST) -> str:
    return ast.dump(node,include_attributes=False)

def read_sealed(path: str, expected: str) -> bytes:
    raw = (ROOT/path).read_bytes()
    require(sha(raw)==expected,'sealed file: '+path)
    return raw

def payload(report: dict) -> dict:
    run = report['test_run']
    value = run.get('stdout_zlib_base64')
    if value is None:
        value = ''.join(run['stdout_zlib_base64_chunks'])
    raw = zlib.decompress(base64.b64decode(value,validate=True))
    require(len(raw)==run['stdout_bytes'] and sha(raw)==run['stdout_sha256'],'lossless retained payload')
    return json.loads(raw)

def load_retained() -> tuple[str, dict, dict, dict]:
    parent = json.loads(read_sealed(PARENT,PARENT_SHA))
    require(parent['task_id']=='AXIAL-SOURCE-BINARY64-GRID-CONSUMER-HOST-001','parent ID')
    pins = {**parent['code_doc_sha256'],PARENT:PARENT_SHA}
    require(len(pins)==493 and pins.get(PROGRAM)==PROGRAM_SHA and pins.get(GRID)==GRID_SHA,'complete inherited lineage')
    for path, expected in pins.items():
        read_sealed(path,expected)
    grid = payload(json.loads(read_sealed(GRID,GRID_SHA)))['data']
    require(len(parent['proof_scope'])==38 and all(v is False for v in parent['proof_scope'].values()),'frozen broad scope')
    return read_sealed(PROGRAM,PROGRAM_SHA).decode('utf-8'),grid['synthetic_grid_INPUT_plans'],pins,parent['proof_scope']

def inspect_AST(text: str) -> dict:
    """Compare syntax, not Python execution or RN/helper semantics."""
    require(type(text) is str and 0<len(text.encode('utf-8'))<=262144,'bounded source text')
    try:
        module = ast.parse(text)
    except (SyntaxError,ValueError,RecursionError) as error:
        raise ValueError('source syntax') from error
    expected = {n.name:n for n in ast.parse(WRAPPERS_TEMPLATE+ENCODER_TEMPLATE).body}
    functions = [n for n in module.body if isinstance(n,ast.FunctionDef)]
    found = {}
    for name, template in expected.items():
        matches = [n for n in functions if n.name==name]
        require(len(matches)==1 and dump(matches[0])==dump(template),'exact AST function: '+name)
        found[name] = matches[0]
    execute = [n for n in functions if n.name=='execute']
    require(len(execute)==1,'unique execute definition')
    prefix = ast.parse(DECODE_PREFIX_TEMPLATE).body[0]
    node = execute[0]
    require(dump(node.args)==dump(prefix.args) and not node.decorator_list and node.returns is None
            and node.type_comment is None and not node.type_params,'plain execute signature')
    require(len(node.body)>=len(prefix.body) and
            all(dump(a)==dump(b) for a,b in zip(node.body,prefix.body)),'exact AST decode prefix')
    # This seal also rejects late rebindings, top-level poison and edits outside
    # the selected graph. It is an identity gate, NOT a semantic proof of them.
    require(sha(dump(module).encode())==MODULE_AST_SHA,'frozen complete module AST identity')
    evidence = []
    for name in ('native_cast32','native_subtract','native_add','native_multiply','encode_source'):
        f = found[name]
        evidence.append({'region':name,'first_line':f.lineno,'last_line':f.end_lineno,'AST_sha256':sha(dump(f).encode())})
    evidence.append({'region':'execute.through_decode1','first_line':node.lineno,
                     'last_line':node.body[len(prefix.body)-1].end_lineno,
                     'AST_sha256':sha(dump(ast.Module(body=node.body[:len(prefix.body)],type_ignores=[])).encode())})
    return {FLAG:True,'regions':evidence,'module_AST_sha256':MODULE_AST_SHA,
            'source_text_sha256':sha(text.encode()),'scope':'AST shape only; helper meanings and actual execution unproved',
            'frozen_target_executions':0,'native_calls':0,'status':'STOP'}

def audit_plans(text: str, plans: dict, *, model: str) -> dict:
    require(type(model) is str and model==MODEL,'explicit static AST model')
    require(type(plans) is dict and set(plans)=={'nonexact_geometry_phase_PASS','thin_resolved','two_sources'},'complete retained synthetic plan set')
    # Validate ALL declared graphs before ANY AST inspection; no source values,
    # mathematical certificates or runtime are evaluated here.
    for name, plan in plans.items():
        require(type(plan) is dict and plan.get('encoder_program_path')==PROGRAM and
                plan.get('encoder_program_sha256')==PROGRAM_SHA,'same frozen target in '+name)
        require(type(plan.get('encoder_graph')) is dict and digest(plan['encoder_graph'])==digest(GRAPH),'same exact declared graph in '+name)
    match = inspect_AST(text)
    rows = {name:{'GRID_INPUT_plan_sha256':digest(plan),'declared_graph_sha256':digest(plan['encoder_graph']),
                  'program_sha256':PROGRAM_SHA,FLAG:True,'status':'STOP'} for name,plan in plans.items()}
    return {'model':MODEL,'match':match,'synthetic_plan_graphs':rows,
            'retained_synthetic_plans_matched':3,'static_source_inspections':1,
            'synthetic_controls_are_real_INPUT':False,'actual_scene_domain_grid_authenticated':False,
            'encoder_graph_execution_authenticated':False,'RN_model_runtime_verified':False,
            'helper_semantics_certified':False,'signed_zero_execution_proved':False,
            'frozen_guard_admission_for_entire_box_proved':False,'uniform_executed_SOURCE_error_L1':None,
            'group_admissions':0,'native_calls':0,'status':'STOP'}

def audit_retained_AST_HOST(*, model: str) -> dict:
    text,plans,pins,false = load_retained()
    result = audit_plans(text,plans,model=model)
    result['inherited_pins_verified'] = len(pins)
    result['proof_scope'] = deepcopy(false)
    return result
