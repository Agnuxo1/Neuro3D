"""Independent bit/rational proof of scalar emulation, loss gate and scene binding."""
from pathlib import Path
from fractions import Fraction as F
import json,hashlib,copy,runpy
ROOT=Path(__file__).resolve().parents[2]
prior=runpy.run_path(str(ROOT/"Blender/tests/test_oblique_root_pair32_wire_HOST.py"))
capture,digest,pair,pf,p32,nearest32=(prior[n]for n in ("capture","digest","pair","pf","p32","nearest32"))
nearest64=prior["prior"]["nearest"]
MODEL="oblique-scalar32-consumer-gate-CPU-v1"
POLICY="EMULATED_RN64_ADD_THEN_RN32_PRESERVE_SEALED_PAIR_SUM_EXACTLY"
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-ROOT-PAIR32-WIRE-HOST-001-CODEX.json"
PSHA="580b012d7921d0130852fa082de6e5cc8bdd066340c790d9849fb381355fc111"


def retained():
    raw=(ROOT/PARENT).read_bytes();assert len(raw)==159924 and hashlib.sha256(raw).hexdigest()==PSHA
    r=json.loads(raw);pins=dict(r["code_doc_sha256"]);assert len(pins)==296
    for p,h in pins.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    d=capture(r["test_run"])["evidence"];_,reference,orig,_,_=prior["retained"]()
    pins[PARENT]=PSHA
    return {x["id"]:x for x in d["records"]},reference,orig,pins,d


def selector(k,e,reference,orig):
    o=orig[k];q=o.get("scene_query",o["request"].get("scene_query"))
    return dict(backend=MODEL,policy=POLICY,record_id=k,parent_receipt_sha256=PSHA,
        parent_record_sha256=digest(e[k]),reference_record_sha256=digest(reference[k]),
        original_record_sha256=digest(o),original_snapshot_sha256=digest(o["scene"]),original_query_sha256=digest(q))


def proof(r,packet,S,B):
    assert r["input_packet"]==packet and r["exact_squared"]==pair(S)and r["inherited_bound"]==pair(B)
    assert r["scope"]=="CPU_RN64_ADD_RN32_CAST_EMULATION_NOT_NATIVE_ALU32"and r["full_costs"]=="UNKNOWN_NOT_ZERO"
    assert type(packet)is str and len(packet)==16 and bytes.fromhex(packet).hex()==packet
    a,b=p32(packet[:8]),p32(packet[8:])
    for w,v in ((packet[:8],a),(packet[8:],b)):
        u=int.from_bytes(bytes.fromhex(w),"little");exponent=(u>>23)&255
        assert exponent not in (0,255)or v==0
        assert abs(v)<=2**33
    Q=a+b;assert 0<Q<=2**33 and 0<S<=2**66 and B>=0 and Q-B>0 and (Q-B)**2<=S<=(Q+B)**2
    assert r["exact_pair_sum"]==pair(Q)
    z=r["ledger"];assert z["a_word32"]==packet[:8]and z["b_word32"]==packet[8:]
    v=nearest64(z["intermediate_word64"],Q)
    assert r["HOST_signed_intermediate_error"]==pair(Q-v)
    T=nearest32(z["candidate_word32"],v)
    assert nearest32(z["candidate_word32"],Q)==T # per-capture one-RN32 mathematical target, NOT universal two-round theorem.
    assert r["candidate_word32"]==z["candidate_word32"]and r["RN64_adds"]==r["RN32_casts"]==1
    assert r["input_decode_calls"]==1
    for n in ("new_products","native_ALU32_sums","new_sqrt_calls","retained_numeric_replays"):assert r[n]==0
    u=int.from_bytes(bytes.fromhex(z["candidate_word32"]),"little");exponent=(u>>23)&255
    if exponent==0:
        assert T!=0 and r["status"]=="STOP_INPUT"and r["reason"]=="target_positive_normal_no_underflow"
        assert r["scalar_word32"]is None and r["scalar_value"]is None and r["output_decode_calls"]==0 and r["decoded_components"]==2
        for n in ("HOST_enclosure","composed_length_error_bound","signed_projection_error","projection_error_bound","exact_projection_preserved"):assert r[n]is None
        return dict(exact=0,loss=0,target_STOP=1,RN64=1,RN32=1,inputs=1,outputs=0)
    E=Q-T;C=B+abs(E)
    assert r["scalar_value"]==pair(T)and r["signed_projection_error"]==pair(E)and r["projection_error_bound"]==pair(abs(E))
    assert r["composed_length_error_bound"]==pair(C)and r["HOST_enclosure"]==[pair(T-C),pair(T+C)]
    assert T-C>0 and (T-C)**2<=S<=(T+C)**2
    assert r["output_decode_calls"]==1 and r["decoded_components"]==3 and r["exact_projection_preserved"]is(E==0)
    if E:
        assert r["status"]=="STOP_PROJECTION_LOSS"and r["reason"]=="nonzero_scalar_projection_loss"and r["scalar_word32"]is None
    else:
        assert r["status"]=="CPU_EMULATED_SCALAR32_EXACT_PAIR_PROJECTION_ONLY"and r["reason"]=="exact_emulated_projection_not_scene_engine"
        assert r["scalar_word32"]==r["candidate_word32"]
    return dict(exact=int(E==0),loss=int(E!=0),target_STOP=0,RN64=1,RN32=1,inputs=1,outputs=1)


