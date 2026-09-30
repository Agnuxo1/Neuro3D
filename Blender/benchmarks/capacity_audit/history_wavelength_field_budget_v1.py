"""Scene-bound ideal many-path error budget for wavelength encoding ONLY.

Generate bounded complete CPU histories, reconstruct effective lengths,
bound ideal amplitudes by outward rational square-root enclosures. No
CPU paths are supplied to a GPU backend; no GPU/Blender dispatch here.
Geometry, coefficients and modes are held exact and identical in the two
ideal models. Acceptance NEVER certifies native propagation or total error.
"""
from fractions import Fraction as F
from frontier_inputs import scalar
from history_trace_cpu_v1 import trace_scene
from history_lengths_cpu_v1 import reconstruct_lengths, sqrt_interval, encoded_interval
from history_lineage_cpu_v2 import scene_binding, triangles
from wavelength_transport_v1 import checked_wavelength
from phase_transport_budget_v1 import PI_UPPER


def encoded_upper(value):
    return encoded_interval(value,value)


def scene_wavelength_field_budget(snapshot, *, coherence_groups,
                                  field_budget, intensity_budget, relative_budget):
    """Compare ideal models differing only in encoded/decoded wavelength.

    |sum a exp(i phi) - sum a exp(i phi')| <= sum |a| min(2, |phi-phi'|).
    Group intensity error <= 2*A*epsilon + epsilon**2, A >= |ideal field|.
    Independent coherence groups add intensities, never complex fields.
    """
    field_budget=F(scalar(field_budget)); intensity_budget=F(scalar(intensity_budget))
    if field_budget<0 or intensity_budget<0:
        raise ValueError('explicit nonnegative field/intensity budgets required')
    binding,packed=scene_binding(snapshot)
    sources={s['id']:s for s in snapshot['sources']}
    if not isinstance(coherence_groups,dict) or set(coherence_groups)!=set(sources):
        raise ValueError('explicit coherence group for every source required')
    if any(not isinstance(g,str) or not g for g in coherence_groups.values()):
        raise ValueError('nonempty coherence group IDs required')
    transport=checked_wavelength(snapshot['lambda_BU'],relative_budget=relative_budget)
    original,decoded=F(snapshot['lambda_BU']),F(transport['decoded_BU'])
    inverse_difference=abs(1/original-1/decoded)
    generated=trace_scene(snapshot)
    lengths=reconstruct_lengths(snapshot,generated['records'])
    terminals={t['id']:t for t in lengths['terminals']}
    geometry=triangles(packed)
    amplitudes={}; ledger=[]
    grouped={p:{g:{'paths':0,'amplitude':F(0),'error':F(0)}
                for g in sorted(set(coherence_groups.values()))} for p in packed.ports}
    for record in generated['records']:
        if record['parent_id'] is None:
            real,imag=map(F,sources[record['source_id']]['field_reim'])
            amplitude=sqrt_interval(real*real+imag*imag)[1]
        else:
            amplitude=amplitudes[record['parent_id']]
            if record['event'] in ('t','r'):
                owner=geometry[record['primitive_id']][0]
                tau=F(packed.optics[owner*12+1])
                power=tau if record['event']=='t' else 1-tau
                amplitude*=sqrt_interval(power)[1]
            # Ideal mirror coefficients have modulus one, regardless of phase.
        amplitudes[record['id']]=amplitude
        if record['id'] not in terminals:continue
        terminal=terminals[record['id']]; effective=terminal['effective_length']
        length_bound=max(abs(F(*effective['rational_lower'])),abs(F(*effective['rational_upper'])))
        phase_upper=2*PI_UPPER*length_bound*inverse_difference
        field_upper=amplitude*min(F(2),phase_upper)
        group=coherence_groups[record['source_id']]; port=terminal['port']
        sums=grouped[port][group]; sums['paths']+=1
        sums['amplitude']+=amplitude; sums['error']+=field_upper
        ledger.append({'id':record['id'],'source_id':record['source_id'],'port':port,
                       'coherence_group':group,'effective_length':effective,
                       'amplitude_upper':encoded_upper(amplitude),
                       'wavelength_phase_error_upper_rad':encoded_upper(phase_upper),
                       'wavelength_field_error_upper':encoded_upper(field_upper)})
    outputs={}; passed=True
    for port,groups in grouped.items():
        result={}; total_intensity_error=F(0)
        for group,sums in groups.items():
            a,e=sums['amplitude'],sums['error']
            intensity_upper=2*a*e+e*e
            total_intensity_error+=intensity_upper
            accepted=e<=field_budget
            passed=passed and accepted
            result[group]={'path_count':sums['paths'],'amplitude_sum_upper':encoded_upper(a),
                           'field_error_upper':encoded_upper(e),
                           'intensity_error_upper':encoded_upper(intensity_upper),
                           'field_budget_satisfied':accepted}
        accepted=total_intensity_error<=intensity_budget
        passed=passed and accepted
        outputs[port]={'groups':result,'intensity_error_upper':encoded_upper(total_intensity_error),
                       'intensity_budget_satisfied':accepted}
    return {'schema':'exp005-history-wavelength-field-budget-CPU-v1',
            'scene_binding_sha256':binding,'coherence_groups':dict(coherence_groups),
            'wavelength_transport':transport,'field_budget_rational':[field_budget.numerator,field_budget.denominator],
            'intensity_budget_rational':[intensity_budget.numerator,intensity_budget.denominator],
            'generated_record_count':len(generated['records']),'nearest_queries':generated['nearest_queries'],
            'ledger':ledger,'ports':outputs,'accepted_wavelength_only':passed,
            'native_promotion_allowed':False,'native_precision_certified':False,
            'scope':'ideal fixed represented scene; conditional wavelength-only many-path bound on CPU',
            'excluded':['geometry/hi-lo position and reference errors','coefficient/source arithmetic',
                        'GPU length accumulation and phase reduction','physical mode overlap',
                        'total native field/intensity error'],
            'no_jev_aval':True}
