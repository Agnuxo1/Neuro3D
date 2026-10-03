"""Focused synthetic suite plus independent capture-only oracle; no external backend."""
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
from pathlib import Path
import copy
import json

MODEL = "oblique-finite-interval-HOST-v1"
LABEL = "NEW_CPU_SYNTHETIC_NOT_SEALED_PHYSICAL"
POINTS = ("origin","detector","A","B","C")
ROOT = Path(__file__).resolve().parents[2]

def digest(v):
    return sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode()).hexdigest()

def pair(x):
    x=F(x)
    return [x.numerator,x.denominator]

def fixtures():
    h=F(1,2**60)
    # Every case has explicitly declared ALL15 nominal coordinates and radii.
    specs=[
        ("cross", (F(1,4),F(1,4),-1),(F(3,8),F(1,4),1),F(1,1024)),
        ("outside", (2,F(1,4),-1),(F(17,8),F(1,4),1),F(1,1024)),
        ("beyond_end", (F(1,4),F(1,4),-2),(F(3,8),F(1,4),-1),F(1,1024)),
        ("behind_origin", (F(1,4),F(1,4),1),(F(3,8),F(1,4),2),F(1,1024)),
        ("edge", (0,F(1,4),-1),(0,F(1,4),1),F(1,1024)),
        ("t0", (F(1,4),F(1,4),0),(F(3,8),F(1,4),1),F(1,1024)),
        ("t1", (F(1,4),F(1,4),-1),(F(3,8),F(1,4),0),F(1,1024)),
        ("coplanar", (F(1,4),F(1,4),0),(F(3,8),F(1,4),0),F(1,1024)),
        ("degenerate", (F(1,4),F(1,4),-1),(F(3,8),F(1,4),1),F(1,1024)),
        ("thin_cross", (F(1,4),F(1,4),-h),(F(3,8),F(1,4),h),h/64),
        ("thin_beyond_end", (F(1,4),F(1,4),-2*h),(F(3,8),F(1,4),-h),h/64),
        ("wide_uncertainty", (F(1,4),F(1,4),-1),(F(3,8),F(1,4),1),F(4))]
    for name,o,e,r in specs:
        for reverse,wind,uncertain in product((False,True),repeat=3):
            coords=[o,e,(0,0,0),(1,0,0),(0,1,0)]
            if name=="degenerate":coords[4]=(2,0,0)
            if reverse:coords[0],coords[1]=coords[1],coords[0]
            if wind:coords[3],coords[4]=coords[4],coords[3]
            suffix=f"{name}/reverse{int(reverse)}/wind{int(wind)}/box{int(uncertain)}"
            scene=dict(label=LABEL,scene_id="NEW-SYNTHETIC/"+suffix,context="original-local/"+suffix,
                units="scene_length",SOURCE={"id":"SOURCE0","point":"origin"},
                DETECTOR={"id":"DETECTOR0","point":"detector"},
                primitive={"id":"TRIANGLE0","vertices":["A","B","C"]},
                points={n:dict(nominal=[pair(x) for x in c],
                               radius=[pair(r if uncertain else 0)]*3) for n,c in zip(POINTS,coords)})
            query=dict(model=MODEL,snapshot_sha256=digest(scene),context=scene["context"],
                       source="SOURCE0",detector="DETECTOR0",primitive="TRIANGLE0",segment="CLOSED_FINITE_0_1")
            yield dict(name=suffix,scene=scene,query=query)

def invalid_inputs(item):
    def yield_change(name, callback, rebind=False):
        x=copy.deepcopy(item)
        callback(x)
        if rebind:x["query"]["snapshot_sha256"]=digest(x["scene"])
        x["name"]="invalid/"+name
        return x
    changes=[
      ("missing_radius", lambda x:x["scene"]["points"]["A"].pop("radius"),True),
      ("missing_end", lambda x:x["scene"]["points"].pop("detector"),True),
      ("bool",lambda x:x["scene"]["points"]["A"]["nominal"][0].__setitem__(0,True),True),
      ("float",lambda x:x["scene"]["points"]["A"]["nominal"][0].__setitem__(0,0.0),True),
      ("negative_radius",lambda x:x["scene"]["points"]["A"]["radius"].__setitem__(0,[-1,2]),True),
      ("noncanonical",lambda x:x["scene"]["points"]["A"]["nominal"].__setitem__(0,[0,2]),True),
      ("zero_denominator",lambda x:x["scene"]["points"]["A"]["nominal"].__setitem__(0,[0,0]),True),
      ("bit_limit",lambda x:x["scene"]["points"]["A"]["nominal"].__setitem__(0,[1,2**129]),True),
      ("domain",lambda x:x["scene"]["points"]["A"]["nominal"].__setitem__(0,[2**33,1]),True),
      ("units",lambda x:x["scene"].__setitem__("units","meters_undeclared"),True),
      ("physical_label",lambda x:x["scene"].__setitem__("label","PHYSICAL"),True),
      ("SOURCE1",lambda x:x["query"].__setitem__("source","SOURCE1"),False),
      ("infinite_ray",lambda x:x["query"].__setitem__("segment","INFINITE"),False),
      ("cross_context",lambda x:x["query"].__setitem__("context","foreign"),False),
      ("stale_snapshot",lambda x:x["scene"]["points"]["A"]["nominal"].__setitem__(0,[1,8]),False),
      ("extra_auth",lambda x:x["scene"].__setitem__("scene_authenticated",True),True),
      ("unknown_radius",lambda x:x["scene"]["points"]["B"]["radius"].__setitem__(0,None),True)]
    for name,func,rebind in changes:yield yield_change(name,func,rebind)

