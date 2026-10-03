"""CPU64 twofold phase model, opt-in output ABI differs from the frozen single-word baseline."""
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
import base64,hashlib,json,math,struct,zlib
ROOT=Path(__file__).resolve().parents[3]
MODEL="precision-axial-common-detector-twofold-CPU-v1"
REPRESENTATION="PAIR_FLOAT64_CPU_NOT_GPU_ABI"
PARENT="coordinacion/respuestas/PRECISION-AXIAL-COMMON-DETECTOR-SOURCE-MATERIAL-CPU-001-CODEX.json"
PARENT_SHA="1adab489f2452018cdc5374ab0b7c6439e06a0b027d578e7c7c808047df3b94f"
PROP="coordinacion/respuestas/PRECISION-AXIAL-COMMON-DETECTOR-PHASE-CPU-001-CODEX.json"
PROP_SHA="0e529d1d0dd5099fad649773cd4a0b4a3cbb2b0fbc707bd3a917116d52444710"
KEYS={"retained_case","retained_result_sha256","literal_request_sha256","original_scene_sha256","representation","units"}
FLAGS=("GPU_executed","native_promotion_allowed","physical_scene_authenticated","native_hit_coverage_certified",
       "length_reference_phase_bound_certified","mirror_material_certified","full_field_certified",
       "coherent_field_admission_allowed","interference_phase_certified")
class ModelStop(ValueError):pass
def require(ok,why):
    if not ok:raise ModelStop(why)
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode())
def pair(v):return [v.numerator,v.denominator]
def word(x):return int.from_bytes(struct.pack("<d",x),"little")
def floating(w):
    require(type(w) is int and 0<=w<2**64,"typed_float64_word")
    x=struct.unpack("<d",w.to_bytes(8,"little"))[0];require(math.isfinite(x),"finite_retained_word");return x
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
def load_retained():return payload(PARENT,PARENT_SHA,57),payload(PROP,PROP_SHA,50)
def native(out,label,kind,a,b):
    require(all(math.isfinite(x) for x in (a,b)),"finite_RN_inputs")
    value=a+b if kind=="add" else a-b
    out["nodes"].append({"label":label,"op":kind,"a_uint64":word(a),"b_uint64":word(b),
                         "result_uint64":word(value),"finite":math.isfinite(value)})
    require(math.isfinite(value),"finite_RN_result")
    return value
def two_sum(out,label,a,b):
    s=native(out,label+".s","add",a,b)
    bb=native(out,label+".bb","sub",s,a)
    aa=native(out,label+".aa","sub",s,bb)
    da=native(out,label+".da","sub",a,aa)
    db=native(out,label+".db","sub",b,bb)
    e=native(out,label+".e","add",da,db)
    defect=abs(F(s)+F(e)-F(a)-F(b))
    out["two_sum_checks"].append({"label":label,"a_uint64":word(a),"b_uint64":word(b),
        "sum_uint64":word(s),"error_uint64":word(e),"exact_pair_defect_cycles":pair(defect)})
    require(defect==0,"TwoSum_exact_pair_failure")
    return s,e
