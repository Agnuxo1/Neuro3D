"""Independent exact endpoint/gauge/cost scope checks, no producer imports or replay."""
import base64,hashlib,json,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
RECEIPT="coordinacion/respuestas/PRECISION-AXIAL-SCENE-DETECTOR-CLOSURE-HOST-001-CODEX.json"
sha=lambda b:hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode())
def unpack(run):
    assert run["rc"]==0 and run["timed_out"] is False
    assert run["threads"]==run["affinity_mask"]==1 and run["hard_child_timeout_seconds"]==60
    assert 0<=run["elapsed_seconds"]<60
    d=zlib.decompressobj();raw=d.decompress(base64.b64decode(run["stdout_zlib_base64"],validate=True),1024*1024+1)
    assert len(raw)<=1024*1024 and d.eof and not d.unused_data and not d.unconsumed_tail
    assert len(raw)==run["stdout_bytes"] and sha(raw)==run["stdout_sha256"]
    v=json.loads(raw);assert v["status"]=="PASS";return v
r=json.loads((ROOT/RECEIPT).read_bytes());assert r["id"]=="PRECISION-AXIAL-SCENE-DETECTOR-CLOSURE-HOST-001"
for p,h in r["code_doc_sha256"].items():assert sha((ROOT/p).read_bytes())==h,p
assert len(r["code_doc_sha256"])>=40
new=unpack(r["test_run"]);assert new["tests"]==7
raw=(ROOT/"coordinacion/respuestas/PRECISION-AXIAL-SCENE-REFERENCE-PHASE-CPU-001-CODEX.json").read_bytes()
assert sha(raw)=="90308f70443f56fd742b19d29dd6be8fc396ea1e3f895048e5575d08005cd0f9"
phase=unpack(json.loads(raw)["test_run"])["data"]
raw=(ROOT/"coordinacion/respuestas/PRECISION-AXIAL-SCENE-TRANSPORT-CPU-001-CODEX.json").read_bytes()
assert sha(raw)=="42298df01944d403c52ebc47edb9988ca812683ba1c9b387eb2b10894cfe1fcc"
transport=unpack(json.loads(raw)["test_run"])["data"]["results"]
def point(p):assert len(p)==3;return tuple(F(*v) for v in p)
nulls=("source_complex_field","detector_complex_field","detector_power","source_material_phase",
       "source_amplitude","SOURCE_phase_error","interference_phase_error")
flags=("GPU_executed","native_promotion_allowed","physical_scene_authenticated","native_hit_coverage_certified",
       "length_reference_phase_bound_certified","mirror_material_certified","full_field_certified",
       "complete_path_coverage_authenticated","detector_measurement_authenticated","coherent_field_admission_allowed")
requests,results=(new["data"][k] for k in ("requests","results"));assert set(requests)==set(results) and len(results)==29
assert new["data"]["synthetic_negative_controls"]==[]
accepted=stopped=endpointchecks=0
for name,out in results.items():
    q=requests[name]
    assert all(out[k] is False for k in flags) and all(out[k] is None for k in nulls)
    assert out["full_costs"]=="UNMEASURED_NOT_ZERO" and out["origin"]=="SEALED_CPU_PATHS_HOST_ENDPOINT_GATE"
    assert out["old_geometry_producers_reexecuted"]==out["phase_producer_reexecuted"]==out["new_native_arithmetic"]==0
    if out["request_sha256"] is not None:
        assert digest({"model":out["model"],"parent":out["parent_sha256"],"request":q})==out["request_sha256"]
    if out["closure_rows"]:
        p=phase["results"][q["phase_case"]];up=transport[phase["cases"][q["phase_case"]]]
        assert digest(p)==q["phase_result_sha256"] and p["status"]=="CPU_DECLARED_PROPAGATION_PHASE_BOUND_ONLY"
        paths=up["original_geometry"]["emitted_paths"]
        assert q["source_ids"]==[v["source_id"] for v in paths]
        assert len(out["closure_rows"])==len(paths)==len(p["rows"])
        for row,path,p_row,p_req in zip(out["closure_rows"],paths,p["rows"],phase["requests"][q["phase_case"]]):
            endpointchecks+=1
            assert row["source_id"]==path["source_id"]==p_row["source_id"]==p_req["source_id"]
            assert row["branch_id"]==path["branch_id"]==p_req["branch_id"]
            assert p_row["path"]==path and p_row["request"]==p_req
            assert row["endpoint_rational_BU"]==path["endpoint_rational_BU"]
            assert row["phase_bound_rad"]==p_row["propagation_phase_error_bound_rad"]
            assert row["matches_declared_detector"] is (point(path["endpoint_rational_BU"])==point(q["detector_point_BU"]))
            assert F(*q["wavelength_BU"])==F(*p_req["wavelength_BU"])
            assert F(*q["reference_plane_x_BU"])==F(*p_req["reference_plane_x_BU"])
            assert q["reference_normal_x"]==p_req["reference_normal_x"] and q["units"]==p_req["units"]
    if out["status"]=="STOP":
        stopped+=1;assert out["endpoint_bundle"]==[] and out["reason"]
    else:
        accepted+=1;assert out["status"]=="HOST_RATIONAL_ENDPOINT_CLOSED_ONLY" and out["reason"] is None
        assert out["endpoint_bundle"]==out["closure_rows"] and all(v["matches_declared_detector"] for v in out["closure_rows"])
assert (accepted,stopped,endpointchecks)==(6,23,13)
for name in ("detector_x0","detector_x1"):
    out=results[name];assert out["reason"]=="noncoincident_SOURCE_endpoints"
    assert [point(v["endpoint_rational_BU"]) for v in out["closure_rows"]]==[(F(0),F(1,4),F(1,4)),(F(1),F(1,4),F(1,4))]
for axis in range(3):
    name="detector_delta_axis"+str(axis);q=requests[name]
    anchor=(F(0),F(1,4),F(1,4))
    assert point(q["detector_point_BU"])[axis]-anchor[axis]==F(1,2**56)
    assert results[name]["reason"]=="declared_detector_not_endpoint"
assert results["subset"]["reason"]==results["reorder"]["reason"]=="ALL_SOURCE_order_and_coverage"
assert results["duplicate"]["reason"]=="typed_unique_complete_SOURCE_ids"
assert results["bool_SOURCE"]["reason"]=="typed_unique_complete_SOURCE_ids"
for name in ("bad_plane","bad_lambda","bad_normal"):assert results[name]["reason"]=="common_reference_wavelength_required"
assert results["bad_scene"]["reason"]=="original_scene_binding"
assert results["bad_result"]["reason"]=="phase_result_binding"
assert results["parent_changed"]["reason"]=="phase_parent_identity"
assert results["upstream_division_budget"]["reason"]=="upstream_phase_STOP:declared_phase_budget_exceeded"
assert results["noncanonical_same_point"]["request_sha256"]!=results["canonical_same_point"]["request_sha256"]
assert results["noncanonical_same_point"]["endpoint_bundle"]==results["canonical_same_point"]["endpoint_bundle"]
assert r["retained_initial_failure"] is None
print(json.dumps({"status":"PASS","pins":len(r["code_doc_sha256"]),"new_requests":29,"metadata_closure_only":6,
 "expected_STOP":23,"endpoint_SOURCE_checks":13,"two_SOURCE_different_endpoints_STOP":2,
 "detector_2_pow_minus56_axis_rejections":3,"old_producers_reexecuted":0,
 "native_arithmetic":0,"coherent_field_admission":False},sort_keys=True))
