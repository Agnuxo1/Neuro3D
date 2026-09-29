from datetime import datetime,timezone
import unittest
from resource_policy import preflight,GIB


class ResourcePolicyTests(unittest.TestCase):
    def case(self,**change):
        kw=dict(kind='mlp',width=32768,batch=256,device_used_bytes=1*GIB,
                ram_available_bytes=9*GIB,temperature_c=65,
                now_utc=datetime(2026,9,29,22,tzinfo=timezone.utc))
        kw.update(change); return preflight(**kw)

    def test_host_first_weights_rejected_before_allocation(self):
        r=self.case(direct_gpu_weights=False)
        self.assertIn('projected_free_host_memory_floor',r['reasons'])
        self.assertFalse(r['allowed'])

    def test_direct_gpu_still_accounts_for_full_device_and_buffers(self):
        self.assertTrue(self.case()['allowed'])
        self.assertFalse(self.case(device_used_bytes=3*GIB)['allowed'])
        self.assertFalse(self.case(width=40960)['allowed'])

    def test_biases_counted_and_matvec_not_four_layers(self):
        self.assertEqual(self.case(width=64)['parameters'],4*(64*64+64))
        self.assertEqual(self.case(kind='matvec',width=64)['parameters'],64*64)

    def test_deadline_temperature_and_duration(self):
        self.assertFalse(self.case(temperature_c=81)['allowed'])
        self.assertFalse(self.case(job_seconds=601)['allowed'])
        late=datetime(2026,9,30,5,55,tzinfo=timezone.utc)
        self.assertFalse(self.case(now_utc=late)['allowed'])
        self.assertTrue(self.case(now_utc=late,job_seconds=120)['allowed'])

    def test_invalid_metadata(self):
        for bad in ({'width':True},{'ram_available_bytes':float('nan')},
                    {'now_utc':datetime(2026,9,29,22)}):
            with self.assertRaises(ValueError): self.case(**bad)


if __name__=='__main__': unittest.main()
