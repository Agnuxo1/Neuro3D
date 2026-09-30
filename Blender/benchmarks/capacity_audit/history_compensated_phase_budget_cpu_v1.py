"""Scene-derived conditional CPU phase budget, never native admission.

Complete frozen CPU histories/length enclosures/amplitude upper bounds;
no GPU routes or fields, no U/GEMM. Geometry and coefficients remain ideal.
"""
from fractions import Fraction as F
from phase_compensated_cpu_v1 import compensated_angle
from phase_circular_budget_cpu_v1 import scalar_circular_budget, PI_UPPER
from history_wavelength_field_budget_v1 import scene_wavelength_field_budget, encoded_upper


def interval_phase_bound(length, decoded_lambda, trace, *, length_interval,
                         lambda_interval, field_budget):
    lo, hi = map(F, length_interval)
    wl, wh = map(F, lambda_interval)
    if lo > hi or wl > wh or wl <= 0:
        raise ValueError('ordered length and strictly positive lambda enclosure required')
    arithmetic = scalar_circular_budget(length, decoded_lambda, trace,
                                        field_budget=float(field_budget))
    represented_turns = F(length)/F(decoded_lambda)
    # Unwrapped extrema: wrapping endpoints would miss a full turn's interior.
    delta = max(abs(l/w-represented_turns) for l in (lo, hi) for w in (wl, wh))
    input_upper = 2*PI_UPPER*delta
    arithmetic_upper = F(*arithmetic['ideal_unit_phasor_error_upper_rational'])
    total = min(F(2), arithmetic_upper+input_upper)
    return {'represented_arithmetic': arithmetic,
            'input_cycles_deviation_upper': encoded_upper(delta),
            'input_phase_upper_rad': encoded_upper(input_upper),
            'ideal_unit_phase_error_upper': encoded_upper(total),
            'conditional_input_enclosures_only': True,
            'native_promotion_allowed': False}


def scene_compensated_phase_budget(snapshot, *, coherence_groups,
                                    field_budget, intensity_budget, relative_budget):
    baseline = scene_wavelength_field_budget(snapshot, coherence_groups=coherence_groups,
        field_budget=field_budget, intensity_budget=intensity_budget,
        relative_budget=relative_budget)
    decoded = baseline['wavelength_transport']['decoded_BU']
    original = F(snapshot['lambda_BU'])
    field_gate = F(*baseline['field_budget_rational'])
    intensity_gate = F(*baseline['intensity_budget_rational'])
    grouped = {port: {group: {'count': 0, 'amplitude': F(0), 'error': F(0)}
                         for group in output['groups']}
               for port, output in baseline['ports'].items()}
    ledger = []
    for path in baseline['ledger']:
        effective = path['effective_length']
        lo, hi = F(*effective['rational_lower']), F(*effective['rational_upper'])
        represented = float((lo+hi)/2)
        trace = compensated_angle(represented, decoded)
        phase = interval_phase_bound(represented, decoded, trace,
            length_interval=(lo, hi), lambda_interval=(original, original),
            field_budget=field_budget)
        amplitude = F(*path['amplitude_upper']['rational_upper'])
        unit_error = F(*phase['ideal_unit_phase_error_upper']['rational_upper'])
        weighted = amplitude*unit_error
        sums = grouped[path['port']][path['coherence_group']]
        sums['count'] += 1; sums['amplitude'] += amplitude; sums['error'] += weighted
        ledger.append({**path, 'represented_effective_length_BU': represented,
                       'CPU_phase_trace': trace, 'phase_budget': phase,
                       'combined_field_error_upper': encoded_upper(weighted)})
    ports = {}; accepted = True
    for port, groups in grouped.items():
        output = {}; total_power = F(0)
        for group, sums in groups.items():
            if sums['count'] != baseline['ports'][port]['groups'][group]['path_count']:
                raise ValueError('complete generated CPU group/path coverage required')
            amplitude, error = sums['amplitude'], sums['error']
            power = 2*amplitude*error+error*error
            total_power += power
            passed = error <= field_gate
            accepted = accepted and passed
            output[group] = {'path_count': sums['count'],
                'amplitude_sum_upper': encoded_upper(amplitude),
                'field_error_upper': encoded_upper(error),
                'intensity_error_upper': encoded_upper(power),
                'field_budget_satisfied': passed}
        accepted = accepted and total_power <= intensity_gate
        ports[port] = {'groups': output, 'intensity_error_upper': encoded_upper(total_power),
                       'intensity_budget_satisfied': total_power <= intensity_gate}
    return {'schema': 'exp005-history-compensated-phase-budget-CPU-v1',
            'scene_binding_sha256': baseline['scene_binding_sha256'],
            'coherence_groups': baseline['coherence_groups'],
            'generated_record_count': baseline['generated_record_count'],
            'nearest_queries': baseline['nearest_queries'],
            'wavelength_transport': baseline['wavelength_transport'],
            'baseline_wavelength_only_accepted': baseline['accepted_wavelength_only'],
            'ledger': ledger, 'ports': ports,
            'accepted_input_and_phase_arithmetic_only': accepted,
            'native_promotion_allowed': False,
            'native_precision_certified': False, 'CPU_paths_supplied_to_GPU': False,
            'scope': 'conditional ideal represented CPU scene: length enclosures, lambda encoding and point phase arithmetic',
            'excluded': ['geometry/hi-lo and reference uncertainty beyond represented scene',
                         'coefficient/source arithmetic and their phases',
                         'native length accumulation/readback/authenticity',
                         'sin/cos driver error and physical mode overlap',
                         'total native field/intensity error'], 'no_jev_aval': True}
