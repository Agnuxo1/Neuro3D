"""Run only the byte-frozen captured pilot after verified operator registration.

Registration records are evidence data, never a substitute for an actual human
instruction or verified external registration. The operator must establish that
origin before invoking this command. No receipt is issued by this program.
"""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from Tools.bind_network_capture_v1 import read_json
from Tools.audit_captured_pilot_result_v1 import audit_result, need

PROTOCOL_SHA256 = "5d0cf372f2f66f043c2a219ba6a60f0182ced8a60039348d486ec163be736226"
PROTOCOL_COMMIT = "f22e7a1307e3a3b4c74a507463a0a8055d45fc04"
PROPOSAL_ID = "957514f2-a233-421f-aa04-50cccd063d97"
BASE = ROOT / "Docs/validation/captured-scalar-ingress-2026-10-08"


def file_sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_protocol(base=BASE):
    base = base.resolve()
    protocol, pin = read_json(base / "pilot_protocol_prepared.json", 65536)
    need(pin == PROTOCOL_SHA256 and protocol["proposal_id"] == PROPOSAL_ID, "frozen protocol identity mismatch")
    files = {}
    for row in protocol["input_files"].values():
        files[row["path"]] = row["sha256"]
    files.update(protocol["source_files"])
    for name, expected in files.items():
        path = (base / name).resolve()
        need(path.is_relative_to(base) and path.is_file() and file_sha(path) == expected, "frozen input/source mismatch: " + name)
    return protocol, files


