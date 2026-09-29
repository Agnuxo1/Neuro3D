"""Neuro3D - optical lattice classifier that lives in a Blender scene (Iris flowers).

Everything runs inside Blender (bpy + the numpy bundled with Blender):
  * the network IS the scene: 16 Mach-Zehnder cells (beam splitters, mirrors, a movable roof
    delay line per cell) tiled on a lattice with 8 optical modes;
  * training (numpy, inside Blender) only adjusts the physical roof-delay offsets d[i,j];
  * inference traces the scene with ``scene.ray_cast`` from every source, sums the complex
    field of every ray path at each detector (coherent path sum) and the brightest of the
    three class detectors is the prediction. No weight matrix is read back from Python;
  * the render (EEVEE) shows every beam with an emission proportional to its computed power.

Honest scope: Blender's ray tracer supplies hits and path lengths; the wave interference is
summed in Blender's Python from those lengths. This is a simulation of a free-space optical
network, not a physical photonic measurement.

Usage (headless):
  blender -b --factory-startup --python neuro3d_iris_demo.py -- --train --verify --render out_dir
Usage (GUI): open Blender, Scripting tab, run this file -> "Neuro3D" tab in the 3D view sidebar.
"""
import cmath, json, math, os, sys, time

import bpy
import numpy as np
from mathutils import Vector

def _demo_dir():
    cands = []
    try: cands.append(os.path.dirname(os.path.abspath(__file__)))
    except NameError: pass
    if bpy.data.filepath: cands += [os.path.dirname(bpy.data.filepath), os.path.dirname(os.path.dirname(bpy.data.filepath))]
    cands.append(os.getcwd())
    for c in cands:
        if os.path.exists(os.path.join(c, "iris.csv")): return c
    return cands[0]


HERE = _demo_dir()
LAM = 0.1                                   # wavelength (Blender units)
KW = 2 * math.pi / LAM
T, R, MIR = 1 / math.sqrt(2), 1j / math.sqrt(2), -1.0   # beam splitter t, r; mirror reflection
K = 4                                       # K x K cells -> 2K modes
S2 = 1 / math.sqrt(2)
N_A, N_B = (S2, -S2, 0.0), (S2, S2, 0.0)
CELL = {"bs1": ((0.0, 0.0), N_A, "bs"), "r1": ((2.0, 0.0), N_A, "mirror"), "r2": ((2.0, 0.5), N_B, "mirror"),
        "f1": ((1.0, 0.5), N_B, "mirror"), "m2": ((0.0, 2.0), N_A, "mirror"), "bs2": ((1.0, 2.0), N_A, "bs")}
RADIUS, DET_R, GAP = 0.2, 0.15, 1.0
INPUTS = ["r0", "r1", "c0", "c1"]           # the four Iris features
REF = "c2"                                  # constant reference beam (optical bias)
CLASS_DET = ["R0", "R1", "R2"]              # setosa, versicolor, virginica
SPECIES = ["setosa", "versicolor", "virginica"]
PALETTE = {"setosa": (0.20, 0.85, 1.00), "versicolor": (1.00, 0.35, 0.85), "virginica": (1.00, 0.78, 0.25)}


# ----------------------------------------------------------------------------------------------
# lattice geometry
def lattice_xy():
    X, Y = [0.0], [0.0]
    for i in range(1, K):
        X.append(X[-1] + 4.0 + 0.0137 * i + 0.0031 * i * i)
        Y.append(Y[-1] + 4.0 + 0.0211 * i + 0.0017 * i * i)
    return X, Y


def origin(i, j):
    X, Y = lattice_xy(); return X[i] + j, Y[j] + 2 * i


def modes():
    ins = [f"r{j}" for j in range(K)] + [f"c{i}" for i in range(K)]
    outs = [f"R{j}" for j in range(K)] + [f"C{i}" for i in range(K)]
    return ins, outs


def source_pose(sid):
    X, Y = lattice_xy(); idx = int(sid[1:])
    if sid[0] == "r": ox, oy = origin(0, idx); return (ox - GAP, oy, 0.0), (1.0, 0.0, 0.0)
    ox, oy = origin(idx, 0); return (ox, oy - GAP, 0.0), (0.0, 1.0, 0.0)


def detector_pose(did):
    idx = int(did[1:])
    if did[0] == "R": ox, oy = origin(K - 1, idx); return (ox + 1 + GAP, oy + 2, 0.0), (1.0, 0.0, 0.0)
    ox, oy = origin(idx, K - 1); return (ox + 1, oy + 2 + GAP, 0.0), (0.0, 1.0, 0.0)


