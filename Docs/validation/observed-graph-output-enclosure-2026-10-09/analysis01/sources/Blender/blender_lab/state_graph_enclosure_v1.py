"""Independent outward interval composition for an audited represented graph.

Includes exact captured affine geometry/parameters, mathematical pi/sqrt/trig,
coherent sums, normalized intensity and the observed native field/readout error.
Does not bound unknown intended geometry, Blender transform rounding, Maxwell,
calibration or an unobserved native execution. No producer kernel is imported.
"""
from fractions import Fraction as F
from functools import lru_cache
import math

from Blender.benchmarks.capacity_audit.rational_interval_v1 import (
    Interval as I,pi_interval,sincos,error_upper,upward_float,
)


def cmultiply(a,b):
    return a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]


@lru_cache(maxsize=512)
def propagation(parameter,norm_squared,wavelength):
    phase=2*pi_interval()*I(parameter)*I(norm_squared).sqrt()/I(wavelength)
    sine,cosine=sincos(phase)
    return cosine,sine


@lru_cache(maxsize=512)
def component(power,turn,phase):
    sine,cosine=sincos(I(phase))
    value=I(power).sqrt()*cosine,I(power).sqrt()*sine
    if turn==0:
        return value
    if turn==1:
        return -value[1],value[0]
    if turn==2:
        return -value[0],-value[1]
    if turn==3:
        return value[1],-value[0]
    raise ValueError('quarter turn must be0..3')


def enclose_fields(graph,fields):
    if graph['status']!='COMPLETE' or graph['unresolved']:
        raise ValueError('audited complete graph required')
    if set(fields)!={r['source_id'] for r in graph['roots']}:
        raise ValueError('complete source fields required')
    incoming=[[] for _ in graph['nodes']]
    outputs={p:[] for p in graph['ports']}
    for root in graph['roots']:
        pair=fields[root['source_id']]
        incoming[root['node']].append((I(pair[0]),I(pair[1])))
    for node_id in graph['topological_order']:
        node=graph['nodes'][node_id]
        merged=tuple(sum((v[k] for v in incoming[node_id]),I(0)) for k in (0,1))
        norm2=sum((F(v)**2 for v in node['direction']),F(0))
        forwarded=cmultiply(merged,propagation(F(node['segment_parameter']),norm2,F(graph['wavelength'])))
        if 'terminal' in node:
            value=cmultiply(forwarded,propagation(F(node['reference_parameter']),norm2,F(graph['wavelength'])))
            outputs[node['terminal']].append(value)
        for edge in node['edges']:
            coefficient=component(F(edge['power']),edge['quarter_turns'],F(edge['phase_rad']))
            incoming[edge['target']].append(cmultiply(forwarded,coefficient))
    return {p:tuple(sum((v[k] for v in values),I(0)) for k in (0,1)) for p,values in outputs.items()}


def observed_certificate(graph,fields,native_fields,native_powers,*,detector_ports=(),field_budget=F(1,10**11),power_budget=F(1,10**11)):
    reference=enclose_fields(graph,fields)
    if set(reference)!=set(native_fields) or set(reference)!=set(native_powers):
        raise ValueError('complete observed native output identity required')
    ports={}
    fields_passed=powers_passed=True
    for name,(real,imag) in reference.items():
        pair=native_fields[name]
        if not isinstance(pair,dict) or set(pair)!={'real','imag'}:
            raise ValueError('observed finite native field wire required')
        power=real.square()+imag.square()
        field_error=error_upper(pair['real'],real)+error_upper(pair['imag'],imag)
        power_error=error_upper(native_powers[name],power)
        fields_passed=fields_passed and field_error<=field_budget
        powers_passed=powers_passed and power_error<=power_budget
        ports[name]={'field_real':real.wire(),'field_imag':imag.wire(),'power':power.wire(),
                     'observed_field_error_L1_upper':[field_error.numerator,field_error.denominator],
                     'observed_power_error_upper':[power_error.numerator,power_error.denominator],
                     'observed_field_error_L1_upward_float':upward_float(field_error),
                     'observed_power_error_upward_float':upward_float(power_error)}
    decision={'status':'NOT_REQUESTED','winner':None}
    if detector_ports:
        if len(set(detector_ports))!=len(detector_ports) or not set(detector_ports)<=set(reference):
            raise ValueError('declared unique detector subset required')
        powers={p:reference[p][0].square()+reference[p][1].square() for p in detector_ports}
        winner=max(detector_ports,key=lambda p:native_powers[p])
        competitors=[p for p in detector_ports if p!=winner]
        margin=powers[winner].lo-max((powers[p].hi for p in competitors),default=F(0))
        margin_float=float(margin)
        if F(margin_float)>margin:
            margin_float=math.nextafter(margin_float,-math.inf)
        decision={'status':'CERTIFIED_REPRESENTED_ARGMAX' if margin>0 else 'UNKNOWN_OVERLAPPING_INTERVALS',
                  'winner':winner if margin>0 else None,'observed_native_winner':winner,
                  'margin_lower':[margin.numerator,margin.denominator],'margin_lower_downward_float':margin_float}
    return {'schema':'optic_neuro_blender.observed_graph_output_certificate.v1',
            'status':'CERTIFIED_OBSERVED_REPRESENTED_OUTPUTS' if fields_passed and powers_passed else 'VALID_BOUNDS_EXCEED_REQUESTED_BUDGET',
            'ports':ports,'decision':decision,'observed_field_budget_passed':fields_passed,'observed_power_budget_passed':powers_passed,
            'scope':{'represented_scalar_graph_reference_enclosed':True,'observed_native_execution_error_bounded':True,
                     'geometry_predicates_require_separate_audit':True,'intended_scene_error_bounded':False,
                     'blender_native_transform_rounding_bounded':False,'unobserved_gpu_error_bounded':False,
                     'physical_model_error':'UNKNOWN_NOT_ZERO','physical_calibration_verified':False},
            'budgets':{'field_L1':[field_budget.numerator,field_budget.denominator],
                       'power':[power_budget.numerator,power_budget.denominator]}}
