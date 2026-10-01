"""Opt-in exact signed512 quotient/centered selector CPU mirror, NOT a field backend."""
from copy import deepcopy
import axial_native_signed512_v1 as limb
import axial_native_original_phase_v1 as phase

MODEL='axial-16limb-euclidean-centered-cycles-CPU-v1'
ONE=[1]+[0]*15
MASK=0xffffffff

def reduce_cycles(length,wavelength,*,model):
    """Exact L=q*w+r; 0<=r<w. Centered tie +1/2 maps to -1/2; no float/RN."""
    limb.require(model==MODEL,'explicit quotient CPU model required')
    limb.valid(length);limb.valid(wavelength)
    limb.require(limb.compare(wavelength,limb.ZERO)>0,'positive signed512 wavelength')
    cost={'bit_rounds':0,'unsigned_shift_words':0,'unsigned_compare_words':0,
          'unsigned_subtract_words':0,'unsigned_increment_words':0}
    def compare(a,b):
        for i in range(15,-1,-1):
            cost['unsigned_compare_words']+=1
            if a[i]!=b[i]:return -1 if a[i]<b[i] else 1
        return 0
    def subtract(a,b):
        out=[];borrow=0
        for x,y in zip(a,b):
            lo=(x-y)&MASK;first=int(x<y)
            v=(lo-borrow)&MASK;second=int(lo<borrow)
            out.append(v);borrow=first|second;cost['unsigned_subtract_words']+=1
        limb.require(borrow==0,'unsigned512 subtract underflow')
        return out
    def increment(a):
        out=list(a);carry=1
        for i in range(16):
            if not carry:break
            old=out[i];out[i]=(old+carry)&MASK;carry=int(out[i]<old)
            cost['unsigned_increment_words']+=1
        limb.require(carry==0,'unsigned512 increment overflow')
        return out
    negative=limb.negative(length)
    magnitude=limb.negate_mod(length) if negative else list(length)
    quotient=[0]*16;remainder=[0]*16
    # Restoring unsigned division of abs(L). abs(INT_MIN) remains unsigned words.
    for bit in range(511,-1,-1):
        carry=(magnitude[bit//32]>>(bit%32))&1
        for i in range(16):
            old=remainder[i];remainder[i]=((old<<1)&MASK)|carry;carry=old>>31
            cost['unsigned_shift_words']+=1
        limb.require(carry==0,'unsigned512 shift overflow')
        if compare(remainder,wavelength)>=0:
            remainder=subtract(remainder,wavelength)
            quotient[bit//32]|=1<<(bit%32)
        cost['bit_rounds']+=1
    if negative:
        if any(remainder):
            quotient=increment(quotient);remainder=subtract(wavelength,remainder)
        limb.require(quotient[15]<0x80000000 or
                     (quotient[15]==0x80000000 and not any(quotient[:15])),
                     'negative signed512 quotient overflow')
        quotient=limb.negate_mod(quotient)
    else:
        limb.require(quotient[15]<0x80000000,'positive signed512 quotient overflow')
    # Compare r with w-r instead of 2*r (which could overflow signed512).
    complement=subtract(wavelength,remainder)
    half_relation=compare(remainder,complement)
    centered_turn=list(quotient);centered_numerator=list(remainder)
    if half_relation>=0:
        centered_turn=limb.add(quotient,ONE)
        centered_numerator=limb.sub(remainder,wavelength)
    return {'model':MODEL,'length_words':list(length),'wavelength_words':list(wavelength),
            'floor_turn_words':quotient,'euclidean_remainder_words':remainder,
            'centered_turn_words':centered_turn,'centered_numerator_words':centered_numerator,
            'centered_denominator_words':list(wavelength),'half_tie_negative':half_relation==0,
            'exact_rational_cycles_CPU_only':True,'new_rounding_phase_error':[0,1],
            'costs_CPU_word_operations':cost,'phase_unit_evaluated':False,
            'accepted_full_field_pipeline':False,'GPU_executed':False}

def centered_branch_matches(original,corners):
    """Selector only for already reduced ORIGINAL + four corners; NOT scene admission."""
    limb.require(type(corners) is list and len(corners)==4,'four reduced enclosure corners')
    turn=limb.valid(original['centered_turn_words'])
    return all(limb.valid(c['centered_turn_words'])==turn for c in corners)

def audit_scene_cycles(name,parent,parent_sha256,overlay,overlay_sha256,*,model):
    """Fresh own scene/reference/cap; ORIGINAL and encoded endpoints kept separate."""
    limb.require(model==MODEL,'explicit quotient CPU model required')
    upstream=phase.audit_scene_original_phase(name,parent,parent_sha256,overlay,overlay_sha256)
    rows=[]
    for prior in upstream['sources']:
        row={'source_id':prior['source_id'],'phase_reference_id':prior['reference']['source_phase_reference_id'],
             'terminal_reference_id':prior['reference']['terminal_reference_id'],
             'cycle_reduction_evaluated_CPU_only':False,'accepted_centered_branch_CPU_only':False,
             'phase_unit_evaluated':False,'accepted_full_field_pipeline':False}
        if not prior['accepted_reference_phase_bound_CPU_only']:
            row['reason']=prior.get('reason','upstream not accepted')
        else:
            try:
                original=reduce_cycles(prior['original_effective_reference_length_words'],
                                       prior['original_lambda_words'],model=model)
                corners=[reduce_cycles(e,w,model=model)
                         for e in prior['reference']['effective_reference_length_interval_words']
                         for w in prior['reference']['wavelength_interval_words']]
                same=centered_branch_matches(original,corners)
                row.update(original_ideal_cycles=original,encoded_enclosure_corner_cycles=corners,
                           cycle_reduction_evaluated_CPU_only=True,accepted_centered_branch_CPU_only=same,
                           original_is_NOT_encoded_nominal=True)
                if not same:row['reason']='centered branch crosses exact half turn; no epsilon or snapping'
            except ValueError as error:row['reason']=str(error)
        rows.append(row)
    return {'model':MODEL,'case_name':name,'input_packet_sha256':parent_sha256,
            'overlay_sha256':overlay_sha256,'scene_binding_sha256':upstream['scene_binding_sha256'],
            'word_ABI_sha256':upstream['word_ABI_sha256'],'source_order':list(upstream['source_order']),
            'upstream':deepcopy(upstream),'sources':rows,
            'accepted_centered_branch_CPU_only':all(r['accepted_centered_branch_CPU_only'] for r in rows),
            'fresh_dependency_recomputation':'own scene YZ/X/events/reference/cap recalculated; no old suites',
            'phase_unit_evaluated':False,'field_values_computed':False,'accepted_full_field_pipeline':False,
            'GLSL_compiled':False,'GPU_executed':False,'GPU_job_admission':False,'execution_authenticated':False}
