"""EXP-002 absolute scene placement; pure Python, no Blender import or trace.

The live runner must capture the untouched nonrect60 A scene once, then call
place_u before EACH optical evaluation. Absolute placement avoids drift when
finite-difference probes visit u+h, u-h and u in changing order.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Callable, TypeVar

from mz_exp001_plan import controls

EXPECTED_MIRROR = 2.0 - 2.0 / math.sqrt(3.0)
ResultT = TypeVar("ResultT")


@dataclass(frozen=True)
class Baseline:
    group: tuple[float, float, float]
    mirror1: tuple[float, float, float]


def _location(obj):
    xyz = tuple(float(v) for v in obj.location)
    if len(xyz) != 3 or not all(math.isfinite(v) for v in xyz):
        raise ValueError("Malformed optical object location")
    return xyz


def capture_baseline(roles) -> Baseline:
    """Reject a wrong layout or detached detectors before any training edit."""
    group = roles["mz_combiner_group"]
    for role in ("mz_bs2", "mz_detector_a", "mz_detector_b"):
        if roles[role].parent is not group:
            raise ValueError(f"{role} is not parented to the combiner group")
    group_xyz = _location(group)
    mirror_xyz = _location(roles["mz_mirror1"])
    expected_group = (2.0, 2.0, 0.0)
    expected_mirror = (EXPECTED_MIRROR, 0.0, 0.0)
    if any(abs(a - b) > 1e-5 for a, b in zip(group_xyz, expected_group)):
        raise ValueError("EXP-002 requires the unedited nonrect60 A group")
    if any(abs(a - b) > 1e-5 for a, b in zip(mirror_xyz, expected_mirror)):
        raise ValueError("EXP-002 requires the unedited nonrect60 A mirror")
    return Baseline(group_xyz, mirror_xyz)


def place_u(roles, baseline: Baseline, u: float) -> None:
    """Edit only M1 and the combiner parent using frozen EXP-001 B-geo deltas."""
    if not math.isfinite(u) or not 0.0 <= u <= 1.0:
        raise ValueError("u must be a finite fraction in [0,1]")
    edit = controls()[1]
    positions = (
        (roles["mz_combiner_group"], baseline.group, edit.group_delta),
        (roles["mz_mirror1"], baseline.mirror1, edit.mirror1_delta),
    )
    for obj, base, delta in positions:
        for i in range(3):
            obj.location[i] = base[i] + u * delta[i]


def place_sham_u(roles, baseline: Baseline, u: float) -> None:
    """Move the combiner in its plane; leave M1 and optical inputs untouched.

    This negative control must use the same optimizer as the real edit. Its
    predicted optical null is a hypothesis to check in the live scene, not a
    power value supplied by this function.
    """
    if not math.isfinite(u) or not 0.0 <= u <= 1.0:
        raise ValueError("u must be a finite fraction in [0,1]")
    group = roles["mz_combiner_group"]
    tangent = 0.3 * u / math.sqrt(2.0)
    group.location[0] = baseline.group[0] + tangent
    group.location[1] = baseline.group[1] + tangent
    group.location[2] = baseline.group[2]


def scene_evaluator(roles, baseline: Baseline,
                    trace: Callable[[], ResultT], *,
                    sham: bool = False) -> Callable[[float], ResultT]:
    """Bind placement to a supplied live-scene trace, without importing bpy.

    The future Blender runner must supply trace_mz_circuit(bpy, scene) here.
    Nothing in this function computes or injects expected optical power.
    """
    def evaluate(u: float) -> ResultT:
        (place_sham_u if sham else place_u)(roles, baseline, u)
        return trace()
    return evaluate
