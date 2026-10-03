"""Independent reduced axial intersection and exact IEEE checks; no producer imports."""
import base64,hashlib,json,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sha=lambda b:hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode())
r=json.loads((ROOT/"coordinacion/respuestas/PRECISION-AXIAL-COMMON-DETECTOR-FIXTURE-CPU-001-CODEX.json").read_bytes())
for path,h in r["code_doc_sha256"].items():assert sha((ROOT/path).read_bytes())==h,path
assert len(r["code_doc_sha256"])==45 and r["retained_initial_failure"] is None
run=r["test_run"]
assert run["rc"]==0 and run["timed_out"] is False and run["elapsed_seconds"]<60
assert run["threads"]==run["affinity_mask"]==1 and run["hard_child_timeout_seconds"]==60
d=zlib.decompressobj();raw=d.decompress(base64.b64decode(run["stdout_zlib_base64"],validate=True),1024*1024+1)
assert len(raw)<=1024*1024 and d.eof and not d.unused_data and not d.unconsumed_tail
assert len(raw)==run["stdout_bytes"] and sha(raw)==run["stdout_sha256"]
v=json.loads(raw);assert v["status"]=="PASS" and v["tests"]==7
data=v["data"];p=data["prepared"];s=p["scene"];t=p["transport"]
assert p["status"]=="CPU_NEW_SCENE_COMMON_ENDPOINT_TRANSPORT_ONLY"
assert s["schema"]=="precision-axial-scene-candidates-CPU-v1" and s["units"]=="BU"
assert t["original_scene_sha256"]==t["decoded_scene_sha256"]==digest(s)
assert digest(s)=="0ce056e0d2684d1d7a3fcc70130e0f3ed1c8a14be2fa09bdaf045b78378068e2"
vec=lambda v:tuple(F(*q) for q in v)
assert [vec(x["position_BU"]) for x in s["sources"]]==[(F(1,4),F(1,4),F(1,4)),(F(3,4),F(1,4),F(1,4))]
assert [x["id"] for x in s["sources"]]==["S0","S1"]
assert all(vec(x["direction"])==(1,0,0) for x in s["sources"])
for i,tri in enumerate(s["triangles"]):
    assert tri["primitive_id"]==i and tri["object_id"]=="common_detector_fixture_surface"
    assert [vec(x) for x in tri["vertices_BU"]]==[(i,0,0),(i,1,0),(i,0,1)]
assert [x["source_id"] for x in p["requests"]]==["S0","S1"]
assert all(x["departure_event"]=="mirror" and x["scene_sha256"]==digest(s) for x in p["requests"])
geometry_SOURCE_checks=0
for g in (t["original_geometry"],t["decoded_geometry"]):
    assert g["status"]=="CPU_AXIAL_ONE_MIRROR_GEOMETRY_ONLY" and g["origin_bias_BU"]==[0,1] and g["branch_queries"]==0
    assert len(g["emitted_paths"])==len(g["departures"])==len(g["root_evidence"]["sources"])==2
    for source,root,depart,path in zip(s["sources"],g["root_evidence"]["sources"],g["departures"],g["emitted_paths"]):
        geometry_SOURCE_checks+=1
        x,y,z=vec(source["position_BU"]);assert y>=0 and z>=0 and y+z<=1
        # Plane0 is behind +x; plane1 is the sole positive ROOT. Its triangle contains (1,y,z).
        hits={h["primitive_id"]:F(*h["distance_rational_BU"]) for h in root["hits"]}
        assert hits=={1:1-x} and root["root_tie_policy"]["selected_primitive"]==1
        assert depart["previous_primitive_id"]==1 and depart["excluded_zero_ids"]==[1]
        assert vec(depart["origin_rational_BU"])==(1,y,z) and vec(depart["direction_rational"])==(-1,0,0)
        # From (1,y,z) along -x, previous plane1 has proven zero; plane0 is exactly distance1.
        assert {h["primitive_id"]:F(*h["distance_rational_BU"]) for h in depart["hits"]}=={0:F(1)}
        assert depart["tie_policy"]["selected_primitive"]==0
        assert path["source_id"]==source["id"] and path["branch_id"]==source["id"]+"/mirror"
        assert path["primitive_ids"]==[1,0]
        assert [F(*q) for q in path["segments_rational_BU"]]==[1-x,F(1)]
        assert F(*path["length_rational_BU"])==2-x and vec(path["endpoint_rational_BU"])==(0,y,z)
