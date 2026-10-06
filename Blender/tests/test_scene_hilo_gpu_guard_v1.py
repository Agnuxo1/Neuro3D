"""CPU-only regression of the new guard; never calls Blender, gpuq or nvidia-smi.

python -I -B -m unittest discover -s Blender/tests -p test_scene_hilo_gpu_guard_v1.py -v
Real Windows cases contain only private Python roots/descendants, <=5 s each,
one processor and a 256 MiB job commit cap. Synthetic executions are explicitly
CPU_CONTROL_PASS, never GPU admission or a native result.
"""
from datetime import datetime, timedelta, timezone
from dataclasses import replace
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import types
import unittest
from unittest import mock

import psutil

HERE = Path(__file__).resolve()
TARGET = HERE.parents[1] / "benchmarks/capacity_audit/scene_hilo_gpu_guard_v1.py"
if not TARGET.is_file():  # Local scratch development copy.
    TARGET = HERE.with_name("scene_hilo_gpu_guard_v1.py")
specification = importlib.util.spec_from_file_location("scene_hilo_gpu_guard_test_target", TARGET)
guard = importlib.util.module_from_spec(specification)
sys.modules[specification.name] = guard
specification.loader.exec_module(guard)

NOW = datetime(2026, 10, 6, 22, 0, tzinfo=timezone.utc)
UUID = "GPU-12345678-1234-1234-1234-123456789abc"


def plan_at(directory):
    directory = Path(directory)
    source = directory / "pinned-input.txt"
    source.write_text(json.dumps({"schema": "neuro3d.scene_hilo.native_job.v1",
        "cases": [{"case_id": "cpu_case"}], "limits": {"max_dispatches": 2}}), encoding="utf-8")
    return guard.Plan(
        "point04-CPU-TEST-12345678", "Synthetic test of current point-4 guard; no GPU permission",
        UUID, NOW, NOW + timedelta(seconds=180), source, source, guard.sha_file(source),
        directory / "worker.json", (directory / "worker.json",),
        {guard.key(source): guard.sha_file(source)})


def sample():
    return {"sampled_utc": NOW.isoformat(), "gpu_count": 1, "gpu_uuid": UUID,
            "name": "NVIDIA GeForce RTX 3090", "driver": "CPU synthetic",
            "device_used_bytes": guard.GIB, "device_total_bytes": 24 * guard.GIB,
            "ram_available_bytes": 8 * guard.GIB, "temperature_c": 30,
            "utilization_percent": 0}


def worker_report(plan):
    raw = b"\x01\x02\x03\x04\x05\x06\x07\x08"
    return {"status": "PASS", "verification_passed": True, "job_id": plan.job_id,
            "input_manifest_sha256": plan.input_sha, "native_gpu_executed": True,
            "backend": "OPENGL", "vendor": "NVIDIA synthetic", "renderer": "RTX 3090 synthetic",
            "background": False, "gpu_dispatch_count": 2,
            "gpu_readback_records": [{"case_id": "cpu_case", "zero_low": mode,
                "input_echo_hex": raw[:4].hex(), "computed_rows_hex": raw[4:].hex()}
                for mode in (False, True)],
            "gpu_readback_sha256": hashlib.sha256(raw + raw).hexdigest()}


class FakeLease:
    def __init__(self, scenario):
        self.calls, self.scenario = 0, scenario

    def check(self):
        self.calls += 1
        if self.scenario == "lease_loss" and self.calls >= 4:
            raise guard.Rejected("synthetic lease lost")
        return {"synthetic": True}


class FakeRuntime:
    synthetic = True

    def __init__(self, plan, directory, scenario="success"):
        self.plan, self.scenario, self.directory = plan, scenario, directory
        self.lease, self.job = FakeLease(scenario), self
        self.events, self.samples, self.closed = [], 0, False
        self.spawned = False

    def start(self):
        pass

    def sample(self, seconds):
        self.samples += 1
        if self.scenario == "telemetry_error" and self.samples == 2:
            raise guard.Rejected("synthetic unavailable telemetry")
        if self.scenario == "telemetry_error_post_exit" and self.samples == 3:
            raise guard.Rejected("synthetic unavailable post-exit telemetry")
        return sample()

    def spawn(self, check):
        check()
        self.spawned = True
        self.events.append({"synthetic_CPU_process": True})
        self.plan.worker_report.write_text(json.dumps(worker_report(self.plan)), encoding="utf-8")
        if self.scenario == "mutated_pin":
            self.plan.input_manifest.write_text("changed after entry\n", encoding="utf-8")
        return {"info": types.SimpleNamespace(pid=123)}

    def poll(self, _):
        return 7 if self.scenario == "nonzero" else 0

    def close(self, seconds):
        self.closed = True
        return {"cleanup_confirmed": self.scenario != "cleanup_error",
                "accounting_after_close": {"active_processes": 0 if self.scenario != "cleanup_error" else 1}}


