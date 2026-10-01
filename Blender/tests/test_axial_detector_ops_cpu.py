"""New detector schedule CPU checks; retained scene fields are not replayed."""
from copy import deepcopy
from fractions import Fraction as F
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'Blender/tests'));sys.path.insert(0,str(ROOT/'Blender/benchmarks/capacity_audit'))
from axial_detector_ops_cpu_v1 import MODEL,audit_retained_detector,measure_group_words,load_retained,_case
from axial_hilo_terminal_cpu_v1 import round32_exact
from axial_hilo_ops_cpu_v1 import component
from axial_relative_gate_cpu_v1 import _relative


def word(v):return round32_exact(F(v))[0]


class DetectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.previous,obs=load_retained();cls.old=obs['cases']
        cls.evidence={'primitives':{},'rejections':{}}

    def test_retained_cases_no_scene_or_reduction_replay(self):
        with patch('axial_quarter_source_ops_cpu_v1.produce_quarter_source_operations',side_effect=AssertionError('no producer replay')):
            r=audit_retained_detector(case_names=list(self.old),detector_model=MODEL)
        self.evidence['audit']=r
        self.assertFalse(r['scene_or_reduction_rerun']);self.assertFalse(r['GPU_executed'])
        for n,c in r['cases'].items():
            self.assertEqual(c['previous_case_accepted'],self.old[n]['accepted_original_ideal_scene_CPU_only'])
            if not c['previous_case_accepted']:self.assertFalse(c['accepted_detector_CPU_only'])
            if self.old[n]['field_values_computed']:
                self.assertEqual(c['original_scene_binding_sha256'],self.old[n]['original_scene_binding_sha256'])
                self.assertEqual(c['RN32_operations'],14*sum(len(p['groups']) for p in c['ports'].values()))

    def test_squares_graph_and_each_RN32_node(self):
        r=measure_group_words([word(.1),word(F(1,2**30)),word(.075),word(-F(1,2**33))],detector_model=MODEL)
        self.evidence['primitives']['two_components']=r
        self.assertEqual(len(r['operations']),13)
        for n in r['operations']:
            a,b=[F(*x) for x in n['inputs_rational']];q=a*b if n['op']=='mul' else a+b
            self.assertEqual(n['output_uint32'],round32_exact(q)[0])
            self.assertEqual(F(*n['rounding_delta_rational']),component(n['output_uint32'])-q)
        self.assertLessEqual(F(*r['actual_detector_error_rational']),F(*r['error_upper_rational']))

    def test_dark_reference_original_not_changed_to_observed(self):
        r=_case(self.old['dark']);p=r['ports']['D']
        ideal=F(1,2**60);actual=abs(F(*p['observed_power_rational'])-ideal)
        self.assertLessEqual(actual,F(*p['composed_original_power_error_upper_rational']))
        self.assertTrue(r['accepted_detector_CPU_only'])
        self.evidence['dark_original_power_oracle']={'ideal_power':[ideal.numerator,ideal.denominator],
            'actual_error':[actual.numerator,actual.denominator],'actual_relative':[ (actual/ideal).numerator,(actual/ideal).denominator]}

    def test_cross_product_rounding_charge_is_doubled(self):
        r=measure_group_words([word(.1),word(.003),0,0],detector_model=MODEL)
        ds=[F(*n['rounding_delta_rational']) for n in r['operations']]
        self.assertNotEqual(ds[1],0)
        expected=abs(ds[0])+2*abs(ds[1])+sum(map(abs,ds[2:]),F(0))
        self.assertEqual(F(*r['error_upper_rational']),expected)
        self.evidence['primitives']['cross_weight2']=r

    def test_subnormal_intermediate_and_overflow_fail_closed(self):
        for words in [[word(F(1,2**70)),0,0,0],[0x7f7fffff,0,0,0],[1,0,0,0],[True,0,0,0]]:
            with self.assertRaises(ValueError):measure_group_words(words,detector_model=MODEL)
        self.evidence['rejections']['subnormal_overflow_words']='selected subnormal/input bool/overflow rejected, no FTZ'

    def test_underflow_to_zero_has_full_charge_and_no_relative_certificate(self):
        r=measure_group_words([word(F(1,2**80)),0,0,0],detector_model=MODEL)
        self.assertEqual(F(*r['observed_power_rational']),0)
        self.assertEqual(F(*r['actual_detector_error_rational']),F(1,2**160))
        self.assertEqual(F(*r['error_upper_rational']),F(1,2**160))
        self.assertFalse(_relative(F(0),F(*r['error_upper_rational']),F(1,10**6))['relative_budget_satisfied'])
        self.evidence['primitives']['underflow_FULL_LOSS']=r

    def test_incoherent_groups_and_absolute_relative_budgets_preserved(self):
        r=_case(self.old['separate_groups']);p=r['ports']['D']
        self.assertEqual(set(p['groups']),{'a','b'})
        self.assertGreater(F(*p['observed_power_rational']),F(1,100))
        self.assertTrue(r['accepted_detector_CPU_only'])
        c=deepcopy(self.old['quarter0']);c['transport']['intensity_absolute_budget']=[0,1]
        self.assertFalse(_case(c)['accepted_detector_CPU_only'])
        c=deepcopy(self.old['quarter0']);c['reduction']['ports']['D']['relative_intensity']['relative_budget_rational']=[0,1]
        self.assertFalse(_case(c)['accepted_detector_CPU_only'])
        self.evidence['rejections']['zero_budgets_CPU_copies']='no file mutation or budget expansion; zero absolute/relative reject'

    def test_optin_SHA_and_coverage_validation(self):
        for names in [[],['dark','dark'],[['bad']],['missing']]:
            with self.assertRaises(ValueError):audit_retained_detector(case_names=names,detector_model=MODEL)
        with self.assertRaises(ValueError):audit_retained_detector(case_names=['dark'],detector_model='physical')
        with patch('axial_detector_ops_cpu_v1.SHA','0'*64):
            with self.assertRaisesRegex(ValueError,'SHA'):load_retained()
        for target in ['phase_reference_id','source_ids','output_hilo_uint32']:
            c=deepcopy(self.old['quarter0']);g=c['reduction']['ports']['D']['groups']['g']
            g[target]='bad' if target=='phase_reference_id' else ([] if target=='source_ids' else [0,0,0,0])
            with self.assertRaises(ValueError):_case(c)
        self.evidence['rejections']['coverage_SHA_optin']='local malformed copies/selection/SHA/optin rejected'


if __name__=='__main__':
    result=unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(DetectorTests))
    if hasattr(DetectorTests,'evidence'):print(json.dumps(DetectorTests.evidence,sort_keys=True,allow_nan=False))
    sys.exit(0 if result.wasSuccessful() else 1)
