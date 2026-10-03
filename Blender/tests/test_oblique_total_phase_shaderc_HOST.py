"""Bounded CPU-only TOTALphase compile/topology/prefix and selector controls."""
import base64,copy,inspect,json,sys,zlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmarks"/"capacity_audit"))
import oblique_total_phase_shaderc_HOST_v1 as m
def main():
    report=m.run_suite()
    if report["status"]!="HOST_COMPILE_TOPOLOGY_PREFIX_ONLY":
        print(json.dumps(dict(status="STOP",data=report),sort_keys=True));raise SystemExit(1)
    data,_=m.retained();q=m.selector("parent_oblique",data);mutations=[]
    for field in q:
        bad=copy.deepcopy(q);bad[field]="wrong"
        result=m._prepare(m.MODEL,bad,data);assert result["status"]=="STOP";mutations.append(dict(field=field,result=result))
    bad=dict(q,extra=True);result=m._prepare(m.MODEL,bad,data);assert result["status"]=="STOP";mutations.append(dict(field="extra",result=result))
    assert list(inspect.signature(m.prepare).parameters)==["model","request"]
    result=m._prepare("not-opt-in",q,data);assert result["status"]=="STOP"
    good=sum(x["result"]["status"]=="HOST_PREPARED_UNATTESTED"for x in report["preparations"])
    assert good==11 and len(report["preparations"])==46 and len(report["prefix"])==78
    assert len(report["valid_compile"]["inspection"]["graph"]["nodes"])==130
    assert all(x["matched_edges"]==130 for x in report["traces"].values())
    assert not report["GPU_launch_allowed"] and report["new_RN_operations"]==0
    report["selector_mutations"]=mutations;report["wrong_model"]=result
    print(json.dumps(dict(status="PASS",test_groups=3,prepared=11,parent_STOP=35,prefix_scenarios=78,
        traces=11,edges_per_trace=130,compiler_calls=2,GPU_executed=False,data=report),sort_keys=True))
if __name__=="__main__":main()
