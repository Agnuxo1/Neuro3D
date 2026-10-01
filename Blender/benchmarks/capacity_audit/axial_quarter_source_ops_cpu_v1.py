"""Scene-derived exact quarter-cycle word permutation, CPU modeled RN32 reduction.

Restricted explicit opt-in; not supplied terminals, cached fields or a GPU kernel.
"""
from fractions import Fraction as F

from axial_field_budget_cpu_v1 import certify_reflected_transport_field_budget
from exp005_precision_transport_audit import transported
from history_lineage_cpu_v2 import scene_binding
from axial_hilo_ops_cpu_v1 import component, _case
from axial_relative_gate_cpu_v1 import ratio, budget

MODEL='axial-quarter-source-words-v1'


def permute_source_words(words,quarter):
    if not isinstance(words,list) or len(words)!=4 or type(quarter) is not int or quarter not in range(4):
        raise ValueError('four source limbs and exact quarter index required')
    list(map(component,words))  # All limbs normal/zero; no FTZ or hidden cast.
    re,im=words[:2],words[2:]
    negate=lambda pair:[w^0x80000000 for w in pair]
    if quarter==0:return negate(re)+negate(im)
    if quarter==1:return im+negate(re)
    if quarter==2:return re+im
    return negate(im)+re


def produce_quarter_source_operations(snapshot,*,phase_model,coherence_groups,
        source_absolute_L1_budget,source_relative_L1_budget,phase_budget_rad,
        field_budget,intensity_budget,field_relative_budget,intensity_relative_budget):
    if phase_model!=MODEL:raise ValueError('explicit axial-quarter-source-words-v1 required')
    fb,pb,fr,ir=map(budget,(field_budget,intensity_budget,field_relative_budget,intensity_relative_budget))
    transport=certify_reflected_transport_field_budget(snapshot,coherence_groups=coherence_groups,
        source_absolute_L1_budget=source_absolute_L1_budget,source_relative_L1_budget=source_relative_L1_budget,
        phase_budget_rad=phase_budget_rad,field_absolute_L1_budget=fb,intensity_absolute_budget=pb)
    base={'schema':'exp005-axial-quarter-source-operations-CPU-v1','phase_model':phase_model,
        'transport':transport,'field_values_computed':False,'accepted_original_ideal_scene_CPU_only':False,
        'GPU_executed':False,'ALU_executed':False,'native_promotion_allowed':False,
        'execution_authenticated':False,'no_jev_aval':True,'source_words_from_scene_ABI_model':True,
        'cached_or_supplied_terminal_fields':False,'rational_terminal_residual_reencoding':False}
    ids=[s['id'] for s in snapshot['sources']];paths=transport['path_certificate']['path_certificates']
    sources=transport['source_transport']['sources'];contributions=transport['contributions']
    if not 1<=len(ids)<=16 or any([r['source_id'] for r in seq]!=ids for seq in (paths,sources,contributions)):
        raise ValueError('complete ordered bounded scene/source/path coverage required')
    if any('transport_field_error_L1_upper_rational' not in c for c in contributions):
        return {**base,'reason':'unproved scene topology/mode; no terminal generation'}
    decoded,_=transported(snapshot);binding,_=scene_binding(decoded)
    if binding!=transport['decoded_scene_binding_sha256']:raise ValueError('decoded scene binding mismatch')
    quarters=[]
    # All paths admitted before generating ANY terminal. No partial fallback.
    for p in paths:
        mid=p['mirror_object_id']
        if snapshot['objects'][mid]['phase_rad']!=0 or decoded['objects'][mid]['phase_rad']!=0:
            return {**base,'reason':'original and decoded mirror phase must be exactly zero'}
        cycles4=4*F(*p['decoded_length_BU'])/F(decoded['lambda_BU'])
        if cycles4.denominator!=1:
            return {**base,'reason':'decoded phase is not an exact quarter cycle; no approximation/fallback'}
        quarters.append((int(cycles4)%4,cycles4))
    rows=[];ports={};xors=0;swaps=0
    reference='ideal-scene-source-gauge:'+transport['original_scene_binding_sha256']
    for sr,tr,(k,cycles4) in zip(sources,contributions,quarters):
        source_words=[w for c in sr['components'] for w in c['limb_uint32']]
        output=permute_source_words(source_words,k)
        vals=list(map(component,source_words));original_limb_sum=[vals[0]+vals[1],vals[2]+vals[3]]
        decode=[F(*c['modeled_CPU64_decode_rational']) for c in sr['components']]
        decode_charge=sum((abs(a-b) for a,b in zip(original_limb_sum,decode)),F(0))
        transport_charge=F(*tr['transport_field_error_L1_upper_rational']);combined=decode_charge+transport_charge
        values=list(map(component,output));field=[values[0]+values[1],values[2]+values[3]]
        row={'source_id':sr['source_id'],'port':tr['port'],'coherence_group':coherence_groups[sr['source_id']],
            'phase_reference_id':reference,'source_limb_uint32':source_words,'field_hilo_uint32':output,
            'decoded_field_rational':[ratio(v) for v in field],'quarter_index':k,
            'four_decoded_cycles_rational':ratio(cycles4),'packed_field_offsets':sr['packed_field_offsets'],
            'limb_vs_CPU64_decode_charge_L1_rational':ratio(decode_charge),
            'transport_charge_L1_upper_rational':ratio(transport_charge),
            'source_charge_L1_upper_rational':tr['source_charge_L1_upper_rational'],
            'phase_charge_L1_upper_rational':tr['phase_charge_L1_upper_rational'],
            'combined_error_L1_upper_rational':ratio(combined)}
        rows.append(row);p=ports.setdefault(tr['port'],{'groups':{}})
        g=p['groups'].setdefault(row['coherence_group'],{'source_ids':[]});g['source_ids'].append(sr['source_id'])
        xors+={0:4,1:2,2:0,3:2}[k];swaps+=k%2
    # Explicit structural adapter to the frozen reducer, NOT a retained report.
    adapter={'accepted_original_ideal_scene_CPU_only':transport['accepted_CPU_transport_budget_only'],
        'field_values_computed':True,'original_scene_binding_sha256':transport['original_scene_binding_sha256'],
        'decoded_scene_binding_sha256':binding,'rows':rows,'transport':transport,'ports':ports,
        'field_budget_rational':ratio(fb),'intensity_budget_rational':ratio(pb),
        'field_relative_budget_rational':ratio(fr),'intensity_relative_budget_rational':ratio(ir)}
    reduced=_case(adapter)
    reduced['new_scene_transport_accepted']=reduced.pop('previous_case_accepted')
    reduced.pop('field_values_regenerated');reduced['reads_new_scene_generated_source_word_terminals']=True
    return {**base,'field_values_computed':True,'rows':rows,'reduction':reduced,
        'original_scene_binding_sha256':transport['original_scene_binding_sha256'],'decoded_scene_binding_sha256':binding,
        'accepted_original_ideal_scene_CPU_only':reduced['accepted_operation_model_CPU_only'],
        'work_counts':{'source_word_reads':4*len(ids),'signbit_xors':xors,'complex_component_swaps':swaps,
            'terminal_RN32_product_ops':0,'RN32_reduction_ops':reduced['RN32_operations'],'GPU_jobs':0},
        'cost_excludes':['CPU rational admission/oracle, packing and geometric certification',
            'native phase selector, general phase producer, IO, memory, energy and detector']}
