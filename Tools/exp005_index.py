"""Genera Docs/EXP-005-INDICE.md: indice navegable de los documentos EXP-005.

El estado derivado (cuentas de PASS, STOP, NULL, FAIL, DEADLINE, UNKNOWN) es
orientativo: cuenta palabras de cada documento y no sustituye a su lectura.
Ningun dato de este indice es evidencia; la evidencia son los recibos y
protocolos congelados.
"""
import hashlib
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "Docs"
OUT = DOCS / "EXP-005-INDICE.md"
TOKENS = ("PASS", "STOP", "NULL", "FAIL", "DEADLINE", "UNKNOWN")
EXCLUDED = {"EXP-005-INDICE.md", "EXP-005-CIERRE.md"}


def classify(text):
    counts = Counter({t: len(re.findall(r"\b%s\b" % t, text)) for t in TOKENS})
    if sum(counts.values()) == 0:
        return "sin_marcador", counts
    dominant = counts.most_common(1)[0][0]
    return dominant.lower(), counts


def theme(name):
    parts = name[len("EXP-005-"):].rsplit(".", 1)[0].split("-")
    return "-".join(parts[:2]) if parts and parts[0] == "AXIAL" else parts[0]


def main():
    rows = []
    for path in sorted(p for p in DOCS.glob("EXP-005-*.md") if p.name not in EXCLUDED):
        text = path.read_text(encoding="utf-8", errors="replace")
        title = next((l[2:].strip() for l in text.splitlines() if l.startswith("# ")), path.stem)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()[:16]
        label, counts = classify(text)
        rows.append((path.name, title, digest, label, counts, theme(path.name)))
    themes = Counter(r[5] for r in rows)
    labels = Counter(r[3] for r in rows)
    out = []
    out.append("# Indice de documentos EXP-005")
    out.append("")
    out.append("Generado por `Tools/exp005_index.py`. Documentos indexados: %d." % len(rows))
    out.append("")
    out.append("> Aviso: el estado derivado cuenta palabras de cada documento (orientativo). No es evidencia; la evidencia son los recibos y protocolos congelados referidos en cada documento.")
    out.append("")
    out.append("## Resumen")
    out.append("")
    out.append("| Tema | Documentos |")
    out.append("|---|---:|")
    for t, n in themes.most_common():
        out.append("| %s | %d |" % (t, n))
    out.append("")
    out.append("| Estado derivado (marcador dominante) | Documentos |")
    out.append("|---|---:|")
    for l, n in labels.most_common():
        out.append("| %s | %d |" % (l, n))
    out.append("")
    out.append("## Tabla")
    out.append("")
    out.append("| Documento | Titulo | SHA-256 (16) | Estado derivado | PASS | STOP | NULL | FAIL | DEADLINE | UNKNOWN |")
    out.append("|---|---|---|---|---:|---:|---:|---:|---:|---:|")
    for name, title, digest, label, counts, _ in rows:
        cells = [str(counts[t]) for t in TOKENS[:6]]
        title_cell = title.replace("|", "/")
        out.append("| `%s` | %s | `%s` | %s | %s |" % (name, title_cell, digest, label, " | ".join(cells)))
    OUT.write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
    print("documentos=%d temas=%d salida=%s" % (len(rows), len(themes), OUT.name))
    return 0


if __name__ == "__main__":
    sys.exit(main())
