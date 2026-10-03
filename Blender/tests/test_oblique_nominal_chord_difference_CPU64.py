"""Independent IEEE-word/nearest-neighbor proof of signed26 graph and same-scene bounds."""
from pathlib import Path
from fractions import Fraction as F
import json,sys,hashlib,zlib,base64,copy,struct
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"Blender/benchmarks/capacity_audit"))
import oblique_nominal_chord_difference_CPU64_v1 as c
PSHA="b01d94f36d904d724029dc0c0d33904ea449390468324efaa72a4e275293b424"

def pair(v):return [v.numerator,v.denominator]
def val(v):
    assert type(v)is list and len(v)==2 and all(type(x)is int for x in v)and v[1]>0
    x=F(*v);assert pair(x)==v;return x

def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()

def capture(a):
    b=zlib.decompress(base64.b64decode(a["stdout_zlib_base64"],validate=True))
    assert a["rc"]==0 and not a["timed_out"]and len(b)==a["stdout_bytes"]and hashlib.sha256(b).hexdigest()==a["stdout_sha256"]
    return json.loads(b)

def retained():
    b=(ROOT/c.PARENT).read_bytes();assert len(b)==156906 and hashlib.sha256(b).hexdigest()==PSHA
    r=json.loads(b);pins=dict(r["code_doc_sha256"]);assert len(pins)==323
    for p,h in pins.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    assert capture(r["independent_pre"])["status"]=="PASS"
    p={x["id"]:x for x in capture(r["test_run"])["evidence"]["records"]}
    b=(ROOT/c.PRODUCER).read_bytes();assert len(b)==242660 and hashlib.sha256(b).hexdigest()==c.PRODSHA==pins[c.PRODUCER]
    n={x["id"]:x for x in capture(json.loads(b)["test_run"])["evidence"]["records"]}
    assert set(p)==set(n)and len(p)==16;pins[c.PARENT]=PSHA
    return p,n,pins

def pf(w):
    assert type(w)is str and len(w)==16 and all(ch in "0123456789abcdef"for ch in w)
    u=int.from_bytes(bytes.fromhex(w),"little");e=(u>>52)&2047;m=u&((1<<52)-1);assert e!=2047
    if e:q=F((1<<52)+m)*F(2)**(e-1023-52)
    else:q=F(m,2**1074)
    return -q if u>>63 else q

def nearest(w,target):
    q=pf(w);u=int.from_bytes(bytes.fromhex(w),"little");m=u&((1<<63)-1)
    if m==0:assert abs(target)<=F(1,2**1075);return q
    for nb in (m-1,m+1):
        assert nb<(2047<<52)
        neighbor=pf((nb|(u&(1<<63))).to_bytes(8,"little").hex())
        d,dn=abs(target-q),abs(target-neighbor)
        assert d<dn or(d==dn and(u&1)==0),(w,str(target))
    return q

def neg(w):return (int.from_bytes(bytes.fromhex(w),"little")^(1<<63)).to_bytes(8,"little").hex()

class ALUStop(Exception):pass

