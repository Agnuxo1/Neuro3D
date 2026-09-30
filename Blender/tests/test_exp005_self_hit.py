import copy
import unittest
from exp005_self_hit_audit import audit, query, TRIALS, T_MIN_BU


class SelfHitAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit()

    def test_moderate_control_has_no_same_triangle_returns(self):
        control = self.report['profiles'][0]
        self.assertEqual(control['world_valid'], TRIALS)
        self.assertEqual(control['local_valid'], TRIALS)
        self.assertEqual(control['world_same_hits'], 0)
        self.assertEqual(control['local_same_hits'], 0)

    def test_local_translation_is_not_a_general_self_hit_fix(self):
        adversary = self.report['profiles'][1]
        self.assertEqual(adversary['world_valid'], TRIALS)
        self.assertEqual(adversary['local_valid'], TRIALS)
        self.assertGreater(adversary['world_same_hits'], 0)
        self.assertGreater(adversary['local_same_hits'], 0)

    def test_retained_query_replays_without_peer_execution(self):
        retained = self.report['retained_same_triangle_adversaries']
        self.assertEqual(len(retained), 12)
        for row in retained:
            world = query(row['record'])
            local = query(row['record'], local=True)
            self.assertEqual(world, row['world_query'])
            self.assertEqual(local, row['local_query'])
            self.assertGreater(world['same_triangle_self_hit_BU'], T_MIN_BU)

    def test_query_does_not_mutate_input_mesh_or_ray(self):
        record = self.report['retained_same_triangle_adversaries'][0]['record']
        before = copy.deepcopy(record)
        query(record)
        query(record, local=True)
        self.assertEqual(record, before)


if __name__ == '__main__': unittest.main()
