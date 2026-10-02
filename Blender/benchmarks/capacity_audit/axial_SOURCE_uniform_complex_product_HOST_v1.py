"""HOST uniform variable SOURCE box times fixed represented UNIT; not scene/guard admission."""
from copy import deepcopy
from fractions import Fraction as F
import axial_SOURCE_box_guard_counterexample_HOST_v1 as prior
encoder=prior.prior
guard,domain=prior.guard,prior.domain
io,allocation,require,digest,pair=prior.io,prior.allocation,prior.require,prior.digest,prior.pair
FALSE=prior.FALSE
MODEL='axial-variable-SOURCE-box-fixed-represented-UNIT-uniform-product-HOST-v1'
FLAG='uniform_bare_product_to_fixed_represented_UNIT_bound_HOST_proved'
ARITH=encoder.ARITHMETIC_MODEL
PARENT='coordinacion/respuestas/AXIAL-SOURCE-BOX-GUARD-COUNTEREXAMPLE-HOST-001-CODEX.json'
PARENT_SHA='54ec7a9d9dcb98354685d7751ad1ed14012e05497543f520d54f05a3e1583f35'
BARE='coordinacion/respuestas/AXIAL-GUARDED-SOURCE-PRODUCT-RN64-CPU-001-CODEX.json'
BARE_FLAG='guarded_source_product_RN64_CPU_executed'
LABELS=('ac','bd','ad','bc','real','imag')

def validate_encoder(b):
    require(type(b) is dict and b['model']==encoder.MODEL and b['arithmetic_model']==ARITH and b[encoder.FLAG] is True,'typed retained encoder model')
    require(b['uniform_executed_SOURCE_error_L1'] is None and b['phase_bound_rad'] is None and b['uniform_SOURCE_enclosure_proved'] is False and
            b['frozen_guard_admission_for_entire_box_proved'] is False and all(b[k] is False for k in FALSE),'encoder ONLY; no broad admission')
    intervals=domain.box_values(b['box_reim']);require(type(b['components']) is list and len(b['components'])==2,'complete component envelope')
    E=D=F(0);maxima=[]
    # Verify existing equations, not regenerate old stage or execute a producer.
    for (lo,hi),c in zip(intervals,b['components']):
        m=max(abs(lo),abs(hi));eh=encoder.rounding(m,32);er=encoder.rounding(eh,64);el=encoder.rounding(eh+er,32)
        enc=er+el;ed=encoder.rounding(m+enc,64)
        expected={'max_abs_ORIGINAL_component':m,'high_cast_error_bound':eh,'high_output_max_bound':m+eh,
            'exact_residual_max_bound':eh,'residual_RN64_error_bound':er,'residual_output_max_bound':eh+er,
            'low_cast_error_bound':el,'low_output_max_bound':eh+er+el,'encoding_error_bound':enc,
            'exact_decode_sum_max_bound':m+enc,'decode_RN64_error_bound':ed,
            'decoded_output_max_bound':m+enc+ed,'encoding_plus_decode_bound':enc+ed}
        require(type(c) is dict and set(c)==set(expected) and all(domain.rational(c[k])==x for k,x in expected.items()),'exact retained component equations')
        require(m+eh<=encoder.MAX[32] and eh+er+el<=encoder.MAX[32] and m+enc+ed<=encoder.MAX[64],'same conservative finite margins')
        E+=enc;D+=ed;maxima.append(m+enc+ed)
    require(domain.rational(b['source_encoding_uniform_L1_bound'])==E and domain.rational(b['source_decode_RN64_uniform_L1_bound'])==D and
            domain.rational(b['source_encoding_plus_decode_uniform_L1_bound'])==E+D,'separate charges, exact ONCE total')
    return maxima,E,D

def node_majorant(m,label,op):
    require(type(m) is F and m>=0 and label in LABELS and op in ('mul','add'),'typed exact node magnitude')
    e=encoder.rounding(m,64);out=m+e
    require(out<=encoder.MAX[64],'conservative output margin; no overflow/clamp')
    return {'label':label,'op':op,'exact_argument_max':pair(m),'RN64_error_bound':pair(e),'output_max':pair(out)}

