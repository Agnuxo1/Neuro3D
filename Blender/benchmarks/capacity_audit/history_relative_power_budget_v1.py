"""Opt-in CPU tightening of wavelength-only intensity error by relative phase.

One common phase per port/coherence group cancels in |E|^2, NOT in E.
Keep the full complex-field gate, scene references, histories and thresholds
unchanged. No GPU, matrix substitution or native precision certificate.
"""
from fractions import Fraction as F
from history_wavelength_field_budget_v1 import scene_wavelength_field_budget, encoded_upper
from phase_transport_budget_v1 import PI_UPPER


def upper(value):
    return F(*value['rational_upper'])


def scene_relative_power_budget(snapshot, *, coherence_groups,
                                field_budget,intensity_budget,relative_budget):
    result=scene_wavelength_field_budget(snapshot,coherence_groups=coherence_groups,
        field_budget=field_budget,intensity_budget=intensity_budget,relative_budget=relative_budget)
    inverse_difference=abs(1/F(snapshot['lambda_BU'])-1/F(result['wavelength_transport']['decoded_BU']))
    phase_factor=2*PI_UPPER*inverse_difference
    power_budget=F(*result['intensity_budget_rational'])
    passed=True
    for port,output in result['ports'].items():
        total=F(0)
        for group,values in output['groups'].items():
            paths=[r for r in result['ledger'] if r['port']==port and r['coherence_group']==group]
            if len(paths)!=values['path_count']:
                raise ValueError('complete path/group coverage required')
            if paths:
                lo=min(F(*r['effective_length']['rational_lower']) for r in paths)
                hi=max(F(*r['effective_length']['rational_upper']) for r in paths)
                anchor=(lo+hi)/2
            else:anchor=F(0)
            epsilon=F(0)
            for path in paths:
                lo=F(*path['effective_length']['rational_lower'])
                hi=F(*path['effective_length']['rational_upper'])
                deviation=max(abs(lo-anchor),abs(hi-anchor))
                epsilon+=upper(path['amplitude_upper'])*min(F(2),phase_factor*deviation)
            amplitude=upper(values['amplitude_sum_upper'])
            relative_power_upper=2*amplitude*epsilon+epsilon*epsilon
            full_power_upper=upper(values['intensity_error_upper'])
            tightened=min(full_power_upper,relative_power_upper)
            values['absolute_phase_intensity_error_upper']=values['intensity_error_upper']
            values['intensity_error_upper']=encoded_upper(tightened)
            values['relative_anchor_BU_rational']=[anchor.numerator,anchor.denominator]
            values['phase_aligned_field_difference_upper']=encoded_upper(epsilon)
            # This is NOT a new complex field error; field_error_upper stays intact.
            total+=tightened
            passed=passed and values['field_budget_satisfied']
        output['absolute_phase_intensity_error_upper']=output['intensity_error_upper']
        output['intensity_error_upper']=encoded_upper(total)
        output['intensity_budget_satisfied']=total<=power_budget
        passed=passed and output['intensity_budget_satisfied']
    result.update(schema='exp005-history-relative-power-budget-CPU-v1',
        accepted_wavelength_only=passed,
        scope='ideal fixed represented scene; wavelength-only intensity bound by group relative phase on CPU',
        complex_fields_rephased=False,scene_reference_changed=False,
        intensity_rule='min(absolute-phase bound, group-relative-phase bound); fields retain absolute gate')
    return result
