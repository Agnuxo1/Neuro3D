"""Independent bit/rational proof of new fixed4 native sum graphs, no numeric replay."""
from pathlib import Path
from fractions import Fraction as F
import json, hashlib, copy, runpy, struct
ROOT = Path(__file__).resolve().parents[2]
prior = runpy.run_path(str(ROOT / "Blender/tests/test_oblique_scene_squared_pair_budget_HOST.py"))
capture, digest, pair, pf, nearest = (prior[n] for n in ("capture", "digest", "pair", "pf", "nearest"))
MODEL = "oblique-scene-squared-expansion-CPU64-v1"
POLICY = "SEALED_PRODUCTS_HOST_BOX_SELECTION_NATIVE_GROW_FIXED4"
PARENT = "coordinacion/respuestas/PRECISION-OBLIQUE-SQUARED-PAIR-BUDGET-HOST-001-CODEX.json"
PSHA = "743749e2d0b9742c740a54d3cfad25933750a91cb3a73eab4310a8e41d608d1e"
ZERO = "0000000000000000"


def retained():
    raw = (ROOT / PARENT).read_bytes()
    assert len(raw) == 78633 and hashlib.sha256(raw).hexdigest() == PSHA
    r = json.loads(raw)
    pins = dict(r["code_doc_sha256"])
    assert len(pins) == 280
    for p, h in pins.items():
        assert hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == h, p
    d = capture(r["test_run"])["evidence"]
    products, reference, orig, _, _ = prior["retained"]()
    pins[PARENT] = PSHA
    return {x["id"]: x for x in d["records"]}, products, reference, orig, pins, d


def selector(k, budgets, products, reference, orig):
    o = orig[k]
    q = o.get("scene_query", o["request"].get("scene_query"))
    return dict(backend=MODEL, policy=POLICY, record_id=k, parent_receipt_sha256=PSHA,
                parent_record_sha256=digest(budgets[k]), product_record_sha256=digest(products[k]),
                reference_record_sha256=digest(reference[k]), original_record_sha256=digest(o),
                original_snapshot_sha256=digest(o["scene"]), original_query_sha256=digest(q))


def normal_word(w):
    v = pf(w)
    assert v == 0 or abs(v) >= F(1, 2**1022)
    assert abs(v) <= 2**66
    return v


def graph(r, expected):
    assert r["input_words"] == expected and r["max_components"] == 4
    assert r["HOST_float_casts"] == r["native_root_calls"] == 0
    assert r["RN_nodes_executed"] == len(r["ledger"])
    assert 1 <= len(expected) <= 24
    for w in expected:
        normal_word(w)
    ledger, steps = r["ledger"], r["steps"]
    idx = 0

    def node(name, op, aw, bw):
        nonlocal idx
        t = ledger[idx]
        assert (t["index"], t["name"], t["op"], t["a"], t["b"]) == (idx, name, op, aw, bw)
        a, b = normal_word(aw), normal_word(bw)
        exact = a+b if op == "add" else a-b
        y = nearest(t["y"], exact)
        normal_word(t["y"])
        assert y != 0 or exact == 0
        idx += 1
        return t["y"]

    e = []
    for i, step in enumerate(steps):
        assert step["input_index"] == i and step["before"] == e and step["node_start"] == idx
        q, h = expected[i], []
        for j, v in enumerate(e):
            stem = f"grow{i}.term{j}"
            oldq = q
            s = node(stem+".s", "add", q, v)
            bb = node(stem+".bb", "sub", s, q)
            ab = node(stem+".ab", "sub", s, bb)
            db = node(stem+".db", "sub", v, bb)
            da = node(stem+".da", "sub", q, ab)
            err = node(stem+".err", "add", da, db)
            assert pf(s)+pf(err) == pf(oldq)+pf(v)
            q = s
            if pf(err) != 0:
                h.append(err)
        if pf(q) != 0 or not h:
            h.append(q)
        assert step["after"] == h and step["node_end"] == idx
        assert sum((pf(w) for w in h), F(0)) == sum((pf(w) for w in expected[:i+1]), F(0))
        e = h
        assert len(e) <= 4 or i == len(steps)-1
    assert idx == len(ledger) and r["processed_words"] == len(steps)
    assert r["partial_component_words"] == e
    if len(e) > 4:
        assert len(e) == 5 and r["status"] == "STOP_CAPACITY" and r["reason"] == "fixed4_capacity_exceeded"
        assert r["component_words"] is None
    else:
        assert len(steps) == len(expected) and r["status"] == "CPU64_EXACT_GROW_EXPANSION_SUM_ONLY"
        assert r["reason"] == "fixed4_exact_sum_not_root" and r["component_words"] == e
        assert sum((pf(w) for w in e), F(0)) == sum((pf(w) for w in expected), F(0))
    return len(ledger)


