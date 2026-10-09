import datetime,hashlib,json,shutil,sys
from pathlib import Path
root=Path('D:/PROJECTS/Neuro3D-Scientific-20261008');sys.path.insert(0,str(root))
from Tools.audit_captured_pilot_result_v1 import decode
from Tools.audit_graph_neighborhood_v1 import audit_graph_neighborhood
from Blender.blender_lab.coherent_state_graph_v1 import propagate_graph
from Tools.trace_indexed_scene_v1 import wire
private=Path('D:/PROJECTS/.cognition/neuro3d-sequential-20261008/trained-geometry-blender-reproduction-20261009-run01')
dest=root/'Docs/validation/trained-geometry-blender-reproduction-2026-10-09/attempt01';shutil.copytree(private,dest)
supervisor=json.loads((dest/'supervisor.json').read_text());result=json.loads((dest/'worker/result.json').read_text());assert supervisor['primary_metric']==1
for name,pin in supervisor['raw_file_sha256'].items():assert hashlib.sha256((dest/name).read_bytes()).hexdigest()==pin
scene_wire=json.loads((dest/'worker/scene.json').read_text());scene=decode(scene_wire);g=decode(json.loads((dest/'worker/graph.json').read_text()))
native=propagate_graph(g,{s['id']:s['field_reim'] for s in scene['sources']})
audit=audit_graph_neighborhood(scene_wire,wire({'graph':g,**native}));assert audit['primary_metric']==1
audit['scope']='Secondary independent geometry audit of the actual saved/reopened Blender capture; unit input native field estimates are separate from150classifiedinputs'
(dest/'independent_recaptured_geometry_audit.json').write_bytes((json.dumps(audit,indent=2)+'\n').encode())
(dest/'archive_and_audit.py').write_bytes(Path(__file__).read_bytes())
index={p.relative_to(dest).as_posix():{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in dest.rglob('*') if p.is_file()}
(dest/'evidence_index.json').write_bytes((json.dumps(index,indent=2)+'\n').encode())
accept=root/'Docs/research/optic_neuro_blender_acceptance_v1.json';a=json.loads(accept.read_text())
for e in a['priorities']:
    if e['id']==5:e.update(status='OWN_GEOMETRY_TRAINING_AND_NATIVE_BLENDER_REPRODUCTION_VERIFIED_FOR_FROZEN_IRIS_FAMILY',remaining='Broader geometry/input families and clean installation; testdataset previously examined; numerical field/decision certification for trainedbatch is separate',achieved=e['achieved']+'; actualBlender4.5.14nativeupdate/save/reopen/capturePASS; exactopticalgeometrymatchesvirtualscene; all150powersandpredictionsidentical')
    if e['id']==9:e['achieved']='Actual trainedscene save/reopen/capture and owninferencePASS; originalblend preserved; new interface and clean install stillpending'
a['latest_native_blender_reproduction']='Docs/validation/trained-geometry-blender-reproduction-2026-10-09/attempt01/worker/result.json'
accept.write_bytes((json.dumps(a,indent=2)+'\n').encode())
now=datetime.datetime.now(datetime.timezone.utc).isoformat();c=Path('D:/PROJECTS/.cognition/neuro3d-sequential-20261008/CHECKPOINT.md')
with c.open('a',encoding='utf-8') as s:s.write(f'\n## {now} — trained geometry actual Blender reproduction PASS\nTraining resultpublished ee6860a. Newnativeprofile f5b44ccd-c01b-4aa5-8c79-7c383d4d182c SHA987e22e4345344d800ead8369a6266f5addcc14906de0dc3c67c2ca467da09a3/source29 andBlenderexecutablepins published2e14f4c beforedata. ActualBlender4.5.14 save/reopen/capture exactidentity+exactopticalgeometricalmatchPASS,133statesfreshrebuilt, all150powersmaxdifference0 andall150predictionsidentical. Worker37.6344s,RSS298.59375MiB; nointerruption. Secondaryindependentrecapturednearest/neighborhoodaudit133statesPASS. Originalblendhashpreserved. Newtrainedblendarchived. Next: matchedbaselines/capacity/stability and NVIDIAownforwardgradientbenchmark underFIFOqueue; AMDabsent/externalIPFSandpeerreproductionstillopen. JEVconnectedprovenance=jevconfidence1.\n')
print(json.dumps({'files':len(index),'new_bytes':sum(v['bytes'] for v in index.values()),'states':audit['states'],'native_status':result['status']}))
