"""Tests only new synthetic RN64 unit; frozen RN32/scene producer not replayed."""
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
import json
import math
import struct
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'Blender/benchmarks/capacity_audit'))
from axial_unit_rn64_cpu_v1 import MODEL,round64,component64,rotation64,permute64,load_retained,_case,audit_retained_rn64
from scene_field_producer_cpu_v1 import PI_LOWER,PI_UPPER


def word(q):return round64(q)[0]


class RN64UnitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report,cls.old,cls.phase=load_retained();cls.evidence={'primitives':{},'rejections':{}}

    def test_rounding_exact_ties_sign_carry(self):
        for q in [F(0),F(1),F(-1),F(1)+F(1,2**53),F(1)+F(3,2**53),F(2)-F(1,2**53),F(1,2**1022)]:
            w,v=round64(q)
            self.assertEqual(w,struct.unpack('<Q',struct.pack('<d',float(q)))[0])
            self.assertEqual(v,component64(w))
        self.assertEqual(round64(F(1,2**1075))[1],0)
        with self.assertRaises(ValueError):round64(F(3,2**1075))
        with self.assertRaises(ValueError):round64(F(2**1024))
        tiny=rotation64(word(F(1,2**600)),rotation_model=MODEL)
        self.assertEqual(tiny['operations'][0]['output_uint64'],0)
        self.assertEqual(F(*tiny['operations'][0]['rounding_delta_rational']),-F(1,2**1200))
        self.assertGreater(F(*tiny['unit_error_L1_upper_rational']),0)
        self.evidence['primitives']['square_rounds_zero_charged']=tiny

    def test_retained_new_precision_no_old_replay(self):
        with patch('axial_unit_rotation_cpu_v1.rotation_word',side_effect=AssertionError('no RN32 replay')),patch('axial_phase_quotient_cpu_v1.quotient_words',side_effect=AssertionError('no quotient replay')),patch('scene_field_producer_cpu_v1.rotation',side_effect=AssertionError('no producer replay')):
            a=audit_retained_rn64(case_names=list(self.old),rotation_model=MODEL)
        self.evidence['audit']=a
        for name,c in a['cases'].items():
            self.assertEqual(c['previous_full_case_accepted'],self.old[name]['previous_full_case_accepted'])
            self.assertFalse(c['accepted_full_field_pipeline']);self.assertFalse(c['field_values_computed'])

    def test_nonquarter_new_partial_certification_old_FAIL_intact(self):
        c=_case(self.old['nonquarter_FAIL'],self.phase['nonquarter_FAIL']);p=c['paths'][0]
        self.assertFalse(c['previous_RN32_unit_accepted']);self.assertTrue(c['accepted_propagation_unit_CPU_only'])
        self.assertFalse(c['previous_full_case_accepted'])
        self.assertEqual(p['phase_budget_rad'],[1,10**12])
        self.assertLessEqual(F(*p['composed_unit_error_L1_upper_rational']),F(*p['derived_unit_L1_budget_rational']))
        self.evidence['rejections']['old_nonquarter_FAIL']='frozen RN32 gate and previous fullcase FAIL retained; new RN64 unit-only gate uses SAME1e-12rad budget'

    def test_quarters_and_nearquarter(self):
        for i,expected in enumerate([(1,0),(0,1),(-1,0),(0,-1)]):
            c=_case(self.old['quarter'+str(i)],self.phase['quarter'+str(i)]);p=c['paths'][0]
            self.assertEqual([F(*v) for v in p['observed_unit_rational']],list(expected))
            self.assertEqual(F(*p['composed_unit_error_L1_upper_rational']),0)
        c=_case(self.old['near_quarter_FAIL'],self.phase['near_quarter_FAIL']);p=c['paths'][0]
        self.assertGreater(F(*p['observed_unit_rational'][1]),0)
        self.assertTrue(c['accepted_propagation_unit_CPU_only']);self.assertFalse(c['previous_full_case_accepted'])

    def test_primitives_nodes_and_distinct_charges(self):
        for name,x in [('positive',F(1,2)),('negative',F(-1,2)),('separate_charges',F(1,10))]:
            r=rotation64(word(x),rotation_model=MODEL);self.evidence['primitives'][name]=r
            self.assertEqual(len(r['operations']),26)
            for node in r['operations']:
                a,b=map(lambda v:F(*v),node['inputs_rational']);exact=a*b if node['op']=='mul' else a+b
                self.assertEqual(node['output_uint64'],round64(exact)[0])
                self.assertEqual(F(*node['rounding_delta_rational']),component64(node['output_uint64'])-exact)
            for t in r['terms'].values():
                b=sum((F(*v) for v in t['error_charges_rational'].values()),F(0))
                self.assertEqual(b,F(*t['polynomial_error_upper_rational']))
                self.assertLessEqual(F(*t['actual_polynomial_error_rational']),b)
                if name=='separate_charges':
                    self.assertTrue(all(F(*v)>0 for v in t['error_charges_rational'].values()))

    def test_original_length_unit_oracle(self):
        # Independent Taylor40 at ORIGINAL length from SHA-pinned quotient metadata.
        for name in ['nonquarter_FAIL','near_quarter_FAIL']:
            c=_case(self.old[name],self.phase[name]);p=c['paths'][0];original=self.phase[name]['paths'][0]
            self.assertEqual(p['phase_reference_id'],original['phase_reference_id'])
            original_cycles=F(*original['original_length_BU'])/F(*original['wavelength_BU_rational'])
            u=original_cycles-original['selector']['CPU_integer_turn']-F(p['quarter_CPU_index'],4)
            x=(PI_LOWER+PI_UPPER)*u
            cos=sum((F((-1)**j)*x**(2*j)/math.factorial(2*j) for j in range(21)),F(0))
            sin=sum((F((-1)**j)*x**(2*j+1)/math.factorial(2*j+1) for j in range(20)),F(0))
            k=p['quarter_CPU_index']%4
            oracle=[cos,sin] if k==0 else ([-sin,cos] if k==1 else ([-cos,-sin] if k==2 else [sin,-cos]))
            observed=[F(*v) for v in p['observed_unit_rational']]
            error=sum((abs(a-b) for a,b in zip(observed,oracle)),F(0))
            tail=abs(x)**41/math.factorial(41)+abs(x)**42/math.factorial(42)+2*abs(u)*(PI_UPPER-PI_LOWER)
            self.assertLessEqual(error+tail,F(*p['composed_unit_error_L1_upper_rational']))

    def test_failclosed_budget_gauge_branch_coverage_domain(self):
        for w in [True,1,0x7ff0000000000000,word(2),word(F(1,2**530))]:
            with self.assertRaises(ValueError):rotation64(w,rotation_model=MODEL)
        old=deepcopy(self.old['nonquarter_FAIL']);ph=deepcopy(self.phase['nonquarter_FAIL'])
        old['paths'][0]['phase_budget_rad']=[0,1];ph['paths'][0]['phase_budget_rad']=[0,1]
        self.assertFalse(_case(old,ph)['accepted_propagation_unit_CPU_only'])
        old=deepcopy(self.old['quarter0']);old['paths'][0]['phase_reference_id']='bad'
        self.assertFalse(_case(old,self.phase['quarter0'])['accepted_propagation_unit_CPU_only'])
        ph=deepcopy(self.phase['quarter0']);ph['paths'][0]['selector']['centered_enclosure_cycles_rational']=[[0,1],[1,8]]
        self.assertFalse(_case(self.old['quarter0'],ph)['accepted_propagation_unit_CPU_only'])
        old=deepcopy(self.old['quarter0']);old['paths'].append(deepcopy(old['paths'][0]))
        with self.assertRaises(ValueError):_case(old,self.phase['quarter0'])
        old=deepcopy(self.old['quarter0']);old['decoded_scene_binding_sha256']='bad'
        with self.assertRaises(ValueError):_case(old,self.phase['quarter0'])
        with self.assertRaises(ValueError):permute64([word(1)],0)
        self.evidence['rejections']['failclosed']='normal-or-zero/subnormal intermediate/domain/gauge/branch/budget/coverage rejects on copies'

    def test_optin_selection_SHA(self):
        for names in [[],['quarter0','quarter0'],[['bad']],['missing']]:
            with self.assertRaises(ValueError):audit_retained_rn64(case_names=names,rotation_model=MODEL)
        with self.assertRaises(ValueError):audit_retained_rn64(case_names=['quarter0'],rotation_model='GPU64')
        with patch('axial_unit_rn64_cpu_v1.SHA','0'*64):
            with self.assertRaisesRegex(ValueError,'SHA'):load_retained()


if __name__=='__main__':
    result=unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(RN64UnitTests))
    if hasattr(RN64UnitTests,'evidence'):print(json.dumps(RN64UnitTests.evidence,sort_keys=True,allow_nan=False))
    sys.exit(0 if result.wasSuccessful() else 1)
