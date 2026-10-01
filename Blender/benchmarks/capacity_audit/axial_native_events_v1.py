"""Opt-in restricted two-event geometry from input-only words; CPU, not GPU."""
import axial_native_signed512_v1 as limb
import axial_native_yz_v1 as yz

MODEL='axial-two-events-16limb-signed512-CPU-v1'

def _source_trace(source_id,interior,planes,source_interval,sign,receipt):
    """Internal helper: caller cannot request a previous-owner skip."""
    out={'source_id':source_id,'accepted_axial_two_event_geometry_CPU_only':False,
         'segments':[],'departure_certificate':None,'accepted_complete_geometry':False}
    try:
        limb.require(type(sign) is int and sign in (-1,1),'signed unit X sign')
        limb.require(type(interior) is list and len(interior)<=64,'bounded interior')
        seen=set()
        for item in interior:
            limb.require(type(item) is list and len(item)==2 and
                         type(item[0]) is int and 0<=item[0]<64 and
                         type(item[1]) is int and item[1] in (0,1),'primitive owner')
            limb.require(item[0] not in seen,'unique primitive');seen.add(item[0])
        limb.require(set(planes)=={0,1},'two shared planes')
        for p in planes.values():
            limb.valid(p['lo']);limb.valid(p['hi'])
            limb.require(limb.compare(p['lo'],p['hi'])<=0,'ordered plane interval')
        limb.require(type(source_interval) is list and len(source_interval)==2,'source interval')
        slo,shi=source_interval;limb.valid(slo);limb.valid(shi)
        limb.require(limb.compare(slo,shi)<=0,'ordered source interval')
        departure=None
        def choose(olo,ohi,s):
            candidates=[];skipped=[];behind=[]
            for pid,owner in interior:
                if departure is not None and owner==departure['owner']:
                    skipped.append(pid);continue
                p=planes[owner]
                low,high=limb.sub(p['lo'],ohi),limb.sub(p['hi'],olo)
                if s<0:low,high=limb.negate(high),limb.negate(low)
                if limb.compare(high,limb.ZERO)<0:behind.append(pid);continue
                if limb.compare(low,limb.ZERO)<=0:
                    raise ValueError('other owner zero contact' if departure is not None else 'source zero contact')
                candidates.append((pid,owner,low,high))
            limb.require(bool(candidates),'no strictly positive root')
            chosen=candidates[0]
            for candidate in candidates[1:]:
                if limb.compare(candidate[2],chosen[2])<0:chosen=candidate
            pid,owner,lo,hi=chosen;gaps=[]
            for pp,oo,_,_ in candidates:
                if pp==pid:continue
                competitor,winner=planes[oo],planes[owner]
                gap=limb.sub(competitor['lo'],winner['hi']) if s>0 else limb.sub(winner['lo'],competitor['hi'])
                limb.require(limb.compare(gap,limb.ZERO)>0,'competitor intervals overlap/touch')
                gaps.append(gap)
            minimum=None
            for gap in gaps:
                if minimum is None or limb.compare(gap,minimum)<0:minimum=gap
            return {'primitive_id':pid,'owner':owner,'segment_interval_words':[lo,hi],
                    'competitor_clearance_words':minimum,'same_owner_departures_skipped':skipped,'behind':behind}
        first=choose(slo,shi,sign)
        limb.require(first['owner']==0,'first event must be mirror')
        # Generated ONLY after accepted first root; shared planes came from scene words.
        m=planes[first['owner']]
        departure={'owner':first['owner'],'primitive_id':first['primitive_id'],
                   'source_id':source_id,'input_packet_sha256':receipt,
                   'shared_plane_interval_words':[list(m['lo']),list(m['hi'])],
                   'origin':'derived-from-accepted-first-event-not-caller-previous-id'}
        out['departure_certificate']=departure
        second=choose(*departure['shared_plane_interval_words'],-sign)
        limb.require(second['owner']==1,'second event must be terminal')
        d=planes[second['owner']];two=[2]+[0]*15
        low=limb.sub(limb.sub(limb.mul(two,m['lo']),shi),d['hi'])
        high=limb.sub(limb.sub(limb.mul(two,m['hi']),slo),d['lo'])
        if sign<0:low,high=limb.negate(high),limb.negate(low)
        limb.require(limb.compare(low,limb.ZERO)>0,'nonpositive complete length')
        out.update(accepted_axial_two_event_geometry_CPU_only=True,segments=[first,second],
                   mirror_owner=first['owner'],terminal_owner=second['owner'],
                   length_interval_words=[low,high],direction_sign=sign)
    except ValueError as error:out['reason']=str(error)
    return out

def trace_scene(name,packet,expected_packet_sha256):
    """Explicit exact-YZ axial two-owner profile, no general-geometry promotion."""
    projection=yz.coverage(name,packet,expected_packet_sha256)
    x=limb.x_enclosures(name,packet,expected_packet_sha256)
    limb.require(projection['source_order']==x['source_order'] and
                 projection['word_ABI_sha256']==x['word_ABI_sha256'],'same input ABI/order')
    rows=[]
    for coverage,source in zip(projection['sources'],x['sources']):
        sid=coverage['source_id'];limb.require(sid==source['source_id'],'ordered source binding')
        if coverage['projection_failures']:
            rows.append({'source_id':sid,'accepted_axial_two_event_geometry_CPU_only':False,
                         'segments':[],'departure_certificate':None,'accepted_complete_geometry':False,
                         'reason':'nondegenerate YZ projection required' if any(p['reason']=='degenerate_FAIL'
                                  for p in coverage['projection_failures']) else 'boundary hit excluded; no snap'})
            continue
        row=_source_trace(sid,coverage['strict_interior_primitive_owner'],x['planes'],
                          source['source_X_interval_words'],source['direction_sign'],expected_packet_sha256)
        if row['accepted_axial_two_event_geometry_CPU_only']:row['projected_misses']=coverage['projected_misses']
        rows.append(row)
    return {'model':MODEL,'case_name':name,'input_packet_sha256':expected_packet_sha256,
            'scene_binding_sha256':x['scene_binding_sha256'],'word_ABI_sha256':x['word_ABI_sha256'],
            'source_order':x['source_order'],'sources':rows,
            'accepted_axial_two_event_geometry_CPU_only':all(s['accepted_axial_two_event_geometry_CPU_only'] for s in rows),
            'profile':'retained-exact-YZ-axial-X-two-owner-two-event-only',
            'accepted_complete_geometry':False,'accepted_full_field_pipeline':False,
            'phase_evaluated':False,'reference_length_not_geometric_length':True,
            'GLSL_compiled':False,'GPU_executed':False,'GPU_job_admission':False}
