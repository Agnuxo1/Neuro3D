"""Original scene bridge -> charged RN64 argument/unit; no scene/native replay."""
import base64
from copy import deepcopy
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import zlib
from axial_argument_pi_rn64_cpu_v1 import argument_words,MODEL as ARGUMENT,TWO_PI
from axial_unit_rn64_cpu_v1 import component64,rotation64,permute64,MODEL as HORNER
from axial_selector_int256_cpu_v1 import unpack
from axial_relative_gate_cpu_v1 import ratio
from scene_field_producer_cpu_v1 import PI_LOWER,PI_UPPER
ROOT=Path(__file__).resolve().parents[3]
REPORT='coordinacion/respuestas/AXIAL-GEOMETRY-QUOTIENT-001-CODEX.json'
SHA='a16fd247a6aca8dd71796f0ee84bddb5efb7a7c439df7b644066e57c2772ab8b'
ARG_REPORT='coordinacion/respuestas/AXIAL-ARGUMENT-PI-RN64-001-CODEX.json'
ARG_SHA='22c8910ce4927250249a0d13d118b956b4ce6f927ac33ef2afce38582d1afef6'
UNIT_REPORT='coordinacion/respuestas/AXIAL-UNIT-ARGUMENT-RN64-001-CODEX.json'
UNIT_SHA='dbcd557575616af8882c4fbf924c91c42db607e777c8bc43309099f336a32c17'
ARG_CODE='Blender/benchmarks/capacity_audit/axial_argument_pi_rn64_cpu_v1.py'
UNIT_CODE='Blender/benchmarks/capacity_audit/axial_unit_rn64_cpu_v1.py'
MODEL='scene-geometry-bridge-argument-unit-RN64-cache-CPU-v1'
S=1<<149

def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def report(path,sha):
    b=(ROOT/path).read_bytes()
    if hashlib.sha256(b).hexdigest()!=sha:raise ValueError('retained report SHA mismatch '+path)
    r=json.loads(b)
    for n,h in r['code_doc_sha256'].items():
        if hashlib.sha256((ROOT/n).read_bytes()).hexdigest()!=h:raise ValueError('changed frozen input '+n)
    return r
def payload(r):
    run=r['test_run'] if 'test_run' in r else r['run']
    b=zlib.decompress(base64.b64decode(run['stdout_zlib_base64'],validate=True))
    if run['rc']!=0 or len(b)!=run['stdout_bytes'] or hashlib.sha256(b).hexdigest()!=run['stdout_sha256']:raise ValueError('raw payload SHA/status mismatch')
    return json.loads(b)['audit']['cases']
def load_retained():
    r=report(REPORT,SHA);a=report(ARG_REPORT,ARG_SHA);u=report(UNIT_REPORT,UNIT_SHA)
    if r['id']!='AXIAL-GEOMETRY-QUOTIENT-001' or a['argument_model']!=ARGUMENT:raise ValueError('retained identity/model mismatch')
    pins=dict(r['code_doc_sha256'],**{REPORT:SHA})
    if pins[ARG_CODE]!=a['code_doc_sha256'][ARG_CODE] or pins[UNIT_CODE]!=u['code_doc_sha256'][UNIT_CODE]:raise ValueError('cache code contract mismatch')
    ab={};ub={}
    def put(bank,key,m):
        if key in bank and digest(bank[key])!=digest(m):raise ValueError('conflicting deterministic cache')
        bank[key]=deepcopy(m)
    for c in payload(a).values():
        for p in c['paths']:
            if p.get('argument_evaluated'):
                m=p['measurement'];put(ab,tuple(m['residual_signed256_words']),m)
    for c in payload(u).values():
        for p in c['paths']:
            if p.get('unit_evaluated') or p.get('unit_cache_reused'):
                m=p['measurement']
                if p['cache_signature']['model']!=HORNER or p['cache_signature']['unit_code_sha256']!=pins[UNIT_CODE]:raise ValueError('unit cache signature mismatch')
                put(ub,m['angle_uint64'],m)
    return pins,payload(r),ab,ub

