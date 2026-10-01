"""Scene-bound ideal one-mirror transport contribution budget, not a field runner.

Composes certified axial path phase with exact source hi-lo errors. Unit passive
mirror (-exp(i*phase)) and co-moving unit plane-wave mode are explicit assumptions.
No numerical phase/reduction evaluation or native backend claim.
"""
from fractions import Fraction as F

from axial_root_margin_cpu_v1 import exact_nonnegative, ratio
from axial_reflection_margin_cpu_v1 import certify_axial_reflection
from source_transport_budget_cpu_v1 import audit_source_transport
from exp005_precision_transport_audit import transported
from history_lineage_cpu_v2 import scene_binding, vec


def certify_reflected_transport_field_budget(snapshot, *, coherence_groups,
        source_absolute_L1_budget, source_relative_L1_budget, phase_budget_rad,
        field_absolute_L1_budget, intensity_absolute_budget, extra_axial_radius_BU=0):
    field_budget = exact_nonnegative(field_absolute_L1_budget)
    power_budget = exact_nonnegative(intensity_absolute_budget)
    path = certify_axial_reflection(snapshot,phase_budget_rad=phase_budget_rad,
                                  extra_axial_radius_BU=extra_axial_radius_BU)
    source_transport = audit_source_transport(snapshot,coherence_groups=coherence_groups,
        absolute_L1_budget=source_absolute_L1_budget,relative_L1_budget=source_relative_L1_budget)
    recovered,_ = transported(snapshot)
    binding,_ = scene_binding(recovered)
    if source_transport['scene_binding_sha256'] != path['original_scene_binding_sha256'] \
            or binding != path['decoded_scene_binding_sha256']:
        raise ValueError('source/path/decoded scene binding mismatch')
    rows = []
    groups = {}
    for original,decoded,sr,pr in zip(snapshot['sources'],recovered['sources'],source_transport['sources'],path['path_certificates']):
        sid = original['id']
        if (sid,)*3 != (decoded['id'],sr['source_id'],pr['source_id']):
            raise ValueError('source order mismatch')
        row = {'source_id':sid,'coherence_group':coherence_groups[sid],
               'accepted_CPU_transport_contribution_only':False}
        try:
            if not pr['accepted_CPU_one_bounce_topology']:
                raise ValueError('unproved one-mirror path: '+pr.get('reason','topology failed'))
            terminal = pr['terminal_object_id']
            incoming = (-F(original['direction'][0]),F(0),F(0))
            for scene in (snapshot,recovered):
                obj = scene['objects'][terminal]
                reference = vec(obj['mode_origin_BU'])
                if reference[0] != F(obj['vertices_world_BU'][0][0]) or vec(obj['mode_direction']) != incoming:
                    raise ValueError('co-moving terminal-plane reference and incoming unit mode required')
            # Conditional extra axial motion also moves the terminal reference
            # with its plane: modal length correction remains identically zero.
            z0 = tuple(map(F,original['field_reim']))
            zd = tuple(F(*c['modeled_CPU64_decode_rational']) for c in sr['components'])
            if zd != tuple(map(F,decoded['field_reim'])):
                raise ValueError('path/source modeled decode mismatch')
            norm = sum(map(abs,z0),F(0))
            source_error = F(*sr['source_transport_error_L1_rational'])
            phase_error = F(*pr['phase_error_bound_rad'])
            # Unit rotations: ||delta z * unit||1 <= 2||delta z||1.
            # Chord2 <= |delta theta|; chord1 <= 2*|delta theta|.
            amplitude_charge = 2*source_error
            phase_charge = 2*norm*phase_error
            combined = amplitude_charge+phase_charge
            accepted = sr['accepted_CPU_source_transport_budget_only'] and pr['accepted_CPU_one_bounce_phase_budget']
            row.update(port=terminal,original_amplitude_L1_upper_rational=ratio(norm),
                source_charge_L1_upper_rational=ratio(amplitude_charge),
                phase_charge_L1_upper_rational=ratio(phase_charge),
                transport_field_error_L1_upper_rational=ratio(combined),
                source_phase_reference_id=pr['phase_reference_id'],
                common_phase_reference_id='ideal-scene-source-gauge:'+path['original_scene_binding_sha256'],
                accepted_CPU_transport_contribution_only=accepted,
                source_budget_satisfied=sr['accepted_CPU_source_transport_budget_only'],
                path_phase_budget_satisfied=pr['accepted_CPU_one_bounce_phase_budget'])
            key = (terminal,coherence_groups[sid])
            group = groups.setdefault(key,{'norm':F(0),'error':F(0),'source_ids':[],'accepted':True})
            group['norm'] += norm
            group['error'] += combined
            group['source_ids'].append(sid)
            group['accepted'] = group['accepted'] and accepted
        except ValueError as exc:
            row['reason'] = str(exc)
        rows.append(row)
    # Never mark a partial coherent group accepted when a source lacked a
    # path/mode bound. Numeric rows remain diagnostics for listed contributors.
    coverage_complete = all('transport_field_error_L1_upper_rational' in r for r in rows)
    terminals = []
    for (port,coherence_group),group in groups.items():
        norm,error = group['norm'],group['error']
        intensity = 2*norm*error+error*error
        terminals.append({'port':port,'coherence_group':coherence_group,'source_ids':group['source_ids'],
            'original_coherent_modulus_upper_rational':ratio(norm),
            'transport_field_error_L1_upper_rational':ratio(error),
            'transport_intensity_error_upper_rational':ratio(intensity),
            'field_budget_satisfied':error <= field_budget,'intensity_budget_satisfied':intensity <= power_budget,
            'scene_source_coverage_complete':coverage_complete,
            'accepted_CPU_transport_budget_only':coverage_complete and group['accepted'] and error <= field_budget and intensity <= power_budget})
    return {'schema':'exp005-axial-field-transport-budget-CPU-v1',
        'original_scene_binding_sha256':path['original_scene_binding_sha256'],
        'decoded_scene_binding_sha256':path['decoded_scene_binding_sha256'],
        'path_certificate':path,'source_transport':source_transport,'contributions':rows,'terminal_groups':terminals,
        'field_absolute_L1_budget':ratio(field_budget),'intensity_absolute_budget':ratio(power_budget),
        'accepted_CPU_transport_budget_only':all(r['accepted_CPU_transport_contribution_only'] for r in rows)
            and all(r['accepted_CPU_transport_budget_only'] for r in terminals),
        'field_values_computed':False,'native_promotion_allowed':False,'GPU_executed':False,'no_jev_aval':True,
        'scope':'conditional ideal one-mirror path, co-moving unit terminal reference, source-zero gauge; transport contribution bounds only',
        'excluded':['numerical phase evaluation, float32 conversion/reduction/detection error',
            'relative terminal field/intensity, arbitrary paths or modal overlap',
            'native arithmetic/bias/FTZ/driver/auth/RT/physical optics']}
