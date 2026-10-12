"""Execute the WAVE-C1 protocol exactly as committed; refuse to overwrite an earlier run."""
from __future__ import annotations

import argparse
from fractions import Fraction
import glob
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import platform
import sys
import time

import numpy as np
import scipy
from scipy.special import erfcinv

from angular_spectrum_wave import (K, SQ2, Grid, MZIGeometry, Splitter, cascade_model, circular_difference,
    discarded_evanescent, gaussian_waist_beam, mzi_model, paraxial_source_beam, port_amplitudes,
    slab_coefficients, solve_cascade, solve_mzi)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WAVE = HERE.parent / "validacion-onda"
CAPTURE = ROOT / "Docs/validation/native-deferred-training-2026-10-09/attempt01/worker"
W = 8.0
N_DEVICE = 2.537430764948469
D_FILM = 0.25
A_ARM = 30.0 / SQ2
DARK = 0.05
REFERENCE = (-186.0, 512.0, 8192)
PRIMARY_VARIANTS = [(-186.0, 512.0, 2048), (-186.0, 512.0, 4096), (-442.0, 1024.0, 8192)]
CASCADE_VARIANTS = [(-186.0, 512.0, 4096), (-442.0, 1024.0, 8192)]
SOLVER_BUDGET, BALANCE_BUDGET, MODEL_BUDGET, CROSS_BUDGET = 1e-9, 1e-9, 0.02, 0.005
EPSILON, CLIP = 0.02, 1e-3


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def frozen(name: str):
    sys.path.insert(0, str(WAVE))
    try:
        spec = importlib.util.spec_from_file_location("p17_" + name, WAVE / f"{name}.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.remove(str(WAVE))


def centre_coefficients() -> tuple[complex, complex]:
    r, t = slab_coefficients(np.array([K / SQ2]), N_DEVICE, D_FILM)
    return complex(r[0]), complex(t[0])


def reim(z: complex) -> list[float]:
    return [z.real, z.imag]


def primary_geometry(j: int) -> MZIGeometry:
    return MZIGeometry(0.0, 0.0, A_ARM, A_ARM + j / (20 * SQ2), 25.0, -25.0, 2 * A_ARM + 25, 2 * A_ARM + 25)


def solve_primary(spec) -> list[dict]:
    grid = Grid(*spec)
    beam = gaussian_waist_beam(grid, 0.0, 0.0, W)
    splitter = Splitter(grid, 0.0, n=N_DEVICE, d=D_FILM)
    rows = []
    for j in range(21):
        g = primary_geometry(j)
        res = solve_mzi(beam, splitter, g)
        c1, c2 = port_amplitudes(res, grid, g, W)
        rows.append({"j": j, "c": [reim(c1), reim(c2)], "P": [abs(c1) ** 2, abs(c2) ** 2],
                     "flux_balance": res["flux_out"] / res["flux_in"] - 1.0,
                     "discarded_evanescent_relative": max(discarded_evanescent(grid, res["out_plus"].spectrum),
                                                          discarded_evanescent(grid, res["out_minus"].spectrum))})
    return rows


def model_rows(geoms, model, r, t) -> list[dict]:
    grid = Grid(*REFERENCE)
    out = []
    for g in geoms:
        a, b = model(g, r, t, grid)
        out.append({"c": [reim(a), reim(b)], "P": [abs(a) ** 2, abs(b) ** 2]})
    return out


def compare(solver, model) -> tuple[float, list[dict]]:
    errors, detail = [], []
    for s, m in zip(solver, model):
        e = [abs(s["P"][p] - m["P"][p]) for p in (0, 1)]
        phases = [circular_difference(complex(*s["c"][p]), complex(*m["c"][p]), DARK) for p in (0, 1)]
        errors.extend(e)
        detail.append({"error": e, "phase_difference_rad": phases})
    return max(errors), detail


def self_consistency(reference, variants) -> float:
    worst = 0.0
    for rows in variants:
        for a, b in zip(reference, rows):
            worst = max(worst, max(abs(a["P"][p] - b["P"][p]) for p in (0, 1)))
    return worst


def run_primary(r, t) -> dict:
    ref = solve_primary(REFERENCE)
    variants = [solve_primary(v) for v in PRIMARY_VARIANTS]
    consistency = self_consistency(ref, variants)
    balance = max(abs(x["flux_balance"]) for rows in [ref] + variants for x in rows)
    geoms = [primary_geometry(j) for j in range(21)]
    m0 = model_rows(geoms, lambda g, r_, t_, grid: mzi_model(g, r_, t_, grid, W, False), r, t)
    m1 = model_rows(geoms, lambda g, r_, t_, grid: mzi_model(g, r_, t_, grid, W, True), r, t)
    e0, d0 = compare(ref, m0)
    e1, d1 = compare(ref, m1)
    solver_ok = consistency <= SOLVER_BUDGET and balance <= BALANCE_BUDGET
    return {"solver_reference": ref, "model_M0": m0, "model_M1": m1, "comparison_M0": d0, "comparison_M1": d1,
            "Emax_M0": e0, "Emax_M1": e1, "self_consistency_max_abs_dP": consistency, "max_abs_flux_balance": balance,
            "solver_budgets_met": solver_ok,
            "H_C1": ("CONFIRMED" if e1 <= MODEL_BUDGET else "REFUTED") if solver_ok else "INCONCLUSIVE",
            "H_C0": ("REPLICATED" if e0 > MODEL_BUDGET else "NOT_REPLICATED") if solver_ok else "INCONCLUSIVE",
            "effective_path_difference_lambda": [j / 20 for j in range(21)],
            "modal_sum_P1_plus_P2": [x["P"][0] + x["P"][1] for x in ref]}


def run_crosscheck() -> dict:
    mzi = frozen("mzi_fdtd")
    calibration = json.loads((WAVE / "calibracion_fdtd_45.json").read_text(encoding="utf-8"))["mallas"]
    points, worst = [], {"i": 0.0, "ii": 0.0, "iii": 0.0}
    for ppl in (16, 24):
        cal = calibration[str(ppl)]
        rpm = complex(cal["plano_medio"]["r_re"], cal["plano_medio"]["r_im"])
        tpm = complex(cal["plano_medio"]["t_re"], cal["plano_medio"]["t_im"])
        for path in sorted(glob.glob(str(WAVE / "resultados" / f"mzi_fdtd_{ppl}_k*.json"))):
            archived = json.loads(Path(path).read_text(encoding="utf-8"))
            k = archived["k"]
            g = mzi.geometria(ppl, k, cal["n_usado"])
            geom = MZIGeometry(g["xS"], g["yS1"], g["a_A"], g["a_B"], g["x_p1"], g["x_p2"],
                               g["yS2"] + (g["x_p1"] - g["xS"]), g["yS2"] + (g["xS"] - g["x_p2"]))
            grid = Grid(g["yS1"] + 34.0 - 256.0, 512.0, 8192)
            beam = paraxial_source_beam(grid, g["x0"], g["yc"], W, -SQ2 * (g["xS"] - g["x0"]))
            variants = {"i": Splitter(grid, g["xS"], n=cal["n_usado"], d=D_FILM),
                        "ii": Splitter(grid, g["xS"], r=rpm, t=tpm),
                        "iii": Splitter(grid, g["xS"], n=N_DEVICE, d=D_FILM)}
            row = {"ppl": ppl, "k": k, "dL_eff": archived["dL_eff"],
                   "fdtd_P": [archived["P1_solver"], archived["P2_solver"]]}
            for name, splitter in variants.items():
                res = solve_mzi(beam, splitter, geom)
                c1, c2 = port_amplitudes(res, grid, geom, W)
                row[name] = {"P": [abs(c1) ** 2, abs(c2) ** 2], "flux_balance": res["flux_out"] / res["flux_in"] - 1}
                diff = max(abs(row[name]["P"][p] - row["fdtd_P"][p]) for p in (0, 1))
                row[name]["max_abs_diff_vs_fdtd"] = diff
                worst[name] = max(worst[name], diff)
            points.append(row)
    return {"points": points, "max_abs_diff_vs_fdtd": worst, "count": len(points),
            "H_C2": "SUPPORTED" if worst["ii"] <= CROSS_BUDGET else "NOT_SUPPORTED",
            "variants": {"i": "slab with the FDTD index of that mesh", "ii": "ideal splitter with FDTD-calibrated centre r,t",
                         "iii": "continuous 50/50 slab of the primary device"}}


def cascade_geometries(dl1: float, j: int) -> list[MZIGeometry]:
    y2 = 4 * A_ARM + 55.0
    return [MZIGeometry(0.0, 0.0, A_ARM, A_ARM + dl1 / SQ2, 25.0, -25.0, 2 * A_ARM + 25, 2 * A_ARM + 25),
            MZIGeometry(30.0, 2 * A_ARM + 30.0, A_ARM, A_ARM + j / (20 * SQ2), 55.0, 5.0, y2, y2)]


def solve_cascade_rows(spec) -> list[dict]:
    grid = Grid(*spec)
    beam = gaussian_waist_beam(grid, 0.0, 0.0, W)
    rows = []
    for dl1 in (0.0, 0.25, 0.5):
        for j in range(21):
            stages = cascade_geometries(dl1, j)
            res = solve_cascade(beam, stages, lambda x: Splitter(grid, x, n=N_DEVICE, d=D_FILM))
            c1, c2 = port_amplitudes(res, grid, stages[-1], W)
            rows.append({"dl1": dl1, "j": j, "c": [reim(c1), reim(c2)], "P": [abs(c1) ** 2, abs(c2) ** 2],
                         "flux_balance": (res["flux_out"] + res["discarded_flux"]) / res["flux_in"] - 1.0})
    return rows


def run_cascade(r, t) -> dict:
    ref = solve_cascade_rows(REFERENCE)
    variants = [solve_cascade_rows(v) for v in CASCADE_VARIANTS]
    consistency = self_consistency(ref, variants)
    geoms = [cascade_geometries(x["dl1"], x["j"]) for x in ref]
    m0 = model_rows(geoms, lambda g, r_, t_, grid: cascade_model(g, r_, t_, grid, W, False), r, t)
    m1 = model_rows(geoms, lambda g, r_, t_, grid: cascade_model(g, r_, t_, grid, W, True), r, t)
    e0, d0 = compare(ref, m0)
    e1, d1 = compare(ref, m1)
    balance = max(abs(x["flux_balance"]) for rows in [ref] + variants for x in rows)
    solver_ok = consistency <= SOLVER_BUDGET and balance <= BALANCE_BUDGET
    return {"solver_reference": ref, "model_M0": m0, "model_M1": m1, "comparison_M0": d0, "comparison_M1": d1,
            "Emax_M0": e0, "Emax_M1": e1, "self_consistency_max_abs_dP": consistency, "max_abs_flux_balance": balance,
            "solver_budgets_met": solver_ok,
            "H_C3": ("CONFIRMED" if e1 <= MODEL_BUDGET else "REFUTED") if solver_ok else "INCONCLUSIVE",
            "flux_note": "flux_balance counts the stage-1 -x output, which leaves the cascade, as discarded flux"}


def fraction(value) -> Fraction:
    return Fraction(value["numerator"], value["denominator"]) if isinstance(value, dict) else Fraction(value)


def vector(values) -> np.ndarray:
    return np.array([float(fraction(v)) for v in values])


def run_regime() -> dict:
    scene = json.loads((CAPTURE / "initial_native_scene.json").read_text(encoding="utf-8"))
    graph = json.loads((CAPTURE / "initial_native_graph.json").read_text(encoding="utf-8"))
    lam = float(fraction(scene["lambda_BU"]))
    zeta_max = 2.0 * math.sqrt(EPSILON / (1.0 - EPSILON))
    clip_ratio = float(erfcinv(CLIP)) / math.sqrt(2.0)
    apertures, normals = {}, {}
    for name, obj in scene["objects"].items():
        v = np.array([vector(p) for p in obj["vertices_world_BU"]])
        centred = v - v.mean(axis=0)
        _, _, axes = np.linalg.svd(centred, full_matrices=False)
        extents = [float(np.ptp(centred @ axes[i])) for i in (0, 1)]
        apertures[name], normals[name] = min(extents), axes[2]
    nodes = graph["nodes"]
    seg_len, eff_ap = [], []
    for node in nodes:
        d = vector(node["direction"])
        norm = float(np.linalg.norm(d))
        length = float(fraction(node["segment_parameter"])) * norm
        if "terminal" in node:
            length += float(fraction(node["reference_parameter"])) * norm
        seg_len.append(length)
        cosine = abs(float(np.dot(d / norm, normals[node["hit_object"]])))
        eff_ap.append(apertures[node["hit_object"]] * cosine)
    paths = []
    stack = [(root["node"], 0.0, math.inf) for root in graph["roots"]]
    while stack:
        i, length, aperture = stack.pop()
        length, aperture = length + seg_len[i], min(aperture, eff_ap[i])
        node = nodes[i]
        if "terminal" in node:
            paths.append((length, aperture))
        for edge in node["edges"]:
            stack.append((edge["target"], length, aperture))
    L = np.array([p[0] for p in paths])
    D = np.array([p[1] for p in paths])
    w_clip = D / (2.0 * clip_ratio)
    with np.errstate(divide="ignore"):
        zeta_at_clip = L * lam / (math.pi * w_clip ** 2)
        lam_max = zeta_max * math.pi * w_clip ** 2 / L
    def quant(a):
        a = np.asarray(a, dtype=float)
        finite = a[np.isfinite(a)]
        return {"min": float(np.min(finite)), "median": float(np.median(finite)), "max": float(np.max(finite)),
                "non_finite_count": int(a.size - finite.size)}
    return {"lambda_BU": lam, "terminal_paths": len(paths), "zeta_max": zeta_max, "clip_half_aperture_over_w": clip_ratio,
            "path_length_over_lambda": quant(L / lam), "limiting_aperture_over_lambda": quant(D / lam),
            "zeta_with_largest_unclipped_beam": quant(zeta_at_clip),
            "fraction_paths_in_regime_at_captured_lambda": float(np.mean(zeta_at_clip <= zeta_max)),
            "largest_lambda_BU_all_paths_in_regime": float(np.min(lam_max)) if np.all(np.isfinite(lam_max)) else None,
            "rescale_factor_lambda_needed": float(np.min(lam_max) / lam) if np.all(np.isfinite(lam_max)) else None,
            "object_aperture_over_lambda_by_kind": {k: quant(np.array([apertures[n] for n, o in scene["objects"].items() if o["kind"] == k]) / lam)
                                                    for k in sorted({o["kind"] for o in scene["objects"].values()})}}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=HERE / "results")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    start = time.perf_counter()
    r, t = centre_coefficients()
    report = {"schema": "neuro3d.wave_c1.v1", "protocol": "PROTOCOL-WAVE-C1.md",
              "environment": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
                              "platform": platform.platform(), "threads": {k: os.environ.get(k) for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")}},
              "device": {"n": N_DEVICE, "d": D_FILM, "w": W, "a_A": A_ARM, "r_c": reim(r), "t_c": reim(t)}}
    sections = {"primary": lambda: run_primary(r, t), "crosscheck_fdtd": run_crosscheck,
                "cascade": lambda: run_cascade(r, t), "network_regime": run_regime}
    for name, fn in sections.items():
        t0 = time.perf_counter()
        report[name] = fn()
        report[name]["seconds"] = time.perf_counter() - t0
        print(name, "done", round(report[name]["seconds"], 2), "s", flush=True)
    report["seconds_total"] = time.perf_counter() - start
    sources = [HERE / "angular_spectrum_wave.py", HERE / "run_wave_c1.py", HERE / "PROTOCOL-WAVE-C1.md",
               HERE / "test_angular_spectrum_wave.py", WAVE / "mzi_fdtd.py", WAVE / "fdtd2d.py",
               WAVE / "calibracion_45.json", WAVE / "calibracion_fdtd_45.json",
               CAPTURE / "initial_native_scene.json", CAPTURE / "initial_native_graph.json"]
    sources += [Path(p) for p in sorted(glob.glob(str(WAVE / "resultados" / "mzi_fdtd_*_k*.json")))]
    report["sources_sha256"] = {str(p.relative_to(ROOT)).replace("\\", "/"): sha256(p) for p in sources}
    target = args.out / "WAVE_C1_RESULTS.json"
    target.write_bytes((json.dumps(report, indent=1, allow_nan=False) + "\n").encode("utf-8"))
    summary = {k: report[k].get(h) for k, h in (("primary", "H_C1"), ("crosscheck_fdtd", "H_C2"), ("cascade", "H_C3"))}
    print(json.dumps({"H": summary, "Emax_M0": report["primary"]["Emax_M0"], "Emax_M1": report["primary"]["Emax_M1"],
                      "H_C0": report["primary"]["H_C0"], "cascade_Emax_M1": report["cascade"]["Emax_M1"],
                      "cross_max": report["crosscheck_fdtd"]["max_abs_diff_vs_fdtd"],
                      "regime": {k: report["network_regime"][k] for k in ("fraction_paths_in_regime_at_captured_lambda", "rescale_factor_lambda_needed")}}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
