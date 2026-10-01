"""Scene-bound sufficient root margin and one-leg phase budget, CPU only.

Deliberately narrow: unit signed X rays, X-normal translated planes, fixed YZ
projection, strict interior hits. Boxes span original and modeled ABI decode;
optional declared axial uncertainty is conditional, not a native error bound.
"""
from fractions import Fraction as F

from exp005_precision_transport_audit import transported
from history_lineage_cpu_v2 import scene_binding, triangles, vec, nearest


def ratio(x):
    return [x.numerator, x.denominator]


def exact_nonnegative(x):
    if isinstance(x, bool) or not isinstance(x, (int, float, F)):
        raise ValueError('finite nonnegative rational budget required')
    try:
        x = F(x)
    except (ValueError, OverflowError):
        raise ValueError('finite nonnegative rational budget required') from None
    if x < 0:
        raise ValueError('finite nonnegative rational budget required')
    return x


def projected_weights(origin, tri):
    """Fixed YZ projection: exact barycentrics, no epsilon/snap."""
    a, b, c = tri
    by, bz = b[1]-a[1], b[2]-a[2]
    cy, cz = c[1]-a[1], c[2]-a[2]
    py, pz = origin[1]-a[1], origin[2]-a[2]
    det = by*cz-bz*cy
    if det == 0:
        raise ValueError('nondegenerate YZ triangle projection required')
    u, v = (py*cz-pz*cy)/det, (by*pz-bz*py)/det
    return (1-u-v, u, v)


def certify_axial_roots(snapshot, *, phase_budget_rad, extra_axial_radius_BU=0):
    budget = exact_nonnegative(phase_budget_rad)
    radius = exact_nonnegative(extra_axial_radius_BU)
    binding, original = scene_binding(snapshot)
    recovered, _ = transported(snapshot)  # Pure helper only, never old audit().
    recovered_binding, decoded = scene_binding(recovered)
    old_geo, new_geo = triangles(original), triangles(decoded)
    if original.source_ids != decoded.source_ids or original.geometry.object_ids != decoded.geometry.object_ids \
            or len(old_geo) != len(new_geo):
        raise ValueError('same source/object/primitive order required')
    rows = []
    for source, new_source in zip(snapshot['sources'], recovered['sources']):
        row = {'source_id': source['id'], 'accepted_CPU_axial_root_margin': False,
               'accepted_CPU_one_leg_phase_budget': False}
        try:
            origin, new_origin = vec(source['position_BU']), vec(new_source['position_BU'])
            direction = vec(source['direction'])
            if direction not in ((1,0,0), (-1,0,0)) or direction != vec(new_source['direction']):
                raise ValueError('unchanged signed unit X direction required')
            if origin[1:] != new_origin[1:]:
                raise ValueError('unchanged source YZ required')
            sign = direction[0]
            source_lo, source_hi = min(origin[0],new_origin[0])-radius, max(origin[0],new_origin[0])+radius
            candidates = []
            misses = []
            for pid, ((owner, tri), (new_owner, new_tri)) in enumerate(zip(old_geo,new_geo)):
                if owner != new_owner or any(a[1:] != b[1:] for a,b in zip(tri,new_tri)):
                    raise ValueError('unchanged triangle YZ/owner required')
                if len({p[0] for p in tri}) != 1 or len({p[0] for p in new_tri}) != 1:
                    raise ValueError('X-normal translated triangle planes required')
                weights = projected_weights(origin, tri)
                if any(w < 0 for w in weights):
                    misses.append(pid)
                    continue
                if any(w == 0 for w in weights):
                    raise ValueError('boundary hit excluded by sufficient margin contract')
                lo, hi = min(tri[0][0],new_tri[0][0])-radius, max(tri[0][0],new_tri[0][0])+radius
                low, high = lo-source_hi, hi-source_lo
                if sign < 0:
                    low, high = -high, -low
                if high < 0:
                    misses.append(pid)
                    continue
                if low <= 0:
                    raise ValueError('axial source-contact interval reaches zero')
                candidates.append((pid, owner, low, high))
            t0, winner, owner, _ = nearest(origin,direction,old_geo,None)
            td, decoded_winner, decoded_owner, _ = nearest(new_origin,direction,new_geo,None)
            if (winner,owner) != (decoded_winner,decoded_owner):
                raise ValueError('endpoint nearest identity changed')
            chosen = next(c for c in candidates if c[0] == winner)
            gaps = [c[2]-chosen[3] for c in candidates if c[0] != winner]
            if gaps and min(gaps) <= 0:
                raise ValueError('competitor axial intervals overlap or touch')
            low, high = chosen[2:]
            row.update(accepted_CPU_axial_root_margin=True, primitive_id=winner,
                object_id=original.geometry.object_ids[owner],
                length_interval_BU=[ratio(low),ratio(high)],
                original_length_BU=ratio(t0), decoded_length_BU=ratio(td),
                source_clearance_lower_BU=ratio(low),
                competitor_clearance_lower_BU=ratio(min(gaps)) if gaps else None,
                proven_miss_primitives=misses,
                positive_candidates=[{'primitive_id':p,'object_index':o,
                    'length_interval_BU':[ratio(a),ratio(b)]} for p,o,a,b in candidates])
            if snapshot['objects'][row['object_id']]['kind'] not in ('det','escape'):
                row['phase_exclusion'] = 'nonterminal root: complete path/reference not certified'
            else:
                # Source phase=0 at each declared origin: original-source gauge.
                # Allow wavelength endpoints to differ; positive interval division.
                w0, wd = F(snapshot['lambda_BU']), F(recovered['lambda_BU'])
                wl, wh = min(w0,wd), max(w0,wd)
                if wl <= 0:
                    raise ValueError('positive wavelength interval required')
                turns0 = t0/w0
                phase_error = 8*max(abs(low/wh-turns0),abs(high/wl-turns0))
                # Elementary pi < 4 => 2*pi < 8, unreduced absolute phase.
                row.update(phase_error_bound_rad=ratio(phase_error),
                    phase_budget_rad=ratio(budget),
                    wavelength_interval_BU=[ratio(wl),ratio(wh)],
                    phase_reference_id='original-source-zero:'+binding+':'+source['id'],
                    accepted_CPU_one_leg_phase_budget=phase_error <= budget)
        except ValueError as exc:
            row['reason'] = str(exc)
        rows.append(row)
    return {'schema':'exp005-axial-root-margin-CPU-v1',
        'original_scene_binding_sha256':binding, 'decoded_scene_binding_sha256':recovered_binding,
        'extra_axial_radius_BU':ratio(radius), 'root_certificates':rows,
        'accepted_CPU_axial_root_margin':all(r['accepted_CPU_axial_root_margin'] for r in rows),
        'accepted_CPU_one_leg_phase_budget':all(r['accepted_CPU_one_leg_phase_budget'] for r in rows),
        'GPU_executed':False, 'native_promotion_allowed':False, 'no_jev_aval':True,
        'scope':'conditional translated-plane X boxes; fixed YZ; roots only; terminal one-leg source-zero phase',
        'excluded':['arbitrary triangle tilt/YZ perturbation/direction change',
            'reflected histories, terminal mode projection, field/power/completeness',
            'native arithmetic/bias/FTZ/driver/RT/authentication/physical optics']}
