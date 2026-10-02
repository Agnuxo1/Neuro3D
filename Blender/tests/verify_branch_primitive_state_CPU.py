"""Independent retained branch-state verifier: no producer imports/spawn/old suite replay."""
import base64,hashlib,json,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sha=lambda b:hashlib.sha256(b).hexdigest()
r=json.loads((ROOT/"coordinacion/respuestas/PRECISION-BRANCH-PRIMITIVE-STATE-CPU-001-CODEX.json").read_bytes())
for p,h in r["code_doc_sha256"].items():assert sha((ROOT/p).read_bytes())==h,p
t=r["test_run"]
assert t["rc"]==0 and not t["timed_out"] and t["threads"]==t["affinity_mask"]==1
assert t["hard_child_timeout_seconds"]==60 and t["elapsed_seconds"]<60
raw=zlib.decompress(base64.b64decode(t["stdout_zlib_base64"],validate=True))
assert len(raw)==t["stdout_bytes"] and sha(raw)==t["stdout_sha256"]
v=json.loads(raw);assert v["status"]=="PASS" and v["tests"]==7
d=v["data"];assert d["origin"]=="NEW_SYNTHETIC_CPU_DECLARATIONS"
cases=d["cases"];assert len(cases)==7
flags=("GPU_executed","native_promotion_allowed","scene_geometry_authenticated","complete_hit_coverage",
 "length_reference_phase_bound_certified","full_field_certified","fork_energy_or_material_certified")
views=[]
def visit(x):
 if type(x) is dict:
  if x.get("model")=="precision-branch-primitive-state-CPU-v1":views.append(x)
  for y in x.values():visit(y)
 elif type(x) is list:
  for y in x:visit(y)
visit(cases)
assert len(views)==24
for x in views:
 assert x["origin"]=="SYNTHETIC_DECLARED_CANDIDATES_CPU_ONLY"
 assert all(x[k] is False for k in flags)
 assert x["snapshot_sha256"]=="a"*64 and x["depth"]<=64
iso=cases["isolation"]
assert iso["parent"]["state"]=="FORKED"
assert iso["left"]["previous"]["primitive_id"]==1 and iso["left"]["state"]=="HIT_PENDING_DEPARTURE"
assert iso["right"]["previous"]["primitive_id"]==0 and iso["right"]["state"]=="STOP"
assert iso["other_SOURCE"]["source_id"]=="SOURCE_B" and iso["other_SOURCE"]["previous"] is None
gap=cases["thin_gap_return"]
assert gap["retry"]==gap["result"] and gap["result"]["state"]=="STOP"
assert gap["result"]["last_policy"]["selected_primitive"]==1
assert gap["result"]["last_policy"]["tie_primitive_ids"]==[0,1]
tiny=cases["tiny_candidate"]
assert tiny["other_face"]["state"]==tiny["source"]["state"]=="HIT_PENDING_DEPARTURE"
assert tiny["source"]["pending"]["distance_BU"]==2**-56
assert tiny["ambiguous"]["reason"]=="tie_policy:ambiguous_object_or_normal"
assert len(cases["binding"])==4 and all(x["state"]=="STOP" for x in cases["binding"])
assert len(cases["invalid_departures"]["atomic"])==4
assert all(x["state"]=="STOP" for x in cases["invalid_departures"]["atomic"])
assert cases["invalid_departures"]["pending_gate"]["reason"]=="pending_hit_requires_departure"
copies=cases["defensive_copy"]
assert copies["child"]["previous"]["primitive_id"]==0 and copies["consumed"]["state"]=="FORKED"
limits=cases["limits"];assert limits["miss"]["state"]==limits["bad"]["state"]=="STOP"
assert limits["at_depth64"]["reason"]=="state_depth_bound_NOT_optical_truncation"
assert len(limits["lineage"])==64
for i,x in enumerate(limits["lineage"]):
 assert x["depth"]==i+1 and x["previous"]["primitive_id"]==i%2
 assert x["previous"]["departure_event"]=="mirror"
print(json.dumps({"status":"PASS","pins":len(r["code_doc_sha256"]),"retained_views":len(views),
 "SOURCE_branch_isolation":True,"GPU_executed":False,"native_promotion_allowed":False,
 "scope":"synthetic CPU candidate/state policy only"},sort_keys=True))