def scope(r):
    assert r["backend"]==MODEL and r["promotion"]=="STOP_SCALAR_LOSS_REAL_CONSUMER_SCENE_PHASE_PHYSICAL_GPU"
    assert r["scope"]=="CPU_EMULATED_SCALAR_PROJECTION_GATE_ORIGINAL_BOX_NOT_ENGINE"
    assert r["full_costs"]=="UNKNOWN_NOT_ZERO"and r["native_length"]is None and r["phase_error_bound"]is None
    for n in ("new_products","native_ALU32_sums","new_sqrt_calls","retained_numeric_replays"):assert r[n]==0
    for n in ("phase_certified","wavelength_known","physical_reference_certified","GPU_used","Bpy_used","shader_used","source_uncertainty_cancelled"):assert r[n]is False


def verify_capture(d,verify_parent=True):
    e,reference,orig,pins,old=retained();assert d["pins"]==pins
    if verify_parent:assert prior["verify_capture"](old)["status"]=="PASS"
    assert len(d["records"])==16 and {x["id"]for x in d["records"]}==set(e)
    count={n:0 for n in ("exact","loss","target_STOP","RN64","RN32","inputs","outputs")};meta={};scenes=stops=0
    def tally(v):
        for n in count:count[n]+=v[n]
    for x in d["records"]:
        k,r=x["id"],x["result"];scope(r)
        assert x["request"]==selector(k,e,reference,orig)and r["request_sha256"]==digest(x["request"])
        p=e[k]["result"];assert r["upstream_status"]==p["status"]and r["retained_canonical_status"]==p["retained_canonical_status"]
        if p["status"]!="CPU_PAIR32_WIRE_HOST_ORIGINAL_BOX_BOUND_ONLY":
            assert r["status"]=="STOP_UPSTREAM"and r["reason"]=="sealed_STOP_not_rescued"and r["diagnostic"]is None
            for n in ("RN64_adds","RN32_casts","input_decode_calls","output_decode_calls","decoded_components"):assert r[n]==0
            stops+=1;continue
        assert r["status"]=="STOP_SCALAR_PAIR_CONSUMPTION_LOSS"and r["reason"]=="pair_information_not_preserved"
        z,rz=r["diagnostic"],reference[k]["result"]["diagnostic"]
        assert z["original_snapshot_sha256"]==digest(orig[k]["scene"])
        assert (z["source"],z["detector"],z["units"])==("SOURCE0","DETECTOR0","scene_length")and len(z["attempts"])==2
        for i,x in enumerate(z["attempts"]):
            w=p["diagnostic"]["packets"][i]["result"]
            assert x["bound"]==("lower","upper")[i]and w["exact_squared"]==rz["extrema"]["squared"][i]
            v=proof(x["result"],w["packet_hex"],F(*w["exact_squared"]),F(*w["composed_length_error_bound"]))
            assert v["loss"]==1;tally(v)
        a,b=(v["result"]for v in z["attempts"])
        low,high=F(*a["HOST_enclosure"][0]),F(*b["HOST_enclosure"][1]);rw=F(*rz["reference_width"])
        Slo,Shi=(F(*v)for v in rz["extrema"]["squared"]);assert 0<low<=high and low*low<=Slo<=Shi<=high*high
        nominal=[F(*v["scalar_value"])for v in (a,b)];C=max(F(*v["composed_length_error_bound"])for v in (a,b))
        assert z["HOST_scalar_length_interval"]==[pair(low),pair(high)]and z["interval_width"]==pair(high-low)
        assert z["nominal_scalar_interval"]==[pair(v)for v in nominal]and z["nominal_scalar_width"]==pair(nominal[1]-nominal[0])
        assert z["reference_interval"]==rz["reference_interval"]and z["reference_width"]==rz["reference_width"]
        assert z["width_over_reference"]==pair((high-low)/rw)and z["max_composed_length_error_bound"]==pair(C)
        assert z["error_bound_over_reference_width"]==pair(C/rw)and z["scalar_attempts_rejected"]==2 and z["HOST_ratio_divisions"]==2
        assert z["retained_wire_interval_width"]==p["diagnostic"]["interval_width"]
        assert (r["RN64_adds"],r["RN32_casts"],r["input_decode_calls"],r["output_decode_calls"],r["decoded_components"])==(2,2,2,2,6)
        meta[k]=dict(nominal_width=str(nominal[1]-nominal[0]),HOST_width=str(high-low),max_composed_bound=str(C),
            bound_over_reference_width=str(C/rw),width_over_reference=str((high-low)/rw),
            candidates=[v["candidate_word32"]for v in (a,b)],
            signed_intermediate_errors=[str(F(*v["HOST_signed_intermediate_error"]))for v in (a,b)],
            signed_projection_errors=[str(F(*v["signed_projection_error"]))for v in (a,b)])
        scenes+=1
    assert (scenes,stops,count["loss"])==(2,14,4)
    assert len(d["invalid"])==8
    for x in d["invalid"]:
        r=x["result"];scope(r);assert r["status"]=="STOP_INPUT"and r["reason"]=="closed_selector"and r["diagnostic"]is None
        assert r["RN64_adds"]==r["RN32_casts"]==r["input_decode_calls"]==r["output_decode_calls"]==0
    assert len(d["controls"])==4
    for r,w in zip(d["controls"],old["controls"]):
        tally(proof(r,w["packet_hex"],F(*w["exact_squared"]),F(*w["composed_length_error_bound"])))
    assert [r["exact_projection_preserved"]for r in d["controls"]]==[True,True,True,False]
    assert len(d["ties"])==2
    expected=[("0000803f00008033","0000803f"),("0100803f00008033","0200803f")]
    for r,(packet,w)in zip(d["ties"],expected):
        Q=p32(packet[:8])+p32(packet[8:])
        v=proof(r,packet,Q*Q,F(0));assert v["loss"]==1 and r["candidate_word32"]==w;tally(v)
    under=d["underflow_STOP"];packet="0100800000008080"
    Q=p32(packet[:8])+p32(packet[8:]);assert Q==F(1,2**149)
    assert under["candidate_word32"]=="01000000";tally(proof(under,packet,Q*Q,F(0)))
    assert len(d["precontrols"])==8
    pre_input=0
    for r in d["precontrols"]:
        assert r["status"]=="STOP_INPUT"and r["RN64_adds"]==r["RN32_casts"]==r["output_decode_calls"]==0
        assert r["ledger"]is None and r["candidate_word32"]is None and r["scalar_word32"]is None and r["HOST_enclosure"]is None
        pre_input+=r["input_decode_calls"];assert r["decoded_components"]==2*r["input_decode_calls"]
    assert pre_input==3
    assert count==dict(exact=3,loss=7,target_STOP=1,RN64=11,RN32=11,inputs=11,outputs=10)
    return dict(status="PASS",eligible_scenes=2,scene_admitted=0,scene_projection_loss=4,upstream_STOP=14,
        exact_synthetic_projections=3,synthetic_projection_loss=3,target_underflow_STOP=1,
        RN64_adds=11,RN32_casts=11,input_decode_calls=14,output_decode_calls=10,decoded_components=38,
        total_decode_calls=24,selectors_rejected=8,precontrols=8,inherited_pins=297,
        retained_numeric_replays=0,new_products=0,native_ALU32_sums=0,new_sqrt_calls=0,by_scene=meta)


