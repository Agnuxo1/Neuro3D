"""Focused own CPU producer tests; no frozen suites or native execution."""
from copy import deepcopy
from fractions import Fraction as F
import json
import math
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT/'Blender/benchmarks/capacity_audit'))
sys.path.insert(0, str(Path(__file__).parent))
from exp005_history_mzi_audit import fixture, analytic
from coherent_reduction_cpu_v1 import component
from scene_field_producer_cpu_v1 import (produce_scene_fields, rotation,
    product_with_error, rounded_error, PI_LOWER, PI_UPPER)


def run_scene(scene, groups=None):
    return produce_scene_fields(scene, coherence_groups={'s': 'g'} if groups is None else groups)


class ProducerTests(unittest.TestCase):
    def test_exact_MZI_scene_fields_and_L1_bounds(self):
        scene, unused_supplied_rows = fixture()
        out = run_scene(scene)
        self.assertTrue(out['accepted_ideal_scene_CPU_only'])
        self.assertEqual(out['generated_record_count'], 13)
        self.assertEqual(len(out['rows']), 4)
        self.assertEqual({r['id'] for r in out['rows']},
                         {b['id'] for b in out['path_error_bounds']})
        # Each ideal terminal is exactly +/-1/2 or -i/2 in this fixture.
        exact = {9: (F(-1,2), F(0)), 10: (F(0), F(-1,2)),
                 11: (F(0), F(-1,2)), 12: (F(1,2), F(0))}
        for row, bound in zip(out['rows'], out['path_error_bounds']):
            values = tuple(map(F, map(component, row['field_uint32'])))
            expected = exact[row['id']]
            error = sum((abs(v-e) for v,e in zip(values, expected)), F(0))
            self.assertLessEqual(error, F(*bound['field_error_L1_upper_rational']))
            self.assertEqual(row['field_uint32'], bound['field_uint32'])
            self.assertEqual(bound['lambda_BU'], .125)
            self.assertIn(out['scene_binding_sha256'], bound['phase_reference_id'])
        self.assertFalse(out['native_promotion_allowed'])
        self.assertFalse(out['GPU_executed'])
        self.assertFalse(out['execution_authenticated'])

    def test_signed_reference_and_nonzero_mirror_phase_diagnostic(self):
        scene, _ = fixture(phase=.75, reference_shift=-8.04)
        out = run_scene(scene)
        self.assertTrue(out['accepted_ideal_scene_CPU_only'])
        self.assertTrue(any(F(*p['effective_length']['rational_upper']) < 0
                            for p in out['path_evidence']))
        reference = analytic(.75, -8.04)
        # Independent binary64 analytic MZI is a diagnostic, not enclosure proof.
        for port, expected in reference.items():
            actual = complex(*out['composition']['represented_reduction']['ports'][port]
                             ['groups']['g']['modeled_field_reim'])
            budget = F(*out['composition']['ports'][port]['groups']['g']
                       ['composed_field_error_upper_rational'])
            self.assertLessEqual(abs(actual.real-expected.real)+abs(actual.imag-expected.imag),
                                 float(budget)+1e-12)

    def test_sources_separated_and_complex_input_charged(self):
        scene, _ = fixture(phase=.3)
        scene['sources'][0]['field_reim'] = [.75, -.625]
        extra = deepcopy(scene['sources'][0]); extra['id'] = 'extra'
        extra['field_reim'] = [-.75, .625]; scene['sources'].append(extra)
        independent = run_scene(scene, {'s': 'g0', 'extra': 'g1'})
        coherent = run_scene(scene, {'s': 'g0', 'extra': 'g0'})
        self.assertEqual(independent['generated_record_count'], 26)
        self.assertEqual(len(independent['rows']), 8)
        self.assertEqual(set(independent['composition']['ports']['Dx']['groups']), {'g0', 'g1'})
        powers = independent['composition']['represented_reduction']['ports']['Dx']['groups']
        self.assertGreater(sum(float(F(*p['reference_intensity_rational'])) for p in powers.values()), 1)
        coherent_power = coherent['composition']['represented_reduction']['ports']['Dx']['groups']['g0']
        self.assertEqual(coherent_power['reference_intensity_rational'], [0,1])

    def test_binding_changes_with_source_optics_reference_lambda(self):
        scene, _ = fixture(phase=.4)
        original = run_scene(scene)
        changed = []
        for kind in ('source', 'optics', 'reference', 'lambda'):
            other = deepcopy(scene)
            if kind == 'source': other['sources'][0]['field_reim'][0] = .875
            elif kind == 'optics': other['objects']['MA']['phase_rad'] = .5
            elif kind == 'reference': other['objects']['Dx']['mode_origin_BU'][0] += .01
            else: other['lambda_BU'] = .126
            result = run_scene(other)
            self.assertNotEqual(original['scene_binding_sha256'], result['scene_binding_sha256'])
            self.assertNotEqual(original['producer_payload_sha256'], result['producer_payload_sha256'])
            changed.append(result)
        self.assertEqual(original['producer_payload_sha256'], run_scene(scene)['producer_payload_sha256'])
        self.assertEqual(json.dumps(scene,sort_keys=True), json.dumps(fixture(phase=.4)[0],sort_keys=True))

    def test_fail_closed_domain_and_source_metadata(self):
        scene, _ = fixture()
        for groups in ({}, {'s': ''}, {'s': True}, {'s':'g', 'unknown':'g'}):
            with self.assertRaises(ValueError): run_scene(scene, groups)
        scene['objects']['MA']['phase_rad'] = 8.125
        with self.assertRaisesRegex(ValueError, 'angle outside'): run_scene(scene)
        with self.assertRaises(TypeError):
            produce_scene_fields(fixture()[0], coherence_groups={'s':'g'}, rows=[])

    def test_subnormal_rejection_and_quadrature_conversion_charged(self):
        # Actual nonzero subnormal output is rejected, not snapped to zero.
        scene, _ = fixture()
        scene['sources'][0]['field_reim'] = [1e-39,0.]
        with self.assertRaisesRegex(ValueError, 'normal-or-zero'): run_scene(scene)
        # Quarter-cycle polynomial residual rounds below smallest binary32:
        # resulting zero IS allowed and its exact conversion error is charged.
        scene, _ = fixture(reference_shift=.03125)
        out = run_scene(scene)
        for path in out['path_evidence']:
            if F(*path['reduced_turns_rational']) == F(1,4):
                self.assertGreater(F(*path['conversion_error_L1_upper_rational']),0)
        self.assertTrue(out['accepted_ideal_scene_CPU_only'])

    def test_rational_product_cross_term_and_outward_compression(self):
        a=(F(3,4),F(-5,8)); b=(F(2,3),F(1,7)); ea=F(1,1000); eb=F(1,2000)
        approx, bound = product_with_error(a,ea,b,eb)
        for da in ((ea,0),(0,-ea),(ea/2,ea/2)):
            for db in ((eb,0),(0,eb),(-eb/2,eb/2)):
                actual,_=product_with_error(tuple(x+y for x,y in zip(a,da)),0,
                                           tuple(x+y for x,y in zip(b,db)),0)
                self.assertLessEqual(sum(abs(x-y) for x,y in zip(actual,approx)), bound)
        for value in (F(0),F(1,3),F(1,10**100),bound):
            compressed=F(*rounded_error(value))
            self.assertGreaterEqual(compressed,value)
            self.assertLess(compressed-value,F(1,2**128))

    def test_rotation_exact_alternating_enclosure_and_pi_bracket(self):
        self.assertEqual(rotation(0),((F(1),F(0)),F(0)))
        def atan_enclosure(x):
            terms=[(-1)**k*x**(2*k+1)/F(2*k+1) for k in range(80)]
            partial=sum(terms,F(0)); remainder=x**161/F(161)
            return partial,partial+remainder
        a,b=atan_enclosure(F(1,5)); c,d=atan_enclosure(F(1,239))
        self.assertLess(PI_LOWER,16*a-4*d)
        self.assertLess(16*b-4*c,PI_UPPER)
        for angle in (-8,-1,F(3,4),8):
            x=F(angle); z,error=rotation(x); enclosure_error=F(0)
            # Separate long alternating sin/cos enclosures, exact rationals;
            # terms decrease past n=8, well before our last n>=200 term.
            for component_index in (0,1):
                terms=[(-1)**k*x**(2*k+component_index)/math.factorial(2*k+component_index)
                       for k in range(101)]
                partial=sum(terms,F(0))
                next_term=(-1)**101*x**(202+component_index)/math.factorial(202+component_index)
                enclosure_error+=max(abs(z[component_index]-partial),
                                     abs(z[component_index]-partial-next_term))
            self.assertLessEqual(enclosure_error,error)


if __name__ == '__main__': unittest.main()
