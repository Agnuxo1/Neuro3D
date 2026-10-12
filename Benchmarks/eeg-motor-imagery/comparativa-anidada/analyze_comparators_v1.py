"""Analyze stored nested-grid logits without retraining or selecting on N1 test.

The published primary interval/decision rule is retained verbatim. Bonferroni
intervals and Holm p-values are separate sensitivity analyses, not substitutes.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
from scipy.stats import wilcoxon


def select(values, default, maximize=False, secondary=None):
    if values is None:
        return default
    if secondary is None:
        return int(np.lexsort((np.arange(len(values))!=default, -values if maximize else values))[0])
    return int(np.lexsort((np.arange(len(values))!=default, secondary, -values))[0])


def estimates(files, optical=False, passive_only=False):
    subjects, rows, selected = [], [], []
    for path in sorted(files):
        with np.load(path,allow_pickle=False) as raw:
            meta=json.loads(str(raw["meta"]))
            if meta.get("pilot"):
                raise ValueError("Pilot folds are not complete subjects")
            if optical:
                configs=[(k,f,f"{w:g}",e) for k,f,w in meta["triples"] for e in meta["epochs"]
                         if not passive_only or k!="free"]
                d=meta["default"]
                default=configs.index((d[0],d[1],f"{d[2]:g}",d[3]))
                runs=meta["runs"]
            else:
                configs=meta["configs"]
                default=meta["default_index"]
                runs=sorted(int(k.split("|")[1]) for k in raw.files if k.startswith("y|"))
            correct=np.zeros(len(configs)); n=0; n1=n1b=0
            for run in runs:
                y=raw[f"y|{run}"]
                if optical:
                    logits=[raw[f"o|{run}|{k}|{f}|{w}|{e}"] for k,f,w,e in configs]
                    inner=sorted(int(key.split("|")[2]) for key in raw.files if key.startswith(f"yv|{run}|"))
                    losses=accs=None
                    if inner:
                        loss=np.zeros(len(configs)); acc=np.zeros(len(configs)); total=0
                        for v in inner:
                            labels=raw[f"yv|{run}|{v}"]; total+=len(labels)
                            for c,(k,f,w,e) in enumerate(configs):
                                z=raw[f"i|{run}|{v}|{k}|{f}|{w}|{e}"]
                                loss[c]+=(np.logaddexp(0,z)-labels*z).sum()
                                acc[c]+=((z>0)==labels).sum()
                        losses,accs=loss/total,acc/total
                else:
                    logits=[raw[f"o|{run}|{c}"] for c in range(len(configs))]
                    losses=raw[f"inner_bce|{run}"]
                    accs=raw[f"inner_acc|{run}"]
                    if len(losses)==0:
                        losses=accs=None
                pick=select(losses,default)
                if not optical and pick!=int(raw[f"selected|{run}"][0]):
                    raise ValueError("Stored N1 selection differs from internal-only selection")
                pick_b=select(accs,default,maximize=True,secondary=losses) if accs is not None else default
                counts=np.array([((z>0)==y).sum() for z in logits])
                correct+=counts; n+=len(y); n1+=counts[pick]; n1b+=counts[pick_b]
            subjects.append(path.stem); rows.append(correct/n); selected.append((n1/n,n1b/n,default))
    if not subjects:
        raise ValueError("No complete subject results")
    loro=np.array(rows)
    n2=[]
    for s in range(len(subjects)):
        others=np.delete(loro,s,axis=0)
        n2.append(float(loro[s,np.argmax(others.mean(axis=0))]) if len(others) else None)
    return {"subjects":subjects,"n_configs":len(configs),
            "N1": [r[0] for r in selected],"N1b":[r[1] for r in selected],"N2":n2,
            "N3":[float(loro[s,r[2]]) for s,r in enumerate(selected)],"MEANgrid":loro.mean(axis=1).tolist()}


def contrast(differences, confidence=0.95):
    d=np.asarray(differences,float)
    if len(d)<2 or not np.isfinite(d).all():
        raise ValueError("At least two independent finite subject differences required")
    rng=np.random.default_rng(0)
    means=d[rng.integers(0,len(d),(10000,len(d)))].mean(axis=1)
    ci=np.quantile(means,[(1-confidence)/2,(1+confidence)/2]).tolist()
    p=1.0 if np.all(d==0) else float(wilcoxon(d,alternative="two-sided",zero_method="wilcox",method="auto").pvalue)
    label="superior" if ci[0]>0 else "equivalent" if ci[0]>=-0.02 and ci[1]<=0.02 else "inconclusive"
    return {"difference":float(d.mean()),"ci":ci,"confidence":confidence,"decision":label,
            "description":"inferior" if ci[1]<0 else label,"p_wilcoxon":p,
            "wins":int((d>0).sum()),"ties":int((d==0).sum()),"losses":int((d<0).sum())}


def holm(pvalues):
    p=np.asarray(pvalues,float); order=np.argsort(p); result=np.zeros(len(p)); previous=0
    for k,i in enumerate(order):
        previous=max(previous,min(1.,(len(p)-k)*p[i])); result[i]=previous
    return result.tolist()


def compare(optical, comparators):
    output={"scope":"Known-subject LORO comparator grids; no blind external/general optical superiority",
            "primary_estimator":"N1","contrasts":{},"exploratory":{}}
    names,pvalues=[],[]
    for name,method in comparators.items():
        shared=sorted(set(optical["subjects"])&set(method["subjects"]))
        if len(shared)<2:
            output["contrasts"][name]={"state":"BLOCKED","reason":"Fewer than two complete subjects"};continue
        oi=[optical["subjects"].index(s) for s in shared]; mi=[method["subjects"].index(s) for s in shared]
        d=np.array(optical["N1"])[oi]-np.array(method["N1"])[mi]
        result=contrast(d);result.update(subjects=shared,partial=len(shared)!=17)
        result["simultaneous_interval_sensitivity"]=contrast(d,confidence=0.975)
        output["contrasts"][name]=result;names.append(name);pvalues.append(result["p_wilcoxon"])
        output["exploratory"][name]={}
        for estimator in ("N1b","N2","N3","MEANgrid"):
            a=[optical[estimator][i] for i in oi]; b=[method[estimator][i] for i in mi]
            if None not in a and None not in b:
                output["exploratory"][name][estimator]=contrast(np.array(a)-np.array(b))
    # The preregistered family contains H1 and H2 even if H2 is unavailable.
    adjusted=holm(pvalues+[1.]*(2-len(pvalues)))
    for name,p in zip(names,adjusted):
        result=output["contrasts"][name];result["p_holm"]=p
        result["wilcoxon_warning"]=result["decision"]=="superior" and p>=0.05
    return output


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--optical-raw",type=Path,required=True)
    parser.add_argument("--fbcsp",type=Path,required=True)
    parser.add_argument("--eegnet",type=Path)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    optical=estimates(args.optical_raw.glob("S*.npz"),optical=True)
    methods={"H1_fbcsp":estimates(args.fbcsp.glob("S*.npz"))}
    if args.eegnet:
        methods["H2_eegnet"]=estimates(args.eegnet.glob("S*.npz"))
    report=compare(optical,methods)
    report["optical"]=optical;report["comparators"]=methods
    report["passive_subfamily_exploratory"]=estimates(args.optical_raw.glob("S*.npz"),optical=True,passive_only=True)
    with args.out.open("x",encoding="utf-8",newline="\n") as stream:
        json.dump(report,stream,indent=2,allow_nan=False);stream.write("\n")
