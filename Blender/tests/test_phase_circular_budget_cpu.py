"""Focused point-trace bounds, branch cuts and tampered arithmetic negatives."""
from copy import deepcopy
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
from phase_circular_budget_cpu_v1 import scalar_circular_budget


def check(length, wavelength):
    trace = compensated_angle(length, wavelength)
    budget = scalar_circular_budget(length, wavelength, trace, field_budget=1e-4)
    q = F(length)/F(wavelength)
    q -= (q+F(1, 2))//1
    exact_angle = math.tau*float(q)
    observed = abs(complex(math.cos(trace['angle_float32']), math.sin(trace['angle_float32']))
                   - complex(math.cos(exact_angle), math.sin(exact_angle)))
    # Only a libm diagnostic; never added to the rational bound or field gate.
    if observed > budget['ideal_unit_phasor_error_upper_float'] + 1e-13:
        raise AssertionError('CPU libm diagnostic outside bound')
    if not budget['field_budget_satisfied_arithmetic_only']:
        raise AssertionError('point-trace arithmetic bound too large')
    return {'L_BU': length, 'lambda_BU': wavelength,
            'observed_CPU_libm_field_difference': observed, **budget}


class CircularBudgetCPU(unittest.TestCase):
    def test_point_controls(self):
        for length, wavelength in ((0., .125), (4.03125, .125),
                                   (1000001.8750002384, 3*2.**-20),
                                   (1000.0625, 1.00416693877201e-12)):
            self.assertFalse(check(length, wavelength)['native_promotion_allowed'])

    def test_branch_cut_and_boundary(self):
        for length in (math.nextafter(.5, 0.), .5, math.nextafter(.5, 1.), 1.5):
            check(length, 1.)

    def test_forged_steps_reject(self):
        trace = compensated_angle(1000001.8750002384, 3*2.**-20)
        for key in ('quotient_binary64', 'residual_binary64', 'correction_binary64',
                    'reduced_cycles_binary64', 'angle_float32'):
            bad = deepcopy(trace); bad[key] = math.nextafter(bad[key], math.inf)
            with self.assertRaises(ValueError):
                scalar_circular_budget(1000001.8750002384, 3*2.**-20, bad, field_budget=1e-4)
        bad = deepcopy(trace); bad['angle_float32'] = math.nan
        with self.assertRaises(ValueError):
            scalar_circular_budget(1000001.8750002384, 3*2.**-20, bad, field_budget=1e-4)

    def test_zero_budget_not_relaxed(self):
        trace = compensated_angle(4.03125, .125)
        result = scalar_circular_budget(4.03125, .125, trace, field_budget=0.)
        self.assertFalse(result['field_budget_satisfied_arithmetic_only'])

    def test_residual_rounded_to_zero_not_claimed_exact(self):
        length = sys.float_info.min
        wavelength = math.nextafter(length, math.inf)
        trace = compensated_angle(length, wavelength)
        self.assertEqual(trace['residual_binary64'], 0.)
        self.assertNotEqual(F(length)-F(trace['quotient_binary64'])*F(wavelength), 0)
        bound = check(length, wavelength)
        self.assertNotEqual(bound['cycle_error_circular_rational'][0], 0)

    def test_outside_domain_and_nontrace_reject(self):
        for length, wavelength, trace in ((sys.float_info.max, sys.float_info.min, {}),
                                         (float(2**52), 1., {}), (1., 1., [])):
            with self.assertRaises(ValueError):
                scalar_circular_budget(length, wavelength, trace, field_budget=1e-4)


def audit():
    started = time.monotonic()
    paths = [Path(__file__), ROOT/'Blender/benchmarks/capacity_audit/phase_circular_budget_cpu_v1.py',
             ROOT/'Blender/benchmarks/capacity_audit/phase_compensated_cpu_v1.py',
             ROOT/'Blender/shaders/exp005_shared_frontier.glsl']
    pins = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    if pins[str(paths[2])] != '32c0ceb114e6cd0bee8886dcec142c0b68a89091b7b0481440a7cd2b05b6c577':
        raise ValueError('candidate changed')
    if pins[str(paths[3])] != '914bf2962ead3c6a7b721a8dc2aa6c1e796af4bde1892db1802c3ca93ebdfcd1':
        raise ValueError('frozen shader changed')
    stream = io.StringIO()
    tests = unittest.TextTestRunner(stream=stream).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(CircularBudgetCPU))
    if not tests.wasSuccessful(): raise AssertionError(stream.getvalue())
    rows = [check(length, wavelength) for length, wavelength in
            ((0., .125), (4.03125, .125), (1000001.8750002384, 3*2.**-20),
             (1000.0625, 1.00416693877201e-12), (math.nextafter(.5, 0.), 1.),
             (.5, 1.), (math.nextafter(.5, 1.), 1.), (1.5, 1.),
             (sys.float_info.min, math.nextafter(sys.float_info.min, math.inf)))]
    for p in paths:
        if hashlib.sha256(p.read_bytes()).hexdigest() != pins[str(p)]:
            raise ValueError('pin changed during audit')
    return {'task_id': 'PHASE-CIRCULAR-001-CODEX',
            'timestamp_utc': datetime.now(timezone.utc).isoformat(),
            'tests': tests.testsRun, 'test_output': stream.getvalue(),
            'cases': rows, 'seconds': time.monotonic()-started, 'code_sha256': pins,
            'maximum_ideal_phasor_bound': max(r['ideal_unit_phasor_error_upper_float'] for r in rows),
            'field_threshold_unchanged': 1e-4, 'CPU_libm_diagnostic_slack_only': 1e-13,
            'native_promotion_allowed': False, 'no_jev_aval': True}


if __name__ == '__main__':
    print(json.dumps(audit(), indent=2))
