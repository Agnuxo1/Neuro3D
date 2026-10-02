"""Opt-in partial HOST gate on pinned retained source-product bounds; no numerical replay."""
import base64
from copy import deepcopy
from fractions import Fraction as F
import hashlib
import zlib
from pathlib import Path
import axial_amplitude_allocation_HOST_v1 as allocation

ROOT=Path(__file__).resolve().parents[3]
MODEL='axial-retained-bare-source-product-budget-HOST-v1'
PREVIOUS='coordinacion/respuestas/AXIAL-AMPLITUDE-ALLOCATION-CONTRACT-001-CODEX.json'
PREVIOUS_SHA='f8432ef9d18b27eb1b64d61a87320ecb2a380b4a68b85438f6cde6b590b970f4'
PRODUCT='coordinacion/respuestas/AXIAL-SOURCE-PRODUCT-HOST-001-CODEX.json'
PRODUCT_SHA='04390dac11ab3d7b2a785542bc9b7c94a0f447686b777def0cdeb0a3dceca1b3'
INGRESS='coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json'
PRESENCE='coordinacion/respuestas/AXIAL-NATIVE-PRESENCE-STOPS-001-CODEX.json'
FLAG='accepted_retained_bare_source_product_budget_CPU_only'
FALSE_FLAGS=('amplitude_budget_accepted','remaining_stages_error_proved',
             'reflection_coefficient_applied','field_values_computed','field_sum_computed',
             'detector_evaluated','native_kernel_implemented','GPU_executed','GPU_job_admission',
             'execution_authenticated','coherence_authenticated','accepted_full_field_pipeline')

def require(ok,why):
    if not ok:
        raise ValueError(why)

def read(path,sha):
    raw=(ROOT/path).read_bytes()
    require(hashlib.sha256(raw).hexdigest()==sha,'pinned receipt/code SHA: '+path)
    return raw

def pins_from(r):
    if 'code_doc_sha256' in r:
        return dict(r['code_doc_sha256'])
    d=r['inherited_pin_source']
    p=pins_from(allocation.parse(read(d['path'],d['sha256'])))
    p[d['path']]=d['sha256'];p.update(r['own_code_doc_sha256'])
    return p

def payload(r):
    t=r['test_run']
    require(t['rc']==0,'retained suite not successful')
    b=zlib.decompress(base64.b64decode(t.get('stdout_zlib_base64') or ''.join(t['stdout_zlib_base64_chunks']),validate=True))
    require(len(b)==t['stdout_bytes'] and hashlib.sha256(b).hexdigest()==t['stdout_sha256'],'retained stdout receipt')
    return allocation.parse(b)

def load_retained():
    # Only owned pinned receipts are read. No old writers/tests or numeric production imports.
    r=allocation.parse(read(PREVIOUS,PREVIOUS_SHA));pins=pins_from(r);pins[PREVIOUS]=PREVIOUS_SHA
    for p,h in pins.items():
        read(p,h)
    require(pins[PRODUCT]==PRODUCT_SHA,'product lineage SHA')
    cases=payload(allocation.parse(read(PRODUCT,PRODUCT_SHA)))['cases']
    packets=payload(allocation.parse(read(INGRESS,pins[INGRESS])))['packets']
    controls=payload(allocation.parse(read(PRESENCE,pins[PRESENCE])))['synthetic_controls']
    packets.update({n:v['parent'] for n,v in controls.items()})
    require(set(packets)==set(cases),'retained case coverage')
    return packets,cases,pins

