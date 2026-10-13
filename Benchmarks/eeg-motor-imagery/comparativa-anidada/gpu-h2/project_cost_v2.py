"""Project the full nested-EEGNet GPU cost from one complete measured fold and apply the
preregistered 3-hour rule (PREREGISTRO-EEG.md section 8) mechanically.

Cost model (declared before execution): wall seconds per optimizer step measured on the
pilot fold (S001, first external fold, all 36 configurations) times the exact number of
optimizer steps of every training of every subject (90 epochs x ceil(n_train / batch)),
plus a fixed 60 s start-up overhead per subject ticket.  Only the `run` field of each
subject file is read (fold structure); no EEG signal, no labels, never Xte.

Rule: projected total <= 3 h -> all 17 subjects.  Otherwise the preregistered partial
strategy: complete subjects in ascending identifier order while the cumulative projected
cost stays <= 3 h; H2 is then evaluated only on those subjects, labelled "partial".
"""
from __future__ import annotations
import argparse
import importlib.util
import json
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
SUBJECTS = ["S001", "S002", "S003", "S004", "S005", "S006", "S007", "S009", "S010", "S011",
            "S012", "S014", "S016", "S017", "S018", "S019", "S020"]
BUDGET_S = 3 * 3600.0
TICKET_OVERHEAD_S = 60.0


def load_v1():
    spec = importlib.util.spec_from_file_location("v1", HERE.parent / "run_nested_comparators_v1.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def steps(n, batch):
    return 90 * -(-n // batch)


def subject_steps(nested, runs, trajectories, first_fold_only=False):
    total = 0
    for k, (train, test, run) in enumerate(nested.outer_folds(runs)):
        sizes = [len(it) for it, iv, v in nested.inner_folds(runs, train)] + [len(train)]
        total += sum(steps(n, bs) for n in sizes for (lr, bs, wd) in trajectories)
        if first_fold_only:
            break
    return total


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--pilot-timing", type=Path, required=True, help="timing.jsonl of the pilot fold")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    v1 = load_v1()
    trajectories = sorted({cfg[:3] for cfg in v1.EEG_CONFIGS})
    if len(trajectories) != 12 or len(v1.EEG_CONFIGS) != 36:
        raise ValueError("Preregistered 12 trajectories / 36 configurations required")
    pilot = [json.loads(line) for line in args.pilot_timing.read_text(encoding="utf-8").splitlines() if line.strip()]
    pilot = [p for p in pilot if p["subject"] == "S001" and p["pilot"]]
    if len(pilot) != 1:
        raise ValueError("Exactly one complete S001 pilot fold record is required")
    pilot = pilot[0]
    with v1.existing_modules() as (nested, _bench):
        per_subject = {}
        for sid in SUBJECTS:
            with np.load(args.data / (sid + ".npz"), allow_pickle=False) as data:
                runs = data["run"]  # fold structure only
            per_subject[sid] = subject_steps(nested, runs, trajectories)
            if sid == "S001":
                pilot_steps_check = subject_steps(nested, runs, trajectories, first_fold_only=True)
    if pilot_steps_check != pilot["steps"]:
        raise ValueError(f"Pilot step count mismatch {pilot_steps_check} != {pilot['steps']}")
    rate = pilot["seconds"] / pilot["steps"]
    cost = {sid: rate * n + TICKET_OVERHEAD_S for sid, n in per_subject.items()}
    total = sum(cost.values())
    plan, cumulative = [], 0.0
    for sid in SUBJECTS:
        if cumulative + cost[sid] > BUDGET_S:
            break
        plan.append(sid)
        cumulative += cost[sid]
    full = total <= BUDGET_S
    report = {"experiment": "EXP-006-EEGNET-GPU-H2-20261013-001",
              "pilot": {k: pilot[k] for k in ("subject", "seconds", "steps", "n_trainings", "training_seconds", "npz_sha256")},
              "seconds_per_step": rate, "ticket_overhead_s": TICKET_OVERHEAD_S,
              "steps_per_subject": per_subject, "projected_seconds_per_subject": cost,
              "projected_total_hours": total / 3600, "budget_hours": BUDGET_S / 3600,
              "execute_full": full, "plan_subjects": SUBJECTS if full else plan,
              "plan_label": "complete" if full else "partial",
              "projected_plan_hours": (total if full else cumulative) / 3600}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    print(json.dumps({k: report[k] for k in ("projected_total_hours", "execute_full", "plan_label", "plan_subjects")}))


if __name__ == "__main__":
    main()
