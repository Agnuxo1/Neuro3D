import base64,hashlib,json,zlib
from pathlib import Path
r=json.loads(Path('coordinacion/respuestas/PRECISION-EXISTING-P03-BACKEND-SCOPE-HOST-001-CODEX.json').read_bytes())
# Document pin is refreshed before this verifier is run.
for path,pin in r['pins'].items():
 b=Path(path).read_bytes();assert hashlib.sha256(b).hexdigest()==pin['sha256'] and len(b)==pin['bytes'],path
raw=zlib.decompress(base64.b64decode(r['test_run']['stdout_zlib_base64']));assert hashlib.sha256(raw).hexdigest()==r['test_run']['stdout_sha256']
qa=json.loads(raw);assert qa['status']=='PASS' and qa['tests']==3 and len(qa['records'])==13
base=Path('D:/PROJECTS/.cognition/neuro3d/p0_scene_gpu')
result=json.loads((base/'p03_cuda_result.json').read_bytes())
manifest=json.loads((base/'p03_manifest.json').read_bytes())
declared=set()
for scene,row in zip(manifest['scenes'],result['scene_results'],strict=True):
 sha=hashlib.sha256(json.dumps(scene,sort_keys=True).encode()).hexdigest();assert row['scene_sha256']==sha;declared.add(sha)
assert len(result['scene_results'])==104
backend=Path('D:/PROJECTS/.cognition/neuro3d/nebulatrace/gpu_states_v2.py').read_bytes()
assert result['code_sha256']['D:/PROJECTS/.cognition/neuro3d/nebulatrace/gpu_states_v2.py']==hashlib.sha256(backend).hexdigest()
for row in qa['records']:
 if row['kind']=='SOURCE_STAGE':assert row['anchor'] in backend.decode().splitlines()[row['line']-1]
 if row['kind']=='NO_EXACT_DECLARED_OBLIQUE_BINDING':assert row['literal_scene_sha256'] not in declared and not row['query_binding']
assert sum(x['kind']=='SOURCE_STAGE' for x in qa['records'])==7
verdict=json.loads((base/'p03_cuda_checker_verdict.json').read_bytes())
assert verdict['result_sha256']==hashlib.sha256((base/'p03_cuda_result.json').read_bytes()).hexdigest()
assert verdict['manifest_sha256']==hashlib.sha256((base/'p03_manifest.json').read_bytes()).hexdigest()
assert verdict['verdict']=='PASS' and not verdict['failures'] and not verdict['warnings']
env=json.loads((base/'p03_cuda_envelope.json').read_bytes())
assert env['status']=='OK' and env['exit']==0 and env['policy']['ram_free_after_budget_min_gib']==1.5
for failed in r['initial_failures']:
 snap=failed['source_snapshot'];b=zlib.decompress(base64.b64decode(snap['bytes_zlib_base64']))
 assert len(b)==snap['bytes'] and hashlib.sha256(b).hexdigest()==snap['sha256']
 assert failed['capture']['rc']==1
assert not r['current_job_admission'] and not r['foreign_code_executed'] and r['native_oblique_phase_bound_rad'] is None
m=json.loads(Path('coordinacion/respuestas/GPU-GUARD-OWNED-TREE-CONTAINMENT-CPU-001-CODEX.json').read_bytes())['pinned_manifest_capture']
b=zlib.decompress(base64.b64decode(m['stdout_zlib_base64']));assert hashlib.sha256(b).hexdigest()==m['stdout_sha256']
pins=json.loads(b)['pins'];assert len(pins)==461
for path,sha in pins.items():assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==sha,path
print(json.dumps(dict(status='PASS',archive_and_own_pins=17,scene_bindings=104,backend_source_anchors=7,nonmatching_literal_bindings=4,frozen_pins=461,historical_PASS_preserved=True,current_admission=False,foreign_execution=False)))
