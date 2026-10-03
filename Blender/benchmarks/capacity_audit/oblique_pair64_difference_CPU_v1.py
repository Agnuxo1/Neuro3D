"""Opt-in native CPU binary64 difference of sealed oblique SOURCE pairs only."""
import base64,hashlib,json,math,struct,zlib
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
MODEL="precision-oblique-pair64-difference-CPU-v1"
REP="OBLIQUE_PAIR64_DIFFERENCE_CPU_NOT_GPU_ABI"
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-CYCLES-PAIR64-CPU-001-CODEX.json"
PSHA="af247e1dde579952adc02eddac33a31d2a19d5a51d009d397c89da95ab7a5748"
KEYS={"case","parent_result_sha256","original_scene_sha256","literal_request_sha256","representation"}
FLAGS=("GPU_executed","native_promotion_allowed","physical_scene_authenticated","native_hit_coverage_certified",
 "length_reference_phase_bound_certified","mirror_material_certified","full_field_certified",
 "coherent_field_admission_allowed","interference_phase_certified")
def require(ok,why):
    if not ok:raise ValueError(why)
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode())
def pair(x):return [x.numerator,x.denominator]
def exact(x):return F.from_float(x)
def word(x):return struct.pack("<d",x).hex()
def scalar(w):
    require(type(w)is str and len(w)==16 and bytes.fromhex(w).hex()==w,"canonical_word")
    x=struct.unpack("<d",bytes.fromhex(w))[0]
    require(math.isfinite(x) and abs(x)<=2**40,"new_CPU_arithmetic_domain")
    return x
def retained():
    raw=(ROOT/PARENT).read_bytes();require(sha(raw)==PSHA,"parent_identity")
    r=json.loads(raw);require(len(r["code_doc_sha256"])==88,"parent_pins")
    for p,h in r["code_doc_sha256"].items():require(sha((ROOT/p).read_bytes())==h,"dependency:"+p)
    t=r["test_run"];require(t["rc"]==0 and t["timed_out"]is False,"parent_PASS")
    z=zlib.decompressobj();raw=z.decompress(base64.b64decode(t["stdout_zlib_base64"],validate=True),1024*1024+1)
    require(len(raw)<=1024*1024 and z.eof and not z.unused_data and not z.unconsumed_tail,"closed_capture")
    require(len(raw)==t["stdout_bytes"] and sha(raw)==t["stdout_sha256"],"capture_identity")
    v=json.loads(raw);require(v["status"]=="PASS" and v["tests"]==6,"specific_suite");return v["data"]
def selector(case="parent_oblique"):
    d=retained();v=d["results"][case]
    return dict(case=case,parent_result_sha256=digest(v),original_scene_sha256=v.get("rows",[{}])[0].get("original_scene_sha256","") if v["rows"] else "",
        literal_request_sha256=v["rows"][0]["literal_request_sha256"] if v["rows"] else "",representation=REP)
def rounded(a,b,op,name,trace):
    require(type(a)is float and type(b)is float and op in ("+","-"),"typed_RN_operands")
    y=a+b if op=="+" else a-b
    require(math.isfinite(y),"finite_native_result")
    target=exact(a)+exact(b) if op=="+" else exact(a)-exact(b)
    trace["nodes"].append(dict(name=name,op=op,a=word(a),b=word(b),y=word(y),error=pair(abs(exact(y)-target))))
    return y
def two_sum(a,b,name,trace):
    s=rounded(a,b,"+",name+"_s",trace)
    bb=rounded(s,a,"-",name+"_bb",trace)
    ab=rounded(s,bb,"-",name+"_ab",trace)
    db=rounded(b,bb,"-",name+"_db",trace)
    da=rounded(a,ab,"-",name+"_da",trace)
    e=rounded(da,db,"+",name+"_e",trace)
    ok=exact(s)+exact(e)==exact(a)+exact(b)
    trace["eft"].append(dict(name=name,a=word(a),b=word(b),hi=word(s),lo=word(e),residual_exact=ok))
    require(ok,"measured_EFT_identity")
    return s,e
def native_difference(a,b,trace):
    require(type(a)is tuple and type(b)is tuple and len(a)==len(b)==2,"typed_pair")
    require(all(type(x)is float and math.isfinite(x) and abs(x)<=2**40 for x in a+b),"bounded_native_pairs")
    # Unary sign flip is exact binary64, not an extra rounded arithmetic node.
    s,e=two_sum(a[0],-b[0],"h",trace)
    t,f=two_sum(a[1],-b[1],"l",trace)
    e=rounded(e,t,"+","e_add",trace)
    h,g=two_sum(s,e,"m",trace)
    l=rounded(g,f,"+","lo_add",trace)
    return two_sum(h,l,"r",trace)
