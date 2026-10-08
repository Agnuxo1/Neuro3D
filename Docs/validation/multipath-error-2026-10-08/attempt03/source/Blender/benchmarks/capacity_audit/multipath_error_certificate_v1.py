"""Actual complete scalar-path error enclosures, not assumed upstream budgets.

CPU represented model or explicit bounded input family. Topology/mode failures
are UNKNOWN. Physical calibration and unexecuted native kernels stay unknown.
"""
from fractions import Fraction as F
from functools import lru_cache
import hashlib
import json

from rational_interval_v1 import Interval as I, BITS, pi_interval, sincos, error_upper, upward_float
from robust_multipath_v1 import trace_scene, geometry, rational, vector, parallel, cross as exact_cross, sub as exact_sub


class Uncertified(Exception):
    pass


def require(value, reason):
    if not value: raise Uncertified(reason)


def wire(value):
    if isinstance(value, I): return value.wire()
    if isinstance(value, F): return [value.numerator, value.denominator]
    if isinstance(value, complex): return [value.real, value.imag]
    if isinstance(value, dict): return {key: wire(v) for key, v in value.items()}
    if isinstance(value, (list, tuple)): return [wire(v) for v in value]
    return value


def snapshot_binding(snapshot):
    return hashlib.sha256(json.dumps(wire(snapshot), sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def default_radii(snapshot):
    return {'vertex_radius': F(0), 'object_translation': {name: (0,0,0) for name in snapshot['objects']},
            'source_position': F(0), 'source_direction': {s['id']: (0,0,0) for s in snapshot['sources']},
            'source_field': F(0), 'wavelength': F(0), 'mirror_phase': F(0), 'transmittance': F(0), 'reference': F(0)}


def validated_radii(snapshot, supplied):
    expected = default_radii(snapshot)
    require(type(supplied) is dict and set(supplied) == set(expected), 'UNKNOWN_MISSING_BOUND')
    result = {}
    for key in expected:
        if key in ('object_translation', 'source_direction'):
            require(type(supplied[key]) is dict and set(supplied[key]) == set(expected[key]), 'UNKNOWN_MISSING_BOUND')
            result[key] = {name: vector(v) for name, v in supplied[key].items()}
            require(all(min(v) >= 0 for v in result[key].values()), 'INVALID_NEGATIVE_BOUND')
        else:
            result[key] = rational(supplied[key]); require(result[key] >= 0, 'INVALID_NEGATIVE_BOUND')
    return result


def box(value, radius): return I(F(value)-radius, F(value)+radius)
def vec_box(value, radii): return tuple(box(v, r) for v, r in zip(value, radii))
def add(a,b): return tuple(x+y for x,y in zip(a,b))
def sub(a,b): return tuple(x-y for x,y in zip(a,b))
def scale(a,s): return tuple(x*s for x in a)
def dot(a,b): return sum((x*y for x,y in zip(a,b)), I(0))
def cross(a,b): return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def norm_squared(a): return sum((v.square() for v in a), I(0))
def is_zero(v): return all(x.lo == x.hi == 0 for x in v)


def triangle_interval(tri, radii):
    translation = radii['object_translation'][tri['object_id']]
    vr = radii['vertex_radius']
    vertices = tuple(vec_box(v, tuple(t+vr for t in translation)) for v in tri['vertices'])
    # Shared translation cancels from edges exactly; this structural identity
    # must be retained rather than subtracting independent interval copies.
    e1, e2 = exact_sub(tri['vertices'][1],tri['vertices'][0]), exact_sub(tri['vertices'][2],tri['vertices'][0])
    edges = tuple(vec_box(e, (2*vr,)*3) for e in (e1,e2))
    return {'triangle': tri, 'vertices': vertices, 'e1': edges[0], 'e2': edges[1], 'normal': cross(*edges)}


def possible_hit(origin, direction, tri):
    for axis in range(3):
        lower = min(v[axis].lo for v in tri['vertices'])
        upper = max(v[axis].hi for v in tri['vertices'])
        if (direction[axis].lo >= 0 and origin[axis].lo > upper) or (
                direction[axis].hi <= 0 and origin[axis].hi < lower):
            return None  # No positive-time point can enter the finite AABB.
    p = cross(direction, tri['e2']); determinant = dot(tri['e1'],p)
    if determinant.lo == determinant.hi == 0:
        plane_distance = dot(sub(origin,tri['vertices'][0]),tri['normal'])
        if not plane_distance.contains(0): return None
    require(not determinant.contains(0), 'UNKNOWN_GRAZING_OR_PARALLEL_CANDIDATE')
    rel = sub(origin,tri['vertices'][0]); q = cross(rel,tri['e1'])
    u,v,t = dot(rel,p)/determinant, dot(direction,q)/determinant, dot(tri['e2'],q)/determinant
    if t.hi < 0 or u.hi < 0 or v.hi < 0 or (u+v).lo > 1: return None
    return {'u':u,'v':v,'t':t,'normal':tri['normal'],'determinant':determinant}


def same_plane(a,b):
    n1 = exact_cross(exact_sub(a['vertices'][1],a['vertices'][0]),exact_sub(a['vertices'][2],a['vertices'][0]))
    n2 = exact_cross(exact_sub(b['vertices'][1],b['vertices'][0]),exact_sub(b['vertices'][2],b['vertices'][0]))
    return parallel(n1,n2) and sum(x*y for x,y in zip(exact_sub(a['vertices'][0],b['vertices'][0]),n2)) == 0


def exact_dot(a,b): return sum((x*y for x,y in zip(a,b)),F(0))


@lru_cache(maxsize=128)
def convex_boundary(faces):
    """Prove finite coplanar triangle union equals one convex polygon.

    Exact separating axes exclude overlapping interiors. Boundary forms one
    oriented cycle; all vertices lie in every inward half-plane; total area
    equals polygon area. An omitted interior point would create positive area.
    """
    a,b,c=faces[0]; normal=exact_cross(exact_sub(b,a),exact_sub(c,a))
    oriented=[]; edges={}; vertices=set()
    for face in faces:
        x,y,z=face; n=exact_cross(exact_sub(y,x),exact_sub(z,x))
        if not parallel(n,normal) or exact_dot(exact_sub(x,a),normal)!=0: return None
        if exact_dot(n,normal)<0: face=(x,z,y)
        oriented.append(face); vertices.update(face)
        for i in range(3):
            first,second=face[i],face[(i+1)%3]
            edges.setdefault(tuple(sorted((first,second))),[]).append((first,second))
    boundary=[]
    for values in edges.values():
        if len(values)==1: boundary.extend(values)
        elif len(values)!=2 or values[0]!=(values[1][1],values[1][0]): return None
    if len(boundary)<3: return None
    outgoing={first:second for first,second in boundary}
    if len(outgoing)!=len(boundary) or {v for _,v in boundary}!=set(outgoing): return None
    start=boundary[0][0]; current=start; visited=set()
    while current not in visited:
        visited.add(current); current=outgoing[current]
    if current!=start or len(visited)!=len(boundary): return None
    for first,second in boundary:
        edge=exact_sub(second,first)
        if any(exact_dot(exact_cross(edge,exact_sub(v,first)),normal)<0 for v in vertices): return None
    for i,first in enumerate(oriented):
        for second in oriented[i+1:]:
            separated=False
            for face in (first,second):
                for j in range(3):
                    axis=exact_cross(exact_sub(face[(j+1)%3],face[j]),normal)
                    pa=[exact_dot(v,axis) for v in first]; pb=[exact_dot(v,axis) for v in second]
                    if max(pa)<=min(pb) or max(pb)<=min(pa): separated=True
            if not separated: return None
    area=sum((exact_dot(exact_cross(exact_sub(f[1],f[0]),exact_sub(f[2],f[0])),normal) for f in oriented),F(0))
    border_area=sum((exact_dot(exact_cross(x,y),normal) for x,y in boundary),F(0))
    if area!=border_area or area<=0: return None
    return tuple(boundary),normal


def covered_by_object(point,selected,triangles,radii):
    if radii['vertex_radius']!=0: return False
    baseline=selected['triangle']; name=baseline['object_id']
    group=[t['triangle']['vertices'] for t in triangles if t['triangle']['object_id']==name and same_plane(t['triangle'],baseline)]
    proof=convex_boundary(tuple(group))
    if proof is None: return False
    boundary,normal=proof
    for first,second in boundary:
        anchor=vec_box(first,radii['object_translation'][name])
        edge=tuple(I(v) for v in exact_sub(second,first))
        if dot(cross(edge,sub(point,anchor)),tuple(I(v) for v in normal)).lo<=0: return False
    return True


def replay_path(snapshot, path, radii, triangles, objects):
    source = next(s for s in snapshot['sources'] if s['id'] == path['source_id'])
    origin = vec_box(vector(source['position_BU']), (radii['source_position'],)*3)
    direction = vec_box(vector(source['direction']), radii['source_direction'][source['id']])
    norm2 = norm_squared(direction)
    require(norm2.lo > 0, 'UNKNOWN_ZERO_DIRECTION')
    length, segments, previous = I(0), [], None
    for item in path['hits']:
        selected = triangles[item['primitive_id']]
        expected = possible_hit(origin,direction,selected)
        require(expected is not None, 'UNKNOWN_SELECTED_HIT')
        point = add(origin,scale(direction,expected['t']))
        interior = expected['u'].lo > 0 and expected['v'].lo > 0 and (expected['u']+expected['v']).hi < 1
        require(expected['t'].lo > 0 and (interior or covered_by_object(point,selected,triangles,radii)),
                'UNKNOWN_BARYCENTRIC_COVERAGE')
        for other in triangles:
            baseline = other['triangle']
            if baseline['primitive_id'] == item['primitive_id']: continue
            if previous is not None and (baseline['primitive_id'] == previous['primitive_id'] or
                    (radii['vertex_radius'] == 0 and baseline['object_id'] == previous['object_id'] and same_plane(baseline,previous))):
                # Origin is constructed on the previous triangle. With nonzero
                # incidence, a straight ray cannot re-intersect that plane.
                det = dot(other['e1'], cross(direction,other['e2']))
                require(not det.contains(0), 'UNKNOWN_DEPARTURE_INCIDENCE'); continue
            if (radii['vertex_radius'] == 0 and baseline['object_id'] == selected['triangle']['object_id'] and
                    same_plane(baseline,selected['triangle'])):
                continue  # Selected interior coverage and identical optical plane proven.
            candidate = possible_hit(origin,direction,other)
            if candidate is not None:
                require(candidate['t'].lo > expected['t'].hi, 'UNKNOWN_HIT_ORDER')
        segment = expected['t']*norm_squared(direction).sqrt()
        length = length+segment; segments.append(segment)
        obj = objects[item['object_id']]
        if item['event'] in ('det','escape'):
            require(is_zero(cross(direction,tuple(I(v) for v in obj['axis']))) and
                    dot(direction,tuple(I(v) for v in obj['axis'])).lo > 0, 'UNKNOWN_TERMINAL_MODE')
            require(radii['vertex_radius'] == 0 and radii['reference'] == 0, 'UNKNOWN_TERMINAL_REFERENCE_PLANE')
            reference = vec_box(obj['reference'],radii['object_translation'][item['object_id']])
            offset = dot(direction,sub(reference,point))/norm_squared(direction).sqrt()
            return length+offset, segments
        if item['event'] in ('mirror','r'):
            normal = expected['normal']; normal2 = norm_squared(normal)
            require(normal2.lo > 0, 'UNKNOWN_DEGENERATE_NORMAL')
            if radii['vertex_radius']==0:
                baseline=selected['triangle']['vertices']
                n=exact_cross(exact_sub(baseline[1],baseline[0]),exact_sub(baseline[2],baseline[0])); n2=exact_dot(n,n)
                direction=tuple(sum((I(F(int(i==j))-2*n[i]*n[j]/n2)*direction[j] for j in range(3)),I(0)) for i in range(3))
            else:
                direction = sub(direction,scale(normal,2*dot(direction,normal)/normal2))
        origin, previous = point, selected['triangle']
    raise Uncertified('UNKNOWN_MISSING_TERMINAL')


def path_enclosure(snapshot, path, radii, wavelength, objects, triangles, represented):
    if represented:
        length = I(path['phase_length_numerator'])/I(path['direction_norm_squared']).sqrt()
        segments = [I(h['parameter'])*I(path['direction_norm_squared']).sqrt() for h in path['hits']]
    else:
        length, segments = replay_path(snapshot,path,radii,triangles,objects)
    source = next(s for s in snapshot['sources'] if s['id'] == path['source_id'])
    amplitude = tuple(box(rational(v),radii['source_field']) for v in source['field_reim'])
    power, mirror_phase = I(1), I(0)
    for event in path['hits']:
        obj = objects[event['object_id']]
        if event['event'] == 'mirror': mirror_phase = mirror_phase+box(obj['phase'],radii['mirror_phase'])
        elif event['event'] in ('t','r'):
            tau = box(obj['tau'],radii['transmittance'])
            require(0 <= tau.lo <= tau.hi <= 1, 'INVALID_TRANSMITTANCE_BOUND')
            power = power*(tau if event['event'] == 't' else 1-tau)
    phase = 2*pi_interval()*length/wavelength+mirror_phase
    sine,cosine = sincos(phase)
    magnitude = power.sqrt()
    real = magnitude*(amplitude[0]*cosine-amplitude[1]*sine)
    imag = magnitude*(amplitude[0]*sine+amplitude[1]*cosine)
    for _ in range(path['quarter_turns']): real,imag = -imag,real
    return {'source_id':path['source_id'],'terminal':path['terminal'],'effective_length_BU':length,
            'segment_lengths_BU':segments,'phase_rad_before_quarter_turn':phase,'power_factor':power,
            'field_real':real,'field_imag':imag}


def certify_scene(snapshot, *, radii=None, max_rays=4096, max_depth=64):
    report = {'schema':'neuro3d-complete-error-certificate-v1','backend':'CPU_RATIONAL_OUTWARD_INTERVALS',
              'interval_bits':BITS,'scene_sha256':snapshot_binding(snapshot),'status':'UNKNOWN',
              'physical_input_bounds':'UNKNOWN_NOT_ZERO','native_full_kernel_certified':False,
              'scope':'represented scalar-optics CPU model' if radii is None else 'explicit supplied scalar-model input box',
              'paths':[],'ports':None}
    try:
        represented = radii is None
        radii = validated_radii(snapshot,default_radii(snapshot) if represented else radii)
        report['input_radii'] = radii
        traced = trace_scene(snapshot,max_rays=max_rays,max_depth=max_depth)
        require(traced['status'] == 'COMPLETE','UNKNOWN_INCOMPLETE_TRACE')
        wavelength,objects,baseline_triangles = geometry(snapshot)
        wave = box(wavelength,radii['wavelength']); require(wave.lo > 0,'UNKNOWN_WAVELENGTH')
        for source in snapshot['sources']:
            require(not (all(rational(v)==0 for v in source['field_reim']) and radii['source_field']>0), 'UNKNOWN_SOURCE_SUPPORT')
        for obj in objects.values():
            if obj['kind']=='bs':
                require(not (obj['tau'] in (0,1) and radii['transmittance']>0),'UNKNOWN_BRANCH_SUPPORT')
        triangles = [triangle_interval(tri,radii) for tri in baseline_triangles]
        enclosures = [path_enclosure(snapshot,path,radii,wave,objects,triangles,represented) for path in traced['paths']]
        report['paths'] = enclosures
        ports = {}
        for name in traced['ports']:
            real = sum((p['field_real'] for p in enclosures if p['terminal']==name), I(0))
            imag = sum((p['field_imag'] for p in enclosures if p['terminal']==name), I(0))
            intensity = real.square()+imag.square()
            estimate = traced['fields'][name]
            field_error = error_upper(estimate.real,real)+error_upper(estimate.imag,imag)
            intensity_error = error_upper(traced['powers'][name],intensity)
            ports[name] = {'field_real':real,'field_imag':imag,'intensity':intensity,
                'estimated_field':[estimate.real,estimate.imag],'estimated_intensity':traced['powers'][name],
                'field_error_L1_upper':field_error,'intensity_error_upper':intensity_error,
                'field_error_L1_upward_float':upward_float(field_error),
                'intensity_error_upward_float':upward_float(intensity_error)}
        report.update(status='CERTIFIED_REPRESENTED_MODEL' if represented else 'CERTIFIED_SUPPLIED_MODEL_BOX',
                      ports=ports,topology_certified=True,pi_interval=pi_interval(),path_count=len(enclosures),rays=traced['rays'])
    except (Uncertified,ValueError,ZeroDivisionError,OverflowError) as error:
        report.update(reason=str(error),topology_certified=False)
    return wire(report)
