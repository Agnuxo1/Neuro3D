"""Exact selector controls for local triangle unions; no optical fields run."""
from fractions import Fraction as F
import unittest

from Blender.benchmarks.capacity_audit.robust_multipath_v1 import select, vector


def fan(directions):
    triangles = []
    center = (F(0), F(0), F(0))
    for i, a in enumerate(directions):
        b = directions[(i+1) % len(directions)]
        triangles.append({'object_id': 'surface', 'primitive_id': i,
                          'vertices': (center, vector((*a, 0)), vector((*b, 0)))})
    return triangles


def hit(triangles, point=(0, 0, 0)):
    return select(vector((point[0], point[1], 1)), vector((0, 0, -1)), triangles)


class SurfaceUnionTests(unittest.TestCase):
    def test_complete_fan_center_is_interior(self):
        self.assertEqual(hit(fan([(1, 0), (0, 1), (-1, 0), (0, -1)]))['status'], 'SELECT')

    def test_missing_sector_remains_boundary(self):
        triangles = fan([(1, 0), (0, 1), (-1, 0), (0, -1)])
        self.assertEqual(hit(triangles[:-1])['status'], 'BOUNDARY')

    def test_arbitrarily_small_open_sector_retained(self):
        directions = [(1, 0), (1, F(1, 2**100)), (0, 1), (-1, 0), (0, -1)]
        triangles = fan(directions)
        self.assertEqual(hit(triangles)['status'], 'SELECT')
        self.assertEqual(hit(triangles[1:])['status'], 'BOUNDARY')

    def test_outer_polygon_vertex_and_edge_remain_boundary(self):
        triangles = fan([(1, 0), (0, 1), (-1, 0), (0, -1)])
        self.assertEqual(hit(triangles, (1, 0, 0))['status'], 'BOUNDARY')
        self.assertEqual(hit(triangles, (F(1, 2), F(1, 2), 0))['status'], 'BOUNDARY')

    def test_opposite_triangle_winding_preserves_union(self):
        triangles = fan([(1, 0), (0, 1), (-1, 0), (0, -1)])
        for row in triangles[::2]: row['vertices'] = tuple(reversed(row['vertices']))
        self.assertEqual(hit(triangles)['status'], 'SELECT')

    def test_distinct_objects_remain_true_tie(self):
        triangles = fan([(1, 0), (0, 1), (-1, 0), (0, -1)])
        triangles[-1]['object_id'] = 'different'
        self.assertEqual(hit(triangles)['status'], 'TRUE_TIE')

    def test_nonconforming_t_junction_interior(self):
        # Upper half-triangle meets two lower triangles at an edge midpoint.
        triangles = [{'object_id':'surface','primitive_id':0,
                      'vertices':vector_list([(-1,0,0),(1,0,0),(0,1,0)])},
                     {'object_id':'surface','primitive_id':1,
                      'vertices':vector_list([(0,0,0),(-1,0,0),(0,-1,0)])},
                     {'object_id':'surface','primitive_id':2,
                      'vertices':vector_list([(0,0,0),(0,-1,0),(1,0,0)])}]
        self.assertEqual(hit(triangles)['status'],'SELECT')

    def test_nearby_detached_triangle_does_not_fill_gap(self):
        triangles = fan([(1, 0), (0, 1), (-1, 0), (0, -1)])[:-1]
        triangles.append({'object_id':'surface','primitive_id':9,
                          'vertices':vector_list([(1,-1,0),(2,-1,0),(2,0,0)])})
        self.assertEqual(hit(triangles)['status'],'BOUNDARY')


def vector_list(values):
    return tuple(vector(value) for value in values)


if __name__ == '__main__':
    unittest.main()
