"""Verifica (--check) o regenera resultados/SHA256SUMS.txt.

Formato publicado: "hash  nombre" (dos espacios, como `sha256sum`); tambien se acepta "hash *nombre".
--check comprueba TODAS las lineas del archivo publicado contra los bytes de cada archivo.
Sin --check reescribe el archivo con los mismos nombres (y orden) del existente, en formato publicado.
"""
import hashlib, re, sys
from pathlib import Path

RES = Path(__file__).resolve().parent / "resultados"
LINE_RE = re.compile(r"^([0-9a-f]{64}) [ *](.+)$")


def parse_manifest(text):
    """Devuelve [(hash, nombre)] de todas las lineas no vacias; ValueError si alguna no tiene formato valido."""
    out = []
    for n, raw in enumerate(text.splitlines(), 1):
        if not raw.strip():
            continue
        m = LINE_RE.match(raw)
        if not m:
            raise ValueError("linea %d con formato invalido: %r" % (n, raw))
        out.append((m.group(1), m.group(2)))
    return out


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(res=RES):
    """Devuelve (total, lista_de_diferencias) sobre todas las lineas de SHA256SUMS.txt."""
    entries = parse_manifest((res / "SHA256SUMS.txt").read_text(encoding="utf-8"))
    bad = []
    for h, name in entries:
        f = res / name
        if not f.is_file():
            bad.append("%s: falta" % name)
        elif sha(f) != h:
            bad.append("%s: hash distinto" % name)
    return len(entries), bad


def write(res=RES):
    entries = parse_manifest((res / "SHA256SUMS.txt").read_text(encoding="utf-8"))
    body = "".join("%s  %s\n" % (sha(res / name), name) for _, name in entries)
    (res / "SHA256SUMS.txt").write_bytes(body.encode("utf-8"))
    return len(entries)


if __name__ == "__main__":
    if "--check" in sys.argv:
        total, bad = check()
        print("OK %d/%d" % (total, total) if not bad else "DIFIEREN (%d de %d): %s" % (len(bad), total, bad))
        raise SystemExit(1 if bad else 0)
    print("escritos %d hashes" % write())
