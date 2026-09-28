"""Expected values for the next OPT-002 step: beam width/overlap and coherence (Claude).

Square MZ (default_scene layout, 45 deg), mirror2 moved by d along -normal:
  wavefront delta_L = 2 d cos45 = sqrt(2) d      -> delta_phi = k sqrt(2) d
  beam separation perpendicular to propagation s_perp = 2 d sin45 = sqrt(2) d
  (NOT the separation of the hits on the 45 deg combiner, which is 2 d)
Gaussian beams of waist w (1/e^2 intensity radius): overlap gamma = exp(-s_perp^2 / (2 w^2)).
Ports use the mixture model of geometry_oracle.mz_ledger (exact conservation).
Incoherent control: gamma = 0 -> A = B = 1/2 for every phase.
Frequency mismatch control: cross factor = mz_oracle.cross_term_average.
Run: python overlap_cases.py  -> expected_overlap_coherence.json
"""

from __future__ import annotations

import json
import math

from geometry_oracle import Arm, mz_ledger, square_single_mirror
from mz_oracle import cross_term_average, gaussian_overlap


def square_offset_case(d: float, wavelength: float, waist: float | None, gamma_source: float = 1.0) -> dict:
    geo = square_single_mirror(d)
    s_perp = geo["lateral_shift"]
    overlap = 1.0 if waist is None else gaussian_overlap(s_perp, waist)
    dphi = 2 * math.pi * geo["delta_L_wavefront"] / wavelength
    led = mz_ledger(1.0, 0.5, 0.5, Arm(), Arm(), dphi, gamma_source, overlap)
    return {"d": d, "wavelength": wavelength, "waist": waist, "gamma_source": gamma_source,
            "delta_L_wavefront": geo["delta_L_wavefront"], "s_perp": s_perp,
            "hit_separation_on_bs2": 2 * d, "overlap": overlap,
            "delta_phi": dphi, "port_a": led["port_a"], "port_b": led["port_b"],
            "residual": led["residual"]}


def build() -> dict:
    lam = 0.02
    d_half = lam / (2 * math.sqrt(2))       # delta_L = lambda/2
    cases = []
    for waist in (None, 0.2, 0.05, 0.01):
        cases.append(square_offset_case(d_half, lam, waist))
    incoherent = [square_offset_case(d_half * k / 4, lam, None, gamma_source=0.0) for k in range(9)]
    freq = [{"delta_f": df, "t_int": 1.0, "cross_factor_dphi0": cross_term_average(0.0, df, 1.0)}
            for df in (0.0, 0.5, 1.0, 10.0, 1000.0)]
    return {
        "note": "Plane-wave + Gaussian overlap reference; not a beam-propagation or Maxwell solver.",
        "square_destructive_vs_waist": cases,
        "incoherent_sweep_gamma0": incoherent,
        "frequency_mismatch_cross_factor": freq,
    }


if __name__ == "__main__":
    data = build()
    with open("expected_overlap_coherence.json", "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
    for c in data["square_destructive_vs_waist"]:
        print(f"w={c['waist']}: s_perp={c['s_perp']:.5f} overlap={c['overlap']:.6f} A={c['port_a']:.6f} B={c['port_b']:.6f}")
    print("incoherent A range:", min(c["port_a"] for c in data["incoherent_sweep_gamma0"]),
          max(c["port_a"] for c in data["incoherent_sweep_gamma0"]))
