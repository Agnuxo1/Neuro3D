import copy
import os
from pathlib import Path
import unittest
from fractions import Fraction
from exp005_departure_replay_audit import load_frozen, replay
from exp005_interval_audit import Interval
REPO_ROOT = Path(__file__).resolve().parents[2]
NEURO3D_COGNITION = Path(os.environ.get("NEURO3D_COGNITION_DIR", REPO_ROOT / ".cognition"))

INPUT = NEURO3D_COGNITION / 'neuro3d/exp005_self_hit_cpu_20260930_0804.json'


class DepartureReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.retained = load_frozen(INPUT)
        cls.original = copy.deepcopy(cls.retained)
        cls.result = replay(cls.retained)

    def test_complete_retained_world_local_coverage_and_immutability(self):
        self.assertEqual(len(self.result['rows']), 24)
        self.assertEqual({(r['case'], r['frame']) for r in self.result['rows']},
            {(i, frame) for i in range(12) for frame in ('world', 'local')})
        self.assertEqual(self.retained, self.original)

    def test_nonzero_departures_never_receive_exact_witness(self):
        rejected = 0
        for row in self.result['rows']:
            exact = row['exact_signed_parameters']
            if exact is None or exact['t'][0] != 0:
                self.assertEqual(row['outcome'], 'rejected'); rejected += 1
        self.assertGreater(rejected, 0)

    def test_exact_parameters_inside_cpu_intervals_when_det_is_resolved(self):
        for row in self.result['rows']:
            interval = row['interval_parameters']; exact = row['exact_signed_parameters']
            if interval['status'] == 'uncertain_determinant' or exact is None: continue
            for key, pair in exact.items():
                self.assertTrue(Interval(*interval['bounds'][key]).contains(Fraction(*pair)))

    def test_invalid_retained_case_count_is_not_silently_partial(self):
        altered = copy.deepcopy(self.retained); altered['retained_same_triangle_adversaries'].pop()
        with self.assertRaises(ValueError): replay(altered)

    def test_changed_saved_query_rejected_before_new_diagnostics(self):
        altered = copy.deepcopy(self.retained)
        altered['retained_same_triangle_adversaries'][0]['world_query']['point_BU'][0] += 1.
        with self.assertRaises(ValueError): replay(altered)


if __name__ == '__main__': unittest.main()