def audit(request,*,model):
    out={"model":MODEL,"representation":REPRESENTATION,"status":"STOP","reason":None,"request_sha256":None,
         "parent_sha256":PARENT_SHA,"literal_request_sha256":None,"retained_baseline_status":None,
         "retained_baseline_result_sha256":None,"nodes":[],"two_sum_checks":[],"rows":[],"relative":None,"emitted_sources":[],
         "geometry_producers_reexecuted":0,"propagation_producers_reexecuted":0,"baseline_material_producers_reexecuted":0,
         "parameter_encoders_reexecuted":0,"detector_complex_field":None,"detector_power":None,"source_amplitude":None,
         "full_costs":"UNMEASURED_NOT_ZERO","origin":"SEALED_SAME_LITERAL_NEW_TWOFOLD_CPU64"}
    out.update({k:False for k in FLAGS})
    try:
        require(type(model) is str and model==MODEL,"explicit_model_required")
        require(type(request) is dict and set(request)==KEYS and all(type(v) is str for v in request.values()),"closed_typed_selector")
        require(request["representation"]==REPRESENTATION and request["units"]=="cycles/rad","explicit_new_representation")
        old,propdata=load_retained();case=request["retained_case"]
        require(case in old["results"],"retained_case_identity")
        baseline=old["results"][case];literal=old["requests"][case]
        require(request["retained_result_sha256"]==digest(baseline),"retained_result_binding")
        require(request["literal_request_sha256"]==digest(literal),"literal_request_binding")
        require(request["original_scene_sha256"]==literal["original_scene_sha256"],"original_scene_binding")
        out["literal_request_sha256"]=digest(literal);out["retained_baseline_status"]=baseline["status"]
        out["retained_baseline_result_sha256"]=digest(baseline)
        require(baseline["request_sha256"] is not None and len(baseline["parameters"])==3
                and all(p["transport_error_cycles"]==[0,1] for p in baseline["parameters"]),"upstream_INPUT_or_transport_STOP")
        require(len(baseline["rows"])==2 and baseline["relative"] is not None,"retained_baseline_diagnostics_required")
        require(baseline["status"]=="CPU_DECLARED_SOURCE_MATERIAL_PHASE_BOUNDS_ONLY" or baseline["reason"]
                in ("SOURCE_total_phase_budget_exceeded","relative_total_phase_budget_exceeded"),"upstream_material_STOP")
        p=propdata["results"][literal["propagation_case"]]
        require(p["status"]=="CPU_DECLARED_COMMON_PROPAGATION_BOUNDS_ONLY"
                and digest(p)==literal["propagation_result_sha256"],"sealed_propagation_binding")
        require([x["source_id"] for x in p["rows"]]==["S0","S1"],"ALL_SOURCE_order")
        require(literal["declaration"]=="DECLARED_NOT_PHYSICALLY_AUTHENTICATED","declared_not_physical")
        request=deepcopy(request);out["request_sha256"]=digest({"model":MODEL,"parent":PARENT_SHA,"request":request})
        decoded=[floating(x["decoded_uint64"]) for x in baseline["parameters"]]
        gammas=[F(*v["phase_cycles"]) for v in literal["source_phases"]];mu=F(*literal["material_phase"]["phase_cycles"])
        require([F(x) for x in decoded]==gammas+[mu],"sealed_exact_parameter_transport")
        totals=[];mix_errors=[]
        for i,(pr,cap) in enumerate(zip(p["rows"],literal["SOURCE_total_phase_budgets_rad"])):
            sid=pr["source_id"];qfp=floating(pr["quotient_uint64"])
            h,l=two_sum(out,sid+".source",qfp,decoded[i])
            s,e=two_sum(out,sid+".material",h,decoded[2])
            t=native(out,sid+".material_low_mix","add",l,e)
            emix=abs(F(t)-F(l)-F(e))
            hi,lo=two_sum(out,sid+".normalize",s,t)
            represented=F(hi)+F(lo);exact=F(*pr["original_cycles"])+gammas[i]+mu
            bound=F(*pr["cycle_error_bound"])+emix
            require(abs(represented-exact)<=bound,"SOURCE_twofold_error_enclosure")
            row={"source_id":sid,"branch_id":pr["branch_id"],"propagation_uint64":pr["quotient_uint64"],
                "pair_uint64":[word(hi),word(lo)],"represented_cycles":pair(represented),
                "original_declared_cycles":pair(exact),"material_low_mix_error_cycles":pair(emix),
                "total_cycle_error_bound":pair(bound),"total_phase_bound_rad":pair(8*bound),
                "budget_rad":cap,"budget_fits":8*bound<=F(*cap)}
            out["rows"].append(row);totals.append((hi,lo));mix_errors.append(emix)
        s,e=two_sum(out,"relative.high",totals[0][0],-totals[1][0])
        t=native(out,"relative.low_difference","sub",totals[0][1],totals[1][1])
        et=abs(F(t)-F(totals[0][1])+F(totals[1][1]))
        u=native(out,"relative.low_mix","add",e,t);eu=abs(F(u)-F(e)-F(t))
        hi,lo=two_sum(out,"relative.normalize",s,u)
        represented=F(hi)+F(lo);base=F(*p["relative"]["cycle_error_bound"])-F(*p["relative"]["delta_RN_error_cycles"])
        require(base>=0,"retained_relative_decomposition")
        bound=base+sum(mix_errors)+et+eu
        exact=F(*p["relative"]["original_cycles"])+gammas[0]-gammas[1]
        require(abs(represented-exact)<=bound,"relative_twofold_error_enclosure")
        out["relative"]={"source_order":["S0","S1"],"pair_uint64":[word(hi),word(lo)],
            "represented_cycles":pair(represented),"original_declared_cycles":pair(exact),
            "retained_relative_without_old_delta_RN_bound_cycles":pair(base),
            "low_difference_error_cycles":pair(et),"low_mix_error_cycles":pair(eu),
            "total_cycle_error_bound":pair(bound),"total_phase_bound_rad":pair(8*bound),
            "budget_rad":literal["relative_total_phase_budget_rad"],
            "budget_fits":8*bound<=F(*literal["relative_total_phase_budget_rad"])}
        require(all(x["budget_fits"] for x in out["rows"]),"SOURCE_total_phase_budget_exceeded")
        require(out["relative"]["budget_fits"],"relative_total_phase_budget_exceeded")
        out["emitted_sources"]=deepcopy(out["rows"]);out["status"]="CPU_DECLARED_TWOFOLD_PHASE_BOUND_ONLY"
    except (ValueError,TypeError,KeyError,OverflowError,struct.error,OSError) as e:
        out["reason"]=str(e) if isinstance(e,ModelStop) else "closed_INPUT:"+type(e).__name__
    return out
