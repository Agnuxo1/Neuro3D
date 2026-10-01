"""New plane-wave reference contract tests; retained geometry never traced."""
from copy import deepcopy
from fractions import Fraction as F
from itertools import product
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'benchmarks' / 'capacity_audit'))
import axial_terminal_reference_cpu_v1 as m


def bind_control(c):
    """Fresh explicitly synthetic HOST control; NOT prior fixture revalidation."""
    abi = c['word_ABI']
    binding = m.digest({'snapshot': c['scene_snapshot'], 'object_order': abi['object_ids'],
                        'source_order': abi['source_order']})
    abi['original_scene_binding_sha256'] = binding
    c['word_ABI_sha256'] = m.digest(abi)
    for p in c['sources']:
        if 'phase_reference_id' in p:
            p['phase_reference_id'] = 'original-source-zero:' + binding + ':' + p['source_id']
    return c


class ReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.output = m.audit(reference_model=m.MODEL, reference_frame=m.FRAME)
        _, cls.cases, cls.closure = m.load_retained()
        cls.controls = {}

    def check(self, c):
        return m.check_case(c, reference_model=m.MODEL, reference_frame=m.FRAME)

    def test_retained_ids_rejections_and_scope(self):
        a = self.output
        self.assertEqual(a['counts']['cases'], 13)
        self.assertEqual(a['counts']['sources'], 14)
        self.assertEqual(a['counts']['reference_evaluated_paths'], 9)
        self.assertEqual(a['counts']['HOST_reference_RN32_encodings'], 16)
        self.assertEqual(a['counts']['HOST_reference_RN64_subtractions'], 8)
        for name, c in a['cases'].items():
            self.assertEqual(c['retained_closure_gates_UNCHANGED'], self.closure[name]['stage_gates_retained'])
            self.assertFalse(c['accepted_full_field_pipeline'])
            self.assertFalse(c['geometric_tree_complete_certified'])
            for p in c['paths']:
                if not p['previous_geometry_accepted']:
                    self.assertFalse(p['reference_evaluated'])
                if not p['previous_phase_accepted']:
                    self.assertFalse(p['accepted_terminal_reference_CPU_only'])
        self.assertFalse(a['cases']['nonexact_geometry_phase_FAIL']['accepted_terminal_reference_CPU_only'])

    def test_positive_negative_and_two_sources_original_gauge(self):
        for name in ('positive', 'negative', 'two_sources'):
            c = self.output['cases'][name]
            self.assertTrue(c['accepted_terminal_reference_CPU_only'])
            for p in c['paths']:
                self.assertEqual(p['original_reference_correction_BU'], [0, 1])
                self.assertEqual(p['phase_error_upper_rad'], [0, 1])
                self.assertEqual(p['effective_reference_length_interval_BU'],
                                 p['geometric_length_interval_BU'])
        self.assertFalse(self.output['cases']['two_sources']['retained_closure_gates_UNCHANGED'][-1])

    def test_correlated_D_reference_cancellation_all_corners(self):
        corner_count = 0
        for c in self.output['cases'].values():
            for p in c['paths']:
                if not p['reference_evaluated']:
                    continue
                intervals = {k: list(map(m.rational, v)) for k, v in p['enclosure_inputs'].items()}
                sign = -int(m.rational(c['terminal_mode_direction'][0]))
                low, high = map(m.rational, p['effective_reference_length_interval_BU'])
                phi = m.rational(p['phase_error_upper_rad'])
                original = m.rational(p['original_effective_cycles'])
                for M, S, D, ref, wavelength in product(*(intervals[k] for k in ('M', 'S', 'D', 'reference', 'lambda'))):
                    length = sign*(2*M-S-D)
                    correction = -sign*(ref-D)
                    effective = length+correction
                    self.assertEqual(effective, sign*(2*M-S-ref))
                    self.assertLessEqual(low, effective); self.assertLessEqual(effective, high)
                    self.assertLessEqual(8*abs(effective/wavelength-original), phi)
                    corner_count += 1
                na = list(map(m.rational, p['independent_sum_NOT_used_BU']))
                self.assertLessEqual(high-low, na[1]-na[0])
        self.assertEqual(corner_count, 288)
        wide = self.output['cases']['declared_radius_PASS']['paths'][0]
        correlated = list(map(m.rational, wide['effective_reference_length_interval_BU']))
        independent = list(map(m.rational, wide['independent_sum_NOT_used_BU']))
        self.assertLess(correlated[1]-correlated[0], independent[1]-independent[0])

    def test_shifted_original_modepoint_is_different_reference_not_free(self):
        c = deepcopy(self.cases['positive'])
        c['scene_snapshot']['objects']['D']['mode_origin_BU'][0] = 0.1
        c = bind_control(c)
        result = self.check(c)
        p = result['paths'][0]
        self.assertNotEqual(p['original_reference_correction_BU'], [0, 1])
        self.assertGreater(m.rational(result['reference_ABI']['encoding_error_BU']), 0)
        self.assertGreater(m.rational(p['mode_encoding_phase_charge_upper_rad']), 0)
        self.assertGreater(m.rational(p['phase_error_upper_rad']), 0)
        self.assertEqual(p['phase_budget_rad'], [0, 1])
        self.assertFalse(p['accepted_terminal_reference_CPU_only'])
        self.assertNotEqual(result['scene_binding_sha256'], self.output['cases']['positive']['scene_binding_sha256'])
        self.controls['changed_original_modepoint_CAP0_FAIL'] = result

    def test_original_gauge_binding_coverage_and_model_fail_closed(self):
        c = deepcopy(self.cases['positive'])
        c['sources'][0]['phase_reference_id'] = 'unrelated-zero'
        with self.assertRaises(ValueError): self.check(c)
        c = deepcopy(self.cases['positive']); c['word_ABI_sha256'] = '0' * 64
        with self.assertRaises(ValueError): self.check(c)
        c = deepcopy(self.cases['positive']); c['sources'].append(deepcopy(c['sources'][0]))
        with self.assertRaises(ValueError): self.check(c)
        with self.assertRaises(ValueError):
            m.check_case(self.cases['positive'], reference_model=m.MODEL, reference_frame='co-moving terminal point')

    def test_mode_axis_oblique_wrong_zero_nonunit_reject(self):
        for axis in ([1.0, 0.0, 0.0], [-1.0, 0.1, 0.0], [0.0, 0.0, 0.0], [-2.0, 0.0, 0.0]):
            c = deepcopy(self.cases['positive']); c['scene_snapshot']['objects']['D']['mode_direction'] = axis
            with self.assertRaises(ValueError): self.check(bind_control(c))

    def test_nonfinite_bool_subnormal_inputs_reject(self):
        for x in (float('nan'), float('inf'), True):
            c = deepcopy(self.cases['positive']); c['scene_snapshot']['objects']['D']['mode_origin_BU'][0] = x
            with self.assertRaises(ValueError): bind_control(c) if x is not True else self.check(bind_control(c))
        for word in (True, -1, 1 << 32, 1, 0x7f800000):
            with self.assertRaises(ValueError): m.decode_word(word)
        c = deepcopy(self.cases['positive']); c['sources'][0]['accepted_phase_budget_CPU_only'] = 'PASS'
        with self.assertRaises(ValueError): self.check(c)

    def test_HOST_encoding_measured_not_assumed_exact(self):
        e = m.encoded_reference(0.1)
        self.assertEqual(e['HOST_RN32_encodings'], 2)
        self.assertEqual(e['HOST_RN64_subtractions'], 1)
        self.assertEqual(m.rational(e['encoding_error_BU']), F(1, 1 << 55))
        self.assertGreaterEqual(m.rational(e['outward_radius_BU']), m.rational(e['encoding_error_BU']))
        self.assertEqual(m.rational(e['HOST_subtraction_defect_BU']), 0)
        self.assertEqual(m.encoded_reference(-0.125)['encoding_error_BU'], [0, 1])


if __name__ == '__main__':
    result = unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(ReferenceTests))
    if result.wasSuccessful():
        print(json.dumps({'audit': ReferenceTests.output, 'controls': ReferenceTests.controls,
                          'control_scope': 'new CPU HOST mathematical mutations, not frozen fixture validation'},
                         sort_keys=True, separators=(',', ':'), allow_nan=False))
    raise SystemExit(not result.wasSuccessful())
