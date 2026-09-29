"""Independent coherent channel audit for measured EXP-004 fields.

Reads stored complex detector and escape amplitudes. It tests the full
augmented scattering matrix, not just each basis input's power. Escape
channels must carry stable physical identifiers across all sources.
No thresholds are chosen here and no result is promoted to PASS.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
import sys


def _complex(value):
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise ValueError("Expected complex [real, imag]")
    z = complex(*value)
    if not math.isfinite(z.real) or not math.isfinite(z.imag):
        raise ValueError("Non-finite measured field")
    return z


def scattering_audit(per_source):
    if not per_source or len(per_source) < 2:
        raise ValueError("Need at least two source modes")
    sources = tuple(sorted(per_source))
    channels = set()
    columns = {}
    for source in sources:
        record = per_source[source]
        if not {"fields", "escape"}.issubset(record):
            raise ValueError("Missing detector or escape fields")
        col = {}
        for kind in ("fields", "escape"):
            for name, value in record[kind].items():
                key = (kind, name)
                col[key] = _complex(value)
                channels.add(key)
        columns[source] = col
    channels = tuple(sorted(channels))
    if not channels:
        raise ValueError("No measured channels")
    gram = {}
    worst_pair = None
    max_error = -1.0
    for a in sources:
        for b in sources:
            inner = sum(columns[a].get(key, 0j).conjugate() *
                        columns[b].get(key, 0j) for key in channels)
            gram[(a, b)] = inner
            error = abs(inner - (1 if a == b else 0))
            if error > max_error:
                max_error, worst_pair = error, (a, b)
    worst_superposition = None
    max_superposition_error = -1.0
    for i, a in enumerate(sources):
        for b in sources[i + 1:]:
            for phase in (1 + 0j, 1j):
                power = sum(abs((columns[a].get(key, 0j) +
                                 phase * columns[b].get(key, 0j)) /
                                math.sqrt(2)) ** 2 for key in channels)
                error = abs(power - 1.0)
                if error > max_superposition_error:
                    max_superposition_error = error
                    worst_superposition = (a, b, "1" if phase == 1 else "i")
    return {"sources": len(sources), "channels": len(channels),
            "max_gram_error": max_error, "worst_gram_pair": worst_pair,
            "max_superposition_balance_error": max_superposition_error,
            "worst_superposition": worst_superposition,
            "max_basis_balance_error": max(
                abs(gram[(s, s)] - 1) for s in sources)}


if __name__ == "__main__":
    for argument in sys.argv[1:]:
        path = Path(argument)
        saved = json.loads(path.read_text(encoding="utf-8"))
        result = scattering_audit(saved["post"]["per_source"])
        print(json.dumps({"file": str(path), **result}, sort_keys=True))
