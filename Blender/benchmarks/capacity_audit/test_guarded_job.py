from datetime import datetime,timedelta,timezone
import unittest
from guarded_job import violations,GIB


class GuardTests(unittest.TestCase):
    def setUp(self):
        self.now=datetime(2026,9,29,23,30,tzinfo=timezone.utc)
        self.sample={'ram_available_bytes':6*GIB,'device_used_bytes':GIB,'temperature_c':40}
    def check(self,**kwargs):
        return violations(self.sample,now=self.now,deadline=self.now+timedelta(hours=6),
                          elapsed=0,timeout=120,**kwargs)
    def test_safe_and_projected_ram(self):
        self.assertEqual(self.check(),[])
        self.assertIn('ram_floor',self.check(host_estimate=3*GIB))
    def test_projected_total_device_memory(self):
        self.assertIn('device_cap',self.check(device_estimate=18*GIB))
    def test_actual_caps(self):
        self.sample.update(ram_available_bytes=3*GIB,device_used_bytes=19*GIB,temperature_c=81)
        self.assertEqual(set(self.check()),{'ram_floor','device_cap','temperature_cap'})
    def test_deadline_and_timeout(self):
        r=violations(self.sample,now=self.now,deadline=self.now,elapsed=120,timeout=120)
        self.assertEqual(set(r),{'night_deadline','job_timeout'})
    def test_invalid_telemetry_and_policy(self):
        self.sample['temperature_c']=float('nan')
        with self.assertRaises(ValueError): self.check()
        with self.assertRaises(ValueError): violations({},now=self.now,deadline=self.now,elapsed=0,timeout=900)


if __name__=='__main__': unittest.main()
