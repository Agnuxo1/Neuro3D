"""Own bridge tests: reuse pinned geometry, no frozen geometry or producer replay."""
from copy import deepcopy
from fractions import Fraction as F
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'Blender/tests'))
sys.path.insert(0,str(ROOT/'Blender/benchmarks/capacity_audit'))
import axial_geometry_quotient_cpu_v1 as new
from axial_selector_int256_cpu_v1 import unpack

class BridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pins,cls.old=new.load_retained();cls.evidence={'rejections':{}}
        with patch('axial_geometry_words_cpu_v1.geometry_words',side_effect=AssertionError('no frozen geometry replay')),patch('axial_geometry_words_cpu_v1.audit_scene_geometry_words',side_effect=AssertionError('no scene replay')),patch('axial_phase_quotient_cpu_v1.centered_selector',side_effect=AssertionError('no rational selector fallback')):
            cls.audit=new.audit_retained_bridge(case_names=list(cls.old),bridge_model=new.MODEL)
        cls.evidence['audit']=cls.audit
    def test_exact_signed_paths_and_source_gauge(self):
        for name in ('positive','negative'):
            c=self.audit['cases'][name];p=c['paths'][0]
            self.assertTrue(c['accepted_bridge_phase_CPU_only'])
            self.assertEqual(p['length_center_BU_rational'],[5,8])
            self.assertEqual(p['composed_phase_bound_rad'],[0,1])
            self.assertEqual((p['selector']['integer_turn'],p['selector']['quarter_index']),(5,0))
            self.assertEqual(unpack(p['center_length_scaled_signed256_words']),5*new.S//8)
    def test_topology_rejections_do_not_execute_arithmetic(self):
        for name in ('thin_collapsed_FAIL','source_contact_FAIL','otherowner_contact_FAIL','boundary_FAIL','declared_contact_FAIL'):
            c=self.audit['cases'][name]
            self.assertFalse(c['accepted_bridge_phase_CPU_only']);self.assertEqual(c['quotient_RN32_operations'],0)
            self.assertTrue(all(not p['arithmetic_evaluated'] for p in c['paths']))
    def test_phase_fail_not_promoted_and_charges_recomposed(self):
        for name,c in self.audit['cases'].items():
            self.assertEqual(c['previous_geometry_accepted'],self.old[name]['accepted_geometry_words_CPU_only'])
            self.assertEqual(c['previous_phase_accepted'],self.old[name]['accepted_phase_budget_CPU_only'])
            if not c['previous_phase_accepted']:self.assertFalse(c['accepted_bridge_phase_CPU_only'])
            for p in c['paths']:
                if not p['arithmetic_evaluated']:continue
                charge=sum(F(*p[k]) for k in ('length_encoding_charge_cycles','quotient_RN_charge_cycles','discarded_lambda_low_charge_cycles'))
                self.assertEqual(F(*p['composed_phase_bound_rad']),F(*p['geometry_phase_bound_rad'])+8*charge)
                self.assertEqual(p['phase_budget_rad'],self.old[name]['sources'][c['paths'].index(p)]['phase_budget_rad'])
    def test_lambda_low_not_ignored_without_charge(self):
        p=self.audit['cases']['lambda_transport_FAIL']['paths'][0]
        self.assertTrue(p['quotient_uses_high32_explicit'])
        self.assertGreater(F(*p['discarded_lambda_low_charge_cycles']),0)
        self.assertNotEqual(p['quotient_wavelength_BU_rational'],p['full_wavelength_center_BU_rational'])
        self.assertFalse(p['accepted_bridge_phase_CPU_only'])
    def test_uncertain_quarter_rejects_despite_previous_phase_PASS(self):
        c=self.audit['cases']['declared_radius_PASS'];p=c['paths'][0]
        self.assertTrue(c['previous_phase_accepted'])
        self.assertFalse(c['accepted_bridge_phase_CPU_only'])
        self.assertFalse(p['selector']['accepted_CPU_integer_selector_only'])
        self.assertIn('quarter branch uncertain',p['selector']['reason'])
    def test_two_sources_keep_distinct_original_references(self):
        c=self.audit['cases']['two_sources'];a,b=c['paths']
        self.assertTrue(c['accepted_bridge_phase_CPU_only'])
        self.assertNotEqual(a['phase_reference_id'],b['phase_reference_id'])
        self.assertEqual((a['selector']['integer_turn'],b['selector']['integer_turn']),(5,6))
        self.assertEqual(b['selector']['quarter_index'],-2)
    def test_digest_optin_coverage_and_tamper_fail_closed(self):
        c=deepcopy(self.old['positive']);h=new.digest(c);c['sources'][0]['length_interval_scaled'][0]+=1
        with self.assertRaisesRegex(ValueError,'digest'):new.bridge_case(c,case_sha256=h,bridge_model=new.MODEL)
        c=deepcopy(self.old['positive']);c['sources'][0]['phase_reference_id']='altered'
        with self.assertRaisesRegex(ValueError,'gauge'):new.bridge_case(c,case_sha256=new.digest(c),bridge_model=new.MODEL)
        c=deepcopy(self.old['positive']);c['sources'][0]['length_interval_scaled'][0]+=1
        with self.assertRaisesRegex(ValueError,'enclosure'):new.bridge_case(c,case_sha256=new.digest(c),bridge_model=new.MODEL)
        for names in ([],['positive','positive'],['unknown'],[True]):
            with self.assertRaises(ValueError):new.audit_retained_bridge(case_names=names,bridge_model=new.MODEL)
        with self.assertRaises(ValueError):new.audit_retained_bridge(case_names=['positive'],bridge_model='GPU')
        with patch.object(new,'SHA','0'*64):
            with self.assertRaisesRegex(ValueError,'SHA'):new.load_retained()
        self.evidence['rejections']['integrity']='case/SHA/gauge/length/order/optin reject before promotion; no relaxed gate'
    def test_scope_and_costs_separated(self):
        for flag in ('GPU_executed','ALU_executed','native_geometry_implemented','native_selector_implemented','execution_authenticated','accepted_full_field_pipeline','field_values_computed','native_promotion_allowed','geometry_or_producer_rerun'):
            self.assertFalse(self.audit[flag])
        self.assertEqual(sum(c['retained_geometry_nodes_NOT_executed'] for c in self.audit['cases'].values()),1706)
        self.assertEqual(sum(c['quotient_RN32_operations'] for c in self.audit['cases'].values()),45)
        self.assertEqual(sum(c['HOST_length_encoding_RN32_operations'] for c in self.audit['cases'].values()),18)
        self.assertEqual(len(self.pins),94)

if __name__=='__main__':
    r=unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(BridgeTests))
    if hasattr(BridgeTests,'evidence'):print(json.dumps(BridgeTests.evidence,sort_keys=True,allow_nan=False))
    sys.exit(0 if r.wasSuccessful() else 1)