def scope(r):
    assert r["backend"] == MODEL and r["full_costs"] == "UNKNOWN_NOT_ZERO"
    assert r["promotion"] == "STOP_LENGTH_PHASE_PHYSICAL_GPU"
    assert r["scope"] == "SQUARED_EXTREMA_SUM_ONLY_HOST_SELECTED_ORIGINAL_BOX"
    assert r["HOST_preprocessing"] == "ORIGINAL_BOX_ENDPOINT_SELECTION_ALL_RADII_RETAINED"
    for n in ("source_uncertainty_cancelled", "phase_certified", "wavelength_known", "physical_reference_certified", "GPU_used"):
        assert r[n] is False
    assert r["native_length"] is None and r["phase_error_bound"] is None
    for n in ("HOST_float_casts", "new_products", "native_root_calls", "new_transport_calls", "new_predicate_calls", "retained_suite_replays"):
        assert r[n] == 0


def verify_capture(d, verify_parent=True):
    budgets, products, reference, orig, pins, old = retained()
    assert d["pins"] == pins
    if verify_parent:
        assert prior["verify_capture"](old)["status"] == "PASS"
    assert len(d["records"]) == 16 and {x["id"] for x in d["records"]} == set(budgets)
    scenes = stops = nodes = 0
    components, by_scene = [], {}
    for x in d["records"]:
        k, r = x["id"], x["result"]
        scope(r)
        assert x["request"] == selector(k, budgets, products, reference, orig)
        assert r["request_sha256"] == digest(x["request"])
        p, br = products[k]["result"], budgets[k]["result"]
        assert r["upstream_status"] == p["status"] and r["retained_canonical_status"] == br["status"]
        assert r["retained_canonical_record_sha256"] == digest(budgets[k])
        if p["status"] != "CPU64_ORIGINAL_BOX_PRODUCTS_ONLY":
            assert r["status"] == "STOP_UPSTREAM" and r["reason"] == "sealed_STOP_not_rescued"
            assert r["diagnostic"] is None and r["RN_nodes_executed"] == 0
            stops += 1
            continue
        assert r["status"] == "CPU64_ORIGINAL_BOX_SQUARED_EXPANSIONS_ONLY" and r["reason"] == "exact_squared_extrema_not_length"
        z, original = r["diagnostic"], orig[k]["scene"]
        box = {}
        for n in ("origin", "detector"):
            box[n] = [(F(*v)-F(*rad), F(*v)+F(*rad)) for v, rad in zip(original["points"][n]["nominal"], original["points"][n]["radius"])]
        delta = [(b[0]-a[1], b[1]-a[0]) for a, b in zip(box["origin"], box["detector"])]
        S = [F(0), F(0)]
        assert len(z["sums"]) == 2 and z["original_snapshot_sha256"] == digest(original)
        assert z["source"] == "SOURCE0" and z["detector"] == "DETECTOR0" and z["units"] == "scene_length_squared"
        assert z["retained_canonical_residuals"] == [c["residual"] for c in br["diagnostic"]["candidate_compressions"]]
        nsum = 0
        counts = []
        for bi, entry in enumerate(z["sums"]):
            bound = ("lower", "upper")[bi]
            assert entry["bound"] == bound and len(entry["selection"]) == 3
            ws = []
            for ax, item in enumerate(entry["selection"]):
                a, b = delta[ax]
                vals = [a*a, b*b]
                cross = bi == 0 and a <= 0 <= b
                side = None if cross else (0 if (vals[0] <= vals[1] if bi == 0 else vals[0] >= vals[1]) else 1)
                limbs = [ZERO]*8 if cross else [t["result"][n] for t in p["products"][2*ax+side]["terms"] for n in ("hi_word", "lo_word")]
                assert item == dict(axis=ax, side=side, cross_zero=cross, words=limbs)
                assert sum((pf(w) for w in limbs), F(0)) == (F(0) if cross else vals[side])
                S[bi] += F(0) if cross else vals[side]
                ws.extend(limbs)
            nsum += graph(entry["result"], ws)
            counts.append(len(entry["result"]["component_words"]))
            components.append(counts[-1])
        assert z["squared_original"] == [pair(v) for v in S] == reference[k]["result"]["diagnostic"]["extrema"]["squared"]
        assert r["RN_nodes_executed"] == nsum
        nodes += nsum
        scenes += 1
        by_scene[k] = dict(components=counts, RN_nodes=nsum, retained_canonical_status=br["status"])
    assert (scenes, stops) == (2, 14)
    assert len(d["invalid"]) == 8
    for x in d["invalid"]:
        r = x["result"]
        scope(r)
        assert r["status"] == "STOP_INPUT" and r["reason"] == "closed_selector" and r["diagnostic"] is None and r["RN_nodes_executed"] == 0
    controls = d["controls"]
    assert len(controls) == 3
    cnodes = sum(graph(r, r["input_words"]) for r in controls)
    assert len(controls[0]["component_words"]) == 3
    assert controls[1]["status"] == "STOP_CAPACITY" and len(controls[1]["partial_component_words"]) == 5
    assert controls[1]["RN_nodes_executed"] == 60
    assert sum((pf(w) for w in controls[2]["component_words"]), F(0)) == 0
    assert len(d["precontrols"]) == 6
    for r in d["precontrols"]:
        assert r["status"] == "STOP_INPUT" and r["component_words"] is None
        assert r["processed_words"] == r["RN_nodes_executed"] == 0 and r["ledger"] == r["steps"] == []
    r = d["bounded_node_STOP"]
    assert r["status"] == "STOP_INPUT" and r["reason"] == "RN_normal_bounded_no_underflow"
    assert r["processed_words"] == 1 and r["component_words"] is None
    assert r["steps"] == [dict(input_index=0, before=[], after=[r["input_words"][0]], node_start=0, node_end=0)]
    assert r["partial_component_words"] == [r["input_words"][0]]
    assert len(r["ledger"]) == r["RN_nodes_executed"] == 1
    t = r["ledger"][0]
    assert (t["index"], t["name"], t["op"], t["a"], t["b"]) == (0, "grow1.term0.s", "add", r["input_words"][0], r["input_words"][1])
    assert nearest(t["y"], pf(t["a"])+pf(t["b"])) == 2**67
    return dict(status="PASS", scenes=scenes, upstream_STOP=stops, native_sums=4,
                max_components=max(components), scene_RN_nodes=nodes, control_RN_nodes=cnodes,
                stopped_node_RN=1, total_new_RN_nodes=nodes+cnodes+1, selectors_rejected=8,
                precontrols=6, fixed5_STOP=True, inherited_pins=len(pins), by_scene=by_scene)


