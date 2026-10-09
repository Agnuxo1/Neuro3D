"""Independent receipt verifier: no imports of tested helpers or suites."""
import base64
from fractions import Fraction as F
import hashlib
import itertools
import json
from pathlib import Path
import zlib

ROOT = Path(__file__).resolve().parents[2]
ID = "PRECISION-ORIGINAL-SOURCE-CANDIDATE-PATH-CYCLES-HOST-001"


def digest(v):
    return hashlib.sha256(json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def cap(r):
    c = r["test_run"]
    assert type(c["rc"]) is int and c["rc"] == 0
    assert c["before_deadline"] is True if "before_deadline" in c else c["timed_out"] is False
    raw = zlib.decompress(base64.b64decode(c["stdout_zlib_base64"]))
    assert len(raw) == c["stdout_bytes"] and hashlib.sha256(raw).hexdigest() == c["stdout_sha256"]
    return json.loads(raw)


receipt = json.loads((ROOT/"coordinacion/respuestas"/(ID+"-CODEX.json")).read_bytes())
data = cap(receipt)
assert data["status"] == "PASS" and data["tests"] == 5
for path, c in receipt["test_run"]["sources"].items():
    b = (ROOT/path).read_bytes()
    assert len(b) == c["bytes"] and hashlib.sha256(b).hexdigest() == c["sha256"]
parents = []
for name, sha in receipt["parents_sha256"].items():
    b = (ROOT/"coordinacion/respuestas"/name).read_bytes()
    assert hashlib.sha256(b).hexdigest() == sha
    parents.append(cap(json.loads(b)))
# Receipt map is sorted on disk by neither caller nor verifier: select by shape.
old_chord = next(x for x in parents if "records" in x)
old_endpoint = next(x for x in parents if "evidence" in x)
old_literal = next(x for x in parents if "data" in x)["data"]["inputs"]
chords = {(x["result"]["case"], x["result"]["source_id"], x["result"]["primitive_id"]): x["result"]
          for x in old_chord["records"] if x["kind"] == "FIXED_LENGTH"}
endpoints = {x["id"]: x["result"] for x in old_endpoint["evidence"]["positive"]}
rows = [x["result"] for x in data["records"] if x["kind"] == "FIXED_PATH_OR_STOP"]
controls = [x["result"] for x in data["records"] if x["kind"] == "QUOTIENT_CONTROL"]
assert len(rows) == 28 and len(controls) == 8 and len(data["records"]) == 87
assert len([x for x in data["records"] if x["kind"] == "BINDING_NEG"]) == 28
assert len([x for x in data["records"] if x["kind"] == "INPUT_NEG"]) == 17
assert len([x for x in data["records"] if x["kind"] == "CAPTURE_NEG"]) == 5
norms = roots = first_corners = quotient_corners = bindings = old_certificates = 0
census = {}
for out in rows:
    census[out["status"]] = census.get(out["status"], 0)+1
    assert out["upstream_ledger_status"] == "STOP_UNRESOLVED_ALL_PRIMITIVES"
    assert out["conditional_first_id"] is None and out["ignored_primitive_ids"] == []
    assert out["origin_offset_applied"] is False
    assert out["phase_error_bound"] is None and out["source_phase"] is None and out["material_phase"] is None
    assert out["field"] is None and out["power"] is None and out["SOURCE_merged"] is False
    assert all(out[k] is False for k in ("phase_certified", "GPU_launch_allowed", "native_precision_certified",
               "native_length_graph_certified", "full_path_visibility_certified", "nearest_hit_certified",
               "launch_exclusion_allowed", "detector_connection_certified", "first_leg_native_ALU_certified"))
    old = chords[(out["case"], out["source_id"], out["primitive_id"])]
    assert all(out[k] == old[k] for k in ("scene_sha256", "query_sha256", "input_sha256", "source_record_sha256",
                                        "CPU_packet_binding_sha256", "previous_primitive_id"))
    if out["cycles_interval"] is None:
        assert "new_first_segment" not in out
        continue
    lit = old_literal[out["case"]]; req = lit["request"]; ep = endpoints[out["case"]]
    assert digest(lit["scene"]) == out["scene_sha256"] and digest(req) == out["query_sha256"]
    assert ep["input_buffer_sha256"] == out["input_sha256"] and ep["query_sha256"] == out["query_sha256"]
    i = 0 if out["source_id"] == "S0" else 1
    origin = [[v, v] for v in lit["scene"]["sources"][i]["position_BU"]]
    assert out["source_origin_box_BU"] == origin == ep["SOURCE_results"][i]["endpoint_boxes"][0]
    assert out["previous_point_box_BU"] == old["point_box"] == ep["SOURCE_results"][i]["endpoint_boxes"][1]
    assert out["candidate_next_point_box_BU"] == old["modeled_next_position_box_BU"]
    assert out["retained_next_segment_length_BU"] == old["chord"]["length_BU"]
    assert out["retained_chord_sha256"] == digest(old["chord"])
    assert out["literal_input_sha256"] == digest(lit)
    bindings += 1; old_certificates += 2
    first = out["new_first_segment"]
    p, q = [[tuple(F(*v) for v in a) for a in out[k]]
            for k in ("source_origin_box_BU", "previous_point_box_BU")]
    squared = [F(0), F(0)]
    for a, b in zip(p, q):
        ds = (b[0]-a[1], b[1]-a[0])
        near = F(0) if ds[0] <= 0 <= ds[1] else min(map(abs, ds))
        far = max(map(abs, ds)); squared[0] += near**2; squared[1] += far**2
    assert [F(*v) for v in first["squared_BU2"]] == squared
    for q2, key in zip(squared, ("root_lower_certificate", "root_upper_certificate")):
        c = first[key]; n, d = q2.numerator << 192, q2.denominator; k = c["floor_scaled_root"]
        assert c["fraction_bits"] == 96 and k*k*d <= n < (k+1)**2*d
        assert c["exact"] is (k*k*d == n)
        assert F(*c["lower_BU"]) == F(k, 2**96)
        assert F(*c["upper_BU"]) == F(k+int(k*k*d != n), 2**96)
        roots += 1
    lo, hi = [F(*v) for v in first["length_BU"]]
    for xyz in itertools.product(*(p+q)):
        val = sum(((xyz[j+3]-xyz[j])**2 for j in range(3)), F(0))
        assert lo*lo <= val <= hi*hi; first_corners += 1
    norms += 1
    assert [F(*v) for v in out["length_BU"]] == [F(*a)+F(*b) for a, b in zip(first["length_BU"], old["chord"]["length_BU"])]
    assert out["reference_BU"] == [req["reference_BU"]]*2 and out["wavelength_BU"] == [req["lambda_BU"]]*2
    assert F(*out["cycles_width"]) > 0 and out["old_ideal_lengths_used"] is False
for out in [r for r in rows if r["cycles_interval"] is not None]+controls:
    l, r, w = [[F(*v) for v in out[k]] for k in ("length_BU", "reference_BU", "wavelength_BU")]
    values = [(a-b)/c for a, b, c in itertools.product(l, r, w)]
    low, high = min(values), max(values)
    assert [F(*v) for v in out["cycles_interval"]] == [low, high]
    assert F(*out["cycles_width"]) == high-low
    assert out["result_units"] == "unwrapped_cycles_NOT_radians"
    quotient_corners += 8
assert census == {"CONDITIONAL_GEOMETRIC_PATH_CYCLES_ONLY":8,"STOP_NO_CONDITIONAL_FORWARD_PATH":16,
                  "STOP_MISSING_LITERAL_REFERENCE_WAVELENGTH_CONTEXT":4}
# Independently verify the two bad capacity fixtures and final 586-bit STOP fixture.
l=(F(1,2**127-1),F(2,2**107-1));r=(F(1,2**89-1),F(2,2**83-1))
capacity_bits = []
for a,b,c,d in ((79,127,83,107),(79,127,101,107),(79,113,101,109)):
    w=(F(2**a-1,2**b-1),F(2**c-1,2**d-1))
    values=[(x-y)/z for x,y,z in itertools.product(l,r,w)]; width=max(values)-min(values)
    capacity_bits.append(max(abs(width.numerator).bit_length(),width.denominator.bit_length()))
assert capacity_bits == [251,352,586]
fr = json.loads((ROOT/"coordinacion/respuestas/GPU-GUARD-OWNED-TREE-CONTAINMENT-CPU-001-CODEX.json").read_bytes())
pc = fr["pinned_manifest_capture"]; raw=zlib.decompress(base64.b64decode(pc["stdout_zlib_base64"]))
assert hashlib.sha256(raw).hexdigest() == pc["stdout_sha256"]
pins=json.loads(raw)["pins"]; assert len(pins)==461
for path, sha in pins.items():
    assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==sha
print(json.dumps(dict(status="PASS", fixed_rows=28, SOURCE_bindings=bindings, new_first_norms=norms,
                      new_first_root_certificates=roots, first_corner_combinations=first_corners,
                      captured_next_chord_contexts=bindings, captured_next_root_certificates=old_certificates,
                      quotient_rows=16, quotient_corner_combinations=quotient_corners,
                      fixed_STOPs=20, NEG_rows=50, unchanged_frozen_pins=461, capacity_fixture_width_bits=capacity_bits,
                      helper_or_suite_imports=0, producer_executions=0, GPU_used=False, phase_certified=False),sort_keys=True))
