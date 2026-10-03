"""Independent exact IEEE/RN wiring and twofold phase bounds. No producer/consumer imports."""
import base64,hashlib,json,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
ID="PRECISION-AXIAL-COMMON-DETECTOR-TWOFOLD-CPU-001"
PSHA="1adab489f2452018cdc5374ab0b7c6439e06a0b027d578e7c7c808047df3b94f"
sha=lambda b:hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode())
def unpack(run):
    assert run["rc"]==0 and run["timed_out"] is False and run["elapsed_seconds"]<60
    assert run["threads"]==run["affinity_mask"]==1 and run["hard_child_timeout_seconds"]==60
    d=zlib.decompressobj();raw=d.decompress(base64.b64decode(run["stdout_zlib_base64"],validate=True),1024*1024+1)
    assert len(raw)<=1024*1024 and d.eof and not d.unused_data and not d.unconsumed_tail
    assert len(raw)==run["stdout_bytes"] and sha(raw)==run["stdout_sha256"]
    v=json.loads(raw);assert v["status"]=="PASS" and v["tests"]==7;return v["data"]
def ieee(w):
    assert type(w) is int and 0<=w<2**64
    e=(w>>52)&2047;m=w%(2**52);assert e<2047
    return (-1 if w>>63 else 1)*F(m if e==0 else m+2**52)*F(2)**((1 if e==0 else e)-1023-52)
def rn(q,w):
    value=ieee(w);mag=w%(2**63)
    if q==0:assert value==0;return value
    assert w>>63==int(q<0)
    if mag==0:assert abs(q)<=F(2)**-1075;return value
    lo,hi=abs(ieee(mag-1)),abs(ieee(mag+1));a,b=(lo+abs(value))/2,(abs(value)+hi)/2;even=mag%2==0
    assert (abs(q)>a or abs(q)==a and even) and (abs(q)<b or abs(q)==b and even);return value
def trace(v,fault=False):
    nodes={n["label"]:n for n in v["nodes"]};assert len(nodes)==len(v["nodes"])
    for n in nodes.values():
        assert n["op"] in ("add","sub")
        a,b=(ieee(n[k]) for k in ("a_uint64","b_uint64"));exact=a+b if n["op"]=="add" else a-b
        if n["finite"] is False:
            assert len(nodes)==1 and abs(exact)>=F(2)**1024-F(2)**970
            assert n["result_uint64"]%(2**63)==2047*2**52 and n["result_uint64"]>>63==int(exact<0)
        else:assert n["finite"] is True;rn(exact,n["result_uint64"])
    for c in v["two_sum_checks"]:
        label=c["label"];ns=[nodes[label+"."+k] for k in ("s","bb","aa","da","db","e")]
        a,b=c["a_uint64"],c["b_uint64"];s,bb,aa,da,db,e=(n["result_uint64"] for n in ns)
        assert ns[0]["a_uint64"]==a and ns[0]["b_uint64"]==b and ns[0]["op"]=="add"
        assert [(n["a_uint64"],n["b_uint64"],n["op"]) for n in ns[1:]]==[
            (s,a,"sub"),(s,bb,"sub"),(a,aa,"sub"),(b,bb,"sub"),(da,db,"add")]
        assert c["sum_uint64"]==s
        if fault:assert len(v["two_sum_checks"])==1 and c["error_uint64"]==0 and e!=0
        else:assert c["error_uint64"]==e
        defect=abs(ieee(c["sum_uint64"])+ieee(c["error_uint64"])-ieee(a)-ieee(b))
        assert F(*c["exact_pair_defect_cycles"])==defect
        assert (defect>0) is fault
    return nodes,{c["label"]:c for c in v["two_sum_checks"]}
r=json.loads((ROOT/f"coordinacion/respuestas/{ID}-CODEX.json").read_bytes())
assert r["id"]==ID and len(r["code_doc_sha256"])==62
for path,h in r["code_doc_sha256"].items():assert sha((ROOT/path).read_bytes())==h,path
capture=r["retained_initial_failure"]
assert capture["reason"].startswith("exec_command output truncated") and capture["altered_algorithm_or_caps"] is False
assert r["scientific_verdict_of_initial_capture"]=="UNKNOWN"
new=unpack(r["test_run"])
raw=(ROOT/"coordinacion/respuestas/PRECISION-AXIAL-COMMON-DETECTOR-SOURCE-MATERIAL-CPU-001-CODEX.json").read_bytes()
assert sha(raw)==PSHA;old=unpack(json.loads(raw)["test_run"])
raw=(ROOT/"coordinacion/respuestas/PRECISION-AXIAL-COMMON-DETECTOR-PHASE-CPU-001-CODEX.json").read_bytes()
assert sha(raw)=="0e529d1d0dd5099fad649773cd4a0b4a3cbb2b0fbc707bd3a917116d52444710";propdata=unpack(json.loads(raw)["test_run"])
flags=("GPU_executed","native_promotion_allowed","physical_scene_authenticated","native_hit_coverage_certified",
       "length_reference_phase_bound_certified","mirror_material_certified","full_field_certified",
       "coherent_field_admission_allowed","interference_phase_certified")
