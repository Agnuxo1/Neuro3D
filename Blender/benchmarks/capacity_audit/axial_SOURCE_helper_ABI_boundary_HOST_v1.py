"""Static sealed helper bindings and retained probes; never import frozen modules."""
import ast
import base64
import hashlib
import json
import zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
DIR='Blender/benchmarks/capacity_audit/'
ENTRY='axial_guarded_source_product_RN64_CPU_v1'
MODEL='axial-SOURCE-helper-ABI-boundary-static-retained-probes-HOST-v1'
FLAG='helper_ABI_static_boundary_bound_HOST'
PARENT='coordinacion/respuestas/AXIAL-SOURCE-ENCODER-GRAPH-AST-HOST-001-CODEX.json'
PARENT_SHA='7f1006dfe09052b924dc7074f61933c5608711ece54210eab05044f581fa5b68'
PROBE_REPORT='coordinacion/respuestas/AXIAL-ORIGINAL-SOURCE-CPU-001-CODEX.json'
PROBE_SHA='a9a894bc3f2749f750aba78714ec31d1bb2cbd6a77c2bf862dfedfd565ccf162'
PROBE_DIGEST='22360581828da0509dcc4a9bb1862a7cbbe914692172f0f693c997bbea0b6244'
EXPECTED = {"axial_ORIGINAL_source_CPU_v1.cast32": "862d1c80bb87d9810cbf05497eecce751aa9a0997dba56c27c4c9d96a9491745","axial_source_float64_stage_CPU_v1.word": "cedb65a04dc286fbbf22a89729d1c4c3416ad52c74864fcab6399eba13a5c1a5","axial_source_float64_stage_CPU_v1.value": "27f90b3ad1618af3cf030df85d487c38875c5f5af756a6d3f621c598f107b443","axial_geometry_decode_guard_CPU_v1.bits": "ec00a941c20fe87f20e5a3eed058af64dc15d1cd821be507535f03a518d1c98c","axial_geometry_decode_guard_CPU_v1.check_RN": "e216a6b45b08ed4b13fa61c5d2aada6c70939cda6cc76ad0f7aa1fbdaaf0f93a"}
QUERIES={
 'transport.cast32':'axial_ORIGINAL_source_CPU_v1.cast32',
 'source.word':'axial_source_float64_stage_CPU_v1.word',
 'source.value':'axial_source_float64_stage_CPU_v1.value',
 'guard.bits':'axial_geometry_decode_guard_CPU_v1.bits',
 'guard.check_RN':'axial_geometry_decode_guard_CPU_v1.check_RN'}
BOUNDARY={
 'cast32_requires_float_finite_input_in_text':True,
 'cast32_output_finite_only_not_normal_guard_in_text':True,
 'source_value_rejects_subnormal_selected_words_in_text':True,
 'source_value_width_type_strict_int_in_text':False,
 'guard_bits_width_type_strict_int_in_text':True,
 'word_has_standalone_finite_input_guard_in_text':False,
 'rational_value_alone_preserves_zero_sign':False,
 'check_RN_exact_zero_checks_word_sign_in_text':True,
 'check_RN_neighbor_bits_allow_subnormal_for_midpoints_in_text':True,
 'entry_widths_remain_literal_32_64':'retained encoder/decode AST receipt; not arbitrary API input',
 'runtime_binding_authenticated':False,'current_runtime_probe_executed':False,
 'whole_domain_RN_model_authenticated':False,'signed_zero_execution_proved':False,
 'selected_guard_accepts_cast_subnormals':False}

def require(ok: bool,message: str) -> None:
    if not ok:raise ValueError(message)
