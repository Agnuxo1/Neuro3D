"""Integrate changed argument once; reuse unchanged SHA-pinned unit words."""
from copy import deepcopy
from fractions import Fraction as F
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'Blender/benchmarks/capacity_audit'))
from axial_unit_argument_rn64_cpu_v1 import MODEL,UNIT_CODE,UNIT_SHA,load_retained,_case,audit_retained_new_argument_units
from axial_unit_rn64_cpu_v1 import rotation64,component64


class NewArgumentUnitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r,cls.arg,cls.old=load_retained();cls.code=cls.r['code_doc_sha256'][UNIT_CODE]
        with patch('axial_unit_argument_rn64_cpu_v1.rotation64',wraps=rotation64) as spy,patch('axial_selector_int256_cpu_v1.select_words',side_effect=AssertionError('no selector replay')),patch('axial_argument_pi_rn64_cpu_v1.argument_words',side_effect=AssertionError('no argument replay')),patch('scene_field_producer_cpu_v1.rotation',side_effect=AssertionError('no producer')):
            cls.audit=audit_retained_new_argument_units(case_names=list(cls.arg),unit_model=MODEL)
            cls.calls=[int(c.args[0]) for c in spy.call_args_list]
        cls.evidence={'audit':cls.audit,'new_rotation_call_uint64':cls.calls,'rejections':{}}

    def test_changed_input_only_new_Horner(self):
        self.assertEqual(self.calls,[0x3fe41b2f769cf130]);self.assertEqual(self.audit['new_RN64_operations'],26)
        self.assertEqual(self.audit['cached_RN64_operations'],520)
        for n,c in self.audit['cases'].items():
            for p in c['paths']:
                self.assertEqual(p['unit_evaluated'],n=='nonquarter_FAIL')
                self.assertEqual(p['unit_cache_reused'],n not in ['nonquarter_FAIL','mode_FAIL'])

    def test_exactword_cache_code_model_report_signature(self):
        for n,c in self.audit['cases'].items():
            for p,old in zip(c['paths'],self.old[n]['paths']):
                if not p['unit_cache_reused']:continue
                self.assertEqual(p['measurement'],old['measurement']);self.assertEqual(p['cache_signature']['report_sha256'],UNIT_SHA)
                self.assertEqual(p['cache_signature']['unit_code_sha256'],self.code)
                self.assertEqual(p['cache_signature']['angle_uint64'],p['measurement']['angle_uint64'])
        c=_case(self.arg['quarter0'],self.old['quarter0'],self.code)
        c['paths'][0]['measurement']['angle_uint64']=123
        self.assertEqual(self.old['quarter0']['paths'][0]['measurement']['angle_uint64'],0)

    def test_new_phase_charge_composition_no_old_double_count(self):
        for n,c in self.audit['cases'].items():
            for p,arg in zip(c['paths'],self.arg[n]['paths']):
                if not p['unit_cache_reused'] and not p['unit_evaluated']:continue
                self.assertEqual(p['new_argument_phase_bound_rad'],arg['composed_phase_bound_rad'])
                phase=F(*arg['composed_phase_bound_rad']);unit=F(*p['measurement']['unit_error_L1_upper_rational'])
                self.assertEqual(F(*p['composed_unit_error_L1_upper_rational']),2*phase+unit)
                self.assertEqual(F(*p['derived_unit_L1_budget_rational']),2*F(*arg['phase_budget_rad']))
                self.assertLessEqual(F(*p['composed_unit_error_L1_upper_rational']),F(*p['derived_unit_L1_budget_rational']))

    def test_nonquarter_partial_and_previous_FAIL_intact(self):
        c=self.audit['cases']['nonquarter_FAIL'];p=c['paths'][0]
        self.assertTrue(c['accepted_unit_CPU_only']);self.assertFalse(c['previous_full_case_accepted']);self.assertFalse(p['previous_RN32_unit_accepted'])
        self.assertTrue(p['previous_RN64_unit_accepted']);self.assertFalse(c['accepted_full_field_pipeline'])
        for n,c in self.audit['cases'].items():
            self.assertEqual(c['previous_full_case_accepted'],self.arg[n]['previous_full_case_accepted'])
            self.assertEqual(c['accepted_unit_CPU_only'],n!='mode_FAIL');self.assertFalse(c['field_values_computed'])

    def test_upstream_rejection_and_same_zero_budget_copies(self):
        c=self.audit['cases']['mode_FAIL'];self.assertFalse(c['accepted_unit_CPU_only']);self.assertEqual(c['new_RN64_operations']+c['cached_RN64_operations'],0)
        arg=deepcopy(self.arg['quarter0']);old=deepcopy(self.old['quarter0'])
        arg['paths'][0]['phase_budget_rad']=[0,1];old['paths'][0]['phase_budget_rad']=[0,1]
        # quarter0 has phase=0 and exact unit=1+0i: zero budget legitimately passes.
        self.assertTrue(_case(arg,old,self.code)['accepted_unit_CPU_only'])
        arg=deepcopy(self.arg['near_quarter_FAIL']);old=deepcopy(self.old['near_quarter_FAIL'])
        arg['paths'][0]['phase_budget_rad']=[0,1];old['paths'][0]['phase_budget_rad']=[0,1]
        self.assertFalse(_case(arg,old,self.code)['accepted_unit_CPU_only'])
        arg=deepcopy(self.arg['quarter0']);arg['paths'][0]['accepted_argument_CPU_only']=False
        c=_case(arg,self.old['quarter0'],self.code);self.assertEqual(c['new_RN64_operations']+c['cached_RN64_operations'],0)
        self.evidence['rejections']['upstream_budget']='mode/no argument stop; zero budget passes exact quarter0 but rejects nonzero nearquarter bound; no budget relaxation'

    def test_gauge_binding_coverage_bits_and_quarter_failclosed(self):
        for key in ['gauge','binding','coverage','bits','quarter','budget']:
            arg=deepcopy(self.arg['quarter0'])
            if key=='gauge':arg['paths'][0]['phase_reference_id']='bad'
            elif key=='binding':arg['decoded_scene_binding_sha256']='bad'
            elif key=='coverage':arg['paths'].append(deepcopy(arg['paths'][0]))
            elif key=='bits':arg['paths'][0]['measurement']['argument_uint64']=True
            elif key=='quarter':arg['paths'][0]['quarter_index']=1
            else:arg['paths'][0]['phase_budget_rad']=[1,1]
            with self.assertRaises(ValueError):_case(arg,self.old['quarter0'],self.code)

    def test_quarter_permutation_exact(self):
        expected={'quarter0':[F(1),F(0)],'quarter1':[F(0),F(1)],'quarter2':[F(-1),F(0)],'quarter3':[F(0),F(-1)]}
        for n,v in expected.items():
            p=self.audit['cases'][n]['paths'][0]
            self.assertEqual(list(map(component64,p['unit_uint64'])),v);self.assertTrue(p['unit_cache_reused'])

    def test_optin_SHA_selection_and_scope(self):
        for names in [[],['quarter0','quarter0'],[['bad']],['missing']]:
            with self.assertRaises(ValueError):audit_retained_new_argument_units(case_names=names,unit_model=MODEL)
        with self.assertRaises(ValueError):audit_retained_new_argument_units(case_names=['quarter0'],unit_model='GPU')
        with patch('axial_unit_argument_rn64_cpu_v1.SHA','0'*64):
            with self.assertRaisesRegex(ValueError,'SHA'):load_retained()
        self.assertFalse(self.audit['GPU_executed']);self.assertFalse(self.audit['ALU_executed']);self.assertFalse(self.audit['native_argument_product_implemented'])
        self.assertFalse(self.audit['old_selector_argument_quotient_scene_or_producer_rerun'])


if __name__=='__main__':
    r=unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(NewArgumentUnitTests))
    if hasattr(NewArgumentUnitTests,'evidence'):print(json.dumps(NewArgumentUnitTests.evidence,sort_keys=True,allow_nan=False))
    sys.exit(0 if r.wasSuccessful() else 1)
