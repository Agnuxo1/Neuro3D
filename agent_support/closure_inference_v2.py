"""Anytime-valid and equivalence inference to complement closure_statistics.

An e-process lets a protocol look at accumulating paired results and stop
early without inflating its type-I error (Ville's inequality). TOST makes the
equivalence claim explicit with a (1-2*alpha) interval.
"""
from __future__ import annotations

import math
from typing import Iterable, Sequence

import numpy as np
from scipy.stats import t as student_t


def paired_sign_eprocess(outcomes: Iterable[int], bets: Sequence[float] = (-0.5, -0.25, 0.25, 0.5)) -> dict:
    """Mixture betting e-process for H0: each discordant pair favors either method with p=1/2.

    outcomes holds +1 when only the candidate is correct and -1 when only the
    reference is correct; ties are excluded before calling. Each fixed bet gives
    a nonnegative martingale with mean one under H0 and their average is one too,
    so P(sup_t E_t >= 1/alpha) <= alpha. Exchangeable independent pairs are assumed.
    """
    x = list(outcomes)
    if any(v not in (-1, 1) or isinstance(v, bool) for v in x):
        raise ValueError("Outcomes must be +1 or -1 discordant pairs")
    lam = np.asarray(bets, dtype=float)
    if lam.ndim != 1 or not lam.size or np.any(lam == 0) or np.any(np.abs(lam) >= 1) or not np.isfinite(lam).all():
        raise ValueError("Bets must be finite, nonzero and inside (-1, 1)")
    wealth, path = np.ones(len(lam)), []
    for v in x:
        wealth *= 1+lam*v
        path.append(float(wealth.mean()))
    return {"discordant_pairs": len(x), "e_value": path[-1] if path else 1.0,
            "max_e_value": max(path, default=1.0), "path": path, "bets": lam.tolist(),
            "assumption": "Independent exchangeable discordant pairs; clustered units need a cluster-level e-process"}


def eprocess_decision(report: dict, alpha: float) -> str:
    """Reject once the running e-process has ever reached 1/alpha."""
    if not 0 < alpha < 1:
        raise ValueError("0 < alpha < 1 is required")
    return "REJECT_H0" if report["max_e_value"] >= 1/alpha else "NOT_REJECTED"


def tost_paired(differences: Iterable[float], margin: float, alpha: float = 0.05) -> dict:
    """Two one-sided t-tests for |mean difference| < margin on independent paired units."""
    d = np.asarray(list(differences), dtype=float)
    if d.ndim != 1 or len(d) < 3 or not np.isfinite(d).all():
        raise ValueError("At least three finite paired differences are required")
    if not math.isfinite(margin) or margin <= 0 or not 0 < alpha < 0.5:
        raise ValueError("A positive margin and 0 < alpha < 0.5 are required")
    n, mean = len(d), float(d.mean())
    se = float(d.std(ddof=1))/math.sqrt(n)
    if se == 0:
        inside = abs(mean) < margin
        return {"units": n, "mean_difference": mean, "interval": [mean, mean], "p_tost": 0.0 if inside else 1.0,
                "equivalent": inside, "alpha": alpha, "margin": margin, "note": "Zero variance; decision is exact for these values"}
    crit = float(student_t.ppf(1-alpha, n-1))
    lower, upper = mean-crit*se, mean+crit*se
    p_low = float(student_t.sf((mean+margin)/se, n-1))
    p_high = float(student_t.cdf((mean-margin)/se, n-1))
    return {"units": n, "mean_difference": mean, "interval": [lower, upper],
            "interval_level": 1-2*alpha, "p_tost": max(p_low, p_high),
            "equivalent": lower > -margin and upper < margin, "alpha": alpha, "margin": margin,
            "assumption": "Independent paired units; approximately normal mean difference"}
