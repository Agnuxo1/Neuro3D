"""New CPU negative controls: historical inventory is NOT GPU admission evidence.

No collector, SDK, queue operation, workload, legacy suite or native backend runs.
Uses the frozen pure HOST policy without modifying its contract or thresholds.
"""
import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Blender/benchmarks/capacity_audit"))
import gpu_job_resource_policy_HOST_v1 as policy

ID = "GPU-POLICY-HOST-INVENTORY-NEG-CPU-001"
RECEIPT = ROOT / "coordinacion/respuestas/MEGA-GEOMETRY-HOST-READINESS-READONLY-001-CODEX.json"
RECEIPT_SHA = "9131102a2b72d5796eef9b0587c56251d52099edc37f7508c50544a2f8b0d76c"
NOW = 1791220000  # Injected synthetic clock, not current telemetry or job deadline.
RESULTS = []


def fixtures():
    plan = dict(job_id="SYNTHETIC-INVENTORY-NEG-NO-RESERVATION", kernel="CONTROL",
                cells=1024, bytes_per_cell=1024, host_fixed_bytes=64,
                host_temporary_bytes=2**20, host_margin_bytes=2**20,
                device_fixed_bytes=128, device_temporary_bytes=2**20,
                device_margin_bytes=2**20, pilot=True, timeout_s=120,
                issued_utc_s=NOW-1, deadline_utc_s=NOW+180)
    snap = dict(job_id=plan["job_id"], sampled_utc_s=NOW,
                ram_available_bytes=8*policy.GIB, device_used_bytes=2*policy.GIB,
                device_total_bytes=24*policy.GIB, temperature_millic=29000,
                elapsed_s=0, gpuq_job_id=plan["job_id"],
                claude_job_id=plan["job_id"], process_scan_job_id=plan["job_id"],
                **{key: True for key in policy.BOOL_KEYS})
    return plan, snap


class Tests(unittest.TestCase):
    def check(self, name, plan, snap, expected, reason=None):
        before = copy.deepcopy((plan, snap))
        out = policy.evaluate(plan, snap, now_utc_s=NOW, model=policy.MODEL)
        self.assertEqual(out["status"], expected, name)
        if reason:
            self.assertIn(reason, out["reasons"], name)
        for key in ("GPU_job_admission", "GPU_executed", "telemetry_authenticated",
                    "reservation_authenticated", "guard_implemented",
                    "near_limit_headroom_proved"):
            self.assertIs(out[key], False, name)
        # Invalid non-finite controls are compared via stable repr; NaN != NaN.
        self.assertEqual(repr((plan, snap)), repr(before), name)
        RESULTS.append(dict(name=name, result=out))
        return out

    def test_historical_inventory_cannot_be_promoted(self):
        raw = RECEIPT.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), RECEIPT_SHA)
        saved = json.loads(raw)
        plan, snap = fixtures()
        obs = saved["observation"]
        self.check("whole_receipt_not_policy_INPUT", plan, saved, "STOP",
                   "invalid_or_missing_INPUT")
        self.check("whole_observation_not_policy_INPUT", plan, obs, "STOP",
                   "invalid_or_missing_INPUT")
        # Even deliberately forged check booleans yield only arithmetic fit,
        # NEVER authenticated telemetry/reservation or a launch permit.
        self.check("synthetic_declared_fit_not_permission", plan, snap,
                   "CONDITIONAL_POLICY_FIT")
        stale = copy.deepcopy(snap)
        stale["sampled_utc_s"] = NOW - 6
        self.check("historical_timestamp_must_not_be_refreshed", plan, stale,
                   "STOP", "telemetry_stale_or_future")
        self.assertTrue(saved["interpretation"]["WDDM_per_process_memory_unknown"])
        self.assertFalse(obs["native_cluster_capability_queried"])
        self.assertFalse(obs["GPU_admission"])

    def test_every_integer_field_rejects_unknown_and_coercion(self):
        plan, snap = fixtures()
        plan_ints = sorted(policy.PLAN_KEYS - {"job_id", "kernel", "pilot"})
        snap_ints = sorted(policy.SNAP_KEYS - policy.BOOL_KEYS -
                          {"job_id", "gpuq_job_id", "claude_job_id", "process_scan_job_id"})
        bad = (None, True, 1.0, float("nan"), float("inf"), -1, 2**63, "[N/A]")
        for side, keys in (("plan", plan_ints), ("snapshot", snap_ints)):
            for key in keys:
                for index, value in enumerate(bad):
                    a, b = copy.deepcopy(plan), copy.deepcopy(snap)
                    (a if side == "plan" else b)[key] = value
                    out = self.check(f"{side}:{key}:invalid{index}", a, b,
                                     "STOP", "invalid_or_missing_INPUT")
                    self.assertIsNone(out["budget"])

    def test_unknown_boolean_checks_never_become_true(self):
        for key in sorted(policy.BOOL_KEYS):
            for value in (None, 1, "true", "UNKNOWN"):
                plan, snap = fixtures()
                snap[key] = value
                self.check(f"{key}:nonbool:{repr(value)}", plan, snap,
                           "STOP", "invalid_or_missing_INPUT")

    def test_unavailable_memory_is_not_zero(self):
        saved = json.loads(RECEIPT.read_text(encoding="utf-8"))
        for index, app in enumerate(saved["observation"]["gpu_apps"]):
            self.assertEqual(app["used_gpu_memory_MiB"], "[N/A]")
            plan, snap = fixtures()
            snap["device_used_bytes"] = app["used_gpu_memory_MiB"]
            self.check(f"WDDM_unavailable_{index}_not_zero", plan, snap,
                       "STOP", "invalid_or_missing_INPUT")

    def test_half_billion_cells_do_not_fit_historical_host_budget(self):
        saved = json.loads(RECEIPT.read_text(encoding="utf-8"))
        plan, snap = fixtures()
        plan["cells"] = 500_000_000  # Cells under THIS policy, not triangles or neurons.
        snap["ram_available_bytes"] = saved["observation"]["ram_available_bytes"]
        out = self.check("500M_policy_cells_HOST_reject", plan, snap,
                         "STOP", "ram_floor_after_budget")
        self.assertIn("device_18GiB_cap", out["reasons"])
        self.assertIn("physical_device_memory", out["reasons"])
        self.assertEqual(out["budget"]["cell_bytes"], 512_000_000_000)
        self.assertLess(out["budget"]["ram_after_budget_bytes"], 0)


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(Tests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print(json.dumps(dict(id=ID, status="PASS" if result.wasSuccessful() else "FAIL",
                         tests=result.testsRun, records=len(RESULTS), controls=RESULTS,
                         historical_receipt_sha256=RECEIPT_SHA,
                         CPU_synthetic_only=True, GPU_job_admission=False,
                         native_precision_or_cluster_capability_certified=False),
                     sort_keys=True, allow_nan=False))
    raise SystemExit(0 if result.wasSuccessful() else 1)
