"""CPU64 sqrt seed + explicit HOST rational certificate; NOT native length engine."""
from pathlib import Path
from fractions import Fraction as F
import json, math, struct
import oblique_scene_squared_expansion_CPU64_v1 as exp
ROOT = Path(__file__).resolve().parents[3]
MODEL = "oblique-expansion-root-cert-CPUHOST-v1"
POLICY = "SEALED_EXPANSION_NATIVE_SQRT_SEED_HOST_IEEE_FIXED2_CERT"
PARENT = "coordinacion/respuestas/PRECISION-OBLIQUE-SQUARED-EXPANSION-CPU-001-CODEX.json"
PSHA = "11cf94df8acf19163cbd6a6dc01628ae8e3160bf85527f144368b362dab685e7"
MAX_STEPS = 2
require, sha, capture, digest, pair, word = exp.require, exp.sha, exp.capture, exp.digest, exp.pair, exp.word


def retained():
    raw = (ROOT/PARENT).read_bytes()
    require(len(raw) == 151262 and sha(raw) == PSHA, "parent_seal")
    r = json.loads(raw)
    pins = dict(r["code_doc_sha256"])
    require(len(pins) == 284, "parent_pins")
    for p, h in pins.items():
        require(sha((ROOT/p).read_bytes()) == h, "dependency:"+p)
    require(capture(r["independent_pre"])["status"] == "PASS", "parent_oracle")
    d = capture(r["test_run"])["evidence"]
    e = {x["id"]: x for x in d["records"]}
    _, _, reference, orig, _ = exp.retained()
    require(set(e) == set(reference) == set(orig) and len(e) == 16, "closed_records")
    pins[PARENT] = PSHA
    return e, reference, orig, pins


def root(words):
    out = dict(status="STOP_INPUT", reason=None, input_words=words, max_steps_per_side=MAX_STEPS,
               sqrt_calls=0, seed_input_word=None, seed_word=None, interval_words=None,
               partial_interval_words=None, HOST_bit_steps=[], HOST_checks=[],
               exact_squared=None, seed_squared_residual=None, length_error_bound=None,
               HOST_float_casts=0, HOST_bound_divisions=0, engine_native_length=False)
    try:
        require(type(words) is list and 1 <= len(words) <= 4, "fixed4_expansion_input")
        xs = [exp.decode(w) for w in words]
        S = sum((F.from_float(x) for x in xs), F(0))
        require(0 < S <= 2**66 and xs[-1] > 0, "positive_total_and_seed_domain")
        out.update(exact_squared=pair(S), seed_input_word=words[-1])
        y = math.sqrt(xs[-1])
        out.update(sqrt_calls=1, seed_word=word(y))
        require(exp.sb.prod.normal(y) and y > 0, "normal_positive_root_seed")
        lo = hi = word(y)
        out["partial_interval_words"] = [lo, hi]
        for side in ("lower", "upper"):
            candidate, steps = word(y), 0
            while True:
                v = F.from_float(struct.unpack("<d", bytes.fromhex(candidate))[0])
                holds = v*v <= S if side == "lower" else v*v >= S
                out["HOST_checks"].append(dict(side=side, candidate_word=candidate,
                                               square=pair(v*v), holds=holds))
                if holds:
                    break
                require(steps < MAX_STEPS, "fixed2_enclosure_capacity")
                bits = int.from_bytes(bytes.fromhex(candidate), "little")
                newbits = bits-1 if side == "lower" else bits+1
                require(0 < newbits < 0x7ff0000000000000, "positive_finite_neighbor")
                nxt = newbits.to_bytes(8, "little").hex()
                out["HOST_bit_steps"].append(dict(side=side, from_word=candidate, to_word=nxt,
                                                 integer_delta=-1 if side == "lower" else 1))
                candidate = nxt
                steps += 1
                if side == "lower": lo = candidate
                else: hi = candidate
                out["partial_interval_words"] = [lo, hi]
            if side == "lower": lo = candidate
            else: hi = candidate
        L, U, Y = exp.sb.frac(lo), exp.sb.frac(hi), F.from_float(y)
        require(0 < L <= U and L*L <= S <= U*U and L*L <= Y*Y, "positive_common_lower_certificate")
        residual = S-Y*Y
        budget = abs(residual)/(2*L)
        out.update(status="CPU64_SEED_HOST_CERTIFIED_EXPANSION_ROOT_ONLY",
                   reason="mixed_certificate_not_native_length",
                   interval_words=[lo, hi], partial_interval_words=[lo, hi],
                   seed_squared_residual=pair(residual), length_error_bound=pair(budget),
                   HOST_bound_divisions=1)
    except (ValueError, TypeError, OverflowError) as ex:
        out["reason"] = str(ex)
        if out["reason"] == "fixed2_enclosure_capacity":
            out["status"] = "STOP_CAPACITY"
    return out


