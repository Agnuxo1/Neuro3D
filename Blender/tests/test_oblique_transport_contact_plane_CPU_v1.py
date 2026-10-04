"""New plane-box consumer; saved intersections/transport reused, never old producer runs."""
from pathlib import Path
from fractions import Fraction as F
import base64,copy,hashlib,importlib.util,json,zlib

ROOT=Path(__file__).resolve().parents[2]
PARENT="coordinacion/respuestas/PRECISION-EXACT-SCALAR-HILO32-CPU-001-CODEX.json"
SHA="fdf61608eaa7e1bcb025983feeba3b2067cab5eb8f754de385944d3edc10f6db"
ORDER="coordinacion/respuestas/PRECISION-EXACT-PARAMETER-ORDER-CPU-001-CODEX.json"
CORE="Blender/benchmarks/capacity_audit/oblique_transport_contact_plane_CPU_v1.py"


def capture(c):
    d=zlib.decompressobj();b=d.decompress(base64.b64decode(c["stdout_zlib_base64"],validate=True),1048577)
    assert d.eof and not d.unused_data and not d.unconsumed_tail and len(b)<=1048576
    assert c["rc"]==0 and not c["timed_out"] and len(b)==c["stdout_bytes"] and hashlib.sha256(b).hexdigest()==c["stdout_sha256"]
    return json.loads(b)


