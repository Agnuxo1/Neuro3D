"""New source-input contract only; retained scene producer never rerun."""
from copy import deepcopy
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'Blender/tests'))
sys.path.insert(0, str(ROOT/'Blender/benchmarks/capacity_audit'))
from source_transport_budget_cpu_v1 import audit_source_transport

PINS = {
    'Blender/tests/exp005_blender_gpu.py': '851f29f9b1fb9b22948f59597d40fa8a55828040673fe0050d24e077b57cf497',
    'coordinacion/respuestas/SCENE-CONVERSION-001-CODEX.json': 'ad04c656087db7511171da92146e17eba73343714c6c43222f046650fd53fd20',
    'Blender/benchmarks/capacity_audit/scene_field_producer_cpu_v1.py': '1a697f1cbe6dab515d27dbf5e4c022aae8b6099115b9961d225c0a318de3d380',
    'Blender/shaders/exp005_shared_frontier.glsl': '914bf2962ead3c6a7b721a8dc2aa6c1e796af4bde1892db1802c3ca93ebdfcd1',
    'coordinacion/respuestas/LEDGER-INTERVAL-001-CODEX.json': '77a0b36f096cdf8ff603d41993bec661765f7be3c303bba73ac7fae69f8ca398',
}


def call(scene, absolute=F(1, 10**4), relative=F(1, 10**6)):
    return audit_source_transport(scene,
        coherence_groups={s['id']: 'g' for s in scene['sources']},
        absolute_L1_budget=absolute, relative_L1_budget=relative)


class SourceBudgetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for path, sha in PINS.items():
            if hashlib.sha256((ROOT/path).read_bytes()).hexdigest() != sha:
                raise ValueError('changed frozen input: '+path)
        retained = json.loads((ROOT/'coordinacion/respuestas/SCENE-CONVERSION-001-CODEX.json').read_text())
        cls.cases = retained['observations']['cases']
        cls.evidence = {'retained': [], 'new_boundary_cases': {}, 'pins_verified': PINS,
                        'old_producer_rerun': False, 'GPU_executed': False}
        for case in cls.cases:
            result = call(case['snapshot'])
            if result['scene_binding_sha256'] != case['producer']['scene_binding_sha256']:
                raise AssertionError('scene binding differs from retained producer')
            cls.evidence['retained'].append({'name': case['name'], 'result': result})

    def test_retained_sources_separate_errors_without_cancellation_credit(self):
        dark = self.evidence['retained'][2]['result']
        errors = [F(*s['components'][0]['total_error_signed_rational']) for s in dark['sources']]
        self.assertEqual(list(map(abs, errors)), [F(1, 2**55), F(3, 2**55)])
        self.assertEqual(sum(errors), -F(1, 2**53))
        self.assertEqual([s['packed_field_offsets'] for s in dark['sources']], [[3,7], [11,15]])
        self.assertTrue(dark['accepted_CPU_source_transport_budget_only'])
        self.assertFalse(dark['terminal_bounds_certified'])

    def test_exactness_budget_rejects_nonexact_transport(self):
        result = call(self.cases[0]['snapshot'], absolute=0, relative=0)
        self.assertFalse(result['accepted_CPU_source_transport_budget_only'])
        self.evidence['new_boundary_cases']['ordinary_exactness_budget_FAIL'] = result

    def test_half_min_subnormal_collapses_absolute_can_pass_relative_fails(self):
        scene = deepcopy(self.cases[0]['snapshot'])
        scene['sources'][0]['field_reim'] = [2.**-150, 0.]
        result = call(scene, absolute=F(1, 2**149), relative=0)
        source = result['sources'][0]
        self.assertTrue(source['absolute_budget_satisfied'])
        self.assertFalse(source['relative_budget_satisfied'])
        self.assertTrue(source['components'][0]['nonzero_input_collapsed_to_zero'])
        self.assertEqual(source['relative_source_transport_error_L1_rational'], [1,1])
        self.assertEqual(source['source_transport_error_L1_rational'], [1, 2**150])
        self.assertFalse(result['native_admitted'])
        self.evidence['new_boundary_cases']['half_min_subnormal_FAIL'] = result

    def test_min_subnormal_exact_CPU_does_not_admit_native(self):
        scene = deepcopy(self.cases[0]['snapshot'])
        scene['sources'][0]['field_reim'] = [2.**-149, 0.]
        result = call(scene, absolute=0, relative=0)
        self.assertTrue(result['accepted_CPU_source_transport_budget_only'])
        self.assertTrue(result['requires_native_subnormal_semantics'])
        self.assertEqual(result['sources'][0]['components'][0]['limb_uint32'], [1,0])
        self.assertFalse(result['native_admitted'])
        self.evidence['new_boundary_cases']['min_subnormal_CPU_only_PASS'] = result

    def test_zero_signed_zero_and_imaginary_lane(self):
        scene = deepcopy(self.cases[0]['snapshot'])
        scene['sources'][0]['field_reim'] = [-0., .125]
        result = call(scene, absolute=0, relative=0)
        real, imag = result['sources'][0]['components']
        self.assertTrue(real['input_negative_zero'])
        self.assertEqual(real['limb_uint32'][0], 0x80000000)
        self.assertEqual(imag['input_binary64_rational'], [1,8])
        self.assertTrue(result['accepted_CPU_source_transport_budget_only'])
        scene['sources'][0]['field_reim'] = [0., 0.]
        self.assertEqual(call(scene, 0, 0)['sources'][0]['relative_source_transport_error_L1_rational'], [0,1])

    def test_fail_closed_malformed_groups_fields_and_budgets(self):
        base = self.cases[0]['snapshot']
        for value in (True, float('nan'), float('inf'), 1e40):
            scene = deepcopy(base)
            scene['sources'][0]['field_reim'][0] = value
            with self.assertRaises(ValueError): call(scene)
        for value in (-1, True, float('nan'), '1e-4'):
            with self.assertRaises(ValueError): call(base, absolute=value)
        with self.assertRaises(ValueError):
            audit_source_transport(base, coherence_groups={}, absolute_L1_budget=0, relative_L1_budget=0)
        scene = deepcopy(self.cases[2]['snapshot'])
        scene['sources'][1]['id'] = scene['sources'][0]['id']
        with self.assertRaises(ValueError): call(scene)


if __name__ == '__main__':
    result = unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(SourceBudgetTests))
    if hasattr(SourceBudgetTests, 'evidence'):
        print(json.dumps(SourceBudgetTests.evidence, sort_keys=True, allow_nan=False))
    sys.exit(0 if result.wasSuccessful() else 1)
