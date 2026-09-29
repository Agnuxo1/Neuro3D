"""Pure four-mode field propagation from externally measured scene paths.

This is an explicitly hybrid numerical consumer, not a Blender ray tracer.
Its caller must obtain and validate each path from re-opened scene geometry.
No fixture displacement or analytic length is used as a phase fallback.
"""

from __future__ import annotations

import cmath
import math

PAIRS = (((0, 1), (2, 3)), ((1, 2),),
         ((0, 1), (2, 3)), ((1, 2),))
SQRT2 = math.sqrt(2.0)


def _phase(path, wavelength, field):
    status = path["status"]
    length = path["length"]
    if status == "lost" and length is None:
        return 0j, abs(field) ** 2
    if status != "reached_bs2" or length is None:
        raise ValueError(f"Unresolved scene path: {status}")
    if not math.isfinite(length) or length < 0:
        raise ValueError("Invalid measured path length")
    return field * cmath.exp(1j * 2 * math.pi * length / wavelength), 0.0


def propagate_measured_mesh(paths_by_cell, inputs, wavelength):
    """Return fields, powers and explicit escaped power for six MZIs.

    ``paths_by_cell[(column, lower_mode)]`` has ``arm1`` and ``arm2``
    records in the EXP-003 path schema. The first coupler maps inputs
    to (x+y, x-y)/sqrt(2); the second maps fields to (a-b, a+b)/sqrt(2),
    preserving EXP-003's A-dark/B-bright port convention for [1,0].
    """
    if not math.isfinite(wavelength) or wavelength <= 0:
        raise ValueError("Invalid wavelength")
    if len(inputs) != 4:
        raise ValueError("Exactly four input modes are required")
    fields = [complex(value) for value in inputs]
    if any(not math.isfinite(part) for field in fields
           for part in (field.real, field.imag)):
        raise ValueError("Non-finite input field")
    expected = {(col, lower) for col, pairs in enumerate(PAIRS)
                for lower, _upper in pairs}
    if set(paths_by_cell) != expected:
        raise ValueError("Missing or unexpected measured cell")
    power_in = sum(abs(value) ** 2 for value in fields)
    escape = 0.0
    for col, pairs in enumerate(PAIRS):
        for lower, upper in pairs:
            cell = paths_by_cell[(col, lower)]
            if set(cell) != {"arm1", "arm2"}:
                raise ValueError("Missing or unexpected measured arm")
            x, y = fields[lower], fields[upper]
            arm1 = (x + y) / SQRT2
            arm2 = (x - y) / SQRT2
            arm1, loss1 = _phase(cell["arm1"], wavelength, arm1)
            arm2, loss2 = _phase(cell["arm2"], wavelength, arm2)
            escape += loss1 + loss2
            fields[lower] = (arm1 - arm2) / SQRT2
            fields[upper] = (arm1 + arm2) / SQRT2
    powers = tuple(abs(value) ** 2 for value in fields)
    return {"fields": tuple(fields), "powers": powers, "escape": escape,
            "absorption": 0.0,
            "balance_error": abs(sum(powers) + escape - power_in)}
