"""Conditional scene-bound ONE-mirror axial path, exact CPU only.

One shared plane variable per owner makes self-departure identically zero;
never grants another owner's contact the exemption. No old suite or fields.
"""
from fractions import Fraction as F

from axial_root_margin_cpu_v1 import ratio, exact_nonnegative, projected_weights
from exp005_precision_transport_audit import transported
from history_lineage_cpu_v2 import scene_binding, triangles, vec, nearest, dot


def signed_interval(lo, hi, sign):
    return (lo,hi) if sign > 0 else (-hi,-lo)


def planes_and_projection(old_geo, new_geo, origin, radius):
    planes = {}
    interior = []
    misses = []
    for pid, ((owner, tri), (new_owner, new_tri)) in enumerate(zip(old_geo,new_geo)):
        if owner != new_owner or any(a[1:] != b[1:] for a,b in zip(tri,new_tri)):
            raise ValueError('unchanged owner and YZ projection required')
        if len({v[0] for v in tri}) != 1 or len({v[0] for v in new_tri}) != 1:
            raise ValueError('X-normal triangle plane required')
        x0, xd = tri[0][0], new_tri[0][0]
        plane = (x0,xd,min(x0,xd)-radius,max(x0,xd)+radius)
        if owner in planes and planes[owner] != plane:
            raise ValueError('ONE shared X plane variable per object required')
        planes[owner] = plane
        weights = projected_weights(origin,tri)
        if any(w < 0 for w in weights):
            misses.append(pid)
        elif any(w == 0 for w in weights):
            raise ValueError('boundary query excluded by sufficient contract')
        else:
            interior.append((pid,owner))
    return planes,interior,misses


def select_step(origin_interval, sign, planes, interior, winner, *, departure_owner=None):
    low_o,high_o = origin_interval
    candidates = []
    skipped_self = []
    behind = []
    for pid,owner in interior:
        if owner == departure_owner:
            # Caller derives origin from this SAME owner/plane, no independent
            # ray-origin error and no caller-supplied previous primitive.
            skipped_self.append(pid)
            continue
        _,_,lo,hi = planes[owner]
        low,high = signed_interval(lo-high_o,hi-low_o,sign)
        if high < 0:
            behind.append(pid)
            continue
        if low <= 0:
            raise ValueError('unproved zero contact interval on another owner' if departure_owner is not None
                             else 'source clearance interval reaches zero')
        candidates.append((pid,owner,low,high))
    chosen = next((c for c in candidates if c[0] == winner),None)
    if chosen is None:
        raise ValueError('endpoint winner not a proven positive candidate')
    _,_,lo_w,hi_w = planes[chosen[1]]
    gaps = []
    for pid,owner,_,_ in candidates:
        if pid == winner:
            continue
        _,_,lo,hi = planes[owner]
        # Origin cancels: compare planes, not unrelated ray-origin boxes.
        gap,_ = signed_interval(lo-hi_w,hi-lo_w,sign)
        gaps.append(gap)
    if gaps and min(gaps) <= 0:
        raise ValueError('competitor plane intervals overlap or touch')
    return {'primitive_id':winner, 'object_index':chosen[1],
        'segment_length_interval_BU':[ratio(chosen[2]),ratio(chosen[3])],
        'clearance_lower_BU':ratio(chosen[2]),
        'competitor_clearance_lower_BU':ratio(min(gaps)) if gaps else None,
        'identical_plane_departures_skipped':skipped_self,'behind_primitives':behind}


def two_events(origin, direction, geometry):
    t1,p1,o1,n = nearest(origin,direction,geometry,None)
    point = tuple(a+t1*b for a,b in zip(origin,direction))
    reflected = tuple(d-2*dot(direction,n)*c/dot(n,n) for d,c in zip(direction,n))
    t2,p2,o2,_ = nearest(point,reflected,geometry,p1)
    return (p1,o1,p2,o2,t1+t2,reflected)


