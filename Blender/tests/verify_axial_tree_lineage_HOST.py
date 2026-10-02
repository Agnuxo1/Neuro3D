"""Independent receipt/budget oracle, stdlib only, no production imports or numeric replay."""
import base64,hashlib,json,math,sys,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REPORT='coordinacion/respuestas/AXIAL-TREE-LINEAGE-HOST-001-CODEX.json'
PREVIOUS='coordinacion/respuestas/AXIAL-AMPLITUDE-ALLOCATION-CONTRACT-001-CODEX.json'
PREVIOUS_SHA='f8432ef9d18b27eb1b64d61a87320ecb2a380b4a68b85438f6cde6b590b970f4'
PRODUCT='coordinacion/respuestas/AXIAL-SOURCE-PRODUCT-HOST-001-CODEX.json'
PRODUCT_SHA='04390dac11ab3d7b2a785542bc9b7c94a0f447686b777def0cdeb0a3dceca1b3'
MODEL='axial-retained-bare-source-product-budget-HOST-v1'
AMODEL='axial-static-amplitude-L1-allocation-HOST-v1'
UNITS='ORIGINAL-source-field-amplitude-L1'
FLAG='accepted_retained_bare_source_product_budget_CPU_only'
FALSE=('amplitude_budget_accepted','remaining_stages_error_proved','reflection_coefficient_applied',
       'field_values_computed','field_sum_computed','detector_evaluated','native_kernel_implemented',
       'GPU_executed','GPU_job_admission','execution_authenticated','coherence_authenticated','accepted_full_field_pipeline')
def canon(v):
    return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def sha(v):
    return hashlib.sha256(v).hexdigest()
def digest(v):
    return sha(canon(v))
def read(p,h):
    b=(ROOT/p).read_bytes();assert sha(b)==h,p;return json.loads(b)
def payload(r):
    t=r['test_run'];assert t['rc']==0
    b=zlib.decompress(base64.b64decode(t.get('stdout_zlib_base64') or ''.join(t['stdout_zlib_base64_chunks']),validate=True))
    assert len(b)==t['stdout_bytes'] and sha(b)==t['stdout_sha256']
    return json.loads(b)
def pins_from(r):
    if 'code_doc_sha256' in r:
        return dict(r['code_doc_sha256'])
    d=r['inherited_pin_source'];p=pins_from(read(d['path'],d['sha256']))
    p[d['path']]=d['sha256'];p.update(r['own_code_doc_sha256']);return p
def rat(v):
    assert type(v) is list and len(v)==2 and all(type(n) is int for n in v)
    assert v[0]>=0 and v[1]>0 and math.gcd(*v)==1
    return F(*v)
def pair(v):
    return [v.numerator,v.denominator]
def context(packet):
    roles={'triangles','sources','wavelength','reference','original_scene_json','input_metadata_json'}
    assert set(packet['buffers_base64'])==set(packet['manifest']['buffers'])==roles
    b={k:base64.b64decode(v,validate=True) for k,v in packet['buffers_base64'].items()}
    for k,v in b.items():
        assert packet['manifest']['buffers'][k]=={'bytes':len(v),'sha256':sha(v)}
    m=json.loads(b['input_metadata_json']);snap=json.loads(b['original_scene_json']);g=m['explicit_group_contract']
    assert m['original_snapshot_sha256']==sha(b['original_scene_json'])
    assert m['source_order']==[s['id'] for s in snap['sources']]
    assert m['case_name']==packet['manifest']['case_name']
    assert g['scene_binding_sha256']==m['scene_binding_sha256']
    assert [a['source_id'] for a in g['assignments']]==m['source_order']
    groups=[]
    for a in g['assignments']:
        assert a['source_phase_reference_id']=='original-source-zero:'+m['scene_binding_sha256']+':'+a['source_id']
        key=[a['port'],a['coherence_group']]
        if key not in groups:
            groups.append(key)
    cap=rat(g['limits']['field_L1'])
    return {'model':AMODEL,'units':UNITS,'case_name':m['case_name'],'input_packet_sha256':digest(packet),
            'scene_binding_sha256':m['scene_binding_sha256'],'word_ABI_sha256':m['word_ABI_sha256'],
            'original_snapshot_sha256':m['original_snapshot_sha256'],'original_group_contract_sha256':digest(g),
            'source_order':m['source_order'],'assignments':g['assignments'],'groups':groups,
            'unchanged_field_L1_cap':pair(cap),'unchanged_limits':g['limits'],
            'grouping_provenance':g['grouping_provenance'],'execution_authenticated':False,'coherence_authenticated':False}