def transport(q,*,model):
    out=dict(model=MODEL,representation=REP,status="STOP",reason=None,rows=[],diagnostics=[],trace={"nodes":[],"eft":[]},
        RN64_operations=0,frozen_producer_replays=0,new_geometry_queries=0,new_sqrt_calls=0,
        source_phase=None,mirror_phase=None,amplitude=None,field=None,power=None,full_costs="UNMEASURED_NOT_ZERO")
    out.update({k:False for k in FLAGS})
    try:
        require(type(model)is str and model==MODEL,"explicit_model")
        require(type(q)is dict and set(q)==KEYS and all(type(x)is str for x in q.values()),"closed_selector")
        require(q["representation"]==REP,"new_representation")
        d=retained();require(q["case"]in d["results"],"case_identity");v=d["results"][q["case"]]
        require(q["parent_result_sha256"]==digest(v),"result_identity")
        require(v["status"]=="CPU_OBLIQUE_PAIR64_GEOMETRIC_TRANSPORT_ONLY","parent_STOP_no_arithmetic")
        require(all(v[k]is False for k in FLAGS) and len(v["rows"])==3,"ALL_sources_scope")
        sources=v["rows"][:2];ref=v["rows"][2]
        require([s["record_id"] for s in sources]==["S0","S1"] and ref["record_id"]=="S0-minus-S1","SOURCE_order")
        require(all(s["original_scene_sha256"]==q["original_scene_sha256"] and s["literal_request_sha256"]==q["literal_request_sha256"] for s in v["rows"]),"scene_literal_identity")
        bounds=[tuple(F(*p) for p in s["interval"]) for s in v["rows"]]
        require(bounds[2]==(bounds[0][0]-bounds[1][1],bounds[0][1]-bounds[1][0]),"relative_interval")
        caps=[F(*s["literal_cap_rad"]) for s in v["rows"]]
        require(all(c>=0 for c in caps),"literal_caps")
        values=[(scalar(s["hi"]["word_le_hex"]),scalar(s["lo"]["word_le_hex"])) for s in sources]
        source_values=[exact(a)+exact(b) for a,b in values]
        source_bounds=[max(abs(y-a),abs(y-b)) for y,(a,b) in zip(source_values,bounds[:2])]
        require(all(8*e<=c for e,c in zip(source_bounds,caps[:2])),"ALL_SOURCE_caps")
        h,l=native_difference(*values,out["trace"]);y=exact(h)+exact(l)
        target=source_values[0]-source_values[1];arithmetic=abs(y-target)
        midpoints=[(a+b)/2 for a,b in bounds[:2]]
        source_rounding=sum(abs(x-m) for x,m in zip(source_values,midpoints))
        radius=(bounds[2][1]-bounds[2][0])/2
        conservative=radius+source_rounding+arithmetic
        direct=max(abs(y-bounds[2][0]),abs(y-bounds[2][1]))
        require(direct<=conservative,"triangle_budget")
        diagnostic=dict(record_id="S0-minus-S1",branch_id="relative",hi_word=word(h),lo_word=word(l),
            pair_value=pair(y),input_pair_difference=pair(target),arithmetic_error_cycles=pair(arithmetic),
            source_rounding_budget_cycles=pair(source_rounding),interval_radius_cycles=pair(radius),
            conservative_error_bound_rad=pair(8*conservative),direct_error_bound_rad=pair(8*direct),
            literal_cap_rad=pair(caps[2]),parent_relative_CONTROL_ONLY=ref,
            original_scene_sha256=q["original_scene_sha256"],literal_request_sha256=q["literal_request_sha256"])
        out["diagnostics"]=[diagnostic]
        nodes=out["trace"]["nodes"]
        require(len(nodes)==26 and word(h)==nodes[-6]["y"] and word(l)==nodes[-1]["y"],"arithmetic_output_identity")
        require(8*conservative<=caps[2],"relative_literal_cap")
        out.update(status="CPU_OBLIQUE_PAIR64_DIFFERENCE_ONLY",rows=sources+[diagnostic],request_sha256=digest(q),parent_receipt_sha256=PSHA)
    except (ValueError,TypeError,KeyError,OSError,zlib.error) as e:out["reason"]=str(e)
    finally:out["RN64_operations"]=len(out["trace"]["nodes"])
    return out
