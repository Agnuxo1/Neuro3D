import ast,base64,hashlib,json,zlib
from fractions import Fraction as F
from pathlib import Path
root=Path.cwd()
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def capture(c):
 b=zlib.decompress(base64.b64decode(c['stdout_zlib_base64'],validate=True))
 assert c['rc']==0 and c.get('timed_out',False)is False and c.get('before_deadline',True)is True
 assert len(b)==c['stdout_bytes'] and sha(b)==c['stdout_sha256']
 d=json.loads(b);assert d['status']=='PASS';return d
p='coordinacion/respuestas/PRECISION-ORIGINAL-SOURCE-POINTWISE-ACCURACY-CONTRACT-HOST-001-CODEX.json'
r=json.loads((root/p).read_bytes())
for p,h in r['code_doc_sha256'].items():
 b=(root/p).read_bytes();assert sha(b)==h
 if p.endswith('.py'):ast.parse(b)
d=capture(r['test_run']);assert d['tests']==4 and len(d['records'])==81
capture(r['prior_test_capture_before_membership_and_input_hardening'])
wpath=root/'coordinacion/respuestas/PRECISION-ORIGINAL-SOURCE-FIRST-LEG-RN64-CAP-WITNESS-CPU-001-CODEX.json'
wb=wpath.read_bytes();assert sha(wb)=='0611221f8b72ba5637f19679af2785fb1674b391653916372a014ee5d9bc70c7'
w=json.loads(wb)
for p,h in w['code_doc_sha256'].items():assert sha((root/p).read_bytes())==h
wd=capture(w['test_run'])
rows={digest(x['result']):x['result']for x in wd['records']if x['kind']=='FIXED_WITNESS_OR_STOP'}
assert len(rows)==28
gb=(root/'coordinacion/respuestas/PRECISION-ORIGINAL-SOURCE-FIRST-LEG-RN64-GRAPH-HOST-001-CODEX.json').read_bytes()
assert sha(gb)=='e25bb94201574e0778023a36d5c7db7bb842727fdffda82890aa314ff8ad2262'
graphs={digest(x['result']):x['result']for x in capture(json.loads(gb)['test_run'])['records']if x['kind']=='FIXED_GRAPH_OR_STOP'}
lb=(root/'coordinacion/respuestas/PRECISION-OBLIQUE-COMMON-DETECTOR-LENGTH-CPU-001-CODEX.json').read_bytes()
assert sha(lb)=='139cb34a315f476fa026bb346086a3a59d7c22241932ca3f4c291a501f4ca47e'
literals=capture(json.loads(lb)['test_run'])['data']['inputs']
def status(lo,hi,b):
 if b is None:return 'STOP_UNALLOCATED_POINTWISE_BUDGET'
 b=F(*b)
 return ('MODEL_BOUND_FITS_EXPLICIT_POINTWISE_BUDGET'if hi<=b else
         'MODEL_ERROR_EXCEEDS_EXPLICIT_POINTWISE_BUDGET'if lo>b else
         'STOP_POINTWISE_BOUND_STRADDLES_BUDGET')
