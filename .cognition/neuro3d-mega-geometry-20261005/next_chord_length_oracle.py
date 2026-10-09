"""Captured endpoint-norm proof audit; no imports of helpers, suites or producers."""
import base64,ctypes,hashlib,itertools,json,pathlib,psutil,zlib
from fractions import Fraction as F
k=ctypes.WinDLL("kernel32");k.GetCurrentProcess.restype=ctypes.c_void_p
k.SetProcessAffinityMask.argtypes=[ctypes.c_void_p,ctypes.c_size_t]
assert k.SetProcessAffinityMask(k.GetCurrentProcess(),1)
assert psutil.virtual_memory().available-128*2**20>=4*2**30
root=pathlib.Path("D:/PROJECTS/9_NEBULA_NEW")
receipt=json.loads((root/"coordinacion/respuestas/PRECISION-ORIGINAL-SOURCE-NEXT-CHORD-LENGTH-CPU-001-CODEX.json").read_bytes())
def unpack(cap):
    dec=zlib.decompressobj()
    raw=dec.decompress(base64.b64decode(cap["stdout_zlib_base64"],validate=True),2097153)
    assert dec.eof and not dec.unused_data and not dec.unconsumed_tail
    assert len(raw)==cap["stdout_bytes"] and len(raw)<=2097152
    assert hashlib.sha256(raw).hexdigest()==cap["stdout_sha256"]
    return json.loads(raw)
d=unpack(receipt["test_run"])
assert d["status"]=="PASS" and d["tests"]==4 and len(d["records"])==64
assert receipt["test_run"]["rc"]==0 and receipt["test_run"]["before_deadline"] is True
dep=receipt["dependency"];raw=(root/dep["path"]).read_bytes()
assert hashlib.sha256(raw).hexdigest()==dep["sha256"]
parent=json.loads(raw);p=unpack(parent["test_run"])
assert parent["initial_FAIL_preserved"]["rc"]==1
parents={(v["result"]["case"],v["result"]["source_id"],v["result"]["primitive_id"]):v["result"] for v in p["records"] if v["kind"]=="FIXED_POSITION"}
assert len(parents)==28
normdep=receipt["pure_arithmetic_dependency"]
assert hashlib.sha256((root/normdep["path"]).read_bytes()).hexdigest()==normdep["sha256"]
assert normdep["fixed_root_fraction_bits"]==96 and normdep["fixed_input_bits"]==128 and normdep["fixed_root_bits"]==512
def pair(q):return [q.numerator,q.denominator]
census={};states={};seen=set();corners=0;certs=0;norms=0;positive_widths=0
for record in d["records"]:
    kind=record["kind"];census[kind]=census.get(kind,0)+1
    if kind not in ("FIXED_LENGTH","CONTROL"):continue
    out=record["result"];norms+=1
    P=[[F(*q)for q in a]for a in out["point_box"]]
    Q=[[F(*q)for q in a]for a in out["modeled_next_position_box_BU"]]
    components=[];squares=[]
    for j in range(3):
        a,b=P[j],Q[j]
        gap=max(F(0),b[0]-a[1],a[0]-b[1])
        maximum=max(abs(x-y)for x in a for y in b)
        components.append(dict(difference_BU=[pair(b[0]-a[1]),pair(b[1]-a[0])],
                               squared_BU2=[pair(gap*gap),pair(maximum*maximum)]))
        squares.append((gap*gap,maximum*maximum))
    squared=[sum((s[i]for s in squares),F(0))for i in range(2)]
    chord=out["chord"]
    assert chord["components"]==components
    assert chord["squared_BU2"]==[pair(v)for v in squared]
    assert out["costs"]==dict(new_interval_segment_norms=1,new_integer_root_certificates=2)
    assert out["root_fraction_bits"]==96
    for i,name in enumerate(("root_lower_certificate","root_upper_certificate")):
        cert=chord[name];certs+=1
        q=squared[i];scale=q.numerator<<192;den=q.denominator;k=cert["floor_scaled_root"]
        assert q>=0 and q<=2**64 and max(q.numerator.bit_length(),den.bit_length())<=512
        assert cert["fraction_bits"]==96 and cert["squared"]==pair(q)
        assert cert["scaled_numerator"]==scale and cert["scaled_denominator"]==den
        assert k*k*den<=scale<(k+1)*(k+1)*den
        exact=k*k*den==scale
        assert cert["exact"] is exact
        assert cert["lower_BU"]==pair(F(k,2**96))
        assert cert["upper_BU"]==pair(F(k+int(not exact),2**96))
    assert chord["length_BU"]==[chord["root_lower_certificate"]["lower_BU"],chord["root_upper_certificate"]["upper_BU"]]
    lo,hi=[F(*v)for v in chord["length_BU"]]
    assert 0<=lo<=hi and lo*lo<=squared[0] and hi*hi>=squared[1]
    for v in itertools.product(*(P+Q)):
        sq=sum(((v[j+3]-v[j])**2 for j in range(3)),F(0))
        assert lo*lo<=sq<=hi*hi;corners+=1
    assert out["native_length_error_bound"] is None and out["length_reference_phase_bound"] is None and out["phase_error_bound"] is None
    for flag in ("native_precision_certified","native_length_graph_certified","length_accuracy_budget_admitted","nearest_hit_certified","launch_exclusion_allowed","full_path_visibility_certified","GPU_launch_allowed","phase_certified","SOURCE_merged"):
        assert out[flag] is False
    if kind=="FIXED_LENGTH":
        key=(out["case"],out["source_id"],out["primitive_id"]);assert key not in seen;seen.add(key)
        prior=parents[key]
        for field in ("case","source_id","scene_sha256","query_sha256","input_sha256","source_record_sha256","CPU_packet_binding_sha256","primitive_id","previous_primitive_id"):
            assert out[field]==prior[field]
        assert out["point_box"]==prior["point_box"]
        assert out["modeled_next_position_box_BU"]==prior["modeled_binary64_position_box_BU"]
        state=out["upstream_triangle_status"];assert state==prior["upstream_triangle_status"]
        states[state]=states.get(state,0)+1
        assert out["upstream_ledger_status"]==prior["upstream_ledger_status"]=="STOP_UNRESOLVED_ALL_PRIMITIVES"
        assert out["conditional_first_id"] is None
        assert out["parent_receipt_sha256"]==dep["sha256"]
        if state.startswith("STOP"):assert lo==hi==0
        if state=="CONDITIONAL_TRIANGLE_INTERIOR_HIT":
            assert 0<lo<hi;positive_widths+=1
    else:
        assert out["parent_receipt_sha256"] is None
        if record["label"]=="root_granularity_2m97_kept":
            assert lo==0 and hi==F(1,2**96)
        if record["label"]=="uncertain_same_contact_NO_correlation_credit":
            assert lo==0 and hi==2
