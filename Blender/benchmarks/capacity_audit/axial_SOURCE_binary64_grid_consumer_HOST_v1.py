"""SHA-sealed retained wordclass certificate -> explicit GRID INPUT consumer, HOST only."""
from copy import deepcopy
import axial_SOURCE_binary64_grid_INPUT_HOST_v1 as prior
io,allocation,require,digest=prior.io,prior.allocation,prior.require,prior.digest
domain,FALSE=prior.domain,prior.FALSE
theorem=prior.prior
MODEL='axial-SOURCE-binary64-grid-INPUT-retained-wordclass-consumer-HOST-v1'
BOUND='retained_wordclass_certificate_bound_to_GRID_INPUT_HOST'
SUFFICIENT='conditional_encoder_numeric_wordclasses_sufficient_HOST'
PARENT='coordinacion/respuestas/AXIAL-SOURCE-BINARY64-GRID-INPUT-HOST-001-CODEX.json'
PARENT_SHA='3eb8e18e7740f7448d92a9e459427ad3a2dd28e58d73c7f950c75417a3db94ff'
VARIANTS=('real_missing','explicit_None_missing','domain_present_grid_missing','synthetic_valid')
CERT_KEYS={'source_id','domain_source_sha256','components',theorem.FLAG,'retained_consumer_SOURCE_sha256',
           'retained_whole_box_guard_admission_disproved','actual_scene_domain_grid_authenticated',
           'frozen_guard_admission_for_entire_box_proved','uniform_executed_SOURCE_error_L1','status'}|set(FALSE)
def load_retained():
    r=allocation.parse(io.read(PARENT,PARENT_SHA));require(r['task_id']=='AXIAL-SOURCE-BINARY64-GRID-INPUT-HOST-001','parent identity')
    pins=io.pins_from(r);pins[PARENT]=PARENT_SHA
    for p,h in pins.items():io.read(p,h)
    loaded=prior.load_retained();require(all(pins.get(p)==h for p,h in loaded[-1].items()),'same fixed ORIGINAL/GRID/wordclass lineage')
    # Seal is derived ONLY from the already SHA-verified immutable theorem receipt.
    certs=loaded[2]['synthetic_valid']['cases']
    seals={name:{s['source_id']:digest(s) for s in v['sources']} for name,v in certs.items()}
    return loaded[0],loaded[1],loaded[2],io.payload(r)['data'],pins,seals

def inspect_retained_SOURCE_HOST(ctx,src,grid_row,cert,expected_seal):
    require(type(expected_seal) is str and len(expected_seal)==64 and all(x in '0123456789abcdef' for x in expected_seal),'trusted SHA seal from pinned antecedent')
    require(type(cert) is dict and set(cert)==CERT_KEYS and digest(cert)==expected_seal,'exact sealed SOURCE certificate, no caller proof/authority substitution')
    require(cert['source_id']==src['source_id']==grid_row['source_id'] and
            cert['domain_source_sha256']==grid_row['domain_source_sha256']==digest(src),'whole-domain SOURCE/grid/cert same binding')
    require(grid_row['ORIGINAL_source_uint64']==src['ORIGINAL_source_uint64'],'same exact original uint64 anchor, no signzero normalization')
    require(cert['status']=='STOP' and all(cert[k] is False for k in FALSE) and
            cert['actual_scene_domain_grid_authenticated'] is cert['frozen_guard_admission_for_entire_box_proved'] is False and
            cert['uniform_executed_SOURCE_error_L1'] is None,'retained conditional certificate is not authority/execution')
    negative=cert['retained_whole_box_guard_admission_disproved']
    require(negative is None or negative is True,'retained negative guard evidence typed; UNKNOWN not PASS')
    comps=cert['components'];require(type(comps) is list and len(comps)==2,'two complete retained component certificates')
    flags=[]
    for comp,interval in zip(comps,src['box_reim']):
        require(comp['model']==theorem.MODEL and comp['explicit_grid_assumption']==theorem.GRID and
                comp['arithmetic_model']==theorem.ARITH and comp['interval']==interval,'same entire component interval and explicit arithmetic/grid hypothesis')
        require(type(comp[theorem.FLAG]) is bool,'typed retained sufficient flag')
        require(comp['status']=='STOP' and all(comp[k] is False for k in FALSE) and
                comp['actual_scene_domain_grid_authenticated'] is comp['all_real_continuum_wordclasses_proved'] is
                comp['frozen_guard_admission_for_entire_box_proved'] is comp['signed_zero_execution_policy_proved'] is
                comp['SOURCE_graph_executed'] is False and
                comp['frozen_guard_verdict'] is comp['uniform_executed_SOURCE_error_L1'] is None,'component proof not actual scene/guard/signed-zero execution')
        require((comp['proof'] is not None) is comp[theorem.FLAG],'retained proof present exactly when sufficient')
        flags.append(comp[theorem.FLAG])
    require(type(cert[theorem.FLAG]) is bool and cert[theorem.FLAG] is all(flags),'typed complete two-component sufficient conjunction')
    if negative is True:require(cert[theorem.FLAG] is False,'negative guard evidence never promoted')
    return {'source_id':src['source_id'],'domain_source_sha256':digest(src),
        'GRID_INPUT_source_sha256':digest(grid_row),'retained_SOURCE_certificate_sha256':expected_seal,
        'retained_component_certificate_sha256':[digest(c) for c in comps],
        'component_sufficient_flags':flags,SUFFICIENT:cert[theorem.FLAG],
        'retained_whole_box_guard_admission_disproved':negative,
        'scope':'retained conditional numeric wordclasses joined to explicit GRID INPUT; not execution/actual guard'}

