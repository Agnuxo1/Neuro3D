"""Opt-in exact HOST quarter reduction and modeled RN64 argument; NOT a unit/kernel."""
from copy import deepcopy
from fractions import Fraction as F
import axial_native_argument_HOST_v1 as prev
MODEL='axial-quarter-rational-HOST-RN64-argument-v1'
CROSS='quarter branch crosses exact eighth turn; no epsilon or snapping'

def require(ok,why):
    if not ok:raise ValueError(why)
def pair(v):
    v=F(v);return [v.numerator,v.denominator]
def quarter_argument_HOST(numerator_words,denominator_words,*,model):
    require(model==MODEL,'explicit quarter HOST model required')
    n=prev.integer_HOST(numerator_words);d=prev.integer_HOST(denominator_words)
    require(d>0,'positive denominator')
    r=F(n,d);require(-F(1,2)<=r<F(1,2),'centered residual [-1/2,1/2)')
    selector=4*r+F(1,2);k=selector.numerator//selector.denominator;t=r-F(k,4)
    require(-F(1,8)<=t<F(1,8),'exact quarter residual [-1/8,1/8)')
    # t is an explicitly arbitrary-width HOST rational, NOT a new signed512 packet.
    cw,cast=prev.round64(t);p=prev.component64(prev.TWO_PI)
    aw,arg=prev.round64(cast*p);delta=arg-cast*p
    const=max(abs(p-2*prev.PI_LOWER),abs(p-2*prev.PI_UPPER))
    charges={'HOST_quarter_RN64_cast':abs(p)*abs(cast-t),
             'constant_2pi':abs(t)*const,'modeled_RN64_multiply':abs(delta)}
    require(abs(arg)<=1,'represented folded argument outside frozen Horner domain')
    return {'model':MODEL,'numerator_words':list(numerator_words),'denominator_words':list(denominator_words),
        'original_residual_cycles_rational':pair(r),'quarter_turns_HOST':k,'quadrant_mod4':k%4,
        'quarter_residual_HOST_rational':pair(t),'exact_selector_error_cycles':[0,1],
        'HOST_cast_uint64':cw,'HOST_cast_rational':pair(cast),'TWO_PI_uint64':prev.TWO_PI,
        'TWO_PI_error_bound_rad':pair(const),'HOST_argument_uint64':aw,
        'HOST_argument_uint32_little_endian':[aw&0xffffffff,aw>>32],'HOST_argument_rational':pair(arg),
        'multiply_rounding_delta_rad':pair(delta),'quarter_argument_charges_rad':{key:pair(v) for key,v in charges.items()},
        'quarter_argument_error_bound_rad':pair(sum(charges.values(),F(0))),
        'MAIN_HOST_uint32_word_extractions':32,'modeled_RN64_casts':1,'modeled_RN64_multiplies':1,
        'HOST_only':True,'native_quarter_implemented':False,'quarter_unit_permutation_executed':False,
        'phase_unit_evaluated':False,'GPU_executed':False,'accepted_full_field_pipeline':False}

def projection(old):
    keys=('source_id','phase_reference_id','terminal_reference_id','accepted_argument_bound_CPU_only','reason',
          'upstream_phase_error_bound_rad','unchanged_original_phase_cap_rad')
    p={key:deepcopy(old[key]) for key in keys if key in old}
    if old['accepted_argument_bound_CPU_only']:
        def words(v):return {k:list(v[k]) for k in ('numerator_words','denominator_words')}
        p['ORIGINAL_residual_words']=words(old['ideal_original_argument_HOST'])
        p['encoded_corner_residual_words']=[words(v) for v in old['encoded_enclosure_arguments_HOST']]
    return p

def audit_scene_quarter_HOST(name,parent,parent_sha256,overlay,overlay_sha256,*,model):
    require(model==MODEL,'explicit quarter HOST model required')
    prior=prev.audit_scene_argument_HOST(name,parent,parent_sha256,overlay,overlay_sha256,model=prev.MODEL)
    rows=[]
    for old in prior['sources']:
        proof=projection(old)
        row={'source_id':old['source_id'],'phase_reference_id':old['phase_reference_id'],
             'terminal_reference_id':old['terminal_reference_id'],'upstream_argument_proof':proof,
             'quarter_HOST_evaluated':False,'accepted_quarter_argument_bound_CPU_only':False}
        if not old['accepted_argument_bound_CPU_only']:row['reason']=old['reason']
        else:
            try:
                def fold(v):return quarter_argument_HOST(v['numerator_words'],v['denominator_words'],model=model)
                original=fold(proof['ORIGINAL_residual_words'])
                corners=[fold(v) for v in proof['encoded_corner_residual_words']]
                same=all(v['quarter_turns_HOST']==original['quarter_turns_HOST'] for v in corners)
                upstream=F(*proof['upstream_phase_error_bound_rad'])
                extra=max(F(*v['quarter_argument_error_bound_rad']) for v in corners)
                budget=F(*proof['unchanged_original_phase_cap_rad']);total=upstream+extra
                row.update(quarter_HOST_evaluated=True,ideal_ORIGINAL_quarter_argument=original,
                    encoded_corner_quarter_arguments=corners,same_exact_quarter_branch=same,
                    ORIGINAL_is_NOT_encoded_nominal=True,quarter_argument_error_bound_rad=pair(extra),
                    composed_quarter_error_bound_rad=pair(total),unchanged_original_phase_cap_rad=pair(budget),
                    accepted_quarter_argument_bound_CPU_only=same and total<=budget)
                if not same:row['reason']=CROSS
                elif total>budget:row['reason']='quarter HOST charges exceed unchanged original phase cap'
            except ValueError as error:row['reason']=str(error)
        rows.append(row)
    return {'model':MODEL,'case_name':name,'input_packet_sha256':parent_sha256,'overlay_sha256':overlay_sha256,
        'scene_binding_sha256':prior['scene_binding_sha256'],'word_ABI_sha256':prior['word_ABI_sha256'],
        'source_order':list(prior['source_order']),'sources':rows,
        'accepted_quarter_argument_bound_CPU_only':all(v['accepted_quarter_argument_bound_CPU_only'] for v in rows),
        'fresh_dependency_recomputation':'own argument/quotient/scene/ref/cap reevaluated; old argument RN cost is EXTRA, not reused',
        'HOST_only':True,'native_quarter_implemented':False,'ALU_executed':False,'Bpy_executed':False,
        'quarter_unit_permutation_executed':False,'phase_unit_evaluated':False,'field_values_computed':False,
        'GPU_executed':False,'GPU_job_admission':False,'execution_authenticated':False,'accepted_full_field_pipeline':False}
