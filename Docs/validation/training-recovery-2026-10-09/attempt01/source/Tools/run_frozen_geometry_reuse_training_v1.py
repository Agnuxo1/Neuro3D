"""Paired full own CPU training: point audits versus fresh continuous proof reuse."""
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

LIMITS = {'total_seconds': 1900, 'cpu_seconds': 900, 'reuse_seconds': 900,
          'free_ram_before_mib': 4000, 'free_ram_floor_mib': 2500,
          'owned_rss_mib': 1500, 'evidence_mib': 128, 'cpu_cores': 1, 'gpu': False}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(path, registration):
    profile, pin = read_json(path, 262144)
    need(profile['schema'] == 'optic_neuro_blender.geometry_reuse_training_profile.v1' and profile['limits'] == LIMITS, 'Fixed paired training profile/envelope required')
    need(profile['parity_tolerances']=={'power':1e-11,'loss':1e-11,'geometry_BU':0.0},'Fixed exact-trajectory/parity controls required')
    for name, expected in profile['pins'].items():
        source = (ROOT / name).resolve()
        need(source.is_relative_to(ROOT) and source.is_file() and sha(source) == expected, 'Training pin mismatch:' + name)
    need({profile['worker'],profile['training_profile'],'Tools/train_captured_geometry_v1.py','Tools/run_frozen_geometry_reuse_training_v1.py','Blender/blender_lab/affine_family_identity_v1.py','Blender/blender_lab/affine_box_audit_v1.py'}<=set(profile['pins']),'Critical own training/proof sources required')
    prerequisite,_=read_json(ROOT/profile['prerequisite_family_certificate'],16*2**20)
    need(prerequisite['status']=='CERTIFIED_WHOLE_DECLARED_TRAINING_FAMILY' and prerequisite['primary_metric']==1,'Published positive whole-family prerequisite required')
    record, rpin = read_json(registration, 65536); check_registration(record, profile, pin)
    return profile, pin, rpin


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--profile', type=Path, required=True)
    parser.add_argument('--registration', type=Path, required=True); parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(); out = args.out.resolve(); out.mkdir(exist_ok=False)
    process = None; owned = {}; peak = 0; code = 3; started = time.monotonic()
    report = {'schema': 'optic_neuro_blender.paired_reuse_training_supervision.v1', 'status': 'NOT_EXECUTED',
              'primary_metric': None, 'gpu_requested': False, 'worker_started': False, 'result_collected': False}
    try:
        import psutil
        profile, pin, rpin = validate(args.profile, args.registration)
        report.update(profile_sha256=pin,registration_sha256=rpin,preflight_free_ram_mib=psutil.virtual_memory().available/2**20)
        need(report['preflight_free_ram_mib'] >= LIMITS['free_ram_before_mib'], 'Fixed4GiBhostRAMpreflight guard')
        for name in profile['pins']:
            target = out / 'source' / name; target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(ROOT / name, target)
        shutil.copyfile(args.profile, out / 'profile.json'); shutil.copyfile(args.registration, out / 'registration.json')
        env = dict(os.environ, OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
        stages = [
            ('cpu_baseline', [sys.executable, '-X', 'utf8', str(ROOT / 'Tools/train_captured_geometry_v1.py'), '--profile', str((ROOT / profile['training_profile']).resolve()), '--out', str(out / 'cpu')], LIMITS['cpu_seconds']),
            ('continuous_proof_training', [sys.executable, '-X', 'utf8', str(ROOT / profile['worker']), '--profile', str(args.profile.resolve()), '--out', str(out / 'reuse')], LIMITS['reuse_seconds']),
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
        reuse, reusepin=read_json(out/'reuse/result.json',64*2**20)
        need(cpu['status'] in ('PASS','FAIL_LOSS_DROP') and reuse['status'] in ('PASS','FAIL_LOSS_DROP'),'Complete valid own training outcomes required')
        need(cpu['geometry_audited_states']==61 and reuse['geometry_audited_states']==0 and reuse['geometry_membership_states']==61 and reuse['continuous_family_proved_states']==133,'Original point audits / optimized continuous proof identity required')
        cpuh=[json.loads(row) for row in (out/'cpu/progress.jsonl').read_text().splitlines()];reuseh=[json.loads(row) for row in (out/'reuse/progress.jsonl').read_text().splitlines()]
        need(len(cpuh)==len(reuseh)==61,'Every optimizer state required')
        delta=max(float(np.max(np.abs(np.array(a['deltas_BU'])-np.array(b['deltas_BU'])))) for a,b in zip(cpuh,reuseh));loss=max(abs(a['train_loss']-b['train_loss']) for a,b in zip(cpuh,reuseh))
        power=float(np.max(np.abs(np.array(cpu['observed_powers'])-np.array(reuse['observed_powers']))));predictions=int(np.sum(np.array(cpu['predictions'])==np.array(reuse['predictions'])))
        need(delta==0 and loss<=1e-11 and power<=1e-11 and predictions==150,'Unchanged complete optimizer trajectory/numeric equivalence gate')
        validate(args.profile,args.registration)
        report.update(status='VALID_PAIRED_POINT_AND_CONTINUOUS_TRAINING',primary_metric=int(cpu['status']==reuse['status']=='PASS'),result_collected=True,
                      cpu_result_sha256=cpupin,reuse_result_sha256=reusepin,peak_owned_aggregate_rss_mib=peak/2**20,cpu_test_correct=cpu['test_correct'],reuse_test_correct=reuse['test_correct'],
                      prediction_agreement=predictions,all61_geometry_delta_max_difference_BU=delta,all61_loss_max_difference=loss,final_power_max_difference=power,
                      full_worker_cpu_over_reuse_ratio=report['stages'][0]['seconds']/report['stages'][1]['seconds'],
                      scope='One paired full-worker CPU comparison: original61pointgeometryaudits versus freshly executed wholecontinuousfamily proof +61exactmembershipchecks. Same data/split/initialization/updates/nativequantization; all61coordinates identical, all150predictions same. Continuous proof and fresh finalrebuild overhead included; no repeatedtiming confidence interval, GPU, energy, native Blender transform or physicalprocessor claim.')
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
        print(json.dumps({key: report.get(key) for key in ('status', 'primary_metric', 'seconds', 'cpu_test_correct', 'reuse_test_correct', 'reason')}), flush=True)
    return code


if __name__ == '__main__':
    raise SystemExit(main())
