"""Word ABI selector CPU tests with independent rational branch oracle."""
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
from axial_selector_int256_cpu_v1 import MODEL,S,MIN,MAX,pack,unpack,decode32_scaled,select_words,host_radius,load_retained,audit_retained_selectors


def word(q):return struct.unpack('<I',struct.pack('<f',float(q)))[0]


class SelectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.evidence={'primitives':{},'independent_oracle_checks':0};cls.r,cls.cases,cls.units=load_retained()
    def primitive(self,name,q,r=0,low=F(0)):
        s=select_words([word(q),word(low)],pack(r),selector_model=MODEL);self.evidence['primitives'][name]=s;return s

    def test_retained_no_producer_or_rational_selector_replay(self):
        with patch('axial_phase_quotient_cpu_v1.centered_selector',side_effect=AssertionError('no old selector')),patch('axial_phase_quotient_cpu_v1.quotient_words',side_effect=AssertionError('no quotient replay')),patch('scene_field_producer_cpu_v1.rotation',side_effect=AssertionError('no producer')):
            a=audit_retained_selectors(case_names=list(self.cases),selector_model=MODEL)
        self.evidence['audit']=a
        for n,c in a['cases'].items():
            self.assertEqual(c['previous_full_case_accepted'],self.cases[n]['previous_full_case_accepted']);self.assertFalse(c['accepted_full_field_pipeline'])
            self.assertEqual(c['accepted_integer_selector_CPU_only'],n!='mode_FAIL')

    def test_tie_right_branch_and_uncertain_turn_quarter(self):
        for q,n,k in [(F(1,2),1,-2),(F(-1,2),0,-2),(F(1,8),0,1),(F(-1,8),0,0)]:
            s=self.primitive('tie_'+str(q),q);self.assertTrue(s['accepted_CPU_integer_selector_only']);self.assertEqual((s['integer_turn'],s['quarter_index']),(n,k))
            t=self.primitive('cross_'+str(q),q,1);self.assertFalse(t['accepted_CPU_integer_selector_only'])

    def test_low_limb_not_dropped(self):
        for sign in [-1,1]:
            s=self.primitive('half_low_'+str(sign),F(1,2),0,F(sign,2**40));self.assertTrue(s['accepted_CPU_integer_selector_only'])
            self.assertEqual(s['integer_turn'],1 if sign>0 else 0)
            self.assertEqual(F(unpack(s['residual_cycles_signed256_words']),S),F(sign,2**40))

    def test_outward_radius_and_conservative_new_rejection(self):
        a=host_radius(F(-1,3*S),F(1,3*S),0);self.assertEqual(unpack(a['radius_signed256_words']),1)
        self.assertEqual(F(*a['outward_inflation_cycles_rational']),F(2,3*S));self.evidence['outward_adapter']=a
        # Old asymmetric [boundary, boundary+small] fits right branch; new symmetric ABI crosses and rejects.
        q=F(1,8);a=host_radius(q,q+F(1,S),q);s=select_words([word(q),0],a['radius_signed256_words'],selector_model=MODEL)
        self.assertFalse(s['accepted_CPU_integer_selector_only']);self.evidence['primitives']['asymmetric_symmetrized_reject']=s
        with self.assertRaises(ValueError):host_radius(1,0,0)

    def test_pack_decode_domain_and_overflow(self):
        for n in [MIN,-1,0,1,MAX]:self.assertEqual(unpack(pack(n)),n)
        self.assertEqual(decode32_scaled(0x00800000),1<<23)
        self.assertEqual(decode32_scaled(0x80000000),0)
        for w in [True,-1,1<<32,1,0x7f800000,0x7fc00000,word(2**106)]:
            with self.assertRaises(ValueError):decode32_scaled(w)
        self.assertEqual(decode32_scaled(word(-2**106)),MIN)
        s=select_words([word(-2**106),0],pack(0),selector_model=MODEL);self.assertTrue(s['accepted_CPU_integer_selector_only']);self.evidence['primitives']['domain_min']=s
        with self.assertRaises(ValueError):select_words([word(-2**106),0],pack(1),selector_model=MODEL)
        with self.assertRaises(ValueError):select_words([word(1),0],pack(MAX),selector_model=MODEL)
        with self.assertRaises(ValueError):select_words([0,0],pack(-1),selector_model=MODEL)

    def test_independent_rational_oracle_and_integer_trace(self):
        rng=random.Random(1190315)
        for _ in range(96):
            a=F(rng.randint(-2000000,2000000),2**20);b=F(rng.randint(-1000,1000),2**40);r=rng.randrange(0,4)
            s=select_words([word(a),word(b)],pack(r),selector_model=MODEL);x=a+b;ends=[x-F(r,S),x,x+F(r,S)]
            ns=[(v+F(1,2))//1 for v in ends];ks=[(4*(v-ns[1])+F(1,2))//1 for v in ends]
            accepted=len(set(ns))==1 and len(set(ks))==1;self.assertEqual(s['accepted_CPU_integer_selector_only'],accepted)
            if accepted:
                self.assertEqual(s['integer_turn'],ns[1]);self.assertEqual(s['quarter_index'],ks[1]);self.assertEqual(F(unpack(s['residual_cycles_signed256_words']),S),x-ns[1]-F(ks[1],4))
            for node in s['operations']:
                x,y=map(unpack,node['inputs_signed256_words']);op=node['op'];expected=x+y if op=='add' else x-y if op=='sub' else x>>y if op=='shr' else x<<y
                self.assertEqual(unpack(node['output_signed256_words']),expected);self.assertLessEqual(expected,MAX);self.assertGreaterEqual(expected,MIN)
            self.evidence['independent_oracle_checks']+=1

    def test_ABI_optin_and_selection(self):
        for words in [[0],[True]+[0]*7,[0]*9]:
            with self.assertRaises(ValueError):unpack(words)
        with self.assertRaises(ValueError):select_words([0],pack(0),selector_model=MODEL)
        with self.assertRaises(ValueError):select_words([0,0],pack(0),selector_model='GPU')
        for names in [[],['dark','dark'],[['x']],['missing']]:
            with self.assertRaises(ValueError):audit_retained_selectors(case_names=names,selector_model=MODEL)
        with patch('axial_selector_int256_cpu_v1.SHA','0'*64):
            with self.assertRaisesRegex(ValueError,'SHA'):load_retained()

    def test_fail_flags_and_cost_scope(self):
        a=audit_retained_selectors(case_names=['nonquarter_FAIL','mode_FAIL','mirror_phase_FAIL'],selector_model=MODEL)
        self.assertFalse(a['native_selector_implemented']);self.assertFalse(a['geometry_ABI_implemented']);self.assertFalse(a['scene_or_producer_rerun'])
        self.assertFalse(a['cases']['nonquarter_FAIL']['previous_full_case_accepted'])
        self.assertFalse(a['cases']['nonquarter_FAIL']['paths'][0]['previous_unit_accepted'])
        self.assertFalse(a['cases']['mode_FAIL']['paths'][0]['integer_selector_evaluated'])
        self.assertIn('no native/hardware/full costs',a['cost_scope'])


if __name__=='__main__':
    r=unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(SelectorTests))
    if hasattr(SelectorTests,'evidence'):print(json.dumps(SelectorTests.evidence,sort_keys=True,allow_nan=False))
    sys.exit(0 if r.wasSuccessful() else 1)
