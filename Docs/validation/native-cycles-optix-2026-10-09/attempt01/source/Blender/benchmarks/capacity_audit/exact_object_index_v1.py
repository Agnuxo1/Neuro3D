"""Conservative exact broad phase; never approximate a hit or prune amplitudes.

Axis-aligned boxes are a standard spatial technique, not a novelty claim. Every
represented triangle is contained in its closed box. A forward ray hitting it
must intersect that box at t>=0. Rational slab tests retain closed contacts,
coplanarity, arbitrarily small gaps and all nearest ties. The existing exact
triangle selector makes the final decision in original primitive order.
"""
from fractions import Fraction as F

from . import robust_multipath_v1 as base


def ray_box_interval(origin, direction, lower, upper):
    """Return the closed forward slab interval, or None (exact rationals)."""
    origin, direction, lower, upper = (base.vector(v) for v in (origin, direction, lower, upper))
    if direction == (0, 0, 0) or any(a > b for a,b in zip(lower,upper)):
        raise ValueError('nonzero ray and ordered closed box required')
    lo, hi = F(0), None
    for o, d, a, b in zip(origin, direction, lower, upper):
        if d == 0:
            if not a <= o <= b:
                return None
            continue
        first, last = (a-o)/d, (b-o)/d
        if first > last:
            first, last = last, first
        lo = max(lo, first)
        hi = last if hi is None else min(hi, last)
        if lo > hi:
            return None
    return lo, hi


class ExactObjectIndex:
    def __init__(self, triangles):
        self.original = triangles
        grouped = {}
        for ordinal, tri in enumerate(triangles):
            a, b, c = tri['vertices']
            if base.cross(base.sub(b, a), base.sub(c, a)) == (0, 0, 0):
                raise ValueError('index requires validated nondegenerate triangles')
            grouped.setdefault(tri['object_id'], []).append((ordinal, tri))
        self.groups = []
        for rows in grouped.values():
            vertices = [v for _, tri in rows for v in tri['vertices']]
            lower = tuple(min(v[k] for v in vertices) for k in range(3))
            upper = tuple(max(v[k] for v in vertices) for k in range(3))
            self.groups.append((lower, upper, rows))
        self.stats = {'queries': 0, 'object_boxes_tested': 0,
                      'triangles_submitted': 0, 'exhaustive_triangle_opportunities': 0}

    def __call__(self, origin, direction, triangles, previous=None):
        if triangles is not self.original:
            raise ValueError('index/geometry identity mismatch')
        if direction == (0, 0, 0):
            raise ValueError('nonzero direction required')
        candidates = []
        for lower, upper, rows in self.groups:
            if ray_box_interval(origin, direction, lower, upper) is not None:
                candidates.extend(rows)
        candidates.sort(key=lambda row: row[0])
        self.stats['queries'] += 1
        self.stats['object_boxes_tested'] += len(self.groups)
        self.stats['triangles_submitted'] += len(candidates)
        self.stats['exhaustive_triangle_opportunities'] += len(triangles)
        return base.select(origin, direction, [tri for _, tri in candidates], previous)


def trace_scene_indexed(snapshot, *, max_rays=4096, max_depth=64):
    indices = []
    def factory(triangles):
        index = ExactObjectIndex(triangles)
        indices.append(index)
        return index
    result = base.trace_scene(snapshot, max_rays=max_rays, max_depth=max_depth,
                              _selection_factory=factory)
    result['selection_backend'] = 'EXACT_OBJECT_AABB_CPU'
    result['selection_statistics'] = indices[0].stats
    result['selection_is_gpu'] = False
    return result
