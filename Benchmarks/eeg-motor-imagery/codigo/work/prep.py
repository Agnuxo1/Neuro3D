"""Epoching for Low Cost Motor Imagery (single subject). Allowed DL preprocessing only:
50 Hz notch + 1-100 Hz broad band-pass (zero-phase), applied to the continuous recording.
Epoch = [cue, cue + 5 s) (1250 samples @ 250 Hz); train cue = 'move'/'rest' marker, test cue = 'cue_start'.
Also stores the 1 s before the cue (inside trail_start period) as an optional baseline.
Output: data/S###.npz with Xtr (n,8,1250), ytr (1=move), run, Xte (40,8,1250), and pre-cue baselines.
"""
import csv, glob, os, re
import numpy as np
from scipy.signal import iirnotch, butter, filtfilt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FS, N, PRE = 250, 1250, 250
CH = ["Fz", "C3", "Cz", "C4", "PO7", "Pz", "PO8", "Oz"]
os.makedirs(os.path.join(ROOT, "work", "data"), exist_ok=True)
bn, an = iirnotch(50, 30, FS)
bb, ab = butter(4, [1, 100], btype="band", fs=FS)


def load(f):
    rows = list(csv.DictReader(open(f)))
    X = np.array([[float(r[c]) for c in CH] for r in rows]).T
    X = filtfilt(bb, ab, filtfilt(bn, an, X - X.mean(1, keepdims=True), axis=1), axis=1)
    marks = [(i, r["Marker_val"]) for i, r in enumerate(rows) if r["Marker_val"]]
    return X.astype(np.float32), marks


def cut(X, i):
    if i - PRE < 0 or i + N > X.shape[1]: return None
    return X[:, i:i + N], X[:, i - PRE:i]


for f in sorted(glob.glob(os.path.join(ROOT, "Single subject test set", "*.csv"))):
    sid = re.search(r"(S\d{3})_test", f).group(1)
    Xte, Bte = [], []
    X, marks = load(f)
    for i, m in marks:
        if m == "cue_start":
            e = cut(X, i); assert e is not None, (sid, i)
            Xte.append(e[0]); Bte.append(e[1])
    Xtr, Btr, ytr, run = [], [], [], []
    for g in sorted(glob.glob(os.path.join(ROOT, "Training set", f"{sid}-*_eeg.csv"))):
        X, marks = load(g); r = int(re.search(r"-(\d{3})_eeg", g).group(1))
        for i, m in marks:
            if m in ("move", "rest"):
                e = cut(X, i)
                if e is None: continue
                Xtr.append(e[0]); Btr.append(e[1]); ytr.append(int(m == "move")); run.append(r)
    np.savez_compressed(os.path.join(ROOT, "work", "data", f"{sid}.npz"), Xtr=np.array(Xtr), Btr=np.array(Btr),
                        ytr=np.array(ytr), run=np.array(run), Xte=np.array(Xte), Bte=np.array(Bte))
    print(sid, "train", len(ytr), "move", sum(ytr), "runs", sorted(set(run)), "test", len(Xte), flush=True)
