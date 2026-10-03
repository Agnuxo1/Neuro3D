"""New fixed26 RN64 width consumer of sealed scene pair64 length bounds."""
from pathlib import Path
from fractions import Fraction as F
import json,struct
import oblique_scene_pair64_payload_CPU_v1 as prior
ROOT=Path(__file__).resolve().parents[3]
MODEL="oblique-pair64-width-consumer-CPU-v1"
POLICY="FIXED26_RN64_PAIR_DIFFERENCE_PRESERVE_SEALED_WIDTH_EXACTLY"
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-SCENE-PAIR64-PAYLOAD-CPU-001-CODEX.json"
PSHA="ed228edd01ecced262362ff2ac8853cba434ce1e359cdfa2385017294f9dbbe9"
require,sha,capture,digest=prior.require,prior.sha,prior.capture,prior.digest


def pair(x):return [x.numerator,x.denominator]


def rational(p):
    require(type(p)is list and len(p)==2 and all(type(v)is int for v in p)and p[1]>0,"canonical_rational")
    x=F(*p);require(pair(x)==p,"canonical_rational");return x


def retained():
    raw=(ROOT/PARENT).read_bytes();require(len(raw)==242660 and sha(raw)==PSHA,"parent_seal")
    r=json.loads(raw);pins=dict(r["code_doc_sha256"]);require(len(pins)==311,"parent_pins")
    for p,h in pins.items():require(sha((ROOT/p).read_bytes())==h,"dependency:"+p)
    require(capture(r["independent_pre"])["status"]=="PASS","parent_oracle")
    d=capture(r["test_run"])["evidence"];producer={x["id"]:x for x in d["records"]}
    _,native,ref,orig,_,_,_=prior.retained()
    require(set(producer)==set(native)==set(ref)==set(orig)and len(producer)==16,"closed_records")
    pins[PARENT]=PSHA
    return producer,native,ref,orig,pins,d


def width(payload,inherited_bound):
    out=dict(status="STOP_INPUT",reason=None,input_payload_hex=payload,inherited_bound=inherited_bound,
        ledger=[],RN_nodes_executed=0,fixed_RN_budget=26,hex_bytes_calls=0,input_word_reads=0,
        float_decode_calls=0,decoded_components=0,sign_flips=0,word_format_calls=0,
        input_width=None,candidate_pair_words=None,native_pair_width=None,HOST_signed_residual=None,
        HOST_arithmetic_error_bound=None,HOST_total_width_error_bound=None,HOST_width_interval=None,
        new_products=0,new_sqrt_calls=0,retained_numeric_replays=0,full_costs="UNKNOWN_NOT_ZERO")
    try:
        B=rational(inherited_bound);require(B>=0,"nonnegative_bound")
        require(type(payload)is str and len(payload)==64
                and all(c in "0123456789abcdef"for c in payload),"canonical_payload32")
        raw=bytes.fromhex(payload);out["hex_bytes_calls"]=1
        for i in range(4):
            u=int.from_bytes(raw[8*i:8*i+8],"little");out["input_word_reads"]+=1
            e=(u>>52)&2047;m=u&((1<<52)-1)
            require(e!=2047 and (e!=0 or m==0),"input_normal_zero:"+str(i))
        lh,ll,uh,ul=struct.unpack("<4d",raw)
        out.update(float_decode_calls=1,decoded_components=4)
        require(all(abs(x)<=2**33 for x in (lh,ll,uh,ul)),"component_bound33")
        W=(F.from_float(uh)+F.from_float(ul))-(F.from_float(lh)+F.from_float(ll))
        out["input_width"]=pair(W);require(0<W<=2**34,"positive_width_domain")

        def word(x):
            out["word_format_calls"]+=1;return struct.pack("<d",x).hex()

        def rn(name,op,a,b):
            require(out["RN_nodes_executed"]<26,"fixed26_budget")
            exact=F.from_float(a)+F.from_float(b)if op=="add"else F.from_float(a)-F.from_float(b)
            v=a+b if op=="add"else a-b # Actual CPU binary64 arithmetic, not HOST reinjection.
            out["ledger"].append(dict(index=len(out["ledger"]),name=name,op=op,a=word(a),b=word(b),y=word(v)))
            out["RN_nodes_executed"]+=1
            q=F.from_float(v)
            require(abs(q)<=2**34 and (q==0 or abs(q)>=F(1,2**1022))and (q!=0 or exact==0),
                    "normal_zero_no_underflow:"+name)
            return v

        def sum2(prefix,a,b):
            s=rn(prefix+".s","add",a,b)
            bb=rn(prefix+".bb","sub",s,a)
            ab=rn(prefix+".ab","sub",s,bb)
            db=rn(prefix+".db","sub",b,bb)
            da=rn(prefix+".da","sub",a,ab)
            e=rn(prefix+".err","add",da,db)
            return s,e

        out["sign_flips"]=2 # Unary negatives of finite decoded words, exact sign-bit changes; no RN.
        p=sum2("p",uh,-lh);q=sum2("q",ul,-ll)
        e=rn("merge.e","add",p[1],q[0]);r=sum2("r",p[0],e)
        l=rn("merge.l","add",r[1],q[1]);y=sum2("y",r[0],l)
        out["candidate_pair_words"]=[word(y[0]),word(y[1])]
        C=F.from_float(y[0])+F.from_float(y[1]);E=W-C;T=B+abs(E)
        out.update(native_pair_width=pair(C),HOST_signed_residual=pair(E),HOST_arithmetic_error_bound=pair(abs(E)),
            HOST_total_width_error_bound=pair(T),HOST_width_interval=[pair(C-T),pair(C+T)])
        require(out["RN_nodes_executed"]==26 and C>0,"positive_candidate_fixed26")
        if E!=0:out.update(status="STOP_PAIR_WIDTH_RESIDUAL",reason="nonzero_pair_width_residual")
        elif C-T<=0:out.update(status="STOP_WIDTH_BUDGET",reason="width_budget_crosses_zero")
        else:out.update(status="CPU64_EXACT_PAIR_WIDTH_ONLY",reason="fixed26_pair_width_not_scene_or_phase")
    except (ValueError,TypeError,KeyError,OverflowError,struct.error)as ex:
        if out["ledger"]:out["status"]="STOP_ALU"
        out["reason"]=str(ex)
    return out