def graph(r):
    payload=r["input_payload_hex"];B=val(r["inherited_bound"]);assert B>=0
    ws=[payload[i*16:(i+1)*16]for i in range(4)];assert len(payload)==64
    a,b,x,y=(pf(w)for w in ws);W=x+y-a-b
    assert r["input_difference"]==pair(W)and abs(W)<=2**34
    assert r["fixed_RN_budget"]==26 and r["new_products"]==r["new_sqrt_calls"]==r["retained_numeric_replays"]==0
    assert r["full_costs"]=="UNKNOWN_NOT_ZERO"
    assert (r["hex_bytes_calls"],r["input_word_reads"],r["float_decode_calls"],r["decoded_components"],r["sign_flips"])==(1,4,1,4,2)
    ledger=r["ledger"];index=0;failed=None
    def step(name,op,aa,bb):
        nonlocal index,failed
        t=ledger[index];assert(t["index"],t["name"],t["op"],t["a"],t["b"])==(index,name,op,aa,bb)
        exact=pf(aa)+pf(bb)if op=="add"else pf(aa)-pf(bb)
        q=nearest(t["y"],exact);index+=1
        if abs(q)>2**34 or(q!=0 and abs(q)<F(1,2**1022))or(q==0 and exact!=0):
            failed=name;raise ALUStop()
        return t["y"]
    def two(prefix,aa,bb):
        s=step(prefix+".s","add",aa,bb);bv=step(prefix+".bb","sub",s,aa)
        av=step(prefix+".ab","sub",s,bv);bd=step(prefix+".db","sub",bb,bv)
        ad=step(prefix+".da","sub",aa,av);e=step(prefix+".err","add",ad,bd)
        assert pf(s)+pf(e)==pf(aa)+pf(bb)
        return s,e
    try:
        p=two("p",ws[2],neg(ws[0]));q=two("q",ws[3],neg(ws[1]))
        e=step("merge.e","add",p[1],q[0]);t=two("r",p[0],e)
        l=step("merge.l","add",t[1],q[1]);v=two("y",t[0],l)
    except ALUStop:
        assert r["status"]=="STOP_ALU"and r["reason"]=="normal_zero_no_underflow:"+failed
        assert r["RN_nodes_executed"]==index==len(ledger)and r["word_format_calls"]==3*index
        assert r["candidate_pair_words"]is None and r["native_pair_difference"]is None
        return dict(kind="ALU_STOP",RN=index)
    assert r["candidate_pair_words"]==list(v)and r["RN_nodes_executed"]==len(ledger)==index==26
    assert r["word_format_calls"]==80
    C=pf(v[0])+pf(v[1]);E=W-C;T=B+abs(E)
    assert r["native_pair_difference"]==pair(C)and r["HOST_signed_residual"]==pair(E)
    assert r["HOST_arithmetic_error_bound"]==pair(abs(E))and r["HOST_total_difference_error_bound"]==pair(T)
    assert r["HOST_difference_interval"]==[pair(C-T),pair(C+T)]
    assert (r["status"],r["reason"])==(("CPU64_EXACT_PAIR_DIFFERENCE_ONLY","fixed26_signed_difference_not_scene_or_phase")
        if E==0 else("STOP_PAIR_DIFFERENCE_RESIDUAL","nonzero_pair_difference_residual"))
    return dict(kind="EXACT"if E==0 else"LOSS",RN=26,C=C,T=T,E=E)

def encoding(r):
    x=val(r["rational"]);assert r["HOST_float_conversions"]==r["HOST_word_formats"]==2
    hi,lo=r["words"];H=nearest(hi,x);L=nearest(lo,x-H);C=H+L;E=x-C
    assert r["payload_hex"]==hi+lo and r["HOST_exact_pair_sum"]==pair(C)
    assert r["HOST_signed_encoding_residual"]==pair(E)and r["HOST_encoding_error_bound"]==pair(abs(E))
    assert r["status"]==("HOST_EXACT_REFERENCE_PAIR64_ONLY"if E==0 else"STOP_REFERENCE_ENCODING")
    return C,abs(E)