# screen layout: the lattice diagonal is drawn horizontally
VIEW_A = math.atan2(21.0, 17.0)                     # angle of the lattice diagonal
EX = Vector((math.cos(VIEW_A), math.sin(VIEW_A), 0)); EY = Vector((-math.sin(VIEW_A), math.cos(VIEW_A), 0))
CENTER = Vector((8.3, 10.0, 0))


def world(u, v, z=0.0):
    return CENTER + u * EX + v * EY + Vector((0, 0, z))


FEATURE_NAMES = {"r0": "sepal length", "r1": "sepal width", "c0": "petal length", "c1": "petal width", "c2": "reference"}


# ----------------------------------------------------------------------------------------------
# numpy model used ONLY for training (closed-form lengths of the same geometry)
def model_U(d):
    X, Y = lattice_xy(); ins, outs = modes(); n = 2 * K
    ph = lambda L: np.exp(1j * KW * L)
    ax = {(i, j): np.zeros(n, complex) for i in range(K) for j in range(K)}; ay = {k: v.copy() for k, v in ax.items()}
    for j in range(K): ax[(0, j)][j] = ph(GAP)
    for i in range(K): ay[(i, 0)][K + i] = ph(GAP)
    U = np.zeros((n, n), complex)
    for i in range(K):
        for j in range(K):
            a1 = (T * ax[(i, j)] + R * ay[(i, j)]) * MIR ** 3 * ph(5.0 + 2 * d[i, j])
            a2 = (R * ax[(i, j)] + T * ay[(i, j)]) * MIR * ph(3.0)
            ox, oy = R * a1 + T * a2, T * a1 + R * a2
            if i + 1 < K: ax[(i + 1, j)] += ox * ph(X[i + 1] - X[i] - 1.0)
            else: U[j] = ox * ph(GAP)
            if j + 1 < K: ay[(i, j + 1)] += oy * ph(Y[j + 1] - Y[j] - 2.0)
            else: U[K + i] = oy * ph(GAP)
    return U                                           # U[out, in]


def encode(x, ref):
    """x: (n,4) features in [0,1] -> (n,8) input amplitudes, normalised to unit power."""
    ins, _ = modes(); a = np.zeros((len(x), 2 * K), complex)
    for c, sid in enumerate(INPUTS): a[:, ins.index(sid)] = x[:, c]
    a[:, ins.index(REF)] = ref
    return a / np.sqrt((np.abs(a) ** 2).sum(1, keepdims=True))


def load_raw():
    rows = [l.strip().split(",") for l in open(os.path.join(HERE, "iris.csv")).read().splitlines()[1:]]
    return np.array([[float(v) for v in r[:4]] for r in rows]), np.array([SPECIES.index(r[4]) for r in rows])


def split():
    rng = np.random.default_rng(0); idx = rng.permutation(150); return idx[30:], idx[:30]   # train, fixed hold-out


def load_iris(scaler=None):
    """Features scaled with a min/max fitted on the TRAIN rows only (persisted with the weights)."""
    x, y = load_raw()
    if scaler is None:
        st_path = os.path.join(HERE, "trained_lattice.json")
        if os.path.exists(st_path) and "scaler_lo" in json.load(open(st_path)):
            st = json.load(open(st_path)); scaler = (np.array(st["scaler_lo"]), np.array(st["scaler_hi"]))
        else:
            tr, _ = split(); scaler = (x[tr].min(0), x[tr].max(0))
    lo, hi = scaler; return (x - lo) / (hi - lo), y, scaler


def loss_acc(p, x, y):
    theta, ref, logt = p[:16].reshape(K, K), p[16], p[17]
    U = model_U(theta * LAM / (4 * math.pi)); _, outs = modes()
    I = np.abs(encode(x, ref) @ U.T) ** 2
    z = I[:, [outs.index(c) for c in CLASS_DET]] * math.exp(logt)
    z = z - z.max(1, keepdims=True); lp = z - np.log(np.exp(z).sum(1, keepdims=True))
    return -lp[np.arange(len(y)), y].mean(), (z.argmax(1) == y).mean()


