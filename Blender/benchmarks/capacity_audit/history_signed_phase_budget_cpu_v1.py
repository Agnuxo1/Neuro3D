"""Opt-in signed effective-reference phase and conditional ideal CPU budget.

Physical segment lengths remain nonnegative; a terminal reference correction
may make their effective sum negative. Frozen nonnegative scalar/native pilot
contracts are untouched. No GPU/driver/geometry transport certification.
"""
from fractions import Fraction as F
import math

from phase_compensated_cpu_v1 import compensated_angle
from phase_circular_budget_cpu_v1 import scalar_circular_budget, PI_UPPER
from history_wavelength_field_budget_v1 import scene_wavelength_field_budget, encoded_upper


def signed_angle(length, wavelength):
    if type(length) is not float or not math.isfinite(length):
        raise ValueError('finite represented effective length required')
    sign = -1 if length < 0 else 1
    magnitude = compensated_angle(abs(length), wavelength)
    return {'effective_length_BU': length, 'phase_sign': sign,
            'magnitude_trace': magnitude,
            'angle_float32': sign*magnitude['angle_float32'],
            'native_promotion_allowed': False}


def signed_scalar_budget(length, wavelength, trace, *, field_budget):
    if type(length) is not float or not math.isfinite(length) or type(trace) is not dict:
        raise ValueError('finite represented length and explicit signed trace required')
    sign = -1 if length < 0 else 1
    if (type(trace.get('phase_sign')) is not int or trace['phase_sign'] != sign
            or type(trace.get('effective_length_BU')) is not float
            or trace['effective_length_BU'] != length):
        raise ValueError('signed trace does not bind effective length')
    magnitude = trace.get('magnitude_trace')
    bound = scalar_circular_budget(abs(length), wavelength, magnitude, field_budget=field_budget)
    angle = trace.get('angle_float32')
    if type(angle) is not float or not math.isfinite(angle) or angle != sign*magnitude['angle_float32']:
        raise ValueError('signed angle does not match validated magnitude trace')
    # Conjugation is an isometry: |exp(-ia)-exp(-ib)| = |exp(ia)-exp(ib)|.
    # Reuse the nonnegative RN/FMA bound without assuming exact FMA residuals.
    return {**bound, 'effective_length_BU': length, 'phase_sign': sign,
            'signed_extension_rule': 'ideal exponential conjugation preserves magnitude error',
            'signed_zero_certified': False}


def signed_interval_budget(length, decoded_lambda, trace, *, length_interval,
                           lambda_interval, field_budget):
    lo, hi = map(F, length_interval)
    wl, wh = map(F, lambda_interval)
    if lo > hi or wl > wh or wl <= 0:
        raise ValueError('ordered signed length and positive wavelength enclosure required')
    arithmetic = signed_scalar_budget(length, decoded_lambda, trace, field_budget=field_budget)
    represented_turns = F(length)/F(decoded_lambda)
    # Ratio extrema are at corners, also for negative L and intervals across 0.
    # Never wrap only interval endpoints: that would lose interior full turns.
    delta = max(abs(l/w-represented_turns) for l in (lo, hi) for w in (wl, wh))
    input_upper = 2*PI_UPPER*delta
    total = min(F(2), F(*arithmetic['ideal_unit_phasor_error_upper_rational'])+input_upper)
    return {'represented_arithmetic': arithmetic,
            'input_cycles_deviation_upper': encoded_upper(delta),
            'input_phase_upper_rad': encoded_upper(input_upper),
            'ideal_unit_phase_error_upper': encoded_upper(total),
            'conditional_input_enclosures_only': True, 'native_promotion_allowed': False}


def scene_signed_phase_budget(snapshot, *, coherence_groups, field_budget,
                              intensity_budget, relative_budget):
    baseline = scene_wavelength_field_budget(snapshot, coherence_groups=coherence_groups,
        field_budget=field_budget, intensity_budget=intensity_budget, relative_budget=relative_budget)
    decoded = baseline['wavelength_transport']['decoded_BU']
    original = F(snapshot['lambda_BU'])
    field_gate = F(*baseline['field_budget_rational'])
    power_gate = F(*baseline['intensity_budget_rational'])
    totals = {p: {g: [0, F(0), F(0)] for g in data['groups']}
              for p, data in baseline['ports'].items()}
    ledger = []
    for path in baseline['ledger']:
        effective = path['effective_length']
        lo, hi = F(*effective['rational_lower']), F(*effective['rational_upper'])
        represented = float((lo+hi)/2)
        trace = signed_angle(represented, decoded)
        bound = signed_interval_budget(represented, decoded, trace,
            length_interval=(lo, hi), lambda_interval=(original, original), field_budget=field_budget)
        amplitude = F(*path['amplitude_upper']['rational_upper'])
        error = amplitude*F(*bound['ideal_unit_phase_error_upper']['rational_upper'])
        sums = totals[path['port']][path['coherence_group']]
        sums[0] += 1; sums[1] += amplitude; sums[2] += error
        ledger.append({**path, 'represented_effective_length_BU': represented,
                       'CPU_signed_phase_trace': trace, 'phase_budget': bound,
                       'combined_field_error_upper': encoded_upper(error)})
    ports = {}; accepted = True
    for p, groups in totals.items():
        out = {}; power = F(0)
        for g, (count, amplitude, error) in groups.items():
            if count != baseline['ports'][p]['groups'][g]['path_count']:
                raise ValueError('complete CPU group/path coverage required')
            group_power = 2*amplitude*error+error*error
            power += group_power
            passed = error <= field_gate
            accepted = accepted and passed
            out[g] = {'path_count': count, 'amplitude_sum_upper': encoded_upper(amplitude),
                      'field_error_upper': encoded_upper(error),
                      'intensity_error_upper': encoded_upper(group_power),
                      'field_budget_satisfied': passed}
        accepted = accepted and power <= power_gate
        ports[p] = {'groups': out, 'intensity_error_upper': encoded_upper(power),
                    'intensity_budget_satisfied': power <= power_gate}
    return {'schema': 'exp005-history-signed-phase-budget-CPU-v1',
            'scene_binding_sha256': baseline['scene_binding_sha256'],
            'coherence_groups': baseline['coherence_groups'],
            'generated_record_count': baseline['generated_record_count'],
            'nearest_queries': baseline['nearest_queries'], 'ledger': ledger, 'ports': ports,
            'accepted_input_and_phase_arithmetic_only': accepted,
            'native_promotion_allowed': False, 'native_precision_certified': False,
            'CPU_paths_supplied_to_GPU': False, 'no_jev_aval': True,
            'scope': 'conditional ideal represented CPU scene with signed terminal references',
            'excluded': ['native geometry and hi-lo/reference uncertainty',
                         'source/coefficient arithmetic and physical mode overlap',
                         'driver sin/cos, authenticated native lengths and total precision']}