def mutations(d):
    accepted = next(x for x in d["records"] if x["result"]["diagnostic"] is not None)
    k = d["records"].index(accepted)
    rejects = 0
    for n in range(8):
        z = copy.deepcopy(d)
        r = z["records"][k]["result"]
        s = r["diagnostic"]["sums"][0]
        if n == 0: r["retained_canonical_status"] = "PASS"
        elif n == 1: s["result"]["component_words"][0] = ZERO
        elif n == 2: s["selection"][0]["side"] = 7
        elif n == 3: s["result"]["max_components"] = 5
        elif n == 4: s["result"]["ledger"][0]["b"] = ZERO
        elif n == 5: r["source_uncertainty_cancelled"] = True
        elif n == 6: r["diagnostic"]["squared_original"][0] = [0, 1]
        else: z["controls"][1]["status"] = "CPU64_EXACT_GROW_EXPANSION_SUM_ONLY"
        try:
            verify_capture(z, verify_parent=False)
        except (AssertionError, ValueError, TypeError, IndexError, KeyError):
            rejects += 1
        else:
            raise AssertionError("mutation_accepted:" + str(n))
    return rejects


def run():
    import oblique_scene_squared_expansion_CPU64_v1 as core
    budgets, products, reference, orig, pins = core.retained()
    records = []
    for k in budgets:
        q = core.selector(k, budgets, products, reference, orig)
        records.append(dict(id=k, request=q, result=core._audit(q, budgets, products, reference, orig)))
    k = next(x["id"] for x in records if x["result"]["diagnostic"] is not None)
    q = core.selector(k, budgets, products, reference, orig)
    invalid = []
    for n in range(8):
        bad = dict(q)
        if n == 0: bad["policy"] = "increase_capacity"
        elif n == 1: bad["backend"] = "GPU"
        elif n == 2: bad["wavelength"] = "500"
        elif n == 3: bad["parent_receipt_sha256"] = "0"*64
        elif n == 4: bad["original_snapshot_sha256"] = "0"*64
        elif n == 5: bad["product_record_sha256"] = "0"*64
        elif n == 6: bad["record_id"] = 0
        else: bad.pop("original_query_sha256")
        result = core._audit(bad, budgets, products, reference, orig)
        if n == 6:
            assert result["reason"] == "closed_record"
            bad = dict(q, original_query_sha256=0)
            result = core._audit(bad, budgets, products, reference, orig)
        invalid.append(dict(request=bad, result=result))
    w = lambda x: struct.pack("<d", x).hex()
    controls = [core.grow([w(1.0), w(2.0**-60), w(2.0**-120)]),
                core.grow([w(2.0**n) for n in (0, -60, -120, -180, -240)]),
                core.grow([w(1.0), w(-1.0), ZERO])]
    pre = [core.grow(a) for a in ([], [w(float("inf"))], [w(2.0**-1074)], [True], tuple([ZERO]), [w(2.0**67)])]
    stopped = core.grow([w(2.0**66), w(2.0**66)])
    d = dict(records=records, invalid=invalid, controls=controls, precontrols=pre, bounded_node_STOP=stopped, pins=pins)
    result = verify_capture(d)
    result["mutations_rejected"] = mutations(d)
    assert result["mutations_rejected"] == 8
    print(json.dumps(dict(status="PASS", summary=result, evidence=d), sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    run()
