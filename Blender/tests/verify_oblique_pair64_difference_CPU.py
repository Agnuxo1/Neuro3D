"""Independent rational binary64 arithmetic-graph, RNE and scene-budget oracle."""
import base64,hashlib,json,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
ID="PRECISION-OBLIQUE-PAIR64-DIFFERENCE-CPU-001"
MODEL="precision-oblique-pair64-difference-CPU-v1"
REP="OBLIQUE_PAIR64_DIFFERENCE_CPU_NOT_GPU_ABI"
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-CYCLES-PAIR64-CPU-001-CODEX.json"
PSHA="af247e1dde579952adc02eddac33a31d2a19d5a51d009d397c89da95ab7a5748"
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode())
def f(p):return F(*p)
def integer(h):
    assert type(h)is str and len(h)==16 and bytes.fromhex(h).hex()==h
    return int.from_bytes(bytes.fromhex(h),"little")
def d(h):
    w=integer(h);e=(w>>52)&2047;m=w&((1<<52)-1);assert e!=2047
    y=F(m,2**1074) if e==0 else F((1<<52)+m)*F(2)**(e-1075)
    return -y if w>>63 else y
def hx(w):return w.to_bytes(8,"little").hex()
def neg(h):return hx(integer(h)^(1<<63))
def rne(h,x):
    w=integer(h);y=d(h)
    if y==0:previous=d(hx(0x8000000000000001));following=d(hx(1))
    else:previous=d(hx(w+1 if w>>63 else w-1));following=d(hx(w-1 if w>>63 else w+1))
    lower=(previous+y)/2;upper=(y+following)/2
    assert lower<=x<=upper
    if x==lower or x==upper:assert w%2==0
def node(n,fault=False):
    a=d(n["a"]);b=d(n["b"]);assert n["op"]in ("+","-")
    x=a+b if n["op"]=="+" else a-b
    assert f(n["error"])==abs(d(n["y"])-x)
    if fault:
        assert n["name"]=="h_e" and n["y"]==hx(0)
        rne(n["fault_original_y"],x);assert d(n["fault_original_y"])!=0
    else:rne(n["y"],x)
def graph(a,b,t,partial_fault=False):
    nodes=t["nodes"];eft=t["eft"];index=[0];ei=[0]
    def step(name,op,x,y):
        n=nodes[index[0]];index[0]+=1
        assert (n["name"],n["op"],n["a"],n["b"])==(name,op,x,y)
        node(n,partial_fault and name=="h_e");return n["y"]
    def ts(a,b,name):
        s=step(name+"_s","+",a,b);bb=step(name+"_bb","-",s,a)
        ab=step(name+"_ab","-",s,bb);db=step(name+"_db","-",b,bb)
        da=step(name+"_da","-",a,ab);e=step(name+"_e","+",da,db)
        z=eft[ei[0]];ei[0]+=1
        assert (z["name"],z["a"],z["b"],z["hi"],z["lo"])==(name,a,b,s,e)
        assert z["residual_exact"]==(d(s)+d(e)==d(a)+d(b))
        if not partial_fault:assert z["residual_exact"]is True
        return s,e
    s,e=ts(a[0],neg(b[0]),"h")
    if partial_fault:
        assert not eft[0]["residual_exact"] and len(nodes)==6 and len(eft)==1;return None
    t0,f0=ts(a[1],neg(b[1]),"l")
    e=step("e_add","+",e,t0);h,g=ts(s,e,"m")
    l=step("lo_add","+",g,f0);hi,lo=ts(h,l,"r")
    assert index[0]==len(nodes)==26 and ei[0]==len(eft)==4
    return hi,lo