def product_bound_HOST(b,unit_words,*,model,arithmetic_model):
    require(type(model) is str and model==MODEL and type(arithmetic_model) is str and arithmetic_model==ARITH,'explicit product RN gradual/noFMA model')
    maxima,E,D=validate_encoder(b)
    require(type(unit_words) is list and len(unit_words)==2,'two fixed typed UNIT words')
    u=[guard.bits(w,64) for w in unit_words];a,bmax=maxima;c,d=map(abs,u)
    magnitudes=[a*c,bmax*d,a*d,bmax*c]
    nodes=[node_majorant(m,l,'mul') for m,l in zip(magnitudes,LABELS[:4])]
    for l,i,j in (('real',0,1),('imag',2,3)):
        nodes.append(node_majorant(domain.rational(nodes[i]['output_max'])+domain.rational(nodes[j]['output_max']),l,'add'))
    N=sum((domain.rational(n['RN64_error_bound']) for n in nodes),F(0));L=sum(map(abs,u),F(0))
    charges={'source_encoding_times_UNIT_L1':E*L,'source_decode_times_UNIT_L1':D*L,'product_six_RN64_nodes_L1':N}
    return {'model':MODEL,'arithmetic_model':ARITH,'box_reim':deepcopy(b['box_reim']),'encoder_bound_sha256':digest(b),
        'fixed_represented_UNIT_uint64':deepcopy(unit_words),'fixed_represented_UNIT_reim':list(map(pair,u)),
        'represented_UNIT_norm_L1':pair(L),'decoded_SOURCE_component_max':list(map(pair,maxima)),
        'nodes':nodes,'charges_L1':{k:pair(x) for k,x in charges.items()},
        'uniform_error_to_A_times_fixed_represented_UNIT_L1':pair(sum(charges.values(),F(0))),FLAG:True,
        'ideal_target':'variable ORIGINAL A times FIXED represented UNIT; not ORIGINAL ideal exp(i theta)',
        'UNIT_error_to_ORIGINAL_included':False,'material_reduction_projection_included':False,
        'uniform_executed_SOURCE_error_L1':None,'uniform_SOURCE_enclosure_proved':False,
        'phase_bound_rad':None,'frozen_guard_admission_for_entire_box_proved':False,
        'device_model_authenticated':False,'signed_zero_execution_policy_proved':False,
        'status':'STOP',**dict.fromkeys(FALSE,False)}

def load_retained():
    r=allocation.parse(io.read(PARENT,PARENT_SHA));require(r['task_id']=='AXIAL-SOURCE-BOX-GUARD-COUNTEREXAMPLE-HOST-001','parent identity')
    pins=io.pins_from(r);pins[PARENT]=PARENT_SHA
    for p,h in pins.items():io.read(p,h)
    packets,data,enc,oldpins=prior.load_retained()
    require(all(pins.get(p)==h for p,h in oldpins.items()),'same immutable encoder/domain branches')
    bare=io.payload(allocation.parse(io.read(BARE,pins[BARE])))['data']['audit']
    return packets,data,enc,io.payload(r)['data'],bare,pins