def mutations(d):
    k=next(i for i,x in enumerate(d["records"])if x["result"]["diagnostic"]is not None);rejects=0
    for n in range(8):
        a=copy.deepcopy(d);r=a["records"][k]["result"];z=r["diagnostic"];v=z["attempts"][0]["result"]
        if n==0:v["status"]="CPU_EMULATED_SCALAR32_EXACT_PAIR_PROJECTION_ONLY"
        elif n==1:v["scalar_word32"]=v["candidate_word32"]
        elif n==2:v["ledger"]["b_word32"]="00000000"
        elif n==3:v["composed_length_error_bound"]=[0,1]
        elif n==4:v["HOST_signed_intermediate_error"]=[0,1]
        elif n==5:r["source_uncertainty_cancelled"]=True
        elif n==6:r["Bpy_used"]=True
        else:a["underflow_STOP"]["scalar_word32"]="01000000"
        try:verify_capture(a,verify_parent=False)
        except (AssertionError,ValueError,TypeError,KeyError,IndexError):rejects+=1
        else:raise AssertionError("mutation_accepted:"+str(n))
    return rejects


def run():
    import oblique_scalar32_consumer_gate_CPU_v1 as core
    e,ref,orig,pins,old=core.retained();records=[]
    for k in e:
        q=core.selector(k,e,ref,orig);records.append(dict(id=k,request=q,result=core._audit(q,e,ref,orig)))
    k=next(x["id"]for x in records if x["result"]["diagnostic"]is not None);q=core.selector(k,e,ref,orig);invalid=[]
    for n in range(8):
        bad=dict(q)
        if n==0:bad["policy"]="relax_loss_tolerance"
        elif n==1:bad["wavelength"]="500"
        elif n==2:bad["backend"]="GPU"
        elif n==3:bad["parent_record_sha256"]="0"*64
        elif n==4:bad["reference_record_sha256"]="0"*64
        elif n==5:bad["original_snapshot_sha256"]="0"*64
        elif n==6:bad["original_query_sha256"]=0
        else:bad.pop("original_record_sha256")
        invalid.append(dict(request=bad,result=core._audit(bad,e,ref,orig)))
    controls=[core.project(w["packet_hex"],w["exact_squared"],w["composed_length_error_bound"])for w in old["controls"]]
    def synthetic(packet):
        Q=p32(packet[:8])+p32(packet[8:])
        return core.project(packet,pair(Q*Q),[0,1])
    ties=[synthetic(p)for p in ("0000803f00008033","0100803f00008033")]
    under=synthetic("0100800000008080")
    one="0000803f00000000";zero="0000000000000000"
    pre=[core.project(p,s,b)for p,s,b in ((True,[1,1],[0,1]),("",[1,1],[0,1]),
         ("0000803F00000000",[1,1],[0,1]),("010000000000803f",[1,1],[0,1]),
         ("0000807f00000000",[1,1],[0,1]),(one,[2,2],[0,1]),(one,[1,1],[-1,1]),(zero,[1,1],[0,1]))]
    d=dict(records=records,invalid=invalid,controls=controls,ties=ties,underflow_STOP=under,precontrols=pre,pins=pins)
    v=verify_capture(d);v["mutations_rejected"]=mutations(d);assert v["mutations_rejected"]==8
    print(json.dumps(dict(status="PASS",summary=v,evidence=d),sort_keys=True,separators=(",",":")))


if __name__=="__main__":run()
