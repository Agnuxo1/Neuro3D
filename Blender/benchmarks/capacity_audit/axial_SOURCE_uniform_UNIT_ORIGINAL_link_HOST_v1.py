"""HOST SOURCE-box UNIT-to-ORIGINAL link; frozen geometry, no execution admission."""
import ast
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
import axial_SOURCE_uniform_complex_product_HOST_v1 as prior
import axial_guarded_source_product_RN64_CPU_v1 as producer
io,allocation,require,digest,pair=prior.io,prior.allocation,prior.require,prior.digest,prior.pair
domain,guard,FALSE=prior.domain,prior.guard,prior.FALSE
MODEL='axial-SOURCE-box-fixed-geometry-UNIT-ORIGINAL-link-HOST-v1'
FLAG='SOURCE_box_UNIT_ORIGINAL_error_link_HOST_proved'
PARENT='coordinacion/respuestas/AXIAL-SOURCE-UNIFORM-COMPLEX-PRODUCT-HOST-001-CODEX.json'
PARENT_SHA='f91e68a2fe8655827c3c1259db89a2caeffafa2ba5c0f02a4cbf4b826d59fd65'
UNIT=producer.PREVIOUS
ARITH=prior.ARITH
DEPS=('argument_uint64','coefficient_profile_sha256','quadrant_mod4','unchanged_phase_cap_rad','upstream_phase_bound_rad','upstream_phase_charges_rad')
GRAPH='Blender/benchmarks/capacity_audit/axial_guarded_argument_unit_RN64_CPU_v1.py'

def dependency_contract(text):
    tree=ast.parse(text);fn=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='execute']
    require(len(fn)==1 and [a.arg for a in fn[0].args.args]==['admission','profile'],'frozen UNIT interface')
    subs=[n for n in ast.walk(fn[0]) if isinstance(n,ast.Subscript) and isinstance(n.value,ast.Name) and n.value.id=='admission']
    require(all(isinstance(n.slice,ast.Constant) and type(n.slice.value) is str for n in subs),'no dynamic UNIT admission access')
    require(sorted({n.slice.value for n in subs})==list(DEPS),'exact fixed UNIT numerical admission dependencies')
    # Not a general symbolic dependency analyser. SHA pins freeze all helpers/globals;
    # manual graph contract + this narrow regression guard apply only to this graph.
    return {'graph':GRAPH,'execute_parameters':['admission','profile'],'numerical_admission_keys':list(DEPS),
            'SOURCE_field_reim_read_by_execute':False,'scope':domain.SCOPE,
            'not_general_dependency_analysis':True}

def load_retained():
    r=allocation.parse(io.read(PARENT,PARENT_SHA));require(r['task_id']=='AXIAL-SOURCE-UNIFORM-COMPLEX-PRODUCT-HOST-001','parent identity')
    pins=io.pins_from(r);pins[PARENT]=PARENT_SHA
    for p,h in pins.items():io.read(p,h)
    packets,data,enc,neg,bare,oldpins=prior.load_retained()
    require(all(pins.get(p)==h for p,h in oldpins.items()),'same SOURCE lineage')
    unit=io.payload(allocation.parse(io.read(UNIT,pins[UNIT])))['data']['audit']
    deps=dependency_contract(io.read(GRAPH,pins[GRAPH]).decode('utf-8'))
    return packets,data,enc,neg,bare,io.payload(r)['data'],unit,deps,pins

def link_bound_HOST(box,unit_charges,*,model,arithmetic_model):
    require(type(model) is str and model==MODEL and type(arithmetic_model) is str and arithmetic_model==ARITH,'explicit fixed-geometry model')
    values=domain.box_values(box)
    require(type(unit_charges) is dict and set(unit_charges)==set(producer.UNIT_NAMES),'exact eleven UNIT charges')
    charges={n:domain.rational(v) for n,v in unit_charges.items()}
    require(all(v>=0 for v in charges.values()) and sum(charges.values(),F(0))<1,'nonnegative small retained UNIT bound')
    maxima=[max(abs(lo),abs(hi)) for lo,hi in values];S=sum(maxima,F(0))
    scaled={'source_unit_'+n:S*v for n,v in charges.items()}
    return {'model':MODEL,'arithmetic_model':ARITH,'box_reim':deepcopy(box),
        'ORIGINAL_SOURCE_component_max':list(map(pair,maxima)),'ORIGINAL_SOURCE_box_norm_L1_bound':pair(S),
        'fixed_UNIT_charges_to_ORIGINAL_L1':deepcopy(unit_charges),
        'charges_L1':{n:pair(v) for n,v in scaled.items()},
        'uniform_A_times_UNIT_error_to_A_times_ideal_UNIT_L1':pair(sum(scaled.values(),F(0))),
        'ideal_target':'variable ORIGINAL A times exp(i fixed ORIGINAL theta); bare, before material',
        FLAG:True,'unit_input_scope':'fixed ORIGINAL geometry/wavelength/path/gauges; SOURCE field reim only varies',
        'frozen_guard_admission_for_entire_box_proved':False,'uniform_SOURCE_enclosure_proved':False,
        'uniform_executed_SOURCE_error_L1':None,'phase_bound_rad':None,'status':'STOP',**dict.fromkeys(FALSE,False)}

