"""Native ledger suite; independent rational/word replay never executes native producer."""
from fractions import Fraction as F
from pathlib import Path
import base64
import copy
import hashlib
import json
import zlib
ROOT=Path(__file__).resolve().parents[2]
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-FINITE-INTERVAL-HOST-001-CODEX.json"
PSHA="3bad55726d8cfb8110f068304dd472cb31115bfd080ce58ffff7f1188a2d275d"
MODEL="oblique-finite-interval-CPU64-v1"
POINTS=("origin","detector","A","B","C")
def digest(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode()).hexdigest()
def pair(x):return [x.numerator,x.denominator]
def bits(w):
    assert type(w) is str and len(w)==16
    return int.from_bytes(bytes.fromhex(w),"little")
def fraction(w, allow_subnormal=False):
    n=bits(w);sign=-1 if n>>63 else 1;exp=(n>>52)&2047;mant=n&((1<<52)-1)
    assert exp!=2047
    if exp==0:
        assert mant==0 or allow_subnormal
        return sign*F(mant,2**1074)
    e=exp-1023-52
    return sign*F((1<<52)+mant)*(F(2)**e)
def neighbor(w,direction):
    n=bits(w)
    if fraction(w)==0:
        raise AssertionError("zero_neighbors_not_requested")
    up=direction=="hi"
    n=n+(1 if (up != bool(n>>63)) else -1)
    return n.to_bytes(8,"little").hex()
def verify_round(entry):
    exact=F(*entry["exact"]);rn=fraction(entry["RN_word"])
    assert entry["status"]=="PASS" and entry["direction"] in ("lo","hi")
    assert rn!=0 or exact==0
    calls=0
    if exact!=0:
        lo,hi=neighbor(entry["RN_word"],"lo"),neighbor(entry["RN_word"],"hi")
        calls=2
        distance=abs(exact-rn)
        for w in (lo,hi):
            other=abs(exact-fraction(w))
            assert distance<=other
            assert distance!=other or bits(entry["RN_word"])%2==0
    outward=(entry["direction"]=="lo" and rn>exact) or (entry["direction"]=="hi" and rn<exact)
    expected=neighbor(entry["RN_word"],entry["direction"]) if outward else entry["RN_word"]
    assert entry["nextafter"]==outward and entry["output_word"]==expected
    out=fraction(expected)
    assert out<=exact if entry["direction"]=="lo" else out>=exact
    return out,calls+int(outward)

