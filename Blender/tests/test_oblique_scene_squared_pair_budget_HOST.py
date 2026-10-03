"""Independent canonical RN/box/error budget audit; sealed products never replayed."""
from pathlib import Path
from fractions import Fraction as F
import json,hashlib,copy,runpy
ROOT=Path(__file__).resolve().parents[2]
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-BOX-PRODUCT-EFT-CPU-001-CODEX.json"
PSHA="5ab5e9df53f03d6f5fb5bb95fd718fb269babcc0c624902935c3f5540101b007"
prior=runpy.run_path(str(ROOT/"Blender/tests/test_oblique_scene_box_product_EFT_CPU64.py"))
capture,digest,pair,pf,nearest=map(prior.get,("capture","digest","pair","pf","nearest"))
MODEL="oblique-scene-squared-pair-budget-HOST-v1"
POLICY="CANONICAL_RN_HI_RN_RESIDUAL_LO_ORIGINAL_BOX_ONLY"

def retained():
    raw=(ROOT/PARENT).read_bytes();assert len(raw)==79023 and hashlib.sha256(raw).hexdigest()==PSHA
    r=json.loads(raw);pins=dict(r["code_doc_sha256"]);assert len(pins)==276;pins[PARENT]=PSHA
    for p,h in pins.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    d=capture(r["test_run"])["evidence"];ref,orig,_,_=prior["retained"]()
    return {x["id"]:x for x in d["records"]},ref,orig,pins,d

def selector(k,e,reference,orig):
    o=orig[k];q=o.get("scene_query",o["request"].get("scene_query"))
    return dict(backend=MODEL,policy=POLICY,record_id=k,parent_receipt_sha256=PSHA,
        parent_record_sha256=digest(e[k]),reference_record_sha256=digest(reference[k]),
        original_record_sha256=digest(o),original_snapshot_sha256=digest(o["scene"]),original_query_sha256=digest(q))

def compression(c,v,L):
    assert c["exact_squared"]==pair(v)and c["length_lower_bound"]==pair(L)and L>0 and L*L<=v
    h=nearest(c["hi_word"],v);l=nearest(c["lo_word"],v-h);Q=h+l;R=v-Q
    assert Q>0 and L*L<=Q and c["candidate_sum"]==pair(Q)and c["residual"]==pair(R)
    assert c["canonical_exact"]is(R==0)
    budget=abs(R)/(2*L)
    assert c["length_error_bound"]==pair(budget)and c["squared_enclosure"]==[pair(Q-abs(R)),pair(Q+abs(R))]
    assert Q-abs(R)<=v<=Q+abs(R)
    # Independently certify root-distance bound without evaluating any root.
    lhs=abs(v-Q)-budget*budget
    if lhs>0:assert lhs*lhs<=4*budget*budget*min(v,Q)
    status="HOST_CANONICAL_PAIR_EXACT_ONLY"if R==0 else"STOP_CANONICAL_PAIR_EXACT_SUM"
    reason="canonical_pair_exact_not_native_sum"if R==0 else"nonzero_canonical_residual_preserved"
    assert(c["status"],c["reason"])==(status,reason)
    assert c["HOST_float_casts"]==2 and c["HOST_bound_divisions"]==1
    return R,budget

def scope(r):
    assert r["backend"]==MODEL and r["promotion"]=="STOP_NATIVE_LENGTH_PHASE_PHYSICAL_GPU"
    assert r["full_costs"]=="UNKNOWN_NOT_ZERO"and r["bound_scope"]=="ISOLATED_HOST_CANONICAL_COMPRESSION_NOT_TOTAL_PIPELINE"
    for k in ("CPU_native_arithmetic","source_uncertainty_cancelled","phase_certified","wavelength_known","physical_reference_certified","GPU_used"):assert r[k]is False
    for k in ("native_sum","native_length","phase_error_bound"):assert r[k]is None
    for k in ("native_root_calls","new_products","new_transport_calls","new_predicate_calls","retained_suite_replays"):assert r[k]==0

