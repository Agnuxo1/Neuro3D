"""Own path-derived Jacobians, checked by independent analytic fields and FD."""
import copy
import cmath
from fractions import Fraction as F
import math
import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent))
from exp005_chain_fixture import chain_fixture,analytic_fields
from Blender.blender_lab.geometric_network_v1 import GeometricNetwork,stable_propagation_phase
from Blender.benchmarks.capacity_audit.robust_multipath_v1 import trace_scene


class GeometricNetworkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scene=chain_fixture(2)
        cls.network=GeometricNetwork(cls.scene,phase_objects=('c0.r1','c1.r1'),tau_objects=('c0.bs1',))
        cls.fields={'row':[.3,.2],'col0':[-.6,.1],'col1':[.1,-.2]}

    def test_all_sources_compiled_and_independent_analytic_fields(self):
        net=self.network
        result=net.forward(self.fields)
        amplitudes=[complex(*self.fields[s]) for s in net.source_ids]
        expected=analytic_fields(2,amplitudes)
        for p,value in expected.items():
            self.assertLess(abs(result['fields'][p]-value),2e-14)
        self.assertFalse(result['field_certified'])

    def test_zero_inputs_are_explicit_and_constructive_interference_kept(self):
        zero={s:[0,0] for s in self.network.source_ids}
        self.assertEqual(set(self.network.forward(zero)['powers'].values()),{0.0})
        a=dict(zero,row=[1,0])
        b=dict(zero,col0=[1,0])
        together=dict(zero,row=[1,0],col0=[1,0])
        separate={p:self.network.forward(a)['powers'][p]+self.network.forward(b)['powers'][p] for p in self.network.ports}
        self.assertGreater(max(abs(self.network.forward(together)['powers'][p]-separate[p]) for p in self.network.ports),1e-3)

    def test_phase_and_tau_jacobians_against_centered_differences(self):
        net=self.network
        values=dict(net.initial)
        result=net.forward(self.fields,values,jacobian=True)
        eps=1e-6
        for key in net.parameters:
            plus,minus=dict(values),dict(values)
            plus[key]+=eps
            minus[key]-=eps
            a,b=net.forward(self.fields,plus),net.forward(self.fields,minus)
            for port in net.ports:
                field=(a['fields'][port]-b['fields'][port])/(2*eps)
                power=(a['powers'][port]-b['powers'][port])/(2*eps)
                self.assertLess(abs(field-result['field_jacobian'][key][port]),2e-9)
                self.assertLess(abs(power-result['power_jacobian'][key][port]),2e-9)

    def test_updated_controls_agree_with_fresh_geometric_trace(self):
        net=self.network
        values=dict(net.initial)
        values['phase:c1.r1']=.61
        values['tau:c0.bs1']=.37
        scene=copy.deepcopy(self.scene)
        for s in scene['sources']:
            s['field_reim']=self.fields[s['id']]
        scene['objects']['c1.r1']['phase_rad']=.61
        scene['objects']['c0.bs1']['power_transmittance']=.37
        traced=trace_scene(scene)
        self.assertEqual(traced['status'],'COMPLETE')
        for p,v in net.forward(self.fields,values)['fields'].items():
            self.assertLess(abs(traced['fields'][p]-v),2e-13)

    def test_detector_mse_gradient_against_difference(self):
        net=self.network
        samples=[(self.fields,{'c0.Y':.12,'c1.Y':.24})]
        values=dict(net.initial)
        loss,gradient=net.power_mse(samples,values)
        self.assertGreaterEqual(loss,0)
        for key in net.parameters:
            a,b=dict(values),dict(values)
            a[key]+=1e-6
            b[key]-=1e-6
            fd=(net.power_mse(samples,a)[0]-net.power_mse(samples,b)[0])/2e-6
            self.assertLess(abs(fd-gradient[key]),2e-9)

    def test_incomplete_geometry_rejected(self):
        scene=copy.deepcopy(self.scene)
        scene['sources'][0]['direction']=[-1,0,0]
        with self.assertRaisesRegex(ValueError,'incomplete'):
            GeometricNetwork(scene)

    def test_invalid_fields_parameters_and_branch_support_rejected(self):
        with self.assertRaises(ValueError):
            self.network.forward({'row':[1,0]})
        values=dict(self.network.initial)
        values['tau:c0.bs1']=0
        with self.assertRaisesRegex(ValueError,'support'):
            self.network.forward(self.fields,values)
        scene=copy.deepcopy(self.scene)
        scene['objects']['c0.bs1']['power_transmittance']=1
        with self.assertRaisesRegex(ValueError,'support'):
            GeometricNetwork(scene,tau_objects=('c0.bs1',))

    def test_exact_large_cycle_reduction(self):
        path={'direction_norm_squared':1,'phase_length_numerator':F(2**100)+F(1,8)}
        self.assertEqual(stable_propagation_phase(path,F(1)),math.pi/4)

    def test_constructor_preserves_supplied_fields_and_scene(self):
        scene=copy.deepcopy(self.scene)
        before=copy.deepcopy(scene)
        GeometricNetwork(scene)
        self.assertEqual(scene,before)


if __name__=='__main__':
    unittest.main()