req,res=(new[k] for k in ("requests","results"));assert set(req)==set(res) and len(res)==30
accepted=stopped=rn_nodes=eft_checks=source_checks=relative_checks=0
for name,v in res.items():
    q=req[name];assert all(v[k] is False for k in flags)
    assert v["representation"]=="PAIR_FLOAT64_CPU_NOT_GPU_ABI" and v["origin"]=="SEALED_SAME_LITERAL_NEW_TWOFOLD_CPU64"
    assert all(v[k] is None for k in ("detector_complex_field","detector_power","source_amplitude"))
    assert v["full_costs"]=="UNMEASURED_NOT_ZERO"
    assert all(v[k]==0 for k in ("geometry_producers_reexecuted","propagation_producers_reexecuted",
                                "baseline_material_producers_reexecuted","parameter_encoders_reexecuted"))
    nodes,checks=trace(v,fault=name=="injected_pair_fault");rn_nodes+=len(nodes);eft_checks+=len(checks)
    if v["request_sha256"] is not None:
        assert v["request_sha256"]==digest({"model":v["model"],"parent":PSHA,"request":q})
        case=q["retained_case"];baseline=old["results"][case];literal=old["requests"][case]
        assert q["retained_result_sha256"]==v["retained_baseline_result_sha256"]==digest(baseline)
        assert q["literal_request_sha256"]==v["literal_request_sha256"]==digest(literal)
        assert q["original_scene_sha256"]==literal["original_scene_sha256"]
        assert v["retained_baseline_status"]==baseline["status"]
        assert baseline["request_sha256"] is not None and len(baseline["rows"])==2
        assert all(p["transport_error_cycles"]==[0,1] for p in baseline["parameters"])
        p=propdata["results"][literal["propagation_case"]];assert digest(p)==literal["propagation_result_sha256"]
        assert p["status"]=="CPU_DECLARED_COMMON_PROPAGATION_BOUNDS_ONLY"
    if v["relative"] is not None:
        assert len(nodes)==52 and len(checks)==8 and len(v["rows"])==2
        decoded=[ieee(x["decoded_uint64"]) for x in baseline["parameters"]]
        gammas=[F(*x["phase_cycles"]) for x in literal["source_phases"]];mu=F(*literal["material_phase"]["phase_cycles"])
        assert decoded==gammas+[mu]
        mix_errors=[];totals=[]
        for i,(row,pr,cap) in enumerate(zip(v["rows"],p["rows"],literal["SOURCE_total_phase_budgets_rad"])):
            source_checks+=1;sid=pr["source_id"];c=checks[sid+".source"];mat=checks[sid+".material"];norm=checks[sid+".normalize"]
            assert c["a_uint64"]==pr["quotient_uint64"]==row["propagation_uint64"]
            assert ieee(c["b_uint64"])==decoded[i]
            assert mat["a_uint64"]==c["sum_uint64"] and ieee(mat["b_uint64"])==decoded[2]
            n=nodes[sid+".material_low_mix"]
            assert (n["a_uint64"],n["b_uint64"],n["op"])==(c["error_uint64"],mat["error_uint64"],"add")
            mix=abs(ieee(n["result_uint64"])-ieee(n["a_uint64"])-ieee(n["b_uint64"]))
            assert norm["a_uint64"]==mat["sum_uint64"] and norm["b_uint64"]==n["result_uint64"]
            assert row["pair_uint64"]==[norm["sum_uint64"],norm["error_uint64"]]
            hi,lo=(ieee(w) for w in row["pair_uint64"]);represented=hi+lo
            exact=F(*pr["original_cycles"])+gammas[i]+mu;bound=F(*pr["cycle_error_bound"])+mix
            fields={"represented_cycles":represented,"original_declared_cycles":exact,"material_low_mix_error_cycles":mix,
                    "total_cycle_error_bound":bound,"total_phase_bound_rad":8*bound,"budget_rad":F(*cap)}
            assert all(F(*row[k])==value for k,value in fields.items())
            assert row["source_id"]==sid and row["branch_id"]==pr["branch_id"] and row["budget_rad"]==cap
            assert abs(represented-exact)<=bound and row["budget_fits"] is (8*bound<=F(*cap))
            mix_errors.append(mix);totals.append((hi,lo))
        c=checks["relative.high"];n=nodes["relative.low_difference"];u=nodes["relative.low_mix"];norm=checks["relative.normalize"]
        assert ieee(c["a_uint64"])==totals[0][0] and ieee(c["b_uint64"])==-totals[1][0]
        assert (ieee(n["a_uint64"]),ieee(n["b_uint64"]),n["op"])==(totals[0][1],totals[1][1],"sub")
        et=abs(ieee(n["result_uint64"])-totals[0][1]+totals[1][1])
        assert (u["a_uint64"],u["b_uint64"],u["op"])==(c["error_uint64"],n["result_uint64"],"add")
        eu=abs(ieee(u["result_uint64"])-ieee(u["a_uint64"])-ieee(u["b_uint64"]))
        assert (norm["a_uint64"],norm["b_uint64"])==(c["sum_uint64"],u["result_uint64"])
        rel=v["relative"];relative_checks+=1;assert rel["pair_uint64"]==[norm["sum_uint64"],norm["error_uint64"]]
        represented=sum(ieee(w) for w in rel["pair_uint64"])
        base=F(*p["relative"]["cycle_error_bound"])-F(*p["relative"]["delta_RN_error_cycles"]);assert base>=0
        bound=base+sum(mix_errors)+et+eu;exact=F(*p["relative"]["original_cycles"])+gammas[0]-gammas[1]
        fields={"represented_cycles":represented,"original_declared_cycles":exact,
                "retained_relative_without_old_delta_RN_bound_cycles":base,"low_difference_error_cycles":et,
                "low_mix_error_cycles":eu,"total_cycle_error_bound":bound,"total_phase_bound_rad":8*bound,
                "budget_rad":F(*literal["relative_total_phase_budget_rad"])}
        assert all(F(*rel[k])==value for k,value in fields.items())
        assert rel["budget_rad"]==literal["relative_total_phase_budget_rad"] and rel["source_order"]==["S0","S1"]
        assert abs(represented-exact)<=bound and rel["budget_fits"] is (8*bound<=F(*literal["relative_total_phase_budget_rad"]))
    else:assert len(nodes)==6 if name=="injected_pair_fault" else len(nodes)==0
    if v["status"]=="STOP":
        stopped+=1;assert v["reason"] and v["emitted_sources"]==[]
    else:
        accepted+=1;assert v["status"]=="CPU_DECLARED_TWOFOLD_PHASE_BOUND_ONLY"
        assert v["emitted_sources"]==v["rows"] and all(x["budget_fits"] for x in v["rows"]) and v["relative"]["budget_fits"]
