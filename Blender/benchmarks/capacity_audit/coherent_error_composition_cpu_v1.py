"""Conditional CPU budget: supplied path-field errors plus represented reduction.

The preceding error bounds are assumptions, NOT measured/certified producer
errors. No scene tracing, GPU dispatch, coefficient or detection arithmetic.
"""
from fractions import Fraction as F

from coherent_reduction_cpu_v1 import reduce_fields, rational


def bound(value):
    if not isinstance(value, list) or len(value) != 2 or \
            any(type(x) is not int or x.bit_length() > 256 for x in value) or \
            value[0] < 0 or value[1] <= 0:
        raise ValueError('bounded nonnegative rational [numerator, positive denominator] required')
    result = F(*value)
    if rational(result) != value:
        raise ValueError('canonical rational error bound required')
    return result


def compose_field_errors(rows, *, expected_ids, sources, path_error_bounds,
                         algorithm, field_budget, intensity_budget):
    """<=64 supplied fields, exact bindings, group-wise absolute gates.

    For represented exact sum S, modeled reduction Y and unknown ideal X,
    assume |X-S| <= B = sum(path L1 upper bounds). Then
    |Y-X| <= R+B, with R the represented reduction L1 error, and
    ||Y|^2-|X|^2| <= D + 2*L1(S)*B + B^2, where D is the EXACT
    represented ideal-power error. Different groups add powers, not fields.
    """
    if not isinstance(sources, dict) or not sources:
        raise ValueError('explicit source metadata required')
    stripped = {}; references = {}
    for sid, info in sources.items():
        if not isinstance(info, dict) or set(info) != {
                'coherence_group', 'lambda_BU', 'phase_reference_id'} or \
                type(info['phase_reference_id']) is not str or not info['phase_reference_id'] or \
                type(info['coherence_group']) is not str:
            raise ValueError('explicit common phase-reference ID required per coherent group')
        group = info['coherence_group']; reference = info['phase_reference_id']
        if group in references and references[group] != reference:
            raise ValueError('coherent sources must already use the SAME phase reference')
        references[group] = reference
        stripped[sid] = {k: info[k] for k in ('coherence_group', 'lambda_BU')}
    reduction = reduce_fields(rows, expected_ids=expected_ids, sources=stripped,
        algorithm=algorithm, field_budget=field_budget, intensity_budget=intensity_budget)
    if not isinstance(path_error_bounds, list) or len(path_error_bounds) != len(rows):
        raise ValueError('one explicitly bound upstream error per supplied row required')
    by_id = {row['id']: row for row in rows}; seen = set(); upstream = {}
    for record in path_error_bounds:
        if not isinstance(record, dict) or set(record) != {
                'id', 'source_id', 'port', 'field_uint32', 'coherence_group',
                'phase_reference_id', 'lambda_BU', 'field_error_L1_upper_rational'} or \
                type(record['id']) is not int or record['id'] not in by_id or record['id'] in seen:
            raise ValueError('complete unique upstream error record IDs required')
        row = by_id[record['id']]; info = sources[row['source_id']]
        for key in ('source_id', 'port'):
            if type(record[key]) is not str or record[key] != row[key]:
                raise ValueError('upstream error binding differs from supplied field')
        words = record['field_uint32']
        if not isinstance(words, list) or len(words) != 2 or \
                any(type(word) is not int for word in words) or words != row['field_uint32']:
            raise ValueError('upstream error must bind exact uint32 field words')
        for key in ('coherence_group', 'phase_reference_id'):
            if type(record[key]) is not str or record[key] != info[key]:
                raise ValueError('upstream coherence/phase-reference binding differs')
        if type(record['lambda_BU']) is not float or record['lambda_BU'] != info['lambda_BU']:
            raise ValueError('upstream wavelength binding differs from supplied source')
        seen.add(record['id']); key = (row['port'], info['coherence_group'])
        upstream[key] = upstream.get(key, F(0))+bound(record['field_error_L1_upper_rational'])
    if seen != set(expected_ids):
        raise ValueError('complete supplied path-ID coverage required, not scene completeness')
    ports = {}; accepted = True
    for port, old_port in reduction['ports'].items():
        groups = {}; port_error = F(0)
        for group, old_group in old_port['groups'].items():
            prior = upstream[(port, group)]
            reduction_error = F(*old_group['field_error_L1_rational'])
            total = prior+reduction_error
            reference_l1 = sum((abs(F(*x)) for x in old_group['reference_field_rational']), F(0))
            prior_power = 2*reference_l1*prior+prior*prior
            power = F(*old_group['intensity_error_rational'])+prior_power
            valid = total <= F(field_budget); accepted = accepted and valid
            port_error += power
            groups[group] = {
                'phase_reference_id': references[group],
                'supplied_path_count': old_group['supplied_path_count'],
                'assumed_upstream_error_L1_upper_rational': rational(prior),
                'represented_reduction_error_L1_rational': rational(reduction_error),
                'composed_field_error_upper_rational': rational(total),
                'represented_reference_L1_rational': rational(reference_l1),
                'upstream_intensity_error_upper_rational': rational(prior_power),
                'composed_intensity_error_upper_rational': rational(power),
                'field_budget_satisfied': valid}
        valid = port_error <= F(intensity_budget); accepted = accepted and valid
        ports[port] = {'groups': groups,
            'intensity_error_upper_rational': rational(port_error),
            'intensity_budget_satisfied': valid}
    return {'schema': 'coherent-error-composition-CPU-v1', 'algorithm': algorithm,
        'field_budget_rational': rational(F(field_budget)),
        'intensity_budget_rational': rational(F(intensity_budget)),
        'represented_reduction': reduction, 'ports': ports,
        'accepted_conditional_upstream_and_reduction_only': accepted,
        'upstream_bounds_independently_certified': False,
        'native_promotion_allowed': False, 'geometry_or_scene_inference': False,
        'GPU_executed': False, 'no_jev_aval': True,
        'excluded': ['upstream producer/scene completeness certification',
                     'native sin/cos, GPU reduction, FTZ/reassociation',
                     'native detection/intensity arithmetic',
                     'physical coherence, mode overlap, all native precision']}
