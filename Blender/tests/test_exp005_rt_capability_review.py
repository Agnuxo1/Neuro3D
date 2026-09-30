import ast
import unittest
from exp005_rt_capability_review import audit, pure_function


class CapabilityReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit()

    def test_pinned_artifacts_and_valid_controls(self):
        self.assertEqual(len(self.report['input_sha256']), 8)
        self.assertEqual([r['T'] for r in self.report['valid_controls']], [2, 32])
        self.assertTrue(all(r['perfect_capture_pass'] for r in self.report['valid_controls']))

    def test_nonfinite_depth_position_accepted_by_peer(self):
        self.assertEqual(len(self.report['nonfinite_checker_cases']), 3)
        self.assertTrue(all(r['peer_pass'] for r in self.report['nonfinite_checker_cases']))
        self.assertTrue(self.report['numeric_bad_depth_rejected'])

    def test_unsafe_guard_inputs_accepted_by_peer(self):
        self.assertEqual(len(self.report['unsafe_guard_cases']), 7)
        self.assertTrue(all(not r['peer_blocked'] for r in self.report['unsafe_guard_cases']))
        self.assertTrue(self.report['positive_low_ram_rejected'])

    def test_no_launch_promotion(self):
        self.assertFalse(self.report['launch_approved'])
        self.assertFalse(self.report['native_or_rt_certified'])

    def test_ast_replay_rejects_writer_import_or_unknown_call(self):
        for src in ('def probe():\n open("anything", "w")', 'def probe():\n import os', 'def probe():\n run()'):
            with self.assertRaises(ValueError): pure_function(src, 'probe', {})


if __name__ == '__main__': unittest.main()
