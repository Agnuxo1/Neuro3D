"""Opt-in lineage bridge to a SHA-pinned existing complete restricted CPU tree proof."""
import base64
from copy import deepcopy
from fractions import Fraction as F
import struct
import axial_source_budget_gate_HOST_v1 as retained
import axial_amplitude_allocation_HOST_v1 as allocation
MODEL='axial-retained-tree-to-HOST-events-lineage-v1'
PREVIOUS='coordinacion/respuestas/AXIAL-MIRROR-ZERO-HOST-001-CODEX.json'
PREVIOUS_SHA='5f5b8ce30a02a7b1a558d26ffbe5fd211d9fc9d78f9554456d93512f91d21586'
TREE='coordinacion/respuestas/AXIAL-TREE-COMPLETENESS-001-CODEX.json'
TREE_SHA='d895ef448dee2a4bb8657da1b6bd3f36635b91f4b8137ae29d194664c6db7d9e'
GEOMETRY='coordinacion/respuestas/AXIAL-GEOMETRY-WORDS-001-CODEX.json'
EVENTS='coordinacion/respuestas/AXIAL-NATIVE-EVENTS-001-CODEX.json'
FLAG='tree_lineage_matches_restricted_CPU_only'
FALSE=('accepted_complete_geometry','accepted_full_field_pipeline','amplitude_budget_accepted',
       'remaining_stages_error_proved','field_values_computed','field_sum_computed','detector_evaluated',
       'native_kernel_implemented','GPU_executed','GPU_job_admission','execution_authenticated','coherence_authenticated')
def require(ok,why):
    if not ok:raise ValueError(why)
def signed_words(v):
    require(type(v) is list and len(v)==16 and all(type(w) is int and 0<=w<2**32 for w in v),'signed512 endpoint words')
    n=sum(w<<(32*i) for i,w in enumerate(v))
    return F(n-(1<<512) if v[-1]&(1<<31) else n,1<<149)
def word_bytes(words):
    require(all(type(w) is int and 0<=w<2**32 for w in words),'uint32 serialized words')
    return struct.pack('<'+'I'*len(words),*words)
def geometry_bytes(g):
    a=g['word_ABI'];tw=[]
    for t in a['triangles']:
        tw.append(t['owner'])
        tw.extend(w for v in t['vertices_uint32_hilo'] for pair in v for w in pair)
        tw.extend((t['X_radius_scaled']>>(32*i))&0xffffffff for i in range(16))
    sources=[]
    for s,o in zip(a['sources'],g['scene_snapshot']['sources']):
        words=[w for v in s['origin_uint32_hilo']+s['direction_uint32_hilo'] for w in v]
        words.extend((s['X_radius_scaled']>>(32*i))&0xffffffff for i in range(16))
        sources.append(word_bytes(words)+struct.pack('<dd',*o['field_reim']))
    return word_bytes(tw),b''.join(sources)
