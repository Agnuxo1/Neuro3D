"""Within-subject benchmark (pre-declared): stratified 5-fold x 3 repeats per subject, same folds for all models.
Models:
  fbcsp   ML category: filter bank CSP (3 pairs/band) + log-var + shrinkage LDA.
  optic   DL category: Morlet CWT (complex) per band -> learned 8x8 UNITARY mesh per band -> |.|^2 (detectors)
          -> mean over time -> log -> linear readout. Unitary = exp(A - A^H) (a mesh of MZIs spans U(8)).
  free    same as optic but unconstrained complex 8x8 matrix (equal parameter count) -> tests unitarity.
  eegnet  EEGNet-8,2 on the 1-100 Hz signal.
Usage: python bench.py [models comma list] [subjects comma list or all]
"""
import glob, json, math, os, sys, time
import numpy as np, torch, torch.nn as nn
from scipy.signal import butter, sosfiltfilt
from scipy.linalg import eigh
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.model_selection import RepeatedStratifiedKFold

torch.set_num_threads(int(os.environ.get("TORCH_THREADS", "8")))
HERE = os.path.dirname(os.path.abspath(__file__)); FS = 250
FREQS = [int(v) for v in os.environ.get("FREQS", "8,10,12,14,17,20,24,28").split(",")]
WIN = int(os.environ.get("WIN", "1"))
BANDS = [(8, 12), (12, 16), (16, 20), (20, 24), (24, 30)]


def cwt(X, freqs=FREQS, ncyc=5, step=5):
    """Complex Morlet CWT, keeps time axis. X (n,8,T) -> (n,F,8,T/step) complex64."""
    n, C, T = X.shape; out = []
    Xf = np.fft.rfft(X, axis=-1); fr = np.fft.rfftfreq(T, 1 / FS)
    for f in freqs:
        s = ncyc / (2 * np.pi * f)
        G = np.exp(-0.5 * ((fr - f) * 2 * np.pi * s) ** 2)            # analytic (positive freqs only)
        Z = np.fft.ifft(np.concatenate([Xf * G * 2, np.zeros_like(Xf[..., 1:T - Xf.shape[-1] + 1])], -1), n=T, axis=-1)
        out.append(Z[..., ::step])
    return np.stack(out, 1).astype(np.complex64)


class Optic(nn.Module):
    def __init__(self, F, C=8, unitary=True, modes=None, read=None):
        super().__init__(); self.unitary = unitary; self.C = C
        M = modes or C; self.read = read or C          # dilation: M-mode mesh, C inputs (rest dark), read first `read` detectors
        self.A = nn.Parameter(0.1 * torch.randn(F, M, M, dtype=torch.cfloat))
        self.norm = nn.Parameter(torch.zeros(F, self.read, WIN)); self.out = nn.Linear(F * self.read * WIN, 1)

    def U(self):
        if self.unitary == "polar":
            u, _, vh = torch.linalg.svd(self.A + torch.eye(self.A.shape[-1], device=self.A.device)); return u @ vh
        if not self.unitary: return self.A + torch.eye(self.A.shape[-1], device=self.A.device)
        return torch.matrix_exp(self.A - self.A.conj().transpose(-1, -2))

    def forward(self, Z):                        # Z (n,F,C,t) complex
        U = self.U()[:, :self.read, :self.C]            # dark auxiliary inputs; unread detectors = loss
        I = torch.einsum("fij,nfjt->nfit", U, Z).abs().pow(2)
        I = torch.stack([c.mean(-1) for c in I.chunk(WIN, -1)], -1)          # detector power per time window
        return self.out((torch.log(I + 1e-6) + self.norm).flatten(1)).squeeze(-1)


class OpticSVD(nn.Module):
    """Photonic SVD architecture (Miller / Shen et al. 2017): mesh U2 -> per-mode attenuators (loss, <=1) -> mesh U1.
    W = U1 diag(sigmoid(s)) U2 is any contraction; physically realizable with two MZI meshes + attenuators."""
    def __init__(self, F, C=8):
        super().__init__()
        self.A1 = nn.Parameter(0.1 * torch.randn(F, C, C, dtype=torch.cfloat))
        self.A2 = nn.Parameter(0.1 * torch.randn(F, C, C, dtype=torch.cfloat))
        self.s = nn.Parameter(torch.zeros(F, C)); self.norm = nn.Parameter(torch.zeros(F, C)); self.out = nn.Linear(F * C, 1)

    def forward(self, Z):
        ex = lambda A: torch.matrix_exp(A - A.conj().transpose(-1, -2))
        W = ex(self.A1) @ (torch.sigmoid(self.s).unsqueeze(-1).to(torch.cfloat) * ex(self.A2))
        I = torch.einsum("fij,nfjt->nfit", W, Z).abs().pow(2).mean(-1)
        return self.out((torch.log(I + 1e-6) + self.norm).flatten(1)).squeeze(-1)


