"""CPU-only four-term declared reference contrast. Two limbs, measured error charged."""
from pathlib import Path
from fractions import Fraction as F
import json,struct
import coplanar_clearance_CPU_v1 as c
import position_phase_pair64_encoder_CPU_v1 as encoding
import oblique_total_phase_pair64_CPU_v1 as arithmetic
ROOT=Path(__file__).resolve().parents[3]
MODEL="precision-position-phase-reference-native-CPU-v1"
PARENT="coordinacion/respuestas/PRECISION-POSITION-PHASE-REFERENCE-OVERLAY-HOST-001-CODEX.json"
PSHA="7c52f61504e126628ff54d76686ba6585abe9d0cf1a5ff8bf99a87d6fe686e14"
REP="CPU_RN64_PAIR_DECLARED_REFERENCE_CONTRAST_NOT_PHYSICAL_TOTAL"
INTENT="ALL16_BYTES_BEFORE_ALU_ALL_FOUR_TERMS_ERROR_CHARGED"
CAP=F(1,10000)
need,sha,digest,pair=c.need,c.sha,c.digest,c.pair
ORDER=(("SOURCE_POINT_0","target",3,1),("SOURCE_POINT_0","reference",1,-1),
       ("MATERIAL_OFFSET","target",3,1),("MATERIAL_OFFSET","reference",1,-1))

def retained():
    raw=(ROOT/PARENT).read_bytes();need(sha(raw)==PSHA and len(raw)==196856,"parent_identity");r=json.loads(raw)
    for path,h in r["code_doc_sha256"].items():need(sha((ROOT/path).read_bytes())==h,"ancestral_pin:"+path)
    v=c.capture(r["independent_pre"]);need(v["status"]=="PASS"and v["pins"]==216,"parent_oracle")
    need(r["root_calls"]==r["producer_replays"]==0,"no_parent_producer")
    d=c.capture(r["test_run"]);need(d["status"]=="PASS"and len(d["data"]["runs"])==336,"closed_parent_capture")
    e={x["id"]:x for x in d["data"]["runs"]};need(len(e)==336,"unique_records")
    pins=dict(r["code_doc_sha256"]);pins[PARENT]=PSHA;return e,pins

def selector(record,e):
    x=e[record];p=x["packet"]
    return dict(record_id=record,parent_receipt_sha256=PSHA,parent_record_sha256=digest(x),
        parent_parameters_sha256=digest(x["request"]),source_context_sha256=digest(p.get("source_context")),
        original_geometry_sha256=p.get("original_geometry_sha256")or digest(None),overlay_sha256=digest(p),
        representation=REP,intent=INTENT)

def baseline():
    r=c.baseline();r.update(model=MODEL,representation=REP,CPU_native_executed=False,
        CPU_binary64_conversion_executed=False,root_calls=0,RN64_conversions=0,decoded_words=0,decoded_term_words=0,
        sign_bit_flips=0,conversion_trace=[],trace=[],stages=[],reference_contrast_conditional=False,
        total_phase_certified=False,material_authenticated=False,wavelength_authenticated=False,
        optical_reference_certified=False,correlation_assumed=False,shared_phase_cancellation_assumed=False,
        periodic_wrapping_used=False,declared_uncertainty_only=True,parent_branches_unchanged=True,
        native_scalar_phase_output=False,pair_words_LE=None,error_rad_upper=None)
    return r

def normal(word):
    need(type(word)is str and len(word)==16,"binary64_word")
    b=int.from_bytes(bytes.fromhex(word),"little");exp=(b>>52)&2047
    need(exp!=2047 and(exp!=0 or b&((1<<63)-1)==0),"normal_zero_only")

def words(v):return [struct.pack("<d",x).hex()for x in v]
def exact(v):return sum((F.from_float(x)for x in v),F(0))

