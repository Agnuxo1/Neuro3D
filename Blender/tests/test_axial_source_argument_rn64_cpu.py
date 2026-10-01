"""New inputs only; reuse pinned product evidence, do not replay producers."""
from copy import deepcopy
from fractions import Fraction as F
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'Blender/benchmarks/capacity_audit'))
import axial_source_argument_rn64_cpu_v1 as new
from axial_source_product_rn64_cpu_v1 import product_words as original_product

class NewArgumentProductTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report,cls.units,cls.sources,cls.old=new.load_retained()
        cls.calls=[]
        def changed(words,unit,**kw):
            cls.calls.append({'source_limb_uint32':words,'unit_uint64':unit})
            return original_product(words,unit,**kw)
        with patch.object(new,'product_words',side_effect=changed),patch('axial_unit_rn64_cpu_v1.rotation64',side_effect=AssertionError('no unit replay')),patch('axial_unit_argument_rn64_cpu_v1.audit_retained_new_argument_units',side_effect=AssertionError('no upstream unit audit')),patch('axial_source_product_rn64_cpu_v1._case',side_effect=AssertionError('no old product audit')),patch('axial_quarter_source_ops_cpu_v1.produce_quarter_source_operations',side_effect=AssertionError('no scene replay')):
            cls.audit=new.audit_retained_new_argument_products(case_names=list(cls.units),product_model=new.MODEL)
        cls.evidence={'audit':cls.audit,'new_product_call_inputs':cls.calls,'rejections':{}}

    def test_one_changed_input_only(self):
        self.assertEqual(len(self.calls),1)
        self.assertEqual(self.audit['new_RN64_operations'],8)
        self.assertEqual(self.audit['cached_RN64_operations'],120)
        self.assertEqual(self.audit['RN64_operations'],128)
        p=self.audit['cases']['nonquarter_FAIL']['paths'][0]
        self.assertTrue(p['product_evaluated']);self.assertFalse(p['product_cache_reused'])
        self.assertNotEqual(p['measurement']['unit_uint64'],self.old['nonquarter_FAIL']['paths'][0]['measurement']['unit_uint64'])

    def test_cache_word_code_model_exact_deepcopy(self):
        for name,c in self.audit['cases'].items():
            for p,old in zip(c['paths'],self.old[name]['paths']):
                if not p['product_cache_reused']:continue
                self.assertEqual(p['measurement'],old['measurement'])
                self.assertIsNot(p['measurement'],old['measurement'])
                sig=p['cache_signature']
                self.assertEqual(sig['product_code_sha256'],self.report['code_doc_sha256'][new.PRODUCT_CODE])
                self.assertEqual(sig['model'],new.PRODUCT_MODEL)
                self.assertEqual(sig['report_sha256'],new.PRODUCT_SHA)
        p=self.audit['cases']['quarter0']['paths'][0]
        self.assertTrue(p['product_cache_reused'])

    def test_new_unit_charge_not_old_total(self):
        for name,c in self.audit['cases'].items():
            for p,u in zip(c['paths'],self.units[name]['paths']):
                self.assertEqual(p['retained_unit_error_L1_upper_rational'],u['composed_unit_error_L1_upper_rational'])
                self.assertEqual(F(*p['error_charges_L1_rational']['unit_phase_numeric']),F(*p['original_amplitude_L1_rational'])*F(*u['composed_unit_error_L1_upper_rational']))
                self.assertEqual(F(*p['composed_path_field_error_L1_upper_rational']),sum((F(*v) for v in p['error_charges_L1_rational'].values()),F(0)))
                self.assertEqual(p['field_absolute_L1_budget_rational'],self.old[name]['field_absolute_L1_budget_rational'])

    def test_scope_and_retained_failures(self):
        cases=self.audit['cases']
        self.assertEqual(len(cases),18)
        self.assertEqual(sum(c['accepted_source_product_absolute_CPU_only'] for c in cases.values()),12)
        self.assertEqual(sum(c['previous_full_case_accepted'] for c in cases.values()),8)
        for c in cases.values():
            for flag in ('accepted_full_field_pipeline','coherent_group_budget_certified','scene_field_reduced','detector_evaluated','GPU_executed','ALU_executed','native_promotion_allowed','execution_authenticated'):
                self.assertFalse(c[flag])
        self.assertFalse(cases['nonquarter_FAIL']['previous_full_case_accepted'])
        self.assertFalse(self.units['nonquarter_FAIL']['paths'][0]['previous_RN32_unit_accepted'])

    def test_cached_zero_budget_reject_and_upstream_stop(self):
        # No changed product recalculated: use cached nonzero-error source_decode.
        s=deepcopy(self.sources['source_decode']);s['transport']['field_absolute_L1_budget']=[0,1]
        with patch.object(new,'product_words',side_effect=AssertionError('no repeat load')):
            c=new._case(self.units['source_decode'],s,self.old['source_decode'],self.report['code_doc_sha256'][new.PRODUCT_CODE])
        self.assertTrue(c['path_field_values_computed']);self.assertFalse(c['accepted_source_product_absolute_CPU_only'])
        self.assertGreater(F(*c['paths'][0]['composed_path_field_error_L1_upper_rational']),0)
        for name in ('mirror_phase_FAIL','mirror_phase_underflow_FAIL','mode_FAIL','source0_FAIL','underflow_FAIL','high_intensity_FAIL'):
            c=self.audit['cases'][name]
            self.assertFalse(c['path_field_values_computed']);self.assertEqual(c['new_RN64_operations'],0)
        self.evidence['rejections']['upstream_and_budget']='six upstream stops; cached source_decode positive bound exceeds zero budget'

    def test_binding_gauge_coverage_groups_reject(self):
        args=(self.units['quarter0'],self.sources['quarter0'],self.old['quarter0'],self.report['code_doc_sha256'][new.PRODUCT_CODE])
        for which in ('binding','gauge','coverage','group','cached_coverage'):
            u,s,o=map(deepcopy,args[:3])
            if which=='binding':u['decoded_scene_binding_sha256']='bad'
            if which=='gauge':s['transport']['source_transport']['sources'][0]['source_phase_reference_id']='bad'
            if which=='coverage':u['paths'].append(deepcopy(u['paths'][0]))
            if which=='group':s['transport']['contributions'][0]['coherence_group']='bad'
            if which=='cached_coverage':o['paths']=[]
            with self.assertRaises(ValueError):new._case(u,s,o,args[3])

    def test_reflection_and_separate_sources(self):
        for i in range(4):
            p=self.audit['cases']['quarter'+str(i)]['paths'][0]
            u=self.units['quarter'+str(i)]['paths'][0]
            self.assertEqual(p['measurement']['unit_uint64'],[w^(1<<63) for w in u['unit_uint64']])
            self.assertEqual(p['mirror_coefficient_exact_reim_rational'],[[-1,1],[0,1]])
        dark=self.audit['cases']['dark']
        self.assertEqual(len(dark['paths']),2)
        self.assertTrue(all(F(*p['composed_path_field_error_L1_upper_rational'])>0 for p in dark['paths']))
        self.assertFalse(dark['scene_field_reduced'])

    def test_optin_selection_pins(self):
        for names in ([],['quarter0','quarter0'],[['bad']],['missing']):
            with self.assertRaises(ValueError):new.audit_retained_new_argument_products(case_names=names,product_model=new.MODEL)
        with self.assertRaises(ValueError):new.audit_retained_new_argument_products(case_names=['quarter0'],product_model='GPU')
        with patch.object(new,'SHA','0'*64):
            with self.assertRaisesRegex(ValueError,'SHA'):new.load_retained()
        with patch.object(new,'PRODUCT_SHA','0'*64):
            with self.assertRaisesRegex(ValueError,'SHA'):new.load_retained()

if __name__=='__main__':
    r=unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(NewArgumentProductTests))
    if hasattr(NewArgumentProductTests,'evidence'):print(json.dumps(NewArgumentProductTests.evidence,sort_keys=True,allow_nan=False))
    sys.exit(0 if r.wasSuccessful() else 1)
