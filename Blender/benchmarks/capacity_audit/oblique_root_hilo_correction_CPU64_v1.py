"""Native hi-lo correction of sealed sqrt seeds; HOST bound, not full scene engine."""
from pathlib import Path
from fractions import Fraction as F
import json, struct
import oblique_expansion_root_cert_CPUHOST_v1 as prior
exp = prior.exp
prod = exp.sb.prod
ROOT = Path(__file__).resolve().parents[3]
MODEL = "oblique-root-hilo-correction-CPU64-v1"
POLICY = "SEALED_SEED_EFT_SQUARE_FIXED4_RESIDUAL_NATIVE_DELTA_HOST_BOUND"
PARENT = "coordinacion/respuestas/PRECISION-OBLIQUE-EXPANSION-ROOT-CERT-CPUHOST-001-CODEX.json"
PSHA = "443b99eed81223011ddb0c910a4d13c43d640e164131c6b6c9c5a5a58baf0645"
require, sha, capture, digest, pair, word = prior.require, prior.sha, prior.capture, prior.digest, prior.pair, prior.word


def retained():
    raw = (ROOT/PARENT).read_bytes()
    require(len(raw) == 144195 and sha(raw) == PSHA, "parent_seal")
    r = json.loads(raw)
    pins = dict(r["code_doc_sha256"])
    require(len(pins) == 288, "parent_pins")
    for p,h in pins.items():
        require(sha((ROOT/p).read_bytes()) == h, "dependency:"+p)
    require(capture(r["independent_pre"])["status"] == "PASS", "parent_oracle")
    d = capture(r["test_run"])["evidence"]
    e = {x["id"]:x for x in d["records"]}
    expansions, reference, orig, _ = prior.retained()
    require(set(e) == set(expansions) == set(reference) == set(orig) and len(e) == 16, "closed_records")
    pins[PARENT] = PSHA
    return e, expansions, reference, orig, pins, d


def negate_word(w):
    return (int.from_bytes(bytes.fromhex(w),"little") ^ (1<<63)).to_bytes(8,"little").hex()


def refine(words, seed_word, lower_word):
    out = dict(status="STOP_INPUT", reason=None, input_words=words, seed_word=seed_word,
               lower_word=lower_word, square=None, residual=None, negated_square_words=None,
               scalar_ledger=[], root_pair_words=None, candidate_pair_words=None,
               exact_squared=None, candidate_sum=None, candidate_squared_residual=None,
               length_error_bound=None, HOST_enclosure=None, RN_nodes_executed=0,
               new_products=0, new_sums=0, new_sqrt_calls=0, HOST_float_casts=0,
               HOST_bound_divisions=0, full_costs="UNKNOWN_NOT_ZERO")
    try:
        require(type(words) is list and 1 <= len(words) <= 4, "fixed4_expansion_input")
        xs = [exp.decode(w) for w in words]
        Y,L = exp.decode(seed_word), exp.decode(lower_word)
        S = sum((F.from_float(x) for x in xs),F(0))
        require(0 < S <= 2**66 and 0 < Y <= 2**32 and 0 < L <= Y and F.from_float(L)**2 <= S,
                "positive_seed_existing_product_domain_and_lower")
        out["exact_squared"] = pair(S)
        p = prod.product(Y,Y)
        out.update(square=p, new_products=1, RN_nodes_executed=p["RN_nodes_executed"])
        require(p["status"] == "CPU64_EFT_PRODUCT_ONLY", "square_STOP:"+str(p["reason"]))
        negatives = [negate_word(p[n]) for n in ("hi_word","lo_word")]
        out["negated_square_words"] = negatives
        residual = exp.grow(words+negatives)
        out.update(residual=residual, new_sums=1,
                   RN_nodes_executed=out["RN_nodes_executed"]+residual["RN_nodes_executed"])
        require(residual["status"] == "CPU64_EXACT_GROW_EXPANSION_SUM_ONLY", "residual_fixed4_STOP")
        R = sum((exp.sb.frac(w) for w in residual["component_words"]),F(0))
        require(R == S-F.from_float(Y)**2, "native_residual_exact")

        def rn(name,op,a,b):
            exact = F.from_float(a)*F.from_float(b) if op=="mul" else F.from_float(a)/F.from_float(b)
            v = a*b if op=="mul" else a/b
            out["scalar_ledger"].append(dict(index=len(out["scalar_ledger"]), name=name, op=op,
                                             a=word(a), b=word(b), y=word(v)))
            out["RN_nodes_executed"] += 1
            require(prod.normal(v) and abs(v) <= 2**33 and (v != 0.0 or exact == 0),
                    "scalar_normal_bounded_no_underflow:"+name)
            return v

        denominator = rn("denominator","mul",2.0,Y)
        Rhi = exp.decode(residual["component_words"][-1])
        delta = rn("delta","div",Rhi,denominator)
        Q = F.from_float(Y)+F.from_float(delta)
        out.update(candidate_pair_words=[seed_word,word(delta)], candidate_sum=pair(Q),
                   candidate_squared_residual=pair(S-Q*Q))
        require(0 < Q <= 2**33 and F.from_float(L)**2 <= Q*Q, "common_lower_candidate_certificate")
        budget = abs(S-Q*Q)/(2*F.from_float(L))
        out.update(status="CPU64_NATIVE_ROOT_PAIR_HOST_BOUND_ONLY", reason="one_native_correction_not_engine",
                   root_pair_words=[seed_word,word(delta)], length_error_bound=pair(budget),
                   HOST_enclosure=[pair(Q-budget),pair(Q+budget)], HOST_bound_divisions=1)
    except (ValueError,TypeError,OverflowError,ZeroDivisionError) as ex:
        out["reason"] = str(ex)
    return out