def check_registration(record):
    need(isinstance(record, dict) and set(record) == {
        "schema", "kind", "proposal_id", "protocol_sha256", "protocol_commit", "approved",
        "evidence_origin", "evidence_reference", "preregId", "ipfsCid"}, "verified registration record required")
    need(record["schema"] == "optic_neuro_blender.pilot_registration.v1", "unknown registration schema")
    need(record["proposal_id"] == PROPOSAL_ID and record["protocol_sha256"] == PROTOCOL_SHA256 and
         record["protocol_commit"] == PROTOCOL_COMMIT, "registration must bind this frozen protocol")
    need(record["approved"] is True, "registration decision still pending")
    reference = record["evidence_reference"]
    need(isinstance(reference, str) and 0 < len(reference) <= 2048 and
         "TEST_ONLY" not in reference and "SYNTHETIC" not in reference, "actual verified evidence reference required")
    if record["kind"] == "HUMAN_GITHUB_EXCEPTION":
        need(record["evidence_origin"] == "DIRECT_HUMAN_USER_MESSAGE_VERIFIED_BY_OPERATOR" and
             record["preregId"] is None and record["ipfsCid"] is None,
             "explicit human GitHub exception must disclose absent external IDs")
    elif record["kind"] == "EXTERNAL_REGISTRATION":
        need(record["evidence_origin"] == "EXTERNAL_REGISTRY_RECEIPT_VERIFIED_BY_OPERATOR" and
             all(isinstance(record[key], str) and record[key] for key in ("preregId", "ipfsCid")),
             "verified external IDs required")
    else:
        raise ValueError("unsupported registration kind")
    return record


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--registration", type=Path)
    parser.add_argument("--preflight-only", action="store_true")
    args = parser.parse_args(argv)
    args.out.mkdir(exist_ok=False)
    report = {"schema": "optic_neuro_blender.captured_pilot_supervision.v1", "status": "NOT_EXECUTED",
        "proposal_id": PROPOSAL_ID, "protocol_sha256": PROTOCOL_SHA256, "protocol_commit": PROTOCOL_COMMIT,
        "preflight_only": args.preflight_only, "worker_started": False, "result_collected": False,
        "primary_metric": None, "gpu_requested": False, "field_certified": False,
        "physical_optics_certified": False, "registration_record_is_not_independent_proof": True,
        "python_version": sys.version, "platform": platform.platform(),
        "supervisor_source_sha256": file_sha(Path(__file__)),
        "auditor_source_sha256": file_sha(ROOT / "Tools/audit_captured_pilot_result_v1.py")}
    process = None
    return_code = 3
    try:
        protocol, pins = check_protocol()
        report["frozen_inputs_sources_verified"] = True
        report["input_source_sha256"] = pins
        import psutil
        report["psutil_version"] = psutil.__version__
        report["host_total_ram_mib"] = psutil.virtual_memory().total / 2**20
        report["preflight_free_ram_mib"] = psutil.virtual_memory().available / 2**20
        report["host_ram_preflight_sufficient"] = report["preflight_free_ram_mib"] >= protocol["supervision"]["preflight_free_ram_mib"]
        registration = None
        if args.registration:
            candidate, reg_pin = read_json(args.registration, 65536)
            registration = check_registration(candidate)
            report["registration_file_sha256"] = reg_pin
        report["registration_accepted"] = registration is not None
        if args.preflight_only:
            report["status"] = "SOFTWARE_PREFLIGHT_ONLY"
            report["registration_requirement"] = "RESOLVED" if registration else "PENDING_HUMAN_OR_EXTERNAL_REGISTRATION"
            return_code = 0
        else:
            need(registration is not None, "registration unresolved: no worker may start")
            limits = protocol["supervision"]
            need(psutil.virtual_memory().available >= limits["preflight_free_ram_mib"] * 2**20, "host RAM preflight guard")
            work = args.out / "worker"
            work.mkdir()
            # Archive exact input bytes and source preimages before any execution.
            for name in ["pilot_protocol_prepared.json", *pins]:
                target = args.out / "frozen" / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(BASE / name, target)
            shutil.copyfile(args.registration, args.out / "registration.json")
            for source in [Path(__file__), ROOT / "Tools/audit_captured_pilot_result_v1.py", ROOT / "Tools/bind_network_capture_v1.py"]:
                shutil.copyfile(source, args.out / source.name)
            command = [sys.executable, str((BASE / protocol["worker_path"]).resolve()),
                       "--scene", str((BASE / "scene.json").resolve()), "--out", str((work / "result.json").resolve()),
                       "--max-rays", "4096", "--max-depth", "64"]
            report["command"] = command
            started, peak, stopped = time.monotonic(), 0, None
            flags = (subprocess.CREATE_NO_WINDOW | subprocess.BELOW_NORMAL_PRIORITY_CLASS) if sys.platform == "win32" else 0
            with (work / "stdout.log").open("xb") as log:
                process = subprocess.Popen(command, cwd=BASE, stdout=log, stderr=subprocess.STDOUT, creationflags=flags)
                report["worker_started"] = True
                tracked = psutil.Process(process.pid)
                cpus = psutil.Process().cpu_affinity()
                need(bool(cpus), "available CPU affinity required")
                tracked.cpu_affinity([cpus[0]])
                report["logical_cpus"] = 1
                while process.poll() is None:
                    try:
                        peak = max(peak, tracked.memory_info().rss)
                    except psutil.NoSuchProcess:
                        break
                    result_path = work / "result.json"
                    if peak > limits["maximum_owned_process_rss_mib"] * 2**20:
                        stopped = "OWNED_PROCESS_RSS_LIMIT"
                    elif psutil.virtual_memory().available < limits["minimum_free_ram_mib"] * 2**20:
                        stopped = "HOST_FREE_RAM_FLOOR"
                    elif time.monotonic() - started > limits["timeout_seconds"]:
                        stopped = "WORKER_DEADLINE"
                    elif result_path.exists() and result_path.stat().st_size > limits["maximum_result_bytes"]:
                        stopped = "RESULT_SIZE_LIMIT"
                    if stopped:
                        process.kill()
                        break
                    time.sleep(.1)
                process.wait(timeout=5)
            report.update(worker_exit_code=process.returncode, stopped=stopped,
                          worker_seconds=time.monotonic() - started, peak_owned_rss_mib=peak / 2**20)
            need(stopped is None, "environment interrupted worker")
            check_protocol()
            need(file_sha(args.registration) == report["registration_file_sha256"], "registration record changed during run")
            result, result_pin = read_json(work / "result.json", limits["maximum_result_bytes"])
            scene, _ = read_json(BASE / "scene.json", 8 * 2**20)
            report.update(result_collected=True, raw_result_sha256=result_pin)
            need(type(result.get("rays")) is int and 0 <= result["rays"] <= 4096 and
                 isinstance(result.get("paths"), list) and len(result["paths"]) <= 4096 and
                 all(isinstance(path.get("hits"), list) and len(path["hits"]) <= 64 for path in result["paths"]),
                 "worker output exceeds frozen ray/depth bounds")
            audit = audit_result(scene, result)
            need(process.returncode == (0 if audit["primary_metric"] == 1 else 2), "exit code/result mismatch")
            report["audit"] = audit
            report["primary_metric"] = audit["primary_metric"]
            report["status"] = "VALID_PILOT_RESULT"
            return_code = 0
    except Exception as exc:
        report["failure_type"] = type(exc).__name__
        # Only our own explicit validation messages are exposed, never raw diagnostics.
        if isinstance(exc, ValueError):
            report["reason"] = str(exc)
        report["status"] = "INCONCLUSIVE_ENVIRONMENT_OR_INVALID_OUTPUT" if report["worker_started"] else "NOT_EXECUTED"
    finally:
        if process is not None and process.poll() is None:
            process.kill()
            process.wait(timeout=5)
        report["owned_worker_cleaned_up"] = process is None or process.poll() is not None
        if report["worker_started"]:
            raw_files = [p for p in args.out.rglob("*") if p.is_file()]
            report["raw_file_sha256"] = {p.relative_to(args.out).as_posix(): file_sha(p) for p in raw_files}
        with (args.out / "supervisor.json").open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps({key: report.get(key) for key in ("status", "worker_started", "result_collected", "primary_metric", "registration_requirement", "reason")}))
    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
