"""Original packed source fields times scene-derived unit; opt-in synthetic CPU."""
from copy import deepcopy
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import struct
from history_lineage_cpu_v2 import scene_binding
from exp005_blender_gpu import split_double
from axial_hilo_ops_cpu_v1 import component
from axial_unit_rn64_cpu_v1 import component64
from axial_relative_gate_cpu_v1 import ratio
from axial_source_product_rn64_cpu_v1 import product_words,MODEL as PRODUCT
from axial_geometry_unit_cpu_v1 import report,digest
from axial_source_product_rn64_cpu_v1 import payload
ROOT=Path(__file__).resolve().parents[3]
REPORT='coordinacion/respuestas/AXIAL-GEOMETRY-UNIT-001-CODEX.json'
SHA='525e7dc3fe7ffb2971390a0cc4034dafe07fd585d64f040223ac8b4ede5ef1cb'
GEOMETRY='coordinacion/respuestas/AXIAL-GEOMETRY-WORDS-001-CODEX.json'
GEOMETRY_SHA='dfdb03a27f7aaa58dd05d750ea1980de789281ed798b75fd2c5209d12712a5fa'
CACHE='coordinacion/respuestas/AXIAL-SOURCE-ARGUMENT-RN64-001-CODEX.json'
CACHE_SHA='a70cc95da56063c96eeb853b95409903212f728efa472421fbb04465dc8b40e6'
CODE='Blender/benchmarks/capacity_audit/axial_source_product_rn64_cpu_v1.py'
MODEL='scene-derived-unit-original-source-ABI-RN64-CPU-v1'

def cap(value):
    if type(value) is int or isinstance(value,F):
        result=F(value)
    elif isinstance(value,list) and len(value)==2 and all(type(x) is int for x in value) and value[1]>0:
        result=F(*value)
    else:raise ValueError('explicit exact nonnegative per-source field cap required')
    if result<0:raise ValueError('negative field cap')
    return result

def load_retained():
    r=report(REPORT,SHA);g=report(GEOMETRY,GEOMETRY_SHA);old=report(CACHE,CACHE_SHA)
    if r['id']!='AXIAL-GEOMETRY-UNIT-001' or old['run']['rc']!=0:
        raise ValueError('retained identity/status mismatch')
    # payload reads run; this new report uses test_run, but validates its bytes.
    units=payload({'run':r['test_run']})['audit']['cases']
    scenes=payload({'run':g['test_run']})['cases']
    prior=payload(old)['audit']['cases'];pins=dict(r['code_doc_sha256'],**{REPORT:SHA})
    if pins[CODE]!=old['code_doc_sha256'][CODE]:raise ValueError('product cache code mismatch')
    bank={}
    for c in prior.values():
        for p in c['paths']:
            sig=p['cache_signature'];m=p['measurement']
            if sig['model']!=PRODUCT or sig['product_code_sha256']!=pins[CODE]:
                raise ValueError('product cache model/signature mismatch')
            key=tuple(m['source_limb_uint32']+m['unit_uint64'])
            if key in bank and digest(bank[key])!=digest(m):raise ValueError('conflicting pure product cache')
            bank[key]=deepcopy(m)
    return pins,units,scenes,bank

