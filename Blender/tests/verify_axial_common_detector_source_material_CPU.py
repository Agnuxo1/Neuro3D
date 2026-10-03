"""Independent stdlib-only verification of retained source/material IEEE words and exact bounds."""
import base64,hashlib,json,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
ID="PRECISION-AXIAL-COMMON-DETECTOR-SOURCE-MATERIAL-CPU-001"
PARENT="coordinacion/respuestas/PRECISION-AXIAL-COMMON-DETECTOR-PHASE-CPU-001-CODEX.json"
PSHA="0e529d1d0dd5099fad649773cd4a0b4a3cbb2b0fbc707bd3a917116d52444710"
sha=lambda b:hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode())
def unpack(run):
    assert run["rc"]==0 and run["timed_out"] is False and run["elapsed_seconds"]<60
    assert run["threads"]==run["affinity_mask"]==1 and run["hard_child_timeout_seconds"]==60
    d=zlib.decompressobj();raw=d.decompress(base64.b64decode(run["stdout_zlib_base64"],validate=True),1024*1024+1)
    assert len(raw)<=1024*1024 and d.eof and not d.unused_data and not d.unconsumed_tail
    assert len(raw)==run["stdout_bytes"] and sha(raw)==run["stdout_sha256"]
    v=json.loads(raw);assert v["status"]=="PASS" and v["tests"]==7;return v["data"]
def ieee(w,width=64):
    assert type(w) is int and 0<=w<2**width
    mb,eb,bias=(52,11,1023) if width==64 else (23,8,127)
    e=(w>>mb)&(2**eb-1);m=w%(2**mb);assert e<2**eb-1
    return (-1 if w>>(width-1) else 1)*F(m if e==0 else m+2**mb)*F(2)**((1 if e==0 else e)-bias-mb)
def rn(q,w,width=64):
    value=ieee(w,width);mag=w%(2**(width-1))
    if q==0:assert value==0;return value
    assert w>>(width-1)==int(q<0)
    if mag==0:assert abs(q)<=F(2)**(-1075 if width==64 else -150);return value
    lo,hi=abs(ieee(mag-1,width)),abs(ieee(mag+1,width))
    a,b=(lo+abs(value))/2,(abs(value)+hi)/2;even=mag%2==0
    assert (abs(q)>a or abs(q)==a and even) and (abs(q)<b or abs(q)==b and even)
    return value
r=json.loads((ROOT/f"coordinacion/respuestas/{ID}-CODEX.json").read_bytes())
assert r["id"]==ID and len(r["code_doc_sha256"])==57 and r["retained_initial_failure"] is None
for path,h in r["code_doc_sha256"].items():assert sha((ROOT/path).read_bytes())==h,path
new=unpack(r["test_run"]);raw=(ROOT/PARENT).read_bytes();assert sha(raw)==PSHA
parent=unpack(json.loads(raw)["test_run"])
fr=(ROOT/"coordinacion/respuestas/PRECISION-AXIAL-COMMON-DETECTOR-FIXTURE-CPU-001-CODEX.json").read_bytes()
assert sha(fr)=="c110b2d9b3d14fea59470833bfb38e6dc075e319c72260182ca4d29043de42cc"
prepared=unpack(json.loads(fr)["test_run"])["prepared"]
paths=prepared["transport"]["original_geometry"]["emitted_paths"]
triangles=prepared["transport"]["decoded_scene"]["triangles"]
flags=("GPU_executed","native_promotion_allowed","physical_scene_authenticated","native_hit_coverage_certified",
       "length_reference_phase_bound_certified","mirror_material_certified","full_field_certified",
       "coherent_field_admission_allowed","interference_phase_certified")
