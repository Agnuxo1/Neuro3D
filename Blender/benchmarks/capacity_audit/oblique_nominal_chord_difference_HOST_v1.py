"""Opt-in HOST signed straight-box length minus explicit nominal chord reference."""
from pathlib import Path
from fractions import Fraction as F
from math import isqrt
import json,hashlib,base64,zlib
ROOT=Path(__file__).resolve().parents[3]
MODEL="oblique-nominal-chord-difference-HOST-v1"
POLICY="SAME_ORIGINAL_STRAIGHT_BOX_MINUS_NOMINAL_CHORD_FIXED96_NO_PHYSICAL_PHASE"
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-WIDTH-PHASE-SEMANTIC-GATE-HOST-001-CODEX.json"
PSHA="394e2198aab8a0893cee4eaa928d599d965ae76abee5ab91fb7ca6454c44196d"
WIDTH="coordinacion/respuestas/PRECISION-OBLIQUE-PAIR64-WIDTH-CONSUMER-CPU-001-CODEX.json"
WSHA="b9f8380cba629c5e4a6d5c120df89f087f2e5a717293d26500f97b2f7329c2ae"
REFERENCE="coordinacion/respuestas/PRECISION-OBLIQUE-PAIR64-LENGTH-REFERENCE-HOST-001-CODEX.json"
RSHA="2dc30d8b5762a179a4d40093ae5a47adcccce9507879c1a715725334e9f40eec"
ORIGINAL="coordinacion/respuestas/PRECISION-OBLIQUE-SCENE-PAIR64-CPU-001-CODEX.json"
OSHA="813fd728006a90adb40f99d1eb49aa3523f8f63bf61edca7775e332dc57106ea"
BITS=96

def need(ok,msg):
    if not ok:raise ValueError(msg)

def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode())
def pair(x):return [x.numerator,x.denominator]

def rat(p):
    need(type(p)is list and len(p)==2 and all(type(v)is int for v in p)and p[1]>0,"typed_rational")
    need(max(abs(v).bit_length()for v in p)<=4096,"bounded_rational")
    x=F(*p);need(pair(x)==p,"canonical_rational");return x

def capture(c):
    need(c["rc"]==0 and not c["timed_out"],"successful_capture")
    b=zlib.decompress(base64.b64decode(c["stdout_zlib_base64"],validate=True))
    need(len(b)==c["stdout_bytes"]and sha(b)==c["stdout_sha256"],"capture_seal")
    return json.loads(b)

def receipt(path,h,n):
    b=(ROOT/path).read_bytes();need(sha(b)==h and len(b)==n,"receipt_seal:"+path)
    return json.loads(b)

def retained():
    r=receipt(PARENT,PSHA,164509);pins=dict(r["code_doc_sha256"]);need(len(pins)==319,"parent_pins")
    for p,h in pins.items():need(sha((ROOT/p).read_bytes())==h,"dependency:"+p)
    need(capture(r["independent_pre"])["status"]=="PASS","parent_oracle")
    for p,h in ((WIDTH,WSHA),(REFERENCE,RSHA),(ORIGINAL,OSHA)):
        need(pins[p]==h,"retained_dependency")
    w=receipt(WIDTH,WSHA,163556);rr=receipt(REFERENCE,RSHA,252843);o=receipt(ORIGINAL,OSHA,84149)
    wc=capture(w["test_run"]);rc=capture(rr["test_run"]);oc=capture(o["test_run"])
    need(wc["status"]=="PASS"and set(rc)==set(oc)=={"evidence","summary"},"retained_capture_schemas")
    width={x["id"]:x for x in wc["evidence"]["records"]}
    ref={x["id"]:x for x in rc["evidence"]["records"]}
    oe=oc["evidence"];orig={"scene:"+x["name"]:x for x in oe["records"]}
    orig["native_inexact"]=oe["inexact"];orig.update({"input:"+x["name"]:x for x in oe["invalid"]})
    need(set(width)==set(ref)==set(orig)and len(width)==16,"closed_records")
    pins[PARENT]=PSHA
    return width,ref,orig,pins

def selector(k,width,ref,orig):
    o=orig[k];query=o.get("scene_query",o["request"].get("scene_query"))
    return dict(model=MODEL,policy=POLICY,record_id=k,parent_receipt_sha256=PSHA,
        width_record_sha256=digest(width[k]),reference_record_sha256=digest(ref[k]),
        original_record_sha256=digest(o),original_snapshot_sha256=digest(o["scene"]),
        original_query_sha256=digest(query),source="SOURCE0",detector="DETECTOR0",
        units="scene_length",reference_role="DECLARED_NOMINAL_STRAIGHT_CHORD_NOT_OPTICAL")

