"""Integer residual ABI -> explicit RN64 conversion/product; CPU only."""
import base64
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import zlib
from axial_selector_int256_cpu_v1 import unpack
from axial_unit_rn64_cpu_v1 import component64,round64
from axial_relative_gate_cpu_v1 import ratio,bound
from scene_field_producer_cpu_v1 import PI_LOWER,PI_UPPER

ROOT=Path(__file__).resolve().parents[3]
REPORT='coordinacion/respuestas/AXIAL-SELECTOR-INT256-001-CODEX.json'
SHA='8ca986be04cb454c75e9c84ab68eb9442cafe711547bb30510ee069e80e16219'
MODEL='axial-residual-ABI-convert-mul-TWOPI-synthetic-RN64-v1'
TWO_PI=0x401921fb54442d18


def convert_residual(words):
    """Bounded bit conversion; no float/Fraction to choose the result bits."""
    n=unpack(words)
    if abs(n)>1<<146:raise ValueError('residual ABI outside certified +/-1/8 cycles')
    if n==0:return {'output_uint64':0,'discarded_integer':0,'discard_shift':0,'tie':False,'rounded_up':False}
    a=abs(n);bits=a.bit_length();e=bits-1-149;shift=max(bits-53,0)
    if shift:
        m=a>>shift;rem=a&((1<<shift)-1);tie=2*rem==1<<shift
        up=2*rem>1<<shift or (tie and bool(m&1))
        m+=int(up)
        if m==1<<53:m>>=1;e+=1
    else:m=a<<(53-bits);rem=0;tie=False;up=False
    w=((1 if n<0 else 0)<<63)|((e+1023)<<52)|(m-(1<<52))
    return {'output_uint64':w,'discarded_integer':rem,'discard_shift':shift,'tie':tie,'rounded_up':up}


def argument_words(residual_words,*,argument_model):
    if argument_model!=MODEL:raise ValueError('explicit synthetic RN64 argument model required')
    conv=convert_residual(residual_words);w=conv['output_uint64'];represented=component64(w)
    original=F(unpack(residual_words),1<<149);cast=abs(represented-original);p=component64(TWO_PI)
    constant=max(abs(p-2*PI_LOWER),abs(p-2*PI_UPPER))
    out,value=round64(represented*p);delta=value-represented*p
    charges={'residual_conversion':abs(p)*cast,'constant_2pi':abs(original)*constant,'multiply_RN64':abs(delta)}
    total=sum(charges.values(),F(0))
    if abs(value)>1:raise ValueError('modeled argument outside current +/-1 rad domain')
    return {'residual_signed256_words':residual_words,'conversion':conv,'represented_residual_rational':ratio(represented),
            'original_residual_rational':ratio(original),'residual_conversion_error_cycles_rational':ratio(cast),
            'TWO_PI_uint64':TWO_PI,'TWO_PI_error_bound_rad_per_cycle_rational':ratio(constant),
            'operations':[{'label':'argument.mul_2pi','op':'mul','inputs_rational':[ratio(represented),ratio(p)],
                           'output_uint64':out,'rounding_delta_rational':ratio(delta)}],
            'argument_uint64':out,'observed_argument_rad_rational':ratio(value),
            'angle_error_charges_rad_rational':{k:ratio(v) for k,v in charges.items()},
            'angle_error_upper_rad_rational':ratio(total),'RN64_operations':1,
            'GPU_executed':False,'ALU_executed':False,'native_argument_product_implemented':False,
            'accepted_full_field_pipeline':False}


def payload(r):
    run=r['run'];raw=zlib.decompress(base64.b64decode(run['stdout_zlib_base64'],validate=True))
    if len(raw)!=run['stdout_bytes'] or hashlib.sha256(raw).hexdigest()!=run['stdout_sha256']:raise ValueError('retained exact payload SHA mismatch')
    return json.loads(raw)


def load_retained():
    raw=(ROOT/REPORT).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SHA:raise ValueError('retained selector report SHA mismatch')
    r=json.loads(raw)
    if r['id']!='AXIAL-SELECTOR-INT256-001-CODEX' or r['run']['rc']!=0:raise ValueError('retained identity/status mismatch')
    for n,h in r['code_doc_sha256'].items():
        if hashlib.sha256((ROOT/n).read_bytes()).hexdigest()!=h:raise ValueError('changed frozen input '+n)
    phase=json.loads((ROOT/'coordinacion/respuestas/AXIAL-PHASE-QUOTIENT-001-CODEX.json').read_bytes())
    return r,payload(r)['audit']['cases'],payload(phase)['audit']['cases']


