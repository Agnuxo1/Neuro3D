"""Independent IEEE32 midpoint and HOST bound proof; no prior numerical replay."""
from pathlib import Path
from fractions import Fraction as F
import json,hashlib,copy,runpy,struct
ROOT = Path(__file__).resolve().parents[2]
prior = runpy.run_path(str(ROOT/"Blender/tests/test_oblique_root_hilo_correction_CPU64.py"))
capture,digest,pair,pf = (prior[n] for n in ("capture","digest","pair","pf"))
MODEL = "oblique-root-pair32-wire-HOST-v1"
POLICY = "SEALED_NATIVE_PAIR_INDEPENDENT_COMPONENT_RN32_WIRE_HOST_COMPOSITION"
PARENT = "coordinacion/respuestas/PRECISION-OBLIQUE-ROOT-HILO-CORRECTION-CPU-001-CODEX.json"
PSHA = "6ef5e1e46e9e9f37c4c7051d064598191e76c93737325dc3683e4aeb3e082eef"


def retained():
    raw=(ROOT/PARENT).read_bytes();assert len(raw)==168330 and hashlib.sha256(raw).hexdigest()==PSHA
    r=json.loads(raw);pins=dict(r["code_doc_sha256"]);assert len(pins)==292
    for p,h in pins.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    d=capture(r["test_run"])["evidence"]
    _,_,reference,orig,_,_=prior["retained"]()
    pins[PARENT]=PSHA
    return {x["id"]:x for x in d["records"]},reference,orig,pins,d


def selector(k,e,reference,orig):
    o=orig[k];q=o.get("scene_query",o["request"].get("scene_query"))
    return dict(backend=MODEL,policy=POLICY,record_id=k,parent_receipt_sha256=PSHA,
        parent_record_sha256=digest(e[k]),reference_record_sha256=digest(reference[k]),
        original_record_sha256=digest(o),original_snapshot_sha256=digest(o["scene"]),
        original_query_sha256=digest(q))


def p32(w):
    assert type(w)is str and len(w)==8 and bytes.fromhex(w).hex()==w
    u=int.from_bytes(bytes.fromhex(w),"little");e=(u>>23)&255;m=u&((1<<23)-1)
    assert e!=255
    n=m if e==0 else (1<<23)+m
    shift=-149 if e==0 else e-127-23
    v=F(n*(2**max(shift,0)),2**max(-shift,0))
    return -v if u>>31 else v


def adjacent32(w,up):
    u=int.from_bytes(bytes.fromhex(w),"little")
    if u & 0x7fffffff == 0:u=1 if up else (1<<31)|1
    else:u += (-1 if up else 1) if u>>31 else (1 if up else -1)
    return u.to_bytes(4,"little").hex()


def nearest32(w,x):
    y=p32(w);lo=p32(adjacent32(w,False));hi=p32(adjacent32(w,True))
    a,b=(lo+y)/2,(y+hi)/2;even=int.from_bytes(bytes.fromhex(w),"little")%2==0
    assert a<=x<=b and (x not in (a,b)or even),("not_RN32",w,str(x))
    return y


