"""Figures generated only from results/WAVE_C1_RESULTS.json (no recomputation)."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
INK, MUTED, GRID = "#1f2933", "#7b8794", "#e4e7eb"
SOLVER, M0, M1, CROSS = "#0b7285", "#c92a2a", "#2b8a3e", "#e8590c"


def style(ax, title):
    ax.set_title(title, loc="left", fontsize=10.5, color=INK, fontweight="bold")
    ax.grid(color=GRID, linewidth=0.8)
    ax.tick_params(colors=INK, labelsize=8.5)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(MUTED)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=HERE / "results" / "WAVE_C1_RESULTS.json")
    parser.add_argument("--out", type=Path, default=HERE / "results")
    args = parser.parse_args()
    data = json.loads(args.results.read_text(encoding="utf-8"))
    p, c, x, g = data["primary"], data["cascade"], data["crosscheck_fdtd"], data["network_regime"]
    dl = np.array(p["effective_path_difference_lambda"])
    sol = np.array([r["P"] for r in p["solver_reference"]])
    m0 = np.array([r["P"] for r in p["model_M0"]])
    m1 = np.array([r["P"] for r in p["model_M1"]])

    fig, axes = plt.subplots(1, 3, figsize=(13.2, 3.9), dpi=160)
    ax = axes[0]
    for port, marker in ((0, "o"), (1, "s")):
        ax.plot(dl, m0[:, port], "--", color=M0, lw=1.2, label="M0 no diffraction" if port == 0 else None)
        ax.plot(dl, m1[:, port], "-", color=M1, lw=1.4, label="M1 free diffraction" if port == 0 else None)
        ax.plot(dl, sol[:, port], marker, color=SOLVER, ms=3.6, mfc="white", mew=1.1,
                label=f"Reference P{port + 1}")
    ax.set_xlabel("effective path difference (λ)", fontsize=9, color=INK)
    ax.set_ylabel("modal output power", fontsize=9, color=INK)
    ax.set_ylim(-0.04, 1.32)
    ax.legend(fontsize=7.2, frameon=False, loc="upper center", ncol=2)
    style(ax, "a  MZI, continuous device, 21 phases")

    ax = axes[1]
    e0 = np.max(np.abs(sol - m0), axis=1)
    e1 = np.max(np.abs(sol - m1), axis=1)
    ax.axhline(0.02, color=INK, lw=0.9, ls=":")
    ax.text(0.02, 0.0207, "budget 0.02", fontsize=7.5, color=INK)
    ax.plot(dl, e0, "-o", color=M0, ms=3, lw=1.2, label=f"M0  Emax {p['Emax_M0']:.4f}")
    ax.plot(dl, e1, "-o", color=M1, ms=3, lw=1.2, label=f"M1  Emax {p['Emax_M1']:.4f}")
    for ppl, marker in ((16, "^"), (24, "v")):
        pts = [q for q in x["points"] if q["ppl"] == ppl]
        ax.plot([q["dL_eff"] for q in pts], [q["ii"]["max_abs_diff_vs_fdtd"] for q in pts], marker,
                color=CROSS, ms=3.8, mfc="white", label=f"|FDTD λ/{ppl} − reference (ii)|")
    ax.set_ylim(0, 0.035)
    ax.set_xlabel("effective path difference (λ)", fontsize=9, color=INK)
    ax.set_ylabel("max |ΔP| over ports", fontsize=9, color=INK)
    ax.set_ylim(0, 0.042)
    ax.legend(fontsize=7, frameon=False, loc="upper right", ncol=2)
    style(ax, "b  Errors and FDTD cross-check")

    ax = axes[2]
    s2 = np.array([r["P"] for r in c["solver_reference"]])
    c0 = np.max(np.abs(s2 - np.array([r["P"] for r in c["model_M0"]])), axis=1)
    c1 = np.max(np.abs(s2 - np.array([r["P"] for r in c["model_M1"]])), axis=1)
    idx = np.arange(len(c0))
    ax.axhline(0.02, color=INK, lw=0.9, ls=":")
    ax.bar(idx, c0, color=M0, alpha=0.35, width=0.9, label=f"M0  Emax {c['Emax_M0']:.3f}")
    ax.bar(idx, c1, color=M1, width=0.9, label=f"M1  Emax {c['Emax_M1']:.4f}")
    for k in (21, 42):
        ax.axvline(k - 0.5, color=MUTED, lw=0.7)
    ax.set_xticks([10, 31, 52], ["ΔL₁ = 0", "ΔL₁ = λ/4", "ΔL₁ = λ/2"], fontsize=8)
    ax.text(52, 0.004, "\n".join(["stage-1 P1 dark:", "no light reaches", "stage 2"]), ha="center", fontsize=7, color=MUTED)
    ax.set_ylabel("max |ΔP| over ports", fontsize=9, color=INK)
    ax.legend(fontsize=7.5, frameon=False, loc="upper right")
    style(ax, "c  Two-MZI cascade, 63 configurations")
    fig.tight_layout()
    first = args.out / "wave-c1-confirmation.png"
    fig.savefig(first, facecolor="white")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.6, 3.6), dpi=160)
    rows = [("path length L/λ", g["path_length_over_lambda"]), ("limiting aperture D/λ", g["limiting_aperture_over_lambda"]),
            ("ζ with largest unclipped beam", g["zeta_with_largest_unclipped_beam"])]
    for i, (label, q) in enumerate(rows):
        ax.plot([q["min"], q["max"]], [i, i], color=SOLVER, lw=6, solid_capstyle="round", alpha=0.55)
        ax.plot(q["median"], i, "o", color=INK, ms=5)
        ax.text(q["max"] * 1.15, i, f"{q['min']:.3g} – {q['max']:.3g}", va="center", fontsize=8, color=INK)
    ax.axvline(g["zeta_max"], color=M0, lw=1.1, ls="--")
    ax.text(g["zeta_max"] * 1.1, 2.35, f"ζmax = {g['zeta_max']:.3f}", color=M0, fontsize=8)
    ax.set_xscale("log")
    ax.set_xlim(0.1, 5000)
    ax.set_yticks(range(3), [r[0] for r in rows], fontsize=8.5)
    ax.set_ylim(-0.6, 2.7)
    ax.set_xlabel("value (log scale); bar = range, dot = median over 17,060 paths", fontsize=8.5, color=INK)
    style(ax, f"Captured network, λ = {g['lambda_BU']} BU: {100 * g['fraction_paths_in_regime_at_captured_lambda']:.0f} % of paths in regime")
    fig.tight_layout()
    second = args.out / "wave-c1-network-regime.png"
    fig.savefig(second, facecolor="white")
    plt.close(fig)
    for path in (first, second):
        print(path.name, hashlib.sha256(path.read_bytes()).hexdigest())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
