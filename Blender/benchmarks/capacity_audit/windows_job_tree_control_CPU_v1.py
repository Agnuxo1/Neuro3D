"""Opt-in real Windows Job Object containment, pinned CPU controls ONLY.

No GPU launch, reservation, telemetry adapter or GPU safety certification.
Frozen supervisors/runners are neither imported nor modified.
"""
import ctypes
from ctypes import wintypes as w
from datetime import datetime, timezone
import hashlib
import math
import os
from pathlib import Path
import subprocess
import time

MODEL = "windows-job-tree-control-CPU-v1"
WORKER = Path(__file__).with_name("windows_job_tree_worker_CPU_v1.py")
WORKER_SHA = "bb8675a1aad847cd98bda45d26eb22b5753e0e007b932f8f752946ea45500807"
PYTHON = Path("C:/Python313/python.exe")
PYTHON_SHA = "d932e5e2f324d57f392e8fd063dcf6d0185be8a664c57c6d24e7762ed02c28ca"
PROFILES = frozenset({"success", "exit_error", "block", "orphan", "supervisor_exit"})
GIB = 2**30
JOB_MEMORY_BYTES = 192 * 2**20  # Commit cap for ALL members, not a GPU budget.
HOST_CONTROL_BUDGET_BYTES = JOB_MEMORY_BYTES + 64 * 2**20
MAX_ACTIVE_PROCESSES = 4
CLEANUP_SECONDS = 2
STOP_EXIT = 90

class BasicLimits(ctypes.Structure):
    _fields_ = [("process_time",ctypes.c_longlong),("job_time",ctypes.c_longlong),
        ("flags",w.DWORD),("min_ws",ctypes.c_size_t),("max_ws",ctypes.c_size_t),
        ("active_limit",w.DWORD),("affinity",ctypes.c_size_t),
        ("priority",w.DWORD),("scheduling",w.DWORD)]

class IOCounters(ctypes.Structure):
    _fields_ = [(n,ctypes.c_ulonglong) for n in
        ("read_ops","write_ops","other_ops","read_bytes","write_bytes","other_bytes")]

class ExtendedLimits(ctypes.Structure):
    _fields_ = [("basic",BasicLimits),("io",IOCounters),
        ("process_memory",ctypes.c_size_t),("job_memory",ctypes.c_size_t),
        ("peak_process_memory",ctypes.c_size_t),("peak_job_memory",ctypes.c_size_t)]

class Accounting(ctypes.Structure):
    _fields_ = [(n,ctypes.c_longlong) for n in
        ("total_user","total_kernel","period_user","period_kernel")] + [
        ("page_faults",w.DWORD),("total_processes",w.DWORD),
        ("active_processes",w.DWORD),("terminated_processes",w.DWORD)]

class Startup(ctypes.Structure):
    _fields_ = [("cb",w.DWORD),("reserved",w.LPWSTR),("desktop",w.LPWSTR),
        ("title",w.LPWSTR),("x",w.DWORD),("y",w.DWORD),("xsize",w.DWORD),
        ("ysize",w.DWORD),("xchars",w.DWORD),("ychars",w.DWORD),
        ("fill",w.DWORD),("flags",w.DWORD),("show",w.WORD),
        ("reserved2bytes",w.WORD),("reserved2",ctypes.POINTER(w.BYTE)),
        ("stdin",w.HANDLE),("stdout",w.HANDLE),("stderr",w.HANDLE)]

class ProcessInfo(ctypes.Structure):
    _fields_ = [("process",w.HANDLE),("thread",w.HANDLE),
        ("pid",w.DWORD),("tid",w.DWORD)]

class MemoryStatus(ctypes.Structure):
    _fields_ = [("length",w.DWORD),("load",w.DWORD)] + [
        (n,ctypes.c_ulonglong) for n in ("total_phys","available_phys",
        "total_page","available_page","total_virtual","available_virtual","extended")]

class ControlFailure(RuntimeError):
    def __init__(self, report):
        self.report = dict(report)
        super().__init__("CPU containment rejected/stopped: " + report["status"])

