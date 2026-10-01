"""Opt-in HOST rational residual -> modeled RN64 argument. NOT native/field execution."""
from copy import deepcopy
from fractions import Fraction as F
import axial_native_quotient_v1 as quotient
from axial_unit_rn64_cpu_v1 import component64,round64
from axial_argument_pi_rn64_cpu_v1 import TWO_PI
from scene_field_producer_cpu_v1 import PI_LOWER,PI_UPPER
MODEL='axial-word-residual-HOST-rational-RN64-argument-CPU-v1'

def require(ok,why):
    if not ok:raise ValueError(why)
def pair(v):
    v=F(v);return [v.numerator,v.denominator]
def integer_HOST(words):
    """Explicit HOST bigint extraction, NOT native uint32 arithmetic."""
    quotient.limb.valid(words)
    n=sum(w<<(32*i) for i,w in enumerate(words))
    return n-2**512 if words[15]&0x80000000 else n

def argument_HOST(numerator_words,denominator_words,*,model):
    require(model==MODEL,'explicit HOST argument model required')
    n=integer_HOST(numerator_words);d=integer_HOST(denominator_words)
    require(d>0,'positive residual denominator')
    residual=F(n,d);require(-F(1,2)<=residual<F(1,2),'centered residual [-1/2,1/2)')
    cast_word,represented=round64(residual);p=component64(TWO_PI)
    out_word,value=round64(represented*p)
    delta=value-represented*p
    constant=max(abs(p-2*PI_LOWER),abs(p-2*PI_UPPER))
    charges={'HOST_residual_RN64_cast':abs(p)*abs(represented-residual),
             'constant_2pi':abs(residual)*constant,'modeled_RN64_multiply':abs(delta)}
    return {'model':MODEL,'numerator_words':list(numerator_words),'denominator_words':list(denominator_words),
            'residual_cycles_rational':pair(residual),'HOST_residual_uint64':cast_word,
            'HOST_residual_rational':pair(represented),'TWO_PI_uint64':TWO_PI,
            'TWO_PI_error_bound_rational':pair(constant),'HOST_argument_uint64':out_word,
            'HOST_argument_uint32_little_endian':[out_word&0xffffffff,out_word>>32],
            'HOST_argument_rational':pair(value),'multiply_rounding_delta_rational':pair(delta),
            'new_argument_charges_rad':{k:pair(v) for k,v in charges.items()},
            'new_argument_error_bound_rad':pair(sum(charges.values(),F(0))),
            'new_HOST_uint32_word_extractions':32,'modeled_RN64_casts':1,'modeled_RN64_multiplies':1,
            'HOST_only':True,'native_argument_implemented':False,'GPU_executed':False,
            'phase_unit_evaluated':False,'accepted_full_field_pipeline':False}

def audit_scene_argument_HOST(name,parent,parent_sha256,overlay,overlay_sha256,*,model):
    require(model==MODEL,'explicit HOST argument model required')
    previous=quotient.audit_scene_cycles(name,parent,parent_sha256,overlay,overlay_sha256,model=quotient.MODEL)
    rows=[]
    for old,proof in zip(previous['sources'],previous['upstream']['sources']):
        row={'source_id':old['source_id'],'phase_reference_id':old['phase_reference_id'],
             'terminal_reference_id':old['terminal_reference_id'],'argument_HOST_evaluated':False,
             'accepted_argument_bound_CPU_only':False,'phase_unit_evaluated':False,'accepted_full_field_pipeline':False}
        if not old['accepted_centered_branch_CPU_only']:
            row['reason']=old['reason']
        else:
            try:
                original=old['original_ideal_cycles'];corners=old['encoded_enclosure_corner_cycles']
                ideal=argument_HOST(original['centered_numerator_words'],original['centered_denominator_words'],model=model)
                encoded=[argument_HOST(c['centered_numerator_words'],c['centered_denominator_words'],model=model) for c in corners]
                cycle_errors=[abs(F(integer_HOST(c['length_words']),integer_HOST(c['wavelength_words']))-
                                   F(integer_HOST(original['length_words']),integer_HOST(original['wavelength_words']))) for c in corners]
                upstream=8*max(cycle_errors)
                cap=proof['original_phase_cap']
                budget=F(integer_HOST(cap['numerator_words']),integer_HOST(cap['denominator_words']))
                # ORIGINAL ideal is a diagnostic/reference, never a nominal encoded output.
                extra=max(F(*v['new_argument_error_bound_rad']) for v in encoded)
                composed=upstream+extra
                row.update(argument_HOST_evaluated=True,ideal_original_argument_HOST=ideal,
                           encoded_enclosure_arguments_HOST=encoded,original_is_NOT_encoded_nominal=True,
                           upstream_phase_error_bound_rad=pair(upstream),new_argument_error_bound_rad=pair(extra),
                           composed_argument_error_bound_rad=pair(composed),unchanged_original_phase_cap_rad=pair(budget),
                           accepted_argument_bound_CPU_only=composed<=budget)
                if composed>budget:row['reason']='HOST argument charges exceed unchanged original phase cap'
            except ValueError as error:row['reason']=str(error)
        rows.append(row)
    return {'model':MODEL,'case_name':name,'input_packet_sha256':parent_sha256,'overlay_sha256':overlay_sha256,
            'scene_binding_sha256':previous['scene_binding_sha256'],'word_ABI_sha256':previous['word_ABI_sha256'],
            'source_order':list(previous['source_order']),'upstream':deepcopy(previous),'sources':rows,
            'accepted_argument_bound_CPU_only':all(r['accepted_argument_bound_CPU_only'] for r in rows),
            'fresh_dependency_recomputation':'own scene/reference/cap/word-quotient, extra redundant HOST work explicit',
            'HOST_only':True,'native_argument_implemented':False,'ALU_executed':False,'Bpy_executed':False,
            'phase_unit_evaluated':False,'field_values_computed':False,'accepted_full_field_pipeline':False,
            'GPU_executed':False,'GPU_job_admission':False,'execution_authenticated':False}
