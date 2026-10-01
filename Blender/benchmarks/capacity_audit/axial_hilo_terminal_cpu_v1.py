"""Explicit opt-in rational CPU terminal expansion model, NOT an ALU backend.

Scene-derived one-mirror fields; exact rational residual re-encoding is charged.
Frozen binary32 producer/reduction untouched. No supplied fields or GPU paths.
"""
from fractions import Fraction as F
import math
import struct

from axial_field_budget_cpu_v1 import certify_reflected_transport_field_budget
from exp005_precision_transport_audit import transported
from history_lineage_cpu_v2 import scene_binding
from scene_field_producer_cpu_v1 import rotation, product_with_error, PI_LOWER, PI_UPPER, rounded_error
from axial_relative_gate_cpu_v1 import budget, ratio, _relative


def word_value(word):return struct.unpack('<f',struct.pack('<I',word))[0]


def round32_exact(q):
    """Nearest-even rational -> binary32. Search neighbor words, not double-round.

    The binary64 seed locates the nearest binary32 or an adjacent word. Exact
    distances and even mantissa break ties. Chosen output normal-or-zero only.
    """
    q=F(q)
    try:seed=struct.unpack('<I',struct.pack('<f',float(q)))[0]
    except (OverflowError,struct.error):raise ValueError('bounded finite binary32 seed required') from None
    candidates=[]
    for word in {seed,seed-1,seed+1,0,0x80000000}:
        if not 0<=word<2**32:continue
        value=word_value(word)
        if math.isfinite(value):candidates.append((abs(q-F(value)),word&1,word,value))
    if not candidates:raise ValueError('finite binary32 candidates required')
    _,_,word,value=min(candidates)
    if value!=0 and abs(value)<2.**-126:
        raise ValueError('normal-or-zero terminal limbs only; no FTZ assumption')
    # Overflow must not be silently clamped to largest finite neighbor.
    if not math.isfinite(word_value(seed)):
        raise ValueError('binary32 overflow outside terminal contract')
    return word,F(value)


def encode_hilo(q):
    q=F(q);wh,hi=round32_exact(q);wl,lo=round32_exact(q-hi)
    decoded=hi+lo
    return [wh,wl],decoded,abs(decoded-q)