req,res=(new[k] for k in ("requests","results"));assert set(req)==set(res) and len(res)==34
accepted=stopped=parameter_checks=source_checks=relative_checks=0
for name,v in res.items():
    q=req[name];assert all(v[k] is False for k in flags)
    assert all(v[k] is None for k in ("detector_complex_field","detector_power","source_amplitude"))
    assert v["origin"]=="SEALED_PATHS_DECLARED_SOURCE_SHARED_MIRROR_CPU64" and v["full_costs"]=="UNMEASURED_NOT_ZERO"
    assert v["geometry_producers_reexecuted"]==v["propagation_producers_reexecuted"]==0
    assert v["model"]=="precision-axial-common-detector-source-material-CPU-v1"
    if v["request_sha256"] is not None:
        assert v["request_sha256"]==digest({"model":v["model"],"parent":PSHA,"request":q})
        p=parent["results"][q["propagation_case"]];pq=parent["requests"][q["propagation_case"]]
        assert q["propagation_result_sha256"]==digest(p) and p["status"]=="CPU_DECLARED_COMMON_PROPAGATION_BOUNDS_ONLY"
        assert v["propagation_request_sha256"]==p["request_sha256"]
        assert q["prepared_sha256"]==pq["prepared_sha256"]==digest(prepared)
        assert q["original_scene_sha256"]==pq["original_scene_sha256"]==prepared["transport"]["original_scene_sha256"]
        assert q["detector_point_BU"]==pq["detector_point_BU"]==[[0,1],[1,4],[1,4]]
        assert q["units"]=="cycles/rad" and q["declaration"]=="DECLARED_NOT_PHYSICALLY_AUTHENTICATED"
        material=q["material_phase"]
        assert material["profile"]=="DECLARED_SHARED_AXIAL_MIRROR_PHASE_CYCLES"
        assert type(material["primitive_id"]) is int and material["primitive_id"]==1
        matching=[x for x in triangles if x["primitive_id"]==material["primitive_id"]]
        assert len(matching)==1 and matching[0]["object_id"]==material["object_id"]=="common_detector_fixture_surface"
        assert [x["source_id"] for x in q["source_phases"]]==["S0","S1"]
        for path,s in zip(paths,q["source_phases"]):
            assert s["branch_id"]==path["branch_id"] and path["primitive_ids"]==[material["primitive_id"],0]
    n=len(v["parameters"]);parameter_checks+=n;assert n in (0,3)
    assert v["new_RN32_casts"]==2*n
    for k in ("new_first_FP64_casts","new_RN64_transport_subtractions","new_CPU_decode_additions"):assert v[k]==n
    decoded=[];errors=[]
    originals=([F(*x["phase_cycles"]) for x in q["source_phases"]]+[F(*q["material_phase"]["phase_cycles"])]) if n else []
    for row,original in zip(v["parameters"],originals):
        assert F(*row["original_cycles"])==original
        first=rn(original,row["first_uint64"]);h=rn(first,row["high_uint32"],32);l=rn(first-h,row["low_uint32"],32)
        d=rn(h+l,row["decoded_uint64"]);e=abs(d-original)
        assert F(*row["transport_error_cycles"])==e;decoded.append(d);errors.append(e)
    count=len(v["rows"]);assert count in (0,2)
    assert v["new_source_phase_RN64_additions"]==v["new_material_phase_RN64_additions"]==count
    assert v["new_relative_RN64_subtractions"]==int(v["relative"] is not None)
    if count:
        assert n==3 and all(e==0 for e in errors)
        p=parent["results"][q["propagation_case"]];assert len(p["emitted_sources"])==2
        totals=[];corrections=[]
        for i,(row,prop,s,cap) in enumerate(zip(v["rows"],p["rows"],q["source_phases"],q["SOURCE_total_phase_budgets_rad"])):
            source_checks+=1;qp=ieee(prop["quotient_uint64"]);gamma=F(*s["phase_cycles"]);mu=originals[2]
            assert row["source_id"]==s["source_id"]==prop["source_id"]
            assert row["branch_id"]==s["branch_id"]==prop["branch_id"]
            assert row["propagation_uint64"]==prop["quotient_uint64"]
            sg=rn(qp+decoded[i],row["source_sum_uint64"]);e1=abs(sg-qp-decoded[i])
            total=rn(sg+decoded[2],row["total_uint64"]);e2=abs(total-sg-decoded[2])
            exact=F(*prop["original_cycles"])+gamma+mu
            bound=F(*prop["cycle_error_bound"])+errors[i]+errors[2]+e1+e2
            fields={"source_add_RN_error_cycles":e1,"material_add_RN_error_cycles":e2,
                    "declared_total_original_cycles":exact,"total_cycle_error_bound":bound,
                    "total_phase_bound_rad":8*bound,"budget_rad":F(*cap)}
            assert all(F(*row[k])==a for k,a in fields.items())
            assert abs(total-exact)<=bound and row["budget_fits"] is (8*bound<=F(*cap))
            totals.append(total);corrections.append(errors[i]+e1+e2)
        rel=v["relative"];relative_checks+=1;delta=rn(totals[0]-totals[1],rel["delta_uint64"])
        e_delta=abs(delta-totals[0]+totals[1])
        base=F(*p["relative"]["cycle_error_bound"])-F(*p["relative"]["delta_RN_error_cycles"])
        assert base>=0 and F(*rel["retained_relative_without_old_delta_RN_bound_cycles"])==base
        bound=base+sum(corrections)+e_delta
        exact=F(*p["relative"]["original_cycles"])+originals[0]-originals[1]
        fields={"declared_original_cycles":exact,"delta_RN_error_cycles":e_delta,
                "total_cycle_error_bound":bound,"total_phase_bound_rad":8*bound,"budget_rad":F(*q["relative_total_phase_budget_rad"])}
        assert all(F(*rel[k])==a for k,a in fields.items())
        assert rel["source_order"]==["S0","S1"] and rel["shared_material_phase_cancels_exactly"] is True
        assert abs(delta-exact)<=bound and rel["budget_fits"] is (8*bound<=F(*q["relative_total_phase_budget_rad"]))
    if v["status"]=="STOP":
        stopped+=1;assert v["emitted_sources"]==[] and v["reason"]
    else:
        accepted+=1;assert v["status"]=="CPU_DECLARED_SOURCE_MATERIAL_PHASE_BOUNDS_ONLY"
        assert v["emitted_sources"]==v["rows"] and count==2
        assert all(x["budget_fits"] for x in v["rows"]) and v["relative"]["budget_fits"] is True
