import unittest
from Blender.blender_lab.native_graphics_geometry_v1 import pack_geometry,pack_queries

class GraphicsAdmissionControls(unittest.TestCase):
    def test_actual_vertices_and_previous_identity_without_hit_feedback(self):
        scene={'objects':{'surface':{'vertices_world_BU':[(1,-1,-1),(1,1,-1),(1,0,1)],'faces':[(0,1,2)]}}}
        names,data,count=pack_geometry(scene);self.assertEqual(count,1);self.assertEqual(data['position'][0],(1.,-1.,-1.))
        q={'origin':[1,0,0],'direction':[1,0,0],'previous_name':'surface'};a,b=pack_queries([q],names);self.assertEqual(a,[1.,0.,0.,0.]);self.assertEqual(b,[1.,0.,0.,0.])
        with self.assertRaises(ValueError):pack_queries([dict(q,hit_object='surface')],names)

    def test_unknown_previous_and_zero_direction_rejected(self):
        for q in ({'origin':[0,0,0],'direction':[0,0,0],'previous_name':None},{'origin':[0,0,0],'direction':[1,0,0],'previous_name':'missing'}):
            with self.assertRaises(ValueError):pack_queries([q],['surface'])

if __name__=='__main__':unittest.main()