def train(x, y, steps=500, seed=0, restarts=4, log=print):
    """Adam on central finite differences (18 physical/optical parameters). Best restart by TRAIN loss."""
    best = None
    for r in range(restarts):
        rng = np.random.default_rng(seed + r)
        p = np.concatenate([rng.uniform(0, 2 * math.pi, 16), [0.5, 2.0]]); m = np.zeros_like(p); v = np.zeros_like(p)
        for t in range(1, steps + 1):
            g = np.zeros_like(p)
            for k in range(len(p)):
                e = np.zeros_like(p); e[k] = 1e-5
                g[k] = (loss_acc(p + e, x, y)[0] - loss_acc(p - e, x, y)[0]) / 2e-5
            m = 0.9 * m + 0.1 * g; v = 0.999 * v + 0.001 * g * g
            p -= 0.05 * (m / (1 - 0.9 ** t)) / (np.sqrt(v / (1 - 0.999 ** t)) + 1e-8)
        L, A = loss_acc(p, x, y); log(f"restart {r}: train loss {L:.4f} acc {A:.3f}")
        if best is None or L < best[0]: best = (L, p.copy())
    return best[1]


# ----------------------------------------------------------------------------------------------
# scene
def mat(name, color, metallic=0.0, rough=0.3, emit=0.0, alpha=1.0, transmission=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*color, 1); b.inputs["Metallic"].default_value = metallic
    b.inputs["Roughness"].default_value = rough; b.inputs["Alpha"].default_value = alpha
    b.inputs["Transmission Weight"].default_value = transmission
    b.inputs["Emission Color"].default_value = (*color, 1); b.inputs["Emission Strength"].default_value = emit
    return m


def disk(name, pos, normal, radius, kind, material):
    me = bpy.data.meshes.new(name); verts = [(0, 0, 0)] + [(radius * math.cos(a), radius * math.sin(a), 0)
                                                        for a in np.linspace(0, 2 * math.pi, 64, endpoint=False)]
    me.from_pydata(verts, [], [(0, k + 1, (k + 1) % 64 + 1) for k in range(64)]); me.update()
    ob = bpy.data.objects.new(name, me); bpy.data.collections["Optics"].objects.link(ob)
    ob.rotation_mode = "QUATERNION"; ob.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(Vector(normal))
    ob.location = pos; ob["kind"] = kind; ob.data.materials.append(material)
    return ob


def text(name, body, loc, size, color, coll="Labels", emit=3.0, rot_z=0.0):
    cu = bpy.data.curves.new(name, "FONT"); cu.body = body; cu.size = size; cu.align_x = "CENTER"
    ob = bpy.data.objects.new(name, cu); bpy.data.collections[coll].objects.link(ob)
    ob.location = loc; ob.rotation_euler = (0, 0, rot_z); ob.data.materials.append(mat("txt_" + name, color, emit=emit))
    return ob


