"""Bit/rational audit of new native residual and hi-lo correction, no sqrt replay."""
from pathlib import Path
from fractions import Fraction as F
import json, hashlib, copy, runpy, struct
ROOT = Path(__file__).resolve().parents[2]
prior = runpy.run_path(str(ROOT/"Blender/tests/test_oblique_expansion_root_cert_CPUHOST.py"))
exptest = prior["prior"]
producttest = exptest["prior"]["prior"]
capture,digest,pair,pf = (prior[n] for n in ("capture","digest","pair","pf"))
nearest = producttest["nearest"]
MODEL = "oblique-root-hilo-correction-CPU64-v1"
POLICY = "SEALED_SEED_EFT_SQUARE_FIXED4_RESIDUAL_NATIVE_DELTA_HOST_BOUND"
PARENT = "coordinacion/respuestas/PRECISION-OBLIQUE-EXPANSION-ROOT-CERT-CPUHOST-001-CODEX.json"
PSHA = "443b99eed81223011ddb0c910a4d13c43d640e164131c6b6c9c5a5a58baf0645"


def retained():
    raw=(ROOT/PARENT).read_bytes();assert len(raw)==144195 and hashlib.sha256(raw).hexdigest()==PSHA
    r=json.loads(raw);pins=dict(r["code_doc_sha256"]);assert len(pins)==288
    for p,h in pins.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    d=capture(r["test_run"])["evidence"];expansions,reference,orig,_,_=prior["retained"]()
    pins[PARENT]=PSHA
    return {x["id"]:x for x in d["records"]},expansions,reference,orig,pins,d


def selector(k,e,expansions,reference,orig):
    o=orig[k];q=o.get("scene_query",o["request"].get("scene_query"))
    return dict(backend=MODEL,policy=POLICY,record_id=k,parent_receipt_sha256=PSHA,
                parent_record_sha256=digest(e[k]),expansion_record_sha256=digest(expansions[k]),
                reference_record_sha256=digest(reference[k]),original_record_sha256=digest(o),
                original_snapshot_sha256=digest(o["scene"]),original_query_sha256=digest(q))


