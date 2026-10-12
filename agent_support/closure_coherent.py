"""Coherent reductions, exact roundoff diagnostics, and equivalent operators.

Greedy ordering is an experimental heuristic, not a constructive implementation
of the new Steinitz theorem. No routine changes optical signs or drops terms.
"""
from __future__ import annotations

import math
import struct
from fractions import Fraction
from typing import Callable, Iterable

import numpy as np


def finite_terms(values: Iterable[complex]) -> list[complex]:
    """Materialize finite complex terms so every method sees identical inputs."""
    values = [complex(v) for v in values]
    if not all(math.isfinite(v.real) and math.isfinite(v.imag) for v in values):
        raise ValueError("All complex terms must be finite")
    return values


def coherent_sum(values: Iterable[complex], method: str = "fsum") -> complex:
    """Reduce complex fields, with separate real and imaginary compensated sums."""
    terms = finite_terms(values)
    if method == "fsum":
        result = complex(math.fsum(v.real for v in terms), math.fsum(v.imag for v in terms))
    elif method == "pairwise":
        while len(terms) > 1:
            terms = [terms[i]+terms[i+1] for i in range(0, len(terms)-1, 2)] + terms[-1:]*(len(terms) % 2)
        result = terms[0] if terms else 0j
    elif method == "naive":
        result = sum(terms, 0j)
    else:
        raise ValueError("Supported methods: fsum, pairwise, naive")
    if not math.isfinite(result.real) or not math.isfinite(result.imag):
        raise ValueError("Reduction overflow is not a valid field")
    return result


def greedy_order(values: Iterable[complex], max_terms: int = 4096) -> list[int]:
    """Choose a diagnostic O(N^2) permutation minimizing the next prefix norm."""
    terms = finite_terms(values)
    if len(terms) > max_terms:
        raise ValueError("Greedy diagnostic exceeds its declared term budget")
    remaining, order, prefix = set(range(len(terms))), [], 0j
    while remaining:
        i = min(remaining, key=lambda j: (abs(prefix+terms[j]), j))
        remaining.remove(i)
        order.append(i)
        prefix += terms[i]
        if not math.isfinite(prefix.real) or not math.isfinite(prefix.imag):
            raise ValueError("Greedy prefix overflow exceeds the diagnostic domain")
    return order


def exact_roundoff_report(values: Iterable[complex], method: str = "fsum") -> dict:
    """Measure exact absolute reduction error for the represented binary64 terms."""
    terms = finite_terms(values)
    exact_real = sum((Fraction.from_float(v.real) for v in terms), Fraction(0))
    exact_imag = sum((Fraction.from_float(v.imag) for v in terms), Fraction(0))
    result = coherent_sum(terms, method)
    if not math.isfinite(result.real) or not math.isfinite(result.imag):
        raise ValueError("Reduction overflow is not a valid optical result")
    error = abs(Fraction.from_float(result.real)-exact_real)+abs(Fraction.from_float(result.imag)-exact_imag)
    prefix, largest = 0j, 0.0
    for term in terms:
        prefix += term
        largest = max(largest, abs(prefix))
    return {"method": method, "terms": len(terms), "field": [result.real, result.imag],
            "exact_real": str(exact_real), "exact_imag": str(exact_imag),
            "observed_reduction_error_L1_exact": str(error), "maximum_naive_prefix_norm": largest,
            "scope": "Reduction of supplied represented terms only; phase, geometry, and physical errors are excluded"}


def pack_complex64(values: Iterable[complex]) -> bytes:
    """Serialize coherent channels as little-endian binary64 real/imaginary pairs."""
    return b"".join(struct.pack("<dd", v.real, v.imag) for v in finite_terms(values))


def unpack_complex64(payload: bytes) -> list[complex]:
    """Decode a complete native channel packet and reject invalid or partial data."""
    if len(payload) % 16:
        raise ValueError("A complex binary64 packet needs a multiple of sixteen bytes")
    return finite_terms(complex(r, i) for r, i in struct.iter_unpack("<dd", payload))


def first_trace_divergence(reference: list[dict], candidate: list[dict], tolerance: float) -> dict | None:
    """Locate the first mismatched state/component in identically ordered traces."""
    if tolerance < 0 or not math.isfinite(tolerance):
        raise ValueError("A finite nonnegative tolerance is required")
    if len(reference) != len(candidate):
        return {"reason": "TRACE_LENGTH", "reference": len(reference), "candidate": len(candidate)}
    for index, (a, b) in enumerate(zip(reference, candidate)):
        if a["state_id"] != b["state_id"]:
            return {"reason": "STATE_IDENTITY", "index": index}
        if set(a["components"]) != set(b["components"]):
            return {"reason": "COMPONENT_IDENTITY", "state_id": a["state_id"]}
        for name in sorted(a["components"]):
            x, y = complex(*a["components"][name]), complex(*b["components"][name])
            if not all(math.isfinite(v) for v in (x.real, x.imag, y.real, y.imag)):
                return {"reason": "NONFINITE_COMPONENT", "state_id": a["state_id"], "component": name}
            error = abs(x-y)
            if error > tolerance:
                return {"reason": "COMPONENT_ERROR", "state_id": a["state_id"], "component": name, "error": error}
    return None


def compile_operator(forward: Callable[[np.ndarray], np.ndarray], input_dimension: int) -> np.ndarray:
    """Compile a fixed linear geometry operator by one forward call per basis input.

    The caller must independently validate linearity, geometry/cache identity,
    source ordering, and forward completeness before using this optimization.
    """
    if input_dimension < 1:
        raise ValueError("A positive input dimension is required")
    basis = np.eye(input_dimension, dtype=np.complex128)
    columns = [np.asarray(forward(basis[i]), dtype=np.complex128) for i in range(input_dimension)]
    if any(c.ndim != 1 or not c.size or c.shape != columns[0].shape or not np.isfinite(c).all() for c in columns):
        raise ValueError("Every basis response must be a complete finite modal vector")
    return np.column_stack(columns)


def apply_operator(operator: np.ndarray, inputs: np.ndarray) -> np.ndarray:
    """Evaluate equivalent fixed-geometry modal fields with optimized matrix work."""
    u, x = np.asarray(operator, dtype=np.complex128), np.asarray(inputs, dtype=np.complex128)
    if u.ndim != 2 or x.ndim != 2 or x.shape[1] != u.shape[1] or not np.isfinite(u).all() or not np.isfinite(x).all():
        raise ValueError("Finite (modes, sources) and (samples, sources) arrays are required")
    result = x @ u.T  # The optical operator is linear, not conjugate-linear.
    if not np.isfinite(result).all():
        raise ValueError("Operator evaluation overflow is not a valid field")
    return result
