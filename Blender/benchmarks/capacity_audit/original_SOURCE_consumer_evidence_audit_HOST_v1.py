"""Read-only linkage of retained SOURCE candidate and consumer captures.

No imports or execution of producers, decoders, geometry, roots or native APIs.
This report links metadata; it never transfers a consumer precision certificate
to the candidate's non-singleton direction boxes.
"""
import base64
import hashlib
import json
from pathlib import Path
import zlib

ROOT = Path(__file__).resolve().parents[3]
ID = "PRECISION-ORIGINAL-SOURCE-CONSUMER-EVIDENCE-AUDIT-HOST-001"
PARENTS = {
    "PRECISION-ORIGINAL-SOURCE-QUERY-PACKET-CPU-001-CODEX.json":
        "5f6b3d0ec64df544fc771044796cd88f62967322a879b10fd74fd012a194d272",
    "PRECISION-OBLIQUE-TRACE-ENDPOINT-LENGTH-ENCLOSURE-HOST-001-CODEX.json":
        "1bf7f82103218e14d04eec0c630531bfe040f9978c843e7981a7bfb8b3502d9a",
    "PRECISION-OBLIQUE-TOTAL-PHASE-VISIBILITY-JOIN-HOST-001-CODEX.json":
        "df45c70348c50838ba4ebc9169f13dacf05bbb9da3cf576cb212f2b3ff3953dc",
}
CASES = ("direction_scaled", "oblique", "shared_ref1000", "tiny_gap_2m60",
         "oblique/outside_segment", "tiny_gap_2m60/outside_segment")
BASE_PHASE = {name: "parent_" + name for name in CASES[:4]}


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def capture(receipt, key):
    cap = receipt[key]
    # Fixed parent formats: final_capture has before_deadline, older test_run
    # has timed_out. Missing evidence is never interpreted as False/zero.
    finished = (cap.get("before_deadline") is True if key == "final_capture"
                else cap.get("timed_out") is False)
    need(cap["rc"] == 0 and finished, "successful_capture")
    decoder = zlib.decompressobj()
    raw = decoder.decompress(base64.b64decode(cap["stdout_zlib_base64"], validate=True),
                             2 * 1024 * 1024 + 1)
    need(decoder.eof and not decoder.unused_data and not decoder.unconsumed_tail
         and len(raw) <= 2 * 1024 * 1024, "bounded_single_capture")
    need(len(raw) == cap["stdout_bytes"] and digest(raw) == cap["stdout_sha256"],
         "capture_identity")
    return json.loads(raw)


def metadata_matches(slot, consumer):
    # SOURCE/case must be selected independently; scene alone is insufficient.
    return (slot["scene_sha256"] == consumer["scene_sha256"]
            and slot["query_sha256"] == consumer["query_sha256"]
            and slot["input_sha256"] == consumer["input_buffer_sha256"])


