"""Opt-in CPU producer with source hi-lo error charged BEFORE propagation.

Only source field_reim changes. Geometry, directions, optics, reference and
wavelength remain represented originals; no native/Blender/RT validation.
"""
from copy import deepcopy
from fractions import Fraction as F

from source_transport_budget_cpu_v1 import audit_source_transport
from scene_field_producer_cpu_v1 import produce_scene_fields, rounded_error
from coherent_error_composition_cpu_v1 import compose_field_errors


def produce_with_source_transport(snapshot, *, coherence_groups,
                                  source_absolute_L1_budget,
                                  source_relative_L1_budget,
                                  algorithm='neumaier32', field_budget=1e-4,
                                  intensity_budget=2e-4):
    transport = audit_source_transport(snapshot, coherence_groups=coherence_groups,
        absolute_L1_budget=source_absolute_L1_budget,
        relative_L1_budget=source_relative_L1_budget)
    decoded = deepcopy(snapshot)
    source_errors = {}
    for source, row in zip(decoded['sources'], transport['sources']):
        if source['id'] != row['source_id']:
            raise ValueError('source order binding changed')
        source['field_reim'] = [float(F(*c['modeled_CPU64_decode_rational']))
                                for c in row['components']]
        source_errors[source['id']] = F(*row['source_transport_error_L1_rational'])
    # This is a NEW input to the frozen producer, not replay of its old tests.
    produced = produce_scene_fields(decoded, coherence_groups=coherence_groups,
        algorithm=algorithm, field_budget=field_budget, intensity_budget=intensity_budget)
    original_binding = transport['scene_binding_sha256']
    metadata = {sid: {'coherence_group': group, 'lambda_BU': snapshot['lambda_BU'],
        'phase_reference_id': 'ideal-scene-source-gauge:'+original_binding}
        for sid, group in coherence_groups.items()}
    bounds = []; components = []
    for record in produced['path_error_bounds']:
        # Ideal passive path: product of sqrt(T), sqrt(1-T), unit mirrors
        # and exp(i*phase) has complex modulus<=1. Thus terminal L1 error
        # <=sqrt(2)*input L1 <=2*input L1. No gain/mode amplification here.
        sid = record['source_id']
        prior = F(*record['field_error_L1_upper_rational'])
        source_charge = 2*source_errors[sid]
        combined = rounded_error(prior+source_charge)  # Outward only.
        bounds.append({**record, **metadata[sid],
            'field_error_L1_upper_rational': combined})
        components.append({'id': record['id'], 'source_id': sid, 'port': record['port'],
            'decoded_scene_producer_error_L1_upper_rational': record['field_error_L1_upper_rational'],
            'propagated_source_transport_L1_upper_rational': [source_charge.numerator, source_charge.denominator],
            'combined_path_error_L1_upper_rational': combined})
    composition = compose_field_errors(produced['rows'],
        expected_ids=[row['id'] for row in produced['rows']], sources=metadata,
        path_error_bounds=bounds, algorithm=algorithm, field_budget=field_budget,
        intensity_budget=intensity_budget)
    return {'schema': 'exp005-scene-source-transport-composition-CPU-v1',
        'original_scene_binding_sha256': original_binding,
        'decoded_scene_binding_sha256': produced['scene_binding_sha256'],
        'decoded_producer_payload_sha256': produced['producer_payload_sha256'],
        'source_transport': transport, 'rows': produced['rows'], 'sources': metadata,
        'path_error_bounds': bounds, 'path_error_components': components,
        'composition': composition, 'generated_record_count': produced['generated_record_count'],
        'passive_source_to_path_L1_factor_upper_rational': [2,1],
        'accepted_original_ideal_scene_CPU_only':
            transport['accepted_CPU_source_transport_budget_only'] and
            composition['accepted_conditional_upstream_and_reduction_only'],
        'reference': 'original represented scene; only source amplitude underwent modeled hi-lo transport',
        'native_promotion_allowed': False, 'GPU_executed': False,
        'execution_authenticated': False, 'no_jev_aval': True,
        'excluded': ['transport of geometry/directions/optics/reference/wavelength',
            'GPU phase/coefficient/RN/FTZ/driver and native detection',
            'active gain, nonunit mode projection, RT and physical optics']}