def run():
    raw=(ROOT/PARENT).read_bytes();assert len(raw)==109555 and hashlib.sha256(raw).hexdigest()==SHA
    parent=json.loads(raw);pins=dict(parent["code_doc_sha256"]);pins[PARENT]=SHA
    for p,h in pins.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    wire=capture(parent["test_run"]);saved=capture(json.loads((ROOT/ORDER).read_bytes())["test_run"])
    spec=importlib.util.spec_from_file_location("own_contact_plane_cpu",ROOT/CORE)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    selected=[e for e in saved["evidence"]if e["rotation"]==0 and not e["swap"]and not e["winding"]and e["result"]["candidate_index"]is not None]
    assert len(selected)==3
    records=[]
    zero=[[[0,1],[0,1]]for _ in range(3)]
    for entry in selected:
        label=entry["case"];candidate=entry["result"]["candidate_index"]
        packets=sorted([e for e in wire["packets"]if e["case"]==label and e["rotation"]==0 and not e["swap"]and not e["winding"]and e["field"].startswith("p")],key=lambda x:x["field"])
        assert len(packets)==3
        words=[w for e in packets for w in (e["packet"]["hi_word"],e["packet"]["lo_word"])]
        assert all(e["packet"]["status"]=="EXACT_PAIR_CPU_ONLY" and e["packet"]["residual_exact"]==[0,1]for e in packets)
        assert all(e["source_raw_stage_sha256"]==entry["result"]["raw_stage_sha256"]for e in packets)
        raw=entry["raw_words"];tri=raw[6+9*candidate:15+9*candidate];direction=raw[3:6]
        gap=F(*entry["result"]["exact_candidate_point"][0]);assert gap>0
        for mode in ("literal_exact","missing_budget","lost_coordinate","uncertain_budget","declared_signed_correction"):
            pwords=words.copy();budget=copy.deepcopy(zero)
            if mode=="missing_budget":budget=None
            if mode in ("lost_coordinate","uncertain_budget","declared_signed_correction"):pwords[:2]=[0,0]
            if mode=="uncertain_budget":budget[0]=[m.pair(-gap),m.pair(gap)]
            if mode=="declared_signed_correction":budget[0]=[m.pair(gap),m.pair(gap)]
            result=m.audit_plane(pwords,tri,direction,budget)
            expected={"literal_exact":"CPU_ZERO_PLANE_CONTACT_ONLY","missing_budget":"STOP_MISSING_DECLARED_POINT_BUDGET","lost_coordinate":"CPU_STRICT_PLANE_SEPARATION_ONLY","uncertain_budget":"CPU_UNCERTAIN_PLANE_CONTACT_STOP","declared_signed_correction":"CPU_ZERO_PLANE_CONTACT_ONLY"}[mode]
            assert result["status"]==expected
            if mode in ("literal_exact","declared_signed_correction"):assert result["plane_parameter_interval"]==[[0,1],[0,1]]
            if mode=="lost_coordinate":assert result["plane_parameter_interval"]==[m.pair(-gap),m.pair(-gap)]
            if mode=="uncertain_budget":assert result["plane_parameter_interval"]==[m.pair(-2*gap),[0,1]]
            for flag in ("GPU_launch_allowed","launch_exclusion_allowed","native_precision_certified","native_point_budget_authenticated","triangle_hit_certified","full_path_visibility_certified","phase_certified"):assert result[flag]is False
            records.append({"case":label,"mode":mode,"saved_raw_stage_sha256":entry["result"]["raw_stage_sha256"],"saved_point_words":words,"input_point_words":pwords,"triangle_words":tri,"direction_words":direction,"declared_errors":budget,"result":result})
    base=records[0]
    controls=[]
    for kind in ("parallel","degenerate","subnormal"):
        p=base["input_point_words"].copy();t=base["triangle_words"].copy();d=base["direction_words"].copy()
        if kind=="parallel":d=[0,0x3f800000,0]
        if kind=="degenerate":t[3:6]=t[:3]
        if kind=="subnormal":p[0]=1
        result=m.audit_plane(p,t,d,zero)
        expected={"parallel":"STOP_ZERO_PLANE_DENOMINATOR","degenerate":"STOP_DEGENERATE_PLANE","subnormal":"STOP_SUBNORMAL_POINT_WIRE"}[kind]
        assert result["status"]==expected and result["plane_parameter_interval"]is None
        controls.append({"kind":kind,"input_point_words":p,"triangle_words":t,"direction_words":d,"declared_errors":zero,"result":result})
    bad=[]
    for value in (True,-1,1<<32,0x7f800000,0x80000000):
        p=base["input_point_words"].copy();p[0]=value;bad.append((p,base["triangle_words"],base["direction_words"],zero))
    bad.append(([],base["triangle_words"],base["direction_words"],zero))
    bad.append((base["input_point_words"],base["triangle_words"],[0,0,0],zero))
    for interval in ([[1,0],[0,1]],[[1,1],[0,1]],[[2,2],[2,1]]):
        budget=copy.deepcopy(zero);budget[0]=interval;bad.append((base["input_point_words"],base["triangle_words"],base["direction_words"],budget))
    for args in bad:
        try:m.audit_plane(*args)
        except ValueError:pass
        else:raise AssertionError("malformed plane audit admitted")
    first=m.audit_plane(base["input_point_words"],base["triangle_words"],base["direction_words"],zero)
    first["point_box"][0][0][0]=99
    assert m.audit_plane(base["input_point_words"],base["triangle_words"],base["direction_words"],zero)["plane_residual_interval"]==[[0,1],[0,1]]
    return {"status":"PASS_CPU_DECLARED_TRANSPORT_BOX_PLANE_CONDITION_ONLY_NOT_TRIANGLE_OR_NATIVE",
            "context_pins":pins,"records":records,"controls":controls,"selected_saved_points":3,
            "new_plane_box_audits":18,"malformed_rejections":len(bad),"mutation_isolation_checked":True,
            "recomputed_intersections":0,"old_producer_executions":0,"original_scene_queries_replayed":0,
            "GPU_used":False,"Bpy_used":False,"RT_used":False,"launch_exclusion_allowed":False,
            "native_precision_certified":False,"phase_error_bound":None,"full_costs":"UNKNOWN_NOT_ZERO",
            "prior_zero_error_gate":parent["prior_zero_error_gate"],"prior_scalar_errors":72,"prior_error_rows":16,"prior_contact_STOP":12}

if __name__=="__main__":print(json.dumps(run(),sort_keys=True))
