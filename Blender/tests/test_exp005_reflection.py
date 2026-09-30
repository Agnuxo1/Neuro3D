"""Regression from actual Blender v1 normal; no bpy or GPU."""
import math
import unittest
from exp005_reflection import reflect_direction


class ReflectionTests(unittest.TestCase):
    def test_recorded_float32_normal_reflects_to_x_without_false_y_drift(self):
        normal=(.7071068286895752,-.7071068286895752,0)
        self.assertGreater(abs(sum(v*v for v in normal)-1),1e-8)
        self.assertEqual(reflect_direction((0,1,0),normal),(1.,0.,0.))
        old=tuple(d-2*(-normal[1]*-1)*n for d,n in zip((0,1,0),normal))
        self.assertGreater(abs(old[1]),1e-8)

    def test_normal_scale_does_not_change_reflection(self):
        d=(1.,.3,.2); normal=(.2,-.9,.7)
        reference=reflect_direction(d,normal)
        for scale in (.001,3.,-4.,1e4):
            actual=reflect_direction(d,tuple(v*scale for v in normal))
            self.assertLess(max(abs(a-b) for a,b in zip(actual,reference)),1e-14)
            self.assertAlmostEqual(math.hypot(*actual),1.,places=14)

    def test_invalid_vectors_fail(self):
        for direction,normal in [((0,0,0),(1,0,0)),((1,0,0),(0,0,0)),
                                  ((float('nan'),0,0),(1,0,0))]:
            with self.assertRaises(ValueError): reflect_direction(direction,normal)


if __name__=='__main__': unittest.main()
