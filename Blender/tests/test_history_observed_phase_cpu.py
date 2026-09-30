"""Focused synthetic observation tests; no peer writers, Blender or GPU."""
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import io
import json
from pathlib import Path
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'Blender/benchmarks/capacity_audit'))
sys.path.insert(0, str(ROOT/'Blender/tests'))
from exp005_history_mzi_audit import fixture
from history_compensated_phase_budget_cpu_v1 import scene_compensated_phase_budget
from history_observed_phase_cpu_v1 import SCHEMA, validate_observed_phase
from phase_compensated_cpu_v1 import compensated_angle


def sample():
    scene, _ = fixture(); scene['lambda_BU'] = 3*2.**-20
    groups = {scene['sources'][0]['id']: 'g0'}
    budget = scene_compensated_phase_budget(scene, coherence_groups=groups,
        field_budget=1e-4, intensity_budget=2e-4, relative_budget=1e-12)
    report = {'schema': SCHEMA, 'scene_binding_sha256': budget['scene_binding_sha256'],
        'coherence_groups': groups, 'decoded_lambda_BU': budget['wavelength_transport']['decoded_BU'],
        'terminals': [{key: p[key] for key in ('id','source_id','port','coherence_group')}
            | {'effective_length_BU': p['represented_effective_length_BU'], 'phase_trace': p['CPU_phase_trace']}
            for p in budget['ledger']]}
    return scene, groups, report


def check(scene, groups, report):
    return validate_observed_phase(scene, report, coherence_groups=groups,
        field_budget=1e-4, intensity_budget=2e-4, relative_budget=1e-12)


class ObservedCPU(unittest.TestCase):
    def test_matching_and_reordered_data(self):
        scene, groups, report = sample(); out = check(scene,groups,report)
        self.assertTrue(out['accepted_conditional_ideal_budget'])
        self.assertEqual(out['generated_record_count'],13); self.assertEqual(len(out['ledger']),4)
        report['terminals'].reverse()
        self.assertEqual(out['ports'],check(scene,groups,report)['ports'])
        self.assertFalse(out['observation_execution_authenticated'])
        self.assertFalse(out['native_promotion_allowed'])

    def test_consistent_but_displaced_length_is_charged(self):
        scene, groups, report = sample(); path = report['terminals'][0]
        path['effective_length_BU'] += 1e-7
        path['phase_trace'] = compensated_angle(path['effective_length_BU'],report['decoded_lambda_BU'])
        out = check(scene,groups,report)
        self.assertFalse(out['accepted_conditional_ideal_budget'])
        self.assertGreater(F(*out['ledger'][0]['field_error_upper']['rational_upper']),F(1e-4))

    def test_missing_duplicate_and_foreign_ids_reject(self):
        scene, groups, report = sample()
        variants = [deepcopy(report) for _ in range(4)]
        variants[0]['terminals'].pop()
        variants[1]['terminals'][1] = deepcopy(variants[1]['terminals'][0])
        variants[2]['terminals'][0]['id'] = 999
        variants[3]['terminals'][0]['id'] = True
        for variant in variants:
            with self.assertRaises(ValueError): check(scene,groups,variant)

    def test_bindings_reject(self):
        scene, groups, report = sample()
        for key in ('scene_binding_sha256','coherence_groups','decoded_lambda_BU'):
            variant = deepcopy(report)
            variant[key] = {'wrong':'g0'} if key=='coherence_groups' else ('wrong' if key.endswith('sha256') else .125)
            with self.assertRaises(ValueError): check(scene,groups,variant)
        for key in ('source_id','port','coherence_group'):
            variant=deepcopy(report); variant['terminals'][0][key]='wrong'
            with self.assertRaises(ValueError): check(scene,groups,variant)

    def test_nonfinite_and_stale_phase_reject(self):
        scene, groups, report = sample()
        for invalid in (float('nan'),float('inf')):
            variant=deepcopy(report);variant['terminals'][0]['effective_length_BU']=invalid
            with self.assertRaises(ValueError): check(scene,groups,variant)
        variant=deepcopy(report);variant['terminals'][0]['phase_trace']['angle_float32'] += .01
        with self.assertRaises(ValueError): check(scene,groups,variant)

    def test_no_native_schema_claims(self):
        scene, groups, report = sample()
        report['schema']='native-GPU-certified'
        with self.assertRaises(ValueError): check(scene,groups,report)
        report['schema']=SCHEMA; report['runtime_certified']=True
        with self.assertRaises(ValueError): check(scene,groups,report)


def audit():
    started=time.monotonic(); retained=ROOT/'coordinacion/respuestas/PHASE-COMPOSED-001-CODEX.json'
    assert hashlib.sha256(retained.read_bytes()).hexdigest()=='45247bba869e7b0bed6a7f0ed99c8e2a9a7a8ef4d5c8042532051ba013efe738'
    baseline=json.loads(retained.read_text()); inherited={**baseline['code_sha256'],**baseline['baseline_code_sha256']}
    paths=[Path(p) for p in inherited]+[Path(__file__),ROOT/'Blender/benchmarks/capacity_audit/history_observed_phase_cpu_v1.py',retained]
    pins={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    assert all(pins[p]==sha for p,sha in inherited.items())
    stream=io.StringIO();tests=unittest.TextTestRunner(stream=stream).run(unittest.defaultTestLoader.loadTestsFromTestCase(ObservedCPU))
    if not tests.wasSuccessful():raise AssertionError(stream.getvalue())
    scene,groups,report=sample();matched=check(scene,groups,report)
    path=report['terminals'][0];path['effective_length_BU']+=1e-7
    path['phase_trace']=compensated_angle(path['effective_length_BU'],report['decoded_lambda_BU'])
    shifted=check(scene,groups,report)
    summary=lambda r:{'accepted':r['accepted_conditional_ideal_budget'],
        'records':r['generated_record_count'],'paths':len(r['ledger']),
        'max_field_upper':max(v['field_error_upper']['outward_float_BU'][1] for v in r['ledger']),
        'max_power_upper':max(v['intensity_error_upper']['outward_float_BU'][1] for v in r['ports'].values()),
        'observation_sha256':r['observation_sha256']}
    assert all(hashlib.sha256(p.read_bytes()).hexdigest()==pins[str(p)] for p in paths)
    return {'task_id':'PHASE-OBSERVED-001-CODEX','timestamp_utc':datetime.now(timezone.utc).isoformat(),
        'tests':tests.testsRun,'test_output':stream.getvalue(),'seconds':time.monotonic()-started,
        'matching_synthetic':summary(matched),'displaced_synthetic':summary(shifted),
        'code_sha256':pins,'native_promotion_allowed':False,'observation_execution_authenticated':False,
        'initial_failure_retained': {'tests':6, 'errors':2, 'exit_code':1,
            'reason':'new schema mistakenly required string terminal IDs; frozen CPU tracer uses nonnegative integers',
            'repair':'new opt-in validator matches existing integer ABI and rejects bool; no frozen code or thresholds changed'},
        'no_jev_aval':True,'scope':'CPU synthetic data consistency and conditional ideal budget; NO runtime/GPU/Bpy'}


if __name__=='__main__':print(json.dumps(audit(),indent=2))