def selector(k, e, reference, orig):
    o = orig[k]
    q = o.get("scene_query", o["request"].get("scene_query"))
    return dict(backend=MODEL, policy=POLICY, record_id=k, parent_receipt_sha256=PSHA,
                parent_record_sha256=digest(e[k]), reference_record_sha256=digest(reference[k]),
                original_record_sha256=digest(o), original_snapshot_sha256=digest(o["scene"]),
                original_query_sha256=digest(q))


def baseline():
    return dict(backend=MODEL, status="STOP_INPUT", reason=None, diagnostic=None, sqrt_calls=0,
                new_sums=0, new_products=0, new_transport_calls=0, new_predicate_calls=0,
                retained_suite_replays=0, HOST_float_casts=0, native_length=None,
                source_uncertainty_cancelled=False, phase_error_bound=None, phase_certified=False,
                wavelength_known=False, physical_reference_certified=False, GPU_used=False,
                full_costs="UNKNOWN_NOT_ZERO", scope="NATIVE_SQRT_SEED_HOST_CERTIFICATE_ORIGINAL_BOX_ONLY",
                promotion="STOP_NATIVE_ENGINE_PHASE_PHYSICAL_GPU")


def _audit(q, e, reference, orig):
    out = baseline()
    try:
        require(type(q) is dict and type(q.get("record_id")) is str and q["record_id"] in e, "closed_record")
        k = q["record_id"]
        require(q == selector(k,e,reference,orig) and all(type(v) is str for v in q.values()), "closed_selector")
        p, z, o = e[k]["result"], reference[k]["result"].get("diagnostic"), orig[k]
        out.update(request_sha256=digest(q), upstream_status=p["status"],
                   retained_canonical_status=p["retained_canonical_status"])
        if p["status"] != "CPU64_ORIGINAL_BOX_SQUARED_EXPANSIONS_ONLY":
            out.update(status="STOP_UPSTREAM", reason="sealed_STOP_not_rescued")
            return out
        require(z["original_scene"] == o["scene"] and z["original_query"] == o["scene_query"], "original_box_binding")
        roots = []
        out["diagnostic"] = dict(roots=roots, original_snapshot_sha256=digest(o["scene"]),
                                 source="SOURCE0", detector="DETECTOR0", units="scene_length")
        for i, entry in enumerate(p["diagnostic"]["sums"]):
            words = entry["result"]["component_words"]
            r = root(words)
            roots.append(dict(bound=entry["bound"], result=r))
            out["sqrt_calls"] += r["sqrt_calls"]
            require(r["status"] == "CPU64_SEED_HOST_CERTIFIED_EXPANSION_ROOT_ONLY", "root_certificate_STOP")
            require(r["exact_squared"] == z["extrema"]["squared"][i], "same_original_box_squared")
        a, b = roots[0]["result"], roots[1]["result"]
        low, high = exp.sb.frac(a["interval_words"][0]), exp.sb.frac(b["interval_words"][1])
        rl, rh = (F(*v) for v in z["reference_interval"])
        width, refwidth = high-low, rh-rl
        require(0 < low <= high and refwidth > 0, "positive_original_length_interval")
        out["diagnostic"].update(HOST_certified_length_interval=[pair(low), pair(high)],
            HOST_certified_words=[a["interval_words"][0], b["interval_words"][1]],
            reference_interval=z["reference_interval"], reference_width=z["reference_width"],
            interval_width=pair(width), width_over_reference=pair(width/refwidth),
            interval_minus_reference=[pair(low-rl), pair(high-rh)],
            max_seed_length_error_bound=pair(max(F(*a["length_error_bound"]), F(*b["length_error_bound"]))),
            HOST_width_ratio_divisions=1)
        out.update(status="CPU64_ROOT_SEEDS_HOST_ORIGINAL_BOX_LENGTH_CERTIFICATE_ONLY",
                   reason="mixed_original_box_certificate_not_native_engine")
    except (ValueError, TypeError, KeyError, IndexError, OSError, OverflowError) as ex:
        out["reason"] = str(ex)
    return out


def audit(q):
    try: e, reference, orig, _ = retained()
    except (ValueError, TypeError, KeyError, OSError) as ex:
        out = baseline()
        out["reason"] = "evidence_integrity:"+str(ex)
        return out
    return _audit(q,e,reference,orig)
