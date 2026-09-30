from datetime import datetime,timedelta,timezone
import unittest
from exp005_history_runtime_cpu_audit import audit
from exp005_history_generated_runtime import deadline_check


class GeneratedRuntimeCPU(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.report=audit()

    def test_three_fake_save_reopen_cases_have_generated_histories(self):
        control=self.report['control'];events=control['events']
        self.assertEqual(sum(e['event']=='save' for e in events),3)
        self.assertEqual(sum(e['event']=='reopen' for e in events),3)
        self.assertEqual(sum(e['event']=='deadline_check' for e in events),14)
        for c in control['result']['cases']:
            self.assertEqual(len(c['result']['generated_history']['records']),13)
            self.assertLess(c['result']['export_checks']['analytic_field_error'],1e-13)
            self.assertFalse(c['result']['bpy_execution_certified'])

    def test_changed_reopen_and_save_failure_stop_without_success_result(self):
        changed=self.report['reopen_changed'];failed=self.report['save_failed']
        self.assertIn('readback mismatch',changed['error']);self.assertNotIn('result',changed)
        self.assertIn('synthetic save failure',failed['error']);self.assertNotIn('result',failed)
        self.assertEqual(sum(e['event']=='save' for e in changed['events']),1)
        self.assertEqual(sum(e['event']=='reopen' for e in failed['events']),0)

    def test_utc_deadline_no_reset_or_unbounded_child(self):
        now=datetime(2026,9,30,14,0,tzinfo=timezone.utc)
        deadline_check(now+timedelta(seconds=110),now)
        for d in (now,now-timedelta(seconds=1),now+timedelta(seconds=121),now.replace(tzinfo=None)):
            with self.assertRaises(ValueError):deadline_check(d,now)


if __name__=='__main__':unittest.main()
