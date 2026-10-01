"""SHA-pinned propagation unit Horner RN32 CPU model; not scene fields/GPU."""
import base64
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path
import zlib

from axial_hilo_ops_cpu_v1 import component
from axial_hilo_terminal_cpu_v1 import round32_exact
from axial_relative_gate_cpu_v1 import ratio
from scene_field_producer_cpu_v1 import PI_LOWER,PI_UPPER

ROOT=Path(__file__).resolve().parents[3]
REPORT='coordinacion/respuestas/AXIAL-PHASE-QUOTIENT-001-CODEX.json'
SHA='fa8ea4f0bbb3202399c1575c6630ba2600631a8a6b62b0491e7f424e425a4d72'
MODEL='axial-unit-rotation-horner26-CPU-v1'


def rotation_word(angle_word,*,rotation_model):
    """Synthetic primitive at represented angle; no supplied field values."""
    if rotation_model!=MODEL:raise ValueError('explicit axial-unit-rotation-horner26-CPU-v1 required')
    x=component(angle_word)
    if abs(x)>1:raise ValueError('represented angle must lie in [-1,1] rad')
    trace=[]
    def rn(a,b,op,label):
        exact=a*b if op=='mul' else a+b;w,v=round32_exact(exact);d=v-exact
        trace.append({'label':label,'op':op,'inputs_rational':[ratio(a),ratio(b)],
            'output_uint32':w,'rounding_delta_rational':ratio(d)})
        return v,d
    z,dz=rn(x,x,'mul','square');coefficients={};terms={}
    for name,odd in [('cos',0),('sin',1)]:
        cs=[F((-1)**j,math.factorial(2*j+odd)) for j in range(7)]
        encoded=[round32_exact(c) for c in cs]
        coefficients[name]=[{'exact_rational':ratio(c),'uint32':w,'error_rational':ratio(abs(v-c))} for c,(w,v) in zip(cs,encoded)]
        h=encoded[-1][1];ideal=cs[-1];b={'coefficients':abs(h-ideal),'square':F(0),'RN_nodes':F(0)}
        for j in range(5,-1,-1):
            p,dp=rn(h,z,'mul',name+'.mul'+str(j));h,dh=rn(p,encoded[j][1],'add',name+'.add'+str(j))
            b={k:abs(z)*v for k,v in b.items()}
            b['coefficients']+=abs(encoded[j][1]-cs[j]);b['square']+=abs(ideal)*abs(dz);b['RN_nodes']+=abs(dp)+abs(dh)
            ideal=ideal*x*x+cs[j]
        if odd:
            h,dh=rn(h,x,'mul','sin.final');ideal*=x
            b={k:abs(x)*v for k,v in b.items()};b['RN_nodes']+=abs(dh)
        bound=sum(b.values(),F(0))
        if abs(h-ideal)>bound:raise ValueError('Horner propagated error bound violated')
        remainder=abs(x)**(14+odd)/math.factorial(14+odd)
        terms[name]={'output_uint32':trace[-1]['output_uint32'],'observed_rational':ratio(h),
            'exact_polynomial_oracle_rational':ratio(ideal),'actual_polynomial_error_rational':ratio(abs(h-ideal)),
            'error_charges_rational':{k:ratio(v) for k,v in b.items()},'polynomial_error_upper_rational':ratio(bound),
            'Taylor_remainder_upper_rational':ratio(remainder)}
    poly=sum((F(*t['polynomial_error_upper_rational']) for t in terms.values()),F(0))
    rem=sum((F(*t['Taylor_remainder_upper_rational']) for t in terms.values()),F(0))
    return {'angle_uint32':angle_word,'coefficients':coefficients,'terms':terms,'operations':trace,'RN32_operations':26,
        'polynomial_error_L1_upper_rational':ratio(poly),'remainder_L1_upper_rational':ratio(rem),
        'unit_error_L1_upper_rational':ratio(poly+rem),'GPU_executed':False,'ALU_executed':False}


def permute_unit(words,k):
    if not isinstance(words,list) or len(words)!=2 or type(k) is not int:raise ValueError('two unit words and integer quarter required')
    list(map(component,words));c,s=words;k%=4
    return [c,s] if k==0 else ([s^0x80000000,c] if k==1 else ([c^0x80000000,s^0x80000000] if k==2 else [s,c^0x80000000]))


