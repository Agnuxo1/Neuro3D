"""Independent ideal scalar ray/phase oracle over exported triangular geometry.

Standard library only; never imports the EXP-005 consumer, Blender, or a learned
matrix. Discovers ALL hits from scene triangles. This remains digital ray optics
with an ideal coherent, single-direction mode per terminal, not Maxwell optics.
Initial validation uses synthetic scenes; actual .blend parity is still pending.
"""
import cmath
import math
from numbers import Real


def scalar(value):
    if isinstance(value,bool) or not isinstance(value,Real) or not math.isfinite(value):
        raise ValueError('finite real required')
    return float(value)


def vec(value):
    if len(value) != 3: raise ValueError('three coordinates required')
    return tuple(scalar(v) for v in value)


def add(a,b): return tuple(x+y for x,y in zip(a,b))
def sub(a,b): return tuple(x-y for x,y in zip(a,b))
def scale(a,s): return tuple(x*s for x in a)
def dot(a,b): return sum(x*y for x,y in zip(a,b))
def cross(a,b):
    return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])


def unit(a):
    norm = math.hypot(*a)
    if not math.isfinite(norm) or norm <= 0: raise ValueError('nonzero finite direction required')
    return scale(a,1/norm)


def triangle_hit(origin,direction,triangle,epsilon):
    """Moller-Trumbore, both faces; no external raycast implementation."""
    a,b,c = triangle
    e1,e2 = sub(b,a),sub(c,a)
    h = cross(direction,e2); det = dot(e1,h)
    if abs(det) <= 1e-14: return None
    rel = sub(origin,a); u = dot(rel,h)/det
    q = cross(rel,e1); v = dot(direction,q)/det
    if u < -1e-10 or v < -1e-10 or u+v > 1+1e-10: return None
    distance = dot(e2,q)/det
    if distance <= epsilon: return None
    return distance, unit(cross(e1,e2))


def geometry(snapshot):
    if snapshot['schema'] not in ('exp005-readback-v1','exp005-readback-v2'): raise ValueError('unsupported readback schema')
    if snapshot['undeclared_meshes']:
        raise ValueError('unaccounted meshes: cannot assume non-interaction')
    wavelength = scalar(snapshot['lambda_BU'])
    if wavelength <= 0: raise ValueError('positive wavelength required')
    if not snapshot['objects']: raise ValueError('nonempty geometry required')
    objects = {}
    for name,record in snapshot['objects'].items():
        kind = record['kind']
        if kind not in ('bs','mirror','det','escape'): raise ValueError('unknown optical role')
        vertices = [vec(v) for v in record['vertices_world_BU']]
        triangles = []
        for face in record['faces']:
            if (len(face)!=3 or len(set(face))!=3 or any(isinstance(i,bool) or
                    not isinstance(i,int) or i<0 or i>=len(vertices) for i in face)):
                raise ValueError('oracle requires valid pre-triangulated faces')
            triangle = tuple(vertices[i] for i in face)
            unit(cross(sub(triangle[1],triangle[0]),sub(triangle[2],triangle[0])))
            triangles.append(triangle)
        if not triangles: raise ValueError('nonempty triangular mesh required')
        obj = {'kind':kind,'triangles':triangles}
        if kind=='bs':
            if snapshot['schema']=='exp005-readback-v2':
                tau=scalar(record['power_transmittance'])
                if not 0<=tau<=1: raise ValueError('splitter transmittance must be between0and1')
                obj['tau']=tau
            else:
                if 'power_transmittance' in record: raise ValueError('variable splitter requires readback-v2')
                obj['tau']=.5
        if kind == 'mirror': obj['phase'] = scalar(record['phase_rad'])
        if kind in ('det','escape'):
            obj['reference'] = vec(record['mode_origin_BU'])
            obj['axis'] = unit(vec(record['mode_direction']))
            tri = triangles[0]
            plane_normal = unit(cross(sub(tri[1],tri[0]),sub(tri[2],tri[0])))
            if abs(dot(plane_normal,obj['axis']))<1e-8:
                raise ValueError('terminal mode grazes its readout plane')
            if any(abs(dot(sub(v,obj['reference']),plane_normal))>1e-7 for v in vertices):
                raise ValueError('terminal mode must have a planar phase-reference surface')
        objects[name] = obj
    return wavelength,objects


