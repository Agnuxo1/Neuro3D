"""Focused Windows CPU containment tests; no GPU, telemetry or queue writes."""
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT / "Blender/benchmarks/capacity_audit"))
import windows_job_tree_control_CPU_v1 as control
RECORDS = []

def new(profile="success", **changes):
    args = dict(deadline=datetime.now(timezone.utc)+timedelta(seconds=30),
        timeout_s=3,model=control.MODEL)
    args.update(changes)
    return control.CPUControl(profile,**args)

class TreeContainment(unittest.TestCase):
    def checked(self, report):
        RECORDS.append(report)
        self.assertTrue(report["cleanup_confirmed"],report)
        self.assertFalse(report["foreign_processes_touched"])
        self.assertFalse(report["GPU_job_admission"])
        self.assertFalse(report["GPU_executed"])
        self.assertFalse(report["runtime_GPU_guard"])
        self.assertFalse(report["full_GPU_tree_containment_certified"])

    def test_real_root_success_and_nonzero(self):
        for profile,code in (("success",0),("exit_error",7)):
            with self.subTest(profile=profile):
                with new(profile) as child:
                    result=child.wait_root()
                    self.assertEqual(code,result["root_exit_code"])
                    self.assertTrue(result["assigned_before_resume"])
                    self.assertTrue(result["resumed"])
                self.checked(child.view())
                self.assertEqual(0,child.view()["accounting_after_close"]["active_processes"])
                self.assertEqual(child.close(),child.close())

    def test_parent_exit_does_not_lose_unobserved_descendant(self):
        with new("orphan") as child:
            result=child.wait_root()
            self.assertEqual(0,result["root_exit_code"])
            counts=child.accounting()
            self.assertEqual(2,counts["total_processes"])
            self.assertEqual(1,counts["active_processes"])  # Parent gone; leaf deliberately remains.
        result=child.view()
        self.assertEqual(1,result["accounting_before_close"]["active_processes"])
        self.assertEqual(0,result["accounting_after_close"]["active_processes"])
        self.checked(result)

    def test_kernel_kill_on_last_close_when_inner_supervisor_exits(self):
        # Outer job measures all members; inner supervisor os._exit bypasses Python cleanup.
        with new("supervisor_exit",timeout_s=5) as outer:
            result=outer.wait_root()
            self.assertEqual(19,result["root_exit_code"],result)
            counts=outer.accounting()
            self.assertEqual(3,counts["total_processes"],counts)
            self.assertEqual(0,counts["active_processes"],counts)
        self.checked(outer.view())

    def test_timeout_cleans_owned_tree(self):
        child=new("block",timeout_s=.5)
        with self.assertRaises(control.ControlFailure) as caught:
            child.wait_root()
        result=caught.exception.report
        self.assertEqual("WAIT_FAILED_CLOSED",result["status"])
        self.assertEqual("TimeoutError",result["error_type"])
        self.assertEqual(0,result["accounting_after_close"]["active_processes"])
        self.checked(result)

    def test_interrupt_closes_owned_job_without_suppressing_interrupt(self):
        with self.assertRaises(KeyboardInterrupt):
            with new("block") as child:
                raise KeyboardInterrupt
        self.checked(child.view())
        self.assertEqual(0,child.view()["accounting_after_close"]["active_processes"])

    def test_assign_and_resume_fail_before_worker_runs(self):
        for method in ("assign","resume"):
            with self.subTest(method=method):
                with patch.object(control.WinAPI,method,side_effect=OSError("injected CPU OS failure")):
                    with self.assertRaises(control.ControlFailure) as caught:
                        new("block")
                report=caught.exception.report
                self.assertTrue(report["created_suspended"])
                self.assertFalse(report["resumed"])
                self.assertEqual(method=="resume",report["assigned_before_resume"])
                self.assertEqual("START_FAILED_CLOSED",report["status"])
                self.checked(report)

    def test_configure_job_failure_prevents_process_creation(self):
        with patch.object(control.WinAPI,"limit",side_effect=OSError("injected limit failure")):
            with self.assertRaises(control.ControlFailure) as caught:
                new()
        report=caught.exception.report
        self.assertFalse(report["created_suspended"])
        self.checked(report)

    def test_interrupt_immediately_after_create_retains_owned_handles(self):
        original = control.WinAPI.create_suspended
        def create_then_interrupt(api, command, env, info):
            original(api, command, env, info)
            raise KeyboardInterrupt
        child = control.CPUControl.__new__(control.CPUControl)
        with patch.object(control.WinAPI,"create_suspended",create_then_interrupt):
            with self.assertRaises(KeyboardInterrupt):
                child.__init__("block",deadline=datetime.now(timezone.utc)+timedelta(seconds=30),
                    timeout_s=3,model=control.MODEL)
        report=child.view()
        self.assertTrue(report["created_suspended"])
        self.assertFalse(report["assigned_before_resume"])
        self.assertFalse(report["resumed"])
        self.checked(report)

    def test_cleanup_error_is_never_pass(self):
        child=new("block")
        # TerminateJobObject error means cleanup cannot be certified, even though
        # closing the last job handle still performs kernel kill-on-close.
        with patch.object(control.WinAPI,"terminate_job",side_effect=OSError("injected terminate failure")):
            result=child.close()
        RECORDS.append(result)
        self.assertEqual("CLEANUP_UNCONFIRMED",result["status"])
        self.assertFalse(result["cleanup_confirmed"])
        self.assertFalse(result["GPU_job_admission"])

    def test_invalid_inputs_pins_and_ram_never_start(self):
        inputs=[{"model":"gpu"}, {"timeout_s":True},{"timeout_s":0},{"timeout_s":6},
            {"timeout_s":float("nan")},{"deadline":datetime.now()},
            {"deadline":datetime.now(timezone.utc)-timedelta(seconds=1)},
            {"deadline":datetime.now(timezone.utc)+timedelta(seconds=61)}]
        for args in inputs:
            with self.subTest(args=str(args)):
                with self.assertRaises(control.ControlFailure) as caught:
                    new(**args)
                self.assertFalse(caught.exception.report["created_suspended"])
                self.checked(caught.exception.report)
        with self.assertRaises(control.ControlFailure) as caught:
            new("GPU_OR_ARBITRARY_COMMAND")
        self.checked(caught.exception.report)
        with patch.object(control,"WORKER_SHA","0"*64):
            with self.assertRaises(control.ControlFailure) as caught:
                new()
        self.assertFalse(caught.exception.report["created_suspended"])
        self.checked(caught.exception.report)
        with patch.object(control.WinAPI,"memory",return_value=4*control.GIB+control.HOST_CONTROL_BUDGET_BYTES-1):
            with self.assertRaises(control.ControlFailure) as caught:
                new()
        self.assertFalse(caught.exception.report["created_suspended"])
        self.checked(caught.exception.report)

if __name__=="__main__":
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(TreeContainment)
    result=unittest.TextTestRunner(stream=sys.stderr,verbosity=2).run(suite)
    print(json.dumps({"model":control.MODEL,"tests_run":result.testsRun,
        "tests_success":result.wasSuccessful(),"records":RECORDS,
        "GPU_executed":False,"queue_mutations":0,"foreign_process_kills":0,
        "geometry_evaluations":0,"runtime_GPU_guard":False,
        "full_GPU_tree_containment_certified":False,
        "structure_sizes":{"basic":control.ctypes.sizeof(control.BasicLimits),
            "extended":control.ctypes.sizeof(control.ExtendedLimits),
            "accounting":control.ctypes.sizeof(control.Accounting)},
        "worker_sha256":hashlib.sha256(control.WORKER.read_bytes()).hexdigest()},
        sort_keys=True,allow_nan=False))
    raise SystemExit(0 if result.wasSuccessful() else 1)
