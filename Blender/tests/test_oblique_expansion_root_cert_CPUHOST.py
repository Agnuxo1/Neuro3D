"""Independent sqrt rounding, IEEE-step trace and rational box certificates."""
from pathlib import Path
from fractions import Fraction as F
import json, hashlib, copy, struct, runpy
ROOT = Path(__file__).resolve().parents[2]
prior = runpy.run_path(str(ROOT/"Blender/tests/test_oblique_scene_squared_expansion_CPU64.py"))
capture, digest, pair, pf = (prior[n] for n in ("capture","digest","pair","pf"))
basebits = prior["prior"]["prior"]
bits, adjacent = basebits["bits"], basebits["adjacent"]
MODEL = "oblique-expansion-root-cert-CPUHOST-v1"
POLICY = "SEALED_EXPANSION_NATIVE_SQRT_SEED_HOST_IEEE_FIXED2_CERT"
PARENT = "coordinacion/respuestas/PRECISION-OBLIQUE-SQUARED-EXPANSION-CPU-001-CODEX.json"
PSHA = "11cf94df8acf19163cbd6a6dc01628ae8e3160bf85527f144368b362dab685e7"


def retained():
    raw = (ROOT/PARENT).read_bytes()
    assert len(raw) == 151262 and hashlib.sha256(raw).hexdigest() == PSHA
    r = json.loads(raw)
    pins = dict(r["code_doc_sha256"])
    assert len(pins) == 284
    for p,h in pins.items(): assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest() == h,p
    d = capture(r["test_run"])["evidence"]
    _, _, reference, orig, _, _ = prior["retained"]()
    pins[PARENT] = PSHA
    return {x["id"]:x for x in d["records"]}, reference, orig, pins, d


def selector(k,e,reference,orig):
    o = orig[k]
    q = o.get("scene_query",o["request"].get("scene_query"))
    return dict(backend=MODEL,policy=POLICY,record_id=k,parent_receipt_sha256=PSHA,
                parent_record_sha256=digest(e[k]),reference_record_sha256=digest(reference[k]),
                original_record_sha256=digest(o),original_snapshot_sha256=digest(o["scene"]),
                original_query_sha256=digest(q))


def rootproof(r,words):
    assert r["input_words"] == words and 1 <= len(words) <= 4 and r["max_steps_per_side"] == 2
    for w in words:
        v=pf(w);assert v==0 or abs(v)>=F(1,2**1022);assert abs(v)<=2**66
    S=sum((pf(w)for w in words),F(0));H=pf(words[-1])
    assert 0<S<=2**66 and H>0 and r["exact_squared"] == pair(S)
    assert r["seed_input_word"] == words[-1] and r["sqrt_calls"] == 1
    assert r["HOST_float_casts"] == 0 and r["engine_native_length"] is False
    w=r["seed_word"];Y=pf(w);assert Y>0
    A,B=pf(adjacent(w,False)),pf(adjacent(w,True))
    mn,mx=((A+Y)/2)**2,((Y+B)/2)**2
    assert mn<=H<=mx and (mn<H<mx or bits(w)%2==0) # no sqrt execution
    checks,steps=r["HOST_checks"],r["HOST_bit_steps"]
    ci=si=0;ends=[w,w]
    for sidei,side in enumerate(("lower","upper")):
        cur,n=w,0
        while True:
            v=pf(cur);holds=v*v<=S if side=="lower"else v*v>=S
            assert checks[ci] == dict(side=side,candidate_word=cur,square=pair(v*v),holds=holds)
            ci+=1
            if holds:break
            if n==2:
                assert r["status"]=="STOP_CAPACITY" and r["reason"]=="fixed2_enclosure_capacity"
                assert ci==len(checks) and si==len(steps)
                assert r["interval_words"] is None and r["length_error_bound"] is None and r["HOST_bound_divisions"]==0
                assert r["partial_interval_words"]==ends
                return dict(sqrt_calls=1,bit_steps=si,checks=ci,capacity_STOP=True)
            nxt=adjacent(cur,side=="upper")
            assert steps[si]==dict(side=side,from_word=cur,to_word=nxt,integer_delta=-1 if side=="lower"else 1)
            assert 0<pf(nxt) and pf(nxt)>=F(1,2**1022)
            si+=1;n+=1;cur=nxt;ends[sidei]=cur
        ends[sidei]=cur
    assert ci==len(checks) and si==len(steps)
    assert r["status"]=="CPU64_SEED_HOST_CERTIFIED_EXPANSION_ROOT_ONLY"and r["reason"]=="mixed_certificate_not_native_length"
    assert r["interval_words"]==r["partial_interval_words"]==ends
    L,U=map(pf,ends);assert 0<L<=U and L*L<=S<=U*U and L*L<=Y*Y
    residual=S-Y*Y;budget=abs(residual)/(2*L)
    assert r["seed_squared_residual"]==pair(residual)and r["length_error_bound"]==pair(budget)
    assert r["HOST_bound_divisions"]==1
    lhs=abs(residual)-budget*budget
    if lhs>0:assert lhs*lhs<=4*budget*budget*min(S,Y*Y)
    return dict(sqrt_calls=1,bit_steps=si,checks=ci,capacity_STOP=False)


