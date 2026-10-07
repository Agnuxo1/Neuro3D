"""Reconcile recorded durations only; no benchmark or foreign execution."""
import ast
from decimal import Decimal as D
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
PARENT = ROOT/'coordinacion/respuestas/PRECISION-EXISTING-P03-BACKEND-SCOPE-HOST-001-CODEX.json'
PARENT_SHA = '71bc2991dc808dac8a28cb191c0b5e7b14d4d420da46ee3a1d598373e1e84b2c'
BASE = 'D:/PROJECTS/.cognition/neuro3d/p0_scene_gpu/'
BACKEND = 'D:/PROJECTS/.cognition/neuro3d/nebulatrace/gpu_states_v2.py'
RECORDS = []


class CostScopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw = PARENT.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=PARENT_SHA:
            raise ValueError('sealed parent content changed')
        parent = json.loads(raw)
        cls.blobs = {}
        for p,pin in parent['pins'].items():
            b = Path(p).read_bytes()
            if len(b)!=pin['bytes'] or hashlib.sha256(b).hexdigest()!=pin['sha256']:
                raise ValueError('retained input changed: '+p)
            cls.blobs[p.replace('\\','/')] = b

    def test_recorded_duration_accounting(self):
        result = json.loads(self.blobs[BASE+'p03_cuda_result.json'],parse_float=D)
        env = json.loads(self.blobs[BASE+'p03_cuda_envelope.json'],parse_float=D)
        groups = result['groups']
        self.assertEqual(len(groups),10)
        total = D(0)
        for group in groups:
            s = group['seconds_total']
            self.assertIsInstance(s,D)
            self.assertTrue(s.is_finite() and s>=0)
            total += s
            RECORDS.append(dict(kind='RETAINED_GROUP_ENGINE_DURATION',shape=group['shape'],
                                seconds=str(s),scope='TRACE_FUNCTION_NOT_BATCH_OR_FULL_HARNESS'))
        harness, guard = result['seconds'],env['seconds']
        self.assertGreater(harness,total)
        self.assertGreater(guard,harness)
        RECORDS.append(dict(kind='RETAINED_DURATION_ARITHMETIC_ONLY',
            engine_group_sum_seconds=str(total),harness_recorded_seconds=str(harness),
            guard_envelope_seconds=str(guard),
            harness_minus_group_sum_seconds=str(harness-total),
            guard_minus_harness_seconds=str(guard-harness),
            subtraction_proves_overhead=False,subtraction_proves_common_clock_or_coverage=False,
            repeat_samples=0,performance_comparison=False))

    def test_timer_placement_in_pinned_source(self):
        text = self.blobs[BACKEND].decode()
        tree = ast.parse(text)
        trace = next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='trace')
        t0 = next(x for x in trace.body if isinstance(x,ast.Assign)
                  and any(isinstance(t,ast.Name) and t.id=='t0' for t in x.targets))
        policy = next(x for x in trace.body if isinstance(x,ast.Assign)
                      and isinstance(x.value,ast.Call) and isinstance(x.value.func,ast.Name)
                      and x.value.func.id=='quant_policy')
        self.assertLess(policy.lineno,t0.lineno)
        self.assertEqual(ast.unparse(t0.value),'time.perf_counter()')
        harness = self.blobs[BASE+'p03_harness_v4.py'].decode()
        anchors = ['Bt = gs.Batch(snaps, DEV); r = gs.trace(Bt, policy=POLICY)',
                   "U = r['U'].cpu().numpy()",'f = complex(U[i, pi] @ amp)',
                   "res['seconds'] = time.time() - t0", "json.dump(res, open(OUT, 'w')"]
        positions = [harness.index(a) for a in anchors]
        self.assertEqual(positions,sorted(positions))
        RECORDS.append(dict(kind='SOURCE_TIMER_BOUNDARIES',
            quant_policy_before_engine_timer=True,batch_before_trace_call=True,
            U_download_and_SOURCE_fields_after_trace=True,
            result_serialization_after_harness_timer=True,
            transfer_completion_attribution='UNKNOWN_ASYNC_NOT_INFERRED',
            clocks=['engine:perf_counter','harness:time.time','guard:recorded_envelope_seconds']))

    def test_missing_costs_remain_unknown(self):
        result = json.loads(self.blobs[BASE+'p03_cuda_result.json'])
        for key in ('batch_seconds','host_source_normalization_seconds',
                    'host_edge_preparation_seconds','H2D_seconds','D2H_seconds',
                    'host_source_field_composition_seconds','energy_joules',
                    'peak_RAM_bytes','peak_VRAM_bytes','cold_warm_repetition_protocol',
                    'per_stage_common_clock_intervals'):
            self.assertNotIn(key,result)
        self.assertTrue(all('seconds_trace' not in x for x in result['groups']))
        self.assertTrue(all('seconds_total' not in result[key] for key in ('mzi','conf1','strict_control')))
        RECORDS.append(dict(kind='COST_DETAIL_NOT_IN_THIS_RESULT',
            missing_top_level_components=11,retained_group_trace_subtimer=False,
            other_controls_engine_duration=None,energy_joules=None,
            whole_pipeline_comparable_cost=None,missing_means_zero=False))


if __name__=='__main__':
    run = unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(CostScopeTests))
    print(json.dumps(dict(status='PASS' if run.wasSuccessful() else 'FAIL',tests=run.testsRun,
        records=RECORDS,scope='RECORDED_TIMERS_AND_SOURCE_BOUNDARIES_ONLY',
        foreign_execution=False,new_GPU_execution=False,equal_work_certified=False,
        full_cost_certified=False,precision_promotion=False)))
    raise SystemExit(0 if run.wasSuccessful() else 1)