census={};active=set();stops=set()
for x in d['records']:
 if x['kind']=='UPSTREAM_STOP_PRESERVED':
  h=x['evidence_row_sha256'];assert rows[h]['status']=='STOP_UPSTREAM_NO_CAP_WITNESS';stops.add(h);continue
 if x['kind'] not in ('FIXED_EXPLICIT_ALLOCATION','PARTIAL_ALLOCATION_STOP'):continue
 out=x['result'];c=out['contract'];h=out['evidence_row_sha256'];row=rows[h];active.add(h)
 g=graphs[row['captured_graph_row_sha256']]
 lit=literals[row['case']];q=lit['request']
 assert digest(lit['scene'])==c['scene_sha256']==q['original_scene_sha256']
 assert digest(q)==c['query_sha256'] and c['source_id']==row['source_id']
 assert c['evidence_receipt_sha256']==sha(wb) and c['evidence_row_sha256']==h
 assert c['reference_BU']==q['reference_BU'] and c['wavelength_BU']==q['lambda_BU']
 assert c['backend']=='CPU_HYPOTHETICAL_RN64_GRAPH_NOT_NATIVE_BACKEND'
 assert c['observable']=='ABS_ERROR_RN64_FIRST_LEG_VS_EXACT_DECLARED_SOURCE_TO_P_NORM'
 assert c['phase_observable']==row['scope'] and c['units']=='BU'
 assert c['budget_provenance']=='CALLER_EXPLICIT_MODEL_ONLY_NOT_ORIGINAL_SCENE_REQUIREMENT'
 assert digest(c)==out['contract_sha256']
 rn=F(*row['selection']['selected_RN64_length_BU'])
 a,b=map(lambda v:F(*v),g['captured_geometric_first_length_BU'])
 lo,hi=rn-b,rn-a
 assert [lo,hi]==[F(*v)for v in row['signed_first_leg_discrepancy_BU']]
 lower=F(0)if lo<=0<=hi else min(abs(lo),abs(hi));upper=max(abs(lo),abs(hi))
 wave=F(*q['lambda_BU'])
 assert [F(*v)for v in out['absolute_error_BU']]==[lower,upper]
 plo,phi=6*lower/wave,8*upper/wave
 assert [F(*v)for v in out['isolated_phase_error_rad']]==[plo,phi]
 ls=status(lower,upper,c['length_accuracy_budget_BU']);ps=status(plo,phi,c['isolated_phase_accuracy_budget_rad'])
 assert out['length_status']==ls and out['isolated_phase_status']==ps
 both=[ls,ps]
 expected=('STOP_UNALLOCATED_POINTWISE_BUDGET'if any('UNALLOCATED'in v for v in both)else
           'MODEL_ERROR_EXCEEDS_EXPLICIT_POINTWISE_BUDGET'if any('EXCEEDS'in v for v in both)else
           'STOP_POINTWISE_BOUND_STRADDLES_BUDGET'if any('STRADDLES'in v for v in both)else
           'MODEL_BOUND_FITS_EXPLICIT_POINTWISE_BUDGET')
 assert out['status']==expected
 if x['kind']=='FIXED_EXPLICIT_ALLOCATION':
  allocated={'unallocated':(None,None),'tight':([1,2**80],[1,2**80]),'loose':([1,2**50],[1,2**40])}[x['label']]
  assert (c['length_accuracy_budget_BU'],c['isolated_phase_accuracy_budget_rad'])==allocated
  census[expected]=census.get(expected,0)+1
 for k in ['native_precision_certified','native_accuracy_budget_admitted','phase_certified','SOURCE_merged','GPU_used','Bpy_used','RT_used','original_width_cap_used_as_accuracy_budget']:assert out[k]is False
 assert out['promotion']=='STOP' and out['native_admission']=='STOP_MISSING_NATIVE_EVIDENCE'
 assert len(out['native_missing'])==6 and out['full_costs']=='UNKNOWN_NOT_ZERO'
 assert out['native_SOURCE_ingress_error_bound_BU']is None and out['total_path_error_bound_rad']is None
 assert out['new_root_evaluations']==out['old_producer_replays']==0
assert len(active)==8 and len(stops)==20
assert census=={'STOP_UNALLOCATED_POINTWISE_BUDGET':8,'MODEL_ERROR_EXCEEDS_EXPLICIT_POINTWISE_BUDGET':6,'MODEL_BOUND_FITS_EXPLICIT_POINTWISE_BUDGET':10}
neg=[x['id']for x in d['records']if x['kind']=='NEGATIVE']
assert len(neg)==29 and 'caller_resealed_witness'in neg and 'observable'in neg and 'same_scene_different_query'in neg
core=ast.parse((root/'Blender/benchmarks/capacity_audit/original_SOURCE_pointwise_accuracy_contract_HOST_v1.py').read_bytes())
for n in ast.walk(core):
 if isinstance(n,ast.Call):
  name=n.func.id if isinstance(n.func,ast.Name)else n.func.attr if isinstance(n.func,ast.Attribute)else ''
  assert name not in ('sqrt','isqrt','select_root','run','enclose_triangle','subprocess')
 if isinstance(n,ast.ImportFrom):assert not(n.module or '').startswith('Blender')
mp=json.loads((root/'coordinacion/respuestas/GPU-GUARD-OWNED-TREE-CONTAINMENT-CPU-001-CODEX.json').read_bytes())['pinned_manifest_capture']
mb=zlib.decompress(base64.b64decode(mp['stdout_zlib_base64']));assert sha(mb)==mp['stdout_sha256']
pins=json.loads(mb)['pins'];assert len(pins)==461
assert all(sha((root/p).read_bytes())==h for p,h in pins.items())
print(json.dumps(dict(status='PASS',fixed_SOURCE_rows=8,upstream_STOP_rows=20,explicit_allocation_checks=24,partial_unknown_STOP=2,boundary_controls=5,negative_controls=29,copy_isolation=1,census=census,frozen_pins=461,new_roots=0,old_producer_replays=0,native_admitted=False,GPU_used=False),sort_keys=True))
