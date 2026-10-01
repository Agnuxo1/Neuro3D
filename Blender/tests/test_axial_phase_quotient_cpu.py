"""Phase-argument checks only: never replay old geometry or field producers."""
from copy import deepcopy
from fractions import Fraction as F
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'Blender/tests'));sys.path.insert(0,str(ROOT/'Blender/benchmarks/capacity_audit'))
from axial_phase_quotient_cpu_v1 import MODEL,quotient_words,centered_selector,load_retained,_case,audit_retained_phase_arguments
from axial_hilo_terminal_cpu_v1 import round32_exact
from axial_hilo_ops_cpu_v1 import component


def word(v):return round32_exact(F(v))[0]


class PhaseQuotientTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.previous,cls.old=load_retained();cls.evidence={'primitives':{},'rejections':{}}

    def test_retained_arguments_without_replaying_scene_or_fields(self):
        with patch('axial_quarter_source_ops_cpu_v1.produce_quarter_source_operations',side_effect=AssertionError('no producer replay')):
            a=audit_retained_phase_arguments(case_names=list(self.old),phase_model=MODEL)
        self.evidence['audit']=a
        for name,c in a['cases'].items():
            self.assertEqual(c['previous_full_case_accepted'],self.old[name]['accepted_original_ideal_scene_CPU_only'])
            self.assertFalse(c['accepted_full_field_pipeline']);self.assertFalse(c['field_values_computed'])
        self.assertTrue(a['cases']['near_quarter_FAIL']['accepted_phase_argument_CPU_only'])
        self.assertFalse(a['cases']['near_quarter_FAIL']['previous_full_case_accepted'])
        self.assertFalse(a['cases']['mode_FAIL']['accepted_phase_argument_CPU_only'])

    def test_each_node_and_graph_error_identity(self):
        m=quotient_words([word(.1),word(F(1,2**30))],word(.3),phase_model=MODEL)
        self.evidence['primitives']['nonexact_product']=m
        self.assertEqual(len(m['operations']),5)
        self.assertNotEqual(F(*m['operations'][1]['rounding_delta_rational']),0)
        for node in m['operations']:
            a,b=[F(*v) for v in node['inputs_rational']]
            exact={'div':lambda:a/b,'mul':lambda:a*b,'sub':lambda:a-b,'add':lambda:a+b}[node['op']]()
            self.assertEqual(node['output_uint32'],round32_exact(exact)[0])
            self.assertEqual(F(*node['rounding_delta_rational']),component(node['output_uint32'])-exact)
        self.assertLessEqual(F(*m['actual_quotient_error_rational']),F(*m['quotient_error_upper_rational']))

    def test_low_phase_survives_simple_binary32_cast_loss(self):
        m=_case(self.old['near_quarter_FAIL'])['paths'][0]['measurement']
        observed=F(*m['modeled_quotient_rational']);plain=component(m['quotient_limb_uint32'][0])
        self.assertEqual(plain,F(5));self.assertEqual(observed,F(5)+F(1,2**27))
        self.assertEqual(F(*m['actual_quotient_error_rational']),0)
        large=quotient_words([word(2**24),word(F(1,8))],word(1),phase_model=MODEL)
        self.assertEqual(F(*large['modeled_quotient_rational']),F(2**24)+F(1,8))
        self.evidence['primitives']['large_cycles_residual']=large

    def test_centered_turn_branch_crossing_and_exact_tie(self):
        for lo,hi,observed in [(F(1,2)-F(1,2**30),F(1,2),F(1,2)),(F(1,2),F(1,2)+F(1,2**30),F(1,2)-F(1,2**30))]:
            self.assertFalse(centered_selector(lo,hi,observed)['accepted_CPU_selector_only'])
        r=centered_selector(F(1,2),F(1,2),F(1,2));self.assertTrue(r['accepted_CPU_selector_only'])
        self.assertEqual(r['CPU_integer_turn'],1);self.assertEqual(F(*r['centered_observed_cycles_rational']),-F(1,2))
        with self.assertRaises(ValueError):centered_selector(F(1),F(0),F(0))
        self.evidence['rejections']['selector_crossing']='interval or observed phase on another centered branch rejected, exact singleton tie validCPU only'

    def test_selected_subnormal_overflow_and_invalid_input_words(self):
        for pair,w in [([word(F(1,2**126)),0],word(2)),([0x7f7fffff,0],word(F(1,2))),([1,0],word(1)),([True,0],word(1)),([word(1),0],0),([word(-1),0],word(1))]:
            with self.assertRaises(ValueError):quotient_words(pair,w,phase_model=MODEL)
        self.evidence['rejections']['subnormal_overflow_invalid']='normal2^-126/2 selects subnormal; overflow/bool/input subnormal/zero wavelength/negative length reject, no FTZ'

    def test_mirror_phase_not_silently_evaluated_or_fullcase_promoted(self):
        for name in ['mirror_phase_FAIL','mirror_phase_underflow_FAIL','nonquarter_FAIL']:
            r=_case(self.old[name]);self.assertFalse(r['previous_full_case_accepted'])
            self.assertFalse(r['mirror_phase_evaluated']);self.assertFalse(r['accepted_full_field_pipeline'])
        r=_case(self.old['mirror_phase_underflow_FAIL'])['paths'][0]
        self.assertEqual(F(*r['mirror_transport_phase_bound_rad']),F(1,2**150))
        self.evidence['rejections']['no_mirror_or_full_field_claim']='geometric partial argument does not remove prior quarter/profile FAIL or infer absolute mirror phase'

    def test_original_budgets_sources_gauge_and_interval_binding(self):
        c=deepcopy(self.old['nonquarter_FAIL']);c['transport']['path_certificate']['path_certificates'][0]['phase_budget_rad']=[0,1]
        self.assertFalse(_case(c)['accepted_phase_argument_CPU_only'])
        c=deepcopy(self.old['quarter0']);c['transport']['path_certificate']['path_certificates'][0]['wavelength_interval_BU'][1]=[1,4]
        self.assertFalse(_case(c)['accepted_phase_argument_CPU_only'])
        c=deepcopy(self.old['quarter0']);c['transport']['path_certificate']['path_certificates'][0]['phase_reference_id']='bad'
        self.assertFalse(_case(c)['accepted_phase_argument_CPU_only'])
        c=deepcopy(self.old['dark']);c['transport']['path_certificate']['path_certificates'].reverse()
        with self.assertRaises(ValueError):_case(c)
        c=deepcopy(self.old['quarter0']);c['transport']['path_certificate']['decoded_scene_binding_sha256']='bad'
        with self.assertRaises(ValueError):_case(c)
        self.evidence['rejections']['budget_bindings']='zero budget/non-singleton wavelength/gauge/order/scene binding reject on copies, no frozen mutation'

    def test_explicit_optin_SHA_and_selection(self):
        for names in [[],['quarter0','quarter0'],[['bad']],['missing']]:
            with self.assertRaises(ValueError):audit_retained_phase_arguments(case_names=names,phase_model=MODEL)
        with self.assertRaises(ValueError):audit_retained_phase_arguments(case_names=['quarter0'],phase_model='native')
        with patch('axial_phase_quotient_cpu_v1.SHA','0'*64):
            with self.assertRaisesRegex(ValueError,'SHA'):load_retained()
        self.evidence['rejections']['SHA_optin_selection']='local wrongSHA/optin/selection rejected'


if __name__=='__main__':
    result=unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(PhaseQuotientTests))
    if hasattr(PhaseQuotientTests,'evidence'):print(json.dumps(PhaseQuotientTests.evidence,sort_keys=True,allow_nan=False))
    sys.exit(0 if result.wasSuccessful() else 1)
