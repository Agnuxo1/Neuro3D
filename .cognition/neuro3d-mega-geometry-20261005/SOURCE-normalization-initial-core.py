"""Opt-in actual CPython CPU64 SOURCE ingress observation, NOT GPU evidence."""
from fractions import Fraction as F
import hashlib
import json
import math
import struct
import sys

MODEL = "original-SOURCE-normalization-CPU64-v1"
GRAPH = "cast_exact_inputs;mul_xx;mul_yy;mul_zz;add_xy;add_z;math.sqrt;div_xyz"


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                    allow_nan=False).encode()).hexdigest()


def rational(value):
    need(type(value) is list and len(value) == 2
         and all(type(x) is int for x in value), "typed rational")
    n, d = value
    need(d > 0 and max(abs(n).bit_length(), d.bit_length()) <= 128, "bounded rational")
    q = F(n, d)
    need([q.numerator, q.denominator] == value and abs(q) <= 10**6, "canonical rational")
    return q


def exact_float(value):
    q = rational(value)
    v = float(q)
    need(math.isfinite(v) and F.from_float(v) == q, "STOP_INPUT_CAST_LOSS")
    return v


def word(value):
    return struct.pack(">d", value).hex()


def observe(scene, query, scene_sha256, query_sha256):
    """Atomic: every SOURCE checked before any record is returned.
    Original scene/query are inputs, never computed hit/length/phase substitutes.
    Signed unit defect is exact arithmetic on CPU-emitted words, NOT angular
    error vs ideal normalized direction or total optical phase.
    """
    out = dict(model=MODEL, status="STOP", reason=None, records=[], graph=GRAPH,
               scope="ACTUAL_CPU64_SOURCE_INGRESS_ONLY", GPU_used=False,
               Bpy_used=False, RT_used=False, SOURCE_merged=False,
               native_GPU_precision_certified=False, ideal_direction_error_bound=None,
               native_phase_bound_rad=None, original_pointwise_budget_certified=False,
               current_GPU_admission=False, full_costs="UNKNOWN_NOT_ZERO")
    try:
        need(sys.implementation.name == "cpython" and sys.float_info.radix == 2
             and sys.float_info.mant_dig == 53 and sys.float_info.max_exp == 1024,
             "CPython binary64 runtime required")
        need(type(scene) is dict and set(scene) == {"schema", "units", "sources", "triangles"}
             and scene["schema"] == "precision-oblique-declared-scene-v1"
             and scene["units"] == "BU", "declared original scene schema")
        need(digest(scene) == scene_sha256 and digest(query) == query_sha256,
             "scene/query content pin mismatch")
        need(query["original_scene_sha256"] == scene_sha256, "query original scene link")
        need(type(scene["sources"]) is list and len(scene["sources"]) == 2
             and [s["id"] for s in scene["sources"]] == query["source_ids"] == ["S0", "S1"],
             "ordered separate original SOURCE channels")
        rows = []
        for s in scene["sources"]:
            need(type(s) is dict and set(s) == {"id", "position_BU", "direction"}, "closed SOURCE")
            need(type(s["position_BU"]) is list and len(s["position_BU"]) == 3
                 and type(s["direction"]) is list and len(s["direction"]) == 3, "SOURCE vector3")
            p = [exact_float(v) for v in s["position_BU"]]
            d = [exact_float(v) for v in s["direction"]]
            xx, yy, zz = d[0]*d[0], d[1]*d[1], d[2]*d[2]
            xy = xx+yy
            squared = xy+zz
            norm = math.sqrt(squared)
            need(math.isfinite(norm) and norm > 0, "nonzero finite SOURCE norm")
            unit = [v/norm for v in d]
            need(all(math.isfinite(v) for v in unit), "finite normalized SOURCE")
            defect = F(1) - sum((F.from_float(v)**2 for v in unit), F(0))
            rows.append(dict(source_id=s["id"], scene_sha256=scene_sha256,
                             query_sha256=query_sha256, position_words_hex=[word(v) for v in p],
                             direction_input_words_hex=[word(v) for v in d],
                             scalar_graph_words_hex={k:word(v) for k,v in
                                 (("xx",xx),("yy",yy),("zz",zz),("xy",xy),
                                  ("squared",squared),("sqrt",norm))},
                             normalized_direction_words_hex=[word(v) for v in unit],
                             one_minus_exact_word_norm_squared=[str(defect.numerator),str(defect.denominator)],
                             SOURCE_position_input_loss_BU=["0","1"]))
        out.update(status="CPU64_SOURCE_WORDS_OBSERVED_ONLY", records=rows,
                   runtime=dict(implementation=sys.implementation.name,
                                python_version=sys.version.split()[0],byteorder=sys.byteorder,
                                float_mant_dig=sys.float_info.mant_dig),
                   root_calls=len(rows))
    except (ValueError, KeyError, TypeError, IndexError, OverflowError) as ex:
        out["reason"] = str(ex)
    return out
