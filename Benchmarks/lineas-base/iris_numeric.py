"""Modulo numerico de Iris (P0-4): extrae del demo SOLO las funciones numericas, sin bpy.

Se extrae el codigo fuente por AST desde Blender/demo_lattice_iris/neuro3d_iris_demo.py, de modo
que no hay copia manual que pueda divergir. Se ejecuta en un espacio de nombres con numpy y math.
"""
import ast, hashlib, math
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parents[2]
DEMO = REPO / "Blender" / "demo_lattice_iris" / "neuro3d_iris_demo.py"
CSV = REPO / "Blender" / "demo_lattice_iris" / "iris.csv"
SPECIES = ["setosa", "versicolor", "virginica"]
_FUNCS = ("lattice_xy", "modes", "model_U", "encode", "loss_acc", "train")
_CONSTS = ("LAM", "KW", "T", "R", "MIR", "K", "GAP", "RADIUS", "DET_R", "INPUTS", "REF", "CLASS_DET", "S2")


def _build():
    src = DEMO.read_text(encoding="utf-8")
    tree = ast.parse(src)
    ns = {"np": np, "math": math, "cmath": __import__("cmath")}
    picked = []
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id in _CONSTS for t in node.targets):
            picked.append(node)
        elif isinstance(node, ast.Assign) and any(isinstance(t, ast.Tuple) and any(isinstance(e, ast.Name) and e.id in _CONSTS for e in t.elts) for t in node.targets):
            picked.append(node)
        elif isinstance(node, ast.FunctionDef) and node.name in _FUNCS:
            picked.append(node)
    mod = ast.Module(body=picked, type_ignores=[])
    exec(compile(mod, str(DEMO), "exec"), ns)
    missing = [f for f in _FUNCS if f not in ns]
    if missing:
        raise RuntimeError("faltan funciones: %s" % missing)
    return ns


_NS = _build()
K = _NS["K"]
train = _NS["train"]
loss_acc = _NS["loss_acc"]
model_U = _NS["model_U"]
encode = _NS["encode"]


def demo_sha256():
    return hashlib.sha256(DEMO.read_bytes()).hexdigest()


def load_raw():
    rows = [l.strip().split(",") for l in CSV.read_text(encoding="utf-8").splitlines()[1:]]
    return np.array([[float(v) for v in r[:4]] for r in rows]), np.array([SPECIES.index(r[4]) for r in rows])