def audit_link_HOST(variant,*,model,arithmetic_model):
    require(type(variant) is str and variant in prior.encoder.VARIANTS and model==MODEL and arithmetic_model==ARITH,'explicit variant/model')
    packets,data,enc,neg,bare,products,unit,deps,pins=load_retained()
    require(deps==dependency_contract(io.read(GRAPH,pins[GRAPH]).decode('utf-8')),'same pinned dependency contract')
    old=data['synthetic_scene_domains'] if variant=='synthetic_domains' else data['real_missing']
    plans=data['synthetic_domain_INPUT_plans'] if variant=='synthetic_domains' else {};checked={}
    for name in old['case_order']:
        ctx=allocation.context_from_packet(packets[name],digest(packets[name]),model=allocation.MODEL)
        pc=products[variant]['cases'][name];uc=unit['cases'][name];bc=bare['cases'][name]
        require(ctx==old['cases'][name]['context']==enc[variant]['cases'][name]['context']==neg[variant]['cases'][name]['context']==pc['context']==uc['context']==bc['context'],'same full ORIGINAL context')
        dom=domain.validate_domain(packets[name],ctx,plans.get(name))
        require(digest(dom)==digest(old['cases'][name]['domain_INPUT']),'unchanged full typed SOURCE domain')
        rows=None
        if dom['domain_INPUT_valid']:
            expected=ctx['source_order']
            for c in (pc,uc,bc):require(type(c['sources']) is list and [s['source_id'] for s in c['sources']]==expected,'complete ordered lineage')
            rows=[]
            for s,p,u,b in zip(dom['sources'],pc['sources'],uc['sources'],bc['sources']):
                require(s['source_id']==p['source_id']==u['source_id']==b['source_id'] and p['domain_source_sha256']==digest(s),'same SOURCE binding')
                require(u[producer.prior.FLAG] is True and b[prior.BARE_FLAG] is True and p['whole_box_guard_admission_disproved'] is True,'typed retained partial eligibility and guard STOP')
                require(u['phase_reference_id']==b['phase_reference_id']==s['source_phase_reference_id'] and
                    u['terminal_reference_id']==b['terminal_reference_id']==s['terminal_reference_id']==s['common_terminal_reference_id'],'fixed SOURCE/terminal gauges')
                require(b['retained_row_sha256']==b['admission']['retained_unit_row_sha256']==digest(u) and p['retained_bare_SOURCE_row_sha256']==digest(b),'exact typed UNIT/bare/product row digests')
                v=producer.validate_retained_unit(u['admission'],unit['coefficient_profile'],u['result'])
                a=b['admission'];proof=p['proof']
                require(digest(a['unit_L1_charges'])==digest(v['unit_L1_charges_to_FIXED_ORIGINAL']) and a['unit_L1_bound']==v['point_unit_L1_bound_to_FIXED_ORIGINAL'],'exact eleven charges, not point SOURCE epsilon')
                require(digest(a['unit_uint64'])==digest(v['unit_uint64'])==digest(proof['fixed_represented_UNIT_uint64']) and proof['box_reim']==s['box_reim'],'same fixed represented UNIT and box')
                require(proof[prior.FLAG] is True and proof['UNIT_error_to_ORIGINAL_included'] is False and
                    proof['frozen_guard_admission_for_entire_box_proved'] is False and proof['uniform_SOURCE_enclosure_proved'] is False and
                    all(proof[k] is False for k in FALSE),'partial product ONLY')
                # Existing product stage is immutable and SHA pinned, not recomputed.
                q={n:domain.rational(v) for n,v in proof['charges_L1'].items()}
                require(set(q)=={'source_encoding_times_UNIT_L1','source_decode_times_UNIT_L1','product_six_RN64_nodes_L1'} and
                    all(v>=0 for v in q.values()) and sum(q.values(),F(0))==domain.rational(proof['uniform_error_to_A_times_fixed_represented_UNIT_L1']),'separate retained product total ONCE')
                rows.append((s,p,u,b))
        else:require(pc['sources'] is None,'missing SOURCE domain means no point UNIT inspection')
        checked[name]=(ctx,dom,rows)
    cases={};count=0
    # ALL INPUT and rational retained UNIT proof checks above before any new link.
    for name,(ctx,dom,rows) in checked.items():
        out=None
        if rows is not None:
            out=[]
            for s,p,u,b in rows:
                link=link_bound_HOST(s['box_reim'],b['admission']['unit_L1_charges'],model=model,arithmetic_model=arithmetic_model)
                charges={**deepcopy(p['proof']['charges_L1']),**deepcopy(link['charges_L1'])}
                total=sum((domain.rational(v) for v in charges.values()),F(0));require(len(charges)==14,'fourteen separate charges ONCE')
                out.append({'source_id':s['source_id'],'domain_source_sha256':digest(s),'retained_product_source_sha256':digest(p),
                    'retained_UNIT_source_sha256':digest(u),'retained_bare_SOURCE_row_sha256':digest(b),
                    'link':link,'bare_charges_L1':charges,'uniform_bare_RN_model_bound_to_A_times_ideal_UNIT_L1':pair(total),
                    'whole_box_guard_admission_disproved':True,'material_included':False,
                    'uniform_executed_SOURCE_error_L1':None,'phase_bound_rad':None,'status':'STOP',**dict.fromkeys(FALSE,False)})
                count+=1
        cases[name]={'context':ctx,'domain_INPUT_valid':dom['domain_INPUT_valid'],'sources':out,'status':'STOP',
            'group_phase_bound_rad':None,'group_field_bound_L1':None,**dict.fromkeys(FALSE,False)}
    return {'model':MODEL,'variant':variant,'case_order':deepcopy(old['case_order']),'cases':cases,'dependency_contract':deepcopy(deps),
        'inherited_pins_verified':len(pins),'analytical_UNIT_links':count,'blocked_guard_boxes_preserved':count,
        'new_native_operations':0,'old_suites_producers_reexecuted':0,'group_admissions':0,
        'uniform_SOURCE_enclosure_proved':False,'cost_scope':'HOST conditional bare RN model only; full costs UNMEASURED NOT zero',**dict.fromkeys(FALSE,False)}