class PureControls(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="neuro3d-hilo-guard-CPU-")
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.plan = plan_at(self.directory)

    def test_policy_boundaries_and_invalid_types(self):
        boundary = sample()
        boundary.update(ram_available_bytes=6 * guard.GIB, device_used_bytes=16 * guard.GIB,
                        temperature_c=80)
        guard.resource_check(boundary, self.plan, NOW)
        violations = [
            ("ram_available_bytes", 6 * guard.GIB - 1),
            ("device_used_bytes", 16 * guard.GIB + 1),
            ("device_total_bytes", 2 * guard.GIB),
            ("temperature_c", 80.0001), ("temperature_c", float("nan")),
            ("utilization_percent", float("inf")), ("ram_available_bytes", True),
            ("device_used_bytes", "N/A"), ("gpu_count", 2), ("gpu_count", True),
            ("gpu_uuid", "GPU-wrong"), ("sampled_utc", (NOW - timedelta(seconds=6)).isoformat()),
            ("sampled_utc", (NOW + timedelta(seconds=1)).isoformat()),
        ]
        for field, value in violations:
            with self.subTest(field=field, value=repr(value)):
                bad = dict(boundary)
                bad[field] = value
                with self.assertRaises((guard.Rejected, KeyError, TypeError)):
                    guard.resource_check(bad, self.plan, NOW)
        self.assertEqual(self.plan.host_budget, 2 * guard.GIB)
        self.assertEqual(self.plan.device_budget, 2 * guard.GIB)

    def test_single_gpu_telemetry_parsing_rejects_unknown_and_multiple(self):
        line = UUID + ", NVIDIA GeForce RTX 3090, 580.00, 1024, 24576, 30, 0"
        parsed = guard.parse_telemetry(line, 8 * guard.GIB, NOW)
        guard.resource_check(parsed, self.plan, NOW)
        for invalid in ("", line + "\n" + line, line.replace("1024", "N/A"),
                        line.replace("30, 0", "NaN, 0")):
            with self.subTest(text=invalid[:45]):
                with self.assertRaises(guard.Rejected):
                    parsed = guard.parse_telemetry(invalid, 8 * guard.GIB, NOW)
                    guard.resource_check(parsed, self.plan, NOW)

    def test_manifest_deadline_budgets_and_closed_schema(self):
        manifest = self.directory / "manifest.json"
        data = {"schema": "scene-hilo-gpu-job-v1", "job_id": self.plan.job_id,
                "authorization_context": "CPU-only synthetic manifest control",
                "gpu_uuid": UUID, "issued_utc": NOW.isoformat(),
                "deadline_utc": (NOW + timedelta(seconds=180)).isoformat(),
                "worker": str(self.plan.worker), "input_manifest": str(self.plan.input_manifest),
                "input_manifest_sha256": self.plan.input_sha,
                "worker_report": str(self.plan.worker_report), "pins": self.plan.pins}
        with mock.patch.object(guard, "critical_paths", return_value=[]):
            manifest.write_text(json.dumps(data), encoding="utf-8")
            valid = guard.load_plan(manifest, NOW)
            self.assertEqual(valid.host_budget, 2 * guard.GIB)
            for field, value in (("deadline_utc", (NOW + timedelta(seconds=159)).isoformat()),
                                 ("issued_utc", (NOW - timedelta(seconds=301)).isoformat()),
                                 ("host_budget_bytes", 2 * guard.GIB + 1),
                                 ("device_budget_bytes", True), ("timeout_seconds", 101),
                                 ("cleanup_seconds", 11), ("undeclared_field", True)):
                changed = dict(data)
                changed[field] = value
                manifest.write_text(json.dumps(changed), encoding="utf-8")
                with self.subTest(field=field):
                    with self.assertRaises(guard.Rejected):
                        guard.load_plan(manifest, NOW)

    def test_lease_parent_child_binding_and_loss(self):
        parent = {"pid": 10, "ctime": 100.125}
        child = {"pid": 11, "ctime": 101.125, "ppid": 10, "command": ["python", "guard.py"]}
        valid = {"name": self.plan.job_id, "pid": 10, "ctime": 100.125,
                 "child_pid": 11, "child_ctime": 101.125, "cmd": child["command"]}
        accepted = guard.lease_record(valid, self.plan, parent, child)
        self.assertEqual(accepted["child_pid"], 11)
        for field, value in (("name", "old-job"), ("pid", 12), ("ctime", 100.126),
                             ("child_pid", 12), ("child_ctime", 101.126),
                             ("cmd", ["python", "other.py"]), ("pid", True)):
            bad = dict(valid)
            bad[field] = value
            with self.subTest(field=field):
                with self.assertRaises(guard.Rejected):
                    guard.lease_record(bad, self.plan, parent, child)
        with self.assertRaises(guard.Rejected):
            guard.lease_record(valid, self.plan, parent, dict(child, ppid=12))

    def test_worker_evidence_hash_and_binding(self):
        good = worker_report(self.plan)
        self.plan.worker_report.write_text(json.dumps(good), encoding="utf-8")
        accepted = guard.worker_gate(self.plan.worker_report, self.plan)
        self.assertEqual(accepted["gpu_readback_bytes"], 16)
        for field, value in (("job_id", "old-job"), ("input_manifest_sha256", "0" * 64),
                             ("verification_passed", 1), ("native_gpu_executed", False),
                             ("gpu_dispatch_count", True), ("background", True),
                             ("gpu_dispatch_count", 7), ("gpu_dispatch_count", 100000),
                             ("backend", "CPU"), ("gpu_readback_sha256", "0" * 64)):
            bad = dict(good)
            bad[field] = value
            self.plan.worker_report.write_text(json.dumps(bad), encoding="utf-8")
            with self.subTest(field=field):
                with self.assertRaises(guard.Rejected):
                    guard.worker_gate(self.plan.worker_report, self.plan)
        bad = dict(good, gpu_readback_records=[{"input_echo_hex": "xx", "computed_rows_hex": "00"}])
        self.plan.worker_report.write_text(json.dumps(bad), encoding="utf-8")
        with self.assertRaises(guard.Rejected):
            guard.worker_gate(self.plan.worker_report, self.plan)
        for rows in (good["gpu_readback_records"][:1], good["gpu_readback_records"][::-1],
                     good["gpu_readback_records"] * 2):
            changed = dict(good, gpu_readback_records=rows, gpu_dispatch_count=len(rows))
            self.plan.worker_report.write_text(json.dumps(changed), encoding="utf-8")
            with self.assertRaises(guard.Rejected):
                guard.worker_gate(self.plan.worker_report, self.plan)

    def run_scenario(self, scenario):
        recorded = []
        def factory(plan, directory):
            obj = FakeRuntime(plan, directory, scenario)
            recorded.append(obj)
            return obj
        result = guard.execute(self.plan, self.directory / "receipt.json", factory,
                               now=lambda: NOW, mono=lambda: 1.0, sleep=lambda _: None)
        self.assertFalse(result["native_gpu_execution_verified"])
        self.assertFalse(result["GPU_job_admission"])
        self.assertTrue(recorded[0].closed)
        self.assertEqual(json.loads((self.directory / "receipt.json").read_text())["status"],
                         result["status"])
        return result, recorded[0]

    def test_success_is_labelled_cpu_only(self):
        result, runtime = self.run_scenario("success")
        self.assertEqual(result["status"], "CPU_CONTROL_PASS")
        self.assertTrue(runtime.spawned)
        self.assertEqual(result["pins_entry"], result["pins_exit"])

    def test_lease_loss_closes_own_job(self):
        result, runtime = self.run_scenario("lease_loss")
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(runtime.spawned)
        self.assertIn("lease", result["failure"]["reason"])

    def test_telemetry_failure_after_rc0_is_not_success(self):
        result, _ = self.run_scenario("telemetry_error_post_exit")
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["worker_exit_code"], 0)
        self.assertIn("telemetry", result["failure"]["reason"])

    def test_telemetry_failure_during_work_closes_job(self):
        result, _ = self.run_scenario("telemetry_error")
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("telemetry", result["failure"]["reason"])

    def test_nonzero_exit_cleanup(self):
        result, _ = self.run_scenario("nonzero")
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["worker_exit_code"], 7)
        self.assertTrue(result["cleanup_confirmed"])

    def test_unconfirmed_cleanup_never_passes(self):
        result, _ = self.run_scenario("cleanup_error")
        self.assertEqual(result["status"], "FAIL")
        self.assertFalse(result["cleanup_confirmed"])

    def test_dependency_change_rejected_at_exit(self):
        result, _ = self.run_scenario("mutated_pin")
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("Dependency hash changed", result["failure"]["reason"])

    def test_stale_receipt_and_raw_output_are_not_reused(self):
        receipt = self.directory / "receipt.json"
        prior = b'{"status":"PASS","old":true}'
        receipt.write_bytes(prior)
        with self.assertRaises(FileExistsError):
            guard.execute(self.plan, receipt, lambda *_: self.fail("must not create runtime"))
        self.assertEqual(receipt.read_bytes(), prior)
        self.plan.worker_report.write_bytes(prior)
        result = guard.execute(self.plan, self.directory / "new.json",
                               lambda *_: self.fail("must not create runtime"),
                               now=lambda: NOW, mono=lambda: 1.0)
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(self.plan.worker_report.read_bytes(), prior)

    def test_late_rc0_and_expired_deadline_are_rejected(self):
        recorded = []
        def factory(plan, directory):
            obj = FakeRuntime(plan, directory)
            recorded.append(obj)
            return obj
        expired = replace(self.plan, deadline=NOW - timedelta(seconds=1))
        result = guard.execute(expired, self.directory / "expired.json", factory,
                               now=lambda: NOW, mono=lambda: 1.0)
        self.assertEqual(result["status"], "FAIL")
        self.assertFalse(recorded[0].spawned)
        self.assertTrue(recorded[0].closed)


