"""Opt-in exact HOST reflection -1 only for the pinned ORIGINAL mirror-zero profile."""
import base64
from copy import deepcopy
from fractions import Fraction as F
import struct
import axial_source_budget_gate_HOST_v1 as retained
import axial_amplitude_allocation_HOST_v1 as allocation
MODEL='axial-original-mirror-zero-exact-sign-HOST-v1'
PREVIOUS='coordinacion/respuestas/AXIAL-SOURCE-BUDGET-GATE-HOST-001-CODEX.json'
PREVIOUS_SHA='4b46ea8d88bde3dd38a1e71e786c79318b92daa1edf81a1b3123874f2c5f19f2'
EVENTS='coordinacion/respuestas/AXIAL-NATIVE-EVENTS-001-CODEX.json'
FLAG='accepted_reflected_source_product_budget_CPU_only'
FALSE=('amplitude_budget_accepted','remaining_stages_error_proved','field_sum_computed','detector_evaluated',
       'execution_authenticated','coherence_authenticated','accepted_full_field_pipeline',
       'native_kernel_implemented','GPU_executed','GPU_job_admission')
SIGN=1<<63

def require(ok,why):
    if not ok:raise ValueError(why)

def pair(v):
    return [v.numerator,v.denominator]

def decode64(w):
    require(type(w) is int and 0<=w<2**64,'finite uint64 word required')
    sign=-1 if w&SIGN else 1;e=(w>>52)&2047;m=w&((1<<52)-1)
    require(e!=2047,'finite uint64 word required')
    if e:m|=1<<52;power=e-1075
    else:power=-1074
    return sign*F(m)*(F(2)**power)

def negate_product_words(words,*,model):
    """Mathematical bit primitive only; not caller-supplied scene or budget evidence."""
    require(model==MODEL,'explicit exact mirror-zero HOST model')
    require(type(words) is list and len(words)==2,'two finite binary64 product words')
    values=[decode64(w) for w in words];out=[w^SIGN for w in words]
    require([decode64(w) for w in out]==[-v for v in values],'exact sign negation invariant')
    return {'input_uint64':list(words),'reflected_uint64':out,
            'input_rational':[pair(v) for v in values],'reflected_rational':[pair(-v) for v in values],
            'additional_rounding_error_L1':[0,1],'HOST_signbit_XORs':2,
            'new_RN64_operations':0,'scope':'bit primitive only; not scene evidence'}

def mirror_zero_profile(snapshot,metadata,event):
    """INPUT/event-bound internal contract; no rounding of original phase."""
    require(metadata['object_ids']==['M','D'] and metadata['kinds']==['mirror','det'],
            'explicit M mirror / D terminal owner profile')
    require(set(snapshot['objects'])=={'M','D'} and not snapshot['undeclared_meshes'],
            'restricted original object coverage')
    m=snapshot['objects']['M'];d=snapshot['objects']['D']
    require(m['kind']=='mirror' and d['kind']=='det','ORIGINAL owner kinds')
    phase=m['phase_rad']
    require(type(phase) is float,'ORIGINAL binary64 phase required')
    w=struct.unpack('<Q',struct.pack('<d',phase))[0]
    require(w in (0,SIGN),'ORIGINAL mirror phase exactly zero; nonzero never rounded/FTZ to zero')
    require(event['accepted_axial_two_event_geometry_CPU_only'] is True and
            event['mirror_owner']==0 and event['terminal_owner']==1 and
            len(event['segments'])==2 and [s['owner'] for s in event['segments']]==[0,1],
            'retained accepted M then D two-event selection')
    departure=event['departure_certificate']
    require(departure['owner']==0 and departure['source_id']==event['source_id'] and
            departure['primitive_id']==event['segments'][0]['primitive_id'] and
            departure['origin']=='derived-from-accepted-first-event-not-caller-previous-id',
            'retained departure certificate')
    return {'mirror_object_id':'M','terminal_object_id':'D','mirror_phase_ORIGINAL_uint64':w,
            'mirror_coefficient_exact_reim':[[-1,1],[0,1]],'coefficient_error_L1':[0,1],
            'profile':'ORIGINAL binary64 +/-0 phase, ideal mirror -exp(i*phase)',
            'coefficient_transport':'HOST original_scene_json INPUT only; no native material buffer implementation'}

