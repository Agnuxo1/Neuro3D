"""Independent CPU total-phase wire verifier; exact bit-string/rational bounds, no producers."""
from pathlib import Path
from fractions import Fraction as F
import ast,base64,copy,hashlib,json,zlib
ROOT=Path(__file__).resolve().parents[2]
ID="PRECISION-OBLIQUE-TOTAL-PHASE-PAIR64-EGRESS-HOST-001"
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-TOTAL-PHASE-PAIR64-CPU-001-CODEX.json"
PSHA="acc107cb584dba1d7845584ac1040569fa3a2dd4be7d2f9c39d702d2ce06b6c3"
MODEL="precision-oblique-total-phase-pair64-egress-HOST-v1"
ORIGIN="CPU_UNATTESTED_BYTES";TAG=0x43545031;INTENT="HOST_CPU_TOTAL_PHASE_EGRESS_ONLY"
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode())
def f(q):
    assert type(q)is list and len(q)==2 and all(type(v)is int for v in q)and q[1]>0
    return F(*q)
def p(q):return [q.numerator,q.denominator]
def capture(t):
    assert t["rc"]==0 and t["timed_out"]is False and t["stderr"]==""
    assert t["threads"]==1 and t["affinity_mask"]==1 and t["hard_child_timeout_seconds"]==60 and 0<=t["elapsed_seconds"]<=65
    b=zlib.decompress(base64.b64decode(t["stdout_zlib_base64"],validate=True))
    assert len(b)==t["stdout_bytes"]and sha(b)==t["stdout_sha256"]
    return json.loads(b)
def dec(b):
    assert len(b)==8
    s=format(int.from_bytes(b,"little"),"064b");e=int(s[1:12],2)
    if e==2047:raise ValueError("raw_nonfinite")
    q=F(int(s[12:],2)+(2**52 if e else 0))*F(2)**(e-1075 if e else -1074)
    return -q if s[0]=="1"else q
def selector(case,ev):
    q=ev[case]["native_request"]
    return dict(case=case,native_request_sha256=digest(q),phase_request_sha256=q["phase_request_sha256"],
        original_scene_sha256=q["original_scene_sha256"],literal_request_sha256=q["literal_request_sha256"],abi_tag=TAG,intent=INTENT)
def packet(a):
    rows=a["native_result"]["rows"]
    return b"".join(v.to_bytes(4,"little")for v in(TAG,6,2,1))+b"".join(bytes.fromhex(r[k])for r in rows for k in("hi","lo"))
def baseline():
    return dict(model=MODEL,status="STOP",reason=None,rows=[],diagnostics=[],raw_hex=None,
        promotion="STOP",GPU_launch_allowed=False,GPU_executed=False,GPU_guard_certified=False,
        V2_total_phase_backend_bound=False,native_promotion_allowed=False,scene_authenticated=False,
        material_authenticated=False,fence_readback_authenticated=False,physical_field_certified=False,
        amplitude=None,field=None,power=None,full_costs="UNMEASURED_NOT_ZERO",
        RN64_operations=0,producer_replays=0,compiler_calls=0,output_extent_bytes=64,
        semantic_order=["SOURCE0_TOTAL","SOURCE1_TOTAL","SOURCE0_MINUS_SOURCE1_TOTAL"])
