"""Restricted-domain ideal mirror -1 applied to a fixed-source error proof; HOST only."""
import base64
from copy import deepcopy
import struct
import axial_zero_source_domain_HOST_v1 as source
import axial_source_budget_gate_HOST_v1 as io
import axial_amplitude_allocation_HOST_v1 as allocation
MODEL='axial-ideal-mirror-zero-fixed-source-domain-HOST-v1'
PREVIOUS='coordinacion/respuestas/AXIAL-ZERO-SOURCE-DOMAIN-HOST-001-CODEX.json'
PREVIOUS_SHA='c5acabf3e19284bf44a33bb69b80b6945768ecd607aa3fd97dcac4eaacdee0dc'
MIRROR='coordinacion/respuestas/AXIAL-MIRROR-ZERO-HOST-001-CODEX.json'
EVENTS='coordinacion/respuestas/AXIAL-NATIVE-EVENTS-001-CODEX.json'
ZERO='coordinacion/respuestas/AXIAL-ZERO-SINGLETON-UNIT-HOST-001-CODEX.json'
DOMAIN='coordinacion/respuestas/AXIAL-SCENE-PARAMETER-DOMAIN-HOST-001-CODEX.json'
FALSE=source.FALSE+('native_material_transport_implemented','physical_mirror_model_validated',
                    'mirror_phase_uncertainty_enclosed','reflection_coefficient_executed_new')
SIGN=1<<63
require=io.require
number=source.number
pair=source.pair
decode=source.decode64
digest=allocation.digest

def load_retained():
    report=allocation.parse(io.read(PREVIOUS,PREVIOUS_SHA))
    require(report['task_id']=='AXIAL-ZERO-SOURCE-DOMAIN-HOST-001','fixed-source predecessor identity')
    pins=io.pins_from(report);pins[PREVIOUS]=PREVIOUS_SHA
    for p,h in pins.items():io.read(p,h)
    old=io.payload(report)['data']['audit']
    mirror=io.payload(allocation.parse(io.read(MIRROR,pins[MIRROR])))['data']['missing']['cases']
    events=io.payload(allocation.parse(io.read(EVENTS,pins[EVENTS])))['cases']
    zero=io.payload(allocation.parse(io.read(ZERO,pins[ZERO])))['data']['audit']
    domains=io.payload(allocation.parse(io.read(DOMAIN,pins[DOMAIN])))['data']['audit']
    packets=io.payload(allocation.parse(io.read(io.INGRESS,pins[io.INGRESS])))['packets']
    controls=io.payload(allocation.parse(io.read(io.PRESENCE,pins[io.PRESENCE])))['synthetic_controls']
    packets.update({n:v['parent'] for n,v in controls.items()})
    require(set(packets)==set(old['cases'])==set(mirror)==set(zero['cases'])==set(domains['cases']),
            'complete predecessor coverage')
    return packets,old,mirror,events,zero,domains,pins

def fixed_ideal_profile(snapshot,metadata,event,domain):
    require(metadata['object_ids']==['M','D'] and metadata['kinds']==['mirror','det'],'M mirror then D detector profile')
    require(set(snapshot['objects'])=={'M','D'} and not snapshot['undeclared_meshes'],'complete declared objects')
    m=snapshot['objects']['M'];require(m['kind']=='mirror' and snapshot['objects']['D']['kind']=='det','ORIGINAL kinds')
    phase=m['phase_rad'];require(type(phase) is float,'ORIGINAL binary64 mirror phase')
    word=struct.unpack('<Q',struct.pack('<d',phase))[0]
    require(word in (0,SIGN),'fixed ORIGINAL +/-0 phase only; no rounding-to-zero or FTZ')
    require(domain['restricted_coordinate_box_to_parameter_rectangle_proved'] is True,'uniform axial domain proof required')
    dp=domain['restricted_domain_proof'];s=dp['uniform_affine_selector_proof']
    require(dp['ORIGINAL_inside_coordinate_box'] is True and dp['all_shared_plane_X_within_box_selector_proved'] is True
            and s['restricted_shared_plane_selector_proved'] is True
            and s['strict_positive_first_and_reflected_second'] is True
            and s['mirror_first_uniform_clearance'] is True
            and s['skip_previous_owner_permitted_only_after_first_root'] is True,'entire restricted M then D selector required')
    require(event['accepted_axial_two_event_geometry_CPU_only'] is True
            and type(event['mirror_owner']) is int and event['mirror_owner']==0
            and type(event['terminal_owner']) is int and event['terminal_owner']==1
            and len(event['segments'])==2 and [v['owner'] for v in event['segments']]==[0,1],'retained M then D events')
    interior=[v for v in dp['fixed_YZ_projection_checks'] if v['classification']=='strict_interior']
    require(all(type(v['owner']) is int and type(v['primitive_id']) is int for v in interior)
            and all(type(v['owner']) is int and type(v['primitive_id']) is int for v in event['segments']),
            'strict integer owner/primitive identities')
    require(len(interior)==2 and [v['owner'] for v in interior]==[0,1]
            and [v['primitive_id'] for v in interior]==[v['primitive_id'] for v in event['segments']],
            'same strict projected primitives across restricted domain/events')
    departure=event['departure_certificate']
    require(departure['owner']==0 and departure['source_id']==event['source_id']
            and departure['primitive_id']==event['segments'][0]['primitive_id']
            and departure['origin']=='derived-from-accepted-first-event-not-caller-previous-id',
            'departure linked to accepted first root, not caller previous owner')
    return {'mirror_object_id':'M','terminal_object_id':'D','fixed_ORIGINAL_mirror_phase_uint64':word,
            'ideal_coefficient_exact_reim':[[-1,1],[0,1]],'coefficient_error_L1':[0,1],
            'coefficient_contract':'fixed ORIGINAL ideal -exp(i*phase), phase +/-0; not Fresnel/polarization/physical validation',
            'restricted_entire_domain_event_chain_proved':True,
            'retained_event_row_sha256':digest(event),'retained_scene_domain_row_sha256':digest(domain),
            'native_material_transport_implemented':False,'mirror_phase_uncertainty_enclosed':False}

