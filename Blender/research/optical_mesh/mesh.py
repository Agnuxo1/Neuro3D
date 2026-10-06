"""OPT-007 prototype (Claude): trainable optical mesh whose weights are scene GEOMETRY.

Every trainable parameter is a displacement d (Blender units) of a delay line
(rigid pair of mirrors at 90 deg). A delay line moved by d adds a path 2d with
no lateral shift, so the phase it contributes is phi = k * 2 d, k = 2*pi/lambda.
This is the scalar plane-wave model of Blender/core/mz_scene.py (verified
against Blender readback in EXP-001), extended to N modes:

    cell (m, m+1):  T = BS . diag(e^{i theta}, 1) . BS . diag(e^{i phi}, 1)
                    BS = (1/sqrt 2) [[1, i], [i, 1]]   (same convention as mz_scene)
    theta = 2 k d_int,  phi = 2 k d_ext
    Clements rectangular layout: N columns, N(N-1)/2 cells, + N output delay lines.

Input: features -> non-negative field amplitudes (unit total power).
Output: detected power |E_j|^2 at N detectors (the only nonlinearity), class =
argmax over the first C detectors. A single scalar gain converts power to
logits for the cross-entropy; it does not change the argmax.
Scalar ideal optics; no loss, diffraction or noise. Not a physical-photon claim.
"""

from __future__ import annotations

import math

import torch

LAMBDA = 0.1  # BU, as EXP-001
K = 2 * math.pi / LAMBDA


def clements_pairs(n: int) -> list[list[tuple[int, int]]]:
    cols = []
    for c in range(n):
        start = c % 2
        cols.append([(m, m + 1) for m in range(start, n - 1, 2)])
    return cols


class OpticalMesh(torch.nn.Module):
    def __init__(self, n: int, n_classes: int, seed: int = 0, d_scale: float = LAMBDA):
        super().__init__()
        g = torch.Generator().manual_seed(seed)
        self.n, self.c = n, n_classes
        self.cols = clements_pairs(n)
        n_cells = sum(len(c) for c in self.cols)
        assert n_cells == n * (n - 1) // 2
        # displacements in BU; a full phase cycle needs d = lambda/2
        self.d_int = torch.nn.Parameter(torch.rand(n_cells, generator=g, dtype=torch.float64) * d_scale)
        self.d_ext = torch.nn.Parameter(torch.rand(n_cells, generator=g, dtype=torch.float64) * d_scale)
        self.d_out = torch.nn.Parameter(torch.rand(n, generator=g, dtype=torch.float64) * d_scale)
        self.gain = torch.nn.Parameter(torch.tensor(8.0, dtype=torch.float64))

    def geometry_parameters(self) -> int:
        return self.d_int.numel() + self.d_ext.numel() + self.d_out.numel()

    def fields(self, amp: torch.Tensor) -> torch.Tensor:
        """amp: (B, N) real non-negative -> complex output fields (B, N)."""
        e = amp.to(torch.complex128)
        s2 = 1 / math.sqrt(2)
        idx = 0
        for col in self.cols:
            if not col:
                continue
            a = torch.tensor([p[0] for p in col]); b = torch.tensor([p[1] for p in col])
            n_c = len(col)
            th = 2 * K * self.d_int[idx: idx + n_c]
            ph = 2 * K * self.d_ext[idx: idx + n_c]
            idx += n_c
            x, y = e[:, a] * torch.exp(1j * ph), e[:, b]          # external phase on upper arm
            u, v = s2 * (x + 1j * y), s2 * (1j * x + y)              # BS
            u = u * torch.exp(1j * th)                               # internal phase
            x2, y2 = s2 * (u + 1j * v), s2 * (1j * u + v)            # BS
            e = e.clone()
            e[:, a], e[:, b] = x2, y2
        return e * torch.exp(1j * 2 * K * self.d_out)

    def powers(self, amp: torch.Tensor) -> torch.Tensor:
        return self.fields(amp).abs() ** 2

    def forward(self, amp: torch.Tensor) -> torch.Tensor:
        return self.gain * self.powers(amp)[:, : self.c]

    def unitary(self) -> torch.Tensor:
        eye = torch.eye(self.n, dtype=torch.float64)
        return self.fields(eye).T  # column j = response to input mode j


def encode(x: torch.Tensor) -> torch.Tensor:
    """Features already scaled to [0,1] -> amplitudes with unit total power."""
    a = x.clamp(min=0) + 1e-6
    return a / a.norm(dim=1, keepdim=True)
