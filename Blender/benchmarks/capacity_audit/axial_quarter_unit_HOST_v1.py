"""Opt-in HOST RN64 complex propagation unit; phase gate only, NOT source/field/native."""
from copy import deepcopy
from fractions import Fraction as F
import axial_quarter_argument_HOST_v1 as quarter
import axial_unit_rn64_cpu_v1 as polynomial
MODEL='axial-quarter-unit-HOST-RN64-phase-bound-v1'
def require(ok,why):
    if not ok:raise ValueError(why)
def pair(v):
    v=F(v);return [v.numerator,v.denominator]
def angle_bound_from_L1(error):
    error=F(error);require(0<=error<F(1,2),'unit L1 error must be nonnegative and <1/2')
    return error/(1-error)
def unit_HOST(numerator_words,denominator_words,*,model):
    require(model==MODEL,'explicit HOST unit model required')
    arg=quarter.quarter_argument_HOST(numerator_words,denominator_words,model=quarter.MODEL)
    rot=polynomial.rotation64(arg['HOST_argument_uint64'],rotation_model=polynomial.MODEL)
    words=[rot['terms'][name]['output_uint64'] for name in ('cos','sin')]
    permuted=polynomial.permute64(words,arg['quarter_turns_HOST'])
    error=F(*rot['unit_error_L1_upper_rational']);angular=angle_bound_from_L1(error)
    return {'model':MODEL,'quarter_argument':arg,'rotation_RN64':rot,'unpermuted_unit_uint64':words,
        'unit_uint64':permuted,'unit_uint32_little_endian':[[v&0xffffffff,v>>32] for v in permuted],
        'unit_rational':[pair(polynomial.component64(v)) for v in permuted],
        'polynomial_Taylor_error_L1_bound':pair(error),'additional_unit_phase_bound_rad':pair(angular),
        'HOST_only':True,'phase_unit_evaluated':True,'quarter_unit_permutation_executed':True,
        'RN64_polynomial_operations':26,'RN64_coefficient_casts':14,'extra_quarter_argument_casts':1,
        'extra_quarter_argument_multiplies':1,'native_unit_implemented':False,
        'amplitude_budget_accepted':False,'field_values_computed':False,'GPU_executed':False,
        'accepted_full_field_pipeline':False}
def audit_scene_unit_HOST(name,parent,parent_sha256,overlay,overlay_sha256,*,model):
    require(model==MODEL,'explicit HOST unit model required')
    previous=quarter.audit_scene_quarter_HOST(name,parent,parent_sha256,overlay,overlay_sha256,model=quarter.MODEL)
    rows=[]
    for old in previous['sources']:
        row={'source_id':old['source_id'],'phase_reference_id':old['phase_reference_id'],
            'terminal_reference_id':old['terminal_reference_id'],'upstream_quarter_proof':deepcopy(old),
            'unit_HOST_evaluated':False,'accepted_unit_phase_bound_CPU_only':False,
            'amplitude_budget_accepted':False,'field_values_computed':False,'accepted_full_field_pipeline':False}
        if not old['accepted_quarter_argument_bound_CPU_only']:row['reason']=old['reason']
        else:
            try:
                def unit(v):return unit_HOST(v['numerator_words'],v['denominator_words'],model=model)
                original=unit(old['ideal_ORIGINAL_quarter_argument'])
                corners=[unit(v) for v in old['encoded_corner_quarter_arguments']]
                phase=F(*old['composed_quarter_error_bound_rad'])
                extra=max(F(*v['additional_unit_phase_bound_rad']) for v in corners)
                l1=max(F(*v['polynomial_Taylor_error_L1_bound']) for v in corners)
                cap=F(*old['unchanged_original_phase_cap_rad']);total=phase+extra
                row.update(unit_HOST_evaluated=True,ideal_ORIGINAL_unit_HOST=original,encoded_corner_units_HOST=corners,
                    ORIGINAL_is_NOT_encoded_nominal=True,inherited_quarter_phase_bound_rad=pair(phase),
                    additional_unit_phase_bound_rad=pair(extra),composed_unit_phase_bound_rad=pair(total),
                    composed_unit_error_L1_to_ORIGINAL_bound=pair(2*phase+l1),
                    unchanged_original_phase_cap_rad=pair(cap),accepted_unit_phase_bound_CPU_only=total<=cap)
                if total>cap:row['reason']='unit angular charge exceeds unchanged original phase cap'
            except ValueError as e:row['reason']=str(e)
        rows.append(row)
    return {'model':MODEL,'case_name':name,'input_packet_sha256':parent_sha256,'overlay_sha256':overlay_sha256,
        'scene_binding_sha256':previous['scene_binding_sha256'],'word_ABI_sha256':previous['word_ABI_sha256'],
        'source_order':list(previous['source_order']),'sources':rows,
        'accepted_unit_phase_bound_CPU_only':all(v['accepted_unit_phase_bound_CPU_only'] for v in rows),
        'fresh_dependency_recomputation':'own quarter/argument/quotient/scene/ref/cap; extra quarter casts for unit inputs',
        'HOST_only':True,'native_unit_implemented':False,'ALU_executed':False,'Bpy_executed':False,
        'GPU_executed':False,'GPU_job_admission':False,'execution_authenticated':False,
        'source_product_evaluated':False,'field_values_computed':False,'amplitude_budget_accepted':False,
        'accepted_full_field_pipeline':False}
