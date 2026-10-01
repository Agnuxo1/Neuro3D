"""Three own CPU scenes; exact rational oracle isolates final field conversion.

No supplied fields/path bounds and no native/GPU/physical inference claims.
Frozen producer unchanged. Straight integer-cycle paths, no optical splitter.
"""
from fractions import Fraction as F
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1]/'benchmarks/capacity_audit'))
from coherent_reduction_cpu_v1 import rational
from scene_field_producer_cpu_v1 import produce_scene_fields


def direct_scene(fields):
    # Completely new small scene within existing geometry/source profile.
    return {'schema': 'exp005-readback-v2', 'lambda_BU': .125,
        'undeclared_meshes': [], 'objects': {'D': {'kind': 'det',
            'vertices_world_BU': [[2.,.875,-.125],[2.,1.125,-.125],
                                  [2.,1.125,.125],[2.,.875,.125]],
            'faces': [[0,1,2],[0,2,3]], 'mode_origin_BU': [2.,1.,0.],
            'mode_direction': [1.,0.,0.]}},
        'sources': [{'id': 's'+str(i), 'position_BU': [-1.,1.,0.],
            'direction': [1.,0.,0.], 'field_reim': list(field)}
            for i,field in enumerate(fields)]}


def audit_conversion():
    cases = []
    for name,fields in (
            ('ordinary',[(.1,0.)]),
            ('high_amplitude_CPU_only',[(.1*2**25,0.)]),
            ('near_dark_absolute_not_relative',[(.1,0.),(-.1+2.**-30,0.)])):
        scene = direct_scene(fields)
        output = produce_scene_fields(scene,
            coherence_groups={s['id']:'g' for s in scene['sources']})
        # Independent oracle: exact 3 BU, lambda1/8 =>24 full cycles,
        # identity propagation, no coefficients. Ideal field=sum source data.
        for path in output['path_evidence']:
            interval = path['effective_length']
            if interval['rational_lower'] != [3,1] or interval['rational_upper'] != [3,1]:
                raise AssertionError('isolated integer-cycle contract changed')
        ideal = [sum((F(s['field_reim'][k]) for s in scene['sources']), F(0))
                 for k in (0,1)]
        reduced = output['composition']['represented_reduction']['ports']['D']['groups']['g']
        measured = list(map(F,reduced['modeled_field_reim']))
        exact_field_error = sum((abs(a-b) for a,b in zip(measured,ideal)), F(0))
        exact_power_error = abs(sum(x*x for x in measured)-sum(x*x for x in ideal))
        group = output['composition']['ports']['D']['groups']['g']
        port = output['composition']['ports']['D']
        bound_field = F(*group['composed_field_error_upper_rational'])
        bound_power = F(*port['intensity_error_upper_rational'])
        if exact_field_error > bound_field or exact_power_error > bound_power:
            raise AssertionError('producer/composition bound refuted by exact scene oracle')
        cases.append({'name': name, 'snapshot': scene,
            'ideal_field_rational': list(map(rational,ideal)),
            'modeled_field_rational': list(map(rational,measured)),
            'exact_field_error_L1_rational': rational(exact_field_error),
            'exact_intensity_error_rational': rational(exact_power_error),
            'relative_field_error_rational': rational(exact_field_error/sum(abs(x) for x in ideal)),
            'field_bound_rational': rational(bound_field), 'intensity_bound_rational': rational(bound_power),
            'field_gate_satisfied': group['field_budget_satisfied'],
            'intensity_gate_satisfied': port['intensity_budget_satisfied'],
            'producer': output})
    return {'id': 'SCENE-CONVERSION-001-CODEX', 'cases': cases,
        'scope': 'CPU synthetic digital scene field conversion versus EXACT rational source oracle',
        'field_gate': 1e-4, 'intensity_gate': 2e-4, 'GPU_executed': False,
        'native_promotion_allowed': False, 'physical_optics_validated': False,
        'producer_changed': False, 'thresholds_changed': False, 'no_jev_aval': True}
