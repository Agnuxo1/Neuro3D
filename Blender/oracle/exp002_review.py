"""EXP-002 pre-run review (Claude): CPU only, never starts Blender.

Drives Codex's frozen optimizer ``mz_geometry_optimizer.fit_port_a`` with
evaluators built on the real CPU engine ``trace_mz`` and the EXP-001
nonrect60 geometry, plus two adversarial evaluators:

* ``scene_evaluator``   - edits geometry by u·delta (group + M1) and traces it.
* ``sham_evaluator``    - u drives an optically NULL edit (in-plane shift of
                          the combiner group); an honest scene path must not
                          reach the targets.
* ``leaky_evaluator``   - ignores geometry, returns the ideal design curve
                          (with gamma read from the scene).  It stands for a
                          runner bug that bypasses the scene.

Result: the leaky evaluator satisfies every criterion and control currently
frozen in EXP-002; the sham control separates it from the honest one.
"""

from __future__ import annotations

import math
from pathlib import Path
import sys
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
for p in (HERE, HERE.parent / "core", HERE.parent / "tests"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import opt013_probe_audit as geo_tools  # noqa: E402  (nonrect60 records)
from mz_exp001_plan import controls  # noqa: E402
from mz_geometry_optimizer import fit_port_a  # noqa: E402
from mz_scene import trace_mz  # noqa: E402
from readback_reconstruct import rebuild  # noqa: E402

B_GEO = next(c for c in controls() if c.name == "B-geo")
TARGETS = ((0.75, 0.10), (0.25, 0.90))


def _trace(geo, opt):
    rec = {"objects": {r: {"matrix_world": geo_tools._matrix(*geo[r])} for r in geo}, "optics": opt}
    return trace_mz(rebuild(rec))


def scene_evaluator(coherence: float = 1.0, log: list | None = None):
    def evaluate(u):
        if log is not None:
            log.append(u)
        geo, opt = geo_tools.base_geometry(), geo_tools.base_optics()
        opt["mz_source"]["mutual_coherence"] = coherence
        for role in ("mz_bs2", "mz_detector_a", "mz_detector_b"):
            geo[role][0] = geo_tools._add(geo[role][0], geo_tools._mul(B_GEO.group_delta, u))
        geo["mz_mirror1"][0] = geo_tools._add(geo["mz_mirror1"][0], geo_tools._mul(B_GEO.mirror1_delta, u))
        return _trace(geo, opt)
    return evaluate


def sham_evaluator(amplitude: float = 0.3):
    """u moves the combiner group inside the BS2 plane: optically null here."""
    tangent = geo_tools._normalize((1.0, 1.0, 0.0))

    def evaluate(u):
        geo, opt = geo_tools.base_geometry(), geo_tools.base_optics()
        for role in ("mz_bs2", "mz_detector_a", "mz_detector_b"):
            geo[role][0] = geo_tools._add(geo[role][0], geo_tools._mul(tangent, amplitude * u))
        return _trace(geo, opt)
    return evaluate


def leaky_evaluator(coherence: float = 1.0):
    """A runner bug: geometry never changes, P_A comes from the design curve."""
    frozen = _trace(geo_tools.base_geometry(), geo_tools.base_optics())

    def evaluate(u):
        pa = 0.5 * (1.0 - coherence * math.cos(math.pi * u))
        return SimpleNamespace(status="ok", interference_valid=True,
                               optical_a=(pa / 3,) * 3, optical_b=((1 - pa) / 3,) * 3,
                               escape_rgb=(0.0,) * 3, unresolved_rgb=(0.0,) * 3,
                               residual_rgb=(0.0,) * 3, mode_overlap=frozen.mode_overlap)
    return evaluate


def frozen_evaluator(start: float):
    """Contract's frozen-geometry control: the scene stays at `start`."""
    real = scene_evaluator()
    return lambda _u: real(start)


def criteria(make_eval) -> dict:
    """Current EXP-002 success test plus its two frozen negative controls."""
    runs = [fit_port_a(make_eval(1.0), t, s) for t, s in TARGETS]
    frozen = [fit_port_a(frozen_evaluator(s), t, s) for t, s in TARGETS]
    incoh = fit_port_a(make_eval(0.0), *TARGETS[0])
    return {
        "both_targets_converged": all(r.converged for r in runs),
        "updates": [r.updates for r in runs],
        "final_u": [r.final_u for r in runs],
        "final_error": [abs(r.observations[-1].power_a - r.target) for r in runs],
        "frozen_control_fails_as_required": not any(r.converged for r in frozen),
        "incoherent_control_holds": (not incoh.converged and
                                     all(abs(o.power_a - 0.5) <= 1e-9 for o in incoh.observations)),
    }


def sham(make_eval=None) -> dict:
    ev = make_eval or sham_evaluator()
    runs = [fit_port_a(ev, t, s) for t, s in TARGETS]
    return {"converged": [r.converged for r in runs], "stop": [r.stop_reason for r in runs],
            "final_power_a": [r.observations[-1].power_a for r in runs]}


def main():
    import json
    out = {
        "honest_scene": criteria(scene_evaluator),
        "leaky_formula": criteria(leaky_evaluator),
        "sham_honest": sham(),
        "sham_leaky": sham(leaky_evaluator()),
        "max_engine_minus_design_curve": max(
            abs(sum(scene_evaluator()(k / 200).optical_a) - math.sin(math.pi * k / 400) ** 2)
            for k in range(201)),
    }
    print(json.dumps(out, indent=2))
    return out


if __name__ == "__main__":
    main()
