"""New rational expansion scene model; old binary32 failures remain pinned."""
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
from axial_hilo_terminal_cpu_v1 import produce_axial_hilo_model, round32_exact, encode_hilo, word_value

PREVIOUS='coordinacion/respuestas/AXIAL-RELATIVE-GATE-001-CODEX.json'
PREVIOUS_SHA='bb81f3a0837b235ed16b2019f5a4d6cfc39ee0b9abfc8a055dc5af8b3aebda1d'

def run(scene,**changes):
    opts={'terminal_model':'rational-hilo32-reencode-v1','coherence_groups':{s['id']:'g' for s in scene['sources']},
        'source_absolute_L1_budget':F(1,10000),'source_relative_L1_budget':F(1,10000),'phase_budget_rad':F(1,10**12),
        'field_budget':F(1,10000),'intensity_budget':F(1,5000),
        'field_relative_budget':F(1,10**6),'intensity_relative_budget':F(1,10**6)}
    opts.update(changes);return produce_axial_hilo_model(scene,**opts)

def dark_scene():
    s=fixture();other=deepcopy(s['sources'][0]);other['id']='other';other['position_BU'][0]=.125
    other['field_reim']=[-.1+2**-30,0.];s['sources'].append(other);return s

class HiloTerminalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw=(ROOT/PREVIOUS).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=PREVIOUS_SHA:raise ValueError('prior relative evidence changed')
        cls.previous=json.loads(raw);cls.pins={**cls.previous['code_doc_sha256'],PREVIOUS:PREVIOUS_SHA}
        for p,h in cls.pins.items():
            if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('changed frozen input '+p)
        cls.old=json.loads((ROOT/'coordinacion/respuestas/AXIAL-SCENE-COMPOSITION-001-CODEX.json').read_text())['run']['observations']['cases']
        cls.evidence={'pins_verified':cls.pins,'cases':{},'rounding_controls':{},'old_producer_or_suites_rerun':False,'GPU_executed':False}
    def keep(self,name,r):self.evidence['cases'][name]=r;return r
    def oracle(self,r,ideal):
        p=r['ports']['D'];g=p['groups']['g'];observed=[F(*x) for x in g['modeled_field_rational']]
        e=sum(abs(a-b) for a,b in zip(observed,ideal));pe=abs(sum(x*x for x in observed)-sum(x*x for x in ideal))
        self.assertLessEqual(e,F(*g['field_error_L1_upper_rational']))
        self.assertLessEqual(pe,F(*p['power_error_upper_rational']))
        return {'original_ideal_field_rational':[[x.numerator,x.denominator] for x in ideal],
            'actual_error_L1_rational':[e.numerator,e.denominator],
            'actual_power_error_rational':[pe.numerator,pe.denominator]}
    def test_exact_rounding_repairs_double_round_tie_seed(self):
        for name,q,word in [('even_tie',F(1)+F(1,2**24),0x3f800000),
            ('above_tie',F(1)+F(1,2**24)+F(1,2**100),0x3f800001),
            ('below_tie',F(1)+F(1,2**24)-F(1,2**100),0x3f800000),
            ('odd_tie',F(1)+F(3,2**24),0x3f800002),
            ('negative_above',-F(1)-F(1,2**24)-F(1,2**100),0xbf800001)]:
            observed,value=round32_exact(q);self.assertEqual(observed,word)
            self.evidence['rounding_controls'][name]={'input':[q.numerator,q.denominator],'word':observed}
        self.assertEqual(round32_exact(F(1,2**150))[1],0)
        with self.assertRaisesRegex(ValueError,'normal-or-zero'):round32_exact(F(1,2**149))
        with self.assertRaisesRegex(ValueError,'bounded finite'):round32_exact(F(2)**200)
    def test_integer_and_quarter_original_oracles(self):
        for name,terminal,ideal in [('integer',-.125,[-F(.1),F(0)]),('quarter',-.15625,[F(0),-F(.1)])]:
            s=fixture();s['objects']['D']['vertices_world_BU']=[[terminal,*v[1:]] for v in s['objects']['D']['vertices_world_BU']]
            s['objects']['D']['mode_origin_BU'][0]=terminal;before=deepcopy(s)
            r=self.keep(name,run(s));self.assertEqual(s,before);r['independent_exact_oracle']=self.oracle(r,ideal)
            self.assertTrue(r['accepted_original_ideal_scene_CPU_only']);self.assertFalse(r['ALU_reduction_implemented'])
    def test_same_scene_dark_residual_new_model_not_frozen_fix(self):
        s=dark_scene();r=self.keep('dark_hilo_model',run(s));r['independent_exact_oracle']=self.oracle(r,[-F(1,2**30),F(0)])
        self.assertEqual(r['original_scene_binding_sha256'],self.old['dark']['original_scene_binding_sha256'])
        self.assertEqual(r['decoded_scene_binding_sha256'],self.old['dark']['decoded_scene_binding_sha256'])
        self.assertTrue(r['accepted_original_ideal_scene_CPU_only'])
        self.assertNotEqual(r['ports']['D']['groups']['g']['modeled_field_rational'][0],[0,1])
        self.assertEqual(self.old['dark']['composition']['represented_reduction']['ports']['D']['groups']['g']['modeled_field_reim'],[0.,0.])
        self.assertFalse(self.previous['run']['observations']['results']['dark_relative_FAIL']['accepted_retained_relative_CPU_only'])
        r['previous_frozen_binary32_dark']='output0/relativeFAIL retained, not repaired/replaced'
    def test_terminal_words_and_reencoding_errors_are_charged(self):
        r=self.keep('coupled',run(fixture(mirror=.1,phase=.1)))
        self.assertTrue(r['accepted_original_ideal_scene_CPU_only'])
        for row in r['rows']:
            words=row['field_hilo_uint32'];decoded=[F(word_value(words[i]))+F(word_value(words[i+1])) for i in (0,2)]
            self.assertEqual(decoded,[F(*v) for v in row['decoded_field_rational']])
            self.assertGreaterEqual(F(*row['combined_error_L1_upper_rational']),
                F(*row['numerical_phase_error_L1_upper_rational'])+F(*row['conversion_error_L1_rational'])+F(*row['transport_charge_L1_upper_rational']))
        for p in r['ports'].values():
            for g in p['groups'].values():
                self.assertLessEqual(F(*g['rational_reduction_error_L1_rational']),
                    sum((F(*s['rational_reencode_error_L1_rational']) for s in g['steps']),F(0)))
    def test_source_order_and_incoherent_groups_explicit(self):
        s=dark_scene();s['sources'].reverse();r=self.keep('dark_reversed',run(s));self.oracle(r,[-F(1,2**30),F(0)])
        self.assertTrue(r['accepted_original_ideal_scene_CPU_only'])
        s=dark_scene();r=self.keep('separate_groups',run(s,coherence_groups={'s':'a','other':'b'}))
        self.assertEqual(set(r['ports']['D']['groups']),{'a','b'});self.assertTrue(r['accepted_original_ideal_scene_CPU_only'])
    def test_source_phase_high_intensity_and_zero_budgets_FAIL_retained(self):
        for name,s,opts in [('source0',fixture(),{'source_absolute_L1_budget':0}),
            ('phase0',fixture(mirror=.1,phase=.1),{'phase_budget_rad':0}),
            ('high_intensity_FAIL',fixture(.1*2**25),{}),('relative0',fixture(),{'field_relative_budget':0}),
            ('underflow',fixture(2**-150),{})]:
            r=self.keep(name,run(s,**opts));self.assertFalse(r['accepted_original_ideal_scene_CPU_only'])
        self.assertFalse(self.evidence['cases']['high_intensity_FAIL']['ports']['D']['intensity_absolute_budget_satisfied'])
        with self.assertRaisesRegex(ValueError,'normal-or-zero'):run(fixture(2**-149))
    def test_opt_in_and_unproved_mode_stop_before_field_evaluation(self):
        with self.assertRaisesRegex(ValueError,'explicit'):run(fixture(),terminal_model='binary32')
        s=fixture();s['objects']['D']['mode_direction']=[1.,0.,0.]
        with patch('axial_hilo_terminal_cpu_v1.rotation',side_effect=AssertionError('must not evaluate')):
            r=self.keep('wrong_mode_FAIL',run(s))
        self.assertFalse(r['field_values_computed']);self.assertFalse(r['accepted_original_ideal_scene_CPU_only'])
    def test_quantization_error_and_zero_relative_denominator(self):
        words,decoded,error=encode_hilo(F(1)+F(1,2**24)+F(1,2**100))
        self.assertEqual(error,abs(decoded-(F(1)+F(1,2**24)+F(1,2**100))))
        self.evidence['rounding_controls']['hilo_conversion']={'words':words,'error':[error.numerator,error.denominator]}
        s=dark_scene();s['sources'][0]['field_reim']=[.125,0.];s['sources'][1]['field_reim']=[-.125,0.]
        r=self.keep('exact_dark_zero_FAIL',run(s));self.oracle(r,[F(0),F(0)])
        self.assertFalse(r['accepted_original_ideal_scene_CPU_only'])
        self.assertIsNone(r['ports']['D']['groups']['g']['relative_field']['relative_error_upper_rational'])

if __name__=='__main__':
    result=unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(HiloTerminalTests))
    if hasattr(HiloTerminalTests,'evidence'):print(json.dumps(HiloTerminalTests.evidence,sort_keys=True,allow_nan=False))
    sys.exit(0 if result.wasSuccessful() else 1)
