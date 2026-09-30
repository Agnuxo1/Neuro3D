"""New signed-reference capability, frozen native/nonnegative suites untouched."""
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction as F
import cmath
import hashlib
import io
import json
import math
from pathlib import Path
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'Blender/benchmarks/capacity_audit'))
from exp005_history_mzi_audit import fixture
from phase_compensated_cpu_v1 import compensated_angle
from history_compensated_phase_budget_cpu_v1 import scene_compensated_phase_budget
from history_signed_phase_budget_cpu_v1 import signed_angle, signed_scalar_budget, signed_interval_budget, scene_signed_phase_budget
from history_trace_cpu_v1 import trace_scene
from history_fields_cpu_v1 import ideal_fields

SCALARS = [(-1e-9, .125), (-.5, .125), (-1000., .125),
           (-math.nextafter(.5, 0.), 1.), (-.5, 1.),
           (-math.nextafter(.5, 1.), 1.),
           (-1000001.8750002384, 3*2.**-20), (0., .125)]


def upper(encoded): return F(*encoded['rational_upper'])


def scalar_case(length, wavelength):
    trace = signed_angle(length, wavelength)
    bound = signed_scalar_budget(length, wavelength, trace, field_budget=1e-4)
    turns = F(length)/F(wavelength)
    reduced = turns-((turns+F(1, 2))//1)
    observed = abs(cmath.exp(1j*trace['angle_float32'])-cmath.exp(1j*math.tau*float(reduced)))
    if observed > bound['ideal_unit_phasor_error_upper_float']+1e-13:
        raise AssertionError('CPU libm diagnostic exceeds rational bound plus diagnostic-only slack')
    return {'length_BU': length, 'lambda_BU': wavelength, 'trace': trace,
            'budget': bound, 'CPU_libm_diagnostic_error': observed}


def scene_case(two=False, independent=False, negative=True):
    snap, _ = fixture()
    snap['lambda_BU'] = .1
    if negative: snap['objects']['Dx']['mode_origin_BU'][0] = -5.03125
    groups = {'s': 'g'}
    if two:
        src = deepcopy(snap['sources'][0]); src['id'] = 'second'
        snap['sources'].append(src); groups['second'] = 'h' if independent else 'g'
    kwargs = dict(coherence_groups=groups, field_budget=1e-4,
                  intensity_budget=2e-4, relative_budget=1e-12)
    result = scene_signed_phase_budget(snap, **kwargs)
    oracle = ideal_fields(snap, trace_scene(snap)['records'], coherence_groups=groups)
    coefficients = {p['id']: complex(*p['amplitude_before_propagation']) for p in oracle['ledger']}
    fields = {p: {g: 0j for g in info['groups']} for p, info in oracle['ports'].items()}
    for path in result['ledger']:
        angle = path['CPU_signed_phase_trace']['angle_float32']
        fields[path['port']][path['coherence_group']] += coefficients[path['id']]*cmath.exp(1j*angle)
    errors = {p: {g: abs(z-complex(*oracle['ports'][p]['groups'][g]['field_reim']))
                  for g, z in groups_out.items()} for p, groups_out in fields.items()}
    for p, group_errors in errors.items():
        for g, error in group_errors.items():
            if error > float(upper(result['ports'][p]['groups'][g]['field_error_upper']))+1e-13:
                raise AssertionError('CPU field diagnostic outside conditional bound')
    return snap, kwargs, result, errors


class SignedPhaseCPU(unittest.TestCase):
    def test_scalar_conjugation_and_retained_negatives(self):
        for length, wavelength in SCALARS:
            row = scalar_case(length, wavelength)
            positive = signed_angle(abs(length), wavelength)
            self.assertEqual(row['trace']['angle_float32'], (-1 if length < 0 else 1)*positive['angle_float32'])
            self.assertTrue(row['budget']['field_budget_satisfied_arithmetic_only'])
            self.assertFalse(row['budget']['native_promotion_allowed'])

    def test_forged_sign_length_angle_and_arithmetic_reject(self):
        trace = signed_angle(-1000001.8750002384, 3*2.**-20)
        for key, value in [('phase_sign', 1), ('phase_sign', True), ('effective_length_BU', 1.),
                           ('angle_float32', math.nextafter(trace['angle_float32'], math.inf))]:
            bad = deepcopy(trace); bad[key] = value
            with self.assertRaises(ValueError): signed_scalar_budget(-1000001.8750002384, 3*2.**-20, bad, field_budget=1e-4)
        bad = deepcopy(trace); bad['magnitude_trace']['quotient_binary64'] += 1
        with self.assertRaises(ValueError): signed_scalar_budget(-1000001.8750002384, 3*2.**-20, bad, field_budget=1e-4)

    def test_original_domain_rejections_not_relaxed(self):
        for length, wavelength in ((-float(2**52), 1.), (-sys.float_info.min/2, 1.),
                                   (-1., 0.), (math.nan, 1.), (-1., sys.float_info.min/2)):
            with self.assertRaises(ValueError): signed_angle(length, wavelength)
        with self.assertRaises(ValueError): compensated_angle(-.5, .125)
        row = signed_scalar_budget(-4.03125, .125, signed_angle(-4.03125, .125), field_budget=0.)
        self.assertFalse(row['field_budget_satisfied_arithmetic_only'])

    def test_signed_intervals_zero_crossing_and_full_turn(self):
        trace = signed_angle(-1., 1.)
        result = signed_interval_budget(-1., 1., trace, length_interval=(-2, 0),
                                        lambda_interval=(1, 1), field_budget=1e-4)
        self.assertEqual(upper(result['ideal_unit_phase_error_upper']), 2)
        result = signed_interval_budget(0., 1., signed_angle(0., 1.), length_interval=(-1, 1),
                                        lambda_interval=(1, 1), field_budget=1e-4)
        self.assertEqual(upper(result['ideal_unit_phase_error_upper']), 2)
        for lrange, wrange in (((0, -2), (1, 1)), ((-2, 0), (0, 1))):
            with self.assertRaises(ValueError): signed_interval_budget(-1., 1., trace, length_interval=lrange, lambda_interval=wrange, field_budget=1e-4)

    def test_positive_control_identical_to_frozen_composition(self):
        snap, kwargs, result, _ = scene_case(negative=False)
        frozen = scene_compensated_phase_budget(snap, **kwargs)
        self.assertEqual(result['ports'], frozen['ports'])

    def test_negative_reference_complete_without_geometry_change(self):
        snap, kwargs, result, _ = scene_case()
        self.assertEqual(result['generated_record_count'], 13)
        self.assertEqual(len(result['ledger']), 4)
        self.assertTrue(result['accepted_input_and_phase_arithmetic_only'])
        lengths = [p['represented_effective_length_BU'] for p in result['ledger'] if p['port'] == 'Dx']
        self.assertTrue(lengths and all(x < 0 for x in lengths))
        with self.assertRaises(ValueError): scene_compensated_phase_budget(snap, **kwargs)

    def test_coherence_groups_complete_and_power_addition(self):
        one = scene_case()[2]; coherent = scene_case(two=True)[2]; separate = scene_case(two=True, independent=True)[2]
        for result in (coherent, separate):
            self.assertEqual(result['generated_record_count'], 26)
            self.assertEqual(len(result['ledger']), 8)
            self.assertTrue(result['accepted_input_and_phase_arithmetic_only'])
        for p in one['ports']:
            power = upper(one['ports'][p]['intensity_error_upper'])
            self.assertGreater(power, 0)
            self.assertEqual(upper(coherent['ports'][p]['intensity_error_upper']), 4*power)
            self.assertEqual(upper(separate['ports'][p]['intensity_error_upper']), 2*power)


def audit():
    started = time.monotonic()
    names = ('history_signed_phase_budget_cpu_v1.py', 'phase_compensated_cpu_v1.py',
             'phase_circular_budget_cpu_v1.py', 'history_compensated_phase_budget_cpu_v1.py',
             'history_wavelength_field_budget_v1.py', 'history_trace_cpu_v1.py',
             'history_fields_cpu_v1.py', 'history_lengths_cpu_v1.py')
    paths = [ROOT/'Blender/benchmarks/capacity_audit'/n for n in names]
    paths += [Path(__file__), ROOT/'Docs/EXP-005-SIGNED-PHASE-CPU-V1.md',
              ROOT/'Blender/tests/exp005_history_mzi_audit.py',
              ROOT/'coordinacion/respuestas/PHASE-COMPENSATED-CRITIQUE-CLAUDE.json',
              ROOT/'Blender/shaders/exp005_phase_compensated_probe.glsl',
              ROOT/'Blender/shaders/exp005_shared_frontier.glsl']
    pins = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    expected = {str(paths[1]): '32c0ceb114e6cd0bee8886dcec142c0b68a89091b7b0481440a7cd2b05b6c577',
                str(paths[-2]): 'd116b8c18d80dae32092aee453ecb0ff9523b8decf9fc5ef106e0ede9e23ed6c',
                str(paths[-1]): '914bf2962ead3c6a7b721a8dc2aa6c1e796af4bde1892db1802c3ca93ebdfcd1'}
    if any(pins[p] != sha for p, sha in expected.items()): raise ValueError('frozen candidate/shader changed')
    stream = io.StringIO()
    tests = unittest.TextTestRunner(stream=stream).run(unittest.defaultTestLoader.loadTestsFromTestCase(SignedPhaseCPU))
    scenes = []
    for label, options in [('negative_single', {}), ('negative_coherent', {'two': True}),
                           ('negative_independent', {'two': True, 'independent': True}),
                           ('positive_control', {'negative': False})]:
        snap, _, result, errors = scene_case(**options)
        compact_ports = {p: {'intensity_error_upper': data['intensity_error_upper']['outward_float_BU'][1],
                            'groups': {g: {'path_count': b['path_count'],
                                           'field_error_upper': b['field_error_upper']['outward_float_BU'][1],
                                           'intensity_error_upper': b['intensity_error_upper']['outward_float_BU'][1]}
                                       for g, b in data['groups'].items()}}
                         for p, data in result['ports'].items()}
        scenes.append({'label': label, 'snapshot': snap, 'records': result['generated_record_count'],
                       'paths': len(result['ledger']), 'ports': compact_ports,
                       'effective_lengths_BU': [p['represented_effective_length_BU'] for p in result['ledger']],
                       'observed_CPU_libm_field_errors': errors,
                       'full_conditional_result_sha256': hashlib.sha256(json.dumps(result, sort_keys=True).encode()).hexdigest(),
                       'accepted_input_and_phase_arithmetic_only': result['accepted_input_and_phase_arithmetic_only']})
    if any(hashlib.sha256(Path(p).read_bytes()).hexdigest() != sha for p, sha in pins.items()):
        raise ValueError('input changed during audit')
    scalar_rows = []
    for pair in SCALARS:
        full = scalar_case(*pair)
        scalar_rows.append({'length_BU': full['length_BU'], 'lambda_BU': full['lambda_BU'],
                            'trace': full['trace'],
                            'ideal_phasor_error_upper': full['budget']['ideal_unit_phasor_error_upper_float'],
                            'CPU_libm_diagnostic_error': full['CPU_libm_diagnostic_error'],
                            'full_rational_budget_sha256': hashlib.sha256(json.dumps(full['budget'], sort_keys=True).encode()).hexdigest()})
    return {'task_id': 'PHASE-SIGNED-001-CODEX', 'timestamp_utc': datetime.now(timezone.utc).isoformat(),
            'tests': tests.testsRun, 'tests_successful': tests.wasSuccessful(), 'test_output': stream.getvalue(),
            'seconds': time.monotonic()-started, 'code_sha256': pins, 'scalars': scalar_rows,
            'scenes': scenes, 'field_threshold_unchanged': 1e-4, 'power_threshold_unchanged': 2e-4,
            'CPU_libm_diagnostic_slack_only': 1e-13, 'native_promotion_allowed': False,
            'GPU_executed': False, 'Bpy_executed': False, 'no_jev_aval': True,
            'scope': 'conditional signed CPU phase/reference capability; no native precision or speed claims'}


if __name__ == '__main__':
    result = audit(); print(json.dumps(result, indent=2, allow_nan=False))
    sys.exit(0 if result['tests_successful'] else 1)
