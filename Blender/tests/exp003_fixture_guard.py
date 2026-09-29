"""Independent EXP-003 fixture and scene-readback acceptance gates.

These checks never provide geometry to inference. They reject a scene that
could satisfy relative-delay tests while differing from the frozen fixture.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

LOCKED_JSON_SHA256 = "89cdd5f50bf23716a6143e074cbcfd9b5c1123b78ae2f17782f43c176faa886b"
OPTICAL = ("bs1", "r1", "r2", "f1", "m2", "bs2")


def load_locked_fixture(path):
    content = Path(path).read_bytes()
    digest = hashlib.sha256(content).hexdigest()
    if digest != LOCKED_JSON_SHA256:
        raise ValueError(f"EXP-003 fixture digest mismatch: {digest}")
    return json.loads(content), digest


def validate_observed_disks(fixture, observed, delay_d=0.0, sham_z=0.0,
                            removed=None, tolerance=1e-6):
    """Validate actual world transforms and mesh topology, not input plans."""
    expected = set(OPTICAL) - ({removed} if removed else set())
    if set(observed) != expected:
        raise ValueError(f"Optical roles differ: {set(observed) ^ expected}")
    for role in expected:
        recorded = observed[role]
        spec = fixture[role]
        centre = tuple(spec["position"])
        if role in fixture["delay_pair"]:
            centre = (centre[0] + delay_d, centre[1], centre[2] + sham_z)
        if math.dist(tuple(recorded["position"]), centre) > tolerance:
            raise ValueError(f"World position differs for {role}")
        actual_normal = tuple(recorded["normal"])
        if math.dist(actual_normal, tuple(spec["normal"])) > tolerance:
            raise ValueError(f"World normal differs for {role}")
        if abs(float(recorded["radius"]) - float(spec["radius"])) > tolerance:
            raise ValueError(f"Radius differs for {role}")
        if recorded["faces"] != 1 or recorded["vertices"] < 32:
            raise ValueError(f"Disk topology differs for {role}")
        if recorded["modifiers"]:
            raise ValueError(f"Modified disk forbidden for {role}")
        if math.dist(tuple(recorded["scale"]), (1.0, 1.0, 1.0)) > tolerance:
            raise ValueError(f"Scale differs for {role}")
    return True


def validate_baseline_paths(paths, tolerance=1e-4):
    """Absolute base-path gate: not an inference fallback."""
    for arm, required in (("arm1", 5.0), ("arm2", 3.0)):
        path = paths[arm]
        if path["status"] != "reached_bs2" or path["length"] is None:
            raise ValueError(f"Base path missing: {arm}")
        if abs(path["length"] - required) > tolerance:
            raise ValueError(f"Base path length differs: {arm}")
    return True
