"""Only new consumer executes; sealed parent evidence is read as DATA."""
from pathlib import Path
from fractions import Fraction as F
import base64, copy, hashlib, importlib.util, json, struct, zlib

ROOT = Path(__file__).resolve().parents[2]
PARENT = "coordinacion/respuestas/PRECISION-ORIGIN-BOX-ZERO-CPU-001-CODEX.json"
PSHA = "9a80c1df6eafc76e424639ef74cc0afef7a58b7b1482bc747dc50756f7dec72b"
GI = "coordinacion/respuestas/PRECISION-OBLIQUE-SCENE-GEOMETRY32-INGRESS-HOST-001-CODEX.json"
CORE = "Blender/benchmarks/capacity_audit/oblique_origin_sealed_consumer_CPU_v1.py"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def captured(cap):
    assert cap["rc"] == 0 and cap["timed_out"] is False
    dec = zlib.decompressobj()
    raw = dec.decompress(base64.b64decode(cap["stdout_zlib_base64"],validate=True),1048577)
    assert len(raw) <= 1048576 and dec.eof and not dec.unused_data and not dec.unconsumed_tail
    assert len(raw) == cap["stdout_bytes"] and sha(raw) == cap["stdout_sha256"]
    return json.loads(raw)


def box(values):
    return tuple(tuple(F(*v) for v in pair) for pair in values)


