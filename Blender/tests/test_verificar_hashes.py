import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Benchmarks" / "lineas-base" / "verificar_hashes.py"


def load():
    spec = importlib.util.spec_from_file_location("verificar_hashes_lb", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class VerificarHashesTest(unittest.TestCase):
    def test_verifica_todas_las_lineas_publicadas(self):
        vh = load()
        manifest = (vh.RES / "SHA256SUMS.txt").read_text(encoding="utf-8")
        published = [l for l in manifest.splitlines() if l.strip()]
        total, bad = vh.check()
        self.assertEqual(total, len(published))
        self.assertGreater(total, 39)
        self.assertEqual(bad, [])

    def test_formato_dos_espacios_y_asterisco(self):
        vh = load()
        h = "a" * 64
        self.assertEqual(vh.parse_manifest(h + "  x/y.json\n" + h + " *z.txt\n"), [(h, "x/y.json"), (h, "z.txt")])

    def test_detecta_hash_distinto_y_falta(self):
        vh = load()
        with tempfile.TemporaryDirectory() as d:
            res = Path(d)
            (res / "a.txt").write_bytes(b"hola")
            (res / "SHA256SUMS.txt").write_text("%s  a.txt\n%s  b.txt\n" % ("0" * 64, "1" * 64), encoding="utf-8")
            total, bad = vh.check(res)
            self.assertEqual(total, 2)
            self.assertEqual(len(bad), 2)


if __name__ == "__main__":
    unittest.main()
