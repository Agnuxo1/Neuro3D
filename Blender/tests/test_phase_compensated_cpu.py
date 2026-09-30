"""Tiny stdlib tests and retained scalar audit; no scene/peer writer/GPU."""
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import io
import json
import math
from pathlib import Path
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'Blender/benchmarks/capacity_audit'))
from phase_compensated_cpu_v1 import compensated_angle

PEER = ROOT / 'coordinacion/respuestas/PRECISION-006-REDUCTION-CLAUDE.json'
PEER_SHA = '0d1a1eaa981f2cb60261e3563c85a8721d499fd6967605025684c3b9903e9609'
SHADER = ROOT / 'Blender/shaders/exp005_shared_frontier.glsl'
SHADER_SHA = '914bf2962ead3c6a7b721a8dc2aa6c1e796af4bde1892db1802c3ca93ebdfcd1'


def scalar_check(length, wavelength):
    result = compensated_angle(float(length), float(wavelength))
    exact = F(length) / F(wavelength)
    exact -= (exact + F(1, 2)) // 1
    difference = F(result['reduced_cycles_binary64']) - exact
    difference -= (difference + F(1, 2)) // 1
    reference = math.tau * float(exact)
    observed = complex(math.cos(result['angle_float32']), math.sin(result['angle_float32']))
    target = complex(math.cos(reference), math.sin(reference))
    return {'L_BU': float(length), 'lambda_BU': float(wavelength),
            'exact_reduced_turns': [exact.numerator, exact.denominator],
            'cycle_error_rational': [difference.numerator, difference.denominator],
            'CPU_unit_field_error': abs(observed - target), **result}


class CompensatedCPU(unittest.TestCase):
    def test_exact_zero_and_quarter(self):
        for length in (0., 4., 4.03125):
            self.assertLess(scalar_check(length, .125)['CPU_unit_field_error'], 1e-4)

    def test_peer_F1_and_fraction_boundary(self):
        for length in (1000001.8750002384, 1000.0625, .5, 1.5):
            self.assertLess(scalar_check(length, 3*2.**-20)['CPU_unit_field_error'], 1e-4)

    def test_general_lambda_inside_domain(self):
        self.assertLess(scalar_check(1000.0625, 1.00416693877201e-12)['CPU_unit_field_error'], 1e-4)

    def test_cap_is_fail_closed(self):
        for length, wavelength in ((float(2**52), 1.), (1e6, 1e-12), (1., 1e-308)):
            with self.assertRaises(ValueError):
                compensated_angle(length, wavelength)

    def test_invalid_inputs(self):
        for length, wavelength in ((-1., .125), (1., 0.), (1., -1.),
                                   (math.inf, 1.), (1., math.nan), (True, 1.),
                                   (5e-324, 1.), (1., 5e-324), (0., 0.)):
            with self.assertRaises(ValueError):
                compensated_angle(length, wavelength)

    def test_FMA_required(self):
        original = math.fma
        try:
            math.fma = None
            with self.assertRaises(ValueError):
                compensated_angle(4., .125)
        finally:
            math.fma = original

    def test_no_underflow_fallback(self):
        with self.assertRaises(ValueError):
            compensated_angle(sys.float_info.min, sys.float_info.max)


def audit():
    start = time.monotonic()
    paths = [PEER, SHADER, Path(__file__),
             ROOT / 'Blender/benchmarks/capacity_audit/phase_compensated_cpu_v1.py']
    pins = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    if pins[str(PEER)] != PEER_SHA or pins[str(SHADER)] != SHADER_SHA:
        raise ValueError('frozen input changed')
    stream = io.StringIO()
    tests = unittest.TextTestRunner(stream=stream).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(CompensatedCPU))
    if not tests.wasSuccessful():
        raise AssertionError(stream.getvalue())
    peer = json.loads(PEER.read_text())
    rows = [scalar_check(c['L_BU'], c['lambda']) for c in peer['cases']]
    rows.append(scalar_check(1000.0625, 1.00416693877201e-12))
    rejections = []
    for length, wavelength in ((1000001.8750002384, 1.00416693877201e-12),
                               (float(2**52), 1.)):
        try:
            compensated_angle(length, wavelength)
        except ValueError as error:
            rejections.append({'L_BU': length, 'lambda_BU': wavelength,
                               'reason': str(error), 'field_emitted': False})
        else:
            raise AssertionError('outside-domain case silently accepted')
    if any(r['CPU_unit_field_error'] >= 1e-4 for r in rows):
        raise AssertionError('new candidate scalar gate failed')
    for p in paths:
        if hashlib.sha256(p.read_bytes()).hexdigest() != pins[str(p)]:
            raise ValueError('input changed during audit')
    return {'timestamp_utc': datetime.now(timezone.utc).isoformat(),
            'tests': tests.testsRun, 'test_output': stream.getvalue(),
            'cases': rows, 'outside_domain_rejections': rejections,
            'seconds': time.monotonic()-start,
            'code_sha256': pins, 'field_threshold_unchanged': 1e-4,
            'maximum_CPU_unit_field_error': max(r['CPU_unit_field_error'] for r in rows),
            'scope': 'represented scalar CPU FMA candidate only; no scene/driver/libm certificate',
            'native_promotion_allowed': False, 'peer_writer_executed': False,
            'no_jev_aval': True}


if __name__ == '__main__':
    print(json.dumps(audit(), indent=2))
