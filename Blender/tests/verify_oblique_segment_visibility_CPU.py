"""Independent determinant oracle; reads captures/pins, never imports geometry producers."""
from pathlib import Path
from fractions import Fraction as F
import ast,base64,hashlib,json,zlib
ROOT=Path(__file__).resolve().parents[2]
RECEIPT=ROOT/"coordinacion/respuestas/PRECISION-OBLIQUE-SEGMENT-VISIBILITY-CPU-001-CODEX.json"
def sha(b):return hashlib.sha256(b).hexdigest()
def pair(x):return [x.numerator,x.denominator]
def vec(v):return tuple(F(*x)for x in v)
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def det(cols):
    a,b,c=cols
    return a[0]*(b[1]*c[2]-b[2]*c[1])-b[0]*(a[1]*c[2]-a[2]*c[1])+c[0]*(a[1]*b[2]-a[2]*b[1])
def cap(t):
    b=zlib.decompress(base64.b64decode(t["stdout_zlib_base64"],validate=True))
    assert t["rc"]==0 and t["timed_out"]is False and len(b)==t["stdout_bytes"]and sha(b)==t["stdout_sha256"]
    return json.loads(b)
def row_check(run,row):
    s=run["scene"];q=run["request"];r=run["parent_result"]
    source=int(row["source_id"][1]);j=row["segment"];tr=next(v for v in s["triangles"]if v["primitive_id"]==row["primitive_id"])
    seg=r["paths"][source]["segments"][j];o=vec(seg["from_BU"]);d=sub(vec(seg["to_BU"]),o)
    a,b,c=map(vec,tr["vertices_BU"]);e0=sub(b,a);e1=sub(c,a);rhs=sub(a,o)
    cols=[d,tuple(-v for v in e0),tuple(-v for v in e1)]
    denom=det(cols)
    if denom==0:
        # Matrix singular: the start lies in the triangle plane iff this scalar triple is zero.
        plane=det([e0,e1,rhs]);expected="COPLANAR_STOP"if plane==0 else"PARALLEL_DISJOINT"
        assert row["t"]is None and row["barycentric"]is None and row["classification"]==expected;return
    answer=[]
    for k in range(3):
        replaced=cols.copy();replaced[k]=rhs;answer.append(det(replaced)/denom)
    t,u,v=answer;assert row["t"]==pair(t)
    if t<0 or t>1:expected="OUTSIDE_SEGMENT";assert row["barycentric"]is None
    else:
        assert row["barycentric"]==[pair(1-u-v),pair(u),pair(v)]
        if u<0 or v<0 or u+v>1:expected="OUTSIDE_TRIANGLE"
        elif t==0 and j==1 and tr["primitive_id"]==q["root_primitive_id"]:expected="EXACT_PREVIOUS_ZERO"
        elif t==1 and tr["primitive_id"]==[q["root_primitive_id"],q["detector_primitive_id"]][j]:expected="EXPECTED_ENDPOINT"
        else:expected="UNEXPECTED_CONTACT_STOP"
    assert row["classification"]==expected,(run["id"],row,expected)
def main():
    receipt=json.loads(RECEIPT.read_bytes());pins=receipt["code_doc_sha256"]
    assert len(pins)==146 and all(sha((ROOT/p).read_bytes())==h for p,h in pins.items())
    parent=json.loads((ROOT/"coordinacion/respuestas/PRECISION-OBLIQUE-COMMON-DETECTOR-LENGTH-CPU-001-CODEX.json").read_bytes())
    old=cap(parent["test_run"])["data"];d=cap(receipt["test_run"]);runs=d["runs"]
    assert d["status"]=="PASS"and len(runs)==44 and len(d["selector_negatives"])==4
    assert len({v["id"]for v in runs})==44
    rows=0;passes=0;oldstop=0
    for run in runs:
        out=run["result"];id=run["id"]
        if id in old["inputs"]:
            assert run["scene"]==old["inputs"][id]["scene"]and run["request"]==old["inputs"][id]["request"]
            assert run["parent_result"]==old["results"][id]
            if old["results"][id]["status"]=="STOP":
                oldstop+=1;assert out["status"]=="STOP"and out["reason"]=="parent_STOP:"+str(old["results"][id]["reason"])
        for flag in("GPU_launch_allowed","GPU_executed","scene_authenticated","native_hit_coverage_certified","physical_field_certified","object_wide_skip"):
            assert out[flag]is False
        assert out["producer_replays"]==out["RN64_operations"]==out["compiler_calls"]==0
        assert out["epsilon_BU"]==[0,1]and out["promotion"]=="STOP"and out["full_costs"]=="UNMEASURED_NOT_ZERO"
        for row in out["diagnostics"]:row_check(run,row);rows+=1
        if out["status"]!="STOP":
            passes+=1;assert out["status"]=="CPU_DECLARED_ALL_SEGMENT_VISIBILITY_ONLY"
            assert out["SOURCE_segments_admitted"]==4 and out["visibility_rows"]==out["diagnostics"]
            assert len(out["visibility_rows"])==4*len(run["scene"]["triangles"])
            assert sum(v["classification"]=="EXACT_PREVIOUS_ZERO"for v in out["visibility_rows"])==2
            assert sum(v["classification"]=="EXPECTED_ENDPOINT"for v in out["visibility_rows"])==4
        else:assert out["visibility_rows"]==[]and out["SOURCE_segments_admitted"]==0
    assert oldstop==24 and passes==6
    expected={"oblique","direction_scaled","shared_ref1000","tiny_gap_2m60","oblique/outside_segment","tiny_gap_2m60/outside_segment"}
    assert {r["id"]for r in runs if r["result"]["status"]!="STOP"}==expected
    for base in("oblique","tiny_gap_2m60"):
        for kind in("interior_same_object","vertex_contact","other_zero_contact","duplicate_endpoint","coplanar"):
            run=next(r for r in runs if r["id"]==base+"/"+kind)
            assert len(run["scene"]["triangles"])==3
            assert run["scene"]["triangles"][2]["object_id"]==old["inputs"][base]["scene"]["triangles"][1]["object_id"]
            assert run["result"]["status"]=="STOP"
            reason="coplanar_ambiguity"if kind=="coplanar"else"unexpected_segment_contact"
            assert run["result"]["reason"]==reason
            if kind=="interior_same_object":
                last=run["result"]["diagnostics"][-1]
                assert last["source_id"]=="S0"and last["segment"]==0 and last["t"]==[1,3]
        tiny=next(r for r in runs if r["id"]=="tiny_gap_2m60")
        assert tiny["scene"]["triangles"][1]["vertices_BU"][0][0]==[1,2**60]
    for n in d["selector_negatives"]:assert n["result"]["status"]=="STOP"and n["result"]["visibility_rows"]==[]
    core=ast.parse((ROOT/"Blender/benchmarks/capacity_audit/oblique_segment_visibility_CPU_v1.py").read_text(encoding="utf-8"))
    public=next(n for n in core.body if isinstance(n,ast.FunctionDef)and n.name=="audit")
    assert [a.arg for a in public.args.args]==["model","request"]
    assert any(isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=="load_evidence"for n in ast.walk(public))
    print(json.dumps(dict(status="PASS",runs=44,admitted=6,STOP=38,selector_STOP=4,sealed_parent_STOP=24,
        independent_determinant_rows=rows,pins=146,producer_replays=0,RN64_operations=0,GPU_launch_allowed=False)))
if __name__=="__main__":main()
