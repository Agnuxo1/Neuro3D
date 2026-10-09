"""Affine geometry derivatives checked against fresh traces and central differences."""
from fractions import Fraction as F
import copy
import numpy as np
import unittest
from Blender.tests.test_coherent_state_graph_v1 import chain_fixture,scene_wire
from Tools.audit_captured_pilot_result_v1 import decode
from Blender.blender_lab.coherent_state_graph_v1 import build_graph,propagate_graph
from Blender.blender_lab.affine_geometry_network_v1 import AffineGeometryNetwork
from Tools.trace_indexed_scene_v1 import wire
from Tools.audit_graph_neighborhood_v1 import audit_graph_neighborhood


def network():
    snapshot=decode(scene_wire(chain_fixture(2)))
    parameters=[{'id':str(i),'objects':{f'c{i}.r1':(1,0,0),f'c{i}.r2':(1,0,0)}} for i in range(2)]
    return AffineGeometryNetwork(snapshot,build_graph(snapshot),parameters)


class AffineGeometryTests(unittest.TestCase):
    def test_forward_equals_fresh_geometric_rebuild_after_nonzero_translation(self):
        net=network();deltas=[F(1,128),F(-1,256)]
        inputs=np.asarray([[.3+.2j,-.6+.1j,.1-.2j],[1,1j,-.5j]])
        actual=net.forward(inputs,deltas)
        scene,graph=net.materialize(deltas);fresh=build_graph(scene)
        self.assertEqual(fresh['status'],'COMPLETE')
        for row,values in enumerate(inputs):
            fields={s: [v.real,v.imag] for s,v in zip(net.source_ids,values)}
            result=propagate_graph(fresh,fields)
            for p in net.ports:self.assertLess(abs(actual['fields'][row,net.ports.index(p)]-result['fields'][p]),1e-13)
        result=propagate_graph(graph,{s:[1,0] for s in net.source_ids})
        self.assertTrue(audit_graph_neighborhood(wire(scene),wire({'graph':graph,**result}))['boundary_neighborhood_independently_verified'])

    def test_field_and_power_gradients_against_central_differences(self):
        net=network();x=np.asarray([[.3+.2j,-.6+.1j,.1-.2j]])
        d=np.asarray([.003,-.005]);result=net.forward(x,d)
        h=1e-7
        for j in range(2):
            delta=np.eye(2)[j]*h
            a,b=net.forward(x,d+delta),net.forward(x,d-delta)
            np.testing.assert_allclose((a['fields']-b['fields'])/(2*h),result['field_jacobian'][:,:,j],atol=1e-7,rtol=1e-8)
            np.testing.assert_allclose((a['powers']-b['powers'])/(2*h),result['power_jacobian'][:,:,j],atol=1e-7,rtol=1e-8)

    def test_own_loss_gradient_and_one_descent_update(self):
        net=network();x=np.asarray([[1,.2,.3],[.2,1,.4],[.5,.1,1]],dtype=complex)
        y=np.asarray([0,1,2]);d=np.asarray([.003,-.005]);ports=net.ports
        loss,grad,_=net.cross_entropy(x,y,d,ports,.15)
        for j in range(2):
            delta=np.eye(2)[j]*1e-7
            a=net.cross_entropy(x,y,d+delta,ports,.15)[0];b=net.cross_entropy(x,y,d-delta,ports,.15)[0]
            self.assertAlmostEqual((a-b)/2e-7,grad[j],delta=1e-6)
        updated=net.cross_entropy(x,y,d-grad*1e-6,ports,.15)[0]
        self.assertLess(updated,loss)

    def test_unsupported_merge_does_not_silently_share_derivatives(self):
        net=network()
        with self.assertRaisesRegex(ValueError,'different affine origins'):
            AffineGeometryNetwork(net.scene,net.graph,[{'id':'unpaired','objects':{'c0.r1':(1,0,0)}}])

    def test_only_finite_complete_inputs_and_mirror_translation_parameters(self):
        net=network()
        with self.assertRaises(ValueError):net.forward([[1,0]],[0,0])
        with self.assertRaises(ValueError):net.forward([[np.nan,0,0]],[0,0])
        with self.assertRaises(ValueError):net.forward([[1,0,0]],[float('nan'),0])
        with self.assertRaisesRegex(ValueError,'mirrors'):
            AffineGeometryNetwork(net.scene,net.graph,[{'id':'bs','objects':{'c0.bs1':(1,0,0)}}])


if __name__=='__main__':unittest.main()