class LatticeNet(nn.Module):
    """Hardware-aware: the only mixing parameters are the roof-delay phases of the Blender lattice (K=4, 16 cells).
    per-band: one lattice per CWT band at lambda0.  spectral: ONE lattice, band f at lambda0*FREQS[0]/FREQS[f]."""
    def __init__(self, F, spectral=False, lam0=0.1, links=False):
        super().__init__(); import lattice_torch as LT; self.LT = LT
        self.spectral = spectral; nb = 1 if spectral else F
        self.theta = nn.Parameter(2 * math.pi * torch.rand(nb, 4, 4, dtype=torch.float64))
        self.phi = nn.Parameter(2 * math.pi * torch.rand(nb, 4, 4, dtype=torch.float64)) if links else None
        lam = [lam0 * FREQS[0] / f for f in FREQS] if spectral else [lam0] * F
        self.register_buffer("lam", torch.tensor(lam, dtype=torch.float64)); self.lam0 = lam0
        self.norm = nn.Parameter(torch.zeros(F, 8, WIN)); self.out = nn.Linear(F * 8 * WIN, 1)

    def d(self):  # physical roof offsets (BU): phase theta at lambda0 = 2*k0*d
        return self.theta * self.lam0 / (4 * math.pi)

    def forward(self, Z):
        dd = self.d().expand(len(self.lam), 4, 4) if self.spectral else self.d()
        dl = None if self.phi is None else self.phi * self.lam0 / (2 * math.pi)
        U = self.LT.lattice_U(dd, self.lam, dlink=dl).to(torch.cfloat)
        I = torch.einsum("fij,nfjt->nfit", U, Z).abs().pow(2)
        I = torch.stack([c.mean(-1) for c in I.chunk(WIN, -1)], -1)
        return self.out((torch.log(I + 1e-6) + self.norm).flatten(1)).squeeze(-1)


class EEGNet(nn.Module):
    def __init__(self, C=8, T=1250, F1=8, D=2, F2=16, p=0.5):
        super().__init__()
        self.b = nn.Sequential(nn.Conv2d(1, F1, (1, 125), padding=(0, 62), bias=False), nn.BatchNorm2d(F1),
                               nn.Conv2d(F1, F1 * D, (C, 1), groups=F1, bias=False), nn.BatchNorm2d(F1 * D), nn.ELU(),
                               nn.AvgPool2d((1, 4)), nn.Dropout(p),
                               nn.Conv2d(F1 * D, F1 * D, (1, 16), padding=(0, 8), groups=F1 * D, bias=False),
                               nn.Conv2d(F1 * D, F2, 1, bias=False), nn.BatchNorm2d(F2), nn.ELU(), nn.AvgPool2d((1, 8)), nn.Dropout(p))
        with torch.no_grad(): n = self.b(torch.zeros(1, 1, C, T)).numel()
        self.out = nn.Linear(n, 1)

    def forward(self, X): return self.out(self.b(X.unsqueeze(1)).flatten(1)).squeeze(-1)


DEV = torch.device(os.environ.get("BENCH_DEV", "cpu"))


def train_torch(make, Xtr, ytr, Xte, epochs, lr=1e-2, wd=1e-3, bs=32, seed=0):
    torch.manual_seed(seed); model = make().to(DEV); opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=wd)
    Xtr, Xte = torch.as_tensor(Xtr).to(DEV), torch.as_tensor(Xte).to(DEV); y = torch.as_tensor(ytr, dtype=torch.float32).to(DEV)
    for ep in range(epochs):
        model.train(); perm = torch.randperm(len(y))
        for i in range(0, len(y), bs):
            b = perm[i:i + bs]; opt.zero_grad()
            nn.functional.binary_cross_entropy_with_logits(model(Xtr[b]), y[b]).backward(); opt.step()
    model.eval()
    with torch.no_grad(): return (model(Xte) > 0).cpu().numpy().astype(int)


def csp_filters(X, y, k=3):
    C = [np.mean([x @ x.T / np.trace(x @ x.T) for x in X[y == c]], 0) for c in (0, 1)]
    w, V = eigh(C[1], C[0] + C[1]); return np.concatenate([V[:, :k], V[:, -k:]], 1)