def run():
    raw = (ROOT/PARENT).read_bytes()
    assert sha(raw) == PSHA and len(raw) == 126063
    parent = json.loads(raw)
    pins = dict(parent["code_doc_sha256"])
    assert len(pins) == 425
    pins[PARENT] = PSHA
    for p,h in pins.items():
        assert sha((ROOT/p).read_bytes()) == h,p
    evidence = captured(parent["test_run"])
    rows = evidence["original_evidence"]
    packets = {r["id"]:r["result"]["packet"] for r in
               captured(json.loads((ROOT/GI).read_bytes())["test_run"])["evidence"]["positive"]}
    spec = importlib.util.spec_from_file_location("own_sealed_consumer",ROOT/CORE)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    requests = []
    for row in rows:
        packet = packets[row["case"]]
        binary = bytes.fromhex(packet["buffer_hex"])
        w = struct.unpack("<%dI"%(len(binary)//4),binary)
        ids = list(w[10:10+w[4]])
        index = ids.index(row["previous_primitive_id"])
        start = 10+w[4]+12+9*index
        triangle = tuple(tuple(w[start+j:start+j+3]) for j in (0,3,6))
        assert row["triangle_words"] == [list(v)for v in triangle]
        assert sha(binary) == row["input_sha256"] == packet["manifest"]["buffer_sha256"]
        assert row["scene_sha256"] == packet["manifest"]["scene_sha256"]
        assert row["query_sha256"] == packet["manifest"]["query_sha256"]
        requests.append([raw,binary,row["scene_sha256"],row["query_sha256"],
                         row["source_id"],row["previous_primitive_id"],
                         box(row["point_bounds"]),box(row["direction_bounds"]),triangle])
    accepted = []
    flags = ("launch_exclusion_allowed","GPU_launch_allowed","native_precision_certified",
             "upstream_binding_authenticated","nearest_hit_certified","phase_certified",
             "full_path_visibility_certified","SOURCE_shared_token","origin_offset_applied")
    for req,row in zip(requests,rows):
        out = m.select_cpu_property(*req)
        assert out["sealed_record"] == row
        assert out["status"] == "CPU_RECORD_BOUND_ADVISORY_ONLY_NO_LAUNCH_CREDENTIAL"
        assert out["local_receipt_integrity_pinned"] is True
        assert out["request_matches_sealed_CPU_record"] is True
        assert all(out[k] is False for k in flags)
        assert out["ignored_primitive_ids"] == [] and out["phase_error_bound"] is None
        assert out["zero_error_gate"] == parent["zero_error_gate"] == evidence["zero_error_gate"]
        accepted.append(out)
    baseline = requests[0]
    negatives = []
    def reject(label,req=None,kw=None):
        try:
            m.select_cpu_property(*(baseline if req is None else req),**(kw or {}))
        except (ValueError,TypeError) as ex:
            negatives.append(dict(label=label,error=str(ex),type=type(ex).__name__))
        else:
            raise AssertionError("negative accepted:"+label)
    def changed(index,value):
        req = baseline[:]
        req[index] = value
        return req
    reject("receipt_bytearray",changed(0,bytearray(raw)))
    reject("receipt_empty",changed(0,b""))
    reject("receipt_appended",changed(0,raw+b" "))
    reject("receipt_truncated",changed(0,raw[:-1]))
    reject("receipt_same_length_bitflip",changed(0,bytes([raw[0]^1])+raw[1:]))
    forged = copy.deepcopy(parent)
    forged["launch_exclusion_allowed"] = True
    reject("forged_promotion_receipt_rehashed",changed(0,json.dumps(forged).encode()))
    forged = copy.deepcopy(parent)
    forged["test_run"]["stdout_sha256"] = "0"*64
    reject("forged_capture_transport_digest",changed(0,json.dumps(forged).encode()))
    reject("caller_replacement_pin",kw={"expected_receipt_sha256":sha(json.dumps(forged).encode())})
    reject("input_bytearray",changed(1,bytearray(baseline[1])))
    reject("input_empty",changed(1,b""))
    reject("input_oversize",changed(1,b"x"*1025))
    reject("input_same_length_bitflip",changed(1,bytes([baseline[1][0]^1])+baseline[1][1:]))
    reject("scene_hash_unknown",changed(2,"0"*64))
    reject("query_hash_unknown",changed(3,"0"*64))
    reject("scene_uppercase",changed(2,baseline[2].upper()))
    reject("query_bool",changed(3,True))
    reject("query_short",changed(3,"0"*63))
    reject("source_bool",changed(4,True))
    reject("source_unknown",changed(4,"S2"))
    reject("previous_bool",changed(5,True))
    reject("previous_negative",changed(5,-1))
    reject("previous_overflow",changed(5,2**32))
    reject("previous_other",changed(5,baseline[5]+100))
    reject("point_list",changed(6,list(baseline[6])))
    reject("point_bool",changed(6,((True,F(0)),*baseline[6][1:])))
    reject("point_capacity",changed(6,((F(1,2**5000),F(1,2**5000)),*baseline[6][1:])))
    reject("point_shift_2^-60",changed(6,((baseline[6][0][0]+F(1,2**60),
                                           baseline[6][0][1]+F(1,2**60)),*baseline[6][1:])))
    reject("point_expansion_not_sealed",changed(6,((baseline[6][0][0]-F(1,2**60),
                                                    baseline[6][0][1]+F(1,2**60)),*baseline[6][1:])))
    reject("direction_shift_2^-60",changed(7,((baseline[7][0][0]+F(1,2**60),
                                               baseline[7][0][1]+F(1,2**60)),*baseline[7][1:])))
    reject("direction_zero",changed(7,((F(0),F(0)),)*3))
    reject("triangle_list",changed(8,list(baseline[8])))
    reject("triangle_bool",changed(8,((True,*baseline[8][0][1:]),*baseline[8][1:])))
    reject("triangle_word_overflow",changed(8,((2**32,*baseline[8][0][1:]),*baseline[8][1:])))
    reject("triangle_same_geometry_reordered_unsealed",changed(8,(baseline[8][0],baseline[8][2],baseline[8][1])))
    reject("epsilon_override",kw={"epsilon":F(1,2**60)})
    reject("ignore_ID_override",kw={"ignore_ids":[baseline[5]]})
    reject("native_promotion_override",kw={"native_precision_certified":True})
    reject("token_override",kw={"SOURCE_shared_token":True})
    assert len(negatives) == 38
    # Complete finite join matrix, not a geometric sweep. Header (input/scene/query/SOURCE)
    # and body (previous/boxes/rawtriangles) must identify a sealed original record.
    matrix = []
    for i,a in enumerate(requests):
        for j,b in enumerate(requests):
            req = a[:5]+b[5:]
            expected = [k for k,x in enumerate(requests) if x[1:] == req[1:]]
            assert len(expected) <= 1
            try:
                out = m.select_cpu_property(*req)
            except ValueError as ex:
                assert not expected
                matrix.append(dict(header=i,body=j,accepted=False,error=str(ex)))
            else:
                assert expected and out["sealed_record"] == rows[expected[0]]
                assert all(out[k] is False for k in flags)
                matrix.append(dict(header=i,body=j,accepted=True,sealed_row=expected[0]))
    assert len(matrix) == 144
    first = m.select_cpu_property(*baseline)
    first["sealed_record"]["result"]["launch_exclusion_allowed"] = True
    first["sealed_record"]["old_ledger_SOURCE_decision_retained"]["conditional_first_id"] = 99
    first["ignored_primitive_ids"].append(99)
    repeated = m.select_cpu_property(*baseline)
    assert repeated == accepted[0] and repeated["ignored_primitive_ids"] == []
    assert all(x["old_ledger_SOURCE_decision_retained"]["conditional_first_id"] is None for x in rows)
    assert all(x["old_triangle_contact_row_retained"]["status"] ==
               "STOP_TRIANGLE_CONTACT_OR_BOUNDARY_UNRESOLVED" for x in rows)
    return dict(status="PASS_PINNED_LOCAL_CPU_CONSUMER_ONLY_NO_NATIVE_AUTHORITY",
                context_pins=pins,positive=accepted,negative=negatives,mixed_request_matrix=matrix,
                mixed_accepted=sum(x["accepted"]for x in matrix),
                mixed_rejected=sum(not x["accepted"]for x in matrix),
                returned_mutation_isolation=True,old_contact_STOP_count_retained=12,
                new_nonzero_errors_preserved=evidence["new_nonzero_errors_preserved"],
                prior_nonzero_error_rows_preserved=evidence["prior_nonzero_error_rows_preserved"],
                zero_error_gate=parent["zero_error_gate"],new_geometric_evaluations=0,
                old_producer_replays=0,GPU_used=False,launch_exclusion_allowed=False,
                native_precision_certified=False,JEV="LOCAL_BLOCKED_NO_RETRY_NO_REMOTE_ENDORSEMENT")


if __name__ == "__main__":
    print(json.dumps(run(),sort_keys=True,ensure_ascii=True))
