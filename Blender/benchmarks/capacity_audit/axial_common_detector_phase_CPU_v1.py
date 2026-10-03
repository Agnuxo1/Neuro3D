"""Retained common endpoint -> explicit CPU64 propagation and relative bounds, not field optics."""
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
import base64,hashlib,importlib.util,json,math,struct,zlib
ROOT=Path(__file__).resolve().parents[3]
MODEL="precision-axial-common-detector-phase-CPU-v1"
PARENT="coordinacion/respuestas/PRECISION-AXIAL-COMMON-DETECTOR-FIXTURE-CPU-001-CODEX.json"
PARENT_SHA="c110b2d9b3d14fea59470833bfb38e6dc075e319c72260182ca4d29043de42cc"
ENCODER="Blender/tests/exp005_blender_gpu.py"
ENCODER_SHA="851f29f9b1fb9b22948f59597d40fa8a55828040673fe0050d24e077b57cf497"
KEYS=("original_scene_sha256","prepared_sha256","detector_point_BU","source_ids","reference_plane_x_BU",
      "reference_normal_x","wavelength_BU","SOURCE_phase_budgets_rad","relative_propagation_budget_rad","units")
FLAGS=("GPU_executed","native_promotion_allowed","physical_scene_authenticated","native_hit_coverage_certified",
       "length_reference_phase_bound_certified","mirror_material_certified","full_field_certified",
       "coherent_field_admission_allowed","interference_phase_certified")
class PhaseStop(ValueError):pass
def require(ok,why):
    if not ok:raise PhaseStop(why)
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode())
def pair(q):return [q.numerator,q.denominator]
def word(x):return int.from_bytes(struct.pack("<d",x),"little")
def rational(v):
    require(type(v) is list and len(v)==2 and all(type(x) is int for x in v),"typed_rational_pair")
    n,d=v;require(d>0 and abs(n).bit_length()<=2048 and d.bit_length()<=2048,"bounded_rational_storage")
    q=F(n,d);require(abs(q)<=10**6,"explicit_parameter_bound");return q
def vector(v):
    require(type(v) is list and len(v)==3,"typed_3D_point")
    return tuple(rational(x) for x in v)
def load_retained():
    raw=(ROOT/PARENT).read_bytes();require(sha(raw)==PARENT_SHA,"sealed_parent_identity")
    r=json.loads(raw);require(r["id"]=="PRECISION-AXIAL-COMMON-DETECTOR-FIXTURE-CPU-001","parent_ID")
    require(len(r["code_doc_sha256"])==45,"complete_parent_pins")
    for p,h in r["code_doc_sha256"].items():require(sha((ROOT/p).read_bytes())==h,"sealed_dependency_identity")
    run=r["test_run"];require(run["rc"]==0 and run["timed_out"] is False,"retained_not_PASS")
    d=zlib.decompressobj();raw=d.decompress(base64.b64decode(run["stdout_zlib_base64"],validate=True),1024*1024+1)
    require(len(raw)<=1024*1024 and d.eof and not d.unused_data and not d.unconsumed_tail,"closed_bounded_payload")
    require(len(raw)==run["stdout_bytes"] and sha(raw)==run["stdout_sha256"],"payload_integrity")
    v=json.loads(raw);require(v["status"]=="PASS" and v["tests"]==7,"retained_suite_identity")
    return v["data"]["prepared"]
def encoder():
    raw=(ROOT/ENCODER).read_bytes();require(sha(raw)==ENCODER_SHA,"encoder_identity")
    spec=importlib.util.spec_from_file_location("sealed_common_phase_split",ROOT/ENCODER)
    module=importlib.util.module_from_spec(spec);exec(compile(raw,str(ROOT/ENCODER),"exec"),module.__dict__)
    return module
