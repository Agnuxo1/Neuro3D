"""Ledger-only tests. Old captures are data, never old evaluator imports."""
from pathlib import Path
from fractions import Fraction as F
import ast, base64, hashlib, importlib.util, json, struct, zlib

ROOT = Path(__file__).resolve().parents[2]
PARENT = "coordinacion/respuestas/PRECISION-NEXT-TRIANGLE-INTERVAL-CPU-001-CODEX.json"
PSHA = "4e64b185a6ebc131c284270318c8793085f17091a27d7eb7ac36cd287e36445e"
CORE = "Blender/benchmarks/capacity_audit/oblique_next_ledger_CPU_v1.py"
PREVIOUS = "Blender/benchmarks/capacity_audit/oblique_next_triangle_interval_CPU_v1.py"
GI = "coordinacion/respuestas/PRECISION-OBLIQUE-SCENE-GEOMETRY32-INGRESS-HOST-001-CODEX.json"


def sha(b):
    return hashlib.sha256(b).hexdigest()


def capture(c):
    assert c["rc"] == 0 and c["timed_out"] is False
    d = zlib.decompressobj()
    b = d.decompress(base64.b64decode(c["stdout_zlib_base64"], validate=True), 1048577)
    assert len(b) <= 1048576 and d.eof and not d.unused_data and not d.unconsumed_tail
    assert sha(b) == c["stdout_sha256"] and len(b) == c["stdout_bytes"]
    return json.loads(b)


def pair(x):
    assert type(x) is list and len(x) == 2
    result = []
    for p in x:
        assert type(p) is list and len(p) == 2 and all(type(v) is int for v in p)
        assert p[1] > 0 and max(abs(v).bit_length() for v in p) <= 4096
        f = F(*p)
        assert p == [f.numerator, f.denominator]
        result.append(f)
    return tuple(result)


