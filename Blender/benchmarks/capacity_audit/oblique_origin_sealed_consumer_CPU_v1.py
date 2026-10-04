"""Pinned local CPU record selection; never a launch credential or native proof."""
from fractions import Fraction
import base64
import hashlib
import json
import zlib

PARENT_SHA256 = "9a80c1df6eafc76e424639ef74cc0afef7a58b7b1482bc747dc50756f7dec72b"
PARENT_BYTES = 126063
CAPTURE_SHA256 = "23ebd46797b16baebea99a6be42d0f72042cfef964cd7f017514b8cbc806646e"
CAPTURE_BYTES = 133577
ERROR_GATE = "FAIL_RETAINED_72_NEW_NONZERO_SCALARS_NO_PROMOTION"


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def hash_label(value):
    require(type(value) is str and len(value) == 64
            and all(c in "0123456789abcdef" for c in value), "STOP_HASH_LABEL")


def box_label(value):
    require(type(value) is tuple and len(value) == 3, "STOP_BOX_SHAPE")
    out = []
    for pair in value:
        require(type(pair) is tuple and len(pair) == 2, "STOP_BOX_PAIR_SHAPE")
        require(all(type(x) is Fraction for x in pair), "STOP_BOX_ENDPOINT_TYPE")
        require(all(x.numerator.bit_length() <= 4096 and x.denominator.bit_length() <= 4096
                    for x in pair), "STOP_BOX_CAPACITY")
        require(pair[0] <= pair[1], "STOP_BOX_REVERSED")
        out.append([[x.numerator, x.denominator] for x in pair])
    return out


def triangle_label(value):
    require(type(value) is tuple and len(value) == 3, "STOP_TRIANGLE_SHAPE")
    for v in value:
        require(type(v) is tuple and len(v) == 3, "STOP_VERTEX_SHAPE")
        require(all(type(x) is int and 0 <= x < 2**32 for x in v), "STOP_WORD_TYPE")
    return [list(v) for v in value]


def pinned_capture(receipt_bytes):
    require(type(receipt_bytes) is bytes, "STOP_RECEIPT_TYPE")
    require(len(receipt_bytes) == PARENT_BYTES, "STOP_RECEIPT_SIZE")
    require(digest(receipt_bytes) == PARENT_SHA256, "STOP_RECEIPT_UNPINNED")
    receipt = json.loads(receipt_bytes)
    require(receipt["zero_error_gate"] == ERROR_GATE, "STOP_ERROR_GATE")
    cap = receipt["test_run"]
    require(cap["rc"] == 0 and cap["timed_out"] is False, "STOP_CAPTURE_EXECUTION")
    compressed = base64.b64decode(cap["stdout_zlib_base64"], validate=True)
    decoder = zlib.decompressobj()
    raw = decoder.decompress(compressed, 1048577)
    require(len(raw) <= 1048576 and decoder.eof and not decoder.unused_data
            and not decoder.unconsumed_tail, "STOP_CAPTURE_DOMAIN")
    require(len(raw) == CAPTURE_BYTES == cap["stdout_bytes"]
            and digest(raw) == CAPTURE_SHA256 == cap["stdout_sha256"],
            "STOP_CAPTURE_INTEGRITY")
    data = json.loads(raw)
    require(data["zero_error_gate"] == ERROR_GATE
            and len(data["original_evidence"]) == 12, "STOP_CAPTURE_SCHEMA")
    return data


def select_cpu_property(receipt_bytes, input_bytes, scene_sha256, query_sha256,
                        source_id, previous_primitive_id, point_bounds,
                        direction_bounds, triangle_words):
    """Return only a sealed ideal CPU advisory for an exactly matching request.

    Assumes this module's fixed digest anchor is itself reviewed and pinned.
    Matching caller labels is not authentication of a renderer or native state.
    No caller-supplied replacement pin, skip, epsilon, or promotion is accepted.
    """
    data = pinned_capture(receipt_bytes)
    require(type(input_bytes) is bytes and 0 < len(input_bytes) <= 1024,
            "STOP_INPUT_TYPE_SIZE")
    hash_label(scene_sha256)
    hash_label(query_sha256)
    require(type(source_id) is str and source_id in ("S0", "S1"), "STOP_SOURCE")
    require(type(previous_primitive_id) is int and 0 <= previous_primitive_id < 2**32,
            "STOP_PREVIOUS_ID")
    point, direction = box_label(point_bounds), box_label(direction_bounds)
    triangle = triangle_label(triangle_words)
    input_sha = digest(input_bytes)
    matches = [r for r in data["original_evidence"]
               if r["input_sha256"] == input_sha
               and r["scene_sha256"] == scene_sha256
               and r["query_sha256"] == query_sha256
               and r["source_id"] == source_id
               and r["previous_primitive_id"] == previous_primitive_id
               and r["point_bounds"] == point and r["direction_bounds"] == direction
               and r["triangle_words"] == triangle]
    require(len(matches) == 1, "STOP_REQUEST_NOT_UNIQUE_SEALED_CPU_RECORD")
    row = matches[0]
    proof, ledger = row["result"], row["old_ledger_SOURCE_decision_retained"]
    require(proof["CPU_box_zero_contact_proved"] is True
            and proof["parameter_zero_range"] == [[0, 1], [0, 1]]
            and proof["launch_exclusion_allowed"] is False
            and proof["native_precision_certified"] is False,
            "STOP_SEALED_PROPERTY_SCOPE")
    require(ledger["status"] == "STOP_UNRESOLVED_ALL_PRIMITIVES"
            and ledger["conditional_first_id"] is None
            and ledger["unresolved_ids"] == [previous_primitive_id],
            "STOP_RETAINED_LEDGER_SCOPE")
    return dict(
        status="CPU_RECORD_BOUND_ADVISORY_ONLY_NO_LAUNCH_CREDENTIAL",
        local_receipt_integrity_pinned=True, request_matches_sealed_CPU_record=True,
        pin_trust_scope="REVIEWED_MODULE_FIXED_DIGEST_NOT_NATIVE_OR_SIGNATURE",
        parent_receipt_sha256=PARENT_SHA256, capture_sha256=CAPTURE_SHA256,
        sealed_record=row, zero_error_gate=ERROR_GATE,
        launch_exclusion_allowed=False, GPU_used=False, GPU_launch_allowed=False,
        native_precision_certified=False, upstream_binding_authenticated=False,
        nearest_hit_certified=False, full_path_visibility_certified=False,
        phase_certified=False, phase_error_bound=None, ignored_primitive_ids=[],
        SOURCE_shared_token=False, origin_offset_applied=False,
        full_costs="UNKNOWN_NOT_ZERO", old_producer_replays=0,
        new_geometric_evaluations=0)
