"""Write a receipt of the v2 CPU controls; never overwrite an earlier receipt.

Synthetic support controls only: no Neuro3D training, GPU, blind task, or
full-device physical validation is executed here.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import platform

import numpy as np
import scipy

from closure_evidence import write_report
from closure_limits import detection_energy_per_mac, landauer_energy, photon_energy, shot_noise_photons
from closure_reference import Interval, exact_first_hit, pi_interval
from closure_v2 import coherent_field_v2, exact_first_hit_v2
from closure_wave import angular_spectrum_1d, gaussian_1d, modal_amplitude


def control_result() -> dict:
    """Evaluate the corrected first hit, bounded enclosures, P1-7 overlap and scales."""
    near = {"primitive_id": "near", "object_id": "A", "vertices": [(-2, -1, 1), (2, -1, 1), (0, 2, 1)]}
    far = {"primitive_id": "far-degenerate", "object_id": "B", "vertices": [(0, 0, 50)]*3}
    v1, v2 = exact_first_hit((0, 0, 0), (0, 0, 1), [near, far]), exact_first_hit_v2((0, 0, 0), (0, 0, 1), [near, far])
    amp = (Interval.point(1), Interval.point(0))
    dark = coherent_field_v2([(amp, Interval.point(0)), (amp, pi_interval())])
    power = dark[0].square()+dark[1].square()
    lam, w, z = 1.0, 8.0, 95.0
    y = np.linspace(-200, 200, 8192, endpoint=False)
    dy = float(y[1]-y[0])
    g0 = gaussian_1d(y, 0, lam, w)
    overlap = abs(modal_amplitude(angular_spectrum_1d(g0, dy, z, lam), g0, dy))**2
    zeta = 2*z/((2*math.pi/lam)*w*w)
    return {"schema": "neuro3d.closure.support_controls.v2",
            "scope": "Synthetic CPU support controls; not a claim about the complete Neuro3D device",
            "environment": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
            "first_hit_far_degenerate": {"v1": v1["status"], "v2": v2["status"], "v2_parameter": str(v2.get("parameter"))},
            "dark_power_upper_bound_v2": float(power.hi),
            "p17_free_space_overlap": {"waist_lambda": w, "distance_lambda": z, "angular_spectrum": overlap,
                                       "paraxial_closed_form": 1/math.sqrt(1+zeta*zeta/4),
                                       "scope": "Scalar free-space overlap only; not the FDTD device"},
            "reference_scales": {"photon_energy_1550nm_J": photon_energy(1550e-9),
                                 "landauer_300K_J": landauer_energy(300.0),
                                 "photons_full_scale_4bit_k2": shot_noise_photons(4, 2.0),
                                 "detection_energy_per_mac_4bit_fanin5_J": detection_energy_per_mac(4, 1550e-9, 5),
                                 "scope": "Ideal Poisson detection design scale; lasers, modulators and electronics excluded"}}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    report = control_result()
    write_report(args.out, report)
    print(json.dumps({"receipt": str(args.out), "scope": report["scope"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
