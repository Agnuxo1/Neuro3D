"""CPU-only supervised, prospectively frozen packet analysis."""
import argparse, hashlib, json, os, subprocess, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from Tools.run_frozen_state_graph_profile_v1 import check_registration
from Tools.audit_captured_pilot_result_v1 import need
LIMITS = {'worker_seconds': 300, 'free_ram_before_mib': 512, 'free_ram_floor_mib': 256,
          'owned_rss_mib': 512, 'evidence_mib': 16, 'cpu_cores': 1, 'gpu': False}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(path, registration):
    profile = json.loads(path.read_bytes())
    need(profile['schema'] == 'optic_neuro_blender.native_packet_workload_profile.v1' and profile['limits'] == LIMITS,
         'Frozen CPU-only secondary resource envelope required')
    need(profile['worker'] == 'Tools/audit_native_packet_workload_v1.py' and profile['batch_sizes'] == [1, 150, 4096], 'Fixed packet replay required')
    for name, pin in profile['pins'].items():
        source = (ROOT / name).resolve()
        need(source.is_relative_to(ROOT) and source.is_file() and sha(source) == pin, 'Frozen source mismatch: ' + name)
    record = json.loads(registration.read_bytes())
    check_registration(record, profile, sha(path))
    return profile


def main():
    import psutil
    parser = argparse.ArgumentParser()
    parser.add_argument('--profile', type=Path, required=True)
    parser.add_argument('--registration', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out = args.out.resolve()
    args.out.mkdir(exist_ok=False)
    process = None
    report = {'schema': 'optic_neuro_blender.native_packet_workload_supervision.v1', 'status': 'NOT_EXECUTED',
              'primary_metric': None, 'worker_started': False, 'gpu_requested': False}
    code = 3
    try:
        profile = validate(args.profile, args.registration)
        pin, rpin = sha(args.profile), sha(args.registration)
        report.update(profile_sha256=pin, registration_sha256=rpin, preflight_free_ram_mib=psutil.virtual_memory().available / 2**20)
        need(report['preflight_free_ram_mib'] >= 512, 'RAM preflight required')
        for source, name in ((args.profile, 'profile.json'), (args.registration, 'registration.json')):
            (args.out / name).write_bytes(source.read_bytes())
        env = dict(os.environ, OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
        start, peak, stopped = time.monotonic(), 0, None
        flags = subprocess.CREATE_NO_WINDOW | subprocess.BELOW_NORMAL_PRIORITY_CLASS if os.name == 'nt' else 0
        with (args.out / 'worker.stdout').open('xb') as stream:
            process = subprocess.Popen([sys.executable, '-X', 'utf8', str(ROOT / profile['worker']), '--profile', str(args.profile.resolve()),
                                        '--out', str(args.out / 'worker')], cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT, creationflags=flags)
            report['worker_started'] = True
            owned = psutil.Process(process.pid)
            owned.cpu_affinity([psutil.Process().cpu_affinity()[0]])
            while process.poll() is None:
                try:
                    peak = max(peak, owned.memory_info().rss)
                except psutil.NoSuchProcess:
                    break
                if time.monotonic() - start > 300:
                    stopped = 'WORKER_DEADLINE'
                elif peak > 512 * 2**20:
                    stopped = 'OWNED_RSS_LIMIT'
                elif psutil.virtual_memory().available < 256 * 2**20:
                    stopped = 'HOST_RAM_FLOOR'
                elif sum(p.stat().st_size for p in args.out.rglob('*') if p.is_file()) > 16 * 2**20:
                    stopped = 'EVIDENCE_LIMIT'
                if stopped:
                    process.kill()
                    break
                time.sleep(.1)
            process.wait(timeout=5)
        report.update(worker_exit_code=process.returncode, worker_seconds=time.monotonic() - start,
                      peak_owned_rss_mib=peak / 2**20, stopped=stopped)
        need(stopped is None and process.returncode == 0, 'Complete secondary packet analysis required')
        validate(args.profile, args.registration)
        need(sha(args.profile) == pin and sha(args.registration) == rpin, 'Immutable registration/profile required')
        result = json.loads((args.out / 'worker/result.json').read_bytes())
        need(result['primary_metric'] == 1 and result['profile_sha256'] == pin and len(result['measurements']) == 6,
             'Exact frozen result required')
        report.update(status='VALID_FROZEN_NATIVE_PACKET_WORKLOAD', primary_metric=1, result_sha256=sha(args.out / 'worker/result.json'))
        code = 0
    except Exception as exc:
        report.update(status='INCONCLUSIVE_ENVIRONMENT_OR_INVALID_OUTPUT' if report['worker_started'] else 'NOT_EXECUTED', failure_type=type(exc).__name__)
        if isinstance(exc, ValueError):
            report['reason'] = str(exc)
    finally:
        if process is not None and process.poll() is None:
            process.kill()
            process.wait(timeout=5)
        report['owned_worker_cleaned_up'] = process is None or process.poll() is not None
        report['raw_file_sha256'] = {p.relative_to(args.out).as_posix(): sha(p) for p in args.out.rglob('*') if p.is_file()}
        (args.out / 'supervisor.json').write_bytes((json.dumps(report, indent=2) + '\n').encode())
        print(json.dumps({key: report.get(key) for key in ('status', 'primary_metric', 'worker_seconds', 'peak_owned_rss_mib', 'reason')}))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