def scope(r):
    assert r["backend"]==MODEL and r["scope"]=="NATIVE_SQRT_SEED_HOST_CERTIFICATE_ORIGINAL_BOX_ONLY"
    assert r["promotion"]=="STOP_NATIVE_ENGINE_PHASE_PHYSICAL_GPU" and r["full_costs"]=="UNKNOWN_NOT_ZERO"
    for n in ("new_sums","new_products","new_transport_calls","new_predicate_calls","retained_suite_replays","HOST_float_casts"):assert r[n]==0
    for n in ("source_uncertainty_cancelled","phase_certified","wavelength_known","physical_reference_certified","GPU_used"):assert r[n]is False
    assert r["native_length"]is None and r["phase_error_bound"]is None


def verify_capture(d,verify_parent=True):
    e,reference,orig,pins,old=retained();assert d["pins"]==pins
    if verify_parent:assert prior["verify_capture"](old)["status"]=="PASS"
    assert len(d["records"])==16 and {x["id"]for x in d["records"]}==set(e)
    scenes=stops=calls=steps=checks=0;meta={}
    for x in d["records"]:
        k,r=x["id"],x["result"];scope(r)
        assert x["request"]==selector(k,e,reference,orig) and r["request_sha256"]==digest(x["request"])
        p=e[k]["result"];assert r["upstream_status"]==p["status"]and r["retained_canonical_status"]==p["retained_canonical_status"]
        if p["status"]!="CPU64_ORIGINAL_BOX_SQUARED_EXPANSIONS_ONLY":
            assert r["status"]=="STOP_UPSTREAM"and r["reason"]=="sealed_STOP_not_rescued"and r["diagnostic"]is None and r["sqrt_calls"]==0
            stops+=1;continue
        assert r["status"]=="CPU64_ROOT_SEEDS_HOST_ORIGINAL_BOX_LENGTH_CERTIFICATE_ONLY"and r["reason"]=="mixed_original_box_certificate_not_native_engine"
        z,rz=r["diagnostic"],reference[k]["result"]["diagnostic"]
        assert z["original_snapshot_sha256"]==digest(orig[k]["scene"])and z["source"]=="SOURCE0"and z["detector"]=="DETECTOR0"and z["units"]=="scene_length"
        assert len(z["roots"])==2
        for i,entry in enumerate(z["roots"]):
            assert entry["bound"]==("lower","upper")[i]
            words=p["diagnostic"]["sums"][i]["result"]["component_words"]
            g=rootproof(entry["result"],words)
            assert not g["capacity_STOP"]and entry["result"]["exact_squared"]==rz["extrema"]["squared"][i]
            calls+=1;steps+=g["bit_steps"];checks+=g["checks"]
        a,b=(v["result"]for v in z["roots"])
        L,U=pf(a["interval_words"][0]),pf(b["interval_words"][1])
        Slo,Shi=(F(*v)for v in rz["extrema"]["squared"])
        assert L*L<=Slo<=Shi<=U*U and 0<L<=U # whole original box via monotonicity
        rl,rh=(F(*v)for v in rz["reference_interval"]);rw=rh-rl
        assert z["HOST_certified_words"]==[a["interval_words"][0],b["interval_words"][1]]
        assert z["HOST_certified_length_interval"]==[pair(L),pair(U)]
        assert z["reference_interval"]==rz["reference_interval"] and z["reference_width"]==rz["reference_width"]
        width=U-L;assert z["interval_width"]==pair(width)and z["width_over_reference"]==pair(width/rw)
        assert z["interval_minus_reference"]==[pair(L-rl),pair(U-rh)]and z["HOST_width_ratio_divisions"]==1
        budget=max(F(*a["length_error_bound"]),F(*b["length_error_bound"]))
        assert z["max_seed_length_error_bound"]==pair(budget)and r["sqrt_calls"]==2
        meta[k]=dict(width=str(width),width_over_reference=str(width/rw),max_seed_length_error_bound=str(budget),
                     reference_width=str(rw),certified_words=z["HOST_certified_words"])
        scenes+=1
    assert (scenes,stops,calls)==(2,14,4)
    assert len(d["invalid"])==8
    for x in d["invalid"]:
        r=x["result"];scope(r);assert r["status"]=="STOP_INPUT"and r["reason"]=="closed_selector"and r["diagnostic"]is None and r["sqrt_calls"]==0
    assert len(d["controls"])==3
    controlproof=[rootproof(r,r["input_words"])for r in d["controls"]]
    assert all(not r["capacity_STOP"]for r in controlproof)
    fail=rootproof(d["capacity_STOP"],d["capacity_STOP"]["input_words"])
    assert fail==dict(sqrt_calls=1,bit_steps=2,checks=3,capacity_STOP=True)
    assert len(d["precontrols"])==7
    for r in d["precontrols"]:
        assert r["status"]=="STOP_INPUT"and r["sqrt_calls"]==0 and r["seed_word"]is None and r["interval_words"]is None
        assert r["HOST_checks"]==r["HOST_bit_steps"]==[]and r["HOST_bound_divisions"]==0
    return dict(status="PASS",scenes=2,upstream_STOP=14,scene_sqrt_calls=4,scene_HOST_bit_steps=steps,
                scene_HOST_checks=checks,controls=3,capacity_STOP=True,precontrols=7,selectors_rejected=8,
                total_new_sqrt_calls=8,total_HOST_bit_steps=steps+sum(v["bit_steps"]for v in controlproof)+2,
                inherited_pins=285,by_scene=meta)


