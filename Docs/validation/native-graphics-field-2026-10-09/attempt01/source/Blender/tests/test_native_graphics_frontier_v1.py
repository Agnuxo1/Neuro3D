"""Adversarial software controls; the mock is explicitly not GPU evidence."""
import math,unittest
from Blender.tests.test_exact_object_index_v1 import plane_x,scene
from Blender.blender_lab.native_graphics_frontier_v1 import build_graphics_graph
from Blender.blender_lab.coherent_state_graph_v1 import build_graph,propagate_graph
from Blender.benchmarks.capacity_audit import robust_multipath_v1 as base


class MockCandidates:
    def __init__(self,snapshot,wrong=False,missing=False):
        self.triangles=base.geometry(snapshot)[2];self.wrong=wrong;self.missing=missing;self.queries=[]
    def query(self,queries):
        self.queries.append(queries);rows=[]
        for q in queries:
            if self.missing:continue
            previous=next((t for t in self.triangles if t['object_id']==q['previous_name']),None)
            if previous is not None:
                a,b,c=previous['vertices'];previous=dict(previous,normal=base.cross(base.sub(b,a),base.sub(c,a)))
            hit=base.select(q['origin'],q['direction'],self.triangles,previous)
            if self.wrong:
                rows.append({'status':'GRAPHICS_SURFACE_CANDIDATE','object':'far','distance_BU':2.0,'primitive_id':1});continue
            if hit['status']!='SELECT':rows.append({'status':'MISS'});continue
            rows.append({'status':'GRAPHICS_SURFACE_CANDIDATE','object':hit['selected']['object_id'],'distance_BU':float(hit['t'])*math.sqrt(float(base.dot(q['direction'],q['direction']))),'primitive_id':hit['selected']['primitive_id']})
        return {'rows':rows}


class GraphicsFrontierControls(unittest.TestCase):
    def test_complete_branches_from_sources_without_expected_hits(self):
        snapshot=scene({'bs':plane_x(1,'bs'),'out':plane_x(2),'escape':plane_x(-1,'escape',axis=(-1,0,0))})
        backend=MockCandidates(snapshot);actual=build_graphics_graph(snapshot,backend);expected=build_graph(snapshot)
        self.assertEqual(actual['nodes'],expected['nodes']);self.assertEqual(actual['status'],'COMPLETE')
        self.assertEqual(propagate_graph(actual,{snapshot['sources'][0]['id']:[1,0]})['represented_terminal_paths'],2)
        self.assertEqual(len(backend.queries),2)
        self.assertTrue(all(set(q)=={'origin','direction','previous_name'} for batch in backend.queries for q in batch))
    def test_wrong_gpu_candidate_is_not_replaced_by_cpu_hit(self):
        snapshot=scene({'near':plane_x(1),'far':plane_x(2)})
        actual=build_graphics_graph(snapshot,MockCandidates(snapshot,wrong=True))
        self.assertEqual(actual['status'],'INCOMPLETE');self.assertEqual(actual['selection_statistics']['rejected_candidates'],1)
        self.assertNotIn('hit_object',actual['nodes'][0]);self.assertFalse(actual['graphics_candidate_fallback'])
        with self.assertRaises(ValueError):propagate_graph(actual,{'input':[1,0]})
    def test_missing_readback_rejected(self):
        snapshot=scene({'out':plane_x(1)})
        with self.assertRaisesRegex(ValueError,'readback'):build_graphics_graph(snapshot,MockCandidates(snapshot,missing=True))


if __name__=='__main__':unittest.main()
