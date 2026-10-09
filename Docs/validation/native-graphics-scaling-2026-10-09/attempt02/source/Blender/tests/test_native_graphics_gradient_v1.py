import math
import struct
import unittest
from fractions import Fraction
from Blender.blender_lab.native_graphics_gradient_v1 import exact_double, uniform_bytes


class PacketContractTests(unittest.TestCase):
    def test_binary64_payload_and_std140_row_stride(self):
        first=[-0.0,math.ldexp(1.0,-1074),1e200,-1e-200]+[float(i) for i in range(10)]
        second=[-float(i) for i in range(14)]
        payload=uniform_bytes([first,second],14)
        self.assertEqual(len(payload),32768)
        self.assertEqual(payload[:112],struct.pack('<14d',*first))
        self.assertEqual(payload[112:128],bytes(16))
        self.assertEqual(payload[128:240],struct.pack('<14d',*second))
        self.assertEqual(payload[240:],bytes(32768-240))

    def test_unsupported_shape_and_nonfinite_are_rejected(self):
        for rows,count in [([],14),([[0.0]*13],14),([[0.0]*14]*257,14),([[0.0]*14],10),([[float('nan')]+[0.0]*13],14)]:
            with self.subTest(count=count,rows=len(rows)):
                with self.assertRaises(ValueError):uniform_bytes(rows,count)

    def test_geometric_tangents_must_be_exactly_representable(self):
        self.assertEqual(exact_double(Fraction(1,8)),.125)
        with self.assertRaises(ValueError):exact_double(Fraction(1,3))


if __name__=='__main__':unittest.main()
