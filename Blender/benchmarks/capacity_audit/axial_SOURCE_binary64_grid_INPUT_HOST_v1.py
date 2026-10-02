"""Explicit binary64-grid SOURCE INPUT binding; syntax only, no word-class replay."""
from copy import deepcopy
import axial_SOURCE_binary64_encoder_wordclass_HOST_v1 as prior
io,allocation,require,digest=prior.io,prior.allocation,prior.require,prior.digest
domain,FALSE=prior.domain,prior.FALSE
MODEL='axial-SOURCE-binary64-grid-snapshot-encoder-INPUT-HOST-v1'
FLAG='SOURCE_binary64_grid_INPUT_bound_HOST'
PARENT='coordinacion/respuestas/AXIAL-SOURCE-BINARY64-ENCODER-WORDCLASS-HOST-001-CODEX.json'
PARENT_SHA='78249147dca45e62cf0ae1e4e9a87cb774f3e000a07da5d6ec81d47d8cb5f748'
PROGRAM='Blender/benchmarks/capacity_audit/axial_guarded_source_product_RN64_CPU_v1.py'
PROGRAM_SHA='611b9f628c0599278938657a5154615bb22fe998ebd62f45e3a1dbad9c154bdc'
GRAPH={'limb_wire_abi':'4x uint32 little-endian; real.high real.low imag.high imag.low','component_order':['real','imag'],'limb_order':['real.high','real.low','imag.high','imag.low'],
       'nodes_per_component':[['high','RN32','ORIGINAL'],
          ['residual','RN64-sub','ORIGINAL','widen64(high)'],
          ['low','RN32','residual'],['decode','RN64-add','widen64(high)','widen64(low)']],
       'widening':'exact binary32 to binary64','signed_zero':'IEEE node signs; no canonicalization',
       'covered':'encoder/decode only; no UNIT product/material/transport/field'}
GAUGES=('source_id','source_phase_reference_id','terminal_reference_id','common_terminal_reference_id')
PLAN_KEYS={'model','grid','arithmetic_model','packet_sha256','context_sha256','original_snapshot_sha256',
           'domain_sha256','scope','encoder_program_path','encoder_program_sha256','encoder_graph','sources'}
SOURCE_KEYS=set(GAUGES)|{'domain_source_sha256','ORIGINAL_source_uint64'}
def load_retained():
    r=allocation.parse(io.read(PARENT,PARENT_SHA));require(r['task_id']=='AXIAL-SOURCE-BINARY64-ENCODER-WORDCLASS-HOST-001','parent identity')
    pins=io.pins_from(r);pins[PARENT]=PARENT_SHA
    for p,h in pins.items():io.read(p,h)
    require(pins[PROGRAM]==PROGRAM_SHA,'frozen encoder pin')
    loaded=prior.load_retained();require(all(pins.get(p)==h for p,h in loaded[-1].items()),'same retained ORIGINAL/domains')
    return loaded[0],loaded[1],io.payload(r)['data'],pins

