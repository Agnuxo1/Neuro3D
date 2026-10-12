"""Run explicit CPU reference controls and save their complete outputs.

The examples are synthetic support-kit controls, not a Neuro3D training result,
blind task, GPU experiment, or full-device physical validation.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as F
import json
from pathlib import Path
import platform

import numpy as np
import scipy

from closure_reference import (Interval, exact_first_hit, phase_from_length,
    coherent_field, modal_power, certified_argmax)
from closure_coherent import exact_roundoff_report, greedy_order
from closure_wave import gaussian_1d, angular_spectrum_1d, modal_amplitude
from closure_evidence import write_report


def control_result() -> dict:
    """Evaluate geometric, interference, cancellation, and free-space controls."""
    triangle = {"primitive_id": "thin-plane", "object_id": "plane",
                "vertices": [(-2, -1, F(1, 2**80)), (2, -1, F(1, 2**80)), (0, 2, F(1, 2**80))]}
    hit = exact_first_hit((0, 0, 0), (0, 0, 1), [triangle])
    amplitude = (Interval.point(1), Interval.point(0))
    phase = phase_from_length(Interval.point(F(1, 2)), Interval.point(1))
    dark = modal_power(coherent_field([(amplitude, Interval.point(0)), (amplitude, phase)]))
    bright = modal_power(coherent_field([(amplitude, Interval.point(0)), (amplitude, Interval.point(0))]))
    terms = [1e16+1e16j, 1+2j, -1e16-1e16j]
    y = np.linspace(-20, 20, 4096, endpoint=False)
    spacing = float(y[1]-y[0])
    initial = gaussian_1d(y, 0, 0.1, 0.8)
    spectral = angular_spectrum_1d(initial, spacing, 2, 0.1)
    paraxial = gaussian_1d(y, 2, 0.1, 0.8)
    projection = modal_amplitude(spectral, paraxial, spacing)
    return {"schema": "neuro3d.closure.support_controls.v1",
            "scope": "Synthetic CPU support controls; not a claim about the complete Neuro3D device",
            "environment": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
            "first_hit": {"status": hit["status"], "parameter_exact": str(hit["parameter"]), "primitive_ids": hit["primitive_ids"]},
            "interference": {"dark_power": dark.outward_wire(), "bright_power": bright.outward_wire(),
                             "wire_scope": "128-bit dyadic outward serialization; bounds may widen",
                             "certified_argmax": certified_argmax([dark, bright])},
            "reductions": [exact_roundoff_report(terms, name) for name in ("naive", "pairwise", "fsum")],
            "diagnostic_permutation": greedy_order(terms),
            "free_space_control": {"samples": len(y), "spacing": spacing, "distance": 2, "wavelength": 0.1, "waist": 0.8,
                                   "max_field_difference": float(np.max(np.abs(spectral-paraxial))),
                                   "modal_amplitude": [projection.real, projection.imag],
                                   "observable": "Normalized scalar modal overlap; not calibrated electromagnetic flux"}}


def main() -> int:
    """Create a new control receipt; never overwrite a previous run."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    report = control_result()
    write_report(args.out, report)
    print(json.dumps({"receipt": str(args.out), "scope": report["scope"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
