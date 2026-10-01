"""New propagation unit tests; retained phase quotient and producers not replayed."""
from copy import deepcopy
from fractions import Fraction as F
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'Blender/tests'));sys.path.insert(0,str(ROOT/'Blender/benchmarks/capacity_audit'))
from axial_unit_rotation_cpu_v1 import MODEL,rotation_word,permute_unit,load_retained,_case,audit_retained_unit_rotations
from axial_hilo_terminal_cpu_v1 import round32_exact
from axial_hilo_ops_cpu_v1 import component


def word(v):return round32_exact(F(v))[0]


class UnitRotationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.previous,cls.old=load_retained();cls.evidence={'primitives':{},'rejections':{}}

    def test_retained_cases_without_quotient_or_old_producer_replay(self):
        with patch('axial_phase_quotient_cpu_v1.quotient_words',side_effect=AssertionError('no quotient replay')),patch('scene_field_producer_cpu_v1.rotation',side_effect=AssertionError('no frozen producer')):
            a=audit_retained_unit_rotations(case_names=list(self.old),rotation_model=MODEL)
        self.evidence['audit']=a
        for name,c in a['cases'].items():
            self.assertEqual(c['previous_full_case_accepted'],self.old[name]['previous_full_case_accepted'])
            self.assertFalse(c['accepted_full_field_pipeline']);self.assertFalse(c['field_values_computed'])
            self.assertFalse(c['mirror_phase_evaluated'])

    def test_exact_quarters_and_zero_error_case(self):
        for i,expected in enumerate([(1,0),(0,1),(-1,0),(0,-1)]):
            c=_case(self.old['quarter'+str(i)]);p=c['paths'][0]
            self.assertEqual([F(*v) for v in p['observed_unit_rational']],list(expected))
            self.assertEqual(F(*p['composed_unit_error_L1_upper_rational']),0)
            self.assertTrue(c['accepted_propagation_unit_CPU_only'])
            self.assertEqual(p['measurement']['RN32_operations'],26)

    def test_each_RN32_node_and_polynomial_bound(self):
        for name,x in [('positive',F(1,2)),('negative',-F(1,2))]:
            r=rotation_word(word(x),rotation_model=MODEL);self.evidence['primitives'][name]=r
            self.assertEqual(len(r['operations']),26)
            for node in r['operations']:
                a,b=[F(*v) for v in node['inputs_rational']];exact=a*b if node['op']=='mul' else a+b
                self.assertEqual(node['output_uint32'],round32_exact(exact)[0])
                self.assertEqual(F(*node['rounding_delta_rational']),component(node['output_uint32'])-exact)
            for t in r['terms'].values():
                self.assertLessEqual(F(*t['actual_polynomial_error_rational']),F(*t['polynomial_error_upper_rational']))
                self.assertEqual(sum((F(*v) for v in t['error_charges_rational'].values()),F(0)),F(*t['polynomial_error_upper_rational']))

    def test_nonquarter_not_certified_by_unchanged_budget(self):
        c=_case(self.old['nonquarter_FAIL']);p=c['paths'][0]
        self.assertTrue(c['previous_phase_argument_accepted']);self.assertFalse(c['accepted_propagation_unit_CPU_only'])
        self.assertGreater(F(*p['composed_unit_error_L1_upper_rational']),F(*p['derived_unit_L1_budget_rational']))
        self.assertEqual(p['phase_budget_rad'],self.old['nonquarter_FAIL']['paths'][0]['phase_budget_rad'])
        self.evidence['rejections']['nonquarter_unchanged_budget']='RN32 propagation unit bound exceeds twice existing1e-12rad; no threshold expansion or full-case promotion'

    def test_nearquarter_low_residual_retained_but_no_field_claim(self):
        c=_case(self.old['near_quarter_FAIL']);p=c['paths'][0]
        self.assertEqual(F(*p['quarter_residual_cycles_rational']),F(1,2**27))
        self.assertGreater(F(*p['observed_unit_rational'][1]),0)
        self.assertTrue(c['accepted_propagation_unit_CPU_only']);self.assertFalse(c['previous_full_case_accepted'])
        self.assertFalse(c['accepted_full_field_pipeline'])
        self.evidence['rejections']['nearquarter_still_fullcase_FAIL']='nonzero propagation sin from retained lowcycles; no scene field/source product/mirror phase/native selector'

    def test_coefficients_square_round_and_remainder_are_separate(self):
        r=rotation_word(word(F(1,10)),rotation_model=MODEL)
        for t in r['terms'].values():
            self.assertGreater(F(*t['error_charges_rational']['coefficients']),0)
            self.assertGreater(F(*t['error_charges_rational']['square']),0)
            self.assertGreater(F(*t['error_charges_rational']['RN_nodes']),0)
            self.assertGreater(F(*t['Taylor_remainder_upper_rational']),0)
        self.evidence['primitives']['separate_charges']=r

    def test_subnormal_domain_selector_gauge_budget_and_coverage_reject(self):
        for w in [1,True,word(F(1,2**70)),0x7f7fffff]:
            with self.assertRaises(ValueError):rotation_word(w,rotation_model=MODEL)
        c=deepcopy(self.old['near_quarter_FAIL']);c['paths'][0]['phase_budget_rad']=[0,1]
        self.assertFalse(_case(c)['accepted_propagation_unit_CPU_only'])
        c=deepcopy(self.old['quarter0']);c['paths'][0]['phase_reference_id']='bad'
        self.assertFalse(_case(c)['accepted_propagation_unit_CPU_only'])
        c=deepcopy(self.old['quarter0']);c['paths'][0]['selector']['centered_enclosure_cycles_rational']=[[0,1],[1,8]]
        self.assertFalse(_case(c)['accepted_propagation_unit_CPU_only'])
        c=deepcopy(self.old['quarter0']);c['paths'].append(deepcopy(c['paths'][0]))
        with self.assertRaises(ValueError):_case(c)
        with self.assertRaises(ValueError):permute_unit([word(1)],0)
        self.evidence['rejections']['fail_closed']='subnormal input/intermediate, bool, domain, quarter branch, gauge, zero budget and duplicate source reject on copies'

    def test_explicit_optin_SHA_selection(self):
        for names in [[],['quarter0','quarter0'],[['bad']],['missing']]:
            with self.assertRaises(ValueError):audit_retained_unit_rotations(case_names=names,rotation_model=MODEL)
        with self.assertRaises(ValueError):audit_retained_unit_rotations(case_names=['quarter0'],rotation_model='physical')
        with patch('axial_unit_rotation_cpu_v1.SHA','0'*64):
            with self.assertRaisesRegex(ValueError,'SHA'):load_retained()
        self.evidence['rejections']['SHA_optin_selection']='wrong localSHA/optin/selection rejected'


if __name__=='__main__':
    result=unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(UnitRotationTests))
    if hasattr(UnitRotationTests,'evidence'):print(json.dumps(UnitRotationTests.evidence,sort_keys=True,allow_nan=False))
    sys.exit(0 if result.wasSuccessful() else 1)