def audit_retained_product_budget_HOST(case_names,allocations_by_case,*,model):
    """Only case selection and static INPUT plans accepted; no external results/contexts/caps."""
    require(model==MODEL,'explicit retained budget HOST model required')
    require(type(case_names) is list and 1<=len(case_names)<=64 and
            all(type(n) is str and n for n in case_names) and len(set(case_names))==len(case_names),
            'bounded ordered unique case selection')
    require(type(allocations_by_case) is dict and set(allocations_by_case)==set(case_names),
            'explicit allocation coverage including None; no missing default')
    packets,old,pins=load_retained()
    require(set(case_names)<=set(packets),'unknown retained case')
    cases={}
    for n in case_names:
        packet=packets[n];prior=old[n];sha=allocation.digest(packet)
        entry=allocation.audit_allocation_HOST(packet,sha,allocations_by_case[n],model=allocation.MODEL)
        ctx=entry['context'];alloc=entry['result']
        for key in ('case_name','input_packet_sha256','scene_binding_sha256','word_ABI_sha256','source_order'):
            require(prior[key]==ctx[key],'retained numerical INPUT identity: '+key)
        require([s['source_id'] for s in prior['sources']]==ctx['source_order'],'retained source coverage/order')
        rows=[]
        for s,a in zip(prior['sources'],ctx['assignments']):
            require(s['phase_reference_id']==a['source_phase_reference_id'] and
                    s['terminal_reference_id']==a['terminal_reference_id'],'retained source/terminal gauge')
            row={'source_id':s['source_id'],'retained_source_row_sha256':allocation.digest(s),
                 'source_product_evaluated':s['source_product_evaluated'],
                 'source_budget_evaluated':False,FLAG:False,
                 'phase_reference_id':s['phase_reference_id'],'terminal_reference_id':s['terminal_reference_id'],
                 **dict.fromkeys(FALSE_FLAGS,False)}
            if not s['source_product_evaluated']:
                row.update(status='STOP',reason=s['reason'],reason_provenance='unchanged_retained_numerical_STOP')
            else:
                b=allocation.rational(s['product_error_L1_to_ORIGINAL_bound'])
                row.update(product_error_L1_to_ORIGINAL_bound=allocation.pair(b),
                           unchanged_original_phase_cap_rad=deepcopy(s['unchanged_original_phase_cap_rad']),
                           upstream_unit_phase_bound_rad=deepcopy(s['upstream_unit_phase_bound_rad']))
                if not alloc['allocation_INPUT_valid']:
                    row.update(status='STOP',reason=alloc['reason'],reason_provenance='missing_static_INPUT_allocation')
                else:
                    cap=allocation.rational(alloc['source_caps_L1'][s['source_id']])
                    ok=b<=cap
                    row.update(source_budget_evaluated=True,source_cap_L1=allocation.pair(cap),
                               status='PASS_PARTIAL' if ok else 'FAIL',
                               reason='retained bare-product bound fits explicit source cap' if ok else
                                      'retained bare-product bound exceeds explicit source cap',
                               reason_provenance='exact_retained_L1_bound_vs_INPUT_cap',
                               **{FLAG:ok})
            rows.append(row)
        groups=[]
        if alloc['allocation_INPUT_valid']:
            for g in alloc['groups']:
                members=[r for r in rows if r['source_id'] in g['source_order']]
                groups.append({**deepcopy(g),FLAG:all(r[FLAG] for r in members),
                               'remaining_stages_error_proved':False,'accepted_full_field_pipeline':False})
        cases[n]={'context':ctx,'allocation_result':alloc,'sources':rows,'groups':groups,
                  FLAG:all(r[FLAG] for r in rows),
                  'numerical_evidence':'retained_no_numerical_reexecution',
                  'product_report_sha256':PRODUCT_SHA,'HOST_only':True,
                  **dict.fromkeys(FALSE_FLAGS,False)}
    return {'model':MODEL,'units':allocation.UNITS,'case_order':deepcopy(case_names),'cases':cases,
            'inherited_pins_verified':len(pins),'allocation_report_sha256':PREVIOUS_SHA,
            'product_report_sha256':PRODUCT_SHA,'new_numeric_products':0,'new_trigonometry_evaluations':0,
            'scope':'retained bare-source-product budgets ONLY; reservations not error proofs; no full field acceptance',
            **dict.fromkeys(FALSE_FLAGS,False)}
