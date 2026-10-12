"""Successor functions for defects reproduced in the v1 support kit.

The v1 modules stay byte-identical. Each function below names the v1 defect
it addresses; test_closure_v2.py reproduces the defect and the correction.
Scope is unchanged: exact represented inputs only, no native Blender, GPU,
fabrication, or Maxwell claim.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path
import sys
from typing import Iterable, Sequence

from closure_coherent import coherent_sum
from closure_evidence import check_pins
from closure_reference import (Interval, complex_product, pi_interval,
    _cross, _dot, _sub, _trig_at_rational, _vector)


def coherent_sum_v2(values: Iterable[complex], method: str = "fsum") -> complex:
    """v1 lets math.fsum raise OverflowError; v2 maps every overflow to ValueError."""
    try:
        return coherent_sum(values, method)
    except OverflowError as exc:
        raise ValueError("Reduction overflow is not a valid field") from exc


def tighten(value: Interval, bits: int = 160) -> Interval:
    """Round endpoints outward to a 2**-bits grid so rational sizes stay bounded.

    v1 keeps exact rational endpoints; through Machin pi and Taylor series their
    denominators reach tens of thousands of bits, so chained stages slow down
    super-linearly. Outward rounding preserves inclusion at a declared cost.
    """
    if not 8 <= bits <= 1024:
        raise ValueError("8..1024 grid bits are required")
    scale = 1 << bits
    lo, hi = value.lo*scale, value.hi*scale
    lower = lo.numerator//lo.denominator
    upper = -((-hi.numerator)//hi.denominator)
    return Interval(Fraction(lower, scale), Fraction(upper, scale))


def _taylor_terms(x: Fraction, bits: int) -> int:
    """Smallest v1 term count whose remainder bound is at most 2**-bits."""
    threshold, ax = Fraction(1, 1 << bits), abs(x)
    power, factorial = ax**17, Fraction(355687428096000)  # 17! for terms=8
    for terms in range(8, 65):
        if power/factorial <= threshold:
            return terms
        power *= ax*ax
        factorial *= (2*terms+2)*(2*terms+3)
    return 64


def unit_phasor_v2(phase: Interval, bits: int = 160) -> tuple[Interval, Interval]:
    """Enclose exp(i*phase) with bounded endpoint sizes and adaptive Taylor order."""
    if not 32 <= bits <= 480:
        raise ValueError("32..480 bits are required")
    period = tighten(2*pi_interval(min(512, bits+32)), bits+16)
    turns = round(phase.midpoint/period.midpoint)
    reduced = tighten(phase-turns*period, bits+16)
    if reduced.radius >= 2 or abs(reduced.midpoint) > 4:
        return Interval(-1, 1), Interval(-1, 1)
    x = reduced.midpoint
    c, s = _trig_at_rational(x, _taylor_terms(x, bits+8))
    e = reduced.radius  # sine and cosine are 1-Lipschitz.
    def clamp(v: Interval) -> Interval:
        return tighten(Interval(max(Fraction(-1), v.lo-e), min(Fraction(1), v.hi+e)), bits)
    return clamp(c), clamp(s)


def coherent_field_v2(paths: Iterable[tuple[tuple[Interval, Interval], Interval]],
                      bits: int = 160) -> tuple[Interval, Interval]:
    """Sum enclosed complex path amplitudes, tightening after every operation."""
    real, imag = Interval.point(0), Interval.point(0)
    for amplitude, phase in paths:
        r, i = complex_product(amplitude, unit_phasor_v2(phase, bits))
        real, imag = tighten(real+r, bits), tighten(imag+i, bits)
    return real, imag


def exact_first_hit_v2(origin: Sequence, direction: Sequence, triangles: Sequence[dict]) -> dict:
    """First hit where degenerate/coplanar primitives block only when they could interfere.

    v1 returns UNKNOWN as soon as it meets any degenerate or coplanar primitive,
    even one behind the origin or beyond a proven nearer hit. The ray parameter
    t(p) = (p-o).d/|d|^2 is linear on a triangle, so any hit lies inside the exact
    range of its vertex projections. A deferred primitive blocks a result only
    if that range meets [0, t_best]. Everything else follows v1 unchanged, and
    UNKNOWN results list primitive_ids (v1 used a single primitive_id).
    """
    o, d = _vector(origin), _vector(direction)
    dd = _dot(d, d)
    if dd == 0:
        raise ValueError("A nonzero direction is required")
    identifiers = [str(t["primitive_id"]) for t in triangles]
    if len(set(identifiers)) != len(identifiers):
        raise ValueError("Primitive identifiers must be unique")
    hits, deferred = [], []
    for triangle, pid in zip(triangles, identifiers):
        vertices = triangle["vertices"]
        if len(vertices) != 3:
            raise ValueError("Three vertices per triangle are required")
        a, b, c = (_vector(x) for x in vertices)
        projections = [_dot(_sub(v, o), d)/dd for v in (a, b, c)]
        e1, e2 = _sub(b, a), _sub(c, a)
        normal = _cross(e1, e2)
        if _dot(normal, normal) == 0:
            deferred.append((min(projections), max(projections), pid, "DEGENERATE_TRIANGLE"))
            continue
        p = _cross(d, e2)
        determinant = _dot(e1, p)
        if determinant == 0:
            if _dot(normal, _sub(o, a)) == 0:
                deferred.append((min(projections), max(projections), pid, "COPLANAR_QUERY"))
            continue
        delta = _sub(o, a)
        u = _dot(delta, p)/determinant
        q = _cross(delta, e1)
        v = _dot(d, q)/determinant
        t = _dot(e2, q)/determinant
        if t >= 0 and u >= 0 and v >= 0 and u+v <= 1:
            hits.append((t, pid, str(triangle["object_id"]), a, normal))
    best = min(h[0] for h in hits) if hits else None
    blocking = [x for x in deferred if x[1] >= 0 and (best is None or x[0] <= best)]
    if blocking:
        return {"status": "UNKNOWN", "reason": blocking[0][3],
                "primitive_ids": sorted(x[2] for x in blocking)}
    if not hits:
        return {"status": "MISS"}
    tied = [h for h in hits if h[0] == best]
    if best == 0:
        return {"status": "UNKNOWN", "reason": "LAUNCH_CONTACT", "primitive_ids": [h[1] for h in tied]}
    reference = tied[0]
    same_surface = all(h[2] == reference[2] and _cross(h[4], reference[4]) == (0, 0, 0)
                       and _dot(reference[4], _sub(h[3], reference[3])) == 0 for h in tied)
    if not same_surface:
        return {"status": "UNKNOWN", "reason": "DISTINCT_SURFACE_TIE", "primitive_ids": [h[1] for h in tied]}
    return {"status": "HIT", "parameter": best, "object_id": reference[2],
            "primitive_ids": sorted(h[1] for h in tied),
            "point": tuple(o[j]+best*d[j] for j in range(3))}


FRONTIER_IDS = ("F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9")
EXTERNAL_ONLY = {"F5", "F9"}  # PASS needs evidence produced by people outside the project.


def verify_frontier(root, document: dict) -> dict:
    """Check the frontier manifest the same way v1 checks the eleven fronts.

    F5 (independent replication) and F9 (adoption) additionally require an
    external_evidence_record pinned in the repository: an agent cannot mark
    them PASS from its own runs.
    """
    if document.get("schema") != "neuro3d.frontier.manifest.v1":
        raise ValueError("Unsupported frontier schema")
    objectives = document.get("objectives", [])
    if not isinstance(objectives, list) or any(not isinstance(x, dict) for x in objectives):
        raise ValueError("Objectives must be dictionaries")
    if sorted(str(x.get("id")) for x in objectives) != sorted(FRONTIER_IDS):
        raise ValueError("Exactly the frontier fronts F1..F9 are required")
    states = {"PASS", "PARTIAL", "OPEN", "BLOCKED", "NOT_APPLICABLE"}
    failures, unresolved = [], []
    for objective in objectives:
        oid, state = objective["id"], objective.get("state")
        if state not in states:
            failures.append({"id": oid, "reason": "INVALID_STATE"})
            continue
        if state == "NOT_APPLICABLE":
            if not objective.get("scope_reason"):
                failures.append({"id": oid, "reason": "UNEXPLAINED_SCOPE_EXCLUSION"})
            continue
        if state != "PASS":
            unresolved.append({"id": oid, "state": state, "remaining": objective.get("remaining", [])})
            continue
        pins = objective.get("pins", {})
        needed = ["scientific_verifier_record"] + (["external_evidence_record"] if oid in EXTERNAL_ONLY else [])
        if objective.get("remaining") or any(not objective.get(k) or objective[k] not in pins for k in needed):
            failures.append({"id": oid, "reason": "PASS_WITHOUT_PINNED_VERIFIER_OR_EXTERNAL_EVIDENCE"})
            continue
        failures.extend({"id": oid, **x} for x in check_pins(root, pins) if x["status"] != "PASS")
    return {"schema": "neuro3d.frontier.integrity.v1", "failures": failures, "unresolved": unresolved,
            "integrity_pass": not failures, "all_frontier_fronts_pass": not failures and not unresolved,
            "scope": "Manifest integrity only; it never certifies scientific importance or recognition"}


def main() -> int:
    """Check the frontier manifest; exit 2 while any front is unresolved."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    try:
        report = verify_frontier(args.repo, json.loads(args.manifest.read_text(encoding="utf-8")))
    except (OSError, ValueError, KeyError) as exc:
        print(json.dumps({"status": "BLOCKED", "reason": str(exc)}), file=sys.stderr)
        return 3
    print(json.dumps(report, indent=2))
    return 0 if report["all_frontier_fronts_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
