"""Opt-in midpoint-to-two-IEEE64 transport of retained oblique geometric cycles only."""
from fractions import Fraction as F
from pathlib import Path
import base64,hashlib,json,math,struct,zlib
ROOT=Path(__file__).resolve().parents[3]
MODEL="precision-oblique-cycles-pair64-CPU-v1"
REP="OBLIQUE_GEOMETRIC_CYCLES_PAIR64_CPU_NOT_GPU_ABI"
PARENT="coordinacion/respuestas/PRECISION-OBLIQUE-COMMON-DETECTOR-LENGTH-CPU-001-CODEX.json"
PARENT_SHA="139cb34a315f476fa026bb346086a3a59d7c22241932ca3f4c291a501f4ca47e"
KEYS={"case","parent_result_sha256","original_scene_sha256","literal_request_sha256","representation"}
FLAGS=("GPU_executed","native_promotion_allowed","physical_scene_authenticated","native_hit_coverage_certified",
       "length_reference_phase_bound_certified","mirror_material_certified","full_field_certified",
       "coherent_field_admission_allowed","interference_phase_certified")

def require(ok,why):
    if not ok:raise ValueError(why)
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode())
def pair(x):return [x.numerator,x.denominator]
def retained():
    raw=(ROOT/PARENT).read_bytes();require(sha(raw)==PARENT_SHA,"parent_identity")
    r=json.loads(raw);pins=r["code_doc_sha256"];require(len(pins)==83,"parent_pins")
    for p,h in pins.items():require(sha((ROOT/p).read_bytes())==h,"dependency:"+p)
    t=r["test_run"];require(t["rc"]==0 and t["timed_out"]is False,"parent_PASS")
    z=zlib.decompressobj();raw=z.decompress(base64.b64decode(t["stdout_zlib_base64"],validate=True),1024*1024+1)
    require(len(raw)<=1024*1024 and z.eof and not z.unused_data and not z.unconsumed_tail,"closed_capture")
    require(len(raw)==t["stdout_bytes"] and sha(raw)==t["stdout_sha256"],"capture_identity")
    v=json.loads(raw);require(v["status"]=="PASS" and v["tests"]==6,"specific_parent_suite");return v["data"]
def selector(case="oblique"):
    d=retained();i=d["inputs"][case];v=d["results"][case]
    return {"case":case,"parent_result_sha256":digest(v),"original_scene_sha256":digest(i["scene"]),
            "literal_request_sha256":digest(i["request"]),"representation":REP}
def rn64(x):
    require(type(x)is F,"rational_RN_input")
    try:y=float(x)
    except OverflowError as e:raise ValueError("RN64_overflow") from e
    require(math.isfinite(y),"finite_RN64")
    f=F.from_float(y)
    return {"input":pair(x),"word_le_hex":struct.pack("<d",y).hex(),"decoded":pair(f),"error":pair(abs(f-x))}
def encode_interval(bounds):
    require(type(bounds)is tuple and len(bounds)==2 and all(type(x)is F for x in bounds) and bounds[0]<=bounds[1],"typed_interval")
    a,b=bounds;mid=(a+b)/2;radius=(b-a)/2
    hi=rn64(mid);h=F(*hi["decoded"]);residual=mid-h;lo=rn64(residual);l=F(*lo["decoded"])
    y=h+l;rounding=abs(mid-y)
    require(rounding==F(*lo["error"]),"firstcast_error_cancels_exact_residual")
    bound=max(abs(y-a),abs(y-b));require(bound==radius+rounding,"interval_plus_secondcast_budget")
    single=max(abs(h-a),abs(h-b))
    return {"interval":[pair(a),pair(b)],"midpoint":pair(mid),"interval_radius":pair(radius),
        "hi":hi,"exact_residual":pair(residual),"lo":lo,"pair_value":pair(y),"pair_rounding_error":pair(rounding),
        "pair_error_bound_cycles":pair(bound),"pair_error_bound_rad":pair(8*bound),
        "single_word_error_bound_rad":pair(8*single),"RN64_casts":2}