class WinAPI:
    def __init__(self):
        if os.name != "nt":
            raise OSError("Windows required")
        self.k = ctypes.WinDLL("kernel32", use_last_error=True)
        declarations = {
            "CreateJobObjectW": ([ctypes.c_void_p,w.LPCWSTR],w.HANDLE),
            "SetInformationJobObject": ([w.HANDLE,ctypes.c_int,ctypes.c_void_p,w.DWORD],w.BOOL),
            "QueryInformationJobObject": ([w.HANDLE,ctypes.c_int,ctypes.c_void_p,w.DWORD,
                ctypes.POINTER(w.DWORD)],w.BOOL),
            "AssignProcessToJobObject": ([w.HANDLE,w.HANDLE],w.BOOL),
            "TerminateJobObject": ([w.HANDLE,w.UINT],w.BOOL),
            "TerminateProcess": ([w.HANDLE,w.UINT],w.BOOL),
            "ResumeThread": ([w.HANDLE],w.DWORD),
            "WaitForSingleObject": ([w.HANDLE,w.DWORD],w.DWORD),
            "GetExitCodeProcess": ([w.HANDLE,ctypes.POINTER(w.DWORD)],w.BOOL),
            "CloseHandle": ([w.HANDLE],w.BOOL),
            "GlobalMemoryStatusEx": ([ctypes.POINTER(MemoryStatus)],w.BOOL),
            "CreateProcessW": ([w.LPCWSTR,w.LPWSTR,ctypes.c_void_p,ctypes.c_void_p,w.BOOL,
                w.DWORD,ctypes.c_void_p,w.LPCWSTR,ctypes.POINTER(Startup),
                ctypes.POINTER(ProcessInfo)],w.BOOL),
        }
        for name,(args,result) in declarations.items():
            function = getattr(self.k,name)
            function.argtypes = args
            function.restype = result

    @staticmethod
    def require(ok):
        if not ok:
            raise ctypes.WinError(ctypes.get_last_error())

    def memory(self):
        value = MemoryStatus()
        value.length = ctypes.sizeof(value)
        self.require(self.k.GlobalMemoryStatusEx(ctypes.byref(value)))
        return value.available_phys

    def job(self):
        handle = self.k.CreateJobObjectW(None,None)  # Unnamed, non-inheritable.
        self.require(handle)
        return handle

    def limit(self, job):
        value = ExtendedLimits()
        # KILL_ON_JOB_CLOSE | JOB_MEMORY | ACTIVE_PROCESS | AFFINITY.
        # No BREAKAWAY_OK/SILENT_BREAKAWAY_OK; descendants inherit membership.
        value.basic.flags = 0x2000 | 0x200 | 0x8 | 0x10
        value.basic.active_limit = MAX_ACTIVE_PROCESSES
        value.basic.affinity = 1
        value.job_memory = JOB_MEMORY_BYTES
        self.require(self.k.SetInformationJobObject(job,9,ctypes.byref(value),ctypes.sizeof(value)))

    def create_suspended(self, command, env, info):
        startup = Startup()
        startup.cb = ctypes.sizeof(startup)
        startup.flags = 1  # STARTF_USESHOWWINDOW, SW_HIDE.
        startup.show = 0
        text = ctypes.create_unicode_buffer(subprocess.list2cmdline(command))
        block = ctypes.create_unicode_buffer("\0".join(k+"="+v for k,v in
            sorted(env.items(),key=lambda item:item[0].upper()))+"\0\0")
        # DETACHED_PROCESS: no console/conhost fixture; this is NOT BREAKAWAY_FROM_JOB.
        self.require(self.k.CreateProcessW(str(PYTHON),text,None,None,False,
            0x4 | 0x8 | 0x400,block,None,ctypes.byref(startup),ctypes.byref(info)))
        return info  # Handles belong only to the process CREATED by this call.

    def assign(self, job, process):
        self.require(self.k.AssignProcessToJobObject(job,process))

    def resume(self, thread):
        if self.k.ResumeThread(thread) == 0xFFFFFFFF:
            raise ctypes.WinError(ctypes.get_last_error())

    def wait(self, process, milliseconds):
        answer = self.k.WaitForSingleObject(process,milliseconds)
        if answer == 0xFFFFFFFF:
            raise ctypes.WinError(ctypes.get_last_error())
        if answer not in (0,258):
            raise OSError("unexpected process wait state")
        return answer == 0

    def exit_code(self, process):
        value = w.DWORD()
        self.require(self.k.GetExitCodeProcess(process,ctypes.byref(value)))
        return value.value

    def accounting(self, job):
        value = Accounting()
        self.require(self.k.QueryInformationJobObject(job,1,ctypes.byref(value),
            ctypes.sizeof(value),None))
        return {"active_processes":value.active_processes,"total_processes":value.total_processes,
            "terminated_processes":value.terminated_processes}

    def terminate_job(self, job):
        self.require(self.k.TerminateJobObject(job,STOP_EXIT))

    def terminate_created_process(self, process):
        self.require(self.k.TerminateProcess(process,STOP_EXIT))

    def close(self, handle):
        self.require(self.k.CloseHandle(handle))