def root96(s):
    need(type(s)is F and s>=0,"nonnegative_squared_chord")
    k=isqrt((s.numerator<<(2*BITS))//s.denominator)
    lo=F(k,1<<BITS);hi=lo if lo*lo==s else F(k+1,1<<BITS)
    return [lo,hi]

def baseline():
    return dict(model=MODEL,status="STOP_INPUT",reason=None,diagnostic=None,
        new_HOST_nominal_products=0,new_HOST_nominal_sum_adds=0,new_HOST_nominal_root_calls=0,
        new_HOST_difference_subtractions=0,new_native_RN=0,new_native_sqrt=0,
        retained_numeric_replays=0,source_uncertainty_cancelled=False,correlation_assumed=False,
        wavelength_known=False,phase_certified=False,physical_reference_certified=False,
        scene_authenticated=False,scene_engine_admitted=False,GPU_used=False,Bpy_used=False,
        native_difference=None,phase_error_bound=None,full_costs="UNKNOWN_NOT_ZERO",
        promotion="STOP_PHASE_PHYSICAL_NATIVE_GPU_AND_FULL_COSTS",
        scope="HOST_STRAIGHT_BOX_LENGTH_MINUS_NEW_DECLARED_NOMINAL_CHORD_ONLY")

def _audit(q,width,ref,orig):
    out=baseline()
    try:
        need(type(q)is dict and type(q.get("record_id"))is str and q["record_id"]in width,"closed_record")
        k=q["record_id"];need(q==selector(k,width,ref,orig)and all(type(v)is str for v in q.values()),"closed_selector")
        w=width[k];r=ref[k];o=orig[k];out["request_sha256"]=digest(q)
        out["upstream_status"]=w["result"]["status"]
        if w["result"]["status"]!="CPU64_SCENE_PAIR_WIDTH_HOST_BOUND_ONLY":
            out.update(status="STOP_UPSTREAM",reason="sealed_STOP_not_rescued");return out
        need(r["result"]["status"]=="HOST_SAME_ORIGINAL_BOX_REFERENCE_ONLY","original_length_reference_status")
        z=r["result"]["diagnostic"];s=o["scene"]
        need(z["original_scene"]==s and z["original_query"]==o["scene_query"],"same_original")
        need(z["original_snapshot_sha256"]==q["original_snapshot_sha256"]
            and w["request"]["original_snapshot_sha256"]==q["original_snapshot_sha256"]
            and w["request"]["original_query_sha256"]==q["original_query_sha256"],"same_snapshot_query")
        need(z["SOURCE"]==q["source"]and z["DETECTOR"]==q["detector"]
            and z["comparison_units"]==q["units"],"same_source_detector_units")
        points=s["points"];need(len(points)==5,"ALL5points")
        radii={n:[pair(rat(v))for v in p["radius"]]for n,p in points.items()}
        need(all(len(v)==3 and all(rat(x)>=0 for x in v)for v in radii.values()),"ALL15_radii")
        a,b=points["origin"]["nominal"],points["detector"]["nominal"]
        need(len(a)==len(b)==3,"nominal_vector3")
        delta=[rat(y)-rat(x)for x,y in zip(a,b)]
        terms=[v*v for v in delta];S=terms[0]+terms[1]+terms[2]
        out.update(new_HOST_nominal_products=3,new_HOST_nominal_sum_adds=2)
        limits=[rat(v)for v in z["extrema"]["squared"]];need(0<=limits[0]<=S<=limits[1],"nominal_inside_original_box")
        R=root96(S);out["new_HOST_nominal_root_calls"]=1
        L=[rat(v)for v in z["reference_interval"]];need(0<=L[0]<=R[0]<=R[1]<=L[1],"same_declared_length_enclosure")
        D=[L[0]-R[1],L[1]-R[0]];out["new_HOST_difference_subtractions"]=2
        need(D[0]<=0<=D[1],"nominal_zero_covered")
        out.update(status="HOST_DECLARED_NOMINAL_CHORD_DIFFERENCE_ONLY",
            reason="signed_difference_not_width_or_phase",
            diagnostic=dict(original_snapshot_sha256=q["original_snapshot_sha256"],
                original_query_sha256=q["original_query_sha256"],source="SOURCE0",detector="DETECTOR0",
                units="scene_length",reference_role=q["reference_role"],ALL15_original_radii=radii,
                nominal_delta=[pair(v)for v in delta],nominal_squared_terms=[pair(v)for v in terms],
                nominal_squared_length=pair(S),reference_root96=[pair(v)for v in R],
                retained_box_squared_interval=z["extrema"]["squared"],retained_box_length_interval=z["reference_interval"],
                signed_difference_interval=[pair(v)for v in D],zero_covered=True,
                reference_rounding_width=pair(R[1]-R[0]),
                uncertainty_policy="FULL_ORIGINAL_BOX_NO_SOURCE_CANCELLATION",
                width_operand_used=False,physical_reference_certified=False,
                reference_definition="sqrt(sum((detector_nominal-source_nominal)^2))"))
    except(ValueError,TypeError,KeyError,IndexError,OSError,ZeroDivisionError)as ex:out["reason"]=str(ex)
    return out

def audit(q):
    try:w,r,o,_=retained();return _audit(q,w,r,o)
    except(ValueError,TypeError,KeyError,OSError)as ex:
        out=baseline();out["reason"]="evidence_integrity:"+str(ex);return out
