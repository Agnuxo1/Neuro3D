"""Consolidate Claude's closure evidence into successor manifests and the canonical record.

Successor manifests are new files; the guide's original and Codex's current
manifests are not modified. The canonical acceptance JSON gains dated evidence
keys and appended text; no earlier statement or status prefix is removed.
"""
from __future__ import annotations

import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agent_support"))
from closure_evidence import verify_closure  # noqa: E402
from closure_v2 import verify_frontier  # noqa: E402

OUT = ROOT / "Docs/closure-20261012/claude"
CANONICAL = ROOT / "Docs/research/optic_neuro_blender_acceptance_v1.json"


def sha(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def put(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def evidence() -> dict:
    wave, cap, g1 = (load("Benchmarks/wave-confirmation-c1/results/WAVE_C1_RESULTS.json"),
                     load("Benchmarks/geometry-capacity-k1/results/HA_K1_RESULTS.json"),
                     load("Benchmarks/compiled-operator-g1/results/G1_RESULTS.json"))
    return {"wave": wave, "cap": cap, "g1": g1}


def manifests(ev: dict) -> dict:
    wave, cap, g1 = ev["wave"], ev["cap"], ev["g1"]
    closure = copy.deepcopy(load("Docs/closure-20261012/closure-manifest-current.json"))
    closure["snapshot_date"] = "2026-10-13"
    closure["scope"] = "Claude successor of closure-manifest-current.json; earlier manifests retained unchanged"
    notes = {
        5: f"HA-K1: decision dimension geom/lin/quad = 12/26/29, four inert translations; H-A1 {cap['H_A1']['decision']}, H-A2 {cap['H_A2']['decision']}, C-A3 met={cap['C_A3']['met']}",
        7: f"WAVE-C1: diffraction-inclusive path model CONFIRMED (Emax {wave['primary']['Emax_M1']:.4f}); captured network outside regime (0/17060 paths); full-network wave validation still open",
        8: f"G1: compiled operator vs graph traversal H-G1 {g1['H_G1']} (min ratio {g1['min_decisive_ratio']:.1f}); GPU/AMD/energy still open",
        10: "External Linux CI rerun of WAVE-C1 and Lean T1-T5; red-team agent report archived; human specialist critique still open",
    }
    for o in closure["objectives"]:
        if o["id"] in notes:
            o["remaining"] = list(o.get("remaining", [])) + ["Still open after: " + notes[o["id"]]]
    frontier = copy.deepcopy(load("Docs/closure-20261012/frontier-manifest-current.json"))
    frontier["snapshot_date"] = "2026-10-13"
    frontier["scope"] = "Claude successor of frontier-manifest-current.json; earlier manifests retained unchanged"
    for o in frontier["objectives"]:
        if o["id"] == "F1":
            o["state"] = "PARTIAL"
            o["remaining"] = [f"H-A executed (HA-K1: H-A1 {cap['H_A1']['decision']}, H-A2 {cap['H_A2']['decision']}); H-B certificate coverage, H-C sim-to-real (needs D0-B) and H-D energy/latency remain"]
        if o["id"] == "F2":
            o["remaining"] = ["T1-T5 compiled in core Lean (standard axioms only); Mathlib real/complex instantiation, operator-norm link, infinite sums, rank-4 bound and reachable-set theory beyond the local dimension count remain"]
        if o["id"] == "F6":
            o["state"] = "PARTIAL"
            o["remaining"] = ["Agent red-team report archived (no number refuted, four statements corrected); owner-sealed labels, human red team and optional Registered Report remain"]
    return {"closure": closure, "frontier": frontier}


def canonical(ev: dict) -> dict:
    wave, cap, g1 = ev["wave"], ev["cap"], ev["g1"]
    doc = load("Docs/research/optic_neuro_blender_acceptance_v1.json")
    stamp = "2026-10-13 (Claude closure branch)"
    doc["latest_wave_confirmation"] = {"protocol": "Benchmarks/wave-confirmation-c1/PROTOCOL-WAVE-C1.md",
        "protocol_commit": "7327b67ab9be95ed92efa63a8a752df0d5e4a41a", "result": "Benchmarks/wave-confirmation-c1/results/WAVE_C1_RESULTS.json",
        "result_sha256": sha("Benchmarks/wave-confirmation-c1/results/WAVE_C1_RESULTS.json"),
        "decisions": {k: wave[s][k] for s, k in (("primary", "H_C1"), ("primary", "H_C0"), ("crosscheck_fdtd", "H_C2"), ("cascade", "H_C3"))},
        "Emax_M1": wave["primary"]["Emax_M1"], "Emax_M0": wave["primary"]["Emax_M0"],
        "captured_network_paths_in_regime": wave["network_regime"]["fraction_paths_in_regime_at_captured_lambda"],
        "captured_network_lambda_rescale_needed": wave["network_regime"]["rescale_factor_lambda_needed"]}
    doc["latest_geometry_capacity"] = {"protocol": "Benchmarks/geometry-capacity-k1/PROTOCOL-HA-K1.md",
        "result": "Benchmarks/geometry-capacity-k1/results/HA_K1_RESULTS.json",
        "result_sha256": sha("Benchmarks/geometry-capacity-k1/results/HA_K1_RESULTS.json"),
        "H_A1": cap["H_A1"]["decision"], "H_A2": cap["H_A2"]["decision"], "C_A3_met": cap["C_A3"]["met"],
        "decision_dimension_geom_lin_quad": [12, 26, 29], "inert_parameters": cap["dimension"]["inert_parameters_for_decision_detectors"]}
    doc["latest_compiled_operator_ablation"] = {"protocol": "Benchmarks/compiled-operator-g1/PROTOCOL-G1.md",
        "result": "Benchmarks/compiled-operator-g1/results/G1_RESULTS.json",
        "result_sha256": sha("Benchmarks/compiled-operator-g1/results/G1_RESULTS.json"), "H_G1": g1["H_G1"],
        "min_ratio_with_recompile": g1["min_decisive_ratio"], "scope": "CPU represented model; no GPU, RT or energy claim"}
    doc["latest_formal_core"] = {"source": "Lean/closure-core/Bounds.lean", "source_sha256": sha("Lean/closure-core/Bounds.lean"),
        "record": "Docs/closure-20261012/claude/lean-bounds.json", "lemmas": ["T2", "T3 (scaled, per-tail)", "T4 (rank<=2, principal minors)", "T5"],
        "axioms": ["propext", "Classical.choice", "Quot.sound"], "mathlib": False}
    doc["latest_red_team"] = {"report": "Docs/closure-20261012/claude/RED-TEAM-WAVE-C1-LEAN.md",
        "scope": "Independent verifier agent, not human review", "refuted_numbers": 0, "corrected_statements": 4}
    for p in doc["priorities"]:
        if p["id"] == 6:
            p["achieved"] += (f" [{stamp}] WAVE-C1: independent mesh-free solver, same continuous device, 21 phases: diffraction-inclusive path model Emax "
                              f"{wave['primary']['Emax_M1']:.4f} <= 0.02 CONFIRMED; no-diffraction model {wave['primary']['Emax_M0']:.4f} refutation replicated; "
                              f"archived FDTD within {wave['crosscheck_fdtd']['max_abs_diff_vs_fdtd']['ii']:.4f}; two-MZI cascade {wave['cascade']['Emax_M1']:.4f}. "
                              f"HA-K1: F_geom decision dimension 12 of 26 (F_lin), four inert translations; H-A1 {cap['H_A1']['decision']}.")
            p["remaining"] += (f" [{stamp}] Captured scene outside the diffraction-free regime at lambda=0.1 BU (0/17060 paths; ~790x shorter lambda needed): "
                               "rescaled geometry or diffraction-inclusive network model before any physical claim.")
        if p["id"] == 10:
            p["achieved"] += f" [{stamp}] External Linux CI reran WAVE-C1 (powers within 8.9e-16) and compiled Lean T1-T5; independent agent red-team archived."
    doc["updated_utc"] = datetime.now(timezone.utc).isoformat()
    return doc


def main() -> int:
    ev = evidence()
    m = manifests(ev)
    put(OUT / "closure-manifest-claude-20261013.json", m["closure"])
    put(OUT / "frontier-manifest-claude-20261013.json", m["frontier"])
    closure_report = verify_closure(ROOT, m["closure"])
    frontier_report = verify_frontier(ROOT, m["frontier"])
    put(OUT / "closure-integrity-claude-20261013.json", {"closure": closure_report, "frontier": frontier_report})
    newline = chr(10)
    CANONICAL.write_text(json.dumps(canonical(ev), indent=2) + newline, encoding="utf-8", newline=newline)  # original format
    print(json.dumps({"closure_integrity": closure_report["integrity_pass"], "closure_complete": closure_report["all_selected_fronts_pass"],
                      "frontier_integrity": frontier_report["integrity_pass"], "frontier_complete": frontier_report["all_frontier_fronts_pass"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
