"""Import-safe successor of the frozen prediction script. Does not submit."""
from __future__ import annotations
import argparse
import importlib
from pathlib import Path
import sys

WORK = Path(__file__).resolve().parents[1]
FREQUENCIES = [6, 8, 10, 12, 14, 16, 18, 20, 23, 26, 30, 35]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model", choices=["polar", "lattice32", "free"])
    parser.add_argument("epochs", type=int)
    parser.add_argument("weight_decay", type=float)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.epochs <= 0 or args.weight_decay < 0 or args.out.exists():
        parser.error("Positive epochs, nonnegative decay and a new output are required")
    import numpy as np
    import torch
    old = list(sys.path)
    try:
        sys.path.insert(0, str(WORK))
        B = importlib.import_module("bench")
    finally:
        sys.path[:] = old
    torch.set_num_threads(2)
    B.WIN = 3
    rows = []
    for path in sorted(args.data.glob("S*.npz")):
        with np.load(path, allow_pickle=False) as data:
            X, y, Xt = data["Xtr"].astype(np.float32), data["ytr"], data["Xte"].astype(np.float32)
        Z, Zt = B.cwt(X, freqs=FREQUENCIES), B.cwt(Xt, freqs=FREQUENCIES)
        scale = np.abs(Z).std(axis=(0, 3), keepdims=True)+1e-6
        Zi, Zti = torch.as_tensor(Z/scale), torch.as_tensor(Zt/scale)
        yt = torch.as_tensor(y, dtype=torch.float32)
        logits = np.zeros(len(Xt))
        for seed in range(5):
            torch.manual_seed(seed)
            model = B.LatticeNet(len(FREQUENCIES), links=True) if args.model == "lattice32" else B.Optic(len(FREQUENCIES), unitary="polar" if args.model == "polar" else False)
            optimizer = torch.optim.AdamW(model.parameters(), lr=2e-2, weight_decay=args.weight_decay)
            for _ in range(args.epochs):
                model.train()
                permutation = torch.randperm(len(yt))
                for i in range(0, len(yt), 32):
                    batch = permutation[i:i+32]
                    optimizer.zero_grad()
                    torch.nn.functional.binary_cross_entropy_with_logits(model(Zi[batch]), yt[batch]).backward()
                    optimizer.step()
            model.eval()
            with torch.no_grad():
                logits += model(Zti).numpy()
        rows.extend("move" if value > 0 else "rest" for value in logits)
    if not rows:
        raise ValueError("No subject files found")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write("ID,TARGET\n")
        stream.writelines(f"{i},{target}\n" for i, target in enumerate(rows))


if __name__ == "__main__":
    main()
