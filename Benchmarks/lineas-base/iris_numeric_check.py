"""Comprueba que iris_numeric reproduce el demo original (bpy/mathutils falsos) con diferencia < 1e-12.

Particion historica: rng default_rng(0), permutation(150): test = idx[:30], train = idx[30:].
"""
import importlib.util, json, sys, time, types
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import iris_numeric as N


class _Any:
    """Objeto permisivo para stubs: atributos, llamadas y operadores devuelven otro _Any."""
    def __init__(self, *a, **k): pass
    def __getattr__(self, n): return _Any()
    def __call__(self, *a, **k): return _Any()
    def __getitem__(self, i): return _Any()
    def get(self, *a, **k): return None
    def __add__(self, o): return self
    __radd__ = __mul__ = __rmul__ = __sub__ = __rsub__ = __add__


def _stub_module(name):
    m = types.ModuleType(name)
    m.__getattr__ = lambda attr: _Any if not attr.startswith("__") else (_ for _ in ()).throw(AttributeError(attr))
    return m


def load_original():
    bpy = _stub_module("bpy")
    bpy.types = _stub_module("bpy.types"); bpy.props = _stub_module("bpy.props"); bpy.utils = _stub_module("bpy.utils")
    bpy.context = _Any(); bpy.data = types.SimpleNamespace(filepath=""); bpy.app = _Any(); bpy.ops = _Any()
    mu = types.ModuleType("mathutils"); mu.Vector = _Any
    sys.modules["bpy"], sys.modules["mathutils"] = bpy, mu
    spec = importlib.util.spec_from_file_location("neuro3d_iris_demo_orig", N.DEMO)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    out = {"demo_sha256": N.demo_sha256()}
    t0 = time.process_time()
    orig = load_original()
    out["stub_import_ok"] = True
    x, y = N.load_raw()
    idx = np.random.default_rng(0).permutation(150)
    te, tr = idx[:30], idx[30:]
    lo, hi = x[tr].min(0), x[tr].max(0)
    xs = (x - lo) / (hi - lo)
    xt, yt = xs[tr], y[tr]
    t = time.process_time(); p_orig = orig.train(xt, yt, seed=0, log=lambda *_: None); out["cpu_s_original"] = time.process_time() - t
    t = time.process_time(); p_num = N.train(xt, yt, seed=0, log=lambda *_: None); out["cpu_s_numeric"] = time.process_time() - t
    l_o, a_o = orig.loss_acc(p_orig, xt, yt); l_n, a_n = N.loss_acc(p_num, xt, yt)
    out.update(loss_original=float(l_o), loss_numeric=float(l_n), loss_abs_diff=abs(float(l_o) - float(l_n)),
               params_max_abs_diff=float(np.max(np.abs(p_orig - p_num))), train_acc=float(a_n),
               test_acc=float(N.loss_acc(p_num, xs[te], y[te])[1]))
    out["equivalent_below_1e-12"] = bool(out["loss_abs_diff"] < 1e-12 and out["params_max_abs_diff"] < 1e-12)
    # comparacion con el estado entrenado guardado (si es la misma particion y escalado)
    st = json.loads((N.DEMO.parent / "trained_lattice.json").read_text())
    same_split = st["train_idx"] == [int(i) for i in tr] and np.allclose(st["scaler_lo"], lo) and np.allclose(st["scaler_hi"], hi)
    saved_p = np.concatenate([st["theta"], [st["ref"], st["logt"]]])
    out["trained_lattice_same_split_and_scaler"] = bool(same_split)
    out["trained_lattice_params_max_abs_diff"] = float(np.max(np.abs(saved_p - p_num)))
    out["trained_lattice_saved_train_acc"] = st["train_acc_model"]
    out["trained_lattice_saved_test_acc"] = st["test_acc_model"]
    out["trained_lattice_loss_of_saved_params"] = float(N.loss_acc(saved_p, xt, yt)[0])
    out["note_published_0.309707"] = ("La cifra 0,309707 pertenece al protocolo de geometria capturada (Wine/Iris con 61 estados "
                                      "auditados), no a train() del demo; no hay cifra de perdida publicada de train() en el repo para comparar.")
    out["cpu_s_total"] = time.process_time() - t0
    (HERE / "resultados").mkdir(exist_ok=True)
    (HERE / "resultados" / "iris_numeric_check.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))
    return 0 if out["equivalent_below_1e-12"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