def wireproof(r,words,S,B):
    assert r["input_words"]==words and r["exact_squared"]==pair(S)and r["inherited_bound"]==pair(B)
    assert len(words)==2
    Q=sum((pf(w)for w in words),F(0))
    for w in words:
        u=int.from_bytes(bytes.fromhex(w),"little");v=pf(w)
        assert (u>>52)&2047 not in (0,2047)or v==0
        assert abs(v)<=2**33
    assert 0<Q<=2**33 and 0<S<=2**66 and B>=0 and Q-B>0 and (Q-B)**2<=S<=(Q+B)**2
    assert r["Q64"]==pair(Q)
    ledger=r["cast_ledger"];assert len(ledger)==r["RN32_casts"]==2
    vals=[];bad=[]
    for i,t in enumerate(ledger):
        assert t["index"]==i and t["input_word64"]==words[i]
        w=t["output_word32"];v=nearest32(w,pf(words[i]));vals.append(v)
        u=int.from_bytes(bytes.fromhex(w),"little");exponent=(u>>23)&255;mantissa=u&((1<<23)-1)
        bad.append(exponent==0 and (mantissa!=0 or pf(words[i])!=0))
        # RN preserves sign, including signed zero.
        assert u>>31==int.from_bytes(bytes.fromhex(words[i]),"little")>>63
    packet="".join(t["output_word32"]for t in ledger);assert r["partial_packet_hex"]==packet
    for n in ("new_products","new_sums","new_sqrt_calls","retained_numeric_replays"):assert r[n]==0
    assert r["full_costs"]=="UNKNOWN_NOT_ZERO"
    if any(bad):
        assert bad==[False,True] # controls intentionally exercise second-word underflow.
        assert r["status"]=="STOP_INPUT"and r["reason"]=="target_normal_zero_no_underflow:1"
        assert r["packet_hex"]is None and r["decoded_words64"]is None and r["Q32"]is None
        assert r["HOST_enclosure"]is None and r["composed_length_error_bound"]is None and r["drop_lo_simulation"]is None
        assert r["packet_decode_calls"]==r["decoded_components"]==0
        return False
    assert r["status"]=="CPU_FORMAT_PAIR32_HOST_BOUND_ONLY"and r["reason"]=="independent_RN32_not_engine"
    assert r["packet_hex"]==packet and len(bytes.fromhex(packet))==8
    assert r["packet_decode_calls"]==1 and r["decoded_components"]==2
    assert [pf(w)for w in r["decoded_words64"]]==vals
    for a,b in zip(r["decoded_words64"],ledger):
        assert int.from_bytes(bytes.fromhex(a),"little")>>63==int.from_bytes(bytes.fromhex(b["output_word32"]),"little")>>31
    q=sum(vals,F(0));E=Q-q;C=B+abs(E)
    assert r["Q32"]==pair(q)and r["signed_transport_error"]==pair(E)and r["transport_error_bound"]==pair(abs(E))
    assert r["composed_length_error_bound"]==pair(C)and r["HOST_enclosure"]==[pair(q-C),pair(q+C)]
    assert q-C>0 and (q-C)**2<=S<=(q+C)**2
    d=r["drop_lo_simulation"];single=vals[0];lost=q-single;D=C+abs(lost)
    assert d==dict(scope="SIMULATED_CONSUMER_DROPS_LO_NOT_BPY_SHADER",nominal_single=pair(single),
        signed_discarded_low=pair(lost),composed_length_error_bound=pair(D),
        HOST_enclosure=[pair(single-D),pair(single+D)],extra_RN32_casts=0)
    assert single-D>0 and (single-D)**2<=S<=(single+D)**2
    return True


def scope(r):
    assert r["backend"]==MODEL and r["promotion"]=="STOP_CONSUMER_BPY_SHADER_SCENE_PHASE_PHYSICAL_GPU"
    assert r["scope"]=="CPU_FORMAT_TEST_HOST_COMPOSITION_SEALED_NATIVE_PAIR_ORIGINAL_BOX_ONLY"
    assert r["full_costs"]=="UNKNOWN_NOT_ZERO"and r["native_length"]is None and r["phase_error_bound"]is None
    for n in ("new_products","new_sums","new_sqrt_calls","retained_numeric_replays"):assert r[n]==0
    for n in ("phase_certified","wavelength_known","physical_reference_certified","GPU_used","Bpy_used","shader_used","source_uncertainty_cancelled"):assert r[n]is False