def reflected_identity(corner,bare_graph):
    words=corner['input_uint64'];out=corner['reflected_uint64']
    require(type(words) is list and len(words)==2 and type(out) is list and len(out)==2,'two complex words')
    before=list(map(decode,words));after=list(map(decode,out))
    require(words==bare_graph['retained_product_uint64'],'same pinned bare-source graph output')
    require(out==[v^SIGN for v in words] and after==[-v for v in before],'exact retained sign XOR/isometry')
    require(allocation.canon(corner['input_rational'])==allocation.canon(list(map(pair,before)))
            and allocation.canon(corner['reflected_rational'])==allocation.canon(list(map(pair,after))),'retained rational sign identity')
    require(corner['retained_corner_product_sha256']==bare_graph['retained_product_sha256'],'same product receipt')
    require(corner['charges_L1_unchanged']==bare_graph['charges_L1'],'all source charges unchanged')
    require(number(corner['additional_rounding_error_L1'])==0 and type(corner['new_RN64_operations']) is int
            and corner['new_RN64_operations']==0 and type(corner['HOST_signbit_XORs']) is int
            and corner['HOST_signbit_XORs']==2,'retained exact sign operation counts')
    error=number(bare_graph['bare_product_error_to_ORIGINAL_L1'])
    original=list(map(number,bare_graph['fixed_original_source_rational']))
    actual=sum(abs(v+o) for v,o in zip(after,original))
    require(actual==error and number(corner['error_L1_to_ORIGINAL_reflected_source_ideal_unit_bound'])==error,
            'negated ORIGINAL reference is L1 isometry; nonzero error preserved')
    return {'retained_reflection_corner_sha256':digest(corner),'retained_product_sha256':bare_graph['retained_product_sha256'],
            'reflected_uint64':deepcopy(out),'reflected_rational':list(map(pair,after)),
            'negated_fixed_ORIGINAL_source_rational':list(map(lambda v:pair(-v),original)),
            'uniform_reflected_source_error_L1':pair(error),'retained_sign_XOR_identities_checked':2,
            'additional_rounding_error_L1':[0,1],'new_RN_or_producer_executions':0}

