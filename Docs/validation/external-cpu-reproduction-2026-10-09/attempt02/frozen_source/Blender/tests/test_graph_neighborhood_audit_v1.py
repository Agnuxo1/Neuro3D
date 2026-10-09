"""Independent neighborhood witness controls, including arbitrarily tiny holes."""
from fractions import Fraction as F
import unittest
from Tools.audit_graph_neighborhood_v1 import square_neighborhood,audit_graph_neighborhood
from Blender.tests.test_coherent_state_graph_v1 import run,scene_wire
from Blender.tests.test_exact_object_index_v1 import plane_x,scene
from Tools.trace_indexed_scene_v1 import wire


def triangles(directions):
    return [((0,0,0),(*a,0),(*directions[(i+1)%len(directions)],0)) for i,a in enumerate(directions)]


class NeighborhoodAuditTests(unittest.TestCase):
    def test_full_fan_reversed_faces_duplicates_and_overlap(self):
        faces=triangles([(1,0),(0,1),(-1,0),(0,-1)])
        for values in (faces,[tuple(reversed(f)) for f in faces],faces+faces):
            witness=square_neighborhood(values,(0,0,0),(0,0,1))
            self.assertTrue(witness['all_four_edges_covered'])
            self.assertGreater(F(*witness['projected_radius']),0)

    def test_tiny_missing_sector_is_not_hidden(self):
        faces=triangles([(1,0),(1,F(1,2**120)),(0,1),(-1,0),(0,-1)])
        self.assertIsNotNone(square_neighborhood(faces,(0,0,0),(0,0,1)))
        self.assertIsNone(square_neighborhood(faces[1:],(0,0,0),(0,0,1)))

    def test_one_sided_seam_and_outer_corner_rejected(self):
        self.assertIsNone(square_neighborhood([((-1,0,0),(1,0,0),(0,1,0))],(0,0,0),(0,0,1)))
        self.assertIsNone(square_neighborhood([((0,0,0),(1,0,0),(0,1,0))],(0,0,0),(0,0,1)))

    def test_nonconforming_tjunction_covers_whole_neighborhood(self):
        faces=[((-1,0,0),(1,0,0),(0,1,0)),((0,0,0),(-1,0,0),(0,-1,0)),((0,0,0),(0,-1,0),(1,0,0))]
        self.assertIsNotNone(square_neighborhood(faces,(0,0,0),(0,0,1)))

    def test_inactive_slack_selects_radius_below_tiny_geometry(self):
        tiny=F(1,2**150)
        faces=[((-tiny,-tiny,0),(tiny,-tiny,0),(0,tiny,0))]
        witness=square_neighborhood(faces,(0,0,0),(0,0,1))
        self.assertLess(F(*witness['projected_radius']),tiny)

    def test_actual_graph_augmentation_and_forged_boundary_rejection(self):
        snapshot=scene({'out':plane_x(1)})
        result=run(snapshot)
        self.assertTrue(audit_graph_neighborhood(scene_wire(snapshot),wire(result))['boundary_neighborhood_independently_verified'])
        snapshot['sources'][0]['position_BU']=[0,0,-4]
        result['graph']['nodes'][0]['origin']=(F(0),F(0),F(-4))
        result['graph']['nodes'][0]['point']=(F(1),F(0),F(-4))
        with self.assertRaisesRegex(ValueError,'interior neighborhood'):
            audit_graph_neighborhood(scene_wire(snapshot),wire(result))


if __name__=='__main__':
    unittest.main()
