"""Opt-in scene-derived CPU fields with certified axial transport charged.

One passive mirror, co-moving unit terminal reference, original scene gauge.
Frozen numerical producer/reduction unchanged; no supplied paths/native claim.
"""
from fractions import Fraction as F
import math

from axial_field_budget_cpu_v1 import certify_reflected_transport_field_budget
from exp005_precision_transport_audit import transported
from scene_field_producer_cpu_v1 import produce_scene_fields, rounded_error
from coherent_error_composition_cpu_v1 import compose_field_errors
from axial_root_margin_cpu_v1 import exact_nonnegative, ratio


def inward_budget(value):
    """Frozen reduction accepts float budgets: convert inward, NEVER enlarge."""
    exact = exact_nonnegative(value)
    rounded = float(exact)
    if not math.isfinite(rounded):raise ValueError('finite CPU budget required')
    if F(rounded) > exact:rounded = math.nextafter(rounded,0.)
    return rounded


def produce_axial_transported_scene(snapshot, *, coherence_groups,
        source_absolute_L1_budget, source_relative_L1_budget, phase_budget_rad,
        field_budget, intensity_budget, algorithm='neumaier32', extra_axial_radius_BU=0):
    transport = certify_reflected_transport_field_budget(snapshot,
        coherence_groups=coherence_groups,
        source_absolute_L1_budget=source_absolute_L1_budget,
        source_relative_L1_budget=source_relative_L1_budget,
        phase_budget_rad=phase_budget_rad, field_absolute_L1_budget=field_budget,
        intensity_absolute_budget=intensity_budget, extra_axial_radius_BU=extra_axial_radius_BU)
    ids = [s['id'] for s in snapshot['sources']]
    contributions = transport['contributions']
    paths = transport['path_certificate']['path_certificates']
    if not ids or [r['source_id'] for r in contributions] != ids or [r['source_id'] for r in paths] != ids:
        raise ValueError('complete ordered source/path coverage required')
    # No numeric partial result if any geometric/mode contribution is unproved.
    if any('transport_field_error_L1_upper_rational' not in r for r in contributions):
        return {'schema':'exp005-axial-scene-composition-CPU-v1', 'transport':transport,
            'field_values_computed':False, 'accepted_original_ideal_scene_CPU_only':False,
            'reason':'unproved source/path/mode coverage; numerical producer not executed',
            'native_promotion_allowed':False,'GPU_executed':False,'execution_authenticated':False,
            'no_jev_aval':True}
    decoded,_ = transported(snapshot)
    field_limit,power_limit = inward_budget(field_budget),inward_budget(intensity_budget)
    produced = produce_scene_fields(decoded, coherence_groups=coherence_groups,
        algorithm=algorithm, field_budget=field_limit, intensity_budget=power_limit)
    if produced['scene_binding_sha256'] != transport['decoded_scene_binding_sha256']:
        raise ValueError('decoded producer binding mismatch')
    rows = produced['rows']; bounds = produced['path_error_bounds']; evidence = produced['path_evidence']
    if len(rows) != len(ids) or produced['generated_record_count'] != 3*len(ids) \
            or len(bounds) != len(rows) or len(evidence) != len(rows):
        raise ValueError('complete one-source/one-mirror/one-terminal producer coverage required')
    if len({r['id'] for r in rows}) != len(rows) or len({r['source_id'] for r in rows}) != len(ids) \
            or {r['source_id'] for r in rows} != set(ids) \
            or [r['id'] for r in bounds] != [r['id'] for r in rows] \
            or [r['id'] for r in evidence] != [r['id'] for r in rows]:
        raise ValueError('unique complete source/row/evidence bindings required')
    by_source = {r['source_id']:(r,p) for r,p in zip(contributions,paths)}
    metadata = {sid:{'coherence_group':coherence_groups[sid], 'lambda_BU':snapshot['lambda_BU'],
        'phase_reference_id':'ideal-scene-source-gauge:'+transport['original_scene_binding_sha256']}
        for sid in ids}
    combined = []; components = []
    for row,bound,ev in zip(rows,bounds,evidence):
        sid = row['source_id']; tr,path = by_source[sid]
        if row['port'] != tr['port'] or any(bound[k] != row[k] for k in ('id','source_id','port','field_uint32')):
            raise ValueError('producer port/field binding mismatch')
        length = F(*path['decoded_length_BU']); enc = ev['effective_length']
        lo,hi = F(*enc['rational_lower']),F(*enc['rational_upper'])
        if not lo <= length <= hi:
            raise ValueError('producer effective length excludes certified decoded path')
        prior = F(*bound['field_error_L1_upper_rational'])
        charge = F(*tr['transport_field_error_L1_upper_rational'])
        total = rounded_error(prior+charge)  # Outward only; no fitted tolerance.
        combined.append({**bound, **metadata[sid], 'field_error_L1_upper_rational':total})
        components.append({'id':row['id'],'source_id':sid,'port':row['port'],
            'decoded_length_BU':path['decoded_length_BU'],'producer_effective_length':enc,
            'numerical_producer_error_L1_upper_rational':bound['field_error_L1_upper_rational'],
            'source_charge_L1_upper_rational':tr['source_charge_L1_upper_rational'],
            'phase_charge_L1_upper_rational':tr['phase_charge_L1_upper_rational'],
            'transport_charge_L1_upper_rational':tr['transport_field_error_L1_upper_rational'],
            'combined_error_L1_upper_rational':total})
    composition = compose_field_errors(rows, expected_ids=[r['id'] for r in rows],
        sources=metadata, path_error_bounds=combined, algorithm=algorithm,
        field_budget=field_limit, intensity_budget=power_limit)
    return {'schema':'exp005-axial-scene-composition-CPU-v1','transport':transport,
        'original_scene_binding_sha256':transport['original_scene_binding_sha256'],
        'decoded_scene_binding_sha256':produced['scene_binding_sha256'],
        'decoded_producer_payload_sha256':produced['producer_payload_sha256'],
        'budget_adapter':{'requested_field':ratio(exact_nonnegative(field_budget)),
            'requested_intensity':ratio(exact_nonnegative(intensity_budget)),
            'inward_field':ratio(F(field_limit)),'inward_intensity':ratio(F(power_limit))},
        'decoded_numerical_producer':produced,'sources':metadata,'rows':rows,
        'path_error_bounds':combined,'path_error_components':components,'composition':composition,
        'field_values_computed':True,
        'accepted_original_ideal_scene_CPU_only':transport['accepted_CPU_transport_budget_only']
            and composition['accepted_conditional_upstream_and_reduction_only'],
        'reference':'same original represented one-mirror scene; modeled ABI decode then numerical producer/RN32 reduction',
        'native_promotion_allowed':False,'GPU_executed':False,'execution_authenticated':False,
        'no_jev_aval':True,
        'excluded':['native transport/RN/FTZ/driver/libm/detection arithmetic',
            'non-axial paths, independent terminal reference, active gain or mode overlap',
            'RT, physical optics, general network or performance advantage']}
