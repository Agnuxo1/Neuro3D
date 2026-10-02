"""Independent retained exact-root scene verifier. No producer imports, tracing or spawn."""
import base64,hashlib,json,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sha=lambda b:hashlib.sha256(b).hexdigest()
r=json.loads((ROOT/"coordinacion/respuestas/PRECISION-AXIAL-SCENE-CANDIDATES-CPU-001-CODEX.json").read_bytes())
for p,h in r["code_doc_sha256"].items():assert sha((ROOT/p).read_bytes())==h,p
t=r["test_run"];assert t["rc"]==0 and not t["timed_out"] and t["threads"]==t["affinity_mask"]==1
assert t["hard_child_timeout_seconds"]==60 and t["elapsed_seconds"]<60
raw=zlib.decompress(base64.b64decode(t["stdout_zlib_base64"],validate=True))
assert len(raw)==t["stdout_bytes"] and sha(raw)==t["stdout_sha256"]
v=json.loads(raw);assert v["status"]=="PASS" and v["tests"]==6
scenes=v["data"]["scenes"];rows=v["data"]["results"];assert len(rows)==16 and set(rows)==set(scenes)
flags=("GPU_executed","native_promotion_allowed","physical_scene_authenticated",
       "native_hit_coverage_certified","length_reference_phase_bound_certified","full_field_certified")
for name,row in rows.items():
 assert all(row[k] is False for k in flags)
 assert row["origin"]=="EXACT_RATIONAL_REDUCED_CPU_SCENE_NOT_BPY_GPU"
 assert row["full_costs"]=="UNMEASURED_NOT_ZERO"
 if row["scene_sha256"] is not None:
  body=json.dumps(scenes[name],sort_keys=True,separators=(",",":"),allow_nan=False).encode()
  assert sha(body)==row["scene_sha256"]
  for source in row["sources"]:
   # Fresh tests are x planes, +x unit sources, interior y=z=1/4; scalar oracle independent of producer.
   declared=next(s for s in scenes[name]["sources"] if s["id"]==source["source_id"])
   assert declared["direction"]==[[1,1],[0,1],[0,1]]
   assert declared["position_BU"][1:]==[[1,4],[1,4]]
   assert [x["primitive_id"] for x in source["visited"]]==list(range(len(scenes[name]["triangles"])))
   origin=F(*declared["position_BU"][0])
   for hit in source["hits"]:
    tri=scenes[name]["triangles"][hit["primitive_id"]]
    x=F(*tri["vertices_BU"][0][0])
    assert all(F(*vertex[0])==x for vertex in tri["vertices_BU"])
    assert [vertex[1:] for vertex in tri["vertices_BU"]]==[[[0,1],[0,1]],[[1,1],[0,1]],[[0,1],[1,1]]]
    assert F(*hit["distance_rational_BU"])==x-origin>0
    assert hit["normal_canonical"]==[1.,0.,0.]
 if row["status"]=="STOP":assert row["branch_queries"]==0 and row["branch_results"]==[]
 else:
  assert row["branch_queries"]==len(row["sources"])
  for branch in row["branch_results"]:
   assert branch["state"]=="HIT_PENDING_DEPARTURE" and branch["previous"] is None
   assert branch["snapshot_sha256"]==row["scene_sha256"]
   assert branch["native_promotion_allowed"] is False and branch["full_field_certified"] is False
valid=rows["two_sources"];assert valid["branch_queries"]==2
assert valid["sources"][0]["hits"][0]["distance_rational_BU"]==[1,1]
assert valid["sources"][1]["hits"][0]["distance_rational_BU"]==[1,2]
bad=rows["cast_collision"];assert bad["reason"]=="float64_minimum_set_changed"
assert bad["sources"][0]["exact_minimum_ids"]==[0] and bad["sources"][0]["float64_minimum_ids"]==[0,1]
assert rows["thin_positive"]["sources"][0]["hits"][0]["distance_rational_BU"]==[1,2**56]
assert rows["thin_ambiguous"]["reason"]=="root_tie_policy:ambiguous_object_or_normal"
assert rows["second_SOURCE_collapse"]["root_queries_computed"]==2
assert rows["tieband_rounding"]["reason"]=="float64_tie_band_changed"
assert rows["tieband_rounding"]["sources"][0]["exact_band_ids"]==[0,1]
assert rows["tieband_rounding"]["sources"][0]["float64_band_ids"]==[0]
for key,reason in (("zero_contact","source_zero_contact_no_departure"),("root_miss","root_miss_NOT_certified"),
                   ("cast_underflow","float64_positive_finite_required")):assert rows[key]["reason"]==reason
print(json.dumps({"status":"PASS","pins":len(r["code_doc_sha256"]),"fresh_scenes":len(rows),
 "cast_collision_STOP":True,"atomic_SOURCE_gate":True,"GPU_executed":False,
 "scope":"represented rational axial ROOT CPU scenes only"},sort_keys=True))