def transport(q,*,model):
    out={"model":MODEL,"representation":REP,"status":"STOP","reason":None,"rows":[],"diagnostics":[],
         "RN64_casts":0,"new_geometry_queries":0,"new_sqrt_calls":0,"frozen_producer_replays":0,
         "source_phase":None,"mirror_phase":None,"amplitude":None,"field":None,"power":None,
         "full_costs":"UNMEASURED_NOT_ZERO"}
    out.update({k:False for k in FLAGS})
    try:
        require(type(model)is str and model==MODEL,"explicit_model")
        require(type(q)is dict and set(q)==KEYS and all(type(x)is str for x in q.values()),"closed_selector")
        require(q["representation"]==REP,"explicit_new_representation")
        d=retained();require(q["case"]in d["results"],"case_identity");i=d["inputs"][q["case"]];v=d["results"][q["case"]]
        require(q["parent_result_sha256"]==digest(v) and q["original_scene_sha256"]==digest(i["scene"])
                and q["literal_request_sha256"]==digest(i["request"]),"complete_binding")
        require(v["status"]=="CPU_OBLIQUE_GEOMETRIC_LENGTH_INTERVAL_ONLY","retained_STOP_no_RN")
        require(v["original_scene_sha256"]==q["original_scene_sha256"] and v["literal_request_sha256"]==q["literal_request_sha256"]
                and all(v[k]is False for k in FLAGS),"retained_partial_scope")
        require(v["phase_scope"]=="GEOMETRIC_PATH_CYCLES_ONLY_NO_MATERIAL"
                and [p["source_id"] for p in v["paths"]]==["S0","S1"],"ALL_geometric_sources")
        bounds=[tuple(F(*x) for x in p["geometric_cycles_interval"]) for p in v["paths"]]
        bounds.append(tuple(F(*x) for x in v["relative_diagnostic"]["geometric_cycles_interval"]))
        caps=[F(*x) for x in i["request"]["source_width_caps_rad"]]+[F(*i["request"]["relative_width_cap_rad"])]
        require(len(caps)==3 and all(x>=0 for x in caps) and all(len(x)==2 and x[0]<=x[1] for x in bounds),"ALL_bounds_caps")
        require(bounds[2]==(bounds[0][0]-bounds[1][1],bounds[0][1]-bounds[1][0]),"relative_interval_from_SOURCEs")
        require(all(8*(b-a)<=c for (a,b),c in zip(bounds,caps)),"retained_width_caps")
        pending=[]
        for rid,bid,bound,cap in zip(("S0","S1","S0-minus-S1"),("S0/mirror","S1/mirror","relative"),bounds,caps):
            e=encode_interval(bound);out["RN64_casts"]+=e["RN64_casts"]
            e.update(record_id=rid,branch_id=bid,literal_cap_rad=pair(cap),
                     pair_fits=F(*e["pair_error_bound_rad"])<=cap,single_word_fits=F(*e["single_word_error_bound_rad"])<=cap,
                     original_scene_sha256=q["original_scene_sha256"],literal_request_sha256=q["literal_request_sha256"])
            pending.append(e);out["diagnostics"].append(e)
        closure=F(*pending[0]["pair_value"])-F(*pending[1]["pair_value"])-F(*pending[2]["pair_value"])
        rounding=sum(F(*p["pair_rounding_error"]) for p in pending)
        require(abs(closure)<=rounding,"SOURCE_relative_closure_budget")
        out["closure_error_cycles"]=pair(abs(closure));out["closure_rounding_budget_cycles"]=pair(rounding)
        out["single_word_ALL_caps_fit"]=all(p["single_word_fits"] for p in pending)
        require(all(p["pair_fits"] for p in pending),"pair_SOURCE_relative_cap")
        out.update(status="CPU_OBLIQUE_PAIR64_GEOMETRIC_TRANSPORT_ONLY",rows=pending,
                   parent_receipt_sha256=PARENT_SHA,request_sha256=digest(q))
    except (ValueError,TypeError,KeyError,OSError,zlib.error) as e:out["reason"]=str(e)
    return out
