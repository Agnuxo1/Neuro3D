"""Independent integer/rational oracle. Never import old numerical producers."""
from pathlib import Path
from fractions import Fraction as Q
import sys,json,copy
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"benchmarks"/"capacity_audit"))
import oblique_difference_math_enclosure_HOST_v1 as m

def frac(x):return Q(x[0],x[1])

def bits(w):
    # Independent big-endian hex rearrangement and scaling of the significand.
    u=int("".join(reversed([w[j:j+2]for j in range(0,16,2)])),16)
    sign=1-2*(u//2**63);expo=(u//2**52)%2048;mant=u%2**52
    assert expo!=2047 and (expo or mant==0)
    if not expo:return Q(0)
    return sign*Q(2**52+mant,2**52)*Q(2)**(expo-1023)

def independent(b,result):
    assert result["status"]=="LEGACY_ENCLOSURE_STOP_PRESERVED"
    c,n,p,r=[x["result"]for x in b];d=result["diagnostic"];nd=n["diagnostic"]
    assert c["status"]=="STOP_INPUT"and c["reason"]=="HOST_reference_inside_native_outer_interval"
    scene=r["diagnostic"]["original_scene"];points=scene["points"]
    ds=[frac(points["detector"]["nominal"][j])-frac(points["origin"]["nominal"][j])for j in range(3)]
    radius=[frac(points["origin"]["radius"][j])+frac(points["detector"]["radius"][j])for j in range(3)]
    # |delta| interval gives identical continuous squared-extrema by a different formula.
    low=sum((max(Q(0),abs(ds[j])-radius[j])**2 for j in range(3)),Q(0))
    high=sum(((abs(ds[j])+radius[j])**2 for j in range(3)),Q(0))
    nominal=sum((x**2 for x in ds),Q(0));assert [frac(x)for x in d["squared_box"]]==[low,high]
    assert frac(d["nominal_squared"])==nominal
    payload=p["envelope"]["payload_hex"];words=[payload[j:j+16]for j in range(0,64,16)]
    L=[bits(words[j])+bits(words[j+1])for j in (0,2)]
    B=[frac(x["retained_length_error_bound"])for x in p["envelope"]["certificates"]]
    ell,u=L[0]-B[0],L[1]+B[1]
    rl,rh=[frac(x)for x in nd["reference_root96"]]
    hl,hu=[frac(x)for x in nd["retained_box_length_interval"]]
    assert 0<=ell and ell**2<=low<=nominal<=high<=u**2
    assert 0<=rl<=rh and rl**2<=nominal<=rh**2
    assert hl**2<=low and high<=hu**2
    A=[ell-rh,u-rl];H=[hl-rh,hu-rl]
    assert [frac(x)for x in d["mathematical_outer_interval"]]==A
    assert [frac(x)for x in d["padded_HOST_difference_interval"]]==H
    assert frac(d["lower_gap"])==A[0]-H[0]==ell-hl>0
    assert frac(d["upper_gap"])==H[1]-A[1]==hu-u>0
    assert not(A[0]<=H[0]and H[1]<=A[1])
    for j,sub in enumerate(c["diagnostic"]["subtractions"]):
        co=sub["consumer"];cand=sum((bits(w)for w in co["candidate_pair_words"]),Q(0))
        assert cand==L[j]-(rh,rl)[j]and frac(co["HOST_total_difference_error_bound"])==B[j]
        assert [bits(w)for w in co["candidate_pair_words"]]==[m.word(w)for w in co["candidate_pair_words"]]
    assert result["mathematical_bound_proved"]is True and d["whole_HOST_interval_contained"]is False
    assert d["ALL15_original_radii"]=={k:v["radius"]for k,v in points.items()}
    assert all(result[f]is False for f in m.FLAGS)
    assert result["phase_error_bound"]is None and result["integer_word_decodes"]==12
    assert d["legacy_outer_interval"]is None and result["legacy_stop_preserved"]is True
    return dict(id=b[0]["id"],status="PASS_CONDITIONAL_MATH_PROOF_LEGACY_STOP",
        lower_gap=d["lower_gap"],upper_gap=d["upper_gap"],old_status=c["status"])

def suite():
    bundles,pins=m.retained();records=[];oracle=[];good=[]
    for k,b in bundles.items():
        req=m.selector(k,b);res=m.evaluate(k,req,b);records.append(dict(id=k,request=req,result=res))
        if "diagnostic"in res:
            oracle.append(independent(b,res));good.append(k)
        else:assert res["status"]=="STOP_UPSTREAM"
    assert len(good)==2 and len(records)==16
    k=good[0];b=bundles[k];req=m.selector(k,b);selectors=[]
    for key,value in [("model","other"),("policy","old_gate_repair"),("source","SOURCE1"),
        ("units","radians"),("original_snapshot_sha256","0"*64),
        ("reference_role","OPTICAL"),("preserve_legacy_stop","OPTIONAL"),("lambda","1")]:
        bad=dict(req);bad[key]=value;out=m.evaluate(k,bad,b)
        assert out["status"]=="STOP_INPUT"and out["integer_word_decodes"]==0
        selectors.append(dict(field=key,result=out))
    mutations=[]
    def edit(name,fn):
        altered=copy.deepcopy(b);fn(altered);out=m.evaluate(k,m.selector(k,altered),altered)
        assert out["status"]=="STOP_INPUT"and out["mathematical_bound_proved"]is False,name
        mutations.append(dict(name=name,result=out,scope="IN_MEMORY_CAPTURE_FORGERY_NO_FILE_CHANGE"))
    edit("legacy_status",lambda x:x[0]["result"].update(status="PASS"))
    edit("legacy_phase",lambda x:x[0]["result"].update(phase_certified=True))
    edit("legacy_outer",lambda x:x[0]["result"]["diagnostic"].update(native_difference_outer_interval=[[0,1],[1,1]]))
    edit("nominal_square",lambda x:x[1]["result"]["diagnostic"].update(nominal_squared_length=[1,1]))
    edit("source_radius",lambda x:x[3]["result"]["diagnostic"]["original_scene"]["points"]["origin"].update(radius=[[0,1]]*3))
    edit("reference_grid",lambda x:x[1]["result"]["diagnostic"].update(reference_root96=[[1,1],[1,1]]))
    edit("inherited_bound",lambda x:x[0]["result"]["diagnostic"]["subtractions"][0]["consumer"].update(inherited_bound=[0,1]))
    edit("candidate_words",lambda x:x[0]["result"]["diagnostic"]["subtractions"][0]["consumer"].update(candidate_pair_words=["0000000000000000"]*2))
    # Synthetic algebraic control, NOT another scene or numerical root run.
    ctl=m.prove(Q(1),Q(2),Q(1),Q(1),Q(3,2),Q(1),Q(1),Q(1),Q(2))
    assert ctl["mathematical_bound_proved"]is True and ctl["whole_HOST_interval_contained"]is False
    assert [frac(x)for x in ctl["mathematical_outer_interval"]]==[Q(0),Q(1,2)]
    bad_controls=[]
    for name,args in [
        ("upper_square_fails",(1,2,1,1,1,1,1,1,2)),
        ("reference_square_fails",(1,2,1,1,Q(3,2),2,2,1,2)),
        ("negative_length_no_square_inference",(1,2,1,-1,Q(3,2),1,1,1,2))]:
        try:m.prove(*map(Q,args))
        except ValueError as ex:bad_controls.append(dict(name=name,reason=str(ex)))
        else:raise AssertionError(name)
    api=[]
    api.append(m.run(k,{**req,"source":"SOURCE1"}))
    original=m.receipt
    def missing(*a):raise OSError("SIMULATED_MISSING_PARENT")
    def drift(*a):raise ValueError("SIMULATED_RECEIPT_SHA_DRIFT")
    try:
        for reader in (missing,drift):
            m.receipt=reader;api.append(m.run(k,req))
    finally:m.receipt=original
    assert api[0]["status"]=="STOP_INPUT"and all(x["integer_word_decodes"]==0 for x in api)
    assert all(x["status"]=="STOP_DEPENDENCY"for x in api[1:])
    summary=dict(records=16,conditional_mathematical_proofs=2,legacy_enclosure_stops_preserved=2,
        upstream_stops_preserved=14,engine_admissions=0,phase_admissions=0,
        integer_word_decodes_for_retained_positive_records=24,new_root_evaluations=0,
        new_RN=0,new_encoder_calls=0,old_numeric_modules_imported=0,
        invalid_selectors=8,in_memory_forgery_rejections=8,synthetic_algebra_control=1,
        invalid_algebra_certificates=3,API_negative=3,dependency_pins=len(pins),
        full_costs="UNKNOWN_NOT_ZERO",seconds_are_QA_not_benchmark=True)
    return dict(status="PASS_HOST_CONDITIONAL_MATH_CERTIFICATES_LEGACY_STOP_PRESERVED",
        evidence=dict(records=records,independent=oracle,invalid_selectors=selectors,
        forged_captures=mutations,algebra_control=dict(label="CPU_SYNTHETIC_ALGEBRA_CONTROL",proof=ctl),
        invalid_algebra_certificates=bad_controls,API_negative=api),summary=summary)

if __name__=="__main__":print(json.dumps(suite(),sort_keys=True,separators=(",",":"),allow_nan=False))
