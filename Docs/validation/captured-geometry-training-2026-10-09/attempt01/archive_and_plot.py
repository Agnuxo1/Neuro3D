from pathlib import Path
import datetime,hashlib,json,shutil,subprocess,sys
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=Path('D:/PROJECTS/Neuro3D-Scientific-20261008')
private=Path('D:/PROJECTS/.cognition/neuro3d-sequential-20261008/captured-geometry-training-20261009-run01')
dest=root/'Docs/validation/captured-geometry-training-2026-10-09/attempt01';shutil.copytree(private,dest)
report=json.loads((dest/'supervisor.json').read_text());result=json.loads((dest/'worker/result.json').read_text())
assert report['primary_metric']==1
for name,pin in report['raw_file_sha256'].items():assert hashlib.sha256((dest/name).read_bytes()).hexdigest()==pin
test=subprocess.run([sys.executable,'-X','utf8','-m','unittest','Blender.tests.test_affine_geometry_network_v1','Blender.tests.test_frozen_geometry_training_v1','-v'],cwd=root,capture_output=True)
(dest/'controls.log').write_bytes(test.stdout+test.stderr);assert test.returncode==0
rows=[json.loads(line) for line in (dest/'worker/progress.jsonl').read_text().splitlines()]
assert len(rows)==61 and all(r['geometry_audit']['primary_metric']==1 for r in rows)
plt.rcParams.update({'font.size':10})
fig,(a,b)=plt.subplots(1,2,figsize=(10.5,4.1),layout='constrained')
a.plot([r['step'] for r in rows],[r['train_loss'] for r in rows],color='#1565a8');a.set(xlabel='Actualización prefijada',ylabel='Entropía cruzada de entrenamiento',yscale='log',title='Gradientes propios desde geometría')
a.grid(alpha=.2)
profile=json.loads((dest/'profile.json').read_text());truth={i:i//50 for i in range(150)}
cm=np.zeros((3,3),dtype=int)
for i in profile['test_indices']:cm[truth[i],result['predictions'][i]]+=1
b.imshow(cm,cmap='Blues',vmin=0,vmax=10)
for i in range(3):
    for j in range(3):b.text(j,i,str(cm[i,j]),ha='center',va='center',color='white' if cm[i,j]>=6 else 'black')
b.set(xticks=range(3),yticks=range(3),xticklabels=['setosa','versicolor','virginica'],yticklabels=['setosa','versicolor','virginica'],xlabel='Predicción del último estado',ylabel='Especie',title=f"Filas reservadas: {result['test_correct']}/30")
fig.suptitle('Captura Iris: 16 traslaciones de parejas de espejos; 61 estados geométricos auditados')
fig.text(.02,-.035,'Validación computacional local. Iris ya utilizado en el proyecto; sin afirmación de novedad o fidelidad física.',fontsize=9)
asset=root/'Docs/assets/captured-own-geometry-training-2026-10-09.png';fig.savefig(asset,dpi=170,bbox_inches='tight');plt.close(fig)
(dest/'archive_and_plot.py').write_bytes(Path(__file__).read_bytes())
index={p.relative_to(dest).as_posix():{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in dest.rglob('*') if p.is_file()}
(dest/'evidence_index.json').write_bytes((json.dumps(index,indent=2)+'\n').encode())
accept=root/'Docs/research/optic_neuro_blender_acceptance_v1.json';a=json.loads(accept.read_text())
for entry in a['priorities']:
    if entry['id']==5:
        entry.update(status='PARTIAL_OWN_CAPTURED_GEOMETRY_TRAINING_VERIFIED',achieved='16pairedmirrortranslations; owngeometryforward/gradients;61independentlyauditedquantizedstates; train110/120,heldout27/30; historicaltraineddelaysreset; freshfinalfieldrebuilderror<=4.619448428525917e-16',remaining='Actual Blender save/reopen/recapture and inference; wider families and clean installation; testdataset was previously examined')
    if entry['id']==7:entry['achieved']='Frozen separated120/30Irisrows,trainonlyscaler,lastprefixedmodel90percentheldout; no equivalent baseline or new independent dataset yet'
a['latest_training_result']='Docs/validation/captured-geometry-training-2026-10-09/attempt01/worker/result.json'
accept.write_bytes((json.dumps(a,indent=2)+'\n').encode())
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
c=Path('D:/PROJECTS/.cognition/neuro3d-sequential-20261008/CHECKPOINT.md')
with c.open('a',encoding='utf-8') as s:s.write(f'\n## {now} — own captured geometry training PASS\nProfilef97e3406-1d52-4d9c-a477-131bb83a8dd7 SHA0eba46caad4b11a4405910d80d6d52c802e7db743e5b267004612d563f971914 published7d09d00 beforeexecution; sources18Gitbytesmatch. Trial369.4277s,RSS59.3203MiB;61states allgeometryauditsPASS. Resetoldtraineddelays tobs1+2BU plusfrozenrandom perturbation,16pairedtranslationparams; loss6.255440538348521→0.30970667211199093; train110/120,heldout27/30; ownall16lossgradientFDmaxerror1.4746713077329332e-6<1e-4; finalfreshgeometricfieldrebuildmaxerror4.619448428525917e-16<1e-11. Nolegacyanalyticmatrix/weights consumed; Irispreviouslyused, no newblinddatasetclaim. Result/privatehashesverified and archived; nextactualBlendersave/reopenrecapture trial. Correction: precedingcheckpoint heading02:56 was a manual approximate timestamp written before02:52:40; evidence facts unchanged. Newtimestamps taken fromUTCclock.\n')
print(json.dumps({'files':len(index),'train_correct':result['train_correct'],'test_correct':result['test_correct'],'cost':result['cost_seconds']}))
