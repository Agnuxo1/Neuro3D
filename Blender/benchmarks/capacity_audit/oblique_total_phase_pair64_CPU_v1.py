"""Native CPU pair64 total declared phase; opt-in, no GPU/physical inference."""
from pathlib import Path
from fractions import Fraction as F
import base64,copy,hashlib,json,math,struct,sys,zlib
ROOT=Path(__file__).resolve().parents[3]
MODEL="precision-oblique-total-phase-pair64-CPU-v1"
REP="TOTAL_DECLARED_PHASE_PAIR64_CPU_NOT_GPU_ABI"
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-SOURCE-MATERIAL-INTERVAL-HOST-001-CODEX.json"
PSHA="f7a5f99aa2d2f18d68b01ab9c4afe4b1db85bc78c7a6a9228809b3066e46a05b"
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode())
def p(q):return [q.numerator,q.denominator]
def f(q):return F(*q)
def need(v,msg):
    if not v:raise ValueError(msg)
def bits(v):need(math.isfinite(v),"finite_native");return struct.pack("<d",v).hex()
def exact(v):need(math.isfinite(v),"finite_native");return F.from_float(v)
def value(v):return exact(v[0])+exact(v[1])
def native(h):return struct.unpack("<d",bytes.fromhex(h))[0]
def load_evidence():
    raw=(ROOT/PARENT).read_bytes();need(sha(raw)==PSHA,"parent_identity");r=json.loads(raw)
    for path,h in r["code_doc_sha256"].items():need(sha((ROOT/path).read_bytes())==h,"ancestral_pin")
    t=r["test_run"];raw=zlib.decompress(base64.b64decode(t["stdout_zlib_base64"],validate=True))
    need(t["rc"]==0 and not t["timed_out"]and sha(raw)==t["stdout_sha256"]and len(raw)==t["stdout_bytes"],"capture_integrity")
    d=json.loads(raw)["data"];e=d["evidence"]
    registry={q["id"]:dict(request=q["request"],declared=q["result"],fixture=e[q["request"]["case"]],kind="SEALED_PARENT")for q in d["runs"]}
    base=copy.deepcopy(registry["parent_oblique"])
    q=copy.deepcopy(base["request"]);q["material"]["phase_interval_cycles"]=[[1,10],[1,10]]
    registry["new_mu_tenth"]=dict(base,request=q,kind="NEW_OWN_VARIANT",declared=None)
    q=copy.deepcopy(base["request"]);q["sources"][0]["phase_interval_cycles"]=[[1,1<<120],[1,1<<120]]
    registry["new_gamma_2m120"]=dict(base,request=q,kind="NEW_OWN_VARIANT",declared=None)
    q=copy.deepcopy(base["request"]);rows=base["fixture"]["rows"]
    prop=max(max(abs(f(r["pair_value"])-f(r["interval"][0])),abs(f(r["pair_value"])-f(r["interval"][1])))for r in rows[:2])
    radius=f(rows[0]["literal_cap_rad"])/8-prop
    need(radius>0,"new_boundary_radius")
    q["material"]["phase_interval_cycles"]=[p(F(1,10)-radius),p(F(1,10)+radius)]
    registry["new_declared_cap_edge_mu_tenth"]=dict(base,request=q,kind="NEW_OWN_VARIANT",declared=None)
    return registry
def selector(case,e):
    a=e[case];q=a["request"]
    return dict(case=case,phase_request_sha256=digest(q),original_scene_sha256=q["original_scene_sha256"],
        literal_request_sha256=q["literal_request_sha256"],representation=REP,intent="CPU_NATIVE_TOTAL_PHASE_ONLY")
def encode(q,name,enc):
    hi=float(q);lo=float(q-exact(hi));v=(hi,lo);error=abs(value(v)-q)
    enc.append(dict(name=name,input=p(q),hi=bits(hi),lo=bits(lo),error_cycles=p(error),RN64_casts=2))
    return v,error
def op(a,b,operator,name,trace):
    y=a+b if operator=="+"else a-b
    expected=exact(a)+exact(b)if operator=="+"else exact(a)-exact(b)
    trace.append(dict(name=name,op=operator,a=bits(a),b=bits(b),y=bits(y),error_cycles=p(abs(exact(y)-expected))))
    return y
