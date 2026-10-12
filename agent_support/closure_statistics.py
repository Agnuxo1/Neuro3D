"""Paired inference with explicit independent-unit and overlap assumptions."""
from __future__ import annotations

import math
from typing import Iterable

import numpy as np
from scipy.stats import t as student_t


def differences(candidate: Iterable[float], reference: Iterable[float]) -> np.ndarray:
    """Validate paired accuracy values and return candidate-minus-reference."""
    a, b = np.asarray(list(candidate), dtype=float), np.asarray(list(reference), dtype=float)
    if a.ndim != 1 or a.shape != b.shape or len(a) < 2:
        raise ValueError("At least two matched experimental units are required")
    if not np.isfinite(a).all() or not np.isfinite(b).all() or np.any((a < 0)|(a > 1)) or np.any((b < 0)|(b > 1)):
        raise ValueError("Accuracy values must be finite and in [0, 1]")
    return a-b


def paired_bootstrap(candidate, reference, *, seed: int = 0, draws: int = 10000, alpha: float = 0.05) -> dict:
    """Bootstrap paired independent units; do not pass overlapping split scores."""
    d = differences(candidate, reference)
    if draws < 1000 or not 0 < alpha < 1:
        raise ValueError("At least 1000 draws and 0 < alpha < 1 are required")
    rng = np.random.default_rng(seed)
    means = np.empty(draws)
    for begin in range(0, draws, 512):
        end = min(draws, begin+512)
        means[begin:end] = d[rng.integers(0, len(d), size=(end-begin, len(d)))].mean(axis=1)
    lo, hi = np.quantile(means, [alpha/2, 1-alpha/2])
    return {"units": len(d), "mean_difference": float(d.mean()), "interval": [float(lo), float(hi)],
            "alpha": alpha, "seed": seed, "draws": draws,
            "wins": int((d > 0).sum()), "ties": int((d == 0).sum()), "losses": int((d < 0).sum()),
            "assumption": "Paired exchangeable independent units; subjects or independent datasets, not overlapping train/test splits"}


def corrected_resampled_interval(candidate, reference, *, test_train_ratio: float, alpha: float = 0.05) -> dict:
    """Approximate overlap-corrected t interval for repeated holdout differences."""
    d = differences(candidate, reference)
    if not math.isfinite(test_train_ratio) or test_train_ratio <= 0 or not 0 < alpha < 1:
        raise ValueError("A positive finite test/train ratio and 0 < alpha < 1 are required")
    variance = float(d.var(ddof=1))
    error = math.sqrt((1/len(d)+test_train_ratio)*variance)
    radius = float(student_t.ppf(1-alpha/2, len(d)-1))*error
    mean = float(d.mean())
    return {"units": len(d), "mean_difference": mean, "interval": [mean-radius, mean+radius],
            "standard_error": error, "alpha": alpha, "test_train_ratio": test_train_ratio,
            "scope": "Nadeau-Bengio-style approximate correction; not a substitute for external independent data"}


def holm_adjust(p_values: Iterable[float]) -> list[float]:
    """Return monotone Holm-adjusted p-values in the original hypothesis order."""
    values = [float(p) for p in p_values]
    if not values or not all(math.isfinite(p) and 0 <= p <= 1 for p in values):
        raise ValueError("Finite p-values in [0, 1] are required")
    order = sorted(range(len(values)), key=values.__getitem__)
    adjusted, previous = [0.0]*len(values), 0.0
    for rank, i in enumerate(order):
        previous = max(previous, min(1.0, (len(values)-rank)*values[i]))
        adjusted[i] = previous
    return adjusted


def comparison_label(interval: Iterable[float], margin: float) -> str:
    """Classify an interval with equivalence checked before directional effects."""
    values = list(interval)
    if len(values) != 2 or not all(math.isfinite(float(x)) for x in values) or values[0] > values[1] or not math.isfinite(margin) or margin <= 0:
        raise ValueError("An ordered finite interval and a positive margin are required")
    lo, hi = values
    if lo >= -margin and hi <= margin:
        return "EQUIVALENT_WITHIN_MARGIN"
    if lo > 0:
        return "POSITIVE_DIFFERENCE"
    if hi < 0:
        return "NEGATIVE_DIFFERENCE"
    return "INCONCLUSIVE"


def exact_mcnemar(candidate_correct: Iterable[bool], reference_correct: Iterable[bool]) -> dict:
    """Compute an exact paired binomial test on the same independent examples."""
    a, b = list(candidate_correct), list(reference_correct)
    if not a or len(a) != len(b) or any(type(x) is not bool for x in a+b):
        raise ValueError("Matched nonempty Boolean correctness arrays are required")
    wins = sum(x and not y for x, y in zip(a, b))
    losses = sum(y and not x for x, y in zip(a, b))
    n = wins+losses
    p = min(1.0, 2*sum(math.comb(n, k) for k in range(min(wins, losses)+1))/(1 << n)) if n else 1.0
    return {"candidate_only_correct": wins, "reference_only_correct": losses, "p_two_sided": p,
            "scope": "Independent paired examples; clustered observations require a cluster-level analysis"}
