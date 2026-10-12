"""Execute the G1 protocol exactly as committed; refuse to overwrite an earlier run."""
from __future__ import annotations

import os
for _name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_name] = "1"
import argparse
import hashlib
import json
from pathlib import Path
import platform
import sys
import time

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from Tools.audit_captured_pilot_result_v1 import decode  # noqa: E402
from Tools.train_captured_geometry_v1 import parameters_and_bases  # noqa: E402
from Blender.blender_lab.affine_geometry_network_v1 import AffineGeometryNetwork  # noqa: E402

CAPTURE = ROOT / "Docs/validation/native-deferred-training-2026-10-09/attempt01/worker"
BATCHES, REPEATS, BOX = (1, 150, 4096), 15, 0.035
FIELD_TOL, TANGENT_TOL, RATIO = 1e-12, 1e-9, 2.0


def load():
    scene = decode(json.loads((CAPTURE / "initial_native_scene.json").read_bytes()))
    graph = decode(json.loads((CAPTURE / "initial_native_graph.json").read_bytes()))
    return AffineGeometryNetwork(scene, graph, parameters_and_bases(scene)[0])


def inputs(n: int) -> np.ndarray:
    f = np.random.default_rng(4242).random((n, 4))
    x = np.column_stack([f, np.ones(n)])
    return (x / np.linalg.norm(x, axis=1, keepdims=True)).astype(np.complex128)


def compiled(net, x, theta, tangents: bool):
    r = net.forward(np.eye(5, dtype=np.complex128), theta, gradients=tangents)
    fields = x @ r["fields"]                       # (n,5) @ (5,8): rows of r are basis responses
    if not tangents:
        return fields, None
    return fields, np.einsum("nk,kpj->npj", x, r["field_jacobian"])


def graph(net, x, theta, tangents: bool):
    r = net.forward(x, theta, gradients=tangents)
    return r["fields"], r["field_jacobian"]


def timed(fn) -> float:
    t0 = time.perf_counter()
    fn()
    return time.perf_counter() - t0


def stats(values) -> dict:
    a = np.asarray(values)
    return {"median_s": float(np.median(a)), "q25_s": float(np.quantile(a, 0.25)), "q75_s": float(np.quantile(a, 0.75)), "n": len(a)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=HERE / "results")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    net = load()
    thetas = {"zero": np.zeros(net.count), "random": np.random.default_rng(7).uniform(-BOX, BOX, net.count)}
    equivalence = {}
    for name, theta in thetas.items():
        x = inputs(4096)
        fg, tg = graph(net, x, theta, True)
        fc, tc = compiled(net, x, theta, True)
        equivalence[name] = {"max_field_diff": float(np.max(np.abs(fg - fc))), "max_tangent_diff": float(np.max(np.abs(tg - tc))),
                             "max_tangent_abs": float(np.max(np.abs(tg)))}
    equivalent = all(e["max_field_diff"] <= FIELD_TOL and e["max_tangent_diff"] <= TANGENT_TOL for e in equivalence.values())
    theta = thetas["random"]
    cells, compile_times = {}, []
    for n in BATCHES:
        x = inputs(n)
        for mode, tangents in (("inference", False), ("training_step", True)):
            g_t, c_t, cached_t = [], [], []
            r_cached = net.forward(np.eye(5, dtype=np.complex128), theta, gradients=tangents)
            for rep in range(REPEATS):
                order = (0, 1) if rep % 2 == 0 else (1, 0)
                for which in order:
                    if which == 0:
                        g_t.append(timed(lambda: graph(net, x, theta, tangents)))
                    else:
                        c_t.append(timed(lambda: compiled(net, x, theta, tangents)))
                cached_t.append(timed(lambda: (x @ r_cached["fields"], np.einsum("nk,kpj->npj", x, r_cached["field_jacobian"]) if tangents else None)))
            compile_times.extend(timed(lambda: net.forward(np.eye(5, dtype=np.complex128), theta, gradients=tangents)) for _ in range(3))
            cell = {"graph": stats(g_t), "compiled_with_recompile": stats(c_t), "compiled_cached_U": stats(cached_t)}
            cell["ratio_graph_over_compiled_with_recompile"] = cell["graph"]["median_s"] / cell["compiled_with_recompile"]["median_s"]
            cell["ratio_graph_over_cached"] = cell["graph"]["median_s"] / cell["compiled_cached_U"]["median_s"]
            cells[f"{mode}_batch{n}"] = cell
            print(mode, n, round(cell["ratio_graph_over_compiled_with_recompile"], 2), flush=True)
    decisive = [cells[f"{m}_batch{n}"]["ratio_graph_over_compiled_with_recompile"] for m in ("inference", "training_step") for n in (150, 4096)]
    decision = ("CONFIRMED" if min(decisive) >= RATIO else "REFUTED") if equivalent else "INCONCLUSIVE"
    report = {"schema": "neuro3d.g1.v1", "protocol": "PROTOCOL-G1.md", "equivalence": equivalence, "equivalent": equivalent,
              "cells": cells, "H_G1": decision, "min_decisive_ratio": min(decisive),
              "compile_seconds_median": float(np.median(compile_times)),
              "environment": {"python": platform.python_version(), "numpy": np.__version__, "platform": platform.platform(),
                              "processor": platform.processor()},
              "sources_sha256": {str(p.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(p.read_bytes()).hexdigest()
                                 for p in (HERE / "PROTOCOL-G1.md", HERE / "run_g1.py",
                                           ROOT / "Blender/blender_lab/affine_geometry_network_v1.py",
                                           CAPTURE / "initial_native_scene.json", CAPTURE / "initial_native_graph.json")}}
    (args.out / "G1_RESULTS.json").write_bytes((json.dumps(report, indent=1, allow_nan=False) + "\n").encode())
    print(json.dumps({"H_G1": decision, "equivalence": equivalence, "min_decisive_ratio": min(decisive)}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
