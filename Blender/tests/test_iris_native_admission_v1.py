"""Meaningful CPU rejection tests for the new full-circuit admission/gate.

Synthetic records exercise controls only, never count as GPU evidence.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import struct
import sys
import tempfile
from types import SimpleNamespace
import unittest
import uuid

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from Blender.benchmarks.capacity_audit import robust_first_hit_gpu_guard_v1 as base
original_gate=base.worker_gate;original_critical=base.critical_paths
from Blender.benchmarks.capacity_audit import iris_native_gpu_guard_v1 as adapter
from Blender.benchmarks.capacity_audit import iris_native_packet_v1 as packet
from Blender.benchmarks.capacity_audit.iris_native_readback_v1 import validate_result
from Blender.tests import iris_native_circuit_v1 as worker

MANIFEST=ROOT/'Docs/validation/iris-native-circuit-2026-10-08/inputs02/input_manifest.json'


def readback(nonce):
    words=[0]*(150*128)
    def double(offset,value):words[offset:offset+2]=struct.unpack('<II',struct.pack('<d',value))
    for index in range(150):
        o=index*128;words[o:o+12]=[packet.RESULT_MAGIC,1,index,1,nonce,nonce^0xffffffff,0,16,8,3,150,1]
        for offset in (12,14,86):double(o+offset,1.)
    return struct.pack('<%dI'%len(words),*words)


class Tests(unittest.TestCase):
    def setUp(self):
        self.job=worker.read(MANIFEST);self.p=worker.read(packet.packet_path(self.job['cases'][0]))

    def change_wire(self,fn):
        value=copy.deepcopy(self.p);words=list(struct.unpack('<1300I',packet.admit(value)));fn(words)
        raw=struct.pack('<1300I',*words);value.update(wire_hex=raw.hex(),wire_sha256=hashlib.sha256(raw).hexdigest());return value

    def test_original_and_controls(self):
        worker.validate_manifest(self.job)
        wires=[packet.admit(worker.read(packet.packet_path(c))) for c in self.job['cases']]
        self.assertEqual(wires[0],wires[2]);self.assertNotEqual(wires[0],wires[1])
        features=struct.unpack('<600d',wires[0][128:4928]);self.assertEqual(features[0],5.1)

    def test_import_does_not_replace_first_hit_supervisor(self):
        self.assertIs(base.worker_gate,original_gate);self.assertIs(base.critical_paths,original_critical)
        self.assertIn(Path(adapter.__file__).resolve(),adapter.critical_paths())

    def test_wrong_row_or_layout(self):
        for modify in (lambda p:p.update(rows=149),lambda p:p['layout']['features'].update(word_offset=36),lambda p:p.update(extra=True)):
            p=copy.deepcopy(self.p);modify(p)
            with self.assertRaises(ValueError):packet.admit(p)

    def test_hash_wrong(self):
        p=copy.deepcopy(self.p);p['wire_sha256']='0'*64
        with self.assertRaises(ValueError):packet.admit(p)

    def test_offset_and_padding(self):
        for fn in (lambda w:w.__setitem__(5,36),lambda w:w.__setitem__(-1,1),lambda w:w.__setitem__(4,149)):
            with self.assertRaises(ValueError):packet.admit(self.change_wire(fn))

    def test_nonfinite_and_zero_scaler(self):
        def nan(w):w[32:34]=struct.unpack('<II',struct.pack('<d',float('nan')))
        def scaler(w):w[1272:1274]=w[1264:1266]
        for fn in (nan,scaler):
            with self.assertRaises(ValueError):packet.admit(self.change_wire(fn))

    def test_duplicate_json_key(self):
        with tempfile.TemporaryDirectory(dir='D:/PROJECTS/.cognition/neuro3d-sequential-20261008') as d:
            p=Path(d)/'duplicate.json';p.write_bytes(b'{"a":1,"a":2}')
            with self.assertRaises(ValueError):worker.read(p)

    def test_full_readback_and_negative_last_sample(self):
        raw=readback(1337);self.assertEqual(len(validate_result(raw,1337)),150)
        for offset,value in ((149*128+2,148),(149*128+4,1336),(149*128+7,15),(149*128+95,1),(149*128+3,2)):
            changed=bytearray(raw);struct.pack_into('<I',changed,offset*4,value)
            with self.assertRaises(ValueError):validate_result(bytes(changed),1337)
        with self.assertRaises(ValueError):validate_result(raw[:-4],1337)
        changed=bytearray(raw);struct.pack_into('<d',changed,(149*128+18)*4,float('nan'))
        with self.assertRaises(ValueError):validate_result(bytes(changed),1337)

    def test_gate_coverage_hash_echo_and_nonce(self):
        job_id=str(uuid.uuid4());records=[];digest=hashlib.sha256()
        for case in self.job['cases']:
            nonce=int.from_bytes(hashlib.sha256((job_id+'/'+case['case_id']).encode()).digest()[:4],'little')&0x7fffffff
            wire=packet.admit(worker.read(packet.packet_path(case)));echo=wire+bytes((-len(wire))%256);raw=readback(nonce)
            records.append({'case_id':case['case_id'],'nonce':nonce,'input_echo_hex':echo.hex(),'result_hex':raw.hex()});digest.update(echo);digest.update(raw)
        report={'schema':'neuro3d.iris_lattice.native_report.v1','status':'PASS','verification_passed':True,
                'job_id':job_id,'input_manifest_sha256':packet.sha(MANIFEST),'native_gpu_executed':True,
                'backend':'OPENGL','background':False,'vendor':'NVIDIA','renderer':'RTX 3090',
                'gpu_dispatch_count':3,'completed_readbacks':3,'gpu_readback_records':records,'gpu_readback_sha256':digest.hexdigest()}
        with tempfile.TemporaryDirectory(dir='D:/PROJECTS/.cognition/neuro3d-sequential-20261008') as d:
            path=Path(d)/'synthetic_worker.json';plan=SimpleNamespace(job_id=job_id,input_sha=packet.sha(MANIFEST),input_manifest=MANIFEST)
            def gate(r):path.write_bytes(json.dumps(r).encode());return adapter.worker_gate(path,plan)
            self.assertTrue(gate(report)['native_gpu_execution_verified']) # synthetic function test only
            for modify in (lambda r:r.update(completed_readbacks=2),lambda r:r.update(gpu_readback_sha256='0'*64),
                           lambda r:r['gpu_readback_records'][2].update(nonce=1),lambda r:r.update(background=True),
                           lambda r:r['gpu_readback_records'][0].update(input_echo_hex='00'),
                           lambda r:r['gpu_readback_records'].reverse()):
                r=copy.deepcopy(report);modify(r)
                with self.assertRaises((base.Rejected,ValueError)):gate(r)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(Tests);result=unittest.TextTestRunner(verbosity=2).run(suite)
    receipt={'schema':'neuro3d.iris_lattice.cpu_admission_tests.v1','status':'PASS' if result.wasSuccessful() else 'FAIL',
             'tests':result.testsRun,'errors':len(result.errors),'failures':len(result.failures),
             'native_gpu_execution_verified':False,'scope':'CPU synthetic admission/rejection tests; zero GPU dispatches',
             'source_sha256':{p.relative_to(ROOT).as_posix():packet.sha(p) for p in (Path(__file__),Path(packet.__file__),Path(adapter.__file__))}}
    with args.out.open('xb') as stream:stream.write((json.dumps(receipt,indent=2)+'\n').encode())
    return 0 if result.wasSuccessful() else 1


if __name__=='__main__':raise SystemExit(main())
