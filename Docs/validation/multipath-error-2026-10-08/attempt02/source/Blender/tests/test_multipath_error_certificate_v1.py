"""End-to-end certificate gates fixed before observing new results."""
import copy
from fractions import Fraction as F
import itertools
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks'/'capacity_audit'))
from rational_interval_v1 import Interval as I, pi_interval, sincos
from multipath_error_certificate_v1 import certify_scene, default_radii
from robust_multipath_v1 import trace_scene
from test_robust_multipath_v1 import scene,plane_x
from exp005_chain_fixture import chain_fixture,inputs,set_fields


def endpoints(value): return F(*value['lo']),F(*value['hi'])
def contains(value,number):
    lo,hi=endpoints(value)
    return lo <= F(number) <= hi


class MathematicalEnclosures(unittest.TestCase):
    def test_sqrt_integer_certificate(self):
        for value in (F(0),F(1),F(2),F(7,13),F(1,2**250),F(10**30)):
            enclosure=I(value).sqrt()
            self.assertLessEqual(enclosure.lo**2,value)
            self.assertGreaterEqual(enclosure.hi**2,value)
            self.assertLessEqual(enclosure.width(),F(1,2**128))

    def test_pi_and_trig_independent_high_precision_diagnostic(self):
        import mpmath as mp  # Diagnostic only; production certificate is stdlib.
        with mp.workdps(90):
            def q(value): return mp.mpf(value.numerator)/value.denominator
            pi=pi_interval()
            self.assertLessEqual(q(pi.lo),mp.pi); self.assertGreaterEqual(q(pi.hi),mp.pi)
            for value in (F(0),F(1,3),F(-3),F(10**12)+F(1,17)):
                sine,cosine=sincos(I(value))
                for enclosure,expected in ((sine,mp.sin(q(value))),(cosine,mp.cos(q(value)))):
                    self.assertLessEqual(q(enclosure.lo),expected); self.assertGreaterEqual(q(enclosure.hi),expected)

    def test_wide_trig_and_singular_denominator(self):
        self.assertEqual(sincos(I(-10,10)),(I(-1,1),I(-1,1)))
        with self.assertRaises(ZeroDivisionError): I(1)/I(-1,1)


class CompleteErrorPipeline(unittest.TestCase):
    def test_all_41_k3_k4_probes(self):
        for cells in (3,4):
            snapshot=chain_fixture(cells)
            for label,amps in inputs(cells+1):
                with self.subTest(cells=cells,probe=label):
                    set_fields(snapshot,amps)
                    certificate=certify_scene(snapshot)
                    self.assertEqual(certificate['status'],'CERTIFIED_REPRESENTED_MODEL',certificate.get('reason'))
                    self.assertTrue(certificate['topology_certified'])
                    for port in certificate['ports'].values():
                        self.assertLessEqual(F(*port['field_error_L1_upper']),F(1,10**11))
                        self.assertLessEqual(F(*port['intensity_error_upper']),F(1,10**11))

    def test_nonzero_stable_geometry_origin_and_direction_box(self):
        snapshot=scene({'out':plane_x(2)})
        bounds=default_radii(snapshot); radius=F(1,10**6)
        bounds['object_translation']['out']=(radius,0,0)
        bounds['source_position']=radius
        bounds['source_direction']['input']=(radius,0,0)
        bounds['source_field']=radius; bounds['wavelength']=F(1,10**9)
        certificate=certify_scene(snapshot,radii=bounds)
        self.assertEqual(certificate['status'],'CERTIFIED_SUPPLIED_MODEL_BOX',certificate.get('reason'))
        port=certificate['ports']['out']
        for surface,origin,direction in itertools.product((-1,1),repeat=3):
            sampled=copy.deepcopy(snapshot)
            shift=surface*radius
            sampled['objects']['out']['vertices_world_BU']=[(F(x)+shift,y,z) for x,y,z in sampled['objects']['out']['vertices_world_BU']]
            sampled['objects']['out']['mode_origin_BU']=(2+shift,0,0)
            sampled['sources'][0]['position_BU']=(origin*radius,0,0)
            sampled['sources'][0]['direction']=(1+direction*radius,0,0)
            result=trace_scene(sampled)
            self.assertTrue(contains(port['field_real'],result['fields']['out'].real))
            self.assertTrue(contains(port['field_imag'],result['fields']['out'].imag))
            self.assertTrue(contains(port['intensity'],result['powers']['out']))

    def test_reflected_path_box_and_source_coefficient_errors(self):
        snapshot=scene({'bs':plane_x(1,'bs'),'right':plane_x(2),'left':plane_x(-1,'escape',axis=(-1,0,0))})
        bounds=default_radii(snapshot)
        bounds['source_position']=F(1,10**7); bounds['source_field']=F(1,10**7); bounds['transmittance']=F(1,10**7)
        certificate=certify_scene(snapshot,radii=bounds)
        self.assertEqual(certificate['status'],'CERTIFIED_SUPPLIED_MODEL_BOX',certificate.get('reason'))
        self.assertEqual(certificate['path_count'],2)

    def test_incomplete_trace_remains_unknown(self):
        certificate=certify_scene(scene({'touch':plane_x(0,'mirror'),'out':plane_x(2)}))
        self.assertEqual(certificate['status'],'UNKNOWN'); self.assertIsNone(certificate['ports'])

    def test_angular_uncertainty_is_not_common_mode_certified(self):
        snapshot=scene({'out':plane_x(2)}); bounds=default_radii(snapshot)
        bounds['source_direction']['input']=(0,F(1,10**6),0)
        certificate=certify_scene(snapshot,radii=bounds)
        self.assertEqual(certificate['status'],'UNKNOWN')
        self.assertEqual(certificate['reason'],'UNKNOWN_TERMINAL_MODE')

    def test_tiny_gap_order_uncertainty_rejected(self):
        gap=F(1,2**44)
        snapshot=scene({'bs':plane_x(1,'bs',power_transmittance=1),'out':plane_x(1+gap)})
        bounds=default_radii(snapshot); bounds['object_translation']['bs']=(gap,0,0)
        certificate=certify_scene(snapshot,radii=bounds)
        self.assertEqual(certificate['status'],'UNKNOWN')

    def test_unknown_physical_bound_never_defaults_zero(self):
        snapshot=scene({'out':plane_x(2)}); bounds=default_radii(snapshot); bounds['vertex_radius']=None
        certificate=certify_scene(snapshot,radii=bounds)
        self.assertEqual(certificate['status'],'UNKNOWN'); self.assertIsNone(certificate['ports'])
        self.assertEqual(certificate['physical_input_bounds'],'UNKNOWN_NOT_ZERO')

    def test_zero_source_or_branch_support_change_rejected(self):
        snapshot=scene({'bs':plane_x(1,'bs',power_transmittance=1),'out':plane_x(2)})
        bounds=default_radii(snapshot); bounds['transmittance']=F(1,10**6)
        self.assertEqual(certify_scene(snapshot,radii=bounds)['reason'],'UNKNOWN_BRANCH_SUPPORT')
        snapshot=scene({'out':plane_x(2)}); snapshot['sources'][0]['field_reim']=[0,0]
        bounds=default_radii(snapshot); bounds['source_field']=F(1,10**6)
        self.assertEqual(certify_scene(snapshot,radii=bounds)['reason'],'UNKNOWN_SOURCE_SUPPORT')


if __name__=='__main__': unittest.main()