def correction(r,words,seed,lower):
    assert r["input_words"]==words and r["seed_word"]==seed and r["lower_word"]==lower
    assert r["new_sqrt_calls"]==r["HOST_float_casts"]==0 and r["full_costs"]=="UNKNOWN_NOT_ZERO"
    S=sum((pf(w)for w in words),F(0));Y,L=pf(seed),pf(lower)
    assert 0<S<=2**66 and 0<Y<=2**32 and 0<L<=Y and L*L<=S and r["exact_squared"]==pair(S)
    p=r["square"];assert p["a_word"]==p["b_word"]==seed
    pn=producttest["graph"](p,Y,Y);assert r["new_products"]==1
    if p["status"]!="CPU64_EFT_PRODUCT_ONLY":
        assert r["status"]=="STOP_INPUT"and r["reason"]=="square_STOP:"+p["reason"]
        assert r["residual"]is None and r["scalar_ledger"]==[]and r["root_pair_words"]is None
        assert r["RN_nodes_executed"]==pn and r["new_sums"]==0 and r["HOST_bound_divisions"]==0
        return dict(RN=pn,products=1,sums=0,accepted=False)
    for t in p["ledger"]:
        for n in ("a","b","y"):
            v=pf(t[n]);assert v==0 or abs(v)>=F(1,2**1022)
    neg=[(int.from_bytes(bytes.fromhex(p[n]),"little")^(1<<63)).to_bytes(8,"little").hex()for n in ("hi_word","lo_word")]
    assert r["negated_square_words"]==neg
    assert all(pf(a)==-pf(p[n])for a,n in zip(neg,("hi_word","lo_word")))
    residue=r["residual"];gn=exptest["graph"](residue,words+neg);assert r["new_sums"]==1
    if residue["status"]!="CPU64_EXACT_GROW_EXPANSION_SUM_ONLY":
        assert residue["status"]=="STOP_CAPACITY"and r["status"]=="STOP_INPUT"and r["reason"]=="residual_fixed4_STOP"
        assert r["scalar_ledger"]==[]and r["root_pair_words"]is None and r["HOST_bound_divisions"]==0
        assert r["RN_nodes_executed"]==pn+gn
        return dict(RN=pn+gn,products=1,sums=1,accepted=False)
    R=sum((pf(w)for w in residue["component_words"]),F(0));assert R==S-Y*Y
    ledger=r["scalar_ledger"];assert len(ledger)==2
    den,low=ledger
    assert (den["index"],den["name"],den["op"],den["a"],den["b"])==(0,"denominator","mul","0000000000000040",seed)
    D=nearest(den["y"],2*Y);assert D==2*Y
    assert (low["index"],low["name"],low["op"],low["a"],low["b"])==(1,"delta","div",residue["component_words"][-1],den["y"])
    delta=nearest(low["y"],pf(low["a"])/D)
    assert delta==0 or abs(delta)>=F(1,2**1022)
    assert abs(delta)<=2**33 and (delta!=0 or pf(low["a"])==0)
    Q=Y+delta;assert 0<Q<=2**33 and L*L<=Q*Q
    assert r["candidate_pair_words"]==r["root_pair_words"]==[seed,low["y"]]
    assert r["candidate_sum"]==pair(Q)and r["candidate_squared_residual"]==pair(S-Q*Q)
    B=abs(S-Q*Q)/(2*L)
    assert r["length_error_bound"]==pair(B)and r["HOST_enclosure"]==[pair(Q-B),pair(Q+B)]
    assert Q-B>0 and (Q-B)**2<=S<=(Q+B)**2 # enclosure without evaluating sqrt
    assert r["HOST_bound_divisions"]==1 and r["RN_nodes_executed"]==pn+gn+2
    assert r["status"]=="CPU64_NATIVE_ROOT_PAIR_HOST_BOUND_ONLY"and r["reason"]=="one_native_correction_not_engine"
    return dict(RN=pn+gn+2,products=1,sums=1,accepted=True)


def scope(r):
    assert r["backend"]==MODEL and r["promotion"]=="STOP_NATIVE_SCENE_ENGINE_PHASE_PHYSICAL_GPU"
    assert r["scope"]=="NATIVE_PAIR_CORRECTION_OF_SEALED_SEED_HOST_BOUND_ORIGINAL_BOX_ONLY"and r["full_costs"]=="UNKNOWN_NOT_ZERO"
    for n in ("new_sqrt_calls","HOST_float_casts","retained_suite_replays"):assert r[n]==0
    for n in ("phase_certified","wavelength_known","physical_reference_certified","GPU_used","source_uncertainty_cancelled"):assert r[n]is False
    assert r["native_length"]is None and r["phase_error_bound"]is None


