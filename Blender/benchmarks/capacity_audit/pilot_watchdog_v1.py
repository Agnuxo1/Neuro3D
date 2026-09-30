"""Own pilot supervisor with a NEW deadline; no GPU/Blender entry point.

Caller admission and artifact gates remain separate. Default admission rejects
everything. Tracked-process cleanup is NOT Windows Job Object containment.
"""
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import subprocess
import time

import psutil
from guarded_job import violations


def reject_admission():
    raise ValueError('exclusive-job admission adapter required; no launch authorized')


def sample_unavailable():
    raise ValueError('fresh resource telemetry adapter required')


def utc_now():
    return datetime.now(timezone.utc)


def observe(child, known):
    try:
        root = psutil.Process(child.pid)
        identity = root.create_time()
        if child.pid in known and identity != known[child.pid]:
            raise ValueError('root PID identity changed')
        known[child.pid] = identity
        for process in root.children(recursive=True):
            known[process.pid] = process.create_time()
    except psutil.NoSuchProcess:
        if child.poll() is None:
            raise ValueError('running child identity unavailable')


def close_tracked(child, known):
    """Never kill by a bare PID. Do not enumerate other projects/processes."""
    observe(child, known)
    live = []
    for pid, created in reversed(list(known.items())):
        try:
            process = psutil.Process(pid)
            if process.create_time() == created:
                process.kill()
                live.append(process)
        except psutil.NoSuchProcess:
            continue
    _, alive = psutil.wait_procs(live, timeout=3)
    child.wait(timeout=3)
    return not alive


def resource_check(sample, deadline, elapsed, timeout, now, host=0, device=0):
    if set(sample) != {'ram_available_bytes', 'device_used_bytes', 'temperature_c'}:
        raise ValueError('missing or unexpected telemetry')
    reasons = violations(sample, now=now, deadline=deadline, elapsed=elapsed,
                         timeout=timeout, host_estimate=host, device_estimate=device)
    return ['job_deadline' if reason == 'night_deadline' else reason for reason in reasons]


def supervise(command, *, envelope, deadline, timeout, host_budget, device_budget,
              admit=reject_admission, sample=sample_unavailable, now=utc_now):
    """Private bounded command; envelope exclusive before launch, finalized once.

    CPU tests explicitly supply fake admission/resources. There is no CLI nor
    production adapter capable of granting GPU admission in this version.
    """
    envelope = Path(envelope)
    result = {'scope': 'own pilot supervision; NOT artifact/GPU correctness certification',
              'status': 'rejected', 'reasons': [], 'child_started': False,
              'tracked_children_closed': False, 'full_tree_containment_certified': False,
              'deadline_utc': str(deadline), 'samples': [], 'no_jev_aval': True}
    child = None
    known = {}
    start = time.monotonic()
    # Failure to create the mandatory envelope prevents any launch.
    with envelope.open('x', encoding='utf-8') as output:
        try:
            if not command or not all(isinstance(arg, str) for arg in command):
                raise ValueError('explicit argument vector required')
            if any(type(value) not in (int,float) or not math.isfinite(value) or value < 0
                   for value in (timeout, host_budget, device_budget)) or not 0 < timeout <= 110:
                raise ValueError('bounded finite pilot policy required')
            clock = now()
            if any(not isinstance(value,datetime) or value.tzinfo is None or value.utcoffset().total_seconds()!=0
                   for value in (clock, deadline)):
                raise ValueError('explicit UTC clocks required')
            if not timeout+7 <= (deadline-clock).total_seconds() <= 120:
                raise ValueError('new deadline requires bounded child plus seven-second close margin')
            admit()
            initial = sample()
            reasons = resource_check(initial, deadline, time.monotonic()-start, timeout,
                                     now(), host_budget, device_budget)
            result['initial'] = dict(initial)
            if reasons:
                result['reasons'] = reasons
            else:
                # Admission must revalidate reservation, command/pins and process
                # inventory immediately before Popen, not just at plan preparation.
                admit()
                if (deadline-now()).total_seconds() < timeout+7:
                    raise ValueError('launch margin exhausted')
                child = subprocess.Popen(command, stdin=subprocess.DEVNULL,
                                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                result.update(child_started=True, child_pid=child.pid)
                while True:
                    observe(child, known)
                    reading = sample()
                    elapsed = time.monotonic()-start
                    reasons = resource_check(reading, deadline, elapsed, timeout, now())
                    result['samples'].append(dict(reading))
                    code = child.poll()
                    if reasons:
                        result['reasons'] = reasons
                        break
                    if code is not None:
                        result['exit_code'] = code
                        result['status'] = 'completed' if code == 0 else 'child_failed'
                        break
                    time.sleep(.05)
        except Exception as error:
            result['status'] = 'failed_closed'
            result['reasons'].append('admission_resource_or_process_error')
            result['error_type'] = type(error).__name__
            # No raw diagnostics/command/environment (could contain secrets).
        finally:
            if child is not None:
                try:
                    result['tracked_children_closed'] = close_tracked(child, known)
                    result['exit_code'] = child.returncode
                except Exception as error:
                    result['reasons'].append('tracked_cleanup_failed')
                    result['cleanup_error_type'] = type(error).__name__
            elapsed = time.monotonic()-start
            result.update(elapsed_s=elapsed, tracked_identities=known)
            try:
                if now() >= deadline:result['reasons'].append('late_finalization')
                if elapsed >= timeout:result['reasons'].append('monotonic_timeout')
            except Exception:
                result['reasons'].append('final_clock_failed')
            if result['reasons'] or (child is not None and not result['tracked_children_closed']):
                result['status'] = 'failed_closed'
            output.write(json.dumps(result, indent=2, allow_nan=False)+'\n')
            output.flush()
    return result
