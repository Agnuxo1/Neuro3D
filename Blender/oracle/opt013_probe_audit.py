"""OPT-013: CPU audit of the GPU ray probe, without GPU, Blender or OpenGL.

Independent Claude artefact. It does not edit the engine or Codex's probe.

What it does
------------
1. Imports the REAL host code of ``Blender/tests/mz_scene_gpu_ray_probe.py``
   (``input_record`` and its packing via ``mz_scene_gpu_probe.pack_record``)
   with stub ``glfw``/``moderngl`` modules, so the byte layout audited is the
   one Codex runs.
2. Executes a line-by-line FP64 Python port of the GLSL ``main()`` on the
   packed input vector (``emulate_shader``). Offsets are read from the same
   flat vector the GPU receives.
3. Rebuilds the seven EXP-001 records from the closed-form ``NonRectMZ(60)``
   geometry plus the frozen edits of ``mz_exp001_plan.controls()``, compares
   against ``trace_mz`` (via ``readback_reconstruct.rebuild``) with the probe's
   own host acceptance rule (``host_accepts``).
4. Runs minimal counter-cases outside EXP-001 to check that every departure
   from the ideal model FAILS LOUDLY in the host comparison, or to show where
   it does not.

Limits: a CPU port is not the NVIDIA driver. It checks the algorithm and the
host acceptance logic, not GPU arithmetic. The real readbacks on D: are only
used if passed on the command line.

Usage::

    python Blender/oracle/opt013_probe_audit.py            # synthetic EXP-001
    python Blender/oracle/opt013_probe_audit.py DIR        # DIR/*.readback.json
"""

from __future__ import annotations

import copy
import json
import math
from pathlib import Path
import struct
import sys
import types

HERE = Path(__file__).resolve().parent
TESTS = HERE.parent / "tests"
CORE = HERE.parent / "core"
for p in (str(HERE), str(TESTS), str(CORE)):
    if p not in sys.path:
        sys.path.insert(0, p)

# The probe modules import glfw/moderngl at module level; stub them so the
# pure-Python packing code can be imported unchanged. No context is created.
for _name in ("glfw", "moderngl"):
    try:
        __import__(_name)
    except ImportError:
        sys.modules[_name] = types.ModuleType(_name)

import mz_scene_gpu_ray_probe as probe  # noqa: E402  (real host code)
from geometry_oracle import NonRectMZ  # noqa: E402
from mz_exp001_plan import controls  # noqa: E402
from mz_scene import trace_mz  # noqa: E402
from readback_reconstruct import rebuild  # noqa: E402

NAMES = ("A", "B-geo", "B-mat", "C-A", "C-B-geo", "C-B-mat", "D")


# --------------------------------------------------------------------------
# FP64 port of the GLSL main(); keep in lock-step with probe.SHADER.
# --------------------------------------------------------------------------

def _v(x, b):
    return (x[b], x[b + 1], x[b + 2])


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _mul(a, k):
    return (a[0] * k, a[1] * k, a[2] * k)


def _normalize(a):
    n = math.sqrt(_dot(a, a))
    return _mul(a, 1.0 / n)


def _refl(d, n):
    return _sub(d, _mul(n, 2.0 * _dot(d, n)))


def cos_near_pi(phase: float) -> float:
    squared = phase * phase
    term = total = 1.0
    for k in range(1, 13):
        term *= -squared / (float(2 * k - 1) * float(2 * k))
        total += term
    return total


def _disc(o, d, c, n, rad):
    den = _dot(d, n)
    if abs(den) < 1e-12:
        return False, None, None
    t = _dot(_sub(c, o), n) / den
    if t <= 1e-9:
        return False, None, None
    hit = _add(o, _mul(d, t))
    return math.sqrt(_dot(_sub(hit, c), _sub(hit, c))) <= rad, hit, t


