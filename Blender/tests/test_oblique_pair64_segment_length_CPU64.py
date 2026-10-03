"""Pure bit/rational oracle for native square/root length; no old producer replay."""
from pathlib import Path
from fractions import Fraction as F
import json,hashlib,copy,runpy,itertools,struct
ROOT=Path(__file__).resolve().parents[2]
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-PAIR64-INTERVAL-CPU-001-CODEX.json"
PSHA="bf34de7e81a004bf602437ab260e88060f7d36f899c5862bcd3c1d652f1bd354"
MODEL="oblique-pair64-segment-length-CPU-v1"
POLICY="DISJOINT_ONLY_ALL_RADII_NATIVE_SQUARE_SQRT_OUTWARD"
legacy=runpy.run_path(str(ROOT/"Blender/tests/test_oblique_finite_interval_CPU64.py"))
frac,bits,neighbor,verify_round=map(legacy.get,("fraction","bits","neighbor","verify_round"))
upstream=runpy.run_path(str(ROOT/"Blender/tests/test_oblique_pair64_interval_consumer_CPU64.py"))
digest,pair,capture=map(upstream.get,("digest","pair","capture"))

def retained():
    raw=(ROOT/PARENT).read_bytes();assert len(raw)==124987 and hashlib.sha256(raw).hexdigest()==PSHA
    r=json.loads(raw);assert len(r["code_doc_sha256"])==264
    pins=dict(r["code_doc_sha256"]);pins[PARENT]=PSHA
    for p,h in pins.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    assert capture(r["independent_pre"])["status"]=="PASS"
    d=capture(r["test_run"])["evidence"]
    e={x["id"]:x for x in d["records"]};assert len(e)==16
    return r,e,pins,d

def selector(k,e):
    x=e[k]
    return dict(backend=MODEL,policy=POLICY,record_id=k,parent_receipt_sha256=PSHA,
        parent_record_sha256=digest(x),upstream_request_sha256=digest(x["request"]),
        frame_sha256=digest(x["result"]["frame"]),output_packet_sha256=x["request"]["output_packet_sha256"])

def scope(r):
    assert r["backend"]==MODEL and r["promotion"]=="STOP_PHYSICAL_PHASE_GPU"
    assert r["scope"]=="DECLARED_STRAIGHT_SOURCE0_DETECTOR0_LENGTH_NOT_OPTICAL_REFERENCE"
    assert r["parent_costs"]=="RETAINED_NONZERO_NOT_REPLAYED_NOT_END_TO_END_MEASUREMENT"
    assert r["new_transport_graph_calls"]==r["new_predicate_calls"]==r["retained_suite_replays"]==0
    assert r["full_costs"]=="UNKNOWN_NOT_ZERO"
    for k in ("EPS_used","FMA_used","source_uncertainty_cancelled","physical_visibility_certified","scene_authenticated",
        "optical_length_certified","optical_reference_certified","phase_certified","GPU_used"):assert r[k]is False

def verify_sqrt(z):
    assert z["op"]=="sqrt"and z["status"]=="PASS"and z["reason"]is None
    assert z["direction"]in ("lo","hi");s,r=frac(z["radicand_word"]),frac(z["RN_word"])
    assert s>=0 and r>=0 and(r!=0 or s==0)
    calls=0
    if s:
        nw=[neighbor(z["RN_word"],d)for d in ("lo","hi")]
        lo=((frac(nw[0])+r)/2)**2;hi=((frac(nw[1])+r)/2)**2
        assert z["neighbor_words"]==nw and z["midpoint_squares"]==[pair(lo),pair(hi)]
        assert lo<=s<=hi and(bits(z["RN_word"])%2==0 or s not in (lo,hi));calls=2
    else:assert r==0 and z["neighbor_words"]is None and z["midpoint_squares"]is None
    widen=(z["direction"]=="lo"and r*r>s)or(z["direction"]=="hi"and r*r<s)
    expected=neighbor(z["RN_word"],z["direction"])if widen else z["RN_word"]
    assert z["nextafter"]==widen and z["output_word"]==expected
    out=frac(expected);assert out>=0
    assert out*out<=s if z["direction"]=="lo"else out*out>=s
    return expected,calls+int(widen)

def cost(native,casts,calls,roots,theorems):
    return dict(native_arithmetic=native,endpoint_casts=casts,nextafter_calls=calls,sign_flips=0,
        exact_audit_fraction_operations="UNMEASURED_NOT_ZERO",total_cost="UNKNOWN_NOT_ZERO",
        native_sqrt=roots,zero_square_theorems=theorems)