def fbcsp(Xtr, ytr, Xte):
    ftr, fte = [], []
    for lo, hi in BANDS:
        sos = butter(4, [lo, hi], btype="band", fs=FS, output="sos")
        a, b = sosfiltfilt(sos, Xtr, axis=-1), sosfiltfilt(sos, Xte, axis=-1)
        W = csp_filters(a, ytr)
        ftr.append(np.log(np.var(np.einsum("ck,nct->nkt", W, a), -1))); fte.append(np.log(np.var(np.einsum("ck,nct->nkt", W, b), -1)))
    lda = LinearDiscriminantAnalysis(solver="lsqr", shrinkage="auto").fit(np.concatenate(ftr, 1), ytr)
    return lda.predict(np.concatenate(fte, 1))


def zscore(Xtr, Xte):
    s = Xtr.std(axis=(0, 2), keepdims=True) + 1e-6; return Xtr / s, Xte / s


def run(models, subjects):
    res = {m: {} for m in models}; t0 = time.time()
    for f in sorted(glob.glob(os.path.join(HERE, "data", "S*.npz"))):
        sid = os.path.basename(f)[:4]
        if subjects and sid not in subjects: continue
        d = np.load(f); X, y = d["Xtr"].astype(np.float32), d["ytr"]
        Z = cwt(X)
        if os.environ.get("CV") == "loro":
            runs = d["run"]; splits = [(np.where(runs != r)[0], np.where(runs == r)[0]) for r in sorted(set(runs))]
        else:
            splits = list(RepeatedStratifiedKFold(n_splits=5, n_repeats=3, random_state=0).split(X, y))
        acc = {m: [] for m in models}; wts = []
        for k, (tr, te) in enumerate(splits):
            wts.append(len(te))
            for m in models:
                if m == "fbcsp": p = fbcsp(X[tr], y[tr], X[te])
                elif m in ("optic", "free", "optic16r8", "optic16r16"):
                    s = np.abs(Z[tr]).std(axis=(0, 3), keepdims=True) + 1e-6
                    kw = {"optic16r8": dict(modes=16, read=8), "optic16r16": dict(modes=16, read=16)}.get(m, {})
                    p = train_torch(lambda: Optic(len(FREQS), unitary=(m != "free"), **kw), Z[tr] / s, y[tr], Z[te] / s, epochs=60, lr=2e-2, seed=k)
                elif m in ("lattice", "spectral", "lattice32"):
                    s = np.abs(Z[tr]).std(axis=(0, 3), keepdims=True) + 1e-6
                    p = train_torch(lambda: LatticeNet(len(FREQS), spectral=(m == "spectral"), links=(m == "lattice32")), Z[tr] / s, y[tr], Z[te] / s, epochs=60, lr=2e-2, seed=k)
                elif m == "polar":
                    s = np.abs(Z[tr]).std(axis=(0, 3), keepdims=True) + 1e-6
                    p = train_torch(lambda: Optic(len(FREQS), unitary="polar"), Z[tr] / s, y[tr], Z[te] / s, epochs=60, lr=2e-2, seed=k)
                elif m == "opticsvd":
                    s = np.abs(Z[tr]).std(axis=(0, 3), keepdims=True) + 1e-6
                    p = train_torch(lambda: OpticSVD(len(FREQS)), Z[tr] / s, y[tr], Z[te] / s, epochs=60, lr=2e-2, seed=k)
                elif m == "eegnet":
                    a, b = zscore(X[tr], X[te]); p = train_torch(lambda: EEGNet(), a, y[tr], b, epochs=80, lr=3e-3, wd=1e-2, seed=k)
                acc[m].append(float((p == y[te]).mean()))
        for m in models: res[m][sid] = float(np.average(acc[m], weights=wts))
        print(sid, {m: round(res[m][sid], 3) for m in models}, f"{time.time() - t0:.0f}s", flush=True)
    summ = {m: {"mean": float(np.mean(list(r.values()))), "per_subject": r} for m, r in res.items()}
    for m in models: print(f"{m:7s} mean acc {summ[m]['mean']:.4f}")
    tag = "_loro" if os.environ.get("CV") == "loro" else ""
    tag += os.environ.get("TAGX", "")
    json.dump(summ, open(os.path.join(HERE, f"bench_{'_'.join(models)}{tag}.json"), "w"), indent=1)


if __name__ == "__main__":
    models = sys.argv[1].split(",") if len(sys.argv) > 1 else ["fbcsp", "optic", "free", "eegnet"]
    subs = sys.argv[2].split(",") if len(sys.argv) > 2 and sys.argv[2] != "all" else None
    run(models, subs)
