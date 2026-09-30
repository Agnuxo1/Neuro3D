import unittest
from exp005_complete_peer_review import audit,verify_peer


class CompletePeerReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=audit()

    def test_retained_inputs_and_results_pinned(self):
        data,checked=verify_peer();self.assertEqual(len(data['results']),12);self.assertEqual(len(checked),9)
        self.assertIn('NO_REFUTATION',data['status'])

    def test_own_replay_and_reindexed_control(self):
        probes={p['case']:p for p in self.report['own_probes']};self.assertEqual(len(probes),9)
        self.assertFalse(probes['duplicate_face_without_downstream_reindex']['accepted'])
        self.assertTrue(probes['duplicate_face_with_correct_global_ids']['accepted'])
        self.assertFalse(probes['subtree4_omitted']['accepted']);self.assertFalse(probes['whole_first_r_arm_omitted']['accepted'])

    def test_valid_remote_vs_invalid_domain(self):
        probes={p['case']:p for p in self.report['own_probes']}
        self.assertFalse(probes['remote_degenerate']['accepted'])
        result=probes['remote_valid_unreached_terminal']['result']
        self.assertEqual(len(result['terminal_ids']),4);self.assertFalse(result['native_exemption_allowed'])


if __name__=='__main__':unittest.main()