def verify(d):
    p,n,pins=retained();assert d["pins"]==pins and len(d["records"])==16
    seen=set();scenes=stops=admitted=sceneRN=0;values=[]
    for a in d["records"]:
        k=a["id"];assert k in p and k not in seen;seen.add(k)
        pq=p[k]["request"];q=a["request"];r=a["result"]
        expected=dict(model=c.MODEL,policy=c.POLICY,record_id=k,parent_receipt_sha256=PSHA,
            parent_record_sha256=digest(p[k]),producer_record_sha256=digest(n[k]),
            original_snapshot_sha256=pq["original_snapshot_sha256"],original_query_sha256=pq["original_query_sha256"],
            source="SOURCE0",detector="DETECTOR0",units="scene_length",
            reference_role="DECLARED_NOMINAL_STRAIGHT_CHORD_NOT_OPTICAL")
        assert q==expected and r["request_sha256"]==digest(q)and r["upstream_status"]==p[k]["result"]["status"]
        for f in("source_uncertainty_cancelled","correlation_assumed","wavelength_known","phase_certified","physical_reference_certified",
                 "scene_authenticated","scene_engine_admitted","GPU_used","Bpy_used"):assert r[f]is False
        for f in("new_native_products","new_native_sqrt","new_HOST_roots","retained_numeric_replays"):assert r[f]==0
        assert r["phase_error_bound"]is None and r["full_costs"]=="UNKNOWN_NOT_ZERO"
        assert r["promotion"]=="STOP_FULL_SCENE_PHASE_PHYSICAL_GPU_AND_FULL_COSTS"
        assert r["scope"]=="NEW_PARTIAL_NATIVE_CPU64_SIGNED_DIFFERENCE_HOST_REFERENCE_ENCODING_AND_BOUND"
        if p[k]["result"]["status"]!="HOST_DECLARED_NOMINAL_CHORD_DIFFERENCE_ONLY":
            assert r["status"]=="STOP_UPSTREAM"and r["reason"]=="sealed_STOP_not_rescued"
            assert r["diagnostic"]is None and r["RN_nodes_executed"]==r["HOST_float_conversions"]==r["HOST_word_formats"]==0
            stops+=1;continue
        old=p[k]["result"]["diagnostic"];env=n[k]["result"]["envelope"];z=r["diagnostic"]
        assert z["original_snapshot_sha256"]==q["original_snapshot_sha256"]==env["original_snapshot_sha256"]
        assert z["original_query_sha256"]==q["original_query_sha256"]==env["original_query_sha256"]
        assert(z["source"],z["detector"],z["units"],z["reference_role"])==("SOURCE0","DETECTOR0","scene_length",q["reference_role"])
        assert z["ALL15_original_radii"]==old["ALL15_original_radii"]
        assert z["reference_rounding_width"]==old["reference_rounding_width"]and z["width_operand_used"]is False
        assert z["reference_rounding_charged"]=="R_UPPER_AT_LOWER_AND_R_LOWER_AT_UPPER_NO_CANCELLATION"
        assert z["legacy_scalar_gate"]==env["legacy_scalar_gate"]and z["legacy_ABI_status"]==env["legacy_ABI_status"]
        assert z["HOST_reference_difference_interval"]==old["signed_difference_interval"]
        refs=z["reference_encoding"];assert len(refs)==2 and [x["rational"]for x in refs]==old["reference_root96"]
        for x in refs:assert encoding(x)[1]==0
        assert r["HOST_float_conversions"]==r["HOST_word_formats"]==4
        vv=[];assert len(z["subtractions"])==2
        for i,j in ((0,1),(1,0)):
            a=z["subtractions"][i];cert=env["certificates"][i]
            assert a["bound"]==("lower","upper")[i]and a["reference_endpoint"]==("lower","upper")[j]
            assert a["retained_length_certificate"]==cert
            v=a["consumer"];assert v["input_payload_hex"]==refs[j]["payload_hex"]+env["payload_hex"][32*i:32*i+32]
            assert val(v["inherited_bound"])==val(cert["retained_length_error_bound"])+encoding(refs[j])[1]
            lw=env["payload_hex"][32*i:32*i+32];L=pf(lw[:16])+pf(lw[16:]);B=val(cert["retained_length_error_bound"])
            S=val(cert["exact_squared"]);assert val(cert["retained_exact_pair_sum"])==L
            assert L-B>0 and(L-B)**2<=S<=(L+B)**2
            assert cert["retained_HOST_enclosure"]==[pair(L-B),pair(L+B)]
            vv.append(graph(v))
        assert r["RN_nodes_executed"]==sum(v["RN"]for v in vv)==52;sceneRN+=52;scenes+=1
        if any(v["kind"]!="EXACT"for v in vv):
            assert r["status"]=="STOP_NATIVE_DIFFERENCE"and z["native_difference_outer_interval"]is None
        else:
            lo,hi=vv[0]["C"]-vv[0]["T"],vv[1]["C"]+vv[1]["T"]
            d0,d1=map(val,old["signed_difference_interval"])
            if lo<=d0<=0<=d1<=hi:
                assert z["native_difference_outer_interval"]==[pair(lo),pair(hi)]
                assert r["status"]=="CPU64_SIGNED_DIFFERENCE_PAIR_HOST_BOUND_ONLY";admitted+=1
            else:
                # Unchanged fixed containment gate: exact ALU is not sufficient for admission.
                assert r["status"]=="STOP_INPUT"and r["reason"]=="HOST_reference_inside_native_outer_interval"
                assert z["native_difference_outer_interval"]is None
        values.append(dict(id=k,status=r["status"],pairs=[v["consumer"]["candidate_pair_words"]for v in z["subtractions"]],
            residuals=[str(v["E"])for v in vv],outer=[str(val(x))for x in z["native_difference_outer_interval"]]if z["native_difference_outer_interval"]else None))
    assert (scenes,stops)==(2,14)
    controls=[graph(x["result"])for x in d["controls"]]
    assert [v["kind"]for v in controls]==["EXACT","EXACT","EXACT","LOSS","ALU_STOP"]
    assert controls[0]["C"]==F(1,2**59)and controls[1]["C"]==-F(1,2**59)and controls[2]["C"]==0
    assert controls[3]["E"]==-F(1,2**120)and controls[4]["RN"]==1
    assert encoding(d["encoding_loss"])[1]==F(1,2**120)
    for x in d["invalid"]:
        assert x["result"]["status"]=="STOP_INPUT"and x["result"]["RN_nodes_executed"]==0
        assert x["result"]["HOST_float_conversions"]==0
    assert len(d["invalid"])==8
    for x in d["kernel_invalid"]:assert x["status"]=="STOP_INPUT"and x["RN_nodes_executed"]==0
    assert len(d["kernel_invalid"])==4
    return dict(scene_candidates=scenes,partial_native_admitted=admitted,upstream_STOP=stops,scene_RN=sceneRN,
        control_RN=sum(v["RN"]for v in controls),suite_total_RN=sceneRN+sum(v["RN"]for v in controls),
        scene_HOST_float_conversions=8,encoding_loss_HOST_float_conversions=2,invalid_selectors=8,kernel_invalid=4,
        new_roots=0,old_numeric_replays=0,phase_certified=False,full_costs="UNKNOWN_NOT_ZERO",values=values)

