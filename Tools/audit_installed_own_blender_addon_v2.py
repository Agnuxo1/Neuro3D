"""Prospective actual Blender install/operators/worker/roundtrip/recovery audit."""
import hashlib
import json
import os
from pathlib import Path
import sys
import time

import bpy
import numpy as np


def need(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    args = sys.argv[sys.argv.index('--') + 1:]
    profile_path, out = Path(args[0]).resolve(), Path(args[1]).resolve()
    profile = json.loads(profile_path.read_bytes()); out.mkdir(exist_ok=False)
    source_archive = Path(profile['archive']).resolve()
    need(hashlib.sha256(source_archive.read_bytes()).hexdigest() == profile['archive_sha256'], 'Published package mismatch')
    need(tuple(bpy.app.version) == tuple(profile['blender_version_numeric']), 'Frozen Blender numeric version mismatch')
    need(Path(os.environ['BLENDER_USER_SCRIPTS']).is_relative_to(out.parent), 'Isolated scripts folder required')
    start = time.perf_counter(); checks = []
    bpy.ops.preferences.addon_install(filepath=str(source_archive), overwrite=False)
    import addon_utils
    addon_utils.enable('optic_neuro_blender', default_set=False, persistent=True)
    import optic_neuro_blender as addon
    from optic_neuro_blender.bootstrap import PACKAGE, verify_bundle
    from optic_neuro_blender.model import capture_current, apply_positions
    from optic_neuro_blender.runtime import read_json
    need(PACKAGE.is_relative_to(Path(os.environ['BLENDER_USER_SCRIPTS'])), 'Installed package is not isolated')
    manifest = verify_bundle()
    need(hashlib.sha256((PACKAGE / 'package_manifest.json').read_bytes()).hexdigest() == profile['manifest_sha256'], 'Frozen manifest mismatch')
    checks.append({'name': 'actual_isolated_zip_install_and_registration', 'pass': True, 'manifest_files': len(manifest['files'])})
    need(bpy.ops.optic_neuro.load_example() == {'FINISHED'}, 'Own example operator failed')
    example = Path(bpy.data.filepath); original_pin = hashlib.sha256(example.read_bytes()).hexdigest()
    settings = bpy.context.scene.optic_neuro_settings
    jobs = out / 'jobs'; jobs.mkdir(); settings.work_directory = str(jobs)
    settings.amplitudes = profile['amplitudes']; settings.phases = profile['phases_rad']
    initial_capture = capture_current()
    need(bpy.ops.optic_neuro.infer() == {'FINISHED'}, 'Inference operator failed')
    inferred_folder = addon._last_folder
    until = time.monotonic() + 180
    while addon._job.state == 'RUNNING' and time.monotonic() < until:
        addon.poll_job(); time.sleep(.1)
    need(addon._job.state == 'COMPLETED', 'Actual background Blender inference did not complete')
    request, inference = addon.validate_recovery(inferred_folder)
    prior = read_json(PACKAGE / 'data/training_result.json')
    difference = float(np.max(np.abs(np.asarray(inference['all150_native_powers']) - np.asarray(prior['observed_powers']))))
    need(difference <= profile['power_tolerance'] and inference['all150_predictions'] == prior['predictions'], 'Installed all150 inference differs from published own training')
    checks.append({'name': 'actual_background_blender_inference_all150', 'pass': True, 'power_max_difference': difference, 'worker_blender_version': inference['blender_version']})
    settings.phases[0] += .01
    try:
        addon.validate_recovery(inferred_folder)
    except ValueError:
        checks.append({'name': 'changed_input_stale_rejected', 'pass': True})
    else:
        raise ValueError('Changed inputs accepted stale result')
    settings.phases = profile['phases_rad']
    obj = bpy.data.objects['c00.r1']; old = obj.matrix_world.copy()
    modified = old.copy(); modified[0][3] += .0001; obj.matrix_world = modified
    try:
        addon.validate_recovery(inferred_folder)
    except ValueError:
        checks.append({'name': 'changed_scene_stale_rejected', 'pass': True})
    else:
        raise ValueError('Changed geometry accepted stale result')
    obj.matrix_world = old; bpy.context.view_layer.update()
    addon.validate_recovery(inferred_folder)
    need(bpy.ops.optic_neuro.infer() == {'FINISHED'}, 'Cancellation fixture failed to start')
    cancelled_folder = addon._last_folder
    need(bpy.ops.optic_neuro.cancel() == {'FINISHED'} and addon._job.state == 'CANCELLED' and addon._job.process.poll() is not None, 'Owned cancellation failed')
    checks.append({'name': 'actual_blender_owned_cancel_and_evidence', 'pass': True, 'result_collected': read_json(cancelled_folder / 'supervision.json')['result_collected']})
    need(bpy.ops.optic_neuro.train() == {'FINISHED'}, 'Native own training operator failed')
    trained_folder = addon._last_folder
    until = time.monotonic() + 1200
    while addon._job.state == 'RUNNING' and time.monotonic() < until:
        addon.poll_job(); time.sleep(.1)
    need(addon._job.state == 'COMPLETED', 'Actual background Blender own training did not complete')
    request, trained = addon.validate_recovery(trained_folder)
    need(trained['training']['geometry_audited_states'] == 61, 'Every optimizer state must be audited')
    training_power_difference = float(np.max(np.abs(np.asarray(trained['all150_native_powers']) - np.asarray(prior['observed_powers']))))
    # Cross-runtime optimizer trajectory is observed, not required to be bit-identical.
    need(trained['training_native_power_max_difference'] <= profile['power_tolerance'], 'Own training native inference mismatch')
    checks.append({'name': 'actual_training_inside_background_blender', 'pass': True, 'states': 61,
                   'initial_loss': trained['training']['initial_train_loss'], 'final_loss': trained['training']['final_train_loss'],
                   'test_correct': trained['training']['test_correct'], 'power_difference_from_earlier_runtime': training_power_difference,
                   'native_power_difference': trained['training_native_power_max_difference']})
    # Reload the addon to prove completed evidence can be recovered after runtime state is gone.
    addon.unregister(); addon.register()
    settings = bpy.context.scene.optic_neuro_settings
    settings.amplitudes = profile['amplitudes']; settings.phases = profile['phases_rad']; settings.recover_directory = str(trained_folder)
    need(bpy.ops.optic_neuro.apply() == {'FINISHED'}, 'Apply/recovery operator failed')
    need(capture_current()['state_sha256'] == trained['final_capture_state_sha256'], 'Recovered native geometry differs')
    checks.append({'name': 'completed_training_recovery_and_atomic_apply', 'pass': True})
    saved = out / 'recovered_geometry.blend'; settings.save_path = str(saved)
    need(bpy.ops.optic_neuro.save_copy() == {'FINISHED'}, 'New copy operator failed')
    need(bpy.data.filepath == str(example) and hashlib.sha256(example.read_bytes()).hexdigest() == original_pin, 'Original installed example changed')
    before = capture_current()['state_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(saved), load_ui=False, use_scripts=False)
    need(capture_current()['state_sha256'] == before, 'Saved recovered geometry changed on reopen')
    checks.append({'name': 'new_copy_reopen_and_original_preserved', 'pass': True})
    # Exact request + result byte integrity is checked on recovery.
    path = trained_folder / 'result.json'; raw = path.read_bytes(); path.write_bytes(raw + b' ')
    try:
        addon.validate_recovery(trained_folder)
    except ValueError:
        checks.append({'name': 'modified_result_receipt_rejected', 'pass': True})
    else:
        raise ValueError('Modified result accepted')
    finally:
        path.write_bytes(raw)
    report = {'schema': 'optic_neuro_blender.installed_native_audit.v1', 'status': 'PASS', 'checks': checks,
              'profile_sha256': hashlib.sha256(profile_path.read_bytes()).hexdigest(), 'archive_sha256': profile['archive_sha256'],
              'manifest_sha256': profile['manifest_sha256'], 'blender_version': bpy.app.version_string,
              'seconds': time.perf_counter() - start, 'original_example_preserved': True,
              'scope': 'Actual isolated local Blender ZIP installation and own registered operators, background inference/training, cancellation, stale rejection, completed-job recovery and copy/reopen. Headless automation is not human UI usability, outside expert replication, physical calibration or AMD GPU execution.'}
    (out / 'result.json').write_bytes((json.dumps(report, indent=2, allow_nan=False) + '\n').encode())
    addon.unregister()
    print(json.dumps({'status': 'PASS', 'checks': len(checks), 'seconds': report['seconds']}), flush=True)


if __name__ == '__main__':
    main()
