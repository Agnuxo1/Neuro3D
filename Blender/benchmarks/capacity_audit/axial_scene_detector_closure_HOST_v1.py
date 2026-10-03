"""Sealed axial CPU phase paths -> exact endpoint/gauge closure, HOST metadata only."""
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
import base64,hashlib,json,zlib
ROOT=Path(__file__).resolve().parents[3]
MODEL="precision-axial-scene-detector-closure-HOST-v1"
PARENT="coordinacion/respuestas/PRECISION-AXIAL-SCENE-REFERENCE-PHASE-CPU-001-CODEX.json"
PARENT_SHA="90308f70443f56fd742b19d29dd6be8fc396ea1e3f895048e5575d08005cd0f9"
TRANSPORT="coordinacion/respuestas/PRECISION-AXIAL-SCENE-TRANSPORT-CPU-001-CODEX.json"
TRANSPORT_SHA="42298df01944d403c52ebc47edb9988ca812683ba1c9b387eb2b10894cfe1fcc"
FLAGS=("GPU_executed","native_promotion_allowed","physical_scene_authenticated",
       "native_hit_coverage_certified","length_reference_phase_bound_certified",
       "mirror_material_certified","full_field_certified")
KEYS=("phase_case","phase_result_sha256","original_scene_sha256","source_ids",
      "detector_point_BU","reference_plane_x_BU","reference_normal_x","wavelength_BU","units")
class ClosureStop(ValueError):pass
def require(ok,why):
    if not ok:raise ClosureStop(why)
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode())
def rational(v):
    require(type(v) is list and len(v)==2 and all(type(x) is int for x in v),"typed_rational_pair")
    n,d=v;require(d>0 and abs(n).bit_length()<=2048 and d.bit_length()<=2048,"bounded_rational")
    q=F(n,d);require(abs(q)<=10**6,"explicit_coordinate_parameter_bound")
    return q
def vector(v):
    require(type(v) is list and len(v)==3,"typed_three_coordinate_point")
    return tuple(rational(x) for x in v)
def unpack(run,tests):
    require(run["rc"]==0 and run["timed_out"] is False,"retained_not_PASS")
    packed=base64.b64decode(run["stdout_zlib_base64"],validate=True)
    d=zlib.decompressobj();raw=d.decompress(packed,1024*1024+1)
    require(len(raw)<=1024*1024 and d.eof and not d.unused_data and not d.unconsumed_tail,"closed_bounded_payload")
    require(len(raw)==run["stdout_bytes"] and sha(raw)==run["stdout_sha256"],"retained_payload_integrity")
    v=json.loads(raw);require(v["status"]=="PASS" and v["tests"]==tests,"retained_suite_identity")
    return v["data"]
def load_retained():
    raw=(ROOT/PARENT).read_bytes();require(sha(raw)==PARENT_SHA,"phase_parent_identity")
    r=json.loads(raw);require(r["id"]=="PRECISION-AXIAL-SCENE-REFERENCE-PHASE-CPU-001","phase_parent_ID")
    require(len(r["code_doc_sha256"])==35,"complete_phase_parent_pins")
    for p,h in r["code_doc_sha256"].items():require(sha((ROOT/p).read_bytes())==h,"sealed_dependency_identity")
    raw=(ROOT/TRANSPORT).read_bytes();require(sha(raw)==TRANSPORT_SHA,"transport_parent_identity")
    t=json.loads(raw)
    return unpack(r["test_run"],7),unpack(t["test_run"],6)["results"]