def trace_scene(snapshot, *, max_rays=4096, max_depth=64):
    """Find paths, then sum amp*exp(ik*TOTAL_LENGTH) in a common output frame.

    Lost rays, ambiguous surfaces and angle-mismatched terminal modes abort.
    No renormalization, discarded escapes, detector-only path shortcuts or
    hidden matrix weights. Bounds are explicit to prevent accidental large loads.
    """
    wavelength,objects = geometry(snapshot)
    fields = {n:0j for n,o in objects.items() if o['kind'] in ('det','escape')}
    paths = []; casts = 0; names = set(); source_power = 0.0
    for source in snapshot['sources']:
        sid = source['id']
        if not isinstance(sid,str) or not sid or sid in names: raise ValueError('unique source IDs required')
        names.add(sid)
        pair = source['field_reim']
        if len(pair)!=2: raise ValueError('explicit real/imag source field required')
        initial = complex(scalar(pair[0]),scalar(pair[1]))
        source_power += abs(initial)**2
        position,direction = vec(source['position_BU']),unit(vec(source['direction']))
        if initial == 0: continue
        stack = [(position,direction,initial,0.0,[])]
        while stack:
            origin,direction,amplitude,length,history = stack.pop()
            casts += 1
            if casts>max_rays or len(history)>=max_depth: raise ValueError('oracle resource/path bound exceeded')
            hits = []
            for name,obj in objects.items():
                for triangle in obj['triangles']:
                    hit = triangle_hit(origin,direction,triangle,1e-9)
                    if hit is not None: hits.append((hit[0],name,hit[1]))
            if not hits: raise ValueError('lost ray: no declared detector/escape boundary')
            distance,name,normal = min(hits,key=lambda h:h[0])
            near = [h for h in hits if abs(h[0]-distance)<1e-9]
            if any(h[1]!=name or abs(dot(h[2],normal))<1-1e-9 for h in near):
                raise ValueError('ambiguous coincident/edge surfaces')
            point = add(origin,scale(direction,distance)); length2 = length+distance
            obj = objects[name]; kind = obj['kind']
            if kind in ('det','escape'):
                if dot(direction,obj['axis'])<1-1e-9:
                    raise ValueError('different arrival direction: not one common coherent mode')
                offset = dot(direction,sub(obj['reference'],point))
                field = amplitude*cmath.exp(2j*math.pi*(length2+offset)/wavelength)
                fields[name] += field
                paths.append({'source_id':sid,'terminal':name,'length_BU':length2,
                              'reference_offset_BU':offset,'field':field,
                              'hits':history+[{'object_id':name,'event':'detect' if kind=='det' else 'escape',
                                              'distance_BU':distance,'coefficient':1+0j}]})
                continue
            reflected = unit(sub(direction,scale(normal,2*dot(direction,normal))))
            branches = [('mirror',reflected,-cmath.exp(1j*obj['phase']))] if kind=='mirror' else [
                ('t',direction,math.sqrt(obj['tau'])),('r',reflected,1j*math.sqrt(1-obj['tau']))]
            for event,ray,coefficient in branches:
                stack.append((point,ray,amplitude*coefficient,length2,history+[
                    {'object_id':name,'event':event,'distance_BU':distance,'coefficient':coefficient}]))
    if not names: raise ValueError('scene-owned sources required')
    powers = {n:abs(f)**2 for n,f in fields.items()}
    return {'fields':fields,'powers':powers,'paths':paths,'rays':casts,
            'input_power':source_power,'output_power':sum(powers.values())}
