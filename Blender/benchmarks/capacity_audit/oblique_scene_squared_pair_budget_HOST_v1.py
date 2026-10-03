"""HOST canonical-pair budget for sealed original-box sums, NOT native accumulation."""
from pathlib import Path
from fractions import Fraction as F
import json,struct
import oblique_scene_box_product_EFT_CPU_v1 as prod
ROOT=Path(__file__).resolve().parents[3]
MODEL="oblique-scene-squared-pair-budget-HOST-v1"
POLICY="CANONICAL_RN_HI_RN_RESIDUAL_LO_ORIGINAL_BOX_ONLY"
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-BOX-PRODUCT-EFT-CPU-001-CODEX.json"
PSHA="5ab5e9df53f03d6f5fb5bb95fd718fb269babcc0c624902935c3f5540101b007"
require,sha,capture,digest=prod.require,prod.sha,prod.capture,prod.digest
pair,word=prod.pair,prod.word

def frac(w):return prod.ref.sealed.decode_word(w)

def retained():
    raw=(ROOT/PARENT).read_bytes();require(len(raw)==79023 and sha(raw)==PSHA,"parent_seal")
    r=json.loads(raw);pins=dict(r["code_doc_sha256"]);require(len(pins)==276,"parent_pins")
    for p,h in pins.items():require(sha((ROOT/p).read_bytes())==h,"dependency:"+p)
    require(capture(r["independent_pre"])["status"]=="PASS","parent_oracle")
    d=capture(r["test_run"])["evidence"];e={x["id"]:x for x in d["records"]}
    reference,orig,_=prod.retained();require(set(e)==set(reference)==set(orig)and len(e)==16,"closed_records")
    pins[PARENT]=PSHA
    return e,reference,orig,pins

def selector(k,e,reference,orig):
    o=orig[k];q=o.get("scene_query",o["request"].get("scene_query"))
    return dict(backend=MODEL,policy=POLICY,record_id=k,parent_receipt_sha256=PSHA,
        parent_record_sha256=digest(e[k]),reference_record_sha256=digest(reference[k]),
        original_record_sha256=digest(o),original_snapshot_sha256=digest(o["scene"]),original_query_sha256=digest(q))

def compress(v,lower):
    """Actual HOST float casts of exact total, NOT TwoSum/native sum graph."""
    out=dict(status="STOP_INPUT",reason=None,exact_squared=None,hi_word=None,lo_word=None,
        candidate_sum=None,residual=None,canonical_exact=None,length_lower_bound=None,
        length_error_bound=None,squared_enclosure=None,HOST_float_casts=0,HOST_bound_divisions=0)
    try:
        require(type(v)is F and type(lower)is F and 0<v<=F(2**66)and lower>0 and lower*lower<=v,"positive_certified_domain")
        out.update(exact_squared=pair(v),length_lower_bound=pair(lower))
        h=float(v);out["HOST_float_casts"]+=1;remain=v-F.from_float(h)
        l=float(remain);out["HOST_float_casts"]+=1
        out.update(hi_word=word(h),lo_word=word(l))
        require(prod.normal(h)and prod.normal(l)and(l!=0.0 or remain==0),"cast_normal_no_underflow")
        q=F.from_float(h)+F.from_float(l);r=v-q
        out.update(candidate_sum=pair(q),residual=pair(r),canonical_exact=r==0)
        require(q>0 and lower*lower<=q,"common_lower_bound")
        budget=abs(r)/(2*lower);out["HOST_bound_divisions"]=1
        out.update(length_error_bound=pair(budget),squared_enclosure=[pair(q-abs(r)),pair(q+abs(r))],
            status="HOST_CANONICAL_PAIR_EXACT_ONLY"if r==0 else"STOP_CANONICAL_PAIR_EXACT_SUM",
            reason="canonical_pair_exact_not_native_sum"if r==0 else"nonzero_canonical_residual_preserved")
    except(ValueError,TypeError,OverflowError,ZeroDivisionError)as ex:out["reason"]=str(ex)
    return out

def baseline():
    return dict(backend=MODEL,status="STOP_INPUT",reason=None,diagnostic=None,HOST_float_casts=0,
        HOST_word_decodes=0,HOST_bound_divisions=0,CPU_native_arithmetic=False,native_sum=None,native_length=None,
        native_root_calls=0,new_products=0,new_transport_calls=0,new_predicate_calls=0,retained_suite_replays=0,
        source_uncertainty_cancelled=False,phase_certified=False,phase_error_bound=None,wavelength_known=False,
        physical_reference_certified=False,GPU_used=False,full_costs="UNKNOWN_NOT_ZERO",
        promotion="STOP_NATIVE_LENGTH_PHASE_PHYSICAL_GPU",
        bound_scope="ISOLATED_HOST_CANONICAL_COMPRESSION_NOT_TOTAL_PIPELINE")

