"""Exact integer/rational oracle over captures; never import/replay native producers."""
from pathlib import Path
from fractions import Fraction as F
import ast,base64,copy,hashlib,json,zlib
ROOT=Path(__file__).resolve().parents[2]
ID="PRECISION-OBLIQUE-TOTAL-PHASE-PAIR64-CPU-001"
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-SOURCE-MATERIAL-INTERVAL-HOST-001-CODEX.json"
PSHA="f7a5f99aa2d2f18d68b01ab9c4afe4b1db85bc78c7a6a9228809b3066e46a05b"
MODEL="precision-oblique-total-phase-pair64-CPU-v1"
REP="TOTAL_DECLARED_PHASE_PAIR64_CPU_NOT_GPU_ABI"
SIGN=1<<63
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode())
def f(q):
    assert type(q)is list and len(q)==2 and all(type(v)is int for v in q)and q[1]>0
    return F(*q)
def p(q):return [q.numerator,q.denominator]
def raw(h):
    assert type(h)is str and len(h)==16 and bytes.fromhex(h).hex()==h
    return int.from_bytes(bytes.fromhex(h),"little")
def word(n):return n.to_bytes(8,"little").hex()
def decint(n):
    sign=-1 if n&SIGN else 1;e=(n>>52)&2047;m=n&((1<<52)-1)
    assert e!=2047,"nonfinite"
    sig=m+(1<<52 if e else 0);shift=e-1075 if e else -1074
    return sign*F(sig*(1<<max(shift,0)),1<<max(-shift,0))
def dec(h):return decint(raw(h))
def pair(words):return sum(map(dec,words),F(0))
def rn(q,h):
    n=raw(h);v=decint(n);mag=n&(SIGN-1)
    if mag==0:lower,upper=-F(1,1<<1074),F(1,1<<1074)
    elif n&SIGN:lower,upper=decint(SIGN|(mag+1)),decint(SIGN|(mag-1))
    else:lower,upper=decint(mag-1),decint(mag+1)
    a,b=(lower+v)/2,(v+upper)/2
    assert a<=q<=b and (q not in(a,b)or n&1==0),"RN64_midpoint_ties_even"
def capture(t,rc=0):
    assert t["rc"]==rc and t["timed_out"]is False
    assert t["threads"]==1 and t["affinity_mask"]==1 and t["hard_child_timeout_seconds"]==60
    assert 0<=t["elapsed_seconds"]<=65
    b=zlib.decompress(base64.b64decode(t["stdout_zlib_base64"],validate=True))
    assert len(b)==t["stdout_bytes"]and sha(b)==t["stdout_sha256"]
    if rc==0:assert t["stderr"]==""
    return b
def restore(parent):
    d=json.loads(capture(parent["test_run"]))["data"];ev=d["evidence"]
    reg={r["id"]:dict(request=r["request"],declared=r["result"],fixture=ev[r["request"]["case"]],kind="SEALED_PARENT")for r in d["runs"]}
    assert len(reg)==34
    base=reg["parent_oblique"]
    for label in("new_mu_tenth","new_gamma_2m120","new_declared_cap_edge_mu_tenth"):
        q=copy.deepcopy(base["request"])
        if label=="new_gamma_2m120":q["sources"][0]["phase_interval_cycles"]=[[1,1<<120],[1,1<<120]]
        else:
            radius=F(0)
            if label.endswith("mu_tenth")and label!="new_mu_tenth":
                rr=base["fixture"]["rows"][:2]
                radius=f(rr[0]["literal_cap_rad"])/8-max(max(abs(f(r["pair_value"])-f(v))for v in r["interval"])for r in rr)
                assert radius>0
            q["material"]["phase_interval_cycles"]=[p(F(1,10)-radius),p(F(1,10)+radius)]
        reg[label]=dict(base,request=q,kind="NEW_OWN_VARIANT",declared=None)
    return reg
def select(case,reg):
    q=reg[case]["request"]
    return dict(case=case,phase_request_sha256=digest(q),original_scene_sha256=q["original_scene_sha256"],
        literal_request_sha256=q["literal_request_sha256"],representation=REP,intent="CPU_NATIVE_TOTAL_PHASE_ONLY")
