"""Opt-in exact axial one-mirror departure, CPU kinematics only. No bias/material defaults."""
from copy import deepcopy
from fractions import Fraction as F
import math
import axial_scene_candidates_exact_CPU_v1 as root
MODEL = "precision-axial-scene-departure-CPU-v1"
class DepartureStop(ValueError): pass

def cast_gate(rows):
    if not rows: raise DepartureStop("departure_miss_NOT_escape_certificate")
    if any(not math.isfinite(r["distance_float64_BU"]) or r["distance_float64_BU"] <= 0 for r in rows):
        raise DepartureStop("departure_positive_finite_float64_required")
    ex = min(F(*r["distance_rational_BU"]) for r in rows)
    fp = min(r["distance_float64_BU"] for r in rows)
    exact_min = sorted(r["primitive_id"] for r in rows if F(*r["distance_rational_BU"]) == ex)
    float_min = sorted(r["primitive_id"] for r in rows if r["distance_float64_BU"] == fp)
    exact_band = sorted(r["primitive_id"] for r in rows if F(*r["distance_rational_BU"])-ex <= F(root.tie.TIE_BU))
    float_band = sorted(r["primitive_id"] for r in rows if abs(r["distance_float64_BU"]-fp) <= root.tie.TIE_BU)
    return {"exact_minimum_ids": exact_min, "float64_minimum_ids": float_min,
            "exact_band_ids": exact_band, "float64_band_ids": float_band}

def prepare_departures(scene, requests, *, model):
    out = {"model": MODEL, "status": "STOP", "reason": None, "scene_sha256": None,
           "root_evidence": None, "departures": [], "emitted_paths": [],
           "departure_queries": 0, "branch_queries": 0, "origin_bias_BU": [0,1],
           "origin": "EXACT_RATIONAL_AXIAL_ONE_MIRROR_CPU_KINEMATICS",
           "GPU_executed": False, "native_promotion_allowed": False,
           "physical_scene_authenticated": False, "native_hit_coverage_certified": False,
           "length_reference_phase_bound_certified": False, "full_field_certified": False,
           "mirror_material_certified": False, "full_costs": "UNMEASURED_NOT_ZERO"}
    try:
        if type(model) is not str or model != MODEL: raise DepartureStop("explicit_model_required")
        scene, requests = deepcopy(scene), deepcopy(requests)
        sha, manifest, triangles, sources = root.bound_scene(scene)
        out["scene_sha256"] = sha
        if type(requests) is not list or len(requests) != len(sources):
            raise DepartureStop("one_explicit_request_per_SOURCE")
        for req, (sid, _, _) in zip(requests, sources):
            root.closed(req, ("scene_sha256", "source_id", "departure_event"))
            if req["scene_sha256"] != sha or req["source_id"] != sid:
                raise DepartureStop("ordered_scene_SOURCE_binding")
            if type(req["departure_event"]) is not str or req["departure_event"] != "mirror":
                raise DepartureStop("explicit_kinematic_mirror_only")
        # prepare() has no Branch.query calls. No old writer, nearest/history or readback.
        roots = root.prepare(scene, model=root.MODEL)
        out["root_evidence"] = roots
        if roots["status"] == "STOP": raise DepartureStop("root_STOP:"+roots["reason"])
        pending = []
        for record, (sid, origin, direction) in zip(roots["sources"], sources):
            prior = record["root_tie_policy"]["selected_primitive"]
            hit = next(r for r in record["hits"] if r["primitive_id"] == prior)
            t = F(*hit["distance_rational_BU"])
            n = tuple(F(*p) for p in hit["normal_rational"])
            n2 = root.geom.dot(n,n)
            # Exact reflection equation; axial unit directions remain exactly unit.
            reflected = root.geom.sub(direction, tuple(2*root.geom.dot(direction,n)*x/n2 for x in n))
            if root.geom.dot(reflected,reflected) != 1:
                raise DepartureStop("reflected_exact_unit_required")
            point = tuple(o+t*d for o,d in zip(origin,direction))
            departure = {"source_id": sid, "previous_primitive_id": prior,
                         "departure_event": "mirror", "origin_rational_BU": [root.pair(x) for x in point],
                         "direction_rational": [root.pair(x) for x in reflected],
                         "root_distance_rational_BU": root.pair(t),
                         "visited": [], "hits": [], "excluded_zero_ids": []}
            out["departures"].append(departure); out["departure_queries"] += 1
            for pid, tri in enumerate(triangles):
                val = root.geom.intersection(point, reflected, tri)
                if val is None:
                    departure["visited"].append({"primitive_id":pid,"classification":"miss"}); continue
                distance, normal = val
                if distance < 0:
                    departure["visited"].append({"primitive_id":pid,"classification":"behind_departure"}); continue
                if distance == 0:
                    if pid != prior: raise DepartureStop("different_primitive_zero_contact")
                    # Only same exact hit point, proven prior primitive, transverse outgoing ray.
                    if root.geom.dot(reflected,normal) == 0:
                        raise DepartureStop("previous_departure_not_transverse")
                    departure["visited"].append({"primitive_id":pid,"classification":"proven_previous_zero_departure"})
                    departure["excluded_zero_ids"].append(pid); continue
                departure["visited"].append({"primitive_id":pid,"classification":"positive_hit"})
                departure["hits"].append({"primitive_id":pid,"distance_rational_BU":root.pair(distance),
                    "distance_float64_BU":float(distance),"normal_canonical":[float(x!=0) for x in normal]})
            if departure["excluded_zero_ids"] != [prior]:
                raise DepartureStop("previous_exact_zero_proof_missing")
            sets = cast_gate(departure["hits"]); departure.update(sets)
            if sets["exact_minimum_ids"] != sets["float64_minimum_ids"]:
                raise DepartureStop("departure_float64_minimum_set_changed")
            if sets["exact_band_ids"] != sets["float64_band_ids"]:
                raise DepartureStop("departure_float64_tie_band_changed")
            candidates = [{"primitive_id":r["primitive_id"],"distance_BU":r["distance_float64_BU"],
                           "normal":r["normal_canonical"]} for r in departure["hits"]]
            policy = root.tie.resolve_candidates(snapshot_sha256=sha, manifest=manifest, candidates=candidates,
                       previous={"snapshot_sha256":sha,"primitive_id":prior,"departure_event":"mirror"})
            departure["tie_policy"] = policy
            if policy["action"] != "continue": raise DepartureStop("departure_tie_policy:"+policy["reason"])
            winner = next(r for r in departure["hits"] if r["primitive_id"] == policy["selected_primitive"])
            gap = F(*winner["distance_rational_BU"])
            endpoint = tuple(p+gap*d for p,d in zip(point,reflected))
            # Exact reduced two-segment geometric length, NOT optical/reference/phase bound.
            pending.append({"scene_sha256":sha,"source_id":sid,"branch_id":sid+"/mirror",
                "primitive_ids":[prior,winner["primitive_id"]],"endpoint_rational_BU":[root.pair(x) for x in endpoint],
                "segments_rational_BU":[root.pair(t),root.pair(gap)],"length_rational_BU":root.pair(t+gap)})
        # All SOURCE roots and departures validated before emitting ANY accepted path.
        out["emitted_paths"] = pending
        out["status"] = "CPU_AXIAL_ONE_MIRROR_GEOMETRY_ONLY"
    except (ValueError,TypeError,KeyError,OverflowError) as exc:
        out["reason"] = str(exc) if isinstance(exc,DepartureStop) else "closed_geometry:"+type(exc).__name__
    return out
