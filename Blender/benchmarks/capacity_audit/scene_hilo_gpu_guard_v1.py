"""Bound one scene-hi/lo GPU pilot; no frozen supervisor is imported or changed.

CLI, inside a NEW gpuq run:
  python -I -B scene_hilo_gpu_guard_v1.py --manifest job.json --receipt guard.json
Read-only dependency inventory:
  python -I -B scene_hilo_gpu_guard_v1.py --describe-pins

Job JSON schema scene-hilo-gpu-job-v1:
  job_id, authorization_context, gpu_uuid, issued_utc, deadline_utc,
  worker, input_manifest, input_manifest_sha256, worker_report, pins.
Optional: fresh_outputs (defaults to [worker_report]), host_budget_bytes and
device_budget_bytes (both default 2 GiB, cannot exceed 2 GiB), timeout_seconds
(default/max 100), cleanup_seconds (default/max 10), schema.
Pins maps absolute paths to lowercase SHA-256. It must include every path from
--describe-pins, worker, input_manifest and ALL imported worker/shader/data
dependencies. The caller freezes this complete dependency closure before launch.
Use a new job ID, deadline, receipt, worker report and output paths for each run.

The fixed argv requests an explicit OpenGL window, one CPU thread and a worker
that exits through its event-loop timer. GPU submission/readback correctness is
the worker's responsibility; the guard checks retained readback bytes and hashes.
This launcher provides local measured admission and owned-process containment,
not a machine-wide safety guarantee or a physical/native precision certificate.
RAM and VRAM reserve allowances remain in force at EVERY telemetry sample.
"""
from __future__ import annotations

import argparse
import csv
import ctypes
from ctypes import wintypes as w
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import io
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time

import psutil

GIB = 2**30
BLENDER = Path("D:/TOOLS/Blender/blender-4.5.14-windows-x64/blender.exe")
QUEUE = Path("D:/PROJECTS/.cognition/gpu_queue/gpuq.py")
SMI = Path("C:/Windows/System32/nvidia-smi.exe")
SHA_RE = re.compile(r"[0-9a-f]{64}")
UUID_RE = re.compile(r"GPU-[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}")
MAX_JSON = 16 * 2**20
MAX_READBACK = 8 * 2**20
MAX_MEMBERS = 4


class Rejected(RuntimeError):
    pass


def require(condition, message):
    if not condition:
        raise Rejected(message)


def utc_now():
    return datetime.now(timezone.utc)


def timestamp(value):
    require(type(value) is str, "UTC timestamp must be a string")
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise Rejected("Invalid UTC timestamp") from error
    require(result.tzinfo is not None and result.utcoffset().total_seconds() == 0,
            "Explicit UTC timestamp required")
    return result


def integer(value, minimum=0, maximum=2**63 - 1):
    require(type(value) is int and minimum <= value <= maximum, "Invalid bounded integer")
    return value


def finite(value, minimum=0, maximum=float("inf")):
    require(type(value) in (int, float) and math.isfinite(value)
            and minimum <= value <= maximum, "Invalid finite number")
    return value


def absolute(value):
    require(type(value) is str and "\0" not in value, "Invalid path")
    path = Path(value)
    require(path.is_absolute(), "Absolute path required")
    return path.resolve()


def key(path):
    return os.path.normcase(str(Path(path).resolve()))


def sha_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(2**20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path, limit=MAX_JSON):
    with Path(path).open("rb") as stream:
        raw = stream.read(limit + 1)
    require(len(raw) <= limit, "JSON size limit exceeded")
    try:
        value = json.loads(raw, parse_constant=lambda _: (_ for _ in ()).throw(
            ValueError("Non-finite JSON value")))
    except (ValueError, UnicodeError) as error:
        raise Rejected("Invalid JSON") from error
    require(type(value) is dict, "JSON object required")
    return value


def atomic_json(path, value):
    path = Path(path)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="\n",
                prefix="." + path.name + ".", suffix=".tmp", dir=path.parent,
                delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def critical_paths():
    paths = {Path(__file__).resolve(), Path(sys.executable).resolve(), BLENDER,
             QUEUE, SMI, Path(sys.executable).with_name("python313.dll"),
             Path("C:/Windows/System32/kernel32.dll")}
    for name, module in tuple(sys.modules.items()):
        if name == "psutil" or name.startswith("psutil."):
            source = getattr(module, "__file__", None)
            if source:
                paths.add(Path(source).resolve())
    for dependency in [Path("C:/Windows/System32/nvml.dll"),
                       *Path(sys.executable).parent.glob("vcruntime*.dll")]:
        if dependency.is_file():
            paths.add(dependency.resolve())
    return sorted(paths, key=key)


