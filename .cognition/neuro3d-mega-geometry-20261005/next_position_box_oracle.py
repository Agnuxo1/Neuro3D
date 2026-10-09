"""Independent captured-data polynomial audit. Imports no production/test helper."""
import base64,ctypes,datetime as dt,hashlib,itertools,json,math,pathlib,psutil,zlib
from fractions import Fraction as F
REPO_ROOT=pathlib.Path(__file__).resolve().parents[2]
k=ctypes.WinDLL("kernel32")
k.GetCurrentProcess.restype=ctypes.c_void_p
k.SetProcessAffinityMask.argtypes=[ctypes.c_void_p,ctypes.c_size_t]
assert k.SetProcessAffinityMask(k.GetCurrentProcess(),1)
assert psutil.virtual_memory().available-128*2**20>=4*2**30
root=REPO_ROOT
rp=root/"coordinacion/respuestas/PRECISION-ORIGINAL-SOURCE-NEXT-POSITION-BOX-CPU-001-CODEX.json"
r=json.loads(rp.read_bytes())
def unpack(cap):
    dec=zlib.decompressobj()
    raw=dec.decompress(base64.b64decode(cap["stdout_zlib_base64"],validate=True),2097153)
    assert dec.eof and not dec.unused_data and not dec.unconsumed_tail
    assert len(raw)==cap["stdout_bytes"] and len(raw)<=2097152
    assert hashlib.sha256(raw).hexdigest()==cap["stdout_sha256"]
    return json.loads(raw)
def parent(name,sha,key):
    raw=(root/("coordinacion/respuestas/"+name+"-CODEX.json")).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==sha
    return unpack(json.loads(raw)[key])
q=parent("PRECISION-ORIGINAL-SOURCE-QUERY-PACKET-CPU-001","5f6b3d0ec64df544fc771044796cd88f62967322a879b10fd74fd012a194d272","final_capture")
t=parent("PRECISION-NEXT-TRIANGLE-INTERVAL-CPU-001","4e64b185a6ebc131c284270318c8793085f17091a27d7eb7ac36cd287e36445e","test_run")
l=parent("PRECISION-NEXT-LEDGER-CPU-001","5319af7a02502d5d4d3816ad897963919b0b5bb58bcf66393dfada1b61cba211","test_run")
assert len(t["new_nonzero_errors_preserved"])==72 and len(t["prior_nonzero_error_rows_preserved"])==16
data=unpack(r["test_run"]); fail=unpack(r["initial_FAIL_preserved"])
assert r["test_run"]["rc"]==0 and r["test_run"]["before_deadline"] is True and data["status"]=="PASS"
assert r["initial_FAIL_preserved"]["rc"]==1 and fail["status"]=="FAIL"
assert "ValueError not raised" in r["initial_FAIL_preserved"]["stderr"]
assert len(data["records"])==67 and data["tests"]==4
count={}
for v in data["records"]:count[v["kind"]]=count.get(v["kind"],0)+1
assert count==dict(FIXED_POSITION=28,CONTROL=8,CALLER_SCOPE_COPY=1,BINDING_NEG=17,INPUT_NEG=9,CAPTURE_NEG=4)
packets={(p["packet"]["slot"]["case"],p["packet"]["slot"]["source_id"]):p["packet"] for p in q["records"] if "packet" in p}
parent_rows={(c["case"],s["source_id"],v["primitive_id"]):(c,s,v) for c in t["cases"] for s in c["sources"] for v in s["rows"]}
ledgers={(c["case"],s["source_id"]):s["result"] for c in l["cases"] for s in c["sources"]}
assert len(packets)==12 and len(parent_rows)==28 and len(ledgers)==12
def qs(q):return [q.numerator,q.denominator]
def direct(q,upper):
    f=float(q); exact=F.from_float(f)
    if (upper and exact<q) or (not upper and exact>q):
        f=math.nextafter(f,math.inf if upper else -math.inf)
    return F.from_float(f)
