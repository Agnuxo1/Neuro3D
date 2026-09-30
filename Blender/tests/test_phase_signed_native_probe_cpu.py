"""New signed native preparation CPU only; no compilation/import GPU."""
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

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'Blender/benchmarks/capacity_audit'))
from phase_signed_native_probe_v1 import pilot_cases, decode, dispatch_signed_probe, SHADER
from phase_native_probe_v1 import scalar, words, KEYS, pack_samples
from history_signed_phase_budget_cpu_v1 import signed_angle


def inputs():
    cases = pilot_cases()
    return [(scalar(c['input_uint32'][:2]), scalar(c['input_uint32'][2:])) for c in cases], [c['expected_status'] for c in cases]


def synthetic():
    pairs, statuses = inputs(); output = []
    for i, ((length, wavelength), status) in enumerate(zip(pairs, statuses)):
        if status:
            output.extend([0]*24+[status, i, 0, 0]); continue
        trace = signed_angle(length, wavelength)
        magnitude = trace['magnitude_trace']
        for key in KEYS:
            value = trace['angle_float32'] if key == 'angle_float32' else magnitude[key]
            output.extend((*words(value), 0, 0))
        angle = trace['angle_float32']
        output.extend((*words(math.cos(angle)), *words(math.sin(angle)), 0, i, 0, 0))
    return output


class SignedNativeCPU(unittest.TestCase):
    def test_exact_words_and_manifest_12cases(self):
        cases = pilot_cases(); pairs, _ = inputs(); packed = pack_samples(pairs)
        self.assertEqual(len(cases), 12)
        for i, c in enumerate(cases): self.assertEqual(packed[4*i:4*i+4], c['input_uint32'])
        self.assertEqual(struct.pack('<d', scalar(words(-0.))), struct.pack('<d', -0.))

    def test_eight_synthetic_successes_not_native_evidence(self):
        pairs, statuses = inputs(); output = decode(pairs, synthetic(), expected_statuses=statuses)
        self.assertEqual(sum(c['status'] == 0 for c in output['cases']), 8)
        for k in ('runtime_execution_authenticated', 'native_promotion_allowed', 'geometry_or_scene_inference'):
            self.assertFalse(output[k])

    def test_four_preregistered_aborts_without_partial_output(self):
        pairs, statuses = inputs(); data = synthetic()
        out = decode(pairs, data, expected_statuses=statuses)
        self.assertEqual([c['status'] for c in out['cases'][8:]], [2, 1, 1, 1])
        self.assertTrue(all(not c['field_emitted'] for c in out['cases'][8:]))
        data[8*28] = 1
        with self.assertRaises(ValueError): decode(pairs, data, expected_statuses=statuses)

    def test_corrupt_signed_angle_field_and_magnitude_reject(self):
        pairs, statuses = inputs(); original = synthetic()
        for offset, value in [(16, -signed_angle(*pairs[0])['angle_float32']), (0, 42.), (20, 10.)]:
            data = original.copy(); data[offset:offset+2] = words(value)
            with self.assertRaises(ValueError): decode(pairs, data, expected_statuses=statuses)

    def test_shape_identity_padding_uint_and_status_reject(self):
        pairs, statuses = inputs(); original = synthetic()
        with self.assertRaises(ValueError): decode(pairs, original[:-1], expected_statuses=statuses)
        for offset, value in [(25, 99), (2, 1), (0, True), (24, 1)]:
            data = original.copy(); data[offset] = value
            with self.assertRaises(ValueError): decode(pairs, data, expected_statuses=statuses)
        with self.assertRaises(ValueError): decode(pairs, original, expected_statuses=[True]*12)
        with self.assertRaises(ValueError): pack_samples([(1., 1.)]*17)

    def test_external_deadline_raw_retention_mandatory_before_gpu(self):
        pairs, statuses = inputs()
        def expired(): raise ValueError('deadline expired')
        with self.assertRaisesRegex(ValueError, 'deadline expired'):
            dispatch_signed_probe(object(), pairs, statuses, expired, lambda _: None)
        with self.assertRaises(ValueError): dispatch_signed_probe(object(), pairs, statuses, lambda: None, None)

    def test_shader_text_only_signed_not_compiled(self):
        source = SHADER.read_text()
        for token in ('double length = abs(effective)', 'if (effective<0.0lf) angle=-angle',
                      'fma(-quotient,wavelength,length)', 'precise double', 'packDouble2x32'):
            self.assertIn(token, source)
        self.assertNotIn('ray_cast', source)


def audit():
    start = time.monotonic()
    paths = [Path(__file__), SHADER, ROOT/'Docs/EXP-005-SIGNED-NATIVE-PREP-V1.md']
    paths += [ROOT/'Blender/benchmarks/capacity_audit'/n for n in (
        'phase_signed_native_probe_v1.py', 'phase_native_probe_v1.py',
        'history_signed_phase_budget_cpu_v1.py', 'phase_compensated_cpu_v1.py',
        'phase_circular_budget_cpu_v1.py')]
    paths += [ROOT/'Blender/shaders/exp005_phase_compensated_probe.glsl',
              ROOT/'coordinacion/respuestas/PHASE-SIGNED-001-CODEX.json']
    pins = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    if pins[str(paths[-2])] != 'd116b8c18d80dae32092aee453ecb0ff9523b8decf9fc5ef106e0ede9e23ed6c':
        raise ValueError('frozen nonnegative shader changed')
    stream = io.StringIO()
    tests = unittest.TextTestRunner(stream=stream).run(unittest.defaultTestLoader.loadTestsFromTestCase(SignedNativeCPU))
    pairs, statuses = inputs(); output = decode(pairs, synthetic(), expected_statuses=statuses)
    if any(hashlib.sha256(Path(p).read_bytes()).hexdigest() != s for p, s in pins.items()):
        raise ValueError('input changed during audit')
    return {'task_id': 'PHASE-SIGNED-NATIVE-PREP-001-CODEX',
            'timestamp_utc': datetime.now(timezone.utc).isoformat(), 'seconds': time.monotonic()-start,
            'tests': tests.testsRun, 'tests_successful': tests.wasSuccessful(), 'test_output': stream.getvalue(),
            'code_sha256': pins, 'pilot_cases_exact_uint32': pilot_cases(),
            'valid_cases': 8, 'abort_cases': 4,
            'max_synthetic_unit_field_error': max(c.get('unit_field_error_vs_CPU_libm', 0.) for c in output['cases']),
            'max_synthetic_point_bound': max(c.get('point_arithmetic_bound', {}).get('ideal_unit_phasor_error_upper_float', 0.) for c in output['cases']),
            'GPU_compilation_verified': False, 'GPU_dispatch_verified': False, 'Bpy_executed': False,
            'operational_admission_granted': False, 'native_promotion_allowed': False,
            'no_jev_aval': True, 'scope': 'signed CPU exact-word ABI/decoder and GLSL text, not native execution'}


if __name__ == '__main__':
    result = audit(); print(json.dumps(result, indent=2, allow_nan=False))
    sys.exit(0 if result['tests_successful'] else 1)
