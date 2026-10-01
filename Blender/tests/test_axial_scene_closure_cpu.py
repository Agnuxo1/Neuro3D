"""New offline identity contract tests; no production arithmetic replay."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'benchmarks' / 'capacity_audit'))
import axial_scene_closure_cpu_v1 as m


class ClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chain, cls.artifacts, cls.pins = m.load_retained()

    def mutated(self, stage, mutate, name='positive'):
        chain = deepcopy(self.chain)
        mutate(chain[stage][name])
        # Refresh structural hashes: matching hashes alone must NOT rescue invalid scope.
        for prev, nxt, key in zip(m.STAGES, m.STAGES[1:],
                ('geometry_case_sha256', 'geometry_bridge_case_sha256',
                 'retained_unit_case_sha256', 'source_product_case_sha256')):
            chain[nxt][name][key] = m.digest(chain[prev][name])
        return chain

    def test_retained_all_cases_and_stops(self):
        cases = m.validate_cases(self.chain)
        self.assertEqual(len(cases), 13)
        self.assertEqual(sum(len(c['source_ids']) for c in cases.values()), 14)
        self.assertEqual(sum(not c['stage_gates_retained'][4] for c in cases.values()), 8)
        self.assertEqual(sum(c['numerical_chain_partial_CPU_only'] for c in cases.values()), 4)
        self.assertFalse(cases['two_sources']['numerical_chain_partial_CPU_only'])
        self.assertTrue(all(not c['accepted_full_field_pipeline'] for c in cases.values()))

    def test_complete_case_and_stage_coverage(self):
        for stage in m.STAGES:
            with self.subTest(stage=stage):
                c = deepcopy(self.chain)
                c[stage].pop('two_sources')
                with self.assertRaises(ValueError):
                    m.validate_cases(c)
        c = deepcopy(self.chain); c.pop('UNIT')
        with self.assertRaises(ValueError):
            m.validate_cases(c)

    def test_case_digest_and_binding(self):
        c = deepcopy(self.chain)
        c['SOURCE']['positive']['retained_unit_case_sha256'] = '0' * 64
        with self.assertRaises(ValueError):
            m.validate_cases(c)
        c = self.mutated('QUOTIENT', lambda v: v.update(original_scene_binding_sha256='0' * 64))
        with self.assertRaises(ValueError):
            m.validate_cases(c)

    def test_source_gauge_ids_order_and_coverage(self):
        mutations = (
            ('SOURCE', lambda v: v['paths'][0].update(phase_reference_id='borrowed-reference')),
            ('SOURCE', lambda v: v.update(source_order=['s', 's'])),
            ('SOURCE', lambda v: v['paths'].append(deepcopy(v['paths'][0]))),
            ('REDUCTION', lambda v: v['contract']['assignments'][0].update(source_id='foreign')),
            ('REDUCTION', lambda v: v['ports']['D']['groups']['g'].update(source_ids=[])),
        )
        for stage, mutate in mutations:
            with self.subTest(stage=stage):
                with self.assertRaises(ValueError):
                    m.validate_cases(self.mutated(stage, mutate))

    def test_object_order_and_domain_not_general_tree(self):
        for mutate in (lambda v: v['word_ABI'].update(object_ids=['D', 'M']),
                       lambda v: v['scene_snapshot']['objects']['M'].update(kind='bs')):
            with self.assertRaises(ValueError):
                m.validate_cases(self.mutated('WORDS', mutate))

    def test_caps_are_frozen_no_defaults_or_relaxation(self):
        for value in ([1, 1], [True, 1], [1, 0], [float('nan'), 1]):
            with self.subTest(value=str(value)):
                c = self.mutated('REDUCTION',
                    lambda v: v['contract']['limits'].update(field_L1=value))
                with self.assertRaises(ValueError):
                    m.validate_cases(c)
        c = self.mutated('SOURCE', lambda v: v['paths'][0].update(field_absolute_L1_budget=[1, 1]))
        with self.assertRaises(ValueError):
            m.validate_cases(c)

    def test_no_revived_failure_and_exact_bool(self):
        for value in (True, 1, 'PASS'):
            c = self.mutated('REDUCTION', lambda v: v.update(accepted_reduction_detector_CPU_only=value),
                             'thin_collapsed_FAIL')
            with self.assertRaises(ValueError):
                m.validate_cases(c)
        c = self.mutated('UNIT', lambda v: v.update(previous_bridge_phase_accepted=1))
        with self.assertRaises(ValueError):
            m.validate_cases(c)
        for mutate in (
                lambda v: v['paths'][0].update(accepted_unit_CPU_only=False),
                lambda v: v['paths'][0].pop('phase_reference_id'),
                lambda v: v['paths'][0].update(previous_bridge_phase_accepted=False)):
            with self.assertRaises(ValueError):
                m.validate_cases(self.mutated('UNIT', mutate))

    def test_cpu_group_hypothesis_not_authentication(self):
        for mutate in (lambda v: v.update(coherence_authenticated=True),
                       lambda v: v.update(accepted_full_field_pipeline=True),
                       lambda v: v['contract'].update(grouping_provenance='measured scene coherence'),
                       lambda v: v['contract']['assignments'][0].update(common_phase_reference_id='borrowed')):
            with self.assertRaises(ValueError):
                m.validate_cases(self.mutated('REDUCTION', mutate))

    def test_historical_gpu_guard_and_cpu_adapters_not_current_proof(self):
        inv = m.inventory(self.artifacts)
        self.assertEqual(inv['historical_native0337']['probes'], 246)
        self.assertFalse(inv['native_promotion_allowed'])
        self.assertFalse(inv['GPU_job_admission'])
        self.assertFalse(inv['historical_native0337']['current_RN64_scene_chain_binding_present'])
        for k in ('supervisorCPU', 'captureCPU'):
            v = deepcopy(self.artifacts); v[k]['runtime_execution_authenticated'] = True
            with self.assertRaises(ValueError):
                m.inventory(v)
        v = deepcopy(self.artifacts); v['guard0337']['deadline_utc'] = '2026-10-01T16:00:00+00:00'
        with self.assertRaises(ValueError):
            m.inventory(v)

    def test_strict_json_and_pin(self):
        for raw in ('{"x":1,"x":2}', '{"x":NaN}', '{"x":Infinity}'):
            with self.assertRaises(ValueError):
                m.parse(raw)
        with self.assertRaises(ValueError):
            m.pinned('coordinacion/respuestas/AXIAL-GEOMETRY-REDUCTION-001-CODEX.json', '0' * 64)


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ClosureTests)
    outcome = unittest.TextTestRunner().run(suite)
    if outcome.wasSuccessful():
        print(json.dumps(m.audit(), sort_keys=True, separators=(',', ':'), allow_nan=False))
    raise SystemExit(not outcome.wasSuccessful())
