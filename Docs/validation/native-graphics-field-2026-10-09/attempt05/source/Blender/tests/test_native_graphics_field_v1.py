"""Binary64 transport and geometry admission tests, not actual GPU evidence."""
import math,struct,unittest
from fractions import Fraction as F
from Blender.blender_lab.native_graphics_field_v1 import texture_words,unpack_complex,exact_double,captured_object_scalars
from Blender.tests.test_exact_object_index_v1 import scene,plane_x


class FieldTransportControls(unittest.TestCase):
    def test_bit_transport_keeps_binary64_and_signed_zero(self):
        rows=[[math.pi,-0.0],[math.nextafter(1,2),1e-200]];words,height=texture_words(rows,2)
        self.assertEqual(height,1)
        for j,row in enumerate(rows):
            value=unpack_complex(words[4*j:4*j+4])
            self.assertEqual(struct.pack('<dd',value.real,value.imag),struct.pack('<dd',*row))
    def test_unsupported_geometry_rounding_rejected(self):
        self.assertEqual(exact_double(F(1,8)),.125)
        with self.assertRaisesRegex(ValueError,'representable'):exact_double(F(1,3))
    def test_geometry_comes_from_captured_plane_not_expected_hit(self):
        s=scene({'out':plane_x(2)})
        scalars=captured_object_scalars(s,['out']);self.assertEqual(scalars[0][3],2)
        s['objects']['out']['vertices_world_BU'][0]=(F(5,2),-4,-4)
        with self.assertRaises(ValueError):captured_object_scalars(s,['out'])
    def test_nonfinite_readback_rejected(self):
        w=list(struct.unpack('<IIII',struct.pack('<dd',math.inf,0)))
        with self.assertRaisesRegex(ValueError,'Finite'):unpack_complex(w)

if __name__=='__main__':unittest.main()
