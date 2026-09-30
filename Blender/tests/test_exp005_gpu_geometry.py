"""Component packing/readback tests only; no Blender/compute dispatch."""
import copy
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).parents[1]/'benchmarks'/'capacity_audit'))
from gpu_geometry_probe import pack_geometry,decode_hits,require_unambiguous
from exp005_escape_fixture import escape_fixture


class GeometryTests(unittest.TestCase):
    def batch(self):
        return pack_geometry(escape_fixture(),[{'origin_BU':[-1,0,0],'direction':[1,0,0]}])

    def test_geometry_contains_only_vertices_indices_and_raw_rays(self):
        batch=self.batch()
        self.assertEqual((batch.triangle_count,batch.query_count),(30,1))
        self.assertEqual(batch.rays,(-1.,0.,0.,1e-6,1.,0.,0.,0.))
        self.assertEqual(len(batch.triangles),360)

    def test_hit_miss_ambiguity_and_fail_closed(self):
        batch=self.batch()
        self.assertEqual(decode_hits(batch,[-1.,-1.,-1.,0.],[0.]*4),[{'status':'miss'}])
        hits=decode_hits(batch,[1.,0.,0.,1.],[0.,0.,1.,0.]); require_unambiguous(hits)
        hits=decode_hits(batch,[1.,0.,0.,2.],[0.,0.,1.,0.])
        with self.assertRaises(ValueError): require_unambiguous(hits)
        for raw in ([1.,0.,0.,3.],[1.,.5,0.,1.],[float('nan'),0.,0.,1.]):
            with self.assertRaises(ValueError): decode_hits(batch,raw,[0.,0.,1.,0.])

    def test_bounds_and_invalid_geometry_queries(self):
        for label in ('missing','zero','nonfinite','bounds','degenerate','unknown'):
            scene=escape_fixture(); queries=[{'origin_BU':[-1,0,0],'direction':[1,0,0]}]
            if label=='missing': queries=[]
            if label=='zero': queries[0]['direction']=[0,0,0]
            if label=='nonfinite': queries[0]['origin_BU']=[float('nan'),0,0]
            if label=='bounds': queries*=257
            if label=='degenerate': scene['objects']['a.bs1']['vertices_world_BU']=[(0,0,0)]*4
            if label=='unknown': scene['undeclared_meshes']=['decor']
            with self.subTest(case=label),self.assertRaises(ValueError): pack_geometry(scene,queries)

    def test_shader_never_reads_a_target_object_or_cpu_hit(self):
        import gpu_geometry_probe as probe
        code=probe.SHADER.read_text()
        for token in ('cross(d,e2)','triangle_count','normalize(cross(e1,e2))','ambiguous'):
            self.assertIn(token,code)
        self.assertNotIn('desired_object',code)
        self.assertNotIn('expected_hit',code)

    def test_independent_reference_and_runtime_import_do_not_need_blender(self):
        from exp005_intersection_runtime import independent_hits,compare,queries_from_records
        scene=escape_fixture(); queries=queries_from_records(scene,[])
        hits=independent_hits(scene,queries)
        self.assertEqual(hits[-2:],[{'status':'miss'}]*2)
        self.assertEqual(compare(hits,hits)['distance_max_BU'],0.)
        altered=copy.deepcopy(hits); altered[0]['distance_BU']+=.01
        with self.assertRaises(ValueError): compare(altered,hits)


if __name__=='__main__': unittest.main()