def mutations(d):
    i=next(i for i,x in enumerate(d["records"])if x["result"]["diagnostic"])
    changes=[
        lambda v:v["records"][i]["result"]["diagnostic"]["subtractions"][0]["consumer"]["ledger"][0].update(y="0000000000000000"),
        lambda v:v["records"][i]["result"]["diagnostic"]["subtractions"][0]["consumer"].update(HOST_total_difference_error_bound=[0,1]),
        lambda v:v["records"][i]["result"]["diagnostic"]["reference_encoding"][0].update(HOST_encoding_error_bound=[1,1]),
        lambda v:v["records"][i]["result"]["diagnostic"].update(ALL15_original_radii={}),
        lambda v:v["records"][i]["result"]["diagnostic"].update(width_operand_used=True),
        lambda v:v["records"][i]["result"].update(phase_certified=True),
        lambda v:v["records"][i]["result"]["diagnostic"].update(source="SOURCE1"),
        lambda v:v["controls"][3]["result"].update(status="CPU64_EXACT_PAIR_DIFFERENCE_ONLY")]
    for change in changes:
        bad=copy.deepcopy(d);change(bad)
        try:verify(bad)
        except(AssertionError,ValueError,KeyError,TypeError,IndexError):continue
        raise AssertionError("mutation_not_rejected")
    return len(changes)

def run():
    p,n,pins=c.retained();d=dict(pins=pins,records=[],invalid=[],controls=[],kernel_invalid=[])
    for k in p:
        q=c.selector(k,p,n);d["records"].append(dict(id=k,request=q,result=c._audit(q,p,n)))
    k=next(x["id"]for x in d["records"]if x["result"]["diagnostic"]);q=c.selector(k,p,n)
    for field,value in(("source","SOURCE1"),("units","radian"),("reference_role","PHYSICAL_OPTICAL"),
        ("original_snapshot_sha256","0"*64),("policy","WIDTH"),("record_id","missing"),("parent_receipt_sha256","0"*64),("wavelength","1")):
        bad=dict(q);bad[field]=value;d["invalid"].append(dict(request=bad,result=c._audit(bad,p,n)))
    def words(v):return "".join(struct.pack("<d",float(x)).hex()for x in v)
    for name,a,b in(("positive",(F(1),F(1,2**59)),(F(1),F(0))),
        ("negative",(F(1),F(0)),(F(1),F(1,2**59))),("zero",(F(1),F(0)),(F(1),F(0))),
        ("loss",(F(1),F(1,2**59)),(F(0),F(1,2**120)))):
        payload=words(b)+words(a);d["controls"].append(dict(name=name,result=c.difference(payload,[0,1])))
    payload="0000000000001000"+"0000000000000000"+"0100000000001000"+"0000000000000000"
    d["controls"].append(dict(name="underflow",result=c.difference(payload,[0,1])))
    d["encoding_loss"]=c.encode_reference(pair(F(1)+F(1,2**59)+F(1,2**120)))
    for payload,B in(("bad",[0,1]),("g"*64,[0,1]),("000000000000f07f"+"0"*48,[0,1]),("0"*64,[-1,1])):
        d["kernel_invalid"].append(c.difference(payload,B))
    summary=verify(d);summary["mutations_rejected"]=mutations(d)
    api=[]
    for name in("selector","missing_parent","drift_sha"):
        if name=="selector":a=c.audit(dict(q,source="SOURCE1"))
        else:
            with patch.object(c,"retained",side_effect=OSError(name)):a=c.audit(q)
        assert a["status"]=="STOP_INPUT"and a["RN_nodes_executed"]==a["HOST_float_conversions"]==0
        api.append(dict(name=name,status=a["status"],reason=a["reason"]))
    print(json.dumps(dict(status="PASS",summary=summary,evidence=d,api_negative=api),sort_keys=True))

if __name__=="__main__":run()
