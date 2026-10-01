"""Own reference argument tests; no frozen producer/suite replay."""
from copy import deepcopy
from fractions import Fraction as F
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks'/'capacity_audit'))
import axial_reference_argument_cpu_v1 as m
from axial_selector_int256_cpu_v1 import pack


class ReferenceArgumentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pins,cls.inputs,cls.cache=m.load_retained()
        cls.output=m.audit(model=m.MODEL)
        cls.numeric_controls=[]

    def call(self,c,sha=None):
        return m.integrate(c,self.cache,model=m.MODEL,expected_case_sha256=sha or m.digest(c))

    def test_scope_coverage_and_upstream_failures(self):
        self.assertEqual(self.output['counts'],{'cases':13,'sources':14,'arguments':6,'accepted_cases_CPU_only':5})
        for n,c in self.output['cases'].items():
            old=self.inputs['audit']['cases'][n]
            self.assertEqual(c['source_order'],old['source_order'])
            self.assertEqual(c['retained_closure_gates_UNCHANGED'],old['retained_closure_gates_UNCHANGED'])
            for p,q in zip(c['paths'],old['paths']):
                self.assertEqual(p['argument_available'],q['accepted_reference_quotient_CPU_only'])
                if not q['accepted_reference_quotient_CPU_only']:
                    self.assertNotIn('measurement',p)
                    self.assertFalse(p['accepted_argument_CPU_only'])
        self.assertFalse(self.output['cases']['declared_radius_PASS']['accepted_argument_CPU_only'])
        self.assertFalse(self.output['cases']['two_sources']['retained_closure_gates_UNCHANGED'][-1])

    def test_new_reference_charges_same_caps_and_gauges(self):
        for n,c in self.output['cases'].items():
            for p,q in zip(c['paths'],self.inputs['audit']['cases'][n]['paths']):
                if not p['argument_available']:
                    continue
                extra=sum((m.rat(v) for v in p['new_argument_error_charges_rad'].values()),F(0))
                self.assertEqual(m.rat(p['composed_argument_phase_bound_rad']),m.rat(q['composed_phase_bound_rad'])+extra)
                self.assertEqual(p['phase_budget_rad'],q['phase_budget_rad'])
                self.assertEqual(p['original_reference_cycles'],q['original_reference_cycles'])
                self.assertEqual(p['source_phase_reference_id'],q['source_phase_reference_id'])
                self.assertEqual(p['terminal_reference_id'],q['terminal_reference_id'])

    def test_cache_only_math_never_old_admission(self):
        for c in self.output['cases'].values():
            for p in c['paths']:
                if p['argument_available'] and p['argument_cache']['cache_hit']:
                    self.assertFalse(p['argument_evaluated'])
                    self.assertIn('phase bound/budget/admission',p['argument_cache']['not_reused'])
        seen=sum(p['argument_available'] for c in self.output['cases'].values() for p in c['paths'])
        costs=self.output['costs']
        self.assertEqual(costs['new_RN64_multiply']+costs['cached_RN64_multiply_NOT_executed'],seen)
        self.assertEqual(costs['new_bit_conversion']+costs['cached_bit_conversion_NOT_executed'],seen)
        # Exact zero residual graph is reusable across distinct original mode bindings.
        zero=self.inputs['controls']['new_mode_minus_quarter_different_observable_CAP0']
        with patch.object(m,'argument_words',side_effect=AssertionError('no zero graph replay')):
            out=self.call(zero)
        self.assertEqual(out['paths'][0]['original_reference_cycles'],[6,1])
        self.assertEqual(out['paths'][0]['integer_turn'],6)
        self.assertEqual(out['paths'][0]['phase_budget_rad'],[0,1])
        self.assertTrue(out['accepted_argument_CPU_only'])

    def test_retained_changed_mode_controls_not_equivalent_improvement(self):
        a=self.output['controls']['new_mode_minus_quarter_different_observable_CAP0']
        b=self.output['controls']['new_mode_point_one_CAP0_FAIL_upstream_stop']
        self.assertNotEqual(a['scene_binding_sha256'],self.output['cases']['positive']['scene_binding_sha256'])
        self.assertEqual(a['paths'][0]['original_reduced_reference_cycles'],[0,1])
        self.assertFalse(b['accepted_argument_CPU_only'])
        self.assertNotIn('measurement',b['paths'][0])
        self.assertFalse(a['accepted_full_field_pipeline'])

    def test_wrong_binding_source_order_gauge_residual_caps_reject(self):
        old=self.inputs['audit']['cases']['positive']
        c=deepcopy(old);c['scene_binding_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'digest'):
            self.call(c,m.digest(old))
        for edit in (
            lambda c:c.update(source_order=['foreign']),
            lambda c:c['paths'][0].update(source_phase_reference_id='foreign'),
            lambda c:c['paths'][0].update(terminal_reference_id='foreign'),
            lambda c:c['paths'][0]['selector'].update(residual_cycles_signed256_words=pack(1)),
            lambda c:c['paths'][0]['selector'].update(integer_turn=True),
            lambda c:c['paths'][0].update(phase_budget_rad=[-1,1]),
            lambda c:c['paths'][0].update(accepted_reference_quotient_CPU_only=1)):
            c=deepcopy(old);edit(c)
            with self.assertRaises(ValueError):
                self.call(c)

    def test_pins_cache_corruption_and_explicit_model(self):
        with patch.object(m,'SHA','0'*64):
            with self.assertRaisesRegex(ValueError,'SHA'):
                m.load_retained()
        with self.assertRaises(ValueError):
            m.audit(model='native')
        cache=deepcopy(self.cache)
        item=next(iter(cache.bank.values()))
        item['output']['argument_uint64']^=1
        with self.assertRaisesRegex(ValueError,'corrupt'):
            cache.find(item['key']['residual_words'])
        for w in (True,1<<32,-1):
            with self.assertRaises(ValueError):
                self.cache.find([w]+[0]*7)

    def test_new_synthetic_conversion_boundaries_ties_and_sign(self):
        values=[1,-1,1<<146,-(1<<146),(1<<145)+(1<<92),(1<<145)+(1<<93)+(1<<92)]
        for n in values:
            words=pack(n)
            value=m.argument_words(words,argument_model=m.ARGUMENT)
            self.numeric_controls.append({'input_signed256':n,'scope':'NEW synthetic argument ABI only; not scene/fixture/GPU',
                                          'measurement':value})
            self.assertLessEqual(abs(m.component64(value['argument_uint64'])),1)
        self.assertTrue(self.numeric_controls[-1]['measurement']['conversion']['tie'])
        self.assertTrue(self.numeric_controls[-1]['measurement']['conversion']['rounded_up'])
        self.assertTrue(self.numeric_controls[-2]['measurement']['conversion']['tie'])
        self.assertFalse(self.numeric_controls[-2]['measurement']['conversion']['rounded_up'])
        with self.assertRaises(ValueError):
            m.argument_words(pack((1<<146)+1),argument_model=m.ARGUMENT)

    def test_no_unit_native_full_field_or_cost_claim(self):
        for flag in ('GPU_executed','ALU_executed','Bpy_executed','execution_authenticated',
                     'physical_coherence_verified','native_promotion_allowed','accepted_full_field_pipeline',
                     'unit_computed','fields_computed','old_upstream_producer_rerun'):
            self.assertIs(self.output[flag],False)


if __name__=='__main__':
    result=unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(ReferenceArgumentTests))
    if hasattr(ReferenceArgumentTests,'output'):
        print(json.dumps({'audit':ReferenceArgumentTests.output,
              'numeric_controls':ReferenceArgumentTests.numeric_controls,
              'numeric_control_costs_separate':{'new_bit_conversion':6,'new_RN64_multiply':6}},
              sort_keys=True,separators=(',',':'),allow_nan=False))
    raise SystemExit(not result.wasSuccessful())
