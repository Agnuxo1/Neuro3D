"""Independent first-hit check of EXP-003 disks; no Blender import or writes.

Each ray chooses the nearest hit among all optical disks, so this catches
cross-occlusions that an ordered path oracle would miss.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
import sys

DISKS = ("bs1", "r1", "r2", "f1", "m2", "bs2")
ARM1 = ("r1", "r2", "f1", "bs2")
ARM2 = ("m2", "bs2")


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def mul(a, scalar):
    return tuple(x * scalar for x in a)


def reflect(direction, normal):
    return sub(direction, mul(normal, 2 * dot(direction, normal)))


def first_hit(origin, direction, disks, previous=None):
    hits = []
    for name, (centre, normal, radius) in disks.items():
        if name == previous:
            continue
        den = dot(direction, normal)
        if abs(den) < 1e-12:
            continue
        distance = dot(sub(centre, origin), normal) / den
        if distance <= 1e-8:
            continue
        point = add(origin, mul(direction, distance))
        if math.dist(point, centre) <= radius + 1e-12:
            hits.append((distance, name, point))
    return min(hits) if hits else None


def trace(fixture, delay_d=0.0, sham_z=0.0, removed=None):
    disks = {}
    for name in DISKS:
        if name == removed:
            continue
        item = fixture[name]
        centre = tuple(float(x) for x in item["position"])
        if name in fixture["delay_pair"]:
            centre = add(centre, (delay_d, 0.0, sham_z))
        normal = tuple(float(x) for x in item["normal"])
        disks[name] = (centre, normal, float(item["radius"]))
    source = fixture["source"]
    source_direction = tuple(source["direction"])
    initial = first_hit(tuple(source["position"]), source_direction, disks)
    if initial is None or initial[1] != "bs1":
        raise AssertionError("Source does not first hit BS1")
    routes = {}
    for arm, direction in (("arm1", source_direction),
                           ("arm2", reflect(source_direction, disks["bs1"][1]))):
        point, previous, length, names = initial[2], "bs1", 0.0, []
        for _ in DISKS:
            hit = first_hit(point, direction, disks, previous)
            if hit is None:
                break
            segment, name, point = hit
            length += segment
            names.append(name)
            previous = name
            if name == "bs2":
                break
            direction = reflect(direction, disks[name][1])
        routes[arm] = {"hits": tuple(names), "length": length,
                       "reached_bs2": bool(names and names[-1] == "bs2")}
    return routes


def check_fixture(fixture):
    base = trace(fixture)
    if base["arm1"]["hits"] != ARM1 or base["arm2"]["hits"] != ARM2:
        raise AssertionError(f"Unexpected first-hit routes: {base}")
    worst_error = 0.0
    for displacement in fixture["interventions"]["delay_d"]:
        moved = trace(fixture, delay_d=displacement)
        if moved["arm1"]["hits"] != ARM1 or moved["arm2"]["hits"] != ARM2:
            raise AssertionError(f"Unintended hit at d={displacement}")
        error = abs(moved["arm1"]["length"] - base["arm1"]["length"]
                    - 2 * displacement)
        worst_error = max(worst_error, error)
        if error > 1e-10:
            raise AssertionError(f"Delay path differs from 2d: {error} BU")
    sham = trace(fixture, sham_z=fixture["interventions"]["sham_z"])
    if sham["arm1"]["hits"] != ARM1 or abs(sham["arm1"]["length"]
                                            - base["arm1"]["length"]) > 1e-10:
        raise AssertionError("Sham changed the optical path")
    ablated = trace(fixture, removed=fixture["interventions"]["ablate"])
    if ablated["arm1"]["reached_bs2"] or ablated["arm2"]["hits"] != ARM2:
        raise AssertionError("Ablation failed to remove only arm 1")
    return {"arm1": base["arm1"], "arm2": base["arm2"],
            "max_delay_error_bu": worst_error,
            "sham_null": True, "ablation_arm1_lost": True}


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: exp003_first_hit_preflight.py fixture.json")
    print(json.dumps(check_fixture(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))),
                     indent=2))
