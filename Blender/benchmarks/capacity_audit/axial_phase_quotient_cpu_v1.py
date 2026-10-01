"""Scene-pinned geometric phase argument, CPU RN32 model; NOT a field backend."""
import base64
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import zlib

from axial_hilo_terminal_cpu_v1 import encode_hilo, round32_exact
from axial_hilo_ops_cpu_v1 import component
from axial_relative_gate_cpu_v1 import ratio

ROOT=Path(__file__).resolve().parents[3]
REPORT='coordinacion/respuestas/AXIAL-DETECTOR-OPS-001-CODEX.json'
SHA='2cb09034b98aeeccfc515dcd9f1643218df6725060d8b3f5cc5a9a87f8534898'
QUARTER='coordinacion/respuestas/AXIAL-QUARTER-SOURCE-OPS-001-CODEX.json'
MODEL='axial-phase-quotient-5rn32-CPU-v1'


def quotient_words(words,wavelength_word,*,phase_model):
    """Synthetic primitive: normal-or-zero limbs, one positive normal wavelength."""
    if phase_model!=MODEL:raise ValueError('explicit axial-phase-quotient-5rn32-CPU-v1 required')
    if not isinstance(words,list) or len(words)!=2:raise ValueError('two length limbs required')
    h,l=map(component,words);w=component(wavelength_word)
    if w<=0 or h+l<=0:raise ValueError('positive wavelength and represented length required')
    trace=[]
    def rn(a,b,op,label):
        exact={'div':lambda:a/b,'mul':lambda:a*b,'sub':lambda:a-b,'add':lambda:a+b}[op]()
        word,value=round32_exact(exact);delta=value-exact
        trace.append({'label':label,'op':op,'inputs_rational':[ratio(a),ratio(b)],
            'output_uint32':word,'rounding_delta_rational':ratio(delta)})
        return value,delta
    q0,d0=rn(h,w,'div','q0');p,dp=rn(q0,w,'mul','product')
    r0,dr0=rn(h,p,'sub','residual_high');r1,dr1=rn(r0,l,'add','residual_low')
    q1,d1=rn(r1,w,'div','q1')
    actual=q0+q1-(h+l)/w
    signed=(-dp+dr0+dr1)/w+d1
    if actual!=signed:raise ValueError('correlated quotient graph identity mismatch')
    b=(abs(dp)+abs(dr0)+abs(dr1))/w+abs(d1)
    return {'length_limb_uint32':words,'wavelength_uint32':wavelength_word,
        'quotient_limb_uint32':[trace[0]['output_uint32'],trace[-1]['output_uint32']],
        'modeled_quotient_rational':ratio(q0+q1),'exact_represented_quotient_rational':ratio((h+l)/w),
        'actual_quotient_error_rational':ratio(abs(actual)),'signed_graph_error_rational':ratio(signed),
        'quotient_error_upper_rational':ratio(b),'operations':trace,'RN32_operations':5,
        'leading_division_delta_rational':ratio(d0),'leading_division_error_cancels_by_graph_identity':True,
        'GPU_executed':False,'ALU_executed':False}


def centered_selector(lo,hi,observed):
    """Exact CPU admission ONLY. Not a native floor/range-reduction operation."""
    if lo>hi:raise ValueError('ordered cycles enclosure required')
    n=(observed+F(1,2))//1
    if (lo+F(1,2))//1!=n or (hi+F(1,2))//1!=n:
        return {'accepted_CPU_selector_only':False,'reason':'interval crosses centered-turn branch; no epsilon/fallback'}
    return {'accepted_CPU_selector_only':True,'CPU_integer_turn':n,
        'centered_observed_cycles_rational':ratio(observed-n),
        'centered_enclosure_cycles_rational':[ratio(lo-n),ratio(hi-n)],
        'native_selector_implemented':False}