def sha(b: bytes) -> str:return hashlib.sha256(b).hexdigest()
def digest(v: object) -> str:return sha(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def dump(n: ast.AST) -> str:return ast.dump(n,include_attributes=False)
def payload(r: dict) -> dict:
    t=r['test_run'];v=t.get('stdout_zlib_base64')
    if v is None:v=''.join(t['stdout_zlib_base64_chunks'])
    b=zlib.decompress(base64.b64decode(v,validate=True))
    require(len(b)==t['stdout_bytes'] and sha(b)==t['stdout_sha256'],'lossless payload')
    return json.loads(b)
def sealed(path: str,h: str) -> bytes:
    b=(ROOT/path).read_bytes();require(sha(b)==h,'sealed '+path);return b

class StaticResolver:
    """Restricted import/name/attribute lookup ONLY; not Python name resolution."""
    def __init__(self,texts: dict[str,str]):
        require(type(texts) is dict,'typed source registry')
        self.texts=texts;self.trees={};self.trace=[]
    def tree(self,module: str) -> ast.Module:
        require(type(module) is str and module.startswith('axial_') and module.isidentifier() and module in self.texts,'sealed known module')
        if module not in self.trees:
            text=self.texts[module]
            require(type(text) is str and len(text.encode())<=262144,'bounded module text')
            try:self.trees[module]=ast.parse(text)
            except (SyntaxError,RecursionError,ValueError) as error:raise ValueError('module syntax') from error
        return self.trees[module]
    def binding(self,module: str,name: str,trail: tuple=()) -> dict:
        require(type(name) is str and name.isidentifier(),'binding name')
        key=(module,name)
        require(key not in trail and len(trail)<64,'cycle/depth fail-closed')
        body=self.tree(module).body;rows=[]
        for n in body:
            if isinstance(n,ast.Import):
                for a in n.names:
                    if (a.asname or a.name.split('.')[0])==name:rows.append(('module',a.name,n))
            elif isinstance(n,ast.Assign):
                if any(isinstance(t,ast.Name) and t.id==name for t in n.targets):rows.append(('alias',n.value,n))
            elif isinstance(n,ast.FunctionDef) and n.name==name:rows.append(('function',name,n))
            elif isinstance(n,ast.ImportFrom):
                if any((a.asname or a.name)==name for a in n.names):rows.append(('unsupported',name,n))
            elif isinstance(n,(ast.AnnAssign,ast.AugAssign)) and isinstance(n.target,ast.Name) and n.target.id==name:
                rows.append(('unsupported',name,n))
        require(len(rows)==1,'unique simple binding '+module+'.'+name)
        kind,value,node=rows[0]
        self.trace.append({'module':module,'symbol':name,'first_line':node.lineno,
                           'AST_sha256':sha(dump(node).encode())})
        if kind=='module':
            self.tree(value)
            return {'kind':'module','module':value}
        if kind=='function':return {'kind':'function','module':module,'name':name}
        require(kind=='alias','unsupported binding form')
        return self.expr(module,value,trail+(key,))
    def expr(self,module: str,node: ast.AST,trail: tuple=()) -> dict:
        if isinstance(node,ast.Name):return self.binding(module,node.id,trail)
        if isinstance(node,ast.Attribute):
            obj=self.expr(module,node.value,trail)
            require(obj['kind']=='module','attribute base must be module')
            return self.binding(obj['module'],node.attr,trail)
        raise ValueError('only names/imported module attributes; no calls/eval')

def inspect_helpers(texts: dict[str,str]) -> dict:
    resolver=StaticResolver(texts);bindings={}
    for query,expected in QUERIES.items():
        endpoint=resolver.expr(ENTRY,ast.parse(query,mode='eval').body)
        require(endpoint['kind']=='function' and endpoint['module']+'.'+endpoint['name']==expected,'expected helper endpoint')
        functions=[n for n in resolver.tree(endpoint['module']).body if isinstance(n,ast.FunctionDef) and n.name==endpoint['name']]
        require(len(functions)==1,'unique helper function')
        node=functions[0];stamp=sha(dump(node).encode())
        require(stamp==EXPECTED[expected],'frozen helper AST boundary '+expected)
        bindings[query]={**endpoint,'first_line':node.lineno,'last_line':node.end_lineno,'AST_sha256':stamp}
    return {FLAG:True,'bindings':bindings,'alias_trace':resolver.trace,
            'parsed_module_count':len(resolver.trees),'boundary':dict(BOUNDARY),
            'target_imports':0,'native_calls':0,'status':'STOP'}

def retain_probe(probe: dict) -> dict:
    require(type(probe) is dict and digest(probe)==PROBE_DIGEST,'exact retained probe digest')
    require(probe['PASS'] is True and probe['binary64']['PASS'] is True,'typed retained probe PASS')
    rows=probe['binary32_cast_checks'];require(len(rows)==4 and probe['CPU_binary32_probe_casts']==4 and probe['CPU_binary64_probe_ops']==6,'retained ten probes')
    for row in rows:require(row['PASS'] is True and row['actual_uint32']==row['expected_uint32'],'retained cast words')
    gradual=[r for r in rows if r['label']=='gradual_cast32']
    require(len(gradual)==1 and type(gradual[0]['actual_uint32']) is int and gradual[0]['actual_uint32']==1,'retained subnormal cast NOT selected guard PASS')
    return {'retained_probe_sha256':PROBE_DIGEST,'retained_cast_checks':rows,
            'retained_binary64_checks':probe['binary64']['checks'],
            'retained_probe_observed_PASS':True,'new_probe_operations':0,'new_probe_casts':0,
            'retained_is_current_runtime_authentication':False,'subnormal_word1_is_selected_guard_admission':False}

def load_retained() -> tuple[dict,dict,dict,dict]:
    parent=json.loads(sealed(PARENT,PARENT_SHA))
    require(parent['task_id']=='AXIAL-SOURCE-ENCODER-GRAPH-AST-HOST-001','parent ID')
    pins={**parent['code_doc_sha256'],PARENT:PARENT_SHA}
    require(len(pins)==498 and pins.get(PROBE_REPORT)==PROBE_SHA,'complete inherited pins and probe lineage')
    for path,h in pins.items():sealed(path,h)
    texts={Path(path).stem:sealed(path,h).decode('utf-8') for path,h in pins.items()
           if path.startswith(DIR+'axial_') and path.endswith('.py')}
    retained=payload(json.loads(sealed(PROBE_REPORT,PROBE_SHA)))['data']['audit']
    require(retained['previous_SOURCE_eight_bit_FAILs_preserved'] is True and
            retained['previous_SOURCE_twelve_zero_sign_mismatches_preserved'] is True,'historical negative evidence retained')
    require(len(parent['proof_scope'])==38 and all(v is False for v in parent['proof_scope'].values()),'frozen general STOP scope')
    return texts,retained['runtime_probe'],pins,parent['proof_scope']

def audit_helper_boundary_HOST(*,model: str) -> dict:
    require(type(model) is str and model==MODEL,'explicit static retained-probe model')
    texts,probe,pins,false=load_retained()
    retained=retain_probe(probe) # sealed probe checked BEFORE static emission
    result=inspect_helpers(texts)
    return {'model':MODEL,'audit':result,'probe':retained,'inherited_pins_verified':len(pins),
            'proof_scope':false,'historical_negative_markers_retained':True,
            'actual_scene_domain_grid_authenticated':False,'encoder_graph_execution_authenticated':False,
            'uniform_executed_SOURCE_error_L1':None,'group_admissions':0,
            'old_producers_and_numerical_controls_reexecuted':0,'status':'STOP'}
