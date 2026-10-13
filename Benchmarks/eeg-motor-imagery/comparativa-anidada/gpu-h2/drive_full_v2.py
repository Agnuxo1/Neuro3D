"""Submit the planned subjects of EXP-006-EEGNET-GPU-H2-20261013-001 to the gpuq FIFO queue,
one small ticket per subject, strictly sequentially, applying the 3-hour budget rule of
PROFILE-EEGNET-GPU-H2.md section 3 (execution time only; queue waiting is not counted).
"""
from __future__ import annotations
import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
GPUQ = "D:/PROJECTS/.cognition/gpu_queue/gpuq.py"


def executed_seconds(out: Path) -> dict:
    log = out / "timing.jsonl"
    if not log.exists():
        return {}
    rows = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines() if line.strip()]
    return {r["subject"]: r["seconds"] for r in rows if not r["pilot"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--projection", type=Path, required=True)
    parser.add_argument("--data", required=True)
    parser.add_argument("--optical-raw", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--journal", type=Path, required=True)
    args = parser.parse_args()
    projection = json.loads(args.projection.read_text(encoding="utf-8"))
    budget = projection["budget_hours"] * 3600
    cost = projection["projected_seconds_per_subject"]
    for sid in projection["plan_subjects"]:
        done = executed_seconds(args.out)
        if sid in done:
            continue
        elapsed = sum(done.values())
        entry = {"subject": sid, "utc_submit": datetime.now(timezone.utc).isoformat(), "elapsed_exec_s": elapsed,
                 "projected_s": cost[sid]}
        if projection["plan_label"] == "partial" and elapsed + cost[sid] > budget:
            entry["action"] = "STOP_BUDGET"
            with args.journal.open("a", encoding="utf-8") as j:
                j.write(json.dumps(entry) + "\n")
            break
        command = [sys.executable, GPUQ, "run", "--name", f"neuro3d:eegnet-h2-{sid}", "--vram", "3", "--ram", "3", "--",
                   sys.executable, str(HERE / "run_nested_eegnet_gpu_v2.py"), "--data", args.data,
                   "--optical-raw", args.optical_raw, "--out", str(args.out), "--subjects", sid,
                   "--require-cuda", "--deadline-seconds", "5400"]
        started = time.monotonic()
        code = subprocess.call(command)
        entry.update(utc_end=datetime.now(timezone.utc).isoformat(), ticket_wall_s=time.monotonic() - started,
                     exit_code=code, exec_s=executed_seconds(args.out).get(sid))
        with args.journal.open("a", encoding="utf-8") as j:
            j.write(json.dumps(entry) + "\n")
        print(json.dumps(entry), flush=True)
        if code != 0:
            print(json.dumps({"stop": "TICKET_FAILED", "subject": sid}), flush=True)
            break


if __name__ == "__main__":
    main()