def audit_uniform_product_HOST(variant,*,model,arithmetic_model):
    require(type(variant) is str and variant in encoder.VARIANTS and type(model) is str and model==MODEL and
            type(arithmetic_model) is str and arithmetic_model==ARITH,'explicit retained variant/product model')
    packets,data,enc,negative,bare,pins=load_retained()
    old=data['synthetic_scene_domains'] if variant=='synthetic_domains' else data['real_missing']
    plans=data['synthetic_domain_INPUT_plans'] if variant=='synthetic_domains' else {};checked={}
    for name in old['case_order']:
        ctx=allocation.context_from_packet(packets[name],digest(packets[name]),model=allocation.MODEL)
        ec=enc[variant]['cases'][name];gc=negative[variant]['cases'][name];bc=bare['cases'][name]
        require(ctx==old['cases'][name]['context']==ec['context']==gc['context']==bc['context'],'same full ORIGINAL SOURCE/UNIT context')
        dom=domain.validate_domain(packets[name],ctx,plans.get(name))
        require(digest(dom)==digest(old['cases'][name]['domain_INPUT']),'exact typed domain INPUT')
        rows=None
        if dom['domain_INPUT_valid']:
            require(all(type(v['sources']) is list and len(v['sources'])==len(dom['sources']) for v in (ec,gc,bc)),'complete ordered certificates')
            rows=[]
            for src,e,g,b in zip(dom['sources'],ec['sources'],gc['sources'],bc['sources']):
                require(src['source_id']==e['source_id']==g['source_id']==b['source_id'] and
                        digest(src)==e['domain_source_sha256']==g['domain_source_sha256'],'same complete SOURCE domain bindings')
                proof=g['proof']
                require(proof[prior.FLAG] is True and proof['frozen_guard_admission_for_entire_box_proved'] is False and
                        proof['box_reim']==src['box_reim'] and proof['ORIGINAL_anchor_uint64']==src['ORIGINAL_source_uint64'],'retain negative guard proof; no box promotion')
                bound=e['bound'];require(bound['box_reim']==src['box_reim'] and e['ORIGINAL_source_uint64']==src['ORIGINAL_source_uint64'],'same exact encoder box and anchor')
                require(g['retained_encoder_decode_bound_sha256']==digest(bound),'same immutable encoder certificate')
                validate_encoder(bound)
                require(b[BARE_FLAG] is True and b['phase_reference_id']==src['source_phase_reference_id'] and
                        b['terminal_reference_id']==src['terminal_reference_id']==src['common_terminal_reference_id'],'retained eligible UNIT and fixed gauges')
                require(b['result']['source_encoder']['ORIGINAL_source_uint64']==src['ORIGINAL_source_uint64'],'retained bare ORIGINAL amplitude')
                words=b['result']['unit_uint64']
                require(digest(words)==digest(b['admission']['unit_uint64']) and type(words) is list and len(words)==2,'exact typed fixed UNIT words')
                for w in words:guard.bits(w,64)
                rows.append((src,bound,g,b,words))
        else:require(ec['sources'] is gc['sources'] is None,'missing domain does not inspect point UNIT')
        checked[name]=(ctx,dom,rows)
    cases={};count=0
    # ALL INPUT/certificates validated above, before ANY new product majorants.
    for name,(ctx,dom,rows) in checked.items():
        out=None
        if rows is not None:
            out=[]
            for src,bound,g,b,words in rows:
                p=product_bound_HOST(bound,words,model=model,arithmetic_model=arithmetic_model);count+=1
                out.append({'source_id':src['source_id'],'domain_source_sha256':digest(src),'negative_guard_source_sha256':digest(g),
                    'retained_bare_SOURCE_row_sha256':digest(b),'proof':p,'whole_box_guard_admission_disproved':True})
        cases[name]={'context':ctx,'sources':out,'domain_INPUT_valid':dom['domain_INPUT_valid'],
            'uniform_executed_SOURCE_error_L1':None,'uniform_SOURCE_enclosure_proved':False,
            'group_phase_bound_rad':None,'group_field_bound_L1':None,'status':'STOP',**dict.fromkeys(FALSE,False)}
    return {'model':MODEL,'variant':variant,'case_order':deepcopy(old['case_order']),'cases':cases,
        'inherited_pins_verified':len(pins),'analytical_product_bounds':count,'new_native_operations':0,
        'old_suites_producers_reexecuted':0,'group_admissions':0,'blocked_guard_boxes_preserved':count,
        'uniform_SOURCE_enclosure_proved':False,'UNIT_error_to_ORIGINAL_included':False,
        'cost_scope':'HOST variable SOURCE/fixed represented UNIT stages only; full costs UNMEASURED NOT zero',**dict.fromkeys(FALSE,False)}
