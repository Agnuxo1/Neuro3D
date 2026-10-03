"""Pinned retained scene paths -> explicit axial reference/wavelength RN64 phase bound, CPU only."""
from copy import deepcopy
from fractions import Fraction as F
import base64,hashlib,importlib.util,json,math,struct,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
MODEL="precision-axial-scene-reference-phase-CPU-v1"
PARENT="coordinacion/respuestas/PRECISION-AXIAL-SCENE-TRANSPORT-CPU-001-CODEX.json"
PARENT_SHA="42298df01944d403c52ebc47edb9988ca812683ba1c9b387eb2b10894cfe1fcc"
ENCODER="Blender/tests/exp005_blender_gpu.py"
ENCODER_SHA="851f29f9b1fb9b22948f59597d40fa8a55828040673fe0050d24e077b57cf497"
class PhaseStop(ValueError):pass
def require(ok,why):
    if not ok:raise PhaseStop(why)
def sha(b):return hashlib.sha256(b).hexdigest()
def pair(q):return [q.numerator,q.denominator]
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode())
def word(v):return int.from_bytes(struct.pack("<d",v),"little")
def rational(v):
    require(type(v) is list and len(v)==2 and all(type(x) is int for x in v),"typed_rational_pair")
    n,d=v;require(d>0 and abs(n).bit_length()<=2048 and d.bit_length()<=2048,"bounded_rational_storage")
    q=F(n,d);require(abs(q)<=10**6,"explicit_parameter_bound")
    return q
def load_retained():
    raw=(ROOT/PARENT).read_bytes();require(sha(raw)==PARENT_SHA,"sealed_parent_changed")
    parent=json.loads(raw);require(parent["id"]=="PRECISION-AXIAL-SCENE-TRANSPORT-CPU-001","parent_ID")
    require(len(parent["code_doc_sha256"])==30,"complete_parent_pins")
    for p,h in parent["code_doc_sha256"].items():require(sha((ROOT/p).read_bytes())==h,"sealed_dependency_changed")
    run=parent["test_run"];require(run["rc"]==0 and not run["timed_out"],"retained_test_NOT_PASS")
    packed=base64.b64decode(run["stdout_zlib_base64"],validate=True)
    decoder=zlib.decompressobj();raw=decoder.decompress(packed,1024*1024+1)
    require(len(raw)<=1024*1024 and decoder.eof and not decoder.unused_data and not decoder.unconsumed_tail,"bounded_closed_retained_payload")
    require(len(raw)==run["stdout_bytes"] and sha(raw)==run["stdout_sha256"],"retained_payload_integrity")
    v=json.loads(raw);require(v["status"]=="PASS" and v["tests"]==6,"retained_suite_identity")
    return v["data"]
def encoder_module():
    raw=(ROOT/ENCODER).read_bytes();require(sha(raw)==ENCODER_SHA,"encoder_identity")
    spec=importlib.util.spec_from_file_location("frozen_reference_CPU_split",ROOT/ENCODER)
    module=importlib.util.module_from_spec(spec)
    exec(compile(raw,str(ROOT/ENCODER),"exec"),module.__dict__)
    return module

