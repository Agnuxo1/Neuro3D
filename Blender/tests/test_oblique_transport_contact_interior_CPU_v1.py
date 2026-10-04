"""Saved fabricated transport reused; new declared-box membership tests only."""
from pathlib import Path
import base64,copy,hashlib,json,zlib
from Blender.benchmarks.capacity_audit import oblique_transport_contact_interior_CPU_v1 as m

ROOT=Path(__file__).resolve().parents[2]
PARENT="coordinacion/respuestas/PRECISION-TRANSPORT-CONTACT-PLANE-CPU-001-CODEX.json"
SHA="d254341bbd74f28799765b264ccac437ab8f2767d7f0baf4bf7e752efb4ee997"
FLAGS=("GPU_launch_allowed","launch_exclusion_allowed","native_precision_certified",
       "native_point_budget_authenticated","triangle_hit_certified",
       "nearest_hit_certified","full_path_visibility_certified","phase_certified")

def capture(c):
    d=zlib.decompressobj()
    raw=d.decompress(base64.b64decode(c["stdout_zlib_base64"],validate=True),1048577)
    assert d.eof and not d.unused_data and not d.unconsumed_tail and len(raw)<=1048576
    assert c["rc"]==0 and not c["timed_out"] and len(raw)==c["stdout_bytes"]
    assert hashlib.sha256(raw).hexdigest()==c["stdout_sha256"]
    return json.loads(raw)

def run():
    raw=(ROOT/PARENT).read_bytes()
    assert len(raw)==107796 and hashlib.sha256(raw).hexdigest()==SHA
    parent=json.loads(raw); pins=dict(parent["code_doc_sha256"]);pins[PARENT]=SHA
    for p,h in pins.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    saved=[r for r in capture(parent["test_run"])["records"] if r["mode"]=="literal_exact"]
    assert len(saved)==3 and len(pins)==444
    zero=[[[0,1],[0,1]] for _ in range(3)]
    records=[]
    expectations={
      "singleton":("CPU_ZERO_CONTACT_STRICT_INTERIOR_CONDITION_ONLY",[[[1,4],[1,4]],[[1,4],[1,4]],[[1,2],[1,2]]]),
      "tangent_box":("CPU_ZERO_CONTACT_STRICT_INTERIOR_CONDITION_ONLY",[[[3,16],[5,16]],[[3,16],[5,16]],[[3,8],[5,8]]]),
      "boundary":("STOP_TRIANGLE_BOUNDARY",[[[0,1],[1,2]],[[1,4],[1,4]],[[1,4],[3,4]]]),
      "uncertain":("STOP_UNCERTAIN_TRIANGLE_MEMBERSHIP",[[[-1,4],[1,4]],[[1,4],[1,4]],[[1,2],[1,1]]]),
      "outside":("CPU_BOX_OUTSIDE_TRIANGLE_ON_PLANE_ONLY",[[[-1,2],[-1,4]],[[1,4],[1,4]],[[1,1],[5,4]]])}
    for source in saved:
        for mode,(expected,intervals) in expectations.items():
            budget=copy.deepcopy(zero)
            if mode=="tangent_box":budget[1]=budget[2]=[[-1,4],[1,4]]
            if mode=="boundary":budget[1]=[[-1,1],[1,1]]
            if mode=="uncertain":budget[1]=[[-2,1],[0,1]]
            if mode=="outside":budget[1]=[[-3,1],[-2,1]]
            p,t,d=source["input_point_words"],source["triangle_words"],source["direction_words"]
            result=m.audit_interior(p,t,d,budget)
            assert result["status"]==expected and result["barycentric_intervals"]==intervals
            records.append(dict(case=source["case"],mode=mode,
               saved_raw_stage_sha256=source["saved_raw_stage_sha256"],
               input_point_words=p,triangle_words=t,direction_words=d,
               declared_errors=budget,result=result))
    base=saved[0]
    oblique_p=[0x3f800000,0,0x3f800000,0,0x40000000,0]
    oblique_t=[0,0,0,0x40800000,0,0x40800000,0,0x40800000,0x40800000]
    controls=[]
    for kind in ("missing_budget","oblique_interior","oblique_uncertain_plane","lost_coordinate"):
        p=base["input_point_words"].copy();t=base["triangle_words"].copy();d=base["direction_words"].copy()
        budget=copy.deepcopy(zero)
        if kind=="missing_budget":budget=None
        if kind.startswith("oblique"):
            p=oblique_p.copy();t=oblique_t.copy();d=[0,0,0xbf800000]
        if kind=="oblique_uncertain_plane":budget[0]=[[-1,4],[1,4]]
        if kind=="lost_coordinate":p[:2]=[0,0]
        result=m.audit_interior(p,t,d,budget)
        if kind=="oblique_interior":
            assert result["status"]==expectations["singleton"][0]
            assert result["barycentric_intervals"]==expectations["singleton"][1]
            assert result["gram_determinant"]==[768,1]
        else:assert result["status"]=="STOP_PLANE_PREREQUISITE" and result["barycentric_intervals"]is None
        controls.append(dict(kind=kind,input_point_words=p,triangle_words=t,direction_words=d,
                             declared_errors=budget,result=result))
    for r in records+controls:
        assert all(r["result"][flag]is False for flag in FLAGS)
        assert r["result"]["phase_error_bound"]is None
    bad=[]
    for value in (True,-1,1<<32,0x7f800000,0x80000000):
        p=base["input_point_words"].copy();p[0]=value;bad.append((p,base["triangle_words"],base["direction_words"],zero))
    bad.append(([],base["triangle_words"],base["direction_words"],zero))
    bad.append((base["input_point_words"],base["triangle_words"],[0,0,0],zero))
    for interval in ([[1,0],[0,1]],[[1,1],[0,1]],[[2,2],[2,1]]):
        budget=copy.deepcopy(zero);budget[0]=interval
        bad.append((base["input_point_words"],base["triangle_words"],base["direction_words"],budget))
    for args in bad:
        try:m.audit_interior(*args)
        except ValueError:pass
        else:raise AssertionError("malformed membership input admitted")
    before=copy.deepcopy((base["input_point_words"],base["triangle_words"],base["direction_words"],zero))
    first=m.audit_interior(*before);first["barycentric_affine"][0]["coefficients"][0][0]=99
    again=m.audit_interior(*before)
    assert again["barycentric_intervals"]==expectations["singleton"][1]
    assert before==(base["input_point_words"],base["triangle_words"],base["direction_words"],zero)
    return dict(status="PASS_CPU_DECLARED_BOX_INTERIOR_CONDITION_ONLY_NOT_NATIVE",
      context_pins=pins,records=records,controls=controls,selected_saved_points=3,
      stored_audits=19,successful_helper_calls_including_mutation=21,
      malformed_rejections=len(bad),mutation_isolation_checked=True,
      prior_zero_error_gate=parent["prior_zero_error_gate"],
      GPU_used=False,Bpy_used=False,RT_used=False,recomputed_intersections=0,
      old_producer_executions=0,original_scene_queries_replayed=0,
      full_costs="UNKNOWN_NOT_ZERO")
if __name__=="__main__":print(json.dumps(run(),sort_keys=True))