def verify_capture(d,verify_parent=True):
    e,reference,orig,pins,old=retained();assert d["pins"]==pins
    if verify_parent:assert prior["verify_capture"](old)["status"]=="PASS"
    assert len(d["records"])==16 and {x["id"]for x in d["records"]}==set(e)
    scenes=stops=casts=decodes=0;meta={}
    for x in d["records"]:
        k,r=x["id"],x["result"];scope(r)
        assert x["request"]==selector(k,e,reference,orig)and r["request_sha256"]==digest(x["request"])
        p=e[k]["result"]
        assert r["upstream_status"]==p["status"]and r["retained_canonical_status"]==p["retained_canonical_status"]
        if p["status"]!="CPU64_SEALED_ROOT_PAIR_CORRECTIONS_HOST_BOUNDS_ONLY":
            assert r["status"]=="STOP_UPSTREAM"and r["reason"]=="sealed_STOP_not_rescued"and r["diagnostic"]is None
            assert r["RN32_casts"]==r["packet_decode_calls"]==r["decoded_components"]==0
            stops+=1;continue
        assert r["status"]=="CPU_PAIR32_WIRE_HOST_ORIGINAL_BOX_BOUND_ONLY"and r["reason"]=="wire_format_not_scene_consumer"
        z,rz=r["diagnostic"],reference[k]["result"]["diagnostic"]
        assert z["original_snapshot_sha256"]==digest(orig[k]["scene"])
        assert (z["source"],z["detector"],z["units"])==("SOURCE0","DETECTOR0","scene_length")
        assert len(z["packets"])==2
        for i,v in enumerate(z["packets"]):
            c=p["diagnostic"]["corrections"][i]["result"]
            assert c["exact_squared"]==rz["extrema"]["squared"][i]
            assert v["bound"]==("lower","upper")[i]
            assert wireproof(v["result"],c["root_pair_words"],F(*c["exact_squared"]),F(*c["length_error_bound"]))
        a,b=(v["result"]for v in z["packets"])
        low,high=F(*a["HOST_enclosure"][0]),F(*b["HOST_enclosure"][1]);rw=F(*rz["reference_width"])
        Slo,Shi=(F(*v)for v in rz["extrema"]["squared"])
        assert 0<low<=high and low*low<=Slo<=Shi<=high*high
        C=max(F(*v["composed_length_error_bound"])for v in (a,b));width=high-low
        assert z["HOST_wire_length_interval"]==[pair(low),pair(high)]and z["interval_width"]==pair(width)
        assert z["reference_width"]==rz["reference_width"]and z["reference_interval"]==rz["reference_interval"]
        assert z["width_over_reference"]==pair(width/rw)and z["max_composed_length_error_bound"]==pair(C)
        assert z["error_bound_over_reference_width"]==pair(C/rw)and z["HOST_ratio_divisions"]==2
        singles=[F(*v["drop_lo_simulation"]["nominal_single"])for v in (a,b)]
        slo,shi=F(*a["drop_lo_simulation"]["HOST_enclosure"][0]),F(*b["drop_lo_simulation"]["HOST_enclosure"][1])
        assert z["drop_lo_nominal_interval"]==[pair(v)for v in singles]and z["drop_lo_nominal_width"]==pair(singles[1]-singles[0])
        assert z["drop_lo_HOST_interval"]==[pair(slo),pair(shi)]and z["drop_lo_HOST_width"]==pair(shi-slo)
        assert slo>0 and slo*slo<=Slo<=Shi<=shi*shi
        assert (r["RN32_casts"],r["packet_decode_calls"],r["decoded_components"])==(4,2,4)
        casts+=4;decodes+=2;scenes+=1
        meta[k]=dict(width=str(width),width_over_reference=str(width/rw),max_composed_length_error_bound=str(C),
            error_bound_over_reference_width=str(C/rw),drop_lo_nominal_width=str(singles[1]-singles[0]),
            drop_lo_HOST_width=str(shi-slo),packets=[v["result"]["packet_hex"]for v in z["packets"]],
            signed_transport_errors=[str(F(*v["result"]["signed_transport_error"]))for v in z["packets"]])
    assert (scenes,stops,casts,decodes)==(2,14,8,4)
    assert len(d["invalid"])==8
    for x in d["invalid"]:
        r=x["result"];scope(r);assert r["status"]=="STOP_INPUT"and r["reason"]=="closed_selector"
        assert r["diagnostic"]is None and r["RN32_casts"]==r["packet_decode_calls"]==r["decoded_components"]==0
    assert len(d["controls"])==4
    expected=[["0000803f","00000080"],["0000803f","00000000"],["0200803f","00000000"],["0000803f","0000802f"]]
    for r,words32 in zip(d["controls"],expected):
        assert wireproof(r,r["input_words"],F(*r["exact_squared"]),F(*r["inherited_bound"]))
        assert [t["output_word32"]for t in r["cast_ledger"]]==words32
    assert len(d["underflow_STOP"])==2
    for r in d["underflow_STOP"]:
        assert not wireproof(r,r["input_words"],F(*r["exact_squared"]),F(*r["inherited_bound"]))
    assert d["underflow_STOP"][0]["cast_ledger"][1]["output_word32"]=="00000000"
    assert p32(d["underflow_STOP"][1]["cast_ledger"][1]["output_word32"])==F(1,2**140)
    assert len(d["precontrols"])==8
    for r in d["precontrols"]:
        assert r["status"]=="STOP_INPUT"and r["RN32_casts"]==r["packet_decode_calls"]==r["decoded_components"]==0
        assert r["cast_ledger"]==[]and r["partial_packet_hex"]==""
        assert r["packet_hex"]is None and r["HOST_enclosure"]is None
    return dict(status="PASS",scenes=2,upstream_STOP=14,scene_RN32_casts=8,scene_packet_decodes=4,
        controls=4,control_RN32_casts=8,underflow_STOP=2,underflow_RN32_casts=4,
        total_RN32_casts=20,total_packet_decodes=8,selectors_rejected=8,precontrols=8,
        inherited_pins=293,new_products=0,new_sums=0,new_sqrt_calls=0,retained_numeric_replays=0,by_scene=meta)


