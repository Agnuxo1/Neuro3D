"""Independent binary64 rational decoder, rounding-cell and retained-receipt oracle.
Never imports producer, float codec, shader, geometry or parent tests.
"""
import base64,hashlib,json,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
ID="PRECISION-OBLIQUE-CYCLES-PAIR64-CPU-001"
MODEL="precision-oblique-cycles-pair64-CPU-v1"
REP="OBLIQUE_GEOMETRIC_CYCLES_PAIR64_CPU_NOT_GPU_ABI"
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-COMMON-DETECTOR-LENGTH-CPU-001-CODEX.json"
PSHA="139cb34a315f476fa026bb346086a3a59d7c22241932ca3f4c291a501f4ca47e"
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode())
def fraction(p):return F(*p)
def decoded(w):
    e=(w>>52)&2047;m=w&((1<<52)-1);assert e!=2047
    value=F(m,2**1074) if e==0 else F((1<<52)+m)*F(2)**(e-1075)
    return -value if w>>63 else value
def node(n,require_RN=True):
    hx=n["word_le_hex"];assert type(hx)is str and len(hx)==16 and bytes.fromhex(hx).hex()==hx
    w=int.from_bytes(bytes.fromhex(hx),"little");y=decoded(w);x=fraction(n["input"])
    assert fraction(n["decoded"])==y and fraction(n["error"])==abs(y-x)
    if require_RN:
        if y==0:
            previous=decoded(0x8000000000000001);following=decoded(1)
            assert bool(w>>63)==(x<0) or x==0
        else:
            previous=decoded(w+1 if w>>63 else w-1)
            following=decoded(w-1 if w>>63 else w+1)
        lower=(previous+y)/2;upper=(y+following)/2
        assert lower<=x<=upper
        if x==lower or x==upper:assert w%2==0
    return y
def row(r,require_RN=True):
    a,b=[fraction(p) for p in r["interval"]];mid=(a+b)/2;radius=(b-a)/2
    assert a<=b and fraction(r["midpoint"])==mid and fraction(r["interval_radius"])==radius
    assert fraction(r["hi"]["input"])==mid;h=node(r["hi"],require_RN)
    assert fraction(r["exact_residual"])==mid-h and fraction(r["lo"]["input"])==mid-h
    l=node(r["lo"],require_RN);y=h+l;err=abs(y-mid)
    assert fraction(r["pair_value"])==y and fraction(r["pair_rounding_error"])==err==fraction(r["lo"]["error"])
    bound=max(abs(y-a),abs(y-b));assert bound==radius+err==fraction(r["pair_error_bound_cycles"])
    assert fraction(r["pair_error_bound_rad"])==8*bound
    assert fraction(r["single_word_error_bound_rad"])==8*max(abs(h-a),abs(h-b)) and r["RN64_casts"]==2
    return y,err
def unpack(t,tests):
    assert t["rc"]==0 and t["timed_out"]is False and t["threads"]==t["affinity_mask"]==1
    assert t["hard_child_timeout_seconds"]==60
    z=zlib.decompressobj();raw=z.decompress(base64.b64decode(t["stdout_zlib_base64"],validate=True),1024*1024+1)
    assert len(raw)<=1024*1024 and z.eof and not z.unused_data and not z.unconsumed_tail
    assert len(raw)==t["stdout_bytes"] and sha(raw)==t["stdout_sha256"]
    v=json.loads(raw);assert v["status"]=="PASS" and v["tests"]==tests;return v["data"]
def eligible(i,parent):
    q=i["selector"]
    if type(i["model"])is not str or i["model"]!=MODEL:return False
    if type(q)is not dict or set(q)!={"case","parent_result_sha256","original_scene_sha256","literal_request_sha256","representation"}:return False
    if not all(type(v)is str for v in q.values()) or q["representation"]!=REP:return False
    if q["case"]not in parent["results"]:return False
    old=parent["results"][q["case"]];inp=parent["inputs"][q["case"]]
    return (q["parent_result_sha256"]==digest(old) and q["original_scene_sha256"]==digest(inp["scene"])
        and q["literal_request_sha256"]==digest(inp["request"]) and old["status"]=="CPU_OBLIQUE_GEOMETRIC_LENGTH_INTERVAL_ONLY")

