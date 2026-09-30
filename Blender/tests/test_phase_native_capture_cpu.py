"""CPU doubles only: evidence retention and fail-closed scalar capture adapters."""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import io
import json
import math
from pathlib import Path
import sys
import tempfile
import time
from types import SimpleNamespace as NS
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'Blender/benchmarks/capacity_audit'))
from phase_compensated_cpu_v1 import compensated_angle
from phase_native_probe_v1 import KEYS, scalar, words
from phase_native_capture_v1 import fresh_deadline, manifest, run_private_capture, validate_manifest


def synthetic_data(plan):
    output = []
    for i, case in enumerate(plan['cases']):
        if case['expected_status']:
            output.extend([0]*24+[case['expected_status'], i, 0, 0]); continue
        length = scalar(case['input_uint32'][:2]); wavelength = scalar(case['input_uint32'][2:])
        trace = compensated_angle(length, wavelength)
        for key in KEYS: output.extend([*words(trace[key]), 0, 0])
        angle = trace['angle_float32']
        output.extend([*words(math.cos(angle)), *words(math.sin(angle)), 0, i, 0, 0])
    return output


class FakeGPU:
    def __init__(self, data, *, compile_failure=False):
        self.events = []; self.data = data; self.compile_failure = compile_failure
        class Info:
            def __getattr__(self, key): return lambda *a, **kw: None
        shader = NS(uniform_sampler=lambda *a: None, image=lambda *a: None,
                    uniform_int=lambda *a: None)
        def compile(info):
            self.events.append('compile')
            if self.compile_failure: raise RuntimeError('synthetic compiler failure')
            return shader
        def texture(size, **kw):
            return NS(read=lambda: NS(to_list=lambda: list(self.data)))
        self.types = NS(GPUShaderCreateInfo=Info, GPUTexture=texture,
                        Buffer=lambda *a: None)
        self.shader = NS(create_from_info=compile)
        self.compute = NS(dispatch=lambda *a: self.events.append('dispatch'))