@unittest.skipUnless(os.name == "nt", "Real containment requires Windows")
class RealOwnedProcessControls(unittest.TestCase):
    def setUp(self):
        if psutil.virtual_memory().available - 256 * 2**20 < 4 * guard.GIB:
            self.skipTest("Insufficient RAM for the bounded private CPU control")
        self.temporary = tempfile.TemporaryDirectory(prefix="neuro3d-hilo-job-CPU-")
        self.addCleanup(self.cleanup_temporary)
        self.directory = Path(self.temporary.name)
        self.job = guard.OwnedJob(256 * 2**20, self.directory)
        self.addCleanup(lambda: self.job.close(2))
        self.env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1",
                        MKL_NUM_THREADS="1", NUMEXPR_NUM_THREADS="1")

    def cleanup_temporary(self):
        # Windows can briefly retain a redirected stdio handle after process/job
        # termination has been confirmed. Require eventual release; never ignore
        # errors or weaken the kernel process/handle checks.
        deadline, retries = time.monotonic() + 1, 0
        while True:
            try:
                self.temporary.cleanup()
                break
            except PermissionError:
                if time.monotonic() >= deadline:
                    raise
                retries += 1
                time.sleep(.01)
        print("CPU_TEMP_RELEASE", self._testMethodName, "retry_count", retries, flush=True)

    def command(self, source):
        return [sys.executable, "-I", "-S", "-B", "-c", source]

    def wait_root(self, child):
        deadline = time.monotonic() + 2
        while self.job.poll(child) is None:
            self.assertLess(time.monotonic(), deadline, "CPU control root exceeded two seconds")
            time.sleep(.01)
        return self.job.poll(child)

    def test_suspended_assignment_stdio_and_rc7(self):
        child = self.job.spawn(self.command("print('private-CPU-control', flush=True); raise SystemExit(7)"),
                               self.env)
        self.assertEqual(self.wait_root(child), 7)
        self.assertIn("private-CPU-control", child["log"].read_text())
        self.assertTrue(child["event"]["created_suspended"])
        self.assertTrue(child["event"]["assigned_before_resume"])
        self.assertTrue(child["event"]["resumed"])
        closed = self.job.close(2)
        self.assertTrue(closed["cleanup_confirmed"])
        self.assertEqual(closed["accounting_after_close"]["active_processes"], 0)

    def test_orphan_descendant_is_contained_after_root_exit(self):
        code = "import subprocess,sys; subprocess.Popen([sys.executable,'-I','-S','-B','-c','import time;time.sleep(3)'])"
        child = self.job.spawn(self.command(code), self.env)
        self.assertEqual(self.wait_root(child), 0)
        self.assertGreaterEqual(self.job.accounting()["active_processes"], 1)
        closed = self.job.close(2)
        self.assertTrue(closed["cleanup_confirmed"])
        self.assertEqual(closed["accounting_after_close"]["active_processes"], 0)

    def test_interrupt_before_resume_does_not_run_the_child(self):
        marker = self.directory / "must-not-exist.txt"
        def interrupt():
            raise KeyboardInterrupt("CPU control before resume")
        with self.assertRaises(KeyboardInterrupt):
            self.job.spawn(self.command("open(" + repr(str(marker)) + ",'w').write('wrong')"),
                           self.env, interrupt)
        closed = self.job.close(2)
        self.assertTrue(closed["cleanup_confirmed"])
        self.assertFalse(marker.exists())
        self.assertFalse(self.job.events[-1]["resumed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
