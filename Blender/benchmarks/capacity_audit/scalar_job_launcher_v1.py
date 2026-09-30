"""Own scalar job integration, invoke ONLY as gpuq's already-acquired child.

No queue acquisition/mutation. Deadline is generated here, never before waiting.
Numerical/content consistency is not runtime/driver authentication.
"""
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'Blender/tests'))
import exp005_signed_scalar_child as E
import scalar_job_bundle_v1 as B
import scalar_job_supervisor_v1 as S
import phase_signed_native_capture_v2 as C

CHILD_REPORT = ROOT/'coordinacion/respuestas/PHASE-SIGNED-SCALAR-CHILD-001-CODEX.json'
CHILD_REPORT_SHA = '6f4c8907874cda25027e572834d7d7bb1e6b112f0f4096f05f68f3c9f0ffce11'


def verify_preparation():
    if C.sha(CHILD_REPORT) != CHILD_REPORT_SHA:
        raise ValueError('frozen child preparation report changed')
    pins = json.loads(CHILD_REPORT.read_text(encoding='utf-8'))['code_sha256']
    if pins.get(str(E.SELF)) != C.sha(E.SELF) or any(C.sha(p) != v for p, v in pins.items()):
        raise ValueError('frozen child dependency changed')
    B.contract()
    return dict(pins, **{str(CHILD_REPORT): CHILD_REPORT_SHA, str(Path(__file__).resolve()): C.sha(__file__)})


def owner_snapshot(name):
    import psutil
    owner = S.assert_reservation(name)
    return {'guard_pid': owner['child_pid'], 'guard_birth': psutil.Process().create_time(),
            'queue_pid': owner['queue_pid'],
            'queue_birth': psutil.Process(owner['queue_pid']).create_time()}


def run(blender, job, queue_name):
    """No caller-supplied clocks, admission adapters, or expired night deadline."""
    pins = verify_preparation()
    executable, folder = Path(blender), Path(job)
    if not executable.is_absolute() or executable.name.lower() != 'blender.exe' or not executable.is_file():
        raise ValueError('existing explicit absolute Blender executable required')
    if not folder.is_absolute() or not folder.resolve().is_relative_to(ROOT) or \
            folder.resolve() == ROOT or not folder.parent.is_dir() or folder.exists():
        raise ValueError('fresh private direct child of an existing project directory required')
    executable, folder = executable.resolve(), folder.resolve()
    executable_sha = C.sha(executable)  # Hash BEFORE starting the short dispatch deadline.
    owner = owner_snapshot(queue_name)  # Fail closed without holder; never acquire a ticket here.
    folder.mkdir(exist_ok=False)
    base = {'runtime_execution_authenticated': False, 'native_promotion_allowed': False,
            'operational_gate_passed': False, 'geometry_or_scene_inference': False,
            'no_jev_aval': True, 'code_sha256': pins, 'executable_sha256': executable_sha,
            'scope': 'scalar lifecycle/content integration only; no GPU/OS authentication'}
    C.write_once(folder/'launcher_initial.json', dict(base, status='in_progress'))
    final = dict(base, status='failed', child_command_started=False)
    try:
        sample = S.telemetry()
        final['prelaunch_sample'] = sample
        reasons = S.resource_reasons(sample, before_launch=True)
        if reasons:
            final.update(status='resource_rejected', reasons=reasons)
            return final
        # This clock is taken INSIDE the admitted gpuq child, after waiting/hash/preflight.
        now = datetime.now(timezone.utc); deadline = now+timedelta(seconds=90)
        rpath, bpath = folder/'recipe.json', folder/'binding.json'
        recipe = B.recipe(E.command(executable, rpath, bpath), folder/'capture', folder/'supervisor',
                          deadline=deadline, now=now, queue_name=queue_name, timeout=60)
        C.write_once(rpath, recipe)
        binding = dict(owner, version='signed-scalar-child-v1', recipe_sha256=C.sha(rpath),
                       entrypoint_sha256=C.sha(E.SELF), executable_sha256=executable_sha)
        C.write_once(bpath, binding)
        if owner_snapshot(queue_name) != owner or verify_preparation() != pins or C.sha(executable) != executable_sha:
            raise ValueError('owner/preparation/executable changed before supervisor')
        final['supervisor_called'] = True
        envelope = S.run_owned(recipe['command'], recipe['supervisor_path'], deadline=deadline,
                               queue_name=queue_name, timeout=60)
        final['child_command_started'] = 'child_pid' in envelope
        final['supervisor_status'] = envelope['status']
        if envelope['status'] != 'completed':
            raise ValueError('scalar child did not complete cleanly')
        C.fresh_deadline(deadline)()  # Late success is rejected, not promoted.
        final['content'] = B.inspect_bundle(recipe)
        sidecar = Path(recipe['capture_path']+'.child.json')
        metadata = json.loads(sidecar.read_text(encoding='utf-8'))
        if metadata.get('recipe_sha256') != C.sha(rpath) or metadata.get('binding_sha256') != C.sha(bpath) or \
                metadata.get('entrypoint_sha256') != C.sha(E.SELF) or \
                metadata.get('child_pid') != envelope.get('child_pid') or \
                metadata.get('guard_pid') != owner['guard_pid'] or metadata.get('queue_pid') != owner['queue_pid'] or \
                metadata.get('runtime_execution_authenticated') is not False or \
                metadata.get('native_promotion_allowed') is not False:
            raise ValueError('private child metadata lineage mismatch')
        final.update(status='content_verified_pending_runtime_authentication',
                     recipe_sha256=C.sha(rpath), binding_sha256=C.sha(bpath),
                     child_metadata_sha256=C.sha(sidecar))
        if verify_preparation() != pins:
            raise ValueError('preparation changed during job')
        C.fresh_deadline(deadline)()
        return final
    except BaseException as error:
        final.update(status='failed', error_type=type(error).__name__)
        raise
    finally:
        C.write_once(folder/'launcher_final.json', final)


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--blender', required=True); p.add_argument('--job', required=True)
    p.add_argument('--queue-name', required=True)
    args = p.parse_args()
    result = run(args.blender, args.job, args.queue_name)
    print(json.dumps({'status': result['status'], 'native_promotion_allowed': False}))
    raise SystemExit(0 if result['status']=='content_verified_pending_runtime_authentication' else 2)


if __name__ == '__main__': main()
