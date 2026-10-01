"""New one-mirror numerical fields; no old suite/sweeps/native dispatch."""
from copy import deepcopy
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'Blender/tests'))
sys.path.insert(0,str(ROOT/'Blender/benchmarks/capacity_audit'))
from test_axial_field_budget_cpu import fixture
from axial_scene_composition_cpu_v1 import produce_axial_transported_scene
from axial_scene_composition_cpu_v1 import inward_budget
from scene_field_producer_cpu_v1 import produce_scene_fields

PREVIOUS='coordinacion/respuestas/AXIAL-FIELD-BUDGET-001-CODEX.json'
PINS={PREVIOUS:'e1e5e05323efade609b52ff7478aaf86e342c78aaa8ba8b9ff05937b06cce09b',
 'Blender/benchmarks/capacity_audit/scene_field_producer_cpu_v1.py':'1a697f1cbe6dab515d27dbf5e4c022aae8b6099115b9961d225c0a318de3d380',
 'Blender/benchmarks/capacity_audit/history_trace_cpu_v1.py':'92ca7ddb64d95afc3205ddcfb129a5a129a9b5255ff51daf9917c0cceb9c1346',
 'Blender/benchmarks/capacity_audit/history_lengths_cpu_v1.py':'af48ff659152b5055bb4b3091ccdfa5655d995a0fb7bf607c784f243ae912ce3',
 'Blender/benchmarks/capacity_audit/history_completeness_cpu_v1.py':'750799dd1ad3639a4c84a30ef2e251ae4b1cb2c384d23511ff75b5fac387593a',
 'Blender/benchmarks/capacity_audit/coherent_error_composition_cpu_v1.py':'7e7988ecdb014d2eb3efff09af8c0e4aaf7cf94b39835fb8b0dfa18d99693879',
 'Blender/benchmarks/capacity_audit/coherent_reduction_cpu_v1.py':'cfd71837b19fd39cbf321ad41319587cd497397d266cc221d9da0c02c4f7d785'}

def run(scene,**changes):
    opts={'coherence_groups':{s['id']:'g' for s in scene['sources']},
        'source_absolute_L1_budget':F(1,10000),'source_relative_L1_budget':F(1,10000),
        'phase_budget_rad':F(1,10**12),'field_budget':F(1,10000),'intensity_budget':F(1,5000)}
    opts.update(changes);return produce_axial_transported_scene(scene,**opts)

class AxialCompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for p,h in PINS.items():
            if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('changed frozen input '+p)
        prior=json.loads((ROOT/PREVIOUS).read_text())
        cls.pins={**prior['code_doc_sha256'],**PINS}
        for p,h in cls.pins.items():
            if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('changed foundation '+p)
        cls.evidence={'pins_verified':cls.pins,'cases':{},'rejections':{},'GPU_executed':False,'old_suites_or_sweeps_rerun':False}
    def keep(self,name,r):self.evidence['cases'][name]=r;return r
    def enclosed(self,r,ideal):
        g=r['composition']['represented_reduction']['ports']['D']['groups']['g']
        actual=list(map(F,g['modeled_field_reim']));b=r['composition']['ports']['D']
        ef=sum(abs(a-i) for a,i in zip(actual,ideal));ep=abs(sum(a*a for a in actual)-sum(i*i for i in ideal))
        self.assertLessEqual(ef,F(*b['groups']['g']['composed_field_error_upper_rational']))
        self.assertLessEqual(ep,F(*b['intensity_error_upper_rational']))
        return {'ideal_field_rational':[[x.numerator,x.denominator] for x in ideal],
            'actual_error_L1_rational':[ef.numerator,ef.denominator],
            'actual_intensity_error_rational':[ep.numerator,ep.denominator]}
    def test_integer_and_quarter_turn_original_oracles(self):
        for name,terminal,ideal in [('integer',-.125,[-F(.1),F(0)]),('quarter',-.15625,[F(0),-F(.1)])]:
            scene=fixture();scene['objects']['D']['vertices_world_BU']=[[terminal,*v[1:]] for v in scene['objects']['D']['vertices_world_BU']]
            scene['objects']['D']['mode_origin_BU'][0]=terminal;before=deepcopy(scene)
            r=self.keep(name,run(scene));self.assertEqual(scene,before)
            r['independent_exact_oracle']=self.enclosed(r,ideal)
            self.assertTrue(r['accepted_original_ideal_scene_CPU_only']);self.assertTrue(r['field_values_computed'])
            self.assertFalse(r['native_promotion_allowed'])
    def test_coupled_nonexact_geometry_phase_and_source_charges(self):
        r=self.keep('coupled',run(fixture(mirror=.1,phase=.1)))
        self.assertTrue(r['accepted_original_ideal_scene_CPU_only'])
        p=r['path_error_components'][0]
        self.assertGreater(F(*p['numerical_producer_error_L1_upper_rational']),0)
        self.assertEqual(p['source_charge_L1_upper_rational'],[1,2**54])
        self.assertGreater(F(*p['phase_charge_L1_upper_rational']),0)
        self.assertGreaterEqual(F(*p['combined_error_L1_upper_rational']),
            F(*p['numerical_producer_error_L1_upper_rational'])+F(*p['transport_charge_L1_upper_rational']))
        self.assertNotEqual(r['original_scene_binding_sha256'],r['decoded_scene_binding_sha256'])
    def test_dark_sources_and_separate_groups(self):
        scene=fixture();s=deepcopy(scene['sources'][0]);s['id']='other';s['position_BU'][0]=.125
        s['field_reim']=[-.1+2**-30,0.];scene['sources'].append(s)
        r=self.keep('dark',run(scene));r['independent_exact_oracle']=self.enclosed(r,[-F(1,2**30),F(0)])
        self.assertTrue(r['accepted_original_ideal_scene_CPU_only']);self.assertEqual(len(r['rows']),2)
        r=self.keep('separate_groups',run(scene,coherence_groups={'s':'a','other':'b'}))
        self.assertEqual(set(r['composition']['ports']['D']['groups']),{'a','b'})
    def test_upstream_failure_not_hidden_by_numerical_pass(self):
        for name,scene,opts in [('phase0',fixture(mirror=.1,phase=.1),{'phase_budget_rad':0}),
            ('source0',fixture(),{'source_absolute_L1_budget':0}),('underflow',fixture(2**-150),{})]:
            r=self.keep(name,run(scene,**opts));self.assertTrue(r['field_values_computed'])
            self.assertFalse(r['accepted_original_ideal_scene_CPU_only'])
            self.assertTrue(r['composition']['accepted_conditional_upstream_and_reduction_only'])
    def test_high_intensity_FAIL_and_normal_output_profile(self):
        r=self.keep('high_intensity_FAIL',run(fixture(.1*2**25)))
        self.assertFalse(r['composition']['ports']['D']['intensity_budget_satisfied'])
        self.assertFalse(r['accepted_original_ideal_scene_CPU_only'])
        with self.assertRaisesRegex(ValueError,'normal-or-zero'):run(fixture(2**-149))
        self.evidence['rejections']['subnormal_output']='frozen normal-or-zero profile, no enlarged bounds'
    def test_unproved_mode_stops_before_producer(self):
        scene=fixture();scene['objects']['D']['mode_direction']=[1.,0.,0.]
        with patch('axial_scene_composition_cpu_v1.produce_scene_fields',side_effect=AssertionError('must not run')):
            r=self.keep('wrong_mode_FAIL',run(scene))
        self.assertFalse(r['field_values_computed']);self.assertFalse(r['accepted_original_ideal_scene_CPU_only'])
    def test_local_tamper_binding_coverage_length_rejected(self):
        def fake(kind):
            def altered(scene,**opts):
                p=produce_scene_fields(scene,**opts)
                if kind=='binding':p['scene_binding_sha256']='0'*64
                elif kind=='coverage':p['rows']=[]
                else:p['path_evidence'][0]['effective_length']['rational_lower']=[1,1]
                return p
            return altered
        for kind in ('binding','coverage','length'):
            with patch('axial_scene_composition_cpu_v1.produce_scene_fields',side_effect=fake(kind)):
                with self.assertRaisesRegex(ValueError,{'binding':'binding mismatch','coverage':'producer coverage','length':'effective length excludes'}[kind]):run(fixture())
            self.evidence['rejections']['local_tamper_'+kind]='rejected synthetic own output; no external artifact or native inference'
    def test_rational_budget_adaptation_is_inward(self):
        for budget in (F(1,10000),F(1,5000),F(1,2**1100),F(0)):
            self.assertLessEqual(F(inward_budget(budget)),budget)
        self.evidence['rejections']['budget_adapter']='inward only; no tolerance/budget enlargement'

if __name__=='__main__':
    result=unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(AxialCompositionTests))
    if hasattr(AxialCompositionTests,'evidence'):print(json.dumps(AxialCompositionTests.evidence,sort_keys=True,allow_nan=False))
    sys.exit(0 if result.wasSuccessful() else 1)