def audit():
    receipts = {}
    pins = {}
    for name, sha in PARENTS.items():
        raw = (ROOT / "coordinacion/respuestas" / name).read_bytes()
        need(digest(raw) == sha, "parent_identity:" + name)
        receipts[name] = json.loads(raw)
        # These two older consumer receipts carry their complete ancestry.
        for path, expected in receipts[name].get("code_doc_sha256", {}).items():
            need(path not in pins or pins[path] == expected, "pin_conflict")
            pins[path] = expected
    for path, expected in pins.items():
        need(digest((ROOT / path).read_bytes()) == expected, "ancestral_pin:" + path)
    query_receipt, length_receipt, phase_receipt = receipts.values()
    for path, expected in query_receipt["code_sha256"].items():
        raw = (ROOT / path).read_bytes()
        need(digest(raw) == expected["sha256"] and len(raw) == expected["bytes"],
             "candidate_pin:" + path)
    query = capture(query_receipt, "final_capture")
    length = capture(length_receipt, "test_run")
    phase = capture(phase_receipt, "test_run")["data"]
    need(query["status"] == length["status"] == "PASS", "retained_PASS")
    packets = [row["packet"] for row in query["records"] if "packet" in row]
    need(len(packets) == 12 and {(p["slot"]["case"], p["slot"]["source_id"])
         for p in packets} == {(c, s) for c in CASES for s in ("S0", "S1")},
         "closed_SOURCE_census")
    lengths = {row["id"]: row["result"] for row in length["evidence"]["positive"]}
    need(len(lengths) == 6 and set(lengths) == set(CASES), "closed_length_census")
    need(set(phase["unmatched_valid_visibility"]) == set(CASES[4:]),
         "retain_unprepared_outside_phase")
    good = {row["phase_case"]: row for row in phase["runs"]
            if row["id"] == "sealed:" + row["phase_case"]}
    need(len(good) == 11, "retained_phase_overlay_census")
    rows = []
    scene_only_false_links = 0
    exact_metadata_pairs = 0
    for packet in packets:
        slot = packet["slot"]
        case, source = slot["case"], slot["source_id"]
        old = lengths[case]
        need(old["status"] == "HOST_DECLARED_LENGTH_ENCLOSURE_ONLY"
             and old["phase_error_bound"] is None and not old["exact_contact_allowed"],
             "retain_length_scope_STOP")
        need(metadata_matches(slot, old), "scene_query_input_link")
        need([s["source_id"] for s in old["SOURCE_results"]] == ["S0", "S1"],
             "length_SOURCE_order")
        retained_source = old["SOURCE_results"][0 if source == "S0" else 1]
        need(slot["saved_point_bounds"] == retained_source["endpoint_boxes"][1],
             "declared_previous_endpoint_box_link")
        need(slot["previous_primitive_id"] == retained_source["coverage"]["primary_primitive_id"],
             "declared_previous_primitive_link")
        need(slot["saved_direction_bounds"][0][0] != slot["saved_direction_bounds"][0][1],
             "non_singleton_direction_retained")
        for other in lengths.values():
            if metadata_matches(slot, other):
                exact_metadata_pairs += 1
            elif slot["scene_sha256"] == other["scene_sha256"]:
                scene_only_false_links += 1
        phase_link = None
        if case in BASE_PHASE:
            pc = BASE_PHASE[case]
            run = good[pc]
            result = run["result"]
            need(phase["good_mapping"][pc] == case and run["visibility_case"] == case,
                 "base_phase_only_no_overlay_substitution")
            need(result["joined_scene_sha256"] == slot["scene_sha256"]
                 and result["joined_literal_sha256"] == slot["query_sha256"],
                 "phase_declared_context_link")
            need(result["promotion"] == "STOP" and result["GPU_launch_allowed"] is False
                 and result["native_promotion_allowed"] is False, "retain_phase_native_STOP")
            ledger = [r for r in run["ledger"] if r["source_id"] == source]
            need(len(ledger) == 4 and any(r["segment"] == 1
                 and r["primitive_id"] == slot["previous_primitive_id"]
                 and r["classification"] == "EXACT_PREVIOUS_ZERO" and r["t"] == [0, 1]
                 for r in ledger), "captured_previous_zero_classification")
            phase_link = dict(case=pc, captured_paths_sha256=run["request"]["paths_sha256"],
                              ledger_rows_for_SOURCE=4, native_admitted=False)
        rows.append(dict(case=case, source_id=source,
                         CPU_packet_binding_sha256=packet["CPU_packet_binding_sha256"],
                         scene_query_original_input_match=True,
                         previous_point_box_match=True, previous_primitive_match=True,
                         consumer_length_interval_BU=retained_source["total_length_BU"],
                         direction_box_non_singleton=True, phase_capture_link=phase_link,
                         direction_to_new_hit_error_bound=None,
                         native_length_reference_phase_bound=None,
                         status="CAPTURE_CONTEXT_LINK_ONLY_NATIVE_STOP"))
    need(exact_metadata_pairs == 12 and scene_only_false_links == 4,
         "cross_case_metadata_counterexample_census")
    need(len([r for r in rows if r["phase_capture_link"]]) == 8, "phase_SOURCE_census")
    return dict(id=ID, status="HOST_RETAINED_EVIDENCE_AUDIT_ONLY", rows=rows,
                parents_sha256=PARENTS, verified_ancestral_pins=len(pins),
                exact_metadata_pairs=12, scene_only_false_links_rejected=4,
                base_phase_SOURCE_context_links=8, outside_SOURCE_phase_missing=4,
                native_consumer_ABI_verified=False, native_direction_consumed=False,
                candidate_errors_composed_into_length_phase=False,
                scene_authenticated=False, phase_certified=False,
                launch_exclusion_allowed=False, nearest_hit_certified=False,
                GPU_launch_allowed=False, new_geometry_queries=0,
                old_producer_replays=0, old_suite_replays=0, root_evaluations=0,
                full_costs="UNKNOWN_NOT_ZERO", phase_error_bound=None,
                JEV="LOCAL_SECURITY_BLOCKED_NO_RETRY")


if __name__ == "__main__":
    print(json.dumps(audit(), sort_keys=True))
