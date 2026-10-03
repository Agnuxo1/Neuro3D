"""Independent bit/rational verifier of the native17RN graph, no native replay."""
from pathlib import Path
from fractions import Fraction as F
import json,hashlib,copy,runpy
ROOT=Path(__file__).resolve().parents[2]
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-PAIR64-LENGTH-REFERENCE-HOST-001-CODEX.json"
PSHA="2dc30d8b5762a179a4d40093ae5a47adcccce9507879c1a715725334e9f40eec"
prior=runpy.run_path(str(ROOT/"Blender/tests/test_oblique_pair64_length_reference_HOST.py"))
capture,digest,pair,frac=map(prior.get,("capture","digest","pair","frac"))
MODEL="oblique-scene-box-product-EFT-CPU64-v1"
POLICY="SEALED_ORIGINAL_ALL_RADII_HOST_ENDPOINTS_PRODUCTS_ONLY"

def retained():
    raw=(ROOT/PARENT).read_bytes();assert len(raw)==252843 and hashlib.sha256(raw).hexdigest()==PSHA
    r=json.loads(raw);pins=dict(r["code_doc_sha256"]);assert len(pins)==272;pins[PARENT]=PSHA
    for p,h in pins.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    d=capture(r["test_run"])["evidence"];_,_,orig,_,_=prior["retained"]()
    return {x["id"]:x for x in d["records"]},orig,pins,d

def selector(k,e,orig):
    return dict(backend=MODEL,policy=POLICY,record_id=k,parent_receipt_sha256=PSHA,
        parent_record_sha256=digest(e[k]),original_record_sha256=digest(orig[k]),original_snapshot_sha256=digest(orig[k]["scene"]))

def bits(w):return int.from_bytes(bytes.fromhex(w),"little")
def adjacent(w,up):
    u=bits(w)
    if u&0x7fffffffffffffff==0:return (1 if up else 0x8000000000000001).to_bytes(8,"little").hex()
    u+=1 if (up==(u>>63==0))else -1
    return u.to_bytes(8,"little").hex()
def pf(w):
    # Independent bit decomposition, permit subnormal for RN-neighbour proof ONLY.
    u=bits(w);s=-1 if u>>63 else 1;m=u&((1<<52)-1);e=(u>>52)&2047
    assert e!=2047
    if e:m|=1<<52;e=e-1023-52
    else:e=-1074
    return s*F(m)*(F(2)**e)
def nearest(w,v):
    y=pf(w);a=pf(adjacent(w,False));b=pf(adjacent(w,True))
    lo,hi=(a+y)/2,(b+y)/2
    assert lo<=v<=hi and (lo<v<hi or bits(w)%2==0)
    return y

def graph(p,expected_a=None,expected_b=None):
    assert p["RN_nodes_executed"]==len(p["ledger"])
    if p["a_word"]is None:
        assert p["status"]=="STOP_INPUT"and p["reason"]=="operand_domain"and not p["ledger"]
        return 0
    aa,bb=pf(p["a_word"]),pf(p["b_word"])
    if expected_a is not None:assert(aa,bb)==(expected_a,expected_b)
    vals={"a":aa,"b":bb,"split":F(134217729)}
    spec=(("ca","*","split","a"),("abig","-","ca","a"),("ah","-","ca","abig"),("al","-","a","ah"),
          ("cb","*","split","b"),("bbig","-","cb","b"),("bh","-","cb","bbig"),("bl","-","b","bh"),
          ("p","*","a","b"),("hh","*","ah","bh"),("e1","-","p","hh"),("lh","*","al","bh"),
          ("e2","-","e1","lh"),("hl","*","ah","bl"),("e3","-","e2","hl"),("ll","*","al","bl"),("err","-","ll","e3"))
    assert len(p["ledger"])<=17
    for i,n in enumerate(p["ledger"]):
        name,op,x,y=spec[i];a,b=vals[x],vals[y]
        assert n["index"]==i and(n["name"],n["op"])==(name,op)and(pf(n["a"]),pf(n["b"]))==(a,b)
        v=a*b if op=="*"else a-b
        vals[name]=nearest(n["y"],v)
    if p["status"]=="CPU64_EFT_PRODUCT_ONLY":
        assert len(p["ledger"])==17 and p["reason"]=="native17RN_exact_pair"
        assert p["hi_word"]==p["ledger"][8]["y"]and p["lo_word"]==p["ledger"][16]["y"]
        assert pf(p["hi_word"])+pf(p["lo_word"])==aa*bb
    else:
        assert p["status"]=="STOP_INPUT"and p["reason"].startswith("node_domain:")
        assert p["hi_word"]is None and p["lo_word"]is None
        n=p["ledger"][-1];v=pf(n["a"])*pf(n["b"])if n["op"]=="*"else pf(n["a"])-pf(n["b"])
        assert (pf(n["y"])==0 and v!=0)or 0<abs(pf(n["y"]))<F(2)**-1022
    return len(p["ledger"])