def verify_record(record):
    scene,request,r=record["scene"],record["request"],record["result"]
    assert request==dict(backend=MODEL,scene_query=record["parent"]["query"],snapshot_sha256=digest(scene))
    assert scene==record["parent"]["scene"]
    assert r["backend"]==MODEL and r["coordinate_boxes"]==15
    assert r["query_sha256"]==digest(request) and r["snapshot_sha256"]==digest(scene)
    assert r["parent_query_sha256"]==digest(record["parent"]["query"])
    for k in ("physical_visibility_certified","phase_certified","GPU_used","scene_authenticated","GPU_backend_certified","EPS_used","FMA_used"):
        assert r[k] is False
    assert r["CPU_binary64_executed"] is True and r["promotion"]=="STOP_PHYSICAL_GPU"
    assert r["division_operations"]==0
    ledger=r["ledger"];cursor=0;calls=0;native=0;casts=0
    def take(op,exact,direction,operands):
        nonlocal cursor,calls,native,casts
        entry=ledger[cursor];assert entry["index"]==cursor and entry["op"]==op
        assert entry["exact"]==pair(exact) and entry["operands"]==operands and entry["direction"]==direction
        out,c=verify_round(entry);calls+=c;cursor+=1
        casts+=int(op=="cast")
        native+=int(op not in ("cast","mul_shared_RN"))
        return entry["output_word"]
    vectors=[]
    for n in POINTS:
        p=scene["points"][n];v=[]
        for x,rad in zip(p["nominal"],p["radius"]):
            x,b=F(*x),F(*rad)
            v.append((take("cast",x-b,"lo",[]),take("cast",x+b,"hi",[])))
        vectors.append(v)
    assert r["input_boxes"]=={n:[list(b) for b in v] for n,v in zip(POINTS,vectors)}
    def scalar(op,a,b,direction):
        fa,fb=fraction(a),fraction(b)
        exact=fa+fb if op=="add" else fa-fb
        return take(op,exact,direction,[a,b])
    def sub(a,b):return scalar("sub",a[0],b[1],"lo"),scalar("sub",a[1],b[0],"hi")
    def add(a,b):return scalar("add",a[0],b[0],"lo"),scalar("add",a[1],b[1],"hi")
    def mul(a,b):
        lower,upper=[],[]
        for x in a:
            for y in b:
                lo=take("mul",fraction(x)*fraction(y),"lo",[x,y])
                hi=take("mul_shared_RN",fraction(x)*fraction(y),"hi",[x,y])
                assert ledger[cursor-2]["RN_word"]==ledger[cursor-1]["RN_word"]
                lower.append(lo);upper.append(hi)
        return min(lower,key=fraction),max(upper,key=fraction)
    def vsub(v,w):return [sub(x,y) for x,y in zip(v,w)]
    def cross(v,w):return [sub(mul(v[j],w[k]),mul(v[k],w[j])) for j,k in ((1,2),(2,0),(0,1))]
    def dot(v,w):
        terms=[mul(x,y) for x,y in zip(v,w)]
        return add(add(terms[0],terms[1]),terms[2])
    o,e,a,b,c=vectors
    d,e1,e2,s=vsub(e,o),vsub(b,a),vsub(c,a),vsub(o,a)
    p,q=cross(d,e2),cross(s,e1)
    det,u,v,t=dot(e1,p),dot(s,p),dot(d,q),dot(e2,q)
    raw=dict(det=det,U=u,V=v,W=sub(sub(det,u),v),T=t,end_slack=sub(det,t))
    assert {k:list(v) for k,v in raw.items()}==r["trace"]
    assert cursor==len(ledger)==280 and casts==30 and native==154
    # Each native interval encloses the original exact HOST interval, without shrinking either.
    parent_raw=record["parent"]["result"]["trace"]
    for k,(lo,hi) in raw.items():
        assert fraction(lo)<=F(*parent_raw[k][0])<=F(*parent_raw[k][1])<=fraction(hi)
    det=tuple(map(fraction,raw["det"]))
    sign=1 if det[0]>0 else -1 if det[1]<0 else 0
    oriented={k:tuple(map(fraction,w)) if sign==1 else tuple(-fraction(x) for x in reversed(w)) for k,w in raw.items()} if sign else None
    assert r["sign"]==sign
    assert (None if r["oriented"] is None else {k:tuple(map(fraction,x)) for k,x in r["oriented"].items()})==oriented
    expected="STOP_UNRESOLVED"
    if sign:
        if any(oriented[k][1]<0 for k in ("U","V","W","T","end_slack")):expected="CPU64_DECLARED_BOX_DISJOINT"
        elif all(oriented[k][0]>0 for k in ("U","V","W","T","end_slack")):expected="CPU64_DECLARED_BOX_INTERIOR_CROSS"
    assert r["status"]==expected
    if record["parent"]["result"]["status"]=="STOP_UNRESOLVED":assert expected=="STOP_UNRESOLVED"
    assert r["costs"]==dict(native_arithmetic=154,endpoint_casts=30,nextafter_calls=calls,
                            sign_flips=12 if sign==-1 else 0,exact_audit_fraction_operations="UNMEASURED_NOT_ZERO",total_cost="UNKNOWN_NOT_ZERO")
    return expected,calls

def verify_capture(cap):
    counts={};calls=0
    parent_bytes=(ROOT/PARENT).read_bytes()
    assert len(parent_bytes)==139020 and hashlib.sha256(parent_bytes).hexdigest()==PSHA
    parent_receipt=json.loads(parent_bytes)
    capture=parent_receipt["test_run"]
    parent_raw=zlib.decompress(base64.b64decode(capture["stdout_zlib_base64"]))
    assert len(parent_raw)==capture["stdout_bytes"]<=2*1024*1024
    assert hashlib.sha256(parent_raw).hexdigest()==capture["stdout_sha256"]
    parent_records=json.loads(parent_raw)["evidence"]["records"]
    allowed={x["name"]:x for x in parent_records if x["name"].endswith("/reverse0/wind0/box1")
             or x["name"] in ("cross/reverse0/wind1/box1","thin_cross/reverse0/wind1/box1")}
    assert set(x["parent"]["name"] for x in cap["records"])==set(allowed)
    assert cap["pins"]==dict(parent_receipt["code_doc_sha256"],**{PARENT:PSHA})
    assert len(cap["records"])==14 and len({x["parent"]["name"] for x in cap["records"]})==14
    for x in cap["records"]:
        assert x["parent"]==allowed[x["parent"]["name"]]
        assert x["parent_record_sha256"]==digest(x["parent"])
        status,n=verify_record(x);calls+=n;counts[status]=counts.get(status,0)+1
    assert len(cap["invalid"])==4
    for x in cap["invalid"]:
        r=x["result"];assert r["status"]=="STOP_INPUT" and r["ledger"]==[]
        assert not r["CPU_binary64_executed"] and r["costs"]["native_arithmetic"]==0
    assert len(cap["helpers"])==5
    for h in cap["helpers"]:
        for e in h["ledger"]:
            if e["op"]=="mul":
                assert F(*e["exact"])==fraction(e["operands"][0])*fraction(e["operands"][1])
        if h["name"]=="halfway_cast":
            assert all(F(*e["exact"])==F(1)+F(1,2**53) for e in h["ledger"])
        if h["name"]=="negative_halfway_cast":
            assert all(F(*e["exact"])==-F(1)-F(1,2**53) for e in h["ledger"])
        if h["expected"]=="PASS":
            for entry in h["ledger"]:verify_round(entry)
            assert h["status"]=="PASS"
        else:
            assert h["status"]=="STOP" and h["ledger"][-1]["status"]=="STOP"
            entry=h["ledger"][-1]
            assert entry["output_word"] is None
            n=bits(entry["RN_word"]);exp=(n>>52)&2047;mant=n&((1<<52)-1)
            assert exp==2047 or (exp==0 and (mant or F(*entry["exact"])!=0))
    for p,h in cap["pins"].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    return dict(status="PASS",main=14,counts=counts,input_STOP=4,helpers=5,
                proof_records=3920,native_arithmetic=2156,endpoint_casts=420,nextafter_calls=calls,
                pins=len(cap["pins"]),parent_producer_replays=0,GPU_calls=0,full_costs="UNKNOWN_NOT_ZERO")