def run():
    raw = (ROOT/PARENT).read_bytes()
    assert sha(raw) == PSHA and len(raw) == 105703
    parent = json.loads(raw)
    pins = dict(parent["code_doc_sha256"])
    assert len(pins) == 417
    pins[PARENT] = PSHA
    for path, h in pins.items():
        assert sha((ROOT/path).read_bytes()) == h, path
    prior = capture(parent["test_run"])
    assert parent["zero_error_gate"] == "FAIL_RETAINED_72_NEW_NONZERO_SCALARS_NO_PROMOTION"
    assert len(prior["new_nonzero_errors_preserved"]) == 72
    assert len(prior["prior_nonzero_error_rows_preserved"]) == 16
    inputs = {x["id"]: x["result"]["packet"] for x in
              capture(json.loads((ROOT/GI).read_bytes())["test_run"])["evidence"]["positive"]}
    names = {"require", "power2", "MAX64", "round_out"}
    def trees(path):
        out = {}
        for n in ast.parse((ROOT/path).read_text(encoding="utf-8")).body:
            name = getattr(n, "name", None)
            if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name):
                name = n.targets[0].id
            if name in names:
                out[name] = ast.dump(n, include_attributes=False)
        return out
    assert trees(CORE) == trees(PREVIOUS) and len(trees(CORE)) == 4
    spec = importlib.util.spec_from_file_location("own_new_ledger", ROOT/CORE)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    cases, count = [], 0
    for case in prior["cases"]:
        p = inputs[case["case"]]
        b = bytes.fromhex(p["buffer_hex"])
        w = struct.unpack("<%dI" % (len(b)//4), b)
        assert sha(b) == case["input_sha256"] == p["manifest"]["buffer_sha256"]
        assert case["scene_sha256"] == p["manifest"]["scene_sha256"]
        assert case["query_sha256"] == p["manifest"]["query_sha256"]
        assert case["primitive_ids"] == list(w[10:10+w[4]])
        base = 10+w[4]
        results = []
        assert [s["source_id"] for s in case["sources"]] == ["S0", "S1"]
        for s in case["sources"]:
            key = (case["input_sha256"], case["scene_sha256"], case["query_sha256"], s["source_id"])
            rows = []
            for index, row in enumerate(s["rows"]):
                tri = [list(w[base+12+9*index+j:base+15+9*index+j]) for j in (0, 3, 6)]
                assert row["triangle_words"] == tri
                assert row["primitive_id"] == case["primitive_ids"][index]
                r = row["result"]
                fields = ["determinant"] if r["status"] == m.DET_ZERO else ["determinant", "parameter", "u", "v", "uv"]
                bounds = tuple(pair(r[f+"_interval"]) for f in fields)
                rows.append((key, row["primitive_id"], r["status"], bounds))
            rows = tuple(rows)
            result = m.audit_source(key, tuple(case["primitive_ids"]), s["previous_primitive_id"], rows)
            assert result["status"] == "STOP_UNRESOLVED_ALL_PRIMITIVES"
            assert result["unresolved_ids"] == [s["previous_primitive_id"]]
            assert result["conditional_first_id"] is None and result["ignored_primitive_ids"] == []
            for flag in ("nearest_hit_certified", "GPU_launch_allowed", "launch_exclusion_allowed",
                         "native_precision_certified", "phase_certified", "source_merged"):
                assert result[flag] is False
            assert result["phase_error_bound"] is None
            count += len(rows)
            results.append(dict(source_id=s["source_id"], result=result))
        cases.append(dict(case=case["case"], input_sha256=case["input_sha256"],
                          primitive_ids=case["primitive_ids"], sources=results))
    key = ("1"*64, "2"*64, "3"*64, "S0")
    ids = (1, 2)
    pt = lambda v: (F(v), F(v))
    def row(pid, kind, tau):
        if kind == m.DET_ZERO:
            bounds = ((F(-1), F(1)),)
        else:
            bounds = (pt(1), tau, pt(F(1, 4)), pt(F(1, 4)), pt(F(1, 2)))
        return (key, pid, kind, bounds)
    good = row(1, m.HIT, pt(1))
    miss = row(2, m.MISS, pt(-1))
    contact = row(2, m.CONTACT, pt(0))
    controls = []
    def control(label, exp_ids, previous, rs, status, candidate):
        result = m.audit_source(key, exp_ids, previous, rs)
        assert result["status"] == status and result["conditional_first_id"] == candidate
        assert result["nearest_hit_certified"] is False and result["GPU_launch_allowed"] is False
        controls.append(dict(label=label, result=result,
                             declared_rows=[dict(primitive_id=r[1], classification=r[2],
                                                 bounds=[[[v.numerator,v.denominator] for v in b] for b in r[3]])
                                            for r in rs]))
    unique = "CONDITIONAL_UNIQUE_FIRST_ON_DECLARED_LEDGER"
    unresolved = "STOP_UNRESOLVED_ALL_PRIMITIVES"
    orderstop = "STOP_FIRST_ORDER_UNRESOLVED"
    control("one_hit_plus_proven_miss", ids, 2, (good, miss), unique, 1)
    control("all_proven_miss", ids, 2, (row(1,m.MISS,pt(-2)),miss),
            "CONDITIONAL_NO_FORWARD_TRIANGLE_ON_DECLARED_LEDGER", None)
    control("previous_contact_cannot_skip", ids, 2, (good, contact), unresolved, None)
    control("other_contact_cannot_skip", ids, 1, (row(1,m.CONTACT,pt(0)),row(2,m.HIT,pt(1))), unresolved, None)
    control("determinant_zero_cannot_skip", ids, 2, (good,row(2,m.DET_ZERO,None)), unresolved, None)
    control("strict_two_hit_order", ids, 2, (good,row(2,m.HIT,pt(2))), unique, 1)
    control("reverse_parameter_order", ids, 2, (row(1,m.HIT,pt(2)),row(2,m.HIT,pt(1))), unique, 2)
    control("overlap", ids, 2, (row(1,m.HIT,(F(1),F(3))),row(2,m.HIT,(F(2),F(4)))), orderstop, None)
    control("tie_no_ID_tiebreak", ids, 2, (good,row(2,m.HIT,pt(1))), orderstop, None)
    control("touch_no_ID_tiebreak", ids, 2, (row(1,m.HIT,(F(1),F(2))),row(2,m.HIT,(F(2),F(3)))), orderstop, None)
    control("binary64_tiny_disjoint_parameter", ids, 2,
            (row(1,m.HIT,pt(F(1,2**60))),row(2,m.HIT,pt(F(1,2**59)))), unique, 1)
    control("later_overlap_does_not_erase_unique_first", (1,2,3), 3,
            (good,row(2,m.HIT,(F(2),F(4))),row(3,m.HIT,(F(3),F(5)))), unique, 1)
    badkey = ("4"*64, key[1], key[2], "S0")
    rowkey = lambda k: (k, good[1], good[2], good[3])
    badbounds = lambda b: (key,1,m.HIT,b)
    negatives = [
        ("missing_row", lambda: m.audit_source(key,ids,2,(good,))),
        ("extra_row", lambda: m.audit_source(key,ids,2,(good,miss,contact))),
        ("duplicate_row", lambda: m.audit_source(key,ids,2,(good,good))),
        ("foreign_id", lambda: m.audit_source(key,ids,2,(good,row(3,m.MISS,pt(-1))))),
        ("reordered_rows", lambda: m.audit_source(key,ids,2,(miss,good))),
        ("duplicate_expected_ID", lambda: m.audit_source(key,(1,1),1,(good,good))),
        ("bool_previous", lambda: m.audit_source(key,ids,True,(good,miss))),
        ("absent_previous", lambda: m.audit_source(key,ids,3,(good,miss))),
        ("bool_expected", lambda: m.audit_source(key,(True,2),2,(good,miss))),
        ("list_rows", lambda: m.audit_source(key,ids,2,[good,miss])),
        ("wrong_INPUT_digest", lambda: m.audit_source(key,ids,2,(rowkey(badkey),miss))),
        ("wrong_scene_digest", lambda: m.audit_source(key,ids,2,(rowkey((key[0],"4"*64,key[2],"S0")),miss))),
        ("wrong_query_digest", lambda: m.audit_source(key,ids,2,(rowkey((key[0],key[1],"4"*64,"S0")),miss))),
        ("SOURCE_cross", lambda: m.audit_source(key,ids,2,(rowkey((*key[:3],"S1")),miss))),
        ("noncanonical_digest", lambda: m.audit_source(("A"*64,*key[1:]),ids,2,(good,miss))),
        ("unknown_status", lambda: m.audit_source(key,ids,2,((key,1,"PASS",good[3]),miss))),
        ("contact_retagged_hit", lambda: m.audit_source(key,ids,2,(good,(key,2,m.HIT,contact[3])))),
        ("missing_scalar", lambda: m.audit_source(key,ids,2,(badbounds(good[3][:-1]),miss))),
        ("reversed_interval", lambda: m.audit_source(key,ids,2,(badbounds((pt(1),(F(2),F(1)),*good[3][2:])),miss))),
        ("bool_endpoint", lambda: m.audit_source(key,ids,2,(badbounds(((True,F(1)),*good[3][1:])),miss))),
        ("nonbinary_endpoint", lambda: m.audit_source(key,ids,2,(badbounds((pt(1),pt(F(1,3)),*good[3][2:])),miss))),
        ("over_capacity", lambda: m.audit_source(key,ids,2,(badbounds((pt(F(1,2**5000)),*good[3][1:])),miss))),
        ("overflow", lambda: m.audit_source(key,ids,2,(badbounds((pt(F(2**1024)),*good[3][1:])),miss))),
        ("det_zero_extra_scalar", lambda: m.audit_source(key,ids,2,(badbounds((pt(0),*good[3][1:])),miss))),
        ("epsilon_override", lambda: m.audit_source(key,ids,2,(good,miss),epsilon=F(1,1000))),
        ("ignored_ID_override", lambda: m.audit_source(key,ids,2,(good,miss),ignored_primitive_ids=(2,))),
    ]
    rejected = []
    for label, call in negatives:
        try:
            call()
        except (ValueError, TypeError) as exc:
            rejected.append(dict(label=label, error=str(exc)))
        else:
            raise AssertionError("negative accepted:"+label)
    exhaustive = []
    import itertools
    intervals = [(F(a),F(b)) for a in (1,2,3) for b in (1,2,3) if a <= b]
    for n in (2,3):
        exp_ids = tuple(range(1,n+1))
        for values in itertools.product(intervals,repeat=n):
            rs = tuple(row(pid,m.HIT,bounds) for pid,bounds in zip(exp_ids,values))
            result = m.audit_source(key,exp_ids,n,rs)
            assert result["conditional_first_id"] is None or not result["unresolved_ids"]
            exhaustive.append(dict(parameter_intervals=[[[x.numerator,x.denominator] for x in b] for b in values],
                                   status=result["status"],conditional_first_id=result["conditional_first_id"],
                                   pair_relations=result["interior_pair_relations"]))
    assert len(exhaustive)==252
    assert len(cases) == 6 and count == 28
    return dict(status="PASS_CPU_COMPARISON_LEDGER_ONLY_NATIVE_ORIGIN_PHASE_STOP",
                context_pins=pins, cases=cases, audited_original_rows=count,
                original_SOURCE_decisions=12, original_contact_STOP=12,
                fabricated_controls=controls, exhaustive_interval_order_controls=exhaustive, negatives=rejected,
                new_nonzero_errors_preserved=prior["new_nonzero_errors_preserved"],
                prior_nonzero_error_rows_preserved=prior["prior_nonzero_error_rows_preserved"],
                zero_error_gate=parent["zero_error_gate"], new_intersections=0,
                old_producer_replays=0, GPU_used=False, JEV="LOCAL_BLOCKED_NO_RETRY_NO_REMOTE_ENDORSEMENT")


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, ensure_ascii=True))