import struct
BASE='coordinacion/respuestas/AXIAL-MIRROR-ZERO-HOST-001-CODEX.json'
BASE_SHA='5f5b8ce30a02a7b1a558d26ffbe5fd211d9fc9d78f9554456d93512f91d21586'
TREE='coordinacion/respuestas/AXIAL-TREE-COMPLETENESS-001-CODEX.json'
TREE_SHA='d895ef448dee2a4bb8657da1b6bd3f36635b91f4b8137ae29d194664c6db7d9e'
GEO='coordinacion/respuestas/AXIAL-GEOMETRY-WORDS-001-CODEX.json'
EVENT='coordinacion/respuestas/AXIAL-NATIVE-EVENTS-001-CODEX.json'
BMODEL='axial-retained-tree-to-HOST-events-lineage-v1'
BFLAG='tree_lineage_matches_restricted_CPU_only'
BFALSE=('accepted_complete_geometry','accepted_full_field_pipeline','amplitude_budget_accepted',
       'remaining_stages_error_proved','field_values_computed','field_sum_computed','detector_evaluated',
       'native_kernel_implemented','GPU_executed','GPU_job_admission','execution_authenticated','coherence_authenticated')
def endpoint(words):
    assert type(words) is list and len(words)==16 and all(type(w) is int and 0<=w<2**32 for w in words)
    raw=b''.join(w.to_bytes(4,'little') for w in words)
    return F(int.from_bytes(raw,'little',signed=True),2**149)
def pack_words(words):
    assert all(type(w) is int and 0<=w<2**32 for w in words)
    return b''.join(w.to_bytes(4,'little') for w in words)