def scope(r):
    assert r["backend"]==MODEL and r["full_costs"]=="UNKNOWN_NOT_ZERO"and r["promotion"]=="STOP_LENGTH_PHASE_PHYSICAL_GPU"
    assert r["endpoint_preparation"]=="HOST_EXACT_ORIGINAL_BOX_NOT_NATIVE_SUBTRACTION"
    for key in ("native_accumulation","phase_certified","GPU_used","source_uncertainty_cancelled","physical_visibility_certified"):assert r[key]is False
    for key in ("native_norm","native_root","native_length"):assert r[key]is None
    for key in ("new_transport_calls","new_predicate_calls","new_root_calls","retained_suite_replays"):assert r[key]==0

def verify_capture(d):
    e,orig,pins,old=retained();assert d["pins"]==pins and prior["verify_capture"](old)["status"]=="PASS"
    assert len(d["records"])==16 and {x["id"]for x in d["records"]}==set(e)
    total=casts=good=stops=low_squares=0
    for x in d["records"]:
        k=x["id"];r=x["result"];scope(r);assert x["request"]==selector(k,e,orig)
        assert r["request_sha256"]==digest(x["request"])and r["upstream_status"]==e[k]["result"]["status"]
        if e[k]["result"]["status"]!="HOST_SAME_ORIGINAL_BOX_REFERENCE_ONLY":
            assert r["status"]=="STOP_UPSTREAM"and r["reason"]=="sealed_STOP_not_rescued"
            assert not r["endpoints"]and not r["products"]and r["HOST_float_casts"]==r["RN_nodes_executed"]==0
            stops+=1;continue
        assert r["status"]=="CPU64_ORIGINAL_BOX_PRODUCTS_ONLY"and r["reason"]=="all24_EFT_products_exact_NO_native_norm"
        s=orig[k]["scene"];box={}
        for n in ("origin","detector"):
            box[n]=[(F(*v)-F(*rad),F(*v)+F(*rad))for v,rad in zip(s["points"][n]["nominal"],s["points"][n]["radius"])]
        delta=[(b[0]-a[1],b[1]-a[0])for a,b in zip(box["origin"],box["detector"])]
        assert len(r["endpoints"])==len(r["products"])==6
        for i,(ep,pp)in enumerate(zip(r["endpoints"],r["products"])):
            ax,side=divmod(i,2);v=delta[ax][side];enc=ep["encoding"]
            assert(ep["axis"],ep["side"],pp["axis"],pp["side"])==(ax,side,ax,side)
            assert enc["exact"]==pair(v)and enc["status"]=="HOST_EXACT_TWO_LIMB_INPUT_ONLY"and enc["HOST_float_casts"]==2
            h=nearest(enc["hi_word"],v);l=nearest(enc["lo_word"],v-h);assert h+l==v
            assert [z["term"]for z in pp["terms"]]==["hh","hl","lh","ll"]
            expected=[(h,h),(h,l),(l,h),(l,l)];value=F(0)
            for z,(a,b)in zip(pp["terms"],expected):
                p=z["result"];total+=graph(p,a,b);value+=pf(p["hi_word"])+pf(p["lo_word"])
            assert value==v*v # HOST diagnostic sum ONLY, never a native norm.
            if l*l==F(2)**-130:low_squares+=1
        assert r["RN_nodes_executed"]==408 and r["HOST_float_casts"]==12
        casts+=12;good+=1
    assert(good,stops,total,casts)==(2,14,816,24)and low_squares>=2
    assert len(d["invalid"])==8
    for x in d["invalid"]:
        r=x["result"];scope(r);assert r["status"]=="STOP_INPUT"and r["reason"]=="closed_selector"
        assert not r["endpoints"]and not r["products"]and r["HOST_float_casts"]==r["RN_nodes_executed"]==0
    controls=d["controls"];assert len(controls)==6
    expected=[(F(1)+F(2)**-27,F(1)-F(2)**-27),(F(-3,2),F(5,4)),(F(0),F(2)),None,None,(F(2)**-600,F(2)**-600)]
    cn=0
    for z,v in zip(controls,expected):cn+=graph(z["result"],*(v or (None,None)))
    first=controls[0]["result"];assert pf(first["hi_word"])!=expected[0][0]*expected[0][1]and pf(first["lo_word"])==-(F(2)**-54)
    assert [z["result"]["status"]for z in controls]==["CPU64_EFT_PRODUCT_ONLY"]*3+["STOP_INPUT"]*3
    fail=d["encoding_failure"];assert fail["status"]=="STOP_INPUT"and fail["reason"]=="endpoint_two_limb_exactness"
    assert F(*fail["exact"])==F(1)+F(2)**-60+F(2)**-120
    return dict(status="PASS",scenes=good,upstream_STOP=stops,invalid=8,scene_products=48,
        scene_RN_nodes=total,HOST_casts=casts,helper_RN_nodes=cn,helpers=6,encoding_STOP=1,low_squares_2pow_minus130=low_squares,
        inherited_pins=len(pins),native_norm=False,phase=False,GPU=False)

