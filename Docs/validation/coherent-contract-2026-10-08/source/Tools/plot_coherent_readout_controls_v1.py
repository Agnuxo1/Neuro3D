"""Plot exact algebraic readout controls, never captured-scene outputs."""
import argparse
from fractions import Fraction as F
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from Blender.blender_lab.coherent_contract_v1 import modal_power


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--receipt", required=True, type=Path)
    args = parser.parse_args()
    if args.out.exists() or args.receipt.exists():
        raise ValueError("fresh outputs required")
    rows = []
    for name, second in [("Constructiva", (1, 0)), ("Destructiva", (-1, 0)), ("Cuadratura", (0, 1))]:
        fields = {"a": (1, 0), "b": second}
        coherent = modal_power(fields, expected_source_ids=["a", "b"])["normalized_modal_power"]
        independent = sum((F(x)**2 + F(y)**2 for x, y in fields.values()), F(0))
        rows.append({"name": name, "input_a_reim": [1, 0], "input_b_reim": list(second),
                     "coherent_normalized_power": int(coherent), "independent_normalized_power": int(independent)})
    assert [row["coherent_normalized_power"] for row in rows] == [4, 0, 2]
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8.5, 4.8), layout="constrained")
    positions = range(len(rows))
    ax.bar([v - .18 for v in positions], [row["coherent_normalized_power"] for row in rows], .34,
           color="#176b87", label="Campo común: |Ea + Eb|²")
    ax.bar([v + .18 for v in positions], [row["independent_normalized_power"] for row in rows], .34,
           color="#cf8d40", label="Fuentes independientes: |Ea|² + |Eb|²")
    ax.set_xticks(list(positions), [row["name"] for row in rows])
    ax.set_ylabel("Potencia modal normalizada")
    ax.set_ylim(0, 4.7)
    ax.set_title("Contrato óptico: términos de interferencia", loc="left", weight="bold")
    ax.legend(loc="upper right", fontsize=9)
    ax.spines[["top", "right"]].set_visible(False)
    ax.text(.5, -.19, "Controles algebraicos exactos; no son salidas propagadas de Iris ni mediciones físicas.",
            transform=ax.transAxes, ha="center", fontsize=9)
    fig.savefig(args.out, dpi=150, facecolor="white")
    plt.close(fig)
    args.receipt.write_text(json.dumps({"schema": "optic_neuro_blender.exact_readout_controls.v1", "controls": rows,
        "optical_forward_executed": False, "gpu_executed": False, "physical_measurement": False}, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
