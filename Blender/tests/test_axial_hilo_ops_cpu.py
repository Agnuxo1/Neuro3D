"""Operation graph CPU checks on retained scene terminals, no scene replay."""
from copy import deepcopy
from fractions import Fraction as F
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'Blender/benchmarks/capacity_audit'))
from axial_hilo_ops_cpu_v1 import MODEL, audit_retained_hilo_operations, add_hilo_words, component, _case, load_retained
from axial_hilo_terminal_cpu_v1 import round32_exact


def word(v):return round32_exact(F(v))[0]


class HiloOpsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.previous=load_retained();cls.old=cls.previous['run']['observations']['cases']
        cls.evidence={'primitives':{},'negative_controls':[]}

    def test_retained_scene_cases_no_producer(self):
        with patch('axial_hilo_terminal_cpu_v1.produce_axial_hilo_model',side_effect=AssertionError('no replay')):
            self.report=audit_retained_hilo_operations(case_names=list(self.old),operation_model=MODEL)
        self.evidence['audit']=self.report
        for n,c in self.report['cases'].items():
            self.assertEqual(c['previous_case_accepted'],self.old[n]['accepted_original_ideal_scene_CPU_only'])
            if not c['previous_case_accepted']:self.assertFalse(c['accepted_operation_model_CPU_only'])
            self.assertFalse(c['ALU_executed']);self.assertFalse(c['GPU_executed'])
            if self.old[n]['field_values_computed']:
                self.assertEqual(c['original_scene_binding_sha256'],self.old[n]['original_scene_binding_sha256'])
                self.assertEqual(c['RN32_operations'],64*len(self.old[n]['rows']))
                for p in c['ports'].values():
                    for g in p['groups'].values():
                        self.assertLessEqual(F(*g['actual_reduction_error_rational']),F(*g['reduction_error_upper_rational']))
        self.assertFalse(self.report['cases']['wrong_mode_FAIL']['accepted_operation_model_CPU_only'])

    def test_each_RN32_node_and_graph_bound(self):
        controls=[('tie',[word(1),0],[word(F(1,2**24)),0]),
            ('cancel',[word(1),word(F(1,2**30))],[word(-1),0]),
            ('unequal',[word(2**24),word(1)],[word(-2**24),word(F(1,2**24))])]
        for name,a,b in controls:
            r=add_hilo_words(a,b,operation_model=MODEL);self.evidence['primitives'][name]=r
            self.assertEqual(len(r['operations']),32)
            for node in r['operations']:
                x,y=map(lambda z:F(*z),node['input_rational']);q=x+y if node['op']=='add' else x-y
                self.assertEqual(node['output_uint32'],round32_exact(q)[0])
                self.assertEqual(F(*node['rounding_delta_rational']),component(node['output_uint32'])-q)
            self.assertLessEqual(F(*r['actual_error_rational']),F(*r['error_upper_rational']))
        self.assertEqual(F(*self.evidence['primitives']['cancel']['decoded_rational']),F(1,2**30))

    def test_nonexact_reduction_charge_not_silently_exact(self):
        a=[word(1),word(F(1,2**24))];b=[word(F(1,2**48)),word(F(1,2**72))]
        r=add_hilo_words(a,b,operation_model=MODEL);self.evidence['primitives']['nonexact']=r
        self.assertGreater(F(*r['actual_error_rational']),0)
        self.assertGreaterEqual(F(*r['error_upper_rational']),F(*r['actual_error_rational']))

    def test_subnormal_intermediate_rejects_without_FTZ(self):
        # Both inputs normal, their sum is the smallest subnormal: reject.
        with self.assertRaisesRegex(ValueError,'normal-or-zero'):
            add_hilo_words([0x00800001,0],[0x80800000,0],operation_model=MODEL)
        self.evidence['negative_controls'].append('normal inputs -> subnormal first sum rejected')

    def test_malformed_nonfinite_overflow_inputs_fail_closed(self):
        for bad in [True,-1,2**32,0x7f800000,0x7fc00000,1]:
            with self.assertRaises(ValueError):add_hilo_words([bad,0],[0,0],operation_model=MODEL)
        with self.assertRaises(ValueError):add_hilo_words([0x7f7fffff,0],[0x7f7fffff,0],operation_model=MODEL)
        with self.assertRaises(ValueError):add_hilo_words([0],[0,0],operation_model=MODEL)
        self.evidence['negative_controls'].append('malformed/nonfinite/subnormal/overflow rejected')

    def test_no_floor_at_exact_dark_zero(self):
        r=_case(self.old['exact_dark_zero_FAIL']);g=r['ports']['D']['groups']['g']
        self.assertIsNone(g['relative_field']['relative_error_upper_rational'])
        self.assertFalse(r['accepted_operation_model_CPU_only'])

    def test_gauge_words_and_coverage_reject_mutated_CPU_copies(self):
        for key in ['phase_reference_id','field_hilo_uint32','source_id','port']:
            c=deepcopy(self.old['integer'])
            c['rows'][0][key]=[0,0,0,0] if key=='field_hilo_uint32' else 'wrong'
            with self.assertRaises(ValueError):_case(c)
        self.evidence['negative_controls'].append('CPU copies only: gauge/words/source/port mismatch rejected')

    def test_optin_selection_and_SHA_required(self):
        for names in [[],['integer','integer'],['unknown'],[['unhashable']], [True]]:
            with self.assertRaises(ValueError):audit_retained_hilo_operations(case_names=names,operation_model=MODEL)
        with self.assertRaises(ValueError):audit_retained_hilo_operations(case_names=['integer'],operation_model='native')
        with patch('axial_hilo_ops_cpu_v1.SHA','0'*64):
            with self.assertRaisesRegex(ValueError,'SHA'):load_retained()
        self.evidence['negative_controls'].append('selection/optin/SHA rejected without file mutation')


if __name__=='__main__':
    result=unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(HiloOpsTests))
    if hasattr(HiloOpsTests,'evidence'):print(json.dumps(HiloOpsTests.evidence,sort_keys=True,allow_nan=False))
    sys.exit(0 if result.wasSuccessful() else 1)
