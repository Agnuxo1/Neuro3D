"""Opt-in HOST proof: mathematical enclosure is not whole padded-interval containment.
No encoder, CPU RN graph, square-root evaluator, GPU or engine is called.
"""
from pathlib import Path
from fractions import Fraction as F
import json,hashlib,base64,zlib
ROOT=Path(__file__).resolve().parents[3]
MODEL="oblique-difference-math-enclosure-HOST-v1"
POLICY="TWO_DISTINCT_OBJECTS_SQUARE_MONOTONICITY_NOT_LEGACY_GATE_REPAIR"
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-NOMINAL-CHORD-DIFFERENCE-CPU-001-CODEX.json"
PSHA="24a385c85f3d071ea98ffcf333fb834d898dc2ea2dfab2c21155c9c00ddab1b2"
SOURCES=[
 ("coordinacion/respuestas/PRECISION-OBLIQUE-NOMINAL-CHORD-DIFFERENCE-HOST-001-CODEX.json","b01d94f36d904d724029dc0c0d33904ea449390468324efaa72a4e275293b424",156906),
 ("coordinacion/respuestas/PRECISION-OBLIQUE-SCENE-PAIR64-PAYLOAD-CPU-001-CODEX.json","ed228edd01ecced262362ff2ac8853cba434ce1e359cdfa2385017294f9dbbe9",242660),
 ("coordinacion/respuestas/PRECISION-OBLIQUE-PAIR64-LENGTH-REFERENCE-HOST-001-CODEX.json","2dc30d8b5762a179a4d40093ae5a47adcccce9507879c1a715725334e9f40eec",252843)]
ROLE="DECLARED_NOMINAL_STRAIGHT_CHORD_NOT_OPTICAL"
FLAGS=("phase_certified","wavelength_known","physical_reference_certified","scene_authenticated",
       "scene_engine_admitted","GPU_used","Bpy_used","source_uncertainty_cancelled","correlation_assumed")

def need(ok,msg):
    if not ok:raise ValueError(msg)

def sha(b):return hashlib.sha256(b).hexdigest()
def digest(x):return sha(json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False).encode())
def pair(q):return [q.numerator,q.denominator]

def rat(v):
    need(type(v)is list and len(v)==2 and all(type(n)is int for n in v)and v[1]>0,"typed_rational")
    need(max(abs(n).bit_length()for n in v)<=4096,"bounded_rational")
    q=F(*v);need(pair(q)==v,"canonical_rational");return q

def word(w):
    need(type(w)is str and len(w)==16 and all(c in "0123456789abcdef"for c in w),"canonical_word")
    u=int.from_bytes(bytes.fromhex(w),"little");e=(u>>52)&2047;m=u&((1<<52)-1)
    need(e!=2047 and (e!=0 or m==0),"normal_zero_word")
    if e==0:return F(0)
    s=-1 if u>>63 else 1;n=s*((1<<52)+m);k=e-1075
    return F(n*2**k)if k>=0 else F(n,2**(-k))

def capture(c):
    need(c["rc"]==0 and c["timed_out"]is False,"successful_capture")
    b=zlib.decompress(base64.b64decode(c["stdout_zlib_base64"],validate=True))
    need(len(b)==c["stdout_bytes"]and sha(b)==c["stdout_sha256"],"capture_seal")
    return json.loads(b)

def receipt(path,h,n):
    b=(ROOT/path).read_bytes();need(len(b)==n and sha(b)==h,"receipt_seal:"+path);return json.loads(b)

def records(r):
    d=capture(r["test_run"]);need(d.get("status","PASS")=="PASS","suite_status")
    a=d["evidence"]["records"];out={x["id"]:x for x in a}
    need(len(out)==len(a)==16,"closed16");return out

def retained():
    r=receipt(PARENT,PSHA,167737);pins=dict(r["code_doc_sha256"]);need(len(pins)==327,"parent_pins")
    for p,h in pins.items():need(sha((ROOT/p).read_bytes())==h,"dependency:"+p)
    need(capture(r["independent_pre"])["status"]=="PASS","parent_oracle")
    allrecords=[records(r)]
    for p,h,n in SOURCES:
        need(pins[p]==h,"source_pin");allrecords.append(records(receipt(p,h,n)))
    need(all(set(x)==set(allrecords[0])for x in allrecords),"same_records")
    pins[PARENT]=PSHA
    return {k:[x[k]for x in allrecords]for k in allrecords[0]},pins

