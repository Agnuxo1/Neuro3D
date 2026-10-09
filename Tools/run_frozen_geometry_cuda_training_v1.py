"""Shared-FIFO paired CPU/CUDA full training, including all CPU geometry work."""
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

LIMITS = {'total_seconds': 1900, 'cpu_seconds': 900, 'cuda_seconds': 900,
          'free_ram_before_mib': 8192, 'free_ram_floor_mib': 4000,
          'owned_rss_mib': 1500, 'evidence_mib': 128, 'cpu_cores': 1,
          'cuda_peak_reserved_mib': 1024}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(path, registration):
    profile, pin = read_json(path, 262144)
    need(profile['schema'] == 'optic_neuro_blender.geometry_cuda_training_profile.v1' and profile['limits'] == LIMITS, 'Fixed paired training profile/envelope required')
    need(profile['cpu_parity_tolerances'] == {'field': 1e-11, 'power': 1e-11, 'loss': 1e-11, 'gradient': 1e-9}, 'Fixed CUDA matched numeric controls required')
    for name, expected in profile['pins'].items():
        source = (ROOT / name).resolve()
        need(source.is_relative_to(ROOT) and source.is_file() and sha(source) == expected, 'Training pin mismatch:' + name)
    need({profile['worker'], profile['training_profile'], 'Tools/train_captured_geometry_v1.py',
          'Tools/run_frozen_geometry_cuda_training_v1.py', 'Blender/blender_lab/torch_training_arithmetic_v1.py',
          'Blender/blender_lab/torch_geometry_backend_v1.py'} <= set(profile['pins']), 'Critical own CPU/GPU sources required')
    record, rpin = read_json(registration, 65536); check_registration(record, profile, pin)
    return profile, pin, rpin


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--profile', type=Path, required=True)
    parser.add_argument('--registration', type=Path, required=True); parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(); out = args.out.resolve(); out.mkdir(exist_ok=False)
    process = None; owned = {}; peak = 0; code = 3; started = time.monotonic()
    report = {'schema': 'optic_neuro_blender.paired_cuda_training_supervision.v1', 'status': 'NOT_EXECUTED',
              'primary_metric': None, 'gpu_requested': True, 'worker_started': False, 'result_collected': False}
    try:
        import psutil
        profile, pin, rpin = validate(args.profile, args.registration)
        need(os.environ.get('GPUQ_HOLDER') == '1' and os.environ.get('GPUQ_NAME') == profile['queue_job_name'], 'Actual shared FIFO admission required')
        report.update(profile_sha256=pin, registration_sha256=rpin, shared_fifo_queue_name=os.environ['GPUQ_NAME'],
                      preflight_free_ram_mib=psutil.virtual_memory().available / 2**20)
        need(report['preflight_free_ram_mib'] >= LIMITS['free_ram_before_mib'], 'Fixed8GiBhostRAMpreflight guard')
        for name in profile['pins']:
            target = out / 'source' / name; target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(ROOT / name, target)
        shutil.copyfile(args.profile, out / 'profile.json'); shutil.copyfile(args.registration, out / 'registration.json')
        env = dict(os.environ, OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
        stages = [
            ('cpu_baseline', [sys.executable, '-X', 'utf8', str(ROOT / 'Tools/train_captured_geometry_v1.py'), '--profile', str((ROOT / profile['training_profile']).resolve()), '--out', str(out / 'cpu')], LIMITS['cpu_seconds']),
            ('cuda_training', [sys.executable, '-X', 'utf8', str(ROOT / profile['worker']), '--profile', str(args.profile.resolve()), '--out', str(out / 'cuda')], LIMITS['cuda_seconds']),
        ]
        report['stages'] = []
        for name, command, budget in stages:
            stage_start = time.monotonic(); stop = None; owned = {}
            with (out / (name + '.stdout')).open('xb') as stream:
                process = subprocess.Popen(command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, env=env,
                                           creationflags=subprocess.CREATE_NO_WINDOW | subprocess.BELOW_NORMAL_PRIORITY_CLASS if os.name == 'nt' else 0)
                parent = psutil.Process(process.pid); parent.cpu_affinity([psutil.Process().cpu_affinity()[0]]); owned[parent.pid] = parent
                report['worker_started'] = True
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
                    elif psutil.virtual_memory().available < LIMITS['free_ram_floor_mib'] * 2**20: stop = 'HOST_RAM_FLOOR'
                    elif sum(path.stat().st_size for path in out.rglob('*') if path.is_file()) > LIMITS['evidence_mib'] * 2**20: stop = 'EVIDENCE_LIMIT'
                    if stop:
                        for item in reversed(list(owned.values())):
                            try: item.kill()
                            except psutil.NoSuchProcess: pass
                        break
                    time.sleep(.2)
                process.wait(timeout=5)
            report['stages'].append({'name': name, 'seconds': time.monotonic() - stage_start, 'exit_code': process.returncode, 'stopped': stop})
            need(stop is None and process.returncode in (0, 2), 'Paired training stage incomplete:' + name)
        import numpy as np
        cpu, cpupin = read_json(out / 'cpu/result.json', 64 * 2**20)
        cuda, cudapin = read_json(out / 'cuda/result.json', 64 * 2**20)
        need(cpu['status'] in ('PASS', 'FAIL_LOSS_DROP') and cuda['status'] in ('PASS', 'FAIL_LOSS_DROP'), 'Complete valid CPU/GPU training outcomes required')
        need(cpu['geometry_audited_states'] == cuda['geometry_audited_states'] == 61 and cuda['actual_readback_verified'] is True,
             'All61geometryaudits andactualCUDA readback required')
        need(cuda['precision'] == 'complex128/float64' and cuda['gpu_executed'] is True and cuda['cuda_peak_reserved_bytes'] <= LIMITS['cuda_peak_reserved_mib'] * 2**20,
             'Actual precision/device allocation required')
        validate(args.profile, args.registration)
        report.update(status='VALID_PAIRED_CPU_CUDA_GEOMETRY_TRAINING', primary_metric=int(cpu['status'] == cuda['status'] == 'PASS'), result_collected=True,
                      cpu_result_sha256=cpupin, cuda_result_sha256=cudapin, peak_owned_aggregate_rss_mib=peak / 2**20,
                      cpu_test_correct=cpu['test_correct'], cuda_test_correct=cuda['test_correct'],
                      prediction_agreement=int(np.sum(np.asarray(cpu['predictions']) == np.asarray(cuda['predictions']))),
                      final_power_max_difference=float(np.max(np.abs(np.asarray(cpu['observed_powers']) - np.asarray(cuda['observed_powers'])))),
                      final_geometry_delta_max_difference_BU=float(np.max(np.abs(np.asarray(cpu['final_deltas_BU']) - np.asarray(cuda['final_deltas_BU'])))),
                      same_optimizer_trajectory_required=False,
                      full_worker_cpu_over_cuda_ratio=report['stages'][0]['seconds'] / report['stages'][1]['seconds'],
                      scope='One paired full-worker CPU/CUDA own training repetition, all61exactCPUgeometryaudits each, same data/split/initialization/updates/precisioncontract. CUDA ownCE/Jacobian/Adam, CPU nativequantization/phasepreparation and geometry. GPUadds perstateCPU numeric controls; timesincludevalidation andcoldimport. No repeatedtiming confidence interval, energy, fullBlenderGPU/triangletracing, AMD or physicalprocessor claim.')
        code = 0
    except Exception as exc:
        report.update(status='INCONCLUSIVE_ENVIRONMENT_OR_INVALID_OUTPUT' if report['worker_started'] else 'NOT_EXECUTED', failure_type=type(exc).__name__)
        if isinstance(exc, ValueError): report['reason'] = str(exc)
    finally:
        if process is not None and process.poll() is None: process.kill(); process.wait(timeout=5)
        for item in reversed(list(owned.values())):
            try:
                if item.is_running(): item.kill(); item.wait(timeout=5)
            except (psutil.NoSuchProcess, psutil.TimeoutExpired): pass
        report['seconds'] = time.monotonic() - started
        report['owned_worker_cleaned_up'] = process is None or process.poll() is not None
        report['raw_file_sha256'] = {path.relative_to(out).as_posix(): sha(path) for path in out.rglob('*') if path.is_file() and '__pycache__' not in path.parts}
        (out / 'supervisor.json').write_bytes((json.dumps(report, indent=2) + '\n').encode())
        print(json.dumps({key: report.get(key) for key in ('status', 'primary_metric', 'seconds', 'cpu_test_correct', 'cuda_test_correct', 'reason')}), flush=True)
    return code


if __name__ == '__main__':
    raise SystemExit(main())
