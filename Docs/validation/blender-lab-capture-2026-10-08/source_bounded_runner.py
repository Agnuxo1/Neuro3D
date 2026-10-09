"""Bounded CPU-only software check runner; never invokes an optical forward."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time

import psutil


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--script", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--scene", type=Path)
    parser.add_argument("--network", type=Path)
    args = parser.parse_args()
    root = Path("D:/PROJECTS/Neuro3D-Scientific-20261008")
    blender = Path("D:/TOOLS/Blender/blender-4.5.14-windows-x64/blender.exe")
    if args.out.exists():
        raise ValueError("fresh attempt directory required")
    if psutil.virtual_memory().available < 4_000 * 2**20:
        raise RuntimeError("4 GiB free host RAM guard")
    args.out.mkdir()
    sources = sorted((root / "Blender/blender_lab").glob("*.py")) + [args.script]
    pins = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    command = [str(blender), "-b", "--factory-startup", "--disable-autoexec", "-t", "1", "-noaudio"]
    if args.scene:
        command += [str(args.scene)]
    command += ["--python-exit-code", "3", "--python", str(args.script), "--"]
    if args.script.name == "export_scene_v1.py":
        command += ["--output", str(args.out / "capture.json")]
        if args.network:
            command += ["--network", str(args.network)]
    else:
        command += [str(args.out)]
    started = time.monotonic()
    stopped = None
    peak = 0
    with (args.out / "blender.log").open("w", encoding="utf-8") as log:
        process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NO_WINDOW | subprocess.BELOW_NORMAL_PRIORITY_CLASS)
        tracked = psutil.Process(process.pid)
        cpus = psutil.Process().cpu_affinity()
        if cpus:
            tracked.cpu_affinity([cpus[0]])
        while process.poll() is None:
            try:
                peak = max(peak, tracked.memory_info().rss)
            except psutil.NoSuchProcess:
                break
            if peak > 1_500 * 2**20:
                stopped = "1.5 GiB owned-process RSS guard"
            elif psutil.virtual_memory().available < 2_500 * 2**20:
                stopped = "2.5 GiB free host RAM guard"
            elif time.monotonic() - started > 90:
                stopped = "90 second software phase guard"
            if stopped:
                process.kill()
                break
            time.sleep(0.1)
        process.wait(timeout=5)
    unchanged = all(hashlib.sha256((root / path).read_bytes()).hexdigest() == value for path, value in pins.items())
    report = {"command": command, "exit_code": process.returncode, "stopped": stopped,
              "peak_rss_mib": peak / 2**20, "elapsed_seconds": time.monotonic() - started,
              "source_sha256": pins, "sources_unchanged": unchanged, "gpu_requested": False,
              "optical_forward_requested": False, "training_requested": False,
              "source_scene_sha256": hashlib.sha256(args.scene.read_bytes()).hexdigest() if args.scene else None}
    report["network_contract_sha256"] = hashlib.sha256(args.network.read_bytes()).hexdigest() if args.network else None
    (args.out / "runner.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report))
    if process.returncode or stopped or not unchanged:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
