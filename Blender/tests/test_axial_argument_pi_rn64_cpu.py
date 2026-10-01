"""Explicit argument ABI conversion and synthetic RN64 product contract."""
from copy import deepcopy
from fractions import Fraction as F
import json
from pathlib import Path
import random
import struct
import sys
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'Blender/benchmarks/capacity_audit'))
from axial_argument_pi_rn64_cpu_v1 import MODEL,TWO_PI,convert_residual,argument_words,load_retained,_case,audit_retained_arguments
from axial_selector_int256_cpu_v1 import pack
from axial_unit_rn64_cpu_v1 import component64
from scene_field_producer_cpu_v1 import PI_LOWER,PI_UPPER


def word(q):return struct.unpack('<Q',struct.pack('<d',float(q)))[0]


class ArgumentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r,cls.old,cls.phase=load_retained();cls.evidence={'primitives':{},'conversion_oracle_checks':0}
    def primitive(self,name,n):
        m=argument_words(pack(n),argument_model=MODEL);self.evidence['primitives'][name]=m;return m

    def test_retained_without_selector_rotation_or_producer_replay(self):
        with patch('axial_selector_int256_cpu_v1.select_words',side_effect=AssertionError('no selector replay')),patch('axial_unit_rn64_cpu_v1.rotation64',side_effect=AssertionError('no rotation')),patch('scene_field_producer_cpu_v1.rotation',side_effect=AssertionError('no producer')):
            a=audit_retained_arguments(case_names=list(self.old),argument_model=MODEL)
        self.evidence['audit']=a;self.assertEqual(a['RN64_operations'],21)
        for n,c in a['cases'].items():
            self.assertEqual(c['previous_full_case_accepted'],self.old[n]['previous_full_case_accepted'])
            self.assertEqual(c['accepted_argument_CPU_only'],n!='mode_FAIL');self.assertFalse(c['accepted_full_field_pipeline'])
            self.assertFalse(c['field_values_computed'])

    def test_zero_minimum_signed_and_domain_endpoints(self):
        for n in [0,1,-1,1<<146,-(1<<146)]:
            m=self.primitive('domain_'+str(n),n);self.assertEqual(component64(m['conversion']['output_uint64']),F(n,1<<149))
            self.assertLessEqual(abs(F(*m['observed_argument_rad_rational'])),1)
        self.assertEqual(self.evidence['primitives']['domain_0']['angle_error_upper_rad_rational'],[0,1])
        self.assertNotEqual(self.evidence['primitives']['domain_1']['argument_uint64'],0)
        with self.assertRaises(ValueError):argument_words(pack((1<<146)+1),argument_model=MODEL)

    def test_ties_even_up_down_and_carry_explicit(self):
        even=(1<<100)+(1<<47);odd=even+(1<<48);carry=(1<<100)-(1<<46)
        for name,n in [('even_tie_down',even),('odd_tie_up',odd),('carry_tie_up',carry),('negative_odd_tie_up',-odd)]:
            m=self.primitive(name,n);c=m['conversion'];self.assertTrue(c['tie']);self.assertEqual(c['rounded_up'],name!='even_tie_down')
            self.assertEqual(c['output_uint64'],word(F(n,1<<149)))
            self.assertGreater(F(*m['residual_conversion_error_cycles_rational']),0)

    def test_constant_and_operation_charges_not_free(self):
        m=self.primitive('nonexact_product',(1<<145)+123456789)
        self.assertEqual(m['TWO_PI_uint64'],TWO_PI);p=component64(TWO_PI)
        midpoint=PI_LOWER+PI_UPPER;self.assertEqual(word(midpoint),TWO_PI)
        constant=max(abs(p-2*PI_LOWER),abs(p-2*PI_UPPER));self.assertGreater(constant,0)
        charges={k:F(*v) for k,v in m['angle_error_charges_rad_rational'].items()}
        x=F(*m['original_residual_rational']);rep=F(*m['represented_residual_rational']);y=F(*m['observed_argument_rad_rational'])
        self.assertEqual(charges['residual_conversion'],abs(p)*abs(rep-x));self.assertEqual(charges['constant_2pi'],abs(x)*constant)
        self.assertEqual(charges['multiply_RN64'],abs(y-rep*p));self.assertEqual(sum(charges.values()),F(*m['angle_error_upper_rad_rational']))
        self.assertLessEqual(max(abs(y-2*PI_LOWER*x),abs(y-2*PI_UPPER*x)),sum(charges.values()))

    def test_conversion_independent_oracle_no_fraction_in_core(self):
        rng=random.Random(315119)
        ns=[rng.getrandbits(146)*rng.choice([-1,1]) for _ in range(96)]
        for n in ns:
            with patch('axial_argument_pi_rn64_cpu_v1.F',side_effect=AssertionError('no Fraction bit conversion')):c=convert_residual(pack(n))
            self.assertEqual(c['output_uint64'],word(F(n,1<<149)));self.evidence['conversion_oracle_checks']+=1

    def test_original_budget_and_upstream_FAIL_preserved(self):
        c=_case(self.old['nonquarter_FAIL'],self.phase['nonquarter_FAIL']);p=c['paths'][0]
        self.assertTrue(c['accepted_argument_CPU_only']);self.assertFalse(c['previous_full_case_accepted']);self.assertFalse(p['previous_RN32_unit_accepted'])
        self.assertEqual(p['phase_budget_rad'],self.phase['nonquarter_FAIL']['paths'][0]['phase_budget_rad'])
        self.assertLessEqual(F(*p['composed_phase_bound_rad']),F(*p['phase_budget_rad']))
        phase=deepcopy(self.phase['nonquarter_FAIL']);phase['paths'][0]['phase_budget_rad']=[0,1]
        self.assertFalse(_case(self.old['nonquarter_FAIL'],phase)['accepted_argument_CPU_only'])
        c=_case(self.old['mode_FAIL'],self.phase['mode_FAIL']);self.assertFalse(c['paths'][0]['argument_evaluated']);self.assertEqual(c['RN64_operations'],0)

    def test_gauge_binding_coverage_ABI_failclosed(self):
        for kind in ['gauge','binding','coverage','residual']:
            c=deepcopy(self.old['quarter0'])
            if kind=='gauge':c['paths'][0]['phase_reference_id']='wrong'
            elif kind=='binding':c['original_scene_binding_sha256']='wrong'
            elif kind=='coverage':c['paths'].append(deepcopy(c['paths'][0]))
            else:c['paths'][0]['selector']['residual_cycles_signed256_words']=pack(1)
            with self.assertRaises(ValueError):_case(c,self.phase['quarter0'])
        for ws in [[0], [True]+[0]*7,[-1]+[0]*7]:
            with self.assertRaises(ValueError):convert_residual(ws)

    def test_optin_SHA_selection_and_no_native(self):
        for ns in [[],['quarter0','quarter0'],[['x']],['missing']]:
            with self.assertRaises(ValueError):audit_retained_arguments(case_names=ns,argument_model=MODEL)
        with self.assertRaises(ValueError):argument_words(pack(0),argument_model='GPU')
        with patch('axial_argument_pi_rn64_cpu_v1.SHA','0'*64):
            with self.assertRaisesRegex(ValueError,'SHA'):load_retained()
        a=audit_retained_arguments(case_names=['quarter0'],argument_model=MODEL)
        self.assertFalse(a['native_argument_product_implemented']);self.assertFalse(a['native_selector_implemented']);self.assertFalse(a['old_selector_unit_quotient_or_producer_rerun'])


if __name__=='__main__':
    r=unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(ArgumentTests))
    if hasattr(ArgumentTests,'evidence'):print(json.dumps(ArgumentTests.evidence,sort_keys=True,allow_nan=False))
    sys.exit(0 if r.wasSuccessful() else 1)
