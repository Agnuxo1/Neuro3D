import base64,datetime,hashlib,json,subprocess,zlib
from pathlib import Path
own=json.loads("{\"Blender/tests/test_existing_p03_backend_scope_HOST_v1.py\":{\"sha256\":\"a78fc4e556f4230e259f1f50633b2570a2aa634db84f715fbb0701d21d7e2886\",\"bytes\":6401},\"Docs/EXP-005-EXISTING-P03-BACKEND-SCOPE-HOST-001.md\":{\"sha256\":\"eaa8585440dad6f025b59e4199d7e70f35649b609bdb3be3a6f738ee0ca12c74\",\"bytes\":3829},\"coordinacion/respuestas/PRECISION-EXISTING-P03-BACKEND-SCOPE-HOST-001-CODEX.json\":{\"sha256\":\"71bc2991dc808dac8a28cb191c0b5e7b14d4d420da46ee3a1d598373e1e84b2c\",\"bytes\":30194}}")
assert subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()=='a07fd8c9caf71a4d5ebfbaadd0265e6848cf8ed3'
assert not subprocess.check_output(['git','diff','--cached','--name-only']).strip()
assert not subprocess.check_output(['git','status','--porcelain','--',*own.keys()]).strip()
for p,pin in own.items():
 b=Path(p).read_bytes();assert hashlib.sha256(b).hexdigest()==pin['sha256'] and len(b)==pin['bytes']
 assert subprocess.check_output(['git','show','HEAD:'+p])==b
r=json.loads(Path('coordinacion/respuestas/PRECISION-EXISTING-P03-BACKEND-SCOPE-HOST-001-CODEX.json').read_bytes())
for p,pin in r['pins'].items():
 b=Path(p).read_bytes();assert hashlib.sha256(b).hexdigest()==pin['sha256'] and len(b)==pin['bytes'],p
for cap in [r['test_run'],r['oracle_run']]+[f['capture']for f in r['initial_failures']]:
 raw=zlib.decompress(base64.b64decode(cap['stdout_zlib_base64']));assert len(raw)==cap['stdout_bytes'] and hashlib.sha256(raw).hexdigest()==cap['stdout_sha256']
 assert cap['before_deadline'] and cap['affinity_mask']==1 and cap['RAM_reserve_after_budget_bytes']>=4*1024**3
 assert datetime.datetime.fromisoformat(cap['ended_utc'])<datetime.datetime.fromisoformat(cap['deadline_utc'])
assert Path('.cognition/neuro3d-mega-geometry-20261005/existing_p03_backend_scope_oracle.py').read_text()==r['oracle_code']
m=json.loads(Path('coordinacion/respuestas/GPU-GUARD-OWNED-TREE-CONTAINMENT-CPU-001-CODEX.json').read_bytes())['pinned_manifest_capture']
raw=zlib.decompress(base64.b64decode(m['stdout_zlib_base64']));assert hashlib.sha256(raw).hexdigest()==m['stdout_sha256']
pins=json.loads(raw)['pins'];assert len(pins)==461
for p,sha in pins.items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==sha,p
boards={}
for p in ('coordinacion/CHECKPOINT.md','coordinacion/COLA-DE-TRABAJO.md','coordinacion/THINKTANK.md','coordinacion/TABLON.md'):
 b=Path(p).read_bytes();s=b.decode();assert r['id'] in s.splitlines()[2]
 if p.endswith('TABLON.md'):assert r['id'] in [x for x in s.splitlines() if x.startswith('|')][-1]
 boards[p]=hashlib.sha256(b).hexdigest()
print(json.dumps(dict(status='PASS',raw_HEAD_equals_disk=True,own_clean=True,index_empty=True,frozen_pins=461,archive_and_own_pins=17,boards=boards,foreign_code_executed=False,new_GPU_execution=False)))
