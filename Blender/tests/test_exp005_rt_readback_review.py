import unittest
import struct
import numpy as np
from exp005_rt_readback_review import audit, independent_gate, pure_bundle, decode_exr


def synthetic_exr(names=('V',)):
    def attr(name,kind,value): return name.encode()+b'\0'+kind.encode()+b'\0'+struct.pack('<i',len(value))+value
    channels=b''.join(n.encode()+b'\0'+struct.pack('<iB3sii',2,0,b'\0'*3,1,1) for n in names)+b'\0'
    header=struct.pack('<II',20000630,2)+attr('channels','chlist',channels)+attr('compression','compression',b'\0')+attr('dataWindow','box2i',struct.pack('<4i',0,0,7,7))+b'\0'
    blocks=[]; offsets=[]; at=len(header)+64
    for y in range(8):
        data=b''.join(struct.pack('<8f',*[100*i+10*y+x for x in range(8)]) for i in range(len(names)))
        block=struct.pack('<ii',y,len(data))+data; offsets.append(at); at+=len(block); blocks.append(block)
    return header+struct.pack('<8Q',*offsets)+b''.join(blocks)


class RetainedReadback(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.report=audit()

    def test_four_captures_decoded_exactly(self):
        self.assertEqual([r['fixture'] for r in self.report['captures']],['T2_cpu','T2_gpu','T32_cpu','T32_gpu'])
        self.assertTrue(all(r['independent_gate_pass'] and r['EXR_equals_JSON_exactly'] for r in self.report['captures']))
        self.assertEqual(sum(r['hits']+r['misses'] for r in self.report['captures']),256)

    def test_repaired_pure_gates(self):
        self.assertEqual(len(self.report['pure_checker_invalids_rejected']),4)
        self.assertEqual(len(self.report['pure_guard_invalids_rejected']),5)
        self.assertTrue(self.report['during_RAM_floor_4_verified'])

    def test_nonfinite_and_shape_rejected_independently(self):
        m={'res':8}
        with self.assertRaises(ValueError): independent_gate(m,np.zeros((7,8)),np.zeros((8,8)),np.zeros((8,8,3)))
        with self.assertRaises(ValueError): independent_gate(m,np.full((8,8),np.nan),np.zeros((8,8)),np.zeros((8,8,3)))

    def test_no_runtime_or_rt_promotion(self):
        self.assertFalse(self.report['launch_approved']); self.assertFalse(self.report['rt_hardware_certified'])
        self.assertEqual(self.report['C3'],'BLOCKED')

    def test_writer_call_rejected(self):
        with self.assertRaises(ValueError): pure_bundle('def probe():\n open("x","w")',('probe',),{})


class NamedEXRDecoder(unittest.TestCase):
    def test_scalar_channel_and_xyz_distinct(self):
        v=decode_exr(synthetic_exr())['V']; self.assertEqual(float(v[7,3]),73.)
        xyz=decode_exr(synthetic_exr(('X','Y','Z')))
        self.assertEqual([float(xyz[k][7,3]) for k in 'XYZ'],[73.,173.,273.])

    def test_truncated_and_unsupported_files_rejected(self):
        data=synthetic_exr()
        for bad in (data[:-1],data[:4],data[:4]+struct.pack('<I',0x202)+data[8:]):
            with self.assertRaises((ValueError,struct.error)): decode_exr(bad)


if __name__=='__main__': unittest.main()