def emulate_shader(x: list[float], i: int = 0) -> list[float]:
    """One invocation of the probe's compute shader on flat input ``x``."""
    b = i * 64
    bs1, m1, m2, bs2 = _v(x, b), _v(x, b + 4), _v(x, b + 8), _v(x, b + 12)
    source, source_dir = _v(x, b + 32), _normalize(_v(x, b + 35))
    bs1_n, m1_n = _normalize(_v(x, b + 38)), _normalize(_v(x, b + 42))
    m2_n, bs2_n = _normalize(_v(x, b + 46)), _normalize(_v(x, b + 50))
    first, h0, t0 = _disc(source, source_dir, bs1, bs1_n, x[b + 41])
    d1, d2 = source_dir, _refl(source_dir, bs1_n)
    a1 = a2 = False
    r1 = r2 = z1 = z2 = None
    t1 = t2 = u1 = u2 = None
    if first:
        ok, h1, t1 = _disc(h0, d1, m1, m1_n, x[b + 45])
        if ok:
            r1 = _refl(d1, m1_n)
            a1, z1, u1 = _disc(h1, r1, bs2, bs2_n, x[b + 53])
        ok, h2, t2 = _disc(h0, d2, m2, m2_n, x[b + 49])
        if ok:
            r2 = _refl(d2, m2_n)
            a2, z2, u2 = _disc(h2, r2, bs2, bs2_n, x[b + 53])
    fa = fb = fe = delta = length_delta = 0.0
    status = 4
    if first:
        if a1 and a2:
            status = 0
            l1 = t0 + t1 + u1 + _dot(r1, _sub(bs2, z1))
            l2 = t0 + t2 + u2 + _dot(r2, _sub(bs2, z2))
            length_delta = l2 - l1
            delta = (6.2831853071795864769 * length_delta * x[b + 18] / x[b + 19]
                     + x[b + 17] - x[b + 16])
            fa = 0.5 * (1.0 - x[b + 20] * cos_near_pi(delta))
            fb = 1.0 - fa
        elif a1 or a2:
            status = 1 if a1 else 2
            fa, fb, fe = 0.25, 0.25, 0.5  # NOTE: constants, not computed
        else:
            status, fe = 3, 1.0
    else:
        fe = 1.0
    y = [0.0] * 12
    for c in range(3):
        p = x[b + 21] * x[b + 22 + c]
        y[c], y[3 + c], y[6 + c] = p * fa, p * fb, p * fe
    y[9], y[10], y[11] = float(status), delta, length_delta
    return y


def host_accepts(sample: list[float], expected: dict) -> dict:
    """Replicates the per-case acceptance in probe.main() (lines 181-202)."""
    if abs(sample[10]) > math.pi + 1e-9:
        return {"raised": "phase outside validated cosine range", "accepted": False}
    ray_status = int(sample[9])
    es = expected["status"]
    status_matches = ((es == "ok" and ray_status == 0) or
                      (es == "missed_bs2" and ray_status in (1, 2)))
    target = list(expected["optical_a"]) + list(expected["optical_b"]) + list(expected["escape_rgb"])
    diff = max(abs(a - b) for a, b in zip(sample[:9], target))
    totals = (sum(sample[:3]), sum(sample[3:6]), sum(sample[6:9]))
    exp_totals = (sum(expected["optical_a"]), sum(expected["optical_b"]), sum(expected["escape_rgb"]))
    tdiff = max(abs(a - b) for a, b in zip(totals, exp_totals))
    return {"ray_status": ray_status, "expected_status": es, "status_matches": status_matches,
            "gpu_a": totals[0], "gpu_b": totals[1], "gpu_escape": totals[2],
            "worst_abs_diff": max(diff, tdiff), "delta_phase": sample[10],
            "accepted": status_matches and max(diff, tdiff) <= 1e-9}


# --------------------------------------------------------------------------
# Synthetic EXP-001 records (same geometry as the adapter's nonrect60)
# --------------------------------------------------------------------------

def _matrix(pos, z):
    z = _normalize(z)
    helper = (0.0, 0.0, 1.0) if abs(z[2]) < 0.9 else (1.0, 0.0, 0.0)
    xa = _normalize((helper[1] * z[2] - helper[2] * z[1], helper[2] * z[0] - helper[0] * z[2],
                     helper[0] * z[1] - helper[1] * z[0]))
    ya = (z[1] * xa[2] - z[2] * xa[1], z[2] * xa[0] - z[0] * xa[2], z[0] * xa[1] - z[1] * xa[0])
    return [xa[0], ya[0], z[0], pos[0], xa[1], ya[1], z[1], pos[1],
            xa[2], ya[2], z[2], pos[2], 0.0, 0.0, 0.0, 1.0]


def _rot_z(v, deg):
    a = math.radians(deg)
    return (v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a), v[2])