def build_scene(theta, ref):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    for c in ("Optics", "Beams", "Labels", "Stage"):
        bpy.context.scene.collection.children.link(bpy.data.collections.new(c))
    m_mirror = mat("mirror", (0.85, 0.88, 0.95), metallic=1.0, rough=0.08)
    m_bs = mat("beamsplitter", (0.55, 0.9, 1.0), rough=0.02, emit=0.6, alpha=0.55, transmission=0.6)
    d = theta * LAM / (4 * math.pi)
    for i in range(K):
        for j in range(K):
            ox, oy = origin(i, j)
            for nm, ((lx, ly), n, kind) in CELL.items():
                x = ox + lx + (d[i, j] if nm in ("r1", "r2") else 0.0)
                disk(f"c{i}{j}.{nm}", (x, oy + ly, 0.0), n, RADIUS, kind, m_bs if kind == "bs" else m_mirror)
    ins, outs = modes()
    for did in outs:
        p, n = detector_pose(did); col = PALETTE[SPECIES[CLASS_DET.index(did)]] if did in CLASS_DET else (0.5, 0.5, 0.6)
        disk(f"det.{did}", p, n, DET_R, "det", mat(f"det_{did}", col, emit=0.2))
    srcs = []
    for sid in INPUTS + [REF]:
        p, dvec = source_pose(sid); srcs.append({"id": sid, "p": p, "d": dvec})
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=p)
        o = bpy.context.active_object; o.name = f"src.{sid}"
        for c in o.users_collection: c.objects.unlink(o)
        bpy.data.collections["Labels"].objects.link(o)          # emitters are not ray targets
        o.data.materials.append(mat(f"src_{sid}", (1.0, 1.0, 1.0) if sid == REF else (0.4, 1.0, 0.6), emit=4.0))
    sc["sources"] = json.dumps(srcs); sc["ref"] = float(ref); sc["theta"] = json.dumps(theta.tolist())
    bpy.context.scene.collection.children.link(bpy.data.collections.new("Decor"))
    m_plate_m = mat("plate_mirror", (0.8, 0.84, 0.92), metallic=1.0, rough=0.12)
    m_plate_b = mat("plate_bs", (0.3, 0.85, 1.0), rough=0.05, emit=1.2, alpha=0.8)
    m_post = mat("post", (0.05, 0.06, 0.08), metallic=0.8, rough=0.3)
    for ob in list(bpy.data.collections["Optics"].objects):
        n = Vector(ob.rotation_quaternion @ Vector((0, 0, 1))); t = Vector((0, 0, 1)).cross(n).normalized()
        kind = ob["kind"]; w, h = (0.46, 0.34) if kind != "det" else (0.36, 0.5)
        bpy.ops.mesh.primitive_cube_add(size=1, location=ob.location)
        pl = bpy.context.active_object; pl.name = "plate." + ob.name
        for c in pl.users_collection: c.objects.unlink(pl)
        bpy.data.collections["Decor"].objects.link(pl)
        pl.rotation_mode = "QUATERNION"; pl.rotation_quaternion = Vector((1, 0, 0)).rotation_difference(t)
        pl.scale = (w, 0.035, h)
        pl.data.materials.append(bpy.data.materials[f"det_{ob.name[4:]}"] if kind == "det" else (m_plate_b if kind == "bs" else m_plate_m))
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.09, depth=0.3, location=ob.location - Vector((0, 0, 0.3)))
        po = bpy.context.active_object; po.name = "post." + ob.name
        for c in po.users_collection: c.objects.unlink(po)
        bpy.data.collections["Decor"].objects.link(po); po.data.materials.append(m_post)
    # stage
    bpy.ops.mesh.primitive_plane_add(size=60, location=(8, 9, -0.35)); pl = bpy.context.active_object; pl.name = "stage"
    for c in pl.users_collection: c.objects.unlink(pl)
    bpy.data.collections["Stage"].objects.link(pl); pl.data.materials.append(mat("stage", (0.015, 0.018, 0.03), rough=0.25, metallic=0.4))
    for ob in bpy.data.collections["Stage"].objects: ob["kind"] = "stage"
    return sc


TRACE_INFO = {"escape": 0.0}   # incoherent escaped power of the last trace (0 when every ray reaches a detector)
SEG_L = {}          # segment -> optical path length at its start (filled by trace, used by the live animation)


def _set_excluded(flag, previous=None):
    """flag=True: exclude every non-Optics collection and return the previous flags; flag=False: restore them."""
    prev = {}
    for lc in bpy.context.view_layer.layer_collection.children:
        if lc.name == "Optics": continue
        prev[lc.name] = lc.exclude
        lc.exclude = True if flag else (previous or {}).get(lc.name, False)
    return prev


def trace(amps):
    """Coherent path sum with scene.ray_cast. amps: {source_id: complex}. Only the Optics collection is
    visible to the rays (decor, beams and labels are excluded from the depsgraph while tracing).
    Returns detector fields, per-segment coherent field (for rendering) and the number of casts."""
    sc = bpy.context.scene; prev = _set_excluded(True); bpy.context.view_layer.update()
    try:
        dg = bpy.context.evaluated_depsgraph_get(); det, seg, casts = {}, {}, 0; SEG_L.clear(); TRACE_INFO["escape"] = 0.0
        for s in json.loads(sc["sources"]):
            a0 = amps.get(s["id"], 0)
            if a0 == 0: continue
            stack = [(Vector(s["p"]), Vector(s["d"]), complex(a0), 0.0, "src." + s["id"], 0)]
            while stack:
                o, d, amp, L, frm, depth = stack.pop()
                if depth > 64: raise RuntimeError("runaway path")
                hit, loc, nrm, _, ob, _ = sc.ray_cast(dg, o + d * 1e-5, d); casts += 1
                if hit and ob.get("kind") not in ("bs", "mirror", "det"): raise RuntimeError(f"non-optical hit {ob.name}")
                end = loc if hit else o + d * 3.0
                key = (frm, ob.name if hit else "escape", tuple(round(c, 4) for c in o), tuple(round(c, 4) for c in end))
                seg[key] = seg.get(key, 0) + amp * cmath.exp(1j * KW * L)
                SEG_L[key] = min(SEG_L.get(key, 1e9), L)
                if not hit:
                    TRACE_INFO["escape"] += abs(amp) ** 2; continue
                L2 = L + (loc - o).length; kind = ob["kind"]
                if kind == "det":
                    det[ob.name[4:]] = det.get(ob.name[4:], 0) + amp * cmath.exp(1j * KW * L2); continue
                n = nrm.normalized(); rd = (d - 2 * d.dot(n) * n).normalized()
                if kind == "mirror": stack.append((loc, rd, amp * MIR, L2, ob.name, depth + 1))
                else:
                    stack.append((loc, d.copy(), amp * T, L2, ob.name, depth + 1))
                    stack.append((loc, rd, amp * R, L2, ob.name, depth + 1))
        return det, seg, casts
    finally:
        _set_excluded(False, prev)


