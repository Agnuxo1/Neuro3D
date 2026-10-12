"""Complete section-18 records after results are actually published."""
from datetime import datetime,timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"agent_support"))
from closure_integrity import validate_experiment_record


def main():
    out=ROOT/"Docs/closure-20261012"
    published=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
    remote=subprocess.check_output(["git","ls-remote","origin","refs/heads/codex/closure-guide-v2-20261012"],cwd=ROOT,text=True).split()[0]
    if published!=remote:raise ValueError("Current results must already be published")
    versions={}
    for name in ("numpy","scipy","scikit-learn","torch"):
        versions[name]=importlib.metadata.version(name)
    def source(path):return {"path":path,"sha256":hashlib.sha256((ROOT/path).read_bytes()).hexdigest()}
    common={"inputs":{},"environment":{"python":"CPython 3.13.7 Windows","packages":versions},"seeds":[],
            "resource_budget":{"cpu_processes":1,"blas_threads":1},"deadline":"2026-10-12",
            "exit_codes":[0],"results":{},"independent_oracle":"No independently produced human replication",
            "decision_rule":"Frozen profile and unchanged original numerical/statistical budgets",
            "decision":"PARTIAL","deviations":[],"limitations":[],"published_commit":published,"status":"PARTIAL"}
    eeg={**common,"id":"EXP-006-EEG-COMPARATORS-20261012-001",
         "hypothesis":"Published H1/H2: known optical-grid primary N1 differs from nested FBCSP/EEGNet",
         "alternative":"No useful paired difference in the original known-subject comparator grids",
         "protocol_commit":"7e239aa328311c28dca46d0e89f6f86892598b6e",
         "sources":[source(p) for p in ["Benchmarks/eeg-motor-imagery/comparativa-anidada/PREREGISTRO-EEG.md",
                     "Benchmarks/eeg-motor-imagery/comparativa-anidada/run_nested_comparators_v1.py",
                     "Benchmarks/eeg-motor-imagery/comparativa-anidada/analyze_comparators_v1.py",
                     "Docs/closure-20261012/eeg-execution.json","Docs/closure-20261012/eeg-comparison.json"]],
         "inputs":{"subjects":json.loads((out/"eeg-execution.json").read_text())["subjects"],
                   "hidden_Xte_access":False,"saved_optical_fold_indices_verified":True},
         "seeds":["external k","internal 100+10*k+j","bootstrap fresh default_rng(0) per comparison"],
         "commands":["run_nested_comparators_v1.py --method fbcsp --subjects S001 S002 S003 S004 S005 S006 S007 S009 S010 S011 S012 S014 S016 S017 S018 S019 S020 --data <legitimate-data> --optical-raw <legitimate-saved-folds> --out <new-owner-workspace>",
                     "analyze_comparators_v1.py --optical-raw <legitimate-saved-folds> --fbcsp <new-owner-results> --out Docs/closure-20261012/eeg-comparison.json"],
         "results":json.loads((out/"eeg-comparison.json").read_text())["contrasts"],
         "decision":"H1 meets original superior-grid rule; H2 unavailable",
         "deviations":["EEGNet pilot interrupted by actual host RAM floor; no H2 claim", "If absent H2 is imputed p=1, Holm retains the original two-comparison family", "Simultaneous interval is a separately labelled sensitivity"],
         "limitations":["Known subjects and biased optical-grid design","free is digital, not a captured passive geometry","No new blind or independent data","Raw derivatives require legitimate access and redistribution permission"]}
    diag={**common,"id":"EXP-006-RESIDENT-ARCHIVE-DIAG-20261012-001",
          "hypothesis":"Actual GPU local coefficients propagated on CPU reproduce the archived reference",
          "alternative":"The archived local coefficients already violate the fixed field budget",
          "protocol_commit":"6bc5dd7ae9562fd1b1bcf9f76a9d1f7925f07c6e",
          "sources":[source(p) for p in ["Tools/diagnose_resident_archive_v1.py","Docs/closure-20261012/archive-diagnostic-profile.json",
                      "Docs/closure-20261012/resident-archive-diagnostic/result.json"]],
          "inputs":{"historical_native_controls":4,"states":133,"new_native_execution":False},
          "commands":["python Tools/diagnose_resident_archive_v1.py --out Docs/closure-20261012/resident-archive-diagnostic"],
          "results":json.loads((out/"resident-archive-diagnostic/result.json").read_text()),
          "decision":"Coefficient CPU ablation passes 1e-11; native resident rejection retained, cause UNKNOWN",
          "limitations":["CPU replay of historical GPU data","No native intermediate-state trace, GPU acceptance, repair or speed claim"]}
    interrupted=[]
    for name,identifier in [("eegnet-pilot-supervision.json","EXP-006-EEGNET-PILOT-20261012-001"),
                            ("full-unittest-supervision.json","EXP-006-CPU-DISCOVERY-20261012-001")]:
        receipt=json.loads((out/name).read_text())
        interrupted.append({**common,"id":identifier,"hypothesis":"The complete selected CPU job finishes within its frozen resource envelope",
           "alternative":"Unavailable host resources prevent a complete result","protocol_commit":"6e53fefcff7943fdf98d1f87133c8d9224bd3ad3",
           "sources":[source("Docs/closure-20261012/"+name)],"commands":[receipt["command"]],"exit_codes":[receipt["exit_code"]],
           "resource_budget":receipt["limits"],"results":receipt,"decision":"BLOCKED by actual host RAM floor; timing/scientific metric NULL",
           "status":"BLOCKED","limitations":["No numerical result; original direct-process RSS scope noted; no matching unittest process remained after stop"]})
    records=[eeg,diag,*interrupted]
    problems={r["id"]:validate_experiment_record(r) for r in records}
    if any(problems.values()):raise ValueError(problems)
    payload={"schema":"neuro3d.closure.experiment_registry.v1","date":datetime.now(timezone.utc).isoformat(),
             "records":records,"validation_problems":problems,
             "scope":"Complete metadata does not itself establish scientific truth or external replication"}
    (out/"experiment-registry.json").write_text(json.dumps(payload,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps({"records":len(records),"validation_errors":0,"published_result_commit":published}))


if __name__=="__main__":main()
