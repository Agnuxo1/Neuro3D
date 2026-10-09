"""Integridad de la evidencia y del codigo del benchmark EEG (P0-3).

- Los manifiestos coinciden con los bytes de los archivos del repositorio.
- Si NEURO3D_EEG_RAW apunta a la carpeta nested/raw restaurada (full y seeds5),
  el analizador del repositorio reproduce byte a byte los JSON de la evidencia.
  Sin la variable la prueba se omite: los datos crudos no estan en git.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EEG = ROOT / "Benchmarks" / "eeg-motor-imagery"
EVID = EEG / "evidencia-validacion-anidada"
CODE = EEG / "codigo"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest_rows(path):
    for line in path.read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#"):
            yield line.split()


class ManifestTests(unittest.TestCase):
    def test_evidence_manifest_matches_bytes(self):
        bad = []
        for fields in manifest_rows(EVID / "MANIFEST-SHA256.txt"):
            digest, rel = fields[0], fields[2]
            if sha256(EVID / rel) != digest:
                bad.append(rel)
        self.assertEqual(bad, [])

    def test_code_copies_match_their_manifest(self):
        bad = []
        for fields in manifest_rows(CODE / "MANIFEST-SHA256.txt"):
            copy_digest, rel = fields[1], fields[3]
            if sha256(EEG / rel) != copy_digest:
                bad.append(rel)
        self.assertEqual(bad, [])


@unittest.skipUnless(os.environ.get("NEURO3D_EEG_RAW"), "NEURO3D_EEG_RAW no definida: datos crudos no incluidos")
class ReproductionTests(unittest.TestCase):
    def test_analysis_reproduces_recorded_json(self):
        raw = Path(os.environ["NEURO3D_EEG_RAW"])
        analyzer = CODE / "work" / "nested" / "analyze_nested.py"
        with tempfile.TemporaryDirectory(prefix="eeg-nested-") as tmp:
            work = Path(tmp) / "nested"
            work.mkdir()
            shutil.copy2(analyzer, work / "analyze_nested.py")
            for tag in ("full", "seeds5"):
                shutil.copytree(raw / tag, work / "raw" / tag)
            for tag in ("full", "seeds5"):
                run = subprocess.run([sys.executable, "analyze_nested.py", "--tag", tag],
                                     cwd=work, capture_output=True, text=True, timeout=600)
                self.assertEqual(run.returncode, 0, run.stderr[-500:])
                produced = json.loads((work / ("results_%s.json" % tag)).read_text(encoding="utf-8"))
                recorded = json.loads((EVID / ("results_%s.json" % tag)).read_text(encoding="utf-8"))
                self.assertEqual(produced, recorded, tag)


if __name__ == "__main__":
    unittest.main()