def _audit(model,q,raw,e):
    out=baseline()
    try:
        need(type(model)is str and model==MODEL,"explicit_model")
        need(type(q)is dict and type(q.get("record_id"))is str and q["record_id"]in e,"closed_record")
        expected=selector(q["record_id"],e)
        need(q==expected and set(q)==set(expected)and all(type(v)is str for v in q.values()),"closed_selector_identity")
        x=e[q["record_id"]];r=x["result"]
        need(r["status"]=="HOST_DECLARED_REFERENCE_CONTRAST_ONLY"and r["reference_overlay_conditional"]is True,"parent_STOP_not_rescued")
        d=r["rows"][0];g=d["parent_normalized_geometry"];p=x["packet"]
        ctx=p["source_context"]
        need(type(ctx)is dict and set(ctx)=={"provenance","synthetic_scene_sha256"}and ctx["provenance"]=="CPU_SYNTHETIC_ONLY_NOT_SEALED_SCENE","synthetic_scope_only")
        need(p["frame"]=="DECLARED_COMMON_TURNS_FRAME_NOT_CALIBRATED"and p["authentication"]=="DECLARED_NOT_PHYSICALLY_AUTHENTICATED"
             and p["reference_point"]==1 and p["target_point"]==3 and p["cap_rad"]==[1,10000],"declared_frame_only")
        want=bytes.fromhex("".join(g["output_words_LE"]))
        need(type(raw)is bytes and len(raw)==16 and raw==want,"ALL16bytes_before_decode")
        for w in g["output_words_LE"]:normal(w)
        value=struct.unpack("<dd",raw);out["decoded_words"]=2
        need(exact(value)==F(*g["decoded_output_exact_HOST"]),"pinned_geometry_value")
        base=sum((F(*d[k])for k in("geometric_radius_turns","encoding_error_turns","normalization_error_turns","all_four_phase_radius_turns")),F(0))
        need(8*base==F(*d["error_rad_upper"])<=CAP,"fixed_parent_budget")
        need(len(d["terms"])==4,"four_terms")
        encsum=F(0);addsum=F(0)
        for i,(term,identity)in enumerate(zip(d["terms"],ORDER)):
            kind,end,point,sign=identity
            need((term["kind"],term["endpoint"],term["point"],term["sign"])==identity,"component_identity")
            mid=encoding.internal(term["midpoint_turns"])
            need(mid==0 or abs(mid)>=encoding.MIN,"subnormal_midpoint_NO_CONVERSION")
            hi,hw=encoding.convert(mid,out);residual=mid-F.from_float(hi)
            need(residual==0 or abs(residual)>=encoding.MIN,"subnormal_residual_STOP_AFTER_HIGH")
            lo,lw=encoding.convert(encoding.internal(pair(residual)),out);encoded=(hi,lo);encerr=abs(exact(encoded)-mid)
            signed_words=[hw,lw]
            if sign==-1:
                signed_words=[(int.from_bytes(bytes.fromhex(w),"little")^(1<<63)).to_bytes(8,"little").hex()for w in signed_words]
                out["sign_bit_flips"]+=2
            signed=tuple(struct.unpack("<d",bytes.fromhex(w))[0]for w in signed_words);out["decoded_term_words"]+=2
            before=words(value);expected_value=exact(value)+sign*exact(encoded)
            result=arithmetic.plus(value,signed,"term"+str(i),out["trace"])
            err=abs(exact(result)-expected_value);encsum+=encerr;addsum+=err
            out["stages"].append(dict(index=i,kind=kind,endpoint=end,point=point,sign=sign,midpoint_turns=pair(mid),
                radius_turns=term["radius_turns"],encoded_words_LE=[hw,lw],signed_words_LE=signed_words,
                before_words_LE=before,after_words_LE=words(result),encoding_error_turns=pair(encerr),addition_error_turns=pair(err)))
            for node in out["trace"][i*26:]:
                for w in(node["a"],node["b"],node["y"]):normal(w)
            value=result
        bound=8*(base+encsum+addsum);low,high=map(lambda v:F(*v),d["interval_contrast_turns"])
        direct=8*max(abs(exact(value)-low),abs(exact(value)-high))
        diag=dict(parent_record_sha256=digest(x),input_frame_sha256=sha(raw),input_words_LE=g["output_words_LE"],
            output_words_LE=words(value),decoded_output_exact_HOST=pair(exact(value)),new_encoding_error_turns=pair(encsum),
            new_addition_error_turns=pair(addsum),parent_budget_turns=pair(base),error_rad_upper=pair(bound),
            direct_error_rad_upper=pair(direct),cap_rad=pair(CAP),scope="CPU_SYNTHETIC_DECLARED_REFERENCE_CONTRAST_NOT_PHYSICAL_TOTAL")
        out["diagnostics"]=[diag]
        need(direct<=bound,"direct_bound_dominated")
        need(len(out["trace"])==104 and out["RN64_conversions"]==8 and out["sign_bit_flips"]==4,"closed_native_graph")
        need(bound<=CAP,"native_reference_budget_exhausted")
        out.update(status="CPU_NATIVE_PAIR_DECLARED_REFERENCE_CONTRAST_ONLY",rows=[diag],pair_words_LE=words(value),
            reference_contrast_conditional=True,error_rad_upper=pair(bound))
    except(ValueError,TypeError,KeyError,IndexError,OverflowError)as ex:out["reason"]=str(ex)
    finally:
        out["RN64_operations"]=len(out["trace"]);out["CPU_native_executed"]=out["RN64_operations"]>0
    return out

def audit(model,request,raw_frame):
    try:e,_=retained()
    except(ValueError,TypeError,KeyError,OSError)as ex:
        r=baseline();r["reason"]="evidence_integrity:"+str(ex);return r
    return _audit(model,request,raw_frame,e)
