"""Declared initial-source + shared mirror phase on sealed common paths; CPU bounds only."""
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
import base64,hashlib,importlib.util,json,math,struct,zlib
ROOT=Path(__file__).resolve().parents[3]
MODEL="precision-axial-common-detector-source-material-CPU-v1"
PARENT="coordinacion/respuestas/PRECISION-AXIAL-COMMON-DETECTOR-PHASE-CPU-001-CODEX.json"
PARENT_SHA="0e529d1d0dd5099fad649773cd4a0b4a3cbb2b0fbc707bd3a917116d52444710"
FIXTURE="coordinacion/respuestas/PRECISION-AXIAL-COMMON-DETECTOR-FIXTURE-CPU-001-CODEX.json"
FIXTURE_SHA="c110b2d9b3d14fea59470833bfb38e6dc075e319c72260182ca4d29043de42cc"
ENCODER="Blender/tests/exp005_blender_gpu.py"
ENCODER_SHA="851f29f9b1fb9b22948f59597d40fa8a55828040673fe0050d24e077b57cf497"
DECLARATION="DECLARED_NOT_PHYSICALLY_AUTHENTICATED"
PROFILE="DECLARED_SHARED_AXIAL_MIRROR_PHASE_CYCLES"
KEYS={"propagation_case","propagation_result_sha256","original_scene_sha256","prepared_sha256",
      "detector_point_BU","source_phases","material_phase","SOURCE_total_phase_budgets_rad",
      "relative_total_phase_budget_rad","units","declaration"}
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
def floating(w):
    require(type(w) is int and 0<=w<2**64,"typed_float64_word")
    x=struct.unpack("<d",w.to_bytes(8,"little"))[0];require(math.isfinite(x),"finite_retained_word");return x
def rational(v):
    require(type(v) is list and len(v)==2 and all(type(x) is int for x in v),"typed_rational_pair")
    n,d=v;require(d>0 and abs(n).bit_length()<=2048 and d.bit_length()<=2048,"bounded_rational_storage")
    q=F(n,d);require(abs(q)<=10**6,"explicit_parameter_bound");return q
def payload(path,expected,pins):
    raw=(ROOT/path).read_bytes();require(sha(raw)==expected,"sealed_parent_identity")
    r=json.loads(raw);require(len(r["code_doc_sha256"])==pins,"complete_parent_pins")
    for p,h in r["code_doc_sha256"].items():require(sha((ROOT/p).read_bytes())==h,"sealed_dependency_identity")
    run=r["test_run"];require(run["rc"]==0 and run["timed_out"] is False,"retained_not_PASS")
    d=zlib.decompressobj();raw=d.decompress(base64.b64decode(run["stdout_zlib_base64"],validate=True),1024*1024+1)
    require(len(raw)<=1024*1024 and d.eof and not d.unused_data and not d.unconsumed_tail,"closed_bounded_payload")
    require(len(raw)==run["stdout_bytes"] and sha(raw)==run["stdout_sha256"],"payload_integrity")
    v=json.loads(raw);require(v["status"]=="PASS" and v["tests"]==7,"retained_suite_identity")
    return v["data"]
def load_retained():return payload(PARENT,PARENT_SHA,50),payload(FIXTURE,FIXTURE_SHA,45)["prepared"]
def encoder():
    raw=(ROOT/ENCODER).read_bytes();require(sha(raw)==ENCODER_SHA,"encoder_identity")
    spec=importlib.util.spec_from_file_location("sealed_source_material_split",ROOT/ENCODER)
    m=importlib.util.module_from_spec(spec);exec(compile(raw,str(ROOT/ENCODER),"exec"),m.__dict__);return m
