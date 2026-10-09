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
print(json.dumps(dict(status='PASS',archive_and_own_pins=20,retained_group_durations=10,exact_decimal_reconciliations=5,source_timer_boundaries=True,frozen_pins=461,full_cost_certified=False,energy_joules=None,durations=a)))