def _audit(q,e,reference,orig):
    out=baseline()
    try:
        require(type(q)is dict and type(q.get("record_id"))is str and q["record_id"]in e,"closed_record")
        k=q["record_id"];require(q==selector(k,e,reference,orig)and all(type(v)is str for v in q.values()),"closed_selector")
        x=e[k];p=x["result"];r=reference[k]["result"];o=orig[k]
        out.update(request_sha256=digest(q),upstream_status=p["status"])
        if p["status"]!="CPU64_ORIGINAL_BOX_PRODUCTS_ONLY":
            out.update(status="STOP_UPSTREAM",reason="sealed_STOP_not_rescued");return out
        require(x["request"]==prod.selector(k,reference,orig),"parent_scene_binding")
        z=r["diagnostic"];require(r["status"]=="HOST_SAME_ORIGINAL_BOX_REFERENCE_ONLY"
            and z["original_scene"]==o["scene"]and z["original_query"]==o["scene_query"],"reference_original_binding")
        require(len(p["endpoints"])==len(p["products"])==6,"six_original_endpoints")
        squares=[]
        for i,(ep,pp)in enumerate(zip(p["endpoints"],p["products"])):
            ax,side=divmod(i,2);require((ep["axis"],ep["side"],pp["axis"],pp["side"])==(ax,side,ax,side),"endpoint_order")
            v=F(*z["extrema"]["delta"][ax][side]);require(ep["encoding"]["exact"]==pair(v),"original_delta")
            require([t["term"]for t in pp["terms"]]==["hh","hl","lh","ll"],"four_terms")
            total=F(0)
            for t in pp["terms"]:
                t=t["result"];require(t["status"]=="CPU64_EFT_PRODUCT_ONLY","parent_product_STOP")
                total+=frac(t["hi_word"])+frac(t["lo_word"]);out["HOST_word_decodes"]+=2
            require(total==v*v,"sealed_endpoint_square_exact");squares.append(total)
        intervals=[]
        for ax in range(3):
            a,b=map(lambda v:F(*v),z["extrema"]["delta"][ax])
            aa,bb=squares[2*ax:2*ax+2]
            intervals.append((F(0)if a<=0<=b else min(aa,bb),max(aa,bb)))
        sl,sh=sum(v[0]for v in intervals),sum(v[1]for v in intervals)
        require([pair(sl),pair(sh)]==z["extrema"]["squared"],"same_original_box_sum")
        lower=F(*z["reference_interval"][0]);width=F(*z["reference_width"])
        require(lower>0 and width>0,"positive_reference_bound_and_width")
        a,b=compress(sl,lower),compress(sh,lower)
        out.update(HOST_float_casts=a["HOST_float_casts"]+b["HOST_float_casts"],
            HOST_bound_divisions=a["HOST_bound_divisions"]+b["HOST_bound_divisions"])
        out["diagnostic"]=dict(squared_original=[pair(sl),pair(sh)],candidate_compressions=[a,b],
            original_snapshot_sha256=digest(o["scene"]),reference_record_sha256=digest(reference[k]),
            geometric_reference_width=pair(width),units_squared="scene_length_squared",units_bound="scene_length",
            source="SOURCE0",detector="DETECTOR0")
        require(all(c["status"]in("HOST_CANONICAL_PAIR_EXACT_ONLY","STOP_CANONICAL_PAIR_EXACT_SUM")for c in(a,b)),"compression_domain_STOP")
        budget=max(F(*a["length_error_bound"]),F(*b["length_error_bound"]))
        ratio=budget/width;out["HOST_bound_divisions"]+=1
        out["diagnostic"].update(max_length_error_bound=pair(budget),error_bound_over_box_width=pair(ratio))
        nonzero=not(a["canonical_exact"]and b["canonical_exact"])
        out.update(status="STOP_CANONICAL_PAIR_EXACT_SUM"if nonzero else"HOST_CANONICAL_PAIR_EXACT_ONLY",
            reason="nonzero_canonical_residual_preserved"if nonzero else"canonical_pair_exact_not_native_sum")
    except(ValueError,TypeError,KeyError,IndexError,OSError,ZeroDivisionError)as ex:out["reason"]=str(ex)
    return out

def audit(q):
    try:e,reference,orig,_=retained()
    except(ValueError,TypeError,KeyError,OSError)as ex:
        out=baseline();out["reason"]="evidence_integrity:"+str(ex);return out
    return _audit(q,e,reference,orig)
