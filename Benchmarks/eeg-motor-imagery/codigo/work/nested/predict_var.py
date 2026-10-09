"""Predicciones para Kaggle con la configuracion elegida por la validacion anidada (no toca predict.py).
Entrena por sujeto con TODOS los runs, 5 semillas, y promedia logits sobre las 40 epocas de test.
Uso (GPU por gpuq): python predict_var.py <polar|lattice32|free> <epocas> <wd> [cuda|cpu]
Salida: work/submission_<modelo>_f12w3_e<epocas>_wd<wd>.csv  (ID,TARGET con move/rest; mismo formato que predict.py)"""
import glob, os, sys
os.environ.update(FREQS="6,8,10,12,14,16,18,20,23,26,30,35", WIN="3")
WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, WORK); os.chdir(WORK)
import numpy as np, torch
import bench as B

model = sys.argv[1]; EP = int(sys.argv[2]); WD = float(sys.argv[3]); dev = sys.argv[4] if len(sys.argv) > 4 else "cpu"
torch.set_num_threads(4)
rows, cnt = [], 0
for f in sorted(glob.glob(os.path.join(B.HERE, "data", "S*.npz"))):
    d = np.load(f); X, y, Xt = d["Xtr"].astype(np.float32), d["ytr"], d["Xte"].astype(np.float32)
    Z, Zt = B.cwt(X), B.cwt(Xt); s = np.abs(Z).std(axis=(0, 3), keepdims=True) + 1e-6
    Zi, Zti = torch.as_tensor(Z / s).to(dev), torch.as_tensor(Zt / s).to(dev); yt = torch.as_tensor(y, dtype=torch.float32).to(dev)
    logit = np.zeros(len(Xt))
    for sd in range(5):
        torch.manual_seed(sd)
        m = (B.LatticeNet(len(B.FREQS), links=True) if model == "lattice32" else B.Optic(len(B.FREQS), unitary=("polar" if model == "polar" else False))).to(dev)
        opt = torch.optim.AdamW(m.parameters(), lr=2e-2, weight_decay=WD)
        for ep in range(EP):
            m.train(); perm = torch.randperm(len(yt))
            for i in range(0, len(yt), 32):
                b = perm[i:i + 32]; opt.zero_grad()
                torch.nn.functional.binary_cross_entropy_with_logits(m(Zi[b]), yt[b]).backward(); opt.step()
        m.eval()
        with torch.no_grad(): logit += m(Zti).cpu().numpy()
    pred = (logit > 0).astype(int)
    for p in pred: rows.append((cnt, "move" if p else "rest")); cnt += 1
    print(os.path.basename(f)[:4], "test", len(pred), "move frac", round(pred.mean(), 2), flush=True)
out = os.path.join(WORK, f"submission_{model}_f12w3_e{EP}_wd{WD:g}.csv")
with open(out, "w", newline="\n") as fh:
    fh.write("ID,TARGET\n"); fh.writelines(f"{i},{t}\n" for i, t in rows)
print("rows", cnt, "->", out)
