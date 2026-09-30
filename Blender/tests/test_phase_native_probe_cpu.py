"""ABI/decoder CPU-only tests for uncompiled opt-in native scalar pilot."""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import io
import json
import math
from pathlib import Path
import struct
import sys
import time
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'Blender/benchmarks/capacity_audit'))
from phase_compensated_cpu_v1 import compensated_angle
from phase_native_probe_v1 import words,scalar,pack_samples,decode,dispatch_probe,flatten,SHADER,KEYS

SAMPLES=[(0.,.125),(4.03125,.125),(1000001.8750002384,3*2.**-20),
         (1000.0625,1.00416693877201e-12),(.5,1.),(1.5,1.)]


def synthetic_rows(samples=SAMPLES):
    data=[]
    for i,(length,wavelength) in enumerate(samples):
        trace=compensated_angle(length,wavelength)
        for key in KEYS:data.extend((*words(trace[key]),0,0))
        angle=trace['angle_float32']
        data.extend((*words(math.cos(angle)),*words(math.sin(angle)),0,i,0,0))
    return data


class NativePreparationCPU(unittest.TestCase):
    def test_exact_binary64_input_roundtrip(self):
        packed=pack_samples(SAMPLES)
        for i,pair in enumerate(SAMPLES):
            for j,value in enumerate(pair):
                self.assertEqual(struct.pack('<d',scalar(packed[4*i+2*j:4*i+2*j+2])),struct.pack('<d',value))
        self.assertEqual(struct.pack('<d',scalar(words(-0.))),struct.pack('<d',-0.))

    def test_synthetic_success_not_native_evidence(self):
        result=decode(SAMPLES,synthetic_rows(),expected_statuses=[0]*len(SAMPLES))
        self.assertEqual(len(result['cases']),6)
        self.assertFalse(result['runtime_execution_authenticated'])
        self.assertFalse(result['geometry_or_scene_inference'])
        self.assertFalse(result['native_promotion_allowed'])

    def test_negative_status_and_no_partial_fields(self):
        invalid=[(-1.,.125),(float(2**52),1.)]
        data=[0]*56;data[24]=1;data[52]=2;data[53]=1
        self.assertEqual([r['status'] for r in decode(invalid,data,expected_statuses=[1,2])['cases']],[1,2])
        with self.assertRaises(ValueError):decode(invalid,data,expected_statuses=[0,2])
        data[0]=1
        with self.assertRaises(ValueError):decode(invalid,data,expected_statuses=[1,2])

    def test_corrupt_trace_shape_identity_and_padding_reject(self):
        data=synthetic_rows()
        mutations=[]
        a=data[:-1];mutations.append(a)
        for index,value in ((25,4),(2,1),(16,0x12345678),(0,True),(0,-1)):
            a=data.copy();a[index]=value;mutations.append(a)
        for variant in mutations:
            with self.assertRaises(ValueError):decode(SAMPLES,variant,expected_statuses=[0]*6)

    def test_deadline_fails_before_gpu_access(self):
        def expired():raise ValueError('expired test deadline')
        with self.assertRaisesRegex(ValueError,'expired'):
            dispatch_probe(object(),SAMPLES,[0]*6,expired)
        with self.assertRaises(ValueError):
            dispatch_probe(object(),SAMPLES,[True]*6,lambda:None)
        with self.assertRaises(ValueError):pack_samples([])
        with self.assertRaises(ValueError):pack_samples([(1.,1.)]*17)
        self.assertEqual(flatten([[[1,2],[3,4]]]),[1,2,3,4])

    def test_opt_in_shader_structure_only(self):
        text=SHADER.read_text()
        for token in ('packDouble2x32','unpackDouble2x32','fma(-quotient,wavelength,length)',
                      'precise double','status=2u','cos(angle)','sin(angle)'):
            self.assertIn(token,text)
        self.assertNotIn('ray_cast',text);self.assertNotIn('geometry_hi',text)


def audit():
    started=time.monotonic();baseline=ROOT/'coordinacion/respuestas/PHASE-CIRCULAR-001-CODEX.json'
    assert hashlib.sha256(baseline.read_bytes()).hexdigest()=='697a5921e9361b8eb91bf74174a994be1ce23ead8bf0a4dbfb6340d65f98dc2b'
    inherited=json.loads(baseline.read_text())['code_sha256']
    paths=[Path(p) for p in inherited]+[Path(__file__),SHADER,
        ROOT/'Blender/benchmarks/capacity_audit/phase_native_probe_v1.py',baseline,
        ROOT/'Blender/shaders/exp005_shared_frontier.glsl']
    pins={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    assert all(pins[p]==sha for p,sha in inherited.items())
    assert pins[str(paths[-1])]=='914bf2962ead3c6a7b721a8dc2aa6c1e796af4bde1892db1802c3ca93ebdfcd1'
    stream=io.StringIO();tests=unittest.TextTestRunner(stream=stream).run(unittest.defaultTestLoader.loadTestsFromTestCase(NativePreparationCPU))
    if not tests.wasSuccessful():raise AssertionError(stream.getvalue())
    controls=decode(SAMPLES,synthetic_rows(),expected_statuses=[0]*6)
    assert all(hashlib.sha256(p.read_bytes()).hexdigest()==pins[str(p)] for p in paths)
    return {'task_id':'PHASE-NATIVE-PREP-001-CODEX','timestamp_utc':datetime.now(timezone.utc).isoformat(),
        'tests':tests.testsRun,'test_output':stream.getvalue(),'seconds':time.monotonic()-started,
        'code_sha256':pins,'valid_scalar_controls':SAMPLES,'expected_statuses':[0]*6,
        'synthetic_max_unit_field_error':max(c['observed_unit_field_error_vs_CPU_reference'] for c in controls['cases']),
        'GPU_compilation_verified':False,'GPU_dispatch_verified':False,'Bpy_executed':False,
        'native_promotion_allowed':False,'no_jev_aval':True,
        'scope':'CPU exact-word ABI/decoder and shader text only, not native compilation/runtime or scene'}


if __name__=='__main__':print(json.dumps(audit(),indent=2))
