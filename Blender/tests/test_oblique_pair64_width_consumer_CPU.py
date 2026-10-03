"""Independent bit/rational fixed26 graph and scene width interval proof."""
from pathlib import Path
from fractions import Fraction as F
import json,hashlib,copy,runpy,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"Blender/benchmarks/capacity_audit"))
old=runpy.run_path(str(ROOT/"Blender/tests/test_oblique_scene_pair64_payload_CPU.py"))
hc=runpy.run_path(str(ROOT/"Blender/tests/test_oblique_root_hilo_correction_CPU64.py"))
capture,digest,pair,pf=(old[n]for n in ("capture","digest","pair","pf"))
nearest=hc["nearest"]
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-SCENE-PAIR64-PAYLOAD-CPU-001-CODEX.json"
PSHA="ed228edd01ecced262362ff2ac8853cba434ce1e359cdfa2385017294f9dbbe9"
MODEL="oblique-pair64-width-consumer-CPU-v1"
POLICY="FIXED26_RN64_PAIR_DIFFERENCE_PRESERVE_SEALED_WIDTH_EXACTLY"


def retained():
    raw=(ROOT/PARENT).read_bytes();assert len(raw)==242660 and hashlib.sha256(raw).hexdigest()==PSHA
    r=json.loads(raw);pins=dict(r["code_doc_sha256"]);assert len(pins)==311
    for p,h in pins.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    d=capture(r["test_run"])["evidence"];p={x["id"]:x for x in d["records"]}
    _,native,ref,orig,_,_,_=old["retained"]()
    pins[PARENT]=PSHA
    assert set(p)==set(native)==set(ref)==set(orig)and len(p)==16
    return p,native,ref,orig,pins,d


def selector(k,p,n,ref,orig):
    o=orig[k];q=o.get("scene_query",o["request"].get("scene_query"))
    return dict(backend=MODEL,policy=POLICY,record_id=k,parent_receipt_sha256=PSHA,
        producer_record_sha256=digest(p[k]),native_record_sha256=digest(n[k]),
        reference_record_sha256=digest(ref[k]),original_record_sha256=digest(o),
        original_snapshot_sha256=digest(o["scene"]),original_query_sha256=digest(q))


def normal(v):return v==0 or abs(v)>=F(1,2**1022)


def neg(w):return (int.from_bytes(bytes.fromhex(w),"little")^(1<<63)).to_bytes(8,"little").hex()


class PartialStop(Exception):pass


