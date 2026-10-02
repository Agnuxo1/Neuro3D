"""Opt-in analytical uniform SOURCE hi-lo encoder/decode, not guard/device admission."""
from copy import deepcopy
from fractions import Fraction as F
import axial_SOURCE_amplitude_disk_box_HOST_v1 as prior
io,allocation,require,digest,pair=prior.io,prior.allocation,prior.require,prior.digest,prior.pair
FALSE=prior.FALSE
MODEL='axial-SOURCE-uniform-hilo32-RN64decode-declared-box-HOST-v1'
ARITHMETIC_MODEL='binary32/binary64 RN-even; gradual underflow; exact widening; no FTZ/FMA'
FLAG='uniform_encoder_decode_bound_for_declared_box_HOST_proved'
PARENT='coordinacion/respuestas/AXIAL-SOURCE-AMPLITUDE-DISK-BOX-HOST-001-CODEX.json'
PARENT_SHA='822d58a334b8be92f7e8421eb330013865c76fab7f55314eff5926f76e52a28e'
U={32:F(1,2**24),64:F(1,2**53)}
ETA={32:F(1,2**150),64:F(1,2**1075)}
MAX={32:F((2**24-1)*2**104),64:F((2**53-1)*2**971)}
VARIANTS=('real_missing','explicit_None_missing','synthetic_domains')

def rounding(m,bits):
    require(type(bits) is int and bits in U and 0<=m<=MAX[bits],'finite exact-operation argument range')
    return U[bits]*m+ETA[bits] if m else F(0)

def uniform_encode_decode_HOST(box,*,model,arithmetic_model):
    require(type(model) is str and model==MODEL and type(arithmetic_model) is str and
            arithmetic_model==ARITHMETIC_MODEL,'explicit uniform encoder model and RN/gradual/noFTZ contract')
    intervals=prior.box_values(box);rows=[]
    for lo,hi in intervals:
        m=max(abs(lo),abs(hi));eh=rounding(m,32)
        high_max=m+eh
        require(high_max<=MAX[32],'conservative high range margin; no clamp/near-overflow admission')
        er=rounding(eh,64);res_max=eh+er
        el=rounding(res_max,32);low_max=res_max+el
        require(low_max<=MAX[32],'conservative low range margin')
        enc=er+el # (h + low) - x = delta_residual + delta_low; high error cancels.
        sum_max=m+enc
        ed=rounding(sum_max,64);decoded_max=sum_max+ed
        require(decoded_max<=MAX[64],'conservative decoded range margin')
        rows.append({'max_abs_ORIGINAL_component':pair(m),'high_cast_error_bound':pair(eh),
            'high_output_max_bound':pair(high_max),'exact_residual_max_bound':pair(eh),
            'residual_RN64_error_bound':pair(er),'residual_output_max_bound':pair(res_max),
            'low_cast_error_bound':pair(el),'low_output_max_bound':pair(low_max),
            'encoding_error_bound':pair(enc),'exact_decode_sum_max_bound':pair(sum_max),
            'decode_RN64_error_bound':pair(ed),'decoded_output_max_bound':pair(decoded_max),
            'encoding_plus_decode_bound':pair(enc+ed)})
    enc=sum((F(*r['encoding_error_bound']) for r in rows),F(0))
    dec=sum((F(*r['decode_RN64_error_bound']) for r in rows),F(0))
    return {'model':MODEL,'arithmetic_model':ARITHMETIC_MODEL,'box_reim':deepcopy(box),'components':rows,
        'source_encoding_uniform_L1_bound':pair(enc),'source_decode_RN64_uniform_L1_bound':pair(dec),
        'source_encoding_plus_decode_uniform_L1_bound':pair(enc+dec),FLAG:True,
        'graph':['h=RN32(x)','r=RN64(x-h)','low=RN32(r)','decoded=RN64(widen(h)+widen(low))'],
        'unit_Horner_product_material_reduction_errors_included':False,'phase_bound_rad':None,
        'uniform_executed_SOURCE_error_L1':None,'uniform_SOURCE_enclosure_proved':False,
        'frozen_guard_admission_for_entire_box_proved':False,'device_model_authenticated':False,
        'signed_zero_execution_policy_proved':False,'status':'STOP',**dict.fromkeys(FALSE,False)}

def load_retained():
    r=allocation.parse(io.read(PARENT,PARENT_SHA))
    require(r['task_id']=='AXIAL-SOURCE-AMPLITUDE-DISK-BOX-HOST-001','parent identity')
    pins=io.pins_from(r);pins[PARENT]=PARENT_SHA
    for p,h in pins.items():io.read(p,h)
    packets,stage,oldpins=prior.load_retained()
    require(all(pins.get(p)==h for p,h in oldpins.items()),'same domain/context branches')
    return packets,stage,io.payload(r)['data'],pins

def audit_uniform_encoder_HOST(variant,*,model,arithmetic_model):
    require(type(variant) is str and variant in VARIANTS and type(model) is str and model==MODEL and
            type(arithmetic_model) is str and arithmetic_model==ARITHMETIC_MODEL,'explicit retained variant/encoder arithmetic')
    packets,stage,data,pins=load_retained()
    old=data['synthetic_scene_domains'] if variant=='synthetic_domains' else data['real_missing']
    plans=data['synthetic_domain_INPUT_plans'] if variant=='synthetic_domains' else ({n:None for n in old['case_order']} if variant=='explicit_None_missing' else {})
    checked={}
    # ALL INPUT domain/context/source rows before ANY bound calculation.
    for name in old['case_order']:
        ctx=allocation.context_from_packet(packets[name],digest(packets[name]),model=allocation.MODEL)
        require(ctx==old['cases'][name]['context'],'same ORIGINAL domain context')
        d=prior.validate_domain(packets[name],ctx,plans.get(name))
        require(digest(d)==digest(old['cases'][name]['domain_INPUT']),'exact typed retained domain INPUT')
        checked[name]=(ctx,d)
    cases={};bounds=0
    for name,(ctx,d) in checked.items():
        rows=None
        if d['domain_INPUT_valid']:
            rows=[]
            for source in d['sources']:
                b=uniform_encode_decode_HOST(source['box_reim'],model=model,arithmetic_model=arithmetic_model);bounds+=1
                rows.append({'source_id':source['source_id'],'domain_source_sha256':digest(source),
                    'ORIGINAL_source_uint64':deepcopy(source['ORIGINAL_source_uint64']),'bound':b,
                    'uniform_executed_SOURCE_error_L1':None,'status':'STOP',**dict.fromkeys(FALSE,False)})
        cases[name]={'context':ctx,'domain_INPUT_valid':d['domain_INPUT_valid'],'sources':rows,
            'uniform_executed_SOURCE_error_L1':None,'uniform_SOURCE_enclosure_proved':False,
            'group_phase_bound_rad':None,'group_field_bound_L1':None,'status':'STOP',**dict.fromkeys(FALSE,False)}
    return {'model':MODEL,'arithmetic_model':ARITHMETIC_MODEL,'variant':variant,'case_order':deepcopy(old['case_order']),
        'cases':cases,'inherited_pins_verified':len(pins),'analytical_encoder_decode_bounds':bounds,
        'new_native_operations':0,'old_suites_producers_reexecuted':0,'group_admissions':0,'point_error_reused_as_uniform':False,
        'uniform_SOURCE_enclosure_proved':False,'frozen_guard_admission_for_entire_box_proved':False,
        'cost_scope':'HOST analytical encoder/decode stages only; IO/setup/upstream/rest UNMEASURED NOT zero',**dict.fromkeys(FALSE,False)}
