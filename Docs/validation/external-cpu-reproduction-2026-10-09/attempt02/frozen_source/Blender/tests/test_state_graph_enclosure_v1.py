"""Outward interval/control errors checked by independent90-digit arithmetic."""
import copy
from fractions import Fraction as F
import unittest
import mpmath as mp

from Blender.tests.test_exact_object_index_v1 import plane_x,scene
from Blender.blender_lab.coherent_state_graph_v1 import build_graph,propagate_graph
from Blender.blender_lab.state_graph_enclosure_v1 import enclose_fields,observed_certificate,tight_sincos,propagation
from Blender.benchmarks.capacity_audit.rational_interval_v1 import Interval as I
from Tools.trace_indexed_scene_v1 import wire


class GraphEnclosureTests(unittest.TestCase):
    def test_tiny_coefficients_do_not_amplify_fixed_grid_rounding(self):
        wavelength=F(3602879701896397,36028797018963968)
        enclosed=propagation(F(4297065,2097152),F(1),wavelength)
        self.assertLess(max(float(i.width()) for i in enclosed),1e-30)
        with mp.workdps(90):
            angle=2*mp.pi*mp.mpf(4297065)/2097152/(mp.mpf(wavelength.numerator)/wavelength.denominator)
            for interval,expected in zip(enclosed,(mp.cos(angle),mp.sin(angle))):
                self.assertTrue(mp.mpf(interval.lo.numerator)/interval.lo.denominator<=expected<=mp.mpf(interval.hi.numerator)/interval.hi.denominator)

    def test_explicit_radius_and_reduction_at_signed_angles(self):
        with mp.workdps(90):
            for center in (F(0),F(-345,11),F(203,7),F(10**20)):
                radius=F(1,10**8)
                sine,cosine=tight_sincos(I(center-radius,center+radius))
                for point in (center-radius,center,center+radius):
                    angle=mp.mpf(point.numerator)/point.denominator
                    for interval,expected in ((sine,mp.sin(angle)),(cosine,mp.cos(angle))):
                        self.assertTrue(mp.mpf(interval.lo.numerator)/interval.lo.denominator<=expected<=mp.mpf(interval.hi.numerator)/interval.hi.denominator)

    def test_exact_direct_phase_and_certified_observed_output(self):
        snapshot=scene({'out':plane_x(2)})
        graph=build_graph(snapshot)
        fields={'input':[1,0]}
        reference=enclose_fields(graph,fields)
        self.assertTrue(reference['out'][0].contains(1))
        self.assertTrue(reference['out'][1].contains(0))
        native=propagate_graph(graph,fields)
        certificate=observed_certificate(graph,fields,wire(native['fields']),native['powers'],detector_ports=['out'])
        self.assertEqual(certificate['status'],'CERTIFIED_OBSERVED_REPRESENTED_OUTPUTS')
        self.assertEqual(certificate['decision']['status'],'CERTIFIED_REPRESENTED_ARGMAX')
        self.assertEqual(certificate['scope']['physical_model_error'],'UNKNOWN_NOT_ZERO')

    def test_independent_high_precision_nontrivial_splitter_and_phase(self):
        snapshot=scene({'bs':plane_x(F(1,3),'bs',power_transmittance=F(3,10)),
                        'out':plane_x(F(7,5)),'escape':plane_x(-F(3,2),'escape',axis=(-1,0,0))})
        snapshot['lambda_BU']=F(3,17)
        graph=build_graph(snapshot)
        fields={'input':[F(2,7),F(-3,11)]}
        reference=enclose_fields(graph,fields)
        with mp.workdps(90):
            source=mp.mpc(mp.mpf(2)/7,-mp.mpf(3)/11)
            expected={'out':source*mp.sqrt(mp.mpf(3)/10)*mp.exp(2j*mp.pi*(mp.mpf(7)/5)/(mp.mpf(3)/17)),
                      'escape':source*1j*mp.sqrt(mp.mpf(7)/10)*mp.exp(2j*mp.pi*(mp.mpf(2)/3+mp.mpf(3)/2)/(mp.mpf(3)/17))}
            for name,value in expected.items():
                for interval,observed in zip(reference[name],(value.real,value.imag)):
                    low=mp.mpf(interval.lo.numerator)/interval.lo.denominator
                    high=mp.mpf(interval.hi.numerator)/interval.hi.denominator
                    self.assertTrue(low<=observed<=high)

    def test_bad_observed_native_value_has_valid_large_error_not_false_pass(self):
        graph=build_graph(scene({'out':plane_x(2)}))
        certificate=observed_certificate(graph,{'input':[1,0]},{'out':{'real':2.,'imag':0.}}, {'out':4.})
        self.assertEqual(certificate['status'],'VALID_BOUNDS_EXCEED_REQUESTED_BUDGET')
        self.assertGreaterEqual(certificate['ports']['out']['observed_field_error_L1_upward_float'],1)

    def test_equal_modal_powers_leave_argmax_unknown(self):
        snapshot=scene({'bs':plane_x(1,'bs'),'out':plane_x(2),'escape':plane_x(-1,'escape',axis=(-1,0,0))})
        graph=build_graph(snapshot)
        fields={'input':[1,0]}
        native=propagate_graph(graph,fields)
        certificate=observed_certificate(graph,fields,wire(native['fields']),native['powers'],detector_ports=['out','escape'])
        self.assertEqual(certificate['decision']['status'],'UNKNOWN_OVERLAPPING_INTERVALS')
        self.assertIsNone(certificate['decision']['winner'])

    def test_incomplete_graph_and_missing_input_rejected(self):
        graph=build_graph(scene({'out':plane_x(1)},direction=(-1,0,0)))
        with self.assertRaises(ValueError):
            enclose_fields(graph,{'input':[1,0]})
        graph=build_graph(scene({'out':plane_x(2)}))
        with self.assertRaises(ValueError):
            enclose_fields(graph,{})


if __name__=='__main__':
    unittest.main()
