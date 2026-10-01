"""Compose new argument with cached same-word RN64 unit or changed input only."""
import base64
from copy import deepcopy
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import zlib
from axial_unit_rn64_cpu_v1 import MODEL as HORNER_MODEL,component64,rotation64,permute64
from axial_relative_gate_cpu_v1 import ratio,bound

ROOT=Path(__file__).resolve().parents[3]
REPORT='coordinacion/respuestas/AXIAL-ARGUMENT-PI-RN64-001-CODEX.json'
SHA='22c8910ce4927250249a0d13d118b956b4ce6f927ac33ef2afce38582d1afef6'
UNIT_REPORT='coordinacion/respuestas/AXIAL-UNIT-RN64-001-CODEX.json'
UNIT_SHA='e920ad271b1d00ada8c9d85a496556d5ac78644bc146a885a0ee4962a75e4609'
MODEL='axial-new-argument-unit-RN64-cached-word-CPU-v1'
UNIT_CODE='Blender/benchmarks/capacity_audit/axial_unit_rn64_cpu_v1.py'


def payload(r):
    s=r['run'];raw=zlib.decompress(base64.b64decode(s['stdout_zlib_base64'],validate=True))
    if len(raw)!=s['stdout_bytes'] or hashlib.sha256(raw).hexdigest()!=s['stdout_sha256']:raise ValueError('retained exact payload SHA mismatch')
    return json.loads(raw)


def load_retained():
    raw=(ROOT/REPORT).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SHA:raise ValueError('retained new argument SHA mismatch')
    r=json.loads(raw)
    if r['id']!='AXIAL-ARGUMENT-PI-RN64-001-CODEX' or r['run']['rc']!=0:raise ValueError('retained identity/status mismatch')
    for n,h in r['code_doc_sha256'].items():
        if hashlib.sha256((ROOT/n).read_bytes()).hexdigest()!=h:raise ValueError('changed frozen input '+n)
    raw=(ROOT/UNIT_REPORT).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=UNIT_SHA:raise ValueError('cached unit report SHA mismatch')
    u=json.loads(raw)
    if u['run']['rc']!=0 or u['rotation_model']!=HORNER_MODEL or u['code_doc_sha256'][UNIT_CODE]!=r['code_doc_sha256'][UNIT_CODE]:raise ValueError('cached unit contract/code mismatch')
    return r,payload(r)['audit']['cases'],payload(u)['audit']['cases']


def _case(arg,old,unit_code_sha):
    if any(arg[k]!=old[k] for k in ('original_scene_binding_sha256','decoded_scene_binding_sha256')):raise ValueError('retained scene binding mismatch')
    ids=[p['source_id'] for p in arg['paths']]
    if not ids or len(set(ids))!=len(ids) or ids!=[p['source_id'] for p in old['paths']]:raise ValueError('ordered unique complete source coverage required')
    rows=[];new=cache=0
    for p,op in zip(arg['paths'],old['paths']):
        row={'source_id':p['source_id'],'phase_reference_id':p['phase_reference_id'],
             'previous_argument_accepted':p['accepted_argument_CPU_only'],
             'previous_RN64_unit_accepted':op['accepted_propagation_unit_CPU_only'],
             'previous_RN32_unit_accepted':p['previous_RN32_unit_accepted'],
             'accepted_unit_CPU_only':False,'unit_evaluated':False,'unit_cache_reused':False};rows.append(row)
        if not p['accepted_argument_CPU_only']:continue
        if p['phase_reference_id']!=op['phase_reference_id'] or p['phase_reference_id']!='original-source-zero:'+arg['original_scene_binding_sha256']+':'+p['source_id']:raise ValueError('original source gauge required')
        budget=bound(p['phase_budget_rad']);phase=bound(p['composed_phase_bound_rad'])
        if p['phase_budget_rad']!=op['phase_budget_rad'] or p['quarter_index']!=op['quarter_CPU_index']:raise ValueError('unchanged budget/quarter required')
        w=p['measurement']['argument_uint64'];x=component64(w)
        if ratio(x)!=p['measurement']['observed_argument_rad_rational']:raise ValueError('new argument bits/decode mismatch')
        reused=w==op['measurement']['angle_uint64']
        if reused:m=deepcopy(op['measurement']);cache+=26
        else:m=rotation64(w,rotation_model=HORNER_MODEL);new+=26
        if m['angle_uint64']!=w or m['RN64_operations']!=26:raise ValueError('Horner word/model node contract mismatch')
        k=p['quarter_index'];words=permute64([m['terms'][n]['output_uint64'] for n in ('cos','sin')],k)
        total=2*phase+bound(m['unit_error_L1_upper_rational'])
        row.update(unit_evaluated=not reused,unit_cache_reused=reused,measurement=m,
                   cache_signature={'model':HORNER_MODEL,'unit_code_sha256':unit_code_sha,'angle_uint64':w,
                                    'report_sha256':UNIT_SHA if reused else None},
                   quarter_index=k,unit_uint64=words,observed_unit_rational=[ratio(component64(v)) for v in words],
                   phase_budget_rad=p['phase_budget_rad'],new_argument_phase_bound_rad=p['composed_phase_bound_rad'],
                   derived_unit_L1_budget_rational=ratio(2*budget),composed_unit_error_L1_upper_rational=ratio(total),
                   accepted_unit_CPU_only=total<=2*budget)
    return {'original_scene_binding_sha256':arg['original_scene_binding_sha256'],'decoded_scene_binding_sha256':arg['decoded_scene_binding_sha256'],
            'previous_full_case_accepted':arg['previous_full_case_accepted'],'previous_argument_accepted':arg['accepted_argument_CPU_only'],
            'previous_RN64_unit_accepted':old['accepted_propagation_unit_CPU_only'],
            'accepted_unit_CPU_only':all(r['accepted_unit_CPU_only'] for r in rows),'paths':rows,
            'accepted_full_field_pipeline':False,'field_values_computed':False,'new_RN64_operations':new,'cached_RN64_operations':cache}


def audit_retained_new_argument_units(*,case_names,unit_model):
    if unit_model!=MODEL:raise ValueError('explicit new-argument RN64 unit CPU contract required')
    if not isinstance(case_names,list) or not case_names or any(type(n) is not str for n in case_names) or len(set(case_names))!=len(case_names):raise ValueError('explicit unique retained case selection required')
    r,arg,old=load_retained()
    if any(n not in arg for n in case_names):raise ValueError('unknown retained case')
    cases={n:_case(arg[n],old[n],r['code_doc_sha256'][UNIT_CODE]) for n in case_names}
    return {'unit_model':MODEL,'cases':cases,'pins_verified':r['code_doc_sha256'],'retained_report_sha256':SHA,
            'new_RN64_operations':sum(c['new_RN64_operations'] for c in cases.values()),'cached_RN64_operations':sum(c['cached_RN64_operations'] for c in cases.values()),
            'GPU_executed':False,'ALU_executed':False,'accepted_full_field_pipeline':False,'field_values_computed':False,
            'native_selector_implemented':False,'native_argument_product_implemented':False,
            'old_selector_argument_quotient_scene_or_producer_rerun':False,
            'cost_scope':'new Horner nodes only for changed uint64 angle; same-word SHA cache not executed; upstream/decode/IO/RAM/energy/guard/full costs excluded'}
