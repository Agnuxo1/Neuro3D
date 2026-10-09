import base64,ctypes,hashlib,json,subprocess,zlib
from pathlib import Path
k=ctypes.windll.kernel32;k.GetCurrentProcess.restype=ctypes.c_void_p;k.SetProcessAffinityMask.argtypes=[ctypes.c_void_p,ctypes.c_size_t];assert k.SetProcessAffinityMask(k.GetCurrentProcess(),1)
own=json.loads("{\"Blender/tests/test_terminal_parameter_reference_identity_HOST_v1.py\":{\"sha256\":\"d792b261cbd4c70281284e37cc3ae6ee59d156e0aea2425013312adea63be3bf\",\"bytes\":5136},\"Docs/EXP-005-TERMINAL-PARAMETER-REFERENCE-IDENTITY-HOST-001.md\":{\"sha256\":\"226c47803108e0a9eaf43cff5daba2b36cf11a51dab02d1858c16d74208ede72\",\"bytes\":3262},\"coordinacion/respuestas/PRECISION-TERMINAL-PARAMETER-REFERENCE-IDENTITY-HOST-001-CODEX.json\":{\"sha256\":\"20e14db6efae75989f023891cc7decb79002142cc5a9fe9ccd31d0df50221124\",\"bytes\":15795}}")
assert subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()=='f915e4c423d64cd5c58355f3f7d58c493eeb5db9'
assert not subprocess.check_output(['git','diff','--cached','--name-only']).strip()
for p,pin in own.items():
 b=Path(p).read_bytes();assert hashlib.sha256(b).hexdigest()==pin['sha256'] and len(b)==pin['bytes']
 assert subprocess.check_output(['git','show','HEAD:'+p])==b
assert not subprocess.check_output(['git','status','--porcelain','--',*own.keys()]).strip()
r=json.loads(Path('coordinacion/respuestas/PRECISION-TERMINAL-PARAMETER-REFERENCE-IDENTITY-HOST-001-CODEX.json').read_bytes())
for cap in [r['test_run'],r['oracle_run'],r['initial_oracle_failure']['capture']]:
 raw=zlib.decompress(base64.b64decode(cap['stdout_zlib_base64']));assert len(raw)==cap['stdout_bytes'] and hashlib.sha256(raw).hexdigest()==cap['stdout_sha256']
 assert cap['before_deadline'] and cap['affinity_mask']==1 and cap['RAM_reserve_after_budget_bytes']>=4*1024**3
assert Path('.cognition/neuro3d-mega-geometry-20261005/terminal_parameter_reference_oracle.py').read_text()==r['oracle_code']
m=json.loads(Path('coordinacion/respuestas/GPU-GUARD-OWNED-TREE-CONTAINMENT-CPU-001-CODEX.json').read_bytes())['pinned_manifest_capture']
raw=zlib.decompress(base64.b64decode(m['stdout_zlib_base64']));assert hashlib.sha256(raw).hexdigest()==m['stdout_sha256']
pins=json.loads(raw)['pins'];assert len(pins)==461
for p,sha in pins.items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==sha,p
boards={}
for p in ('coordinacion/CHECKPOINT.md','coordinacion/COLA-DE-TRABAJO.md','coordinacion/THINKTANK.md','coordinacion/TABLON.md'):
 b=Path(p).read_bytes();s=b.decode();assert r['id'] in s.splitlines()[2]
 if p.endswith('TABLON.md'):assert r['id'] in [x for x in s.splitlines() if x.startswith('|')][-1]
 boards[p]=hashlib.sha256(b).hexdigest()
print(json.dumps(dict(status='PASS',raw_HEAD_equals_disk=True,own_clean=True,index_empty=True,frozen_pins=461,boards=boards,native_execution=False)))

