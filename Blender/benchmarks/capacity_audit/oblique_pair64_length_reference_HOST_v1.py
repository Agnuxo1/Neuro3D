"""HOST same-ORIGINAL-box reference vs sealed CPU64 width; not optical/native."""
from pathlib import Path
from fractions import Fraction as F
import json
import oblique_pair64_interval_consumer_CPU_v1 as sealed
import oblique_finite_interval_HOST_v1 as host
import oblique_common_detector_length_CPU_v1 as lattice
ROOT=Path(__file__).resolve().parents[3]
MODEL="oblique-pair64-length-reference-HOST-v1"
POLICY="SAME_ORIGINAL_ALL_RADII_CONTINUOUS_BOX_FIXED96_ONLY"
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-PAIR64-LENGTH-CPU-001-CODEX.json"
PSHA="1de93e48c76b96904d17d0ccfa994c992fa7bbb69deefe0f7fa3f4dd354ad94d"
ORIGINAL="coordinacion/respuestas/PRECISION-OBLIQUE-SCENE-PAIR64-CPU-001-CODEX.json"
OSHA="813fd728006a90adb40f99d1eb49aa3523f8f63bf61edca7775e332dc57106ea"
ROOTCODE="Blender/benchmarks/capacity_audit/oblique_common_detector_length_CPU_v1.py"
ROOTSHA="f510517d0c91c45e9ebaadfe593a4c8116e4587bb3eb4d06be7a0ab651079c49"
require,sha,capture=sealed.require,sealed.sha,sealed.capture
digest=host.digest
def pair(x):return [x.numerator,x.denominator]

def retained():
    raw=(ROOT/PARENT).read_bytes();require(len(raw)==193411 and sha(raw)==PSHA,"parent_seal")
    r=json.loads(raw);require(len(r["code_doc_sha256"])==268,"parent_pins")
    for p,h in r["code_doc_sha256"].items():require(sha((ROOT/p).read_bytes())==h,"dependency:"+p)
    require(r["code_doc_sha256"][ROOTCODE]==ROOTSHA and lattice.BITS==96,"frozen_root96")
    require(capture(r["independent_pre"])["status"]=="PASS","sealed_parent_oracle")
    d=capture(r["test_run"])["evidence"];e={x["id"]:x for x in d["records"]}
    raw=(ROOT/ORIGINAL).read_bytes();require(len(raw)==84149 and sha(raw)==OSHA,"original_seal")
    o=capture(json.loads(raw)["test_run"])["evidence"]
    orig={"scene:"+x["name"]:x for x in o["records"]};orig["native_inexact"]=o["inexact"]
    orig.update({"input:"+x["name"]:x for x in o["invalid"]})
    require(set(e)==set(orig)and len(e)==16,"closed_records")
    pins=dict(r["code_doc_sha256"]);pins[PARENT]=PSHA
    return e,orig,pins

def selector(k,e,orig):
    x,o=e[k],orig[k]
    query=o.get("scene_query",o["request"].get("scene_query"))
    return dict(backend=MODEL,policy=POLICY,record_id=k,parent_receipt_sha256=PSHA,
        parent_record_sha256=digest(x),original_receipt_sha256=OSHA,original_record_sha256=digest(o),
        original_snapshot_sha256=digest(o["scene"]),original_query_sha256=digest(query),
        length_frame_sha256=digest(x["result"].get("scene")),root_algorithm_sha256=ROOTSHA)

def box_extrema(boxes):
    a,b=boxes["origin"],boxes["detector"];delta=[];squares=[];lower_witness=[[],[]];upper_witness=[[],[]]
    for aa,bb in zip(a,b):
        lo,hi=bb[0]-aa[1],bb[1]-aa[0];delta.append((lo,hi))
        if lo<=0<=hi:
            v=max(aa[0],bb[0]);require(v<=min(aa[1],bb[1]),"zero_delta_witness")
            mn=F(0);lower_witness[0].append(v);lower_witness[1].append(v)
        elif lo>0:
            mn=lo*lo;lower_witness[0].append(aa[1]);lower_witness[1].append(bb[0])
        else:
            mn=hi*hi;lower_witness[0].append(aa[0]);lower_witness[1].append(bb[1])
        if lo*lo>=hi*hi:
            mx=lo*lo;upper_witness[0].append(aa[1]);upper_witness[1].append(bb[0])
        else:
            mx=hi*hi;upper_witness[0].append(aa[0]);upper_witness[1].append(bb[1])
        squares.append((mn,mx))
    squared=sum(v[0]for v in squares),sum(v[1]for v in squares)
    return dict(delta=[[pair(v)for v in iv]for iv in delta],squares=[[pair(v)for v in iv]for iv in squares],
        squared=[pair(v)for v in squared],
        lower_witness=[[pair(v)for v in vv]for vv in lower_witness],
        upper_witness=[[pair(v)for v in vv]for vv in upper_witness])