def validate_plan(packet,expected_packet_sha256,domain_plan,plan,*,model):
    require(type(model) is str and model==MODEL,'explicit binary64-grid INPUT model')
    ctx=allocation.context_from_packet(packet,expected_packet_sha256,model=allocation.MODEL)
    dom=domain.validate_domain(packet,ctx,domain_plan)
    base={FLAG:False,'context_sha256':digest(ctx),'domain_sha256':dom.get('domain_sha256'),
          'domain_INPUT_valid':dom['domain_INPUT_valid'],'sources':None,
          'actual_scene_domain_grid_authenticated':False,'encoder_graph_execution_authenticated':False,
          'frozen_guard_admission_for_entire_box_proved':False,'uniform_executed_SOURCE_error_L1':None,
          'phase_INPUT_quota_fits':None,'status':'STOP',**dict.fromkeys(FALSE,False)}
    if plan is None:return ctx,{**base,'reason':'missing explicit grid INPUT; snapshot anchor alone does not change domain semantics'}
    require(dom['domain_INPUT_valid'] is True,'explicit whole SOURCE domain required; no anchor fallback')
    require(type(plan) is dict and set(plan)==PLAN_KEYS,'exact new INPUT whitelist; no proof/authority/output/bounds adapter')
    for k,v in (('model',MODEL),('grid',prior.GRID),('arithmetic_model',prior.ARITH),
                ('packet_sha256',expected_packet_sha256),('context_sha256',digest(ctx)),
                ('original_snapshot_sha256',ctx['original_snapshot_sha256']),('domain_sha256',dom['domain_sha256']),
                ('scope',domain.SCOPE),('encoder_program_path',PROGRAM),('encoder_program_sha256',PROGRAM_SHA)):
        require(type(plan[k]) is str and plan[k]==v,'exact grid/model/arithmetic/ORIGINAL/domain/encoder binding: '+k)
    require(type(plan['encoder_graph']) is dict and digest(plan['encoder_graph'])==digest(GRAPH),'exact encoder graph; no FMA/reorder/canonicalization/product substitution')
    rows=plan['sources']
    require(type(rows) is list and len(rows)==len(ctx['source_order']) and
            all(type(s) is dict and set(s)==SOURCE_KEYS for s in rows),'complete source INPUT row whitelist')
    require([s['source_id'] for s in rows]==ctx['source_order']==[s['source_id'] for s in dom['sources']],'complete ordered SOURCE domain coverage')
    for row,a,src in zip(rows,ctx['assignments'],dom['sources']):
        for k in GAUGES:require(type(row[k]) is str and row[k]==a[k]==src[k],'exact source/terminal gauges')
        require(a['terminal_reference_id']==a['common_terminal_reference_id'],'fixed common terminal gauge')
        require(type(row['domain_source_sha256']) is str and row['domain_source_sha256']==digest(src),'complete SOURCE domain SHA')
        words=row['ORIGINAL_source_uint64']
        require(type(words) is list and len(words)==2 and all(type(w) is int and 0<=w<2**64 for w in words),'typed original uint64 pair; bool/float invalid')
        for w in words:
            exp=(w>>52)&2047;frac=w&((1<<52)-1)
            require(0<exp<2047 or exp==frac==0,'normal-or-zero ORIGINAL words only')
        require(words==src['ORIGINAL_source_uint64'],'exact ORIGINAL snapshot words, signed zero bits never normalized')
    return ctx,{**base,FLAG:True,'model':MODEL,'grid':prior.GRID,'arithmetic_model':prior.ARITH,
        'packet_sha256':expected_packet_sha256,'original_snapshot_sha256':ctx['original_snapshot_sha256'],
        'scope':domain.SCOPE,'encoder_program_path':PROGRAM,'encoder_program_sha256':PROGRAM_SHA,
        'encoder_graph':deepcopy(GRAPH),'plan_sha256':digest(plan),'sources':deepcopy(rows),
        'reason':'explicit declared finite-grid INPUT bound to snapshot/domain/program/graph; syntax not scene authority, word-class theorem, execution or guard admission'}

def audit_INPUT_HOST(case_order,domain_plans,plans,packets,*,model):
    require(type(model) is str and model==MODEL,'explicit new INPUT model')
    require(type(case_order) is list and 1<=len(case_order)<=64 and all(type(n) is str and n for n in case_order)
            and len(set(case_order))==len(case_order),'bounded unique case order')
    require(type(plans) is dict and set(plans)<=set(case_order) and type(domain_plans) is dict
            and set(domain_plans)<=set(case_order),'selected grid/domain INPUT keys only')
    require(type(packets) is dict and set(case_order)<=set(packets),'complete packet coverage')
    cases={}
    # Whole batch INPUT only: no old numerical predicate/certificates, including on valid schema.
    for name in case_order:
        ctx,v=validate_plan(packets[name],digest(packets[name]),domain_plans.get(name),plans.get(name),model=model)
        cases[name]={'context':ctx,'INPUT':v,'status':'STOP',**dict.fromkeys(FALSE,False)}
    return {'model':MODEL,'case_order':deepcopy(case_order),'cases':cases,
        'valid_INPUT_cases':sum(c['INPUT'][FLAG] for c in cases.values()),
        'missing_INPUT_cases':sum(not c['INPUT'][FLAG] for c in cases.values()),
        'wordclass_predicate_assessments':0,'certificate_inspections':0,'new_native_operations':0,
        'old_suites_producers_reexecuted':0,'old_counterexamples_reexecuted':0,'group_admissions':0,
        'actual_scene_domain_grid_authenticated':False,'encoder_graph_execution_authenticated':False,
        'cost_scope':'HOST INPUT syntax/binding only; IO/setup/upstream/full UNMEASURED NOT zero',**dict.fromkeys(FALSE,False)}