def iv(v):return tuple(F(*p) for p in v)
def scalar_sub(a,b):return tuple(x-y for x,y in zip(a,b))
def det3(a,b,c):
    # Independent scalar Cramer's-rule determinant, not Moller cross/dot implementation.
    return a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0])
def scalar_slacks(points):
    o,e,a,b,c=points
    e1,e2,minusd,s=scalar_sub(b,a),scalar_sub(c,a),scalar_sub(o,e),scalar_sub(o,a)
    det=det3(e1,e2,minusd)
    u,v,t=det3(s,e2,minusd),det3(e1,s,minusd),det3(e1,e2,s)
    return dict(det=det,U=u,V=v,W=det-u-v,T=t,end_slack=det-t)

def oracle_trace(scene):
    # Expression-tree interval evaluation independent of producer functions.
    def operation(op,*vs):
        if op=="+" :return vs[0][0]+vs[1][0],vs[0][1]+vs[1][1]
        if op=="-" :return vs[0][0]-vs[1][1],vs[0][1]-vs[1][0]
        xs=[a*b for a,b in product(*vs)]
        return min(xs),max(xs)
    vectors=[]
    for n in POINTS:
        p=scene["points"][n]
        vectors.append([(F(*x)-F(*r),F(*x)+F(*r)) for x,r in zip(p["nominal"],p["radius"])])
    o,e,a,b,c=vectors
    d,e1,e2,s=[[operation("-",x,y) for x,y in zip(v,w)] for v,w in ((e,o),(b,a),(c,a),(o,a))]
    def cr(v,w):
        return [operation("-",operation("*",v[j],w[k]),operation("*",v[k],w[j]))
                for j,k in ((1,2),(2,0),(0,1))]
    def dp(v,w):
        a,b,c=[operation("*",x,y) for x,y in zip(v,w)]
        return operation("+",operation("+",a,b),c)
    p,q=cr(d,e2),cr(s,e1)
    det,u,v,t=dp(e1,p),dp(s,p),dp(d,q),dp(e2,q)
    return dict(det=det,U=u,V=v,W=operation("-",operation("-",det,u),v),
                T=t,end_slack=operation("-",det,t))