def verify_capture(d,verify_parent=True):
    e,expansions,reference,orig,pins,old=retained();assert d["pins"]==pins
    if verify_parent:assert prior["verify_capture"](old)["status"]=="PASS"
    assert len(d["records"])==16 and {x["id"]for x in d["records"]}==set(e)
    scenes=stops=nodes=products=sums=0;meta={}
    for x in d["records"]:
        k,r=x["id"],x["result"];scope(r)
        assert x["request"]==selector(k,e,expansions,reference,orig)and r["request_sha256"]==digest(x["request"])
        p=e[k]["result"];assert r["upstream_status"]==p["status"]and r["retained_canonical_status"]==p["retained_canonical_status"]
        if p["status"]!="CPU64_ROOT_SEEDS_HOST_ORIGINAL_BOX_LENGTH_CERTIFICATE_ONLY":
            assert r["status"]=="STOP_UPSTREAM"and r["reason"]=="sealed_STOP_not_rescued"and r["diagnostic"]is None
            assert r["RN_nodes_executed"]==r["new_products"]==r["new_sums"]==0
            stops+=1;continue
        assert r["status"]=="CPU64_SEALED_ROOT_PAIR_CORRECTIONS_HOST_BOUNDS_ONLY"and r["reason"]=="paired_native_correction_host_bound_not_scene_engine"
        z,rz=r["diagnostic"],reference[k]["result"]["diagnostic"]
        assert z["original_snapshot_sha256"]==digest(orig[k]["scene"])and(z["source"],z["detector"],z["units"])==("SOURCE0","DETECTOR0","scene_length")
        assert len(z["corrections"])==2
        n=0
        for i,v in enumerate(z["corrections"]):
            root=p["diagnostic"]["roots"][i]["result"]
            words=expansions[k]["result"]["diagnostic"]["sums"][i]["result"]["component_words"]
            assert v["bound"]==("lower","upper")[i]and root["input_words"]==words
            a=correction(v["result"],words,root["seed_word"],root["interval_words"][0]);assert a["accepted"]
            assert v["result"]["exact_squared"]==rz["extrema"]["squared"][i]
            n+=a["RN"];products+=a["products"];sums+=a["sums"]
        assert r["RN_nodes_executed"]==n and r["new_products"]==r["new_sums"]==2;nodes+=n
        a,b=(v["result"]for v in z["corrections"]);low,high=F(*a["HOST_enclosure"][0]),F(*b["HOST_enclosure"][1])
        Slo,Shi=(F(*v)for v in rz["extrema"]["squared"]);assert 0<low<=high and low*low<=Slo<=Shi<=high*high
        rw=F(*rz["reference_width"]);width=high-low;B=max(F(*a["length_error_bound"]),F(*b["length_error_bound"]))
        assert z["HOST_corrected_length_interval"]==[pair(low),pair(high)]and z["interval_width"]==pair(width)
        assert z["reference_width"]==rz["reference_width"]and z["reference_interval"]==rz["reference_interval"]
        assert z["width_over_reference"]==pair(width/rw)and z["max_pair_length_error_bound"]==pair(B)and z["error_bound_over_reference_width"]==pair(B/rw)
        assert z["HOST_ratio_divisions"]==2
        assert z["retained_seed_interval_width"]==p["diagnostic"]["interval_width"]and z["retained_seed_width_over_reference"]==p["diagnostic"]["width_over_reference"]
        meta[k]=dict(width=str(width),width_over_reference=str(width/rw),max_pair_length_error_bound=str(B),
                     error_bound_over_reference_width=str(B/rw),RN_nodes=n,root_pairs=[v["result"]["root_pair_words"]for v in z["corrections"]])
        scenes+=1
    assert (scenes,stops,products,sums)==(2,14,4,4)
    assert len(d["invalid"])==8
    for v in d["invalid"]:
        r=v["result"];scope(r);assert r["status"]=="STOP_INPUT"and r["reason"]=="closed_selector"and r["diagnostic"]is None
        assert r["RN_nodes_executed"]==r["new_products"]==r["new_sums"]==0
    assert len(d["controls"])==3
    good=[]
    for c,root in zip(d["controls"],old["controls"]):
        good.append(correction(c,root["input_words"],root["seed_word"],root["interval_words"][0]))
        assert good[-1]["accepted"]
    f=d["capacity_STOP"];cap=correction(f,f["input_words"],f["seed_word"],f["lower_word"])
    assert cap==dict(RN=77,products=1,sums=1,accepted=False)
    u=d["underflow_STOP"];under=correction(u,u["input_words"],u["seed_word"],u["lower_word"])
    assert under==dict(RN=9,products=1,sums=0,accepted=False)
    assert len(d["precontrols"])==7
    for r in d["precontrols"]:
        assert r["status"]=="STOP_INPUT"and r["square"]is None and r["residual"]is None and r["root_pair_words"]is None
        assert r["new_sums"]==r["new_products"]==r["RN_nodes_executed"]==r["new_sqrt_calls"]==0
    return dict(status="PASS",scenes=2,upstream_STOP=14,scene_products=4,scene_sums=4,scene_RN_nodes=nodes,
                control_RN_nodes=sum(x["RN"]for x in good),capacity_STOP_RN=77,underflow_STOP_RN=9,
                total_new_RN_nodes=nodes+sum(x["RN"]for x in good)+86,total_new_products=9,total_new_sums=8,
                new_sqrt_calls=0,capacity_STOP=True,underflow_STOP=True,selectors_rejected=8,precontrols=7,
                inherited_pins=289,by_scene=meta)


