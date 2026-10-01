"""Only changed terminal graph is evaluated; other graphs remain pinned."""
from copy import deepcopy
from fractions import Fraction as F
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'Blender/benchmarks/capacity_audit'))
import axial_reduction_argument_rn64_cpu_v1 as new

class NewArgumentReductionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report,cls.cases,cls.sources,cls.oldproduct,cls.oldred,cls.defaults=new.load_retained()
        cls.calls=[];original=new.Nodes.rn
        def count(node,a,b,op,label):
            cls.calls.append(label);return original(node,a,b,op,label)
        with patch.object(new.Nodes,'rn',count),patch('axial_source_product_rn64_cpu_v1.product_words',side_effect=AssertionError('no product')),patch('axial_source_argument_rn64_cpu_v1.audit_retained_new_argument_products',side_effect=AssertionError('no upstream audit')),patch('axial_unit_rn64_cpu_v1.rotation64',side_effect=AssertionError('no unit')),patch('axial_reduction_detector_rn64_cpu_v1._case',side_effect=AssertionError('no old audit')):
            cls.audit=new.audit_retained_new_argument_reduction(case_names=list(cls.cases),detector_model=new.MODEL)
        cls.evidence={'audit':cls.audit,'new_RN64_labels':cls.calls,'rejections':{}}

    @classmethod
    def cached_case(cls,n,c=None,lim=None):
        c=cls.cases[n] if c is None else c
        if lim is None:lim=new.limits(n,cls.sources[n],cls.defaults)
        with patch.object(new.Nodes,'rn',side_effect=AssertionError('no repeated RN')):
            return new._case(c,cls.sources[n],lim,cls.oldproduct[n],cls.oldred[n],cls.report['code_doc_sha256'][new.RED_CODE])

    def test_one_changed_case_six_nodes_only(self):
        self.assertEqual(self.calls,['reduce.0','reduce.1','detector.real_square','detector.imag_square','detector.combine','port.incoherent_sum'])
        self.assertEqual(self.audit['new_RN64_operations'],6)
        self.assertEqual(self.audit['cached_RN64_operations'],78)
        self.assertEqual(self.audit['RN64_operations'],84)
        c=self.audit['cases']['nonquarter_FAIL'];self.assertFalse(c['reduction_cache_reused'])
        self.assertNotEqual(c['ports']['D']['groups']['g']['output_uint64'],self.oldred['nonquarter_FAIL']['ports']['D']['groups']['g']['output_uint64'])

    def test_cached_nodes_exact_but_bounds_new(self):
        for name,c in self.audit['cases'].items():
            if not c['reduction_cache_reused']:continue
            sig=c['cache_signature']
            self.assertEqual(sig['reducer_code_sha256'],self.report['code_doc_sha256'][new.RED_CODE])
            self.assertEqual(sig['model'],new.FROZEN_MODEL);self.assertEqual(sig['report_sha256'],new.RED_SHA)
            self.assertEqual(sig['ordered_terminals'],new.signature(self.oldproduct[name]))
            for port,p in c['ports'].items():
                self.assertEqual(p['add_steps'],self.oldred[name]['ports'][port]['add_steps'])
                for group,g in p['groups'].items():
                    old=self.oldred[name]['ports'][port]['groups'][group]
                    self.assertEqual(g['steps'],old['steps']);self.assertEqual(g['detector'],old['detector'])
                    self.assertIsNot(g['detector'],old['detector'])
                    total=sum((F(*r['composed_path_field_error_L1_upper_rational']) for r in self.cases[name]['paths'] if r['port']==port and r['coherence_group']==group),F(0))
                    self.assertEqual(F(*g['path_error_upper_rational']),total)
        self.assertEqual(sum(c['reduction_cache_reused'] for c in self.audit['cases'].values()),11)

    def test_dark_relative_reference_same_budgets(self):
        for n in ('dark','dark_reversed'):
            c=self.audit['cases'][n];g=c['ports']['D']['groups']['g'];p=c['ports']['D']
            self.assertTrue(c['accepted_reduction_detector_CPU_only'])
            self.assertEqual(g['relative_field']['relative_budget_rational'],[1,10**6])
            self.assertEqual(p['relative_power']['relative_budget_rational'],[1,10**6])
            self.assertGreater(F(*g['relative_field']['ideal_reference_lower_rational']),0)
            self.assertLessEqual(F(*g['relative_field']['relative_error_upper_rational']),F(1,10**6))
            self.assertLessEqual(F(*p['relative_power']['relative_error_upper_rational']),F(1,10**6))

    def test_failures_scope_and_incoherent_groups(self):
        cases=self.audit['cases'];self.assertEqual(len(cases),18)
        self.assertEqual(sum(c['accepted_reduction_detector_CPU_only'] for c in cases.values()),10)
        self.assertEqual(sum(c['previous_full_case_accepted'] for c in cases.values()),8)
        for c in cases.values():
            for k in ('accepted_full_field_pipeline','GPU_executed','ALU_executed','native_promotion_allowed','execution_authenticated'):
                self.assertFalse(c[k])
        self.assertFalse(cases['exact_dark_zero_FAIL']['accepted_reduction_detector_CPU_only'])
        self.assertEqual(cases['exact_dark_zero_FAIL']['ports']['D']['groups']['g']['relative_field']['ideal_reference_lower_rational'],[0,1])
        self.assertFalse(cases['relative0_FAIL']['accepted_reduction_detector_CPU_only'])
        self.assertEqual(cases['relative0_FAIL']['budgets']['relative_field'],[0,1])
        self.assertEqual(set(cases['separate_groups']['ports']['D']['groups']),{'a','b'})
        for n in ('nonquarter_FAIL','near_quarter_FAIL'):
            self.assertFalse(cases[n]['previous_full_case_accepted'])

    def test_recompose_bounds_even_identical_terminal_words(self):
        c=deepcopy(self.cases['dark'])
        for p in c['paths']:p['composed_path_field_error_L1_upper_rational']=[1,1]
        out=self.cached_case('dark',c)
        self.assertTrue(out['reduction_cache_reused'])
        self.assertEqual(out['new_RN64_operations'],0)
        self.assertEqual(out['ports']['D']['groups']['g']['path_error_upper_rational'],[2,1])
        self.assertFalse(out['accepted_reduction_detector_CPU_only'])
        lim=new.limits('dark',self.sources['dark'],self.defaults);lim['power']=[0,1]
        out=self.cached_case('dark',lim=lim);self.assertFalse(out['accepted_reduction_detector_CPU_only'])
        self.evidence['rejections']['bounds_not_cached']='same terminal bits reuse nodes but larger NEW bounds/zero power budget reject without RN execution'

    def test_upstream_stops_and_input_failclosed(self):
        for n in ('mirror_phase_FAIL','mirror_phase_underflow_FAIL','mode_FAIL','source0_FAIL','underflow_FAIL','high_intensity_FAIL'):
            c=self.audit['cases'][n];self.assertFalse(c['scene_field_reduced']);self.assertEqual(c['new_RN64_operations'],0)
        for key in ('gauge','coverage','word','binding'):
            c=deepcopy(self.cases['dark'])
            if key=='gauge':c['paths'][0]['phase_reference_id']='bad'
            if key=='coverage':c['paths'].reverse()
            if key=='word':c['paths'][0]['measurement']['output_uint64'][0]=True
            if key=='binding':c['decoded_scene_binding_sha256']='bad'
            with self.assertRaises(ValueError):self.cached_case('dark',c)
        with self.assertRaises(ValueError):new._case(self.cases['dark'],self.sources['dark'],None,self.oldproduct['dark'],self.oldred['dark'],self.report['code_doc_sha256'][new.RED_CODE])

    def test_cached_trace_tamper_reject(self):
        old=deepcopy(self.oldred['dark']);old['ports']['D']['groups']['g']['steps'][0]['operations'][0]['rounding_delta_rational']=[1,1]
        with self.assertRaises(ValueError):new._case(self.cases['dark'],self.sources['dark'],new.limits('dark',self.sources['dark'],self.defaults),self.oldproduct['dark'],old,self.report['code_doc_sha256'][new.RED_CODE])

    def test_optin_selection_SHA(self):
        for ns in ([],['dark','dark'],[['bad']],['missing']):
            with self.assertRaises(ValueError):new.audit_retained_new_argument_reduction(case_names=ns,detector_model=new.MODEL)
        with self.assertRaises(ValueError):new.audit_retained_new_argument_reduction(case_names=['dark'],detector_model='GPU')
        for pin in ('SHA','RED_SHA'):
            with patch.object(new,pin,'0'*64):
                with self.assertRaisesRegex(ValueError,'SHA'):new.load_retained()

if __name__=='__main__':
    r=unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(NewArgumentReductionTests))
    if hasattr(NewArgumentReductionTests,'evidence'):print(json.dumps(NewArgumentReductionTests.evidence,sort_keys=True,allow_nan=False))
    sys.exit(0 if r.wasSuccessful() else 1)
