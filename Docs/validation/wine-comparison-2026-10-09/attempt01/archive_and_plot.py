import datetime,hashlib,json,shutil
from pathlib import Path
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
repo=Path('D:/PROJECTS/Neuro3D-Scientific-20261008');base=Path(__file__).resolve().parent
private=base/'wine-comparison-20261009-run01';report=json.loads((private/'supervisor.json').read_bytes())
assert report['status']=='VALID_FROZEN_WINE_COMPARISON_RESULT' and report['result_collected']
dest=repo/'Docs/validation/wine-comparison-2026-10-09/attempt01';shutil.copytree(private,dest)
for name,pin in report['raw_file_sha256'].items():assert hashlib.sha256((dest/name).read_bytes()).hexdigest()==pin,name
result=json.loads((dest/'worker/result.json').read_bytes());assert len(result['runs'])==3
for run in result['runs']:
    progress=[json.loads(line) for line in (dest/f"worker/seed{run['seed']}/progress.jsonl").read_text().splitlines()]
    assert len(progress)==61 and all(p['geometry_audit']['primary_metric']==1 for p in progress)
for filename in ['wine-published-preexecution-verification-20261009.json','verify_wine_freeze_20261009.py','prepare_wine_protocol_20261009.py']:
    shutil.copyfile(base/filename,dest/filename)
controls={'schema':'optic_neuro_blender.operator_recorded_software_controls.v1','preexecution':True,'tests_passed':5,'tests_failed':0,
          'suite':['Blender.tests.test_classifier_comparison_v1','Blender.tests.test_frozen_wine_profile_v1'],
          'evidence':'Successful tool execution beforecommit0e2e7c1,unittest5tests0.608seconds. This is a factualoperatorreceipt, not a rawstdout capture; no controls rerun solely for logging.'}
(dest/'control_receipt.json').write_bytes((json.dumps(controls,indent=2)+'\n').encode())
plt.rcParams.update({'font.size':10});fig,(a,b)=plt.subplots(1,2,figsize=(11.7,4.6),layout='constrained')
for run in result['runs']:
    rows=[json.loads(line) for line in (dest/f"worker/seed{run['seed']}/progress.jsonl").read_text().splitlines()]
    a.plot([p['step'] for p in rows],[p['train_loss'] for p in rows],label=str(run['seed']))