def mutations(d):
    k=next(i for i,x in enumerate(d["records"])if x["result"]["diagnostic"]is not None);rejects=0
    for n in range(8):
        a=copy.deepcopy(d);r=a["records"][k]["result"];z=r["diagnostic"];c=z["corrections"][0]["result"]
        if n==0:c["root_pair_words"][1]="0000000000000000"
        elif n==1:c["square"]["lo_word"]="0000000000000000"
        elif n==2:c["residual"]["max_components"]=5
        elif n==3:c["scalar_ledger"][1]["a"]=c["seed_word"]
        elif n==4:c["length_error_bound"]=[1,1]
        elif n==5:r["source_uncertainty_cancelled"]=True
        elif n==6:r["phase_certified"]=True
        else:a["capacity_STOP"]["status"]="CPU64_NATIVE_ROOT_PAIR_HOST_BOUND_ONLY"
        try:verify_capture(a,verify_parent=False)
        except (AssertionError,ValueError,TypeError,IndexError,KeyError):rejects+=1
        else:raise AssertionError("mutation_accepted:"+str(n))
    return rejects


def run():
    import oblique_root_hilo_correction_CPU64_v1 as core
    e,exps,ref,orig,pins,old=core.retained();records=[]
    for k in e:
        q=core.selector(k,e,exps,ref,orig);records.append(dict(id=k,request=q,result=core._audit(q,e,exps,ref,orig)))
    k=next(x["id"]for x in records if x["result"]["diagnostic"]is not None);q=core.selector(k,e,exps,ref,orig);invalid=[]
    for n in range(8):
        bad=dict(q)
        if n==0:bad["policy"]="raise_capacity"
        elif n==1:bad["wavelength"]="500"
        elif n==2:bad["backend"]="GPU"
        elif n==3:bad["parent_record_sha256"]="0"*64
        elif n==4:bad["expansion_record_sha256"]="0"*64
        elif n==5:bad["original_snapshot_sha256"]="0"*64
        elif n==6:bad["original_query_sha256"]=0
        else:bad.pop("reference_record_sha256")
        invalid.append(dict(request=bad,result=core._audit(bad,e,exps,ref,orig)))
    controls=[core.refine(r["input_words"],r["seed_word"],r["interval_words"][0])for r in old["controls"]]
    w=lambda x:struct.pack("<d",x).hex();one,half=w(1.0),w(0.5)
    failure=core.refine([w(2.0**n)for n in (-240,-180,-120,-60)],one,w(2.0**-31))
    under=core.refine([w(2.0**-1000)],w(2.0**-600),w(2.0**-601))
    pre=[core.refine(a,b,c)for a,b,c in (([],one,half),([one]*5,one,half),([True],one,half),
         ([w(float("inf"))],one,half),([w(2.0**-1074)],one,half),([one],True,half),([one],one,w(2.0)))]
    d=dict(records=records,invalid=invalid,controls=controls,capacity_STOP=failure,underflow_STOP=under,precontrols=pre,pins=pins)
    v=verify_capture(d);v["mutations_rejected"]=mutations(d);assert v["mutations_rejected"]==8
    print(json.dumps(dict(status="PASS",summary=v,evidence=d),sort_keys=True,separators=(",",":")))


if __name__=="__main__":run()
