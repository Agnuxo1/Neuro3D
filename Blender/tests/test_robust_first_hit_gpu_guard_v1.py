import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from Blender.benchmarks.capacity_audit import robust_first_hit_gpu_guard_v1 as guard


class WorkerGateTests(unittest.TestCase):
    def fixture(self, directory):
        root = Path(directory)
        manifest = {
            "schema": "neuro3d.robust_first_hit.native_job.v1",
            "expected_backend": "OPENGL",
            "expected_renderer_contains": "RTX 3090",
            "limits": {"max_triangles": 64, "max_dispatches": 20},
            "cases": [{
                "case_id": "fixture",
                "input_class": "synthetic_adversarial",
                "packet_path": "unused.json",
                "packet_sha256": "0" * 64,
                "queries": [{
                    "source_index": i,
                    "previous_primitive": None,
                    "departure_event": None,
                    "expected": {},
                } for i in range(20)],
            }],
        }
        manifest_path = root / "input.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        input_sha = guard.sha_file(manifest_path)
        records = [{
            "case_id": "fixture", "query_index": i, "source_index": i,
            "previous_primitive": None, "departure_event": None,
            "input_echo_hex": "00", "result_hex": "00",
        } for i in range(20)]
        digest = hashlib.sha256()
        for row in records:
            digest.update(bytes.fromhex(row["input_echo_hex"]))
            digest.update(bytes.fromhex(row["result_hex"]))
        report = {
            "schema": "neuro3d.robust_first_hit.native_report.v1",
            "status": "PASS", "verification_passed": True,
            "job_id": "job-robust-0001", "input_manifest_sha256": input_sha,
            "native_gpu_executed": True, "backend": "OPENGL", "background": False,
            "vendor": "NVIDIA Corporation", "renderer": "NVIDIA GeForce RTX 3090",
            "gpu_dispatch_count": 20, "completed_readbacks": 20,
            "gpu_readback_records": records, "gpu_readback_sha256": digest.hexdigest(),
        }
        report_path = root / "worker.json"
        report_path.write_text(json.dumps(report), encoding="utf-8")
        plan = guard.Plan(
            "job-robust-0001", "auth", "GPU-00000000-0000-0000-0000-000000000000",
            datetime.now(timezone.utc), datetime.now(timezone.utc),
            root / "worker.py", manifest_path, input_sha, report_path, (report_path,), {},
        )
        return plan, report, report_path

    def test_complete_ordered_worker_is_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            plan, report, path = self.fixture(tmp)
            result = guard.worker_gate(path, plan)
            self.assertEqual(result["gpu_dispatch_count"], 20)
            self.assertTrue(result["native_gpu_execution_verified"])

    def test_missing_readback_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            plan, report, path = self.fixture(tmp)
            report["gpu_readback_records"].pop()
            report["completed_readbacks"] = 19
            report["gpu_dispatch_count"] = 19
            path.write_text(json.dumps(report), encoding="utf-8")
            with self.assertRaises(guard.Rejected):
                guard.worker_gate(path, plan)

    def test_reordered_readback_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            plan, report, path = self.fixture(tmp)
            report["gpu_readback_records"][0], report["gpu_readback_records"][1] = (
                report["gpu_readback_records"][1], report["gpu_readback_records"][0])
            digest = hashlib.sha256()
            for row in report["gpu_readback_records"]:
                digest.update(bytes.fromhex(row["input_echo_hex"]))
                digest.update(bytes.fromhex(row["result_hex"]))
            report["gpu_readback_sha256"] = digest.hexdigest()
            path.write_text(json.dumps(report), encoding="utf-8")
            with self.assertRaises(guard.Rejected):
                guard.worker_gate(path, plan)

    def test_malformed_hex_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            plan, report, path = self.fixture(tmp)
            report["gpu_readback_records"][0]["result_hex"] = "zz"
            path.write_text(json.dumps(report), encoding="utf-8")
            with self.assertRaises(guard.Rejected):
                guard.worker_gate(path, plan)


if __name__ == "__main__":
    unittest.main(verbosity=2)