def audit_retained_scene_units(*,case_names,unit_model):
    if unit_model!=MODEL:raise ValueError('explicit scene-derived RN64 CPU unit model required')
    if not isinstance(case_names,list) or not case_names or any(type(n) is not str for n in case_names) or len(set(case_names))!=len(case_names):raise ValueError('unique explicit retained case selection required')
    pins,cases,ab,ub=load_retained()
    if any(n not in cases for n in case_names):raise ValueError('unknown retained case')
    result={};counts={'new_argument_RN64':0,'cache_argument_RN64_NOT_executed':0,'new_Horner_RN64':0,'cache_Horner_RN64_NOT_executed':0}
    for name in case_names:
        c=cases[name];rows=[];ids=[p['source_id'] for p in c['paths']]
        if not ids or len(set(ids))!=len(ids):raise ValueError('ordered unique complete source IDs required')
        for p in c['paths']:
            row={'source_id':p['source_id'],'previous_bridge_phase_accepted':p['accepted_bridge_phase_CPU_only'],'argument_evaluated':False,'unit_evaluated':False,'accepted_unit_CPU_only':False};rows.append(row)
            if not p['accepted_bridge_phase_CPU_only']:
                row['reason']='retained bridge rejected; no argument/unit';continue
            ref='original-source-zero:'+c['original_scene_binding_sha256']+':'+p['source_id']
            if p['phase_reference_id']!=ref:raise ValueError('original source gauge mismatch')
            s=p['selector']
            if not s['accepted_CPU_integer_selector_only'] or s['residual_scale_exponent']!=-149:raise ValueError('selector certificate required')
            words=s['residual_cycles_signed256_words'];n=unpack(words);residual=F(n,S)
            if residual!=F(*p['measurement']['modeled_quotient_rational'])-s['integer_turn']-F(s['quarter_index'],4):raise ValueError('new residual/turn/quarter mismatch')
            reused_arg=tuple(words) in ab
            m=deepcopy(ab[tuple(words)]) if reused_arg else argument_words(words,argument_model=ARGUMENT)
            counts['cache_argument_RN64_NOT_executed' if reused_arg else 'new_argument_RN64']+=1
            if m['residual_signed256_words']!=words or m['TWO_PI_uint64']!=TWO_PI:raise ValueError('argument cache input/constant mismatch')
            x=component64(m['argument_uint64']);represented=component64(m['conversion']['output_uint64']);piword=component64(TWO_PI)
            delta=x-represented*piword
            if ratio(delta)!=m['operations'][0]['rounding_delta_rational']:raise ValueError('argument cache node mismatch')
            const=max(abs(piword-2*PI_LOWER),abs(piword-2*PI_UPPER))
            charges={'residual_conversion':abs(piword)*abs(represented-residual),'constant_2pi':abs(residual)*const,'multiply_RN64':abs(delta)}
            angle=sum(charges.values(),F(0));phase=F(*p['composed_phase_bound_rad'])+angle;budget=F(*p['phase_budget_rad'])
            row.update(argument_evaluated=not reused_arg,argument_cache_reused=reused_arg,phase_reference_id=ref,argument_measurement=m,
                       argument_cache_signature={'model':ARGUMENT,'code_sha256':pins[ARG_CODE],'residual_words':words,'source_report_sha256':ARG_SHA if reused_arg else None},
                       new_argument_error_charges_rad={k:ratio(v) for k,v in charges.items()},new_argument_error_bound_rad=ratio(angle),
                       bridge_phase_bound_rad=p['composed_phase_bound_rad'],composed_argument_phase_bound_rad=ratio(phase),phase_budget_rad=p['phase_budget_rad'],
                       accepted_argument_CPU_only=phase<=budget,original_cycles_rational=p['original_cycles_rational'],quarter_index=s['quarter_index'],integer_turn=s['integer_turn'])
            if phase>budget:row['reason']='new argument charge exceeds unchanged original budget';continue
            w=m['argument_uint64'];reused_unit=w in ub
            um=deepcopy(ub[w]) if reused_unit else rotation64(w,rotation_model=HORNER)
            counts['cache_Horner_RN64_NOT_executed' if reused_unit else 'new_Horner_RN64']+=26
            if um['angle_uint64']!=w or um['RN64_operations']!=26:raise ValueError('unit cache input/model mismatch')
            pure=sum((F(*t['polynomial_error_upper_rational'])+F(*t['Taylor_remainder_upper_rational']) for t in um['terms'].values()),F(0))
            if pure!=F(*um['unit_error_L1_upper_rational']):raise ValueError('unit pure node error composition mismatch')
            total=2*phase+pure;k=s['quarter_index'];out=permute64([um['terms'][t]['output_uint64'] for t in ('cos','sin')],k)
            row.update(unit_evaluated=not reused_unit,unit_cache_reused=reused_unit,unit_measurement=um,
                       unit_cache_signature={'model':HORNER,'code_sha256':pins[UNIT_CODE],'angle_uint64':w,'source_report_sha256':UNIT_SHA if reused_unit else None},
                       pure_unit_error_L1_upper=ratio(pure),composed_unit_error_L1_upper=ratio(total),derived_unit_L1_budget=ratio(2*budget),
                       unit_uint64=out,observed_unit_rational=[ratio(component64(v)) for v in out],accepted_unit_CPU_only=total<=2*budget)
        result[name]={'geometry_bridge_case_sha256':digest(c),'original_scene_binding_sha256':c['original_scene_binding_sha256'],
                      'previous_bridge_phase_accepted':c['accepted_bridge_phase_CPU_only'],'paths':rows,'accepted_unit_CPU_only':all(r['accepted_unit_CPU_only'] for r in rows)}
    return {'unit_model':MODEL,'cases':result,'counts':counts,'pins_verified':pins,'retained_report_sha256':SHA,
            'argument_cache_report_sha256':ARG_SHA,'unit_cache_report_sha256':UNIT_SHA,
            'GPU_executed':False,'ALU_executed':False,'native_geometry_implemented':False,'native_argument_unit_implemented':False,
            'execution_authenticated':False,'accepted_full_field_pipeline':False,'field_values_computed':False,'native_promotion_allowed':False,
            'geometry_quotient_selector_or_producer_rerun':False,'scope':'CPU RN64 nodes/cache; new original-source phase charges. No native/ALU/Bpy/RT/physical optics or full costs.'}
