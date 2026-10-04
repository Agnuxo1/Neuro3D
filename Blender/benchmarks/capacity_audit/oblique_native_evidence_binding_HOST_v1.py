"""Opt-in byte/content binding only. Never execute, authenticate or admit GPU."""
from pathlib import Path
from datetime import datetime, timedelta
import base64, hashlib, json, math, zlib
ROOT = Path(__file__).resolve().parents[3]
PARENT = "coordinacion/respuestas/PRECISION-OBLIQUE-EXISTING-EVIDENCE-INVENTORY-HOST-001-CODEX.json"
PSHA = "e9130e8f3f6aa8d5673ab03f3d0f9338d0cec8d56437610f490c8ec23e97ac2a"
SCHEMA = "oblique-native-byte-content-binding-HOST-v1"
COMPONENTS = ("queue_wait", "export", "input_validation", "compile", "acceleration_build",
              "upload", "scene_geometry", "reference_phase", "source_products", "group_detector",
              "readback", "output_validation", "guard_overhead", "host_evidence_check")
POLICY = {"fail_closed": True, "RAM_free_after_budget_min_bytes": 4*2**30,
          "VRAM_total_max_bytes": 18*2**30, "temperature_max_C": 80,
          "bytes_per_cell_min": 1024, "margins_and_temporaries_included": True,
          "exclusive_job_reservation_required": True}
MAX_JSON = 1024*1024
MAX_TOTAL = 8*1024*1024
FALSE = ("GPU_launch_allowed", "execution_authenticated", "native_IEEE_RN_graph_certified",
         "physical_phase_admitted", "equivalent_runtime_work_certified",
         "efficiency_comparison_certified", "costs_authenticated", "SOURCE_merged",
         "fresh_job_admitted", "guard_runtime_certified", "contact_certified")

def need(ok, message):
    if not ok:
        raise ValueError(message)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def digest(value):
    return sha(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode())

def same(actual, expected, message):
    need(digest(actual) == digest(expected), message)

def number(x, message, positive=False):
    need(type(x) is int and x >= (1 if positive else 0), message)
    return x

def identifier(x):
    need(type(x) is str and 0 < len(x) <= 128 and
         all(c.isascii() and (c.isalnum() or c in "._:-") for c in x), "bounded_identifier")
    return x

def parse(raw):
    need(type(raw) is bytes and len(raw) <= MAX_JSON, "bounded_JSON_bytes")
    def finite(s):
        x = float(s)
        need(math.isfinite(x), "nonfinite_exponent")
        return x
    def invalid(s):
        raise ValueError("nonfinite_constant")
    def unique(items):
        out = {}
        for k, v in items:
            need(k not in out, "duplicate_key")
            out[k] = v
        return out
    value = json.loads(raw, object_pairs_hook=unique, parse_float=finite, parse_constant=invalid)
    stack = [(value, 0)]
    count = 0
    while stack:
        v, depth = stack.pop()
        count += 1
        need(depth <= 64 and count <= 100000, "bounded_JSON_tree")
        if type(v) is dict:
            stack.extend((x, depth+1) for x in v.values())
        elif type(v) is list:
            stack.extend((x, depth+1) for x in v)
    return value

def retained_capture(w):
    need(type(w["rc"]) is int and w["rc"] == 0 and w["timed_out"] is False, "retained_PASS")
    number(w["stdout_bytes"], "capture_size")
    need(w["stdout_bytes"] <= MAX_JSON, "capture_cap")
    dec = zlib.decompressobj()
    raw = dec.decompress(base64.b64decode(w["stdout_zlib_base64"], validate=True), MAX_JSON+1)
    need(dec.eof and not dec.unused_data and not dec.unconsumed_tail, "complete_zlib")
    need(len(raw) == w["stdout_bytes"] and sha(raw) == w["stdout_sha256"], "capture_seal")
    return parse(raw)

def load_plan():
    raw = (ROOT/PARENT).read_bytes()
    need(len(raw) == 208948 and sha(raw) == PSHA, "anchor_seal")
    report = parse(raw)
    pins = dict(report["code_doc_sha256"])
    need(len(pins) == 382, "anchor_pins382")
    for name, h in pins.items():
        need(sha((ROOT/name).read_bytes()) == h, "dependency:" + name)
    oracle = retained_capture(report["independent_verification"])
    suite = retained_capture(report["test_run"])
    need(oracle["status"] == suite["status"] == "PASS", "anchor_checks")
    targets = suite["evidence"]["original"]["anchor_cases"]
    need(type(targets) is list and len(targets) == 6, "six_cases")
    need(len({t["case"] for t in targets}) == 6, "unique_cases")
    for t in targets:
        same(t["source_ids"], ["S0", "S1"], "original_SOURCE")
    plan = dict(schema=SCHEMA, anchor_sha256=PSHA, cases=targets,
                output_scope="ordered_SOURCE_raw_bytes_opaque_ABI_not_semantic_precision_proof",
                cost_components=list(COMPONENTS))
    pins[PARENT] = PSHA
    return plan, pins