def audit(request,*,model):
    out={"model":MODEL,"status":"STOP","reason":None,"request_sha256":None,"parent_sha256":PARENT_SHA,
      "parameters":[],"shared_reference":None,"rows":[],"relative":None,"emitted_sources":[],
      "geometry_producers_reexecuted":0,"old_phase_producers_reexecuted":0,
      "parameter_RN32_casts":0,"parameter_RN64_subtractions":0,"parameter_CPU_decode_additions":0,
      "new_path_RN64_additions":0,"new_shared_reference_RN64_subtractions":0,
      "new_residual_RN64_subtractions":0,"new_quotient_RN64_divisions":0,"new_relative_RN64_subtractions":0,
      "detector_complex_field":None,"detector_power":None,"source_amplitude":None,"source_material_phase":None,
      "full_costs":"UNMEASURED_NOT_ZERO","origin":"SEALED_COMMON_ENDPOINT_DECLARED_PROPAGATION_CPU64"}
    out.update({k:False for k in FLAGS})
    try:
        require(type(model) is str and model==MODEL,"explicit_model_required")
        require(type(request) is dict and set(request)==set(KEYS),"closed_request")
        require(type(request["source_ids"]) is list and request["source_ids"]==["S0","S1"]
                    and all(type(x) is str for x in request["source_ids"]),"ALL_SOURCE_order")
        point=vector(request["detector_point_BU"]);ref=rational(request["reference_plane_x_BU"])
        lam=rational(request["wavelength_BU"])
        require(type(request["reference_normal_x"]) is int and request["reference_normal_x"] in (-1,1)
                and request["units"]=="BU/rad" and lam>0,"explicit_common_gauge_units")
        caps=request["SOURCE_phase_budgets_rad"]
        require(type(caps) is list and len(caps)==2,"explicit_each_SOURCE_budget")
        caps=[rational(v) for v in caps];relative_cap=rational(request["relative_propagation_budget_rad"])
        require(all(x>=0 for x in caps+[relative_cap]),"nonnegative_explicit_budgets")
        prepared=load_retained()
        require(prepared["status"]=="CPU_NEW_SCENE_COMMON_ENDPOINT_TRANSPORT_ONLY","upstream_STOP")
        require(type(request["prepared_sha256"]) is str and request["prepared_sha256"]==digest(prepared),"prepared_binding")
        t=prepared["transport"]
        require(type(request["original_scene_sha256"]) is str and request["original_scene_sha256"]==t["original_scene_sha256"],"original_scene_binding")
        paths=t["original_geometry"]["emitted_paths"]
        require(len(paths)==2 and [p["source_id"] for p in paths]==request["source_ids"],"complete_retained_paths")
        require(all(vector(p["endpoint_rational_BU"])==point for p in paths),"common_detector_original_endpoints")
        request=deepcopy(request);out["request_sha256"]=digest({"model":MODEL,"parent":PARENT_SHA,"request":request})
        module=encoder();decoded=[]
        for label,q in (("reference_plane_x_BU",ref),("wavelength_BU",lam)):
            first=float(q);h,l=module.split_double(first);fp=float(h)+float(l)
            out["parameter_RN32_casts"]+=2;out["parameter_RN64_subtractions"]+=1;out["parameter_CPU_decode_additions"]+=1
            out["parameters"].append({"label":label,"original_rational":pair(q),"first_uint64":word(first),
              "high_uint32":int.from_bytes(struct.pack("<f",h),"little"),"low_uint32":int.from_bytes(struct.pack("<f",l),"little"),
              "decoded_uint64":word(fp),"point_error_abs":pair(abs(F(fp)-q))})
            decoded.append(fp)
        require(all(v["point_error_abs"]==[0,1] for v in out["parameters"]),"parameter_transport_loss")
        endpoint=float(point[0]);require(F(endpoint)==point[0],"endpoint_cast_loss")
        rfp=endpoint-decoded[0];out["new_shared_reference_RN64_subtractions"]+=1
        if request["reference_normal_x"]==-1:rfp=-rfp
        rexact=request["reference_normal_x"]*(point[0]-ref);er=abs(F(rfp)-rexact)
        out["shared_reference"]={"exact_BU":pair(rexact),"float64_uint64":word(rfp),"error_abs_BU":pair(er)}
        qvalues=[];lengths=[]
        for path,cap in zip(paths,caps):
            sid=path["source_id"];a,b=(F(*x) for x in path["segments_rational_BU"])
            root=next(x for x in t["original_geometry"]["root_evidence"]["sources"] if x["source_id"]==sid)
            dep=next(x for x in t["original_geometry"]["departures"] if x["source_id"]==sid)
            fa=next(x["distance_float64_BU"] for x in root["hits"] if x["primitive_id"]==path["primitive_ids"][0])
            fb=next(x["distance_float64_BU"] for x in dep["hits"] if x["primitive_id"]==path["primitive_ids"][1])
            length=fa+fb;out["new_path_RN64_additions"]+=1
            el=abs(F(fa)-a)+abs(F(fb)-b)+abs(F(length)-F(fa)-F(fb))
            residual=length-rfp;out["new_residual_RN64_subtractions"]+=1
            es=abs(F(residual)-F(length)+F(rfp))
            quotient=residual/decoded[1];out["new_quotient_RN64_divisions"]+=1
            require(math.isfinite(quotient),"finite_quotient")
            ed=abs(F(quotient)-F(residual)/lam);cycles=(a+b-rexact)/lam
            bound=(el+er+es)/lam+ed;require(abs(F(quotient)-cycles)<=bound,"SOURCE_error_enclosure")
            row={"source_id":sid,"branch_id":path["branch_id"],"segments_retained_uint64":[word(fa),word(fb)],
                 "length_exact_BU":pair(a+b),"length_uint64":word(length),"length_error_BU":pair(el),
                 "residual_uint64":word(residual),"residual_RN_error_BU":pair(es),"quotient_uint64":word(quotient),
                 "division_RN_error_cycles":pair(ed),"original_cycles":pair(cycles),"cycle_error_bound":pair(bound),
                 "propagation_phase_bound_rad":pair(8*bound),"budget_rad":pair(cap),"budget_fits":8*bound<=cap}
            out["rows"].append(row);qvalues.append(quotient);lengths.append(a+b)
        delta=qvalues[0]-qvalues[1];out["new_relative_RN64_subtractions"]+=1
        require(math.isfinite(delta),"finite_relative")
        e_delta=abs(F(delta)-F(qvalues[0])+F(qvalues[1]))
        # SAME represented reference used twice; it cancels in residual difference, NOT in individual budgets.
        relative_bound=sum((F(*v["length_error_BU"])+F(*v["residual_RN_error_BU"]))/lam
                           +F(*v["division_RN_error_cycles"]) for v in out["rows"])+e_delta
        original_delta=(lengths[0]-lengths[1])/lam
        require(abs(F(delta)-original_delta)<=relative_bound,"relative_error_enclosure")
        out["relative"]={"source_order":["S0","S1"],"original_cycles":pair(original_delta),"delta_uint64":word(delta),
          "shared_reference_cancels_exactly":True,"delta_RN_error_cycles":pair(e_delta),
          "cycle_error_bound":pair(relative_bound),"propagation_phase_bound_rad":pair(8*relative_bound),
          "budget_rad":pair(relative_cap),"budget_fits":8*relative_bound<=relative_cap}
        require(all(v["budget_fits"] for v in out["rows"]),"SOURCE_phase_budget_exceeded")
        require(out["relative"]["budget_fits"],"relative_propagation_budget_exceeded")
        out["emitted_sources"]=deepcopy(out["rows"]);out["status"]="CPU_DECLARED_COMMON_PROPAGATION_BOUNDS_ONLY"
    except (ValueError,TypeError,KeyError,OverflowError,struct.error) as e:
        out["reason"]=str(e) if isinstance(e,PhaseStop) else "closed_INPUT:"+type(e).__name__
    return out
