"""Relative gates on SHA-pinned retained scene-derived CPU evidence only.

No producer/suite replay; no caller-supplied scene fields or replacement report.
Certified lower denominators, never a floor, and all prior failures retained.
"""
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
REPORT='coordinacion/respuestas/AXIAL-SCENE-COMPOSITION-001-CODEX.json'
REPORT_SHA='c4eceb7c32d54b7e996aacbc19af448e54bc42e6fa1ace18639494543a574277'


def ratio(x):return [x.numerator,x.denominator]


def budget(value):
    if isinstance(value,bool) or not isinstance(value,(int,float,F)):
        raise ValueError('explicit finite nonnegative relative budget required')
    try:x=F(value)
    except (ValueError,OverflowError):raise ValueError('finite relative budget required') from None
    if x<0:raise ValueError('nonnegative relative budget required')
    return x


def bound(pair):
    if not isinstance(pair,list) or len(pair)!=2 or any(type(x) is not int for x in pair) \
            or pair[0]<0 or pair[1]<=0:
        raise ValueError('canonical nonnegative rational bound required')
    x=F(*pair)
    if ratio(x)!=pair:raise ValueError('canonical bound required')
    return x


def _relative(observed,b,limit):
    """||ideal|| >= ||observed|| - bound; works for norm or scalar power."""
    if observed<0 or b<0:raise ValueError('nonnegative observed norm and bound required')
    lower=max(F(0),observed-b)
    upper=b/lower if lower>0 else None
    return {'observed_rational':ratio(observed),'absolute_error_upper_rational':ratio(b),
        'ideal_reference_lower_rational':ratio(lower),
        'relative_error_upper_rational':ratio(upper) if upper is not None else None,
        'relative_budget_rational':ratio(limit),
        'status':'CERTIFIED_BOUND' if upper is not None else 'NO_POSITIVE_REFERENCE_LOWER_BOUND',
        'relative_budget_satisfied':upper is not None and upper<=limit}


def _load_retained():
    raw=(ROOT/REPORT).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=REPORT_SHA:raise ValueError('retained report SHA mismatch')
    report=json.loads(raw)
    if report['id']!='AXIAL-SCENE-COMPOSITION-001-CODEX' or report['run']['rc']!=0:
        raise ValueError('unexpected retained CPU evidence identity/status')
    for name,sha in report['code_doc_sha256'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=sha:
            raise ValueError('changed frozen evidence input: '+name)
    return report


def _audit_case(case,field_limit,power_limit):
    base={'accepted_retained_relative_CPU_only':False,
        'previous_absolute_and_upstream_accepted':case['accepted_original_ideal_scene_CPU_only'],
        'original_scene_binding_sha256':case.get('original_scene_binding_sha256',
            case['transport']['original_scene_binding_sha256']),
        'decoded_scene_binding_sha256':case.get('decoded_scene_binding_sha256',
            case['transport']['decoded_scene_binding_sha256']),
        'field_values_computed_in_retained_run':case['field_values_computed']}
    if not case['field_values_computed']:
        return {**base,'reason':'no numerical field in retained case; prior rejection retained','ports':{}}
    comp=case['composition'];red=comp['represented_reduction']
    if not comp['ports'] or set(comp['ports'])!=set(red['ports']):
        raise ValueError('complete nonempty retained port coverage required')
    reference='ideal-scene-source-gauge:'+base['original_scene_binding_sha256']
    ports={};relative_pass=True
    for port,p in comp['ports'].items():
        old=red['ports'][port]['groups']
        if not p['groups'] or set(p['groups'])!=set(old):
            raise ValueError('complete nonempty retained group coverage required')
        groups={};observed_power=F(0)
        for group,g in p['groups'].items():
            if g['phase_reference_id']!=reference:raise ValueError('original scene gauge mismatch')
            values=tuple(map(F,old[group]['modeled_field_reim']))
            if len(values)!=2:raise ValueError('complex represented field required')
            observed_power+=sum((v*v for v in values),F(0))
            gate=_relative(sum(map(abs,values),F(0)),bound(g['composed_field_error_upper_rational']),field_limit)
            groups[group]={**gate,'phase_reference_id':reference}
            relative_pass=relative_pass and gate['relative_budget_satisfied']
        power=_relative(observed_power,bound(p['intensity_error_upper_rational']),power_limit)
        relative_pass=relative_pass and power['relative_budget_satisfied']
        ports[port]={'field_L1_groups':groups,'incoherent_total_power':power}
    return {**base,'ports':ports,'relative_gates_satisfied':relative_pass,
        'accepted_retained_relative_CPU_only':base['previous_absolute_and_upstream_accepted'] and relative_pass}


def audit_retained_axial_relative(*,case_names,field_relative_budget,intensity_relative_budget):
    field_limit,power_limit=budget(field_relative_budget),budget(intensity_relative_budget)
    if not isinstance(case_names,list) or not case_names or any(type(n) is not str for n in case_names) \
            or len(set(case_names))!=len(case_names):
        raise ValueError('explicit unique nonempty retained case selection required')
    report=_load_retained();cases=report['run']['observations']['cases']
    if any(n not in cases for n in case_names):raise ValueError('unknown retained case')
    results={n:_audit_case(cases[n],field_limit,power_limit) for n in case_names}
    return {'schema':'exp005-axial-relative-gate-retained-CPU-v1',
        'retained_report_id':report['id'],'retained_report_sha256':REPORT_SHA,
        'pins_verified':report['code_doc_sha256'],'cases':results,
        'accepted_retained_relative_CPU_only':all(c['accepted_retained_relative_CPU_only'] for c in results.values()),
        'field_relative_budget_rational':ratio(field_limit),'intensity_relative_budget_rational':ratio(power_limit),
        'field_metric':'relative complex L1 per coherent group, denominator original ideal field L1',
        'intensity_metric':'relative ideal incoherent total power per port; exact squared represented output model',
        'new_field_values_computed':False,'old_producer_or_suites_rerun':False,
        'GPU_executed':False,'native_promotion_allowed':False,'execution_authenticated':False,'no_jev_aval':True,
        'excluded':['new scenes or outputs outside SHA-pinned evidence',
            'native RN/FTZ/driver/detection/RT/physical optics/performance',
            'phase accuracy or coherent addition between different groups']}
