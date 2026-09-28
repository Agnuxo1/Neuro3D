"""Bounded Windows runner for the real Blender CPU-only optical smoke check.

Uses one logical CPU, below-normal priority, a 45-second timeout per phase and
memory guards. It never asks Blender to render or dispatch GPU shaders.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

import psutil


MAX_RSS = 1_500 * 2**20
MIN_FREE = 2_500 * 2**20
TIMEOUT_SECONDS = 45


def run_phase(blender: Path, script: Path, artifact: Path, phase: str) -> dict:
    command = [
        str(blender), "-b", "--factory-startup", "--disable-autoexec",
        "-t", "1", "-noaudio",
    ]
    if phase == "reopen":
        command.append(str(artifact))
    command.extend([
        "--python-exit-code", "3", "--python", str(script), "--", phase, str(artifact),
    ])
    log_path = artifact.parent / f"blender-smoke-{phase}.log"
    with log_path.open("w", encoding="utf-8", errors="replace") as log:
        process = subprocess.Popen(
            command, stdout=log, stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NO_WINDOW | subprocess.BELOW_NORMAL_PRIORITY_CLASS,
        )
        tracked = psutil.Process(process.pid)
        allowed_cpus = psutil.Process().cpu_affinity()
        if allowed_cpus:
            tracked.cpu_affinity([allowed_cpus[0]])
        start = time.monotonic()
        peak_rss = 0
        stop_reason = None
        while process.poll() is None:
            try:
                peak_rss = max(peak_rss, tracked.memory_info().rss)
            except psutil.NoSuchProcess:
                break
            if peak_rss > MAX_RSS:
                stop_reason = "Blender exceeded the 1.5 GiB process guard"
            elif psutil.virtual_memory().available < MIN_FREE:
                stop_reason = "Host free RAM fell below 2.5 GiB"
            elif time.monotonic() - start > TIMEOUT_SECONDS:
                stop_reason = "Blender exceeded the 45-second phase timeout"
            if stop_reason:
                process.kill()
                break
            time.sleep(0.1)
        process.wait(timeout=5)
    output = log_path.read_text(encoding="utf-8", errors="replace")
    records = [json.loads(line.split("NEURO3D_SMOKE ", 1)[1])
               for line in output.splitlines() if line.startswith("NEURO3D_SMOKE ")]
    if stop_reason or process.returncode != 0 or len(records) != 1:
        raise RuntimeError(f"{phase}: {stop_reason or 'Blender failed'}; exit={process.returncode}; log={log_path}")
    return {**records[0], "peak_rss_mib": round(peak_rss / 2**20, 1), "log": str(log_path)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--blender", required=True, type=Path)
    parser.add_argument("--artifacts", required=True, type=Path)
    args = parser.parse_args()
    if not args.blender.is_file():
        raise SystemExit("Blender executable not found")
    if psutil.virtual_memory().available < 4_000 * 2**20:
        raise SystemExit("Available RAM below the 4 GiB preflight guard")
    args.artifacts.mkdir(parents=True, exist_ok=True)
    blend = args.artifacts / "neuro3d-optical-circuit.blend"
    script = Path(__file__).with_name("blender_runtime_smoke.py")
    results = [run_phase(args.blender, script, blend, "create")]
    results.append(run_phase(args.blender, script, blend, "reopen"))
    print(json.dumps({"blender": str(args.blender), "phases": results}, ensure_ascii=False))


if __name__ == "__main__":
    main()
