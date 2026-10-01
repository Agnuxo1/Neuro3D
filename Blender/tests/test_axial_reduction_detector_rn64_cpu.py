"""New reduction and detector only; no scene/unit/product replay."""
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
import json
import sys
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'Blender/benchmarks/capacity_audit'))
from axial_reduction_detector_rn64_cpu_v1 import MODEL,Nodes,detector_words,load_retained,limits,_case,audit_retained_reduction_detector
from axial_unit_rn64_cpu_v1 import round64
from axial_relative_gate_cpu_v1 import _relative


class ReductionDetectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report,cls.cases,cls.sources,cls.defaults=load_retained();cls.evidence={'primitives':{},'rejections':{}}
    def case(self,n):return _case(self.cases[n],self.sources[n],limits(n,self.sources[n],self.defaults) if self.cases[n]['accepted_source_product_absolute_CPU_only'] else None)

    def test_new_reduction_no_producer_replay(self):
        with patch('axial_source_product_rn64_cpu_v1.product_words',side_effect=AssertionError('no product replay')),patch('axial_unit_rn64_cpu_v1.rotation64',side_effect=AssertionError('no unit replay')),patch('scene_field_producer_cpu_v1.rotation',side_effect=AssertionError('no scene producer')):
            a=audit_retained_reduction_detector(case_names=list(self.cases),detector_model=MODEL)
        self.evidence['audit']=a
        for n,c in a['cases'].items():
            self.assertEqual(c['previous_full_case_accepted'],self.cases[n]['previous_full_case_accepted'])
            self.assertFalse(c['accepted_full_field_pipeline'])

    def test_dark_residual_relative_same_budgets(self):
        for n in ['dark','dark_reversed']:
            c=self.case(n);g=c['ports']['D']['groups']['g'];p=c['ports']['D']
            self.assertTrue(c['accepted_reduction_detector_CPU_only'])
            self.assertGreater(abs(F(*g['observed_field_rational'][0])),0)
            self.assertEqual(g['relative_field']['relative_budget_rational'],[1,10**6])
            self.assertEqual(p['relative_power']['relative_budget_rational'],[1,10**6])
            self.assertLessEqual(F(*g['relative_field']['relative_error_upper_rational']),F(1,10**6))
            self.assertLessEqual(F(*p['relative_power']['relative_error_upper_rational']),F(1,10**6))

    def test_nonquarter_and_nearquarter_still_previous_full_FAIL(self):
        for n in ['nonquarter_FAIL','near_quarter_FAIL']:
            c=self.case(n);self.assertTrue(c['accepted_reduction_detector_CPU_only'])
            self.assertFalse(c['previous_full_case_accepted']);self.assertFalse(c['accepted_full_field_pipeline'])
            self.assertIn('defaults parsed AST',c['budgets']['origin'])
            self.assertEqual(c['budgets']['relative_field'],[1,10**6])

    def test_groups_incoherent_and_exactdark_zero(self):
        c=self.case('separate_groups');self.assertEqual(set(c['ports']['D']['groups']),{'a','b'})
        self.assertTrue(c['accepted_reduction_detector_CPU_only'])
        c=self.case('exact_dark_zero_FAIL');g=c['ports']['D']['groups']['g']
        self.assertEqual(g['relative_field']['ideal_reference_lower_rational'],[0,1])
        self.assertFalse(c['accepted_reduction_detector_CPU_only'])
        self.assertFalse(c['ports']['D']['relative_power']['relative_budget_satisfied'])

    def test_relative0_and_all_upstream_rejections(self):
        c=self.case('relative0_FAIL');self.assertFalse(c['accepted_reduction_detector_CPU_only'])
        self.assertEqual(c['budgets']['relative_field'],[0,1])
        for n in ['mirror_phase_FAIL','mirror_phase_underflow_FAIL','mode_FAIL','source0_FAIL','underflow_FAIL','high_intensity_FAIL']:
            c=self.case(n);self.assertFalse(c['scene_field_reduced']);self.assertEqual(c['RN64_operations'],0)
        self.evidence['rejections']['retained_FAIL']='relative0/exactdark lower0 reject; six upstream failures no computation; previous fullFAILs preserved'

    def test_synthetic_detector_loss_and_incoherent_add_charge(self):
        words=[round64(F(1,2**600))[0],0];d=detector_words(words,detector_model=MODEL)
        self.evidence['primitives']['power_underflow_rounds_zero_charged']=d
        self.assertEqual(F(*d['observed_power_rational']),0)
        self.assertEqual(F(*d['detector_error_upper_rational']),F(1,2**1200))
        self.assertFalse(_relative(F(0),F(*d['detector_error_upper_rational']),F(1,10**6))['relative_budget_satisfied'])
        with self.assertRaises(ValueError):detector_words([round64(F(1,2**530))[0],0],detector_model=MODEL)
        o=Nodes();v,delta,w=o.rn(F(1),F(1,2**60),'add','synthetic.port_sum')
        self.assertEqual(v,1);self.assertEqual(delta,-F(1,2**60))
        self.evidence['primitives']['port_sum_loses_small_group_charged']={'operations':o.trace,'RN64_operations':1}

    def test_gauge_group_coverage_word_budget_failclosed(self):
        lim=limits('dark',self.sources['dark'],self.defaults)
        c=deepcopy(self.cases['dark']);c['paths'][0]['phase_reference_id']='bad'
        with self.assertRaises(ValueError):_case(c,self.sources['dark'],lim)
        c=deepcopy(self.cases['dark']);c['paths'][0]['coherence_group']='different'
        with self.assertRaises(ValueError):_case(c,self.sources['dark'],lim)
        c=deepcopy(self.cases['dark']);c['paths'].reverse()
        with self.assertRaises(ValueError):_case(c,self.sources['dark'],lim)
        c=deepcopy(self.cases['dark']);c['paths'][0]['measurement']['output_uint64'][0]=True
        with self.assertRaises(ValueError):_case(c,self.sources['dark'],lim)
        with self.assertRaises(ValueError):_case(self.cases['dark'],self.sources['dark'],None)
        lim=deepcopy(lim);lim['power']=[0,1]
        self.assertFalse(_case(self.cases['dark'],self.sources['dark'],lim)['accepted_reduction_detector_CPU_only'])

    def test_optin_selection_SHA(self):
        for ns in [[],['dark','dark'],[['bad']],['missing']]:
            with self.assertRaises(ValueError):audit_retained_reduction_detector(case_names=ns,detector_model=MODEL)
        with self.assertRaises(ValueError):audit_retained_reduction_detector(case_names=['dark'],detector_model='GPU')
        with patch('axial_reduction_detector_rn64_cpu_v1.SHA','0'*64):
            with self.assertRaisesRegex(ValueError,'SHA'):load_retained()


if __name__=='__main__':
    r=unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(ReductionDetectorTests))
    if hasattr(ReductionDetectorTests,'evidence'):print(json.dumps(ReductionDetectorTests.evidence,sort_keys=True,allow_nan=False))
    sys.exit(0 if r.wasSuccessful() else 1)