def verify_record(row,x):
    q,r=row["request"],row["result"];scope(r)
    assert r["parent_record_sha256"]==digest(x)and r["parent_receipt_sha256"]==PSHA
    assert r["request_sha256"]==digest(q)and r["upstream_status"]==x["result"]["status"]and r["upstream_reason"]==x["result"]["reason"]
    if x["result"]["status"]!="CPU64_DECLARED_BOX_DISJOINT":
        assert r["status"]=="STOP_UPSTREAM"and r["reason"]=="non_disjoint_parent_not_rescued"
        assert r["scene"]is None and r["trace"]is None and r["ledger"]==r["sqrt_ledger"]==[]
        assert r["packet_bytes"]==r["word_decodes"]==r["exact_pair_decodes"]==0
        assert r["CPU_binary64_executed"]is False and r["costs"]==cost(0,0,0,0,0)
        return dict(native=0,casts=0,roots=0,nextafter=0,corners=0)
    assert r["status"]=="CPU64_DECLARED_SEGMENT_LENGTH_ONLY"and r["reason"]=="native_squared_root_enclosure"
    f=x["result"]["frame"];s=f["scene"]
    assert r["scene"]==s and r["scene_query"]==f["scene_query"]and r["frame_sha256"]==digest(f)
    assert r["decode_ledger"]==f["decode_ledger"]and r["CPU_binary64_executed"]is True
    assert r["packet_bytes"]==240 and r["word_decodes"]==30 and r["exact_pair_decodes"]==15
    text=x["request"]["output_packet_hex"];assert len(text)==480 and hashlib.sha256(bytes.fromhex(text)).hexdigest()==q["output_packet_sha256"]
    for i,d in enumerate(r["decode_ledger"]):
        n,j=("origin","detector","A","B","C")[i//3],i%3
        assert d==dict(point=n,axis=j,hi_word=text[32*i:32*i+16],lo_word=text[32*i+16:32*i+32],
            decoded=pair(frac(text[32*i:32*i+16])+frac(text[32*i+16:32*i+32])),radius=s["points"][n]["radius"][j])
        assert d["decoded"]==s["points"][n]["nominal"][j]
    ledger=r["ledger"];cursor=calls=0
    def take(op,exact,direction,operands):
        nonlocal cursor,calls
        z=ledger[cursor];assert z["index"]==cursor and z["op"]==op and z["exact"]==pair(exact)
        assert z["direction"]==direction and z["operands"]==operands
        _,c=verify_round(z);calls+=c;cursor+=1;return z["output_word"]
    actual={}
    exact_boxes={}
    for n in ("origin","detector"):
        actual[n]=[];exact_boxes[n]=[]
        for nom,rad in zip(s["points"][n]["nominal"],s["points"][n]["radius"]):
            v,b=F(*nom),F(*rad);exact_boxes[n].append((v-b,v+b))
            actual[n].append((take("cast",v-b,"lo",[]),take("cast",v+b,"hi",[])))
    def scalar(a,b,op,d):
        x,y=frac(a),frac(b);ex=x-y if op=="sub"else x+y if op=="add"else x*y
        return take(op,ex,d,[a,b])
    def add(a,b):return scalar(a[0],b[0],"add","lo"),scalar(a[1],b[1],"add","hi")
    delta=[(scalar(b[0],a[1],"sub","lo"),scalar(b[1],a[0],"sub","hi"))for a,b in zip(actual["origin"],actual["detector"])]
    squares=[];theorems=0
    for iv in delta:
        lo=[scalar(w,w,"mul","lo")for w in iv];hi=[scalar(w,w,"mul","hi")for w in iv]
        crossing=frac(iv[0])<=0<=frac(iv[1]);theorems+=int(crossing)
        squares.append(("0000000000000000"if crossing else min(lo,key=frac),max(hi,key=frac)))
    squared=add(add(squares[0],squares[1]),squares[2]);assert len(ledger)==cursor==34
    roots=r["sqrt_ledger"];assert len(roots)==2
    length=[]
    for i,d in enumerate(("lo","hi")):
        z=roots[i];assert z["index"]==i and z["direction"]==d and z["radicand_word"]==squared[i]
        w,c=verify_sqrt(z);calls+=c;length.append(w)
    assert r["trace"]==dict(input_boxes={n:[list(v)for v in vs]for n,vs in actual.items()},
        delta=[list(v)for v in delta],squares=[list(v)for v in squares],squared=list(squared),length=length)
    # Analytic continuous box extrema, not only corner sampling.
    exact_delta=[(b[0]-a[1],b[1]-a[0])for a,b in zip(exact_boxes["origin"],exact_boxes["detector"])]
    def square_bounds(a,b):return (F(0)if a<=0<=b else min(a*a,b*b),max(a*a,b*b))
    exact_squares=[square_bounds(*iv)for iv in exact_delta]
    sl,sh=map(sum,zip(*exact_squares));low,high=map(frac,length)
    assert 0<=low and low*low<=sl<=sh<=high*high
    assert frac(squared[0])<=sl<=sh<=frac(squared[1])
    for iv,ex in zip(squares,exact_squares):assert frac(iv[0])<=ex[0]<=ex[1]<=frac(iv[1])
    # Original box corner norms also independently enclosed: 64 per scene.
    for corner in itertools.product((0,1),repeat=6):
        a=[exact_boxes["origin"][j][corner[j]]for j in range(3)]
        b=[exact_boxes["detector"][j][corner[j+3]]for j in range(3)]
        v=sum((y-x)**2 for x,y in zip(a,b));assert low*low<=v<=high*high
    assert r["costs"]==cost(22,12,calls,2,theorems)
    return dict(native=22,casts=12,roots=2,nextafter=calls,corners=64)

ROOT_INPUTS=("0000000000000000","0000000000000040","0000000000000040","0000000000001040",
    "0000000000001000","ffffffffffffef7f","000000000000f0bf","0100000000000000","000000000000f07f")
ROOT_DIRS=("lo","lo","hi","hi","hi","hi","hi","hi","hi")
def verify_helpers(data):
    assert len(data["root_helpers"])==10
    calls=roots=0
    for i,h in enumerate(data["root_helpers"]):
        assert h["label"]=="NEW_CPU_ROOT_CONTROL_NOT_SCENE"and h["id"]==i
        assert h["input_word"]==(ROOT_INPUTS[i]if i<9 else ROOT_INPUTS[1])
        assert h["direction"]==(ROOT_DIRS[i]if i<9 else"hi")
        if i<6:
            assert h["status"]=="PASS"and len(h["ledger"])==1 and h["error"]is None
            z=h["ledger"][0];assert z["radicand_word"]==h["input_word"]and z["direction"]==h["direction"]and z["index"]==0
            _,c=verify_sqrt(z);assert h["costs"]==cost(0,0,c,1,0);calls+=c;roots+=1
        elif i<9:
            assert h["status"]=="STOP"and h["error"]=="sqrt_nonnegative_normal_zero_input"
            assert h["ledger"]==[]and h["costs"]==cost(0,0,0,0,0)
        else:
            assert h["fault_injection"]=="SIMULATED_wrong_RN1_NOT_SYSTEM_FAILURE"
            z=h["ledger"][0];rn=frac(z["RN_word"]);s=frac(z["radicand_word"])
            assert rn==1 and s==2 and z["output_word"]is None and z["status"]=="STOP"
            nw=[neighbor(z["RN_word"],d)for d in ("lo","hi")]
            mids=[((frac(w)+rn)/2)**2 for w in nw]
            assert z["neighbor_words"]==nw and z["midpoint_squares"]==[pair(v)for v in mids]and not mids[0]<=s<=mids[1]
            assert h["error"]==z["reason"]=="sqrt_not_nearest_even_STOP"and h["costs"]==cost(0,0,2,1,0)
            calls+=2;roots+=1
    return dict(native_sqrt=roots,nextafter=calls,passed=6,input_STOP=3,simulated_RN_STOP=1)

def verify_capture(data):
    _,e,pins,old=retained();assert data["pins"]==pins
    assert upstream["verify_capture"](old)["status"]=="PASS" # PURE oracle only
    assert len(data["records"])==16 and {x["id"]for x in data["records"]}==set(e)
    totals=dict(native=0,casts=0,roots=0,nextafter=0,corners=0);counts={}
    for row in data["records"]:
        assert row["request"]==selector(row["id"],e)
        r=row["result"];counts[r["status"]]=counts.get(r["status"],0)+1
        z=verify_record(row,e[row["id"]])
        for k in totals:totals[k]+=z[k]
    assert counts==dict(CPU64_DECLARED_SEGMENT_LENGTH_ONLY=2,STOP_UPSTREAM=14)
    names=("backend","policy","parent_receipt_sha256","parent_record_sha256","upstream_request_sha256","frame_sha256","output_packet_sha256","extra_radius")
    assert tuple(x["id"]for x in data["invalid"])==names
    k=next(k for k in e if e[k]["result"]["status"]=="CPU64_DECLARED_BOX_DISJOINT")
    for x in data["invalid"]:
        q=selector(k,e)
        if x["id"]=="extra_radius":q["radius_override"]="0"
        else:q[x["id"]]="wrong"
        assert x["request"]==q;r=x["result"];scope(r)
        assert r["status"]=="STOP_INPUT"and r["reason"]=="closed_selector"and r["scene"]is None and r["trace"]is None
        assert r["ledger"]==r["sqrt_ledger"]==[]and r["costs"]==cost(0,0,0,0,0)
        assert r["word_decodes"]==r["packet_bytes"]==r["exact_pair_decodes"]==0
    helpers=verify_helpers(data)
    return dict(status="PASS",records=16,lengths=2,upstream_STOP=14,invalid=8,scene_costs=totals,
        helpers=helpers,inherited_pins=len(pins),producer_replays=0,predicate_replays=0,GPU_calls=0)

def mutants(data):
    names=("SOURCE_radius_zero","root_midpoint","root_RN","length_upper","cost_omitted","upstream_rescued","fake_phase","selector_frame")
    accepted=[]
    first=next(i for i,x in enumerate(data["records"])if x["result"]["status"]=="CPU64_DECLARED_SEGMENT_LENGTH_ONLY")
    blocked=next(i for i,x in enumerate(data["records"])if x["result"]["status"]=="STOP_UPSTREAM")
    for name in names:
        z=copy.deepcopy(data);r=z["records"][first]["result"]
        if name=="SOURCE_radius_zero":r["scene"]["points"]["origin"]["radius"][0]=[0,1]
        elif name=="root_midpoint":r["sqrt_ledger"][0]["midpoint_squares"][0]=[0,1]
        elif name=="root_RN":r["sqrt_ledger"][0]["RN_word"]="000000000000f03f"
        elif name=="length_upper":r["trace"]["length"][1]="0000000000000000"
        elif name=="cost_omitted":r["costs"]["native_sqrt"]=0
        elif name=="upstream_rescued":z["records"][blocked]["result"]["status"]="CPU64_DECLARED_SEGMENT_LENGTH_ONLY"
        elif name=="fake_phase":r["phase_certified"]=True
        else:z["records"][first]["request"]["frame_sha256"]="wrong"
        try:verify_capture(z);accepted.append(name)
        except(AssertionError,ValueError,KeyError,IndexError,TypeError):pass
    assert accepted==[]
    return dict(status="PASS",rejected=len(names),names=list(names))

def run():
    import oblique_pair64_segment_length_CPU_v1 as core
    from unittest.mock import patch
    e,pins=core.retained();rows=[dict(id=k,request=core.selector(k,e),result=core._evaluate(core.selector(k,e),e))for k in e]
    k=next(k for k in e if e[k]["result"]["status"]=="CPU64_DECLARED_BOX_DISJOINT")
    invalid=[]
    for name in ("backend","policy","parent_receipt_sha256","parent_record_sha256","upstream_request_sha256","frame_sha256","output_packet_sha256","extra_radius"):
        q=core.selector(k,e)
        if name=="extra_radius":q["radius_override"]="0"
        else:q[name]="wrong"
        invalid.append(dict(id=name,request=q,result=core._evaluate(q,e)))
    helpers=[]
    for i in range(10):
        a=core.LengthOutward();w=ROOT_INPUTS[i]if i<9 else ROOT_INPUTS[1];d=ROOT_DIRS[i]if i<9 else"hi"
        v=struct.unpack("<d",bytes.fromhex(w))[0];error=None;status="PASS"
        try:
            if i==9:
                with patch.object(core.math,"sqrt",return_value=1.0):a.sqrt(v,d)
            else:a.sqrt(v,d)
        except ValueError as ex:error=str(ex);status="STOP"
        h=dict(id=i,label="NEW_CPU_ROOT_CONTROL_NOT_SCENE",input_word=w,direction=d,status=status,error=error,
            ledger=a.sqrt_ledger,costs=a.costs())
        if i==9:h["fault_injection"]="SIMULATED_wrong_RN1_NOT_SYSTEM_FAILURE"
        helpers.append(h)
    data=dict(pins=pins,records=rows,invalid=invalid,root_helpers=helpers)
    summary=verify_capture(data);summary["mutations"]=mutants(data)
    print(json.dumps(dict(summary=summary,evidence=data),sort_keys=True,separators=(",",":"),allow_nan=False))
if __name__=="__main__":run()