def load_retained():
    raw=(ROOT/REPORT).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SHA:raise ValueError('retained phase quotient SHA mismatch')
    r=json.loads(raw)
    if r['id']!='AXIAL-PHASE-QUOTIENT-001-CODEX' or r['run']['rc']!=0:raise ValueError('retained identity/status mismatch')
    for name,h in r['code_doc_sha256'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=h:raise ValueError('changed frozen input '+name)
    run=r['run'];raw=zlib.decompress(base64.b64decode(run['stdout_zlib_base64'],validate=True))
    if len(raw)!=run['stdout_bytes'] or hashlib.sha256(raw).hexdigest()!=run['stdout_sha256']:raise ValueError('retained exact payload mismatch')
    return r,json.loads(raw)['audit']['cases']


def _case(c):
    result={'previous_full_case_accepted':c['previous_full_case_accepted'],
        'previous_phase_argument_accepted':c['accepted_phase_argument_CPU_only'],
        'accepted_propagation_unit_CPU_only':False,'accepted_full_field_pipeline':False,'field_values_computed':False,
        'mirror_phase_evaluated':False,'native_selector_implemented':False,'native_argument_product_implemented':False,
        'GPU_executed':False,'ALU_executed':False,'native_promotion_allowed':False,'execution_authenticated':False,
        'scene_or_quotient_or_producer_rerun':False,'no_jev_aval':True,'RN32_operations':0,'paths':[],
        'original_scene_binding_sha256':c['original_scene_binding_sha256'],'decoded_scene_binding_sha256':c['decoded_scene_binding_sha256']}
    ids=[p['source_id'] for p in c['paths']]
    if len(set(ids))!=len(ids):raise ValueError('unique complete retained path IDs required')
    for path in c['paths']:
        out={'source_id':path['source_id'],'phase_reference_id':path['phase_reference_id'],'accepted_propagation_unit_CPU_only':False};result['paths'].append(out)
        try:
            if not path['accepted_phase_argument_CPU_only']:raise ValueError('retained phase argument rejected; no rotation')
            if path['phase_reference_id']!='original-source-zero:'+c['original_scene_binding_sha256']+':'+path['source_id']:raise ValueError('source gauge binding mismatch')
            selector=path['selector'];r=F(*selector['centered_observed_cycles_rational']);lo,hi=[F(*v) for v in selector['centered_enclosure_cycles_rational']]
            k=(4*r+F(1,2))//1
            if not lo<=r<=hi or (4*lo+F(1,2))//1!=k or (4*hi+F(1,2))//1!=k:raise ValueError('quarter selector interval crosses branch; no epsilon/fallback')
            residual=r-F(k,4)
            if abs(residual)>F(1,8):raise ValueError('quarter residual outside certified polynomial input')
            midpoint_angle=(PI_LOWER+PI_UPPER)*residual;w,x=round32_exact(midpoint_angle)
            angle_charge=abs(x-midpoint_angle)+abs(residual)*(PI_UPPER-PI_LOWER)
            measurement=rotation_word(w,rotation_model=MODEL);result['RN32_operations']+=26
            words=permute_unit([measurement['terms'][n]['output_uint32'] for n in ['cos','sin']],k)
            upstream=F(*path['composed_phase_bound_rad']);budget=F(*path['phase_budget_rad'])
            new=F(*measurement['unit_error_L1_upper_rational']);total=2*(upstream+angle_charge)+new
            out.update(measurement=measurement,quarter_CPU_index=k,quarter_residual_cycles_rational=ratio(residual),
                angle_encoding_charge_rad=ratio(angle_charge),angle_input_origin='CPU rational residual times pi midpoint encoded RN32, not native multiply',
                phase_budget_rad=path['phase_budget_rad'],retained_phase_bound_rad=path['composed_phase_bound_rad'],
                derived_unit_L1_budget_rational=ratio(2*budget),composed_unit_error_L1_upper_rational=ratio(total),
                propagation_unit_uint32=words,observed_unit_rational=[ratio(component(v)) for v in words],
                accepted_propagation_unit_CPU_only=total<=2*budget)
        except ValueError as exc:out['reason']=str(exc)
    result['accepted_propagation_unit_CPU_only']=bool(ids) and all(p['accepted_propagation_unit_CPU_only'] for p in result['paths'])
    return result


def audit_retained_unit_rotations(*,case_names,rotation_model):
    if rotation_model!=MODEL:raise ValueError('explicit axial-unit-rotation-horner26-CPU-v1 required')
    if not isinstance(case_names,list) or not case_names or any(type(n) is not str for n in case_names) or len(set(case_names))!=len(case_names):raise ValueError('explicit unique nonempty retained case selection required')
    report,cases=load_retained()
    if any(n not in cases for n in case_names):raise ValueError('unknown retained case')
    results={n:_case(cases[n]) for n in case_names}
    return {'schema':'exp005-axial-unit-rotation-CPU-v1','rotation_model':MODEL,'cases':results,
        'RN32_operations':sum(c['RN32_operations'] for c in results.values()),'pins_verified':report['code_doc_sha256'],
        'retained_report_sha256':SHA,'GPU_executed':False,'ALU_executed':False,'accepted_full_field_pipeline':False,
        'native_promotion_allowed':False,'field_values_computed':False,'scene_or_quotient_or_producer_rerun':False,
        'cost_scope':'26 RN32/path; excludes CPU selector/input-encoding/coefficient loads, geometry, source-product, mirror phase, reduction/detector, IO, memory, energy and guard'}