def unpack(t):
    assert t["rc"]==0 and t["timed_out"]is False and t["threads"]==t["affinity_mask"]==1 and t["hard_child_timeout_seconds"]==60
    z=zlib.decompressobj();raw=z.decompress(base64.b64decode(t["stdout_zlib_base64"],validate=True),1024*1024+1)
    assert len(raw)<=1024*1024 and z.eof and not z.unused_data and not z.unconsumed_tail
    assert len(raw)==t["stdout_bytes"] and sha(raw)==t["stdout_sha256"]
    v=json.loads(raw);assert v["status"]=="PASS" and v["tests"]==6;return v["data"]
def eligible(i,parent):
    q=i["selector"]
    if type(i["model"])is not str or i["model"]!=MODEL:return False
    if type(q)is not dict or set(q)!={"case","parent_result_sha256","original_scene_sha256","literal_request_sha256","representation"}:return False
    if not all(type(v)is str for v in q.values()) or q["representation"]!=REP:return False
    if q["case"]not in parent["results"]:return False
    v=parent["results"][q["case"]]
    if q["parent_result_sha256"]!=digest(v) or v["status"]!="CPU_OBLIQUE_PAIR64_GEOMETRIC_TRANSPORT_ONLY":return False
    return all(s["original_scene_sha256"]==q["original_scene_sha256"] and s["literal_request_sha256"]==q["literal_request_sha256"] for s in v["rows"])
def budget(v,p,allow_fault=False):
    src=p["rows"][:2];ref=p["rows"][2]
    a,b=[tuple(s[k]["word_le_hex"] for k in ("hi","lo")) for s in src]
    hi,lo=graph(a,b,v["trace"]);e=v["diagnostics"][0]
    if allow_fault:
        assert e["hi_word"]==hi and e["lo_word"]==hx(0) and lo!=hx(0)
        assert v["status"]=="STOP" and v["reason"]=="arithmetic_output_identity" and v["rows"]==[]
    else:assert (e["hi_word"],e["lo_word"])==(hi,lo)
    y=d(e["hi_word"])+d(e["lo_word"]);values=[sum(d(w) for w in x) for x in (a,b)]
    bounds=[tuple(f(x) for x in s["interval"]) for s in p["rows"]]
    assert bounds[2]==(bounds[0][0]-bounds[1][1],bounds[0][1]-bounds[1][0])
    source_errors=sum(abs(x-(aa+bb)/2) for x,(aa,bb) in zip(values,bounds[:2]))
    radius=(bounds[2][1]-bounds[2][0])/2;target=values[0]-values[1];err=abs(y-target)
    conservative=8*(radius+source_errors+err)
    direct=8*max(abs(y-bounds[2][0]),abs(y-bounds[2][1]))
    assert direct<=conservative==f(e["conservative_error_bound_rad"]) and direct==f(e["direct_error_bound_rad"])
    assert f(e["pair_value"])==y and f(e["input_pair_difference"])==target
    assert f(e["arithmetic_error_cycles"])==err and f(e["source_rounding_budget_cycles"])==source_errors
    assert f(e["interval_radius_cycles"])==radius and e["literal_cap_rad"]==ref["literal_cap_rad"]
    assert e["parent_relative_CONTROL_ONLY"]==ref and e["record_id"]=="S0-minus-S1" and e["branch_id"]=="relative"
    assert e["original_scene_sha256"]==ref["original_scene_sha256"] and e["literal_request_sha256"]==ref["literal_request_sha256"]
    for x,(aa,bb),s in zip(values,bounds[:2],src):assert 8*max(abs(x-aa),abs(x-bb))<=f(s["literal_cap_rad"])
    if not allow_fault:
        assert conservative<=f(ref["literal_cap_rad"]) and v["rows"]==src+[e] and v["RN64_operations"]==26
