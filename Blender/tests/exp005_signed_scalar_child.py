"""Private Blender scalar entrypoint; no queue acquisition or CPU fallback.

Pure import does not import bpy/gpu. Binding checks are process/content checks,
not OS/driver authentication. Use only under the own bounded supervisor.
"""
from datetime import datetime
import gc
import json
import math
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).resolve()
sys.path.insert(0, str(ROOT/'Blender/benchmarks/capacity_audit'))
import scalar_job_bundle_v1 as B
import phase_signed_native_capture_v2 as C
import scalar_job_supervisor_v1 as S


def command(executable, recipe_path, binding_path):
    paths = [Path(v) for v in (executable, recipe_path, binding_path)]
    if any(not p.is_absolute() for p in paths):
        raise ValueError('explicit absolute executable/recipe/binding paths required')
    return [str(paths[0].resolve()), '--factory-startup', '-t', '1',
            '--python-exit-code', '17', '--python', str(SELF), '--',
            '--recipe', str(paths[1].resolve()), '--binding', str(paths[2].resolve())]


def validate_binding(recipe, binding, *, recipe_path, binding_path, holder,
                     current, parent, queue, environ):
    """Pure checker; CPU tests supply synthetic process snapshots explicitly."""
    B.validate_recipe(recipe)
    keys = {'version', 'recipe_sha256', 'entrypoint_sha256', 'executable_sha256',
            'guard_pid', 'guard_birth', 'queue_pid', 'queue_birth'}
    if not isinstance(binding, dict) or set(binding) != keys or \
            binding['version'] != 'signed-scalar-child-v1':
        raise ValueError('exact child binding schema required')
    for path in (recipe_path, binding_path):
        p = Path(path)
        if not p.is_absolute() or not p.resolve().is_relative_to(ROOT):
            raise ValueError('private absolute project input path required')
    expected = command(recipe['command'][0], recipe_path, binding_path)
    if recipe['command'] != expected or current.get('argv') != expected:
        raise ValueError('private factory-startup argv binding mismatch')
    if binding['recipe_sha256'] != C.sha(recipe_path) or \
            binding['entrypoint_sha256'] != C.sha(SELF) or \
            binding['executable_sha256'] != C.sha(expected[0]):
        raise ValueError('recipe/entrypoint/executable binding changed')
    for process in (current, parent, queue):
        if any(type(process.get(k)) is not int or process[k] <= 0 for k in ('pid', 'ppid')):
            raise ValueError('positive exact process identities required')
        birth = process.get('birth')
        if isinstance(birth, bool) or not isinstance(birth, (int, float)) or \
                not math.isfinite(birth) or birth <= 0:
            raise ValueError('finite process birth identity required')
    if type(binding['guard_pid']) is not int or type(binding['queue_pid']) is not int:
        raise ValueError('exact bound guard/queue PID required')
    for key in ('guard_birth', 'queue_birth'):
        value = binding[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or \
                not math.isfinite(value) or value <= 0:
            raise ValueError('finite bound birth identity required')
    if current['ppid'] != parent['pid'] or parent['ppid'] != queue['pid'] or \
            binding['guard_pid'] != parent['pid'] or binding['queue_pid'] != queue['pid'] or \
            abs(binding['guard_birth']-parent['birth']) >= .01 or \
            abs(binding['queue_birth']-queue['birth']) >= .01:
        raise ValueError('owned Blender -> supervisor -> gpuq chain mismatch')
    if environ.get('GPUQ_HOLDER') != '1' or environ.get('GPUQ_NAME') != recipe['queue_name']:
        raise ValueError('inherited named gpuq environment required')
    S.verify_holder_record(holder, recipe['queue_name'], parent['pid'],
                           parent['birth'], queue['birth'])
    if holder['pid'] != queue['pid']:
        raise ValueError('holder queue PID mismatch')
    return {'child_pid': current['pid'], 'child_birth': current['birth'],
            'guard_pid': parent['pid'], 'queue_pid': queue['pid'],
            'runtime_execution_authenticated': False, 'native_promotion_allowed': False}


def real_binding(recipe, binding, recipe_path, binding_path):
    import psutil
    child = psutil.Process(); parent = child.parent()
    if parent is None or parent.parent() is None:
        raise ValueError('missing supervisor/gpuq ancestors')
    queue = parent.parent()
    def snapshot(p):
        return {'pid': p.pid, 'ppid': p.ppid(), 'birth': p.create_time()}
    current = snapshot(child); current['argv'] = child.cmdline()
    current['argv'][0] = str(Path(current['argv'][0]).resolve())
    return validate_binding(recipe, binding, recipe_path=recipe_path, binding_path=binding_path,
        holder=json.loads(S.HOLDER.read_text(encoding='utf-8')), current=current,
        parent=snapshot(parent), queue=snapshot(queue), environ=os.environ)


def private_preferences(bpy):
    # Only this owned --factory-startup process; never save user preferences.
    p = bpy.context.preferences
    p.use_preferences_save = False
    p.view.use_save_prompt = False
    p.filepaths.use_auto_save_temporary_files = False
    if p.use_preferences_save or p.view.use_save_prompt or p.filepaths.use_auto_save_temporary_files:
        raise ValueError('private non-persistent no-dialog preferences required')


def schedule_clean_exit(bpy):
    def close():
        windows = list(bpy.context.window_manager.windows)
        if not windows:
            raise RuntimeError('private GPU context needs a Blender window')
        with bpy.context.temp_override(window=windows[0]):
            bpy.ops.wm.quit_blender()
        return None
    bpy.app.timers.register(close, first_interval=.1)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--recipe', required=True); parser.add_argument('--binding', required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    recipe = json.loads(Path(args.recipe).read_text(encoding='utf-8'))
    binding = json.loads(Path(args.binding).read_text(encoding='utf-8'))
    check = C.fresh_deadline(datetime.fromisoformat(recipe['deadline_utc']))
    def admit():
        check(); identity = real_binding(recipe, binding, args.recipe, args.binding)
        if S.resource_reasons(S.telemetry(), before_launch=False):
            raise ValueError('running scalar resource floor/cap violated')
        check(); return identity
    identity = admit()  # Before explicit bpy/gpu import, compilation or dispatch.
    import bpy
    import gpu
    private_preferences(bpy)
    backend = {k: getattr(gpu.platform, k+'_get')() for k in
               ('backend_type', 'vendor', 'renderer', 'version')}
    if 'NVIDIA' not in (backend['vendor']+' '+backend['renderer']).upper():
        raise ValueError('NVIDIA native backend required; no CPU fallback')
    sidecar = Path(recipe['capture_path']+'.child.json')
    C.write_once(sidecar, dict(identity, backend=backend, recipe_sha256=C.sha(args.recipe),
        binding_sha256=C.sha(args.binding), entrypoint_sha256=C.sha(SELF),
        blender_version=bpy.app.version_string, scope='runtime metadata, not GPU authentication',
        no_jev_aval=True))
    C.run_private_capture(gpu, recipe['contract']['capture_manifest'],
                          recipe['capture_path'], check, admit=admit)
    admit(); gc.collect(); schedule_clean_exit(bpy)
    # Failure propagates to --python-exit-code17; outer guard remains mandatory.


if __name__ == '__main__': main()
