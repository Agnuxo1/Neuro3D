"""Conservative pre-dispatch checks, not physical modal orthogonality proof.

No oracle/Blender/GPU imports and no field propagation. Reads real terminal hit
positions/directions; names alone cannot establish independent optical channels.
"""
import math
from numbers import Real

POSITION_TOL_BU = 1e-6
DIRECTION_TOL = 1e-6


def number(value):
    if isinstance(value, bool) or not isinstance(value, Real) or not math.isfinite(value):
        raise ValueError('finite mode coordinate required')
    return float(value)


def vector(value):
    if len(value) != 3:
        raise ValueError('three mode coordinates required')
    return tuple(number(v) for v in value)


def dot(a, b): return sum(x*y for x, y in zip(a, b))
def sub(a, b): return tuple(x-y for x, y in zip(a, b))
def cross(a, b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def unit(value):
    v = vector(value); length = math.hypot(*v)
    if not math.isfinite(length) or length <= 0:
        raise ValueError('nonzero finite mode direction required')
    return tuple(x/length for x in v)


def mode_geometry(snapshot):
    sources = snapshot['sources']
    if not 1 <= len(sources) <= 8:
        raise ValueError('one to eight declared source modes required')
    declared = {}
    for source in sources:
        name = source['id']
        if not isinstance(name, str) or not name or name in declared:
            raise ValueError('unique source IDs required')
        position, direction = vector(source['position_BU']), unit(source['direction'])
        for p, d in declared.values():
            # Same oriented infinite ray line, even different longitudinal origins.
            if dot(direction, d) >= 1-DIRECTION_TOL and math.hypot(*cross(sub(position, p), d)) <= POSITION_TOL_BU:
                raise ValueError('co-propagating collinear source aliases are not independent modes')
        declared[name] = position, direction
    terminals = {}
    for name, obj in snapshot['objects'].items():
        if obj['kind'] not in ('det', 'escape'):
            continue
        origin, axis = vector(obj['mode_origin_BU']), unit(obj['mode_direction'])
        vertices = [vector(v) for v in obj['vertices_world_BU']]
        faces = obj['faces']
        if not vertices or not faces:
            raise ValueError('nonempty terminal surface required')
        normal = None
        for face in faces:
            if (len(face) != 3 or len(set(face)) != 3 or any(isinstance(i, bool) or
                    not isinstance(i, int) or not 0 <= i < len(vertices) for i in face)):
                raise ValueError('triangulated terminal surface required')
            a, b, c = (vertices[i] for i in face)
            n = unit(cross(sub(b, a), sub(c, a)))
            if normal is not None and abs(dot(n, normal)) < 1-DIRECTION_TOL:
                raise ValueError('one planar terminal mode required')
            normal = n
        if abs(dot(normal, axis)) < DIRECTION_TOL:
            raise ValueError('terminal mode grazes its reference plane')
        if any(abs(dot(sub(v, origin), normal)) > POSITION_TOL_BU for v in vertices):
            raise ValueError('terminal reference outside planar readout surface')
        bounds = tuple((min(v[i] for v in vertices), max(v[i] for v in vertices)) for i in range(3))
        for other in terminals.values():
            if (dot(axis, other['axis']) >= 1-DIRECTION_TOL and
                    abs(dot(normal, other['normal'])) >= 1-DIRECTION_TOL and
                    abs(dot(sub(origin, other['origin']), normal)) <= POSITION_TOL_BU and
                    all(a <= d+POSITION_TOL_BU and c <= b+POSITION_TOL_BU
                        for (a,b),(c,d) in zip(bounds, other['bounds']))):
                raise ValueError('overlapping output apertures cannot be declared independent modes')
        terminals[name] = dict(origin=origin, axis=axis, normal=normal, bounds=bounds, kind=obj['kind'])
    if not terminals:
        raise ValueError('declared terminal modes required')
    return declared, terminals


def validate_native_modes(snapshot, paths):
    sources, terminals = mode_geometry(snapshot)
    if not 1 <= len(paths) <= 512:
        raise ValueError('bounded real path set required')
    worst_offset = 0.
    for path in paths:
        if path['source_id'] not in sources or not 1 <= len(path['hits']) <= 64:
            raise ValueError('complete source-owned hit history required')
        hit = path['hits'][-1]
        if hit['object_id'] not in terminals:
            raise ValueError('explicit declared terminal required')
        terminal = terminals[hit['object_id']]
        if hit['event'] != ('detect' if terminal['kind'] == 'det' else 'escape'):
            raise ValueError('terminal event/role mismatch')
        point, direction = vector(hit['point_BU']), unit(hit['incoming_direction'])
        if dot(direction, terminal['axis']) < 1-DIRECTION_TOL:
            raise ValueError('different arrival direction: not one common terminal mode')
        if abs(dot(sub(point, terminal['origin']), terminal['normal'])) > POSITION_TOL_BU:
            raise ValueError('terminal hit outside reference plane')
        if any(not a-POSITION_TOL_BU <= p <= b+POSITION_TOL_BU
               for p,(a,b) in zip(point, terminal['bounds'])):
            raise ValueError('terminal hit outside aperture bounds')
        offset = number(path['reference_offset_BU'])  # No silent zero fallback.
        error = abs(offset-dot(direction, sub(terminal['origin'], point)))
        worst_offset = max(worst_offset, error)
        if error > POSITION_TOL_BU:
            raise ValueError('terminal reference offset differs from measured hit')
    return {'sources': len(sources), 'terminals': len(terminals), 'paths': len(paths),
            'worst_reference_offset_error_BU': worst_offset, 'geometry_gate_passed': False,
            'scope': 'conservative point-ray mode exclusions, not physical orthogonality'}