def parameters(enc,gi,mu):
    assert len(enc)==3
    values=[];errors=[]
    for j,x in enumerate(enc):
        q=sum(gi[j])/2 if j<2 else sum(mu)/2
        assert set(x)=={"name","input","hi","lo","error_cycles","RN64_casts"}
        assert x["name"]==("gamma"+str(j)if j<2 else "mu")and f(x["input"])==q and x["RN64_casts"]==2
        rn(q,x["hi"]);rn(q-dec(x["hi"]),x["lo"])
        if q==0:assert raw(x["hi"])==0
        if q-dec(x["hi"])==0:assert raw(x["lo"])==0
        words=(x["hi"],x["lo"]);err=abs(pair(words)-q)
        assert f(x["error_cycles"])==err
        values.append(words);errors.append(err)
    return values,errors
def graph(nodes,a,b,prefix):
    assert len(nodes)==26
    cursor=0
    def node(x,y,operator,name):
        nonlocal cursor
        z=nodes[cursor];cursor+=1
        assert set(z)=={"name","op","a","b","y","error_cycles"}
        assert (z["a"],z["b"],z["op"],z["name"])==(x,y,operator,name)
        target=dec(x)+(dec(y)if operator=="+"else -dec(y))
        rn(target,z["y"])
        assert f(z["error_cycles"])==abs(dec(z["y"])-target)
        return z["y"]
    def twosum(x,y,name):
        s=node(x,y,"+",name+"_s")
        bb=node(s,x,"-",name+"_bb");ab=node(s,bb,"-",name+"_ab")
        db=node(y,bb,"-",name+"_db");da=node(x,ab,"-",name+"_da")
        e=node(da,db,"+",name+"_e")
        assert dec(s)+dec(e)==dec(x)+dec(y),"EFT_identity"
        return s,e
    h=twosum(a[0],b[0],prefix+"_h");l=twosum(a[1],b[1],prefix+"_l")
    e=node(h[1],l[0],"+",prefix+"_eadd");m=twosum(h[0],e,prefix+"_m")
    low=node(m[1],l[1],"+",prefix+"_ladd");out=twosum(m[0],low,prefix+"_r")
    assert cursor==26
    return out