def verify_pins(pins):
    actual = {}
    for path, expected in sorted(pins.items()):
        require(type(expected) is str and SHA_RE.fullmatch(expected), "Invalid pin SHA-256")
        actual[path] = sha_file(path)
        require(actual[path] == expected, "Dependency hash changed: " + Path(path).name)
    return actual


@dataclass(frozen=True)
class Plan:
    job_id: str
    authorization: str
    gpu_uuid: str
    issued: datetime
    deadline: datetime
    worker: Path
    input_manifest: Path
    input_sha: str
    worker_report: Path
    fresh_outputs: tuple
    pins: dict
    host_budget: int = 2 * GIB
    device_budget: int = 2 * GIB
    timeout: float = 100
    cleanup: float = 10

    def command(self):
        return [str(BLENDER), "--factory-startup", "--disable-autoexec", "--threads", "1",
                "--python-exit-code", "1", "--gpu-backend", "opengl",
                "--window-geometry", "0", "0", "128", "128", "--python", str(self.worker),
                "--", "--input-manifest", str(self.input_manifest),
                "--report", str(self.worker_report), "--job-id", self.job_id]


def load_plan(path, now):
    raw = read_json(path)
    required = {"job_id", "authorization_context", "gpu_uuid", "issued_utc", "deadline_utc",
                "worker", "input_manifest", "input_manifest_sha256", "worker_report", "pins"}
    allowed = required | {"schema", "fresh_outputs", "host_budget_bytes", "device_budget_bytes",
                          "timeout_seconds", "cleanup_seconds"}
    require(required <= set(raw) <= allowed, "Closed job schema required")
    require(raw.get("schema", "scene-hilo-gpu-job-v1") == "scene-hilo-gpu-job-v1",
            "Wrong job schema")
    require(type(raw["job_id"]) is str and re.fullmatch(r"[A-Za-z0-9_.:-]{8,128}", raw["job_id"]),
            "Unique bounded job_id required")
    require(type(raw["authorization_context"]) is str
            and 1 <= len(raw["authorization_context"]) <= 2000, "Current authorization context required")
    require(type(raw["gpu_uuid"]) is str and UUID_RE.fullmatch(raw["gpu_uuid"]), "GPU UUID required")
    issued, deadline = timestamp(raw["issued_utc"]), timestamp(raw["deadline_utc"])
    timeout = finite(raw.get("timeout_seconds", 100), .05, 100)
    cleanup = finite(raw.get("cleanup_seconds", 10), 1, 10)
    require(0 <= (now - issued).total_seconds() <= 300, "Job issue time is stale or future")
    require(timeout + 60 <= (deadline - now).total_seconds() <= 600,
            "New deadline requires work timeout plus 60 seconds")
    worker, inp, report = (absolute(raw[name]) for name in
                           ("worker", "input_manifest", "worker_report"))
    require(type(raw["pins"]) is dict and 1 <= len(raw["pins"]) <= 256, "Dependency pins required")
    pins = {key(absolute(p)): digest for p, digest in raw["pins"].items()}
    require(len(pins) == len(raw["pins"]), "Duplicate normalized dependency paths")
    for critical in [*critical_paths(), worker, inp, absolute(str(path))]:
        require(key(critical) in pins or key(critical) == key(path),
                "Missing critical dependency pin: " + str(critical))
    require(type(raw["input_manifest_sha256"]) is str
            and SHA_RE.fullmatch(raw["input_manifest_sha256"])
            and pins[key(inp)] == raw["input_manifest_sha256"], "Input manifest pin mismatch")
    outputs = raw.get("fresh_outputs", [str(report)])
    require(type(outputs) is list and 1 <= len(outputs) <= 32, "Fresh output list required")
    fresh = tuple(absolute(value) for value in outputs)
    require(len(set(map(key, fresh))) == len(fresh) and key(report) in set(map(key, fresh)),
            "Unique fresh outputs must include worker report")
    require(not any(key(p) in pins or key(p) == key(path) for p in fresh), "Output overlaps an input")
    return Plan(raw["job_id"], raw["authorization_context"], raw["gpu_uuid"], issued, deadline,
                worker, inp, raw["input_manifest_sha256"], report, fresh, pins,
                integer(raw.get("host_budget_bytes", 2 * GIB), 256 * 2**20, 2 * GIB),
                integer(raw.get("device_budget_bytes", 2 * GIB), 16 * 2**20, 2 * GIB),
                timeout, cleanup)


