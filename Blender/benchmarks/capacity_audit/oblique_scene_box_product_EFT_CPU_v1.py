"""Opt-in native CPU64 Dekker products of sealed scene-box HOST endpoints.
Partial primitive only: no native accumulation, norm, root, length or phase.
"""
from pathlib import Path
from fractions import Fraction as F
import json,math,struct
import oblique_pair64_length_reference_HOST_v1 as ref
ROOT=Path(__file__).resolve().parents[3]
MODEL="oblique-scene-box-product-EFT-CPU64-v1"
POLICY="SEALED_ORIGINAL_ALL_RADII_HOST_ENDPOINTS_PRODUCTS_ONLY"
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-PAIR64-LENGTH-REFERENCE-HOST-001-CODEX.json"
PSHA="2dc30d8b5762a179a4d40093ae5a47adcccce9507879c1a715725334e9f40eec"
require,sha,capture,digest=ref.require,ref.sha,ref.capture,ref.digest
SPLITTER=134217729.0
MIN_NORMAL=2.0**-1022
MAX_OPERAND=2.0**32

def pair(x):return [x.numerator,x.denominator]
def word(x):return struct.pack("<d",x).hex()
def exact(x):return F.from_float(x)
def normal(x):return type(x)is float and math.isfinite(x)and(x==0.0 or abs(x)>=MIN_NORMAL)

def product(a,b):
    out=dict(status="STOP_INPUT",reason=None,a_word=None,b_word=None,ledger=[],hi_word=None,lo_word=None)
    try:
        require(normal(a)and normal(b)and abs(a)<=MAX_OPERAND and abs(b)<=MAX_OPERAND,"operand_domain")
        out.update(a_word=word(a),b_word=word(b))
        def rn(name,op,x,y):
            z=x*y if op=="*" else x-y
            v=exact(x)*exact(y)if op=="*"else exact(x)-exact(y)
            out["ledger"].append(dict(index=len(out["ledger"]),name=name,op=op,a=word(x),b=word(y),y=word(z)))
            require(normal(z)and(z!=0.0 or v==0),"node_domain:"+name)
            return z
        ca=rn("ca","*",SPLITTER,a);abig=rn("abig","-",ca,a)
        ah=rn("ah","-",ca,abig);al=rn("al","-",a,ah)
        cb=rn("cb","*",SPLITTER,b);bbig=rn("bbig","-",cb,b)
        bh=rn("bh","-",cb,bbig);bl=rn("bl","-",b,bh)
        p=rn("p","*",a,b)
        hh=rn("hh","*",ah,bh);e1=rn("e1","-",p,hh)
        lh=rn("lh","*",al,bh);e2=rn("e2","-",e1,lh)
        hl=rn("hl","*",ah,bl);e3=rn("e3","-",e2,hl)
        ll=rn("ll","*",al,bl);err=rn("err","-",ll,e3)
        require(len(out["ledger"])==17 and exact(p)+exact(err)==exact(a)*exact(b),"EFT_identity")
        out.update(status="CPU64_EFT_PRODUCT_ONLY",reason="native17RN_exact_pair",hi_word=word(p),lo_word=word(err))
    except(ValueError,TypeError,OverflowError)as ex:out["reason"]=str(ex)
    out["RN_nodes_executed"]=len(out["ledger"])
    return out

def encode(v):
    """HOST exact preprocessing. NOT native paired subtraction or scene inference."""
    out=dict(status="STOP_INPUT",reason=None,exact=None,hi_word=None,lo_word=None,HOST_float_casts=0)
    try:
        require(type(v)is F and abs(v)<=F(2**32),"endpoint_domain")
        out["exact"]=pair(v)
        h=float(v);out["HOST_float_casts"]+=1
        l=float(v-exact(h));out["HOST_float_casts"]+=1
        out.update(hi_word=word(h),lo_word=word(l))
        require(normal(h)and normal(l)and exact(h)+exact(l)==v,"endpoint_two_limb_exactness")
        out.update(status="HOST_EXACT_TWO_LIMB_INPUT_ONLY",reason="HOST_residual_encoding_not_native")
    except(ValueError,TypeError,OverflowError)as ex:out["reason"]=str(ex)
    return out