def sum2(a,b,name,trace):
    s=op(a,b,"+",name+"_s",trace);bb=op(s,a,"-",name+"_bb",trace)
    ab=op(s,bb,"-",name+"_ab",trace);db=op(b,bb,"-",name+"_db",trace)
    da=op(a,ab,"-",name+"_da",trace);error=op(da,db,"+",name+"_e",trace)
    need(exact(s)+exact(error)==exact(a)+exact(b),"EFT_identity")
    return s,error
def plus(a,b,name,trace):
    h=sum2(a[0],b[0],name+"_h",trace);l=sum2(a[1],b[1],name+"_l",trace)
    err=op(h[1],l[0],"+",name+"_eadd",trace);mid=sum2(h[0],err,name+"_m",trace)
    low=op(mid[1],l[1],"+",name+"_ladd",trace)
    return sum2(mid[0],low,name+"_r",trace)
def _compute_fixture(model,request,e):
    out=dict(model=MODEL,representation=REP,status="STOP",reason=None,rows=[],diagnostics=[],encodings=[],trace=[],
        promotion="STOP",GPU_executed=False,GPU_launch_allowed=False,physical_field_certified=False,
        scene_authenticated=False,material_authenticated=False,native_promotion_allowed=False,
        V2_total_phase_backend_bound=False,analytic_interval_admitted=False,amplitude=None,field=None,power=None,full_costs="UNMEASURED_NOT_ZERO",
        compiler_calls=0,frozen_producer_replays=0,RN64_arithmetic_operations=0,RN64_parameter_casts=0)
    try:
        need(model==MODEL,"model")
        need(type(request)is dict and set(request)=={"case","phase_request_sha256","original_scene_sha256",
                "literal_request_sha256","representation","intent"},"closed_selector")
        need(request["case"]in e,"case");a=e[request["case"]]
        need(request==selector(request["case"],e),"selector_identity")
        if a["declared"]is not None:
            need(a["declared"]["status"]=="HOST_DECLARED_TOTAL_PHASE_INTERVAL_ONLY","parent_STOP:"+str(a["declared"]["reason"]))
        need(sys.float_info.mant_dig==53 and sys.float_info.max_exp==1024 and struct.calcsize("d")==8,"native64")
        q=a["request"];rows=a["fixture"]["rows"];trace=out["trace"];enc=out["encodings"]
        gi=[tuple(map(f,s["phase_interval_cycles"]))for s in q["sources"]];mu=tuple(map(f,q["material"]["phase_interval_cycles"]))
        if a["kind"]=="NEW_OWN_VARIANT":
            for j,r in enumerate(rows[:2]):
                nominal=f(r["pair_value"])+sum(gi[j])/2+sum(mu)/2
                lower=f(r["interval"][0])+gi[j][0]+mu[0];upper=f(r["interval"][1])+gi[j][1]+mu[1]
                need(8*max(abs(nominal-lower),abs(nominal-upper))<=f(r["literal_cap_rad"]),"new_analytic_SOURCE_cap")
            rr=rows[2];lower=f(rr["parent_relative_CONTROL_ONLY"]["interval"][0])+gi[0][0]-gi[1][1]
            upper=f(rr["parent_relative_CONTROL_ONLY"]["interval"][1])+gi[0][1]-gi[1][0]
            nominal=f(rr["pair_value"])+sum(gi[0])/2-sum(gi[1])/2
            need(8*max(abs(nominal-lower),abs(nominal-upper))<=f(rr["literal_cap_rad"]),"new_analytic_relative_cap")
        out["analytic_interval_admitted"]=True
        gamma=[encode((lo+hi)/2,"gamma"+str(j),enc)for j,(lo,hi)in enumerate(gi)]
        material,merr=encode(sum(mu)/2,"mu",enc)
        outputs=[];source_errors=[];source_prop=[];pending=[];allfits=[]
        # Four pair additions, 26 native +/- each. No old producer arithmetic is replayed.
        for j,r in enumerate(rows[:2]):
            prop=(native(r["hi"]["word_le_hex"]),native(r["lo"]["word_le_hex"]))
            need(value(prop)==f(r["pair_value"]),"sealed_SOURCE_pair")
            gpair,gerr=gamma[j];v1=plus(prop,gpair,"S"+str(j)+"_gamma",trace)
            e1=abs(value(v1)-value(prop)-value(gpair))
            total=plus(v1,material,"S"+str(j)+"_mu",trace)
            e2=abs(value(total)-value(v1)-value(material))
            lo,hi=map(f,r["interval"]);base=max(abs(value(prop)-lo),abs(value(prop)-hi))
            gamma_radius=(gi[j][1]-gi[j][0])/2;mu_radius=(mu[1]-mu[0])/2
            lower,upper=lo+gi[j][0]+mu[0],hi+gi[j][1]+mu[1]
            conservative=8*(base+gamma_radius+mu_radius+gerr+merr+e1+e2)
            direct=8*max(abs(value(total)-lower),abs(value(total)-upper));cap=f(r["literal_cap_rad"])
            need(direct<=conservative,"SOURCE_bound_dominates")
            pending.append(dict(record_id="S"+str(j),hi=bits(total[0]),lo=bits(total[1]),value_cycles=p(value(total)),
                interval_cycles=[p(lower),p(upper)],geometric_error_cycles=p(base),
                gamma_encoding_error_cycles=p(gerr),mu_encoding_error_cycles=p(merr),
                gamma_add_error_cycles=p(e1),mu_add_error_cycles=p(e2),gamma_radius_cycles=p(gamma_radius),
                mu_radius_cycles=p(mu_radius),direct_error_rad=p(direct),conservative_error_rad=p(conservative),
                literal_cap_rad=p(cap),fits=conservative<=cap))
            outputs.append(total);source_errors.append(e1+e2);source_prop.append(value(prop));allfits.append(conservative<=cap)
        # Unary sign-bit negation is exact and is not counted as an RN +/-.
        neg=tuple(-v for v in outputs[1]);relative=plus(outputs[0],neg,"relative",trace)
        re=abs(value(relative)-(value(outputs[0])-value(outputs[1])))
        lo,hi=map(f,rows[2]["parent_relative_CONTROL_ONLY"]["interval"]);pv=source_prop[0]-source_prop[1]
        base=max(abs(pv-lo),abs(pv-hi));offset=sum(gi[0])/2-sum(gi[1])/2
        low,high=lo+gi[0][0]-gi[1][1],hi+gi[0][1]-gi[1][0]
        grad=(gi[0][1]-gi[0][0]+gi[1][1]-gi[1][0])/2
        # Same encoded mu cancels algebraically; per-SOURCE add errors NEVER cancel by assumption.
        cb=8*(base+grad+gamma[0][1]+gamma[1][1]+sum(source_errors)+re)
        db=8*max(abs(value(relative)-low),abs(value(relative)-high));cap=f(rows[2]["literal_cap_rad"])
        need(db<=cb,"relative_bound_dominates")
        pending.append(dict(record_id="S0-minus-S1",hi=bits(relative[0]),lo=bits(relative[1]),value_cycles=p(value(relative)),
            interval_cycles=[p(low),p(high)],geometric_error_cycles=p(base),gamma_radius_cycles=p(grad),
            SOURCE_add_error_cycles=p(sum(source_errors)),relative_arithmetic_error_cycles=p(re),
            gamma_encoding_error_cycles=p(gamma[0][1]+gamma[1][1]),
            shared_mu_encoding_cancellation="SAME_ENCODED_PAIR_ONLY_NOT_SOURCE_ADDITIONS",
            source_phase_offset_cycles=p(offset),direct_error_rad=p(db),conservative_error_rad=p(cb),
            literal_cap_rad=p(cap),fits=cb<=cap))
        out["diagnostics"]=pending;out["phase_request_sha256"]=digest(q)
        need(all(allfits),"ALL_SOURCE_cap_after_encoding_arithmetic")
        need(cb<=cap,"relative_cap_after_encoding_arithmetic")
        out.update(status="CPU_DECLARED_TOTAL_PHASE_PAIR64_ONLY",rows=pending)
    except(ValueError,KeyError,TypeError,IndexError,OverflowError,OSError)as ex:out["reason"]=str(ex)
    out["RN64_arithmetic_operations"]=len(out["trace"])
    out["RN64_parameter_casts"]=sum(v["RN64_casts"]for v in out["encodings"])
    return out
def compute(model,request):
    try:e=load_evidence()
    except(ValueError,KeyError,TypeError,OSError)as ex:
        r=_compute_fixture("INVALID_EVIDENCE",request,{});r["reason"]="evidence_integrity:"+str(ex);return r
    return _compute_fixture(model,request,e)