def resource_check(sample, plan, now):
    require(type(sample) is dict, "Telemetry must be an object")
    for field in ("ram_available_bytes", "device_used_bytes", "device_total_bytes", "gpu_count"):
        integer(sample[field])
    require(sample["gpu_count"] == 1 and sample["gpu_uuid"] == plan.gpu_uuid,
            "OpenGL mapping requires exactly the declared single NVIDIA GPU")
    require("RTX 3090" in sample["name"], "Unexpected physical NVIDIA device")
    age = (now - timestamp(sample["sampled_utc"])).total_seconds()
    require(0 <= age <= 5, "Stale or future telemetry")
    finite(sample["temperature_c"], 0, 80)
    finite(sample["utilization_percent"], 0, 100)
    require(sample["ram_available_bytes"] - plan.host_budget >= 4 * GIB,
            "RAM floor after reserved budget")
    projected = sample["device_used_bytes"] + plan.device_budget
    require(projected <= 18 * GIB and projected <= sample["device_total_bytes"],
            "VRAM global/physical limit after reserved budget")


def lease_record(record, plan, parent, child):
    require(type(record) is dict and record.get("name") == plan.job_id, "Wrong or missing lease")
    for prefix, identity in (("", parent), ("child_", child)):
        pid, created = record.get(prefix + "pid"), record.get(prefix + "ctime")
        require(type(pid) is int and pid > 0 and type(created) in (int, float)
                and math.isfinite(created), "Invalid lease process identity")
        require(pid == identity["pid"] and created == identity["ctime"],
                "Lease process identity mismatch")
    require(record.get("cmd") == child["command"], "Lease child command mismatch")
    require(child["ppid"] == parent["pid"], "Lease parent is not this supervisor's parent")
    return {"name": record["name"], "pid": parent["pid"], "ctime": parent["ctime"],
            "child_pid": child["pid"], "child_ctime": child["ctime"]}


class Lease:
    def __init__(self, plan):
        self.plan = plan
        self.holder = QUEUE.parent / "holder.json"

    def check(self):
        own = psutil.Process()
        parent = own.parent()
        require(parent is not None, "Queue parent is absent")
        require(key(parent.exe()) == key(sys.executable), "Queue interpreter mismatch")
        parent_cmd = parent.cmdline()
        arguments = parent_cmd[1:]
        while arguments and arguments[0] in ("-I", "-B", "-S", "-u"):
            arguments = arguments[1:]
        require(len(arguments) >= 4 and key(arguments[0]) == key(QUEUE)
                and arguments[1] == "run", "Parent is not the pinned queue run")
        require("--name" in arguments and arguments[arguments.index("--name") + 1] == self.plan.job_id,
                "Wrong queue job name")
        child = {"pid": own.pid, "ctime": own.create_time(), "ppid": own.ppid(),
                 "command": own.cmdline()}
        parent_id = {"pid": parent.pid, "ctime": parent.create_time()}
        return lease_record(read_json(self.holder, 2**20), self.plan, parent_id, child)

    def wait_initial(self, seconds=2):
        # gpuq writes child_pid after Popen through a non-atomic rewrite.
        end = time.monotonic() + seconds
        while True:
            try:
                return self.check()
            except (Rejected, OSError, psutil.Error, KeyError):
                if time.monotonic() >= end:
                    raise Rejected("Queue lease did not become bound within two seconds") from None
                time.sleep(.025)


# New contained implementation. No import or mutation of the frozen CPU profile.
class BasicLimits(ctypes.Structure):
    _fields_ = [("process_time", ctypes.c_longlong), ("job_time", ctypes.c_longlong),
                ("flags", w.DWORD), ("min_ws", ctypes.c_size_t), ("max_ws", ctypes.c_size_t),
                ("active_limit", w.DWORD), ("affinity", ctypes.c_size_t),
                ("priority", w.DWORD), ("scheduling", w.DWORD)]


class IOCounters(ctypes.Structure):
    _fields_ = [(name, ctypes.c_ulonglong) for name in
                ("read_ops", "write_ops", "other_ops", "read_bytes", "write_bytes", "other_bytes")]


class ExtendedLimits(ctypes.Structure):
    _fields_ = [("basic", BasicLimits), ("io", IOCounters),
                ("process_memory", ctypes.c_size_t), ("job_memory", ctypes.c_size_t),
                ("peak_process_memory", ctypes.c_size_t), ("peak_job_memory", ctypes.c_size_t)]


class Accounting(ctypes.Structure):
    _fields_ = [(name, ctypes.c_longlong) for name in
                ("total_user", "total_kernel", "period_user", "period_kernel")] + [
                ("page_faults", w.DWORD), ("total_processes", w.DWORD),
                ("active_processes", w.DWORD), ("terminated_processes", w.DWORD)]