assert (accepted,stopped,rn_nodes,eft_checks,source_checks,relative_checks)==(11,19,630,97,24,12)
controls=new["controls"];assert len(controls)==8
control_nodes=control_eft=0
for name,c in controls.items():
    nodes,checks=trace(c);control_nodes+=len(nodes);control_eft+=len(checks)
    if name=="overflow":assert c["status"]=="STOP" and c["reason"]=="finite_RN_result" and len(nodes)==1
    else:
        assert c["status"]=="EXACT_PAIR" and len(nodes)==6 and len(checks)==1
        assert c["pair_uint64"]==[checks["control"]["sum_uint64"],checks["control"]["error_uint64"]]
        assert sum(ieee(w) for w in c["pair_uint64"])==ieee(c["a_uint64"])+ieee(c["b_uint64"])
assert (control_nodes,control_eft)==(43,7)
for name in ("small_SOURCE_zero_STOP","small_SOURCE_relative_STOP","shared_material_SOURCE_STOP","shared_material_relative_STOP"):
    assert res[name]["retained_baseline_status"]=="STOP" and old["results"][name]["status"]=="STOP"
    assert F(*old["results"][name]["rows"][0]["total_cycle_error_bound"])>0
    assert res[name]["relative"]["total_cycle_error_bound"]==[0,1] and res[name]["status"]=="CPU_DECLARED_TWOFOLD_PHASE_BOUND_ONLY"
assert res["retained_second_SOURCE_zero_STOP"]["reason"]=="SOURCE_total_phase_budget_exceeded"
assert F(*res["retained_second_SOURCE_zero_STOP"]["rows"][1]["total_cycle_error_bound"])>0
assert res["injected_pair_fault"]["reason"]=="TwoSum_exact_pair_failure" and res["injected_pair_fault"]["emitted_sources"]==[]
print(json.dumps({"status":"PASS","pins":62,"new_selectors":30,"partial_CPU":11,"STOP":19,"RN_phase_nodes":630,
                  "EFT_checks":97,"SOURCE_checks":24,"relative_checks":12,"synthetic_controls":8,
                  "control_RN_nodes":43,"control_EFT_checks":7,"frozen_baseline_replayed":0,"GPU_executed":False,
                  "output_same_as_native_baseline":False,"full_costs":"UNMEASURED_NOT_ZERO"},sort_keys=True))