def classify(x_row):
    ref = bpy.context.scene["ref"]; a = encode(x_row[None], ref)[0]; ins, _ = modes()
    amps = {sid: a[ins.index(sid)] for sid in INPUTS + [REF]}
    det, seg, casts = trace(amps)
    P = [abs(det.get(c, 0)) ** 2 for c in CLASS_DET]
    return int(np.argmax(P)), P, det, seg, casts


def show(seg, P, pred, truth=None, x_row=None, hidden=False):
    """Beams as emissive tubes; radius and brightness follow the coherent power on each segment."""
    for ob in list(bpy.data.collections["Beams"].objects): bpy.data.objects.remove(ob, do_unlink=True)
    for ob in list(bpy.data.collections["Labels"].objects):
        if ob.name.startswith("hud."): bpy.data.objects.remove(ob, do_unlink=True)
    hot = Vector(PALETTE[SPECIES[pred]]); cold = Vector((0.10, 0.35, 1.0))
    for n, (key, f) in enumerate(seg.items()):
        pw = abs(f) ** 2
        if pw < 1e-3: continue
        a, b = Vector(key[2]), Vector(key[3]); L = (b - a).length
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.012 + 0.045 * math.sqrt(pw), depth=L, location=(a + b) / 2)
        c = bpy.context.active_object; c.name = f"beam.{n}"
        c.rotation_mode = "QUATERNION"; c.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(b - a)
        for cc in c.users_collection: cc.objects.unlink(c)
        bpy.data.collections["Beams"].objects.link(c)
        q = min(1.0, math.sqrt(pw) * 1.6); col = cold.lerp(hot, q)
        if key[1] == "escape": col = Vector((1.0, 0.25, 0.1))
        c.data.materials.append(mat(f"beam_{n}", tuple(col), emit=1.5 + 22.0 * pw))
        c["L0"] = float(SEG_L.get(key, 0.0)); c["L1"] = c["L0"] + L
        if hidden: c.hide_viewport = c.hide_render = True
    tot = sum(P) + 1e-12
    for k, did in enumerate(CLASS_DET):
        b = bpy.data.materials[f"det_{did}"].node_tree.nodes["Principled BSDF"]
        b.inputs["Emission Strength"].default_value = 0.3 + (45.0 if k == pred else 6.0) * P[k] / tot
    rz = VIEW_A
    text("hud.title", "NEURO3D", world(0, 10.2), 1.05, (0.9, 0.97, 1.0), emit=3.0, rot_z=rz)
    text("hud.sub", "an optical neural network that lives in a Blender scene", world(0, 9.3), 0.42, (0.6, 0.72, 0.9), emit=1.6, rot_z=rz)
    text("hud.foot", "16 Mach-Zehnder cells  ·  8 optical modes  ·  trained mirror delays  ·  inference = ray tracing the scene",
         world(0, -9.6), 0.34, (0.45, 0.55, 0.72), emit=1.2, rot_z=rz)
    msg = SPECIES[pred].upper()
    if truth is not None: msg += "   ✓" if truth == pred else f"   ✗  (true: {SPECIES[truth]})"
    text("hud.pred", msg, world(10.5, -7.6), 0.62, PALETTE[SPECIES[pred]], emit=5.0, rot_z=rz)
    text("hud.predlbl", "prediction", world(10.5, -6.8), 0.3, (0.6, 0.7, 0.85), emit=1.4, rot_z=rz)
    for k, did in enumerate(CLASS_DET):
        p, _ = detector_pose(did)
        text(f"hud.det{k}", f"{SPECIES[k]}  {100 * P[k] / tot:4.1f}%", Vector(p) + 0.9 * EX - 0.35 * EY, 0.3,
             PALETTE[SPECIES[k]], emit=2.8 if k == pred else 1.2, rot_z=rz)
    if x_row is not None:
        for c, sid in enumerate(INPUTS + [REF]):
            p, dvec = source_pose(sid); val = float(x_row[c]) if c < 4 else float(bpy.context.scene["ref"])
            base = Vector(p) - 0.55 * Vector(dvec)
            bpy.ops.mesh.primitive_cube_add(size=1, location=base + Vector((0, 0, 0.05 + 0.6 * val)))
            bar = bpy.context.active_object; bar.name = f"hud.bar.{sid}"; bar.scale = (0.14, 0.14, 1.2 * val + 0.02)
            for cc in bar.users_collection: cc.objects.unlink(bar)
            bpy.data.collections["Labels"].objects.link(bar)
            bar.data.materials.append(mat(f"bar_{sid}", (0.4, 1.0, 0.6) if sid != REF else (1, 1, 1), emit=2.5))
            text(f"hud.in.{sid}", f"{FEATURE_NAMES[sid]} {val:.2f}", base - 0.75 * EY, 0.24, (0.55, 0.9, 0.7), emit=1.4, rot_z=rz)


