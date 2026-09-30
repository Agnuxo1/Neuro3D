import unittest
from exp005_history_generated_export_cpu_audit import audit,fixture


class GeneratedExportCPU(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.report=audit()

    def test_three_optical_controls_and_four_invalid_readbacks(self):
        self.assertEqual(len(self.report['cases']),4);self.assertEqual(len(self.report['negatives']),4)
        for case in self.report['cases']:
            result=case['result'];self.assertFalse(result['bpy_execution_certified'])
            self.assertFalse(result['native_backend_received_paths'])
            self.assertEqual(result['generated_history']['nearest_queries'],9)
            self.assertLess(result['export_checks']['analytic_field_error'],1e-13)

    def test_fresh_ids_follow_added_face_without_reusing_fixture_rows(self):
        original=self.report['cases'][0]['result']['generated_history']['records']
        changed=self.report['cases'][3]['result']['generated_history']['records']
        self.assertEqual(len(changed),13)
        self.assertEqual(original[9]['primitive_id'],10)
        self.assertEqual(changed[9]['primitive_id'],11)
        self.assertNotEqual(original[0]['snapshot_sha256'],changed[0]['snapshot_sha256'])
        _,old_rows=fixture();self.assertNotEqual(changed,old_rows)

    def test_negative_reason_is_retained_not_silenced(self):
        reasons={r['case']:r['reason'] for r in self.report['negatives']}
        self.assertIn('evaluated readback',reasons['unchecked'])
        self.assertIn('save/reopen readback mismatch',reasons['reopen_change'])
        self.assertIn('fixture-to-evaluated-scene mismatch',reasons['same_side_phase_change'])
        self.assertIn('coherence groups mismatch',reasons['coherence_change'])


if __name__=='__main__':unittest.main()
