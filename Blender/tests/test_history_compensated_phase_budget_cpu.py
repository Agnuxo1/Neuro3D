"""Small composed-budget tests; no frozen suites, peer writers, Blender/GPU."""
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import io
import json
from pathlib import Path
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'Blender/benchmarks/capacity_audit'))
sys.path.insert(0, str(ROOT/'Blender/tests'))
from exp005_history_mzi_audit import fixture
from phase_compensated_cpu_v1 import compensated_angle
from history_compensated_phase_budget_cpu_v1 import interval_phase_bound, scene_compensated_phase_budget


def upper(record): return F(*record['rational_upper'])


def run_scene(*, two=False, independent=False, large=False, wavelength=.125):
    scene, _ = fixture(); scene['lambda_BU'] = wavelength
    if large: scene['objects']['Dx']['mode_origin_BU'][0] = 999999.875+2**-22
    source_id = scene['sources'][0]['id']; groups = {source_id: 'g0'}
    if two:
        second = deepcopy(scene['sources'][0]); second['id'] = 'source_extra'
        scene['sources'].append(second); groups['source_extra'] = 'g1' if independent else 'g0'
    return scene_compensated_phase_budget(scene, coherence_groups=groups,
        field_budget=1e-4, intensity_budget=2e-4, relative_budget=1e-12)


class ComposedPhaseCPU(unittest.TestCase):
    def test_scene_controls_and_no_pruning(self):
        single = run_scene(); self.assertEqual(single['generated_record_count'], 13)
        self.assertEqual(len(single['ledger']), 4)
        self.assertTrue(single['accepted_input_and_phase_arithmetic_only'])
        self.assertFalse(single['native_promotion_allowed'])

    def test_coherence_power_rule(self):
        one = run_scene(wavelength=.1)
        coherent = run_scene(two=True, wavelength=.1)
        separate = run_scene(two=True, independent=True, wavelength=.1)
        self.assertEqual(coherent['generated_record_count'], 26)
        self.assertEqual(len(coherent['ledger']), 8)
        for port in one['ports']:
            p = upper(one['ports'][port]['intensity_error_upper'])
            self.assertGreater(p, 0)  # Do not prove 4x/2x by comparing zeros.
            self.assertEqual(upper(coherent['ports'][port]['intensity_error_upper']), 4*p)
            self.assertEqual(upper(separate['ports'][port]['intensity_error_upper']), 2*p)

    def test_F1_scene_and_general_lambda(self):
        for result in (run_scene(large=True, wavelength=3*2.**-20),
                       run_scene(wavelength=.1)):
            self.assertTrue(result['accepted_input_and_phase_arithmetic_only'])
            self.assertFalse(result['native_precision_certified'])

    def test_unsupported_long_general_case_rejects(self):
        with self.assertRaises(ValueError):
            run_scene(large=True, wavelength=1.00416693877201e-12)

    def test_full_turn_interval_does_not_wrap_endpoints(self):
        trace = compensated_angle(1., 1.)
        bound = interval_phase_bound(1., 1., trace, length_interval=(F(0), F(2)),
                                    lambda_interval=(F(1), F(1)), field_budget=1e-4)
        self.assertEqual(upper(bound['ideal_unit_phase_error_upper']), 2)

    def test_inverted_or_nonpositive_enclosures_reject(self):
        trace = compensated_angle(1., 1.)
        for length_range, wavelength_range in (((2, 1), (1, 1)), ((0, 2), (0, 1)), ((0, 2), (2, 1))):
            with self.assertRaises(ValueError):
                interval_phase_bound(1., 1., trace, length_interval=length_range,
                                     lambda_interval=wavelength_range, field_budget=1e-4)


def audit():
    started = time.monotonic()
    retained = ROOT/'coordinacion/respuestas/PHASE-CIRCULAR-001-CODEX.json'
    if hashlib.sha256(retained.read_bytes()).hexdigest() != '697a5921e9361b8eb91bf74174a994be1ce23ead8bf0a4dbfb6340d65f98dc2b':
        raise ValueError('circular baseline changed')
    baseline = json.loads(retained.read_text())
    for name, sha in baseline['code_sha256'].items():
        if hashlib.sha256(Path(name).read_bytes()).hexdigest() != sha:
            raise ValueError('frozen baseline code changed')
    names = ('history_compensated_phase_budget_cpu_v1.py', 'history_wavelength_field_budget_v1.py',
             'history_trace_cpu_v1.py', 'history_lengths_cpu_v1.py', 'phase_transport_budget_v1.py')
    paths = [ROOT/'Blender/benchmarks/capacity_audit'/n for n in names]
    paths += [Path(__file__), ROOT/'Blender/tests/exp005_history_mzi_audit.py', retained]
    pins = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    stream = io.StringIO(); tests = unittest.TextTestRunner(stream=stream).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(ComposedPhaseCPU))
    if not tests.wasSuccessful(): raise AssertionError(stream.getvalue())
    scenarios = [('one', {'wavelength': .1}), ('two_coherent', {'two': True, 'wavelength': .1}),
                 ('two_independent', {'two': True, 'independent': True, 'wavelength': .1}),
                 ('F1_scene', {'large': True, 'wavelength': 3*2.**-20}),
                 ('general_lambda', {'wavelength': .1})]
    rows = []
    for label, options in scenarios:
        result = run_scene(**options)
        # Keep the retained audit bounded: exact rationals remain reproducible
        # from pinned code/options and are bound by the full-result digest.
        compact_ports = {}
        for port, output in result['ports'].items():
            compact_ports[port] = {
                'intensity_error_upper': output['intensity_error_upper']['outward_float_BU'][1],
                'intensity_budget_satisfied': output['intensity_budget_satisfied'],
                'exact_bounds_sha256': hashlib.sha256(json.dumps(output, sort_keys=True).encode()).hexdigest(),
                'groups': {group: {
                    'path_count': bound['path_count'],
                    'field_error_upper': bound['field_error_upper']['outward_float_BU'][1],
                    'intensity_error_upper': bound['intensity_error_upper']['outward_float_BU'][1],
                    'field_budget_satisfied': bound['field_budget_satisfied'],
                } for group, bound in output['groups'].items()},
            }
        rows.append({'case': label, 'scene_binding_sha256': result['scene_binding_sha256'],
                     'fixture_options': options,
                     'full_result_sha256': hashlib.sha256(json.dumps(result, sort_keys=True).encode()).hexdigest(),
                     'generated_record_count': result['generated_record_count'],
                     'terminal_paths': len(result['ledger']), 'ports': compact_ports,
                     'accepted_input_and_phase_arithmetic_only': result['accepted_input_and_phase_arithmetic_only'],
                     'native_promotion_allowed': False})
    for path in paths:
        if hashlib.sha256(path.read_bytes()).hexdigest() != pins[str(path)]:
            raise ValueError('input changed during audit')
    return {'task_id': 'PHASE-COMPOSED-001-CODEX', 'timestamp_utc': datetime.now(timezone.utc).isoformat(),
            'tests': tests.testsRun, 'test_output': stream.getvalue(), 'cases': rows,
            'seconds': time.monotonic()-started, 'code_sha256': pins,
            'baseline_code_sha256': baseline['code_sha256'],
            'field_threshold_unchanged': 1e-4, 'power_threshold_unchanged': 2e-4,
            'native_promotion_allowed': False, 'CPU_paths_supplied_to_GPU': False,
            'scope': 'conditional ideal represented CPU scene and exact bound composition, not native precision',
            'no_jev_aval': True}


if __name__ == '__main__': print(json.dumps(audit(), indent=2))