class Startup(ctypes.Structure):
    _fields_ = [("cb", w.DWORD), ("reserved", w.LPWSTR), ("desktop", w.LPWSTR),
                ("title", w.LPWSTR), ("x", w.DWORD), ("y", w.DWORD), ("xs", w.DWORD),
                ("ys", w.DWORD), ("xc", w.DWORD), ("yc", w.DWORD), ("fill", w.DWORD),
                ("flags", w.DWORD), ("show", w.WORD), ("reserved_bytes", w.WORD),
                ("reserved2", ctypes.POINTER(w.BYTE)), ("stdin", w.HANDLE),
                ("stdout", w.HANDLE), ("stderr", w.HANDLE)]


class StartupEx(ctypes.Structure):
    _fields_ = [("startup", Startup), ("attributes", ctypes.c_void_p)]


class ProcessInfo(ctypes.Structure):
    _fields_ = [("process", w.HANDLE), ("thread", w.HANDLE), ("pid", w.DWORD), ("tid", w.DWORD)]


class OwnedJob:
    def __init__(self, memory_bytes, directory):
        require(os.name == "nt", "Windows Job Objects required")
        self.directory, self.memory_bytes = Path(directory), memory_bytes
        self.k = ctypes.WinDLL("kernel32", use_last_error=True)
        self.processes, self.events = [], []
        self.handle, self.closed, self.cleanup_confirmed = None, False, False
        self.serial = 0
        signatures = {
            "CreateJobObjectW": ([ctypes.c_void_p, w.LPCWSTR], w.HANDLE),
            "SetInformationJobObject": ([w.HANDLE, ctypes.c_int, ctypes.c_void_p, w.DWORD], w.BOOL),
            "QueryInformationJobObject": ([w.HANDLE, ctypes.c_int, ctypes.c_void_p, w.DWORD,
                                          ctypes.POINTER(w.DWORD)], w.BOOL),
            "AssignProcessToJobObject": ([w.HANDLE, w.HANDLE], w.BOOL),
            "TerminateJobObject": ([w.HANDLE, w.UINT], w.BOOL),
            "TerminateProcess": ([w.HANDLE, w.UINT], w.BOOL),
            "ResumeThread": ([w.HANDLE], w.DWORD),
            "WaitForSingleObject": ([w.HANDLE, w.DWORD], w.DWORD),
            "GetExitCodeProcess": ([w.HANDLE, ctypes.POINTER(w.DWORD)], w.BOOL),
            "CloseHandle": ([w.HANDLE], w.BOOL),
            "CreateProcessW": ([w.LPCWSTR, w.LPWSTR, ctypes.c_void_p, ctypes.c_void_p, w.BOOL,
                               w.DWORD, ctypes.c_void_p, w.LPCWSTR, ctypes.c_void_p,
                               ctypes.POINTER(ProcessInfo)], w.BOOL),
            "InitializeProcThreadAttributeList": ([ctypes.c_void_p, w.DWORD, w.DWORD,
                                                   ctypes.POINTER(ctypes.c_size_t)], w.BOOL),
            "UpdateProcThreadAttribute": ([ctypes.c_void_p, w.DWORD, ctypes.c_size_t,
                                           ctypes.c_void_p, ctypes.c_size_t,
                                           ctypes.c_void_p, ctypes.c_void_p], w.BOOL),
            "DeleteProcThreadAttributeList": ([ctypes.c_void_p], None),
        }
        for name, (arguments, result) in signatures.items():
            fn = getattr(self.k, name)
            fn.argtypes, fn.restype = arguments, result
        try:
            self.handle = self.k.CreateJobObjectW(None, None)
            self.ok(self.handle)
            limits = ExtendedLimits()
            limits.basic.flags = 0x2000 | 0x200 | 0x8 | 0x10
            limits.basic.active_limit, limits.basic.affinity = MAX_MEMBERS, 1
            limits.job_memory = integer(memory_bytes, 16 * 2**20, 2 * GIB)
            self.ok(self.k.SetInformationJobObject(self.handle, 9, ctypes.byref(limits),
                                                    ctypes.sizeof(limits)))
        except BaseException:
            if self.handle:
                self.k.CloseHandle(self.handle)
                self.handle = None
            raise

    @staticmethod
    def ok(value):
        if not value:
            raise ctypes.WinError(ctypes.get_last_error())

    def accounting(self):
        value = Accounting()
        self.ok(self.k.QueryInformationJobObject(self.handle, 1, ctypes.byref(value),
                                                  ctypes.sizeof(value), None))
        return {"active_processes": value.active_processes,
                "total_processes": value.total_processes}

    def spawn(self, command, environment, before_resume=lambda: None):
        import msvcrt
        require(not self.closed, "Owned job is closed")
        self.serial += 1
        log = self.directory / ("process-%03d.log" % self.serial)
        info = ProcessInfo()  # Survives interruption immediately after CreateProcessW.
        event = {"sequence": self.serial, "executable": str(command[0]),
                 "log": str(log), "created_suspended": False, "assigned_before_resume": False,
                 "resumed": False}
        self.events.append(event)
        entry = {"info": info, "event": event, "log": log, "assigned": False}
        self.processes.append(entry)
        attributes, attributes_initialized = None, False
        try:
            with log.open("xb") as output, open(os.devnull, "rb") as source:
                handles = (w.HANDLE * 2)(msvcrt.get_osfhandle(output.fileno()),
                                        msvcrt.get_osfhandle(source.fileno()))
                for handle in handles:
                    os.set_handle_inheritable(handle, True)
                size = ctypes.c_size_t()
                self.k.InitializeProcThreadAttributeList(None, 1, 0, ctypes.byref(size))
                require(size.value > 0, "Attribute-list allocation failed")
                buffer = ctypes.create_string_buffer(size.value)
                attributes = ctypes.cast(buffer, ctypes.c_void_p)
                self.ok(self.k.InitializeProcThreadAttributeList(attributes, 1, 0, ctypes.byref(size)))
                attributes_initialized = True
                self.ok(self.k.UpdateProcThreadAttribute(attributes, 0, 0x20002, handles,
                                                          ctypes.sizeof(handles), None, None))
                startup = StartupEx()
                startup.startup.cb = ctypes.sizeof(startup)
                startup.startup.flags = 0x100 | 1  # Explicit stdio and hidden initial window.
                startup.startup.show = 0
                startup.startup.stdout = startup.startup.stderr = handles[0]
                startup.startup.stdin = handles[1]
                startup.attributes = attributes
                args = ctypes.create_unicode_buffer(subprocess.list2cmdline(command))
                env = ctypes.create_unicode_buffer("\0".join(k + "=" + v for k, v in
                    sorted(environment.items(), key=lambda pair: pair[0].upper())) + "\0\0")
                self.ok(self.k.CreateProcessW(str(command[0]), args, None, None, True,
                    0x4 | 0x8 | 0x400 | 0x80000, env, str(self.directory),
                    ctypes.byref(startup), ctypes.byref(info)))
                event.update(created_suspended=True, pid=info.pid)
                self.ok(self.k.AssignProcessToJobObject(self.handle, info.process))
                entry["assigned"] = event["assigned_before_resume"] = True
                before_resume()
                require(self.k.ResumeThread(info.thread) != 0xFFFFFFFF, "ResumeThread failed")
                event["resumed"] = True
            self.ok(self.k.CloseHandle(info.thread))
            info.thread = None
            return entry
        except BaseException:
            event.update(created_suspended=bool(info.process), pid=info.pid or None)
            if info.process and not entry["assigned"]:
                self.ok(self.k.TerminateProcess(info.process, 90))
                require(self.k.WaitForSingleObject(info.process, 2000) == 0,
                        "Unassigned owned root did not terminate")
            raise
        finally:
            if attributes_initialized:
                self.k.DeleteProcThreadAttributeList(attributes)

    def poll(self, entry):
        answer = self.k.WaitForSingleObject(entry["info"].process, 0)
        require(answer in (0, 258), "Owned process wait failed")
        if answer == 258:
            return None
        code = w.DWORD()
        self.ok(self.k.GetExitCodeProcess(entry["info"].process, ctypes.byref(code)))
        return code.value

    def capture(self, command, environment, seconds):
        entry = self.spawn(command, environment)
        end = time.monotonic() + seconds
        while self.poll(entry) is None:
            require(time.monotonic() < end, "Telemetry process timeout")
            time.sleep(.01)
        require(time.monotonic() < end and self.poll(entry) == 0, "Telemetry process failed or late")
        with entry["log"].open("rb") as stream:
            raw = stream.read(65537)
        require(len(raw) <= 65536, "Telemetry output exceeds bound")
        return raw.decode("utf-8", errors="strict")

    def close(self, seconds):
        if self.closed:
            return {"cleanup_confirmed": self.cleanup_confirmed}
        end = time.monotonic() + seconds
        errors, after = [], None
        try:
            for entry in self.processes:
                info = entry["info"]
                if info.process and not entry["assigned"] and self.poll(entry) is None:
                    self.ok(self.k.TerminateProcess(info.process, 90))
            self.ok(self.k.TerminateJobObject(self.handle, 90))
            while True:
                after = self.accounting()
                roots_closed = all(not e["info"].process or self.poll(e) is not None
                                   for e in self.processes)
                if after["active_processes"] == 0 and roots_closed:
                    break
                require(time.monotonic() < end, "Owned job cleanup unconfirmed")
                time.sleep(.01)
        except BaseException as error:
            errors.append(type(error).__name__)
            if not isinstance(error, Exception):
                interrupt = error
            else:
                interrupt = None
        else:
            interrupt = None
        finally:
            for entry in self.processes:
                for member in ("thread", "process"):
                    handle = getattr(entry["info"], member)
                    if handle:
                        if not self.k.CloseHandle(handle):
                            errors.append("CloseProcessHandleFailed")
                        setattr(entry["info"], member, None)
            if self.handle:
                if not self.k.CloseHandle(self.handle):
                    errors.append("CloseJobHandleFailed")
                self.handle = None
            self.closed, self.cleanup_confirmed = True, not errors
        if interrupt is not None:
            raise interrupt
        return {"cleanup_confirmed": self.cleanup_confirmed, "accounting_after_close": after,
                "cleanup_errors": errors}