def setup_render(res=(1920, 1080)):
    sc = bpy.context.scene; sc.render.engine = "BLENDER_EEVEE_NEXT"
    sc.render.resolution_x, sc.render.resolution_y = res
    try: sc.eevee.taa_render_samples = 64
    except Exception: pass
    w = bpy.data.worlds.new("world"); sc.world = w; w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (0.003, 0.005, 0.012, 1)
    cam = bpy.data.objects.new("camera", bpy.data.cameras.new("camera")); sc.collection.objects.link(cam); sc.camera = cam
    tilt = math.radians(24); dist = 36.0
    cam.location = world(0, -dist * math.sin(tilt) - 0.6, dist * math.cos(tilt))
    cam.rotation_mode = "XYZ"; cam.rotation_euler = (tilt, 0, VIEW_A)
    cam.data.lens = 32; cam.data.sensor_width = 36
    key = bpy.data.objects.new("key", bpy.data.lights.new("key", "AREA")); sc.collection.objects.link(key)
    key.location = world(0, 0, 16); key.data.energy = 900; key.data.size = 24; key.data.color = (0.65, 0.75, 1.0)
    sc.view_settings.view_transform = "AgX"
    try: sc.view_settings.look = "AgX - Punchy"
    except Exception: pass
    sc.use_nodes = True; nt = sc.node_tree; nt.nodes.clear()
    rl = nt.nodes.new("CompositorNodeRLayers"); gl = nt.nodes.new("CompositorNodeGlare"); out = nt.nodes.new("CompositorNodeComposite")
    gl.glare_type = "FOG_GLOW"
    try: gl.quality = "HIGH"
    except Exception: pass
    for attr, val in (("threshold", 0.5), ("size", 8)):
        try: setattr(gl, attr, val)
        except Exception: pass
    nt.links.new(rl.outputs["Image"], gl.inputs["Image"]); nt.links.new(gl.outputs["Image"], out.inputs["Image"])


# ----------------------------------------------------------------------------------------------
# interactive panel (GUI): 3D View > Sidebar > Neuro3D
class NEURO3D_OT_classify(bpy.types.Operator):
    bl_idname = "neuro3d.classify_flower"; bl_label = "Classify flower (ray trace)"
    step: bpy.props.IntProperty(default=1)

    def execute(self, context):
        x, y, _ = load_iris(); sc = context.scene
        sc["flower"] = int(sc.get("flower", 0) + self.step) % len(y); n = sc["flower"]
        pred, P, _, seg, casts = classify(x[n]); show(seg, P, pred, truth=int(y[n]), x_row=x[n])
        self.report({"INFO"}, f"flower #{n}: {SPECIES[pred]} (true {SPECIES[y[n]]}), {casts} rays"); return {"FINISHED"}


class NEURO3D_OT_build(bpy.types.Operator):
    bl_idname = "neuro3d.build_trained"; bl_label = "Build trained lattice"

    def execute(self, context):
        st = json.load(open(os.path.join(HERE, "trained_lattice.json")))
        build_scene(np.array(st["theta"]).reshape(K, K), st["ref"]); setup_render(); return {"FINISHED"}


# ----------------------------------------------------------------------------------------------
# live mode (GUI): flowers are traced one after another; light is revealed as it propagates
LIVE = {"on": False, "phase": "trace", "front": 0.0, "hold": 0, "P": None, "pred": 0}
LIGHT_SPEED = 1.2          # BU revealed per timer tick (visual only)


def _dim_detectors():
    for did in CLASS_DET:
        bpy.data.materials[f"det_{did}"].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 0.3


