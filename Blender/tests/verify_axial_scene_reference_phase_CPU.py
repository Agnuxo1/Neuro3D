"""Independent retained rational/IEEE metrology, no producer imports, no child or scene replay."""
import base64,hashlib,json,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sha=lambda b:hashlib.sha256(b).hexdigest()
r=json.loads((ROOT/"coordinacion/respuestas/PRECISION-AXIAL-SCENE-REFERENCE-PHASE-CPU-001-CODEX.json").read_bytes())
for p,h in r["code_doc_sha256"].items():assert sha((ROOT/p).read_bytes())==h,p
def unpack(run):
    assert run["threads"]==run["affinity_mask"]==1 and run["hard_child_timeout_seconds"]==60
    assert not run["timed_out"] and run["elapsed_seconds"]<60
    raw=zlib.decompress(base64.b64decode(run["stdout_zlib_base64"],validate=True))
    assert len(raw)==run["stdout_bytes"] and sha(raw)==run["stdout_sha256"]
    return json.loads(raw)
assert r["test_run"]["rc"]==0 and r["retained_initial_failure"]["rc"]==1
new=unpack(r["test_run"]);old=unpack(r["retained_initial_failure"])
assert new["status"]=="PASS" and new["tests"]==7 and old["status"]=="FAIL" and old["tests"]==7
for p,row in r["retained_initial_sources"].items():
    b=base64.b64decode(row["base64"],validate=True);assert sha(b)==row["sha256"]
    if "/benchmarks/" in p:assert (ROOT/p).read_bytes()==b
    else:
        original=b.decode().replace("\r\n","\n")
        expected=original.replace('        with patch.object(a,"PARENT_SHA","0"*64):\n            r=run("parent_identity_STOP","noncanonical_literal",requests("noncanonical_literal"))',
           '        q=requests("noncanonical_literal")\n        with patch.object(a,"PARENT_SHA","0"*64):\n            r=run("parent_identity_STOP","noncanonical_literal",q)')
        assert original!=expected and (ROOT/p).read_text()==expected
assert "parent_identity_STOP" not in old["data"]["results"]
parent=json.loads((ROOT/"coordinacion/respuestas/PRECISION-AXIAL-SCENE-TRANSPORT-CPU-001-CODEX.json").read_bytes())
retained=unpack(parent["test_run"])["data"]["results"]
def ieee(w,width=64):
    assert type(w) is int and 0<=w<2**width
    mb,eb,bias=(52,11,1023) if width==64 else (23,8,127)
    e=(w>>mb)&(2**eb-1);m=w%(2**mb);assert e<2**eb-1
    return (-1 if w>>(width-1) else 1)*F(m if e==0 else m+2**mb)*F(2)**((1 if e==0 else e)-bias-mb)
def rn(q,w,width=64):
    val=ieee(w,width);mag=w%(2**(width-1))
    if q==0:assert val==0;return val
    assert w>>(width-1)==int(q<0)
    if mag==0:
        assert abs(q)<=F(2)**(-1075 if width==64 else -150);return val
    lower,upper=abs(ieee(mag-1,width)),abs(ieee(mag+1,width))
    left,right=(lower+abs(val))/2,(abs(val)+upper)/2;even=mag%2==0
    assert (abs(q)>left or abs(q)==left and even) and (abs(q)<right or abs(q)==right and even)
    return val
rows,reqs,cases=(new["data"][k] for k in ("results","requests","cases"))
assert len(rows)==19 and set(rows)==set(reqs)==set(cases)
flags=("GPU_executed","native_promotion_allowed","physical_scene_authenticated","native_hit_coverage_certified",
       "length_reference_phase_bound_certified","mirror_material_certified","full_field_certified")
