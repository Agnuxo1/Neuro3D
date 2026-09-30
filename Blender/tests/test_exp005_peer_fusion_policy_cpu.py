"""Expected numerical failures remain failures, even when regression tests pass."""
import io
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'Blender/benchmarks/capacity_audit'))
from exp005_peer_fusion_policy_cpu import audit, SMALL


class FusionPolicyCPU(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.result = audit()

    def rows(self, policy):
        return [r for r in self.result['cases'] if r['policy_name'] == policy]

    def test_independent_complete_two_source_reference(self):
        for ref in self.result['references']:
            self.assertEqual(len(ref['records']), 26)
            self.assertEqual(len(ref['reference']['ledger']), 8)
            for port in ref['reference']['ports'].values():
                self.assertEqual(set(port['groups']), {'s', 's2'})

    def test_legacy_failure_not_hidden(self):
        for row in self.rows('fixed')[:2]:
            small = next(e for e in row['errors'] if e['lambda_BU'] == SMALL)
            self.assertFalse(small['global_gate_1e4'])

    def test_auto_per_scene_global_repair_both_orders_only(self):
        for row in self.rows('auto_per_scene'):
            self.assertEqual(row['status'], 'accepted')
            self.assertEqual([p['lambda'] for p in row['policy']['per_scene']], row['lambdas_BU'])
            for e in row['errors']:
                self.assertTrue(e['global_gate_1e4'])
                if e['lambda_BU'] == SMALL: self.assertTrue(e['strict_gate_1e8'])
                else: self.assertFalse(e['strict_gate_1e8'])

    def test_strict_rejects_entire_mixed_batch_before_geometry(self):
        rows = self.rows('auto_strict_per_scene')
        for row in rows[:2]:
            self.assertEqual(row['status'], 'rejected')
            self.assertEqual(row['nearest_calls'], 0)
            self.assertFalse(row['fields_emitted'])
        self.assertEqual(rows[2]['status'], 'accepted')
        self.assertTrue(rows[2]['errors'][0]['strict_gate_1e8'])

    def test_cpu_scope(self):
        self.assertEqual(self.result['threads'], 1)
        for k in ('CUDA_initialized', 'GPU_executed', 'Bpy_executed', 'native_promotion_allowed'):
            self.assertFalse(self.result[k])


if __name__ == '__main__':
    stream = io.StringIO()
    test = unittest.TextTestRunner(stream=stream).run(unittest.defaultTestLoader.loadTestsFromTestCase(FusionPolicyCPU))
    report = FusionPolicyCPU.result
    report.update(tests=test.testsRun, tests_successful=test.wasSuccessful(), test_output=stream.getvalue(),
                  test_failures=len(test.failures), test_errors=len(test.errors))
    print(json.dumps(report, indent=2, allow_nan=False))
    sys.exit(0 if test.wasSuccessful() else 1)
