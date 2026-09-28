"""Guarded EXP-001 Blender CPU runner. Do not run without fresh user approval.

One CPU affinity, below-normal priority, 45 s and 1.5 GiB per Blender phase.
No render or GPU command is issued. Existing artifact directories are never
overwritten or deleted; a failure leaves all evidence intact.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

import psutil

from mz_exp001_plan import controls

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "oracle"))
from readback_reconstruct import compare as compare_readback  # noqa: E402

MAX_RSS = 1_500 * 2**20
MIN_FREE = 2_500 * 2**20
PREFLIGHT_FREE = 4_000 * 2**20
TIMEOUT_SECONDS = 45
MARKER = "NEURO3D_MZ_EXP001 "


def _run(blender: Path, script: Path, input_blend: Path | None,
         output_blend: Path, mode: str, case: str) -> dict:
    if psutil.virtual_memory().available < PREFLIGHT_FREE:
        raise RuntimeError(f"{case}/{mode}: available RAM below 4 GiB before phase")
    command = [str(blender), "-b", "--factory-startup", "--disable-autoexec",
               "-t", "1", "-noaudio"]
    if input_blend is not None:
        command.append(str(input_blend))
    command += ["--python-exit-code", "3", "--python", str(script), "--",
                mode, case, str(output_blend)]
    log_path = output_blend.with_suffix(f".{mode}.log")
    with log_path.open("x", encoding="utf-8", errors="replace") as log:
        process = subprocess.Popen(
            command, stdout=log, stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NO_WINDOW | subprocess.BELOW_NORMAL_PRIORITY_CLASS,
        )
        tracked = psutil.Process(process.pid)
        try:
            allowed = psutil.Process().cpu_affinity()
            if not allowed:
                raise RuntimeError("No allowed CPUs available for Blender")
            tracked.cpu_affinity([allowed[0]])
        except Exception:
            process.kill()
            process.wait(timeout=5)
            raise
        started = time.monotonic()
        peak = 0
        stop_reason = None
        while process.poll() is None:
            try:
                peak = max(peak, tracked.memory_info().rss)
            except psutil.NoSuchProcess:
                break
            if peak > MAX_RSS:
                stop_reason = "Blender exceeded 1.5 GiB RSS"
            elif psutil.virtual_memory().available < MIN_FREE:
                stop_reason = "Host available RAM fell below 2.5 GiB"
            elif time.monotonic() - started > TIMEOUT_SECONDS:
                stop_reason = "Blender exceeded the 45-second phase limit"
            if stop_reason:
                process.kill()
                break
            time.sleep(0.1)
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired as exc:
            process.kill()
            raise RuntimeError(f"{case}/{mode}: child did not exit after kill; log={log_path}") from exc
    output = log_path.read_text(encoding="utf-8", errors="replace")
    records = [json.loads(line[len(MARKER):]) for line in output.splitlines()
               if line.startswith(MARKER)]
    if stop_reason or process.returncode != 0 or len(records) != 1:
        raise RuntimeError(f"{case}/{mode}: {stop_reason or 'phase failed'}; "
                           f"exit={process.returncode}; log={log_path}")
    return {**records[0], "peak_rss_mib": round(peak / 2**20, 1), "log": str(log_path)}


def _verify_readback(artifact: Path) -> dict:
    readback_path = artifact.with_suffix(".readback.json")
    record = json.loads(readback_path.read_text(encoding="utf-8"))
    result = compare_readback(record, tolerance=1e-12)
    if not result["passes"]:
        raise AssertionError(f"Independent CPU readback failed: {readback_path}: {result}")
    return {"readback": str(readback_path), "readback_worst_abs_diff": result["worst_abs_diff"]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--blender", required=True, type=Path)
    parser.add_argument("--artifacts", required=True, type=Path)
    parser.add_argument("--authorized-by-user", action="store_true",
                        help="Only use after the user explicitly authorizes EXP-001 Blender CPU")
    args = parser.parse_args()
    if not args.authorized_by_user:
        raise SystemExit("EXP-001 Blender is blocked until the user authorizes this run")
    if not args.blender.is_file():
        raise SystemExit("Blender executable not found")
    if args.artifacts.exists():
        raise SystemExit("Artifact directory already exists; choose a new one")
    if psutil.virtual_memory().available < PREFLIGHT_FREE:
        raise SystemExit("Available RAM below the 4 GiB preflight guard")
    args.artifacts.mkdir(parents=True, exist_ok=False)
    script = Path(__file__).with_name("blender_mz_exp001.py")
    base = args.artifacts / "A.blend"
    records = []
    failure = None
    report_path = args.artifacts / "report.json"
    try:
        records.append(_run(args.blender, script, None, base, "init", "A"))
        verified = _run(args.blender, script, base, base, "verify", "A")
        records.append({**verified, **_verify_readback(base)})
        for case in controls()[1:]:
            artifact = args.artifacts / f"{case.name}.blend"
            records.append(_run(args.blender, script, base, artifact, "edit", case.name))
            verified = _run(args.blender, script, artifact, artifact, "verify", case.name)
            records.append({**verified, **_verify_readback(artifact)})
    except BaseException as exc:
        failure = {"type": type(exc).__name__, "detail": str(exc)}
        raise
    finally:
        report = {"experiment": "EXP-001", "blender": str(args.blender),
                  "controls": records, "runtime_verified": failure is None,
                  "failure": failure}
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"report": str(report_path), "phases": len(records)}))


if __name__ == "__main__":
    main()