def audit(request,*,model):
    out={"model":MODEL,"status":"STOP","reason":None,"request_sha256":None,
      "parent_sha256":PARENT_SHA,"closure_rows":[],"endpoint_bundle":[],
      "old_geometry_producers_reexecuted":0,"phase_producer_reexecuted":0,"new_native_arithmetic":0,
      "full_costs":"UNMEASURED_NOT_ZERO","origin":"SEALED_CPU_PATHS_HOST_ENDPOINT_GATE",
      "source_complex_field":None,"detector_complex_field":None,"detector_power":None,
      "source_material_phase":None,"source_amplitude":None,"SOURCE_phase_error":None,
      "interference_phase_error":None,"complete_path_coverage_authenticated":False,
      "detector_measurement_authenticated":False,"coherent_field_admission_allowed":False}
    out.update({k:False for k in FLAGS})
    try:
        require(type(model) is str and model==MODEL,"explicit_model_required")
        require(type(request) is dict and set(request)==set(KEYS),"closed_request")
        require(all(type(request[k]) is str and 1<=len(request[k])<=128
                    for k in ("phase_case","phase_result_sha256","original_scene_sha256","units")),"typed_identifiers")
        require(all(len(request[k])==64 and all(c in "0123456789abcdef" for c in request[k])
                    for k in ("phase_result_sha256","original_scene_sha256")),"canonical_SHA_required")
        ids=request["source_ids"]
        require(type(ids) is list and 1<=len(ids)<=5 and all(type(x) is str and 1<=len(x)<=64 for x in ids)
                    and len(set(ids))==len(ids),"typed_unique_complete_SOURCE_ids")
        point=vector(request["detector_point_BU"]);ref=rational(request["reference_plane_x_BU"])
        lam=rational(request["wavelength_BU"])
        require(lam>0 and type(request["reference_normal_x"]) is int
                  and request["reference_normal_x"] in (-1,1) and request["units"]=="BU/rad","explicit_common_gauge_units")
        request=deepcopy(request);data,transport=load_retained();name=request["phase_case"]
        require(name in data["results"],"unknown_phase_case");phase=data["results"][name]
        require(digest(phase)==request["phase_result_sha256"],"phase_result_binding")
        require(phase["original_scene_sha256"]==request["original_scene_sha256"],"original_scene_binding")
        out["request_sha256"]=digest({"model":MODEL,"parent":PARENT_SHA,"request":request})
        require(phase["status"]=="CPU_DECLARED_PROPAGATION_PHASE_BOUND_ONLY","upstream_phase_STOP:"+str(phase["reason"]))
        require(all(phase[k] is False for k in FLAGS),"upstream_native_flags_NOT_permission")
        up=transport[data["cases"][name]]
        require(up["original_scene_sha256"]==phase["original_scene_sha256"],"transport_scene_binding")
        paths=up["original_geometry"]["emitted_paths"];rows=phase["rows"];reqs=data["requests"][name]
        actual=[p["source_id"] for p in paths]
        require(ids==actual and len(rows)==len(reqs)==len(paths),"ALL_SOURCE_order_and_coverage")
        staged=[]
        for path,row,q in zip(paths,rows,reqs):
            require(row["source_id"]==path["source_id"]==q["source_id"]
                    and row["request"]==q and row["path"]==path
                    and q["branch_id"]==path["branch_id"],"SOURCE_branch_path_binding")
            require(row["propagation_phase_bound_computed"] is True and row["budget_fits"] is True,"each_SOURCE_phase_budget")
            require(q["original_scene_sha256"]==request["original_scene_sha256"]
                    and q["units"]==request["units"]
                    and q["reference_normal_x"]==request["reference_normal_x"]
                    and rational(q["reference_plane_x_BU"])==ref and rational(q["wavelength_BU"])==lam,"common_reference_wavelength_required")
            endpoint=vector(path["endpoint_rational_BU"])
            staged.append({"source_id":path["source_id"],"branch_id":path["branch_id"],
              "endpoint_rational_BU":deepcopy(path["endpoint_rational_BU"]),
              "phase_bound_rad":deepcopy(row["propagation_phase_error_bound_rad"]),
              "matches_declared_detector":endpoint==point})
        out["closure_rows"]=staged
        endpoints=[vector(x["endpoint_rational_BU"]) for x in staged]
        require(all(x==endpoints[0] for x in endpoints),"noncoincident_SOURCE_endpoints")
        require(all(x["matches_declared_detector"] is True for x in staged),"declared_detector_not_endpoint")
        out["endpoint_bundle"]=deepcopy(staged);out["status"]="HOST_RATIONAL_ENDPOINT_CLOSED_ONLY"
        # Deliberately no amplitudes, material phases, summation, field or physics certification.
    except (ValueError,TypeError,KeyError,OverflowError) as exc:
        out["reason"]=str(exc) if isinstance(exc,ClosureStop) else "closed_INPUT:"+type(exc).__name__
    return out
