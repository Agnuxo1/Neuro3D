"""Opt-in declared CPU reference turns -> two native radian words. No wrapping/field."""
from pathlib import Path
from fractions import Fraction as F
import json,struct
import coplanar_clearance_CPU_v1 as c
import oblique_total_phase_pair64_CPU_v1 as arithmetic
ROOT=Path(__file__).resolve().parents[3]
MODEL="precision-position-phase-reference-angle-native-CPU-v1"
PARENT="coordinacion/respuestas/PRECISION-POSITION-PHASE-REFERENCE-NATIVE-CPU-001-CODEX.json"
PSHA="317d58a77be135250954bef9ad4cf9f8669cb9604a968c3286d3f8029a42511d"
HOST="coordinacion/respuestas/PRECISION-POSITION-PHASE-REFERENCE-OVERLAY-HOST-001-CODEX.json"
HSHA="7c52f61504e126628ff54d76686ba6585abe9d0cf1a5ff8bf99a87d6fe686e14"
REP="CPU_RN64_PAIR_DECLARED_REFERENCE_ANGLE_NOT_PHYSICAL_TOTAL"
INTENT="ALL16_BYTES_TURNS_TO_RAD_CONSTANT_AND_ALL_NATIVE_ERRORS_CHARGED"
TAU_WORD="182d4454fb211940"
CAP=F(1,10000)
need,sha,digest,pair=c.need,c.sha,c.digest,c.pair

def certificate():
    # Integral geometric-series remainder bounds atan(1/q). 20 terms = lower.
    intervals=[]
    for q in (5,239):
        lower=sum((F((-1)**k,(2*k+1)*q**(2*k+1)) for k in range(20)),F(0))
        upper=lower+F(1,41*q**41)
        intervals.append((lower,upper))
    a,b=intervals
    lo=2*(16*a[0]-4*b[1]);hi=2*(16*a[1]-4*b[0])
    # (5+i)^4=476+480i; multiply by (239-i) gives equal positive parts.
    real=476*239+480;imag=480*239-476
    need(real==imag==114244 and 0<4*a[0]-b[1]<4*a[1]-b[0]<F(4,5),"Machin_identity_branch")
    need(0<lo<hi<8 and hi-lo<F(1,10**27),"tau_enclosure")
    return dict(method="ATAN_INTEGRAL_ALTERNATING_20_MACHIN_EXACT_COMPLEX_BRANCH",
        terms_per_atan=20,denominators=[5,239],atan_intervals=[[pair(x),pair(y)] for x,y in intervals],
        complex_power4=[476,480],complex_product=[real,imag],tau_interval_rad_per_turn=[pair(lo),pair(hi)],
        HOST_fraction_terms=40,HOST_integer_powers=42,physical_calibration=False)
CERT=certificate()
CERT_SHA=digest(CERT)

def retained():
    raw=(ROOT/PARENT).read_bytes();need(sha(raw)==PSHA and len(raw)==333604,"parent_identity");r=json.loads(raw)
    for p,h in r["code_doc_sha256"].items():need(sha((ROOT/p).read_bytes())==h,"ancestral_pin:"+p)
    v=c.capture(r["independent_pre"]);need(v["status"]=="PASS" and v["pins"]==220,"parent_oracle")
    td=c.capture(r["test_run"]);need(td["status"]=="PASS","parent_capture")
    runs=td["data"]["runs"];e={x["id"]:x for x in runs}
    need(len(e)==len(runs)==482 and sum(x["result"]["reference_contrast_conditional"]is True for x in runs)==39,"closed_parent_grid")
    hraw=(ROOT/HOST).read_bytes();need(sha(hraw)==HSHA and len(hraw)==196856,"HOST_identity")
    hosts={x["id"]:x for x in c.capture(json.loads(hraw)["test_run"])["data"]["runs"]}
    pins=dict(r["code_doc_sha256"]);pins[PARENT]=PSHA
    return e,hosts,pins

