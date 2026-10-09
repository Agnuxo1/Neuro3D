import base64,hashlib,json,zlib
from fractions import Fraction as F
from pathlib import Path
r=json.loads(Path('coordinacion/respuestas/PRECISION-TERMINAL-PARAMETER-REFERENCE-IDENTITY-HOST-001-CODEX.json').read_bytes())
for path,pin in r['pins'].items():
 b=Path(path).read_bytes();assert len(b)==pin['bytes'] and hashlib.sha256(b).hexdigest()==pin['sha256']
assert hashlib.sha256(Path(r['shader']['path']).read_bytes()).hexdigest()==r['shader']['sha256']
raw=zlib.decompress(base64.b64decode(r['test_run']['stdout_zlib_base64']))
assert hashlib.sha256(raw).hexdigest()==r['test_run']['stdout_sha256']
q=json.loads(raw);assert q['status']=='PASS' and q['tests']==5 and len(q['records'])==13
def rat(pair):return F(int(pair[0]),int(pair[1]))
count=0
for row in q['records']:
 if row['kind']=='SYNTHETIC_EXACT_IDENTITY':
  dx,dy,dz=map(rat,row['direction']);s=rat(row['s_BU'])
  # Expanded scalar polynomial, independently of vector test functions.
  baseline=F(7,8)+dx*F(3999,4)-dy*F(5,4)-dz
  deviation=s*(1-dx*dx-dy*dy-dz*dz)+F(3,2**57)-dx*F(1,2**60)+dy*F(1,2**59)-dz*F(1,2**58)
  bound=abs(s)*abs(1-dx*dx-dy*dy-dz*dz)+F(7,2**57)+abs(dx)*F(1,2**60)+abs(dy)*F(1,2**59)+abs(dz)*F(1,2**58)
  assert rat(row['baseline_BU'])==baseline and rat(row['deviation_BU'])==deviation
  assert rat(row['effective_BU'])==baseline+deviation and rat(row['allowance_BU'])==bound
  assert abs(deviation)<=bound;count+=1
assert count==8
sens=[rat(x['delta_BU']) for x in q['records'] if x['kind']=='SYNTHETIC_PARAMETER_SENSITIVITY']
assert sens==[0,-F(1,2**51)-F(1,2**104)]
u=[x for x in q['records'] if x['kind']=='SYNTHETIC_UNIT_NONZERO_RESIDUAL'][0]
assert rat(u['value_BU'])==F(1,2**60)
b=[x for x in q['records'] if x['kind']=='SYNTHETIC_BIAS_PARAMETER_ONLY'][0]
assert rat(b['parameter_BU'])==F(3,4) and rat(b['axial_geometric_length_BU'])==F(3,2)
assert not q['native_precision_certified'] and q['native_direction_norm_defect'] is None and q['native_ALU_residual_bound_BU'] is None and q['native_phase_error_bound_rad'] is None and q['scene_replays']==0
m=json.loads(Path('coordinacion/respuestas/GPU-GUARD-OWNED-TREE-CONTAINMENT-CPU-001-CODEX.json').read_bytes())['pinned_manifest_capture']
raw=zlib.decompress(base64.b64decode(m['stdout_zlib_base64']));assert hashlib.sha256(raw).hexdigest()==m['stdout_sha256']
pins=json.loads(raw)['pins'];assert len(pins)==461
for path,sha in pins.items():assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==sha,path
print(json.dumps(dict(status='PASS',independent_scalar_identities=8,sensitivity_controls=2,residual_controls=1,bias_controls=1,frozen_pins=461,production_imports=0,scene_replays=0,GPU_used=False)))