def base_geometry():
    g = NonRectMZ(60, 2, 2).scene()
    P = g["bs2"]["position"]
    return {
        "mz_source": [(-1.0, 0.0, 0.0), (1.0, 0.0, 0.0)],
        "mz_bs1": [g["bs1"]["position"], g["bs1"]["normal"]],
        "mz_bs2": [P, g["bs2"]["normal"]],
        "mz_mirror1": [g["mirror1"]["position"], g["mirror1"]["normal"]],
        "mz_mirror2": [g["mirror2"]["position"], g["mirror2"]["normal"]],
        "mz_detector_a": [_add(P, g["port_a_direction"]), (0.0, 0.0, 1.0)],
        "mz_detector_b": [_add(P, g["port_b_direction"]), (0.0, 0.0, 1.0)],
    }


def base_optics():
    det = {"radius": 0.2, "responsivity_rgb": [1.0, 1.0, 1.0],
           "activation_threshold": 0.25, "response_gain": 1.0}
    return {
        "mz_source": {"power": 1.0, "rgb": [1.0, 1.0, 1.0], "frequency": 100.0, "phase": 0.0,
                      "propagation_speed": 10.0, "absorption_per_unit": 0.0, "beam_waist": 0.2,
                      "mutual_coherence": 1.0},
        "mz_bs1": {"radius": 0.4, "transmission": 0.5},
        "mz_bs2": {"radius": 0.4, "transmission": 0.5, "overlap_tolerance": 0.02,
                   "direction_tolerance": 1e-5},
        "mz_mirror1": {"radius": 0.4, "reflectance_rgb": [1.0, 1.0, 1.0], "phase_shift": 0.0},
        "mz_mirror2": {"radius": 0.4, "reflectance_rgb": [1.0, 1.0, 1.0], "phase_shift": 0.0},
        "mz_detector_a": dict(det),
        "mz_detector_b": dict(det),
    }


def make_record(geo, optics):
    rec = {"objects": {r: {"matrix_world": _matrix(*geo[r])} for r in geo}, "optics": optics}
    res = trace_mz(rebuild(rec))
    rec["result"] = {"status": res.status,
                     **{k: list(getattr(res, k)) for k in
                        ("optical_a", "optical_b", "escape_rgb", "unresolved_rgb", "residual_rgb")}}
    return rec


def exp001_records():
    out = {}
    for c in controls():
        geo, opt = base_geometry(), base_optics()
        for role in ("mz_bs2", "mz_detector_a", "mz_detector_b"):
            geo[role][0] = _add(geo[role][0], c.group_delta)
        geo["mz_mirror1"][0] = _add(geo["mz_mirror1"][0], c.mirror1_delta)
        opt["mz_mirror2"]["phase_shift"] = c.mirror2_phase
        opt["mz_source"]["mutual_coherence"] = c.mutual_coherence
        if c.mirror2_turn_deg:
            geo["mz_mirror2"][1] = _rot_z(geo["mz_mirror2"][1], c.mirror2_turn_deg)
        out[c.name] = make_record(geo, opt)
    return out


def run_probe_on(record):
    return host_accepts(emulate_shader(probe.input_record(record)), record["result"])