def _live_tick():
    if not LIVE["on"]: return None
    sc = bpy.context.scene; x, y, _ = load_iris()
    if LIVE["phase"] == "trace":
        sc["flower"] = int(sc.get("flower", -1) + 1) % len(y); n = sc["flower"]
        pred, P, _, seg, casts = classify(x[n])
        show(seg, P, pred, truth=int(y[n]), x_row=x[n], hidden=True); _dim_detectors()
        for ob in bpy.data.collections["Labels"].objects:
            if ob.name.startswith(("hud.pred", "hud.det")): ob.hide_viewport = ob.hide_render = True
        LIVE.update(phase="propagate", front=0.0, P=P, pred=pred, casts=casts); return 0.05
    if LIVE["phase"] == "propagate":
        LIVE["front"] += LIGHT_SPEED; left = 0
        for ob in bpy.data.collections["Beams"].objects:
            if ob.hide_viewport and ob["L0"] <= LIVE["front"]: ob.hide_viewport = ob.hide_render = False
            if ob.hide_viewport: left += 1
        if left == 0:
            P, pred = LIVE["P"], LIVE["pred"]; tot = sum(P) + 1e-12
            for k, did in enumerate(CLASS_DET):
                b = bpy.data.materials[f"det_{did}"].node_tree.nodes["Principled BSDF"]
                b.inputs["Emission Strength"].default_value = 0.3 + (45.0 if k == pred else 6.0) * P[k] / tot
            for ob in bpy.data.collections["Labels"].objects:
                if ob.name.startswith(("hud.pred", "hud.det")): ob.hide_viewport = ob.hide_render = False
            LIVE["phase"] = "hold"; LIVE["hold"] = 0
        return 0.05
    LIVE["hold"] += 1
    if LIVE["hold"] > 30: LIVE["phase"] = "trace"
    return 0.05


class NEURO3D_OT_live(bpy.types.Operator):
    bl_idname = "neuro3d.live"; bl_label = "Play / pause live network"

    def execute(self, context):
        LIVE["on"] = not LIVE["on"]; LIVE["phase"] = "trace"
        if LIVE["on"] and not bpy.app.timers.is_registered(_live_tick): bpy.app.timers.register(_live_tick, first_interval=0.1)
        return {"FINISHED"}


class NEURO3D_PT_panel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"; bl_region_type = "UI"; bl_category = "Neuro3D"; bl_label = "Optical lattice (Iris)"

    def draw(self, context):
        col = self.layout.column(align=True)
        col.operator("neuro3d.live", text=("Pause" if LIVE["on"] else "Play live"), icon=("PAUSE" if LIVE["on"] else "PLAY"))
        col.separator()
        col.operator("neuro3d.build_trained", icon="LIGHT_SUN")
        row = col.row(align=True)
        row.operator("neuro3d.classify_flower", text="Previous", icon="TRIA_LEFT").step = -1
        row.operator("neuro3d.classify_flower", text="Next", icon="TRIA_RIGHT").step = 1
        col.label(text=f"flower #{context.scene.get('flower', 0)}")


def register():
    for c in (NEURO3D_OT_classify, NEURO3D_OT_build, NEURO3D_OT_live, NEURO3D_PT_panel):
        try: bpy.utils.register_class(c)
        except ValueError: pass