def selector(k,b):
    q=b[0]["request"]
    return dict(model=MODEL,policy=POLICY,record_id=k,parent_receipt_sha256=PSHA,
        cpu_record_sha256=digest(b[0]),nominal_record_sha256=digest(b[1]),
        producer_record_sha256=digest(b[2]),reference_record_sha256=digest(b[3]),
        original_snapshot_sha256=q["original_snapshot_sha256"],original_query_sha256=q["original_query_sha256"],
        source="SOURCE0",detector="DETECTOR0",units="scene_length",reference_role=ROLE,
        proof_object="MATHEMATICAL_DIFFERENCE_AND_SEPARATE_WHOLE_HOST_INTERVAL",
        preserve_legacy_stop="REQUIRED")

def prove(smin,smax,snom,ell,u,rl,rh,hl,hu):
    """Exact rational sufficient conditions; no evaluation of any sqrt.
    Positive length endpoints make squaring monotone. Signed D is NOT squared.
    """
    need(0<=smin<=snom<=smax,"nominal_in_squared_box")
    need(0<=ell<=u and 0<=rl<=rh and 0<=hl<=hu,"nonnegative_length_roots")
    need(ell*ell<=smin and smax<=u*u,"native_squared_certificate")
    need(rl*rl<=snom<=rh*rh,"nominal_squared_certificate")
    need(hl*hl<=smin and smax<=hu*hu,"HOST_squared_certificate")
    a=[ell-rh,u-rl];h=[hl-rh,hu-rl]
    need(a[0]<=0<=a[1],"nominal_zero_inside_math_bound")
    return dict(mathematical_bound_proved=True,
        whole_HOST_interval_contained=(a[0]<=h[0]and h[1]<=a[1]),
        mathematical_outer_interval=[pair(x)for x in a],
        padded_HOST_difference_interval=[pair(x)for x in h],
        lower_gap=pair(a[0]-h[0]),upper_gap=pair(h[1]-a[1]),
        gap_identity="LOWER=ell-HLlower; UPPER=HLupper-u; SAME_EXPLICIT_REFERENCE_ENDPOINT_ONLY",
        theorem="ell-Rh <= sqrt(Smin)-sqrt(Snom) <= sqrt(Sactual)-sqrt(Snom) <= sqrt(Smax)-sqrt(Snom) <= u-Rl",
        quantification="ALL_POINTS_OF_DECLARED_INDEPENDENT_ORIGINAL_SOURCE_DETECTOR_BOX",
        source_uncertainty_cancelled=False,correlation_assumed=False)