def expected(item,ev):
    out=baseline();req=item["request"];raw=bytes.fromhex(item["raw_hex"])if item["raw_type"]=="bytes"else None
    reason=None
    if item["origin"]!=ORIGIN:reason="unattested_origin_only"
    elif item["model"]!=MODEL:reason="model"
    elif type(req)is not dict or set(req)!=set(selector("parent_oblique",ev)):reason="closed_selector"
    elif type(req["case"])is not str or req["case"]not in ev:reason="case"
    elif type(req["abi_tag"])is not int or req!=selector(req["case"],ev):reason="selector_identity"
    elif ev[req["case"]]["native_result"]["status"]!="CPU_DECLARED_TOTAL_PHASE_PAIR64_ONLY":
        reason="parent_STOP:"+str(ev[req["case"]]["native_result"]["reason"])
    elif raw is None:reason="raw_type"
    elif len(raw)!=64:reason="output_extent"
    elif [int.from_bytes(raw[j:j+4],"little")for j in range(0,16,4)]!=[TAG,6,2,1]:reason="CPU_total_phase_header"
    if reason:out["reason"]=reason;return out
    a=ev[req["case"]];pr=a["native_result"]["rows"]
    assert [r["record_id"]for r in pr]==["S0","S1","S0-minus-S1"]
    words=[raw[16+8*j:24+8*j]for j in range(6)]
    try:decoded=[dec(b)for b in words]
    except ValueError as ex:out["reason"]=str(ex);return out
    vals=[decoded[2*j]+decoded[2*j+1]for j in range(3)];deltas=[];diags=[]
    for j,r in enumerate(pr[:2]):
        lo,hi=map(f,r["interval_cycles"]);delta=abs(vals[j]-f(r["value_cycles"]))
        components=sum((f(r[k])for k in("geometric_error_cycles","gamma_radius_cycles","mu_radius_cycles",
            "gamma_encoding_error_cycles","mu_encoding_error_cycles","gamma_add_error_cycles","mu_add_error_cycles")),F(0))
        assert 8*components==f(r["conservative_error_rad"])
        cb=8*(components+delta);db=8*(abs(vals[j]-(lo+hi)/2)+(hi-lo)/2);cap=f(r["literal_cap_rad"])
        assert db<=cb
        diags.append(dict(record_id=r["record_id"],hi=words[2*j].hex(),lo=words[2*j+1].hex(),value_cycles=p(vals[j]),
            interval_cycles=[p(lo),p(hi)],egress_delta_cycles=p(delta),direct_error_rad=p(db),conservative_error_rad=p(cb),literal_cap_rad=p(cap),fits=cb<=cap))
        deltas.append(delta)
    r=pr[2];lo,hi=map(f,r["interval_cycles"]);err=abs(vals[2]-(vals[0]-vals[1]))
    components=sum((f(r[k])for k in("geometric_error_cycles","gamma_radius_cycles","gamma_encoding_error_cycles","SOURCE_add_error_cycles")),F(0))
    assert 8*(components+f(r["relative_arithmetic_error_cycles"]))==f(r["conservative_error_rad"])
    cb=8*(components+sum(deltas)+err);db=8*(abs(vals[2]-(lo+hi)/2)+(hi-lo)/2);cap=f(r["literal_cap_rad"])
    assert db<=cb
    diags.append(dict(record_id=r["record_id"],hi=words[4].hex(),lo=words[5].hex(),value_cycles=p(vals[2]),
        interval_cycles=[p(lo),p(hi)],SOURCE_egress_delta_cycles=p(sum(deltas)),relative_arithmetic_error_cycles=p(err),
        direct_error_rad=p(db),conservative_error_rad=p(cb),literal_cap_rad=p(cap),fits=cb<=cap))
    out["diagnostics"]=diags
    if not all(v["fits"]for v in diags[:2]):reason="ALL_SOURCE_egress_cap"
    elif not diags[2]["fits"]:reason="relative_egress_cap"
    elif raw!=packet(a):reason="native_total_phase_bits"
    if reason:out["reason"]=reason
    else:out.update(status="HOST_CPU_TOTAL_PHASE_UNATTESTED_MATCH",rows=diags,raw_hex=raw.hex())
    return out
def manifest(ev):
    cases=[]
    def add(label,case,raw,req=None,model=MODEL,origin=ORIGIN):
        cases.append(dict(id=label,case=case,request=selector(case,ev)if req is None else req,model=model,origin=origin,
            raw_type=type(raw).__name__,raw_hex=raw.hex()if type(raw)is bytes else None))
    valid=[]
    for c,a in ev.items():
        ok=a["native_result"]["status"]=="CPU_DECLARED_TOTAL_PHASE_PAIR64_ONLY"
        add("sealed_"+c,c,packet(a)if ok else b"")
        if ok:valid.append(c)
    c="parent_oblique";raw=packet(ev[c]);base=selector(c,ev)
    add("wrong_model",c,raw,model="V2_PROPAGATION_ONLY")
    for origin in("GPU_READBACK","GPU_ATTESTED","CPU_AUTHENTICATED"):add("origin_"+origin,c,raw,origin=origin)
    for k in("native_request_sha256","phase_request_sha256","original_scene_sha256","literal_request_sha256","abi_tag","intent"):
        q=copy.deepcopy(base);q[k]="wrong";add("bad_"+k,c,raw,q)
    for label,key,v in(("boolean_tag","abi_tag",True),("unknown_case","case","unknown"),("extra_launch","launch_GPU",True)):
        q=copy.deepcopy(base);q[key]=v;add(label,c,raw,q)
    q=copy.deepcopy(base);del q["intent"];add("missing_intent",c,raw,q)
    add("raw_string",c,"bad")
    for label,cut in(("short",raw[:-1]),("long",raw+b"\0"),("V2_extent",raw[:32]),("header_only",raw[:16])):add(label,c,cut)
    for j,v in enumerate((0x4f444632,4,1,0)):
        b=bytearray(raw);b[4*j:4*j+4]=v.to_bytes(4,"little");add("header_"+str(j),c,bytes(b))
    for j in range(6):
        for n in(0x7ff0000000000000,0xfff0000000000000,0x7ff8000000000001,0xfff0000000000001):
            b=bytearray(raw);b[16+8*j:24+8*j]=n.to_bytes(8,"little");add("nonfinite_"+str(j)+"_"+hex(n),c,bytes(b))
    for j in range(2):
        b=bytearray(raw);b[16+16*j:32+16*j]=bytes(16);add("SOURCE_zero_"+str(j),c,bytes(b))
        b=bytearray(raw);b[24+16*j:32+16*j]=bytes(8);add("SOURCE_hi_only_"+str(j),c,bytes(b))
    b=bytearray(raw);b[48:64]=bytes(16);add("relative_zero",c,bytes(b))
    for j in range(3):
        b=bytearray(raw);b[24+16*j]^=1;add("within_cap_low_bit_"+str(j),c,bytes(b))
    b=bytearray(raw);b[16:32],b[32:48]=raw[32:48],raw[16:32];add("SOURCE_reordered",c,bytes(b))
    classes={}
    for name in valid:classes.setdefault(packet(ev[name]).hex(),[]).append(name)
    dup=[names for names in classes.values()if len(names)>1];assert dup
    witness=dup[0][1];add("copied_matching_bytes_NOT_provenance",witness,packet(ev[dup[0][0]]))
    q=selector(c,ev);q["case"]=witness;add("foreign_selector_not_rebound",witness,raw,q)
    return cases,dup