def load_retained():
    raw=(ROOT/REPORT).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SHA:raise ValueError('retained detector SHA mismatch')
    report=json.loads(raw)
    if report['id']!='AXIAL-DETECTOR-OPS-001-CODEX' or report['run']['rc']!=0:
        raise ValueError('retained identity/status mismatch')
    for name,h in report['code_doc_sha256'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=h:raise ValueError('changed frozen input '+name)
    # Reads the earlier scene data, never invokes producer/geometry/reducer.
    quarter=json.loads((ROOT/QUARTER).read_bytes());run=quarter['run']
    raw=zlib.decompress(base64.b64decode(run['stdout_zlib_base64'],validate=True))
    if len(raw)!=run['stdout_bytes'] or hashlib.sha256(raw).hexdigest()!=run['stdout_sha256']:
        raise ValueError('retained scene payload mismatch')
    return report,json.loads(raw)['cases']


def _case(c):
    t=c['transport'];ids=[s['source_id'] for s in t['source_transport']['sources']]
    paths=t['path_certificate']['path_certificates'];contrib=t['contributions']
    original=t['original_scene_binding_sha256'];decoded=t['decoded_scene_binding_sha256']
    if any([p['source_id'] for p in seq]!=ids for seq in (paths,contrib)) or len(set(ids))!=len(ids):
        raise ValueError('complete unique ordered path/source/contribution coverage required')
    if t['path_certificate']['original_scene_binding_sha256']!=original \
            or t['path_certificate']['decoded_scene_binding_sha256']!=decoded:
        raise ValueError('path/source scene binding mismatch')
    result={'previous_full_case_accepted':c['accepted_original_ideal_scene_CPU_only'],
        'accepted_phase_argument_CPU_only':False,'accepted_full_field_pipeline':False,
        'field_values_computed':False,'mirror_phase_evaluated':False,'scene_or_producer_rerun':False,
        'GPU_executed':False,'ALU_executed':False,'native_promotion_allowed':False,
        'execution_authenticated':False,'no_jev_aval':True,'RN32_operations':0,'paths':[],
        'original_scene_binding_sha256':original,'decoded_scene_binding_sha256':decoded}
    for path,source,row in zip(paths,t['source_transport']['sources'],contrib):
        out={'source_id':path['source_id'],'phase_reference_id':path.get('phase_reference_id'),
             'accepted_phase_argument_CPU_only':False}
        result['paths'].append(out)
        try:
            if not path['accepted_CPU_one_bounce_topology'] or 'transport_field_error_L1_upper_rational' not in row:
                raise ValueError('prior topology/mode rejection; no arithmetic')
            if source['scene_binding_sha256']!=original or path['phase_reference_id']!='original-source-zero:'+original+':'+path['source_id']:
                raise ValueError('original source gauge/binding mismatch')
            wl,wh=[F(*v) for v in path['wavelength_interval_BU']]
            if wl<=0 or wl!=wh:raise ValueError('singleton wavelength required; decoded wavelength cannot be guessed')
            ww,w=round32_exact(wl)
            if w!=wl:raise ValueError('wavelength exactly representable normal32 required; no hidden cast')
            length=F(*path['decoded_length_BU']);words,represented,cast=encode_hilo(length)
            m=quotient_words(words,ww,phase_model=MODEL);result['RN32_operations']+=5
            lo,hi=[F(*v) for v in path['length_interval_BU']]
            if not 0<lo<=length<=hi:raise ValueError('decoded length not enclosed by positive retained path interval')
            original_length=F(*path['original_length_BU'])
            if not lo<=original_length<=hi:raise ValueError('original length not enclosed')
            observed=F(*m['modeled_quotient_rational']);numeric=cast/w+F(*m['quotient_error_upper_rational'])
            # Include both physical endpoints and modeled argument in SAME branch.
            selector=centered_selector(min(lo/w,observed-numeric),max(hi/w,observed+numeric),observed)
            geometric=F(*path['geometric_phase_error_bound_rad']);mirror=F(*path['mirror_phase_transport_error_rad'])
            if geometric+mirror!=F(*path['phase_error_bound_rad']):raise ValueError('retained phase source charges mismatch')
            budget=F(*path['phase_budget_rad']);new=8*numeric;total=geometric+mirror+new
            out.update(measurement=m,length_input_origin='retained decoded CPU path length re-encoded, NOT native geometric ABI',
                length_encoding_error_BU_rational=ratio(cast),length_interval_BU=path['length_interval_BU'],
                original_length_BU=path['original_length_BU'],decoded_length_BU=path['decoded_length_BU'],
                wavelength_BU_rational=ratio(w),selector=selector,
                geometric_transport_phase_bound_rad=ratio(geometric),mirror_transport_phase_bound_rad=ratio(mirror),
                new_numerical_phase_bound_rad=ratio(new),composed_phase_bound_rad=ratio(total),phase_budget_rad=ratio(budget),
                accepted_phase_argument_CPU_only=path['accepted_CPU_one_bounce_phase_budget'] and selector['accepted_CPU_selector_only'] and total<=budget)
        except ValueError as exc:out['reason']=str(exc)
    result['accepted_phase_argument_CPU_only']=bool(ids) and all(p['accepted_phase_argument_CPU_only'] for p in result['paths'])
    return result


def audit_retained_phase_arguments(*,case_names,phase_model):
    if phase_model!=MODEL:raise ValueError('explicit axial-phase-quotient-5rn32-CPU-v1 required')
    if not isinstance(case_names,list) or not case_names or any(type(n) is not str for n in case_names) \
            or len(set(case_names))!=len(case_names):raise ValueError('explicit unique nonempty retained selection required')
    report,cases=load_retained()
    if any(n not in cases for n in case_names):raise ValueError('unknown retained case')
    results={n:_case(cases[n]) for n in case_names}
    return {'schema':'exp005-axial-phase-quotient-CPU-v1','phase_model':MODEL,'cases':results,
        'RN32_operations':sum(c['RN32_operations'] for c in results.values()),'pins_verified':report['code_doc_sha256'],
        'retained_detector_sha256':SHA,'GPU_executed':False,'ALU_executed':False,'native_promotion_allowed':False,
        'accepted_full_field_pipeline':False,'field_values_computed':False,'scene_or_producer_rerun':False,
        'cost_scope':'5 modeled RN32/path; excludes length encode, CPU integer/interval selector, trig, fields, IO, memory, energy and full pipeline'}