def run():
    import sys
    sys.path.insert(0,str(ROOT/"Blender/benchmarks/capacity_audit"))
    import oblique_finite_interval_CPU64_v1 as m
    raw=(ROOT/PARENT).read_bytes();assert len(raw)==139020 and hashlib.sha256(raw).hexdigest()==PSHA
    d=json.loads(raw);pins=dict(d["code_doc_sha256"]);pins[PARENT]=PSHA
    c=d["test_run"];assert c["rc"]==0 and not c["timed_out"]
    raw=zlib.decompress(base64.b64decode(c["stdout_zlib_base64"]))
    assert len(raw)==c["stdout_bytes"]<=2*1024*1024 and hashlib.sha256(raw).hexdigest()==c["stdout_sha256"]
    data=json.loads(raw)["evidence"]
    selected=[x for x in data["records"] if x["name"].endswith("/reverse0/wind0/box1")]
    selected += [x for x in data["records"] if x["name"] in ("cross/reverse0/wind1/box1","thin_cross/reverse0/wind1/box1")]
    records=[]
    for parent in selected:
        q=dict(backend=MODEL,scene_query=parent["query"],snapshot_sha256=digest(parent["scene"]))
        records.append(dict(parent=parent,parent_record_sha256=digest(parent),scene=parent["scene"],
                            request=q,result=m.classify(parent["scene"],q)))
    invalid=[]
    for parent in data["invalid"]:
        if parent["name"] not in ("invalid/missing_radius","invalid/SOURCE1","invalid/infinite_ray"):continue
        q=dict(backend=MODEL,scene_query=parent["query"],snapshot_sha256=digest(parent["scene"]))
        invalid.append(dict(name=parent["name"],result=m.classify(parent["scene"],q)))
    q=copy.deepcopy(records[0]["request"]);q["backend"]="GPU_ALIAS"
    invalid.append(dict(name="unknown_backend",result=m.classify(records[0]["scene"],q)))
    helpers=[]
    for name,args,expected in [
        ("halfway_cast",(F(1)+F(1,2**53),),"PASS"),
        ("negative_halfway_cast",(-F(1)-F(1,2**53),),"PASS"),
        ("underflow",(float.fromhex("0x1p-600"),float.fromhex("0x1p-600")),"STOP"),
        ("subnormal",(float.fromhex("0x1p-1022"),0.5),"STOP"),
        ("overflow",(1e300,1e300),"STOP")]:
        a=m.Outward();status="PASS"
        try:
            if len(args)==1:a.cast(args[0],"lo");a.cast(args[0],"hi")
            else:a.arithmetic(*args,"mul","lo")
        except ValueError:status="STOP"
        helpers.append(dict(name=name,expected=expected,status=status,ledger=a.ledger,costs=a.costs()))
    cap=dict(records=records,invalid=invalid,helpers=helpers,pins=pins)
    summary=verify_capture(cap)
    mutations=[]
    for name in ("omit_rounding","output_word","shrink_box","physical","rescue_parent_STOP","omit_cost","snapshot","shared_product_RN"):
        x=copy.deepcopy(cap);r=x["records"][0]["result"]
        if name=="omit_rounding":r["ledger"][0]["exact"]=[0,1]
        elif name=="output_word":r["ledger"][0]["output_word"]="0"*16
        elif name=="shrink_box":r["input_boxes"]["A"][0][0]="0"*16
        elif name=="physical":r["physical_visibility_certified"]=True
        elif name=="rescue_parent_STOP":
            next(z for z in x["records"] if z["parent"]["name"].startswith("edge/"))["result"]["status"]="CPU64_DECLARED_BOX_INTERIOR_CROSS"
        elif name=="omit_cost":r["costs"]["native_arithmetic"]=0
        elif name=="snapshot":r["snapshot_sha256"]="0"*64
        else:next(e for e in r["ledger"] if e["op"]=="mul_shared_RN")["RN_word"]="0"*16
        try:verify_capture(x)
        except (AssertionError,ValueError,KeyError):mutations.append(name)
        else:raise AssertionError("mutation_not_rejected/"+name)
    summary["mutations_rejected"]=mutations
    return dict(summary=summary,evidence=cap)
