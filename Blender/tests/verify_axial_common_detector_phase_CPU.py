"""Independent exact rational and IEEE metrology, no producer imports or geometry replay."""
import base64,hashlib,json,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sha=lambda b:hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode())
def unpack(run):
    assert run["rc"]==0 and run["timed_out"] is False and run["elapsed_seconds"]<60
    assert run["threads"]==run["affinity_mask"]==1 and run["hard_child_timeout_seconds"]==60
    d=zlib.decompressobj();raw=d.decompress(base64.b64decode(run["stdout_zlib_base64"],validate=True),1024*1024+1)
    assert len(raw)<=1024*1024 and d.eof and not d.unused_data and not d.unconsumed_tail
    assert len(raw)==run["stdout_bytes"] and sha(raw)==run["stdout_sha256"]
    v=json.loads(raw);assert v["status"]=="PASS" and v["tests"]==7;return v["data"]
r=json.loads((ROOT/"coordinacion/respuestas/PRECISION-AXIAL-COMMON-DETECTOR-PHASE-CPU-001-CODEX.json").read_bytes())
for path,h in r["code_doc_sha256"].items():assert sha((ROOT/path).read_bytes())==h,path
assert len(r["code_doc_sha256"])==50 and r["retained_initial_failure"] is None
new=unpack(r["test_run"])
raw=(ROOT/"coordinacion/respuestas/PRECISION-AXIAL-COMMON-DETECTOR-FIXTURE-CPU-001-CODEX.json").read_bytes()
assert sha(raw)=="c110b2d9b3d14fea59470833bfb38e6dc075e319c72260182ca4d29043de42cc"
prepared=unpack(json.loads(raw)["test_run"])["prepared"]
paths=prepared["transport"]["original_geometry"]["emitted_paths"]
assert [F(*x["length_rational_BU"]) for x in paths]==[F(7,4),F(5,4)]
assert all(x["endpoint_rational_BU"]==[[0,1],[1,4],[1,4]] for x in paths)
def ieee(w,width=64):
    assert type(w) is int and 0<=w<2**width
    mb,eb,bias=(52,11,1023) if width==64 else (23,8,127)
    e=(w>>mb)&(2**eb-1);m=w%(2**mb);assert e<2**eb-1
    return (-1 if w>>(width-1) else 1)*F(m if e==0 else m+2**mb)*F(2)**((1 if e==0 else e)-bias-mb)
def rn(q,w,width=64):
    val=ieee(w,width);mag=w%(2**(width-1))
    if q==0:assert val==0;return val
    assert w>>(width-1)==int(q<0)
    if mag==0:assert abs(q)<=F(2)**(-1075 if width==64 else -150);return val
    lo,hi=abs(ieee(mag-1,width)),abs(ieee(mag+1,width))
    left,right=(lo+abs(val))/2,(abs(val)+hi)/2;even=mag%2==0
    assert (abs(q)>left or abs(q)==left and even) and (abs(q)<right or abs(q)==right and even)
    return val
flags=("GPU_executed","native_promotion_allowed","physical_scene_authenticated","native_hit_coverage_certified",
       "length_reference_phase_bound_certified","mirror_material_certified","full_field_certified",
       "coherent_field_admission_allowed","interference_phase_certified")
