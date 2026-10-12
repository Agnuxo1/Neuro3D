"""Write section-18 records for Claude's closure experiments after their results are published.

Each record cites its preregistration commit and the commit that published its
results; both must already be on origin. Validation uses agent_support's
validate_experiment_record; problems are stored, never hidden.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agent_support"))
from closure_integrity import validate_experiment_record  # noqa: E402

BRANCH = "claude/closure-guide-v2-20261012"


def source(path: str) -> dict:
    return {"path": path, "sha256": hashlib.sha256((ROOT / path).read_bytes()).hexdigest()}


def on_origin(commit: str) -> bool:
    remote = subprocess.check_output(["git", "rev-parse", "origin/" + BRANCH], cwd=ROOT, text=True).strip()
    return subprocess.run(["git", "merge-base", "--is-ancestor", commit, remote], cwd=ROOT).returncode == 0


def jev() -> list[dict]:
    record = json.loads((ROOT / "Docs/closure-20261012/claude/jev-wave-c1.json").read_text(encoding="utf-8"))
    return [{"question": c["question"], "answer": c["answer"], "date": record["date"], "provenance": record["provenance"],
             "confidence": c["confidence"]} for c in record["consultations"]]


def wave_record() -> dict:
    res = json.loads((ROOT / "Benchmarks/wave-confirmation-c1/results/WAVE_C1_RESULTS.json").read_text(encoding="utf-8"))
    p, x, c, g = res["primary"], res["crosscheck_fdtd"], res["cascade"], res["network_regime"]
    base = "Benchmarks/wave-confirmation-c1/"
    return {
        "id": "EXP-006-WAVE-C1-20261012-001",
        "hypothesis": "H-C1: the P1-7 path model with free paraxial Gaussian diffraction (M1) predicts the 45-degree MZI modal powers of the continuous device within Emax <= 0.02 over 21 phases and 2 ports",
        "alternative": "Emax(M1) > 0.02; secondary H-C0 (M0 refutation replicated), H-C2 (archived FDTD within 0.005), H-C3 (two-MZI cascade)",
        "protocol_commit": "7327b67ab9be95ed92efa63a8a752df0d5e4a41a",
        "sources": [source(base + f) for f in ("PROTOCOL-WAVE-C1.md", "angular_spectrum_wave.py", "run_wave_c1.py",
                                                "test_angular_spectrum_wave.py", "results/WAVE_C1_RESULTS.json", "RESULTS-WAVE-C1.md")],
        "inputs": {"device": res["device"], "archived_fdtd_points": x["count"],
                   "captured_scene": "Docs/validation/native-deferred-training-2026-10-09/attempt01/worker/initial_native_scene.json"},
        "environment": res["environment"],
        "seeds": [],
        "resource_budget": {"cpu_processes": 1, "blas_threads": 1, "wall_limit_s": 1800, "gpu": False},
        "deadline": "2026-10-12",
        "commands": ["cd Benchmarks/wave-confirmation-c1 && python run_wave_c1.py"],
        "exit_codes": [0],
        "results": {"Emax_M1": p["Emax_M1"], "Emax_M0": p["Emax_M0"], "solver_self_consistency": p["self_consistency_max_abs_dP"],
                    "flux_balance": p["max_abs_flux_balance"], "fdtd_crosscheck_max": x["max_abs_diff_vs_fdtd"],
                    "cascade_Emax_M1": c["Emax_M1"], "cascade_Emax_M0": c["Emax_M0"],
                    "network_paths_in_regime": g["fraction_paths_in_regime_at_captured_lambda"],
                    "network_lambda_rescale_needed": g["rescale_factor_lambda_needed"], "seconds": res["seconds_total"]},
        "independent_oracle": "Mesh-free angular-spectrum reference sharing no code with the P1-7 FDTD or the path models; 11 verification tests including an independent direct plane-wave quadrature; external Linux CI rerun 38314187345 reproduced every power within 8.9e-16 and every decision",
        "decision_rule": "Solver self-consistency and energy balance <= 1e-9, then H-C1 CONFIRMED iff Emax(M1) <= 0.02 (P1-7 budget unchanged)",
        "decision": f"H-C1 {p['H_C1']}; H-C0 {p['H_C0']}; H-C2 {x['H_C2']}; H-C3 {c['H_C3']}",
        "deviations": [],
        "limitations": ["Confirmation not blind: exploratory P1-7 values were known and stated as predictions",
                        "2D scalar Ez, infinite planar elements without edge diffraction, lossless film, ideal conductor, w = 8 lambda",
                        "21 of 63 cascade configurations carry no light into stage 2 (stage-1 dark port); found after execution and declared",
                        "The captured network is outside the diffraction-free regime at lambda = 0.1 BU; no physical validation of it"],
        "published_commit": "aeffaa3cb199f8011aff03276c42e0e3e4da2ff5",
        "status": "PASS",
        "jev_consultations": jev(),
    }


def capacity_record() -> dict | None:
    path = ROOT / "Benchmarks/geometry-capacity-k1/results/HA_K1_RESULTS.json"
    meta = ROOT / "Benchmarks/geometry-capacity-k1/results/PUBLISHED_COMMIT.txt"
    if not path.exists() or not meta.exists():
        return None
    res = json.loads(path.read_text(encoding="utf-8"))
    base = "Benchmarks/geometry-capacity-k1/"
    h1, h2, ctrl = res["H_A1"], res["H_A2"], res["C_A3"]
    status = "PASS" if h1["decision"] in ("SUPPORTED", "OPPOSITE") and ctrl["met"] else "PARTIAL"
    return {
        "id": "EXP-006-HA-K1-20261012-001",
        "hypothesis": "H-A1: on linear-teacher tasks the free linear optical class beats the captured 16-parameter geometry in test accuracy; H-A2: on quadratic-teacher tasks the quadratic class beats the free linear class",
        "alternative": "No positive paired difference (Wilcoxon one-sided, Holm, bootstrap interval) over 10 seeds",
        "protocol_commit": "57dc00229c4cfb47ccb12d34dc225a5953f28256",
        "sources": [source(base + f) for f in ("PROTOCOL-HA-K1.md", "capacity_k1.py", "results/HA_K1_RESULTS.json", "RESULTS-HA-K1.md")],
        "inputs": {"captured_network": "Docs/validation/native-deferred-training-2026-10-09/attempt01/worker/initial_native_{scene,graph}.json",
                   "tasks": "synthetic teachers, seeds 0-9, 400 train / 2000 test"},
        "environment": res["environment"],
        "seeds": list(range(10)),
        "resource_budget": {"cpu_processes": 1, "blas_threads": 1, "wall_limit_s": 7200, "gpu": False},
        "deadline": "2026-10-13",
        "commands": ["cd Benchmarks/geometry-capacity-k1 && python capacity_k1.py"],
        "exit_codes": [0],
        "results": {"means": res["means"], "H_A1": {k: h1[k] for k in ("mean_difference", "holm_p", "decision")},
                    "H_A2": {k: h2[k] for k in ("mean_difference", "holm_p", "decision")}, "C_A3": ctrl,
                    "decision_dimension": {"geom": sorted({d["decision_rank"] for d in res["dimension"]["geom"]}),
                                           "lin": res["dimension"]["lin_decision_ranks"], "quad": res["dimension"]["quad_decision_rank"]},
                    "inert_parameters": res["dimension"]["inert_parameters_for_decision_detectors"], "seconds": res["seconds_total"]},
        "independent_oracle": "Teacher labels generated independently of every student; every kept geometry rebuilt by the exact CPU graph builder; statistics from agent_support closure_statistics",
        "decision_rule": "SUPPORTED iff Holm-adjusted one-sided Wilcoxon p < 0.05 and paired bootstrap 95 % lower end > 0; C-A3 requires mean S_geom accuracy on T_geom >= 0.95",
        "decision": f"H-A1 {h1['decision']}; H-A2 {h2['decision']}; C-A3 {'met' if ctrl['met'] else 'not met'}",
        "deviations": [],
        "limitations": ["Synthetic teacher tasks measure representational restriction and optimizer reach, not real-data generalization",
                        "Represented scalar model on CPU; the captured scene is outside the diffraction-free regime (WAVE-C1)",
                        "Fixed student hyperparameters; a different optimizer budget could change S_geom"],
        "published_commit": meta.read_text(encoding="utf-8").strip(),
        "status": status,
        "jev_consultations": [],
    }


def g1_record() -> dict | None:
    path = ROOT / "Benchmarks/compiled-operator-g1/results/G1_RESULTS.json"
    meta = ROOT / "Benchmarks/compiled-operator-g1/results/PUBLISHED_COMMIT.txt"
    if not path.exists() or not meta.exists():
        return None
    res = json.loads(path.read_text(encoding="utf-8"))
    base = "Benchmarks/compiled-operator-g1/"
    return {
        "id": "EXP-006-G1-20261013-001",
        "hypothesis": "H-G1: with recompilation charged every call, the compiled operator is at least 2x faster than graph traversal for batches 150 and 4096, inference and training step",
        "alternative": "Any decisive cell below 2x with equivalence holding",
        "protocol_commit": subprocess.check_output(["git", "rev-parse", "b857779"], cwd=ROOT, text=True).strip(),
        "sources": [source(base + f) for f in ("PROTOCOL-G1.md", "run_g1.py", "results/G1_RESULTS.json", "RESULTS-G1.md")],
        "inputs": {"captured_network": "Docs/validation/native-deferred-training-2026-10-09/attempt01/worker/initial_native_{scene,graph}.json",
                   "batches": [1, 150, 4096], "repeats": 15},
        "environment": res["environment"],
        "seeds": [4242, 7],
        "resource_budget": {"cpu_processes": 1, "blas_threads": 1, "wall_limit_s": 1500, "gpu": False},
        "deadline": "2026-10-13",
        "commands": ["cd Benchmarks/compiled-operator-g1 && python run_g1.py"],
        "exit_codes": [0],
        "results": {"equivalence": res["equivalence"], "min_decisive_ratio": res["min_decisive_ratio"],
                    "ratios": {k: v["ratio_graph_over_compiled_with_recompile"] for k, v in res["cells"].items()},
                    "cached_ratios": {k: v["ratio_graph_over_cached"] for k, v in res["cells"].items()}},
        "independent_oracle": "Graph traversal and compiled operator are separate computations of the same fields and tangents; equivalence checked before timing",
        "decision_rule": "CONFIRMED iff equivalence holds and every decisive median ratio >= 2",
        "decision": f"H-G1 {res['H_G1']}",
        "deviations": [],
        "limitations": ["Local CPU timing with uncontrolled host load; not a scaling law", "No GPU, RT, energy or physical claim"],
        "published_commit": meta.read_text(encoding="utf-8").strip(),
        "status": "FAIL" if res["H_G1"] == "REFUTED" else "PASS",
        "jev_consultations": [],
    }


def main() -> int:
    records = [wave_record()]
    for extra in (capacity_record(), g1_record()):
        if extra:
            records.append(extra)
    for r in records:
        for key in ("protocol_commit", "published_commit"):
            if not on_origin(r[key]):
                raise SystemExit(f"{r['id']}: {key} {r[key]} is not on origin/{BRANCH}")
    problems = {r["id"]: validate_experiment_record(r) for r in records}
    out = {"schema": "neuro3d.closure.experiment_registry.v1", "agent": "Claude", "records": records,
           "validation_problems": problems,
           "scope": "Complete metadata does not itself establish scientific truth or external replication"}
    target = ROOT / "Docs/closure-20261012/claude/experiment-registry-claude.json"
    target.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(problems))
    return 0 if not any(problems.values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
