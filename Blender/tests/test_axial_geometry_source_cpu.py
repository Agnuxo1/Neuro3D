"""Scene-source product focused tests; no retained producer/kernel replays."""
from copy import deepcopy
from fractions import Fraction as F
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'Blender/tests'));sys.path.insert(0,str(ROOT/'Blender/benchmarks/capacity_audit'))
import axial_geometry_source_cpu_v1 as new

class SourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pins,cls.units,cls.geometry,cls.bank=new.load_retained()
        # New explicit per-source absolute cap, predeclared; never conf1/phase cap.
        cls.caps={n:{p['source_id']:F(1,10**12) for p in c['paths']} for n,c in cls.units.items()}
        cls.calls=[];original=new.product_words
        def spy(words,unit,**kw):
            cls.calls.append([words,unit]);return original(words,unit,**kw)
        with patch.object(new,'product_words',side_effect=spy),patch('axial_geometry_unit_cpu_v1.audit_retained_scene_units',side_effect=AssertionError('no unit replay')),patch('axial_geometry_quotient_cpu_v1.audit_retained_bridge',side_effect=AssertionError('no bridge replay')),patch('axial_geometry_words_cpu_v1.geometry_words',side_effect=AssertionError('no geometry replay')):
            cls.audit=new.audit_scene_source_products(case_names=list(cls.units),field_caps=cls.caps,product_model=new.MODEL)
        cls.evidence={'audit':cls.audit,'new_product_call_inputs':cls.calls}

    def test_source_ABI_and_separate_original_gauges(self):
        c=self.audit['cases']['two_sources'];a,b=c['paths']
        self.assertTrue(c['accepted_source_product_absolute_CPU_only'])
        self.assertNotEqual(a['phase_reference_id'],b['phase_reference_id'])
        # HOST hi-lo source transport is charged, not secretly assumed exact.
        self.assertEqual(F(*a['measurement']['observed_path_field_rational'][0]),-F(*a['measurement']['decoded_source_rational'][0]))
        self.assertEqual(F(*b['measurement']['observed_path_field_rational'][0]),F(*b['measurement']['decoded_source_rational'][0]))
        self.assertNotEqual(a['measurement']['decoded_source_rational'][0],a['source_ABI']['source_original_rational'][0])
        for p in (a,b):
            self.assertEqual(p['source_ABI']['packed_source_stride8_rational'][3],p['source_ABI']['source_original_rational'][0])
            self.assertEqual(p['source_ABI']['packed_source_stride8_rational'][7],p['source_ABI']['source_original_rational'][1])
            self.assertEqual(p['port'],'D')

    def test_all_upstream_stops_have_no_source_arithmetic(self):
        count=0
        for n,c in self.audit['cases'].items():
            for p,up in zip(c['paths'],self.units[n]['paths']):
                self.assertEqual(p['previous_unit_accepted'],up['accepted_unit_CPU_only'])
                if not up['accepted_unit_CPU_only']:
                    count+=1;self.assertNotIn('source_ABI',p);self.assertNotIn('measurement',p)
                    self.assertFalse(p['accepted_source_product_absolute_CPU_only'])
        self.assertEqual(count,8)

    def test_cache_calls_only_changed_pure_inputs(self):
        paths=[p for c in self.audit['cases'].values() for p in c['paths'] if 'measurement' in p]
        changed=[p for p in paths if tuple(p['source_ABI']['source_limb_uint32']+p['measurement']['unit_uint64']) not in self.bank]
        self.assertEqual(self.audit['new_RN64_operations'],8*len(changed))
        self.assertEqual(len(self.calls),len(changed))
        self.assertEqual(self.audit['cached_RN64_operations_NOT_executed'],8*(len(paths)-len(changed)))
        self.assertEqual(self.audit['source_HOST_RN32_encodings'],4*len(paths))
        for p in paths:
            if p['product_cache_reused']:
                k=tuple(p['measurement']['source_limb_uint32']+p['measurement']['unit_uint64'])
                self.assertEqual(new.digest(p['measurement']),new.digest(self.bank[k]))

    def test_composed_new_bounds_with_original_norm(self):
        for n,c in self.audit['cases'].items():
            for p,up in zip(c['paths'],self.units[n]['paths']):
                if 'measurement' not in p:continue
                charge=sum(F(*v) for v in p['error_charges_L1'].values())
                self.assertEqual(F(*p['composed_path_field_error_L1']),charge)
                self.assertEqual(F(*p['retained_scene_unit_error_L1']),F(*up['composed_unit_error_L1_upper']))
                self.assertEqual(F(*p['field_absolute_L1_budget']),F(1,10**12))
                self.assertEqual(p['accepted_source_product_absolute_CPU_only'],charge<=F(1,10**12))
                self.assertGreater(F(*p['source_encoding_error_L1']),0)

    def test_zero_cap_rejects_even_cached_exact_quarter(self):
        with patch.object(new,'product_words',side_effect=AssertionError('pure identical cache must not execute')):
            c=new.compose(self.units['positive'],self.geometry['positive'],{'s':0},self.bank,self.pins[new.CODE])
        self.assertFalse(c['accepted_source_product_absolute_CPU_only'])
        self.assertGreater(F(*c['paths'][0]['composed_path_field_error_L1']),0)
        self.evidence['zero_cap_control']=c

    def test_binding_order_gauge_and_mirror_fail_closed(self):
        for mutation in ('source','gauge','mirror','order'):
            u=deepcopy(self.units['two_sources']);g=deepcopy(self.geometry['two_sources'])
            if mutation=='source':g['scene_snapshot']['sources'][0]['field_reim'][0]=.2
            if mutation=='gauge':u['paths'][0]['phase_reference_id']='wrong'
            if mutation=='mirror':g['scene_snapshot']['objects']['M']['phase_rad']=.1
            if mutation=='order':u['paths'].reverse()
            with self.assertRaises(ValueError):new.compose(u,g,self.caps['two_sources'],self.bank,self.pins[new.CODE])

    def test_explicit_caps_model_selection_SHA(self):
        for value in (True,.00001,-1,[1,0],[],None):
            with self.assertRaises(ValueError):new.cap(value)
        for names in ([],['positive','positive'],['unknown'],[True]):
            with self.assertRaises(ValueError):new.audit_scene_source_products(case_names=names,field_caps={},product_model=new.MODEL)
        for budget in ({},{'s':0,'extra':0}):
            with self.assertRaises(ValueError):new.compose(self.units['positive'],self.geometry['positive'],budget,self.bank,self.pins[new.CODE])
        with self.assertRaises(ValueError):new.audit_scene_source_products(case_names=['positive'],field_caps={},product_model='GPU')
        with patch.object(new,'SHA','0'*64):
            with self.assertRaisesRegex(ValueError,'SHA'):new.load_retained()

    def test_no_hardware_reduction_full_pipeline(self):
        for flag in ('GPU_executed','ALU_executed','native_source_product_implemented','execution_authenticated','accepted_full_field_pipeline','scene_field_reduced','detector_evaluated','coherent_group_budget_certified','native_promotion_allowed','geometry_quotient_unit_or_producer_rerun'):
            self.assertFalse(self.audit[flag])
        self.assertEqual(len(self.pins),102)

if __name__=='__main__':
    r=unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(SourceTests))
    if hasattr(SourceTests,'evidence'):print(json.dumps(SourceTests.evidence,sort_keys=True,allow_nan=False))
    sys.exit(0 if r.wasSuccessful() else 1)
