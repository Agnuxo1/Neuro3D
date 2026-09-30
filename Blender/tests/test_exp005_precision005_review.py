import unittest
from exp005_precision005_review_audit import audit


class Precision005ReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.report = audit()

    def test_four_frame_cases_match_reported_peer_values(self):
        self.assertEqual(len(self.report['frames']), 4)
        for row in self.report['frames']:
            self.assertTrue(all(value <= 1e-12 for values in row['peer_numeric_error_delta'].values() for value in values.values()))

    def test_distant_cluster_fails_frozen_budget_while_near_control_passes(self):
        for row in self.report['frames']:
            error = max(row['own']['abi_vs_raw_world'].values())
            if row['lambda_BU'] == 1e-6 and row['separation_BU'] > 1e5:
                self.assertGreater(error, self.report['field_tolerance_unchanged'])
            else: self.assertLessEqual(error, self.report['field_tolerance_unchanged'])

    def test_selfhit_classification_reproduces_but_numeric_parity_is_false(self):
        for row in self.report['selfhit_queries']:
            hit = row['own']['same_triangle_self_hit_BU']
            if row['label'] == 'failing' and row['frame'] == 'world':
                self.assertIsNotNone(hit); self.assertGreater(hit, 1e-9)
                self.assertAlmostEqual(hit, 5.119168804116071e-9, delta=1e-12)
                self.assertGreater(row['peer_same_triangle_t_delta_BU'], 1e-12)
            else: self.assertIsNone(hit)

    def test_folded_other_triangle_return_not_lost(self):
        hits = self.report['folded_query']['other_triangle_hits_not_classified']
        self.assertEqual([x['triangle'] for x in hits], [1])
        self.assertAlmostEqual(hits[0]['distance_BU'], .6288047980451352, delta=1e-12)

    def test_origin_depends_on_source_order_without_native_claim(self):
        order = self.report['source_order']
        self.assertNotEqual(order['forward']['metadata']['origin_BU'], order['reverse']['metadata']['origin_BU'])
        self.assertGreater(max(order['forward']['abi_vs_raw_world'].values()), self.report['field_tolerance_unchanged'])


if __name__ == '__main__': unittest.main()
