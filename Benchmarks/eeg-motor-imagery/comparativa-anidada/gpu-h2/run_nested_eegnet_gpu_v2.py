"""GPU successor runner for the preregistered nested EEGNet comparator (H2).

Identity: EXP-006-EEGNET-GPU-H2-20261013-001 (see PROFILE-EEGNET-GPU-H2.md).

The frozen v1 runner (../run_nested_comparators_v1.py, sha256 3215b859...) is
imported, not copied or edited.  Everything that defines the experiment is taken
from v1 unchanged: the 36-configuration grid (EEG_CONFIGS), the default
configuration, the outer/inner LORO folds and their equality checks against the
saved optical folds, the seeds (outer k, inner 100+10k+j), the internal-BCE
selection rule (v1.choose), the snapshots at epochs 30/60/90 of a single
90-epoch trajectory, and the stored NPZ schema.  The only replaced function is
v1.fit_eegnet, re-implemented here with identical arithmetic but with the
model and tensors on CUDA (the declared deviation).  Initial weights and the
mini-batch order still come from the CPU generator seeded with
torch.manual_seed(seed), exactly as in v1; dropout masks come from the CUDA
generator (seeded by the same call), so they differ from a CPU run.

Loads Xtr/ytr/run only (through v1.run_subject); Xte is never read.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import platform
import sys
import time
import warnings
from pathlib import Path

# Thread and cuBLAS settings must exist before torch / bench / nested_bench are imported.
os.environ.setdefault("TORCH_THREADS", "2")
os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")

import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
V1_PATH = HERE.parent / "run_nested_comparators_v1.py"
V1_SHA256 = "3215b8594e8fa9c142d7576a1483ca9cea32f996eaf497a0f3aba9cf9958122a"
HOST_RAM_FLOOR_MIB = 700.0


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_v1():
    digest = sha256(V1_PATH)
    if digest != V1_SHA256:
        raise RuntimeError(f"Frozen v1 runner changed: {digest}")
    spec = importlib.util.spec_from_file_location("run_nested_comparators_v1", V1_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


v1 = load_v1()
STATE = {"deadline": None, "device": None, "trainings": [], "min_available_mib": None}


class ResourceStop(RuntimeError):
    pass


def check_resources():
    import psutil
    available = psutil.virtual_memory().available / 2**20
    if STATE["min_available_mib"] is None or available < STATE["min_available_mib"]:
        STATE["min_available_mib"] = available
    if available < HOST_RAM_FLOOR_MIB:
        raise ResourceStop(f"HOST_RAM_FLOOR: {available:.1f} MiB available < {HOST_RAM_FLOOR_MIB} MiB")
    if STATE["deadline"] is not None and time.monotonic() > STATE["deadline"]:
        raise ResourceStop("DEADLINE: per-ticket wall-clock limit exceeded")


def fit_eegnet_gpu(B, X, y, train, evaluations, lr, batch, wd, seed):
    """v1.fit_eegnet with the model and tensors on STATE['device'] (same arithmetic otherwise)."""
    import torch
    device = STATE["device"]
    started = time.perf_counter()
    torch.manual_seed(seed)
    # Same training-only channel standard deviation as the historical bench (computed on CPU, float32 input).
    scale = X[train].std(axis=(0, 2), keepdims=True) + 1e-6
    xt = torch.as_tensor(X[train] / scale, dtype=torch.float32).to(device)
    yt = torch.as_tensor(y[train], dtype=torch.float32).to(device)
    xe = [torch.as_tensor(X[index] / scale, dtype=torch.float32).to(device) for index in evaluations]
    model = B.EEGNet().to(device)  # initialised on CPU from the seeded CPU generator, as in v1
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=wd)
    output = {}
    for epoch in range(1, 91):
        model.train()
        order = torch.randperm(len(train))  # CPU generator, identical order to v1
        for i in range(0, len(train), batch):
            indices = order[i:i + batch].to(device)
            optimizer.zero_grad()
            torch.nn.functional.binary_cross_entropy_with_logits(model(xt[indices]), yt[indices]).backward()
            optimizer.step()
        if epoch in (30, 60, 90):
            model.eval()
            with torch.no_grad():
                output[epoch] = [model(value).cpu().numpy().copy() for value in xe]
        if epoch % 10 == 0:
            check_resources()
    if device.type == "cuda":
        torch.cuda.synchronize()
    STATE["trainings"].append({"n_train": int(len(train)), "batch": int(batch), "seed": int(seed),
                               "steps": int(90 * -(-len(train) // batch)),
                               "seconds": time.perf_counter() - started})
    return output


v1.fit_eegnet = fit_eegnet_gpu  # the single, declared substitution


def environment(torch, determinism_warnings):
    cuda = torch.cuda.is_available()
    return {
        "python": sys.version, "platform": platform.platform(), "numpy": np.__version__,
        "torch": torch.__version__, "torch_cuda": torch.version.cuda,
        "cudnn": torch.backends.cudnn.version() if cuda else None,
        "device": str(STATE["device"]),
        "gpu": torch.cuda.get_device_name(0) if cuda else None,
        "torch_threads": torch.get_num_threads(),
        "determinism": {
            "cudnn.deterministic": torch.backends.cudnn.deterministic,
            "cudnn.benchmark": torch.backends.cudnn.benchmark,
            "use_deterministic_algorithms": torch.are_deterministic_algorithms_enabled(),
            "warn_only": torch.is_deterministic_algorithms_warn_only_enabled(),
            "CUBLAS_WORKSPACE_CONFIG": os.environ.get("CUBLAS_WORKSPACE_CONFIG"),
            "warnings": sorted(set(determinism_warnings)),
            "note": "GPU kernels may still be nondeterministic; results may differ numerically from a CPU run",
        },
        "source_sha256": {
            "run_nested_comparators_v1.py": V1_SHA256,
            "run_nested_eegnet_gpu_v2.py": sha256(Path(__file__).resolve()),
            "bench.py": sha256(v1.WORK / "bench.py"),
            "nested_bench.py": sha256(v1.WORK / "nested" / "nested_bench.py"),
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--optical-raw", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--subjects", nargs="+", required=True)
    parser.add_argument("--pilot", action="store_true", help="first complete external fold only (timing)")
    parser.add_argument("--require-cuda", action="store_true")
    parser.add_argument("--deadline-seconds", type=float, default=5400.0)
    args = parser.parse_args()
    for sid in args.subjects:
        if len(sid) != 4 or not sid.startswith("S") or not sid[1:].isdigit():
            parser.error("Subject IDs must have the S### format")

    import torch
    torch.set_num_threads(2)
    torch.set_num_interop_threads(1)
    cuda = torch.cuda.is_available()
    if args.require_cuda and not cuda:
        raise SystemExit("BLOCKED: CUDA unavailable")
    STATE["device"] = torch.device("cuda" if cuda else "cpu")
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    torch.use_deterministic_algorithms(True, warn_only=True)
    determinism_warnings = []
    warnings.simplefilter("always")
    original_showwarning = warnings.showwarning

    def capture(message, category, filename, lineno, file=None, line=None):
        determinism_warnings.append(f"{category.__name__}: {str(message)[:300]}")
        original_showwarning(message, category, filename, lineno, file, line)

    warnings.showwarning = capture
    args.out.mkdir(parents=True, exist_ok=True)
    STATE["deadline"] = time.monotonic() + args.deadline_seconds
    check_resources()
    log = args.out / "timing.jsonl"
    for sid in args.subjects:
        target = args.out / (sid + ".npz")
        if target.exists():
            raise FileExistsError(f"Refusing to overwrite {target}")
        STATE["trainings"] = []
        started = time.monotonic()
        result = v1.run_subject(args.data / (sid + ".npz"), "eegnet", args.optical_raw / (sid + ".npz"), args.pilot)
        seconds = time.monotonic() - started
        env = environment(torch, determinism_warnings)
        if cuda:
            env["max_memory_allocated_mib"] = torch.cuda.max_memory_allocated() / 2**20
        record = {"experiment": "EXP-006-EEGNET-GPU-H2-20261013-001", "subject": sid, "pilot": args.pilot,
                  "seconds": seconds, "n_trainings": len(STATE["trainings"]),
                  "steps": sum(t["steps"] for t in STATE["trainings"]),
                  "training_seconds": sum(t["seconds"] for t in STATE["trainings"]),
                  "min_host_available_mib": STATE["min_available_mib"], "environment": env,
                  "trainings": STATE["trainings"]}
        result["gpu_meta"] = json.dumps(record)
        np.savez_compressed(args.out / (sid + ".npz.partial.npz"), **result)
        os.replace(args.out / (sid + ".npz.partial.npz"), target)
        record["npz_sha256"] = sha256(target)
        with log.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps({k: v for k, v in record.items() if k != "trainings"}) + "\n")
        print(json.dumps({"done": sid, "seconds": seconds, "sha256": record["npz_sha256"]}), flush=True)


if __name__ == "__main__":
    main()