def main():
    receipt=json.loads((ROOT/("coordinacion/respuestas/"+ID+"-CODEX.json")).read_bytes());pins=receipt["code_doc_sha256"]
    assert len(pins)==136
    for path,h in pins.items():assert sha((ROOT/path).read_bytes())==h,("pin",path)
    b=(ROOT/PARENT).read_bytes();assert sha(b)==PSHA and pins[PARENT]==PSHA
    par=json.loads(b);assert len(par["code_doc_sha256"])==131 and all(pins[k]==v for k,v in par["code_doc_sha256"].items())
    assert capture(par["independent_pre_after_whitespace"])["status"]=="PASS"
    pdata=capture(par["test_run"])["data"]
    ev={v["id"]:dict(native_request=v["request"],native_model=v["model"],native_result=v["result"],
        registry_entry=pdata["registry"].get(v["id"]))for v in pdata["runs"]}
    d=capture(receipt["test_run"]);assert d["status"]=="PASS"and d["groups"]==6;data=d["data"]
    assert capture(receipt['initial_test_run'])==d and receipt['initial_test_run']['stdout_sha256']==receipt['test_run']['stdout_sha256']
    old=receipt['initial_core_source']
    revised=old.replace('        words=[raw[16+8*j:24+8*j]for j in range(6)];decoded=[number(v)for v in words]', '        words=[raw[16+8*j:24+8*j]for j in range(6)]\n        need(all((int.from_bytes(v,"little")>>52)&2047!=2047 for v in words),"raw_nonfinite")\n        decoded=[number(v)for v in words]')
    assert (ROOT/'Blender/benchmarks/capacity_audit/oblique_total_phase_pair64_egress_HOST_v1.py').read_text(encoding='utf-8')==revised
    assert (ROOT/'Blender/tests/test_oblique_total_phase_pair64_egress_HOST.py').read_text(encoding='utf-8')==receipt['initial_test_source']
    assert data["evidence"]==ev
    cases,dup=manifest(ev);runs=data["runs"]
    assert len(cases)==len(runs)==104 and len({v["id"]for v in runs})==104
    assert {v["id"]:v for v in cases}=={v["id"]:{k:v[k]for k in cases[0]}for v in runs}
    assert data["duplicate_byte_classes"]==dup
    for v in runs:assert v["result"]==expected(v,ev),v["id"]
    assert sum(v["result"]["status"]=="HOST_CPU_TOTAL_PHASE_UNATTESTED_MATCH"for v in runs)==12
    exp=data["exports"];assert len(exp)==46 and {v["case"]for v in exp}==set(ev)
    lookup={v["case"]:v for v in runs if v["id"].startswith("sealed_")}
    for v in exp:
        assert v["request"]==selector(v["case"],ev)and v["result"]==lookup[v["case"]]["result"]
    assert all(data[k]==0 for k in("RN64_operations","producer_replays","compiler_calls"))
    assert next(v for v in runs if v["id"]=="sealed_new_declared_cap_edge_mu_tenth")["result"]["reason"]=="parent_STOP:ALL_SOURCE_cap_after_encoding_arithmetic"
    low=[v for v in runs if v["id"].startswith("within_cap_low_bit_")]
    assert len(low)==3 and all(all(z["fits"]for z in v["result"]["diagnostics"])and v["result"]["rows"]==[]for v in low)
    assert len([v for v in runs if v["id"].startswith("nonfinite_")and v["result"]["diagnostics"]==[]])==24
    tree=ast.parse((ROOT/"Blender/benchmarks/capacity_audit/oblique_total_phase_pair64_egress_HOST_v1.py").read_text(encoding="utf-8"))
    for name,args in(("compare",["model","request","raw","origin"]),("export",["model","request"])):
        fun=next(v for v in tree.body if isinstance(v,ast.FunctionDef)and v.name==name)
        assert [v.arg for v in fun.args.args]==args and not fun.args.defaults and fun.args.kwarg is None
        assert any(isinstance(v,ast.Call)and isinstance(v.func,ast.Name)and v.func.id=="load_evidence"for v in ast.walk(fun))
    print(json.dumps(dict(status="PASS",cases=104,matches=12,stops=92,exports=46,pins=136,
        nonfinite_raw_prebudget_rejections=24,within_cap_wrong_bits_rejections=3,
        copied_matching_bytes_NOT_provenance=True,RN64_operations=0,producer_replays=0,
        GPU_launch_allowed=False,V2_total_phase_backend_bound=False)))
if __name__=="__main__":main()
