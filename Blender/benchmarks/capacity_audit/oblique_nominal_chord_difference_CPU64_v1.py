"""New opt-in CPU64 signed length-reference subtraction, HOST certified, no phase."""
from pathlib import Path
from fractions import Fraction as F
import json,struct
import oblique_nominal_chord_difference_HOST_v1 as prior
ROOT=Path(__file__).resolve().parents[3]
MODEL="oblique-nominal-chord-difference-CPU64-v1"
POLICY="SAME_ORIGINAL_SIGNED_LENGTH_MINUS_EXPLICIT_NOMINAL_REF_PAIR64_FIXED26_EXACT_RESIDUAL0"
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-NOMINAL-CHORD-DIFFERENCE-HOST-001-CODEX.json"
PSHA="b01d94f36d904d724029dc0c0d33904ea449390468324efaa72a4e275293b424"
PRODUCER="coordinacion/respuestas/PRECISION-OBLIQUE-SCENE-PAIR64-PAYLOAD-CPU-001-CODEX.json"
PRODSHA="ed228edd01ecced262362ff2ac8853cba434ce1e359cdfa2385017294f9dbbe9"
require,sha,capture,digest=prior.need,prior.sha,prior.capture,prior.digest
pair,rational=prior.pair,prior.rat

def retained():
    b=(ROOT/PARENT).read_bytes();require(len(b)==156906 and sha(b)==PSHA,"parent_seal")
    r=json.loads(b);pins=dict(r["code_doc_sha256"]);require(len(pins)==323,"parent_pins")
    for p,h in pins.items():require(sha((ROOT/p).read_bytes())==h,"dependency:"+p)
    require(capture(r["independent_pre"])["status"]=="PASS","parent_oracle")
    d=capture(r["test_run"]);require(d["status"]=="PASS","parent_capture")
    parent={x["id"]:x for x in d["evidence"]["records"]}
    require(pins[PRODUCER]==PRODSHA,"explicit_ROOT64_producer")
    p=(ROOT/PRODUCER).read_bytes();require(len(p)==242660 and sha(p)==PRODSHA,"producer_seal")
    pd=capture(json.loads(p)["test_run"]);producer={x["id"]:x for x in pd["evidence"]["records"]}
    require(set(parent)==set(producer)and len(parent)==16,"closed_records")
    pins[PARENT]=PSHA
    return parent,producer,pins

def encode_reference(p):
    # Explicit new HOST RN64 pair representation of a sealed rational endpoint.
    out=dict(status="STOP_REFERENCE_ENCODING",rational=p,words=None,payload_hex=None,
        HOST_float_conversions=0,HOST_word_formats=0,HOST_exact_pair_sum=None,
        HOST_signed_encoding_residual=None,HOST_encoding_error_bound=None)
    try:
        x=rational(p);require(0<=x<=2**33,"reference_domain")
        hi=float(x);out["HOST_float_conversions"]+=1
        lo=float(x-F.from_float(hi));out["HOST_float_conversions"]+=1
        words=[struct.pack("<d",v).hex()for v in (hi,lo)];out["HOST_word_formats"]=2
        y=F.from_float(hi)+F.from_float(lo);E=x-y
        out.update(words=words,payload_hex="".join(words),HOST_exact_pair_sum=pair(y),
            HOST_signed_encoding_residual=pair(E),HOST_encoding_error_bound=pair(abs(E)))
        require(all(v==0 or abs(F.from_float(v))>=F(1,2**1022)for v in (hi,lo)),"normal_zero_reference_words")
        require(E==0,"reference_pair_exact_residual0")
        out["status"]="HOST_EXACT_REFERENCE_PAIR64_ONLY"
    except(ValueError,TypeError,KeyError,OverflowError)as ex:out["reason"]=str(ex)
    return out

