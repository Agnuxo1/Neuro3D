"""NEW coupled source/path cases, bound only; no old producer/sweep."""
from copy import deepcopy
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'Blender/tests'))
sys.path.insert(0,str(ROOT/'Blender/benchmarks/capacity_audit'))
from axial_field_budget_cpu_v1 import certify_reflected_transport_field_budget
from test_axial_reflection_margin_cpu import reflected_scene, PINS as PATH_PINS

PINS=dict(PATH_PINS,**{
    'Blender/benchmarks/capacity_audit/axial_reflection_margin_cpu_v1.py':'8ff4a6f7f89f3edcec0a9fd3015e0258d57bd3d0449b29395d64d2e86b1035d9',
    'Blender/tests/test_axial_reflection_margin_cpu.py':'c9a2e1bcc4083258ab6379a4830dee0e166f3450158926faaabd91c584cb8bfe',
    'coordinacion/respuestas/AXIAL-REFLECTION-MARGIN-001-CODEX.json':'80656fc8c3abebb7cb65dc797e9315e65adc9c2833e98533daf54c9b22e8cced',
    'Blender/benchmarks/capacity_audit/source_transport_budget_cpu_v1.py':'e6aeda7f4d6423719eacc119828190b9b56b2e9cd4be0ce25a89450e11bb8fcb'})


def fixture(amplitude=.1,mirror=.25,phase=0.):
    snapshot=reflected_scene(mirror,-.125,mirror_phase=phase)
    snapshot['objects']['D']['mode_direction']=[-1.,0.,0.]
    snapshot['sources'][0]['field_reim']=[amplitude,0.]
    return snapshot


def certify(snapshot,**changes):
    options={'coherence_groups':{s['id']:'g' for s in snapshot['sources']},
        'source_absolute_L1_budget':F(1,10000),'source_relative_L1_budget':F(1,10000),
        'phase_budget_rad':F(1,10**12),'field_absolute_L1_budget':F(1,10000),
        'intensity_absolute_budget':F(1,5000)}
    options.update(changes)
    return certify_reflected_transport_field_budget(snapshot,**options)


class FieldBudgetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for p,h in PINS.items():
            if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h:
                raise ValueError('changed frozen foundation: '+p)
        cls.evidence={'pins_verified':PINS,'new_cases':{},'old_producer_or_sweeps_rerun':False,'GPU_executed':False}

    def keep(self,name,result):
        self.evidence['new_cases'][name]=result
        return result['terminal_groups'][0] if result['terminal_groups'] else None

    def test_source_error_composed_in_same_scene(self):
        snapshot=fixture();before=deepcopy(snapshot);result=certify(snapshot)
        group=self.keep('ordinary_source_PASS',result)
        self.assertEqual(snapshot,before)
        self.assertTrue(result['accepted_CPU_transport_budget_only'])
        self.assertEqual(group['transport_field_error_L1_upper_rational'],[1,2**54])
        self.assertEqual(result['contributions'][0]['phase_charge_L1_upper_rational'],[0,1])
        self.assertFalse(result['field_values_computed']);self.assertFalse(result['native_promotion_allowed'])

    def test_large_source_power_gate_fail_remains(self):
        result=certify(fixture(.1*2**25));group=self.keep('high_amplitude_intensity_FAIL',result)
        self.assertEqual(group['transport_field_error_L1_upper_rational'],[1,2**29])
        self.assertTrue(group['field_budget_satisfied'])
        self.assertFalse(group['intensity_budget_satisfied'])
        self.assertFalse(result['accepted_CPU_transport_budget_only'])

    def test_geometry_mirror_phase_and_source_charges_remain_separate(self):
        result=certify(fixture(mirror=.1,phase=.1));self.keep('coupled_geometry_source_PASS',result)
        row=result['contributions'][0]
        expected=2*F(.1)*(F(1,2**48)+F(1,2**55))
        self.assertEqual(F(*row['phase_charge_L1_upper_rational']),expected)
        self.assertEqual(row['source_charge_L1_upper_rational'],[1,2**54])
        self.assertTrue(result['accepted_CPU_transport_budget_only'])
        tight=certify(fixture(mirror=.1,phase=.1),phase_budget_rad=0)
        self.keep('phase_budget_zero_FAIL',tight)
        self.assertTrue(tight['terminal_groups'][0]['field_budget_satisfied'])
        self.assertFalse(tight['accepted_CPU_transport_budget_only'])

    def test_distinct_dark_sources_no_cancellation_credit(self):
        snapshot=fixture();second=deepcopy(snapshot['sources'][0])
        second['id']='other';second['position_BU'][0]=.125
        second['field_reim']=[-.1+2**-30,0.];snapshot['sources'].append(second)
        result=certify(snapshot);group=self.keep('dark_sources_separate_PASS',result)
        rows=result['contributions']
        self.assertEqual([r['source_id'] for r in rows],['s','other'])
        self.assertEqual(F(*group['transport_field_error_L1_upper_rational']),
            sum((F(*r['source_charge_L1_upper_rational']) for r in rows),F(0)))
        # Both represented paths have integer turns (5 and4), mirror sign=-1.
        original=-sum((F(s['field_reim'][0]) for s in snapshot['sources']),F(0))
        recovered=-sum((F(*r['components'][0]['modeled_CPU64_decode_rational']) for r in result['source_transport']['sources']),F(0))
        self.assertEqual(original,-F(1,2**30))
        self.assertLessEqual(abs(recovered-original),F(*group['transport_field_error_L1_upper_rational']))
        self.assertGreater(F(*group['original_coherent_modulus_upper_rational']),abs(original))

    def test_coherence_groups_do_not_silently_merge(self):
        snapshot=fixture();second=deepcopy(snapshot['sources'][0]);second['id']='other'
        second['position_BU'][0]=.125;snapshot['sources'].append(second)
        result=certify(snapshot,coherence_groups={'s':'g1','other':'g2'})
        self.evidence['new_cases']['separate_coherence_groups_PASS']=result
        self.assertEqual(len(result['terminal_groups']),2)
        self.assertEqual([g['source_ids'] for g in result['terminal_groups']],[['s'],['other']])
        with self.assertRaises(ValueError):certify(snapshot,coherence_groups={'s':'g'})

    def test_mode_reference_and_direction_are_required(self):
        for name,change in (('wrong_reference',True),('wrong_direction',False)):
            snapshot=fixture()
            if change:snapshot['objects']['D']['mode_origin_BU'][0]+=.03125
            else:snapshot['objects']['D']['mode_direction']=[1.,0.,0.]
            result=certify(snapshot);self.keep(name+'_FAIL',result)
            self.assertFalse(result['accepted_CPU_transport_budget_only'])
            self.assertIn('co-moving',result['contributions'][0]['reason'])

    def test_underflow_and_source_exactness_budget_fail_independently(self):
        result=certify(fixture(2**-150));self.keep('underflow_relative_source_FAIL',result)
        self.assertTrue(result['terminal_groups'][0]['field_budget_satisfied'])
        self.assertFalse(result['source_transport']['accepted_CPU_source_transport_budget_only'])
        self.assertFalse(result['accepted_CPU_transport_budget_only'])

    def test_partial_coherent_group_is_never_accepted(self):
        snapshot=fixture();second=deepcopy(snapshot['sources'][0]);second['id']='other'
        second['position_BU'][0]=.125;second['direction']=[-1.,0.,0.]
        snapshot['sources'].append(second)
        result=certify(snapshot);group=self.keep('partial_group_coverage_FAIL',result)
        self.assertFalse(group['scene_source_coverage_complete'])
        self.assertFalse(group['accepted_CPU_transport_budget_only'])
        self.assertFalse(result['accepted_CPU_transport_budget_only'])
        self.assertIn('unproved',result['contributions'][1]['reason'])
        result=certify(fixture(),source_absolute_L1_budget=0)
        self.keep('source_exactness_zero_FAIL',result)
        self.assertFalse(result['accepted_CPU_transport_budget_only'])


if __name__=='__main__':
    result=unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(FieldBudgetTests))
    if hasattr(FieldBudgetTests,'evidence'):
        print(json.dumps(FieldBudgetTests.evidence,sort_keys=True,allow_nan=False))
    sys.exit(0 if result.wasSuccessful() else 1)