def check_computed(result,entry):
    q=entry["request"];rows=entry["fixture"]["rows"]
    gi=[tuple(map(f,s["phase_interval_cycles"]))for s in q["sources"]];mu=tuple(map(f,q["material"]["phase_interval_cycles"]))
    # Independent midpoint/radius formulation of the declared analytic gate.
    gm=[sum(v)/2 for v in gi];gr=[(v[1]-v[0])/2 for v in gi];mm=sum(mu)/2;mr=(mu[1]-mu[0])/2
    prop=[(r["hi"]["word_le_hex"],r["lo"]["word_le_hex"])for r in rows[:2]]
    geom=[tuple(map(f,r["interval"]))for r in rows[:2]]
    for j in range(2):
        assert pair(prop[j])==f(rows[j]["pair_value"])
        assert 8*(abs(pair(prop[j])-sum(geom[j])/2)+(geom[j][1]-geom[j][0])/2+gr[j]+mr)<=f(rows[j]["literal_cap_rad"])
    relgeom=tuple(map(f,rows[2]["parent_relative_CONTROL_ONLY"]["interval"]))
    assert 8*(abs(f(rows[2]["pair_value"])-sum(relgeom)/2)+(relgeom[1]-relgeom[0])/2+sum(gr))<=f(rows[2]["literal_cap_rad"])
    assert result["analytic_interval_admitted"]is True
    params,errors=parameters(result["encodings"],gi,mu);trace=result["trace"]
    assert len(trace)==130 and result["RN64_arithmetic_operations"]==130 and result["RN64_parameter_casts"]==6
    totals=[];add_errors=[];expected=[]
    for j in range(2):
        first=graph(trace[52*j:52*j+26],prop[j],params[j],"S"+str(j)+"_gamma")
        final=graph(trace[52*j+26:52*j+52],first,params[2],"S"+str(j)+"_mu")
        e1=abs(pair(first)-pair(prop[j])-pair(params[j]));e2=abs(pair(final)-pair(first)-pair(params[2]))
        lo,hi=geom[j];base=abs(pair(prop[j])-(lo+hi)/2)+(hi-lo)/2
        low,high=lo+gi[j][0]+mu[0],hi+gi[j][1]+mu[1]
        direct=8*(abs(pair(final)-(low+high)/2)+(high-low)/2)
        conservative=8*(base+gr[j]+mr+errors[j]+errors[2]+e1+e2);cap=f(rows[j]["literal_cap_rad"])
        assert direct<=conservative
        expected.append(dict(record_id="S"+str(j),hi=final[0],lo=final[1],value_cycles=p(pair(final)),
            interval_cycles=[p(low),p(high)],geometric_error_cycles=p(base),
            gamma_encoding_error_cycles=p(errors[j]),mu_encoding_error_cycles=p(errors[2]),
            gamma_add_error_cycles=p(e1),mu_add_error_cycles=p(e2),gamma_radius_cycles=p(gr[j]),mu_radius_cycles=p(mr),
            direct_error_rad=p(direct),conservative_error_rad=p(conservative),literal_cap_rad=p(cap),fits=conservative<=cap))
        totals.append(final);add_errors.append(e1+e2)
    neg=tuple(word(raw(v)^SIGN)for v in totals[1])
    relative=graph(trace[104:],totals[0],neg,"relative")
    err=abs(pair(relative)-(pair(totals[0])-pair(totals[1])))
    lo,hi=relgeom;pv=pair(prop[0])-pair(prop[1]);base=abs(pv-(lo+hi)/2)+(hi-lo)/2
    low,high=lo+gi[0][0]-gi[1][1],hi+gi[0][1]-gi[1][0]
    cb=8*(base+sum(gr)+sum(errors[:2])+sum(add_errors)+err)
    db=8*(abs(pair(relative)-(low+high)/2)+(high-low)/2);cap=f(rows[2]["literal_cap_rad"])
    assert db<=cb
    expected.append(dict(record_id="S0-minus-S1",hi=relative[0],lo=relative[1],value_cycles=p(pair(relative)),
        interval_cycles=[p(low),p(high)],geometric_error_cycles=p(base),gamma_radius_cycles=p(sum(gr)),
        SOURCE_add_error_cycles=p(sum(add_errors)),relative_arithmetic_error_cycles=p(err),gamma_encoding_error_cycles=p(sum(errors[:2])),
        shared_mu_encoding_cancellation="SAME_ENCODED_PAIR_ONLY_NOT_SOURCE_ADDITIONS",source_phase_offset_cycles=p(gm[0]-gm[1]),
        direct_error_rad=p(db),conservative_error_rad=p(cb),literal_cap_rad=p(cap),fits=cb<=cap))
    assert result["diagnostics"]==expected and result["phase_request_sha256"]==digest(q)
    reason=None if all(r["fits"]for r in expected)else("ALL_SOURCE_cap_after_encoding_arithmetic"if not all(r["fits"]for r in expected[:2])else "relative_cap_after_encoding_arithmetic")
    assert result["reason"]==reason
    assert result["rows"]==([]if reason else expected)
    assert result["status"]==("STOP"if reason else "CPU_DECLARED_TOTAL_PHASE_PAIR64_ONLY")
