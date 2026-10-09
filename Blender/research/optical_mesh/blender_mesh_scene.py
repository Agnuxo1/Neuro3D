"""OPT-007: the trained digits network LIVES in a Blender scene (Claude).

Each trainable weight is a delay-line object (cube) whose world Z offset from its
stored rest height IS the displacement d (Blender units). Inference reads
matrix_world of every delay-line object, converts d -> phase 2k*d, and propagates
the input fields through the Clements mesh (numpy; same optics as mesh.py and
mz_scene). Nothing is read from the training file at inference time except the
held-out digits and labels.

Modes:
  blender -b --python blender_mesh_scene.py -- verify OUT.blend   (build, infer, save, reopen, re-infer)
  blender    --python blender_mesh_scene.py -- live               (GUI: classify digits one by one)
"""

import colorsys
import json
import math
import sys
from pathlib import Path

import bpy
import numpy as np

HERE = Path("D:/PROJECTS/9_NEBULA_NEW/Blender/research/optical_mesh")
DATA = json.loads((HERE / "digits_mesh_seed0.json").read_text())
N, C, LAM = DATA["n"], DATA["classes"], DATA["lambda"]
K = 2 * math.pi / LAM
DX, DY = 0.5, 0.35
COL = "Neuro3D Optical Mesh"


def pairs(n):
    return [[(m, m + 1) for m in range(c % 2, n - 1, 2)] for c in range(n)]


def build():
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    col = bpy.data.collections.new(COL)
    bpy.context.scene.collection.children.link(col)
    bpy.context.scene["neuro3d_mesh"] = COL

    def cube(name, loc, size, role, idx, d):
        bpy.ops.mesh.primitive_cube_add(size=size, location=(loc[0], loc[1], d))
        o = bpy.context.active_object
        o.name = name
        for c in list(o.users_collection):
            c.objects.unlink(o)
        col.objects.link(o)
        o["neuro3d_role"], o["index"], o["rest_z"] = role, idx, 0.0
        return o

    k = 0
    for c, colpairs in enumerate(pairs(N)):
        for (m, _) in colpairs:
            x, y = 0.5 + c * DX, (m + 0.5) * DY
            cube(f"int {c}:{m}", (x, y), 0.12, "d_int", k, DATA["d_int"][k])
            cube(f"ext {c}:{m}", (x - 0.18, y), 0.07, "d_ext", k, DATA["d_ext"][k])
            k += 1
    for j in range(N):
        cube(f"out {j}", (0.5 + N * DX, j * DY), 0.1, "d_out", j, DATA["d_out"][j])
    return col


