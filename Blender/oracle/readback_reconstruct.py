"""Rebuild an MZ trace from values read back from a saved .blend (EXP-001 step 3; Claude).

Input: the JSON record written by Blender/tests/blender_mz_exp001.py. Required
content (proposed extension of `_capture`):
  record["objects"][role]["matrix_world"]  16 floats, row-major (as captured now)
  record["optics"][role]                   every optical custom property of that object
  record["result"]                         outputs of trace_mz_circuit inside Blender
Roles: mz_source, mz_bs1, mz_bs2, mz_mirror1, mz_mirror2, mz_detector_a, mz_detector_b.

Position = translation column of matrix_world; normal / direction = its local +Z
column, normalised. That is what the adapter reads with matrix_world.
The rebuilt scene is traced with Blender/core/mz_scene.trace_mz OUTSIDE Blender
and compared with the stored result (default tolerance 1e-12). This checks the
readback and serialisation path; it is not an independent optics model.

CLI:  python readback_reconstruct.py path/to/B-geo.json [more.json ...]
"""

from __future__ import annotations

import json
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "core"))
from mz_scene import Detector, MZScene, Mirror, Source, Splitter, distance, reflected, trace_mz  # noqa: E402

ROLES = ("mz_source", "mz_bs1", "mz_bs2", "mz_mirror1", "mz_mirror2", "mz_detector_a", "mz_detector_b")
RESULT_KEYS = ("optical_a", "optical_b", "escape_rgb", "unresolved_rgb", "residual_rgb")


def _rows(flat):
    if len(flat) != 16:
        raise ValueError("matrix_world must have 16 values")
    return [flat[4 * i: 4 * i + 4] for i in range(4)]


def position(flat) -> tuple[float, float, float]:
    m = _rows(flat)
    return (m[0][3], m[1][3], m[2][3])


def local_z(flat) -> tuple[float, float, float]:
    m = _rows(flat)
    v = (m[0][2], m[1][2], m[2][2])
    n = math.sqrt(sum(x * x for x in v))
    if not n or not math.isfinite(n):
        raise ValueError("degenerate local Z axis")
    return (v[0] / n, v[1] / n, v[2] / n)


def rebuild(record: dict) -> MZScene:
    obj, opt = record["objects"], record["optics"]
    missing = [r for r in ROLES if r not in obj or r not in opt]
    if missing:
        raise KeyError(f"record lacks roles: {missing}")
    rgb = lambda v: tuple(float(x) for x in v)  # noqa: E731
    s = opt["mz_source"]
    waist = float(s["beam_waist"])
    source = Source(position(obj["mz_source"]["matrix_world"]), local_z(obj["mz_source"]["matrix_world"]),
                    float(s["power"]), rgb(s["rgb"]), float(s["frequency"]), float(s["phase"]),
                    beam_waist=None if waist == 0.0 else waist, mutual_coherence=float(s["mutual_coherence"]))

    def splitter(role):
        return Splitter(position(obj[role]["matrix_world"]), local_z(obj[role]["matrix_world"]),
                        float(opt[role]["radius"]), float(opt[role]["transmission"]))

    def mirror(role):
        return Mirror(position(obj[role]["matrix_world"]), local_z(obj[role]["matrix_world"]),
                      float(opt[role]["radius"]), rgb(opt[role]["reflectance_rgb"]), float(opt[role]["phase_shift"]))

    def detector(role):
        return Detector(position(obj[role]["matrix_world"]), float(opt[role]["radius"]),
                        rgb(opt[role]["responsivity_rgb"]), float(opt[role]["activation_threshold"]),
                        float(opt[role]["response_gain"]))

    bs2 = opt["mz_bs2"]
    return MZScene(source, splitter("mz_bs1"), mirror("mz_mirror1"), mirror("mz_mirror2"), splitter("mz_bs2"),
                   detector("mz_detector_a"), detector("mz_detector_b"),
                   float(s["propagation_speed"]), float(s["absorption_per_unit"]),
                   float(bs2["overlap_tolerance"]), float(bs2["direction_tolerance"]))


def compare(record: dict, tolerance: float = 1e-12) -> dict:
    """Retrace outside Blender and report the worst deviation from the stored result."""

    result = trace_mz(rebuild(record))
    stored = record["result"]
    worst = 0.0
    for key in RESULT_KEYS:
        mine = getattr(result, key)
        for a, b in zip(mine, stored[key]):
            worst = max(worst, abs(float(a) - float(b)))
    return {"status_match": result.status == stored["status"], "status": result.status,
            "worst_abs_diff": worst, "passes": result.status == stored["status"] and worst <= tolerance}


def direction_gaps(record: dict) -> dict:
    """Nominal output-direction gaps from reopened transforms; diagnostic only.

    The rays might miss a mirror or BS2, so this cannot replace trace status.
    It never changes EXP-001 acceptance criteria.
    """

    scene = rebuild(record)
    arm1 = reflected(scene.source.direction, scene.mirror1.normal)
    arm2_start = reflected(scene.source.direction, scene.bs1.normal)
    arm2 = reflected(arm2_start, scene.mirror2.normal)
    gap_a = distance(arm1, reflected(arm2, scene.bs2.normal))
    gap_b = distance(reflected(arm1, scene.bs2.normal), arm2)
    return {"gap_a": gap_a, "gap_b": gap_b,
            "direction_tolerance": scene.direction_tolerance,
            "within_tolerance": max(gap_a, gap_b) <= scene.direction_tolerance}


if __name__ == "__main__":
    ok = True
    for path in sys.argv[1:]:
        report = compare(json.loads(pathlib.Path(path).read_text(encoding="utf-8")))
        ok &= report["passes"]
        print(path, json.dumps(report))
    sys.exit(0 if ok else 1)
