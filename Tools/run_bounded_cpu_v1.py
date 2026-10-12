"""Supervise only a newly spawned CPU worker; preserve NULL on interruption."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import psutil


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--receipt",type=Path,required=True)
    p.add_argument("--stdout",type=Path,required=True)
    p.add_argument("--seconds",type=float,required=True)
    p.add_argument("--rss-mib",type=float,default=1200)
    p.add_argument("--free-ram-mib",type=float,default=700)
    p.add_argument("command",nargs=argparse.REMAINDER)
    a=p.parse_args();command=a.command
    if command and command[0]=="--":command=command[1:]
    if not command or a.seconds<=0 or a.rss_mib<=0 or a.free_ram_mib<0:
        p.error("A command and positive resource limits are required")
    if a.receipt.exists() or a.stdout.exists():raise ValueError("New receipt and stdout required")
    a.receipt.parent.mkdir(parents=True,exist_ok=True);a.stdout.parent.mkdir(parents=True,exist_ok=True)
    report={"schema":"neuro3d.bounded_cpu.v1","started_utc":datetime.now(timezone.utc).isoformat(),
            "command":command,"status":"NOT_EXECUTED","metric":None,
            "limits":{"seconds":a.seconds,"rss_mib":a.rss_mib,"free_ram_mib":a.free_ram_mib}}
    reason=None;peak=0;start=time.monotonic();process=None
    try:
        if psutil.virtual_memory().available/2**20<a.free_ram_mib:
            reason="RAM_PREFLIGHT"
        else:
            env=dict(os.environ,OPENBLAS_NUM_THREADS="1",OMP_NUM_THREADS="1",MKL_NUM_THREADS="1",
                     PYTHONUTF8="1",PYTHONDONTWRITEBYTECODE="1")
            with a.stdout.open("xb") as stream:
                process=subprocess.Popen(command,stdout=stream,stderr=subprocess.STDOUT,env=env,
                    creationflags=subprocess.CREATE_NO_WINDOW|subprocess.BELOW_NORMAL_PRIORITY_CLASS if os.name=="nt" else 0)
                owned=psutil.Process(process.pid)
                while process.poll() is None:
                    try:peak=max(peak,owned.memory_info().rss/2**20)
                    except psutil.NoSuchProcess:break
                    if time.monotonic()-start>a.seconds:reason="DEADLINE"
                    elif peak>a.rss_mib:reason="OWNED_RSS"
                    elif psutil.virtual_memory().available/2**20<a.free_ram_mib:reason="HOST_RAM_FLOOR"
                    if reason:
                        process.terminate()
                        try:process.wait(timeout=5)
                        except subprocess.TimeoutExpired:process.kill();process.wait(timeout=5)
                        break
                    time.sleep(0.5)
                process.wait(timeout=5)
            report.update(exit_code=process.returncode,owned_pid=process.pid,
                          status="COMPLETED" if process.returncode==0 and reason is None else "INCOMPLETE",
                          stdout_sha256=hashlib.sha256(a.stdout.read_bytes()).hexdigest())
    finally:
        if process is not None and process.poll() is None:
            process.kill();process.wait(timeout=5)
        report.update(reason=reason,seconds=time.monotonic()-start,peak_rss_mib=peak,
                      owned_worker_terminal=process is None or process.poll() is not None)
        a.receipt.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps(report))
    return 0 if report["status"]=="COMPLETED" else 2


if __name__=="__main__":raise SystemExit(main())
