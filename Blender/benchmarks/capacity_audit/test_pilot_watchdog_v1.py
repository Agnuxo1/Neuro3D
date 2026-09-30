from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import psutil
import pilot_watchdog_v1 as guard


def audit():
    results = {}
    good = {'ram_available_bytes': 9*2**30, 'device_used_bytes': 2**30, 'temperature_c':40}
    with tempfile.TemporaryDirectory(prefix='cpu-watchdog-',dir='D:/PROJECTS/.cognition/neuro3d') as temporary:
        directory = Path(temporary)
        def run(label, code="import time;time.sleep(.08)", **changes):
            options = dict(envelope=directory/(label+'.json'),
                deadline=datetime.now(timezone.utc)+timedelta(seconds=30),timeout=2,
                host_budget=2**30,device_budget=2**30,admit=lambda:None,sample=lambda:good)
            options.update(changes)
            result = guard.supervise([sys.executable,'-B','-c',code], **options)
            assert json.loads(options['envelope'].read_text()) == json.loads(json.dumps(result))
            if result['child_started']:assert not psutil.pid_exists(result['child_pid'])
            results[label]=result
            return result
        run('cpu_success')
        run('cpu_nonzero', code='import sys,time;time.sleep(.08);sys.exit(3)')
        run('cpu_timeout', code='import time;time.sleep(2)',timeout=.12)
        run('default_admission_reject',admit=guard.reject_admission)
        run('low_ram_reject',sample=lambda:dict(good,ram_available_bytes=4*2**30))
        run('missing_telemetry',sample=lambda:{})
        run('nan_telemetry',sample=lambda:dict(good,temperature_c=float('nan')))
        run('invalid_timeout',timeout=float('nan'))
        admissions=[0]
        def second_admission_fails():
            admissions[0]+=1
            if admissions[0]==2:raise ValueError('synthetic lost reservation')
        run('second_admission_failure',admit=second_admission_fails)
        reads=[0]
        def breaks_after_launch():
            reads[0]+=1
            if reads[0]>1:raise OSError('synthetic telemetry failure')
            return good
        run('telemetry_failure_after_launch',code='import time;time.sleep(2)',sample=breaks_after_launch)
        clock_calls=[0];anchor=datetime.now(timezone.utc);deadline=anchor+timedelta(seconds=30)
        def late_clock():
            clock_calls[0]+=1
            return deadline if clock_calls[0]>=4 else anchor
        run('deadline_failure_after_launch',code='import time;time.sleep(2)',deadline=deadline,now=late_clock)
        clock_calls=[0];anchor=datetime.now(timezone.utc);deadline=anchor+timedelta(seconds=30)
        original_close=guard.close_tracked
        def close_then_late(child,known):
            out=original_close(child,known);clock_calls[0]=1;return out
        with patch.object(guard,'close_tracked',close_then_late):
            run('late_finalization',deadline=deadline,
                now=lambda:deadline if clock_calls[0] else anchor)
        existing=directory/'cpu_success.json';before=existing.read_bytes()
        with patch.object(guard.subprocess,'Popen',side_effect=AssertionError('must not launch')):
            try:run('existing_envelope',envelope=existing)
            except FileExistsError:pass
            else:raise AssertionError('existing envelope accepted')
        assert existing.read_bytes()==before
    return {'scope':'real tiny CPU children; synthetic admission/resources, no Blender/GPU/queue mutation',
            'cases':results,'existing_envelope_rejected':True}


class PilotWatchdogCPU(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.report=audit()

    def test_real_cpu_child_success_and_nonzero_exit(self):
        cases=self.report['cases']
        self.assertEqual(cases['cpu_success']['status'],'completed')
        self.assertEqual(cases['cpu_success']['exit_code'],0)
        self.assertEqual(cases['cpu_nonzero']['status'],'child_failed')
        self.assertEqual(cases['cpu_nonzero']['exit_code'],3)
        self.assertFalse(cases['cpu_success']['full_tree_containment_certified'])

    def test_deadline_timeout_and_failure_close_only_tracked_children(self):
        for label in ('cpu_timeout','telemetry_failure_after_launch','deadline_failure_after_launch','late_finalization'):
            with self.subTest(label=label):
                result=self.report['cases'][label]
                self.assertEqual(result['status'],'failed_closed')
                self.assertTrue(result['tracked_children_closed'])
        self.assertIn('late_finalization',self.report['cases']['late_finalization']['reasons'])

    def test_no_launch_on_admission_resource_or_output_failure(self):
        for label in ('default_admission_reject','low_ram_reject','missing_telemetry',
                      'nan_telemetry','invalid_timeout','second_admission_failure'):
            self.assertFalse(self.report['cases'][label]['child_started'])
        self.assertTrue(self.report['existing_envelope_rejected'])


if __name__=='__main__':unittest.main()