requests,results=(new[k] for k in ("requests","results"));assert set(requests)==set(results) and len(results)==22
accepted=stopped=source_checks=relative_checks=parameter_checks=0
for name,out in results.items():
    q=requests[name]
    assert all(out[k] is False for k in flags)
    assert all(out[k] is None for k in ("detector_complex_field","detector_power","source_amplitude","source_material_phase"))
    assert out["geometry_producers_reexecuted"]==out["old_phase_producers_reexecuted"]==0
    assert out["origin"]=="SEALED_COMMON_ENDPOINT_DECLARED_PROPAGATION_CPU64" and out["full_costs"]=="UNMEASURED_NOT_ZERO"
    if out["request_sha256"] is not None:
        assert out["request_sha256"]==digest({"model":out["model"],"parent":out["parent_sha256"],"request":q})
        assert q["prepared_sha256"]==digest(prepared)
        assert q["original_scene_sha256"]==prepared["transport"]["original_scene_sha256"]
        assert q["source_ids"]==["S0","S1"] and q["detector_point_BU"]==[[0,1],[1,4],[1,4]]
    n=len(out["parameters"]);parameter_checks+=n
    assert out["parameter_RN32_casts"]==2*n and out["parameter_RN64_subtractions"]==out["parameter_CPU_decode_additions"]==n
    for row in out["parameters"]:
        original=F(*row["original_rational"]);first=rn(original,row["first_uint64"])
        h=rn(first,row["high_uint32"],32);low=rn(first-h,row["low_uint32"],32)
        decoded=rn(h+low,row["decoded_uint64"])
        assert F(*row["point_error_abs"])==abs(decoded-original)
    count=len(out["rows"])
    for k in ("new_path_RN64_additions","new_residual_RN64_subtractions","new_quotient_RN64_divisions"):assert out[k]==count
    assert out["new_shared_reference_RN64_subtractions"]==int(count!=0)
    assert out["new_relative_RN64_subtractions"]==int(out["relative"] is not None)
    if count:
        assert count==2
        lam=F(*q["wavelength_BU"]);ref=F(*q["reference_plane_x_BU"]);reference=q["reference_normal_x"]*(-ref)
        rfp=rn(reference,out["shared_reference"]["float64_uint64"]);er=abs(rfp-reference)
        assert F(*out["shared_reference"]["exact_BU"])==reference and F(*out["shared_reference"]["error_abs_BU"])==er
        native_q=[];bounds=[]
        for row,path,cap in zip(out["rows"],paths,q["SOURCE_phase_budgets_rad"]):
            source_checks+=1;a,b=(F(*v) for v in path["segments_rational_BU"])
            fa,fb=(ieee(w) for w in row["segments_retained_uint64"])
            assert fa==a and fb==b
            length=rn(fa+fb,row["length_uint64"]);el=abs(fa-a)+abs(fb-b)+abs(length-fa-fb)
            residual=rn(length-rfp,row["residual_uint64"]);es=abs(residual-length+rfp)
            quotient=rn(residual/lam,row["quotient_uint64"]);ed=abs(quotient-residual/lam)
            original=(a+b-reference)/lam;bound=(el+er+es)/lam+ed
            expected={"length_exact_BU":a+b,"length_error_BU":el,"residual_RN_error_BU":es,
                      "division_RN_error_cycles":ed,"original_cycles":original,"cycle_error_bound":bound,
                      "propagation_phase_bound_rad":8*bound,"budget_rad":F(*cap)}
            assert row["source_id"]==path["source_id"] and row["branch_id"]==path["branch_id"]
            assert all(F(*row[k])==v for k,v in expected.items())
            assert abs(quotient-original)<=bound and row["budget_fits"] is (8*bound<=F(*cap))
            native_q.append(quotient);bounds.append((el,es,ed))
        rel=out["relative"];relative_checks+=1
        delta=rn(native_q[0]-native_q[1],rel["delta_uint64"])
        e_delta=abs(delta-native_q[0]+native_q[1]);bound=sum((el+es)/lam+ed for el,es,ed in bounds)+e_delta
        original_delta=(F(*paths[0]["length_rational_BU"])-F(*paths[1]["length_rational_BU"]))/lam
        assert rel["shared_reference_cancels_exactly"] is True and rel["source_order"]==["S0","S1"]
        assert F(*rel["original_cycles"])==original_delta and F(*rel["cycle_error_bound"])==bound
        assert F(*rel["delta_RN_error_cycles"])==e_delta and F(*rel["propagation_phase_bound_rad"])==8*bound
        assert rel["budget_fits"] is (8*bound<=F(*q["relative_propagation_budget_rad"]))
        assert abs(delta-original_delta)<=bound
    if out["status"]=="STOP":
        stopped+=1;assert out["emitted_sources"]==[] and out["reason"]
    else:
        accepted+=1;assert out["status"]=="CPU_DECLARED_COMMON_PROPAGATION_BOUNDS_ONLY"
        assert out["emitted_sources"]==out["rows"] and count==2
        assert all(row["budget_fits"] for row in out["rows"]) and out["relative"]["budget_fits"] is True
assert (accepted,stopped,source_checks,relative_checks,parameter_checks)==(5,17,16,8,20)
assert results["exact"]["relative"]["original_cycles"]==[4,1]
assert [v["original_cycles"] for v in results["exact"]["rows"]]==[[14,1],[10,1]]
assert [v["original_cycles"] for v in results["signed_reference"]["rows"]]==[[6,1],[2,1]]
assert results["signed_reference"]["relative"]["original_cycles"]==[4,1]
assert results["quotient_partial"]["relative"]["original_cycles"]==[2,3]
assert F(*results["quotient_partial"]["relative"]["cycle_error_bound"])>0
assert results["relative_zero_STOP"]["reason"]=="relative_propagation_budget_exceeded"
for name in ("second_SOURCE_zero_STOP","large_reference_SOURCE_STOP"):
    assert results[name]["reason"]=="SOURCE_phase_budget_exceeded" and results[name]["relative"]["budget_fits"] is True
assert results["relative_zero_STOP"]["relative"]["propagation_phase_bound_rad"]==results["quotient_partial"]["relative"]["propagation_phase_bound_rad"]
assert results["relative_zero_STOP"]["request_sha256"]!=results["quotient_partial"]["request_sha256"]
for name in ("lambda_transport_loss","reference_transport_loss"):
    assert results[name]["reason"]=="parameter_transport_loss" and results[name]["new_path_RN64_additions"]==0
assert results["parent_changed"]["reason"]=="sealed_parent_identity"
print(json.dumps({"status":"PASS","pins":50,"new_requests":22,"partial_CPU":5,"STOP":17,
 "SOURCE_phase_checks":16,"relative_phase_checks":8,"parameter_IEEE_checks":20,
 "geometry_replayed":0,"old_phase_replayed":0,"GPU_executed":False,"interference_phase_certified":False},sort_keys=True))
