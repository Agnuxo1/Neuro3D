"""Exact broad-phase parity against exhaustive selection, not a physics oracle."""
import copy
from fractions import Fraction as F
import random
import unittest

from Blender.benchmarks.capacity_audit import robust_multipath_v1 as base
from Blender.benchmarks.capacity_audit.exact_object_index_v1 import ExactObjectIndex, ray_box_interval, trace_scene_indexed


def plane_x(x, role='det', axis=(1,0,0), **extra):
    row={'kind':role,'vertices_world_BU':[(x,-4,-4),(x,4,-4),(x,0,5)],'faces':[(0,1,2)]}
    if role in ('det','escape'):
        row.update(mode_origin_BU=(x,0,0),mode_direction=axis)
    if role=='mirror':
        row['phase_rad']=0
    if role=='bs':
        row['power_transmittance']=F(1,2)
    row.update(extra)
    return row


def scene(objects, origin=(0,0,0), direction=(1,0,0)):
    return {'schema':'exp005-readback-v2','lambda_BU':F(1,8),'objects':objects,'undeclared_meshes':[],
            'sources':[{'id':'input','position_BU':origin,'direction':direction,'field_reim':[1,0]}]}


class ExactIndexTests(unittest.TestCase):
    def test_closed_tangent_and_zero_axis_and_reverse(self):
        self.assertEqual(ray_box_interval((0,0,0),(1,0,0),(1,0,0),(1,1,1)), (1,1))
        self.assertIsNone(ray_box_interval((0,-1,0),(1,0,0),(1,0,0),(2,1,1)))
        self.assertEqual(ray_box_interval((3,0,0),(-1,0,0),(1,0,0),(2,1,1)), (1,2))
        self.assertIsNone(ray_box_interval((3,0,0),(1,0,0),(1,0,0),(2,1,1)))

    def test_arbitrarily_small_positive_gap(self):
        gap = F(1,2**120)
        self.assertEqual(ray_box_interval((1,0,0),(1,0,0),(1+gap,-1,-1),(1+gap,1,1)), (gap,gap))

    def test_invalid_box_and_zero_ray_rejected(self):
        with self.assertRaises(ValueError):
            ray_box_interval((0,0,0),(0,0,0),(1,0,0),(2,1,1))
        with self.assertRaises(ValueError):
            ray_box_interval((0,0,0),(1,0,0),(2,0,0),(1,1,1))

    def test_random_exact_queries_and_same_hit_order(self):
        rng = random.Random(1940)
        objects = {str(i):plane_x(F(i,4)) for i in range(-8,9)}
        _, _, triangles = base.geometry(scene(objects))
        index = ExactObjectIndex(triangles)
        for _ in range(160):
            origin = tuple(F(rng.randrange(-16,17),8) for _ in range(3))
            direction = tuple(F(rng.randrange(-4,5),4) for _ in range(3))
            if direction == (0,0,0):
                continue
            self.assertEqual(index(origin,direction,triangles), base.select(origin,direction,triangles))
        self.assertLess(index.stats['triangles_submitted'], index.stats['exhaustive_triangle_opportunities'])

    def test_contacts_ties_boundaries_coplanar_and_miss(self):
        fixtures = [scene({'contact':plane_x(0,'mirror'), 'out':plane_x(2)}),
                    scene({'a':plane_x(1), 'b':plane_x(1)}),
                    scene({'out':plane_x(1)},origin=(0,0,-4)),
                    scene({'out':plane_x(1)},origin=(1,0,0),direction=(0,1,0)),
                    scene({'out':plane_x(1)},direction=(-1,0,0))]
        for snapshot in fixtures:
            _,_,triangles=base.geometry(snapshot)
            src=snapshot['sources'][0]
            origin,direction=base.vector(src['position_BU']),base.vector(src['direction'])
            self.assertEqual(ExactObjectIndex(triangles)(origin,direction,triangles),base.select(origin,direction,triangles))

    def test_departure_exclusion_and_positive_return(self):
        snapshot=scene({'left':plane_x(0,'mirror'),'right':plane_x(1,'mirror'),'out':plane_x(2)},origin=(F(1,2),0,0))
        indexed=trace_scene_indexed(snapshot,max_depth=7)
        for key,value in base.trace_scene(snapshot,max_depth=7).items():
            self.assertEqual(indexed[key],value)
        self.assertEqual(indexed['unresolved'][0]['ray']['history'][2]['parameter'],1)

    def test_all_nonzero_splitter_branches_and_exact_zero(self):
        for tau in (0,F(1,2),1):
            snapshot=scene({'bs':plane_x(1,'bs',power_transmittance=tau),'out':plane_x(2),
                            'escape':plane_x(-1,'escape',axis=(-1,0,0))})
            indexed=trace_scene_indexed(snapshot)
            for key,value in base.trace_scene(snapshot).items():
                self.assertEqual(indexed[key],value)

    def test_wrong_geometry_and_degenerate_rejected(self):
        _,_,triangles=base.geometry(scene({'out':plane_x(1)}))
        index=ExactObjectIndex(triangles)
        with self.assertRaisesRegex(ValueError,'identity'):
            index((0,0,0),(1,0,0),copy.deepcopy(triangles))
        triangles[0]['vertices']=((1,0,0),)*3
        with self.assertRaisesRegex(ValueError,'nondegenerate'):
            ExactObjectIndex(triangles)


if __name__=='__main__':
    unittest.main()
