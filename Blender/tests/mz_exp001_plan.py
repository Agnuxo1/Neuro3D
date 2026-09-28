"""Frozen scene edits for EXP-001; pure Python, never starts Blender.

This module defines inputs for a future bounded Blender runner. It does not
trace light or supply expected results to the optical engine.
"""

from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Control:
    name: str
    group_delta: tuple[float, float, float] = (0.0, 0.0, 0.0)
    mirror1_delta: tuple[float, float, float] = (0.0, 0.0, 0.0)
    mirror2_phase: float = 0.0
    mutual_coherence: float = 1.0
    mirror2_turn_deg: float = 0.0
    expected_a: float = 0.0
    expected_b: float = 1.0
    expected_escape: float = 0.0
    expected_status: str = "ok"


def controls() -> tuple[Control, ...]:
    """A, B-geo, B-mat, three C variants, D in pre-registered order."""

    beta = math.radians(60.0)
    wavelength = 10.0 / 100.0  # BU: speed / frequency in EXP-001
    distance = (wavelength / 2.0) / (
        (math.sin(beta) - math.cos(beta)) * (1.0 - math.tan(beta / 2.0))
    )
    dx, dy = distance * math.sin(beta), distance * math.cos(beta)
    # From mirror1.x = X - Y*cot(beta), with P moving by (dx,dy).
    dm1 = dx - dy * math.cos(beta) / math.sin(beta)
    group = (dx, dy, 0.0)
    mirror1 = (dm1, 0.0, 0.0)
    return (
        Control("A"),
        Control("B-geo", group, mirror1, expected_a=1.0, expected_b=0.0),
        Control("B-mat", mirror2_phase=math.pi, expected_a=1.0, expected_b=0.0),
        Control("C-A", mutual_coherence=0.0, expected_a=0.5, expected_b=0.5),
        Control("C-B-geo", group, mirror1, mutual_coherence=0.0,
                expected_a=0.5, expected_b=0.5),
        Control("C-B-mat", mirror2_phase=math.pi, mutual_coherence=0.0,
                expected_a=0.5, expected_b=0.5),
        Control("D", mirror2_turn_deg=10.0, expected_a=0.25,
                expected_b=0.25, expected_escape=0.5, expected_status="missed_bs2"),
    )
