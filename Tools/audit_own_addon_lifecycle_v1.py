"""Short native lifecycle regression; training evidence is retained from v0.1.1."""
import hashlib
import json
import os
from pathlib import Path
import sys
import time
import zipfile
import bpy
import numpy as np


def need(value, message):
    if not value:
        raise ValueError(message)


def main():
    args = sys.argv[sys.argv.index('--') + 1:]
    profile_path, out = Path(args[0]).resolve(), Path(args[1]).resolve()
    profile = json.loads(profile_path.read_bytes()); out.mkdir(exist_ok=False)
    archive = Path(profile['archive']).resolve(); previous = Path(profile['previous_archive']).resolve()
    need(hashlib.sha256(archive.read_bytes()).hexdigest() == profile['archive_sha256'] and hashlib.sha256(previous.read_bytes()).hexdigest() == profile['previous_archive_sha256'], 'Versioned package identity mismatch')
    need(list(bpy.app.version) == [4, 5, 14], 'Frozen Blender numeric version required')
    start = time.perf_counter(); checks = []
    with zipfile.ZipFile(archive) as current, zipfile.ZipFile(previous) as old:
        need(set(current.namelist()) == set(old.namelist()), 'Unexpected package file addition/removal')
        names = old.namelist(); changed = [name for name in names if current.read(name) != old.read(name)]
        need(set(changed) == {'optic_neuro_blender/__init__.py', 'optic_neuro_blender/INSTALL.txt', 'optic_neuro_blender/package_manifest.json'}, 'Unexpected scientific-worker/data change')
    checks.append({'name': 'unchanged_scientific_worker_vendor_and_data_bytes', 'pass': True, 'changed_package_files': changed})
    bpy.ops.preferences.addon_install(filepath=str(archive), overwrite=False)
    import addon_utils
    addon_utils.enable('optic_neuro_blender', default_set=False, persistent=True)
    import optic_neuro_blender as addon
    from optic_neuro_blender.bootstrap import PACKAGE, verify_bundle
    verify_bundle(); need(addon._registered, 'Addon not registered')
    for _ in range(3):
        addon.register(); addon.unregister(); addon.unregister(); addon.register()
        need(addon._registered, 'Idempotent lifecycle failed')
    checks.append({'name': 'three_direct_duplicate_register_unregister_cycles', 'pass': True})
    for _ in range(2):
        addon_utils.disable('optic_neuro_blender', default_set=False)
        need(not addon._registered, 'Blender utility disable did not unregister')
        addon_utils.enable('optic_neuro_blender', default_set=False, persistent=True)
        need(addon._registered, 'Blender utility enable did not register')
    checks.append({'name': 'two_actual_blender_enable_disable_cycles', 'pass': True})
    need(bpy.ops.optic_neuro.load_example() == {'FINISHED'}, 'Own example failed')
    jobs = out / 'jobs'; jobs.mkdir(); bpy.context.scene.optic_neuro_settings.work_directory = str(jobs)
    need(bpy.ops.optic_neuro.infer() == {'FINISHED'}, 'Worker cancellation-on-disable fixture failed')
    cancelled = addon._job
    addon_utils.disable('optic_neuro_blender', default_set=False)
    need(cancelled.state == 'CANCELLED' and cancelled.process.poll() is not None, 'Disable left owned worker active')
    checks.append({'name': 'disabling_addon_cancels_owned_blender_job', 'pass': True})
    addon_utils.enable('optic_neuro_blender', default_set=False, persistent=True)
    settings = bpy.context.scene.optic_neuro_settings
    settings.work_directory = str(jobs)
    settings.amplitudes = [.2, .3, .4, .5, 1]; settings.phases = [.1, .2, -.3, .4, 0]
    need(bpy.ops.optic_neuro.infer() == {'FINISHED'}, 'Inference after lifecycle failed to start')
    until = time.monotonic() + 120
    while addon._job.state == 'RUNNING' and time.monotonic() < until:
        addon.poll_job(); time.sleep(.1)
    need(addon._job.state == 'COMPLETED', 'Inference after lifecycle incomplete')
    request, result = addon.validate_recovery(addon._last_folder)
    reference = json.loads((PACKAGE / 'data/training_result.json').read_bytes())
    difference = float(np.max(np.abs(np.asarray(result['all150_native_powers']) - np.asarray(reference['observed_powers']))))
    need(difference <= 1e-11 and result['all150_predictions'] == reference['predictions'], 'Native150 inference changed after lifecycle fix')
    checks.append({'name': 'native150_inference_after_enable_disable', 'pass': True, 'power_max_difference': difference})
    # Recreate the former double-dispatch shutdown path intentionally.
    addon.unregister(); addon.unregister()
    report = {'schema': 'optic_neuro_blender.native_addon_lifecycle.v1', 'status': 'PASS', 'checks': checks,
              'archive_sha256': profile['archive_sha256'], 'previous_archive_sha256': profile['previous_archive_sha256'],
              'profile_sha256': hashlib.sha256(profile_path.read_bytes()).hexdigest(), 'seconds': time.perf_counter() - start,
              'blender_version': bpy.app.version_string, 'training_reexecuted': False,
              'scope': 'Actual local Blender lifecycle regression and native150 inference; unchanged training worker/core/data independently byte-checked against ZIP0.1.1; no new training, human usability, physical or independent expert claim'}
    (out / 'result.json').write_bytes((json.dumps(report, indent=2) + '\n').encode())
    print(json.dumps({'status': 'PASS', 'checks': len(checks), 'seconds': report['seconds']}), flush=True)


if __name__ == '__main__':
    main()