class NativeCaptureCPU(unittest.TestCase):
    def setUp(self): self.plan = manifest()

    def run_case(self, directory, gpu, **kw):
        return run_private_capture(gpu, self.plan, directory, lambda: None,
                                   admit=lambda: None, **kw)

    def test_twelve_preregistered_exact_word_cases(self):
        samples, statuses = validate_manifest(self.plan)
        self.assertEqual(statuses, [0]*6+[1]*4+[2]*2)
        self.assertTrue(math.isnan(samples[8][0]))
        self.assertNotIn('NaN', json.dumps(self.plan, allow_nan=False))
        for key in ('cases', 'policy', 'code_sha256'):
            corrupted = deepcopy(self.plan); corrupted[key] = {}
            with self.assertRaises(ValueError): validate_manifest(corrupted)
        corrupted = deepcopy(self.plan); corrupted['cases'][0]['expected_status'] = False
        with self.assertRaises(ValueError): validate_manifest(corrupted)

    def test_success_does_not_authenticate_gpu_or_guard(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)/'private'
            gpu = FakeGPU(synthetic_data(self.plan))
            result = self.run_case(folder, gpu)
            self.assertEqual(gpu.events, ['compile', 'dispatch'])
            self.assertEqual(len(result['decoded']['cases']), 12)
            for key in ('runtime_execution_authenticated', 'native_promotion_allowed',
                        'operational_gate_passed', 'geometry_or_scene_inference'):
                self.assertFalse(result[key])
            self.assertTrue(result['readback_retained'])
            before = (folder/'result.json').read_bytes()
            with self.assertRaises(FileExistsError): self.run_case(folder, gpu)
            self.assertEqual(before, (folder/'result.json').read_bytes())

    def test_corrupt_numeric_output_retained_before_rejection(self):
        for index in (0, 25, 6*28):
            with tempfile.TemporaryDirectory() as temp:
                folder = Path(temp)/'private'; data = synthetic_data(self.plan)
                data[index] = 12345678
                with self.assertRaises(ValueError): self.run_case(folder, FakeGPU(data))
                self.assertEqual(json.loads((folder/'raw_uint32.json').read_text()), data)
                report = json.loads((folder/'result.json').read_text())
                self.assertEqual(report['status'], 'failed')
                self.assertTrue(report['readback_retained'])

    def test_compilation_and_admission_failure_no_readback(self):
        with tempfile.TemporaryDirectory() as temp:
            gpu = FakeGPU([], compile_failure=True); folder = Path(temp)/'compile'
            with self.assertRaises(RuntimeError): self.run_case(folder, gpu)
            self.assertEqual(gpu.events, ['compile'])
            self.assertFalse((folder/'raw_uint32.json').exists())
            self.assertEqual(json.loads((folder/'result.json').read_text())['status'], 'failed')
            gpu = FakeGPU([]); folder = Path(temp)/'no-admission'
            with self.assertRaises(ValueError):
                run_private_capture(gpu, self.plan, folder, lambda: None)
            self.assertEqual(gpu.events, [])

    def test_expired_and_monotonic_deadlines(self):
        now = datetime.now(timezone.utc)
        for deadline in (now, now+timedelta(seconds=91), now.replace(tzinfo=None)):
            with self.assertRaises(ValueError): fresh_deadline(deadline, now=lambda: now)
        elapsed = [0.]; check = fresh_deadline(now+timedelta(seconds=1),
                         now=lambda: now, monotonic=lambda: elapsed[0])
        elapsed[0] = 1.
        with self.assertRaises(ValueError): check()
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)/'expired'; gpu = FakeGPU([])
            with self.assertRaises(ValueError): run_private_capture(gpu, self.plan, folder, check)
            self.assertEqual(gpu.events, []); self.assertFalse(folder.exists())

    def test_post_readback_deadline_failure_still_retains_raw(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)/'private'; gpu = FakeGPU(synthetic_data(self.plan))
            def check():
                if (folder/'raw_uint32.json').exists(): raise ValueError('synthetic late readback')
            with self.assertRaises(ValueError):
                run_private_capture(gpu, self.plan, folder, check, admit=lambda: None)
            self.assertTrue((folder/'raw_uint32.json').exists())
            self.assertEqual(json.loads((folder/'result.json').read_text())['status'], 'failed')

    def test_mandatory_storage_failure_cannot_be_success(self):
        original = Path.open
        for target in ('result.json', 'raw_uint32.json'):
            with tempfile.TemporaryDirectory() as temp:
                folder = Path(temp)/'private'; gpu = FakeGPU(synthetic_data(self.plan))
                def open_file(path, *args, **kw):
                    if path.name == target and args and args[0] == 'x':
                        raise OSError('synthetic evidence storage failure')
                    return original(path, *args, **kw)
                with patch.object(Path, 'open', open_file):
                    with self.assertRaises(OSError): self.run_case(folder, gpu)
                if target == 'result.json': self.assertEqual(gpu.events, [])
                else:
                    report = json.loads((folder/'result.json').read_text())
                    self.assertEqual(report['status'], 'failed')
                    self.assertFalse(report['readback_retained'])


def audit():
    started = time.monotonic(); plan = manifest(); before = plan['code_sha256']
    stream = io.StringIO()
    tests = unittest.TextTestRunner(stream=stream).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(NativeCaptureCPU))
    if not tests.wasSuccessful(): raise AssertionError(stream.getvalue())
    after = manifest()['code_sha256']
    if before != after: raise AssertionError('input pins changed')
    pins = dict(before); pins[str(Path(__file__))] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    return {'task_id': 'PHASE-NATIVE-CAPTURE-001-CODEX',
            'timestamp_utc': datetime.now(timezone.utc).isoformat(), 'tests': tests.testsRun,
            'seconds': time.monotonic()-started, 'test_output': stream.getvalue(),
            'code_sha256': pins, 'CPU_doubles_only': True,
            'GPU_compilation_verified': False, 'GPU_dispatch_verified': False,
            'Bpy_executed': False, 'native_promotion_allowed': False,
            'operational_guard_verified': False, 'no_jev_aval': True}


if __name__ == '__main__': print(json.dumps(audit(), indent=2))
