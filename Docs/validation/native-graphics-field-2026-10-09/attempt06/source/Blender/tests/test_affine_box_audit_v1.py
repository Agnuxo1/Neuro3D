"""Exact range, continuous support, fresh geometry and adverse controls."""
import copy
from fractions import Fraction as F
import unittest
import mpmath as mp
from Blender.tests.test_coherent_state_graph_v1 import chain_fixture,scene_wire
from Blender.tests.test_exact_object_index_v1 import plane_x,scene
from Tools.audit_captured_pilot_result_v1 import decode
from Tools.audit_graph_neighborhood_v1 import audit_graph_neighborhood
from Tools.trace_indexed_scene_v1 import wire
from Blender.blender_lab.coherent_state_graph_v1 import build_graph,propagate_graph
from Blender.blender_lab.affine_box_audit_v1 import Affine,IndependentAffineBox
from Blender.benchmarks.capacity_audit.rational_interval_v1 import Interval as I


def fixture():
    snapshot=decode(scene_wire(chain_fixture(2)));graph=build_graph(snapshot)
    audit_graph_neighborhood(wire(snapshot),wire({'graph':graph,**propagate_graph(graph,{s['id']:[1,0] for s in snapshot['sources']})}))
    parameters=[{'id':str(i),'objects':{f'c{i}.r1':(1,0,0),f'c{i}.r2':(1,0,0)}} for i in range(2)]
    return snapshot,graph,parameters


def high_precision_graph(graph):
    def m(v):v=F(v);return mp.mpf(v.numerator)/v.denominator
    incoming=[mp.mpc(0) for _ in graph['nodes']];outputs={p:mp.mpc(0) for p in graph['ports']}
    for root in graph['roots']:incoming[root['node']]+=1
    for i in graph['topological_order']:
        node=graph['nodes'][i];norm=mp.sqrt(sum(m(v)**2 for v in node['direction']))
        value=incoming[i]*mp.exp(2j*mp.pi*m(node['segment_parameter'])*norm/m(graph['wavelength']))
        if 'terminal' in node:outputs[node['terminal']]+=value*mp.exp(2j*mp.pi*m(node['reference_parameter'])*norm/m(graph['wavelength']))
        for edge in node['edges']:incoming[edge['target']]+=value*mp.sqrt(m(edge['power']))*1j**edge['quarter_turns']*mp.exp(1j*m(edge['phase_rad']))
    return outputs


class AffineBoxTests(unittest.TestCase):
    def test_exact_signed_affine_range(self):
        a=Affine(F(2),(F(3),F(-4)));bound=a.bounds([(F(-1),F(2)),(F(1),F(5))])
        self.assertEqual((bound.lo,bound.hi),(F(-21),F(4)))
        with self.assertRaises(ValueError):a.bounds([(F(1),F(0)),(F(0),F(1))])

    def test_continuous_proof_and_fresh_high_precision_fields(self):
        scene,graph,parameters=fixture();net=IndependentAffineBox(scene,graph,parameters);box=[(-F(1,10000),F(1,10000))]*2
        proof=net.prove_box(box);self.assertEqual(proof['status'],'PROVED_CONTINUOUS_AFFINE_BOX_TOPOLOGY')
        reference=net.enclose_fields(box,{r['source_id']:(I(1),I(0)) for r in graph['roots']})
        # Endpoint examples are controls of the analytic proof, not its basis.
        with mp.workdps(90):
            for deltas in [(0,0),(-F(1,10000),F(1,10000)),(F(1,10000),-F(1,10000))]:
                translated=copy.deepcopy(scene)
                for parameter,delta in zip(parameters,deltas):
                    for name in parameter['objects']:
                        translated['objects'][name]['vertices_world_BU']=[(F(v[0])+delta,F(v[1]),F(v[2])) for v in translated['objects'][name]['vertices_world_BU']]
                fresh=build_graph(translated);self.assertEqual(fresh['status'],'COMPLETE')
                for port,value in high_precision_graph(fresh).items():
                    for interval,number in zip(reference[port],(value.real,value.imag)):
                        self.assertTrue(mp.mpf(interval.lo.numerator)/interval.lo.denominator<=number<=mp.mpf(interval.hi.numerator)/interval.hi.denominator)

    def test_large_box_unknown_cannot_produce_fields(self):
        scene,graph,parameters=fixture();net=IndependentAffineBox(scene,graph,parameters);box=[(-F(1),F(1))]*2
        proof=net.prove_box(box);self.assertEqual(proof['status'],'UNKNOWN_TOPOLOGY_NOT_PROVED');self.assertTrue(proof['issues'])
        with self.assertRaises(ValueError):net.enclose_fields(box,{r['source_id']:(I(1),I(0)) for r in graph['roots']})

    def test_unpaired_merge_rejected(self):
        scene,graph,_=fixture()
        with self.assertRaises(ValueError):IndependentAffineBox(scene,graph,[{'id':'unpaired','objects':{'c0.r1':(1,0,0)}}])

    def test_near_competing_surface_not_certified_by_interior_support_alone(self):
        snapshot=scene({'mirror':plane_x(1,'mirror'),'near':plane_x(1+F(1,10**6),'mirror'),'out':plane_x(-1,axis=(-1,0,0))})
        graph=build_graph(snapshot);self.assertEqual(graph['status'],'COMPLETE')
        net=IndependentAffineBox(snapshot,graph,[{'id':'moving','objects':{'mirror':(1,0,0)}}])
        proof=net.prove_box([(-F(1,10**5),F(1,10**5))])
        self.assertEqual(proof['status'],'UNKNOWN_TOPOLOGY_NOT_PROVED')
        self.assertTrue(any(row.get('object')=='near' for row in proof['issues']))


if __name__=='__main__':unittest.main()