accepted=stopped=calculated=parameter_scalars=0
for name,out in rows.items():
    assert all(out[k] is False for k in flags) and out["old_geometry_producers_reexecuted"]==0
    assert out["full_costs"]=="UNMEASURED_NOT_ZERO"
    assert out["origin"]=="RETAINED_EXACT_POINT_CPU_PATHS_NEW_DECLARED_REFERENCE_GAUGE"
    params=sum(len(row["parameters"]) for row in out["rows"]);parameter_scalars+=params
    assert out["new_parameter_RN32_casts"]==2*params
    assert out["new_parameter_RN64_subtractions"]==out["new_parameter_RN64_decode_additions"]==out["new_parameter_float64_casts"]==params
    n=sum(row["propagation_phase_bound_computed"] for row in out["rows"]);calculated+=n
    for k in ("new_endpoint_float64_casts","new_path_RN64_additions","new_reference_RN64_subtractions",
              "new_residual_RN64_subtractions","new_quotient_RN64_divisions"):assert out[k]==n
    if out["request_sha256"] is not None:
        canonical={"model":out["model"],"case":cases[name],"parent":out["parent_sha256"],"requests":reqs[name]}
        assert sha(json.dumps(canonical,sort_keys=True,separators=(",",":"),allow_nan=False).encode())==out["request_sha256"]
    for row in out["rows"]:
        for v in row["parameters"]:
            q=F(*v["original_rational"]);first=rn(q,v["first_uint64"])
            h=rn(first,v["high_uint32"],32);l=rn(first-h,v["low_uint32"],32)
            decoded=rn(h+l,v["decoded_uint64"])
            assert F(*v["decoded_rational"])==decoded and F(*v["point_error_abs"])==abs(decoded-q)
        if not row["propagation_phase_bound_computed"]:continue
        source=row["source_id"];up=retained[cases[name]];q=next(x for x in reqs[name] if x["source_id"]==source)
        path=next(x for x in up["original_geometry"]["emitted_paths"] if x["source_id"]==source)
        assert row["request"]==q and row["path"]==path
        a,b=(F(*v) for v in path["segments_rational_BU"])
        fp_a,fp_b=(ieee(w) for w in row["retained_segment_float64_uint64"])
        assert fp_a==F(float(a)) and fp_b==F(float(b))
        length=rn(fp_a+fp_b,row["length_float64_uint64"])
        endpoint=F(*path["endpoint_rational_BU"][0]);ref=F(*q["reference_plane_x_BU"]);lam=F(*q["wavelength_BU"])
        reference_exact=q["reference_normal_x"]*(endpoint-ref)
        # Exact sign reversal commutes with symmetric ties-to-even for the represented projection.
        reference=rn(reference_exact,row["reference_float64_uint64"])
        residual=rn(length-reference,row["residual_float64_uint64"])
        quotient=rn(residual/lam,row["quotient_float64_uint64"])
        e_inputs=abs(fp_a-a)+abs(fp_b-b);e_sum=abs(length-fp_a-fp_b);e_length=e_inputs+e_sum
        e_reference=abs(reference-reference_exact);e_sub=abs(residual-length+reference)
        e_residual=e_length+e_reference+e_sub;e_div=abs(quotient-residual/lam)
        cycles=(a+b-reference_exact)/lam;observed=abs(quotient-cycles);bound=e_residual/lam+e_div
        expected={"length_exact_BU":a+b,"reference_exact_BU":reference_exact,
          "segment_input_error_bound_BU":e_inputs,"length_sum_RN64_error_bound_BU":e_sum,"length_error_bound_BU":e_length,
          "reference_error_bound_BU":e_reference,"residual_sub_RN64_error_bound_BU":e_sub,"residual_error_bound_BU":e_residual,
          "quotient_div_RN64_error_bound_cycles":e_div,"original_cycles":cycles,"observed_cycle_error_abs":observed,
          "cycle_error_bound_abs":bound,"propagation_phase_error_bound_rad":8*bound,
          "declared_phase_budget_rad":F(*q["phase_budget_rad"])}
        assert all(F(*row[k])==v for k,v in expected.items())
        assert observed<=bound and row["budget_fits"]==(8*bound<=F(*q["phase_budget_rad"]))
    if out["status"]=="STOP":stopped+=1;assert out["emitted_sources"]==[] and out["reason"]
    else:
        accepted+=1;assert out["status"]=="CPU_DECLARED_PROPAGATION_PHASE_BOUND_ONLY"
        assert len(out["emitted_sources"])==len(out["rows"])==len(reqs[name])
        assert all(row["budget_fits"] for row in out["rows"])
assert (accepted,stopped,calculated,parameter_scalars)==(4,15,7,20)
assert [x["original_cycles"] for x in rows["two_SOURCE_zero_error"]["rows"]]==[[14,1],[6,1]]
assert rows["signed_negative_cycles"]["rows"][0]["original_cycles"]==[-26,1]
assert rows["reference_cancellation"]["rows"][0]["reference_error_bound_BU"]==[1,2**48]
assert rows["reference_cancellation"]["rows"][0]["propagation_phase_error_bound_rad"]==[5,65536]
assert rows["reference_cancellation"]["reason"]==rows["division_zero_budget_STOP"]["reason"]=="declared_phase_budget_exceeded"
assert rows["division_partial_bound"]["rows"][0]["propagation_phase_error_bound_rad"]==rows["division_zero_budget_STOP"]["rows"][0]["propagation_phase_error_bound_rad"]
assert rows["division_partial_bound"]["request_sha256"]!=rows["division_zero_budget_STOP"]["request_sha256"]
assert rows["second_SOURCE_parameter_loss"]["new_path_RN64_additions"]==0
assert rows["parent_identity_STOP"]["reason"]=="sealed_parent_changed"
assert rows["upstream_world_thin"]["reason"].startswith("upstream_STOP:")
print(json.dumps({"status":"PASS","pins":len(r["code_doc_sha256"]),"new_requests":19,"accepted_CPU":4,
 "expected_STOP":15,"phase_bound_SOURCE_checks":7,"parameter_RN_checks":20,"old_geometry_replayed":0,
 "initial_setup_failure_retained_core_unchanged":True,"GPU_executed":False,"native_phase_certified":False},sort_keys=True))