def parse_telemetry(text, ram, sampled):
    rows = list(csv.reader(io.StringIO(text.strip())))
    require(len(rows) == 1 and len(rows[0]) == 7, "Exactly one physical NVIDIA GPU required")
    uuid, name, driver, used, total, temperature, utilization = (v.strip() for v in rows[0])
    try:
        used_mib, total_mib = int(used), int(total)
        temp, util = float(temperature), float(utilization)
    except ValueError as error:
        raise Rejected("Unavailable or invalid global GPU telemetry") from error
    return {"sampled_utc": sampled.isoformat(), "gpu_count": len(rows), "gpu_uuid": uuid,
            "name": name, "driver": driver, "device_used_bytes": used_mib * 2**20,
            "device_total_bytes": total_mib * 2**20, "temperature_c": temp,
            "utilization_percent": util, "ram_available_bytes": ram}


def worker_gate(path, plan):
    report_sha = sha_file(path)
    result = read_json(path)
    require(result.get("status") == "PASS" and result.get("verification_passed") is True,
            "Worker verification did not pass")
    require(result.get("job_id") == plan.job_id and result.get("input_manifest_sha256") == plan.input_sha,
            "Worker evidence binding mismatch")
    require(result.get("native_gpu_executed") is True and result.get("backend") == "OPENGL",
            "Native OpenGL execution evidence required")
    integer(result.get("gpu_dispatch_count"), 1, 100000)
    require(result.get("background") is False and "NVIDIA" in result.get("vendor", "")
            and "RTX 3090" in result.get("renderer", ""), "Worker device/context mismatch")
    records = result.get("gpu_readback_records")
    require(type(records) is list and 1 <= len(records) <= 128, "Readback records required")
    inputs = read_json(plan.input_manifest)
    require(inputs.get("schema") == "neuro3d.scene_hilo.native_job.v1", "Unexpected input schema")
    cases = inputs.get("cases")
    require(type(cases) is list and 1 <= len(cases) <= 64, "Input cases required")
    case_ids = [case.get("case_id") for case in cases if type(case) is dict]
    require(len(case_ids) == len(cases) and all(type(value) is str and value for value in case_ids)
            and len(set(case_ids)) == len(case_ids), "Input case identities must be unique")
    max_dispatches = integer(inputs.get("limits", {}).get("max_dispatches"), 1, 128)
    require(result["gpu_dispatch_count"] == len(records) == 2 * len(cases)
            and len(records) <= max_dispatches, "Dispatch/readback count differs from fixed input")
    observed = []
    for record in records:
        require(type(record) is dict and type(record.get("zero_low")) in (int, bool)
                and record["zero_low"] in (0, 1), "Invalid readback mode")
        observed.append((record.get("case_id"), bool(record["zero_low"])))
    require(observed == [(case, mode) for case in case_ids for mode in (False, True)],
            "Readback case/mode coverage or order mismatch")
    digest, count = hashlib.sha256(), 0
    for record in records:
        require(type(record) is dict, "Invalid readback record")
        for field in ("input_echo_hex", "computed_rows_hex"):
            value = record.get(field)
            require(type(value) is str and value and len(value) % 2 == 0
                    and re.fullmatch(r"[0-9a-f]+", value), "Invalid readback hex")
            count += len(value) // 2
            require(count <= MAX_READBACK, "Readback size limit exceeded")
            digest.update(bytes.fromhex(value))
    require(result.get("gpu_readback_sha256") == digest.hexdigest(), "Readback hash mismatch")
    require(sha_file(path) == report_sha, "Worker report changed during validation")
    return {"worker_report_sha256": report_sha, "gpu_readback_sha256": digest.hexdigest(),
            "gpu_readback_bytes": count, "gpu_dispatch_count": result["gpu_dispatch_count"],
            "backend": result["backend"], "renderer": result["renderer"],
            "vendor": result["vendor"], "native_gpu_execution_verified": True}