def selector(record,e):
    x=e[record]
    return dict(record_id=record,parent_receipt_sha256=PSHA,parent_record_sha256=digest(x),
        parent_request_sha256=digest(x["request"]),source_context_sha256=x["request"]["source_context_sha256"],
        original_geometry_sha256=x["request"]["original_geometry_sha256"],overlay_sha256=x["request"]["overlay_sha256"],
        tau_word_LE=TAU_WORD,tau_certificate_sha256=CERT_SHA,representation=REP,intent=INTENT)

def baseline():
    out=c.baseline()
    out.update(model=MODEL,representation=REP,CPU_native_executed=False,root_calls=0,RN64_conversions=0,
        decoded_phase_words=0,decoded_constant_words=0,trace=[],trace_unit="rad",angle_conditional=False,
        total_phase_certified=False,material_authenticated=False,wavelength_authenticated=False,
        optical_reference_certified=False,correlation_assumed=False,shared_phase_cancellation_assumed=False,
        periodic_wrapping_used=False,native_scalar_phase_output=False,declared_uncertainty_only=True,
        parent_branches_unchanged=True,pair_words_LE=None,error_rad_upper=None,tau_certificate_sha256=CERT_SHA)
    return out

def normal(word):
    need(type(word)is str and len(word)==16,"binary64_word")
    b=int.from_bytes(bytes.fromhex(word),"little");exp=(b>>52)&2047
    need(exp!=2047 and(exp!=0 or b&((1<<63)-1)==0),"normal_zero_only")
    need(abs(F.from_float(struct.unpack("<d",bytes.fromhex(word))[0]))<=10**6,"unchanged_numeric_domain_1e6")

def words(v):return [struct.pack("<d",x).hex()for x in v]
def exact(v):return sum((F.from_float(x)for x in v),F(0))

def compute_pair(raw,budget_turns,out):
    """Internal numerical helper; caller binds sealed scene record before entering."""
    need(type(raw)is bytes and len(raw)==16,"typed_16_byte_frame")
    need(type(budget_turns)is F and 0<=budget_turns<=CAP/8,"fixed_inherited_budget")
    iw=[raw[:8].hex(),raw[8:].hex()]
    for w in iw+[TAU_WORD]:normal(w)
    a,b=struct.unpack("<dd",raw);out["decoded_phase_words"]=2
    tau=struct.unpack("<d",bytes.fromhex(TAU_WORD))[0];out["decoded_constant_words"]=1
    tf=F.from_float(tau);lo,hi=map(lambda v:F(*v),CERT["tau_interval_rad_per_turn"])
    ce=max(abs(tf-lo),abs(tf-hi));products=[]
    for i,v in enumerate((a,b)):
        y=v*tau;err=abs(F.from_float(y)-F.from_float(v)*tf)
        out["trace"].append(dict(name="product"+str(i),op="*",a=words((v,))[0],b=TAU_WORD,
            y=words((y,))[0],error_rad=pair(err)))
        for w in(out["trace"][-1]["a"],TAU_WORD,out["trace"][-1]["y"]):normal(w)
        products.append(y)
    try:
        value=arithmetic.sum2(products[0],products[1],"angle",out["trace"])
    finally:
        # Even failed partial graphs keep explicit radian units; frozen helper stays intact.
        for t in out["trace"][2:]:
            t["error_rad"]=t.pop("error_cycles")
    for t in out["trace"][2:]:
        for w in(t["a"],t["b"],t["y"]):normal(w)
    normerr=abs(exact(value)-exact(products))
    charges=dict(inherited_rad_upper=pair(8*budget_turns),constant_rad_upper=pair(ce*abs(exact((a,b)))),
        product_high_error_rad=out["trace"][0]["error_rad"],product_low_error_rad=out["trace"][1]["error_rad"],
        normalization_error_rad=pair(normerr))
    bound=sum((F(*x)for x in charges.values()),F(0))
    return dict(input_words_LE=iw,input_exact_turns_HOST=pair(exact((a,b))),output_words_LE=words(value),
        output_exact_rad_HOST=pair(exact(value)),tau_word_LE=TAU_WORD,tau_error_rad_per_turn=pair(ce),
        tau_certificate_sha256=CERT_SHA,charges_rad=charges,error_rad_upper=pair(bound),cap_rad=pair(CAP))