def main():
    r=json.loads((ROOT/("coordinacion/respuestas/"+ID+"-CODEX.json")).read_bytes())
    assert r["id"]==ID and r["model"]==MODEL and r["status"]=="CPU_GEOMETRIC_PAIR64_ONLY"
    pins=r["code_doc_sha256"];assert len(pins)==88
    for p,h in pins.items():assert sha((ROOT/p).read_bytes())==h,p
    raw=(ROOT/PARENT).read_bytes();assert sha(raw)==PSHA;pr=json.loads(raw)
    assert len(pr["code_doc_sha256"])==83 and all(pins[p]==h for p,h in pr["code_doc_sha256"].items())
    parent=unpack(pr["test_run"],6);d=unpack(r["test_run"],6)
    assert len(d["inputs"])==len(d["results"])==37
    good=bad=0;rn=0
    flags=("GPU_executed","native_promotion_allowed","physical_scene_authenticated","native_hit_coverage_certified",
           "length_reference_phase_bound_certified","mirror_material_certified","full_field_certified",
           "coherent_field_admission_allowed","interference_phase_certified")
    for name,i in d["inputs"].items():
        v=d["results"][name];ok=eligible(i,parent)
        assert all(v[k]is False for k in flags)
        assert v["source_phase"]is v["mirror_phase"]is v["amplitude"]is v["field"]is v["power"]is None
        assert v["new_geometry_queries"]==v["new_sqrt_calls"]==v["frozen_producer_replays"]==0
        assert v["full_costs"]=="UNMEASURED_NOT_ZERO" and v["representation"]==REP
        if not ok:
            bad+=1;assert v["status"]=="STOP" and v["rows"]==[] and v["RN64_casts"]==0
            continue
        good+=1;rn+=v["RN64_casts"]
        assert v["status"]=="CPU_OBLIQUE_PAIR64_GEOMETRIC_TRANSPORT_ONLY" and v["rows"]==v["diagnostics"] and len(v["rows"])==3
        q=i["selector"];case=q["case"];old=parent["results"][case];inp=parent["inputs"][case]
        bounds=[p["geometric_cycles_interval"] for p in old["paths"]]+[old["relative_diagnostic"]["geometric_cycles_interval"]]
        caps=inp["request"]["source_width_caps_rad"]+[inp["request"]["relative_width_cap_rad"]]
        vals=[];errs=[]
        for j,e in enumerate(v["rows"]):
            y,err=row(e);vals.append(y);errs.append(err)
            assert e["interval"]==bounds[j] and e["literal_cap_rad"]==caps[j]
            assert e["record_id"]==("S0","S1","S0-minus-S1")[j] and e["branch_id"]==("S0/mirror","S1/mirror","relative")[j]
            assert e["original_scene_sha256"]==q["original_scene_sha256"] and e["literal_request_sha256"]==q["literal_request_sha256"]
            assert e["pair_fits"]is True and fraction(e["pair_error_bound_rad"])<=fraction(caps[j])
            assert e["single_word_fits"]==(fraction(e["single_word_error_bound_rad"])<=fraction(caps[j]))
        assert fraction(v["closure_error_cycles"])==abs(vals[0]-vals[1]-vals[2])<=sum(errs)==fraction(v["closure_rounding_budget_cycles"])
        assert v["single_word_ALL_caps_fit"]==all(p["single_word_fits"] for p in v["rows"])
        assert v["parent_receipt_sha256"]==PSHA and v["request_sha256"]==digest(q) and v["RN64_casts"]==6
    assert (good,bad,rn)==(4,33,24)
    assert all("parent_"+case in d["results"] for case in parent["results"])
    for e in d["synthetic"].values():row(e)
    assert len(d["synthetic"])==6
    assert d["controls"]["single_word_scene_ALL_caps"]==dict(oblique=False,direction_scaled=False,shared_ref1000=False,tiny_gap_2m60=True)
    c=d["controls"]["low_loss_result"];assert c["status"]=="STOP" and c["rows"]==[] and c["RN64_casts"]==6
    # Fault-injected zero lows are NOT represented as successful RN nodes.
    for e in c["diagnostics"]:row(e,require_RN=False)
    assert not all(e["pair_fits"] for e in c["diagnostics"])
    assert d["controls"]["parent_changed_STOP"]is True and d["controls"]["read_denied_STOP"]is True
    print(json.dumps({"status":"PASS","pins":88,"requests":37,"CPU_partial":4,"STOP":33,"production_RN_nodes":24,
        "synthetic_RN_nodes":12,"fault_ledger_nodes":6,"fault_real_RN_nodes":3,"rows_emitted":12,
        "GPU_executed":False,"frozen_geometry_replays":0},sort_keys=True))
if __name__=="__main__":main()
