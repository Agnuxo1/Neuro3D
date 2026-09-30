from fractions import Fraction
import unittest
from exp005_normal_residual_audit import audit,plane_offset


class NormalResidualTests(unittest.TestCase):
    def test_retained_annex_exact_plane_and_triangle_agree(self):
        report = audit()
        self.assertGreater(report['self_hit']['signed_plane_t_BU_display'],1e-9)
        self.assertLess(report['predicted_t_display_delta_BU'],1e-20)
        self.assertLess(report['unit_normal_residual_display_delta_BU'],1e-30)
        self.assertGreater(report['exact_vs_peer_float_t_delta_BU'],1e-10)
        self.assertFalse(report['native_promotion_allowed'])

    def test_tangential_shift_does_not_change_residual(self):
        triangle = [[0.,0.,0.],[1.,0.,0.],[0.,1.,0.]]
        a = plane_offset(triangle,[0.,0.,1e-8],[1.,0.,-.001])
        b = plane_offset(triangle,[100.,-300.,1e-8],[1.,0.,-.001])
        self.assertEqual(a['signed_plane_t_rational'],b['signed_plane_t_rational'])
        # Second origin may lie outside the triangle: diagnostic must not claim hit.
        self.assertIn('does not validate triangle',b['scope'])

    def test_signed_normal_offsets_and_origin_zero_preserved(self):
        tri = [[0.,0.,0.],[1.,0.,0.],[0.,1.,0.]]
        a = plane_offset(tri,[.1,.1,1e-8],[0.,0.,-1.])
        b = plane_offset(tri,[.1,.1,-1e-8],[0.,0.,-1.])
        z = plane_offset(tri,[.1,.1,0.],[0.,0.,-1.])
        self.assertEqual(Fraction(*a['signed_plane_t_rational']),Fraction(1e-8))
        self.assertEqual(Fraction(*b['signed_plane_t_rational']),-Fraction(1e-8))
        self.assertEqual(z['signed_plane_t_rational'],[0,1])

    def test_close_different_plane_is_legitimate_not_exempted(self):
        report = audit(); t = report['legitimate_parallel_surface']['signed_plane_t_BU_display']
        self.assertTrue(report['band_0_332_would_omit_legitimate_surface'])
        self.assertGreater(t,1e-9); self.assertAlmostEqual(t,1e-5,delta=2e-12)

    def test_parallel_degenerate_and_nonfinite_reject(self):
        tri = [[0.,0.,0.],[1.,0.,0.],[0.,1.,0.]]
        for geometry,point,direction in ((tri,[0.,0.,1.],[1.,0.,0.]),
            ([tri[0]]*3,[0.,0.,0.],[0.,0.,1.]),(tri,[float('nan'),0.,0.],[0.,0.,1.])):
            with self.assertRaises(ValueError): plane_offset(geometry,point,direction)


if __name__ == '__main__': unittest.main()
