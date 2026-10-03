"""Opt-in CPU64 grow expansion of sealed products; HOST endpoint selection only."""
from pathlib import Path
from fractions import Fraction as F
import json, struct
import oblique_scene_squared_pair_budget_HOST_v1 as sb

ROOT = Path(__file__).resolve().parents[3]
MODEL = "oblique-scene-squared-expansion-CPU64-v1"
POLICY = "SEALED_PRODUCTS_HOST_BOX_SELECTION_NATIVE_GROW_FIXED4"
PARENT = "coordinacion/respuestas/PRECISION-OBLIQUE-SQUARED-PAIR-BUDGET-HOST-001-CODEX.json"
PSHA = "743749e2d0b9742c740a54d3cfad25933750a91cb3a73eab4310a8e41d608d1e"
MAX_COMPONENTS = 4
require, sha, capture, digest, pair, word = sb.require, sb.sha, sb.capture, sb.digest, sb.pair, sb.word
ZERO = word(0.0)


def retained():
    raw = (ROOT / PARENT).read_bytes()
    require(len(raw) == 78633 and sha(raw) == PSHA, "parent_seal")
    r = json.loads(raw)
    pins = dict(r["code_doc_sha256"])
    require(len(pins) == 280, "parent_pins")
    for p, h in pins.items():
        require(sha((ROOT / p).read_bytes()) == h, "dependency:" + p)
    require(capture(r["independent_pre"])["status"] == "PASS", "parent_oracle")
    old = capture(r["test_run"])["evidence"]
    budgets = {x["id"]: x for x in old["records"]}
    products, reference, orig, _ = sb.retained()
    require(set(budgets) == set(products) == set(reference) == set(orig), "closed_records")
    pins[PARENT] = PSHA
    return budgets, products, reference, orig, pins


def decode(w):
    require(type(w) is str and len(w) == 16 and all(c in "0123456789abcdef" for c in w), "canonical_word")
    x = struct.unpack("<d", bytes.fromhex(w))[0]
    require(sb.prod.normal(x) and abs(x) <= 2.0**66, "normal_bounded_word")
    return x


def grow(words):
    """Only floating add/sub outputs produce components; exact F is audit-only."""
    out = dict(status="STOP_INPUT", reason=None, max_components=MAX_COMPONENTS,
               input_words=words, component_words=None, partial_component_words=[],
               processed_words=0, ledger=[], steps=[], RN_nodes_executed=0,
               HOST_float_casts=0, native_root_calls=0)
    e = []
    try:
        require(type(words) is list and 1 <= len(words) <= 24, "bounded_input_list")
        xs = [decode(w) for w in words]  # admission before any arithmetic

        def rn(name, op, a, b):
            exact = F.from_float(a) + F.from_float(b) if op == "add" else F.from_float(a) - F.from_float(b)
            y = a + b if op == "add" else a - b
            out["ledger"].append(dict(index=len(out["ledger"]), name=name, op=op,
                                      a=word(a), b=word(b), y=word(y)))
            out["RN_nodes_executed"] += 1
            require(sb.prod.normal(y) and abs(y) <= 2.0**66 and (y != 0.0 or exact == 0),
                    "RN_normal_bounded_no_underflow")
            return y

        def two_sum(a, b, stem):
            s = rn(stem + ".s", "add", a, b)
            bb = rn(stem + ".bb", "sub", s, a)
            ab = rn(stem + ".ab", "sub", s, bb)
            db = rn(stem + ".db", "sub", b, bb)
            da = rn(stem + ".da", "sub", a, ab)
            err = rn(stem + ".err", "add", da, db)
            require(F.from_float(s) + F.from_float(err) == F.from_float(a) + F.from_float(b),
                    "TwoSum_exact_identity")
            return s, err

        for i, x in enumerate(xs):
            q, h = x, []
            before = [word(v) for v in e]
            start = len(out["ledger"])
            for j, v in enumerate(e):
                q, err = two_sum(q, v, f"grow{i}.term{j}")
                if err != 0.0:  # ONLY exact zero elimination; never an epsilon
                    h.append(err)
            if q != 0.0 or not h:
                h.append(q)
            out["processed_words"] = i + 1
            out["partial_component_words"] = [word(v) for v in h]
            out["steps"].append(dict(input_index=i, before=before, after=[word(v) for v in h],
                                     node_start=start, node_end=len(out["ledger"])))
            require(len(h) <= MAX_COMPONENTS, "fixed4_capacity_exceeded")
            e = h
        out.update(status="CPU64_EXACT_GROW_EXPANSION_SUM_ONLY", reason="fixed4_exact_sum_not_root",
                   component_words=[word(v) for v in e])
    except (ValueError, TypeError, OverflowError) as ex:
        out["reason"] = str(ex)
        if out["reason"] == "fixed4_capacity_exceeded":
            out["status"] = "STOP_CAPACITY"
    return out


