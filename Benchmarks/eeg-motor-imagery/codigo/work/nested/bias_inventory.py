"""Inventario y estimacion del sesgo de seleccion en los LORO historicos de Motor Imagery.
Solo lee los bench_*.json (por sujeto) de work/. CPU, segundos.  Uso: python bias_inventory.py
Salida: bias_inventory.json + texto por stdout."""
import json, os, itertools, sys
import numpy as np
from scipy.stats import wilcoxon, ttest_rel

W = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(20260930)


def load(fn, key):
    d = json.load(open(os.path.join(W, fn)))[key]["per_subject"]; return d


SRC = {   # nombre: (fichero, clave, protocolo)
    "fbcsp_f8":        ("bench_fbcsp_optic_polar_free_loro.json", "fbcsp"),
    "optic_f8":        ("bench_fbcsp_optic_polar_free_loro.json", "optic"),
    "polar_f8w1":      ("bench_fbcsp_optic_polar_free_loro.json", "polar"),
    "free_f8w1":       ("bench_fbcsp_optic_polar_free_loro.json", "free"),
    "eegnet":          ("bench_eegnet_loro.json", "eegnet"),
    "lattice_f8w1":    ("bench_lattice_lattice32_loro.json", "lattice"),
    "lattice32_f8w1":  ("bench_lattice_lattice32_loro.json", "lattice32"),
    "polar_f12w3":     ("bench_polar_lattice32_loro_f12w3.json", "polar"),
    "lattice32_f12w3": ("bench_polar_lattice32_loro_f12w3.json", "lattice32"),
}
D = {k: load(*v) for k, v in SRC.items()}
subs = sorted(next(iter(D.values())).keys()); n = len(subs)
M = {k: np.array([D[k][s] for s in subs]) for k in D}
res = {"n_subjects": n, "subjects": subs, "loro_mean": {}, "paired": {}, "winner_curse": {}}

print(f"== LORO por configuracion (n={n} sujetos): media, SD entre sujetos, EE = SD/sqrt(n)")
for k, v in sorted(M.items(), key=lambda kv: -kv[1].mean()):
    res["loro_mean"][k] = dict(mean=float(v.mean()), sd=float(v.std(ddof=1)), se=float(v.std(ddof=1) / np.sqrt(n)))
    print(f"  {k:18s} {v.mean():.4f}  sd {v.std(ddof=1):.3f}  ee {v.std(ddof=1)/np.sqrt(n):.4f}")

B = 20000
def paired(a, b):
    d = M[a] - M[b]; idx = rng.integers(0, n, (B, n)); bs = d[idx].mean(1)
    lo, hi = np.percentile(bs, [2.5, 97.5])
    # sign-flip (permutation) exacto/MC
    signs = rng.choice([-1, 1], (B, n)); pf = float((np.abs((signs * d).mean(1)) >= abs(d.mean()) - 1e-12).mean())
    try: pw = float(wilcoxon(d).pvalue)
    except Exception: pw = float("nan")
    return dict(diff=float(d.mean()), ee=float(d.std(ddof=1) / np.sqrt(n)), ci95=[float(lo), float(hi)], p_signflip=pf,
                p_wilcoxon=pw, p_ttest=float(ttest_rel(M[a], M[b]).pvalue), wins=int((d > 0).sum()), ties=int((d == 0).sum()), losses=int((d < 0).sum()))

print("\n== Diferencias emparejadas por sujeto (a - b): media, EE, IC95% bootstrap por sujetos, p sign-flip, Wilcoxon, victorias/empates/derrotas")
for a, b in [("polar_f12w3", "polar_f8w1"), ("lattice32_f12w3", "lattice32_f8w1"), ("polar_f12w3", "lattice32_f12w3"),
             ("polar_f12w3", "free_f8w1"), ("polar_f12w3", "lattice32_f8w1"), ("polar_f8w1", "free_f8w1"), ("polar_f12w3", "fbcsp_f8"),
             ("lattice32_f12w3", "polar_f8w1"), ("lattice32_f12w3", "free_f8w1"), ("polar_f12w3", "eegnet")]:
    r = paired(a, b); res["paired"][f"{a} - {b}"] = r
    print(f"  {a:16s}-{b:16s} {r['diff']:+.4f} ee {r['ee']:.4f} IC95 [{r['ci95'][0]:+.4f},{r['ci95'][1]:+.4f}] p_sf {r['p_signflip']:.3f} p_wil {r['p_wilcoxon']:.3f} {r['wins']}/{r['ties']}/{r['losses']}")

# Maldicion del ganador: elegir el mejor de K candidatos con la muestra in-bag; medir su media en los sujetos OOB.
def winner_curse(names, B=4000):
    X = np.stack([M[k] for k in names], 1); K = len(names); opt = []; oob_all = []; pick = np.zeros(K)
    for _ in range(B):
        idx = rng.integers(0, n, n); oob = np.setdiff1d(np.arange(n), idx)
        if len(oob) < 2: continue
        inb = X[idx].mean(0); w = int(inb.argmax()); pick[w] += 1
        opt.append(inb[w] - X[oob, w].mean())
    return float(np.mean(opt)), np.percentile(opt, [5, 95]).tolist(), (pick / pick.sum()).tolist()

print("\n== Maldicion del ganador (bootstrap por sujetos: media del mejor in-bag menos su media en sujetos OOB)")
sets = {"todas_9": list(M), "opticas_con_pesos_libres_f8_y_f12w3": ["polar_f8w1", "free_f8w1", "lattice_f8w1", "lattice32_f8w1", "polar_f12w3", "lattice32_f12w3"],
        "solo_polar_y_lattice32_dos_features": ["polar_f8w1", "polar_f12w3", "lattice32_f8w1", "lattice32_f12w3"],
        "solo_f8w1_vs_f12w3_polar": ["polar_f8w1", "polar_f12w3"]}
for nm, ks in sets.items():
    o, ci, pk = winner_curse(ks); res["winner_curse"][nm] = dict(K=len(ks), optimism=o, p5_p95=ci, pick_freq=dict(zip(ks, pk)))
    print(f"  {nm:40s} K={len(ks)}  optimismo medio {o:+.4f}  (p5..p95 {ci[0]:+.4f}..{ci[1]:+.4f})  mas elegido: {ks[int(np.argmax(pk))]} ({max(pk):.2f})")

# Ruido de un solo numero LORO: EE de la media entre sujetos y su equivalente binomial por epoca
tot = 0
import glob
ne = {os.path.basename(f)[:4]: 0 for f in glob.glob(os.path.join(W, "data", "S*.npz"))}
for f in glob.glob(os.path.join(W, "data", "S*.npz")):
    ne[os.path.basename(f)[:4]] = int(len(np.load(f)["ytr"]))
N = sum(ne.values()); p = 0.7
res["n_epochs_loro"] = N; res["binomial_se_pooled_epochs"] = float(np.sqrt(p * (1 - p) / N))
print(f"\nEpocas totales LORO: {N}; EE binomial (p=0.7) de una exactitud agrupada: {res['binomial_se_pooled_epochs']:.4f}; EE entre sujetos de una media LORO: ~{M['polar_f12w3'].std(ddof=1)/np.sqrt(n):.4f}")
json.dump(res, open(os.path.join(OUT, "bias_inventory.json"), "w"), indent=1)
