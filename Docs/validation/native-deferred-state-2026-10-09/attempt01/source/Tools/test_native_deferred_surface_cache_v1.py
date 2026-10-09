"""Cache identity and stale-geometry controls; these are not GPU execution."""
import unittest
from fractions import Fraction as F
from types import SimpleNamespace
from unittest.mock import patch
from Blender.blender_lab.native_deferred_graphics_gradient_v1 import NativeDeferredGraphicsGradientTransport as Deferred,ForwardTransport,ray_key,FRAGMENT,FORWARD_FRAGMENT

class DeferredCacheControls(unittest.TestCase):
    def backend(self):
        b=Deferred.__new__(Deferred);b.candidate_cache={};b.geometry_generation=0;b.native_triangle_surface_queries=0;b.candidate_receipts=[];b.shader='optical';b.batch='quad';b.selector_shader='captured';b.selector_batch='triangles';b.stage_audit=SimpleNamespace(after=lambda _:None)
        return b
    def ray(self):return {'origin':(F(0),F(1),F(2)),'direction':(F(1),F(0),F(0)),'previous_name':None}
    def test_duplicate_ray_actual_candidate_fill_once(self):
        b=self.backend();r=self.ray();row={'object':'actual','primitive_id':2,'distance_BU':3.}
        with patch.object(ForwardTransport,'query',return_value={'rows':[row]}) as draw:
            self.assertEqual(b.selected_candidates([r,r]),[row,row]);self.assertEqual(b.selected_candidates([r]),[row]);self.assertEqual(draw.call_count,1)
        self.assertEqual(b.native_triangle_surface_queries,1);self.assertEqual(b.shader,'optical')
    def test_actual_geometry_update_invalidates_candidate(self):
        b=self.backend();b.candidate_cache[ray_key(self.ray())]={'object':'old'}
        with patch.object(ForwardTransport,'update_geometry',return_value=None):b.update_geometry({'actual':'changed'})
        self.assertEqual(b.candidate_cache,{});self.assertEqual(b.geometry_generation,1);self.assertEqual(b.shader,'optical')
    def test_exclusion_and_nonrepresentable_ray_identity(self):
        r=self.ray();s=dict(r,previous_name='mirror');self.assertNotEqual(ray_key(r),ray_key(s))
        with self.assertRaises(ValueError):ray_key(dict(r,origin=(F(1,3),F(0),F(0))))
    def test_optical_phase_and_tangent_expressions_unchanged(self):
        first='  dvec3 origin=';last='  out_color='
        self.assertEqual(FRAGMENT[FRAGMENT.index(first):FRAGMENT.index(last)],FORWARD_FRAGMENT[FORWARD_FRAGMENT.index(first):FORWARD_FRAGMENT.index(last)])
        self.assertNotIn('ray_lane',FRAGMENT);self.assertIn('texelFetch(actual_candidates',FRAGMENT)

if __name__=='__main__':unittest.main()
