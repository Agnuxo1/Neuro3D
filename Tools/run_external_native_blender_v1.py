"""Prospectively pinned actual Linux Blender installation/training reproduction."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from Tools.bind_network_capture_v1 import read_json
from Tools.run_frozen_state_graph_profile_v1 import check_registration
from Tools.audit_captured_pilot_result_v1 import need

LIMITS = {'total_seconds': 2200, 'preparation_seconds': 600, 'native_seconds': 1500,
          'free_ram_before_mib': 4000, 'free_ram_floor_mib': 2500, 'owned_rss_mib': 2000,
          'evidence_mib': 256, 'archive_mib': 1024, 'cpu_cores': 1, 'gpu': False}


def sha(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        while chunk := stream.read(2**20):
            value.update(chunk)
    return value.hexdigest()


def validate(path, registration):
    profile, pin = read_json(path, 65536)
    need(profile['schema'] == 'optic_neuro_blender.external_native_profile.v1' and profile['limits'] == LIMITS, 'Fixed external native profile required')
    need(profile['power_tolerance'] == 1e-11 and profile['blender_version_numeric'] == [4, 5, 14], 'Fixed native version/tolerance required')
    need(profile['archive_relative'] == 'Blender/releases/optic-neuro-blender-0.1.2.zip', 'Fixed standalone package required')
    for name, expected in profile['pins'].items():
        source = (ROOT / name).resolve()
        need(source.is_relative_to(ROOT) and source.is_file() and sha(source) == expected, 'Native source pin mismatch:' + name)
    need({profile['archive_relative'], profile['worker'], 'Tools/run_external_native_blender_v1.py',
          'Tools/prepare_official_linux_blender_v1.py', 'Tools/audit_installed_own_blender_addon_v3.py',
          profile['workflow'], profile['requirements']} <= set(profile['pins']), 'Critical native source pins required')
    record, rpin = read_json(registration, 65536)
    check_registration(record, profile, pin)
    need(record['human_sequence_approval_sha256'] == sha(ROOT / record['evidence_reference']), 'Human continuity receipt mismatch')
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    need(commit == os.environ.get('GITHUB_SHA', commit), 'Git checkout/event mismatch')
    all_pins = dict(profile['pins'])
    for source in (path, registration):
        source = source.resolve(); need(source.is_relative_to(ROOT), 'Repository profile/receipt required')
        all_pins[source.relative_to(ROOT).as_posix()] = sha(source)
    for name, expected in all_pins.items():
        blob = subprocess.check_output(['git', 'show', commit + ':' + name], cwd=ROOT)
        need(hashlib.sha256(blob).hexdigest() == expected and blob == (ROOT / name).read_bytes(), 'Published Git blob mismatch:' + name)
    return profile, pin, rpin, {'published_commit': commit, 'git_blob_byte_identity': True, 'pins_including_profile_registration': len(all_pins)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--profile', type=Path, required=True)
    parser.add_argument('--registration', type=Path, required=True)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--verify-only', action='store_true')
    args = parser.parse_args()
    profile, pin, rpin, publication = validate(args.profile, args.registration)
    if args.verify_only:
        print(json.dumps(publication), flush=True); return 0
    need(args.out is not None, 'New evidence directory required')
    out = args.out.resolve(); out.mkdir(exist_ok=False)
    started = time.monotonic(); process = None; owned = {}; code = 3; peak = 0
    report = {'schema': 'optic_neuro_blender.external_native_supervision.v1',
              'status': 'NOT_EXECUTED', 'primary_metric': None, 'native_blender_executed': False,
              'gpu_executed': False, 'independent_human_replication': False,
              'external_registration_obtained': False, 'profile_sha256': pin,
              'registration_sha256': rpin, **publication}
    temporary = None
    try:
        import psutil
        need(sys.platform.startswith('linux') and platform.machine() == 'x86_64', 'Actual Linux x86_64 required')
        need(list(sys.version_info[:3]) == [3, 12, 12] and psutil.__version__ == '7.0.0', 'Fixed supervisor runtime required')
        report.update(preflight_free_ram_mib=psutil.virtual_memory().available / 2**20,
                      supervisor_runtime={'python': sys.version, 'psutil': psutil.__version__, 'platform': platform.platform()},
                      github={key: os.environ.get(key) for key in ('GITHUB_RUN_ID', 'GITHUB_RUN_ATTEMPT', 'GITHUB_SHA', 'RUNNER_OS', 'RUNNER_ARCH')})
        need(report['preflight_free_ram_mib'] >= LIMITS['free_ram_before_mib'], 'Native RAM preflight rejected')
        for name in profile['pins']:
            target = out / 'source' / name; target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)
        shutil.copyfile(args.profile, out / 'profile.json'); shutil.copyfile(args.registration, out / 'registration.json')
        temporary = tempfile.TemporaryDirectory(prefix='optic-neuro-native-')
        prepared = Path(temporary.name) / 'official'
        env = dict(os.environ, BLENDER_USER_SCRIPTS=str(out / 'isolated/scripts'),
                   BLENDER_USER_CONFIG=str(out / 'isolated/config'),
                   OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
        Path(env['BLENDER_USER_SCRIPTS']).mkdir(parents=True); Path(env['BLENDER_USER_CONFIG']).mkdir(parents=True)
        report['stages'] = []

        def stage(name, command, budget):
            nonlocal process, owned, peak
            owned = {}; stop = None; stage_start = time.monotonic()
            with (out / (name + '.stdout')).open('xb') as stream:
                process = subprocess.Popen(command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, env=env)
                parent = psutil.Process(process.pid); owned[parent.pid] = parent
                parent.cpu_affinity([psutil.Process().cpu_affinity()[0]])
                while process.poll() is None:
                    try:
                        for child in parent.children(recursive=True): owned[child.pid] = child
                    except psutil.NoSuchProcess:
                        break
                    total = 0
                    for item in list(owned.values()):
                        try: total += item.memory_info().rss
                        except psutil.NoSuchProcess: pass
                    peak = max(peak, total)
                    if time.monotonic() - stage_start > budget or time.monotonic() - started > LIMITS['total_seconds']: stop = 'DEADLINE'
                    elif total > LIMITS['owned_rss_mib'] * 2**20: stop = 'OWNED_AGGREGATE_RSS'
                    elif psutil.virtual_memory().available < LIMITS['free_ram_floor_mib'] * 2**20: stop = 'RAM_FLOOR'
                    elif sum(path.stat().st_size for path in out.rglob('*') if path.is_file()) > LIMITS['evidence_mib'] * 2**20: stop = 'EVIDENCE_LIMIT'
                    if stop:
                        for item in reversed(list(owned.values())):
                            try: item.kill()
                            except psutil.NoSuchProcess: pass
                        break
                    time.sleep(.2)
                process.wait(timeout=10)
            report['stages'].append({'name': name, 'seconds': time.monotonic() - stage_start, 'exit_code': process.returncode, 'stopped': stop})
            need(stop is None and process.returncode == 0, 'External native stage failed:' + name)

        stage('preparation', [sys.executable, '-X', 'utf8', str(ROOT / 'Tools/prepare_official_linux_blender_v1.py'),
                             '--profile', str(args.profile.resolve()), '--directory', str(prepared),
                             '--receipt', str(out / 'official_binary_receipt.json')], LIMITS['preparation_seconds'])
        receipt, _ = read_json(out / 'official_binary_receipt.json', 65536)
        executable = Path(receipt['executable'])
        need(sha(executable) == profile['official_blender']['binary_sha256'], 'Prepared native binary mismatch')
        runtime = dict(profile, archive=str((ROOT / profile['archive_relative']).resolve()))
        runtime_path = out / 'runtime_profile.json'; runtime_path.write_bytes((json.dumps(runtime, indent=2) + '\n').encode())
        report['native_blender_executed'] = True
        stage('native', [str(executable), '--background', '--factory-startup', '--disable-autoexec', '--threads', '1', '-noaudio',
                         '--python-exit-code', '3', '--python', str(ROOT / profile['worker']), '--', str(runtime_path), str(out / 'worker')], LIMITS['native_seconds'])
        log = (out / 'native.stdout').read_text(encoding='utf-8', errors='replace')
        need(not any(marker in log for marker in ('Traceback (most recent call last)', 'RuntimeError:', 'Exception in module unregister')), 'Post-exit native lifecycle/log failure')
        result, resultpin = read_json(out / 'worker/result.json', 128 * 2**20)
        need(result['status'] == 'PASS' and result['archive_sha256'] == profile['archive_sha256'], 'Native result identity mismatch')
        need(len(result['checks']) == 9 and all(row['pass'] for row in result['checks']), 'Nine actual native controls required')
        need(result['external_runtime']['machine'] == 'x86_64' and result['external_runtime']['platform'].startswith('Linux'), 'Actual external native runtime missing')
        validate(args.profile, args.registration)
        report.update(status='VALID_EXTERNAL_NATIVE_BLENDER_REPRODUCTION', primary_metric=1,
                      result_sha256=resultpin, runtime_profile_sha256=sha(runtime_path),
                      checks=result['checks'], native_runtime=result['external_runtime'],
                      post_exit_log_checked=True, peak_owned_aggregate_rss_mib=peak / 2**20,
                      scope='Official checksum-pinned Linux Blender, isolated standalone ZIP0.1.2, all nine actual native controls, own training61audits and recovery. Setup/preparation/native/full-worker costs retained; external environment is not independent human replication, GPU or physical proof.')
        code = 0
    except Exception as exc:
        report.update(status='INCONCLUSIVE_EXTERNAL_NATIVE_ENVIRONMENT_OR_INVALID_OUTPUT', failure_type=type(exc).__name__)
        if isinstance(exc, ValueError): report['reason'] = str(exc)
    finally:
        if process is not None and process.poll() is None: process.kill(); process.wait(timeout=10)
        for item in reversed(list(owned.values())):
            try:
                if item.is_running(): item.kill(); item.wait(timeout=5)
            except (psutil.NoSuchProcess, psutil.TimeoutExpired): pass
        if temporary is not None: temporary.cleanup()
        report['owned_worker_cleaned_up'] = process is None or process.poll() is not None
        report['seconds'] = time.monotonic() - started
        report['raw_file_sha256'] = {path.relative_to(out).as_posix(): sha(path) for path in out.rglob('*') if path.is_file() and '__pycache__' not in path.parts}
        (out / 'result.json').write_bytes((json.dumps(report, indent=2) + '\n').encode())
        print(json.dumps({key: report.get(key) for key in ('status', 'primary_metric', 'seconds', 'reason')}), flush=True)
    return code


if __name__ == '__main__':
    raise SystemExit(main())