def emit_conditional_SOURCE_HOST(inspected):
    return {**deepcopy(inspected),BOUND:True,'model':MODEL,
        'actual_scene_domain_grid_authenticated':False,'encoder_graph_execution_authenticated':False,
        'frozen_guard_admission_for_entire_box_proved':False,'uniform_executed_SOURCE_error_L1':None,
        'phase_INPUT_quota_fits':None,'status':'STOP',**dict.fromkeys(FALSE,False)}

def audit_consumer_HOST(variant,*,model):
    require(type(model) is str and model==MODEL and type(variant) is str and variant in VARIANTS,'explicit retained consumer variant/model')
    packets,inputs,certs,grid,pins,seals=load_retained()
    base=grid[variant];names=base['case_order'];withdom=variant in ('domain_present_grid_missing','synthetic_valid')
    domains=inputs['synthetic_domain_INPUT_plans'] if withdom else {}
    plans=grid['synthetic_grid_INPUT_plans'] if variant=='synthetic_valid' else {}
    # ALL typed complete INPUT before ANY certificate inspection; no old mathematical predicates.
    fresh=prior.audit_INPUT_HOST(names,domains,plans,packets,model=prior.MODEL)
    require(digest(fresh)==digest(base),'same full retained validated GRID INPUT, not output-fitted declaration')
    prepared={}
    for name in names:
        case=fresh['cases'][name];ctx=case['context'];v=case['INPUT']
        require(digest(ctx)==digest(inputs['synthetic_valid' if withdom else 'real_missing']['cases'][name]['context'])
                ==digest(certs['synthetic_valid' if withdom else 'real_missing']['cases'][name]['context']),'same complete ORIGINAL INPUT context')
        dom=None
        if v[prior.FLAG]:
            dom=domain.validate_domain(packets[name],ctx,domains[name])
            require(digest(dom)==digest(inputs['synthetic_validated_domains'][name]),'same complete validated domain')
        prepared[name]=(ctx,v,dom)
    # ALL certificates before ANY result binding/emission. Missing INPUT cannot inspect points.
    inspected={}
    for name,(ctx,v,dom) in prepared.items():
        rows=None
        if v[prior.FLAG]:
            previous=certs['synthetic_valid']['cases'][name]['sources']
            require(type(previous) is list and [s['source_id'] for s in previous]==ctx['source_order'] and
                    set(seals[name])==set(ctx['source_order']),'complete ordered trusted certificate coverage')
            rows=[inspect_retained_SOURCE_HOST(ctx,src,g,cert,seals[name][src['source_id']])
                  for src,g,cert in zip(dom['sources'],v['sources'],previous)]
        inspected[name]=rows
    cases={};count=sufficient=negative=0
    for name,(ctx,v,dom) in prepared.items():
        rows=inspected[name];out=None if rows is None else [emit_conditional_SOURCE_HOST(x) for x in rows]
        if out is not None:
            count+=len(out);sufficient+=sum(x[SUFFICIENT] for x in out)
            negative+=sum(x['retained_whole_box_guard_admission_disproved'] is True for x in out)
        cases[name]={'context':ctx,'GRID_INPUT':v,'sources':out,'group_field_bound_L1':None,
            'group_phase_bound_rad':None,'status':'STOP',**dict.fromkeys(FALSE,False)}
    return {'model':MODEL,'variant':variant,'case_order':deepcopy(names),'cases':cases,'inherited_pins_verified':len(pins),
        'retained_SOURCE_certificate_inspections':count,'bound_SOURCE_certificates':count,
        'conditional_sufficient_SOURCE_count':sufficient,'retained_negative_guard_SOURCE_count':negative,
        'new_wordclass_predicates':0,'new_native_operations':0,'old_suites_producers_reexecuted':0,
        'old_counterexamples_reexecuted':0,'group_admissions':0,'actual_scene_domain_grid_authenticated':False,
        'encoder_graph_execution_authenticated':False,
        'cost_scope':'HOST pinned certificate INPUT consumer only; IO/setup/upstream/full UNMEASURED NOT zero',
        **dict.fromkeys(FALSE,False)}
