"""CPU readiness for raw-scene GPU pilot, no runtime certification."""
import unittest
from exp005_nearest_runtime import raw_cases, require_status
from exp005_triangle_oracle import trace_scene
from frontier_inputs import pack_frontier


class NearestRuntimeTests(unittest.TestCase):
    def test_frozen_counts_and_raw_triangle_abi(self):
        rows = list(raw_cases())
        self.assertEqual(len(rows), 21)
        self.assertEqual(len(set(r[0] for r in rows)), 21)
        self.assertEqual(sum(r[2] == 2 for r in rows), 12)
        self.assertEqual(sum(r[2] == 0 for r in rows), 8)
        self.assertEqual(sum(r[2] == 1 for r in rows), 1)
        for _, snapshot, _ in rows:
            batch = pack_frontier(snapshot)
            self.assertLessEqual(batch.geometry.triangle_count, 8)
            self.assertEqual(len(batch.ports), 1)

    def test_CE3_and_miss_against_independent_oracle(self):
        for label, snapshot, expected in raw_cases():
            if label.startswith('CE3_') or label == 'miss':
                with self.assertRaisesRegex(ValueError, 'ambiguous' if expected == 2 else 'lost ray'):
                    trace_scene(snapshot, max_rays=4)
            elif expected == 0:
                oracle = trace_scene(snapshot, max_rays=4)
                self.assertEqual(oracle['rays'], 2)
                self.assertEqual(len(oracle['paths']), 1)

    def test_status_gate_rejects_false_flag_or_partial_fields(self):
        valid = {'valid': True, 'ports': {'D': {}}, 'errors': {},
                 'work': {'status': 0, 'total_casts': 2, 'total_terminal_paths': 1}}
        require_status(valid, 0)
        with self.assertRaises(ValueError): require_status(valid, 2)
        aborted = {'valid': False, 'ports': {}, 'errors': {'D': 'ambiguous geometry'},
                   'work': {'status': 2, 'total_casts': 1, 'total_terminal_paths': 0}}
        require_status(aborted, 2)
        aborted['ports'] = {'D': {'field_reim': [1, 0]}}
        with self.assertRaises(ValueError): require_status(aborted, 2)


if __name__ == '__main__': unittest.main()
