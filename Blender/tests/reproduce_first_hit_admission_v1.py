"""Retain CPU regression evidence without loading Blender or submitting GPU work."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from Blender.tests import robust_first_hit_native_v1 as fixed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--original-worker", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise ValueError("fresh evidence output required")
    manifest = ROOT / "Docs/validation/robust-first-hit-2026-10-07/inputs01/input_manifest.json"
    job = fixed.read_json(manifest)
    spec = importlib.util.spec_from_file_location("original_first_hit_worker", args.original_worker)
    original = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(original)
    before = {"accepted": False, "error": None}
    try:
        original.validate_job(job)
        before["accepted"] = True
    except ValueError as error:
        before["error"] = type(error).__name__ + ": " + str(error)
    tests = subprocess.run([sys.executable, "-B", "-X", "utf8", "-m", "unittest",
        "Blender.tests.test_robust_first_hit_native_inputs_v1",
        "Blender.tests.test_robust_first_hit_exact_v1",
        "Blender.tests.test_robust_first_hit_gpu_guard_v1", "-v"],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    evidence = {
        "schema": "neuro3d.first_hit.admission_fix.cpu.v1",
        "status": "PASS" if before["error"] == "ValueError: pinned packet" and
            fixed.validate_job(job) == 20 and tests.returncode == 0 else "FAIL",
        "gpu_executed": False,
        "manifest_sha256": fixed.sha(manifest),
        "cases": len(job["cases"]), "queries_after": fixed.validate_job(job),
        "original_worker_sha256": fixed.sha(args.original_worker),
        "fixed_worker_sha256": fixed.sha(Path(fixed.__file__)),
        "before": before, "tests_exit_code": tests.returncode,
        "test_output": tests.stdout + tests.stderr,
        "packet_sha256": {case["case_id"]: fixed.sha(fixed.pinned_packet_path(case))
                          for case in job["cases"]},
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: evidence[key] for key in
                     ("status", "gpu_executed", "cases", "queries_after", "before", "tests_exit_code")}))
    return 0 if evidence["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
