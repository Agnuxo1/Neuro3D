"""Frozen GitHub-hosted Linux CPU reproduction; never an independent-human claim."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from Tools.bind_network_capture_v1 import read_json
from Tools.run_frozen_state_graph_profile_v1 import check_registration
from Tools.audit_captured_pilot_result_v1 import need

LIMITS = {'total_seconds': 1500, 'control_seconds': 120, 'certificate_seconds': 120, 'training_seconds': 900, 'free_ram_before_mib': 4000, 'free_ram_floor_mib': 2500, 'owned_rss_mib': 1500, 'evidence_mib': 128, 'cpu_cores': 1, 'gpu': False}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_profile(path):
    profile, pin = read_json(path, 65536)
    need(profile['schema'] == 'optic_neuro_blender.external_cpu_profile.v1' and profile['limits'] == LIMITS, 'fixed external CPU profile/budgets required')
    need(profile['python_version'] == [3, 12, 12] and profile['packages'] == {'numpy': '2.2.6', 'psutil': '7.0.0', 'mpmath': '1.3.0'}, 'fixed CPU runtime required')
    for name, expected in profile['pins'].items():
        path = (ROOT / name).resolve()
        need(path.is_relative_to(ROOT) and path.is_file() and sha(path) == expected, 'external sourcepin mismatch:' + name)
    need({'Tools/run_external_cpu_reproduction_v1.py', profile['training_profile'], profile['training_registration'], profile['reference_training_result'], profile['requirements']} <= set(profile['pins']), 'critical reproduction sources required')
    return profile, pin


def verify_publication(profile, path, registration_path):
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    declared = os.environ.get('GITHUB_SHA', commit)
    need(commit == declared, 'Git checkout does not match workflow event')
    pins = dict(profile['pins'])
    for item in (path, registration_path):
        item = item.resolve(); need(item.is_relative_to(ROOT), 'repository profile/receipt required')
        pins[item.relative_to(ROOT).as_posix()] = sha(item)
    for name, expected in pins.items():
        blob = subprocess.check_output(['git', 'show', commit + ':' + name], cwd=ROOT)
        need(hashlib.sha256(blob).hexdigest() == expected and blob == (ROOT / name).read_bytes(), 'published Git blob mismatch:' + name)
    return {'published_commit': commit, 'git_blob_byte_identity': True, 'pins_including_profile_registration': len(pins)}


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--profile', type=Path, required=True); parser.add_argument('--registration', type=Path, required=True); parser.add_argument('--out', type=Path); parser.add_argument('--verify-only', action='store_true'); parser.add_argument('--validate-only', action='store_true')
    args = parser.parse_args()
    profile, pin = validate_profile(args.profile)
    registration, rpin = read_json(args.registration, 65536); check_registration(registration, profile, pin)
    if args.validate_only:
        print(json.dumps({'profile_valid': True, 'profile_sha256': pin, 'registration_sha256': rpin})); return 0
    published = verify_publication(profile, args.profile, args.registration)
    if args.verify_only:
        print(json.dumps(published)); return 0
    need(args.out is not None, 'new output directory required')
    out = args.out.resolve(); out.mkdir(exist_ok=False)
    process = None; owned = {}; started = time.monotonic(); code = 3
    report = {'schema': 'optic_neuro_blender.external_cpu_reproduction.v1', 'status': 'NOT_EXECUTED', 'primary_metric': None, 'gpu_executed': False, 'native_blender_executed': False, 'independent_human_replication': False, 'external_registration_obtained': False, **published}
    try:
        import numpy as np
        import psutil
        import mpmath
        need(sys.platform.startswith('linux') and platform.machine() == 'x86_64' and list(sys.version_info[:3]) == profile['python_version'], 'declared Linux x86_64/Python runtime required')
        versions = {'numpy': np.__version__, 'psutil': psutil.__version__, 'mpmath': mpmath.__version__}
        need(versions == profile['packages'], 'installed dependency version mismatch')
        report.update(profile_sha256=pin, registration_sha256=rpin, runtime={'python': sys.version, 'packages': versions, 'platform': platform.platform(), 'machine': platform.machine()}, github={key: os.environ.get(key) for key in ('GITHUB_RUN_ID', 'GITHUB_RUN_ATTEMPT', 'GITHUB_SHA', 'GITHUB_WORKFLOW', 'RUNNER_OS', 'RUNNER_ARCH')}, preflight_free_ram_mib=psutil.virtual_memory().available / 2**20)
        need(report['preflight_free_ram_mib'] >= LIMITS['free_ram_before_mib'], 'external RAM preflight rejected')
        stages = [
            ('controls', [sys.executable, '-X', 'utf8', '-m', 'unittest', *profile['control_modules'], '-v'], LIMITS['control_seconds']),
            ('certificate', [sys.executable, '-X', 'utf8', 'Tools/certify_captured_graph_outputs_v1.py', '--scene', profile['certificate_scene'], '--result', profile['certificate_graph_result'], '--out', str(out / 'certificate.json')], LIMITS['certificate_seconds']),
            ('training', [sys.executable, '-X', 'utf8', 'Tools/run_frozen_geometry_training_v1.py', '--profile', profile['training_profile'], '--registration', profile['training_registration'], '--out', str(out / 'training')], LIMITS['training_seconds'] + 15),
        ]
        report['stages'] = []; peak = 0
        env = dict(os.environ, OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
        for name, command, budget in stages:
            stop = None; stage_start = time.monotonic(); owned = {}
            with (out / (name + '.stdout')).open('xb') as stream:
                process = subprocess.Popen(command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, env=env)
                parent = psutil.Process(process.pid); parent.cpu_affinity([psutil.Process().cpu_affinity()[0]]); owned[parent.pid] = parent
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
                process.wait(timeout=5)
            report['stages'].append({'name': name, 'seconds': time.monotonic() - stage_start, 'exit_code': process.returncode, 'stopped': stop})
            need(stop is None and process.returncode == 0, 'external stage failed:' + name)
        certificate = read_json(out / 'certificate.json', 64 * 2**20)[0]
        training = read_json(out / 'training/worker/result.json', 64 * 2**20)[0]
        supervision = read_json(out / 'training/supervisor.json', 64 * 2**20)[0]
        reference = read_json(ROOT / profile['reference_training_result'], 64 * 2**20)[0]
        need(certificate['status'] == 'CERTIFIED_OBSERVED_REPRESENTED_OUTPUTS', 'independent certificate replay failed')
        need(supervision['status'] == 'VALID_FROZEN_TRAINING_PROFILE_RESULT' and supervision['primary_metric'] in (0, 1), 'external training outcome invalid')
        difference = float(np.max(np.abs(np.asarray(training['observed_powers']) - np.asarray(reference['observed_powers']))))
        validate_profile(args.profile); verify_publication(profile, args.profile, args.registration)
        report.update(status='VALID_EXTERNAL_CPU_REPRODUCTION_RESULT', primary_metric=supervision['primary_metric'], peak_owned_aggregate_rss_mib=peak / 2**20,
                      train_correct=training['train_correct'], test_correct=training['test_correct'], geometry_audited_states=training['geometry_audited_states'],
                      prediction_agreement_with_local_reference=int(np.sum(np.asarray(training['predictions']) == np.asarray(reference['predictions']))),
                      max_power_difference_with_local_reference=difference,
                      reference_trajectory_equality_required=False,
                      scope='GitHub-hosted Linux CPU repeat of frozen represented geometry training, selected adverse software controls and independent rational certificate replay. Cross-runtime optimizer differences retained. No native Blender/GPU, outside specialist or physical proof.'); code = 0
    except Exception as exc:
        report.update(status='INCONCLUSIVE_EXTERNAL_ENVIRONMENT_OR_INVALID_OUTPUT', failure_type=type(exc).__name__)
        if isinstance(exc, ValueError): report['reason'] = str(exc)
    finally:
        if process is not None and process.poll() is None: process.kill(); process.wait(timeout=5)
        for item in reversed(list(owned.values())):
            try:
                if item.is_running(): item.kill(); item.wait(timeout=5)
            except (psutil.NoSuchProcess, psutil.TimeoutExpired): pass
        report['seconds'] = time.monotonic() - started
        report['raw_file_sha256'] = {path.relative_to(out).as_posix(): sha(path) for path in out.rglob('*') if path.is_file() and '__pycache__' not in path.parts}
        (out / 'result.json').write_bytes((json.dumps(report, indent=2) + '\n').encode())
        print(json.dumps({key: report.get(key) for key in ('status', 'primary_metric', 'seconds', 'train_correct', 'test_correct', 'reason')}), flush=True)
    return code


if __name__ == '__main__':
    raise SystemExit(main())
