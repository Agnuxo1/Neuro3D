"""Opt-in exact CPU root-ray parity after actual hi-lo ABI roundtrip.

No positive hit cutoff, no departure exemption at a source, no fields/phase.
Uses only the inspected pure transported() helper, not its sweep or writer.
"""
from fractions import Fraction as F

from exp005_precision_transport_audit import transported
from history_lineage_cpu_v2 import scene_binding, triangles, vec, nearest, cross, dot


def ratio(x):
    return [x.numerator, x.denominator]


def root_hit(source, packed, geometry):
    try:
        parameter, pid, owner, normal = nearest(vec(source['position_BU']),
            vec(source['direction']), geometry, None)
    except ValueError as exc:
        return {'accepted_exact_CPU_root_query': False, 'reason': str(exc)}
    return {'accepted_exact_CPU_root_query': True,
        'ray_parameter_rational': ratio(parameter), 'primitive_id': pid,
        'object_id': packed.geometry.object_ids[owner],
        'unnormalized_normal_rational': [ratio(x) for x in normal]}


def audit_root_transport(snapshot):
    original_binding, original = scene_binding(snapshot)
    original_geometry = triangles(original)
    before = [root_hit(s, original, original_geometry) for s in snapshot['sources']]
    # Native parameters/deadlines/guards are deliberately not involved here.
    try:
        decoded_snapshot, legacy_delta = transported(snapshot)
        decoded_binding, decoded = scene_binding(decoded_snapshot)
        decoded_geometry = triangles(decoded)
    except (ValueError, OverflowError) as exc:
        return {'schema': 'exp005-root-transport-topology-CPU-v1',
            'original_scene_binding_sha256': original_binding,
            'transport_error': str(exc), 'original_roots': before,
            'accepted_CPU_root_topology_parity_only': False,
            'GPU_executed': False, 'native_promotion_allowed': False,
            'complete_scene_or_field_certified': False, 'no_jev_aval': True}
    if original.geometry.object_ids != decoded.geometry.object_ids or \
            original.source_ids != decoded.source_ids:
        raise ValueError('object/source identity order changed in transport')
    rows = []
    for source, recovered, old in zip(snapshot['sources'], decoded_snapshot['sources'], before):
        new = root_hit(recovered, decoded, decoded_geometry)
        parity = old['accepted_exact_CPU_root_query'] and new['accepted_exact_CPU_root_query']
        if parity:
            n0 = tuple(F(*x) for x in old['unnormalized_normal_rational'])
            n1 = tuple(F(*x) for x in new['unnormalized_normal_rational'])
            parity = old['object_id'] == new['object_id'] and old['primitive_id'] == new['primitive_id'] \
                and cross(n0,n1) == (0,0,0) and dot(n0,n1) > 0
        rows.append({'source_id': source['id'], 'original': old, 'decoded': new,
            'accepted_CPU_root_topology_parity_only': bool(parity)})
    return {'schema': 'exp005-root-transport-topology-CPU-v1',
        'original_scene_binding_sha256': original_binding,
        'decoded_scene_binding_sha256': decoded_binding,
        'object_order': list(original.geometry.object_ids),
        'source_order': list(original.source_ids), 'root_queries': rows,
        'legacy_max_input_delta_float_not_certified_bound': legacy_delta,
        'accepted_CPU_root_topology_parity_only': all(
            row['accepted_CPU_root_topology_parity_only'] for row in rows),
        'GPU_executed': False, 'native_promotion_allowed': False,
        'complete_scene_or_field_certified': False, 'no_jev_aval': True,
        'scope': 'initial declared-source rays only; exact CPU nearest primitive and normal orientation parity',
        'excluded': ['departures/reflected branches and complete histories',
            'length/reference/wavelength/coefficient/field/power budgets',
            'native epsilon/RN/FTZ/driver/authentication, RT and physical optics']}
