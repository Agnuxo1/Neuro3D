"""New explicit-deadline OWN child supervisor, not the frozen night launcher.

Invoke only as gpuq's direct child. No CLI, no queue mutation or acquisition.
Injected adapters are explicitly CPU test evidence, never operational GPU proof.
"""
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import time

import psutil
from guarded_job import telemetry, stop_own_tree

GIB = 2**30
HOLDER = Path('D:/PROJECTS/.cognition/gpu_queue/holder.json')


def verify_holder_record(record, name, self_pid, self_birth, queue_birth):
    if not isinstance(name, str) or not name or not isinstance(record, dict):
        raise ValueError('named exclusive gpuq holder required')
    if any(type(record.get(k)) is not int for k in ('pid', 'child_pid')):
        raise ValueError('exact queue/child PID required')
    times = [record.get('ctime'), record.get('child_ctime'), self_birth, queue_birth]
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or
           not math.isfinite(v) or v <= 0 for v in times):
        raise ValueError('finite process birth identities required')
    if record.get('name') != name or record['child_pid'] != self_pid or \
            abs(record['child_ctime']-self_birth) >= .01 or \
            abs(record['ctime']-queue_birth) >= .01:
        raise ValueError('holder is not this direct supervised gpuq child')
    return {'name': name, 'queue_pid': record['pid'], 'child_pid': self_pid}


def assert_reservation(name):
    # Read-only. Never prune, cancel, create or release somebody else's ticket.
    record = json.loads(HOLDER.read_text(encoding='utf-8'))
    if psutil.Process().ppid() != record.get('pid') or \
            os.environ.get('GPUQ_HOLDER') != '1' or os.environ.get('GPUQ_NAME') != name:
        raise ValueError('real direct gpuq parent/environment required')
    return verify_holder_record(record, name, os.getpid(), psutil.Process().create_time(),
                                psutil.Process(record['pid']).create_time())


def validate_policy(deadline, timeout, now):
    if any(not isinstance(x, datetime) or x.tzinfo is None or
           x.utcoffset().total_seconds() != 0 for x in (now, deadline)):
        raise ValueError('explicit aware UTC deadline required')
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or \
            not math.isfinite(timeout) or not 0 < timeout <= 70:
        raise ValueError('scalar timeout must be positive and <=70s')
    remaining = (deadline-now).total_seconds()
    if not timeout+20 <= remaining <= 90:
        raise ValueError('new deadline <=90s with >=20s telemetry/cleanup margin required')


def resource_reasons(sample, *, before_launch):
    keys = ('ram_available_bytes', 'device_used_bytes', 'temperature_c')
    if not isinstance(sample, dict) or set(sample) != set(keys):
        raise ValueError('complete telemetry required')
    if any(isinstance(sample[k], bool) or not isinstance(sample[k], (int, float)) or
           not math.isfinite(sample[k]) or sample[k] < 0 for k in keys):
        raise ValueError('finite nonnegative telemetry required')
    # Fixed scalar pilot: 2GiB host reserve before launch, >=4GiB running floor.
    # Not a geometry scaling estimate. No geometry is constructed by this module.
    reasons = []
    if sample['ram_available_bytes']-(2*GIB if before_launch else 0) < 4*GIB:
        reasons.append('ram_floor')
    if sample['device_used_bytes']+(.25*GIB if before_launch else 0) > 18*GIB:
        reasons.append('vram_cap')
    if sample['temperature_c'] > 80: reasons.append('temperature_cap')
    return reasons


def write_once(path, value):
    text = json.dumps(value, indent=2, allow_nan=False)+'\n'
    with Path(path).open('x', encoding='utf-8') as out:
        out.write(text); out.flush(); os.fsync(out.fileno())


def run_owned(command, evidence, *, deadline, queue_name, timeout=60,
              sample=telemetry, reservation=assert_reservation):
    """Synchronous own subprocess only; production uses real queue+telemetry.

    CPU tests inject adapters but launch ONLY own lightweight Python children.
    Completed means process rc0, NOT valid scalar output/Blender/GPU execution.
    """
    started = datetime.now(timezone.utc)
    validate_policy(deadline, timeout, started)
    if not isinstance(command, (list, tuple)) or not command or \
            any(not isinstance(v, str) or not v for v in command):
        raise ValueError('explicit argv required; no shell')
    if not callable(sample) or not callable(reservation):
        raise ValueError('telemetry and reservation interfaces required')
    folder = Path(evidence); folder.mkdir(exist_ok=False)
    result = {'status': 'rejected', 'reasons': [], 'deadline_utc': deadline.isoformat(),
              'timeout_s': timeout, 'host_estimate_GiB': 2, 'device_estimate_GiB': .25,
              'command_sha256': hashlib.sha256(json.dumps(command).encode()).hexdigest(),
              'injected_test_adapters': sample is not telemetry or reservation is not assert_reservation,
              'runtime_execution_authenticated': False, 'native_promotion_allowed': False,
              'scope': 'own process supervision only, not numerical/GPU authentication',
              'no_jev_aval': True}
    write_once(folder/'initial.json', dict(result, status='in_progress'))
    child = None; known = {}; begin = time.monotonic(); result['samples'] = []
    try:
        result['reservation'] = reservation(queue_name)
        initial = sample()
        result['reasons'] = resource_reasons(initial, before_launch=True)
        result['samples'].append(initial)
        validate_policy(deadline, timeout, datetime.now(timezone.utc))
        if result['reasons']: return result
        with (folder/'stdout.txt').open('x', encoding='utf-8') as stdout, \
             (folder/'stderr.txt').open('x', encoding='utf-8') as stderr:
            child = subprocess.Popen(command, stdout=stdout, stderr=stderr, shell=False)
            result['child_pid'] = child.pid
            known[child.pid] = psutil.Process(child.pid).create_time()
            begin = time.monotonic()
            while child.poll() is None:
                reservation(queue_name)
                try:
                    known.update({p.pid: p.create_time() for p in
                                  psutil.Process(child.pid).children(recursive=True)})
                except psutil.NoSuchProcess:
                    if child.poll() is None: raise
                elapsed = time.monotonic()-begin
                reasons = []
                if not math.isfinite(elapsed) or elapsed < 0:
                    raise ValueError('invalid monotonic elapsed time')
                if elapsed >= timeout: reasons.append('child_timeout')
                if datetime.now(timezone.utc) >= deadline: reasons.append('job_deadline')
                if reasons: result['reasons'] = reasons; break
                value = sample()
                result['reasons'] = resource_reasons(value, before_launch=False)
                result['samples'].append(value)
                if result['reasons']: break
                time.sleep(.1)
            result['status'] = 'stopped' if result['reasons'] else 'exited'
    except Exception as error:
        result.update(status='rejected_or_stopped', error_type=type(error).__name__)
        result['reasons'].append('reservation_telemetry_or_process_error')
    finally:
        if child is not None:
            try:
                # Frozen helper has PID+birth checks; historical DEADLINE not used.
                if child.pid not in known and child.poll() is None:
                    child.kill()  # Owned Popen handle, not an unverified external PID.
                stop_own_tree(child, known)
                result['exit_code'] = child.wait(timeout=5)
                result['cleanup_completed'] = True
            except Exception as error:
                result.update(status='cleanup_failed', cleanup_completed=False,
                              cleanup_error_type=type(error).__name__)
            if result['status'] == 'exited':
                result['status'] = 'completed' if result.get('exit_code') == 0 else 'child_failed'
        result['elapsed_s'] = time.monotonic()-begin
        write_once(folder/'final.json', result)
    return result
