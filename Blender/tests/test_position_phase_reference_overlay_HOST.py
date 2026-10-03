"""Four independent endpoint terms, cumulative budget and incompatible old scene regression."""
import copy,inspect,json,sys
from pathlib import Path
from fractions import Fraction as F
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmarks"/"capacity_audit"))
import position_phase_reference_overlay_HOST_v1 as m
def main():
    e,pins=m.retained();runs=[]
    def run(ID,record,p,q=None,model=m.MODEL):
        q=m.selector(record,e,p)if q is None else q
        r=m._audit(model,q,p,e);runs.append(dict(id=ID,record_id=record,request=q,packet=p,model=model,result=r));return r
    admitted=[]
    for record,x in e.items():
        p=m.packet(record,e);r=run("parent:"+record,record,p)
        positive=x["result"]["geometric_normalization_budget_conditional"]and p["source_context"]is not None
        assert r["reference_overlay_conditional"]is positive,(record,r)
        if positive:admitted.append(record);assert r["rows"][0]["error_rad_upper"]==x["result"]["error_rad_upper"]
    assert len(admitted)==13
    for record in admitted:
        for label,rad,positive in (("offsets",F(0),True),("four_radii_under",F(1,640000),True),("each_under_total_over",F(1,160000),False),("all_cap_no_geometric_slack",F(1,320000),False)):
            p=m.packet(record,e);means=[F(1,7),F(1,5),F(1,3),F(1,2)]if label=="offsets"else [F(0)]*4
            for term,mean in zip(p["components"],means):term["phase_interval_turns"]=[m.pair(mean-rad),m.pair(mean+rad)]
            r=run(label+":"+record,record,p);assert r["reference_overlay_conditional"]is positive,(label,record,r)
            if not positive:assert r["reason"]=="cumulative_reference_phase_budget_exhausted"and r["diagnostics"][0]["all_terms_individually_fit"]
            if label=="offsets":
                d=r["rows"][0];v=F(*e[record]["result"]["rows"][0]["decoded_output_exact_HOST"])
                assert F(*d["nominal_contrast_turns"])==v+F(1,7)-F(1,5)+F(1,3)-F(1,2)
    record=admitted[0];good=m.packet(record,e);bad=[]
    p=copy.deepcopy(good);p["extra"]=True;bad.append(("extra",p))
    p=copy.deepcopy(good);p["components"].pop();bad.append(("missing_term",p))
    p=copy.deepcopy(good);p["components"][1]=copy.deepcopy(p["components"][0]);bad.append(("duplicate",p))
    p=copy.deepcopy(good);p["components"].reverse();bad.append(("reordered",p))
    for label,key,val in (("context","source_context",{"provenance":"SEALED","synthetic_scene_sha256":"wrong"}),("geometry","original_geometry_sha256","wrong"),("reference","reference_point",2),("units","units",dict(phase="rad",cap="rad")),("auth","authentication","AUTHENTICATED"),("cap","cap_rad",[1,1000])):
        p=copy.deepcopy(good);p[key]=val;bad.append((label,p))
    p=copy.deepcopy(good);p["components"][0]["phase_interval_turns"]=[[True,1],[1,1]];bad.append(("bool_rational",p))
    p=copy.deepcopy(good);p["components"][0]["phase_interval_turns"]=[[0,1],[1,2**128]];bad.append(("rational_domain",p))
    oldpath="coordinacion/respuestas/PRECISION-OBLIQUE-SOURCE-MATERIAL-INTERVAL-HOST-001-CODEX.json"
    raw=(m.ROOT/oldpath).read_bytes();assert m.sha(raw)==pins[oldpath]
    old=m.c.capture(json.loads(raw)["test_run"])["data"]["runs"][0]["request"]
    p=copy.deepcopy(good);p["source_context"]=dict(provenance="CPU_SYNTHETIC_ONLY_NOT_SEALED_SCENE",synthetic_scene_sha256=old["original_scene_sha256"]);bad.append(("old_scene_crossjoin",p))
    for label,p in bad:assert run("packet:"+label,record,p)["status"]=="STOP"
    q=m.selector(record,e,good)
    for k in q:
        b=dict(q);b[k]="wrong";assert run("selector:"+k,record,good,b)["status"]=="STOP"
    for label,b in (("extra",dict(q,extra=True)),("missing",{k:v for k,v in q.items()if k!="intent"}),("bool",dict(q,representation=True))):assert run("selector:"+label,record,good,b)["status"]=="STOP"
    assert run("wrong_model",record,good,q,"GPU")["reason"]=="explicit_model"
    public=m.audit(m.MODEL,q,good);assert public==runs[0]["result"]
    saved=m.retained
    def absent():raise ValueError("simulated_missing_receipt")
    m.retained=absent;missing=m.audit(m.MODEL,q,good);m.retained=saved;assert missing["reason"]=="evidence_integrity:simulated_missing_receipt"
    flags=("GPU_launch_allowed","GPU_executed","CPU_native_executed","CPU_binary64_conversion_executed","scene_authenticated","uncertainty_authenticated","material_authenticated","wavelength_authenticated","total_phase_certified","full_visibility_certified","phase_certified","physical_field_certified","optical_reference_certified","correlation_assumed","shared_phase_cancellation_assumed","periodic_wrapping_used")
    for x in runs+[dict(result=public),dict(result=missing)]:
        r=x["result"];assert all(r[k]is False for k in flags)
        assert r["root_calls"]==r["producer_replays"]==r["compiler_calls"]==r["RN64_conversions"]==r["RN64_operations"]==0 and r["promotion"]=="STOP"and r["full_costs"]=="UNMEASURED_NOT_ZERO"
        if r["status"]=="STOP":assert r["rows"]==[]and not r["reference_overlay_conditional"]
    assert list(inspect.signature(m.audit).parameters)==["model","request","declared_overlay"]
    assert len(runs)==336 and sum(x["result"]["reference_overlay_conditional"]for x in runs)==39
    print(json.dumps(dict(status="PASS",data=dict(runs=runs,public=public,missing=missing,pins=len(pins),old_phase_request=old,
        census=dict(main=336,HOST_contrasts=39,STOP=297,parent_records=258,parent_STOP=241,unbound_helpers=4,
                    scene_scoped_synthetic_parents=13,derived=52,derived_under=26,derived_exhausted=26,packet_controls=13,selector_model=13),
        root_calls=0,producer_replays=0,GPU_executed=False,RN64_operations=0)),sort_keys=True))
if __name__=="__main__":main()
