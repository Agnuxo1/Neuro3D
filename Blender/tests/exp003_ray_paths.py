"""EXP-003 path accumulator for a scene-owned nearest-hit ray caster.

The ``cast`` callback must query actual scene geometry and return the first
hit as (object_name, world_point, world_normal), or None. This module never
uses fixture positions or predicted lengths for inference.
"""

from __future__ import annotations

import math

EPSILON = 1e-4
MAX_HITS = 8


def _dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def _add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def _scale(a, scalar):
    return tuple(x * scalar for x in a)


def _unit(v):
    length = math.sqrt(_dot(v, v))
    if not math.isfinite(length) or length <= 0:
        raise ValueError("Ray direction or hit normal is invalid")
    return _scale(v, 1 / length)


def _reflect(direction, normal):
    normal = _unit(normal)
    return _unit(_add(direction, _scale(normal, -2 * _dot(direction, normal))))


def trace_paths(cast, source_position, source_direction, expected_routes=None):
    """Return measured BS1-to-BS2 paths; missing hits remain explicit loss."""
    direction = _unit(source_direction)
    first = cast(tuple(source_position), direction)
    if first is None or first[0] != "bs1":
        raise ValueError("Source must first hit BS1")
    bs1_point, bs1_normal = tuple(first[1]), tuple(first[2])
    results = {}
    for arm, launch in (("arm1", direction),
                        ("arm2", _reflect(direction, bs1_normal))):
        point = bs1_point
        ray = launch
        segments = []
        status = "lost"
        previous_name = "bs1"
        for _ in range(MAX_HITS):
            hit = cast(_add(point, _scale(ray, EPSILON)), ray)
            if hit is None:
                break
            name, hit_point, normal = hit
            hit_point = tuple(hit_point)
            distance = math.dist(point, hit_point)
            if not math.isfinite(distance) or distance <= EPSILON / 2:
                raise ValueError("Non-progressing or invalid scene ray hit")
            segments.append({"object": name, "point": hit_point,
                             "incoming_direction": tuple(ray),
                             "length": distance, "status": "hit"})
            point = hit_point
            if name.startswith("unmapped:"):
                status = "invalid_unmapped_hit"
                break
            if name == previous_name:
                status = "invalid_self_hit"
                break
            previous_name = name
            if name == "bs2":
                status = "reached_bs2"
                break
            if name == "bs1":
                raise ValueError("Unexpected second BS1 impact")
            ray = _reflect(ray, tuple(normal))
        if expected_routes is not None and status == "reached_bs2":
            if tuple(item["object"] for item in segments) != tuple(expected_routes[arm]):
                status = "unexpected_route"
        traversed = sum(item["length"] for item in segments)
        results[arm] = {"status": status,
                        "length": traversed if status == "reached_bs2" else None,
                        "traversed_length": traversed,
                        "hits": segments}
    return results