assert census==dict(FIXED_LENGTH=28,CONTROL=8,CALLER_SCOPE_COPY=1,PROMOTION_NEG=17,INPUT_NEG=10)
assert states==dict(CONDITIONAL_TRIANGLE_INTERIOR_HIT=12,STOP_TRIANGLE_CONTACT_OR_BOUNDARY_UNRESOLVED=12,CONDITIONAL_TRIANGLE_MISS=4)
assert norms==36 and certs==72 and corners==2304 and positive_widths==12
rootNEG=next(v for v in d["records"] if v.get("label")=="root_capacity512_retained")
assert rootNEG["error"]=="root_capacity"
snapshots=0
for path,e in receipt["test_run"]["sources"].items():
    raw=zlib.decompress(base64.b64decode(e["zlib_base64"],validate=True))
    assert len(raw)==e["bytes"] and hashlib.sha256(raw).hexdigest()==e["sha256"]
    assert (root/path).read_bytes()==raw;snapshots+=1
for path,e in parent["test_run"]["sources"].items():
    assert hashlib.sha256((root/path).read_bytes()).hexdigest()==e["sha256"]
pins=unpack(json.loads((root/"coordinacion/respuestas/GPU-GUARD-OWNED-TREE-CONTAINMENT-CPU-001-CODEX.json").read_bytes())["pinned_manifest_capture"])["pins"]
assert len(pins)==461
for path,sha in pins.items():assert hashlib.sha256((root/path).read_bytes()).hexdigest()==sha,path
print(json.dumps(dict(status="PASS",captured_norm_rows=norms,independent_root_certificates=certs,
                     fixed_bindings=28,SOURCE_slots=12,corner_combinations=corners,
                     original_ledger_STOPs=12,positive_nonzero_width_length_intervals=positive_widths,
                     root_fraction_bits=96,capacity_NEG_preserved=True,promotion_NEG=17,input_NEG=10,
                     source_snapshots=snapshots,frozen_pins=461,old_position_replays=0,
                     GPU_used=False,native_length_error_bound=None,phase_error_bound=None),sort_keys=True))