def compose(unit,geometry,budgets,bank,code_sha):
    abi=geometry['word_ABI'];snapshot=deepcopy(geometry['scene_snapshot'])
    snapshot['objects']={name:snapshot['objects'][name] for name in abi['object_ids']}
    binding,packed=scene_binding(snapshot)
    ids=list(packed.source_ids)
    if binding!=unit['original_scene_binding_sha256'] or binding!=abi['original_scene_binding_sha256']:
        raise ValueError('original scene binding mismatch')
    if ids!=abi['source_order'] or ids!=[p['source_id'] for p in unit['paths']] or ids!=[p['source_id'] for p in geometry['sources']]:
        raise ValueError('ordered complete source IDs required')
    if type(budgets) is not dict or set(budgets)!=set(ids):
        raise ValueError('explicit complete per-source caps required; no default')
    limits={sid:cap(budgets[sid]) for sid in ids}
    out={'original_scene_binding_sha256':binding,'retained_unit_case_sha256':digest(unit),
         'source_order':ids,'paths':[],'accepted_source_product_absolute_CPU_only':False,
         'new_RN64_operations':0,'cached_RN64_operations_NOT_executed':0,
         'source_HOST_RN32_encodings':0}
    for i,(sid,up,gp) in enumerate(zip(ids,unit['paths'],geometry['sources'])):
        row={'source_id':sid,'previous_unit_accepted':up['accepted_unit_CPU_only'],
             'product_evaluated':False,'accepted_source_product_absolute_CPU_only':False,
             'field_absolute_L1_budget':ratio(limits[sid])};out['paths'].append(row)
        if not up['accepted_unit_CPU_only']:
            row['reason']='retained scene unit rejected; no source encode/decode/product';continue
        ref='original-source-zero:'+binding+':'+sid
        if up['phase_reference_id']!=ref or gp['phase_reference_id']!=ref:
            raise ValueError('original source phase reference mismatch')
        mirror=abi['object_ids'][gp['mirror_owner']];terminal=abi['object_ids'][gp['terminal_owner']]
        if snapshot['objects'][mirror]['kind']!='mirror' or F(snapshot['objects'][mirror]['phase_rad'])!=0:
            raise ValueError('original mirror-zero reflection required')
        source=snapshot['sources'][i];raw=packed.sources[8*i:8*i+8]
        original=[F(raw[j]) for j in (3,7)]
        if source['id']!=sid or original!=list(map(F,source['field_reim'])):
            raise ValueError('original source ABI field mismatch')
        words=[]
        for v in (raw[3],raw[7]):
            hi,lo=split_double(v)
            words.extend(struct.unpack('<I',struct.pack('<f',x))[0] for x in (hi,lo))
        sums=[component(words[j])+component(words[j+1]) for j in (0,2)]
        encoding=sum((abs(a-b) for a,b in zip(original,sums)),F(0))
        out['source_HOST_RN32_encodings']+=4
        reflected=[w^(1<<63) for w in up['unit_uint64']]
        key=tuple(words+reflected);reused=key in bank
        m=deepcopy(bank[key]) if reused else product_words(words,reflected,product_model=PRODUCT)
        if m['source_limb_uint32']!=words or m['unit_uint64']!=reflected or m['RN64_operations']!=8:
            raise ValueError('pure product input/node mismatch')
        out['cached_RN64_operations_NOT_executed' if reused else 'new_RN64_operations']+=8
        unorm=sum((abs(component64(w)) for w in reflected),F(0));anorm=sum(map(abs,original),F(0))
        eu=F(*up['composed_unit_error_L1_upper'])
        charges={'source_encoding':encoding*unorm,
                 'source_decode':F(*m['source_decode_error_L1_upper_rational'])*unorm,
                 'original_source_norm_times_unit_error':anorm*eu,
                 'product_RN64':F(*m['product_error_L1_upper_rational'])}
        total=sum(charges.values(),F(0))
        row.update(product_evaluated=not reused,product_cache_reused=reused,
                   phase_reference_id=ref,port=terminal,
                   source_ABI={'layout':'pack_frontier stride8 indices3/7; HOST split_double hi-lo32',
                               'packed_source_stride8_rational':[ratio(F(v)) for v in raw],
                               'source_limb_uint32':words,'source_original_rational':[ratio(v) for v in original],
                               'source_exact_limb_sum_rational':[ratio(v) for v in sums]},
                   mirror_coefficient_exact_reim=[[-1,1],[0,1]],
                   cache_signature={'model':PRODUCT,'code_sha256':code_sha,
                                    'source_limb_uint32':words,'unit_uint64':reflected,
                                    'report_sha256':CACHE_SHA if reused else None},
                   measurement=m,source_encoding_error_L1=ratio(encoding),
                   original_source_norm_L1=ratio(anorm),observed_unit_norm_L1=ratio(unorm),
                   retained_scene_unit_error_L1=ratio(eu),
                   error_charges_L1={k:ratio(v) for k,v in charges.items()},
                   composed_path_field_error_L1=ratio(total),
                   accepted_source_product_absolute_CPU_only=total<=limits[sid])
    out['accepted_source_product_absolute_CPU_only']=all(p['accepted_source_product_absolute_CPU_only'] for p in out['paths'])
    return out

def audit_scene_source_products(*,case_names,field_caps,product_model):
    if product_model!=MODEL:raise ValueError('explicit scene source product CPU model required')
    if not isinstance(case_names,list) or not case_names or any(type(n) is not str for n in case_names) or len(set(case_names))!=len(case_names):
        raise ValueError('explicit unique retained case selection required')
    pins,units,scenes,bank=load_retained()
    if any(n not in units for n in case_names):raise ValueError('unknown retained case')
    if type(field_caps) is not dict or set(field_caps)!=set(case_names):
        raise ValueError('explicit complete case field caps required')
    cases={n:compose(units[n],scenes[n],field_caps[n],bank,pins[CODE]) for n in case_names}
    return {'model':MODEL,'cases':cases,'pins_verified':pins,'retained_report_sha256':SHA,
            'geometry_report_sha256':GEOMETRY_SHA,'product_cache_report_sha256':CACHE_SHA,
            'new_RN64_operations':sum(c['new_RN64_operations'] for c in cases.values()),
            'cached_RN64_operations_NOT_executed':sum(c['cached_RN64_operations_NOT_executed'] for c in cases.values()),
            'source_HOST_RN32_encodings':sum(c['source_HOST_RN32_encodings'] for c in cases.values()),
            'field_cap_scope':'new explicit per-path L1 caps; not inherited phase/fixture/conf1/group/relative budgets',
            'GPU_executed':False,'ALU_executed':False,'native_source_product_implemented':False,
            'execution_authenticated':False,'accepted_full_field_pipeline':False,
            'scene_field_reduced':False,'detector_evaluated':False,'coherent_group_budget_certified':False,
            'native_promotion_allowed':False,'geometry_quotient_unit_or_producer_rerun':False,
            'cost_scope':'source HOST encodings and changed eight-node RN64 product only; cached evidence NOT executed; IO/build/RAM/energy/guard/upstream/group/reduction/detector/full costs excluded'}