def mutations(d):
    k=next(i for i,x in enumerate(d["records"])if x["result"]["diagnostic"]is not None);rejects=0
    for n in range(8):
        a=copy.deepcopy(d);r=a["records"][k]["result"];z=r["diagnostic"];v=z["packets"][0]["result"]
        if n==0:v["packet_hex"]="00"*8
        elif n==1:v["cast_ledger"][1]["input_word64"]=v["input_words"][0]
        elif n==2:v["cast_ledger"][0]["output_word32"]="0000803f"
        elif n==3:v["composed_length_error_bound"]=[0,1]
        elif n==4:v["drop_lo_simulation"]["scope"]="Bpy"
        elif n==5:r["source_uncertainty_cancelled"]=True
        elif n==6:r["phase_certified"]=True
        else:a["underflow_STOP"][0]["status"]="CPU_FORMAT_PAIR32_HOST_BOUND_ONLY"
        try:verify_capture(a,verify_parent=False)
        except (AssertionError,ValueError,TypeError,KeyError,IndexError):rejects+=1
        else:raise AssertionError("mutation_accepted:"+str(n))
    return rejects


def run():
    import oblique_root_pair32_wire_HOST_v1 as core
    e,ref,orig,pins,_=core.retained();records=[]
    for k in e:
        q=core.selector(k,e,ref,orig);records.append(dict(id=k,request=q,result=core._audit(q,e,ref,orig)))
    k=next(x["id"]for x in records if x["result"]["diagnostic"]is not None);q=core.selector(k,e,ref,orig);invalid=[]
    for n in range(8):
        bad=dict(q)
        if n==0:bad["policy"]="renormalize_HOST_residual"
        elif n==1:bad["wavelength"]="500"
        elif n==2:bad["backend"]="Bpy"
        elif n==3:bad["parent_record_sha256"]="0"*64
        elif n==4:bad["reference_record_sha256"]="0"*64
        elif n==5:bad["original_snapshot_sha256"]="0"*64
        elif n==6:bad["original_query_sha256"]=0
        else:bad.pop("original_record_sha256")
        invalid.append(dict(request=bad,result=core._audit(bad,e,ref,orig)))
    w=lambda v:struct.pack("<d",v).hex()
    def control(h,l):
        words=[w(h),w(l)];Q=pf(words[0])+pf(words[1])
        return core.wire(words,pair(Q*Q),[0,1])
    controls=[control(1.0,-0.0),control(1.0+2.0**-24,0.0),control(1.0+3*2.0**-24,0.0),control(1.0,2.0**-32)]
    under=[control(1.0,2.0**-200),control(1.0,2.0**-140)]
    one,zero=w(1.0),w(0.0)
    pre=[core.wire(a,b,c)for a,b,c in (([],[1,1],[0,1]),([True,zero],[1,1],[0,1]),
        ([w(float("inf")),zero],[1,1],[0,1]),([w(2.0**-1074),zero],[1,1],[0,1]),
        ([w(2.0**34),zero],[1,1],[0,1]),([one,zero],[True,1],[0,1]),
        ([one,zero],[2,2],[0,1]),([one,zero],[1,1],[-1,1]))]
    d=dict(records=records,invalid=invalid,controls=controls,underflow_STOP=under,precontrols=pre,pins=pins)
    v=verify_capture(d);v["mutations_rejected"]=mutations(d);assert v["mutations_rejected"]==8
    print(json.dumps(dict(status="PASS",summary=v,evidence=d),sort_keys=True,separators=(",",":")))


if __name__=="__main__":run()
