"""Scene-derived group/detector tests; all group declarations are CPU hypotheses."""
from copy import deepcopy
from fractions import Fraction as F
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'Blender/tests'));sys.path.insert(0,str(ROOT/'Blender/benchmarks/capacity_audit'))
import axial_geometry_reduction_cpu_v1 as new
class ReductionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pins,cls.sources,cls.steps,cls.detectors,cls.adds=new.load_retained()
        cls.limits={'field_L1':F(1,10**12),'power':F(1,10**12),'relative_field':F(1,10**6),'relative_power':F(1,10**6)}
        cls.contracts={n:new.contract_for(c,{sid:'g' for sid in c['source_order']},cls.limits) for n,c in cls.sources.items()}
        with patch('axial_geometry_source_cpu_v1.audit_scene_source_products',side_effect=AssertionError('no source replay')),patch('axial_geometry_unit_cpu_v1.audit_retained_scene_units',side_effect=AssertionError('no unit replay')),patch('axial_geometry_words_cpu_v1.geometry_words',side_effect=AssertionError('no geometry replay')):
            cls.audit=new.audit_scene_reduction(case_names=list(cls.sources),case_contracts=cls.contracts,reduction_model=new.MODEL)
        cls.evidence={'audit':cls.audit}
    def compose(self,name,contract=None):
        return new.compose(self.sources[name],contract or self.contracts[name],self.steps,self.detectors,self.adds,self.pins[new.CODE])
    def test_accepted_single_sources_have_new_composed_bounds(self):
        for n in ('positive','negative','thin_resolved','nonexact_geometry_phase_PASS'):
            c=self.audit['cases'][n];self.assertTrue(c['accepted_reduction_detector_CPU_only'])
            p=c['ports']['D'];g=p['groups']['g'];source=self.sources[n]['paths'][0]
            self.assertEqual(g['path_error_L1'],source['composed_path_field_error_L1'])
            e=F(*g['composed_field_error_L1']);norm=sum(map(abs,map(lambda x:F(*x),g['observed_field_rational'])),F(0))
            self.assertEqual(F(*g['transport_power_error']),2*norm*e+e*e)
            self.assertEqual(p['relative_power']['status'],'CERTIFIED_BOUND')
    def test_coherent_zero_must_reject_relative_not_force_PASS(self):
        c=self.audit['cases']['two_sources'];p=c['ports']['D'];g=p['groups']['g']
        self.assertTrue(c['scene_field_reduced']);self.assertTrue(c['detector_evaluated'])
        self.assertEqual(g['observed_field_rational'],[[0,1],[0,1]])
        self.assertEqual(p['observed_power_rational'],[0,1])
        self.assertGreater(F(*g['composed_field_error_L1']),0)
        self.assertFalse(c['accepted_reduction_detector_CPU_only'])
        self.assertEqual(g['relative_field']['status'],'NO_POSITIVE_REFERENCE_LOWER_BOUND')
        self.assertEqual(p['relative_power']['status'],'NO_POSITIVE_REFERENCE_LOWER_BOUND')
        self.assertFalse(c['coherence_authenticated'])
    def test_explicit_separate_groups_change_observable_not_threshold(self):
        c=self.sources['two_sources'];contract=new.contract_for(c,{'s':'one','other':'two'},self.limits)
        out=self.compose('two_sources',contract);self.evidence['separate_group_control']=out
        self.assertTrue(out['accepted_reduction_detector_CPU_only'])
        self.assertEqual(out['contract']['limits'],self.audit['cases']['two_sources']['contract']['limits'])
        p=out['ports']['D'];self.assertEqual(set(p['groups']),{'one','two'})
        self.assertGreater(F(*p['observed_power_rational']),F(19,1000))
        self.assertLess(F(*p['observed_power_rational']),F(21,1000))
    def test_all_upstream_stops_do_not_reduce(self):
        for n,c in self.audit['cases'].items():
            if self.sources[n]['accepted_source_product_absolute_CPU_only']:continue
            self.assertFalse(c['scene_field_reduced']);self.assertFalse(c['detector_evaluated'])
            self.assertEqual(c['new_RN64_operations'],0);self.assertEqual(c['cached_RN64_operations_NOT_executed'],0)
            self.assertEqual(c['ports'],{})
    def test_exact_word_cache_and_costs_not_execution_claim(self):
        count=0
        for c in self.audit['cases'].values():
            for sig in c['cache_signatures']:
                self.assertEqual(sig['model'],new.NUMERIC);self.assertEqual(sig['code_sha256'],self.pins[new.CODE])
                n={'reduce2':2,'detector3':3,'power_add1':1}[sig['kind']];count+=n
                self.assertIn(sig['report_sha256'],(None,new.CACHE_SHA))
        self.assertEqual(count,self.audit['new_RN64_operations']+self.audit['cached_RN64_operations_NOT_executed'])
        self.assertGreater(self.audit['cached_RN64_operations_NOT_executed'],0)
        self.assertGreater(self.audit['new_RN64_operations'],0)
    def test_zero_cap_preserves_identical_numeric_evidence(self):
        ct=deepcopy(self.contracts['positive']);ct['limits']['field_L1']=0;out=self.compose('positive',ct)
        self.evidence['zero_cap_control']=out
        self.assertFalse(out['accepted_reduction_detector_CPU_only'])
        self.assertEqual(out['ports']['D']['groups']['g']['detector'],self.audit['cases']['positive']['ports']['D']['groups']['g']['detector'])
        self.assertFalse(out['ports']['D']['groups']['g']['field_absolute_pass'])
    def test_complete_order_binding_reference_and_declaration_required(self):
        for key in ('binding','reference','assignment','order','declaration','limits','type'):
            c=deepcopy(self.contracts['two_sources'])
            if key=='binding':c['scene_binding_sha256']='wrong'
            if key=='reference':c['assignments'][0]['common_phase_reference_id']='wrong'
            if key=='assignment':c['assignments'].pop()
            if key=='order':c['assignments'].reverse()
            if key=='declaration':c['grouping_provenance']='measured physical optics'
            if key=='limits':c['limits'].pop('power')
            if key=='type':c['assignments'][0]['coherence_group']=True
            with self.assertRaises(ValueError):self.compose('two_sources',c)
        with self.assertRaises(ValueError):new.contract_for(self.sources['positive'],{'s':True},self.limits)
    def test_selection_SHA_and_no_native_full_or_auth(self):
        for names in ([],['positive','positive'],['unknown'],[True]):
            with self.assertRaises(ValueError):new.audit_scene_reduction(case_names=names,case_contracts={},reduction_model=new.MODEL)
        with self.assertRaises(ValueError):new.audit_scene_reduction(case_names=['positive'],case_contracts={},reduction_model='GPU')
        with patch.object(new,'SHA','0'*64):
            with self.assertRaisesRegex(ValueError,'SHA'):new.load_retained()
        for flag in ('GPU_executed','ALU_executed','native_reduction_detector_implemented','execution_authenticated','coherence_authenticated','accepted_full_field_pipeline','native_promotion_allowed','geometry_unit_source_or_producer_rerun'):
            self.assertFalse(self.audit[flag])
        self.assertEqual(len(self.pins),106)
if __name__=='__main__':
    r=unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(ReductionTests))
    if hasattr(ReductionTests,'evidence'):print(json.dumps(ReductionTests.evidence,sort_keys=True,allow_nan=False))
    sys.exit(0 if r.wasSuccessful() else 1)
