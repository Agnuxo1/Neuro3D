"""Validacion ANIDADA por sujeto para Motor Imagery (modelos opticos). Ver PREINSCRIPCION.md (rejilla declarada ANTES de ejecutar).

Bucle externo : leave-one-run-out (LORO) por sujeto, identico a bench.py (CV=loro): semilla = indice del fold.
Bucle interno : dentro del entrenamiento externo, leave-one-run-out interno (grupo = 'run', nunca se mezclan epocas de un mismo run
                entre entrenamiento y validacion; un run externo de test no aparece nunca en el bucle interno).
Este script SOLO entrena y guarda logits crudos (externos e internos) por sujeto en raw/<tag>/S###.npz;
la seleccion y todas las estimaciones se hacen fuera, en analyze_nested.py (asi no hay forma de "mirar" el test externo al elegir).

Numero de epocas: la trayectoria de entrenamiento (AdamW, lr constante, semilla fija) es identica hasta la epoca e, asi que UNA
ejecucion de max(EPOCHS) epocas da los logits de todas las instantaneas (epocas 30/60/90) sin coste extra (verificado en test_nested_groups.py).

Uso (CPU o GPU; la GPU SOLO por la cola gpuq, lo lanza Claude principal):
  python nested_bench.py --grid full --tag full --dev cuda --subjects all --shard 0/4
  python nested_bench.py --grid smoke --tag smoke --dev cpu --subjects S001,S007
"""
import argparse, glob, itertools, json, os, sys, time
os.environ.setdefault("TORCH_THREADS", "4"); os.environ.setdefault("OMP_NUM_THREADS", "4")
HERE = os.path.dirname(os.path.abspath(__file__)); WORK = os.path.dirname(HERE)
sys.path.insert(0, WORK)
import numpy as np

FEATS = {"f8w1": ([8, 10, 12, 14, 17, 20, 24, 28], 1),
         "f12w3": ([6, 8, 10, 12, 14, 16, 18, 20, 23, 26, 30, 35], 3)}
MIN_TRAIN, MIN_VAL = 20, 10            # reglas declaradas para folds internos validos (ver PREINSCRIPCION.md)
LR, BS = 2e-2, 32

GRIDS = {   # (modelos, features, wd, epocas-instantanea, config por defecto)
    "full": dict(kinds=["polar", "lattice32", "free"], feats=["f8w1", "f12w3"], wds=[1e-3, 1e-2], epochs=[30, 60, 90],
                 default=("polar", "f12w3", 1e-3, 60)),
    "finalists": dict(kinds=["polar", "lattice32", "free"], feats=["f12w3"], wds=[1e-2], epochs=[90],
                      default=("polar", "f12w3", 1e-2, 90)),   # ADDENDUM-SEEDS5.md (post-hoc, declarado antes de ejecutar)
    "smoke": dict(triples=[("polar", "f8w1", 1e-3), ("polar", "f12w3", 1e-3), ("lattice32", "f8w1", 1e-3), ("lattice32", "f12w3", 1e-3),
                         ("free", "f8w1", 1e-3), ("free", "f12w3", 1e-3)],
                  epochs=[2, 4], default=("polar", "f12w3", 1e-3, 4)),
}


def grid_triples(g):
    return g["triples"] if "triples" in g else [(k, f, w) for k in g["kinds"] for f in g["feats"] for w in g["wds"]]


# ----------------------------------------------------------------------------- particiones (probadas en test_nested_groups.py)
def outer_folds(runs):
    """LORO externo, en el mismo orden que bench.py: [(idx_train, idx_test, run_test)]."""
    return [(np.where(runs != r)[0], np.where(runs == r)[0], int(r)) for r in sorted(set(runs.tolist()))]


