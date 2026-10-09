"""Owned, bounded jobs; no Blender imports or global process termination."""
import ctypes
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def read_json(path, limit=64 * 2**20):
    raw = Path(path).read_bytes()
    if len(raw) > limit:
        raise ValueError('Archivo de evidencia demasiado grande')
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('Clave JSON duplicada')
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=lambda _: (_ for _ in ()).throw(ValueError('JSON no finito')))


def free_ram_mib():
    if os.name == 'nt':
        class Memory(ctypes.Structure):
            _fields_ = [('length', ctypes.c_ulong), ('load', ctypes.c_ulong)] + [(name, ctypes.c_ulonglong) for name in ('total', 'available', 'total_page', 'available_page', 'total_virtual', 'available_virtual', 'extended')]
        record = Memory(); record.length = ctypes.sizeof(record)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(record)):
            raise OSError('No se pudo medir la RAM libre')
        return record.available / 2**20
    if Path('/proc/meminfo').exists():
        rows = dict(line.split(':', 1) for line in Path('/proc/meminfo').read_text().splitlines())
        return int(rows['MemAvailable'].split()[0]) / 1024
    raise OSError('La supervisión de RAM requiere Windows o Linux')


def rss_mib(pid):
    if os.name == 'nt':
        class Counters(ctypes.Structure):
            _fields_ = [('cb', ctypes.c_ulong), ('faults', ctypes.c_ulong)] + [(name, ctypes.c_size_t) for name in ('peak_working', 'working', 'peak_paged', 'paged', 'peak_nonpaged', 'nonpaged', 'pagefile', 'peak_pagefile')]
        kernel = ctypes.windll.kernel32
        kernel.OpenProcess.restype = ctypes.c_void_p
        kernel.OpenProcess.argtypes = [ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong]
        kernel.CloseHandle.argtypes = [ctypes.c_void_p]
        process = kernel.OpenProcess(0x410, False, pid)
        if not process:
            raise OSError('No se pudo medir el proceso propio')
        try:
            record = Counters(); record.cb = ctypes.sizeof(record)
            ctypes.windll.psapi.GetProcessMemoryInfo.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong]
            if not ctypes.windll.psapi.GetProcessMemoryInfo(process, ctypes.byref(record), record.cb):
                raise OSError('No se pudo medir el RSS propio')
            return record.working / 2**20
        finally:
            kernel.CloseHandle(process)
    return int(Path(f'/proc/{pid}/statm').read_text().split()[1]) * os.sysconf('SC_PAGE_SIZE') / 2**20


class OwnedJob:
    """Only the explicitly spawned process can be stopped. Files remain recoverable."""
    def __init__(self, command, folder, *, deadline=1800, ram_floor=2500, rss_limit=1500):
        self.folder = Path(folder).resolve()
        self.deadline, self.ram_floor, self.rss_limit = deadline, ram_floor, rss_limit
        if not self.folder.is_dir() or (self.folder / 'supervision.json').exists():
            raise ValueError('Se necesita una carpeta nueva de trabajo')
        if free_ram_mib() < 4000:
            raise ValueError('Se requieren 4000 MiB de RAM libre para iniciar')
        self.stream = (self.folder / 'worker.stdout').open('xb')
        env = dict(os.environ, OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
        flags = subprocess.CREATE_NO_WINDOW | subprocess.BELOW_NORMAL_PRIORITY_CLASS if os.name == 'nt' else 0
        try:
            self.process = subprocess.Popen(command, stdout=self.stream, stderr=subprocess.STDOUT, env=env, creationflags=flags, stdin=subprocess.DEVNULL)
        except Exception:
            self.stream.close()
            raise
        self.started = time.monotonic(); self.peak_rss = 0.0; self.state = 'RUNNING'; self.reason = None

    def _finish(self, state, reason=None):
        self.state, self.reason = state, reason
        self.stream.close()
        receipt = {'schema': 'optic_neuro_blender.owned_job.v1', 'state': state, 'reason': reason,
                   'owned_pid': self.process.pid, 'exit_code': self.process.returncode,
                   'seconds': time.monotonic() - self.started, 'peak_rss_mib': self.peak_rss,
                   'owned_process_terminated': self.process.poll() is not None, 'result_collected': state == 'COMPLETED'}
        if state == 'COMPLETED':
            receipt['result_sha256'] = hashlib.sha256((self.folder / 'result.json').read_bytes()).hexdigest()
        (self.folder / 'supervision.json').write_bytes(canonical(receipt))
        return state

    def cancel(self, reason='USER_CANCELLED'):
        if self.state != 'RUNNING':
            return self.state
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.kill(); self.process.wait(timeout=3)
        return self._finish('CANCELLED', reason)

    def poll(self):
        if self.state != 'RUNNING':
            return self.state
        code = self.process.poll()
        if code is not None:
            return self._finish('COMPLETED' if code == 0 and (self.folder / 'result.json').exists() else 'FAILED', None if code == 0 else 'WORKER_FAILED')
        try:
            self.peak_rss = max(self.peak_rss, rss_mib(self.process.pid))
            elapsed = time.monotonic() - self.started
            reason = 'DEADLINE' if elapsed > self.deadline else 'RAM_FLOOR' if free_ram_mib() < self.ram_floor else 'OWNED_RSS' if self.peak_rss > self.rss_limit else None
            if sum(path.stat().st_size for path in self.folder.rglob('*') if path.is_file()) > 128 * 2**20:
                reason = 'EVIDENCE_LIMIT'
            if reason:
                return self.cancel(reason)
        except OSError:
            if self.process.poll() is not None:
                return self.poll()
            return self.cancel('RESOURCE_MEASUREMENT_UNAVAILABLE')
        return self.state
