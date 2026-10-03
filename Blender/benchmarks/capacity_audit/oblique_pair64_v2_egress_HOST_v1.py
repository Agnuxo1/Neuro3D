"""Opt-in V2 egress comparator. Exact integer/rational HOST only; never GPU admission."""
from pathlib import Path
from fractions import Fraction as F
import base64, hashlib, json, struct, zlib

ROOT = Path(__file__).resolve().parents[3]
MODEL = "precision-oblique-pair64-v2-egress-HOST-v1"
ORIGIN = "CPU_UNATTESTED_BYTES"
CASES = ("parent_oblique", "parent_direction_scaled", "parent_shared_ref1000", "parent_tiny_gap_2m60")
PARENTS = {
    "coordinacion/respuestas/PRECISION-OBLIQUE-PAIR64-RAW-GUARD-SHADERC-001-CODEX.json":
    "3fd747841aaea192619df18add3a701a69cc0f20beed598497125d8202f252cf",
    "coordinacion/respuestas/PRECISION-OBLIQUE-PAIR64-DIFFERENCE-CPU-001-CODEX.json":
    "bb67a76885010c9485415007b1f1b5e7fbe03689812216d464baf21dcf4a9dfb",
}
SHADER = "277a94ba2d223a2e2d06052037c6ef549b04270748a3678501ecd2da4446b70f"

def sha(b): return hashlib.sha256(b).hexdigest()
def digest(v): return sha(json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False).encode())
def rational(q):
    if not isinstance(q, list) or len(q) != 2 or any(type(n) is not int for n in q) or q[1] <= 0:
        raise ValueError("fraction")
    return F(*q)
def pair(q): return [q.numerator, q.denominator]

def word(raw):
    """Decode finite little-endian IEEE64 bits without float/RN."""
    if len(raw) != 8: raise ValueError("word_size")
    v = int.from_bytes(raw, "little"); e = (v >> 52) & 2047
    if e == 2047: raise ValueError("nonfinite_raw")
    m = v & ((1 << 52) - 1)
    if e: m |= 1 << 52
    power = e - 1075 if e else -1074
    q = F(m << power) if power >= 0 else F(m, 1 << -power)
    return -q if v >> 63 else q

def capture(r):
    t = r["test_run"]
    raw = zlib.decompress(base64.b64decode(t["stdout_zlib_base64"], validate=True))
    if len(raw) != t["stdout_bytes"] or sha(raw) != t["stdout_sha256"] or t["rc"] != 0 or t["timed_out"]:
        raise ValueError("capture_integrity")
    d = json.loads(raw)
    if d["status"] != "PASS": raise ValueError("parent_suite")
    return d["data"]

def load_evidence():
    """Read existing receipts/pins. No producer import, compiler, GPU or numerical replay."""
    data = []
    for path, h in PARENTS.items():
        raw = (ROOT/path).read_bytes()
        if sha(raw) != h: raise ValueError("parent_identity")
        r = json.loads(raw)
        for p, expected in r["code_doc_sha256"].items():
            if sha((ROOT/p).read_bytes()) != expected: raise ValueError("ancestral_pin")
        data.append(capture(r))
    v2, cpu = data
    result = {}
    for case in CASES:
        p = v2["results"][case]["packet"]
        rows = cpu["results"][case]["rows"]
        if len(rows) != 3 or [x["record_id"] for x in rows] != ["S0", "S1", "S0-minus-S1"]:
            raise ValueError("sealed_completeness")
        result[case] = dict(packet=p, rows=rows)
    return result

def selector(case, e):
    p = e[case]["packet"]
    return dict(case=case, packet_sha256=digest(p), original_scene_sha256=p["scene_sha256"],
                literal_request_sha256=p["literal_sha256"], shader_sha256=p["shader_sha256"],
                intent="HOST_V2_EGRESS_ONLY")