def selector(k,e,expansions,reference,orig):
    o = orig[k]
    q = o.get("scene_query",o["request"].get("scene_query"))
    return dict(backend=MODEL,policy=POLICY,record_id=k,parent_receipt_sha256=PSHA,
                parent_record_sha256=digest(e[k]),expansion_record_sha256=digest(expansions[k]),
                reference_record_sha256=digest(reference[k]),original_record_sha256=digest(o),
                original_snapshot_sha256=digest(o["scene"]),original_query_sha256=digest(q))


def baseline():
    return dict(backend=MODEL,status="STOP_INPUT",reason=None,diagnostic=None,RN_nodes_executed=0,
                new_products=0,new_sums=0,new_sqrt_calls=0,HOST_float_casts=0,retained_suite_replays=0,
                native_length=None,phase_error_bound=None,phase_certified=False,wavelength_known=False,
                physical_reference_certified=False,GPU_used=False,source_uncertainty_cancelled=False,
                full_costs="UNKNOWN_NOT_ZERO",promotion="STOP_NATIVE_SCENE_ENGINE_PHASE_PHYSICAL_GPU",
                scope="NATIVE_PAIR_CORRECTION_OF_SEALED_SEED_HOST_BOUND_ORIGINAL_BOX_ONLY")


def _audit(q,e,expansions,reference,orig):
    out = baseline()
    try:
        require(type(q) is dict and type(q.get("record_id")) is str and q["record_id"] in e,"closed_record")
        k = q["record_id"]
        require(q == selector(k,e,expansions,reference,orig) and all(type(v) is str for v in q.values()),"closed_selector")
        p,z,o = e[k]["result"],reference[k]["result"].get("diagnostic"),orig[k]
        out.update(request_sha256=digest(q),upstream_status=p["status"],
                   retained_canonical_status=p["retained_canonical_status"])
        if p["status"] != "CPU64_ROOT_SEEDS_HOST_ORIGINAL_BOX_LENGTH_CERTIFICATE_ONLY":
            out.update(status="STOP_UPSTREAM",reason="sealed_STOP_not_rescued")
            return out
        require(z["original_scene"] == o["scene"] and z["original_query"] == o["scene_query"],"original_box_binding")
        corrections = []
        out["diagnostic"] = dict(corrections=corrections,original_snapshot_sha256=digest(o["scene"]),
                                 source="SOURCE0",detector="DETECTOR0",units="scene_length")
        for i,x in enumerate(p["diagnostic"]["roots"]):
            root = x["result"]
            require(root["input_words"] == expansions[k]["result"]["diagnostic"]["sums"][i]["result"]["component_words"],
                    "same_sealed_expansion")
            r = refine(root["input_words"],root["seed_word"],root["interval_words"][0])
            corrections.append(dict(bound=x["bound"],result=r))
            for n in ("RN_nodes_executed","new_products","new_sums"):out[n] += r[n]
            require(r["status"] == "CPU64_NATIVE_ROOT_PAIR_HOST_BOUND_ONLY","native_pair_correction_STOP")
            require(r["exact_squared"] == z["extrema"]["squared"][i],"same_original_squared")
        a,b = (x["result"] for x in corrections)
        low,high = F(*a["HOST_enclosure"][0]),F(*b["HOST_enclosure"][1])
        rw = F(*z["reference_width"])
        budget = max(F(*a["length_error_bound"]),F(*b["length_error_bound"]))
        require(0 < low <= high and rw > 0,"positive_bound_interval")
        out["diagnostic"].update(HOST_corrected_length_interval=[pair(low),pair(high)],
            interval_width=pair(high-low),reference_interval=z["reference_interval"],reference_width=z["reference_width"],
            width_over_reference=pair((high-low)/rw),max_pair_length_error_bound=pair(budget),
            error_bound_over_reference_width=pair(budget/rw),HOST_ratio_divisions=2,
            retained_seed_interval_width=p["diagnostic"]["interval_width"],
            retained_seed_width_over_reference=p["diagnostic"]["width_over_reference"])
        out.update(status="CPU64_SEALED_ROOT_PAIR_CORRECTIONS_HOST_BOUNDS_ONLY",
                   reason="paired_native_correction_host_bound_not_scene_engine")
    except (ValueError,TypeError,KeyError,IndexError,OSError,OverflowError) as ex:out["reason"] = str(ex)
    return out


def audit(q):
    try:e,expansions,reference,orig,_,_ = retained()
    except (ValueError,TypeError,KeyError,OSError) as ex:
        out = baseline();out["reason"] = "evidence_integrity:"+str(ex);return out
    return _audit(q,e,expansions,reference,orig)