checked=0;corner_count=0;status_count={};fixed_keys=set();nonzero_widths=0
for record in data["records"]:
    if record["kind"] not in ("FIXED_POSITION","CONTROL"):continue
    out=record["result"];checked+=1
    P=[[F(*v) for v in a]for a in out["point_box"]]
    D=[[F(*v) for v in a]for a in out["direction_box"]]
    T=[F(*v) for v in out["parameter_interval"]]
    corners=list(itertools.product(*(P+D+[T])));assert len(corners)==record["corner_combinations"]==128
    corner_count+=len(corners)
    expected=[];rounded=[]
    for j in range(3):
        vals=[v[j]+v[6]*v[j+3] for v in corners]
        expected.append([qs(min(vals)),qs(max(vals))])
        products=[tt*dd for tt in T for dd in D[j]]
        ml=direct(min(products),False);mh=direct(max(products),True)
        rounded.append([qs(direct(P[j][0]+ml,False)),qs(direct(P[j][1]+mh,True))])
        for v in corners:
            prod=F.from_float(float(v[6]*v[j+3]))
            rn=F.from_float(float(v[j]+prod))
            lo,hi=[F(*e)for e in rounded[-1]];assert lo<=rn<=hi
    assert out["exact_ray_position_box_BU"]==expected
    assert out["modeled_binary64_position_box_BU"]==rounded
    assert out["status"]=="CONDITIONAL_RAY_POSITION_BOX_ONLY"
    assert out["native_position_error_bound"] is None and out["length_reference_phase_bound"] is None
    for key in ("native_precision_certified","triangle_hit_certified","nearest_hit_certified","launch_exclusion_allowed","GPU_launch_allowed","full_path_visibility_certified","phase_certified"):
        assert out[key] is False
    assert out["ignored_primitive_ids"]==[] and out["origin_offset_applied"] is False
    if record["kind"]=="FIXED_POSITION":
        key=(out["case"],out["source_id"],out["primitive_id"]);assert key not in fixed_keys;fixed_keys.add(key)
        c,s,v=parent_rows[key];slot=packets[key[:2]]["slot"]
        for field in ("scene_sha256","query_sha256","input_sha256","source_record_sha256"):assert out[field]==slot[field]
        assert out["CPU_packet_binding_sha256"]==packets[key[:2]]["CPU_packet_binding_sha256"]
        assert out["point_box"]==slot["saved_point_bounds"]==s["point_interval"]
        assert out["direction_box"]==slot["saved_direction_bounds"]==s["reflected_direction_interval"]
        assert out["parameter_interval"]==v["result"]["parameter_interval"]
        assert out["triangle_geometry_words"]==v["triangle_words"]
        assert out["upstream_triangle_status"]==v["result"]["status"]
        state=out["upstream_triangle_status"];status_count[state]=status_count.get(state,0)+1
        assert out["upstream_ledger_status"]==ledgers[key[:2]]["status"]=="STOP_UNRESOLVED_ALL_PRIMITIVES"
        assert out["conditional_first_id"] is None
        if state.startswith("STOP"):
            assert expected==out["point_box"] and T==[F(0),F(0)]
        if state=="CONDITIONAL_TRIANGLE_INTERIOR_HIT":
            nonzero_widths+=int(any(a[0]!=a[1] for a in expected))
    elif record["label"]=="separate_rounding_tie":
        exact=F(1)+F(1,2**53)
        assert F.from_float(float(exact))-exact==-F(1,2**53)
assert len(fixed_keys)==28 and checked==36 and corner_count==4608 and nonzero_widths==12
frozen=json.loads((root/"coordinacion/respuestas/GPU-GUARD-OWNED-TREE-CONTAINMENT-CPU-001-CODEX.json").read_bytes())
pins=unpack(frozen["pinned_manifest_capture"])["pins"]
assert len(pins)==461
for path,sha in pins.items():assert hashlib.sha256((root/path).read_bytes()).hexdigest()==sha,path
snapshots=0
for cap in (r["initial_FAIL_preserved"],r["test_run"]):
    for path,e in cap["sources"].items():
        raw=zlib.decompress(base64.b64decode(e["zlib_base64"],validate=True))
        assert len(raw)==e["bytes"] and hashlib.sha256(raw).hexdigest()==e["sha256"]
        snapshots+=1
for path,e in r["test_run"]["sources"].items():assert (root/path).read_bytes()==zlib.decompress(base64.b64decode(e["zlib_base64"]))
corepath="Blender/benchmarks/capacity_audit/original_SOURCE_next_position_box_CPU_v1.py"
assert r["initial_FAIL_preserved"]["sources"][corepath]["sha256"]==r["test_run"]["sources"][corepath]["sha256"]
print(json.dumps(dict(status="PASS",captured_polynomial_rows=checked,fixed_binding_rows=28,SOURCE_slots=12,
                     independently_checked_corner_combinations=corner_count,fixed_nonzero_width_position_boxes=nonzero_widths,
                     upstream_status_counts=status_count,ledger_STOPs=12,new_negative_records=30,retained_nonzero_scalars=72,
                     retained_prior_error_rows=16,source_snapshots=snapshots,frozen_pins=461,old_triangle_queries=0,
                     GPU_used=False,native_position_error_bound=None,phase_error_bound=None),sort_keys=True))

