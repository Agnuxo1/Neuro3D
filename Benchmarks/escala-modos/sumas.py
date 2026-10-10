"""Genera resultados/SHA256SUMS.txt (LF, rutas relativas a Benchmarks/escala-modos)."""
import hashlib
from pathlib import Path

root = Path(__file__).parent
files = sorted(p for p in root.rglob("*") if p.is_file() and "__pycache__" not in p.parts
               and p.name != "SHA256SUMS.txt" and p.suffix != ".pyc")
lines = [f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(root).as_posix()}" for p in files]
(root / "resultados" / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
print(len(lines), "archivos")