assert (accepted,stopped,parameter_checks,source_checks,relative_checks)==(7,27,45,24,12)
assert res["exact"]["relative"]["declared_original_cycles"]==[31,8]
assert res["quotient_partial"]["relative"]["declared_original_cycles"]==[13,24]
for name in ("small_SOURCE_zero_STOP","shared_material_SOURCE_STOP","retained_second_SOURCE_zero_STOP"):
    assert res[name]["reason"]=="SOURCE_total_phase_budget_exceeded" and res[name]["relative"]["budget_fits"] is True
for name in ("small_SOURCE_relative_STOP","shared_material_relative_STOP"):
    assert res[name]["reason"]=="relative_total_phase_budget_exceeded"
assert res["small_SOURCE_zero_STOP"]["rows"][0]["source_add_RN_error_cycles"]==[1,2**56]
assert res["shared_material_relative_STOP"]["relative"]["declared_original_cycles"]==[4,1]
assert F(*res["shared_material_relative_STOP"]["relative"]["total_cycle_error_bound"])>0
for name in ("source_transport_loss","material_transport_loss","first_cast_loss"):
    assert res[name]["reason"]=="phase_parameter_transport_loss" and res[name]["rows"]==[]
for name in ("source_subset","source_reorder","branch_changed","primitive_changed","primitive_bool","object_changed",
             "profile_changed","declaration_changed","scene_changed","prepared_changed","result_changed","detector_changed",
             "negative_cap","missing_caps","missing_material","units_changed","upstream_STOP","parent_changed","wrong_model"):
    assert res[name]["new_RN32_casts"]==0 and res[name]["rows"]==[]
assert res["upstream_STOP"]["reason"]=="upstream_propagation_STOP"
assert res["parent_changed"]["reason"]=="sealed_parent_identity"
assert res["small_SOURCE_partial"]["request_sha256"]!=res["small_SOURCE_zero_STOP"]["request_sha256"]
assert res["small_SOURCE_partial"]["rows"][0]["total_phase_bound_rad"]==res["small_SOURCE_zero_STOP"]["rows"][0]["total_phase_bound_rad"]
print(json.dumps({"status":"PASS","pins":57,"new_requests":34,"partial_CPU":7,"STOP":27,"parameter_IEEE_checks":45,
                  "SOURCE_total_checks":24,"relative_total_checks":12,"geometry_replayed":0,"propagation_replayed":0,
                  "GPU_executed":False,"interference_phase_certified":False},sort_keys=True))
