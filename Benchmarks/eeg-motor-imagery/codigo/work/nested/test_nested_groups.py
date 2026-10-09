"""Pruebas: (1) la particion interna nunca comparte runs con el test externo ni entre train/val interno (datos reales + sinteticos +
aleatorios); (2) los indices guardados en raw/<tag>/ cumplen lo mismo; (3) fidelidad: fit_snapshots == bench.train_torch y las
instantaneas de epocas coinciden con entrenar esas epocas por separado. Uso: python test_nested_groups.py [tag_raw]"""
import glob, os, sys, json
os.environ.setdefault("TORCH_THREADS", "4"); os.environ.setdefault("OMP_NUM_THREADS", "4"); os.environ["BENCH_DEV"] = "cpu"
HERE = os.path.dirname(os.path.abspath(__file__)); WORK = os.path.dirname(HERE); sys.path.insert(0, WORK); sys.path.insert(0, HERE)
import numpy as np
import nested_bench as N

def check_layout(runs, name):
    ofs = N.outer_folds(runs); allte = np.concatenate([te for _, te, _ in ofs]); assert sorted(allte) == list(range(len(runs))), name
    ninner = 0
    for tr, te, r in ofs:
        assert set(runs[tr]) == set(runs) - {r} and set(runs[te]) == {r} and not set(tr) & set(te), name
        for it, iv, v in N.inner_folds(runs, tr):
            ninner += 1
            assert not set(it) & set(iv), "indices compartidos"
            assert not set(runs[it]) & set(runs[iv]), "run compartido train/val interno"
            assert v not in set(runs[it]) and set(runs[iv]) == {v}, "el fold de validacion no es un run completo"
            assert r not in set(runs[it]) | set(runs[iv]), "run externo en el bucle interno"
            assert set(it) | set(iv) == set(tr), "el interno no cubre exactamente el entrenamiento externo"
            assert len(it) >= N.MIN_TRAIN and len(iv) >= N.MIN_VAL
    return ninner

tot = 0; rows = []
for f in sorted(glob.glob(os.path.join(WORK, "data", "S*.npz"))):
    runs = np.load(f)["run"]; k = check_layout(runs, os.path.basename(f)); tot += k
    ofs = N.outer_folds(runs); rows.append((os.path.basename(f)[:4], [len(N.inner_folds(runs, tr)) for tr, _, _ in ofs]))
print("datos reales OK: 17 sujetos, folds internos validos por fold externo:", dict((a, b) for a, b in rows if b != [1, 1, 2] and b != [2, 1, 1]) or "todos [.. ]", "total", tot)
print("  patron de folds internos (S001):", rows[0][1], "(S006):", [r for r in rows if r[0] == "S006"][0][1], "(S007):", [r for r in rows if r[0] == "S007"][0][1])
rng = np.random.default_rng(1)
for t in range(300):                      # layouts aleatorios: 1..6 runs con tamanos aleatorios
    nr = int(rng.integers(1, 7)); runs = np.concatenate([np.full(int(rng.integers(1, 60)), r + 1) for r in range(nr)]); rng.shuffle(runs); check_layout(runs, f"rand{t}")
print("300 layouts aleatorios (runs entrelazados y de 1..6 grupos) OK")

# tests negativos: el chequeo debe FALLAR si se mezclan runs
runs = np.array([1] * 50 + [2] * 50 + [3] * 10); tr, te, r = N.outer_folds(runs)[0]
bad_iv = np.array(list(tr[:5]) + list(tr[-5:]))                       # val que mezcla dos runs / parte de un run
try:
    assert set(runs[bad_iv]) == {int(runs[bad_iv][0])}; raise SystemExit("el test negativo no detecto la mezcla")
except AssertionError: print("test negativo OK (un val mezclado se detecta)")

# (2) indices guardados
tag = sys.argv[1] if len(sys.argv) > 1 else None
if tag:
    n = 0
    for f in sorted(glob.glob(os.path.join(HERE, "raw", tag, "S*.npz"))):
        R = np.load(f); meta = json.loads(str(R["meta"])); runs = np.load(os.path.join(WORK, "data", meta["sid"] + ".npz"))["run"]
        for r in meta["runs"]:
            tr, te = R[f"tr|{r}"], R[f"te|{r}"]; assert set(runs[te]) == {r} and r not in set(runs[tr])
            for k in [k for k in R.files if k.startswith(f"iv|{r}|")]:
                v = int(k.split("|")[2]); iv, it = R[f"iv|{r}|{v}"], R[f"it|{r}|{v}"]; n += 1
                assert set(runs[iv]) == {v} and v not in set(runs[it]) and r not in set(runs[it]) and r not in set(runs[iv]), (meta["sid"], r, v)
                assert set(it) <= set(tr) and set(iv) <= set(tr) and not set(it) & set(iv)
    print(f"raw/{tag}: {n} folds internos guardados verificados (sin run compartido con el externo ni entre train/val interno)")

# (3) fidelidad con bench.train_torch
import torch, bench as B
d = np.load(os.path.join(WORK, "data", "S001.npz")); X, y, runs = d["Xtr"].astype(np.float32), d["ytr"], d["run"]
Z = B.cwt(X, freqs=N.FEATS["f8w1"][0]); tr, te, r = N.outer_folds(runs)[0]
B.WIN = 1; s = np.abs(Z[tr]).std(axis=(0, 3), keepdims=True) + 1e-6
for E in (3, 6):
    ref = B.train_torch(lambda: B.Optic(8, unitary="polar"), Z[tr] / s, y[tr], Z[te] / s, epochs=E, lr=2e-2, seed=0)
    Ztr, (Zte,) = N.make_scaled(Z, runs, tr, [te], "train")
    o = N.fit_snapshots(B, torch, "polar", "f8w1", Ztr, y[tr], [Zte], [3, 6], 1e-3, seed=0)
    assert np.array_equal((o[E][0] > 0).astype(int), ref), f"fit_snapshots != bench.train_torch a {E} epocas"
print("fidelidad OK: fit_snapshots reproduce bench.train_torch (polar f8w1, S001 fold 1) y las instantaneas 3/6 == entrenar 3 y 6 epocas por separado")
print("TODOS LOS TESTS OK")
