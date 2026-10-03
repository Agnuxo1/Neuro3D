"""HOST length enclosures from sealed native pair words; no native replay."""
from pathlib import Path
from fractions import Fraction as F
import json,struct,re
import coplanar_clearance_CPU_v1 as c
ROOT=Path(__file__).resolve().parents[3]
MODEL="precision-position-pair-length-HOST-v1"
PARENT="coordinacion/respuestas/PRECISION-POSITION-PAIR-RECENTER-NATIVE-CPU-001-CODEX.json"
PSHA="12ea3f705ab4397de8057854dc1ba11bfd6fa2f704bb68492f2c29e77d9a7944"
LENGTH="Blender/benchmarks/capacity_audit/oblique_common_detector_length_CPU_v1.py"
LSHA="f510517d0c91c45e9ebaadfe593a4c8116e4587bb3eb4d06be7a0ab651079c49"
REP="EXACT_HOST_PAIR_WORDS_RATIONAL_ROOT_INTERVAL_96BITS"
INTENT="LENGTH_AND_SAME_GEOMETRY_END_REFERENCE_ONLY"
need,sha,digest,pair=c.need,c.sha,c.digest,c.pair

def restore(v):
    z=dict(v);mode=z.pop("rows_mode");h=z.pop("result_sha256")
    need(mode in ("EMPTY","DIAGNOSTICS"),"rows_mode")
    z["rows"]=[] if mode=="EMPTY" else z["diagnostics"]
    need(digest(z)==h,"captured_result_identity");return z

def retained():
    raw=(ROOT/PARENT).read_bytes();need(sha(raw)==PSHA and len(raw)==90899,"parent_identity");r=json.loads(raw)
    for p,h in r["code_doc_sha256"].items():need(sha((ROOT/p).read_bytes())==h,"ancestral_pin:"+p)
    need(r["code_doc_sha256"][LENGTH]==LSHA and c.capture(r["independent_pre"])["status"]=="PASS","parent_oracle_root")
    rows=c.capture(r["test_run"])["data"]["runs"];e={}
    for x in rows:
        if x["id"].startswith("retained:"):
            z=dict(x);z["result"]=restore(x["result"]);e[x["id"]]=z
    need(len(e)==20 and sum(x["result"]["status"]=="CPU_POSITION_PAIR_RECENTER_ONLY" for x in e.values())==8,"closed_twenty_records")
    pins=dict(r["code_doc_sha256"]);pins[PARENT]=PSHA
    return e,pins

def selector(record,e):
    x=e[record]
    return dict(record_id=record,parent_receipt_sha256=PSHA,parent_record_sha256=digest(x),
        original_geometry_sha256=x["request"]["geometry_sha256"],relative_geometry_sha256=digest(x["result"]["relative_geometry"]),
        representation=REP,intent=INTENT)

def word64(h):
    need(type(h)is str and re.fullmatch("[0-9a-f]{16}",h)is not None,"typed_LE_binary64_word")
    w=int.from_bytes(bytes.fromhex(h),"little");ex=(w>>52)&2047;mant=w&((1<<52)-1)
    need(ex!=2047 and (ex!=0 or mant==0),"normal_or_zero_word")
    v=F(0) if ex==0 else (-1 if w>>63 else 1)*F((1<<52)+mant)*F(2)**(ex-1075)
    need(max(abs(v.numerator).bit_length(),v.denominator.bit_length())<=128 and abs(v)<=10**6,"bounded_limb")
    return v

def root(s):
    need(sha((ROOT/LENGTH).read_bytes())==LSHA,"pinned_root")
    import oblique_common_detector_length_CPU_v1 as length
    need(length.BITS==96,"fixed_96bits")
    return length.root_bracket(s)

def baseline():
    r=c.baseline();r.update(model=MODEL,representation=REP,CPU_native_executed=False,length_enclosure_verified=False,
        optical_reference_certified=False,reference_scope="SAME_GEOMETRY_END_LENGTH_NOT_OPTICAL_REFERENCE",
        lengths=[],relative_lengths=[],HOST_cost=dict(pair_words_decoded=0,exact_pair_sums=0,squared_norms=0,sqrt_brackets=0,reference_subtractions=0),
        original_geometry_sha256=None,relative_geometry_sha256=None,parent_native_execution_replayed=False)
    return r