def audit(b):
    cpu,nom,prod,ref=[x["result"]for x in b]
    need(cpu["status"]=="STOP_INPUT"and cpu["reason"]=="HOST_reference_inside_native_outer_interval","legacy_stop_required")
    need(all(cpu[f]is False for f in FLAGS)and cpu["phase_error_bound"]is None,"legacy_scope")
    nd=nom["diagnostic"];cd=cpu["diagnostic"];rd=ref["diagnostic"];env=prod["envelope"]
    need(cd["native_difference_outer_interval"]is None,"legacy_outer_remains_null")
    scene=rd["original_scene"];query=rd["original_query"]
    snap=digest(scene);qsha=digest(query)
    need(scene["label"]=="NEW_CPU_SYNTHETIC_NOT_SEALED_PHYSICAL"and scene["units"]=="scene_length","declared_scene")
    need(scene["SOURCE"]==dict(id="SOURCE0",point="origin")and scene["DETECTOR"]==dict(id="DETECTOR0",point="detector"),"source_detector")
    need(query["source"]=="SOURCE0"and query["detector"]=="DETECTOR0"and query["snapshot_sha256"]==snap,"query_binding")
    for x in (nd,cd,env):
        need(x["original_snapshot_sha256"]==snap and x["original_query_sha256"]==qsha,"same_original")
        need(x["source"]=="SOURCE0"and x["detector"]=="DETECTOR0"and x["units"]=="scene_length","same_role_units")
    need(nd["reference_role"]==cd["reference_role"]==ROLE,"reference_role")
    radii={k:v["radius"]for k,v in scene["points"].items()}
    need(set(radii)=={"A","B","C","origin","detector"}and all(len(v)==3 for v in radii.values()),"all15_radii")
    need(nd["ALL15_original_radii"]==cd["ALL15_original_radii"]==radii,"radii_unchanged")
    need(all(rat(r)>=0 for a in radii.values()for r in a),"radii_nonnegative")
    src=scene["points"]["origin"];det=scene["points"]["detector"]
    delta=[rat(det["nominal"][j])-rat(src["nominal"][j])for j in range(3)]
    extrema=rd["extrema"];smin=F(0);smax=F(0)
    for j,d in enumerate(delta):
        r=rat(src["radius"][j])+rat(det["radius"][j]);a=d-r;c=d+r
        low=F(0)if a<=0<=c else min(a*a,c*c);high=max(a*a,c*c)
        need(extrema["delta"][j]==[pair(a),pair(c)]and extrema["squares"][j]==[pair(low),pair(high)],"original_axis_square")
        smin+=low;smax+=high
    snom=sum((d*d for d in delta),F(0))
    need(nd["nominal_delta"]==[pair(d)for d in delta]and rat(nd["nominal_squared_length"])==snom,"nominal_square")
    need(extrema["squared"]==nd["retained_box_squared_interval"]==[pair(smin),pair(smax)],"same_squared_box")
    rl,rh=map(rat,nd["reference_root96"]);hl,hu=map(rat,nd["retained_box_length_interval"])
    need(rh-rl<=F(1,2**96)and (rl*2**96).denominator==(rh*2**96).denominator==1,"sealed96_grid")
    need(rd["reference_interval"]==nd["retained_box_length_interval"],"same_HOST_lengths")
    for enc,r in zip(cd["reference_encoding"],(rl,rh)):
        need(enc["status"]=="HOST_EXACT_REFERENCE_PAIR64_ONLY"and len(enc["words"])==2,"sealed_reference_encoding")
        need(sum((word(w)for w in enc["words"]),F(0))==r==rat(enc["rational"])==rat(enc["HOST_exact_pair_sum"]),"reference_word_sum")
        need(rat(enc["HOST_signed_encoding_residual"])==rat(enc["HOST_encoding_error_bound"])==0,"encoding_zero_preserved")
    need(len(cd["reference_encoding"])==len(cd["subtractions"])==len(env["certificates"])==2,"two_endpoints")
    payload=env["payload_hex"]
    need(len(payload)==64 and sha(payload.encode())==env["payload_hex_ASCII_sha256"],"length_payload_seal")
    length_words=[payload[i:i+16]for i in range(0,64,16)]
    lengths=[word(length_words[j])+word(length_words[j+1])for j in (0,2)]
    bounds=[];candidates=[];totals=[]
    for j,sub in enumerate(cd["subtractions"]):
        cert=env["certificates"][j];co=sub["consumer"];L=lengths[j];R=(rh,rl)[j];B=rat(cert["retained_length_error_bound"])
        need(B>=0 and sub["retained_length_certificate"]==cert,"retained_bound")
        need(cert["bound"]==sub["bound"]==("lower","upper")[j]and sub["reference_endpoint"]==("upper","lower")[j],"endpoint_roles")
        need(rat(cert["exact_squared"])==(smin,smax)[j]and rat(cert["retained_exact_pair_sum"])==L,"length_sum_squared")
        need(cert["retained_HOST_enclosure"]==[pair(L-B),pair(L+B)],"length_enclosure")
        words=co["candidate_pair_words"];need(len(words)==2,"candidate_pair")
        C=sum((word(w)for w in words),F(0));T=rat(co["HOST_total_difference_error_bound"])
        need(co["status"]=="CPU64_EXACT_PAIR_DIFFERENCE_ONLY"and co["RN_nodes_executed"]==26,"sealed_CPU_graph")
        need(co["input_payload_hex"]=="".join(cd["reference_encoding"][1-j]["words"]+length_words[2*j:2*j+2]),"sealed_subtraction_inputs")
        need(C==L-R==rat(co["native_pair_difference"])==rat(co["input_difference"]),"sealed_difference")
        need(rat(co["HOST_signed_residual"])==rat(co["HOST_arithmetic_error_bound"])==0 and T==B==rat(co["inherited_bound"]),"error_bound_unchanged")
        need(co["HOST_difference_interval"]==[pair(C-T),pair(C+T)],"candidate_bounds")
        bounds.append(B);candidates.append(C);totals.append(T)
    ell=lengths[0]-bounds[0];u=lengths[1]+bounds[1]
    pr=prove(smin,smax,snom,ell,u,rl,rh,hl,hu)
    need(pr["mathematical_outer_interval"]==[pair(candidates[0]-totals[0]),pair(candidates[1]+totals[1])],"math_equals_legacy_candidate")
    need(pr["padded_HOST_difference_interval"]==nd["signed_difference_interval"]==cd["HOST_reference_difference_interval"],"whole_HOST_target")
    need(pr["whole_HOST_interval_contained"]is False and rat(pr["lower_gap"])>0 and rat(pr["upper_gap"])>0,"legacy_failure_preserved")
    pr.update(original_snapshot_sha256=snap,original_query_sha256=qsha,ALL15_original_radii=radii,
        squared_box=[pair(smin),pair(smax)],nominal_squared=pair(snom),
        certified_lengths=[pair(ell),pair(u)],reference96=[pair(rl),pair(rh)],
        sealed_candidate_words=[x["consumer"]["candidate_pair_words"]for x in cd["subtractions"]],
        legacy_status=cpu["status"],legacy_reason=cpu["reason"],legacy_outer_interval=None,
        new_integer_word_decodes=12,new_root_evaluations=0,new_RN=0,new_encoder_calls=0,
        old_numeric_modules_imported=0,retained_numeric_replays=0)
    return pr

