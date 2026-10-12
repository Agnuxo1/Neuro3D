"""Generate the sourced claim matrix and prospectively pinned campaign plan."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"Docs/closure-20261012"
BASE="69db25ce7b04a98e24609bcd539c5041f269658d"


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def put(path,value):path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+"\n",encoding="utf-8",newline="\n")


def main():
    OUT.mkdir(exist_ok=True)
    claims=[
      ("Captured represented scalar scene","Historical Blender capture","104 objects, 6656 triangles, 5 sources, 8 modes; 133 states, 186 edges, 17060 paths","Docs/SCIENTIFIC_ACCEPTANCE_REPORT_2026-10-09.md","L2 internal frozen simulation","One admitted scalar family; not Maxwell paths"),
      ("Hybrid geometry learning","Historical Iris split","16 parameters, 60 updates, 61 captures; train 110/120, test 27/30","Docs/validation/native-deferred-training-2026-10-09/attempt01/worker/result.json","L2 internal frozen simulation","Topology, coherent merging, loss and Adam on CPU; known split"),
      ("Final decision enclosure","150 historical Iris rows","150 separated decisions; 137 correct labels and 13 wrong","Docs/validation/native-deferred-training-certificate-2026-10-09/attempt01/worker/certificate.json","L2 numerical certificate","Numerical separation is not accuracy or physical fidelity"),
      ("Rejected resident graph","Four archived coherent controls","6.376147888196662e-8 exceeds fixed 1e-11 budget","Docs/validation/native-resident-graph-2026-10-09/attempt03/worker/coherence_control_observations_before_gate.json","L2 observed negative","Five input echoes pass; first divergence cause unknown before new diagnostic"),
      ("GPU total inference cost","Same-output 1/150/4096 pairs","GPU slower in all six pairs","Docs/NATIVE_GRAPHICS_SCALING_PROTOCOL_2026-10-09.md","L2 paired local measurement","No global speedup, isolated energy or AMD execution"),
      ("Auxiliary benchmark","Known Wine partitions","Optical 0.7910; tuned SVM 0.8676","Benchmarks/benchmark-v1/resultados/RESULTADOS_BENCHMARK_V1.md","L1 or retained preregistered scope in original report","Not native captured Blender generalization"),
      ("Auxiliary Clements mesh","Digits, 64 modes","Mesh 0.9492; tuned logistic 0.9703","Benchmarks/escala-modos/sensibilidad/resultados_sensibilidad.md","L1 tuning sensitivity","Auxiliary mesh; no captured geometry, physical fabrication or superiority"),
      ("P1-7 wave negative","2D TM MZI, w=8 lambda","Emax 0.02692643372060144 at lambda/16; 0.02751899213404152 at lambda/24; limit 0.02 missed","Benchmarks/validacion-onda/resultados/RESULTADOS_VALIDACION.json","L2 with declared deviations","12/18 discrete phases; recalibrated devices; no full-network validation"),
      ("P1-7 diffraction diagnostic","Same historical MZI","Exploratory Emax 0.005134910435326212 / 0.004615348997879409","Benchmarks/validacion-onda/resultados/RESULTADOS_VALIDACION.json","L1 exploratory","Not new confirmation; no retrospective threshold change"),
      ("Fixed-index wave control","Same nominal film index","Stable model-solver Emax; coarse R about 0.583 versus fine 0.497","Benchmarks/validacion-onda/control_fijo/resultados/RESULTADOS_CONTROL.md","L2 limited control","Model-solver agreement and calibrated 50/50 device fidelity are distinct"),
      ("Auxiliary F4","Interference mesh comparison","Read according to the original preregistered report, including negatives","Benchmarks/ablation-F4/INFORME-EJECUCION-F4.md","Historical auxiliary study","No transfer to captured passive network; zero differences do not prove equivalence"),
      ("EEG optical grid","17 known subjects","Primary N1 0.7009; secondary N2 0.7274","Benchmarks/eeg-motor-imagery/evidencia-validacion-anidada/results_full.json","Retained nested evaluation with known-data bias","free is an unconstrained digital matrix; EEG comparators not yet nested"),
      ("CPU addon recovery","Installed 0.1.3","One owner interruption at checkpoint12, exact resume in Windows and Linux","Docs/EXTERNAL_INSTALLED_BLENDER_RECOVERY_PROTOCOL_2026-10-09.md","L3 automatic external execution","No repeated power-loss, human usability or external specialist interpretation"),
      ("Novelty search","Bounded primary corpus","No complete combination found within searched scope","Docs/research/novelty-p1-6/VEREDICTO-P1-6.md","Bounded literature search","No universal absence, exceptional importance or independent adoption"),
    ]
    # Locate the existing auxiliary F4 report rather than inventing a path.
    for i,row in enumerate(claims):
        if row[0]=="Auxiliary F4" and not (ROOT/row[3]).is_file():
            matches=list((ROOT/"Benchmarks").rglob("INFORME*F4*.md"))
            if len(matches)!=1:raise ValueError("Unambiguous F4 report required")
            claims[i]=(*row[:3],matches[0].relative_to(ROOT).as_posix(),*row[4:])
    records=[]
    for model,data,result,source,evidence,limit in claims:
        if not (ROOT/source).is_file():raise FileNotFoundError(source)
        records.append(dict(model=model,data=data,result=result,source=source,sha256=sha(ROOT/source),evidence=evidence,
                            allowed_interpretation="Only the stated represented model, dataset and original protocol",limitation=limit))
    put(OUT/"claims.json",{"base_commit":BASE,"claims":records,"scope":"Sourced historical evidence; no new experiment claims"})
    lines=["# Claim matrix — 12 October 2026","","Historical numbers retain their original scope and deviations. Source hashes identify evidence, not an independently established physical truth.","", "| Model/family | Data | Result | Source and SHA256 | Evidence | Allowed interpretation | Limitation |","|---|---|---|---|---|---|---|"]
    for r in records:
        lines.append("| "+" | ".join([r["model"],r["data"],r["result"],f'[{r["source"]}](../../{r["source"]}) `{r["sha256"]}`',r["evidence"],r["allowed_interpretation"],r["limitation"]])+" |")
    (OUT/"CLAIMS.md").write_text("\n".join(lines)+"\n",encoding="utf-8",newline="\n")
    sources=list((ROOT/"agent_support").glob("*.py"))+[ROOT/p for p in [
      "Tools/run_closure_regressions_v1.py","Tools/restore_pinned_checkout_v1.py","Tools/prepare_closure_campaign_v1.py",
      "Benchmarks/eeg-motor-imagery/comparativa-anidada/run_nested_comparators_v1.py",
      "Benchmarks/eeg-motor-imagery/comparativa-anidada/analyze_comparators_v1.py",
      "Benchmarks/eeg-motor-imagery/codigo/work/bench.py","Benchmarks/eeg-motor-imagery/codigo/work/nested/nested_bench.py"]]
    profile={"schema":"neuro3d.closure.campaign.v1","id":"EXP-006-CLOSURE-20261012-001","base_commit":BASE,
      "created_utc":datetime.now(timezone.utc).isoformat(),"sources":{p.relative_to(ROOT).as_posix():sha(p) for p in sources},
      "registration":"Publish this profile and exact code on GitHub before new experimental data; existing human GitHub sequence authorization retained, no external registry claim",
      "known_results":"P1-7 diffraction diagnostic, archived resident rejection, EEG N1/N2, Wine/Digits comparisons all already known",
      "cpu_budget":{"processes":1,"blas_threads":1,"diagnostic_module_deadline_seconds":45,"eeg_torch_threads":2,"eeg_max_processes":2},
      "trials":[
        {"id":"EXP-006-EEG-COMPARATORS-20261012-001","hypothesis":"Original H1/H2 in the 2026-10-10 preregistration, primary N1",
         "protocol":"Benchmarks/eeg-motor-imagery/comparativa-anidada/PREREGISTRO-EEG.md","method":"Exact published grids, seeds and folds; pilot one complete external fold; no hidden Xte access",
         "stop":"Measure one fold per method; complete FBCSP 17 subjects; EEGNet follows original 3h rule, no 17-subject claim from partial data",
         "metrics":"Raw logits; subject N1; original bootstrap/Wilcoxon/Holm rule; simultaneous intervals separate sensitivity",
         "limits":["known subjects and biased optical grid","not native captured optical geometry","restricted data not redistributed"]},
        {"id":"EXP-006-RESIDENT-ARCHIVE-DIAG-20261012-001","hypothesis":"Archived unit coefficients propagated in binary64 explain the rejected GPU outputs, or isolate traversal/readback",
         "method":"CPU replay of all 133 archived states with actual GPU local coefficient rows; compare to archived CPU and GPU four-control fields",
         "budget":"900 seconds, one CPU thread, 512 MiB working data; native GPU trial separate and only after resource admission",
         "rule":"Keep fixed field threshold 1e-11; do not assign a GPU precision cause from a CPU-only diagnostic",
         "limits":["no new native execution","cannot locate native first differing intermediate state without native trace"]}
      ]}
    put(OUT/"campaign-profile.json",profile)
    print(json.dumps({"claims":len(records),"sources_pinned":len(sources),"profile_sha256":sha(OUT/"campaign-profile.json")}))


if __name__=="__main__":main()