def main():
    raw=(ROOT/PARENT).read_bytes();assert sha(raw)==PSHA;pr=json.loads(raw);parent=unpack(pr["test_run"])
    r=json.loads((ROOT/("coordinacion/respuestas/"+ID+"-CODEX.json")).read_bytes())
    assert r["id"]==ID and r["model"]==MODEL and r["status"]=="CPU_RELATIVE_ARITHMETIC_ONLY"
    pins=r["code_doc_sha256"];assert len(pins)==93 and len(pr["code_doc_sha256"])==88
    assert all(pins[p]==h for p,h in pr["code_doc_sha256"].items())
    for p,h in pins.items():assert sha((ROOT/p).read_bytes())==h,p
    data=unpack(r["test_run"]);assert len(data["results"])==len(data["inputs"])==46
    good=bad=0
    flags=("GPU_executed","native_promotion_allowed","physical_scene_authenticated","native_hit_coverage_certified",
        "length_reference_phase_bound_certified","mirror_material_certified","full_field_certified","coherent_field_admission_allowed","interference_phase_certified")
    for name,i in data["inputs"].items():
        v=data["results"][name];ok=eligible(i,parent)
        assert all(v[k]is False for k in flags) and v["representation"]==REP
        assert all(v[k]is None for k in ("source_phase","mirror_phase","amplitude","field","power"))
        assert v["new_geometry_queries"]==v["new_sqrt_calls"]==v["frozen_producer_replays"]==0
        if not ok:
            bad+=1;assert v["status"]=="STOP" and v["rows"]==[] and v["RN64_operations"]==0;continue
        good+=1;assert v["status"]=="CPU_OBLIQUE_PAIR64_DIFFERENCE_ONLY"
        budget(v,parent["results"][i["selector"]["case"]])
        assert v["request_sha256"]==digest(i["selector"]) and v["parent_receipt_sha256"]==PSHA
    assert (good,bad)==(4,42)
    assert set(parent["results"]).issubset(data["results"])
    for name,c in data["controls"].items():
        if name.startswith("parent_") and type(c)is dict and "trace"in c:
            p=parent["results"][name];src=p["rows"][:2];ns=c["trace"]["nodes"];assert len(ns)==3
            for n in ns:node(n)
            assert (ns[0]["a"],ns[0]["b"])==tuple(src[0][k]["word_le_hex"] for k in ("hi","lo"))
            assert (ns[1]["a"],ns[1]["b"])==tuple(src[1][k]["word_le_hex"] for k in ("hi","lo"))
            assert (ns[2]["a"],ns[2]["b"],ns[2]["op"])==(ns[0]["y"],ns[1]["y"],"-")
            aa,bb=[f(x) for x in p["rows"][2]["interval"]];y=d(c["value"]);assert c["value"]==ns[2]["y"]
            bound=8*max(abs(y-aa),abs(y-bb));assert f(c["bound_rad"])==bound and c["cap_rad"]==p["rows"][2]["literal_cap_rad"]
            assert c["fits"]==(bound<=f(c["cap_rad"]))
    assert len(data["synthetic"])==5
    for e in data["synthetic"].values():
        assert graph(e["a"],e["b"],e["trace"])==(e["hi"],e["lo"])
        assert d(e["hi"])+d(e["lo"])==sum(map(d,e["a"]))-sum(map(d,e["b"]))
    budget(data["controls"]["output_low_loss"],parent["results"]["parent_oblique"],allow_fault=True)
    graph([hx(0x3ff0000000000000),hx(0)],[hx(0xbc70000000000000),hx(0)],data["controls"]["corrupt_EFT_trace"],partial_fault=True)
    assert data["controls"]["parent_identity_STOP"]is data["controls"]["read_denied_STOP"]is True
    print(json.dumps(dict(status="PASS",pins=93,requests=46,CPU_partial=good,STOP=bad,production_RN_operations=104,
        synthetic_RN_operations=130,collapsed_control_RN_operations=12,output_fault_RN_operations=26,
        EFT_fault_actual_RN_operations=6,fabricated_EFT_word=1,GPU_executed=False,frozen_replays=0),sort_keys=True))
if __name__=="__main__":main()