def ledger(c, job, planhash, io_hashes, backend_hash, kind):
    same(c["evidence_kind"], kind, "cost_origin_label")
    same(c["job_id"], job, "cost_job")
    same(c["plan_sha256"], planhash, "cost_plan")
    same(c["io_sha256"], io_hashes, "cost_input_output_lineage")
    same(c["backend_sha256"], backend_hash, "cost_backend")
    need(type(c["regime"]) is str and c["regime"] in ("cold", "warm"), "cold_warm")
    runs = number(c["amortization_runs"], "amortization", True)
    need(c["regime"] != "cold" or runs == 1, "cold_no_amortization")
    wall = number(c["total_wall_ns"], "wall", True)
    need(c["clock"] == "single_monotonic_ns", "clock")
    rows = c["components"]
    need(type(rows) is list and len(rows) == len(COMPONENTS), "all_cost_components")
    intervals = []
    for row, name in zip(rows, COMPONENTS):
        same(row["component"], name, "cost_order")
        a = number(row["start_ns"], "cost_start")
        b = number(row["end_ns"], "cost_end")
        need(a <= b <= wall, "inside_wall")
        reason = row["reason"]
        need(type(reason) is str and len(reason) <= 512, "cost_reason")
        if row["status"] == "measured":
            need(a < b and reason == "", "measured_span")
            intervals.append((a, b))
        else:
            need(row["status"] == "not_applicable" and a == b and bool(reason.strip()), "justified_NA_not_unknown")
    frontier = 0
    for a, b in sorted(intervals):
        need(a <= frontier, "unaccounted_wall_gap")
        frontier = max(frontier, b)
    need(frontier == wall, "unaccounted_wall_tail")
    for k in ("sampled_RAM_max_bytes", "sampled_VRAM_max_bytes", "upload_bytes", "readback_bytes"):
        number(c[k], k)
    need(c["memory_scope"] == "sampled_maximum_not_global_peak", "sampler_scope")
    e = c["energy"]
    need(type(e["method"]) is str and 0 < len(e["method"].strip()) <= 512, "energy_method")
    if e["status"] == "measured":
        number(e["microjoules"], "energy_unit")
    else:
        need(e["status"] == "unavailable" and e["microjoules"] is None, "energy_unknown_not_zero")
    return {"declared_cost_component_coverage": True, "costs_authenticated": False,
            "energy_available_declared": e["status"] == "measured", "overlap_spans_not_summed": True}