def budget(p, rows, raw):
    """ALL SOURCE caps plus conservative relative bound; never caller-supplied thresholds."""
    if len(rows) != 3 or [r["record_id"] for r in rows] != ["S0", "S1", "S0-minus-S1"]:
        raise ValueError("source_completeness")
    incoming = bytes.fromhex(p["input_hex"])
    if len(incoming) != 48 or struct.unpack("<4I", incoming[:16]) != (0x4f444632, 8, 2, 1):
        raise ValueError("input_ABI")
    source_values=[]; intervals=[]; source_round=F(0); source_bounds=[]
    for j, r in enumerate(rows[:2]):
        if r["original_scene_sha256"] != p["scene_sha256"] or r["literal_request_sha256"] != p["literal_sha256"]:
            raise ValueError("source_identity")
        hi = incoming[16+16*j:24+16*j]; lo = incoming[24+16*j:32+16*j]
        if hi.hex() != r["hi"]["word_le_hex"] or lo.hex() != r["lo"]["word_le_hex"]:
            raise ValueError("source_bits")
        a,b = word(hi),word(lo)
        if max(abs(a),abs(b)) > (1 << 40): raise ValueError("source_domain")
        lower,upper = map(rational,r["interval"])
        if lower > upper: raise ValueError("source_interval")
        cap = rational(r["literal_cap_rad"])
        if cap <= 0 or cap != rational(p["source_literal_caps"][j]): raise ValueError("source_cap_identity")
        v = a+b
        bound = 8*max(abs(v-lower),abs(v-upper))
        if bound > cap: raise ValueError("source_cap")
        source_values.append(v); intervals.append((lower,upper)); source_bounds.append(pair(bound))
        source_round += abs(v-(lower+upper)/2)
    rel = rows[2]
    if rel["original_scene_sha256"] != p["scene_sha256"] or rel["literal_request_sha256"] != p["literal_sha256"]:
        raise ValueError("relative_identity")
    lower = intervals[0][0]-intervals[1][1]; upper = intervals[0][1]-intervals[1][0]
    sealed_interval = rel["parent_relative_CONTROL_ONLY"]["interval"]
    if [pair(lower),pair(upper)] != sealed_interval: raise ValueError("relative_interval")
    cap = rational(rel["literal_cap_rad"])
    if cap <= 0 or cap != rational(p["retained_CPU_budget"]["literal_cap_rad"]): raise ValueError("relative_cap_identity")
    v = word(raw[16:24])+word(raw[24:32])
    arithmetic_error=abs(v-(source_values[0]-source_values[1]))
    radius=(upper-lower)/2
    conservative=8*(radius+source_round+arithmetic_error)
    direct=8*max(abs(v-lower),abs(v-upper))
    if direct > conservative or conservative > cap: raise ValueError("relative_cap")
    return dict(source_bounds_rad=source_bounds, arithmetic_error_cycles=pair(arithmetic_error),
                source_rounding_budget_cycles=pair(source_round), interval_radius_cycles=pair(radius),
                direct_error_bound_rad=pair(direct), conservative_error_bound_rad=pair(conservative),
                literal_cap_rad=pair(cap), relative_value=pair(v))

def _compare_fixture(model, request, raw, origin, evidence):
    result=dict(model=MODEL, status="STOP", reason=None, promotion="STOP", GPU_executed=False,
                GPU_launch_allowed=False, GPU_guard_certified=False, scene_authenticated=False,
                fence_readback_authenticated=False, physical_field_certified=False,
                native_promotion_allowed=False, full_costs="UNMEASURED_NOT_ZERO",
                new_RN_operations=0, compiler_calls=0, frozen_producer_replays=0)
    try:
        if model != MODEL: raise ValueError("model")
        if origin != ORIGIN: raise ValueError("unattested_origin_only")
        if not isinstance(request,dict) or set(request) != {"case","packet_sha256","original_scene_sha256",
                "literal_request_sha256","shader_sha256","intent"}:
            raise ValueError("closed_selector")
        if type(raw) is not bytes or len(raw) != 32: raise ValueError("output_extent")
        if request["case"] not in CASES: raise ValueError("case")
        case = request["case"]; p = evidence[case]["packet"]
        if request != selector(case,evidence): raise ValueError("selector_identity")
        if p["shader_sha256"] != SHADER or p["ABI_tag"] != 0x4f444632: raise ValueError("shader_ABI")
        if struct.unpack("<4I",raw[:16]) != (0x4f444632,4,2,1): raise ValueError("output_header")
        b = budget(p,evidence[case]["rows"],raw)
        # The reference is sealed native CPU arithmetic, NOT a phase copied into GPU input.
        nodes_ref = evidence[case]["rows"][2]
        expected = bytes.fromhex(nodes_ref["hi_word"]+nodes_ref["lo_word"])
        if raw[16:] != expected: raise ValueError("native_bits_mismatch")
        if raw.hex() != p["expected_CONTROL_ONLY_hex"]: raise ValueError("sealed_expected_mismatch")
        result.update(status="HOST_UNATTESTED_BYTES_MATCH", budget=b, output_sha256=sha(raw),
                      packet_sha256=digest(p), completeness="SEALED_2_SOURCE_1_RELATIVE_ONLY",
                      costs=dict(input_SSBO_bytes=48,output_SSBO_bytes=32,total_SSBO_bytes=80,
                                 source_records=2,relative_records=1,
                                 scene_build="UNMEASURED_NOT_ZERO", upload="UNMEASURED_NOT_ZERO",
                                 dispatch="UNMEASURED_NOT_ZERO", fence_readback="UNMEASURED_NOT_ZERO",
                                 geometry_material_field="UNMEASURED_NOT_ZERO"))
    except (ValueError,KeyError,TypeError,OverflowError,IndexError,OSError) as ex:
        result["reason"] = str(ex)
    return result

def compare(model, request, raw, origin):
    """Public sealed contract: caller cannot override evidence, caps or reference."""
    try:
        evidence = load_evidence()
    except (ValueError,KeyError,TypeError,OverflowError,OSError) as ex:
        r = _compare_fixture("INVALID_EVIDENCE", request, raw, origin, {})
        r["reason"] = "evidence_integrity:" + str(ex)
        return r
    return _compare_fixture(model, request, raw, origin, evidence)