def produce_axial_hilo_model(snapshot, *, terminal_model, coherence_groups,
        source_absolute_L1_budget, source_relative_L1_budget, phase_budget_rad,
        field_budget, intensity_budget, field_relative_budget, intensity_relative_budget):
    if terminal_model!='rational-hilo32-reencode-v1':
        raise ValueError('explicit rational-hilo32-reencode-v1 opt-in required; not an ALU backend')
    limits=list(map(budget,(field_budget,intensity_budget,field_relative_budget,intensity_relative_budget)))
    fb,pb,fr,pr=limits
    transport=certify_reflected_transport_field_budget(snapshot,coherence_groups=coherence_groups,
        source_absolute_L1_budget=source_absolute_L1_budget,source_relative_L1_budget=source_relative_L1_budget,
        phase_budget_rad=phase_budget_rad,field_absolute_L1_budget=fb,intensity_absolute_budget=pb)
    ids=[s['id'] for s in snapshot['sources']];paths=transport['path_certificate']['path_certificates']
    contributions=transport['contributions']
    base={'schema':'exp005-axial-hilo-terminal-rational-CPU-v1','terminal_model':terminal_model,
        'transport':transport,'accepted_original_ideal_scene_CPU_only':False,
        'GPU_executed':False,'native_promotion_allowed':False,'execution_authenticated':False,
        'ALU_reduction_implemented':False,'rational_residual_evaluation':True,'no_jev_aval':True}
    if not 1<=len(ids)<=16 or [p['source_id'] for p in paths]!=ids or [c['source_id'] for c in contributions]!=ids:
        raise ValueError('complete ordered bounded scene source coverage required')
    if any('transport_field_error_L1_upper_rational' not in c for c in contributions):
        return {**base,'field_values_computed':False,'reason':'unproved topology/mode; no field evaluation'}
    decoded,_=transported(snapshot);binding,_=scene_binding(decoded)
    if binding!=transport['decoded_scene_binding_sha256']:raise ValueError('decoded scene binding mismatch')
    rows=[];groups={};reference='ideal-scene-source-gauge:'+transport['original_scene_binding_sha256']
    for s,path,tr in zip(decoded['sources'],paths,contributions):
        if s['id']!=tr['source_id']:raise ValueError('decoded source order mismatch')
        z=tuple(map(F,s['field_reim']));mirror=decoded['objects'][path['mirror_object_id']]
        coeff,ec=rotation(F(mirror['phase_rad']))
        z,ez=product_with_error(z,F(0),tuple(-v for v in coeff),ec)
        turns=F(*path['decoded_length_BU'])/F(decoded['lambda_BU'])
        reduced=turns-((turns+F(1,2))//1)
        unit,et=rotation((PI_LOWER+PI_UPPER)*reduced)
        eu=et+2*abs(reduced)*(PI_UPPER-PI_LOWER)
        approx,en=product_with_error(z,ez,unit,eu)
        words=[];represented=[];conversion=F(0)
        for v in approx:
            w,a,e=encode_hilo(v);words+=w;represented.append(a);conversion+=e
        upstream=F(*tr['transport_field_error_L1_upper_rational'])
        numeric_bound=F(*rounded_error(en))
        combined=F(*rounded_error(numeric_bound+conversion+upstream))
        row={'source_id':s['id'],'port':tr['port'],'coherence_group':coherence_groups[s['id']],
            'phase_reference_id':reference,'field_hilo_uint32':words,
            'decoded_field_rational':[ratio(v) for v in represented],
            'numerical_phase_error_L1_upper_rational':ratio(numeric_bound),
            'conversion_error_L1_rational':ratio(conversion),
            'transport_charge_L1_upper_rational':ratio(upstream),
            'source_charge_L1_upper_rational':tr['source_charge_L1_upper_rational'],
            'phase_charge_L1_upper_rational':tr['phase_charge_L1_upper_rational'],
            'combined_error_L1_upper_rational':ratio(combined),
            'decoded_length_BU':path['decoded_length_BU'],'reduced_turns_rational':ratio(reduced)}
        rows.append(row);key=(tr['port'],coherence_groups[s['id']])
        g=groups.setdefault(key,{'acc':[F(0),F(0)],'exact_sum':[F(0),F(0)],'bound':F(0),'steps':[],'source_ids':[]})
        next_acc=[];next_words=[];step_error=F(0)
        for a,v in zip(g['acc'],represented):
            # Explicit CPU RATIONAL recurrence, not silently claimed TwoSum/ALU.
            w,new,error=encode_hilo(a+v);next_words+=w;next_acc.append(new);step_error+=error
        g['acc']=next_acc;g['exact_sum']=[a+b for a,b in zip(g['exact_sum'],represented)]
        g['bound']+=combined;g['source_ids'].append(s['id'])
        g['steps'].append({'source_id':s['id'],'accumulator_hilo_uint32':next_words,
            'rational_reencode_error_L1_rational':ratio(step_error)})
    ports={};all_valid=True
    for (port,group),g in groups.items():
        y=g['acc'];reduction=sum((abs(a-b) for a,b in zip(y,g['exact_sum'])),F(0))
        total=g['bound']+reduction;norm=sum(map(abs,y),F(0));q=sum((v*v for v in y),F(0))
        pe=2*norm*total+total*total;rel=_relative(norm,total,fr)
        p=ports.setdefault(port,{'groups':{},'observed_power':F(0),'power_error':F(0)})
        p['observed_power']+=q;p['power_error']+=pe
        p['groups'][group]={'source_ids':g['source_ids'],'phase_reference_id':reference,
            'modeled_field_rational':[ratio(v) for v in y],'steps':g['steps'],
            'path_error_sum_L1_upper_rational':ratio(g['bound']),
            'rational_reduction_error_L1_rational':ratio(reduction),
            'field_error_L1_upper_rational':ratio(total),'power_error_upper_rational':ratio(pe),
            'field_absolute_budget_satisfied':total<=fb,'relative_field':rel}
        all_valid=all_valid and total<=fb and rel['relative_budget_satisfied']
    for p in ports.values():
        rel=_relative(p['observed_power'],p['power_error'],pr)
        p['modeled_incoherent_power_rational']=ratio(p.pop('observed_power'))
        p['power_error_upper_rational']=ratio(p.pop('power_error'))
        p['intensity_absolute_budget_satisfied']=F(*p['power_error_upper_rational'])<=pb
        p['relative_intensity']=rel
        all_valid=all_valid and p['intensity_absolute_budget_satisfied'] and rel['relative_budget_satisfied']
    return {**base,'field_values_computed':True,'rows':rows,'ports':ports,
        'original_scene_binding_sha256':transport['original_scene_binding_sha256'],
        'decoded_scene_binding_sha256':binding,
        'accepted_original_ideal_scene_CPU_only':transport['accepted_CPU_transport_budget_only'] and all_valid,
        'field_budget_rational':ratio(fb),'intensity_budget_rational':ratio(pb),
        'field_relative_budget_rational':ratio(fr),'intensity_relative_budget_rational':ratio(pr),
        'new_CPU_work_counts':{'scene_sources':len(ids),'polynomial_rotations':2*len(ids),
            'path_terminal_words':4*len(ids),'rational_reencode_steps':len(ids),'GPU_jobs':0},
        'excluded':['ALU expansion/TwoSum/FTZ/RN/driver/detection/native performance',
            'arbitrary paths, independent terminal reference, RT and physical optics']}
