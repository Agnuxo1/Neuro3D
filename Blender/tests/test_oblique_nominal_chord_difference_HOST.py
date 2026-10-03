"""Independent rational/squared-inequality oracle, no old numerical producer."""
from pathlib import Path
from fractions import Fraction as F
import sys,json,hashlib,zlib,base64,copy
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"Blender/benchmarks/capacity_audit"))
import oblique_nominal_chord_difference_HOST_v1 as c
PSHA="394e2198aab8a0893cee4eaa928d599d965ae76abee5ab91fb7ca6454c44196d"

def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()
def enc(v):return [v.numerator,v.denominator]
def val(v):
    assert type(v)is list and len(v)==2 and all(type(x)is int for x in v)and v[1]>0
    x=F(*v);assert enc(x)==v;return x

def cap(a):
    b=zlib.decompress(base64.b64decode(a["stdout_zlib_base64"],validate=True))
    assert a["rc"]==0 and not a["timed_out"]and len(b)==a["stdout_bytes"]and hashlib.sha256(b).hexdigest()==a["stdout_sha256"]
    return json.loads(b)

def retained():
    b=(ROOT/c.PARENT).read_bytes();assert len(b)==164509 and hashlib.sha256(b).hexdigest()==PSHA
    r=json.loads(b);pins=dict(r["code_doc_sha256"]);assert len(pins)==319
    for p,h in pins.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    assert cap(r["independent_pre"])["status"]=="PASS"
    def old(p):
        raw=(ROOT/p).read_bytes();assert hashlib.sha256(raw).hexdigest()==pins[p]
        return cap(json.loads(raw)["test_run"])["evidence"]
    w={x["id"]:x for x in old(c.WIDTH)["records"]};rr={x["id"]:x for x in old(c.REFERENCE)["records"]}
    e=old(c.ORIGINAL);o={"scene:"+x["name"]:x for x in e["records"]}
    o["native_inexact"]=e["inexact"];o.update({"input:"+x["name"]:x for x in e["invalid"]})
    assert set(w)==set(rr)==set(o)and len(w)==16;pins[c.PARENT]=PSHA
    return w,rr,o,pins

def checkroot(s,words):
    a,b=map(val,words);grid=F(1,2**96)
    assert a>=0 and a/grid==int(a/grid)and a*a<=s<(a+grid)*(a+grid)
    assert b==(a if a*a==s else a+grid)and s<=b*b
    return a,b

def verify(d):
    w,rr,o,pins=retained();assert d["pins"]==pins and len(d["records"])==16
    seen=set();pos=stop=roots=0
    for x in d["records"]:
        k=x["id"];assert k not in seen and k in w;seen.add(k)
        q=x["request"];r=x["result"]
        expected=dict(model=c.MODEL,policy=c.POLICY,record_id=k,parent_receipt_sha256=PSHA,
            width_record_sha256=digest(w[k]),reference_record_sha256=digest(rr[k]),original_record_sha256=digest(o[k]),
            original_snapshot_sha256=digest(o[k]["scene"]),
            original_query_sha256=digest(o[k].get("scene_query",o[k]["request"].get("scene_query"))),
            source="SOURCE0",detector="DETECTOR0",units="scene_length",reference_role="DECLARED_NOMINAL_STRAIGHT_CHORD_NOT_OPTICAL")
        assert q==expected and r["request_sha256"]==digest(q)
        for f in ("source_uncertainty_cancelled","correlation_assumed","wavelength_known","phase_certified",
                  "physical_reference_certified","scene_authenticated","scene_engine_admitted","GPU_used","Bpy_used"):assert r[f]is False
        for f in ("new_native_RN","new_native_sqrt","retained_numeric_replays"):assert r[f]==0
        assert r["native_difference"]is None and r["phase_error_bound"]is None and r["full_costs"]=="UNKNOWN_NOT_ZERO"
        assert r["promotion"]=="STOP_PHASE_PHYSICAL_NATIVE_GPU_AND_FULL_COSTS"
        assert r["scope"]=="HOST_STRAIGHT_BOX_LENGTH_MINUS_NEW_DECLARED_NOMINAL_CHORD_ONLY"
        if w[k]["result"]["status"]!="CPU64_SCENE_PAIR_WIDTH_HOST_BOUND_ONLY":
            assert r["status"]=="STOP_UPSTREAM"and r["reason"]=="sealed_STOP_not_rescued"and r["diagnostic"]is None
            for f in ("new_HOST_nominal_products","new_HOST_nominal_sum_adds","new_HOST_nominal_root_calls","new_HOST_difference_subtractions"):assert r[f]==0
            stop+=1;continue
        z=r["diagnostic"];s=o[k]["scene"];old=rr[k]["result"]["diagnostic"]
        assert r["status"]=="HOST_DECLARED_NOMINAL_CHORD_DIFFERENCE_ONLY"and r["reason"]=="signed_difference_not_width_or_phase"
        assert z["original_snapshot_sha256"]==q["original_snapshot_sha256"]and z["original_query_sha256"]==q["original_query_sha256"]
        assert z["source"]=="SOURCE0"and z["detector"]=="DETECTOR0"and z["units"]=="scene_length"
        assert z["reference_role"]==q["reference_role"]and z["reference_definition"]=="sqrt(sum((detector_nominal-source_nominal)^2))"
        assert z["uncertainty_policy"]=="FULL_ORIGINAL_BOX_NO_SOURCE_CANCELLATION"
        assert z["width_operand_used"]is False and z["physical_reference_certified"]is False
        assert z["ALL15_original_radii"]=={n:p["radius"]for n,p in s["points"].items()}
        ds=[val(y)-val(a)for a,y in zip(s["points"]["origin"]["nominal"],s["points"]["detector"]["nominal"])]
        S=sum(v*v for v in ds);assert z["nominal_delta"]==[enc(v)for v in ds]
        assert z["nominal_squared_terms"]==[enc(v*v)for v in ds]and val(z["nominal_squared_length"])==S
        # Independent continuous endpoint-box extrema, not corner sampling.
        extrema=[]
        for j in range(3):
            ar=val(s["points"]["origin"]["radius"][j]);br=val(s["points"]["detector"]["radius"][j])
            l,h=ds[j]-ar-br,ds[j]+ar+br
            extrema.append((F(0)if l<=0<=h else min(l*l,h*h),max(l*l,h*h)))
        sl,sh=sum(t[0]for t in extrema),sum(t[1]for t in extrema)
        assert z["retained_box_squared_interval"]==old["extrema"]["squared"]==[enc(sl),enc(sh)]
        rlo,rhi=checkroot(S,z["reference_root96"]);roots+=1
        lmin=checkroot(sl,old["roots"][0]);lmax=checkroot(sh,old["roots"][1])
        L=[lmin[0],lmax[1]];assert z["retained_box_length_interval"]==old["reference_interval"]==[enc(v)for v in L]
        assert z["signed_difference_interval"]==[enc(L[0]-rhi),enc(L[1]-rlo)]
        dlo,dhi=map(val,z["signed_difference_interval"]);assert dlo<=0<=dhi and z["zero_covered"]is True
        assert val(z["reference_rounding_width"])==rhi-rlo
        assert (r["new_HOST_nominal_products"],r["new_HOST_nominal_sum_adds"],r["new_HOST_nominal_root_calls"],r["new_HOST_difference_subtractions"])==(3,2,1,2)
        pos+=1
    assert (pos,stop,roots)==(2,14,2)
    for ctl in d["root_controls"]:
        checkroot(val(ctl["squared"]),ctl["root"])
    assert len(d["root_controls"])==2
    for n in d["invalid"]:
        assert n["result"]["status"]=="STOP_INPUT"and n["result"]["diagnostic"]is None
        assert n["result"]["new_HOST_nominal_root_calls"]==0
    assert len(d["invalid"])==8
    return dict(eligible=pos,upstream_STOP=stop,new_scene_nominal_roots=roots,
        root_controls=2,invalid_selectors=8,source_uncertainty_cancelled=False,
        native_RN=0,old_numeric_replays=0,full_costs="UNKNOWN_NOT_ZERO",
        values=[dict(id=x["id"],squared=str(val(x["result"]["diagnostic"]["nominal_squared_length"])),
           reference=[str(val(v))for v in x["result"]["diagnostic"]["reference_root96"]],
           difference=[str(val(v))for v in x["result"]["diagnostic"]["signed_difference_interval"]])
           for x in d["records"]if x["result"]["diagnostic"]])

