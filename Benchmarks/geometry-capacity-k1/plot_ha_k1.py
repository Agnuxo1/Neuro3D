"""Figure generated only from results/HA_K1_RESULTS.json (no recomputation)."""
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
COLORS = {"S_quad": "#5f3dc4", "S_lin": "#0b7285", "S_geom": "#e8590c"}
LABELS = {"S_quad": "F_quad student", "S_lin": "F_lin student (free)", "S_geom": "F_geom student (captured, 16 params)"}
TEACHERS = {"T_lin": "linear teacher", "T_quad": "quadratic teacher", "T_geom": "geometry teacher (control)"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=HERE / "results" / "HA_K1_RESULTS.json")
    parser.add_argument("--out", type=Path, default=HERE / "results" / "ha-k1-capacity.png")
    args = parser.parse_args()
    data = json.loads(args.results.read_text(encoding="utf-8"))
    rows = [r for r in data["seeds"] if "teachers" in r]
    fig, ax = plt.subplots(figsize=(8.6, 3.9), dpi=160)
    width = 0.26
    for ti, teacher in enumerate(TEACHERS):
        for si, student in enumerate(COLORS):
            values = [r["teachers"][teacher][student]["test"] for r in rows if r["teachers"][teacher][student]["test"] is not None]
            x = ti + (si - 1) * width
            ax.bar(x, np.mean(values), width * 0.9, color=COLORS[student], alpha=0.85,
                   label=LABELS[student] if ti == 0 else None)
            jitter = np.linspace(-width * 0.28, width * 0.28, len(values))
            ax.plot(x + jitter, values, "o", ms=2.6, color=INK, alpha=0.65)
        majority = np.mean([r["teachers"][teacher]["majority_test_rate"] for r in rows])
        ax.hlines(majority, ti - 1.5 * width, ti + 1.5 * width, color=MUTED, lw=1, ls="--",
                  label="majority class" if ti == 0 else None)
    ax.axhline(0.95, color=INK, lw=0.7, ls=":")
    ax.set_xticks(range(3), list(TEACHERS.values()), fontsize=9)
    ax.set_ylim(0.3, 1.02)
    ax.set_ylabel("test accuracy (10 seeds, 2000 inputs each)", fontsize=9, color=INK)
    a1, a2 = data["H_A1"], data["H_A2"]
    ax.set_title(f"HA-K1  H-A1 {a1['decision']} (Δ {a1['mean_difference']:+.3f})   "
                 f"H-A2 {a2['decision']} (Δ {a2['mean_difference']:+.3f})", loc="left", fontsize=10, color=INK, fontweight="bold")
    ax.grid(axis="y", color=GRID)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.legend(fontsize=7.5, frameon=False, loc="lower left", ncol=2)
    fig.tight_layout()
    fig.savefig(args.out, facecolor="white")
    print(args.out.name, hashlib.sha256(args.out.read_bytes()).hexdigest())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