def mutations(d):
    k=next(i for i,x in enumerate(d["records"])if x["result"]["diagnostic"]is not None)
    rejected=0
    for n in range(8):
        a=copy.deepcopy(d);r=a["records"][k]["result"];z=r["diagnostic"];root=z["roots"][0]["result"]
        if n==0:root["seed_word"]="0000000000000000"
        elif n==1:root["max_steps_per_side"]=3
        elif n==2:root["HOST_checks"][0]["holds"]=not root["HOST_checks"][0]["holds"]
        elif n==3:root["exact_squared"]=[0,1]
        elif n==4:z["HOST_certified_words"][0]="0000000000000000"
        elif n==5:r["phase_certified"]=True
        elif n==6:r["retained_canonical_status"]="PASS"
        else:a["capacity_STOP"]["status"]="CPU64_SEED_HOST_CERTIFIED_EXPANSION_ROOT_ONLY"
        try:verify_capture(a,verify_parent=False)
        except (AssertionError,ValueError,TypeError,IndexError,KeyError):rejected+=1
        else:raise AssertionError("mutation_accepted:"+str(n))
    return rejected


def run():
    import oblique_expansion_root_cert_CPUHOST_v1 as core
    e,reference,orig,pins=core.retained();records=[]
    for k in e:
        q=core.selector(k,e,reference,orig)
        records.append(dict(id=k,request=q,result=core._audit(q,e,reference,orig)))
    k=next(x["id"]for x in records if x["result"]["diagnostic"]is not None)
    q=core.selector(k,e,reference,orig);invalid=[]
    for n in range(8):
        bad=dict(q)
        if n==0:bad["policy"]="raise_limit"
        elif n==1:bad["wavelength"]="500"
        elif n==2:bad["backend"]="GPU"
        elif n==3:bad["parent_record_sha256"]="0"*64
        elif n==4:bad["original_snapshot_sha256"]="0"*64
        elif n==5:bad["parent_receipt_sha256"]="0"*64
        elif n==6:bad["original_query_sha256"]=0
        else:bad.pop("reference_record_sha256")
        invalid.append(dict(request=bad,result=core._audit(bad,e,reference,orig)))
    w=lambda x:struct.pack("<d",x).hex()
    controls=[core.root([w(1.0)]),core.root([w(2.0)]),core.root([w(2.0**-120),w(2.0**-60),w(1.0)])]
    failure=core.root([w(-0.5),w(1.0)])
    pre=[core.root(a)for a in ([],[w(1.0)]*5,[True],[w(float("inf"))],[w(2.0**-1074)],[w(0.0)],[w(-1.0)])]
    d=dict(records=records,invalid=invalid,controls=controls,capacity_STOP=failure,precontrols=pre,pins=pins)
    v=verify_capture(d);v["mutations_rejected"]=mutations(d);assert v["mutations_rejected"]==8
    print(json.dumps(dict(status="PASS",summary=v,evidence=d),sort_keys=True,separators=(",",":")))


if __name__=="__main__":run()