def inner_folds(runs, tr, min_train=MIN_TRAIN, min_val=MIN_VAL):
    """LORO interno sobre el entrenamiento externo `tr` (indices absolutos). Grupo = run. Devuelve [(it, iv, run_val)].
    Solo folds con >= min_train epocas de entrenamiento y >= min_val de validacion. Nunca mezcla un run entre it y iv."""
    rr = runs[tr]; out = []
    for v in sorted(set(rr.tolist())):
        iv, it = tr[rr == v], tr[rr != v]
        if len(it) >= min_train and len(iv) >= min_val and len(set(rr[rr != v].tolist())) >= 1:
            assert not (set(runs[it].tolist()) & set(runs[iv].tolist())), "run compartido entre train y val interno"
            out.append((it, iv, int(v)))
    return out


# ----------------------------------------------------------------------------- entrenamiento con instantaneas
def make_scaled(Z, runs, tr, evs, norm):
    """Escala por banda/canal. norm='train' (bench.py): std de Z[tr]. norm='run' (sin etiquetas): cada run con su propia std."""
    if norm == "train":
        s = np.abs(Z[tr]).std(axis=(0, 3), keepdims=True) + 1e-6
        return Z[tr] / s, [Z[e] / s for e in evs]
    def sc(idx):
        out = np.empty_like(Z[idx])
        for r in set(runs[idx].tolist()):
            m = runs[idx] == r; z = Z[idx][m]
            out[m] = z / (np.abs(z).std(axis=(0, 3), keepdims=True) + 1e-6)
        return out
    return sc(tr), [sc(e) for e in evs]


def fit_snapshots(B, torch, kind, feat, Ztr, ytr, Zevs, snaps, wd, seed, lr=LR, bs=BS):
    """Igual que bench.train_torch, pero devuelve los logits (no las etiquetas) en cada epoca de `snaps`."""
    freqs, win = FEATS[feat]; B.WIN = win            # bench.py lee WIN global al construir y en forward
    torch.manual_seed(seed)
    if kind == "polar": model = B.Optic(len(freqs), unitary="polar")
    elif kind == "free": model = B.Optic(len(freqs), unitary=False)
    elif kind == "lattice32": model = B.LatticeNet(len(freqs), links=True)
    else: raise ValueError(kind)
    model = model.to(B.DEV); opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=wd)
    Xtr = torch.as_tensor(Ztr).to(B.DEV); y = torch.as_tensor(ytr, dtype=torch.float32).to(B.DEV)
    Xev = [torch.as_tensor(z).to(B.DEV) for z in Zevs]; out = {}
    for ep in range(1, max(snaps) + 1):
        model.train(); perm = torch.randperm(len(y))
        for i in range(0, len(y), bs):
            b = perm[i:i + bs]; opt.zero_grad()
            torch.nn.functional.binary_cross_entropy_with_logits(model(Xtr[b]), y[b]).backward(); opt.step()
        if ep in snaps:
            model.eval()
            with torch.no_grad(): out[ep] = [model(x).cpu().numpy().astype(np.float32) for x in Xev]
    return out


