"""Bounded CPU binary32 reduction model over supplied represented fields.

Exact rational oracle is independent of summation order/algorithm. This is NOT
scene propagation, GPU reduction, coefficient transport or a driver certificate.
"""
from fractions import Fraction as F
import math
import struct


def rational(x): return [x.numerator, x.denominator]


def f32(value):
    try: result = struct.unpack('<f', struct.pack('<f', value))[0]
    except (OverflowError, struct.error) as error:
        raise ValueError('binary32 overflow') from error
    if not math.isfinite(result) or (result != 0 and abs(result) < 2.**-126):
        raise ValueError('finite normal-or-zero binary32 model only; no FTZ assumption')
    return result


def component(word):
    if type(word) is not int or not 0 <= word < 2**32:
        raise ValueError('exact uint32 field component required')
    result = struct.unpack('<f', struct.pack('<I', word))[0]
    return f32(result)


def sum_component(values, algorithm):
    total = 0.; correction = 0.
    for value in values:
        updated = f32(total+value)
        if algorithm == 'neumaier32':
            delta = f32(f32(total-updated)+value) if abs(total) >= abs(value) else f32(f32(value-updated)+total)
            correction = f32(correction+delta)
        total = updated
    return f32(total+correction) if algorithm == 'neumaier32' else total


def reduce_fields(rows, *, expected_ids, sources, algorithm, field_budget, intensity_budget):
    """Conditional supplied-field reduction; <=64 rows, no hidden partial sum."""
    if algorithm not in ('linear32', 'neumaier32'):
        raise ValueError('explicit modeled binary32 reduction algorithm required')
    for value in (field_budget, intensity_budget):
        if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
            raise ValueError('finite nonnegative absolute budgets required')
    if not isinstance(rows, list) or not 1 <= len(rows) <= 64 or \
            not isinstance(expected_ids, list) or len(expected_ids) != len(rows) or \
            any(type(i) is not int or i < 0 for i in expected_ids) or len(set(expected_ids)) != len(expected_ids):
        raise ValueError('explicit complete unique IDs, one to64 supplied rows required')
    if not isinstance(sources, dict) or not sources:
        raise ValueError('explicit source/coherence/frequency metadata required')
    frequencies = {}
    for sid, info in sources.items():
        if type(sid) is not str or not sid or not isinstance(info, dict) or \
                set(info) != {'coherence_group', 'lambda_BU'} or \
                type(info['coherence_group']) is not str or not info['coherence_group'] or \
                type(info['lambda_BU']) is not float or not math.isfinite(info['lambda_BU']) or info['lambda_BU'] <= 0:
            raise ValueError('nonempty source/group and represented positive wavelength required')
        group, wavelength = info['coherence_group'], F(info['lambda_BU'])
        if group in frequencies and frequencies[group] != wavelength:
            raise ValueError('different represented wavelengths cannot share a coherent group')
        frequencies[group] = wavelength
    grouped = {}; ids = []; used = set()
    for row in rows:
        if not isinstance(row, dict) or set(row) != {'id', 'source_id', 'port', 'field_uint32'} or \
                type(row['id']) is not int or type(row['port']) is not str or not row['port'] or \
                type(row['source_id']) is not str or row['source_id'] not in sources or \
                not isinstance(row['field_uint32'], list) or len(row['field_uint32']) != 2:
            raise ValueError('exact represented field row schema required')
        sid = row['source_id']; used.add(sid); ids.append(row['id'])
        key = (row['port'], sources[sid]['coherence_group'])
        grouped.setdefault(key, []).append(tuple(map(component, row['field_uint32'])))
    if len(set(ids)) != len(ids) or set(ids) != set(expected_ids) or used != set(sources):
        raise ValueError('complete supplied-ID/source coverage required; not a scene completeness proof')
    ports = {}; passed = True
    for (port, group), values in grouped.items():
        reference = [sum((F(v[k]) for v in values), F(0)) for k in (0,1)]
        modeled = [sum_component([v[k] for v in values], algorithm) for k in (0,1)]
        error = sum((abs(F(modeled[k])-reference[k]) for k in (0,1)), F(0))
        reference_power = sum((v*v for v in reference), F(0))
        modeled_power = sum((F(v)**2 for v in modeled), F(0))
        power_error = abs(modeled_power-reference_power)
        valid = error <= F(field_budget); passed = passed and valid
        out = ports.setdefault(port, {'groups': {}, 'power_error_bound': F(0)})
        out['power_error_bound'] += power_error
        out['groups'][group] = {'supplied_path_count': len(values),
            'reference_field_rational': list(map(rational, reference)), 'modeled_field_reim': modeled,
            'field_error_L1_rational': rational(error), 'intensity_error_rational': rational(power_error),
            'reference_intensity_rational': rational(reference_power), 'field_budget_satisfied': valid}
    for out in ports.values():
        error = out.pop('power_error_bound')
        out['intensity_error_bound_rational'] = rational(error)
        out['intensity_budget_satisfied'] = error <= F(intensity_budget)
        passed = passed and out['intensity_budget_satisfied']
    return {'schema': 'coherent-reduction-CPU-v1', 'algorithm': algorithm, 'ports': ports,
            'accepted_represented_reduction_only': passed, 'native_promotion_allowed': False,
            'geometry_or_scene_inference': False, 'GPU_executed': False, 'no_jev_aval': True,
            'scope': 'conditional ideal reduction of supplied represented fields, CPU RN32 model only',
            'excluded': ['input field/phase/geometry/coefficient errors', 'GPU/libm/FTZ/reassociation',
                         'native detection or intensity arithmetic', 'physical coherence/mode overlap',
                         'scene completeness and native precision']}