def read_geometry():
    """Weights = world Z of delay-line objects minus their rest height."""
    col = bpy.data.collections[bpy.context.scene["neuro3d_mesh"]]
    bpy.context.view_layer.update()
    arrays = {"d_int": np.zeros(N * (N - 1) // 2), "d_ext": np.zeros(N * (N - 1) // 2), "d_out": np.zeros(N)}
    for o in col.objects:
        role = o.get("neuro3d_role")
        if role in arrays:
            arrays[role][int(o["index"])] = o.matrix_world.translation.z - float(o["rest_z"])
    return arrays


def forward(amp, g):
    e = amp.astype(np.complex128).copy(); s2 = 1 / math.sqrt(2); idx = 0
    for colpairs in pairs(N):
        a = np.array([p[0] for p in colpairs]); b = np.array([p[1] for p in colpairs]); nc = len(colpairs)
        th = 2 * K * g["d_int"][idx: idx + nc]; ph = 2 * K * g["d_ext"][idx: idx + nc]; idx += nc
        x, y = e[:, a] * np.exp(1j * ph), e[:, b]
        u, v = s2 * (x + 1j * y), s2 * (1j * x + y); u = u * np.exp(1j * th)
        e[:, a], e[:, b] = s2 * (u + 1j * v), s2 * (1j * u + v)
    return np.abs(e * np.exp(1j * 2 * K * g["d_out"])) ** 2


def encode(X):
    a = np.clip(X, 0, None) + 1e-6
    return a / np.linalg.norm(a, axis=1, keepdims=True)


XVA, YVA = np.array(DATA["Xva"]), np.array(DATA["yva"])


def accuracy():
    p = forward(encode(XVA), read_geometry())
    return float((p[:, :C].argmax(1) == YVA).mean()), p


# ------------------------------------------------------------------ live GUI
LIVE = {"i": 0, "hits": 0}


def _mat_obj(name, loc, size, kind="sphere"):
    if kind == "sphere":
        bpy.ops.mesh.primitive_uv_sphere_add(radius=size, location=loc, segments=16, ring_count=8)
    else:
        bpy.ops.mesh.primitive_plane_add(size=size, location=loc)
    o = bpy.context.active_object; o.name = name
    return o


def live_setup():
    for r in range(4):
        for c in range(4):
            _mat_obj(f"px {r}{c}", (-2.6 + c * 0.32, 4.4 - r * 0.32, 0), 0.3, "plane")
    for j in range(C):
        _mat_obj(f"det {j}", (1.3 + N * DX, j * DY, 0), 0.13)
    curve = bpy.data.curves.new("readout", "FONT")
    t = bpy.data.objects.new("readout", curve); bpy.context.scene.collection.objects.link(t)
    t.location, t.scale = (-3.0, 6.2, 0), (0.28,) * 3
    for area in bpy.context.screen.areas:
        if area.type == "VIEW_3D":
            sp = area.spaces.active
            sp.shading.type, sp.shading.color_type = "SOLID", "OBJECT"
            sp.shading.background_type, sp.shading.background_color = "VIEWPORT", (0.02, 0.02, 0.03)
            sp.overlay.show_floor = sp.overlay.show_axis_x = sp.overlay.show_axis_y = False
            r3 = sp.region_3d; r3.view_perspective = "ORTHO"; r3.view_rotation = (1, 0, 0, 0)
            r3.view_location, r3.view_distance = (3.6, 3.2, 0), 13.0
    # colour delay lines by the phase they contribute (the weights, read from geometry)
    g = read_geometry()
    col = bpy.data.collections[COL]
    for o in col.objects:
        role = o.get("neuro3d_role")
        if role in g:
            ph = (2 * K * g[role][int(o["index"])]) % (2 * math.pi) / (2 * math.pi)
            r, gg, b = colorsys.hsv_to_rgb(ph, 0.8, 0.95); o.color = (r, gg, b, 1)


def live_tick():
    i = LIVE["i"] % len(YVA)
    x = XVA[i:i + 1]
    p = forward(encode(x), read_geometry())[0]           # inference from scene geometry NOW
    pred = int(p[:C].argmax()); LIVE["hits"] += int(pred == YVA[i]); LIVE["i"] += 1
    for r in range(4):
        for c in range(4):
            v = float(x[0, r * 4 + c]); bpy.data.objects[f"px {r}{c}"].color = (v, v, v, 1)
    top = max(p[:C].max(), 1e-9)
    for j in range(C):
        o = bpy.data.objects[f"det {j}"]; s = float(p[j] / top)
        o.color = ((1.0, 0.8, 0.2, 1) if j == pred else (0.15 + 0.6 * s, 0.25 + 0.5 * s, 0.9 * s + 0.1, 1))
        o.scale = (0.6 + 1.2 * s,) * 3
    bpy.data.objects["readout"].data.body = (
        f"Red optica en escena (256 lineas de retardo = pesos)\n"
        f"digito real = {YVA[i]}   prediccion = {pred}   {'OK' if pred == YVA[i] else 'FALLO'}\n"
        f"aciertos en vivo = {LIVE['hits']}/{LIVE['i']} = {LIVE['hits'] / LIVE['i']:.3f}")
    return 0.6


def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["live"]
    if args[0] == "verify":
        out = Path(args[1]); build()
        acc1, p1 = accuracy()
        bpy.ops.wm.save_as_mainfile(filepath=str(out), check_existing=False, compress=False)
        bpy.ops.wm.open_mainfile(filepath=str(out))
        acc2, p2 = accuracy()
        print("NEURO3D_MESH_VERIFY " + json.dumps({"acc_before_save": acc1, "acc_after_reopen": acc2,
              "max_power_diff": float(np.abs(p1 - p2).max()), "trained_val_acc": DATA["val_acc"]}), flush=True)
        return
    try:
        bpy.context.preferences.view.show_splash = False
    except Exception:
        pass
    build(); live_setup()
    bpy.app.timers.register(live_tick, first_interval=2.0)


main()
