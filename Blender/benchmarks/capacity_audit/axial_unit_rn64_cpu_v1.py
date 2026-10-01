"""Opt-in synthetic CPU RN64 propagation unit; no native/GPU/scene fields."""
import base64
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path
import zlib

from axial_relative_gate_cpu_v1 import ratio
from scene_field_producer_cpu_v1 import PI_LOWER, PI_UPPER

ROOT=Path(__file__).resolve().parents[3]
REPORT='coordinacion/respuestas/AXIAL-UNIT-ROTATION-001-CODEX.json'
SHA='2fe36151a7f474bdd02340b3ed49b0a1f4c594e8d94e2493e562f5ac2e33a212'
MODEL='axial-unit-horner26-synthetic-RN64-v1'


def pow2(e):
    return F(2**e) if e>=0 else F(1,2**(-e))


def component64(word):
    if type(word) is not int or not 0<=word<2**64:
        raise ValueError('exact uint64 required')
    e=(word>>52)&2047; m=word&((1<<52)-1)
    if e==2047 or (e==0 and m):
        raise ValueError('finite normal-or-zero RN64 only; no FTZ')
    if e==0:return F(0)
    return (-1 if word>>63 else 1)*F((1<<52)+m)*pow2(e-1023-52)


def round64(q):
    """Exact rational nearest-even; selected subnormals/overflow fail closed."""
    q=F(q)
    if not q:return 0,F(0)
    sign=1 if q<0 else 0; a=abs(q)
    e=a.numerator.bit_length()-a.denominator.bit_length()
    if a<pow2(e):e-=1
    step=pow2(max(e,-1022)-52)
    scaled=a/step; n,rem=divmod(scaled.numerator,scaled.denominator)
    if 2*rem>scaled.denominator or (2*rem==scaled.denominator and n&1):n+=1
    value=F(n)*step
    if not value:return sign<<63,F(0)
    if value<pow2(-1022):raise ValueError('selected RN64 subnormal; no FTZ')
    if value>=pow2(1024):raise ValueError('RN64 overflow')
    if n==(1<<53):n>>=1;e+=1
    e=max(e,-1022)
    word=(sign<<63)|((e+1023)<<52)|(n-(1<<52))
    out=-value if sign else value
    if component64(word)!=out:raise ValueError('RN64 encoding identity violated')
    return word,out


def rotation64(angle_word,*,rotation_model):
    if rotation_model!=MODEL:raise ValueError('explicit synthetic RN64 model required')
    x=component64(angle_word)
    if abs(x)>1:raise ValueError('represented angle outside [-1,1] rad')
    trace=[]; coefficients={}; terms={}
    def rn(a,b,op,label):
        exact=a*b if op=='mul' else a+b; w,v=round64(exact); d=v-exact
        trace.append({'label':label,'op':op,'inputs_rational':[ratio(a),ratio(b)],
                      'output_uint64':w,'rounding_delta_rational':ratio(d)})
        return v,d
    z,dz=rn(x,x,'mul','square')
    for name,odd in [('cos',0),('sin',1)]:
        cs=[F((-1)**j,math.factorial(2*j+odd)) for j in range(7)]
        encoded=[round64(c) for c in cs]
        coefficients[name]=[{'exact_rational':ratio(c),'uint64':w,'error_rational':ratio(abs(v-c))}
                           for c,(w,v) in zip(cs,encoded)]
        h=encoded[-1][1]; ideal=cs[-1]
        charges={'coefficients':abs(h-ideal),'square':F(0),'RN_nodes':F(0)}
        for j in range(5,-1,-1):
            p,dp=rn(h,z,'mul',name+'.mul'+str(j))
            h,dh=rn(p,encoded[j][1],'add',name+'.add'+str(j))
            charges={key:abs(z)*val for key,val in charges.items()}
            charges['coefficients']+=abs(encoded[j][1]-cs[j])
            charges['square']+=abs(ideal)*abs(dz)
            charges['RN_nodes']+=abs(dp)+abs(dh)
            ideal=ideal*x*x+cs[j]
        if odd:
            h,dh=rn(h,x,'mul','sin.final');ideal*=x
            charges={key:abs(x)*val for key,val in charges.items()}
            charges['RN_nodes']+=abs(dh)
        b=sum(charges.values(),F(0)); rem=abs(x)**(14+odd)/math.factorial(14+odd)
        if abs(h-ideal)>b:raise ValueError('polynomial bound violated')
        terms[name]={'output_uint64':trace[-1]['output_uint64'],
                     'observed_rational':ratio(h),'exact_polynomial_oracle_rational':ratio(ideal),
                     'actual_polynomial_error_rational':ratio(abs(h-ideal)),
                     'error_charges_rational':{k:ratio(v) for k,v in charges.items()},
                     'polynomial_error_upper_rational':ratio(b),
                     'Taylor_remainder_upper_rational':ratio(rem)}
    total=sum((F(*t['polynomial_error_upper_rational'])+F(*t['Taylor_remainder_upper_rational'])
               for t in terms.values()),F(0))
    return {'angle_uint64':angle_word,'coefficients':coefficients,'terms':terms,'operations':trace,
            'RN64_operations':26,'unit_error_L1_upper_rational':ratio(total)}