def evaluate(k,request,b):
    out=dict(model=MODEL,status="STOP_INPUT",legacy_stop_preserved=True,mathematical_bound_proved=False,
        scene_engine_admitted=False,phase_certified=False,wavelength_known=False,physical_reference_certified=False,
        scene_authenticated=False,GPU_used=False,Bpy_used=False,source_uncertainty_cancelled=False,
        correlation_assumed=False,phase_error_bound=None,new_root_evaluations=0,new_RN=0,new_encoder_calls=0,
        integer_word_decodes=0,full_costs="UNKNOWN_NOT_ZERO",scope="HOST_CONDITIONAL_MATH_PROOF_NOT_ENGINE")
    try:
        expected=selector(k,b)
        need(type(request)is dict and set(request)==set(expected),"closed_selector")
        need(all(type(request[x])is str and request[x]==expected[x]for x in expected),"selector_binding")
        if b[0]["result"]["status"]=="STOP_UPSTREAM":
            out.update(status="STOP_UPSTREAM",reason="retained_CPU_upstream_stop",upstream_status=b[0]["result"]["status"])
            return out
        # A rejected certificate may already have decoded words: unknown, NEVER zero.
        out["integer_word_decodes"]=None
        pr=audit(b);out.update(status="LEGACY_ENCLOSURE_STOP_PRESERVED",mathematical_bound_proved=True,
            reason="NEW_CONDITIONAL_MATH_THEOREM_NOT_OLD_GATE_PASS",diagnostic=pr,integer_word_decodes=12)
    except(ValueError,KeyError,TypeError,IndexError,OverflowError)as ex:out["reason"]=str(ex)
    return out

def run(k,request):
    try:
        bundles,pins=retained();need(k in bundles,"unknown_record")
        return evaluate(k,request,bundles[k])
    except(OSError,ValueError,KeyError,TypeError)as ex:
        return dict(status="STOP_DEPENDENCY",reason=str(ex),new_RN=0,new_root_evaluations=0,integer_word_decodes=0,
            phase_certified=False,scene_engine_admitted=False,legacy_stop_preserved=True)