def run_glsl(records: list[dict]) -> list[list[float]] | None:
    """Execute the probe's REAL GLSL source on a headless software GL.

    Uses Mesa llvmpipe through EGL (CPU, no GPU). Returns None if no OpenGL
    4.3 context can be created. This checks the shader text itself (GLSL
    semantics, FP64 path, buffer layout), not NVIDIA arithmetic.
    """
    try:
        import moderngl as mgl
        ctx = mgl.create_standalone_context(require=430, backend="egl")
    except Exception:
        return None
    try:
        values = [v for r in records for v in probe.input_record(r)]
        shader = ctx.compute_shader(probe.SHADER)
        src = ctx.buffer(struct.pack(f"<{len(values)}d", *values))
        dst = ctx.buffer(reserve=len(records) * probe.OUT_STRIDE * 8)
        src.bind_to_storage_buffer(0)
        dst.bind_to_storage_buffer(1)
        shader["control_count"].value = len(records)
        shader.run(group_x=(len(records) + 31) // 32)
        ctx.finish()
        flat = struct.unpack(f"<{len(records) * probe.OUT_STRIDE}d", dst.read())
        return [list(flat[i * 12:(i + 1) * 12]) for i in range(len(records))]
    finally:
        ctx.release()


# --------------------------------------------------------------------------
# Counter-cases (outside EXP-001) - each should fail loudly, or is a finding
# --------------------------------------------------------------------------

def counter_cases():
    cases = {}
    A = exp001_records()["A"]

    # CX1: tilt BS2 by 1e-3 rad. Both arms still hit its disc; the engine
    # rejects the non-collinear output modes.
    geo, opt = base_geometry(), base_optics()
    geo["mz_bs2"][1] = _rot_z(geo["mz_bs2"][1], math.degrees(1e-3))
    cases["CX1_bs2_tilt_1e-3rad"] = make_record(geo, opt)

    # CX2: translate BS2+detectors 0.02 BU along the BS2 NORMAL with finite
    # waist: directions still match but the two impacts separate (overlap
    # ~0.98); the engine damps interference, the shader uses gamma =
    # mutual_coherence only. (An in-plane shift changes nothing.)
    geo, opt = base_geometry(), base_optics()
    shift = _mul(_normalize(geo["mz_bs2"][1]), 0.02)
    for role in ("mz_bs2", "mz_detector_a", "mz_detector_b"):
        geo[role][0] = _add(geo[role][0], shift)
    cases["CX2_normal_offset_0.02BU"] = make_record(geo, opt)

    # CX3: detector B moved onto port A's path (occlusion). The shader has
    # no detectors at all.
    geo, opt = base_geometry(), base_optics()
    P = geo["mz_bs2"][0]
    va = _sub(geo["mz_detector_a"][0], P)
    geo["mz_detector_b"][0] = _add(P, _mul(va, 0.5))
    cases["CX3_detector_occlusion"] = make_record(geo, opt)

    # CX4: lose the M1 arm instead (M1 +10 deg). The engine labels this
    # missed_bs2_aperture; the host accepts only missed_bs2, so it is rejected
    # by label although the ray status (2) and powers agree.
    geo, opt = base_geometry(), base_optics()
    geo["mz_mirror1"][1] = _rot_z(geo["mz_mirror1"][1], 10.0)
    cases["CX4_D_other_arm_lost"] = make_record(geo, opt)

    # CX5: an equivalent phase written unreduced (2*pi + pi on M2) - the
    # engine reduces it, the probe refuses |delta| > pi.
    geo, opt = base_geometry(), base_optics()
    opt["mz_mirror2"]["phase_shift"] = 3 * math.pi
    cases["CX5_unreduced_phase_3pi"] = make_record(geo, opt)

    # CX6: D with -10 deg (DEC-011's rejected sign): engine gives
    # missed_bs2_aperture, same powers; host rejects on the label only.
    geo, opt = base_geometry(), base_optics()
    geo["mz_mirror2"][1] = _rot_z(geo["mz_mirror2"][1], -10.0)
    cases["CX6_D_minus10deg_aperture"] = make_record(geo, opt)
    return cases


def taylor_error(samples: int = 200001) -> float:
    worst = 0.0
    lim = math.pi + 1e-9
    for k in range(samples):
        p = -lim + 2 * lim * k / (samples - 1)
        worst = max(worst, abs(cos_near_pi(p) - math.cos(p)))
    return worst


def main(argv):
    report = {"taylor_max_abs_error_on_[-pi-1e-9,pi+1e-9]": taylor_error()}
    if len(argv) > 1:
        d = Path(argv[1])
        recs = {n: json.loads((d / f"{n}.readback.json").read_text(encoding="utf-8")) for n in NAMES}
        report["source"] = str(d)
    else:
        recs = exp001_records()
        report["source"] = "synthetic NonRectMZ(60,2,2) + mz_exp001_plan.controls()"
    report["exp001"] = {n: run_probe_on(r) for n, r in recs.items()}
    report["counter_cases"] = {}
    for n, r in counter_cases().items():
        h = run_probe_on(r)
        h["engine_status"] = r["result"]["status"]
        h["engine_a_b_escape_unresolved"] = [sum(r["result"][k]) for k in
                                             ("optical_a", "optical_b", "escape_rgb", "unresolved_rgb")]
        report["counter_cases"][n] = h
    print(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    main(sys.argv)