class Runtime:
    synthetic = False

    def __init__(self, plan, directory):
        self.plan, self.directory = plan, Path(directory)
        self.lease = Lease(plan)
        self.job = None
        self.environment = dict(os.environ)
        for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                     "NUMEXPR_NUM_THREADS", "BLIS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
            self.environment[name] = "1"
        self.environment.update(TEMP=str(directory), TMP=str(directory), PYTHONDONTWRITEBYTECODE="1")

    def start(self):
        self.lease.wait_initial()
        self.job = OwnedJob(self.plan.host_budget, self.directory)

    def sample(self, seconds):
        sampled, ram = utc_now(), psutil.virtual_memory().available
        # Do not use --id here: all physical NVIDIA devices must be counted for OpenGL mapping.
        raw = self.job.capture([str(SMI),
            "--query-gpu=uuid,name,driver_version,memory.used,memory.total,temperature.gpu,utilization.gpu",
            "--format=csv,noheader,nounits"], self.environment, min(2, seconds))
        return parse_telemetry(raw, ram, sampled)

    def spawn(self, check):
        return self.job.spawn(self.plan.command(), self.environment, check)

    def close(self, seconds):
        return self.job.close(seconds) if self.job else {"cleanup_confirmed": True}


def execute(plan, receipt, runtime_factory=Runtime, now=utc_now, mono=time.monotonic,
            sleep=time.sleep):
    """Testable supervisor core; CLI never accepts injected services or admission."""
    receipt = Path(receipt).resolve()
    start, started_utc = mono(), now()
    report = {"schema": "scene-hilo-gpu-guard-v1", "job_id": plan.job_id, "status": "RUNNING",
              "started_utc": started_utc.isoformat(), "authorization_context": plan.authorization,
              "deadline_utc": plan.deadline.isoformat(), "timeout_seconds": plan.timeout,
              "cleanup_seconds": plan.cleanup, "host_budget_bytes": plan.host_budget,
              "device_budget_bytes": plan.device_budget, "ram_floor_bytes": 4 * GIB,
              "vram_cap_bytes": 18 * GIB, "temperature_cap_c": 80,
              "reserve_allowance_applies_during_runtime": True, "samples": [],
              "GPU_job_admission": False, "native_gpu_execution_verified": False,
              "physical_precision_certified": False, "native_precision_certified": False,
              "global_machine_safety_certified": False, "foreign_processes_terminated": False}
    runtime, child, failure, interrupt = None, None, None, None
    require(key(receipt) not in plan.pins and key(receipt) not in set(map(key, plan.fresh_outputs)),
            "Receipt overlaps a protected path")
    receipt.parent.mkdir(parents=True, exist_ok=True)
    # A prior receipt is never replaced, including one that claimed PASS.
    with receipt.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, allow_nan=False)
        stream.flush()
        os.fsync(stream.fileno())
    directory = receipt.with_name(receipt.stem + "-run")

    def clock_check():
        require(now() < plan.deadline and mono() - start < plan.timeout, "Work deadline/timeout")

    def admission_check():
        clock_check()
        report["lease"] = runtime.lease.check()
        if report["samples"]:
            resource_check(report["samples"][-1], plan, now())

    try:
        require(not any(p.exists() for p in plan.fresh_outputs), "A declared output already exists")
        directory.mkdir(exist_ok=False)
        report["pins_entry"] = verify_pins(plan.pins)
        runtime = runtime_factory(plan, directory)
        report["synthetic_CPU_control"] = runtime.synthetic
        runtime.start()
        admission_check()
        sample = runtime.sample(min(2, plan.timeout - (mono() - start)))
        resource_check(sample, plan, now())
        report["samples"].append(sample)
        verify_pins(plan.pins)
        admission_check()
        child = runtime.spawn(admission_check)
        report["workload_pid"] = child["info"].pid
        report["GPU_job_admission"] = not runtime.synthetic
        while True:
            admission_check()
            sample = runtime.sample(min(2, plan.timeout - (mono() - start)))
            resource_check(sample, plan, now())
            report["samples"].append(sample)
            clock_check()  # No rc0 accepted after deadline, lease or telemetry failure.
            code = runtime.job.poll(child)
            if code is not None:
                report["worker_exit_code"] = code
                require(code == 0, "Worker process returned a nonzero exit code")
                admission_check()
                final_sample = runtime.sample(min(2, plan.timeout - (mono() - start)))
                resource_check(final_sample, plan, now())
                final_sample["stage"] = "after_worker_exit_before_job_close"
                report["samples"].append(final_sample)
                clock_check()
                break
            sleep(min(.25, max(0, plan.timeout - (mono() - start))))
    except BaseException as error:
        failure = {"type": type(error).__name__, "reason": str(error)[:1000]}
        if not isinstance(error, Exception):
            interrupt = error
    finally:
        if runtime is not None:
            try:
                report.update(runtime.close(plan.cleanup))
                report["process_events"] = runtime.job.events if runtime.job else []
                require(report.get("cleanup_confirmed") is True, "Owned job cleanup unconfirmed")
            except BaseException as error:
                failure = {"type": type(error).__name__, "reason": "Owned job cleanup failed"}
                report["cleanup_confirmed"] = False
                if not isinstance(error, Exception):
                    interrupt = error
        else:
            report["cleanup_confirmed"] = True
        try:
            report["pins_exit"] = verify_pins(plan.pins)
            require(now() < plan.deadline and mono() - start < plan.timeout + plan.cleanup,
                    "Late finalization")
            if failure is None:
                report["lease_final"] = runtime.lease.check()
                require(all(p.is_file() for p in plan.fresh_outputs), "Declared worker outputs missing")
                report.update(worker_gate(plan.worker_report, plan))
                require(now() < plan.deadline and mono() - start < plan.timeout + plan.cleanup,
                        "Worker evidence validation finalized too late")
                resource_check(report["samples"][-1], plan, now())
                if runtime.synthetic:
                    report["native_gpu_execution_verified"] = False
                    report["GPU_job_admission"] = False
                report["status"] = "CPU_CONTROL_PASS" if runtime.synthetic else "PASS"
        except BaseException as error:
            failure = {"type": type(error).__name__, "reason": str(error)[:1000]}
            if not isinstance(error, Exception):
                interrupt = error
        if failure is not None:
            report.update(status="FAIL", failure=failure, native_gpu_execution_verified=False)
        report["finished_utc"], report["elapsed_seconds"] = now().isoformat(), mono() - start
        if now() >= plan.deadline or report["elapsed_seconds"] >= plan.timeout + plan.cleanup:
            report.update(status="FAIL", native_gpu_execution_verified=False,
                          failure={"type": "Rejected", "reason": "Late receipt finalization"})
        atomic_json(receipt, report)
        if (now() >= plan.deadline or mono() - start >= plan.timeout + plan.cleanup) and report["status"] != "FAIL":
            report.update(status="FAIL", native_gpu_execution_verified=False,
                          failure={"type": "Rejected", "reason": "Receipt write exceeded deadline"})
            atomic_json(receipt, report)
    if interrupt is not None:
        raise interrupt
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--describe-pins", action="store_true")
    args = parser.parse_args(argv)
    if args.describe_pins:
        require(args.manifest is None and args.receipt is None, "Inventory cannot launch a job")
        print(json.dumps({key(p): sha_file(p) for p in critical_paths()}, indent=2))
        return 0
    require(args.manifest is not None and args.receipt is not None, "Manifest and new receipt required")
    require(os.name == "nt", "Windows required")
    try:
        manifest_sha = sha_file(args.manifest)
        plan = load_plan(args.manifest.resolve(), utc_now())
        require(sha_file(args.manifest) == manifest_sha, "Job manifest changed while being read")
        # Bind the job contract itself without a circular self-hash.
        plan.pins[key(args.manifest)] = manifest_sha
    except Exception as error:
        rejection = {"schema": "scene-hilo-gpu-guard-v1", "status": "FAIL",
                     "stage": "manifest_validation", "workload_started": False,
                     "GPU_job_admission": False, "native_gpu_execution_verified": False,
                     "failure": {"type": type(error).__name__, "reason": str(error)[:1000]}}
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        with args.receipt.open("x", encoding="utf-8") as stream:
            json.dump(rejection, stream, allow_nan=False)
            stream.write("\n")
        print(json.dumps(rejection, allow_nan=False))
        return 1
    result = execute(plan, args.receipt)
    print(json.dumps({name: result.get(name) for name in
                     ("job_id", "status", "worker_exit_code", "cleanup_confirmed",
                      "worker_report_sha256", "elapsed_seconds", "failure")}, allow_nan=False))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