def _audit(model,q,e):
    out=baseline()
    try:
        need(type(model)is str and model==MODEL,"explicit_model")
        need(type(q)is dict and type(q.get("record_id"))is str and q["record_id"]in e,"closed_record")
        expected=selector(q["record_id"],e)
        need(q==expected and set(q)==set(expected)and all(type(v)is str for v in q.values()),"closed_selector_identity")
        x=e[q["record_id"]];r=x["result"]
        need(r["status"]=="CPU_POSITION_PAIR_RECENTER_ONLY" and r["exact_pair_recenter_verified"]is True,"parent_STOP_not_rescued")
        need(len(r["diagnostics"])==1 and len(r["output_pairs"])==15,"complete_parent")
        d=r["diagnostics"][0];g=d["original_geometry"];local=r["relative_geometry"]
        need(digest(g)==q["original_geometry_sha256"] and digest(local)==q["relative_geometry_sha256"],"geometry_identity")
        points=[g["origin_BU"],g["end_BU"]]+g["triangle_BU"];origin=g["origin_BU"]
        expected_points=[[pair(F(*p[k])-F(*origin[k]))for k in range(3)]for p in points]
        expected_context=dict(original_context=g["context"],coordinate_frame="NATIVE_CPU_PAIR64_POINT_MINUS_SOURCE_ORIGIN_KEEP_LIMBS",
            frame_origin_BU=origin,original_geometry_sha256=digest(g))
        expected_geometry=dict(origin_BU=expected_points[0],end_BU=expected_points[1],triangle_BU=expected_points[2:],context=expected_context)
        need(local==expected_geometry and d["relative_geometry"]==local,"explicit_original_translation")
        need(d["all_original_error_radii_zero"]is True and len(d["coordinates"])==15,"exact_parent_coordinates")
        decoded=[]
        for i,(p,t)in enumerate(zip(r["output_pairs"],d["coordinates"])):
            need(set(p)=={"point","coordinate","hi_word_le_hex","lo_word_le_hex"}and type(p["point"])is int and type(p["coordinate"])is int
                and (p["point"],p["coordinate"])==(i//3,i%3),"all_unique_ordered_coordinates")
            need(t["exact_pair_difference"]is True and t["error_abs_BU"]==[0,1] and
                all(p[k]==t[k]for k in ("point","coordinate","hi_word_le_hex","lo_word_le_hex")),"captured_pair_identity")
            hi,lo=word64(p["hi_word_le_hex"]),word64(p["lo_word_le_hex"])
            out["HOST_cost"]["pair_words_decoded"]+=2;out["HOST_cost"]["exact_pair_sums"]+=1
            v=hi+lo
            need(v==F(*expected_points[i//3][i%3]),"word_pair_against_ORIGINAL")
            decoded.append(v)
        need(decoded[:3]==[F(0)]*3,"source_at_local_origin")
        records=[]
        for i in range(1,5):
            delta=decoded[3*i:3*i+3];s=sum(v*v for v in delta)
            out["HOST_cost"]["squared_norms"]+=1
            lo,hi=root(s);out["HOST_cost"]["sqrt_brackets"]+=1
            records.append(dict(point=i,from_point=0,delta_BU=list(map(pair,delta)),squared_BU2=pair(s),
                length_interval_BU=[pair(lo),pair(hi)],width_BU=pair(hi-lo),fractional_bits=96))
        ref=records[0];reflo,refhi=map(lambda v:F(*v),ref["length_interval_BU"]);relative=[]
        for row in records:
            if row["point"]==1:lo=hi=F(0);basis="IDENTICAL_RANDOM_VARIABLE_CANCELS_EXACTLY"
            else:
                l,h=map(lambda v:F(*v),row["length_interval_BU"]);lo,hi=l-refhi,h-reflo
                basis="CONSERVATIVE_INTERVAL_DIFFERENCE_NO_CORRELATION_ASSUMED";out["HOST_cost"]["reference_subtractions"]+=2
            relative.append(dict(point=row["point"],reference_point=1,difference_interval_BU=[pair(lo),pair(hi)],basis=basis))
        diag=dict(selector=q,parent_record_sha256=digest(x),original_geometry=g,relative_geometry=local,
            input_pairs_sha256=digest(r["output_pairs"]),source_context=g["context"],lengths=records,relative_lengths=relative,
            fixed_resolution_limit="A_POSITION_GAP_IS_NOT_A_LENGTH_OR_PHASE_GUARANTEE")
        out.update(status="HOST_PAIR_LENGTH_ENCLOSURE_ONLY",rows=[diag],diagnostics=[diag],verified_queries=1,
            length_enclosure_verified=True,lengths=records,relative_lengths=relative,
            original_geometry_sha256=digest(g),relative_geometry_sha256=digest(local))
    except(ValueError,TypeError,KeyError,IndexError,ZeroDivisionError,OverflowError,struct.error,OSError)as ex:out["reason"]=str(ex)
    return out

def audit(model,request):
    try:e,_=retained()
    except(ValueError,TypeError,KeyError,OSError)as ex:
        r=baseline();r["reason"]="evidence_integrity:"+str(ex);return r
    return _audit(model,request,e)