def mutations(d):
    pos=next(i for i,x in enumerate(d["records"])if x["result"]["diagnostic"])
    changes=[
        lambda v:v["records"][pos]["result"]["diagnostic"].update(reference_root96=[[0,1],[0,1]]),
        lambda v:v["records"][pos]["result"]["diagnostic"].update(signed_difference_interval=[[0,1],[0,1]]),
        lambda v:v["records"][pos]["result"]["diagnostic"].update(source="SOURCE1"),
        lambda v:v["records"][pos]["result"]["diagnostic"].update(units="radian"),
        lambda v:v["records"][pos]["result"]["diagnostic"].update(width_operand_used=True),
        lambda v:v["records"][pos]["result"].update(phase_certified=True),
        lambda v:v["records"][pos]["result"]["diagnostic"].update(ALL15_original_radii={}),
        lambda v:v["records"][pos]["result"].update(new_HOST_nominal_root_calls=0)]
    for mutate in changes:
        bad=copy.deepcopy(d);mutate(bad)
        try:verify(bad)
        except(AssertionError,ValueError,KeyError,TypeError):continue
        raise AssertionError("mutation_not_rejected")
    return len(changes)

def run():
    w,r,o,pins=c.retained()
    d=dict(pins=pins,records=[dict(id=k,request=c.selector(k,w,r,o),result=c._audit(c.selector(k,w,r,o),w,r,o))for k in w],
           invalid=[],root_controls=[])
    k=next(x["id"]for x in d["records"]if x["result"]["diagnostic"]);q=c.selector(k,w,r,o)
    for field,value in (("source","SOURCE1"),("units","radian"),("reference_role","PHYSICAL_OPTICAL"),
        ("original_snapshot_sha256","0"*64),("policy","WIDTH"),("record_id","missing"),
        ("parent_receipt_sha256","0"*64),("wavelength","1")):
        bad=dict(q);bad[field]=value;d["invalid"].append(dict(request=bad,result=c._audit(bad,w,r,o)))
    for s in (F(1,64),F(2)):
        d["root_controls"].append(dict(squared=enc(s),root=[enc(v)for v in c.root96(s)]))
    summary=verify(d);summary["mutations_rejected"]=mutations(d)
    api=[]
    for name in ("selector","missing_parent","drift_sha"):
        if name=="selector":x=c.audit(dict(q,source="SOURCE1"))
        else:
            with patch.object(c,"receipt",side_effect=OSError(name)):x=c.audit(q)
        assert x["status"]=="STOP_INPUT"and x["new_HOST_nominal_root_calls"]==0
        api.append(dict(name=name,status=x["status"],reason=x["reason"]))
    print(json.dumps(dict(status="PASS",summary=summary,evidence=d,api_negative=api),sort_keys=True))

if __name__=="__main__":run()