def _audit(model,q,raw,e,hosts):
    out=baseline()
    try:
        need(type(model)is str and model==MODEL,"explicit_model")
        need(type(q)is dict and type(q.get("record_id"))is str and q["record_id"]in e,"closed_record")
        want=selector(q["record_id"],e)
        need(q==want and set(q)==set(want)and all(type(v)is str for v in q.values()),"closed_selector_identity")
        x=e[q["record_id"]];r=x["result"]
        need(r["status"]=="CPU_NATIVE_PAIR_DECLARED_REFERENCE_CONTRAST_ONLY"and r["reference_contrast_conditional"]is True,"parent_STOP_not_rescued")
        d=r["rows"][0];h=hosts[x["record_id"]];hd=h["result"]["rows"][0];packet=h["packet"]
        need(digest(h)==x["request"]["parent_record_sha256"] and digest(packet)==q["overlay_sha256"]
            and digest(packet["source_context"])==q["source_context_sha256"]
            and packet["original_geometry_sha256"]==q["original_geometry_sha256"],"same_SOURCE_ORIGINAL_reference_overlay")
        need(packet["frame"]=="DECLARED_COMMON_TURNS_FRAME_NOT_CALIBRATED"
            and packet["authentication"]=="DECLARED_NOT_PHYSICALLY_AUTHENTICATED"
            and type(packet["reference_point"])is int and packet["reference_point"]==1
            and type(packet["target_point"])is int and packet["target_point"]==3
            and packet["cap_rad"]==[1,10000],"declared_scope_only")
        expected=bytes.fromhex("".join(r["pair_words_LE"]))
        need(type(raw)is bytes and len(raw)==16 and raw==expected,"ALL16bytes_before_decode")
        budget=sum((F(*d[k])for k in("parent_budget_turns","new_encoding_error_turns","new_addition_error_turns")),F(0))
        need(F(*d["error_rad_upper"])==8*budget<=CAP,"fixed_parent_budget")
        diag=compute_pair(raw,budget,out);out["diagnostics"]=[diag]
        lo,hi=map(lambda v:F(*v),hd["interval_contrast_turns"])
        tl,th=map(lambda v:F(*v),CERT["tau_interval_rad_per_turn"])
        corners=[t*p for t in(tl,th)for p in(lo,hi)];val=F(*diag["output_exact_rad_HOST"])
        direct=max(abs(val-p)for p in corners)
        diag.update(parent_record_sha256=digest(x),input_frame_sha256=sha(raw),reference_point=1,target_point=3,
            interval_angle_rad_HOST=[pair(min(corners)),pair(max(corners))],direct_error_rad_upper=pair(direct),
            scope="CPU_SYNTHETIC_DECLARED_REFERENCE_ANGLE_NOT_PHYSICAL_TOTAL")
        need(direct<=F(*diag["error_rad_upper"]),"direct_bound_dominated")
        need(len(out["trace"])==8,"closed_eight_native_nodes")
        need(F(*diag["error_rad_upper"])<=CAP,"angle_budget_exhausted")
        out.update(status="CPU_NATIVE_PAIR_DECLARED_REFERENCE_ANGLE_ONLY",rows=[diag],angle_conditional=True,
            pair_words_LE=diag["output_words_LE"],error_rad_upper=diag["error_rad_upper"])
    except(ValueError,TypeError,KeyError,IndexError,OverflowError)as ex:out["reason"]=str(ex)
    finally:
        out["RN64_operations"]=len(out["trace"]);out["CPU_native_executed"]=out["RN64_operations"]>0
    return out

def audit(model,request,raw_frame):
    try:e,h,_=retained()
    except(ValueError,TypeError,KeyError,OSError)as ex:
        r=baseline();r["reason"]="evidence_integrity:"+str(ex);return r
    return _audit(model,request,raw_frame,e,h)