def difference(payload,inherited_bound):
    out=dict(status="STOP_INPUT",reason=None,input_payload_hex=payload,inherited_bound=inherited_bound,
        ledger=[],RN_nodes_executed=0,fixed_RN_budget=26,hex_bytes_calls=0,input_word_reads=0,
        float_decode_calls=0,decoded_components=0,sign_flips=0,word_format_calls=0,
        input_difference=None,candidate_pair_words=None,native_pair_difference=None,HOST_signed_residual=None,
        HOST_arithmetic_error_bound=None,HOST_total_difference_error_bound=None,HOST_difference_interval=None,
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
        out["input_difference"]=pair(W);require(abs(W)<=2**34,"signed_difference_domain")

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
        out.update(native_pair_difference=pair(C),HOST_signed_residual=pair(E),HOST_arithmetic_error_bound=pair(abs(E)),
            HOST_total_difference_error_bound=pair(T),HOST_difference_interval=[pair(C-T),pair(C+T)])
        require(out["RN_nodes_executed"]==26,"fixed26_candidate")
        if E!=0:out.update(status="STOP_PAIR_DIFFERENCE_RESIDUAL",reason="nonzero_pair_difference_residual")
        else:out.update(status="CPU64_EXACT_PAIR_DIFFERENCE_ONLY",reason="fixed26_signed_difference_not_scene_or_phase")
    except (ValueError,TypeError,KeyError,OverflowError,struct.error)as ex:
        if out["ledger"]:out["status"]="STOP_ALU"
        out["reason"]=str(ex)
    return out

def selector(k,parent,producer):
    q=parent[k]["request"]
    return dict(model=MODEL,policy=POLICY,record_id=k,parent_receipt_sha256=PSHA,
        parent_record_sha256=digest(parent[k]),producer_record_sha256=digest(producer[k]),
        original_snapshot_sha256=q["original_snapshot_sha256"],original_query_sha256=q["original_query_sha256"],
        source="SOURCE0",detector="DETECTOR0",units="scene_length",
        reference_role="DECLARED_NOMINAL_STRAIGHT_CHORD_NOT_OPTICAL")

def baseline():
    return dict(model=MODEL,status="STOP_INPUT",reason=None,diagnostic=None,
        RN_nodes_executed=0,HOST_float_conversions=0,HOST_word_formats=0,
        new_native_products=0,new_native_sqrt=0,new_HOST_roots=0,retained_numeric_replays=0,
        source_uncertainty_cancelled=False,correlation_assumed=False,wavelength_known=False,
        phase_certified=False,physical_reference_certified=False,scene_authenticated=False,
        scene_engine_admitted=False,GPU_used=False,Bpy_used=False,phase_error_bound=None,
        full_costs="UNKNOWN_NOT_ZERO",promotion="STOP_FULL_SCENE_PHASE_PHYSICAL_GPU_AND_FULL_COSTS",
        scope="NEW_PARTIAL_NATIVE_CPU64_SIGNED_DIFFERENCE_HOST_REFERENCE_ENCODING_AND_BOUND")

def _audit(q,parent,producer):
    out=baseline()
    try:
        require(type(q)is dict and type(q.get("record_id"))is str and q["record_id"]in parent,"closed_record")
        k=q["record_id"];require(q==selector(k,parent,producer)and all(type(v)is str for v in q.values()),"closed_selector")
        r=parent[k]["result"];p=producer[k]["result"]
        out.update(request_sha256=digest(q),upstream_status=r["status"])
        if r["status"]!="HOST_DECLARED_NOMINAL_CHORD_DIFFERENCE_ONLY":
            out.update(status="STOP_UPSTREAM",reason="sealed_STOP_not_rescued");return out
        z=r["diagnostic"];e=p["envelope"]
        require(p["status"]=="CPU_HOST_PAIR64_LENGTH_BYTES_ONLY"and e["pair_bytes"]==16
            and e["payload_bytes"]==32 and e["word_type"]=="IEEE754_BINARY64"
            and e["provenance_branch"]=="EXPLICIT_ROOT64_PRE_WIRE_BYTES_NOT_PAIR32_REPAIR_OR_ENGINE","ROOT64_partial_type")
        require(z["original_snapshot_sha256"]==e["original_snapshot_sha256"]==q["original_snapshot_sha256"]
            and z["original_query_sha256"]==e["original_query_sha256"]==q["original_query_sha256"]
            and e["source"]==z["source"]==q["source"]and e["detector"]==z["detector"]==q["detector"]
            and z["units"]==e["units"]==q["units"],"same_original_context")
        require(e["source_uncertainty_cancelled"]is False and z["reference_role"]==q["reference_role"],"no_reference_alias")
        text=e["payload_hex"];require(type(text)is str and len(text)==64 and sha(text.encode("ascii"))==e["payload_hex_ASCII_sha256"],"sealed_length_payload")
        refs=[encode_reference(v)for v in z["reference_root96"]]
        out["HOST_float_conversions"]=sum(v["HOST_float_conversions"]for v in refs)
        out["HOST_word_formats"]=sum(v["HOST_word_formats"]for v in refs)
        out["diagnostic"]=dict(reference_encoding=refs,subtractions=[],original_snapshot_sha256=q["original_snapshot_sha256"],
            original_query_sha256=q["original_query_sha256"],source=q["source"],detector=q["detector"],units=q["units"],
            reference_role=q["reference_role"],ALL15_original_radii=z["ALL15_original_radii"],
            HOST_reference_difference_interval=z["signed_difference_interval"],native_difference_outer_interval=None,
            reference_rounding_width=z["reference_rounding_width"],reference_rounding_charged="R_UPPER_AT_LOWER_AND_R_LOWER_AT_UPPER_NO_CANCELLATION",
            width_operand_used=False,legacy_scalar_gate=e["legacy_scalar_gate"],legacy_ABI_status=e["legacy_ABI_status"])
        require(all(v["status"]=="HOST_EXACT_REFERENCE_PAIR64_ONLY"for v in refs),"reference_encoding_STOP")
        for i,j in ((0,1),(1,0)):
            cert=e["certificates"][i];require(cert["bound"]==("lower","upper")[i],"ordered_length_certificate")
            B=rational(cert["retained_length_error_bound"])+rational(refs[j]["HOST_encoding_error_bound"])
            # Kernel input word order: reference hi/lo, length hi/lo, output length-reference.
            v=difference(refs[j]["payload_hex"]+text[32*i:32*i+32],pair(B))
            out["RN_nodes_executed"]+=v["RN_nodes_executed"]
            out["diagnostic"]["subtractions"].append(dict(bound=cert["bound"],reference_endpoint=("lower","upper")[j],
                retained_length_certificate=cert,consumer=v))
        vv=[x["consumer"]for x in out["diagnostic"]["subtractions"]]
        if any(x["status"]!="CPU64_EXACT_PAIR_DIFFERENCE_ONLY"for x in vv):
            out.update(status="STOP_NATIVE_DIFFERENCE",reason="candidate_and_ledger_preserved_exact_residual0_invariant");return out
        lo=rational(vv[0]["native_pair_difference"])-rational(vv[0]["HOST_total_difference_error_bound"])
        hi=rational(vv[1]["native_pair_difference"])+rational(vv[1]["HOST_total_difference_error_bound"])
        D=[rational(v)for v in z["signed_difference_interval"]]
        require(lo<=D[0]<=0<=D[1]<=hi,"HOST_reference_inside_native_outer_interval")
        out["diagnostic"]["native_difference_outer_interval"]=[pair(lo),pair(hi)]
        out.update(status="CPU64_SIGNED_DIFFERENCE_PAIR_HOST_BOUND_ONLY",
            reason="signed_pairs_of_sealed_partial_inputs_not_scene_or_phase")
    except(ValueError,TypeError,KeyError,IndexError,OSError,OverflowError)as ex:out["reason"]=str(ex)
    return out

def audit(q):
    try:p,n,_=retained();return _audit(q,p,n)
    except(ValueError,TypeError,KeyError,OSError)as ex:
        out=baseline();out["reason"]="evidence_integrity:"+str(ex);return out