def audit_retained_mirror_zero_HOST(case_names,allocations_by_case,*,model):
    require(model==MODEL,'explicit mirror-zero HOST model')
    report=allocation.parse(retained.read(PREVIOUS,PREVIOUS_SHA))
    pins=retained.pins_from(report);pins[PREVIOUS]=PREVIOUS_SHA
    for p,h in pins.items():retained.read(p,h)
    packets,products,_=retained.load_retained()
    budgets=retained.audit_retained_product_budget_HOST(case_names,allocations_by_case,model=retained.MODEL)
    events=retained.payload(allocation.parse(retained.read(EVENTS,pins[EVENTS])))['cases']
    cases={};xors=0;reflections=0
    for name in case_names:
        old=products[name];packet=packets[name];budget=budgets['cases'][name]
        snap=allocation.parse(base64.b64decode(packet['buffers_base64']['original_scene_json'],validate=True))
        meta=allocation.parse(base64.b64decode(packet['buffers_base64']['input_metadata_json'],validate=True))
        rows=[]
        for s,b in zip(old['sources'],budget['sources']):
            row={'source_id':s['source_id'],'phase_reference_id':s['phase_reference_id'],
                 'terminal_reference_id':s['terminal_reference_id'],'retained_product_row_sha256':allocation.digest(s),
                 'retained_budget_row_sha256':allocation.digest(b),
                 'reflection_coefficient_applied_HOST':False,'source_budget_evaluated':b['source_budget_evaluated'],
                 FLAG:False,**dict.fromkeys(FALSE,False)}
            # Numeric STOP has precedence; budget-missing/FAIL cannot promote full acceptance.
            if not s['source_product_evaluated']:
                row.update(status='STOP',reason=s['reason'],reason_provenance='unchanged_retained_numerical_STOP')
            else:
                require(name in events,'retained event receipt required')
                e=events[name]
                for key in ('case_name','input_packet_sha256','scene_binding_sha256','word_ABI_sha256','source_order'):
                    require(e[key]==old[key],'event/product INPUT binding: '+key)
                require([v['source_id'] for v in e['sources']]==old['source_order'],'event source coverage')
                event=e['sources'][old['source_order'].index(s['source_id'])]
                require(event['departure_certificate']['input_packet_sha256']==allocation.digest(packet),'departure INPUT receipt')
                try:profile=mirror_zero_profile(snap,meta,event)
                except ValueError as exc:
                    row.update(status='STOP',reason=str(exc),reason_provenance='ORIGINAL_mirror_profile_STOP')
                else:
                    corners=[]
                    for p in s['encoded_corner_products']:
                        exact=negate_product_words(p['product_uint64'],model=model)
                        corners.append({**exact,'retained_corner_product_sha256':allocation.digest(p),
                            'charges_L1_unchanged':deepcopy(p['charges_L1']),
                            'error_L1_to_ORIGINAL_reflected_source_ideal_unit_bound':
                                 deepcopy(p['error_L1_to_original_source_times_ideal_unit_bound']),
                            'ideal_reference_transform':'negation of ORIGINAL source times ideal propagation unit; L1 isometry'})
                        xors+=2;reflections+=1
                    row.update(reflection_coefficient_applied_HOST=True,mirror_profile=profile,
                        retained_event_row_sha256=allocation.digest(event),reflected_corner_products_HOST=corners,
                        reflected_source_error_L1_to_ORIGINAL_bound=deepcopy(s['product_error_L1_to_ORIGINAL_bound']),
                        coefficient_error_L1=[0,1],additional_rounding_error_L1=[0,1],
                        unchanged_original_phase_cap_rad=deepcopy(s['unchanged_original_phase_cap_rad']),
                        status=b['status'],reason=b['reason'],reason_provenance=b['reason_provenance'],
                        **{FLAG:b[retained.FLAG]})
                    if b['source_budget_evaluated']:row['source_cap_L1']=deepcopy(b['source_cap_L1'])
            rows.append(row)
        cases[name]={'context':deepcopy(budget['context']),'allocation_result':deepcopy(budget['allocation_result']),
                     'sources':rows,FLAG:all(s[FLAG] for s in rows),'reflected_field_sum_computed':False,
                     'profile_scope':'restricted one ORIGINAL zero-phase mirror, not general optics',
                     **dict.fromkeys(FALSE,False)}
    return {'model':MODEL,'units':allocation.UNITS,'case_order':list(case_names),'cases':cases,
            'budget_report_sha256':PREVIOUS_SHA,'inherited_pins_verified':len(pins),
            'HOST_corner_reflections':reflections,'HOST_signbit_XORs':xors,'new_RN64_operations':0,
            'new_products':0,'new_trigonometry_evaluations':0,'geometry_reexecuted':False,
            'coefficient_model_implemented_HOST_only':True,**dict.fromkeys(FALSE,False),
            'scope':'partial retained source products with exact ideal mirror -1; no remaining-stage proof or full-field promotion',
            'cost_scope':'2 HOST sign XOR per retained corner; receipt reads/hash/decompression and INPUT allocation extra; NOT fullcost/native timing'}
