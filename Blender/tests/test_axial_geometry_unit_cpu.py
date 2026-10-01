"""Scene-derived unit tests: no old geometry/quotient/selector replay."""
from fractions import Fraction as F
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'Blender/tests'));sys.path.insert(0,str(ROOT/'Blender/benchmarks/capacity_audit'))
import axial_geometry_unit_cpu_v1 as new
class UnitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pins,cls.old,cls.ab,cls.ub=new.load_retained();cls.evidence={}
        with patch('axial_geometry_quotient_cpu_v1.audit_retained_bridge',side_effect=AssertionError('no quotient bridge replay')),patch('axial_selector_int256_cpu_v1.select_words',side_effect=AssertionError('no selector replay')),patch('axial_geometry_words_cpu_v1.geometry_words',side_effect=AssertionError('no geometry replay')):
            cls.audit=new.audit_retained_scene_units(case_names=list(cls.old),unit_model=new.MODEL)
        cls.evidence['audit']=cls.audit
    def test_exact_sources_and_signed_quarter(self):
        for name in ('positive','negative','two_sources'):
            self.assertTrue(self.audit['cases'][name]['accepted_unit_CPU_only'])
        a,b=self.audit['cases']['two_sources']['paths']
        self.assertEqual(a['observed_unit_rational'],[[1,1],[0,1]])
        self.assertEqual(b['observed_unit_rational'],[[-1,1],[0,1]])
        self.assertNotEqual(a['phase_reference_id'],b['phase_reference_id'])
    def test_upstream_rejections_no_argument_unit(self):
        for name,c in self.audit['cases'].items():
            for p,old in zip(c['paths'],self.old[name]['paths']):
                self.assertEqual(p['previous_bridge_phase_accepted'],old['accepted_bridge_phase_CPU_only'])
                if not old['accepted_bridge_phase_CPU_only']:
                    self.assertFalse(p['accepted_unit_CPU_only']);self.assertNotIn('argument_measurement',p)
        self.assertFalse(self.audit['cases']['declared_radius_PASS']['accepted_unit_CPU_only'])
    def test_same_word_cache_cannot_replay_kernel(self):
        for name in ('positive','negative','two_sources'):
            for p in self.audit['cases'][name]['paths']:
                self.assertTrue(p['argument_cache_reused']);self.assertTrue(p['unit_cache_reused'])
                self.assertFalse(p['argument_evaluated']);self.assertFalse(p['unit_evaluated'])
                self.assertEqual(p['composed_unit_error_L1_upper'],[0,1])
    def test_composed_bounds_and_unchanged_budgets(self):
        for name,c in self.audit['cases'].items():
            for p,old in zip(c['paths'],self.old[name]['paths']):
                if 'argument_measurement' not in p:continue
                self.assertEqual(p['phase_budget_rad'],old['phase_budget_rad'])
                angle=sum(F(*x) for x in p['new_argument_error_charges_rad'].values())
                phase=F(*old['composed_phase_bound_rad'])+angle
                self.assertEqual(F(*p['composed_argument_phase_bound_rad']),phase)
                if 'unit_measurement' in p:
                    self.assertEqual(F(*p['composed_unit_error_L1_upper']),2*phase+F(*p['pure_unit_error_L1_upper']))
                    self.assertEqual(F(*p['derived_unit_L1_budget']),2*F(*p['phase_budget_rad']))
    def test_changed_scene_inputs_new_measurements_only(self):
        p=self.audit['cases']['thin_resolved']['paths'][0]
        self.assertFalse(p['argument_cache_reused']);self.assertFalse(p['unit_cache_reused'])
        self.assertTrue(p['argument_evaluated']);self.assertTrue(p['unit_evaluated'])
        self.assertTrue(p['accepted_unit_CPU_only'])
        # Different scene can have exactly the same PURE residual/angle words.
        p=self.audit['cases']['nonexact_geometry_phase_PASS']['paths'][0]
        words=tuple(p['argument_measurement']['residual_signed256_words']);w=p['argument_measurement']['argument_uint64']
        self.assertEqual(new.digest(p['argument_measurement']),new.digest(self.ab[words]))
        self.assertEqual(new.digest(p['unit_measurement']),new.digest(self.ub[w]))
        self.assertTrue(p['argument_cache_reused']);self.assertTrue(p['unit_cache_reused'])
        self.assertEqual(self.audit['counts'],{'new_argument_RN64':1,'cache_argument_RN64_NOT_executed':5,'new_Horner_RN64':26,'cache_Horner_RN64_NOT_executed':130})
    def test_identity_optin_SHA_and_domains(self):
        for names in ([],['positive','positive'],['unknown'],[True]):
            with self.assertRaises(ValueError):new.audit_retained_scene_units(case_names=names,unit_model=new.MODEL)
        with self.assertRaises(ValueError):new.audit_retained_scene_units(case_names=['positive'],unit_model='GPU')
        with patch.object(new,'SHA','0'*64):
            with self.assertRaisesRegex(ValueError,'SHA'):new.load_retained()
    def test_no_native_full_field_or_hardware_claim(self):
        for flag in ('GPU_executed','ALU_executed','native_geometry_implemented','native_argument_unit_implemented','execution_authenticated','accepted_full_field_pipeline','field_values_computed','native_promotion_allowed','geometry_quotient_selector_or_producer_rerun'):
            self.assertFalse(self.audit[flag])
        self.assertEqual(len(self.pins),98)
if __name__=='__main__':
    r=unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(UnitTests))
    if hasattr(UnitTests,'evidence'):print(json.dumps(UnitTests.evidence,sort_keys=True,allow_nan=False))
    sys.exit(0 if r.wasSuccessful() else 1)