# ----------------------------------------------------------------------------- sujeto
def run_subject(B, torch, sid, grid, args, log):
    d = np.load(os.path.join(WORK, "data", sid + ".npz")); X, y, runs = d["Xtr"].astype(np.float32), d["ytr"], d["run"]
    triples = grid_triples(grid); epochs = grid["epochs"]; feats = sorted({f for _, f, _ in triples})
    Z = {f: B.cwt(X, freqs=FEATS[f][0]) for f in feats}
    R = {"meta": json.dumps(dict(sid=sid, triples=[[k, f, w] for k, f, w in triples], epochs=epochs, default=list(grid["default"]),
                                 norm=args.norm, seeds=args.seeds, runs=sorted(set(runs.tolist())), min_train=MIN_TRAIN, min_val=MIN_VAL,
                                 inner=not args.no_inner, dev=str(B.DEV)))}
    t0 = time.time(); ntrain = 0
    for k, (tr, te, r_out) in enumerate(outer_folds(runs)):
        R[f"tr|{r_out}"], R[f"te|{r_out}"], R[f"y|{r_out}"] = tr, te, y[te]
        inner = [] if args.no_inner else inner_folds(runs, tr)
        for it, iv, v in inner:
            assert not (set(runs[it].tolist()) | set(runs[iv].tolist())) & {r_out}, "el run externo de test aparece en el bucle interno"
            assert set(it.tolist()) | set(iv.tolist()) <= set(tr.tolist())
            R[f"it|{r_out}|{v}"], R[f"iv|{r_out}|{v}"], R[f"yv|{r_out}|{v}"] = it, iv, y[iv]
        for kind, feat, wd in triples:
            Ztr, (Zte,) = make_scaled(Z[feat], runs, tr, [te], args.norm)
            acc = None
            for sd in range(args.seeds):           # semilla 0 del externo = indice de fold (como bench.py); >1 => promedio de logits
                o = fit_snapshots(B, torch, kind, feat, Ztr, y[tr], [Zte], epochs, wd, seed=k + 1000 * sd); ntrain += 1
                acc = o if acc is None else {e: [acc[e][0] + o[e][0]] for e in o}
            for e in epochs: R[f"o|{r_out}|{kind}|{feat}|{wd:g}|{e}"] = acc[e][0] / args.seeds
            for j, (it, iv, v) in enumerate(inner):
                Zit, (Ziv,) = make_scaled(Z[feat], runs, it, [iv], args.norm)
                o = fit_snapshots(B, torch, kind, feat, Zit, y[it], [Ziv], epochs, wd, seed=100 + 10 * k + j); ntrain += 1
                for e in epochs: R[f"i|{r_out}|{v}|{kind}|{feat}|{wd:g}|{e}"] = o[e][0]
        log(f"  {sid} fold run={r_out} test={len(te)} inner_folds={[v for _, _, v in inner]} {time.time() - t0:.1f}s")
    R["seconds"] = np.array([time.time() - t0]); R["n_trainings"] = np.array([ntrain])
    return R


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--grid", default="smoke", choices=list(GRIDS)); ap.add_argument("--tag", default=None)
    ap.add_argument("--dev", default="cpu"); ap.add_argument("--subjects", default="all")
    ap.add_argument("--shard", default="0/1"); ap.add_argument("--seeds", type=int, default=1)
    ap.add_argument("--norm", default="train", choices=["train", "run"]); ap.add_argument("--no-inner", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args(); tag = args.tag or args.grid
    os.environ["BENCH_DEV"] = args.dev
    import torch, bench as B
    assert str(B.DEV) == args.dev or (args.dev == "cuda" and B.DEV.type == "cuda")
    torch.set_num_threads(int(os.environ["TORCH_THREADS"]))
    outdir = os.path.join(HERE, "raw", tag); os.makedirs(outdir, exist_ok=True)
    allsubs = sorted(os.path.basename(f)[:4] for f in glob.glob(os.path.join(WORK, "data", "S*.npz")))
    subs = allsubs if args.subjects == "all" else args.subjects.split(",")
    i, n = map(int, args.shard.split("/")); subs = [s for j, s in enumerate(subs) if j % n == i]
    grid = GRIDS[args.grid]; T0 = time.time()
    log = lambda m: print(m, flush=True)
    log(f"[nested] grid={args.grid} tag={tag} dev={B.DEV} threads={torch.get_num_threads()} subjects={subs} seeds={args.seeds} norm={args.norm} inner={not args.no_inner}")
    for sid in subs:
        fn = os.path.join(outdir, sid + ".npz")
        if os.path.exists(fn) and not args.force: log(f"  {sid}: ya existe, se omite"); continue
        R = run_subject(B, torch, sid, grid, args, log)
        np.savez_compressed(fn + ".tmp.npz", **R); os.replace(fn + ".tmp.npz", fn)
        log(f"{sid} listo: {int(R['n_trainings'][0])} entrenamientos en {float(R['seconds'][0]):.1f}s ({(time.time() - T0):.0f}s acumulados)")
    log(f"[nested] fin {time.time() - T0:.0f}s")


if __name__ == "__main__":
    main()
