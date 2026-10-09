"""Escribe resultados/SHA256SUMS.txt (o con --check verifica contra el existente)."""
import hashlib, sys
from pathlib import Path

RES = Path(__file__).resolve().parent / "resultados"
NAMES = (["RESULTADOS.json", "RESULTADOS.md", "RESULTADOS_EXTENSION.json", "RESULTADOS_EXTENSION.md", "SENSIBILIDAD_IRIS.json", "SENSIBILIDAD_IRIS.md",
          "splits.json", "baselines.json", "optical_iris.json"] + ["optical_wine_k%d.json" % k for k in range(10)])


def files():
    out = [RES / n for n in NAMES if (RES / n).exists()]
    return out + sorted((RES / "extension").glob("*.json"))


def line(f):
    return "%s *%s" % (hashlib.sha256(f.read_bytes()).hexdigest(), f.relative_to(RES).as_posix())


if __name__ == "__main__":
    sums = RES / "SHA256SUMS.txt"
    if "--check" in sys.argv:
        bad = [l for l in sums.read_text().splitlines() if l not in {line(f) for f in files()}]
        print("OK" if not bad else "DIFIEREN: %s" % bad)
        raise SystemExit(1 if bad else 0)
    sums.write_text("\n".join(line(f) for f in files()) + "\n", encoding="utf-8")
    print("escritos %d hashes" % len(files()))