def _case(old,phase):
    for k in ('original_scene_binding_sha256','decoded_scene_binding_sha256'):
        if old[k]!=phase[k]:raise ValueError('retained scene binding mismatch')
    ids=[p['source_id'] for p in old['paths']]
    if not ids or len(set(ids))!=len(ids) or ids!=[p['source_id'] for p in phase['paths']]:raise ValueError('complete unique ordered source coverage required')
    rows=[]
    for p,pp in zip(old['paths'],phase['paths']):
        row={'source_id':p['source_id'],'phase_reference_id':p['phase_reference_id'],
             'previous_phase_argument_accepted':p['previous_phase_argument_accepted'],
             'previous_RN32_unit_accepted':p['previous_unit_accepted'],
             'accepted_argument_CPU_only':False,'argument_evaluated':False};rows.append(row)
        if not p.get('selector',{}).get('accepted_CPU_integer_selector_only',False):continue
        if p['phase_reference_id']!=pp['phase_reference_id'] or p['phase_reference_id']!='original-source-zero:'+old['original_scene_binding_sha256']+':'+p['source_id']:raise ValueError('original source gauge required')
        s=p['selector'];words=s['residual_cycles_signed256_words'];n=unpack(words)
        expected=F(*pp['selector']['centered_observed_cycles_rational'])-F(s['quarter_index'],4)
        if s['residual_scale_exponent']!=-149 or s['integer_turn']!=pp['selector']['CPU_integer_turn'] or F(n,1<<149)!=expected:raise ValueError('retained argument/quarter binding mismatch')
        upstream=bound(pp['composed_phase_bound_rad']);budget=bound(pp['phase_budget_rad'])
        m=argument_words(words,argument_model=MODEL);total=upstream+bound(m['angle_error_upper_rad_rational'])
        row.update(argument_evaluated=True,measurement=m,retained_phase_bound_rad=pp['composed_phase_bound_rad'],
                   phase_budget_rad=pp['phase_budget_rad'],composed_phase_bound_rad=ratio(total),
                   integer_turn=s['integer_turn'],quarter_index=s['quarter_index'],
                   accepted_argument_CPU_only=p['previous_phase_argument_accepted'] and pp['accepted_phase_argument_CPU_only'] and total<=budget)
    return {'original_scene_binding_sha256':old['original_scene_binding_sha256'],'decoded_scene_binding_sha256':old['decoded_scene_binding_sha256'],
            'previous_full_case_accepted':old['previous_full_case_accepted'],'previous_integer_selector_accepted':old['accepted_integer_selector_CPU_only'],
            'accepted_argument_CPU_only':all(p['accepted_argument_CPU_only'] for p in rows),'paths':rows,
            'accepted_full_field_pipeline':False,'field_values_computed':False,'native_argument_product_implemented':False,
            'RN64_operations':sum(int(p['argument_evaluated']) for p in rows)}


def audit_retained_arguments(*,case_names,argument_model):
    if argument_model!=MODEL:raise ValueError('explicit synthetic RN64 argument model required')
    if not isinstance(case_names,list) or not case_names or any(type(n) is not str for n in case_names) or len(set(case_names))!=len(case_names):raise ValueError('explicit unique retained case selection required')
    r,old,phase=load_retained()
    if any(n not in old for n in case_names):raise ValueError('unknown retained case')
    cases={n:_case(old[n],phase[n]) for n in case_names}
    return {'argument_model':MODEL,'cases':cases,'pins_verified':r['code_doc_sha256'],'retained_report_sha256':SHA,
            'RN64_operations':sum(c['RN64_operations'] for c in cases.values()),'GPU_executed':False,'ALU_executed':False,
            'native_argument_product_implemented':False,'accepted_full_field_pipeline':False,'native_selector_implemented':False,
            'field_values_computed':False,'old_selector_unit_quotient_or_producer_rerun':False,
            'cost_scope':'1 synthetic RN64mul/path plus bit-conversion separate; excludes retained upstream/native/IO/RAM/energy/guard/full costs'}
