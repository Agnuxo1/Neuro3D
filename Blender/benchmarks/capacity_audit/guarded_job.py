"""Bounded launcher for OWN jobs only; invoke inside a gpuq reservation.

Stops only its child tree on a resource violation, deadline or timeout. This is
not a system-wide GPU watchdog and never cancels another queue holder.
"""
import argparse
from datetime import datetime,timezone
import json
import math
from pathlib import Path
import subprocess
import time

import psutil

GIB=2**30
DEADLINE=datetime(2026,9,30,6,tzinfo=timezone.utc)


def violations(sample,*,now,deadline,elapsed,timeout,host_estimate=0,device_estimate=0):
    if not 0 < timeout <= 600 or min(host_estimate,device_estimate)<0:
        raise ValueError('invalid bounded job policy')
    if now.tzinfo is None or deadline.tzinfo is None:
        raise ValueError('aware UTC time required')
    if any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or v<0
           for v in (*sample.values(),elapsed,host_estimate,device_estimate)):
        raise ValueError('invalid telemetry')
    reasons=[]
    if sample['ram_available_bytes']-host_estimate < 4*GIB: reasons.append('ram_floor')
    if sample['device_used_bytes']+device_estimate > 18*GIB: reasons.append('device_cap')
    if sample['temperature_c']>80: reasons.append('temperature_cap')
    if elapsed>=timeout: reasons.append('job_timeout')
    if now>=deadline: reasons.append('night_deadline')
    return reasons


def telemetry():
    p=subprocess.run(['nvidia-smi','--query-gpu=memory.used,temperature.gpu',
                      '--format=csv,noheader,nounits'],capture_output=True,text=True,timeout=5,check=True)
    lines=p.stdout.strip().splitlines()
    if len(lines)!=1: raise ValueError('exactly one GPU required')
    used,temp=map(float,lines[0].split(','))
    return {'ram_available_bytes':psutil.virtual_memory().available,
            'device_used_bytes':used*2**20,'temperature_c':temp}


def stop_own_tree(process,known):
    try: known.update({p.pid:p.create_time() for p in psutil.Process(process.pid).children(recursive=True)})
    except psutil.Error: pass
    known[process.pid]=known.get(process.pid)
    for pid,created in reversed(list(known.items())):
        if created is None: continue
        try:
            p=psutil.Process(pid)
            if abs(p.create_time()-created)<.01: p.kill()
        except psutil.Error: pass
    process.wait(timeout=10)


def run(command,*,timeout,host_estimate,device_estimate,output):
    initial=telemetry(); now=datetime.now(timezone.utc)
    reasons=violations(initial,now=now,deadline=DEADLINE,elapsed=0,timeout=timeout,
                       host_estimate=host_estimate,device_estimate=device_estimate)
    if (DEADLINE-now).total_seconds()<timeout+60: reasons.append('shutdown_margin')
    result={'scope':'own-child guard, not system safety guarantee','initial':initial,'reasons':reasons,
            'deadline_utc':DEADLINE.isoformat()}
    if not reasons:
        child=subprocess.Popen(command)
        known={child.pid:psutil.Process(child.pid).create_time()}; start=time.monotonic()
        result['child_pid']=child.pid; result['samples']=[]
        try:
            while child.poll() is None:
                known.update({p.pid:p.create_time() for p in psutil.Process(child.pid).children(recursive=True)})
                sample=telemetry(); elapsed=time.monotonic()-start
                result['samples'].append(sample)
                reasons=violations(sample,now=datetime.now(timezone.utc),deadline=DEADLINE,
                                   elapsed=elapsed,timeout=timeout)
                if reasons: break
                time.sleep(1)
        except psutil.NoSuchProcess:
            if child.poll() is None: reasons=['child_disappeared']
        except (OSError,ValueError,psutil.Error,subprocess.SubprocessError) as exc:
            reasons=['telemetry_or_process_error']; result['error_type']=type(exc).__name__
        finally:
            # Also clean any owned telemetry helper left behind by a normal exit.
            stop_own_tree(child,known)
        result.update(reasons=reasons,exit_code=child.wait(),elapsed_s=time.monotonic()-start)
    result['status']='rejected_or_stopped' if reasons else ('completed' if result['exit_code']==0 else 'child_failed')
    Path(output).write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    return result


def main():
    p=argparse.ArgumentParser(); p.add_argument('--timeout',type=int,default=120)
    p.add_argument('--estimated-host-gib',type=float,required=True)
    p.add_argument('--estimated-device-gib',type=float,required=True)
    p.add_argument('--output',required=True); p.add_argument('command',nargs=argparse.REMAINDER)
    a=p.parse_args(); command=a.command[1:] if a.command[:1]==['--'] else a.command
    if not command: p.error('child command required')
    r=run(command,timeout=a.timeout,host_estimate=a.estimated_host_gib*GIB,
          device_estimate=a.estimated_device_gib*GIB,output=a.output)
    print(json.dumps({'status':r['status'],'reasons':r['reasons']}))
    raise SystemExit(0 if r['status']=='completed' else 2)


if __name__=='__main__': main()
