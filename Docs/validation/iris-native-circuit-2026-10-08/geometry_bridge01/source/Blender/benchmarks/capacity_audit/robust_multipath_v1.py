"""Complete CPU scalar-optics propagation, exact represented geometry.

No Blender/GPU/learned matrices; no epsilon, ray bias or heuristic pruning.
Fields are estimates; exact symbolic path definitions support error certification.
Historical EXP-005 engines remain unchanged. This is not Maxwell/physical optics.
"""
from fractions import Fraction as F
import cmath
import math


def rational(value):
    if isinstance(value, bool) or not isinstance(value, (int, float, F)):
        raise ValueError('finite represented real required')
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError('finite represented real required')
    return F(value)


def vector(value):
    if len(value) != 3:
        raise ValueError('three coordinates required')
    return tuple(rational(v) for v in value)


def add(a, b): return tuple(x+y for x, y in zip(a, b))
def sub(a, b): return tuple(x-y for x, y in zip(a, b))
def scale(a, s): return tuple(x*s for x in a)
def dot(a, b): return sum((x*y for x, y in zip(a, b)), F(0))
def cross(a, b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
def parallel(a, b): return cross(a, b) == (0, 0, 0)


def reflected(direction, normal):
    return sub(direction, scale(normal, 2*dot(direction, normal)/dot(normal, normal)))


def coplanar_interval(origin, direction, vertices, normal):
    """Exact half-plane clipping of a coplanar ray against a finite triangle."""
    lower, upper = F(0), None
    for i in range(3):
        vertex, edge = vertices[i], sub(vertices[(i+1) % 3], vertices[i])
        a = dot(cross(edge, sub(origin, vertex)), normal)
        b = dot(cross(edge, direction), normal)
        if b == 0:
            if a < 0: return None
        elif b > 0:
            lower = max(lower, -a/b)
        else:
            bound = -a/b
            upper = bound if upper is None else min(upper, bound)
        if upper is not None and lower > upper: return None
    return lower, upper


def intersection(origin, direction, triangle):
    a, b, c = triangle['vertices']
    e1, e2 = sub(b, a), sub(c, a)
    n = cross(e1, e2)
    if n == (0, 0, 0): return dict(triangle, kind='degenerate')
    p, rel = cross(direction, e2), sub(origin, a)
    determinant = dot(e1, p)
    if determinant == 0:
        if dot(rel, n) != 0: return None
        interval = coplanar_interval(origin, direction, (a, b, c), n)
        if interval is None: return None
        return dict(triangle, kind='coplanar', t=interval[0], interval=interval, normal=n)
    q = cross(rel, e1)
    u, v, t = dot(rel, p)/determinant, dot(direction, q)/determinant, dot(e2, q)/determinant
    if t < 0 or u < 0 or v < 0 or u+v > 1: return None
    return dict(triangle, kind='contact' if t == 0 else 'boundary' if 0 in (u, v, 1-u-v) else 'interior',
                t=t, normal=n, barycentric=(1-u-v, u, v))


def internal_seam(rows, point):
    """Certify local full surface coverage across one shared interior mesh edge."""
    for i, first in enumerate(rows):
        for second in rows[i+1:]:
            shared = set(first['vertices']) & set(second['vertices'])
            if len(shared) != 2: continue
            a, b = sorted(shared)
            edge = sub(b, a)
            # Open edge only: vertices require a complete fan certificate.
            if not parallel(sub(point, a), edge): continue
            parameter = dot(sub(point, a), edge)/dot(edge, edge)
            if not 0 < parameter < 1: continue
            va = next(v for v in first['vertices'] if v not in shared)
            vb = next(v for v in second['vertices'] if v not in shared)
            side_a, side_b = cross(edge, sub(va, a)), cross(edge, sub(vb, a))
            if dot(side_a, side_b) < 0: return True
    return False


def select(origin, direction, triangles, previous=None):
    if direction == (0, 0, 0): raise ValueError('nonzero direction required')
    candidates, excluded = [], []
    for triangle in triangles:
        row = intersection(origin, direction, triangle)
        if row is None: continue
        if row['kind'] == 'degenerate':
            return {'status': 'INVALID_GEOMETRY', 'candidates': [row], 'excluded': excluded}
        # Exclusion needs an actual contact on the previous optical plane.
        if (row['kind'] == 'contact' and previous is not None and
                row['object_id'] == previous['object_id'] and parallel(row['normal'], previous['normal']) and
                dot(sub(row['vertices'][0], previous['vertices'][0]), previous['normal']) == 0):
            excluded.append(row['primitive_id']); continue
        candidates.append(row)
    if not candidates: return {'status': 'MISS', 'candidates': [], 'excluded': excluded}
    nearest = min(row['t'] for row in candidates)
    rows = [row for row in candidates if row['t'] == nearest]
    result = {'candidates': rows, 'excluded': excluded, 't': nearest}
    if nearest == 0:
        return dict(result, status='COPLANAR' if any(r['kind'] == 'coplanar' for r in rows) else 'CONTACT')
    if any(row['kind'] == 'coplanar' for row in rows): return dict(result, status='COPLANAR')
    first = rows[0]
    if any(row['object_id'] != first['object_id'] or not parallel(row['normal'], first['normal']) for row in rows):
        return dict(result, status='TRUE_TIE')
    point = add(origin, scale(direction, nearest))
    if not any(row['kind'] == 'interior' for row in rows) and not internal_seam(rows, point):
        return dict(result, status='BOUNDARY')
    return dict(result, status='SELECT', selected=first, point=point)


def geometry(snapshot):
    if snapshot['schema'] not in ('exp005-readback-v1', 'exp005-readback-v2') or snapshot['undeclared_meshes']:
        raise ValueError('complete declared scene required')
    wavelength = rational(snapshot['lambda_BU'])
    if wavelength <= 0 or not snapshot['objects']: raise ValueError('positive wavelength/nonempty scene required')
    objects, triangles = {}, []
    for name, record in snapshot['objects'].items():
        if not isinstance(name, str) or not name: raise ValueError('object identity required')
        role = record['kind']
        if role not in ('mirror', 'bs', 'det', 'escape'): raise ValueError('unknown optical role')
        vertices = [vector(v) for v in record['vertices_world_BU']]
        local = []
        for face in record['faces']:
            if len(face) != 3 or len(set(face)) != 3 or any(type(i) is not int or not 0 <= i < len(vertices) for i in face):
                raise ValueError('valid pre-triangulated faces required')
            tri = {'object_id': name, 'primitive_id': len(triangles), 'vertices': tuple(vertices[i] for i in face)}
            n = cross(sub(tri['vertices'][1], tri['vertices'][0]), sub(tri['vertices'][2], tri['vertices'][0]))
            if n == (0, 0, 0): raise ValueError('degenerate triangle')
            local.append(tri); triangles.append(tri)
        if not local: raise ValueError('nonempty mesh required')
        obj = {'kind': role}
        if role == 'bs':
            if snapshot['schema'].endswith('v1') and 'power_transmittance' in record:
                raise ValueError('variable splitter requires v2')
            obj['tau'] = rational(record['power_transmittance'] if snapshot['schema'].endswith('v2') else .5)
            if not 0 <= obj['tau'] <= 1: raise ValueError('invalid transmission')
        if role == 'mirror': obj['phase'] = rational(record['phase_rad'])
        if role in ('det', 'escape'):
            obj['reference'], obj['axis'] = vector(record['mode_origin_BU']), vector(record['mode_direction'])
            n = cross(sub(local[0]['vertices'][1], local[0]['vertices'][0]), sub(local[0]['vertices'][2], local[0]['vertices'][0]))
            if dot(n, obj['axis']) == 0: raise ValueError('grazing/zero terminal mode')
            if any(dot(sub(v, obj['reference']), n) != 0 for v in vertices):
                raise ValueError('exact planar terminal reference required')
        objects[name] = obj
    return wavelength, objects, triangles


def estimate_path_field(path, wavelength):
    source = complex(*(float(v) for v in path['source_reim']))
    phase = (2*math.pi*float(path['phase_length_numerator']) /
             (float(wavelength)*math.sqrt(float(path['direction_norm_squared']))) +
             float(path['mirror_phase']) + path['quarter_turns']*math.pi/2)
    return source*math.sqrt(float(path['power_factor']))*cmath.exp(1j*phase)


def trace_scene(snapshot, *, max_rays=4096, max_depth=64):
    """Enumerate all nonzero branches, preserving exact path provenance.

    COMPLETE certifies finite traversal/topology only. It does not certify float
    fields; point 4 supplies outward error intervals. INCOMPLETE has fields=None.
    """
    if type(max_rays) is not int or max_rays < 1 or type(max_depth) is not int or max_depth < 1:
        raise ValueError('positive resource bounds required')
    wavelength, objects, triangles = geometry(snapshot)
    ports = [n for n, o in objects.items() if o['kind'] in ('det', 'escape')]
    if not ports: raise ValueError('declared terminal required')
    paths, unresolved, stack, names = [], [], [], set()
    input_power, zero_branches, casts, departure_exclusions = F(0), 0, 0, 0
    for source in snapshot['sources']:
        sid = source['id']
        if not isinstance(sid, str) or not sid or sid in names: raise ValueError('unique source IDs required')
        names.add(sid)
        if len(source['field_reim']) != 2: raise ValueError('explicit real/imag source required')
        amplitude = tuple(rational(v) for v in source['field_reim'])
        origin, direction = vector(source['position_BU']), vector(source['direction'])
        norm2 = dot(direction, direction)
        if norm2 == 0: raise ValueError('nonzero source direction required')
        input_power += sum(v*v for v in amplitude)
        if amplitude == (0, 0): zero_branches += 1; continue
        stack.append({'source_id': sid, 'source_reim': amplitude, 'origin': origin, 'direction': direction,
                      'norm2': norm2, 'parameter_length': F(0), 'power_factor': F(1), 'mirror_phase': F(0),
                      'quarter_turns': 0, 'history': [], 'previous': None})
    if not names: raise ValueError('scene-owned sources required')
    while stack:
        ray = stack.pop()
        if casts >= max_rays:
            unresolved.append({'status': 'RESOURCE_LIMIT', 'ray': ray, 'pending': stack.copy()}); break
        if len(ray['history']) >= max_depth:
            unresolved.append({'status': 'RESOURCE_LIMIT', 'ray': ray}); continue
        casts += 1
        hit = select(ray['origin'], ray['direction'], triangles, ray['previous'])
        departure_exclusions += len(hit['excluded'])
        if hit['status'] != 'SELECT':
            unresolved.append({'status': hit['status'], 'ray': ray, 'selection': hit}); continue
        selected, parameter = hit['selected'], hit['t']
        name, normal = selected['object_id'], selected['normal']
        obj = objects[name]
        length = ray['parameter_length'] + parameter
        history = ray['history'] + [{'object_id': name, 'primitive_id': selected['primitive_id'],
                    'coincident_primitives': [r['primitive_id'] for r in hit['candidates']],
                    'parameter': parameter, 'point': hit['point'], 'direction': ray['direction']}]
        if obj['kind'] in ('det', 'escape'):
            if not parallel(ray['direction'], obj['axis']) or dot(ray['direction'], obj['axis']) <= 0:
                unresolved.append({'status': 'MODE_MISMATCH', 'ray': ray, 'selection': hit}); continue
            numerator = ray['norm2']*length + dot(ray['direction'], sub(obj['reference'], hit['point']))
            path = {'source_id': ray['source_id'], 'terminal': name, 'source_reim': ray['source_reim'],
                    'direction_norm_squared': ray['norm2'], 'parameter_length': length,
                    'phase_length_numerator': numerator, 'power_factor': ray['power_factor'],
                    'mirror_phase': ray['mirror_phase'], 'quarter_turns': ray['quarter_turns'],
                    'hits': history}
            history[-1]['event'] = obj['kind']
            paths.append(path); continue
        direction_r = reflected(ray['direction'], normal)
        if dot(direction_r, direction_r) != ray['norm2']: raise ArithmeticError('reflection norm invariant')
        branches = ([('mirror', direction_r, F(1), 2, obj['phase'])] if obj['kind'] == 'mirror' else
                    [('t', ray['direction'], obj['tau'], 0, F(0)), ('r', direction_r, 1-obj['tau'], 1, F(0))])
        for event, direction, power, turn, phase in branches:
            if power == 0: zero_branches += 1; continue
            branch_history = [*history[:-1], dict(history[-1], event=event, coefficient_power=power)]
            stack.append(dict(ray, origin=hit['point'], direction=direction, parameter_length=length,
                              power_factor=ray['power_factor']*power, mirror_phase=ray['mirror_phase']+phase,
                              quarter_turns=(ray['quarter_turns']+turn) % 4, history=branch_history, previous=selected))
    fields = None
    if not unresolved:
        contributions = {n: [] for n in ports}
        for path in paths: contributions[path['terminal']].append(estimate_path_field(path, wavelength))
        fields = {n: complex(math.fsum(v.real for v in a), math.fsum(v.imag for v in a)) for n, a in contributions.items()}
    return {'schema': 'neuro3d-exact-multipath-v1', 'backend': 'CPU_FRACTION',
            'status': 'INCOMPLETE' if unresolved else 'COMPLETE', 'fields': fields,
            'powers': None if fields is None else {n: abs(v)**2 for n, v in fields.items()},
            'paths': paths, 'unresolved': unresolved, 'rays': casts, 'input_power_exact': input_power,
            'input_power': float(input_power), 'output_power': None if fields is None else sum(abs(v)**2 for v in fields.values()),
            'exact_zero_branches': zero_branches, 'departure_exclusions': departure_exclusions,
            'wavelength': wavelength, 'ports': ports, 'field_certified': False}