def audit(request,*,model):
    out={"model":MODEL,"status":"STOP","reason":None,"request_sha256":None,"parent_sha256":PARENT_SHA,
         "parameters":[],"rows":[],"relative":None,"emitted_sources":[],
         "new_RN32_casts":0,"new_RN64_transport_subtractions":0,"new_CPU_decode_additions":0,"new_first_FP64_casts":0,
         "new_source_phase_RN64_additions":0,"new_material_phase_RN64_additions":0,"new_relative_RN64_subtractions":0,
         "geometry_producers_reexecuted":0,"propagation_producers_reexecuted":0,
         "detector_complex_field":None,"detector_power":None,"source_amplitude":None,
         "full_costs":"UNMEASURED_NOT_ZERO","origin":"SEALED_PATHS_DECLARED_SOURCE_SHARED_MIRROR_CPU64"}
    out.update({k:False for k in FLAGS})
    try:
        require(type(model) is str and model==MODEL,"explicit_model_required")
        require(type(request) is dict and set(request)==KEYS,"closed_request")
        require(request["units"]=="cycles/rad" and request["declaration"]==DECLARATION,"explicit_declared_units")
        sources=request["source_phases"];material=request["material_phase"]
        require(type(sources) is list and len(sources)==2,"ALL_SOURCE_required")
        for i,s in enumerate(sources):
            require(type(s) is dict and set(s)=={"source_id","branch_id","phase_cycles"},"closed_SOURCE_phase")
            require(type(s["source_id"]) is str and s["source_id"]==f"S{i}"
                    and type(s["branch_id"]) is str and s["branch_id"]==f"S{i}/mirror","SOURCE_path_order_binding")
        gammas=[rational(s["phase_cycles"]) for s in sources]
        require(type(material) is dict and set(material)=={"object_id","primitive_id","profile","phase_cycles"},"closed_material_phase")
        require(type(material["object_id"]) is str and type(material["primitive_id"]) is int
                and material["profile"]==PROFILE,"explicit_material_profile")
        mu=rational(material["phase_cycles"])
        caps=request["SOURCE_total_phase_budgets_rad"]
        require(type(caps) is list and len(caps)==2,"explicit_each_SOURCE_budget")
        caps=[rational(v) for v in caps];relative_cap=rational(request["relative_total_phase_budget_rad"])
        require(all(v>=0 for v in caps+[relative_cap]),"nonnegative_explicit_budgets")
        data,prepared=load_retained();case=request["propagation_case"]
        require(type(case) is str and case in data["results"],"retained_case_identity")
        prop=data["results"][case];pq=data["requests"][case]
        require(prop["status"]=="CPU_DECLARED_COMMON_PROPAGATION_BOUNDS_ONLY","upstream_propagation_STOP")
        require(type(request["propagation_result_sha256"]) is str
                and request["propagation_result_sha256"]==digest(prop),"propagation_result_binding")
        require(type(request["original_scene_sha256"]) is str and request["original_scene_sha256"]
                ==pq["original_scene_sha256"]==prepared["transport"]["original_scene_sha256"],"original_scene_binding")
        require(type(request["prepared_sha256"]) is str and request["prepared_sha256"]==pq["prepared_sha256"]
                ==digest(prepared),"prepared_binding")
        point=request["detector_point_BU"]
        require(type(point) is list and len(point)==3,"typed_3D_point")
        point=tuple(rational(v) for v in point)
        require(point==tuple(rational(v) for v in pq["detector_point_BU"]),"common_detector_binding")
        t=prepared["transport"];paths=t["original_geometry"]["emitted_paths"]
        require(len(paths)==len(prop["emitted_sources"])==2,"ALL_retained_SOURCE_paths")
        for path,s,row in zip(paths,sources,prop["emitted_sources"]):
            require(path["source_id"]==s["source_id"]==row["source_id"]
                    and path["branch_id"]==s["branch_id"]==row["branch_id"],"retained_SOURCE_branch")
            require(path["primitive_ids"]==[material["primitive_id"],0]
                    and tuple(rational(v) for v in path["endpoint_rational_BU"])==point,"shared_material_path_binding")
        triangles=t["decoded_scene"]["triangles"]
        matches=[v for v in triangles if v["primitive_id"]==material["primitive_id"]]
        require(len(matches)==1 and matches[0]["object_id"]==material["object_id"],"material_object_primitive_binding")
        # Parent guarantees ORIGINAL == decoded on this exact-point fixture; no geometric producer is called.
        request=deepcopy(request);out["request_sha256"]=digest({"model":MODEL,"parent":PARENT_SHA,"request":request})
        out["propagation_request_sha256"]=prop["request_sha256"]
        m=encoder();decoded=[]
        for label,q in (( "S0.initial_phase_cycles",gammas[0]),("S1.initial_phase_cycles",gammas[1]),("shared_mirror.phase_cycles",mu)):
            first=float(q);h,l=m.split_double(first);fp=float(h)+float(l)
            out["new_first_FP64_casts"]+=1;out["new_RN32_casts"]+=2
            out["new_RN64_transport_subtractions"]+=1;out["new_CPU_decode_additions"]+=1
            out["parameters"].append({"label":label,"original_cycles":pair(q),"first_uint64":word(first),
                "high_uint32":int.from_bytes(struct.pack("<f",h),"little"),
                "low_uint32":int.from_bytes(struct.pack("<f",l),"little"),"decoded_uint64":word(fp),
                "transport_error_cycles":pair(abs(F(fp)-q))})
            decoded.append(fp)
        require(all(v["transport_error_cycles"]==[0,1] for v in out["parameters"]),"phase_parameter_transport_loss")
        totals=[];corrections=[]
        for i,(p,gamma,cap) in enumerate(zip(prop["rows"],gammas,caps)):
            qfp=floating(p["quotient_uint64"]);original=F(*p["original_cycles"])
            sg=qfp+decoded[i];out["new_source_phase_RN64_additions"]+=1
            e1=abs(F(sg)-F(qfp)-F(decoded[i]))
            total=sg+decoded[2];out["new_material_phase_RN64_additions"]+=1
            require(math.isfinite(total),"finite_total_phase")
            e2=abs(F(total)-F(sg)-F(decoded[2]))
            eg=F(*out["parameters"][i]["transport_error_cycles"]);em=F(*out["parameters"][2]["transport_error_cycles"])
            b=F(*p["cycle_error_bound"])+eg+em+e1+e2;exact=original+gamma+mu
            require(abs(F(total)-exact)<=b,"SOURCE_total_error_enclosure")
            out["rows"].append({"source_id":p["source_id"],"branch_id":p["branch_id"],
                "propagation_uint64":p["quotient_uint64"],"source_sum_uint64":word(sg),"total_uint64":word(total),
                "source_add_RN_error_cycles":pair(e1),"material_add_RN_error_cycles":pair(e2),
                "declared_total_original_cycles":pair(exact),"total_cycle_error_bound":pair(b),
                "total_phase_bound_rad":pair(8*b),"budget_rad":pair(cap),"budget_fits":8*b<=cap})
            totals.append(total);corrections.append((eg,e1,e2))
        delta=totals[0]-totals[1];out["new_relative_RN64_subtractions"]+=1
        require(math.isfinite(delta),"finite_relative_phase")
        edelta=abs(F(delta)-F(totals[0])+F(totals[1]))
        pr=prop["relative"];base=F(*pr["cycle_error_bound"])-F(*pr["delta_RN_error_cycles"])
        require(base>=0,"retained_relative_decomposition")
        # Replaced parent delta subtraction is NOT rerun or charged twice. SAME decoded mirror phase cancels.
        rb=base+sum(eg+e1+e2 for eg,e1,e2 in corrections)+edelta
        exact_delta=F(*pr["original_cycles"])+gammas[0]-gammas[1]
        require(abs(F(delta)-exact_delta)<=rb,"relative_total_error_enclosure")
        out["relative"]={"source_order":["S0","S1"],"declared_original_cycles":pair(exact_delta),
            "delta_uint64":word(delta),"delta_RN_error_cycles":pair(edelta),
            "retained_relative_without_old_delta_RN_bound_cycles":pair(base),
            "shared_material_phase_cancels_exactly":True,"total_cycle_error_bound":pair(rb),
            "total_phase_bound_rad":pair(8*rb),"budget_rad":pair(relative_cap),"budget_fits":8*rb<=relative_cap}
        require(all(v["budget_fits"] for v in out["rows"]),"SOURCE_total_phase_budget_exceeded")
        require(out["relative"]["budget_fits"],"relative_total_phase_budget_exceeded")
        out["emitted_sources"]=deepcopy(out["rows"]);out["status"]="CPU_DECLARED_SOURCE_MATERIAL_PHASE_BOUNDS_ONLY"
    except (ValueError,TypeError,KeyError,OverflowError,struct.error,OSError) as e:
        out["reason"]=str(e) if isinstance(e,PhaseStop) else "closed_INPUT:"+type(e).__name__
    return out
