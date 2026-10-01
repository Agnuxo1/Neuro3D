"""New referenced unit tests; frozen graphs are read, not replayed."""
from copy import deepcopy
from fractions import Fraction as F
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks'/'capacity_audit'))
import axial_reference_unit_cpu_v1 as m


class ReferenceUnitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pins,cls.inputs,cls.cache=m.load_retained()
        cls.output=m.audit(model=m.MODEL)

    def call(self,c,sha=None):
        return m.integrate(c,self.cache,model=m.MODEL,expected_case_sha256=sha or m.digest(c))

    def test_complete_scope_and_upstream_failures_intact(self):
        self.assertEqual(self.output['counts'],{'cases':13,'sources':14,'units':6,'accepted_cases_CPU_only':5})
        for name,c in self.output['cases'].items():
            old=self.inputs['audit']['cases'][name]
            self.assertEqual(c['source_order'],old['source_order'])
            self.assertEqual(c['retained_closure_gates_UNCHANGED'],old['retained_closure_gates_UNCHANGED'])
            for p,q in zip(c['paths'],old['paths']):
                self.assertEqual(p['unit_available'],q['accepted_argument_CPU_only'])
                if not q['accepted_argument_CPU_only']:
                    self.assertNotIn('unit_measurement',p)
                    self.assertFalse(p['accepted_unit_CPU_only'])
        self.assertFalse(self.output['cases']['declared_radius_PASS']['accepted_unit_CPU_only'])
        self.assertFalse(self.output['cases']['two_sources']['retained_closure_gates_UNCHANGED'][-1])

    def test_new_bounds_original_cap_derived_budget_and_gauges(self):
        for name,c in self.output['cases'].items():
            for p,q in zip(c['paths'],self.inputs['audit']['cases'][name]['paths']):
                if not p['unit_available']:
                    continue
                total=sum((m.rat(v) for v in p['new_unit_error_charges_L1'].values()),F(0))
                self.assertEqual(total,2*m.rat(q['composed_argument_phase_bound_rad'])+m.rat(p['pure_unit_error_L1_upper']))
                self.assertEqual(m.rat(p['composed_unit_error_L1_upper']),total)
                self.assertEqual(m.rat(p['derived_unit_L1_budget']),2*m.rat(q['phase_budget_rad']))
                self.assertEqual(p['phase_budget_rad'],q['phase_budget_rad'])
                self.assertEqual(p['source_phase_reference_id'],q['source_phase_reference_id'])
                self.assertEqual(p['terminal_reference_id'],q['terminal_reference_id'])
                self.assertEqual(p['accepted_unit_CPU_only'],total<=2*m.rat(q['phase_budget_rad']))

    def test_cache_does_not_replay_old_unit(self):
        with patch.object(m,'rotation64',side_effect=AssertionError('no old unit producer replay')):
            for c in self.inputs['audit']['cases'].values():
                self.call(c)
        costs=self.output['costs']
        self.assertEqual(costs,{'new_Horner_RN64':0,'cached_Horner_RN64_NOT_executed':156,
            'new_coefficient_HOST_RN64':0,'cached_coefficient_HOST_RN64_NOT_executed':84,
            'quarter_bit_sign_toggles_new':5,'quarter_word_swaps_new':1})
        for c in self.output['cases'].values():
            for p in c['paths']:
                if p['unit_available']:
                    self.assertFalse(p['unit_evaluated'])
                    self.assertIn('phase/L1 bounds and caps/admission',p['unit_cache']['not_reused'])

    def test_signed_quarter_and_separate_source_ids(self):
        a,b=self.output['cases']['two_sources']['paths']
        self.assertEqual(a['observed_unit_rational'],[[1,1],[0,1]])
        self.assertEqual(b['observed_unit_rational'],[[-1,1],[0,1]])
        self.assertNotEqual(a['source_phase_reference_id'],b['source_phase_reference_id'])
        words=[0x3ff0000000000000,0]
        for k in (-2,-1,0,1,2):
            out,costs=m.apply_quarter(words,k)
            self.assertEqual([m.component64(w) for w in out],
                             {0:[1,0],1:[0,1],2:[-1,0],3:[0,-1]}[k%4])
        for k in (True,3,-3):
            with self.assertRaises(ValueError):
                m.apply_quarter(words,k)

    def test_retained_mode_controls_not_field_or_equivalent_improvement(self):
        a=self.output['controls']['new_mode_minus_quarter_different_observable_CAP0']
        b=self.output['controls']['new_mode_point_one_CAP0_FAIL_upstream_stop']
        self.assertTrue(a['accepted_unit_CPU_only'])
        self.assertNotEqual(a['scene_binding_sha256'],self.output['cases']['positive']['scene_binding_sha256'])
        self.assertEqual(a['paths'][0]['original_reference_cycles'],[6,1])
        self.assertEqual(a['paths'][0]['derived_unit_L1_budget'],[0,1])
        self.assertFalse(b['accepted_unit_CPU_only'])
        self.assertNotIn('unit_measurement',b['paths'][0])

    def test_new_numeric_unit_controls_have_explicit_separate_costs(self):
        controls=self.output['numeric_unit_controls']
        self.assertEqual(len(controls),6)
        for p,q in zip(controls,self.inputs['numeric_controls']):
            self.assertFalse(p['unit_cache']['cache_hit'])
            self.assertEqual(p['input_argument_uint64'],q['measurement']['argument_uint64'])
            self.assertEqual(p['retained_argument_control_sha256'],m.digest(q))
            self.assertEqual(p['unit_measurement']['RN64_operations'],26)
            self.assertNotIn('accepted_unit_CPU_only',p)
        self.assertEqual(self.output['numeric_unit_control_costs_separate'],{
            'new_Horner_RN64':156,'cached_Horner_RN64_NOT_executed':0,
            'new_coefficient_HOST_RN64':84,'cached_coefficient_HOST_RN64_NOT_executed':0,
            'quarter_bit_sign_toggles_new':6,'quarter_word_swaps_new':2})

    def test_reject_provenance_corruption_and_domains(self):
        old=self.inputs['audit']['cases']['positive'];c=deepcopy(old);c['scene_binding_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'digest'):
            self.call(c,m.digest(old))
        for edit in (
            lambda c:c.update(source_order=['foreign']),
            lambda c:c['paths'][0].update(terminal_reference_id='foreign'),
            lambda c:c['paths'][0].update(source_phase_reference_id='foreign'),
            lambda c:c['paths'][0].update(quarter_index=True),
            lambda c:c['paths'][0].update(phase_budget_rad=[-1,1]),
            lambda c:c['paths'][0].update(composed_argument_phase_bound_rad=[1,1]),
            lambda c:c['paths'][0].update(accepted_argument_CPU_only='PASS')):
            c=deepcopy(old);edit(c)
            with self.assertRaises(ValueError):
                self.call(c)
        cache=deepcopy(self.cache);item=next(iter(cache.bank.values()))
        item['output']['unit_error_L1_upper_rational']=[1,1]
        with self.assertRaisesRegex(ValueError,'corrupt'):
            cache.find(item['key']['angle_uint64'])
        for w in (True,1,0x7ff0000000000000,0x4000000000000000):
            with self.assertRaises(ValueError):
                self.cache.find(w)
        with patch.object(m,'SHA','0'*64):
            with self.assertRaisesRegex(ValueError,'SHA'):
                m.load_retained()
        with self.assertRaises(ValueError):
            m.audit(model='native')

    def test_no_source_mirror_field_or_hardware_promotion(self):
        for flag in ('GPU_executed','ALU_executed','Bpy_executed','execution_authenticated',
                     'physical_coherence_verified','native_promotion_allowed','accepted_full_field_pipeline',
                     'source_fields_computed','mirror_phase_computed','old_upstream_producer_rerun'):
            self.assertIs(self.output[flag],False)


if __name__=='__main__':
    result=unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(ReferenceUnitTests))
    if hasattr(ReferenceUnitTests,'output'):
        print(json.dumps({'audit':ReferenceUnitTests.output},sort_keys=True,separators=(',',':'),allow_nan=False))
    raise SystemExit(not result.wasSuccessful())
