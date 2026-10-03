"""New two-SOURCE axial fixture, real reduced CPU queries, not a physical optical model."""
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[3]
MODEL="precision-axial-common-detector-fixture-CPU-v1"
PARENT="coordinacion/respuestas/PRECISION-AXIAL-SCENE-DETECTOR-CLOSURE-HOST-001-CODEX.json"
PARENT_SHA="8420b8382d0b9398fdc4fc9f897bfe3c085d37e6ac6651ea0e0bc435f01546d2"
FLAGS=("GPU_executed","native_promotion_allowed","physical_scene_authenticated","native_hit_coverage_certified",
       "length_reference_phase_bound_certified","mirror_material_certified","full_field_certified","coherent_field_admission_allowed")
class FixtureStop(ValueError):pass
def require(ok,why):
    if not ok:raise FixtureStop(why)
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode())
def pair(x):
    x=F(x);return [x.numerator,x.denominator]
def vector(x,y,z):return [pair(x),pair(y),pair(z)]
def fixture():
    return {"schema":"precision-axial-scene-candidates-CPU-v1","units":"BU",
      "triangles":[{"primitive_id":i,"object_id":"common_detector_fixture_surface",
        "vertices_BU":[vector(x,0,0),vector(x,1,0),vector(x,0,1)]} for i,x in enumerate((0,1))],
      "sources":[{"id":"S"+str(i),"position_BU":vector(x,F(1,4),F(1,4)),"direction":vector(1,0,0)}
                 for i,x in enumerate((F(1,4),F(3,4)))]}
def state():
    out={"model":MODEL,"status":"STOP","reason":None,"scene":None,"requests":None,"transport":None,
      "new_scene_geometry_passes":0,"old_fixtures_replayed":0,"phase_arithmetic_executed":0,
      "endpoint_bundle":[],"detector_complex_field":None,"detector_power":None,"source_amplitude":None,
      "source_material_phase":None,"full_costs":"UNMEASURED_NOT_ZERO"}
    out.update({k:False for k in FLAGS});return out
def prepare(*,model):
    out=state()
    try:
        require(type(model) is str and model==MODEL,"explicit_model_required")
        raw=(ROOT/PARENT).read_bytes();require(sha(raw)==PARENT_SHA,"sealed_parent_identity")
        pins=json.loads(raw)["code_doc_sha256"];require(len(pins)==40,"complete_parent_pins")
        for path,h in pins.items():require(sha((ROOT/path).read_bytes())==h,"sealed_dependency_identity")
        # Pure owned modules; only this NEW scene, never earlier test suites/fixtures/writers.
        import axial_scene_transport_exact_CPU_v1 as transport
        s=fixture();h=digest(s)
        requests=[{"scene_sha256":h,"source_id":v["id"],"departure_event":"mirror"} for v in s["sources"]]
        out["scene"],out["requests"]=deepcopy(s),deepcopy(requests)
        t=transport.audit(s,requests,model=transport.MODEL);out["transport"]=t
        out["new_scene_geometry_passes"]=1+int(t["decoded_geometry"] is not None)
        require(t["status"]=="CPU_EXACT_POINT_TRANSPORT_ONLY","new_fixture_transport_STOP:"+str(t["reason"]))
        paths=t["original_geometry"]["emitted_paths"]
        require([v["source_id"] for v in paths]==["S0","S1"],"complete_original_SOURCE")
        require(all(v["primitive_ids"]==[1,0] for v in paths),"same_declared_mirror_detector_paths")
        require([v["length_rational_BU"] for v in paths]==[[7,4],[5,4]],"original_lengths")
        require(all(v["endpoint_rational_BU"]==vector(0,F(1,4),F(1,4)) for v in paths),"common_original_endpoint")
        out["status"]="CPU_NEW_SCENE_COMMON_ENDPOINT_TRANSPORT_ONLY"
    except (ValueError,KeyError,TypeError,OverflowError) as e:
        out["reason"]=str(e) if isinstance(e,FixtureStop) else "closed_INPUT:"+type(e).__name__
    return out
def check_detector(prepared,request,*,model):
    out={"model":MODEL,"status":"STOP","reason":None,"request_sha256":None,"endpoint_bundle":[],
      "old_fixtures_replayed":0,"new_geometry_passes":0,"phase_arithmetic_executed":0,
      "detector_complex_field":None,"detector_power":None,"source_amplitude":None,
      "source_material_phase":None,"full_costs":"UNMEASURED_NOT_ZERO"}
    out.update({k:False for k in FLAGS})
    try:
        require(type(model) is str and model==MODEL,"explicit_model_required")
        require(type(request) is dict and set(request)=={"prepared_sha256","original_scene_sha256","source_ids","detector_point_BU","units"},"closed_detector_request")
        require(type(request["prepared_sha256"]) is str and digest(prepared)==request["prepared_sha256"],"prepared_binding")
        require(prepared["status"]=="CPU_NEW_SCENE_COMMON_ENDPOINT_TRANSPORT_ONLY","prepared_STOP")
        require(all(prepared[k] is False for k in FLAGS),"NO_native_permission")
        s=fixture();require(prepared["scene"]==s and digest(s)==request["original_scene_sha256"],"new_literal_scene_binding")
        require(type(request["source_ids"]) is list and request["source_ids"]==["S0","S1"]
                and all(type(x) is str for x in request["source_ids"]) and request["units"]=="BU","ALL_SOURCE_units")
        point=request["detector_point_BU"]
        require(type(point) is list and len(point)==3,"typed_3Dpoint")
        for v in point:
            require(type(v) is list and len(v)==2 and all(type(x) is int for x in v)
              and v[1]>0 and abs(v[0]).bit_length()<=2048 and v[1].bit_length()<=2048
              and abs(F(*v))<=10**6,"bounded_exact_rational")
        out["request_sha256"]=digest({"model":MODEL,"request":request})
        paths=prepared["transport"]["original_geometry"]["emitted_paths"]
        require(len(paths)==2 and [p["source_id"] for p in paths]==request["source_ids"],"ALL_paths")
        require(all(tuple(F(*v) for v in p["endpoint_rational_BU"])==tuple(F(*v) for v in point)
                    for p in paths),"detector_not_all_original_endpoints")
        out["endpoint_bundle"]=deepcopy(paths);out["status"]="CPU_EXACT_COMMON_ENDPOINT_METADATA_ONLY"
    except (ValueError,KeyError,TypeError,OverflowError) as e:
        out["reason"]=str(e) if isinstance(e,FixtureStop) else "closed_INPUT:"+type(e).__name__
    return out