def graph(r,payload,B):
    assert r["input_payload_hex"]==payload and r["inherited_bound"]==pair(B)and r["fixed_RN_budget"]==26
    assert r["new_products"]==r["new_sqrt_calls"]==r["retained_numeric_replays"]==0 and r["full_costs"]=="UNKNOWN_NOT_ZERO"
    ws=[payload[16*i:16*i+16]for i in range(4)];assert len(payload)==64
    lh,ll,uh,ul=(pf(w)for w in ws);W=(uh+ul)-(lh+ll)
    assert 0<W<=2**34 and r["input_width"]==pair(W)and B>=0
    assert all(normal(v)and abs(v)<=2**33 for v in (lh,ll,uh,ul))
    assert (r["hex_bytes_calls"],r["input_word_reads"],r["float_decode_calls"],r["decoded_components"],r["sign_flips"])==(1,4,1,4,2)
    ledger=r["ledger"];index=0;stop_name=None

    def step(name,op,a,b):
        nonlocal index,stop_name
        assert index<len(ledger);x=ledger[index]
        assert (x["index"],x["name"],x["op"],x["a"],x["b"])==(index,name,op,a,b)
        target=pf(a)+pf(b)if op=="add"else pf(a)-pf(b)
        v=nearest(x["y"],target);index+=1
        if not(normal(v)and abs(v)<=2**34 and (v!=0 or target==0)):
            stop_name=name;raise PartialStop()
        return x["y"]

    def two(prefix,a,b):
        s=step(prefix+".s","add",a,b);bb=step(prefix+".bb","sub",s,a)
        ab=step(prefix+".ab","sub",s,bb);db=step(prefix+".db","sub",b,bb)
        da=step(prefix+".da","sub",a,ab);e=step(prefix+".err","add",da,db)
        assert pf(s)+pf(e)==pf(a)+pf(b)
        return s,e

    try:
        p=two("p",ws[2],neg(ws[0]));q=two("q",ws[3],neg(ws[1]))
        e=step("merge.e","add",p[1],q[0]);z=two("r",p[0],e)
        l=step("merge.l","add",z[1],q[1]);y=two("y",z[0],l)
    except PartialStop:
        assert r["status"]=="STOP_ALU"and r["reason"]=="normal_zero_no_underflow:"+stop_name
        assert r["candidate_pair_words"]is None and r["native_pair_width"]is None
        assert r["HOST_width_interval"]is None and r["HOST_signed_residual"]is None
        assert index==len(ledger)==r["RN_nodes_executed"]
        assert r["word_format_calls"]==3*index
        return dict(kind="ALU_STOP",RN=index,formats=3*index)
    assert index==len(ledger)==r["RN_nodes_executed"]==26
    assert r["candidate_pair_words"]==list(y)and r["word_format_calls"]==80
    C=pf(y[0])+pf(y[1]);E=W-C;T=B+abs(E)
    assert C>0 and r["native_pair_width"]==pair(C)
    assert r["HOST_signed_residual"]==pair(E)and r["HOST_arithmetic_error_bound"]==pair(abs(E))
    assert r["HOST_total_width_error_bound"]==pair(T)and r["HOST_width_interval"]==[pair(C-T),pair(C+T)]
    if E!=0:
        assert r["status"]=="STOP_PAIR_WIDTH_RESIDUAL"and r["reason"]=="nonzero_pair_width_residual";kind="LOSS"
    elif C-T<=0:
        assert r["status"]=="STOP_WIDTH_BUDGET"and r["reason"]=="width_budget_crosses_zero";kind="BUDGET_STOP"
    else:
        assert r["status"]=="CPU64_EXACT_PAIR_WIDTH_ONLY"and r["reason"]=="fixed26_pair_width_not_scene_or_phase";kind="EXACT"
    return dict(kind=kind,RN=26,formats=80,W=W,C=C,B=T,E=E)


def scope(r):
    assert r["backend"]==MODEL and r["scope"]=="NATIVE_CPU64_WIDTH_OF_SEALED_PAIR_LENGTH_BOUNDS_HOST_CERT_ONLY"
    assert r["promotion"]=="STOP_FULL_SCENE_PAIR64_PHASE_PHYSICAL_GPU_AND_COSTS"
    assert r["full_costs"]=="UNKNOWN_NOT_ZERO"and r["native_length"]is None and r["phase_error_bound"]is None
    assert r["new_products"]==r["new_sqrt_calls"]==r["retained_numeric_replays"]==0
    for p in ("phase_certified","wavelength_known","physical_reference_certified","GPU_used","Bpy_used",
              "shader_used","scene_engine_admitted","source_uncertainty_cancelled"):assert r[p]is False,p