a.set(xlabel='Actualización prefijada',ylabel='Pérdida de entrenamiento',yscale='log',title='Tres inicializaciones: geometría propia');a.legend(title='Semilla');a.grid(alpha=.2)
models=[r['heldout'] for r in result['runs']]+[r['heldout'] for r in result['baselines']]+[result['majority']['heldout']]
labels=[str(r['seed']) for r in result['runs']]+['Lineal','Cuadrático','Mayoría']
values=np.asarray([m['accuracy'] for m in models]);bounds=np.asarray([m['wilson_95_interval'] for m in models]);positions=np.arange(len(models))
b.bar(positions,values,color=['#2979b9']*3+['#ed8b35','#77913a','#8f8f8f'],width=.6)
b.errorbar(positions,values,yerr=np.array([values-bounds[:,0],bounds[:,1]-values]),fmt='none',color='black',capsize=3)
for i,m in enumerate(models):b.text(i,m['accuracy']+.04,f"{m['correct']}/{m['count']}",ha='center',fontsize=9)
b.set(xticks=positions,xticklabels=labels,ylim=(0,1.12),ylabel='Acierto en 37 filas reservadas',title='Mismos datos y codificación; Wilson 95%');b.grid(axis='y',alpha=.2)
fig.suptitle('Wine: cuatro variables fijadas antes de entrenar; 183 estados geométricos auditados')
fig.text(.025,-.03,'Las tres semillas comparten una partición; no se agrupan como observaciones independientes. Baselines con restricciones distintas.',fontsize=9)
asset=repo/'Docs/assets/wine-geometry-and-baselines-2026-10-09.png';fig.savefig(asset,dpi=170,bbox_inches='tight');plt.close(fig)
(dest/'archive_and_plot.py').write_bytes(Path(__file__).read_bytes())
index={f.relative_to(dest).as_posix():{'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size} for f in dest.rglob('*') if f.is_file()}
(dest/'evidence_index.json').write_bytes((json.dumps(index,indent=2)+'\n').encode())
accept=repo/'Docs/research/optic_neuro_blender_acceptance_v1.json';policy=json.loads(accept.read_bytes())
for entry in policy['priorities']:
    if entry['id']==2:entry['remaining']='Broader geometry/model families and calibrated physical units; existing solver/training consume declared common-coherence unit-power input contract'
    if entry['id']==3:entry['remaining']='Originalpilotdeadline remains unchanged/null; wideradmittedfamilies andexternalregistration remain separate'
    if entry['id']==4:entry['remaining']='Unknown intendedgeometry/native Blender transform andphysicalmodel error; nativeparameter/input uncertainty andtrainedbatch certificates remain separate. ActualNVIDIA60probe outputs haveindependentbounds.'
    if entry['id']==6:entry.update(status='PARTIAL_REAL_QUADRATIC_CAPACITY_AND_THREE_SEED_STABILITY_CHARACTERIZED',achieved='All8ports realquadratic equivalence: rank<=2perdetector; sameinputdensefields/powers reconstructed. Threefixedinitializations and183independentaudits evaluated; broadcapacity/universalitynotclaimed',remaining='Quantifiedparameter/inputperturbation robustness andindependentwave references; actualfullnetworkphysicalerror unknown')
    if entry['id']==7:entry.update(status='PARTIAL_PROSPECTIVE_WINE_HELDOUT_AND_TRAINONLY_BASELINES_VERIFIED',achieved='PublicWine fixedfirst4features,141/37train/test,trainonlyscaler,3fixed60updateseedsallreported;15nominalparamlinear/45nominalparamquadratic convexbaselines sameencoding; Wilsondescriptiveintervals andexploratorypairedMcNemar; noheldoutselection',remaining='Broaderdatasets/tasks, transferwithoutretraining, multiplerandomsplits andexternalblinddata. No superiorityclaim.')
policy['latest_wine_comparison']='Docs/validation/wine-comparison-2026-10-09/attempt01/worker/result.json'
policy['claim_policy']['prospectively_frozen_new_dataset_evaluation_collected']=True
accept.write_bytes((json.dumps(policy,indent=2)+'\n').encode())
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
with (base/'CHECKPOINT.md').open('a',encoding='utf-8') as stream:
    stream.write('\n## '+now+' — Wine complete; raw audit and matched baselines archived\nFrozen0e2e7c1/profileaf7bd4fd/SHA623623be beforeexecution; all3seeds/183geometryauditsPASS, allfinalfreshgeometryrebuildswithinbudget. Supervisorstatus'+report['status']+',metric'+str(report['primary_metric'])+',seconds'+str(report['worker_seconds'])+',RSSMiB'+str(report['peak_owned_rss_mib'])+'. All3heldoutcorrect/37='+str([r['heldout']['correct'] for r in result['runs']])+';baselinecorrect='+str({r['kind']:r['heldout']['correct'] for r in result['baselines']})+'. Onecommonsplit, no pooling/seedingselection; publicdata notexternalblind/zero-shotphysical. Allsupervisorrawhashesverified; raw'+str(len(index))+'files andscienceplotprepared; needpublishresultsnext beforewaveexecution. Waveprofilepreparednotyetpublished/executed,5softwarecontrolsPASS. PrimaryHo2025/QAIBP2023/DeepG2019 reinforce NOVELTY_NOT_ESTABLISHED. Goalactive until13:55UTC.\n')
print(json.dumps({'files':len(index),'supervisor':{k:report[k] for k in ('status','primary_metric','worker_seconds','peak_owned_rss_mib')},'runs':[{'seed':r['seed'],'loss':[r['initial_train_loss'],r['final_train_loss']],'train':r['train'],'heldout':r['heldout'],'gradient_fd':r['gradient_difference_max_absolute_error'],'rebuild':r['field_rebuild_max_absolute_error'],'cost':r['cost_seconds'],'paired':r['paired_baselines']} for r in result['runs']],'baselines':result['baselines'],'majority':result['majority']}))
