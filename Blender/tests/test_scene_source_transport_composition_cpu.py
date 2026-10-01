"""New decoded source inputs, no old producer suite/barrado/native launch."""
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
from scene_source_transport_composition_cpu_v1 import produce_with_source_transport
from exp005_history_mzi_audit import fixture

PINS = {
    'Blender/benchmarks/capacity_audit/source_transport_budget_cpu_v1.py': 'e6aeda7f4d6423719eacc119828190b9b56b2e9cd4be0ce25a89450e11bb8fcb',
    'Blender/benchmarks/capacity_audit/scene_field_producer_cpu_v1.py': '1a697f1cbe6dab515d27dbf5e4c022aae8b6099115b9961d225c0a318de3d380',
    'Blender/benchmarks/capacity_audit/coherent_error_composition_cpu_v1.py': '7e7988ecdb014d2eb3efff09af8c0e4aaf7cf94b39835fb8b0dfa18d99693879',
    'coordinacion/respuestas/SCENE-CONVERSION-001-CODEX.json': 'ad04c656087db7511171da92146e17eba73343714c6c43222f046650fd53fd20',
    'coordinacion/respuestas/LEDGER-INTERVAL-001-CODEX.json': '77a0b36f096cdf8ff603d41993bec661765f7be3c303bba73ac7fae69f8ca398',
    'Blender/shaders/exp005_shared_frontier.glsl': '914bf2962ead3c6a7b721a8dc2aa6c1e796af4bde1892db1802c3ca93ebdfcd1',
}


def run(scene, groups=None, absolute=F(1,10**4), relative=F(1,10**6)):
    return produce_with_source_transport(scene,
        coherence_groups=groups or {s['id']:'g' for s in scene['sources']},
        source_absolute_L1_budget=absolute, source_relative_L1_budget=relative)


def summary(result):
    # Keep words, IDs, both bindings, source charges and composed gates.
    return {k: result[k] for k in ('original_scene_binding_sha256',
        'decoded_scene_binding_sha256', 'decoded_producer_payload_sha256',
        'rows', 'sources', 'path_error_components', 'generated_record_count',
        'composition', 'accepted_original_ideal_scene_CPU_only', 'GPU_executed',
        'native_promotion_allowed', 'execution_authenticated')}


class SourceCompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for path, sha in PINS.items():
            if hashlib.sha256((ROOT/path).read_bytes()).hexdigest() != sha:
                raise ValueError('changed frozen input: '+path)
        cls.cases = json.loads((ROOT/'coordinacion/respuestas/SCENE-CONVERSION-001-CODEX.json').read_text())['observations']['cases']
        cls.results = [run(case['snapshot']) for case in cls.cases]
        cls.evidence = {'pins_verified': PINS, 'new_decoded_direct_cases':
            [{'name': case['name'], 'result': summary(result)}
             for case, result in zip(cls.cases, cls.results)], 'boundaries': {},
            'old_suite_rerun': False, 'GPU_executed': False}

    def test_direct_original_scene_exact_oracles_inside_composed_bounds(self):
        for case, result in zip(self.cases, self.results):
            ideal = [F(*x) for x in case['ideal_field_rational']]
            reduced = result['composition']['represented_reduction']['ports']['D']['groups']['g']
            observed = list(map(F, reduced['modeled_field_reim']))
            error = sum(abs(a-b) for a,b in zip(observed, ideal))
            power_error = abs(sum(x*x for x in observed)-sum(x*x for x in ideal))
            port = result['composition']['ports']['D']
            self.assertLessEqual(error, F(*port['groups']['g']['composed_field_error_upper_rational']))
            self.assertLessEqual(power_error, F(*port['intensity_error_upper_rational']))
            self.assertEqual(result['original_scene_binding_sha256'], case['producer']['scene_binding_sha256'])
            self.assertNotEqual(result['original_scene_binding_sha256'], result['decoded_scene_binding_sha256'])

    def test_high_field_rejection_is_preserved_not_fixed_by_hi_lo(self):
        result = self.results[1]
        self.assertFalse(result['accepted_original_ideal_scene_CPU_only'])
        self.assertFalse(result['composition']['ports']['D']['intensity_budget_satisfied'])
        self.assertFalse(result['native_promotion_allowed'])

    def test_source_charge_precedes_coefficients_and_zero_budget_rejects(self):
        result = self.results[2]
        charges = [F(*p['propagated_source_transport_L1_upper_rational']) for p in result['path_error_components']]
        self.assertEqual(charges, [F(1,2**54), F(3,2**54)])
        for p in result['path_error_components']:
            self.assertGreaterEqual(F(*p['combined_path_error_L1_upper_rational']),
                F(*p['decoded_scene_producer_error_L1_upper_rational'])+
                F(*p['propagated_source_transport_L1_upper_rational']))
        tight = run(self.cases[0]['snapshot'], absolute=0, relative=0)
        self.assertFalse(tight['accepted_original_ideal_scene_CPU_only'])
        self.evidence['boundaries']['tight_source_budget_FAIL'] = summary(tight)

    def test_new_passive_MZI_source_not_unit_amplitude_or_supplied_paths(self):
        scene, unused = fixture()
        scene['sources'][0]['field_reim'] = [.1, 0.]
        before = deepcopy(scene)
        result = run(scene)
        self.assertEqual(scene, before)
        self.assertEqual(result['generated_record_count'], 13)
        self.assertEqual(len(result['rows']), 4)
        # Independent original ideal MZI: Dx=-i*input, Dy=0, phase0.
        ideal = {'Dx': [F(0),-F(.1)], 'Dy': [F(0),F(0)]}
        for port, expected in ideal.items():
            reduced = result['composition']['represented_reduction']['ports'][port]['groups']['g']
            actual = list(map(F,reduced['modeled_field_reim']))
            bound = F(*result['composition']['ports'][port]['groups']['g']['composed_field_error_upper_rational'])
            self.assertLessEqual(sum(abs(a-b) for a,b in zip(actual, expected)), bound)
        self.assertTrue(result['accepted_original_ideal_scene_CPU_only'])
        self.evidence['boundaries']['new_MZI_source_point1_CPU'] = summary(result)

    def test_underflow_rejects_even_when_composed_absolute_gates_pass(self):
        scene = deepcopy(self.cases[0]['snapshot'])
        scene['sources'][0]['field_reim'] = [2.**-150,0.]
        result = run(scene, absolute=F(1,2**149), relative=0)
        self.assertTrue(result['composition']['accepted_conditional_upstream_and_reduction_only'])
        self.assertFalse(result['accepted_original_ideal_scene_CPU_only'])
        self.evidence['boundaries']['underflow_source_relative_FAIL'] = summary(result)

    def test_frozen_normal_output_profile_and_passive_optics_not_enlarged(self):
        scene = deepcopy(self.cases[0]['snapshot'])
        scene['sources'][0]['field_reim'] = [2.**-149,0.]
        with self.assertRaisesRegex(ValueError, 'normal-or-zero'): run(scene)
        scene, _ = fixture()
        scene['sources'][0]['field_reim'] = [.1,0.]
        scene['objects']['B1']['power_transmittance'] = 1.01
        with self.assertRaisesRegex(ValueError, 'transmittance'): run(scene)


if __name__ == '__main__':
    result = unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(SourceCompositionTests))
    if hasattr(SourceCompositionTests, 'evidence'):
        print(json.dumps(SourceCompositionTests.evidence, sort_keys=True, allow_nan=False))
    sys.exit(0 if result.wasSuccessful() else 1)