def compare_bridge(packet,g,tree,event_case):
    """Internal comparison only. Public API cannot supply certificates/geometry/events."""
    c=allocation.context_from_packet(packet,allocation.digest(packet),model=allocation.MODEL)
    snap=allocation.parse(base64.b64decode(packet['buffers_base64']['original_scene_json'],validate=True))
    require(snap==g['scene_snapshot'] and allocation.digest(snap)==c['original_snapshot_sha256'],'identical ORIGINAL snapshot')
    a=g['word_ABI'];require(allocation.digest(a)==g['word_ABI_sha256']==c['word_ABI_sha256'],'identical geometry ABI')
    require(a['original_scene_binding_sha256']==c['scene_binding_sha256'] and a['source_order']==c['source_order'],'scene/source identity')
    triangles,sources=geometry_bytes(g)
    require(base64.b64decode(packet['buffers_base64']['triangles'],validate=True)==triangles and
            base64.b64decode(packet['buffers_base64']['sources'],validate=True)==sources,'exact geometry/source serialized INPUT bytes')
    for k in ('case_name','input_packet_sha256','scene_binding_sha256','word_ABI_sha256','source_order'):
        require(event_case[k]==c[k],'event exact INPUT identity: '+k)
    require(tree['geometric_tree_complete_restricted_CPU_only'] is True and
            event_case['accepted_axial_two_event_geometry_CPU_only'] is True,'both retained restricted geometry admissions')
    cert=tree['certificate']
    require(allocation.digest(cert)==tree['certificate_sha256'] and cert['geometry_case_sha256']==allocation.digest(g),'tree/geometry receipt')
    require(cert['scene_binding_sha256']==c['scene_binding_sha256'] and cert['word_ABI_sha256']==c['word_ABI_sha256'] and
            cert['source_order']==c['source_order'] and cert['object_order']==['M','D'] and cert['primitive_count']==4,'tree scene ABI order profile')
    require([s['source_id'] for s in event_case['sources']]==c['source_order'] and len(cert['trees'])==len(c['source_order']),'complete source/tree coverage')
    require(tree['record_count']==3*len(c['source_order']) and tree['transition_count']==2*len(c['source_order']),'complete tree counts')
    out=[]
    for sid,nodes,event in zip(c['source_order'],cert['trees'],event_case['sources']):
        require(event['accepted_axial_two_event_geometry_CPU_only'] is True and
                type(event['direction_sign']) is int and event['direction_sign'] in (-1,1),'strict accepted event direction')
        require(len(nodes)==3 and [n['event'] for n in nodes]==['source','reflect','detect'],'three closed events')
        ids=[sid+':root',sid+':mirror',sid+':det']
        require([n['id'] for n in nodes]==ids and all(n['source_id']==sid for n in nodes),'tree source/IDs')
        require([n['parent'] for n in nodes]==[None,ids[0],ids[1]] and
                [n['children'] for n in nodes]==[[ids[1]],[ids[2]],[]] and nodes[2]['direction_sign'] is None,'complete lineage/absorbing terminal')
        require(type(nodes[0]['direction_sign']) is int and type(nodes[1]['direction_sign']) is int and
                nodes[0]['direction_sign']==event['direction_sign']==-nodes[1]['direction_sign'],'same directions')
        require(len(event['segments'])==2 and type(event['mirror_owner']) is int and event['mirror_owner']==0 and
                type(event['terminal_owner']) is int and event['terminal_owner']==1,'M then D event owner profile')
        checks=[]
        for j in (0,1):
            seg=event['segments'][j];partition=nodes[j]['next_primitive_partition']
            require(type(seg['owner']) is int and seg['owner']==j and type(seg['primitive_id']) is int,'strict event owner/primitive types')
            require(len(partition)==4 and [p['primitive_id'] for p in partition]==list(range(4)) and
                    all(type(p['primitive_id']) is int and type(p['owner']) is int and p['owner']==p['primitive_id']//2 for p in partition),'four exact ordered primitive owners')
            selected=[p for p in partition if p['relation']=='chosen']
            require(len(selected)==1 and selected[0]['primitive_id']==seg['primitive_id'] and
                    type(nodes[j+1]['arrival_primitive_id']) is int and nodes[j+1]['arrival_primitive_id']==seg['primitive_id'],'same chosen root')
            lo,hi=map(signed_words,seg['segment_interval_words'])
            require(lo>0 and hi>=lo and [F(*v) for v in selected[0]['distance_BU']]==[lo,hi],'same positive root enclosure')
            misses=[p['primitive_id'] for p in partition if p['relation']=='projected_miss']
            behind=[p['primitive_id'] for p in partition if p['relation']=='behind']
            skip=[p['primitive_id'] for p in partition if p['relation']=='same_owner_departure']
            for values in (event['projected_misses'],seg['behind'],seg['same_owner_departures_skipped']):
                require(type(values) is list and all(type(x) is int and 0<=x<4 for x in values)
                        and values==sorted(set(values)),'strict ordered unique classification primitive IDs')
            require(misses==event['projected_misses'] and behind==seg['behind'] and skip==seg['same_owner_departures_skipped'],'same full primitive classification/departure')
            later=[F(*p['shared_origin_clearance_BU']) for p in partition if p['relation']=='strictly_later']
            clearance=seg['competitor_clearance_words']
            require((clearance is None and not later) or
                    (clearance is not None and later and min(later)>0 and signed_words(clearance)==min(later)),'same strictly positive competitor clearance')
            checks.append({'selected_primitive_id':seg['primitive_id'],'partition_sha256':allocation.digest(partition),
                           'event_segment_sha256':allocation.digest(seg),'root_enclosure_BU':[[lo.numerator,lo.denominator],[hi.numerator,hi.denominator]]})
        departure=event['departure_certificate']
        require(departure['input_packet_sha256']==c['input_packet_sha256'] and departure['source_id']==sid and
                type(departure['owner']) is int and departure['owner']==0 and
                type(departure['primitive_id']) is int and departure['primitive_id']==event['segments'][0]['primitive_id'] and
                departure['origin']=='derived-from-accepted-first-event-not-caller-previous-id','same derived departure binding')
        out.append({'source_id':sid,'tree_nodes_sha256':allocation.digest(nodes),'native_event_row_sha256':allocation.digest(event),
                    'checks':checks,'certificate_sha256':tree['certificate_sha256'],FLAG:True})
    return {'context':c,'sources':out,'certificate_sha256':tree['certificate_sha256'],FLAG:True,
            'reuse_provenance':'previously independently verified CPU tree proof; new lineage/bytes/endpoint checks ONLY'}
def load_retained():
    r=allocation.parse(retained.read(PREVIOUS,PREVIOUS_SHA));pins=retained.pins_from(r);pins[PREVIOUS]=PREVIOUS_SHA
    for p,h in pins.items():retained.read(p,h)
    require(pins[TREE]==TREE_SHA,'tree lineage SHA')
    packets,products,_=retained.load_retained()
    return packets,products,retained.payload(allocation.parse(retained.read(TREE,TREE_SHA)))['cases'],\
           retained.payload(allocation.parse(retained.read(GEOMETRY,pins[GEOMETRY])))['cases'],\
           retained.payload(allocation.parse(retained.read(EVENTS,pins[EVENTS])))['cases'],pins
def audit_tree_lineage_HOST(case_names,*,model):
    require(model==MODEL and type(case_names) is list and 1<=len(case_names)<=64 and
            all(type(n) is str and n for n in case_names) and len(set(case_names))==len(case_names),'explicit model/unique bounded case selection')
    packets,products,trees,geometry,events,pins=load_retained()
    require(set(case_names)<=set(packets),'unknown retained INPUT case')
    out={}
    for n in case_names:
        row={'input_packet_sha256':allocation.digest(packets[n]),FLAG:False,'sources':[],
             'retained_source_product_row_sha256s':[allocation.digest(s) for s in products[n]['sources']],
             'retained_source_product_evaluated':[s['source_product_evaluated'] for s in products[n]['sources']],
             'retained_source_numerical_STOP_reasons':[None if s['source_product_evaluated'] else s['reason'] for s in products[n]['sources']],
             **dict.fromkeys(FALSE,False)}
        if n not in events or n not in geometry or n not in trees:
            row.update(status='STOP',reason='no exact current INPUT event/geometry/tree receipt; no same-snapshot alias borrowing')
        elif not trees[n]['geometric_tree_complete_restricted_CPU_only']:
            require(events[n]['accepted_axial_two_event_geometry_CPU_only'] is False,'retained geometric rejection mismatch')
            row.update(status='STOP',reason=trees[n]['reason'])
        else:
            row.update(compare_bridge(packets[n],geometry[n],trees[n],events[n]),status='MATCH_RETAINED_CPU_TREE')
        out[n]=row
    return {'model':MODEL,'case_order':list(case_names),'cases':out,'inherited_pins_verified':len(pins),
            'tree_report_sha256':TREE_SHA,'previous_report_sha256':PREVIOUS_SHA,'new_ray_traces':0,
            'new_barycentric_evaluations':0,'new_products':0,'new_trigonometry':0,
            'native_event_arithmetic_reexecuted':False,**dict.fromkeys(FALSE,False),
            'scope':'reuse restricted original/shared-X-family CPU tree proof; NOT signed512/native complete-geometry verification or field gate'}