class CPUControl:
    def __init__(self, profile, *, deadline, timeout_s, model):
        self._job = self._process = self._thread = None
        # Caller-owned buffer survives an interrupt immediately after CreateProcessW.
        self._creation_info = ProcessInfo()
        self._api = None
        self._closed = False
        self._deadline = deadline
        self._timeout = timeout_s
        self._start = time.monotonic()
        self._report = {"model":MODEL,"status":"REJECTED","profile":None,
            "created_suspended":False,"assigned_before_resume":False,"resumed":False,
            "cleanup_confirmed":False,"foreign_processes_touched":False,
            "GPU_job_admission":False,"GPU_executed":False,"runtime_GPU_guard":False,
            "native_precision_certified":False,"live_GPU_telemetry":False,
            "reservation_authenticated":False,"full_GPU_tree_containment_certified":False}
        try:
            if type(model) is not str or model != MODEL or type(profile) is not str or profile not in PROFILES:
                raise ValueError("explicit pinned CPU control required")
            if type(timeout_s) not in (int,float) or not math.isfinite(timeout_s) or not 0.05 <= timeout_s <= 5:
                raise ValueError("CPU-control timeout 0.05..5 seconds required")
            now = datetime.now(timezone.utc)
            if type(deadline) is not datetime or deadline.tzinfo is None or deadline.utcoffset().total_seconds()!=0:
                raise ValueError("explicit aware UTC deadline required")
            if not timeout_s+CLEANUP_SECONDS+1 <= (deadline-now).total_seconds() <= 60:
                raise ValueError("fresh bounded control deadline and cleanup margin required")
            source = WORKER.read_bytes()
            if hashlib.sha256(source).hexdigest()!=WORKER_SHA or hashlib.sha256(PYTHON.read_bytes()).hexdigest()!=PYTHON_SHA:
                raise ValueError("CPU worker or Python pin mismatch")
            self._report.update(profile=profile,worker_sha256=WORKER_SHA,python_sha256=PYTHON_SHA,
                deadline_utc=deadline.isoformat(),timeout_s=timeout_s,
                job_commit_cap_bytes=JOB_MEMORY_BYTES,host_budget_bytes=HOST_CONTROL_BUDGET_BYTES)
            self._api = WinAPI()
            ram = self._api.memory()
            self._report["ram_available_before_bytes"] = ram
            if ram-HOST_CONTROL_BUDGET_BYTES < 4*GIB:
                raise ValueError("RAM floor after CPU control budget")
            self._job = self._api.job()
            self._api.limit(self._job)
            env = dict(os.environ)
            for key in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS"):
                env[key]="1"
            core = Path(__file__).resolve()
            command = [str(PYTHON),"-I","-S","-B","-c",source.decode("utf-8"),profile,
                str(core),hashlib.sha256(core.read_bytes()).hexdigest()]
            info = self._api.create_suspended(command,env,self._creation_info)
            self._process,self._thread = info.process,info.thread
            self._report.update(created_suspended=True,own_pid=info.pid)
            self._api.assign(self._job,self._process)
            self._report["assigned_before_resume"] = True
            # Include time spent hashing and starting; no late resume.
            self._check_clock()
            self._api.resume(self._thread)
            self._report["resumed"] = True
            self._api.close(self._thread)
            self._thread = None
            self._report["status"]="RUNNING_CPU_CONTROL"
        except BaseException as exc:
            if self._process is None and self._creation_info.process:
                self._process,self._thread = self._creation_info.process,self._creation_info.thread
                self._report.update(created_suspended=True,own_pid=self._creation_info.pid)
            self._report.update(status="START_FAILED_CLOSED",error_type=type(exc).__name__)
            self.close()
            if not isinstance(exc,Exception):
                raise
            raise ControlFailure(self._report) from None

    def _check_clock(self):
        if datetime.now(timezone.utc)>=self._deadline or time.monotonic()-self._start>=self._timeout:
            raise TimeoutError("CPU control deadline/monotonic timeout")

    def view(self):
        return dict(self._report)

    def accounting(self):
        if self._closed or self._job is None:
            raise ValueError("closed CPU job has no query handle")
        return self._api.accounting(self._job)

    def wait_root(self):
        if self._closed or self._process is None:
            raise ValueError("closed CPU control")
        try:
            while True:
                self._check_clock()  # Also check before accepting an already-exited root.
                if self._api.wait(self._process,0):
                    code = self._api.exit_code(self._process)
                    self._report.update(status="CPU_ROOT_EXITED",root_exit_code=code,
                        active_after_root=self.accounting()["active_processes"])
                    return self.view()
                time.sleep(.01)
        except BaseException as exc:
            self._report.update(status="WAIT_FAILED_CLOSED",error_type=type(exc).__name__)
            self.close()
            if not isinstance(exc,Exception):
                raise
            raise ControlFailure(self._report) from None

    def close(self):
        if self._closed:
            return self.view()
        errors = []
        try:
            # An assignment failure leaves only OUR suspended root outside the job.
            if self._process is not None and not self._report["assigned_before_resume"]:
                self._api.terminate_created_process(self._process)
                if not self._api.wait(self._process,2000):
                    raise OSError("unassigned owned root termination unconfirmed")
            if self._job is not None:
                self._report["accounting_before_close"] = self._api.accounting(self._job)
                self._api.terminate_job(self._job)
                end = time.monotonic()+CLEANUP_SECONDS
                while True:
                    after = self._api.accounting(self._job)
                    if after["active_processes"] == 0:
                        self._report["accounting_after_close"] = after
                        break
                    if time.monotonic()>=end:
                        raise OSError("owned job members termination unconfirmed")
                    time.sleep(.01)
            if self._process is not None and not self._api.wait(self._process,2000):
                raise OSError("owned root close unconfirmed")
        except BaseException as exc:
            errors.append(type(exc).__name__)
            interrupted = exc if not isinstance(exc,Exception) else None
        else:
            interrupted = None
        finally:
            for attribute in ("_thread","_process","_job"):
                handle = getattr(self,attribute)
                if handle is not None:
                    try:
                        self._api.close(handle)  # Last job handle is a second fail-closed mechanism.
                        setattr(self,attribute,None)
                    except BaseException as exc:
                        errors.append(type(exc).__name__)
                        if not isinstance(exc,Exception):
                            interrupted = exc
            self._closed = True
            self._report.update(cleanup_confirmed=not errors,cleanup_error_types=errors,
                elapsed_s=time.monotonic()-self._start)
            if errors:
                self._report["status"]="CLEANUP_UNCONFIRMED"
        if interrupted is not None:
            raise interrupted
        return self.view()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
        if not self._report["cleanup_confirmed"]:
            raise ControlFailure(self._report)
        return False
