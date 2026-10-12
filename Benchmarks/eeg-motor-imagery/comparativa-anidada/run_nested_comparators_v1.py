"""Complete CPU runner for the published 36-configuration EEG comparator grid.

Loads Xtr/ytr/run only. The existing outer_folds, inner_folds, CSP and EEGNet
implementations are reused. Each invocation is a fresh process (two Torch
threads). A pilot is a complete external fold, not a changed configuration.
"""
from __future__ import annotations
import argparse
from contextlib import contextmanager
import hashlib
import importlib
import json
import os
from pathlib import Path
import sys
import time
import numpy as np
from scipy.signal import butter, sosfiltfilt
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

WORK = Path(__file__).resolve().parents[1]/"codigo/work"
BANDS = {"A": [(8,12),(12,16),(16,20),(20,24),(24,30)],
         "B": [(i,i+4) for i in range(4,40,4)],
         "C": [(8,13),(13,20),(20,30)], "D": [(8,30)]}
CS = [10.0**i for i in range(-4,5)]
EEG_CONFIGS = [(lr,bs,wd,e) for lr in (1e-3,3e-3,1e-2) for bs in (16,32)
               for wd in (1e-3,1e-2) for e in (30,60,90)]


@contextmanager
def existing_modules():
    paths, environment = list(sys.path), dict(os.environ)
    try:
        sys.path[:0] = [str(WORK), str(WORK/"nested")]
        os.environ["BENCH_DEV"] = "cpu"
        yield importlib.import_module("nested_bench"), importlib.import_module("bench")
    finally:
        sys.path[:] = paths
        os.environ.clear()
        os.environ.update(environment)


def choose(losses, default):
    """Exactly lowest pooled internal BCE; exact tie prefers the default."""
    if losses is None:
        return default
    values = np.asarray(losses, float)
    if values.ndim != 1 or not np.isfinite(values).all():
        raise ValueError("Finite internal losses required")
    return int(np.lexsort((np.arange(len(values)) != default, values))[0])


def fit_fbcsp(B, filtered, labels, train, evaluations, c):
    train_features, evaluation_features = [], [[] for _ in evaluations]
    for band in filtered:
        filters = B.csp_filters(band[train], labels[train], k=3)
        def features(indices):
            projected = np.einsum("cf,nct->nft", filters, band[indices])
            return np.log(np.maximum(np.var(projected, axis=-1), 1e-12))
        train_features.append(features(train))
        for result, indices in zip(evaluation_features, evaluations):
            result.append(features(indices))
    scaler = StandardScaler().fit(np.concatenate(train_features, axis=1))
    model = LogisticRegression(C=c, solver="lbfgs", max_iter=1000).fit(
        scaler.transform(np.concatenate(train_features, axis=1)), labels[train])
    return [model.decision_function(scaler.transform(np.concatenate(f,axis=1))) for f in evaluation_features]


def fit_eegnet(B, X, y, train, evaluations, lr, batch, wd, seed):
    import torch
    torch.manual_seed(seed)
    # Same training-only channel standard deviation as the historical bench.
    scale = X[train].std(axis=(0,2),keepdims=True)+1e-6
    xt = torch.as_tensor(X[train]/scale, dtype=torch.float32)
    yt = torch.as_tensor(y[train], dtype=torch.float32)
    xe = [torch.as_tensor(X[index]/scale, dtype=torch.float32) for index in evaluations]
    model = B.EEGNet()
    optimizer = torch.optim.AdamW(model.parameters(),lr=lr,weight_decay=wd)
    output = {}
    for epoch in range(1,91):
        model.train()
        order = torch.randperm(len(train))
        for i in range(0,len(train),batch):
            indices = order[i:i+batch]
            optimizer.zero_grad()
            torch.nn.functional.binary_cross_entropy_with_logits(model(xt[indices]),yt[indices]).backward()
            optimizer.step()
        if epoch in (30,60,90):
            model.eval()
            with torch.no_grad():
                output[epoch] = [model(value).numpy().copy() for value in xe]
    return output


