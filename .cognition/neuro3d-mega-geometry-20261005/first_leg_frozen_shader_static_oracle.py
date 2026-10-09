import ast,base64,hashlib,json,zlib
from pathlib import Path
root=Path.cwd()
def sha(b):return hashlib.sha256(b).hexdigest()
r=json.loads((root/'coordinacion/respuestas/PRECISION-FIRST-LEG-FROZEN-SHADER-STATIC-AUDIT-HOST-001-CODEX.json').read_bytes())
for p,h in r['code_doc_sha256'].items():
 b=(root/p).read_bytes();assert sha(b)==h
 if p.endswith('.py'):ast.parse(b)
c=r['test_run'];b=zlib.decompress(base64.b64decode(c['stdout_zlib_base64'],validate=True))
assert c['rc']==0 and c['before_deadline'] and not c['timed_out']
assert sha(b)==c['stdout_sha256'] and len(b)==c['stdout_bytes']
d=json.loads(b);assert d['status']=='PASS' and d['tests']==2 and len(d['records'])==11
out=d['records'][0]['result'];assert d['records'][0]['kind']=='PINNED_STATIC_AUDIT'
assert out['status']=='STATIC_SOURCE_PATH_DIFFERS_FROM_HYPOTHETICAL_ENDPOINT_NORM_GRAPH'
count=0
for p,record in out['evidence'].items():
 b=(root/p).read_bytes();assert sha(b)==record['sha256']==r['source_pins'][p]['sha256']
 assert len(b)==record['bytes']==r['source_pins'][p]['bytes']
 lines=b.decode('utf-8').splitlines()
 for role,a in record['anchors'].items():
  assert lines[a['line']-1].strip()==a['code']
  assert sum(s.strip()==a['code']for s in lines)==1;count+=1
s=(root/'Blender/shaders/exp005_shared_frontier.glsl').read_text(encoding='utf-8')
nearest=s.split('void nearest(',1)[1].split('void main()',1)[0]
main=s.split('void main()',1)[1]
assert 'dvec3 biased=origin+d*BIAS;'in nearest and 'double t=dot(e2,q)/det;'in nearest
assert 'best=t;'in nearest and 'best+=BIAS;'in nearest
assert 'nearest(ray.o,ray.d,distance,object,normal,ambiguous);'in main
assert 'double length=ray.length+distance;'in main
assert 'length(point-ray.o)'not in s and 'sqrt(dot(point-ray.o'not in s
assert 'double effective=length+dot(ray.d,reference-point);'in main
assert 'float angle=float(phase-TAU*floor(phase/TAU+0.5));'in s
tree=ast.parse((root/'Blender/benchmarks/capacity_audit/original_SOURCE_first_leg_RN64_graph_HOST_v1.py').read_bytes())
graph=[n.value.value for n in tree.body if isinstance(n,ast.Assign)and isinstance(n.value,ast.Constant)and any(isinstance(t,ast.Name)and t.id=='GRAPH'for t in n.targets)]
assert graph==['sub_xyz; square_xyz; add_xy; add_z; correctly_rounded_sqrt']
assert out['hypothetical_length_graph']==graph[0]
assert out['semantic_equivalence_or_nonequivalence_in_exact_geometry']=='NOT_PROVED_BY_TEXT_AUDIT'
assert out['scope']=='PINNED_SOURCE_TEXT_ONLY_NOT_COMPILED_NATIVE_GRAPH_OR_NUMERICAL_FAILURE'
for k in ['native_IEEE_graph_identity_verified','phase_certified','GPU_used','Bpy_used','RT_used']:assert out[k]is False
for k in ['native_first_leg_error_bound_BU','native_SOURCE_ingress_error_bound_BU','native_phase_error_bound_rad']:assert out[k]is None
assert out['promotion']=='STOP' and out['full_costs']=='UNKNOWN_NOT_ZERO'
assert out['shader_compilations']==out['geometry_evaluations']==out['old_producer_replays']==0
assert len([x for x in d['records']if x['kind']=='NEGATIVE'])==10 and count==13
manifest=json.loads((root/'coordinacion/respuestas/GPU-GUARD-OWNED-TREE-CONTAINMENT-CPU-001-CODEX.json').read_bytes())['pinned_manifest_capture']
b=zlib.decompress(base64.b64decode(manifest['stdout_zlib_base64']));assert sha(b)==manifest['stdout_sha256']
pins=json.loads(b)['pins'];assert len(pins)==461 and all(sha((root/p).read_bytes())==h for p,h in pins.items())
assert pins['Blender/shaders/exp005_shared_frontier.glsl']==r['source_pins']['Blender/shaders/exp005_shared_frontier.glsl']['sha256']
assert 'Blender/benchmarks/capacity_audit/shared_frontier_gpu.py' not in pins
# Runner is separately pinned above, not retroactively added to the frozen 461.
print(json.dumps(dict(status='PASS',pinned_sources=3,exact_line_anchors=13,pin_negative_controls=10,frozen_pins=461,runner_additional_pin_not_in_frozen_manifest=True,compiled_native_GRAPH_certified=False,numerical_failure_proved=False,ideal_nonequivalence_proved=False,GPU_used=False),sort_keys=True))