def reflected_domain_proof(packet,ctx,index,src,mirror,event,zero,domain):
    require(src['restricted_fixed_source_bare_product_error_to_ORIGINAL_proved'] is True,'restricted bare-source domain proof')
    p=src['proof']
    require(p['retained_zero_unit_row_sha256']==digest(zero)
            and zero['proof']['retained_scene_domain_source_sha256']==digest(domain),'complete source->zero unit->scene domain chain')
    source.fixed_source_words(packet,ctx,index) # Fresh INPUT bits/context only, not old numeric producer.
    meta=allocation.parse(base64.b64decode(packet['buffers_base64']['input_metadata_json'],validate=True))
    snap=allocation.parse(base64.b64decode(packet['buffers_base64']['original_scene_json'],validate=True))
    sid=ctx['source_order'][index];assignment=ctx['assignments'][index]
    require(src['source_id']==mirror['source_id']==event['source_id']==domain['source_id']==sid,'complete ordered source/gauge chain')
    require(mirror['phase_reference_id']==assignment['source_phase_reference_id']
            and mirror['terminal_reference_id']==assignment['terminal_reference_id'],'ORIGINAL source/terminal gauge')
    require(event['departure_certificate']['input_packet_sha256']==digest(packet),'same departure INPUT')
    profile=fixed_ideal_profile(snap,meta,event,domain)
    require(mirror['reflection_coefficient_applied_HOST'] is True and mirror['retained_event_row_sha256']==digest(event),
            'retained reflection/event identity')
    require(mirror['retained_product_row_sha256']==p['retained_source_product_row_sha256'],'same SOURCE product row')
    mp=mirror['mirror_profile']
    require(mp['mirror_phase_ORIGINAL_uint64']==profile['fixed_ORIGINAL_mirror_phase_uint64']
            and mp['mirror_coefficient_exact_reim']==profile['ideal_coefficient_exact_reim'],'same fixed material coefficient')
    require(number(mirror['coefficient_error_L1'])==number(mirror['additional_rounding_error_L1'])==0,'unchanged exact mirror charges')
    corners=mirror['reflected_corner_products_HOST'];require(len(corners)==len(p['graph_checks'])==4,'all four retained reflected products')
    identities=[reflected_identity(c,g) for c,g in zip(corners,p['graph_checks'])]
    error=number(p['uniform_bare_product_L1_error_to_fixed_ORIGINAL_bound'])
    require(number(mirror['reflected_source_error_L1_to_ORIGINAL_bound'])==error,'same old reflected error bound')
    return {'model':MODEL,'restricted_ideal_reflected_fixed_source_error_to_ORIGINAL_proved':True,
            'scope':'one fixed ideal -1 mirror, fixed ORIGINAL amplitude, restricted axial zero-unit domain only',
            'retained_fixed_source_domain_row_sha256':digest(src),'retained_mirror_source_row_sha256':digest(mirror),
            'profile':profile,'retained_corner_identities':identities,
            'uniform_ideal_reflected_source_L1_error_to_fixed_ORIGINAL_bound':pair(error),
            'additional_coefficient_error_L1':[0,1],'additional_reflection_rounding_error_L1':[0,1],
            'nonzero_encoding_error_preserved':error>0,'missing_source_allocation_NOT_promoted':mirror['source_budget_evaluated'] is False,
            'retained_mirror_source_status':mirror['status'],'retained_mirror_source_reason':mirror['reason'],
            'new_RN_or_scene_producer_executions':0,**dict.fromkeys(FALSE,False)}

def audit_reflected_source_domain_HOST(case_names,*,model):
    require(model==MODEL,'explicit ideal reflected-source domain model')
    require(type(case_names) is list and 1<=len(case_names)<=64 and all(type(n) is str and n for n in case_names)
            and len(set(case_names))==len(case_names),'bounded unique case selection')
    packets,old,mirrors,events,zero,domains,pins=load_retained();require(set(case_names)<=set(packets),'known cases')
    cases={};count=stops=nonzero=0
    for n in case_names:
        ctx=allocation.context_from_packet(packets[n],digest(packets[n]),model=allocation.MODEL)
        require(ctx==old['cases'][n]['context']==mirrors[n]['context']==zero['cases'][n]['context']==domains['cases'][n]['context'],
                'same complete fresh INPUT context across domains')
        sets=[old['cases'][n]['sources'],mirrors[n]['sources'],zero['cases'][n]['sources'],domains['cases'][n]['sources']]
        require(all([v['source_id'] for v in ss]==ctx['source_order'] for ss in sets),'complete source coverage/order')
        rows=[]
        for i,(s,m,z,d) in enumerate(zip(*sets)):
            row={'source_id':s['source_id'],'retained_fixed_source_domain_row_sha256':digest(s),
                 'restricted_ideal_reflected_fixed_source_error_to_ORIGINAL_proved':False,
                 'retained_unit_polynomial_charge_fits':s['retained_unit_polynomial_charge_fits'],**dict.fromkeys(FALSE,False)}
            if not s['restricted_fixed_source_bare_product_error_to_ORIGINAL_proved']:
                if s['reason_provenance']=='unchanged_retained_unit_STOP':stops+=1
                else:nonzero+=1
                row.update(status='STOP',reason=s['reason'],reason_provenance=s['reason_provenance'])
            else:
                e=events[n]
                for k in ('case_name','input_packet_sha256','scene_binding_sha256','word_ABI_sha256','source_order'):
                    require(e[k]==ctx[k],'same retained event INPUT: '+k)
                require([v['source_id'] for v in e['sources']]==ctx['source_order'],'ordered retained event coverage')
                proof=reflected_domain_proof(packets[n],ctx,i,s,m,e['sources'][i],z,d);count+=1
                row.update(restricted_ideal_reflected_fixed_source_error_to_ORIGINAL_proved=True,proof=proof,status='STOP',
                           reason=m['reason'],reason_provenance=m['reason_provenance'])
            rows.append(row)
        cases[n]={'context':ctx,'sources':rows,**dict.fromkeys(FALSE,False)}
    return {'model':MODEL,'case_order':deepcopy(case_names),'cases':cases,'inherited_pins_verified':len(pins),
            'restricted_ideal_reflected_source_domains_proved':count,'retained_unit_STOPs':stops,'nonzero_domains_not_refined':nonzero,
            'new_RN_or_scene_producer_executions':0,**dict.fromkeys(FALSE,False)}