def mutations(d):
    checks=[]
    for name in ("lost_residual","wrong_node","wrong_original_endpoint","cancel_SOURCE_radius","fake_norm","fake_phase","STOP_rescue","bad_parent_pin"):
        m=copy.deepcopy(d);r=next(x["result"]for x in m["records"]if x["result"]["status"]=="CPU64_ORIGINAL_BOX_PRODUCTS_ONLY")
        if name=="lost_residual":m["controls"][0]["result"]["lo_word"]="0000000000000000"
        elif name=="wrong_node":r["products"][0]["terms"][0]["result"]["ledger"][0]["op"]="-"
        elif name=="wrong_original_endpoint":r["endpoints"][0]["encoding"]["exact"]=[0,1]
        elif name=="cancel_SOURCE_radius":r["source_uncertainty_cancelled"]=True
        elif name=="fake_norm":r["native_norm"]=[1,1]
        elif name=="fake_phase":r["phase_certified"]=True
        elif name=="STOP_rescue":next(x["result"]for x in m["records"]if x["result"]["status"]=="STOP_UPSTREAM")["status"]="CPU64_ORIGINAL_BOX_PRODUCTS_ONLY"
        else:m["pins"][PARENT]="0"*64
        try:verify_capture(m)
        except(AssertionError,ValueError,KeyError):checks.append(name)
        else:raise AssertionError("mutation_not_rejected:"+name)
    return checks

def run():
    import oblique_scene_box_product_EFT_CPU_v1 as backend
    e,orig,pins=backend.retained();records=[]
    for k in e:
        q=backend.selector(k,e,orig);records.append(dict(id=k,request=q,result=backend._audit(q,e,orig)))
    k=next(k for k in e if e[k]["result"]["status"]=="HOST_SAME_ORIGINAL_BOX_REFERENCE_ONLY")
    invalid=[]
    for name in ("backend","policy","parent_receipt_sha256","parent_record_sha256","original_record_sha256","original_snapshot_sha256","extra","record_id"):
        q=backend.selector(k,e,orig)
        if name=="extra":q["extra"]="wrong"
        elif name=="record_id":q[name]=next(k for k in e if k!=q[name]) # valid id with mismatched seals
        else:q[name]="wrong"
        invalid.append(dict(id=name,request=q,result=backend._audit(q,e,orig)))
    operands=[(1.0+2.0**-27,1.0-2.0**-27),(-1.5,1.25),(0.0,2.0),(2.0**33,1.0),(float("inf"),1.0),(2.0**-600,2.0**-600)]
    controls=[dict(id=str(i),result=backend.product(a,b))for i,(a,b)in enumerate(operands)]
    d=dict(pins=pins,records=records,invalid=invalid,controls=controls,encoding_failure=backend.encode(F(1)+F(2)**-60+F(2)**-120))
    summary=verify_capture(d);summary["mutations_rejected"]=mutations(d)
    print(json.dumps(dict(evidence=d,summary=summary),sort_keys=True,separators=(",",":")))

if __name__=="__main__":run()