def main():
    rec=json.loads((ROOT/("coordinacion/respuestas/"+ID+"-CODEX.json")).read_bytes())
    pins=rec["code_doc_sha256"];assert len(pins)==131
    for path,h in pins.items():assert sha((ROOT/path).read_bytes())==h,("pin",path)
    pb=(ROOT/PARENT).read_bytes();assert sha(pb)==PSHA
    parent=json.loads(pb)
    assert len(parent["code_doc_sha256"])==126 and all(pins[k]==v for k,v in parent["code_doc_sha256"].items())
    assert pins[PARENT]==PSHA
    data=json.loads(capture(rec["test_run"]));assert data["status"]=="PASS"and data["groups"]==5
    d=data["data"];reg=restore(parent);assert d["registry"]==reg and len(reg)==37
    runs=d["runs"];assert len(runs)==46 and len({v["id"]for v in runs})==46
    expected_ids=set(reg)|{"native_wrong_model","unknown_case","extra_launch","missing_intent"}|{"bad_"+k for k in("phase_request_sha256","original_scene_sha256","literal_request_sha256","representation","intent")}
    assert {v["id"]for v in runs}==expected_ids
    keys=set(select("parent_oblique",reg));computed=passed=0
    for item in runs:
        label=item["id"];req=item["request"];r=item["result"]
        assert r["model"]==MODEL and r["representation"]==REP and r["promotion"]=="STOP"
        for k in("GPU_executed","GPU_launch_allowed","physical_field_certified","scene_authenticated","material_authenticated","native_promotion_allowed","V2_total_phase_backend_bound"):assert r[k]is False
        assert all(r[k]is None for k in("amplitude","field","power"))
        assert r["compiler_calls"]==r["frozen_producer_replays"]==0 and r["full_costs"]=="UNMEASURED_NOT_ZERO"
        if label in reg:assert req==select(label,reg)and item["model"]==MODEL
        else:
            expected=select("parent_oblique",reg);model=MODEL
            if label=="native_wrong_model":model="V2_TOTAL_GPU"
            elif label.startswith("bad_"):expected[label[4:]]="wrong"
            elif label=="unknown_case":expected["case"]="unknown"
            elif label=="extra_launch":expected["launch_GPU"]=True
            elif label=="missing_intent":del expected["intent"]
            assert req==expected and item["model"]==model
        reason=None
        if item["model"]!=MODEL:reason="model"
        elif set(req)!=keys:reason="closed_selector"
        elif req["case"]not in reg:reason="case"
        elif req!=select(req["case"],reg):reason="selector_identity"
        else:
            entry=reg[req["case"]]
            if entry["declared"]is not None and entry["declared"]["status"]!="HOST_DECLARED_TOTAL_PHASE_INTERVAL_ONLY":
                reason="parent_STOP:"+entry["declared"]["reason"]
        if reason:
            assert r["reason"]==reason and r["status"]=="STOP"and r["analytic_interval_admitted"]is False
            assert r["rows"]==r["diagnostics"]==r["encodings"]==r["trace"]==[]
            assert r["RN64_arithmetic_operations"]==r["RN64_parameter_casts"]==0
        else:check_computed(r,reg[req["case"]]);computed+=1
        passed+=r["status"]=="CPU_DECLARED_TOTAL_PHASE_PAIR64_ONLY"
    assert computed==12 and passed==11
    assert d["total_new_arithmetic_RN"]==1560 and d["total_new_parameter_RN"]==72 and d["parent_producer_replays"]==0
    byid={v["id"]:v["result"]for v in runs};edge=byid["new_declared_cap_edge_mu_tenth"]
    assert edge["status"]=="STOP"and edge["analytic_interval_admitted"]and f(edge["encodings"][2]["error_cycles"])>0
    assert edge["rows"]==[]and any(not v["fits"]for v in edge["diagnostics"][:2])
    assert any(f(v["gamma_add_error_cycles"])>0 for v in byid["new_gamma_2m120"]["diagnostics"][:2])
    assert capture(rec["initial_failure"],1)==b""
    assert "AssertionError"in rec["initial_failure"]["stderr"]
    old=rec["initial_test_source"]
    repaired=old.replace('        r=m.compute(model,req)','        assert label not in {v["id"] for v in runs},"unique_case_before_execution"\n        r=m.compute(model,req)').replace('run("wrong_model",base,','run("native_wrong_model",base,')
    assert (ROOT/"Blender/tests/test_oblique_total_phase_pair64_CPU.py").read_text()==repaired
    source=ast.parse((ROOT/"Blender/benchmarks/capacity_audit/oblique_total_phase_pair64_CPU_v1.py").read_text())
    public=next(v for v in source.body if isinstance(v,ast.FunctionDef)and v.name=="compute")
    assert [v.arg for v in public.args.args]==["model","request"]and not public.args.defaults and public.args.kwarg is None
    assert any(isinstance(v,ast.Call)and isinstance(v.func,ast.Name)and v.func.id=="load_evidence"for v in ast.walk(public))
    print(json.dumps(dict(status="PASS",cases=46,CPU_admitted=11,stopped=35,computed_cases=12,
        RN64_arithmetic_nodes_verified=1560,RN64_parameter_casts_verified=72,pins=131,
        initial_ID_collision_failure_preserved=True,boundary_analytic_PASS_native_STOP=True,
        producer_replays=0,GPU_launch_allowed=False,V2_total_phase_backend_bound=False)))
if __name__=="__main__":main()
