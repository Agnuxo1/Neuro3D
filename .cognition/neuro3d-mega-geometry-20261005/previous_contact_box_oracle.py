import ast,base64,hashlib,itertools,json,struct,zlib
from fractions import Fraction as F
from pathlib import Path
root=Path.cwd()
receipt=json.loads((root/'coordinacion/respuestas/PRECISION-ORIGINAL-SOURCE-PREVIOUS-CONTACT-BOX-CPU-001-CODEX.json').read_bytes())
def sha(b):return hashlib.sha256(b).hexdigest()
def capture(c):
 b=zlib.decompress(base64.b64decode(c['stdout_zlib_base64'],validate=True));assert c['rc']==0 and c['before_deadline'] and len(b)==c['stdout_bytes'] and sha(b)==c['stdout_sha256'];return json.loads(b)
body=capture(receipt['test_run']);assert body['status']=='PASS' and body['tests']==4 and len(body['records'])==35
for p,s in receipt['test_run']['sources'].items():
 b=(root/p).read_bytes();assert sha(b)==s['sha256'] and len(b)==s['bytes'];ast.parse(b)
 assert zlib.decompress(base64.b64decode(s['zlib_base64']))==b
for name in ['initial_PASS_before_provenance_scope_and_codec_pin','second_PASS_before_transitive_codec_pin']:
 old=receipt[name];assert capture(old)['status']=='PASS'
 for p,s in old['sources'].items():
  b=zlib.decompress(base64.b64decode(s['zlib_base64']));assert len(b)==s['bytes'] and sha(b)==s['sha256']
raw=(root/receipt['dependency']['path']).read_bytes();assert sha(raw)==receipt['dependency']['sha256']
parent=json.loads(raw);prior=capture(parent['final_capture']);packets={(p['packet']['slot']['case'],p['packet']['slot']['source_id']):p['packet'] for p in prior['records'] if 'packet' in p}
def decode(w):
 e=(w>>23)&255;m=w&0x7fffff;s=w>>31;assert e!=255
 q=F(((1<<23)+m) if e else m);power=e-150 if e else -149
 q=q*2**power if power>=0 else q/F(2**(-power));return -q if s else q
def det(a,b,c):return a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0])
def corners(box):return list(itertools.product(*[[F(*lo),F(*hi)] for lo,hi in box]))
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
false=['native_point_budget_authenticated','native_direction_budget_authenticated','native_precision_certified','launch_exclusion_allowed','nearest_hit_certified','GPU_launch_allowed','phase_certified']
counts={};original=0;corner_combinations=0;bindings=set()
for row in body['records']:
 if 'result' not in row:continue
 out=row['result'];assert all(out[k] is False for k in false)
 assert out['phase_error_bound'] is None and out['full_costs']=='UNKNOWN_NOT_ZERO' and not out['ignored_primitive_ids'] and out['origin_offset_applied'] is False
 if row['kind']=='CALLER_RESEALED_NOT_FIXED_PARENT':
  assert out['parent_receipt_sha256'] is None and out['scope']=='CALLER_CONDITIONAL_CPU_CONTENT_ONLY' and out['slot']['scene_sha256']=='0'*64;continue
 if row['kind']=='ORIGINAL_CAPTURE':
  original+=1;packet=packets[row['case'],row['source_id']];s=packet['slot']
  assert out['slot']==s and out['point_box']==s['saved_point_bounds'] and out['direction_box']==s['saved_direction_bounds'] and out['CPU_packet_binding_sha256']==packet['CPU_packet_binding_sha256']
  assert s['saved_direction_bounds'][0][0]!=s['saved_direction_bounds'][0][1];tri=s['saved_triangle_words'];bindings.add(out['CPU_packet_binding_sha256'])
 else:tri=row['triangle'];assert out['point_box']==row['point'] and out['direction_box']==row['direction']
 a,b,c=[tuple(decode(w) for w in v) for v in tri];e1,e2=sub(b,a),sub(c,a)
 n=(e1[1]*e2[2]-e1[2]*e2[1],e1[2]*e2[0]-e1[0]*e2[2],e1[0]*e2[1]-e1[1]*e2[0])
 if not any(n):assert out['status']=='STOP_DEGENERATE_PLANE';counts[out['status']]=counts.get(out['status'],0)+1;continue
 ps,ds=corners(out['point_box']),corners(out['direction_box'])
 residuals=[det(e1,e2,sub(p,a)) for p in ps];denominators=[det(e1,e2,d) for d in ds]
 residual=(min(residuals),max(residuals));den=(min(denominators),max(denominators))
 assert tuple(F(*q) for q in out['plane_residual_interval'])==residual and tuple(F(*q) for q in out['denominator_interval'])==den
 if den[0]<=0<=den[1]:assert out['status']=='STOP_DIRECTION_PLANE_DENOMINATOR_ZERO_POSSIBLE' and out['plane_parameter_interval'] is None
 elif residual!=(F(0),F(0)):assert out['status']=='STOP_POINT_BOX_NOT_IDENTICALLY_ON_PREVIOUS_PLANE' and out['barycentric_intervals'] is None
 else:
  gram=det(e1,e2,n);assert gram>0
  bary=[]
  for p in ps:
   rhs=sub(p,a);u=det(rhs,e2,n)/gram;v=det(e1,rhs,n)/gram;bary.append((u,v,1-u-v))
  bounds=[(min(z[i] for z in bary),max(z[i] for z in bary)) for i in range(3)]
  assert bounds==[tuple(F(*q) for q in interval) for interval in out['barycentric_intervals']]
  strict=all(lo>0 for lo,hi in bounds)
  assert strict==out['CPU_strict_interior_contact_for_all_directions']
  assert out['status']==('CPU_STRICT_PREVIOUS_CONTACT_ALL_DECLARED_DIRECTIONS_ONLY' if strict else 'STOP_PREVIOUS_TRIANGLE_NOT_STRICT_INTERIOR')
  assert out['plane_parameter_interval']==[[0,1],[0,1]]
  if row['kind']=='ORIGINAL_CAPTURE':
   for p,d in itertools.product(ps,ds):
    assert det(e1,e2,sub(p,a))==0 and det(e1,e2,d)!=0;corner_combinations+=1
 counts[out['status']]=counts.get(out['status'],0)+1
assert original==12 and len(bindings)==12 and corner_combinations==768
assert sum(x['kind']=='MALFORMED_NEGATIVE' for x in body['records'])==9 and sum(x['kind']=='SELECTOR_NEGATIVE' for x in body['records'])==3
old=json.loads((root/'coordinacion/respuestas/GPU-GUARD-OWNED-TREE-CONTAINMENT-CPU-001-CODEX.json').read_bytes())
cap=old['pinned_manifest_capture'];b=zlib.decompress(base64.b64decode(cap['stdout_zlib_base64']));assert sha(b)==cap['stdout_sha256'];pins=json.loads(b)['pins']
assert len(pins)==461 and all(sha((root/p).read_bytes())==h for p,h in pins.items())
print(json.dumps(dict(status='PASS',original_SOURCE_bindings=12,original_corner_combinations_not_unique_samples=768,condition_rows_checked=21,condition_classifications=counts,malformed_NEG=9,selector_NEG=3,caller_resealed_no_parent=True,source_snapshots_verified=6,frozen_pins_unchanged=461,old_contact_evaluator_or_suite_replays=0,native_exclusion_or_phase_admitted=False),sort_keys=True))