def audit(case,requests,*,model):
    out={"model":MODEL,"status":"STOP","reason":None,"case":case,"request_sha256":None,
       "parent_sha256":PARENT_SHA,"original_scene_sha256":None,"rows":[],"emitted_sources":[],
       "old_geometry_producers_reexecuted":0,"new_parameter_RN32_casts":0,
       "new_parameter_RN64_subtractions":0,"new_parameter_RN64_decode_additions":0,
       "new_parameter_float64_casts":0,"new_endpoint_float64_casts":0,
       "new_path_RN64_additions":0,"new_reference_RN64_subtractions":0,
       "new_residual_RN64_subtractions":0,"new_quotient_RN64_divisions":0,
       "GPU_executed":False,"native_promotion_allowed":False,"physical_scene_authenticated":False,
       "native_hit_coverage_certified":False,"length_reference_phase_bound_certified":False,
       "mirror_material_certified":False,"full_field_certified":False,
       "origin":"RETAINED_EXACT_POINT_CPU_PATHS_NEW_DECLARED_REFERENCE_GAUGE",
       "full_costs":"UNMEASURED_NOT_ZERO"}
    try:
        require(type(model) is str and model==MODEL,"explicit_model_required")
        require(type(case) is str,"typed_case")
        data=load_retained();require(case in data["results"],"unknown_retained_case")
        upstream=data["results"][case];out["original_scene_sha256"]=upstream["original_scene_sha256"]
        require(upstream["status"]=="CPU_EXACT_POINT_TRANSPORT_ONLY","upstream_STOP:"+str(upstream["reason"]))
        requests=deepcopy(requests);paths=upstream["original_geometry"]["emitted_paths"]
        require(type(requests) is list and len(requests)==len(paths),"ALL_SOURCE_explicit_requests")
        staged=[]
        for req,path in zip(requests,paths):
            keys=("original_scene_sha256","source_id","branch_id","reference_plane_x_BU",
                  "reference_normal_x","wavelength_BU","phase_budget_rad","units")
            require(type(req) is dict and set(req)==set(keys),"closed_request")
            require(req["original_scene_sha256"]==upstream["original_scene_sha256"] and
                    req["source_id"]==path["source_id"] and req["branch_id"]==path["branch_id"],"scene_SOURCE_branch_binding")
            require(req["units"]=="BU/rad" and type(req["reference_normal_x"]) is int and
                    req["reference_normal_x"] in (-1,1),"explicit_axial_reference_units")
            ref,lam,cap=(rational(req[k]) for k in ("reference_plane_x_BU","wavelength_BU","phase_budget_rad"))
            require(lam>0 and cap>=0,"positive_wavelength_nonnegative_budget")
            staged.append((req,path,ref,lam,cap))
        out["request_sha256"]=digest({"model":MODEL,"case":case,"parent":PARENT_SHA,"requests":requests})
        encoder=encoder_module();parameter_rows=[]
        for req,path,ref,lam,cap in staged:
            values=[]
            for label,q in (("reference_plane_x_BU",ref),("wavelength_BU",lam)):
                first=float(q);hi,lo=encoder.split_double(first);decoded=float(hi)+float(lo)
                out["new_parameter_float64_casts"]+=1;out["new_parameter_RN32_casts"]+=2
                out["new_parameter_RN64_subtractions"]+=1;out["new_parameter_RN64_decode_additions"]+=1
                values.append({"label":label,"original_rational":pair(q),"first_uint64":word(first),
                  "high_uint32":int.from_bytes(struct.pack("<f",hi),"little"),
                  "low_uint32":int.from_bytes(struct.pack("<f",lo),"little"),"decoded_uint64":word(decoded),
                  "decoded_rational":pair(F(decoded)),"point_error_abs":pair(abs(F(decoded)-q))})
            parameter_rows.append((req,path,ref,lam,cap,values))
        out["rows"]=[{"source_id":req["source_id"],"parameters":vals,"propagation_phase_bound_computed":False}
                     for req,path,ref,lam,cap,vals in parameter_rows]
        require(all(v["point_error_abs"]==[0,1] for row in out["rows"] for v in row["parameters"]),
                "reference_or_wavelength_transport_loss")
        pending=[];any_budget_FAIL=False
        for row,(req,path,ref,lam,cap,vals) in zip(out["rows"],parameter_rows):
            sid=path["source_id"];a,b=(F(*x) for x in path["segments_rational_BU"])
            root_record=next(x for x in upstream["original_geometry"]["root_evidence"]["sources"] if x["source_id"]==sid)
            depart_record=next(x for x in upstream["original_geometry"]["departures"] if x["source_id"]==sid)
            first=next(x["distance_float64_BU"] for x in root_record["hits"] if x["primitive_id"]==path["primitive_ids"][0])
            second=next(x["distance_float64_BU"] for x in depart_record["hits"] if x["primitive_id"]==path["primitive_ids"][1])
            length=first+second;out["new_path_RN64_additions"]+=1
            e_inputs=abs(F(first)-a)+abs(F(second)-b);e_sum=abs(F(length)-F(first)-F(second))
            length_bound=e_inputs+e_sum;exact_length=a+b
            endpoint=F(*path["endpoint_rational_BU"][0]);endpoint_fp=float(endpoint)
            out["new_endpoint_float64_casts"]+=1;require(F(endpoint_fp)==endpoint,"endpoint_cast_loss")
            ref_dec=struct.unpack("<d",vals[0]["decoded_uint64"].to_bytes(8,"little"))[0]
            reference_fp=endpoint_fp-ref_dec;out["new_reference_RN64_subtractions"]+=1
            if req["reference_normal_x"]==-1:reference_fp=-reference_fp # Exact sign reversal, not material phase.
            exact_ref=req["reference_normal_x"]*(endpoint-ref)
            reference_bound=abs(F(reference_fp)-exact_ref)
            residual=length-reference_fp;out["new_residual_RN64_subtractions"]+=1
            subtraction_bound=abs(F(residual)-(F(length)-F(reference_fp)))
            residual_bound=length_bound+reference_bound+subtraction_bound
            lambda_fp=struct.unpack("<d",vals[1]["decoded_uint64"].to_bytes(8,"little"))[0]
            quotient=residual/lambda_fp;out["new_quotient_RN64_divisions"]+=1
            require(math.isfinite(quotient),"finite_quotient_required")
            division_bound=abs(F(quotient)-F(residual)/lam)
            cycle_bound=residual_bound/lam+division_bound
            original_cycles=(exact_length-exact_ref)/lam;observed=abs(F(quotient)-original_cycles)
            require(observed<=cycle_bound,"cycle_error_enclosure")
            # For propagation phase 2*pi*q, pi<4 => |delta_phi| < 8*cycle_bound.
            # No pi/trig/modulo implementation or physical/material phase inference.
            phase_bound=8*cycle_bound;fits=phase_bound<=cap
            row.update({"request":deepcopy(req),"path":deepcopy(path),
              "retained_segment_float64_uint64":[word(first),word(second)],
              "length_float64_uint64":word(length),"reference_float64_uint64":word(reference_fp),
              "residual_float64_uint64":word(residual),"quotient_float64_uint64":word(quotient),
              "length_exact_BU":pair(exact_length),"reference_exact_BU":pair(exact_ref),
              "segment_input_error_bound_BU":pair(e_inputs),"length_sum_RN64_error_bound_BU":pair(e_sum),
              "length_error_bound_BU":pair(length_bound),"reference_error_bound_BU":pair(reference_bound),
              "residual_sub_RN64_error_bound_BU":pair(subtraction_bound),"residual_error_bound_BU":pair(residual_bound),
              "quotient_div_RN64_error_bound_cycles":pair(division_bound),
              "original_cycles":pair(original_cycles),"observed_cycle_error_abs":pair(observed),
              "cycle_error_bound_abs":pair(cycle_bound),"propagation_phase_error_bound_rad":pair(phase_bound),
              "declared_phase_budget_rad":pair(cap),"budget_fits":fits,"propagation_phase_bound_computed":True})
            if not fits:any_budget_FAIL=True
            pending.append({"source_id":sid,"branch_id":req["branch_id"],"request_sha256":out["request_sha256"],
                             "propagation_phase_error_bound_rad":pair(phase_bound)})
        require(not any_budget_FAIL,"declared_phase_budget_exceeded")
        out["emitted_sources"]=pending;out["status"]="CPU_DECLARED_PROPAGATION_PHASE_BOUND_ONLY"
    except (ValueError,TypeError,KeyError,OverflowError,struct.error) as exc:
        out["reason"]=str(exc) if isinstance(exc,PhaseStop) else "closed_INPUT:"+type(exc).__name__
    return out
