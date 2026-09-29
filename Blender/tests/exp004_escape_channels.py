"""Independent, fail-closed grouping of raw outgoing optical rays.

This is a diagnostic for the proposed EXP-004 conf1 comparator, not a
replacement for Blender tracing or proof of a physical open channel.
Tolerances must be frozen before use in an acceptance experiment.
"""

from __future__ import annotations

import math


def _vec3(value):
    if not isinstance(value, (tuple, list)) or len(value) != 3:
        raise ValueError("Expected three-vector")
    values = tuple(float(x) for x in value)
    if any(not math.isfinite(x) for x in values):
        raise ValueError("Non-finite ray geometry")
    return values


def _unit(value):
    vec = _vec3(value)
    norm = math.sqrt(sum(x*x for x in vec))
    if norm <= 0:
        raise ValueError("Zero outgoing direction")
    return tuple(x/norm for x in vec)


def _distance(a, b):
    direction_a, direction_b = a["dir"], b["dir"]
    dot = max(-1., min(1., sum(x*y for x, y in zip(direction_a,
                                                   direction_b))))
    angle = math.acos(dot)
    displacement = tuple(x-y for x, y in zip(a["point"], b["point"]))
    projected = sum(x*y for x, y in zip(displacement, direction_a))
    lateral = math.sqrt(max(0., sum(x*x for x in displacement) - projected**2))
    return angle, lateral


def group_raw_escapes(records, angle_tolerance=1e-4,
                      lateral_tolerance=1e-3, ambiguity_factor=10):
    """Sum amplitudes only for clearly coincident outgoing ray channels.

    Returns a list of (last_object, complex_amplitude, count). A ray in
    the grey zone between tolerance and 10*tolerance raises rather than
    being silently merged or split. Every member of a group must match
    every other member, preventing non-transitive chaining.
    """
    if (angle_tolerance <= 0 or lateral_tolerance <= 0 or
            ambiguity_factor <= 1):
        raise ValueError("Invalid channel tolerances")
    groups = []
    for raw in records:
        last = raw["last"]
        if not isinstance(last, str) or not last:
            raise ValueError("Missing last optical object")
        field = raw["field"]
        if not isinstance(field, (tuple, list)) or len(field) != 2:
            raise ValueError("Invalid escape field")
        amplitude = complex(*field)
        if not math.isfinite(amplitude.real) or not math.isfinite(amplitude.imag):
            raise ValueError("Non-finite escape field")
        ray = {"last": last, "point": _vec3(raw["point"]),
               "dir": _unit(raw["dir"]), "field": amplitude}
        compatible = []
        for index, group in enumerate(groups):
            if group[0]["last"] != last:
                continue
            comparisons = [_distance(ray, member) for member in group]
            if all(angle <= angle_tolerance and lateral <= lateral_tolerance
                   for angle, lateral in comparisons):
                compatible.append(index)
            elif any(angle <= ambiguity_factor * angle_tolerance and
                     lateral <= ambiguity_factor * lateral_tolerance
                     for angle, lateral in comparisons):
                raise ValueError("Ambiguous escape channel boundary")
        if len(compatible) > 1:
            raise ValueError("Escape ray fits multiple channels")
        if compatible:
            groups[compatible[0]].append(ray)
        else:
            groups.append([ray])
    return [(group[0]["last"], sum(ray["field"] for ray in group),
             len(group)) for group in groups]
