"""Bounded integration tests on sealed HOST captures, not new scene producers."""
import copy,inspect,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmarks"/"capacity_audit"))
import oblique_phase_visibility_join_HOST_v1 as m

def main():
    e,pins=m.retained();runs=[];legacy=[];spy_counts=[];good={}
    def check(name,pc,vi,ledger=None,inp=None,out=None,q=None,model=None,origin=None):
        a=e["phases"][pc]
        if ledger is None:ledger=e["visibility"][vi]["result"]["visibility_rows"]
        if inp is None:inp=a["input"]
        if out is None:out=a["output"]
        request=m.selector(pc,vi,e)if q is None else q
        result=m._compare(m.MODEL if model is None else model,request,ledger,inp,out,m.ORIGIN if origin is None else origin,e)
        runs.append(dict(id=name,phase_case=pc,visibility_case=vi,request=request,ledger=ledger,
            input_hex=inp.hex()if type(inp)is bytes else None,output_hex=out.hex()if type(out)is bytes else None,
            model=m.MODEL if model is None else model,origin=m.ORIGIN if origin is None else origin,result=result))
        return result
    for pc,a in e["phases"].items():
        if a["input"]is None:
            r=check("parent_STOP:"+pc,pc,"oblique");assert r["status"]=="STOP" and r["reason"].startswith("phase_parent_STOP:")
        else:
            geo=e["geometries"][pc]["geometry"]
            candidates=[k for k,v in e["visibility"].items()if m.exact(v["scene"],geo["scene"])and m.exact(v["request"],geo["request"])and v["result"]["status"]!="STOP"]
            assert len(candidates)==1;vi=candidates[0];good[pc]=vi
            r=check("sealed:"+pc,pc,vi);assert r["status"]!="STOP" and (r["verified_phase_rows"],r["verified_visibility_rows"])==(3,8)
    validvis=[k for k,v in e["visibility"].items()if v["result"]["status"]!="STOP"]
    old_phase=m.rb._compare;old_vis=m.vc._validate
    calls=[]
    def phase_spy(*args):calls.append("phase");return old_phase(*args)
    def vis_spy(*args):calls.append("visibility");return old_vis(*args)
    m.rb._compare=phase_spy;m.vc._validate=vis_spy
    for pc,vi in good.items():
        a=e["phases"][pc]
        for other in validvis:
            if other==vi:continue
            calls.clear();r=check("cross_valid:"+pc+":"+other,pc,other)
            assert r["status"]=="STOP" and r["reason"]in("same_ORIGINAL_scene","same_literal_request") and calls==[]
            pp=old_phase(m.rb.MODEL,m.rb.selector(pc,e["phases"]),a["input"],a["output"],m.ORIGIN,e["phases"])
            vv=old_vis(m.vc.MODEL,m.vc.selector(other),e["visibility"][other]["result"]["visibility_rows"],e["visibility"])
            assert pp["status"]=="HOST_UNATTESTED_TOTAL_PHASE_MATCH" and vv["status"]=="HOST_UNATTESTED_VISIBILITY_LEDGER_MATCH"
            legacy.append(dict(phase_case=pc,visibility_case=other,phase_status=pp["status"],visibility_status=vv["status"],
                incorrect_AND_would_admit=True,joint_status=r["status"],joint_reason=r["reason"]))
    for vi,a in e["visibility"].items():
        if a["result"]["status"]=="STOP":
            calls.clear();r=check("visibility_parent_STOP:"+vi,"parent_oblique",vi)
            assert r["reason"].startswith("visibility_parent_STOP:") and calls==[]
    for pc,vi in good.items():
        ledger=e["visibility"][vi]["result"]["visibility_rows"]
        for label in("duplicate_S0_over_S1","missing","wrong_SOURCE","order","classification","extra_field"):
            bad=copy.deepcopy(ledger)
            if label=="duplicate_S0_over_S1":bad[4]=copy.deepcopy(bad[0])
            elif label=="missing":bad.pop()
            elif label=="wrong_SOURCE":bad[0]["source_id"]="S1"
            elif label=="order":bad.reverse()
            elif label=="classification":bad[0]["classification"]="FORGED_CLEAR"
            else:bad[0]["extra"]=0
            calls.clear();r=check("ledger:"+pc+":"+label,pc,vi,ledger=bad)
            assert r["status"]=="STOP" and r["reason"].startswith("visibility_ledger:") and calls==["visibility"]
            spy_counts.append(dict(id=runs[-1]["id"],phase_calls=0,visibility_calls=1))
        output=bytearray(e["phases"][pc]["output"]);bits=int.from_bytes(output[24:32],"little")
        output[24:32]=(bits+1).to_bytes(8,"little");calls.clear()
        r=check("within_cap_wrong_bits:"+pc,pc,vi,out=bytes(output))
        assert r["reason"]=="phase_readback:native_TOTAL_phase_bits" and all(x["fits"]for x in r["phase_diagnostics"]["diagnostics"])
        assert calls==["visibility","phase"]
    m.rb._compare=old_phase;m.vc._validate=old_vis
    path_controls=[]
    for label in("SOURCE_order","squared_certificate","endpoint"):
        altered=copy.deepcopy(e)
        paths=altered["visibility"]["oblique"]["parent_result"]["paths"]
        if label=="SOURCE_order":paths.reverse()
        elif label=="squared_certificate":paths[0]["segments"][0]["squared_BU2"]=[1,1]
        else:paths[0]["segments"][0]["to_BU"][0]=[0,1]
        a=e["phases"]["parent_oblique"];vi="oblique"
        result=m._compare(m.MODEL,m.selector("parent_oblique",vi,e),e["visibility"][vi]["result"]["visibility_rows"],a["input"],a["output"],m.ORIGIN,altered)
        assert result["reason"]=="same_SOURCE_paths_certificates" and result["status"]=="STOP"
        assert result["phase_diagnostics"]is None and result["visibility_diagnostics"]is None
        path_controls.append(dict(mutation=label,result=result))
    pc="parent_oblique";vi=good[pc];q=m.selector(pc,vi,e)
    for field in q:
        bad=copy.deepcopy(q);bad[field]="wrong"
        assert check("selector:"+field,pc,vi,q=bad)["status"]=="STOP"
    for parent,fields in(("phase_selector",list(q["phase_selector"])),("visibility_selector",list(q["visibility_selector"]))):
        for field in fields:
            bad=copy.deepcopy(q);bad[parent][field]="wrong"
            assert check("nested_selector:"+parent+":"+field,pc,vi,q=bad)["status"]=="STOP"
    assert check("selector:extra",pc,vi,q=dict(q,extra=True))["status"]=="STOP"
    for label,kwargs in(("wrong_model",dict(model="GPU")),("device_origin",dict(origin="GPU_NATIVE_READBACK"))):
        assert check(label,pc,vi,**kwargs)["status"]=="STOP"
    for side in("input","output"):
        a=e["phases"][pc];original=a[side]
        for label,packet in(("nonfinite",original[:16]+bytes.fromhex("010000000000f87f")+original[24:]),
            ("short",original[:-1]),("domain",original[:16]+(0x4270000000000001).to_bytes(8,"little")+original[24:])):
            r=check("bytes:"+side+":"+label,pc,vi,**{("inp"if side=="input"else "out"):packet})
            assert r["status"]=="STOP" and r["reason"].startswith("phase_readback:") and r["phase_diagnostics"]["decoded_components"]==0
    assert list(inspect.signature(m.compare).parameters)==["model","request","ledger","input_bytes","output_bytes","origin"]
    a=e["phases"][pc];ledger=e["visibility"][vi]["result"]["visibility_rows"]
    public=m.compare(m.MODEL,q,ledger,a["input"],a["output"],m.ORIGIN);assert public["status"]!="STOP"
    old=m.sealed
    def unavailable(*args):raise ValueError("simulated_missing_or_corrupt_receipt")
    m.sealed=unavailable
    missing=m.compare(m.MODEL,q,ledger,a["input"],a["output"],m.ORIGIN);m.sealed=old
    assert missing["reason"]=="evidence_integrity:simulated_missing_or_corrupt_receipt" and missing["status"]=="STOP"
    for x in runs:
        r=x["result"]
        assert not any(r[k]for k in("GPU_launch_allowed","GPU_executed","GPU_guard_certified","scene_authenticated","material_authenticated",
            "ledger_authenticated","device_egress_authenticated","fence_readback_authenticated","native_promotion_allowed","physical_field_certified"))
        assert (r["RN64_operations"],r["compiler_calls"],r["producer_replays"])==(0,0,0) and r["full_costs"]=="UNMEASURED_NOT_ZERO"
        if r["status"]=="STOP":
            assert r["rows"]==[] and r["verified_phase_rows"]==r["verified_visibility_rows"]==0
            assert all(r[k]is None for k in("joined_scene_sha256","joined_literal_sha256","joined_paths_sha256","output_sha256"))
    assert len(good)==11 and len(legacy)==55 and len(spy_counts)==66
    print(json.dumps(dict(status="PASS",test_groups=5,data=dict(runs=runs,legacy_wrong_AND_controls=legacy,
        visibility_first_spies=spy_counts,path_copy_controls=path_controls,public_match=public,missing_evidence_STOP=missing,
        good_mapping=good,unmatched_valid_visibility=[x for x in validvis if x not in good.values()],
        census=dict(runs=len(runs),matches=sum(x["result"]["status"]!="STOP"for x in runs),phase_parent_STOP=35,
            visibility_parent_STOP=38,cross_valid_STOP=55,ledger_STOP=66,within_cap_wrong_bits_STOP=11),
        compiler_calls=0,RN64_operations=0,producer_replays=0,GPU_executed=False,GPU_launch_allowed=False)),sort_keys=True))
if __name__=="__main__":main()