def selector(k, budgets, products, reference, orig):
    o = orig[k]
    q = o.get("scene_query", o["request"].get("scene_query"))
    return dict(backend=MODEL, policy=POLICY, record_id=k, parent_receipt_sha256=PSHA,
                parent_record_sha256=digest(budgets[k]), product_record_sha256=digest(products[k]),
                reference_record_sha256=digest(reference[k]), original_record_sha256=digest(o),
                original_snapshot_sha256=digest(o["scene"]), original_query_sha256=digest(q))


def selected_words(p, z, bound):
    """HOST geometry theorem/selection; no product or RN-cast of an exact sum."""
    words, selected = [], []
    for ax in range(3):
        endpoints = p["products"][2*ax:2*ax+2]
        limbs = [[t["result"][n] for t in ep["terms"] for n in ("hi_word", "lo_word")] for ep in endpoints]
        vals = [sum((sb.frac(w) for w in ws), F(0)) for ws in limbs]
        a, b = (F(*v) for v in z["extrema"]["delta"][ax])
        require(vals == [a*a, b*b], "original_endpoint_squares")
        cross = bound == "lower" and a <= 0 <= b
        side = None if cross else (0 if (vals[0] <= vals[1] if bound == "lower" else vals[0] >= vals[1]) else 1)
        ws = [ZERO]*8 if cross else limbs[side]
        words.extend(ws)
        selected.append(dict(axis=ax, side=side, cross_zero=cross, words=ws))
    return words, selected


def baseline():
    return dict(backend=MODEL, status="STOP_INPUT", reason=None, diagnostic=None,
                RN_nodes_executed=0, HOST_float_casts=0, new_products=0,
                native_root_calls=0, new_transport_calls=0, new_predicate_calls=0,
                retained_suite_replays=0, source_uncertainty_cancelled=False,
                native_length=None, phase_error_bound=None, phase_certified=False,
                wavelength_known=False, physical_reference_certified=False, GPU_used=False,
                full_costs="UNKNOWN_NOT_ZERO", promotion="STOP_LENGTH_PHASE_PHYSICAL_GPU",
                scope="SQUARED_EXTREMA_SUM_ONLY_HOST_SELECTED_ORIGINAL_BOX",
                HOST_preprocessing="ORIGINAL_BOX_ENDPOINT_SELECTION_ALL_RADII_RETAINED")


def _audit(q, budgets, products, reference, orig):
    out = baseline()
    try:
        require(type(q) is dict and type(q.get("record_id")) is str and q["record_id"] in budgets, "closed_record")
        k = q["record_id"]
        require(q == selector(k, budgets, products, reference, orig) and all(type(v) is str for v in q.values()), "closed_selector")
        br, p, z, o = budgets[k]["result"], products[k]["result"], reference[k]["result"].get("diagnostic"), orig[k]
        out.update(request_sha256=digest(q), upstream_status=p["status"],
                   retained_canonical_status=br["status"], retained_canonical_record_sha256=digest(budgets[k]))
        if p["status"] != "CPU64_ORIGINAL_BOX_PRODUCTS_ONLY":
            out.update(status="STOP_UPSTREAM", reason="sealed_STOP_not_rescued")
            return out
        require(products[k]["request"] == sb.prod.selector(k, reference, orig), "product_scene_binding")
        require(z["original_scene"] == o["scene"] and z["original_query"] == o["scene_query"], "original_box_binding")
        require(br["status"] in ("HOST_CANONICAL_PAIR_EXACT_ONLY", "STOP_CANONICAL_PAIR_EXACT_SUM"), "budget_domain")
        sums = []
        for j, bound in enumerate(("lower", "upper")):
            ws, selection = selected_words(p, z, bound)
            r = grow(ws)
            out["RN_nodes_executed"] += r["RN_nodes_executed"]
            sums.append(dict(bound=bound, selection=selection, result=r))
            require(r["status"] == "CPU64_EXACT_GROW_EXPANSION_SUM_ONLY", "native_sum_STOP")
            require(sum((sb.frac(w) for w in r["component_words"]), F(0)) == F(*z["extrema"]["squared"][j]), "native_sum_exact_box")
        out.update(status="CPU64_ORIGINAL_BOX_SQUARED_EXPANSIONS_ONLY", reason="exact_squared_extrema_not_length",
                   diagnostic=dict(sums=sums, squared_original=z["extrema"]["squared"],
                                   original_snapshot_sha256=digest(o["scene"]),
                                   source="SOURCE0", detector="DETECTOR0", units="scene_length_squared",
                                   retained_canonical_residuals=[c["residual"] for c in br["diagnostic"]["candidate_compressions"]]))
    except (ValueError, TypeError, KeyError, IndexError, OSError, OverflowError) as ex:
        out["reason"] = str(ex)
        if "sums" in locals():
            out["diagnostic"] = dict(partial_sums=sums)
    return out


def audit(q):
    try:
        budgets, products, reference, orig, _ = retained()
    except (ValueError, TypeError, KeyError, OSError) as ex:
        out = baseline()
        out["reason"] = "evidence_integrity:" + str(ex)
        return out
    return _audit(q, budgets, products, reference, orig)