def run_subject(path, method, reference, pilot=False):
    start = time.monotonic()
    with np.load(path,allow_pickle=False) as data:
        X,y,runs = data["Xtr"].astype(np.float32),data["ytr"],data["run"]
    if X.ndim!=3 or X.shape[1:]!=(8,1250) or set(np.unique(y))!={0,1}:
        raise ValueError("The preregistered 8x1250 binary subject format is required")
    if not reference.is_file():
        raise FileNotFoundError("Exact saved optical folds required: "+str(reference))
    configs = [(band,c) for band in BANDS for c in CS] if method=="fbcsp" else EEG_CONFIGS
    default = configs.index(("A",1.0) if method=="fbcsp" else (3e-3,32,1e-2,60))
    output = {"meta":json.dumps({"sid":path.stem,"method":method,"configs":configs,"default_index":default,
                                "pilot":pilot,"source_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
                                "reference_sha256":hashlib.sha256(reference.read_bytes()).hexdigest()})}
    with existing_modules() as (nested,B), np.load(reference,allow_pickle=False) as ref:
        filtered = {}
        if method=="fbcsp":
            for name,bands in BANDS.items():
                filtered[name] = [sosfiltfilt(butter(4,[lo,hi],btype="bandpass",fs=250,output="sos"),X,axis=-1) for lo,hi in bands]
        for k,(train,test,run) in enumerate(nested.outer_folds(runs)):
            np.testing.assert_array_equal(train,ref[f"tr|{run}"])
            np.testing.assert_array_equal(test,ref[f"te|{run}"])
            inner = nested.inner_folds(runs,train)
            for it,iv,v in inner:
                np.testing.assert_array_equal(it,ref[f"it|{run}|{v}"])
                np.testing.assert_array_equal(iv,ref[f"iv|{run}|{v}"])
                if set(it)&set(test) or set(iv)&set(test):
                    raise ValueError("External test leakage")
            output[f"tr|{run}"],output[f"te|{run}"],output[f"y|{run}"] = train,test,y[test]
            losses = np.zeros(36) if inner else None
            accuracies = np.zeros(36) if inner else None
            total = 0
            for j,(it,iv,v) in enumerate(inner):
                output[f"it|{run}|{v}"],output[f"iv|{run}|{v}"],output[f"yv|{run}|{v}"] = it,iv,y[iv]
                if method=="fbcsp":
                    predictions = [fit_fbcsp(B,filtered[band],y,it,[iv],c)[0] for band,c in configs]
                else:
                    snapshots = {cfg:fit_eegnet(B,X,y,it,[iv],*cfg,seed=100+10*k+j) for cfg in dict.fromkeys(c[:3] for c in configs)}
                    predictions = [snapshots[cfg[:3]][cfg[3]][0] for cfg in configs]
                for c,z in enumerate(predictions):
                    output[f"i|{run}|{v}|{c}"] = z
                    losses[c] += (np.logaddexp(0,z)-y[iv]*z).sum()
                    accuracies[c] += ((z>0)==y[iv]).sum()
                total += len(iv)
            if total:
                losses /= total
                accuracies /= total
            chosen = choose(losses,default)
            # All external grid logits are retained to compute N2/N3; N1 was
            # irrevocably selected from internal data before reading y[test].
            if method=="fbcsp":
                predictions = [fit_fbcsp(B,filtered[band],y,train,[test],c)[0] for band,c in configs]
            else:
                snapshots = {cfg:fit_eegnet(B,X,y,train,[test],*cfg,seed=k) for cfg in dict.fromkeys(c[:3] for c in configs)}
                predictions = [snapshots[cfg[:3]][cfg[3]][0] for cfg in configs]
            for c,z in enumerate(predictions):
                output[f"o|{run}|{c}"] = z
            output[f"selected|{run}"] = np.array([chosen])
            output[f"inner_bce|{run}"] = losses if losses is not None else np.empty(0)
            output[f"inner_acc|{run}"] = accuracies if accuracies is not None else np.empty(0)
            print(json.dumps({"subject":path.stem,"run":run,"method":method,"seconds":time.monotonic()-start}),flush=True)
            if pilot:
                break
    output["seconds"] = np.array([time.monotonic()-start])
    return output


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data",type=Path,required=True)
    parser.add_argument("--optical-raw",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    parser.add_argument("--method",choices=["fbcsp","eegnet"],required=True)
    parser.add_argument("--subjects",nargs="+",default=["S001"])
    parser.add_argument("--pilot",action="store_true")
    args=parser.parse_args()
    import torch
    torch.set_num_threads(2)
    torch.set_num_interop_threads(1)  # Once, at startup of this fresh process.
    args.out.mkdir(parents=True,exist_ok=False)
    for sid in args.subjects:
        if len(sid)!=4 or not sid.startswith("S") or not sid[1:].isdigit():
            parser.error("Subject IDs must have the S### format")
        result=run_subject(args.data/(sid+".npz"),args.method,args.optical_raw/(sid+".npz"),args.pilot)
        np.savez_compressed(args.out/(sid+".npz"),**result)