def verify_capture(d,verify_parent=True):
    p,n,ref,orig,pins,parent=retained()
    if verify_parent:old["verify_capture"](parent)
    assert d["pins"]==pins and len(pins)==312
    assert len(d["records"])==16 and {x["id"]for x in d["records"]}==set(p)
    scenes=stops=accepted=0;totals=dict(RN=0,formats=0,hex=0,reads=0,decodes=0,components=0,signs=0);meta=[]
    def tally(r):
        for key,name in (("RN","RN_nodes_executed"),("formats","word_format_calls"),("hex","hex_bytes_calls"),
                         ("reads","input_word_reads"),("decodes","float_decode_calls"),
                         ("components","decoded_components"),("signs","sign_flips")):totals[key]+=r[name]
    for rec in d["records"]:
        k=rec["id"];q=selector(k,p,n,ref,orig);assert rec["request"]==q
        r=rec["result"];scope(r)
        assert r["request_sha256"]==digest(q)and r["upstream_status"]==p[k]["result"]["status"]
        assert r["retained_canonical_status"]==n[k]["result"]["retained_canonical_status"]
        if p[k]["result"]["status"]!="CPU_HOST_PAIR64_LENGTH_BYTES_ONLY":
            assert r["status"]=="STOP_UPSTREAM"and r["reason"]=="sealed_STOP_not_rescued"and r["diagnostic"]is None
            assert all(r[name]==0 for name in ("RN_nodes_executed","hex_bytes_calls","input_word_reads",
                         "float_decode_calls","decoded_components","sign_flips","word_format_calls"))
            stops+=1;continue
        z=r["diagnostic"];env=p[k]["result"]["envelope"];rz=ref[k]["result"]["diagnostic"]
        assert rz["original_scene"]==orig[k]["scene"]and rz["original_query"]==orig[k]["scene_query"]
        assert z["producer_envelope_sha256"]==digest(env)and z["original_snapshot_sha256"]==digest(orig[k]["scene"])
        assert (z["source"],z["detector"],z["units"])==("SOURCE0","DETECTOR0","scene_length")
        assert z["source_uncertainty_cancelled"]is False and z["legacy_ABI_status"]==env["legacy_ABI_status"]
        assert z["legacy_scalar_gate"]==env["legacy_scalar_gate"]=="STOP_SCALAR_PAIR_CONSUMPTION_LOSS"
        B=sum((F(*v["retained_length_error_bound"])for v in env["certificates"]),F(0))
        g=graph(z["consumer"],env["payload_hex"],B);tally(z["consumer"])
        for name in ("RN_nodes_executed","hex_bytes_calls","input_word_reads","float_decode_calls",
                     "decoded_components","sign_flips","word_format_calls"):assert r[name]==z["consumer"][name]
        roots=[[F(*x)for x in rr]for rr in rz["roots"]]
        refWI=[roots[1][0]-roots[0][1],roots[1][1]-roots[0][0]]
        assert z["retained_reference_width_interval"]==[pair(v)for v in refWI]
        assert z["retained_reference_outer_width"]==pair(refWI[1])==rz["reference_width"]
        # Reference root intervals certify each original squared endpoint separately.
        for rr,S in zip(roots,rz["extrema"]["squared"]):
            assert 0<rr[0]<=rr[1]and rr[0]**2<=F(*S)<=rr[1]**2
        c=z["consumer"];C,T=g["C"],g["B"]
        assert max(C-T,refWI[0])<=min(C+T,refWI[1])
        if g["kind"]=="EXACT":
            assert r["status"]=="CPU64_SCENE_PAIR_WIDTH_HOST_BOUND_ONLY"and r["reason"]=="native_width_partial_not_scene_engine"
            accepted+=1
        else:assert r["status"]=="STOP_WIDTH_CONSUMER"and r["reason"]==c["status"]+":"+c["reason"]
        meta.append(dict(id=k,native_width=str(C),exact_input_width=str(g["W"]),arithmetic_residual=str(g["E"]),
            HOST_width_interval=[str(C-T),str(C+T)],retained_reference_width_interval=[str(v)for v in refWI],
            composed_width_bound=str(T),status=r["status"],candidate_pair_words=c["candidate_pair_words"]))
        scenes+=1
    assert (scenes,stops)==(2,14)
    assert len(d["invalid"])==8
    for x in d["invalid"]:
        r=x["result"];scope(r)
        assert r["status"]=="STOP_INPUT"and r["reason"]=="closed_selector"and r["diagnostic"]is None
        assert r["RN_nodes_executed"]==r["hex_bytes_calls"]==r["float_decode_calls"]==0
    assert len(d["controls"])==2
    exact,loss=d["controls"]
    for r in d["controls"]:graph(r,r["input_payload_hex"],F(0));tally(r)
    assert exact["status"]=="CPU64_EXACT_PAIR_WIDTH_ONLY"and exact["input_width"]==pair(F(1,2**59))
    assert loss["status"]=="STOP_PAIR_WIDTH_RESIDUAL"and loss["HOST_signed_residual"]==pair(F(1,2**120))
    u=d["underflow_STOP"];g=graph(u,u["input_payload_hex"],F(0));assert g["RN"]==1 and u["ledger"][0]["y"]=="0100000000000000";tally(u)
    zero=d["zero_STOP"];assert zero["status"]=="STOP_INPUT"and zero["reason"]=="positive_width_domain"
    assert zero["RN_nodes_executed"]==zero["sign_flips"]==zero["word_format_calls"]==0
    assert zero["input_width"]==[0,1]and zero["candidate_pair_words"]is None;tally(zero)
    assert len(d["precontrols"])==8
    for r in d["precontrols"]:
        assert r["status"]=="STOP_INPUT"and r["RN_nodes_executed"]==r["sign_flips"]==r["word_format_calls"]==0
        assert r["candidate_pair_words"]is None and r["ledger"]==[];tally(r)
    assert totals==dict(RN=105,formats=323,hex=9,reads=30,decodes=7,components=28,signs=10),totals
    return dict(status="PASS",eligible_scenes=2,upstream_STOP=14,scene_width_exact=accepted,
        scene_width_rejected=2-accepted,scene_engine_admitted=0,selectors_rejected=8,
        exact_synthetic_width=1,third_component_loss_STOP=1,underflow_STOP=1,zero_width_STOP=1,precontrols=8,
        counted_scope="OWN_WIDTH_KERNEL_ONLY_ORACLES_IO_COST_UNKNOWN_NOT_ZERO",totals=totals,
        inherited_pins=312,new_products=0,new_sqrt_calls=0,retained_numeric_replays=0,by_scene=meta)


