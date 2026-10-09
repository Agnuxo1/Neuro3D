import base64,hashlib,json,zlib
from fractions import Fraction as F
from pathlib import Path
r=json.loads(Path('coordinacion/respuestas/PRECISION-EXISTING-P03-COST-SCOPE-HOST-001-CODEX.json').read_bytes())
for p,pin in r['pins'].items():
 b=Path(p).read_bytes();assert hashlib.sha256(b).hexdigest()==pin['sha256'] and len(b)==pin['bytes'],p
raw=zlib.decompress(base64.b64decode(r['test_run']['stdout_zlib_base64']))
assert hashlib.sha256(raw).hexdigest()==r['test_run']['stdout_sha256']
qa=json.loads(raw);assert qa['status']=='PASS' and qa['tests']==3 and len(qa['records'])==13
base=Path('D:/PROJECTS/.cognition/neuro3d/p0_scene_gpu')
result=json.loads((base/'p03_cuda_result.json').read_bytes(),parse_float=F)
env=json.loads((base/'p03_cuda_envelope.json').read_bytes(),parse_float=F)
rows=[x for x in qa['records'] if x['kind']=='RETAINED_GROUP_ENGINE_DURATION'];assert len(rows)==10
for row,g in zip(rows,result['groups'],strict=True):
 assert row['shape']==g['shape'] and F(row['seconds'])==g['seconds_total']
a=[x for x in qa['records'] if x['kind']=='RETAINED_DURATION_ARITHMETIC_ONLY'][0]
total=sum((g['seconds_total'] for g in result['groups']),F(0))
assert F(a['engine_group_sum_seconds'])==total
assert F(a['harness_recorded_seconds'])==result['seconds']
assert F(a['guard_envelope_seconds'])==env['seconds']
assert F(a['harness_minus_group_sum_seconds'])==result['seconds']-total
assert F(a['guard_minus_harness_seconds'])==env['seconds']-result['seconds']
assert not a['subtraction_proves_overhead'] and not a['performance_comparison']
code=Path('D:/PROJECTS/.cognition/neuro3d/nebulatrace/gpu_states_v2.py').read_text()
trace=code[code.index('def trace('):]
assert trace.index('quant_policy(B, policy, quant, dquant)')<trace.index('t0 = time.perf_counter()')
h=(base/'p03_harness_v4.py').read_text()
assert h.index('Bt = gs.Batch(snaps, DEV)')<h.index('r = gs.trace(Bt, policy=POLICY)')<h.index("U = r['U'].cpu().numpy()")<h.index('f = complex(U[i, pi] @ amp)')
assert h.index("res['seconds'] = time.time() - t0")<h.index("json.dump(res, open(OUT, 'w')")
assert all('seconds_trace' not in g for g in result['groups'])
assert all('seconds_total' not in result[k] for k in ('mzi','conf1','strict_control'))
assert not r['full_cost_certified'] and r['energy_joules'] is None and not r['precision_promotion']
m=json.loads(Path('coordinacion/respuestas/GPU-GUARD-OWNED-TREE-CONTAINMENT-CPU-001-CODEX.json').read_bytes())['pinned_manifest_capture']
b=zlib.decompress(base64.b64decode(m['stdout_zlib_base64']));assert hashlib.sha256(b).hexdigest()==m['stdout_sha256']
pins=json.loads(b)['pins'];assert len(pins)==461
for p,sha in pins.items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==sha,p
import subprocess
own=json.loads("{\"Blender/tests/test_existing_p03_cost_scope_HOST_v1.py\":{\"sha256\":\"bcfc6c986eaa878b23e011075a0e4b41e51215e5f94f111c8270e753171e404a\",\"bytes\":5523},\"Docs/EXP-005-EXISTING-P03-COST-SCOPE-HOST-001.md\":{\"sha256\":\"dd3d394577ba7ef634e3fc1ab7913b0619c1196726e9ee2af2f21736b984df6e\",\"bytes\":3587},\"coordinacion/respuestas/PRECISION-EXISTING-P03-COST-SCOPE-HOST-001-CODEX.json\":{\"sha256\":\"8253dff5124fb8a9c5b9206140a560c17611834bf3ac3ea9790c6fb546e49e58\",\"bytes\":15796}}")
assert subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()=='b3db56243ce1ac45b467eb64c6e606ace9b46be3'
assert not subprocess.check_output(['git','diff','--cached','--name-only']).strip()
assert not subprocess.check_output(['git','status','--porcelain','--',*own.keys()]).strip()
for p,pin in own.items():
 b=Path(p).read_bytes();assert hashlib.sha256(b).hexdigest()==pin['sha256'] and len(b)==pin['bytes']
 assert subprocess.check_output(['git','show','HEAD:'+p])==b
for cap in [r['test_run'],r['oracle_run']]:
 b=zlib.decompress(base64.b64decode(cap['stdout_zlib_base64']));assert hashlib.sha256(b).hexdigest()==cap['stdout_sha256'] and len(b)==cap['stdout_bytes']
 assert cap['before_deadline'] and cap['affinity_mask']==1 and cap['RAM_reserve_after_budget_bytes']>=4*1024**3
assert Path('.cognition/neuro3d-mega-geometry-20261005/existing_p03_cost_scope_oracle.py').read_text()==r['oracle_code']
boards={}
for p in ('coordinacion/CHECKPOINT.md','coordinacion/COLA-DE-TRABAJO.md','coordinacion/THINKTANK.md','coordinacion/TABLON.md'):
 b=Path(p).read_bytes();s=b.decode();assert r['id'] in s.splitlines()[2]
 if p.endswith('TABLON.md'):assert r['id'] in [x for x in s.splitlines() if x.startswith('|')][-1]
 boards[p]=hashlib.sha256(b).hexdigest()
print(json.dumps(dict(status='PASS',raw_HEAD_equals_disk=True,own_clean=True,index_empty=True,archive_and_own_pins=20,frozen_pins=461,post_review_independent_reconciliations=5,boards=boards,foreign_code_executed=False,new_GPU_execution=False,full_cost_certified=False)))