def certify_axial_reflection(snapshot, *, phase_budget_rad, extra_axial_radius_BU=0):
    budget = exact_nonnegative(phase_budget_rad)
    radius = exact_nonnegative(extra_axial_radius_BU)
    binding,packed = scene_binding(snapshot)
    decoded_snapshot,_ = transported(snapshot)
    decoded_binding,decoded = scene_binding(decoded_snapshot)
    geometry,new_geometry = triangles(packed),triangles(decoded)
    if packed.source_ids != decoded.source_ids or packed.geometry.object_ids != decoded.geometry.object_ids \
            or len(geometry) != len(new_geometry):
        raise ValueError('same source/object/primitive order required')
    rows = []
    for source,new_source in zip(snapshot['sources'],decoded_snapshot['sources']):
        row = {'source_id':source['id'], 'accepted_CPU_one_bounce_topology':False,
               'accepted_CPU_one_bounce_phase_budget':False}
        try:
            origin,new_origin = vec(source['position_BU']),vec(new_source['position_BU'])
            direction = vec(source['direction'])
            if direction not in ((1,0,0),(-1,0,0)) or direction != vec(new_source['direction']) \
                    or origin[1:] != new_origin[1:]:
                raise ValueError('unchanged signed unit X ray and source YZ required')
            planes,interior,misses = planes_and_projection(geometry,new_geometry,origin,radius)
            old = two_events(origin,direction,geometry)
            new = two_events(new_origin,direction,new_geometry)
            if old[:4] != new[:4]:
                raise ValueError('two endpoint event identities changed')
            p1,o1,p2,o2,length0,reflected = old
            name1,name2 = packed.geometry.object_ids[o1],packed.geometry.object_ids[o2]
            if snapshot['objects'][name1]['kind'] != 'mirror' or snapshot['objects'][name2]['kind'] not in ('det','escape'):
                raise ValueError('exactly one mirror then terminal required; other branches excluded')
            sign = direction[0]
            if reflected != (-sign,0,0) or new[5] != reflected:
                raise ValueError('unproved axial reflection')
            source_lo,source_hi = min(origin[0],new_origin[0])-radius,max(origin[0],new_origin[0])+radius
            first = select_step((source_lo,source_hi),sign,planes,interior,p1)
            _,_,mirror_lo,mirror_hi = planes[o1]
            second = select_step((mirror_lo,mirror_hi),-sign,planes,interior,p2,departure_owner=o1)
            _,_,terminal_lo,terminal_hi = planes[o2]
            # Preserve correlation: L=sign*(2*M-S-D), one mirror variable.
            low,high = signed_interval(2*mirror_lo-source_hi-terminal_hi,
                                      2*mirror_hi-source_lo-terminal_lo,sign)
            if low <= 0:
                raise ValueError('nonpositive complete one-bounce length interval')
            w0,wd = F(snapshot['lambda_BU']),F(decoded_snapshot['lambda_BU'])
            wl,wh = min(w0,wd),max(w0,wd)
            if wl <= 0:
                raise ValueError('positive transported wavelength required')
            mirror_phase0 = F(snapshot['objects'][name1]['phase_rad'])
            mirror_phased = F(decoded_snapshot['objects'][name1]['phase_rad'])
            mirror_error = abs(mirror_phased-mirror_phase0)
            geometric_error = 8*max(abs(low/wh-length0/w0),abs(high/wl-length0/w0))
            phase_error = geometric_error+mirror_error
            row.update(accepted_CPU_one_bounce_topology=True,
                accepted_CPU_one_bounce_phase_budget=phase_error <= budget,
                mirror_object_id=name1,terminal_object_id=name2,segments=[first,second],
                projected_miss_primitives=misses,
                length_interval_BU=[ratio(low),ratio(high)],
                original_length_BU=ratio(length0),decoded_length_BU=ratio(new[4]),
                wavelength_interval_BU=[ratio(wl),ratio(wh)],
                geometric_phase_error_bound_rad=ratio(geometric_error),
                mirror_phase_transport_error_rad=ratio(mirror_error),
                phase_error_bound_rad=ratio(phase_error),phase_budget_rad=ratio(budget),
                phase_reference_id='original-source-zero:'+binding+':'+source['id'])
        except ValueError as exc:
            row['reason'] = str(exc)
        rows.append(row)
    return {'schema':'exp005-axial-one-bounce-margin-CPU-v1',
        'original_scene_binding_sha256':binding,'decoded_scene_binding_sha256':decoded_binding,
        'extra_axial_radius_BU':ratio(radius),'path_certificates':rows,
        'accepted_CPU_one_bounce_topology':all(r['accepted_CPU_one_bounce_topology'] for r in rows),
        'accepted_CPU_one_bounce_phase_budget':all(r['accepted_CPU_one_bounce_phase_budget'] for r in rows),
        'GPU_executed':False,'native_promotion_allowed':False,'no_jev_aval':True,
        'scope':'conditional shared-owner X-plane boxes, unchanged YZ; exactly mirror then terminal, source-zero path phase',
        'excluded':['arbitrary tilt/YZ/direction errors, more bounces and splitters',
            'source amplitude, terminal modal phase/field/power and general scene completeness',
            'native bias/RN/FTZ/driver/auth/RT/physical optics']}
