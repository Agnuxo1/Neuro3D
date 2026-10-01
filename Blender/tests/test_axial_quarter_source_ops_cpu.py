"""New source-word producer tests; no frozen producer/suite replay."""
from copy import deepcopy
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'Blender/tests'));sys.path.insert(0,str(ROOT/'Blender/benchmarks/capacity_audit'))
from test_axial_field_budget_cpu import fixture
from axial_quarter_source_ops_cpu_v1 import MODEL, produce_quarter_source_operations, permute_source_words
from axial_hilo_ops_cpu_v1 import component

PREVIOUS='coordinacion/respuestas/AXIAL-HILO-OPS-001-CODEX.json'
SHA='1963fa6f0ca0f1ce37ff383363aa574a9d308cf4312f689b07dc79caf8a3e624'


def run(s,**changes):
    opts={'phase_model':MODEL,'coherence_groups':{x['id']:'g' for x in s['sources']},
        'source_absolute_L1_budget':F(1,10000),'source_relative_L1_budget':F(1,10000),'phase_budget_rad':F(1,10**12),
        'field_budget':F(1,10000),'intensity_budget':F(1,5000),
        'field_relative_budget':F(1,10**6),'intensity_relative_budget':F(1,10**6)}
    opts.update(changes);return produce_quarter_source_operations(s,**opts)


def dark():
    s=fixture();other=deepcopy(s['sources'][0]);other['id']='other';other['position_BU'][0]=.125
    other['field_reim']=[-.1+2**-30,0.];s['sources'].append(other);return s


class QuarterSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw=(ROOT/PREVIOUS).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=SHA:raise ValueError('changed prior report')
        previous=json.loads(raw);cls.pins={**previous['code_doc_sha256'],PREVIOUS:SHA}
        for p,h in cls.pins.items():
            if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('changed frozen input '+p)
        cls.evidence={'pins_verified':cls.pins,'cases':{},'rejections':{},'old_producer_or_suites_rerun':False,'GPU_executed':False}

    def keep(self,n,r):self.evidence['cases'][n]=r;return r

    def oracle(self,r,ideal):
        g=r['reduction']['ports']['D']['groups']['g'];observed=[F(*v) for v in g['modeled_field_rational']]
        err=sum((abs(a-b) for a,b in zip(observed,ideal)),F(0))
        pe=abs(sum((a*a for a in observed),F(0))-sum((a*a for a in ideal),F(0)))
        self.assertLessEqual(err,F(*g['field_error_upper_rational']))
        self.assertLessEqual(pe,F(*r['reduction']['ports']['D']['power_error_upper_rational']))
        r['independent_exact_oracle']={'original_ideal_field_rational':[[a.numerator,a.denominator] for a in ideal],
            'actual_error_L1_rational':[err.numerator,err.denominator],'actual_power_error_rational':[pe.numerator,pe.denominator]}

    def test_all_quarters_from_actual_scene_both_components(self):
        re,im=F(.1),F(.075)
        for k,terminal,ideal in [(0,-.125,[-re,-im]),(1,-.15625,[im,-re]),
                (2,-.1875,[re,im]),(3,-.21875,[-im,re])]:
            s=fixture();s['sources'][0]['field_reim']=[.1,.075]
            s['objects']['D']['vertices_world_BU']=[[terminal,*v[1:]] for v in s['objects']['D']['vertices_world_BU']]
            s['objects']['D']['mode_origin_BU'][0]=terminal;before=deepcopy(s)
            r=self.keep('quarter'+str(k),run(s));self.oracle(r,ideal)
            self.assertTrue(r['accepted_original_ideal_scene_CPU_only']);self.assertEqual(s,before)
            self.assertEqual(r['rows'][0]['quarter_index'],k);self.assertEqual(r['work_counts']['RN32_reduction_ops'],64)

    def test_dark_original_scene_not_supplied_terminal(self):
        s=dark();r=self.keep('dark',run(s));self.oracle(r,[-F(1,2**30),F(0)])
        self.assertTrue(r['accepted_original_ideal_scene_CPU_only']);self.assertFalse(r['cached_or_supplied_terminal_fields'])
        old=json.loads((ROOT/'coordinacion/respuestas/AXIAL-HILO-TERMINAL-001-CODEX.json').read_bytes())['run']['observations']['cases']['dark_hilo_model']
        self.assertEqual(r['original_scene_binding_sha256'],old['original_scene_binding_sha256'])
        self.assertEqual(r['decoded_scene_binding_sha256'],old['decoded_scene_binding_sha256'])
        s['sources'].reverse();r=self.keep('dark_reversed',run(s));self.oracle(r,[-F(1,2**30),F(0)])
        self.assertTrue(r['accepted_original_ideal_scene_CPU_only'])

    def test_source_words_and_decode_charge_not_omitted(self):
        r=self.keep('source_decode',run(fixture()));row=r['rows'][0]
        sr=r['transport']['source_transport']['sources'][0]
        self.assertEqual(row['source_limb_uint32'],[w for c in sr['components'] for w in c['limb_uint32']])
        expected=sum((abs(F(*c['exact_limb_sum_rational'])-F(*c['modeled_CPU64_decode_rational'])) for c in sr['components']),F(0))
        self.assertEqual(F(*row['limb_vs_CPU64_decode_charge_L1_rational']),expected)
        self.assertEqual(F(*row['combined_error_L1_upper_rational']),expected+F(*row['transport_charge_L1_upper_rational']))
        self.oracle(r,[-F(.1),F(0)])

    def test_nonquarter_mirrorphase_and_mode_stop_before_production(self):
        for n,s in [('nonquarter',fixture(mirror=.1)),('mirror_phase',fixture(phase=.1)),('mode',fixture())]:
            if n=='mode':s['objects']['D']['mode_direction']=[1.,0.,0.]
            with patch('axial_quarter_source_ops_cpu_v1.permute_source_words',side_effect=AssertionError('must not produce')):
                r=self.keep(n+'_FAIL',run(s))
            self.assertFalse(r['field_values_computed']);self.assertFalse(r['accepted_original_ideal_scene_CPU_only'])

    def test_old_upstream_and_relative_failures_stay_fail(self):
        for n,s,opts in [('source0',fixture(),{'source_absolute_L1_budget':0}),
                ('high_intensity',fixture(.1*2**25),{}),('relative0',fixture(),{'field_relative_budget':0}),
                ('underflow',fixture(2**-150),{})]:
            r=self.keep(n+'_FAIL',run(s,**opts));self.assertFalse(r['accepted_original_ideal_scene_CPU_only'])
        with self.assertRaisesRegex(ValueError,'normal-or-zero'):run(fixture(2**-149))
        self.evidence['rejections']['subnormal_source']='normal-or-zero input rejection; no FTZ'

    def test_incoherent_groups_and_exact_zero_lower(self):
        s=dark();r=self.keep('separate_groups',run(s,coherence_groups={'s':'a','other':'b'}))
        self.assertEqual(set(r['reduction']['ports']['D']['groups']),{'a','b'});self.assertTrue(r['accepted_original_ideal_scene_CPU_only'])
        s=dark();s['sources'][0]['field_reim']=[.125,0.];s['sources'][1]['field_reim']=[-.125,0.]
        r=self.keep('exact_dark_zero_FAIL',run(s));self.oracle(r,[F(0),F(0)])
        self.assertFalse(r['accepted_original_ideal_scene_CPU_only'])

    def test_optin_limits_invalid_words_and_no_old_producer(self):
        with self.assertRaises(ValueError):run(fixture(),phase_model='general')
        with self.assertRaises(ValueError):permute_source_words([True,0,0,0],0)
        with self.assertRaises(ValueError):permute_source_words([0,0,0,0],True)
        with patch('axial_hilo_terminal_cpu_v1.produce_axial_hilo_model',side_effect=AssertionError('old producer')):
            r=run(fixture());self.assertTrue(r['accepted_original_ideal_scene_CPU_only'])
        self.evidence['rejections']['optin_words']='invalid model/bool words/quarter rejected'

    def test_no_near_quarter_tolerance_or_underflow_phase_admission(self):
        s=fixture();terminal=-.125-2**-30
        s['objects']['D']['vertices_world_BU']=[[terminal,*v[1:]] for v in s['objects']['D']['vertices_world_BU']]
        s['objects']['D']['mode_origin_BU'][0]=terminal
        for n,scene in [('near_quarter',s),('mirror_phase_underflow',fixture(phase=2**-150))]:
            with patch('axial_quarter_source_ops_cpu_v1.permute_source_words',side_effect=AssertionError('must not produce')):
                r=self.keep(n+'_FAIL',run(scene))
            self.assertFalse(r['field_values_computed']);self.assertFalse(r['accepted_original_ideal_scene_CPU_only'])


if __name__=='__main__':
    result=unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(QuarterSourceTests))
    if hasattr(QuarterSourceTests,'evidence'):print(json.dumps(QuarterSourceTests.evidence,sort_keys=True,allow_nan=False))
    sys.exit(0 if result.wasSuccessful() else 1)