def verify_capture(d, verify_parent=True):
    e,reference,orig,pins,old=retained();assert d["pins"]==pins
    if verify_parent:assert prior["verify_capture"](old)["status"]=="PASS" # bit/rational ONLY
    assert len(d["records"])==16 and {x["id"]for x in d["records"]}==set(e)
    exact=lost=stops=casts=words=divisions=0;results={}
    for x in d["records"]:
        k=x["id"];r=x["result"];scope(r)
        assert x["request"]==selector(k,e,reference,orig)and r["request_sha256"]==digest(x["request"])
        p=e[k]["result"];assert r["upstream_status"]==p["status"]
        if p["status"]!="CPU64_ORIGINAL_BOX_PRODUCTS_ONLY":
            assert r["status"]=="STOP_UPSTREAM"and r["reason"]=="sealed_STOP_not_rescued"and r["diagnostic"]is None
            assert r["HOST_float_casts"]==r["HOST_word_decodes"]==r["HOST_bound_divisions"]==0
            stops+=1;continue
        original=orig[k]["scene"];box={}
        for n in ("origin","detector"):
            box[n]=[(F(*v)-F(*rad),F(*v)+F(*rad))for v,rad in zip(original["points"][n]["nominal"],original["points"][n]["radius"])]
        delta=[(b[0]-a[1],b[1]-a[0])for a,b in zip(box["origin"],box["detector"])]
        squares=[(F(0)if a<=0<=b else min(a*a,b*b),max(a*a,b*b))for a,b in delta]
        S=sum(v[0]for v in squares),sum(v[1]for v in squares);z=r["diagnostic"]
        assert z["squared_original"]==[pair(v)for v in S]and z["original_snapshot_sha256"]==digest(original)
        assert z["reference_record_sha256"]==digest(reference[k])
        rz=reference[k]["result"]["diagnostic"];assert z["squared_original"]==rz["extrema"]["squared"]
        assert z["geometric_reference_width"]==rz["reference_width"]and z["source"]=="SOURCE0"and z["detector"]=="DETECTOR0"
        assert z["units_squared"]=="scene_length_squared"and z["units_bound"]=="scene_length"
        L=F(*rz["reference_interval"][0]);assert len(z["candidate_compressions"])==2
        audit=[compression(c,v,L)for c,v in zip(z["candidate_compressions"],S)]
        nonzero=any(a!=0 for a,b in audit);budget=max(b for a,b in audit);width=F(*rz["reference_width"])
        assert width>0 and z["max_length_error_bound"]==pair(budget)and z["error_bound_over_box_width"]==pair(budget/width)
        status="STOP_CANONICAL_PAIR_EXACT_SUM"if nonzero else"HOST_CANONICAL_PAIR_EXACT_ONLY"
        reason="nonzero_canonical_residual_preserved"if nonzero else"canonical_pair_exact_not_native_sum"
        assert(r["status"],r["reason"])==(status,reason)
        assert r["HOST_float_casts"]==4 and r["HOST_word_decodes"]==48 and r["HOST_bound_divisions"]==3
        if nonzero:lost+=1
        else:exact+=1
        casts+=4;words+=48;divisions+=3
        results[k]=dict(residuals=[str(a)for a,b in audit],max_length_error_bound=str(budget),bound_over_box_width=str(budget/width),status=status)
    assert(exact,lost,stops,casts,words,divisions)==(1,1,14,8,96,6)
    assert len(d["invalid"])==8
    for x in d["invalid"]:
        r=x["result"];scope(r);assert r["status"]=="STOP_INPUT"and r["reason"]=="closed_selector"and r["diagnostic"]is None
        assert r["HOST_float_casts"]==r["HOST_word_decodes"]==r["HOST_bound_divisions"]==0
    assert len(d["controls"])==4
    for c in d["controls"]:
        assert c["status"]=="STOP_INPUT"and c["reason"]=="positive_certified_domain"and c["HOST_float_casts"]==0 and c["HOST_bound_divisions"]==0
    return dict(status="PASS",canonical_exact_scene=exact,canonical_loss_STOP_scene=lost,upstream_STOP=stops,
        invalid=8,controls=4,inherited_pins=len(pins),HOST_casts=casts,HOST_word_decodes=words,HOST_divisions=divisions,
        new_native_products=0,new_native_roots=0,native_sum=False,phase=False,results=results)

def mutations(d):
    checks=[]
    for name in ("erase_residual","zero_error_budget","false_common_lower","wrong_original_sum","cancel_SOURCE","promote_phase","rescue_exactness_STOP","wrong_reference_query"):
        m=copy.deepcopy(d);x=next(x for x in m["records"]if x["result"]["status"]=="STOP_CANONICAL_PAIR_EXACT_SUM");r=x["result"];z=r["diagnostic"];c=z["candidate_compressions"][0]
        if name=="erase_residual":c["residual"]=[0,1]
        elif name=="zero_error_budget":c["length_error_bound"]=[0,1]
        elif name=="false_common_lower":c["length_lower_bound"]=[2,1]
        elif name=="wrong_original_sum":z["squared_original"][0]=[1,1]
        elif name=="cancel_SOURCE":r["source_uncertainty_cancelled"]=True
        elif name=="promote_phase":r["phase_certified"]=True
        elif name=="rescue_exactness_STOP":r["status"]="HOST_CANONICAL_PAIR_EXACT_ONLY"
        else:x["request"]["original_query_sha256"]="0"*64
        # Parent proof already checked by caller; unchanged parent SHA/pins are rechecked.
        try:verify_capture(m, verify_parent=False)
        except(AssertionError,ValueError,KeyError):checks.append(name)
        else:raise AssertionError("mutation_not_rejected:"+name)
    return checks

def run():
    import oblique_scene_squared_pair_budget_HOST_v1 as b
    e,ref,orig,pins=b.retained();records=[]
    for k in e:
        q=b.selector(k,e,ref,orig);records.append(dict(id=k,request=q,result=b._audit(q,e,ref,orig)))
    k=next(k for k in e if e[k]["result"]["status"]=="CPU64_ORIGINAL_BOX_PRODUCTS_ONLY")
    invalid=[]
    for name in ("backend","policy","parent_receipt_sha256","parent_record_sha256","reference_record_sha256","original_snapshot_sha256","original_query_sha256","extra"):
        q=b.selector(k,e,ref,orig);q[name]="wrong";invalid.append(dict(id=name,request=q,result=b._audit(q,e,ref,orig)))
    controls=[b.compress(v,L)for v,L in ((None,F(1)),(F(-1),F(1)),(F(1),F(0)),(F(1),F(2)))]
    d=dict(pins=pins,records=records,invalid=invalid,controls=controls)
    summary=verify_capture(d);summary["mutations_rejected"]=mutations(d)
    print(json.dumps(dict(evidence=d,summary=summary),sort_keys=True,separators=(",",":")))
if __name__=="__main__":run()