# ----------------------------------------------------------------------------------------------
def main(argv):
    x, y, _ = load_iris(); out_dir = None; state_path = os.path.join(HERE, "trained_lattice.json")
    if "--render" in argv: out_dir = argv[argv.index("--render") + 1]; os.makedirs(out_dir, exist_ok=True)
    tr, te = split()
    if "--train" in argv:
        x, y, scaler = load_iris(scaler=(load_raw()[0][tr].min(0), load_raw()[0][tr].max(0)))
        t0 = time.time(); p = train(x[tr], y[tr])
        json.dump({"theta": p[:16].tolist(), "ref": p[16], "logt": p[17], "train_idx": tr.tolist(), "test_idx": te.tolist(),
                   "scaler_lo": scaler[0].tolist(), "scaler_hi": scaler[1].tolist(), "scaler_fit": "train rows only",
                   "train_acc_model": loss_acc(p, x[tr], y[tr])[1], "test_acc_model": loss_acc(p, x[te], y[te])[1],
                   "seconds": time.time() - t0}, open(state_path, "w"), indent=1)
        print("TRAINED", json.load(open(state_path))["test_acc_model"], flush=True)
    st = json.load(open(state_path)); theta = np.array(st["theta"]).reshape(K, K)
    build_scene(theta, st["ref"])
    if "--verify" in argv:
        # in-scene inference for every flower (ray tracing); compare with the numpy training model
        t0 = time.time(); preds, maxdiff, casts = [], 0.0, 0
        U = model_U(theta * LAM / (4 * math.pi)); _, outs = modes()
        for n in range(len(y)):
            pred, P, det, _, c = classify(x[n]); preds.append(pred); casts += c
            Pm = np.abs(encode(x[n][None], st["ref"]) @ U.T)[0] ** 2
            maxdiff = max(maxdiff, max(abs(P[k] - Pm[outs.index(cd)]) for k, cd in enumerate(CLASS_DET)))
        preds = np.array(preds)
        rep = {"scene_test_acc": float((preds[te] == y[te]).mean()), "scene_train_acc": float((preds[tr] == y[tr]).mean()),
               "scene_vs_model_max_power_diff": maxdiff, "ray_casts_total": casts, "seconds": time.time() - t0,
               "per_sample_ms": 1000 * (time.time() - t0) / len(y)}
        # extended gate on the hold-out flowers: all 8 complex outputs + escape, decoration invariance, save/reopen
        ins, outs = modes(); probe = [int(n) for n in te]
        def outputs(n):
            a = encode(x[n][None], st["ref"])[0]; det, _, _ = trace({sid: a[ins.index(sid)] for sid in INPUTS + [REF]})
            return [det.get(o, 0j) for o in outs], TRACE_INFO["escape"]
        before = {n: outputs(n) for n in probe}
        pred, P, _, seg, _ = classify(x[probe[0]]); show(seg, P, pred, truth=int(y[probe[0]]), x_row=x[probe[0]])   # add decoration
        after = {n: outputs(n) for n in probe}
        blend = os.path.join(HERE, "renders", "verify_tmp.blend"); os.makedirs(os.path.dirname(blend), exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=blend); bpy.ops.wm.open_mainfile(filepath=blend)
        reopened = {n: outputs(n) for n in probe}
        U = model_U(theta * LAM / (4 * math.pi))
        model = {n: list(U @ encode(x[n][None], st["ref"])[0]) for n in probe}
        diff = lambda A, B: max(max(abs(a - b) for a, b in zip(A[n][0], B[n][0])) for n in probe)
        rep.update({"outputs_complex_vs_model_max": max(max(abs(a - b) for a, b in zip(before[n][0], model[n])) for n in probe),
                    "decoration_invariance_max": diff(before, after), "save_reopen_max": diff(before, reopened),
                    "escape_max": max(v[1] for v in before.values()),
                    "power_balance_max_err": max(abs(sum(abs(c) ** 2 for c in v[0]) + v[1] - 1) for v in before.values())})
        os.remove(blend)
        json.dump(rep, open(os.path.join(HERE, "scene_verification.json"), "w"), indent=1); print("VERIFY", rep, flush=True)
        st2 = json.load(open(state_path)); theta = np.array(st2["theta"]).reshape(K, K); build_scene(theta, st2["ref"])
    if out_dir:
        setup_render(); sc = bpy.context.scene
        picks = [int(te[np.where(y[te] == c)[0][0]]) for c in range(3)]
        for k, n in enumerate(picks):
            pred, P, _, seg, _ = classify(x[n]); show(seg, P, pred, truth=int(y[n]), x_row=x[n])
            sc.render.filepath = os.path.join(out_dir, f"iris_{SPECIES[y[n]]}.png"); bpy.ops.render.render(write_still=True)
            print("RENDERED", sc.render.filepath, flush=True)
        txt = bpy.data.texts.get("neuro3d_iris_demo.py") or bpy.data.texts.new("neuro3d_iris_demo.py")
        txt.from_string(open(os.path.join(HERE, "neuro3d_iris_demo.py"), encoding="utf-8").read())
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out_dir, "neuro3d_iris_lattice.blend"))
    print("NEURO3D_IRIS_DONE", flush=True)


if __name__ == "__main__":
    if bpy.app.background:
        main(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
    else:
        register()   # GUI: use the Neuro3D tab in the 3D view sidebar

        def _present():
            for win in bpy.context.window_manager.windows:
                for area in win.screen.areas:
                    if area.type == "VIEW_3D":
                        sp = area.spaces.active; sp.shading.type = "RENDERED"; sp.region_3d.view_perspective = "CAMERA"
                        sp.show_region_ui = True
                        try: sp.overlay.show_overlays = False
                        except Exception: pass
            return None
        bpy.app.timers.register(_present, first_interval=1.0)
        LIVE["on"] = True; bpy.app.timers.register(_live_tick, first_interval=2.0)   # start the live demo
