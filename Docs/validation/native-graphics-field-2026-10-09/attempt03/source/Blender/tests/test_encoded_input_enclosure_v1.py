"""Independent high-precision and adverse controls for ideal input encoding."""
from fractions import Fraction as F
import unittest
import mpmath as mp
from Blender.blender_lab.encoded_input_enclosure_v1 import encode_feature_row,enclose_interval_inputs
from Blender.benchmarks.capacity_audit.rational_interval_v1 import Interval as I
from Blender.blender_lab.coherent_state_graph_v1 import build_graph
from Blender.tests.test_exact_object_index_v1 import plane_x,scene
from Tools.certify_native_training_batch_v1 import certificate_from_reference


class EncodingEnclosureTests(unittest.TestCase):
    def test_signed_outside_training_range_high_precision_and_reordered_sources(self):
        values=[-0.1,0.2,1.3,0.7];low=[0.,0.,0.,0.];high=[1.,1.,1.,1.];ids=['c2','c1','r1','c0','r0']
        encoded=encode_feature_row(values,low,high,ids)
        with mp.workdps(90):
            exact=[mp.mpf(F(v).numerator)/F(v).denominator for v in values]+[mp.mpf(1)]
            norm=mp.sqrt(sum(v*v for v in exact))
            for sid,value in zip(['r0','r1','c0','c1','c2'],exact):
                bound=encoded[sid][0]
                self.assertTrue(mp.mpf(bound.lo.numerator)/bound.lo.denominator<=value/norm<=mp.mpf(bound.hi.numerator)/bound.hi.denominator)
                self.assertTrue(encoded[sid][1].contains(0))
        self.assertLess(encoded['r0'][0].hi,0)  # No implicit clipping.

    def test_invalid_feature_range_and_duplicate_source_rejected(self):
        with self.assertRaises(ValueError):encode_feature_row([0]*4,[0]*4,[0]*4,['r0','r1','c0','c1','c2'])
        with self.assertRaises(ValueError):encode_feature_row([0]*4,[0]*4,[1]*4,['r0','r0','c0','c1','c2'])

    def test_interval_input_endpoint_propagation_and_large_native_error(self):
        graph=build_graph(scene({'out':plane_x(2)}))
        reference=enclose_interval_inputs(graph,{'input':[I(F(1,3),F(2,3)),I(0)]})
        self.assertTrue(reference['out'][0].contains(F(1,3)))
        self.assertTrue(reference['out'][0].contains(F(2,3)))
        with self.assertRaises(ValueError):enclose_interval_inputs(graph,{})
        # Three modes are deliberate class-readout fixtures, independent of labels.
        refs={p:reference['out'] for p in ['a','b','c']}
        obs={p:{'real':2.,'imag':0.} for p in refs};powers={p:4. for p in refs}
        cert=certificate_from_reference(refs,obs,powers,list(refs),F(1,10**11),F(1,10**11))
        self.assertEqual(cert['status'],'VALID_BOUNDS_EXCEED_REQUESTED_BUDGET')
        self.assertEqual(cert['decision']['status'],'UNKNOWN_OVERLAPPING_INTERVALS')

    def test_equal_zero_class_powers_do_not_produce_certified_winner(self):
        refs={p:(I(0),I(0)) for p in ['a','b','c']};obs={p:{'real':0.,'imag':0.} for p in refs}
        cert=certificate_from_reference(refs,obs,{p:0. for p in refs},list(refs),F(1,10**11),F(1,10**11))
        self.assertEqual(cert['status'],'CERTIFIED_OBSERVED_REPRESENTED_OUTPUTS')
        self.assertEqual(cert['decision']['status'],'UNKNOWN_OVERLAPPING_INTERVALS')
        self.assertIsNone(cert['decision']['winner'])


if __name__=='__main__':unittest.main()
