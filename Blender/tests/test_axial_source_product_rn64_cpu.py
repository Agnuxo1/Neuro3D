"""Bounded new product model only; old scene/rotations are not replayed."""
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
import json
import sys
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'Blender/benchmarks/capacity_audit'))
from axial_source_product_rn64_cpu_v1 import MODEL,product_words,load_retained,_case,audit_retained_source_products
from axial_hilo_terminal_cpu_v1 import round32_exact
from axial_hilo_ops_cpu_v1 import component
from axial_unit_rn64_cpu_v1 import round64,component64


class SourceProductTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report,cls.units,cls.sources=load_retained();cls.evidence={'primitives':{},'rejections':{}}

    def test_retained_products_no_old_replay(self):
        with patch('axial_unit_rn64_cpu_v1.rotation64',side_effect=AssertionError('no unit replay')),patch('axial_quarter_source_ops_cpu_v1.produce_quarter_source_operations',side_effect=AssertionError('no scene replay')),patch('scene_field_producer_cpu_v1.rotation',side_effect=AssertionError('no producer')):
            a=audit_retained_source_products(case_names=list(self.units),product_model=MODEL)
        self.evidence['audit']=a
        for name,c in a['cases'].items():
            self.assertEqual(c['previous_full_case_accepted'],self.units[name]['previous_full_case_accepted'])
            self.assertFalse(c['accepted_full_field_pipeline']);self.assertFalse(c['scene_field_reduced']);self.assertFalse(c['detector_evaluated'])
            self.assertFalse(c['coherent_group_budget_certified'])

    def test_nonquarter_nearquarter_terminals_partial_only(self):
        for name in ['nonquarter_FAIL','near_quarter_FAIL']:
            c=_case(self.units[name],self.sources[name])
            self.assertTrue(c['path_field_values_computed'])
            self.assertTrue(c['accepted_source_product_absolute_CPU_only'])
            self.assertFalse(c['previous_full_case_accepted'])
            p=c['paths'][0]
            self.assertEqual(p['field_absolute_L1_budget_rational'],[1,10000])
            self.assertNotEqual(F(*p['measurement']['observed_path_field_rational'][1]),0)
            self.assertGreater(F(*p['error_charges_L1_rational']['unit_phase_numeric']),0)

    def test_exact_quarter_reflection_and_sourceABI(self):
        for i in range(4):
            c=_case(self.units['quarter'+str(i)],self.sources['quarter'+str(i)]);p=c['paths'][0];m=p['measurement']
            self.assertEqual(m['source_limb_uint32'],[w for comp in self.sources['quarter'+str(i)]['transport']['source_transport']['sources'][0]['components'] for w in comp['limb_uint32']])
            ar,ai=[F(*v) for v in m['decoded_source_rational']]
            expected=[-ar,-ai] if i==0 else ([ai,-ar] if i==1 else ([ar,ai] if i==2 else [-ai,ar]))
            self.assertEqual([F(*v) for v in m['observed_path_field_rational']],expected)
            self.assertEqual(F(*m['product_error_L1_upper_rational']),0)

    def test_dark_sources_separate_no_cancel_credit(self):
        c=_case(self.units['dark'],self.sources['dark'])
        self.assertEqual(len(c['paths']),2)
        self.assertTrue(all(F(*p['composed_path_field_error_L1_upper_rational'])>0 for p in c['paths']))
        self.assertEqual([p['source_id'] for p in c['paths']],[p['source_id'] for p in self.units['dark']['paths']])
        self.assertFalse(c['scene_field_reduced'])

    def test_nodes_and_nonexact_product_charges(self):
        words=[round32_exact(F(v))[0] for v in [F(1,10),F(1,2**28),F(3,10),F(-1,2**28)]]
        unit=[round64(F(v))[0] for v in [F(1,3),F(2,3)]]
        m=product_words(words,unit,product_model=MODEL);self.evidence['primitives']['nonexact']=m
        self.assertEqual(len(m['operations']),8)
        for n in m['operations']:
            a,b=[F(*v) for v in n['inputs_rational']]
            exact=a+b if n['op']=='add' else (a-b if n['op']=='sub' else a*b)
            self.assertEqual(n['output_uint64'],round64(exact)[0])
            self.assertEqual(F(*n['rounding_delta_rational']),component64(n['output_uint64'])-exact)
        self.assertGreater(F(*m['product_error_L1_upper_rational']),0)
        self.assertLessEqual(F(*m['actual_product_error_L1_rational']),F(*m['product_error_L1_upper_rational']))

    def test_profile_and_upstream_rejections(self):
        for name in ['mirror_phase_FAIL','mirror_phase_underflow_FAIL','mode_FAIL','source0_FAIL','underflow_FAIL','high_intensity_FAIL']:
            c=_case(self.units[name],self.sources[name]);self.assertFalse(c['path_field_values_computed']);self.assertEqual(c['RN64_operations'],0)
        unit=deepcopy(self.units['nonquarter_FAIL']);src=deepcopy(self.sources['nonquarter_FAIL'])
        src['transport']['field_absolute_L1_budget']=[0,1]
        c=_case(unit,src);self.assertTrue(c['path_field_values_computed']);self.assertFalse(c['accepted_source_product_absolute_CPU_only'])
        self.evidence['rejections']['profile_upstream_budget']='mirror phase nonzero or originalunderflow/source/geometry reject without product; zero fieldbudget rejects composed new bound, no tolerance relax'

    def test_reference_coverage_binding_and_primitive_domains(self):
        unit=deepcopy(self.units['quarter0']);unit['decoded_scene_binding_sha256']='bad'
        with self.assertRaises(ValueError):_case(unit,self.sources['quarter0'])
        src=deepcopy(self.sources['quarter0']);src['transport']['source_transport']['sources'][0]['source_phase_reference_id']='bad'
        with self.assertRaises(ValueError):_case(self.units['quarter0'],src)
        src=deepcopy(self.sources['quarter0']);src['transport']['contributions'][0]['coherence_group']='bad'
        with self.assertRaises(ValueError):_case(self.units['quarter0'],src)
        unit=deepcopy(self.units['quarter0']);unit['paths'].append(deepcopy(unit['paths'][0]))
        with self.assertRaises(ValueError):_case(unit,self.sources['quarter0'])
        for words,u in [([True,0,0,0],[round64(1)[0],0]),([1,0,0,0],[round64(1)[0],0]),([0,0,0],[0,0]),([round32_exact(F(1,2**100))[0],0,0,0],[round64(F(1,2**950))[0],0])]:
            with self.assertRaises(ValueError):product_words(words,u,product_model=MODEL)
        self.evidence['rejections']['failclosed']='gauge/binding/portgroup/coverage/bool/source-subnormal/selectedRN64subnormal reject'

    def test_optin_selection_SHA(self):
        for names in [[],['quarter0','quarter0'],[['bad']],['missing']]:
            with self.assertRaises(ValueError):audit_retained_source_products(case_names=names,product_model=MODEL)
        with self.assertRaises(ValueError):audit_retained_source_products(case_names=['quarter0'],product_model='GPU')
        with patch('axial_source_product_rn64_cpu_v1.SHA','0'*64):
            with self.assertRaisesRegex(ValueError,'SHA'):load_retained()


if __name__=='__main__':
    r=unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(SourceProductTests))
    if hasattr(SourceProductTests,'evidence'):print(json.dumps(SourceProductTests.evidence,sort_keys=True,allow_nan=False))
    sys.exit(0 if r.wasSuccessful() else 1)
