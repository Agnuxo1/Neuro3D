"""Issue a fresh bounded first-hit job and acquire its exclusive gpuq turn.

Run this launcher directly; gpuq must be the guard's immediate parent.
Inputs and numerical criteria remain the original 2026-10-07 preregistration.
"""
import argparse
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from Blender.benchmarks.capacity_audit import robust_first_hit_gpu_guard_v1 as guard
from Blender.tests import robust_first_hit_native_v1 as native


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--host-budget-mib", type=int, default=2048,
                        choices=(1024, 1280, 1536, 2048))
    parser.add_argument("--ram-free-gib", type=float, default=9.0)
    args = parser.parse_args()
    out = args.out_dir.resolve()
    out.mkdir(parents=True, exist_ok=False)
    manifest = ROOT / "Docs/validation/robust-first-hit-2026-10-07/inputs01/input_manifest.json"
    expected = "1ba451212cc136442ea34a1ec9a7cefd44fdf366211f28813590f21b732ba800"
    if native.sha(manifest) != expected:
        raise ValueError("preregistered manifest changed")
    inputs = native.read_json(manifest)
    native.validate_job(inputs)
    dependencies = [Path(native.__file__), manifest, Path(__file__),
        ROOT / "Blender/benchmarks/capacity_audit/scene_hilo_gpu_v1.py",
        ROOT / "Blender/benchmarks/capacity_audit/scene_hilo_transport_v1.py",
        ROOT / "Blender/benchmarks/capacity_audit/oblique_exact_scalar_hilo32_CPU_v1.py",
        ROOT / "Blender/shaders/scene_hilo_transport_v1.glsl",
        native.SHADER, native.SIGNED512,
        ROOT / "Blender/tests/exp005_blender_gpu.py",
        ROOT / "Blender/tests/robust_first_hit_raw_gl_v1.py",
        ROOT / "Docs/ROBUST_FIRST_HIT_NATIVE_PLAN_2026-10-07.md",
        *(native.pinned_packet_path(case) for case in inputs["cases"]),
        *guard.critical_paths()]
    gpu = subprocess.run([str(guard.SMI), "--query-gpu=uuid", "--format=csv,noheader"],
                         check=True, capture_output=True, text=True).stdout.strip().splitlines()
    if len(gpu) != 1:
        raise ValueError("single declared GPU required")
    now = datetime.now(timezone.utc)
    source_archive = out / "source"
    for path in dependencies:
        try:
            relative = path.resolve().relative_to(ROOT)
        except ValueError:
            continue
        target = source_archive / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(path.read_bytes())
    job = {
        "schema": "scene-hilo-gpu-job-v1", "job_id": str(uuid.uuid4()),
        "authorization_context": "User 2026-10-08 authorizes sequential Neuro3D scientific closure and GPU. Run original 13 cases / 20 queries after the CPU-verified packet path fix; no numerical criteria changed.",
        "gpu_uuid": gpu[0], "issued_utc": now.isoformat(),
        "deadline_utc": (now + timedelta(seconds=590)).isoformat(),
        "worker": str(Path(native.__file__).resolve()),
        "input_manifest": str(manifest), "input_manifest_sha256": expected,
        "worker_report": str(out / "worker.json"),
        "pins": {str(path.resolve()): guard.sha_file(path) for path in dependencies},
        "host_budget_bytes": args.host_budget_mib * 2**20,
        "device_budget_bytes": 2 * guard.GIB,
        "timeout_seconds": 100, "cleanup_seconds": 10,
    }
    job_path = out / "job.json"
    guard.atomic_json(job_path, job)
    command = [sys.executable, str(guard.QUEUE), "run", "--name", job["job_id"],
               "--vram", "2", "--ram", str(args.ram_free_gib),
               "--max-wait", "4", "--cwd", str(ROOT),
               "--", sys.executable, "-I", "-B", str(Path(guard.__file__).resolve()),
               "--manifest", str(job_path), "--receipt", str(out / "guard.json")]
    result = subprocess.run(command, capture_output=True)
    # Retain bytes: gpuq's Windows stderr can use the system code page.
    (out / "guard_stdout.txt").write_bytes(result.stdout)
    (out / "guard_stderr.txt").write_bytes(result.stderr)
    guard.atomic_json(out / "launch.json", {
        "schema": "neuro3d.first_hit.guarded_launch.v1", "returncode": result.returncode,
        "job_id": job["job_id"], "pin_count": len(job["pins"]),
        "manifest_sha256": expected,
    })
    print(json.dumps({"returncode": result.returncode, "out": str(out),
                      "job_id": job["job_id"]}))
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
