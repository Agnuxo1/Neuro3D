"""New reference bridge contract tests; no frozen suite/writer replay."""
from copy import deepcopy
from fractions import Fraction as F
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'benchmarks'/'capacity_audit'))
import axial_reference_quotient_cpu_v1 as m
import axial_terminal_reference_cpu_v1 as ref
import axial_tree_completeness_cpu_v1 as tree


def fresh_mode_control(g, new_x):
    # Explicit NEW synthetic profile: old snapshot file is not modified.
    g=deepcopy(g);g['scene_snapshot']['objects']['D']['mode_origin_BU'][0]=new_x
    a=g['word_ABI']
    b=m.digest({'snapshot':g['scene_snapshot'],'object_order':a['object_ids'],'source_order':a['source_order']})
    a['original_scene_binding_sha256']=b;g['word_ABI_sha256']=m.digest(a)
    for p in g['sources']:
        if 'phase_reference_id' in p:p['phase_reference_id']='original-source-zero:'+b+':'+p['source_id']
    r=ref.check_case(g,reference_model=ref.MODEL,reference_frame=ref.FRAME)
    t=tree.verify_witness(g,tree.make_witness(g,model=tree.MODEL),model=tree.MODEL)
    return g,r,t


class ReferenceQuotientTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pins,cls.geometry,cls.refs,cls.trees,cls.cache=m.load_retained()
        # All retained quotient/encoding inputs hit; no filler RN computations.
        with patch.object(m,'quotient_words',side_effect=AssertionError('no old quotient replay')),patch.object(m,'encode_hilo',side_effect=AssertionError('no old encoding replay')):
            cls.output=m.audit(model=m.MODEL)
        cls.controls={}
        cls.control_inputs={}

    def call(self,g,r,t):
        return m.integrate(g,r,t,self.cache,model=m.MODEL)

    def test_scope_coverage_and_failures_unchanged(self):
        self.assertEqual(self.output['counts'],{'cases':13,'sources':14,'evaluated_paths':7,'accepted_cases_CPU_only':5})
        for name,c in self.output['cases'].items():
            self.assertEqual(c['retained_closure_gates_UNCHANGED'],self.trees[name]['retained_closure_gates_UNCHANGED'])
            self.assertFalse(c['accepted_full_field_pipeline'])
        for name in ('thin_collapsed_FAIL','source_contact_FAIL','otherowner_contact_FAIL','boundary_FAIL',
                     'declared_contact_FAIL','nonexact_geometry_phase_FAIL','lambda_transport_FAIL'):
            self.assertFalse(self.output['cases'][name]['paths'][0]['arithmetic_evaluated'])
        self.assertFalse(self.output['cases']['two_sources']['retained_closure_gates_UNCHANGED'][-1])
        for f in ('geometry_or_old_producer_rerun','GPU_executed','ALU_executed','Bpy_executed',
                  'execution_authenticated','physical_coherence_verified','native_promotion_allowed',
                  'accepted_full_field_pipeline','fields_computed'):
            self.assertIs(self.output[f],False)

    def test_new_costs_not_old_numeric_replays(self):
        self.assertEqual(self.output['costs'],{
            'length_integer_new':22,'HOST_length_RN32_new':0,'HOST_length_RN32_cached_NOT_executed':14,
            'quotient_RN32_new':0,'quotient_RN32_cached_NOT_executed':35,
            'selector_integer_new':19,'selector_integer_cached_NOT_executed':126})
        for c in self.output['cases'].values():
            for p in c['paths']:
                if not p['arithmetic_evaluated']:continue
                self.assertTrue(p['encoding_cache']['cache_hit'])
                self.assertTrue(p['quotient_cache']['cache_hit'])
                self.assertIn('reference.center.minusR',[n['label'] for n in p['reference_length_integer_operations']])
                self.assertNotIn('length.center.minusD',[n['label'] for n in p['reference_length_integer_operations']])

    def test_new_reference_bounds_budget_and_original_gauge(self):
        for c in self.output['cases'].values():
            for p in c['paths']:
                if not p['arithmetic_evaluated']:continue
                numeric=sum(m.rat(p[k]) for k in ('length_encoding_charge_cycles','quotient_RN_charge_cycles','discarded_lambda_low_charge_cycles'))
                self.assertEqual(m.rat(p['composed_phase_bound_rad']),m.rat(p['reference_phase_bound_rad'])+8*numeric)
                q=m.rat(p['measurement']['modeled_quotient_rational']);original=m.rat(p['original_reference_cycles'])
                self.assertLessEqual(8*abs(q-original),m.rat(p['composed_phase_bound_rad']))
                self.assertNotEqual(p['source_phase_reference_id'],p['terminal_reference_id'])

    def test_declared_quarter_failure_stays_failure_not_rescued(self):
        p=self.output['cases']['declared_radius_PASS']['paths'][0]
        self.assertTrue(p['previous_reference_accepted'])
        self.assertEqual(p['reference_phase_bound_rad'],[3,2])
        self.assertEqual(p['phase_budget_rad'],[2,1])
        self.assertFalse(p['accepted_reference_quotient_CPU_only'])
        self.assertIn('quarter branch uncertain',p['selector']['reason'])
        self.assertFalse(p['selector_cache']['cache_hit'])

    def test_changed_original_mode_drives_new_quotient_without_caps_change(self):
        g,r,t=fresh_mode_control(self.geometry['positive'],-0.25)
        out=self.call(g,r,t);p=out['paths'][0]
        self.assertNotEqual(out['scene_binding_sha256'],self.output['cases']['positive']['scene_binding_sha256'])
        self.assertEqual(p['length_center_BU'],[3,4])
        self.assertEqual(p['original_reference_cycles'],[6,1])
        self.assertEqual(p['measurement']['modeled_quotient_rational'],[6,1])
        self.assertEqual(p['selector']['integer_turn'],6)
        self.assertEqual(p['phase_budget_rad'],[0,1])
        self.assertTrue(out['accepted_reference_quotient_CPU_only'])
        self.assertEqual(out['costs'],{'length_integer_new':3,'HOST_length_RN32_new':2,
            'HOST_length_RN32_cached_NOT_executed':0,'quotient_RN32_new':5,
            'quotient_RN32_cached_NOT_executed':0,'selector_integer_new':21,
            'selector_integer_cached_NOT_executed':0})
        self.controls['new_mode_minus_quarter_different_observable_CAP0']=out
        self.control_inputs['new_mode_minus_quarter_different_observable_CAP0']={
            'base_case':'positive','new_original_modepoint_X':-0.25,
            'reference_certificate':r,'tree_certificate':t}
        g,r,t=fresh_mode_control(self.geometry['positive'],0.1)
        out=self.call(g,r,t)
        self.assertFalse(out['paths'][0]['arithmetic_evaluated'])
        self.assertFalse(out['accepted_reference_quotient_CPU_only'])
        self.controls['new_mode_point_one_CAP0_FAIL_upstream_stop']=out
        self.control_inputs['new_mode_point_one_CAP0_FAIL_upstream_stop']={
            'base_case':'positive','new_original_modepoint_X':0.1,
            'reference_certificate':r,'tree_certificate':t}

    def test_wrong_reference_tree_identity_coverage_and_gauge_reject(self):
        for change in (
                lambda r:r.update(reference_frame='co-moving detector'),
                lambda r:r.update(geometry_case_sha256='0'*64),
                lambda r:r.update(source_ids=['foreign']),
                lambda r:r['paths'][0].update(terminal_reference_id='foreign'),
                lambda r:r['paths'][0].update(phase_budget_rad=[1,1]),
                lambda r:r['paths'][0].update(effective_reference_length_interval_BU=[[1,1],[1,1]])):
            r=deepcopy(self.refs['positive']);change(r)
            with self.assertRaises(ValueError):self.call(self.geometry['positive'],r,self.trees['positive'])
        t=deepcopy(self.trees['positive']);t['certificate_sha256']='0'*64
        with self.assertRaises(ValueError):self.call(self.geometry['positive'],self.refs['positive'],t)
        with self.assertRaises(ValueError):m.integrate(self.geometry['positive'],self.refs['positive'],self.trees['positive'],self.cache,model='native')

    def test_corrupt_cache_and_input_identity_no_admission_reuse(self):
        cache=deepcopy(self.cache)
        item=next(iter(cache.tables['quotient'].values()));item['output']['quotient_error_upper_rational']=[0,2]
        # Locate this very entry directly; changed data cannot be credited as cache hit.
        with self.assertRaises(ValueError):cache.find('quotient',item['key']['inputs'])
        a,info=self.cache.find('quotient',[[0,0],0x3e000000])
        self.assertIsNone(a);self.assertFalse(info['cache_hit'])
        for c in self.output['cases'].values():
            for p in c['paths']:
                if p['arithmetic_evaluated']:
                    self.assertIn('scene acceptance',p['quotient_cache']['not_reused'])

    def test_nonfinite_word_bool_radius_and_original_caps_reject(self):
        for w in (True,-1,1<<32,1,0x7f800000):
            with self.assertRaises(ValueError):m.decode([w,0])
        for v in (True,-1,1<<511):
            with self.assertRaises(ValueError):m.integer_radius(v)
        r=deepcopy(self.refs['positive']);r['paths'][0]['previous_phase_accepted']='PASS'
        with self.assertRaises(ValueError):self.call(self.geometry['positive'],r,self.trees['positive'])


if __name__=='__main__':
    result=unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(ReferenceQuotientTests))
    if result.wasSuccessful():print(json.dumps({'audit':ReferenceQuotientTests.output,'controls':ReferenceQuotientTests.controls,
        'control_inputs':ReferenceQuotientTests.control_inputs,
        'control_scope':'new mode-reference synthetic CPU profiles with different binding/observable, not equivalent fixture improvement; new HOST mode and tree controls cost separate'},
        sort_keys=True,separators=(',',':'),allow_nan=False))
    raise SystemExit(not result.wasSuccessful())
