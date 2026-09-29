"""Hybrid EXP-003 combiner: only measured scene paths provide phase.

This numerical field combination is *outside* Blender's light engine and
must never be described as all-optical or scene-executed interference.
"""

from __future__ import annotations

import cmath
import math


def combine_measured_paths(paths, wavelength, input_power=1.0):
    if not math.isfinite(wavelength) or wavelength <= 0:
        raise ValueError("Invalid wavelength")
    if not math.isfinite(input_power) or input_power < 0:
        raise ValueError("Invalid input power")
    fields = []
    lost_power = 0.0
    for arm in ("arm1", "arm2"):
        path = paths[arm]
        status, length = path["status"], path["length"]
        if status == "lost" and length is None:
            fields.append(0j)
            lost_power += input_power / 2
        elif status == "reached_bs2" and length is not None and math.isfinite(length):
            fields.append(math.sqrt(input_power / 2) * cmath.exp(
                1j * 2 * math.pi * length / wavelength))
        else:
            raise ValueError(f"Invalid or unresolved path: {arm}={status}")
    arm1, arm2 = fields
    port_a = abs((arm1 - arm2) / math.sqrt(2)) ** 2
    port_b = abs((arm1 + arm2) / math.sqrt(2)) ** 2
    return {"P_A": port_a, "P_B": port_b, "escape": lost_power,
            "absorption": 0.0, "unresolved": 0.0,
            "balance_error": abs(port_a + port_b + lost_power - input_power)}
