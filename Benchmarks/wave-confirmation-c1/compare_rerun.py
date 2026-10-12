"""Compare an independent WAVE-C1 rerun with the committed results (powers, errors and decisions)."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent


def powers(section: dict, key: str) -> list[float]:
    return [p for row in section[key] for p in row["P"]]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rerun", type=Path)
    parser.add_argument("--reference", type=Path, default=HERE / "results" / "WAVE_C1_RESULTS.json")
    parser.add_argument("--tolerance", type=float, default=1e-9)
    args = parser.parse_args()
    ref = json.loads(args.reference.read_text(encoding="utf-8"))
    new = json.loads(args.rerun.read_text(encoding="utf-8"))
    worst, problems = 0.0, []
    for section in ("primary", "cascade"):
        for key in ("solver_reference", "model_M0", "model_M1"):
            a, b = powers(ref[section], key), powers(new[section], key)
            if len(a) != len(b):
                problems.append(f"{section}.{key}: length {len(a)} != {len(b)}")
                continue
            worst = max(worst, max(abs(x - y) for x, y in zip(a, b)))
    for a, b in zip(ref["crosscheck_fdtd"]["points"], new["crosscheck_fdtd"]["points"]):
        for variant in ("i", "ii", "iii"):
            worst = max(worst, max(abs(x - y) for x, y in zip(a[variant]["P"], b[variant]["P"])))
    for section, key in (("primary", "H_C1"), ("primary", "H_C0"), ("crosscheck_fdtd", "H_C2"), ("cascade", "H_C3")):
        if ref[section][key] != new[section][key]:
            problems.append(f"decision {key}: {ref[section][key]} != {new[section][key]}")
    regime = ("fraction_paths_in_regime_at_captured_lambda", "largest_lambda_BU_all_paths_in_regime", "terminal_paths")
    for key in regime:
        a, b = ref["network_regime"][key], new["network_regime"][key]
        if abs(a - b) > args.tolerance * max(1.0, abs(a)):
            problems.append(f"regime {key}: {a} != {b}")
    if worst > args.tolerance:
        problems.append(f"max power difference {worst} > {args.tolerance}")
    print(json.dumps({"max_abs_power_difference": worst, "tolerance": args.tolerance, "problems": problems,
                      "reference_environment": ref["environment"], "rerun_environment": new["environment"]}, indent=1))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