def retained():
    raw=(ROOT/PARENT).read_bytes();require(len(raw)==252843 and sha(raw)==PSHA,"parent_seal")
    r=json.loads(raw);pins=dict(r["code_doc_sha256"]);require(len(pins)==272,"parent_pins")
    for p,h in pins.items():require(sha((ROOT/p).read_bytes())==h,"dependency:"+p)
    require(capture(r["independent_pre"])["status"]=="PASS","parent_oracle")
    d=capture(r["test_run"])["evidence"];e={x["id"]:x for x in d["records"]}
    _,orig,_=ref.retained();require(set(e)==set(orig)and len(e)==16,"closed_records")
    pins[PARENT]=PSHA
    return e,orig,pins

def selector(k,e,orig):
    return dict(backend=MODEL,policy=POLICY,record_id=k,parent_receipt_sha256=PSHA,
        parent_record_sha256=digest(e[k]),original_record_sha256=digest(orig[k]),
        original_snapshot_sha256=digest(orig[k]["scene"]))

def baseline():
    return dict(backend=MODEL,status="STOP_INPUT",reason=None,endpoints=[],products=[],
        HOST_float_casts=0,RN_nodes_executed=0,native_accumulation=False,native_norm=None,
        native_root=None,native_length=None,phase_certified=False,GPU_used=False,
        source_uncertainty_cancelled=False,physical_visibility_certified=False,
        new_transport_calls=0,new_predicate_calls=0,new_root_calls=0,retained_suite_replays=0,
        endpoint_preparation="HOST_EXACT_ORIGINAL_BOX_NOT_NATIVE_SUBTRACTION",
        full_costs="UNKNOWN_NOT_ZERO",promotion="STOP_LENGTH_PHASE_PHYSICAL_GPU")

def _audit(q,e,orig):
    out=baseline()
    try:
        require(type(q)is dict and type(q.get("record_id"))is str and q["record_id"]in e,"closed_record")
        k=q["record_id"];require(q==selector(k,e,orig)and all(type(v)is str for v in q.values()),"closed_selector")
        x,o=e[k],orig[k];r=x["result"];out.update(request_sha256=digest(q),upstream_status=r["status"])
        if r["status"]!="HOST_SAME_ORIGINAL_BOX_REFERENCE_ONLY":
            out.update(status="STOP_UPSTREAM",reason="sealed_STOP_not_rescued");return out
        z=r["diagnostic"];require(z["original_scene"]==o["scene"]and z["original_query"]==o["scene_query"]
            and z["original_snapshot_sha256"]==digest(o["scene"]),"original_scene_binding")
        boxes=ref.host.validate(o["scene"],o["scene_query"])
        delta=[[pair(b[0]-a[1]),pair(b[1]-a[0])]for a,b in zip(boxes["origin"],boxes["detector"])]
        require(delta==z["extrema"]["delta"]and delta==z["shifted_extrema"]["delta"],"same_original_delta")
        # Validate all six HOST encodings before launching ANY native graph.
        for axis,iv in enumerate(delta):
            for side,pv in enumerate(iv):
                v=encode(F(*pv));out["endpoints"].append(dict(axis=axis,side=side,encoding=v))
                out["HOST_float_casts"]+=v["HOST_float_casts"]
                require(v["status"]=="HOST_EXACT_TWO_LIMB_INPUT_ONLY","endpoint_encoding_STOP")
        for ep in out["endpoints"]:
            enc=ep["encoding"];h,l=(struct.unpack("<d",bytes.fromhex(enc[n]))[0]for n in ("hi_word","lo_word"))
            terms=[]
            out["products"].append(dict(axis=ep["axis"],side=ep["side"],terms=terms))
            for name,a,b in (("hh",h,h),("hl",h,l),("lh",l,h),("ll",l,l)):
                p=product(a,b);terms.append(dict(term=name,result=p));out["RN_nodes_executed"]+=p["RN_nodes_executed"]
                require(p["status"]=="CPU64_EFT_PRODUCT_ONLY","product_STOP:"+str(p["reason"]))
        out.update(status="CPU64_ORIGINAL_BOX_PRODUCTS_ONLY",reason="all24_EFT_products_exact_NO_native_norm")
    except(ValueError,TypeError,KeyError,IndexError,OSError)as ex:out["reason"]=str(ex)
    return out

def audit(q):
    try:e,orig,_=retained()
    except(ValueError,TypeError,KeyError,OSError)as ex:
        out=baseline();out["reason"]="evidence_integrity:"+str(ex);return out
    return _audit(q,e,orig)