def mutations(d):
    k=next(i for i,x in enumerate(d["records"])if x["result"]["diagnostic"]is not None);rejected=0
    for i in range(8):
        a=copy.deepcopy(d);r=a["records"][k]["result"];z=r["diagnostic"];v=z["consumer"]
        if i==0:v["ledger"][0]["b"]="0000000000000000"
        elif i==1:v["RN_nodes_executed"]=25
        elif i==2:v["HOST_total_width_error_bound"]=[0,1]
        elif i==3:z["retained_reference_width_interval"]=[[0,1],[0,1]]
        elif i==4:r["source_uncertainty_cancelled"]=True
        elif i==5:r["GPU_used"]=True
        elif i==6:a["controls"][1]["status"]="CPU64_EXACT_PAIR_WIDTH_ONLY"
        else:a["underflow_STOP"]["candidate_pair_words"]=["0100000000000000","0000000000000000"]
        try:verify_capture(a,verify_parent=False)
        except (AssertionError,ValueError,TypeError,KeyError,IndexError):rejected+=1
        else:raise AssertionError("mutation_accepted:"+str(i))
    return rejected


def run():
    import oblique_pair64_width_consumer_CPU_v1 as c
    p,n,ref,orig,pins,_=c.retained();records=[]
    for k in p:
        q=c.selector(k,p,n,ref,orig);records.append(dict(id=k,request=q,result=c._audit(q,p,n,ref,orig)))
    q=next(x["request"]for x in records if x["result"]["diagnostic"]);invalid=[]
    for key in ("policy","backend","producer_record_sha256","native_record_sha256","reference_record_sha256",
                "original_snapshot_sha256","original_query_sha256","original_record_sha256"):
        bad=dict(q);bad[key]="unsealed_or_scalar_or_relaxed"
        invalid.append(dict(request=bad,result=c._audit(bad,p,n,ref,orig)))
    one="000000000000f03f";one125="000000000000f23f";lo="000000000000303c";tiny="0000000000007038";zero="0000000000000000"
    exact=one+neg(lo)+one+lo;loss=one+neg(lo)+one125+tiny
    controls=[c.width(v,[0,1])for v in (exact,loss)]
    under="0000000000001000"+zero+"0100000000001000"+zero
    u=c.width(under,[0,1]);z=c.width(one+zero+one+zero,[0,1])
    inf="000000000000f07f"+zero+one+zero;sub="0100000000000000"+zero+one+zero
    mag=zero+zero+"0000000000001042"+zero
    pre=[c.width(payload,b)for payload,b in ((True,[0,1]),("",[0,1]),(exact.upper(),[0,1]),
         (inf,[0,1]),(sub,[0,1]),(mag,[0,1]),(exact,[-1,1]),(exact,[2,2]))]
    d=dict(records=records,invalid=invalid,controls=controls,underflow_STOP=u,zero_STOP=z,precontrols=pre,pins=pins)
    summary=verify_capture(d);summary["mutations_rejected"]=mutations(d);assert summary["mutations_rejected"]==8
    print(json.dumps(dict(status="PASS",summary=summary,evidence=d),sort_keys=True,separators=(",",":")))


if __name__=="__main__":run()