assert [F(*v["length_rational_BU"]) for v in t["original_geometry"]["emitted_paths"]]==[F(7,4),F(5,4)]
def ieee(w,width):
    assert type(w) is int and 0<=w<2**width
    mb,eb,bias=(52,11,1023) if width==64 else (23,8,127)
    e=(w>>mb)&(2**eb-1);m=w%(2**mb);assert e<2**eb-1
    return (-1 if w>>(width-1) else 1)*F(m if e==0 else m+2**mb)*F(2)**((1 if e==0 else e)-bias-mb)
assert len(t["scalars"])==30 and t["new_RN32_casts"]==60
assert t["new_RN64_subtractions"]==t["new_CPU_RN64_decode_additions"]==30
for row in t["scalars"]:
    q=F(*row["original_rational"]);literal=s
    for node in row["path"]:literal=literal[node]
    assert F(*literal)==q
    assert ieee(row["first_float64_uint64"],64)==q==ieee(row["high_uint32"],32)
    assert ieee(row["low_uint32"],32)==0 and ieee(row["decoded_uint64"],64)==q
    assert F(*row["first_rational"])==F(*row["decoded_rational"])==q
    assert row["hilo_le_hex"]==(row["high_uint32"].to_bytes(4,"little")+row["low_uint32"].to_bytes(4,"little")).hex()
    assert all(row[k]==[0,1] for k in ("first_cast_error_abs","hilo_encoding_error_abs","CPU_decode_add_error_abs","total_point_bound_abs","observed_point_error_abs"))
flags=("GPU_executed","native_promotion_allowed","physical_scene_authenticated","native_hit_coverage_certified",
       "length_reference_phase_bound_certified","mirror_material_certified","full_field_certified","coherent_field_admission_allowed")
assert all(p[k] is False for k in flags)
assert p["new_scene_geometry_passes"]==2 and p["old_fixtures_replayed"]==p["phase_arithmetic_executed"]==0
assert t["decoded_scene"]==s
requests,results=(data[k] for k in ("requests","results"));assert set(requests)==set(results) and len(results)==14
accepted=stopped=0
for name,out in results.items():
    q=requests[name];assert all(out[k] is False for k in flags)
    assert all(out[k] is None for k in ("detector_complex_field","detector_power","source_amplitude","source_material_phase"))
    assert out["full_costs"]=="UNMEASURED_NOT_ZERO" and out["new_geometry_passes"]==out["old_fixtures_replayed"]==out["phase_arithmetic_executed"]==0
    if out["request_sha256"] is not None:assert out["request_sha256"]==digest({"model":out["model"],"request":q})
    if out["status"]=="STOP":stopped+=1;assert out["endpoint_bundle"]==[]
    else:
        accepted+=1;assert out["status"]=="CPU_EXACT_COMMON_ENDPOINT_METADATA_ONLY"
        assert q["prepared_sha256"]==digest(p) and q["original_scene_sha256"]==digest(s)
        assert q["source_ids"]==["S0","S1"] and vec(q["detector_point_BU"])==(0,F(1,4),F(1,4))
        assert out["endpoint_bundle"]==t["original_geometry"]["emitted_paths"]
assert (accepted,stopped)==(2,12)
for axis in range(3):
    for sign in (-1,1):
        name="delta_"+str(axis)+"_"+str(sign)
        target=vec(requests[name]["detector_point_BU"]);actual=(F(0),F(1,4),F(1,4))
        assert target[axis]-actual[axis]==sign*F(1,2**56)
        assert results[name]["reason"]=="detector_not_all_original_endpoints"
assert results["forged_cache"]["reason"]==results["bad_prepared"]["reason"]=="prepared_binding"
assert results["bad_scene"]["reason"]=="new_literal_scene_binding"
assert results["subset"]["reason"]==results["order"]["reason"]=="ALL_SOURCE_units"
assert data["prepare_STOP_controls"]==[{"reason":"explicit_model_required","geometry_passes":0},{"reason":"sealed_parent_identity","geometry_passes":0}]
print(json.dumps({"status":"PASS","pins":45,"fresh_scenes":1,"geometry_passes":2,"geometry_SOURCE_checks":geometry_SOURCE_checks,
 "scalar_exact_IEEE_checks":30,"detector_requests":14,"metadata_only":2,"STOP":12,"detector_signed_axis_rejections":6,
 "old_fixtures_replayed":0,"GPU_executed":False,"coherent_field_admission":False},sort_keys=True))
