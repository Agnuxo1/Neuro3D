"""Plot retained numeric evidence with explicit model and timing boundaries."""
import hashlib
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"Docs/closure-20261012/figures"


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    inputs=["Benchmarks/validacion-onda/resultados/RESULTADOS_VALIDACION.json",
            "Docs/validation/native-graphics-scaling-2026-10-09/attempt02/worker/result.json",
            "Docs/closure-20261012/resident-archive-diagnostic/result.json"]
    data=[json.loads((ROOT/p).read_text(encoding="utf-8")) for p in inputs]
    plt.rcParams.update({"font.size":10,"axes.spines.top":False,"axes.spines.right":False})
    fig,ax=plt.subplots(figsize=(7.1,3.6),layout="constrained")
    grid=np.arange(2)
    ax.bar(grid-.16,[data[0]["mallas"][str(n)]["E_max"] for n in (16,24)],width=.32,label="Primary: no path diffraction")
    ax.bar(grid+.16,[data[0]["mallas"][str(n)]["E_max_diagnostico_con_difraccion"] for n in (16,24)],width=.32,label="Exploratory Gaussian correction")
    ax.axhline(.02,color="crimson",linestyle="--",label="Original fixed budget 0.02")
    ax.set(xticks=grid,xticklabels=["lambda/16 (12 phases)","lambda/24 (18 phases)"],ylabel="Maximum absolute modal-power error",
           title="Historical 2D MZI: primary failure retained")
    ax.legend(fontsize=8);fig.savefig(OUT/"wave-negative.png",dpi=180);plt.close(fig)
    fig,ax=plt.subplots(figsize=(7.1,3.6),layout="constrained")
    for arm,label in (("CPU_GEOMETRY_DAG","CPU geometry DAG"),("GPU_DEFERRED_GRAPHICS","GPU with CPU coherent merging")):
        xs=[r["batch_size"] for r in data[1]["results"]];ys=[r["seconds"][arm] for r in data[1]["results"]]
        ax.scatter(xs,ys,label=label,s=35)
    ax.set(xscale="log",yscale="log",xlabel="Inputs in a batch",ylabel="Paired inference seconds",
           title="Historical same-output local pairs: GPU slower in all six")
    ax.set_xticks([1,150,4096],["1","150","4096"]);ax.legend(fontsize=8)
    fig.savefig(OUT/"paired-cost.png",dpi=180);plt.close(fig)
    fig,ax=plt.subplots(figsize=(7.1,3.6),layout="constrained")
    vals=[data[2]["gpu_coefficients_cpu_replay_vs_archived_cpu_max_field"],data[2]["gpu_coefficients_cpu_replay_vs_archived_gpu_max_field"]]
    ax.bar([0,1],vals,color=["#267b69","#b24343"]);ax.axhline(1e-11,color="black",linestyle="--",label="Unchanged 1e-11 field budget")
    ax.set(yscale="log",xticks=[0,1],xticklabels=["Actual GPU coefficients / CPU replay","CPU replay / archived GPU outputs"],
           ylabel="Maximum absolute complex-field difference",title="133-state CPU ablation of archived GPU readbacks")
    ax.tick_params(axis="x",labelsize=8);ax.legend(fontsize=8)
    fig.savefig(OUT/"resident-ablation.png",dpi=180);plt.close(fig)
    comparison=ROOT/"Docs/closure-20261012/eeg-comparison.json"
    if comparison.exists():
        inputs.append(comparison.relative_to(ROOT).as_posix());eeg=json.loads(comparison.read_text(encoding="utf-8"))
        optical=np.array(eeg["optical"]["N1"]);fbcsp=np.array(eeg["comparators"]["H1_fbcsp"]["N1"])
        fig,ax=plt.subplots(figsize=(7.1,3.6),layout="constrained")
        ax.scatter(fbcsp,optical);ax.plot([.4,1],[.4,1],color="gray",linestyle="--")
        ax.set(xlabel="FBCSP nested N1 subject accuracy",ylabel="Optical-grid nested N1 subject accuracy",
               title="17 known EEG subjects; free digital matrix included in optical grid",xlim=(.4,1),ylim=(.4,1))
        fig.savefig(OUT/"eeg-paired.png",dpi=180);plt.close(fig)
    report={"source_pins":{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in inputs},
            "figures":{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.glob("*.png")},
            "scope":"Plots of retained numerical records; not new native/physical experiments"}
    (OUT/"manifest.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps({"figures":len(report["figures"])}))


if __name__=="__main__":main()