def validate(packet,g,t,e):
    c=context(packet)
    s=json.loads(base64.b64decode(packet['buffers_base64']['original_scene_json'],validate=True))
    assert s==g['scene_snapshot'] and digest(s)==c['original_snapshot_sha256']
    a=g['word_ABI'];assert digest(a)==g['word_ABI_sha256']==c['word_ABI_sha256']
    assert a['original_scene_binding_sha256']==c['scene_binding_sha256'] and a['source_order']==c['source_order']
    triangle_bytes=b''
    for tri in a['triangles']:
        w=[tri['owner']]+[w for v in tri['vertices_uint32_hilo'] for p in v for w in p]
        assert type(tri['X_radius_scaled']) is int
        triangle_bytes+=pack_words(w)+tri['X_radius_scaled'].to_bytes(64,'little')
    source_bytes=b''
    for enc,original in zip(a['sources'],s['sources']):
        w=[w for p in enc['origin_uint32_hilo']+enc['direction_uint32_hilo'] for w in p]
        assert type(enc['X_radius_scaled']) is int
        source_bytes+=pack_words(w)+enc['X_radius_scaled'].to_bytes(64,'little')+struct.pack('<dd',*original['field_reim'])
    assert triangle_bytes==base64.b64decode(packet['buffers_base64']['triangles'],validate=True)
    assert source_bytes==base64.b64decode(packet['buffers_base64']['sources'],validate=True)
    for k in ('case_name','input_packet_sha256','scene_binding_sha256','word_ABI_sha256','source_order'):assert e[k]==c[k]
    assert e['accepted_axial_two_event_geometry_CPU_only'] is t['geometric_tree_complete_restricted_CPU_only'] is True
    cert=t['certificate'];assert digest(cert)==t['certificate_sha256']
    assert cert['geometry_case_sha256']==digest(g)
    assert cert['scene_binding_sha256']==c['scene_binding_sha256'] and cert['word_ABI_sha256']==c['word_ABI_sha256']
    assert cert['source_order']==c['source_order'] and cert['object_order']==['M','D'] and cert['primitive_count']==4
    assert [v['source_id'] for v in e['sources']]==c['source_order'] and len(cert['trees'])==len(c['source_order'])
    assert t['record_count']==3*len(c['source_order']) and t['transition_count']==2*len(c['source_order'])
    rows=[]
    for sid,nodes,event in zip(c['source_order'],cert['trees'],e['sources']):
        assert event['accepted_axial_two_event_geometry_CPU_only'] is True
        assert type(event['direction_sign']) is int and event['direction_sign'] in (-1,1)
        assert len(nodes)==3 and [n['event'] for n in nodes]==['source','reflect','detect']
        ids=[sid+':root',sid+':mirror',sid+':det']
        assert [n['id'] for n in nodes]==ids and all(n['source_id']==sid for n in nodes)
        assert [n['parent'] for n in nodes]==[None,ids[0],ids[1]]
        assert [n['children'] for n in nodes]==[[ids[1]],[ids[2]],[]] and nodes[2]['direction_sign'] is None
        assert all(type(nodes[j]['direction_sign']) is int for j in (0,1))
        assert nodes[0]['direction_sign']==event['direction_sign']==-nodes[1]['direction_sign']
        assert len(event['segments'])==2 and type(event['mirror_owner']) is int and event['mirror_owner']==0
        assert type(event['terminal_owner']) is int and event['terminal_owner']==1
        checks=[]
        for j in (0,1):
            seg=event['segments'][j];p=nodes[j]['next_primitive_partition']
            assert type(seg['owner']) is int and seg['owner']==j and type(seg['primitive_id']) is int
            assert len(p)==4 and [v['primitive_id'] for v in p]==[0,1,2,3]
            assert all(type(v['primitive_id']) is int and type(v['owner']) is int and v['owner']==v['primitive_id']//2 for v in p)
            chosen=[v for v in p if v['relation']=='chosen']
            assert len(chosen)==1 and chosen[0]['primitive_id']==seg['primitive_id']
            assert type(nodes[j+1]['arrival_primitive_id']) is int and nodes[j+1]['arrival_primitive_id']==seg['primitive_id']
            lo,hi=map(endpoint,seg['segment_interval_words'])
            assert lo>0 and hi>=lo and [F(*x) for x in chosen[0]['distance_BU']]==[lo,hi]
            for values in (event['projected_misses'],seg['behind'],seg['same_owner_departures_skipped']):
                assert type(values) is list and all(type(v) is int and 0<=v<4 for v in values) and values==sorted(set(values))
            assert [v['primitive_id'] for v in p if v['relation']=='projected_miss']==event['projected_misses']
            assert [v['primitive_id'] for v in p if v['relation']=='behind']==seg['behind']
            assert [v['primitive_id'] for v in p if v['relation']=='same_owner_departure']==seg['same_owner_departures_skipped']
            gaps=[F(*v['shared_origin_clearance_BU']) for v in p if v['relation']=='strictly_later']
            assert (seg['competitor_clearance_words'] is None and not gaps) or (seg['competitor_clearance_words'] is not None and gaps and min(gaps)>0 and endpoint(seg['competitor_clearance_words'])==min(gaps))
            checks.append({'selected_primitive_id':seg['primitive_id'],'partition_sha256':digest(p),
                           'event_segment_sha256':digest(seg),'root_enclosure_BU':[pair(lo),pair(hi)]})
        d=event['departure_certificate']
        assert d['input_packet_sha256']==c['input_packet_sha256'] and d['source_id']==sid
        assert type(d['owner']) is int and d['owner']==0 and type(d['primitive_id']) is int
        assert d['primitive_id']==event['segments'][0]['primitive_id']
        assert d['origin']=='derived-from-accepted-first-event-not-caller-previous-id'
        rows.append({'source_id':sid,'tree_nodes_sha256':digest(nodes),'native_event_row_sha256':digest(event),
                     'checks':checks,'certificate_sha256':t['certificate_sha256'],BFLAG:True})
    return c,rows
def main():
    report=json.loads((ROOT/REPORT).read_bytes())
    assert report['inherited_pin_source']=={'path':BASE,'sha256':BASE_SHA}
    pins=pins_from(report)
    for p,h in pins.items():assert sha((ROOT/p).read_bytes())==h,p
    assert len(pins)==227 and pins[TREE]==TREE_SHA
    tree=payload(read(TREE,TREE_SHA))['cases'];geometry=payload(read(GEO,pins[GEO]))['cases'];events=payload(read(EVENT,pins[EVENT]))['cases']
    packets=payload(read('coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json',pins['coordinacion/respuestas/AXIAL-NATIVE-INGRESS-001-CODEX.json']))['packets']
    presence='coordinacion/respuestas/AXIAL-NATIVE-PRESENCE-STOPS-001-CODEX.json'
    packets.update({n:v['parent'] for n,v in payload(read(presence,pins[presence]))['synthetic_controls'].items()})
    products=payload(read(PRODUCT,PRODUCT_SHA))['cases']
    data=payload(report);assert data['PASS'] is True and data['tests']==5;data=data['data'];result=data['audit']
    assert result['model']==BMODEL and set(result['cases'])==set(packets) and len(packets)==17
    assert result['case_order']==list(packets) and result['inherited_pins_verified']==223
    assert result['tree_report_sha256']==TREE_SHA and result['previous_report_sha256']==BASE_SHA
    assert all(result[k]==0 for k in ('new_ray_traces','new_barycentric_evaluations','new_products','new_trigonometry'))
    assert result['native_event_arithmetic_reexecuted'] is False and all(result[k] is False for k in BFALSE)
    matches=0;sources=0;geometry_STOP=0;missing_STOP=0;numeric_STOPs=0;numeric_evaluated=0
    for n,v in result['cases'].items():
        assert v['input_packet_sha256']==digest(packets[n]) and all(v[k] is False for k in BFALSE)
        old=products[n]['sources'];assert v['retained_source_product_row_sha256s']==[digest(s) for s in old]
        assert v['retained_source_product_evaluated']==[s['source_product_evaluated'] for s in old]
        reasons=[None if s['source_product_evaluated'] else s['reason'] for s in old]
        assert v['retained_source_numerical_STOP_reasons']==reasons
        numeric_STOPs+=sum(x is not None for x in reasons);numeric_evaluated+=sum(v['retained_source_product_evaluated'])
        if n not in events or n not in geometry or n not in tree:
            missing_STOP+=1;assert v[BFLAG] is False and v['status']=='STOP' and v['sources']==[]
            assert v['reason']=='no exact current INPUT event/geometry/tree receipt; no same-snapshot alias borrowing'
        elif not tree[n]['geometric_tree_complete_restricted_CPU_only']:
            geometry_STOP+=1;assert events[n]['accepted_axial_two_event_geometry_CPU_only'] is False
            assert v[BFLAG] is False and v['status']=='STOP' and v['sources']==[] and v['reason']==tree[n]['reason']
        else:
            matches+=1;c,rows=validate(packets[n],geometry[n],tree[n],events[n])
            assert v['context']==c and v['sources']==rows and v[BFLAG] is True and v['status']=='MATCH_RETAINED_CPU_TREE'
            assert v['certificate_sha256']==tree[n]['certificate_sha256']
            assert v['reuse_provenance']=='previously independently verified CPU tree proof; new lineage/bytes/endpoint checks ONLY'
            sources+=len(rows)
    assert (matches,sources,geometry_STOP,missing_STOP,numeric_STOPs,numeric_evaluated)==(8,9,5,4,14,5)
    assert len(data['rejections'])==23
    from copy import deepcopy
    for r in data['rejections']:
        try:
            if r['target']=='public':
                names=r['names'];assert r['model']==BMODEL and type(names) is list and 1<=len(names)<=64
                assert all(type(n) is str and n for n in names) and len(set(names))==len(names) and set(names)<=set(packets)
            else:
                objects={'packet':deepcopy(packets['positive']),'geometry':deepcopy(geometry['positive']),
                         'tree':deepcopy(tree['positive']),'events':deepcopy(events['positive'])}
                current=objects[r['target']]
                for key in r['path'][:-1]:current=current[key]
                current[r['path'][-1]]=deepcopy(r['value'])
                if r['rehash_tree']:objects['tree']['certificate_sha256']=digest(objects['tree']['certificate'])
                validate(objects['packet'],objects['geometry'],objects['tree'],objects['events'])
        except (AssertionError,KeyError,TypeError):
            pass
        else:raise AssertionError('invalid rejection '+r['label'])
    print(json.dumps({'PASS':True,'pins_verified':227,'cases':17,'retained_tree_matches':8,'matched_sources':9,
                      'old_geometry_STOPs':5,'missing_exact_event_receipt_STOPs':4,'numeric_STOPs_preserved':14,
                      'numeric_products_evaluated_retained':5,'rejections':23,'partition_comparisons':72,
                      'root_endpoint_comparisons':36,'new_ray_traces':0,'new_barycentric':0,
                      'native_complete_geometry_accepted':False,'full_field_accepted':False},sort_keys=True))
if __name__=='__main__':main()
