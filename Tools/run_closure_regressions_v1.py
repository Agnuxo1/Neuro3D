"""Run an explicit CPU selection in isolated processes, preserving every log.

No historical fixture, source pin or scientific acceptance state is rewritten.
The diagnostic mode includes historical tests and is not a production gate.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
SELECTED = ["test_governance_consistency", "test_coherent_state_graph_v1",
            "test_state_graph_enclosure_v1", "test_surface_union_interior_v1",
            "test_robust_first_hit_exact_v1", "test_affine_geometry_network_v1",
            "test_escala_modos", "test_verificar_hashes"]


def category(log: str, code: int | None) -> str:
    if code is None:
        return "DEADLINE"
    if code == 0:
        return "PASS"
    if "sealed_dependency_identity" in log:
        return "HISTORICAL_SEALED_IDENTITY"
    if ".cognition" in log and ("FileNotFoundError" in log or "missing" in log.lower()):
        return "EXTERNAL_COGNITION_FIXTURE"
    if "ModuleNotFoundError" in log:
        return "DEPENDENCY_UNAVAILABLE"
    if "FileNotFoundError" in log:
        return "MISSING_FILE"
    if "set_num_interop_threads" in log:
        return "TORCH_PROCESS_CONFIGURATION"
    if re.search(r"pin mismatch|sha256|hash mismatch|dependency.*identity", log, re.I):
        return "FROZEN_PIN_OR_RECEIPT"
    if "AssertionError" in log:
        return "ASSERTION_FAILURE"
    return "EXECUTION_ERROR"


def run(out: Path, diagnostic=False, timeout=90) -> dict:
    out.mkdir(parents=True, exist_ok=False)
    env = dict(os.environ, PYTHONNOUSERSITE="1", PYTHONDONTWRITEBYTECODE="1",
               OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1", MKL_NUM_THREADS="1",
               PYTHONUTF8="1", PYTHONPATH=str(ROOT), TEMP=str(out), TMP=str(out))
    # A clean reproduction cannot silently consume the station's private fixtures.
    env.pop("NEURO3D_COGNITION_DIR", None)
    if diagnostic:
        modules = sorted(p.stem for p in (ROOT / "Blender/tests").glob("test_*.py"))
        selections = [("historical-diagnostic", modules, ROOT)]
    else:
        selections = [("normal", SELECTED, ROOT), ("reverse", list(reversed(SELECTED)), ROOT),
                      ("foreign-cwd", SELECTED, out)]
    records = []
    for order, modules, cwd in selections:
        for module in modules:
            command = [sys.executable, "-m", "unittest", "Blender.tests." + module, "-v"]
            start = time.monotonic()
            name = order + "-" + module + ".txt"
            try:
                result = subprocess.run(command, cwd=cwd, env=env, capture_output=True,
                                        timeout=timeout, encoding="utf-8", errors="replace")
                log, code = result.stdout + result.stderr, result.returncode
            except subprocess.TimeoutExpired as exc:
                log = (exc.stdout or b"").decode("utf-8", "replace") + (exc.stderr or b"").decode("utf-8", "replace")
                code = None
            (out / name).write_text(log, encoding="utf-8", newline="\n")
            count = re.search(r"Ran (\d+) tests?", log)
            record = {"selection": order, "module": module, "command": command,
                      "cwd": str(cwd), "exit_code": code, "seconds": time.monotonic()-start,
                      "tests": int(count[1]) if count else None,
                      "category": category(log, code), "log": name,
                      "log_sha256": hashlib.sha256((out/name).read_bytes()).hexdigest()}
            records.append(record)
            print(json.dumps({k: record[k] for k in ("selection", "module", "category", "tests")}), flush=True)
    versions = {}
    for package in ("numpy", "scipy", "scikit-learn", "mpmath", "psutil", "torch"):
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = None
    report = {"schema": "neuro3d.closure.regressions.v1", "utc": datetime.now(timezone.utc).isoformat(),
              "python": sys.version, "versions": versions, "records": records,
              "diagnostic": diagnostic, "all_pass": all(x["category"] == "PASS" and x["tests"] for x in records),
              "scope": "Selected software regression only; no complete-project or physical validation"}
    (out/"report.json").write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--diagnostic", action="store_true")
    parser.add_argument("--timeout", type=float, default=90)
    args = parser.parse_args()
    report = run(args.out.resolve(), args.diagnostic, args.timeout)
    raise SystemExit(0 if report["all_pass"] else 2)
