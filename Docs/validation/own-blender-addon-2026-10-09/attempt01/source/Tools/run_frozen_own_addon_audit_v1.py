"""Bounded actual install audit, including every owned descendant Blender."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from Tools.bind_network_capture_v1 import read_json
from Tools.run_frozen_state_graph_profile_v1 import check_registration
from Tools.audit_captured_pilot_result_v1 import need

LIMITS = {'worker_seconds': 1500, 'free_ram_before_mib': 4000, 'free_ram_floor_mib': 2500, 'owned_rss_mib': 2000, 'evidence_mib': 128, 'cpu_cores': 1, 'gpu': False}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(path):
    profile, pin = read_json(path, 65536)
    need(profile['schema'] == 'optic_neuro_blender.installed_addon_profile.v1' and profile['limits'] == LIMITS, 'fixed own addon profile and budgets required')
    need(profile['worker'] == 'Tools/audit_installed_own_blender_addon_v1.py' and profile['power_tolerance'] == 1e-11, 'fixed own native worker/tolerance required')
    for name, expected in profile['pins'].items():
        source = (ROOT / name).resolve()
        need(source.is_relative_to(ROOT) and source.is_file() and sha(source) == expected, 'addon sourcepin mismatch: ' + name)
    need({profile['worker'], 'Tools/run_frozen_own_addon_audit_v1.py', 'Tools/build_own_blender_addon_v1.py', profile['archive_relative']} <= set(profile['pins']), 'critical installed package sources required')
    archive = (ROOT / profile['archive_relative']).resolve()
    need(sha(archive) == profile['archive_sha256'], 'frozen archive mismatch')
    executable = Path(profile['blender_executable'])
    need(executable.is_file() and sha(executable) == profile['blender_executable_sha256'], 'Blender binary pin mismatch')
    return profile, pin


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--profile', type=Path, required=True); parser.add_argument('--registration', type=Path, required=True); parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(); out = args.out.resolve(); out.mkdir(exist_ok=False)
    process = None; owned = {}; code = 3
    report = {'schema': 'optic_neuro_blender.installed_addon_supervision.v1', 'status': 'NOT_EXECUTED', 'worker_started': False, 'result_collected': False, 'primary_metric': None}
    try:
        import psutil
        profile, pin = validate(args.profile)
        registration, rpin = read_json(args.registration, 65536); check_registration(registration, profile, pin)
        report.update(profile_sha256=pin, registration_sha256=rpin, preflight_free_ram_mib=psutil.virtual_memory().available / 2**20)
        need(report['preflight_free_ram_mib'] >= LIMITS['free_ram_before_mib'], 'RAM preflight rejected')
        for name in profile['pins']:
            target = out / 'source' / name; target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(ROOT / name, target)
        shutil.copyfile(args.profile, out / 'profile.json'); shutil.copyfile(args.registration, out / 'registration.json')
        runtime_profile = dict(profile, archive=str((ROOT / profile['archive_relative']).resolve()))
        runtime_path = out / 'runtime_profile.json'; runtime_path.write_bytes((json.dumps(runtime_profile, indent=2) + '\n').encode())
        env = dict(os.environ, BLENDER_USER_SCRIPTS=str(out / 'isolated/scripts'), BLENDER_USER_CONFIG=str(out / 'isolated/config'), OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
        Path(env['BLENDER_USER_SCRIPTS']).mkdir(parents=True); Path(env['BLENDER_USER_CONFIG']).mkdir(parents=True)
        command = [profile['blender_executable'], '--background', '--factory-startup', '--disable-autoexec', '--threads', '1', '-noaudio', '--python-exit-code', '3', '--python', str(ROOT / profile['worker']), '--', str(runtime_path), str(out / 'worker')]
        start = time.monotonic(); peak = 0; stop = None
        with (out / 'blender.log').open('xb') as stream:
            process = subprocess.Popen(command, stdout=stream, stderr=subprocess.STDOUT, cwd=ROOT, env=env, creationflags=subprocess.CREATE_NO_WINDOW | subprocess.BELOW_NORMAL_PRIORITY_CLASS if os.name == 'nt' else 0)
            parent = psutil.Process(process.pid); parent.cpu_affinity([psutil.Process().cpu_affinity()[0]])
            owned[parent.pid] = parent; report['worker_started'] = True
            while process.poll() is None:
                try:
                    for child in parent.children(recursive=True):
                        owned[child.pid] = child
                except psutil.NoSuchProcess:
                    break
                total = 0
                for pid, item in list(owned.items()):
                    try:
                        if item.is_running():
                            total += item.memory_info().rss
                    except psutil.NoSuchProcess:
                        pass
                peak = max(peak, total)
                if time.monotonic() - start > LIMITS['worker_seconds']:
                    stop = 'DEADLINE'
                elif total > LIMITS['owned_rss_mib'] * 2**20:
                    stop = 'OWNED_AGGREGATE_RSS'
                elif psutil.virtual_memory().available < LIMITS['free_ram_floor_mib'] * 2**20:
                    stop = 'RAM_FLOOR'
                elif sum(path.stat().st_size for path in (out / 'worker').rglob('*') if path.is_file()) > LIMITS['evidence_mib'] * 2**20:
                    stop = 'EVIDENCE_LIMIT'
                if stop:
                    break
                time.sleep(.2)
            if stop:
                for item in reversed(list(owned.values())):
                    try:
                        item.kill()
                    except psutil.NoSuchProcess:
                        pass
            process.wait(timeout=5)
        report.update(worker_seconds=time.monotonic() - start, worker_exit_code=process.returncode, peak_owned_aggregate_rss_mib=peak / 2**20, stopped=stop, owned_pids=list(owned))
        need(stop is None and process.returncode == 0, 'native addon audit did not complete')
        _, after = validate(args.profile); need(after == pin and sha(args.registration) == rpin, 'profile or registration changed')
        result, resultpin = read_json(out / 'worker/result.json', 128 * 2**20)
        need(result['schema'] == 'optic_neuro_blender.installed_native_audit.v1' and result['status'] == 'PASS' and result['archive_sha256'] == profile['archive_sha256'], 'native addon result mismatch')
        need(len(result['checks']) == 9 and all(row['pass'] for row in result['checks']), 'all nine native controls required')
        report.update(status='VALID_INSTALLED_NATIVE_ADDON_AUDIT', primary_metric=1, result_collected=True, result_sha256=resultpin, runtime_profile_sha256=sha(runtime_path)); code = 0
    except Exception as exc:
        report.update(failure_type=type(exc).__name__, status='INCONCLUSIVE_ENVIRONMENT_OR_INVALID_OUTPUT' if report['worker_started'] else 'NOT_EXECUTED')
        if isinstance(exc, ValueError):
            report['reason'] = str(exc)
    finally:
        if process is not None and process.poll() is None:
            process.kill(); process.wait(timeout=5)
        for item in reversed(list(owned.values())):
            try:
                if item.is_running():
                    item.kill(); item.wait(timeout=5)
            except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                pass
        report['owned_worker_cleaned_up'] = process is None or process.poll() is not None
        report['raw_file_sha256'] = {path.relative_to(out).as_posix(): sha(path) for path in out.rglob('*') if path.is_file() and '__pycache__' not in path.parts}
        (out / 'supervisor.json').write_bytes((json.dumps(report, indent=2) + '\n').encode())
        print(json.dumps({key: report.get(key) for key in ('status', 'primary_metric', 'worker_seconds', 'peak_owned_aggregate_rss_mib', 'reason')}), flush=True)
    return code


if __name__ == '__main__':
    raise SystemExit(main())
