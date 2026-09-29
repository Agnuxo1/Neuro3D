"""CPU-only EXP-002 optimizer; the caller must evaluate real scene geometry.

This module never creates Blender objects and never supplies an optical
prediction to the engine. Its unit tests use a synthetic evaluator solely
to check optimization control flow, not to claim EXP-002 success.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Callable, Protocol


H = 1e-4
STEP = 0.2
MAX_UPDATES = 50
TARGET_TOLERANCE = 1e-4
RESIDUAL_TOLERANCE = 1e-12
OVERLAP_MIN = 1.0 - 1e-9


class OpticalResult(Protocol):
    status: str
    interference_valid: bool
    optical_a: tuple[float, float, float]
    optical_b: tuple[float, float, float]
    escape_rgb: tuple[float, float, float]
    unresolved_rgb: tuple[float, float, float]
    residual_rgb: tuple[float, float, float]
    mode_overlap: float | None


@dataclass(frozen=True)
class Observation:
    u: float
    power_a: float
    power_b: float
    escape: float
    overlap: float


@dataclass(frozen=True)
class FitRun:
    target: float
    start: float
    final_u: float
    updates: int
    converged: bool
    stop_reason: str
    observations: tuple[Observation, ...]


def _rgb(values: tuple[float, ...], name: str) -> tuple[float, float, float]:
    if len(values) != 3 or not all(math.isfinite(x) for x in values):
        raise ValueError(f"{name} must contain three finite channels")
    return values


def _measure(u: float, evaluate: Callable[[float], OpticalResult]) -> Observation:
    result = evaluate(u)
    if result.status != "ok" or not result.interference_valid:
        raise ValueError(f"invalid optical mode at u={u}: {result.status}")
    a = _rgb(result.optical_a, "optical_a")
    b = _rgb(result.optical_b, "optical_b")
    escape = _rgb(result.escape_rgb, "escape_rgb")
    unresolved = _rgb(result.unresolved_rgb, "unresolved_rgb")
    residual = _rgb(result.residual_rgb, "residual_rgb")
    if max(map(abs, unresolved)) > RESIDUAL_TOLERANCE:
        raise ValueError(f"unresolved power at u={u}")
    if max(map(abs, residual)) > RESIDUAL_TOLERANCE:
        raise ValueError(f"energy imbalance at u={u}")
    overlap = result.mode_overlap
    if overlap is None or not math.isfinite(overlap) or overlap < OVERLAP_MIN:
        raise ValueError(f"insufficient mode overlap at u={u}")
    return Observation(u, sum(a), sum(b), sum(escape), overlap)


def fit_port_a(
    evaluate: Callable[[float], OpticalResult], target: float, start: float
) -> FitRun:
    """Apply the frozen EXP-002 finite-difference update to a scene evaluator.

    The callback must place geometry at normalized displacement u and trace
    that scene; it must not substitute the ideal analytic formula in a real
    run. Every finite-difference observation passes the optical gates.
    """
    if not (math.isfinite(target) and 0.0 <= target <= 1.0 and
            math.isfinite(start) and 0.0 <= start <= 1.0):
        raise ValueError("target and start must be finite fractions")
    observations: list[Observation] = []
    u = start
    for updates in range(MAX_UPDATES + 1):
        here = _measure(u, evaluate)
        observations.append(here)
        if abs(here.power_a - target) <= TARGET_TOLERANCE:
            return FitRun(target, start, u, updates, True, "target", tuple(observations))
        if updates == MAX_UPDATES:
            break
        lo, hi = max(0.0, u - H), min(1.0, u + H)
        low = _measure(lo, evaluate)
        high = _measure(hi, evaluate)
        observations.extend((low, high))
        gradient = (high.power_a - low.power_a) / (hi - lo)
        if not math.isfinite(gradient):
            raise ValueError("non-finite optical gradient")
        if gradient == 0.0:
            # The high probe was the last callback; restore the reported u
            # so a Blender caller cannot accidentally save the probe scene.
            observations.append(_measure(u, evaluate))
            return FitRun(target, start, u, updates, False, "zero_gradient",
                          tuple(observations))
        u = min(1.0, max(0.0, u + STEP * (target - here.power_a) * gradient))
    return FitRun(target, start, u, MAX_UPDATES, False, "max_updates",
                  tuple(observations))