def verify_capture(evidence):
    assert evidence["model"]==MODEL and evidence["label"]==LABEL
    assert len(evidence["records"])==96 and len(evidence["invalid"])==17
    counts={}
    corner_checks=0
    for record in evidence["records"]:
        scene,q,r=record["scene"],record["query"],record["result"]
        assert q==dict(model=MODEL,snapshot_sha256=digest(scene),context=scene["context"],
                       source="SOURCE0",detector="DETECTOR0",primitive="TRIANGLE0",segment="CLOSED_FINITE_0_1")
        raw=oracle_trace(scene)
        assert r["snapshot_sha256"]==digest(scene) and r["query_sha256"]==digest(q)
        assert {k:iv(v) for k,v in r["trace"].items()}==raw
        det=raw["det"]
        sign=1 if det[0]>0 else -1 if det[1]<0 else 0
        oriented={k:x if sign==1 else (-x[1],-x[0]) for k,x in raw.items()} if sign else None
        assert r["sign"]==sign and (None if r["oriented"] is None else {k:iv(v) for k,v in r["oriented"].items()})==oriented
        expected="STOP_UNRESOLVED"
        if sign:
            if any(oriented[k][1]<0 for k in ("U","V","W","T","end_slack")):expected="DECLARED_BOX_DISJOINT"
            elif all(oriented[k][0]>0 for k in ("U","V","W","T","end_slack")):expected="DECLARED_BOX_INTERIOR_CROSS"
        assert r["status"]==expected
        assert r["coordinate_boxes"]==15 and r["radius_slots"]==15
        assert r["exact_interval_operations"]==dict(add=8,sub=21,mul=24,neg=6 if sign==-1 else 0)
        assert r["division_operations"]==0 and r["EPS_used"] is False
        assert r["promotion"]=="STOP_PHYSICAL_NATIVE_GPU"
        assert r["costs"]=="HOST_PARTIAL_ONLY_FULL_COSTS_UNKNOWN"
        for flag in ("physical_visibility_certified","phase_certified","native_backend_certified","GPU_used","scene_authenticated"):
            assert r[flag] is False
        name=record["name"].split("/")[0]
        if name in ("cross","thin_cross"):assert expected=="DECLARED_BOX_INTERIOR_CROSS"
        if name in ("outside","beyond_end","behind_origin","thin_beyond_end"):assert expected=="DECLARED_BOX_DISJOINT"
        if name in ("edge","t0","t1","coplanar","degenerate","wide_uncertainty"):
            assert expected=="STOP_UNRESOLVED" or (name=="wide_uncertainty" and record["name"].endswith("box0"))
        counts[expected]=counts.get(expected,0)+1
        # 16 declared-box corners per case: sampling, NOT an exhaustive 2^15 proof.
        for index in range(16):
            mask=0 if index==0 else (2**15-1 if index==1 else 1<<(index-2))
            flat=[]
            for j,n in enumerate(POINTS):
                pt=scene["points"][n]
                flat.append(tuple(F(*x)+(1 if mask & (1<<(j*3+axis)) else -1)*F(*rad)
                                  for axis,(x,rad) in enumerate(zip(pt["nominal"],pt["radius"]))))
            exact=scalar_slacks(flat)
            assert all(raw[k][0]<=x<=raw[k][1] for k,x in exact.items())
            if expected=="DECLARED_BOX_INTERIOR_CROSS":
                assert all(exact[k]*sign>0 for k in ("U","V","W","T","end_slack"))
            if expected=="DECLARED_BOX_DISJOINT":
                assert any(exact[k]*sign<0 for k in ("U","V","W","T","end_slack"))
            corner_checks+=1
    for item in evidence["invalid"]:
        r=item["result"]
        assert r["status"]=="STOP_INPUT" and r["trace"] is None
        assert all(r[k] is False for k in ("physical_visibility_certified","phase_certified","native_backend_certified","GPU_used","scene_authenticated"))
    assert len(evidence["pins"])>=244
    for item in evidence["pins"]:
        data=(ROOT/item["path"]).read_bytes()
        assert len(data)==item["bytes"] and sha256(data).hexdigest()==item["sha256"]
    return dict(status="PASS",counts=counts,main=96,invalid=17,corner_checks=corner_checks,
                pins=len(evidence["pins"]),GPU_calls=0,backend_calls=0,full_costs="UNKNOWN_NOT_ZERO")

def run():
    import sys
    sys.path.insert(0,str(ROOT/"Blender/benchmarks/capacity_audit"))
    from oblique_finite_interval_HOST_v1 import classify
    records=list(fixtures())
    for x in records:x["result"]=classify(x["scene"],x["query"])
    invalid=list(invalid_inputs(records[0]))
    for x in invalid:x["result"]=classify(x["scene"],x["query"])
    parent=ROOT/"coordinacion/respuestas/PRECISION-RELATIVE-FIELD-ANCHOR-HOST-001-CODEX.json"
    receipt=json.loads(parent.read_text(encoding="utf-8-sig"))
    # Sealed dependencies only; no parent producer or backend execution.
    pins=[dict(path=p,bytes=len((ROOT/p).read_bytes()),sha256=h) for p,h in receipt["code_doc_sha256"].items()]
    data=parent.read_bytes()
    pins=copy.deepcopy(pins)+[dict(path=str(parent.relative_to(ROOT)).replace("\\","/"),
                                 bytes=len(data),sha256=sha256(data).hexdigest())]
    evidence=dict(model=MODEL,label=LABEL,records=records,invalid=invalid,pins=pins)
    summary=verify_capture(evidence)
    # Independent capture mutations must be rejected, with first failures retained by runner.
    mutations=[]
    for name in ("physical","EPS","infinite","omit_radius","det_trace","sign","result","snapshot"):
        altered=copy.deepcopy(evidence)
        x=altered["records"][0]
        if name=="physical":x["result"]["physical_visibility_certified"]=True
        elif name=="EPS":x["result"]["EPS_used"]=True
        elif name=="infinite":x["query"]["segment"]="INFINITE"
        elif name=="omit_radius":x["result"]["radius_slots"]=14
        elif name=="det_trace":x["result"]["trace"]["det"][0]=[0,1]
        elif name=="sign":x["result"]["sign"]=0
        elif name=="result":x["result"]["status"]="DECLARED_BOX_DISJOINT"
        else:x["result"]["snapshot_sha256"]="0"*64
        try:verify_capture(altered)
        except (AssertionError,ValueError,KeyError):mutations.append(name)
        else:raise AssertionError("mutation_not_rejected/"+name)
    summary["mutations_rejected"]=mutations
    return dict(summary=summary,evidence=evidence)