def selector(k,producer,native,ref,orig):
    o=orig[k];query=o.get("scene_query",o["request"].get("scene_query"))
    return dict(backend=MODEL,policy=POLICY,record_id=k,parent_receipt_sha256=PSHA,
        producer_record_sha256=digest(producer[k]),native_record_sha256=digest(native[k]),
        reference_record_sha256=digest(ref[k]),original_record_sha256=digest(o),
        original_snapshot_sha256=digest(o["scene"]),original_query_sha256=digest(query))


def baseline():
    return dict(backend=MODEL,status="STOP_INPUT",reason=None,diagnostic=None,
        RN_nodes_executed=0,hex_bytes_calls=0,input_word_reads=0,float_decode_calls=0,decoded_components=0,
        sign_flips=0,word_format_calls=0,new_products=0,new_sqrt_calls=0,retained_numeric_replays=0,
        native_length=None,phase_error_bound=None,phase_certified=False,wavelength_known=False,
        physical_reference_certified=False,GPU_used=False,Bpy_used=False,shader_used=False,
        scene_engine_admitted=False,source_uncertainty_cancelled=False,full_costs="UNKNOWN_NOT_ZERO",
        promotion="STOP_FULL_SCENE_PAIR64_PHASE_PHYSICAL_GPU_AND_COSTS",
        scope="NATIVE_CPU64_WIDTH_OF_SEALED_PAIR_LENGTH_BOUNDS_HOST_CERT_ONLY")


def _audit(q,producer,native,ref,orig):
    out=baseline()
    try:
        require(type(q)is dict and type(q.get("record_id"))is str and q["record_id"]in producer,"closed_record")
        k=q["record_id"]
        require(q==selector(k,producer,native,ref,orig)and all(type(v)is str for v in q.values()),"closed_selector")
        p=producer[k]["result"];n=native[k]["result"]
        out.update(request_sha256=digest(q),upstream_status=p["status"],
                   retained_canonical_status=n["retained_canonical_status"])
        if p["status"]!="CPU_HOST_PAIR64_LENGTH_BYTES_ONLY":
            out.update(status="STOP_UPSTREAM",reason="sealed_STOP_not_rescued");return out
        z=p["envelope"];rz=ref[k]["result"]["diagnostic"]
        require(rz["original_scene"]==orig[k]["scene"]and rz["original_query"]==orig[k]["scene_query"],
                "same_original_box")
        require(z["word_type"]=="IEEE754_BINARY64"and z["pair_bytes"]==16 and z["payload_bytes"]==32
            and z["provenance_branch"]==prior.POLICY and z["source_uncertainty_cancelled"]is False,
            "sealed_ROOT64_pre_wire_type")
        Bs=[rational(v["retained_length_error_bound"])for v in z["certificates"]]
        require(len(Bs)==2,"two_original_bounds");v=width(z["payload_hex"],pair(Bs[0]+Bs[1]))
        for key in ("RN_nodes_executed","hex_bytes_calls","input_word_reads","float_decode_calls",
                    "decoded_components","sign_flips","word_format_calls"):out[key]=v[key]
        # Width reference interval uses both retained root enclosures, not outer-width as ground truth.
        roots=[[rational(x)for x in rr]for rr in rz["roots"]]
        ref_width_interval=[pair(roots[1][0]-roots[0][1]),pair(roots[1][1]-roots[0][0])]
        out["diagnostic"]=dict(consumer=v,producer_envelope_sha256=digest(z),
            original_snapshot_sha256=digest(orig[k]["scene"]),source="SOURCE0",detector="DETECTOR0",
            units="scene_length",retained_reference_width_interval=ref_width_interval,
            retained_reference_outer_width=rz["reference_width"],
            source_uncertainty_cancelled=False,legacy_ABI_status=z["legacy_ABI_status"],
            legacy_scalar_gate=z["legacy_scalar_gate"])
        if v["status"]=="CPU64_EXACT_PAIR_WIDTH_ONLY":
            out.update(status="CPU64_SCENE_PAIR_WIDTH_HOST_BOUND_ONLY",reason="native_width_partial_not_scene_engine")
        else:out.update(status="STOP_WIDTH_CONSUMER",reason=v["status"]+":"+str(v["reason"]))
    except (ValueError,TypeError,KeyError,IndexError,OSError)as ex:out["reason"]=str(ex)
    return out


def audit(q):
    try:
        producer,native,ref,orig,_,_=retained()
        return _audit(q,producer,native,ref,orig)
    except (ValueError,TypeError,KeyError,OSError)as ex:
        out=baseline();out["reason"]=str(ex);return out