def permute64(words,k):
    if type(k) is not int or not isinstance(words,list) or len(words)!=2:
        raise ValueError('two unit words and integer quarter required')
    list(map(component64,words));c,s=words;k%=4;sign=1<<63
    return [c,s] if k==0 else ([s^sign,c] if k==1 else ([c^sign,s^sign] if k==2 else [s,c^sign]))


def payload(report):
    run=report['run']
    raw=zlib.decompress(base64.b64decode(run['stdout_zlib_base64'],validate=True))
    if len(raw)!=run['stdout_bytes'] or hashlib.sha256(raw).hexdigest()!=run['stdout_sha256']:
        raise ValueError('retained exact payload SHA mismatch')
    return json.loads(raw)['audit']['cases']


def load_retained():
    raw=(ROOT/REPORT).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SHA:raise ValueError('retained unit report SHA mismatch')
    report=json.loads(raw)
    if report['id']!='AXIAL-UNIT-ROTATION-001-CODEX' or report['run']['rc']!=0:
        raise ValueError('retained identity/status mismatch')
    for name,sha in report['code_doc_sha256'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=sha:
            raise ValueError('changed frozen input '+name)
    phase=json.loads((ROOT/'coordinacion/respuestas/AXIAL-PHASE-QUOTIENT-001-CODEX.json').read_bytes())
    return report,payload(report),payload(phase)


def _case(old,phase):
    if any(old[k]!=phase[k] for k in ('original_scene_binding_sha256','decoded_scene_binding_sha256')):
        raise ValueError('original/decoded scene binding mismatch')
    result={'previous_full_case_accepted':old['previous_full_case_accepted'],
            'previous_RN32_unit_accepted':old['accepted_propagation_unit_CPU_only'],
            'accepted_propagation_unit_CPU_only':False,'accepted_full_field_pipeline':False,
            'field_values_computed':False,'mirror_phase_evaluated':False,'GPU_executed':False,
            'ALU_executed':False,'native_promotion_allowed':False,'execution_authenticated':False,
            'native_selector_implemented':False,'native_argument_product_implemented':False,
            'old_rotation_or_quotient_or_producer_rerun':False,
            'original_scene_binding_sha256':old['original_scene_binding_sha256'],
            'decoded_scene_binding_sha256':old['decoded_scene_binding_sha256'],
            'paths':[],'RN64_operations':0}
    ids=[p['source_id'] for p in old['paths']]
    if not ids or len(set(ids))!=len(ids) or ids!=[p['source_id'] for p in phase['paths']]:
        raise ValueError('complete ordered unique source coverage required')
    for op,pp in zip(old['paths'],phase['paths']):
        out={'source_id':op['source_id'],'phase_reference_id':op['phase_reference_id'],
             'accepted_propagation_unit_CPU_only':False};result['paths'].append(out)
        try:
            if not pp['accepted_phase_argument_CPU_only']:
                raise ValueError('retained phase argument rejected; no rotation')
            if op['phase_reference_id']!='original-source-zero:'+old['original_scene_binding_sha256']+':'+op['source_id'] or op['phase_reference_id']!=pp['phase_reference_id']:
                raise ValueError('original source gauge mismatch')
            selector=pp['selector'];r=F(*selector['centered_observed_cycles_rational'])
            lo,hi=map(lambda v:F(*v),selector['centered_enclosure_cycles_rational'])
            k=(4*r+F(1,2))//1
            if not lo<=r<=hi or (4*lo+F(1,2))//1!=k or (4*hi+F(1,2))//1!=k:
                raise ValueError('quarter selector interval crosses branch')
            u=r-F(k,4)
            if abs(u)>F(1,8) or k!=op['quarter_CPU_index'] or ratio(u)!=op['quarter_residual_cycles_rational']:
                raise ValueError('retained quarter/residual binding mismatch')
            if op['phase_budget_rad']!=pp['phase_budget_rad'] or op['retained_phase_bound_rad']!=pp['composed_phase_bound_rad']:
                raise ValueError('unchanged phase budget/bound mismatch')
            budget=F(*pp['phase_budget_rad']); upstream=F(*pp['composed_phase_bound_rad'])
            if budget<0 or upstream<0:raise ValueError('nonnegative bound/budget required')
            midpoint=(PI_LOWER+PI_UPPER)*u;w,x=round64(midpoint)
            angle=abs(x-midpoint)+abs(u)*(PI_UPPER-PI_LOWER)
            measurement=rotation64(w,rotation_model=MODEL);result['RN64_operations']+=26
            words=permute64([measurement['terms'][n]['output_uint64'] for n in ('cos','sin')],k)
            total=2*(upstream+angle)+F(*measurement['unit_error_L1_upper_rational'])
            out.update(measurement=measurement,quarter_CPU_index=k,quarter_residual_cycles_rational=ratio(u),
                       angle_encoding_charge_rad=ratio(angle),phase_budget_rad=pp['phase_budget_rad'],
                       retained_phase_bound_rad=pp['composed_phase_bound_rad'],
                       derived_unit_L1_budget_rational=ratio(2*budget),
                       composed_unit_error_L1_upper_rational=ratio(total),
                       propagation_unit_uint64=words,observed_unit_rational=[ratio(component64(v)) for v in words],
                       accepted_propagation_unit_CPU_only=total<=2*budget)
        except ValueError as exc:out['reason']=str(exc)
    result['accepted_propagation_unit_CPU_only']=all(p['accepted_propagation_unit_CPU_only'] for p in result['paths'])
    return result


def audit_retained_rn64(*,case_names,rotation_model):
    if rotation_model!=MODEL:raise ValueError('explicit synthetic RN64 model required')
    if not isinstance(case_names,list) or not case_names or any(type(n) is not str for n in case_names) or len(set(case_names))!=len(case_names):
        raise ValueError('explicit unique nonempty selection required')
    report,old,phase=load_retained()
    if any(n not in old for n in case_names):raise ValueError('unknown retained case')
    cases={n:_case(old[n],phase[n]) for n in case_names}
    return {'schema':'exp005-axial-unit-synthetic-RN64-v1','rotation_model':MODEL,'cases':cases,
            'RN64_operations':sum(c['RN64_operations'] for c in cases.values()),'GPU_executed':False,
            'ALU_executed':False,'accepted_full_field_pipeline':False,'native_promotion_allowed':False,
            'field_values_computed':False,'retained_report_sha256':SHA,
            'pins_verified':report['code_doc_sha256'],
            'cost_scope':'26 modeled RN64/path; 14 coefficient encodings and rational selector/pi input generation excluded; NO geometry/source-product/mirror/reduction/detector/IO/memory/energy/guard/full-cost comparison'}
