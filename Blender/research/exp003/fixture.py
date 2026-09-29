"""OPT-015 (Claude): frozen EXP-003 fixture + analytic validator (pure Python, no Blender).

Single Mach-Zehnder cell. Arm 1 contains a roof delay line (R1, R2 at 90 deg):
moving the rigid pair by +d along x adds exactly 2d of path with no lateral
shift. Arm 2 is a single fold mirror. Units BU, lambda = 0.1.

  source (-1,0,0) --+x--> BS1 (0,0)
  arm1: BS1 -+x-> R1 (2,0) -+y-> R2 (2,0.5) --x-> F1 (1,0.5) -+y-> BS2 (1,2)
  arm2: BS1 -+y-> M2 (0,2) -+x-> BS2 (1,2)
  BS2 port A (+y) -> detector A (1,3);  port B (+x) -> detector B (2,2)
  L1 = 2 + 0.5 + 1 + 1.5 = 5.0 ; L2 = 2 + 1 = 3.0 ; L1 - L2 = 2.0 = 20 lambda -> base A dark.

Interventions (frozen by EXP-003): delay pair +d along x, d in {0, 0.0025, 0.005};
sham: pair +0.01 along z (tangent to both mirror planes); ablation: remove R2.
Run: python fixture.py  -> validates and writes fixture.json
"""

from __future__ import annotations

import json
import math
from pathlib import Path

LAMBDA = 0.1
S2 = 1 / math.sqrt(2)


def unit(v):
    n = math.sqrt(sum(x * x for x in v)); return tuple(x / n for x in v)


FIXTURE = {
    "lambda": LAMBDA, "frequency": 100.0, "propagation_speed": 10.0, "mutual_coherence": 1.0, "absorption": 0.0,
    "source": {"position": (-1.0, 0.0, 0.0), "direction": (1.0, 0.0, 0.0), "power": 1.0},
    "bs1": {"position": (0.0, 0.0, 0.0), "normal": unit((1, -1, 0)), "radius": 0.2, "transmission": 0.5},
    "r1": {"position": (2.0, 0.0, 0.0), "normal": unit((1, -1, 0)), "radius": 0.2},   # +x -> +y
    "r2": {"position": (2.0, 0.5, 0.0), "normal": unit((1, 1, 0)), "radius": 0.2},    # +y -> -x
    "f1": {"position": (1.0, 0.5, 0.0), "normal": unit((1, 1, 0)), "radius": 0.2},   # -x -> +y
    "m2": {"position": (0.0, 2.0, 0.0), "normal": unit((1, -1, 0)), "radius": 0.2},   # +y -> +x
    "bs2": {"position": (1.0, 2.0, 0.0), "normal": unit((1, -1, 0)), "radius": 0.2, "transmission": 0.5},
    "detector_a": {"position": (1.0, 3.0, 0.0), "radius": 0.15},
    "detector_b": {"position": (2.0, 2.0, 0.0), "radius": 0.15},
    "hit_order": {"arm1": ["bs1", "r1", "r2", "f1", "bs2"], "arm2": ["bs1", "m2", "bs2"]},
    "delay_pair": ["r1", "r2"],
    "interventions": {"delay_d": [0.0, 0.0025, 0.005], "sham_z": 0.01, "ablate": "r2"},
}


def reflect(d, n):
    k = 2 * sum(a * b for a, b in zip(d, n)); return unit(tuple(a - k * b for a, b in zip(d, n)))


def hit_plane(o, d, p, n, r):
    den = sum(a * b for a, b in zip(d, n))
    if abs(den) < 1e-12: return None
    t = sum((pi - oi) * ni for pi, oi, ni in zip(p, o, n)) / den
    if t <= 1e-9: return None
    h = tuple(oi + t * di for oi, di in zip(o, d))
    return (h, t) if math.dist(h, p) <= r + 1e-12 else None


def trace(fx, delay_d=0.0, sham_z=0.0, ablate=None):
    """Independent analytic trace. Returns per-arm hit log and lengths (None if a hit is lost)."""
    def obj(name):
        o = dict(fx[name])
        if name in fx["delay_pair"]:
            o["position"] = (o["position"][0] + delay_d, o["position"][1], o["position"][2] + sham_z)
        return o
    out = {}
    src = fx["source"]; h, t0 = hit_plane(src["position"], src["direction"], obj("bs1")["position"], obj("bs1")["normal"], obj("bs1")["radius"])
    for arm, start_dir in (("arm1", src["direction"]), ("arm2", reflect(src["direction"], obj("bs1")["normal"]))):
        o, d, L, log = h, start_dir, 0.0, []
        for name in fx["hit_order"][arm][1:]:
            if name == ablate:
                log.append((name, "removed")); L = None; break
            ob = obj(name); res = hit_plane(o, d, ob["position"], ob["normal"], ob["radius"])
            if res is None:
                log.append((name, "missed")); L = None; break
            o, seg = res; L += seg; log.append((name, tuple(round(x, 12) for x in o), round(seg, 12)))
            if name != "bs2": d = reflect(d, ob["normal"])
        out[arm] = {"length": L, "arrival_dir": d, "hits": log, "end": o}
    return out


def ports(tr, lam=LAMBDA):
    L1, L2 = tr["arm1"]["length"], tr["arm2"]["length"]
    if L1 is None or L2 is None:
        return None
    dphi = 2 * math.pi * (L1 - L2) / lam
    return {"P_A": math.sin(dphi / 2) ** 2, "P_B": math.cos(dphi / 2) ** 2, "delta_L": L1 - L2}


if __name__ == "__main__":
    base = trace(FIXTURE)
    assert abs(base["arm1"]["length"] - 5.0) < 1e-12 and abs(base["arm2"]["length"] - 3.0) < 1e-12
    assert math.dist(base["arm1"]["end"], FIXTURE["bs2"]["position"]) < 1e-12
    assert math.dist(base["arm2"]["end"], FIXTURE["bs2"]["position"]) < 1e-12
    assert math.dist(base["arm1"]["arrival_dir"], (0.0, 1.0, 0.0)) < 1e-12 and math.dist(base["arm2"]["arrival_dir"], (1.0, 0.0, 0.0)) < 1e-12
    pred = {}
    for d in FIXTURE["interventions"]["delay_d"]:
        tr = trace(FIXTURE, delay_d=d); p = ports(tr)
        assert abs((tr["arm1"]["length"] - base["arm1"]["length"]) - 2 * d) < 1e-12
        assert math.dist(tr["arm1"]["end"], FIXTURE["bs2"]["position"]) < 1e-12   # no lateral shift
        pred[f"d={d}"] = p
    sham = trace(FIXTURE, sham_z=FIXTURE["interventions"]["sham_z"])
    assert abs(sham["arm1"]["length"] - 5.0) < 1e-12
    abl = trace(FIXTURE, ablate="r2")
    assert abl["arm1"]["length"] is None and abs(abl["arm2"]["length"] - 3.0) < 1e-12
    fx = {k: v for k, v in FIXTURE.items()}
    fx["predictions"] = {**pred, "sham": ports(sham), "ablation": "arm1 lost at r2; single-arm: P_A = P_B = 0.25, escape = 0.5"}
    fx["sham_note"] = "z shift keeps hits on both roof planes; hit z = 0.01 is within radius 0.2 of the moved centres"
    Path(__file__).with_name("fixture.json").write_text(json.dumps(fx, indent=2))
    print(json.dumps(fx["predictions"], indent=1))
