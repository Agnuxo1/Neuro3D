import datetime
import hashlib
import json
from pathlib import Path
import shutil
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

base = Path(__file__).resolve().parent
repo = Path('D:/PROJECTS/Neuro3D-Scientific-20261008')
private = base / 'own-blender-addon-20261009-run03'
report = json.loads((private / 'supervisor.json').read_bytes())
assert report['status'] == 'VALID_INSTALLED_NATIVE_ADDON_AUDIT' and report['primary_metric'] == 1
dest = repo / 'Docs/validation/own-blender-addon-2026-10-09/attempt03'
shutil.copytree(private, dest, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
for name, pin in report['raw_file_sha256'].items():
    assert hashlib.sha256((dest / name).read_bytes()).hexdigest() == pin, name
for name in ['published-own-addon-v3-20261009.json', 'prepare_own_addon_sources_v3_20261009.py', 'prepare_own_addon_profile_v3_20261009.py']:
    shutil.copyfile(base / name, dest / name)
native = json.loads((dest / 'worker/result.json').read_bytes()); assert len(native['checks']) == 9 and all(row['pass'] for row in native['checks'])
jobroot = dest / 'worker/jobs'
training_folder = next(path.parent for path in jobroot.glob('*/result.json') if json.loads(path.read_bytes())['action'] == 'TRAIN')
inference_folder = next(path.parent for path in jobroot.glob('*/result.json') if json.loads(path.read_bytes())['action'] == 'INFER')
training_result = json.loads((training_folder / 'result.json').read_bytes())
inference = json.loads((inference_folder / 'result.json').read_bytes())
history = [json.loads(line) for line in (training_folder / 'training/progress.jsonl').read_text().splitlines()]
assert len(history) == 61 and all(row['geometry_audit']['primary_metric'] == 1 for row in history)
fig, axes = plt.subplots(1, 2, figsize=(12, 4.7), layout='constrained')
axes[0].plot([row['step'] for row in history], [row['train_loss'] for row in history], '-o', markersize=2)
axes[0].set(xlabel='Actualización geométrica', ylabel='Pérdida de entrenamiento', title='Entrenamiento propio dentro de Blender: 61 estados auditados')
axes[0].grid(alpha=.2)
ports = inference['ports']; powers = [inference['powers'][port] for port in ports]
axes[1].bar(ports, powers)
axes[1].tick_params(axis='x', rotation=45)
axes[1].set(ylabel='Potencia modal normalizada', title='Inferencia compleja desde la escena instalada')
axes[1].text(.5, .98, 'Potencia de entrada total: ' + format(inference['input_total_normalized_power'], '.6g'), transform=axes[1].transAxes, ha='center', va='top')
fig.suptitle('ZIP0.1.1: prueba nativa local de operadores; pendiente corregir doble desregistro al cerrar')
asset = repo / 'Docs/assets/own-blender-addon-native-training-2026-10-09.png'; fig.savefig(asset, dpi=170, bbox_inches='tight'); plt.close(fig)
receipt = {'scope': 'Factual operator receipt, not raw stdout', 'all_nine_frozen_native_controls_passed': True, 'metric': 1, 'shutdown_log_contains_double_unregister_RuntimeError': True, 'shutdown_issue_affects_declared_numeric_or_training_result': False, 'shutdown_lifecycle_closed': False, 'next_action': 'Separate versioned package idempotent registration/unregistration and short actual lifecycle audit; preserve original metric and raw log', 'training_job_relative': training_folder.relative_to(dest).as_posix(), 'inference_job_relative': inference_folder.relative_to(dest).as_posix()}
(dest / 'operator_lifecycle_limitation_receipt.json').write_bytes((json.dumps(receipt, indent=2) + '\n').encode())
(dest / 'archive_and_plot.py').write_bytes(Path(__file__).read_bytes())
index = {path.relative_to(dest).as_posix(): {'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'bytes': path.stat().st_size} for path in dest.rglob('*') if path.is_file()}
(dest / 'evidence_index.json').write_bytes((json.dumps(index, indent=2) + '\n').encode())
accept_path = repo / 'Docs/research/optic_neuro_blender_acceptance_v1.json'; acceptance = json.loads(accept_path.read_bytes())
for entry in acceptance['priorities']:
    if entry['id'] == 6:
        entry.update(achieved='Restrictedquadraticcapacity and3seedWinevariability; originalGaussianwindownegativepreserved; separatelyfrozenlargerwindow36casespassallsamegates,observedradialfieldmax9.292e-8L64. Fullnetworkphysicalfidelityunknown', remaining='Parameter/input/nativeuncertaintyrobustness andfullnetworkwave model/physicalmeasurements; declaredGaussianfamilydoesnotderivecapturedmode')
    if entry['id'] == 9:
        entry.update(status='PARTIAL_STANDALONE_NATIVE_ADDON_FLOW_VERIFIED_WITH_OPEN_SHUTDOWN_LIFECYCLE', achieved='ZIP0.1.1 isolatedactualinstall/registeredoperators; ownbackgroundBlenderinfer150/training61audits27of30,staleinput/scene,ownedcancel,recover/apply,newcopy/reopen,tamperrejectionPASS9. Originalpreserved;shutdownlogshowsdoubleunregisterRuntimeError retained', remaining='Idempotentregistration/unregistration shortnativeaudit; interruptedhost/crashrecovery,Windows/Linuxcleaninstallandspecialistoutsideusability')
    if entry['id'] == 5:
        entry['achieved'] += '; ZIP0.1.1 ownoptimizerandmanualgradients runinsidebackgroundBlender,61audits,all150nativepowerdifference0 and27of30sameheldout'
acceptance['latest_own_addon_native_audit'] = dest.relative_to(repo).as_posix() + '/worker/result.json'
acceptance['latest_wave_remedial'] = 'Docs/validation/gaussian-wave-remedial-2026-10-09/attempt01/worker/result.json'
accept_path.write_bytes((json.dumps(acceptance, indent=2) + '\n').encode())
stats = {'metric': 1, 'checks': 9, 'seconds': report['worker_seconds'], 'rss_mib': report['peak_owned_aggregate_rss_mib'], 'raw_files': len(index), 'result_sha256': report['result_sha256'], 'training_job_relative': receipt['training_job_relative'], 'inference_job_relative': receipt['inference_job_relative'], 'native_training_loss': [training_result['training']['initial_train_loss'], training_result['training']['final_train_loss']], 'test_correct': training_result['training']['test_correct'], 'all150_native_training_power_difference': training_result['training_native_power_max_difference'], 'shutdown_lifecycle_error_retained': True}
(base / 'own-addon-native-summary-20261009.json').write_bytes((json.dumps(stats, indent=2) + '\n').encode())
with (base / 'CHECKPOINT.md').open('a', encoding='utf-8') as stream:
    stream.write('\n## ' + datetime.datetime.now(datetime.timezone.utc).isoformat() + ' — own standalone native addon nine controls PASS, lifecycle gap retained\nFrozenb7127929/profilef862a823/source32Gitblobsverifiedbeforedata. Stats=' + json.dumps(stats) + '. NativebackgroundBlenderowntrainingexactlysame27of30/61audits/loss6.25544→.3097067;all150powersdifference0. Originalpreserved,allrawSHAverified. ShutdownlogdoubleunregisterRuntimeErrorpreservedexplicitly,notpartofthe9originalgates; needsseparatelifecyclefix/profile. Article3125wordsdraftpreparednotyetpublished; externalLinuxCPU38pinprofileecb48f85preparednotpublished/executed, pinnedPyPIwheels/actionsverified. Goalactiveuntil13:55UTC; noAMD/externalIPFSIDs/independenthumanreproduction/noveltyclaim. Nextpublishthisresultbeforechangingaddoninit.\n')
print(json.dumps(stats))
