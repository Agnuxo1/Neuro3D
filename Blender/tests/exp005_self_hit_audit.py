"""Own bounded CPU grazing-ray queries; no peer code, GPU or full-network claim."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import random
from exp005_triangle_oracle import add, sub, scale, unit, cross, dot, triangle_hit

SEED = 202609300800
TRIALS = 192
T_MIN_BU = 1e-9
PROFILES = ((1., 1e-4), (100., 1e-7), (1e4, 1e-5))


def fixture(rng, extent, grazing_angle):
    normal = unit(tuple(rng.gauss(0., 1.) for _ in range(3)))
    tangent = unit(cross(normal, tuple(rng.gauss(0., 1.) for _ in range(3))))
    other = cross(normal, tangent)
    center = scale(unit(tuple(rng.gauss(0., 1.) for _ in range(3))), extent)
    target = add(center, add(scale(tangent, rng.uniform(-.05, .05)),
                             scale(other, rng.uniform(-.05, .05))))
    direction = unit(sub(scale(tangent, math.cos(grazing_angle)),
                         scale(normal, math.sin(grazing_angle))))
    vertices = [add(center, scale(add(scale(tangent, a), scale(other, b)), .125))
                for a, b in ((-1., -1.), (1., -1.), (1., 1.), (-1., 1.))]
    return {'vertices': vertices, 'faces': ((0, 1, 2), (0, 2, 3)),
            'origin_BU': sub(target, scale(direction, 2.)), 'direction': direction}


def query(record, *, local=False):
    anchor = record['origin_BU'] if local else (0., 0., 0.)
    vertices = [sub(v, anchor) for v in record['vertices']]
    origin, direction = sub(record['origin_BU'], anchor), record['direction']
    triangles = [tuple(vertices[i] for i in face) for face in record['faces']]
    hits = []
    for index, triangle in enumerate(triangles):
        hit = triangle_hit(origin, direction, triangle, T_MIN_BU)
        if hit is not None: hits.append((hit[0], index, hit[1]))
    if not hits: return {'missed_initial': True}
    distance, index, normal = min(hits, key=lambda x:x[0])
    point = add(origin, scale(direction, distance))
    reflected = unit(sub(direction, scale(normal, 2*dot(direction, normal))))
    same = triangle_hit(point, reflected, triangles[index], T_MIN_BU)
    others = []
    for other_index, triangle in enumerate(triangles):
        if other_index == index: continue
        hit = triangle_hit(point, reflected, triangle, T_MIN_BU)
        if hit is not None: others.append({'triangle': other_index, 'distance_BU': hit[0]})
    return {'missed_initial': False, 'first_triangle': index,
            'first_distance_BU': distance, 'point_BU': point,
            'reflected_direction': reflected, 'anchor_BU': anchor,
            'same_triangle_self_hit_BU': None if same is None else same[0],
            # Other-face returns may be real for non-coplanar represented meshes.
            'other_triangle_hits_not_classified': others}


def audit():
    result = {'scope': 'CPU independent scalar triangle queries, NO GPU/Bpy/network',
              'seed': SEED, 'trials_per_profile': TRIALS, 't_min_BU': T_MIN_BU,
              'profiles': [], 'retained_same_triangle_adversaries': []}
    for profile, (extent, angle) in enumerate(PROFILES):
        rng = random.Random(SEED+profile)
        row = {'extent_BU': extent, 'grazing_angle_rad': angle, 'trials': TRIALS,
               'world_valid': 0, 'local_valid': 0, 'world_same_hits': 0, 'local_same_hits': 0}
        for trial in range(TRIALS):
            record = fixture(rng, extent, angle)
            world, local = query(record), query(record, local=True)
            for prefix, trace in (('world', world), ('local', local)):
                row[prefix+'_valid'] += not trace['missed_initial']
                row[prefix+'_same_hits'] += trace.get('same_triangle_self_hit_BU') is not None
            if (world.get('same_triangle_self_hit_BU') is not None and
                    len(result['retained_same_triangle_adversaries']) < 12):
                result['retained_same_triangle_adversaries'].append({
                    'profile': profile, 'trial': trial, 'record': record,
                    'world_query': world, 'local_query': local})
        result['profiles'].append(row)
    result['limitations'] = ('No previous-face exclusion implementation or certified planar-mesh domain; '
                            'other-face returns are not called numerical self-hits. '
                            'Local query uses translated float64 input, not GPU ABI/readback.')
    return result


def main():
    p = argparse.ArgumentParser(); p.add_argument('--output', type=Path, required=True); a = p.parse_args()
    if a.output.exists(): raise ValueError('new artifact required')
    result = audit()
    paths = (Path(__file__), Path(__file__).with_name('exp005_triangle_oracle.py'))
    result['code_sha256'] = {str(x): hashlib.sha256(x.read_bytes()).hexdigest() for x in paths}
    a.output.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps({'profiles': result['profiles'],
        'retained': len(result['retained_same_triangle_adversaries']),
        'sha256': hashlib.sha256(a.output.read_bytes()).hexdigest()}))


if __name__ == '__main__': main()
