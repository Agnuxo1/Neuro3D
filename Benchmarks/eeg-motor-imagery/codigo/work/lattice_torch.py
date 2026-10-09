"""Differentiable K x K lattice of EXP-003 cells (same geometry/conventions as exp004/lattice_oracle.py).
Trainable parameters are physical: roof offsets d[i,j] (BU). U(d, lambda) maps inputs (r0..r{K-1}, c0..c{K-1})
to detectors (R0..R{K-1}, C0..C{K-1}). The trained d can be written into a Blender scene and ray-traced."""
import math, torch

T = 1 / math.sqrt(2); R = 1j / math.sqrt(2); M = -1.0
SRC_GAP = DET_GAP = 1.0


def lattice_xy(K, variant="v0"):
    X = [0.0]; Y = [0.0]
    a, b, c, d = (0.0137, 0.0031, 0.0211, 0.0017) if variant == "v0" else (0.0293, -0.0023, 0.0079, 0.0041)
    for i in range(1, K):
        X.append(X[-1] + 4.0 + a * i + b * i * i); Y.append(Y[-1] + 4.0 + c * i + d * i * i)
    return X, Y


def lattice_U(d, lam, K=4, variant="v0", dlink=None):
    """d: (B, K, K) real offsets; lam: (B,) wavelengths. Returns U (B, 2K, 2K) complex, U[:, out, in]."""
    X, Y = lattice_xy(K, variant); B = d.shape[0]; n = 2 * K
    k = (2 * math.pi / lam).to(torch.cdouble if d.dtype == torch.float64 else torch.cfloat).view(B, 1)
    dv = d.device
    ph = lambda L: torch.exp(1j * k * torch.as_tensor(L, dtype=torch.float64, device=dv))                          # (B,1)
    eye = torch.eye(n, dtype=k.dtype, device=d.device).unsqueeze(0).expand(B, n, n)  # columns = inputs
    ax = {(i, j): torch.zeros(B, n, dtype=k.dtype, device=d.device) for i in range(K) for j in range(K)}; ay = dict(ax)
    for j in range(K): ax[(0, j)] = eye[:, j, :] * ph(SRC_GAP)
    for i in range(K): ay[(i, 0)] = eye[:, K + i, :] * ph(SRC_GAP)
    out = [None] * n
    for i in range(K):
        for j in range(K):
            L1 = 5.0 + 2 * d[:, i, j].view(B, 1)
            a1 = (T * ax[(i, j)] + R * ay[(i, j)]) * (M ** 3) * torch.exp(1j * k * L1)
            a2 = (R * ax[(i, j)] + T * ay[(i, j)]) * M * ph(3.0)
            ox, oy = R * a1 + T * a2, T * a1 + R * a2
            if dlink is not None: ox = ox * torch.exp(1j * k * dlink[:, i, j].view(B, 1))   # extra delay line on the +x exit
            if i + 1 < K: ax[(i + 1, j)] = ax[(i + 1, j)] + ox * ph(X[i + 1] - X[i] - 1.0)
            else: out[j] = ox * ph(DET_GAP)
            if j + 1 < K: ay[(i, j + 1)] = ay[(i, j + 1)] + oy * ph(Y[j + 1] - Y[j] - 2.0)
            else: out[K + i] = oy * ph(DET_GAP)
    return torch.stack(out, 1)                                   # (B, out, in)


if __name__ == "__main__":
    # validate against the independent oracle (exp004/lattice_oracle.py, oracle A path sum and B transfer)
    import sys, os; sys.path.insert(0, os.environ.get("NEURO3D_EXTERNAL", os.path.join(os.path.dirname(os.path.abspath(__file__)), "exp004")))
    import lattice_oracle as O
    K = 4; d0 = O.base_offsets(K)
    d = torch.tensor([[[d0[(i, j)] for j in range(K)] for i in range(K)]], dtype=torch.float64)
    U = lattice_U(d, torch.tensor([0.1], dtype=torch.float64))[0]
    Uo, ins, outs = O.transfer(K)
    err = max(abs(U[o_i, s_i].item() - Uo[o][s]) for o_i, o in enumerate(outs) for s_i, s in enumerate(ins))
    uni = (U.conj().T @ U - torch.eye(2 * K, dtype=U.dtype)).abs().max().item()
    fa, _, _ = O.run_A(K, {"r0": 1.0}); errA = max(abs(U[o_i, 0].item() - fa[o]) for o_i, o in enumerate(outs))
    print(f"torch vs oracle B {err:.2e}; vs path-sum A (input r0) {errA:.2e}; unitarity {uni:.2e}")