def baseline():
    return dict(backend=MODEL,status="STOP_INPUT",reason=None,diagnostic=None,HOST_root_calls=0,
        HOST_box_extrema=0,HOST_word_decodes=0,HOST_exact_divisions=0,CPU_native_executed=False,
        native_root_calls=0,new_transport_graph_calls=0,new_predicate_calls=0,retained_suite_replays=0,
        source_uncertainty_cancelled=False,correlation_assumed=False,phase_certified=False,
        optical_reference_certified=False,physical_visibility_certified=False,scene_authenticated=False,GPU_used=False,
        comparison_scope="SAME_ORIGINAL_DECLARED_STRAIGHT_BOX_ONLY_NOT_OPTICAL_REFERENCE",
        promotion="STOP_PHYSICAL_PHASE_GPU",full_costs="UNKNOWN_NOT_ZERO",
        parent_native_costs="RETAINED_NONZERO_NOT_REPLAYED",root_bits=96)

def _audit(q,e,orig):
    out=baseline()
    try:
        require(type(q)is dict and type(q.get("record_id"))is str and q["record_id"]in e,"closed_record")
        expected=selector(q["record_id"],e,orig)
        require(q==expected and set(q)==set(expected)and all(type(v)is str for v in q.values()),"closed_selector")
        x,o=e[q["record_id"]],orig[q["record_id"]];r=x["result"]
        out.update(request_sha256=digest(q),parent_record_sha256=digest(x),
            original_record_sha256=digest(o),upstream_status=r["status"],upstream_reason=r["reason"])
        if r["status"]!="CPU64_DECLARED_SEGMENT_LENGTH_ONLY":
            out.update(status="STOP_UPSTREAM",reason="sealed_length_STOP_not_rescued");return out
        require(r["phase_certified"]is False and r["source_uncertainty_cancelled"]is False
            and r["upstream_status"]=="CPU64_DECLARED_BOX_DISJOINT","parent_scope")
        s=o["scene"];boxes=host.validate(s,o["scene_query"]);f=o["result"]["frame"];local=r["scene"]
        require(o["result"]["status"]=="CPU_NATIVE_PAIR64_RECENTER_ONLY"and f["scene"]==local,"original_frame_identity")
        require(r["scene_query"]==f["scene_query"]and digest(local)==f["snapshot_sha256"],"frame_query")
        text=f["output_packet_hex"];require(len(text)==480 and sha(bytes.fromhex(text))==x["request"]["output_packet_sha256"],"ALL240bytes")
        for i in range(15):
            n,j=host.POINTS[i//3],i%3;hi,lo=text[32*i:32*i+16],text[32*i+16:32*i+32]
            v=sealed.decode_pair(hi,lo);out["HOST_word_decodes"]+=2
            require(pair(v)==local["points"][n]["nominal"][j]
                and v==F(*s["points"][n]["nominal"][j])-F(*s["points"]["origin"]["nominal"][j]),"ALL15_original_common_constant")
            require(local["points"][n]["radius"][j]==s["points"][n]["radius"][j],"ALL15_original_radii")
        original=box_extrema(boxes);out["HOST_box_extrema"]+=1
        localboxes=host.validate(local,r["scene_query"]);shifted=box_extrema(localboxes);out["HOST_box_extrema"]+=1
        require(original["delta"]==shifted["delta"]and original["squares"]==shifted["squares"]and original["squared"]==shifted["squared"],"exact_common_frame_extrema")
        sl,sh=map(lambda v:F(*v),original["squared"])
        roots=[]
        for v in (sl,sh):
            a,b=lattice.root_bracket(v);out["HOST_root_calls"]+=1;roots.append([pair(a),pair(b)])
        lower,upper=F(*roots[0][0]),F(*roots[1][1])
        nl,nu=map(sealed.decode_word,r["trace"]["length"]);out["HOST_word_decodes"]+=2
        width=upper-lower;require(width>0,"zero_reference_width_ratio_UNRESOLVED")
        require(nl<=lower<=upper<=nu,"reference_inside_retained_native")
        margin=[lower-nl,nu-upper];ratio=(nu-nl)/width;out["HOST_exact_divisions"]=1
        out.update(status="HOST_SAME_ORIGINAL_BOX_REFERENCE_ONLY",reason="fixed96_extrema_and_native_width_comparison",
            diagnostic=dict(original_scene=s,original_query=o["scene_query"],original_snapshot_sha256=digest(s),
                local_scene_sha256=digest(local),extrema=original,shifted_extrema=shifted,
                roots=roots,reference_interval=[pair(lower),pair(upper)],reference_width=pair(width),
                native_interval=[pair(nl),pair(nu)],native_words=r["trace"]["length"],native_width=pair(nu-nl),
                outward_excess=[pair(v)for v in margin],native_width_over_reference=pair(ratio),
                comparison_units="scene_length",SOURCE="SOURCE0",DETECTOR="DETECTOR0"))
    except(ValueError,TypeError,KeyError,IndexError,OSError,ZeroDivisionError)as ex:
        out["reason"]=str(ex)
    return out

def audit(q):
    try:e,orig,_=retained()
    except(ValueError,TypeError,KeyError,OSError)as ex:
        out=baseline();out["reason"]="evidence_integrity:"+str(ex);return out
    return _audit(q,e,orig)
