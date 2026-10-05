"""Pinned CPU-only fixtures; descendants stay in the inherited Windows Job Object."""
import ctypes
import os
from pathlib import Path
import subprocess
import sys
import time

kernel = ctypes.WinDLL("kernel32", use_last_error=True)
kernel.GetCurrentProcess.restype = ctypes.c_void_p
kernel.SetProcessAffinityMask.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
if not kernel.SetProcessAffinityMask(kernel.GetCurrentProcess(), 1):
    raise ctypes.WinError(ctypes.get_last_error())
profile = sys.argv[1]
if profile == "success":
    raise SystemExit(0)
if profile == "exit_error":
    raise SystemExit(7)
if profile == "block":
    time.sleep(10)  # Always contained by the caller's <=5s CPU-control deadline.
elif profile == "orphan":
    leaf = "import ctypes,time; k=ctypes.WinDLL('kernel32'); k.GetCurrentProcess.restype=ctypes.c_void_p; k.SetProcessAffinityMask.argtypes=[ctypes.c_void_p,ctypes.c_size_t]; assert k.SetProcessAffinityMask(k.GetCurrentProcess(),1); time.sleep(10)"
    subprocess.Popen([sys.executable, "-I", "-S", "-B", "-c", leaf],
        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        creationflags=subprocess.DETACHED_PROCESS)
    raise SystemExit(0)  # Deliberately leaves an owned descendant, without PID enumeration.
elif profile == "supervisor_exit":
    import hashlib
    from datetime import datetime, timedelta, timezone
    core = Path(sys.argv[2])
    if hashlib.sha256(core.read_bytes()).hexdigest() != sys.argv[3]:
        raise SystemExit(81)
    sys.path.insert(0, str(core.parent))
    import windows_job_tree_control_CPU_v1 as control
    inner = control.CPUControl("orphan", deadline=datetime.now(timezone.utc)+timedelta(seconds=15),
        timeout_s=3, model=control.MODEL)
    inner.wait_root()
    if inner.accounting()["active_processes"] != 1:
        raise SystemExit(82)
    os._exit(19)  # No finally/destructor: kernel closes the last inner job handle.
else:
    raise SystemExit(83)
