from pathlib import Path
import hashlib,json,subprocess,sys,time
root=Path('D:/PROJECTS/Neuro3D-Scientific-20261008');sys.path.insert(0,str(root))
from Tools.audit_graph_neighborhood_v1 import audit_graph_neighborhood
scene=root/'Docs/validation/captured-scalar-ingress-2026-10-08/scene.json'
result=root/'Docs/validation/coherent-state-graph-capture-2026-10-09/attempt01/result.json'
start=time.perf_counter();a=audit_graph_neighborhood(json.loads(scene.read_text()),json.loads(result.read_text()));elapsed=time.perf_counter()-start
dest=root/'Docs/validation/independent-surface-neighborhood-2026-10-09';dest.mkdir(exist_ok=False)
a.update(scene_sha256=hashlib.sha256(scene.read_bytes()).hexdigest(),result_sha256=hashlib.sha256(result.read_bytes()).hexdigest(),elapsed_seconds=elapsed,
         analysis_scope='Deterministic secondary independent audit of previously published observed graph; no new experimental data',method_published_commit='a1b-placeholder')
a['method_published_commit']=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
(dest/'audit.json').write_bytes((json.dumps(a,indent=2)+'\n').encode())
test=subprocess.run([sys.executable,'-X','utf8','-m','unittest','Blender.tests.test_graph_neighborhood_audit_v1','-v'],cwd=root,capture_output=True)
(dest/'controls.log').write_bytes(test.stdout+test.stderr);assert test.returncode==0
for name in ('Tools/audit_graph_neighborhood_v1.py','Tools/audit_coherent_state_graph_v1.py','Tools/audit_captured_pilot_result_v1.py','Blender/tests/test_graph_neighborhood_audit_v1.py'):
    p=dest/'sources'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((root/name).read_bytes())
(dest/'archive_and_audit.py').write_bytes(Path(__file__).read_bytes())
index={p.relative_to(dest).as_posix():{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in dest.rglob('*') if p.is_file()}
(dest/'evidence_index.json').write_bytes((json.dumps(index,indent=2)+'\n').encode())
from fractions import Fraction as F
radii=[F(*w['projected_radius']) for w in a['neighborhood_witnesses']]
print(json.dumps({'status':a['status'],'states':a['states'],'neighborhoods':len(radii),'minimum_projected_radius':float(min(radii)),'elapsed_seconds':elapsed}))
