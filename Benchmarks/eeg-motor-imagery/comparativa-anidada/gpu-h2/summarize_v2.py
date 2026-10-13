"""Aggregate EXP-006-EEGNET-GPU-H2-20261013-001 outputs for the repository: per-subject hashes,
timings and estimator accuracies (no EEG, no labels, no logits), plus a check that the H1
contrast recomputed by the frozen analyzer equals the published eeg-comparison.json.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, required=True, help="directory of full-run S###.npz + timing.jsonl")
    parser.add_argument("--analysis", type=Path, required=True)
    parser.add_argument("--published", type=Path, required=True, help="Docs/closure-20261012/eeg-comparison.json")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    analysis = json.loads(args.analysis.read_text(encoding="utf-8"))
    published = json.loads(args.published.read_text(encoding="utf-8"))
    timing = {}
    for line in (args.raw / "timing.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            timing[row["subject"]] = row
    eeg = analysis["comparators"]["H2_eegnet"]
    subjects = []
    for i, sid in enumerate(eeg["subjects"]):
        path = args.raw / (sid + ".npz")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != timing[sid]["npz_sha256"]:
            raise ValueError(f"Hash mismatch for {sid}")
        subjects.append({"subject": sid, "npz_sha256": digest, "seconds": timing[sid]["seconds"],
                         "n_trainings": timing[sid]["n_trainings"], "steps": timing[sid]["steps"],
                         **{k: eeg[k][i] for k in ("N1", "N1b", "N2", "N3", "MEANgrid")}})
    h1_new, h1_old = analysis["contrasts"]["H1_fbcsp"], published["contrasts"]["H1_fbcsp"]
    h1_check = {k: (h1_new[k] == h1_old[k]) for k in ("difference", "ci", "p_wilcoxon", "wins", "ties", "losses", "decision")}
    environments = {json.dumps(t["environment"]["determinism"], sort_keys=True) for t in timing.values()}
    report = {"experiment": "EXP-006-EEGNET-GPU-H2-20261013-001",
              "analysis_sha256": hashlib.sha256(args.analysis.read_bytes()).hexdigest(),
              "n_subjects": len(subjects), "total_exec_seconds": sum(s["seconds"] for s in subjects),
              "eegnet_mean": {k: sum(s[k] for s in subjects if s[k] is not None) / len(subjects)
                              for k in ("N1", "N1b", "N2", "N3", "MEANgrid")},
              "optical_mean_N1": sum(analysis["optical"]["N1"]) / len(analysis["optical"]["N1"]),
              "h1_matches_published": h1_check,
              "h1_p_holm_published_vs_now": [h1_old["p_holm"], h1_new["p_holm"]],
              "environment": next(iter(timing.values()))["environment"],
              "determinism_settings_identical_across_subjects": len(environments) == 1,
              "subjects": subjects}
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: report[k] for k in ("n_subjects", "total_exec_seconds", "eegnet_mean", "optical_mean_N1", "h1_matches_published")}))


if __name__ == "__main__":
    main()