def validate(plan, m, artifacts):
    """Pure caller-content check. Even forged fully matching bytes are not execution proof."""
    need(type(m) is dict and m["schema"] == SCHEMA, "schema")
    same(m["plan"], plan, "immutable_scene_query_input_SOURCE_plan")
    kind = m["evidence_kind"]
    need(type(kind) is str and kind in ("synthetic_contract_fixture", "retained_native_content"), "origin_label")
    job = identifier(m["job_id"])
    need(m["backend_kind"] == "GPU_ALU_digital" and
         m["work_origin"] == "scene_traversal_not_U_GEMM_or_lookup", "no_backend_substitution")
    need(all(m[k] is False for k in FALSE), "no_auth_promotion_claim")
    need(m["phase_error_bound"] is None, "no_bound_from_byte_binding")
    cases = plan["cases"]
    need(type(cases) is list and len(cases) == 6 and len({x["case"] for x in cases}) == 6, "six_unique_cases")
    names = {t["case"] + "/" + role for t in cases for role in ("input", "output")}
    names.update(("backend", "guard", "cost_ledger"))
    need(type(artifacts) is dict and set(artifacts) == set(m["artifact_sha256"]) ==
         set(m["artifact_bytes"]) == names, "complete_exact_artifact_set")
    need(all(type(raw) is bytes for raw in artifacts.values()), "raw_bytes_only")
    need(sum(len(raw) for raw in artifacts.values()) <= MAX_TOTAL, "total_byte_cap")
    for name in sorted(names):
        size = number(m["artifact_bytes"][name], "artifact_size", True)
        need(len(artifacts[name]) == size and sha(artifacts[name]) == m["artifact_sha256"][name], "raw_seal:" + name)
    need(type(m["outputs"]) is list and len(m["outputs"]) == 6, "all_outputs")
    for t, out in zip(cases, m["outputs"]):
        same(out["case"], t["case"], "ordered_cases")
        same(out["source_ids"], t["source_ids"], "SOURCE_order")
        same(out["source_ids"], ["S0", "S1"], "two_separate_SOURCE")
        same(out["scene_sha256"], t["scene_sha256"], "scene")
        same(out["query_sha256"], t["query_sha256"], "query")
        same(out["input_buffer_sha256"], t["input_buffer_sha256"], "input_binding")
        inp, output = t["case"] + "/input", t["case"] + "/output"
        need(sha(artifacts[inp]) == t["input_buffer_sha256"], "original_input_raw_bytes")
        identifier(out["ABI_id"])
        stride = number(out["SOURCE_stride_bytes"], "stride", True)
        need(stride % 4 == 0 and len(artifacts[output]) == 2*stride, "output_raw_shape")
        need(out["output_sha256"] == sha(artifacts[output]), "output_raw_fingerprint")
    ph = digest(plan)
    ioh = {k: m["artifact_sha256"][k] for k in sorted(names) if "/" in k}
    bh = m["artifact_sha256"]["backend"]
    g = parse(artifacts["guard"])
    same(g["evidence_kind"], kind, "guard_origin_label")
    same(g["job_id"], job, "guard_job")
    same(g["plan_sha256"], ph, "guard_plan")
    same(g["io_sha256"], ioh, "guard_input_output")
    same(g["backend_sha256"], bh, "guard_backend")
    same(g["cost_ledger_sha256"], m["artifact_sha256"]["cost_ledger"], "guard_cost")
    same(g["policy"], POLICY, "current_policy_content_no_override")
    need(g["status"] == "completed" and type(g["child_exit_code"]) is int and
         g["child_exit_code"] == 0 and g["reasons"] == [], "complete_child_content")
    stamps = []
    for k in ("child_start_utc", "child_end_utc", "recorded_deadline_utc"):
        x = g[k]
        need(type(x) is str and x.endswith("+00:00"), "explicit_UTC")
        stamps.append(datetime.fromisoformat(x))
    start, end, deadline = stamps
    seconds = number(g["timeout_s"], "timeout", True)
    need(type(g["job_kind"]) is str and g["job_kind"] in ("pilot", "child") and
         seconds <= (120 if g["job_kind"] == "pilot" else 600) and
         start <= end <= deadline and end-start <= timedelta(seconds=seconds),
         "recorded_deadline_timeout_not_fresh_admission")
    c = ledger(parse(artifacts["cost_ledger"]), job, ph, ioh, bh, kind)
    recorded = parse(artifacts["cost_ledger"])
    for role, field, component in (("input", "upload_bytes", "upload"),
                                  ("output", "readback_bytes", "readback")):
        payload_bytes = sum(len(artifacts[t["case"] + "/" + role]) for t in cases)
        need(recorded[field] >= payload_bytes, "transfer_payload_lower_bound:" + role)
        row = recorded["components"][COMPONENTS.index(component)]
        need(row["status"] == "measured", "nonzero_transfer_not_NA:" + role)
    return dict(c, status="CONTENT_MATCH_ONLY_NOT_NATIVE_PRECISION_OR_JOB_ADMISSION",
                content_matched=True, evidence_kind=kind,
                synthetic_fixture_only=kind == "synthetic_contract_fixture",
                origin_authenticated=False, output_ABI_semantics_verified=False,
                phase_error_bound=None, **{k: False for k in FALSE})

def inspect_bundle(manifest_raw=None, artifact_bytes=None):
    """Pinned public entrypoint. Missing evidence STOP; no file paths from manifest."""
    result = dict(status="STOP_EVIDENCE", content_matched=False, reason=None,
                  phase_error_bound=None, **{k: False for k in FALSE})
    try:
        plan, pins = load_plan()
        need(manifest_raw is not None and artifact_bytes is not None, "missing_native_bundle_no_filler_load")
        result = validate(plan, parse(manifest_raw), artifact_bytes)
        result["dependency_pins"] = pins
    except (ValueError, KeyError, TypeError, OSError, RecursionError, zlib.error) as ex:
        result.update(status="STOP_EVIDENCE", content_matched=False, reason=str(ex))
    return result
