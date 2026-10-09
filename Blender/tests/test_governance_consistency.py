"""Coherencia de la gobernanza: una sola fuente de verdad (Docs/GOVERNANCE.md).

Comprueba que las cifras publicas aparecen en el registro canonico, que el
indice EXP-005 cubre todos los documentos y que los enlaces canonicos existen.
Solo lee archivos del repositorio; no ejecuta experimentos.
"""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ACCEPTANCE = ROOT / "Docs/research/optic_neuro_blender_acceptance_v1.json"
PAPER = ROOT / "Docs/paper/optic_neuro_blender_reproducible_draft_2026-10-09.md"
README = ROOT / "README.md"
GOVERNANCE = ROOT / "Docs/GOVERNANCE.md"
INDEX = ROOT / "Docs/EXP-005-INDICE.md"
CLOSURE = ROOT / "Docs/EXP-005-CIERRE.md"
VALID_PREFIXES = ("OPEN", "PARTIAL_", "CAPTURED_", "OWN_", "COMPLETE_")

# (texto del README, forma normalizada que debe aparecer en el JSON o en el artículo, en su redaccion original)
README_CLAIMS = [
    ("133 estados", "133states"),
    ("186 aristas", "186edges"),
    ("17.060 caminos", "17060path"),
    ("104 objetos", "104opticalobjects"),
    ("27/30", "27/30"),
    ("137 etiquetas correctas", "137correct"),
    ("13 incorrectas", "13wrong"),
    ("150/150 decisiones", "150uniqueargmaxdecisions"),
]


def normalize(text):
    return re.sub(r"[\s.,]", "", text).lower()


class GovernanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.acceptance = json.loads(ACCEPTANCE.read_text(encoding="utf-8"))
        cls.paper = PAPER.read_text(encoding="utf-8")
        cls.readme = README.read_text(encoding="utf-8")
        cls.canonical_norm = normalize(ACCEPTANCE.read_text(encoding="utf-8") + cls.paper)

    def test_acceptance_has_ten_objectives_with_valid_status(self):
        priorities = self.acceptance["priorities"]
        self.assertEqual([p["id"] for p in priorities], list(range(1, 11)))
        for p in priorities:
            self.assertTrue(p["name"].strip())
            self.assertTrue(p["status"].startswith(VALID_PREFIXES), p["status"])
            if p["status"].startswith("COMPLETE_"):
                self.assertFalse(p.get("remaining", "").strip(), "COMPLETE con pendientes: %s" % p["id"])

    def test_readme_claims_appear_in_canonical_record(self):
        missing = []
        for shown, token in README_CLAIMS:
            if shown not in self.readme:
                missing.append("README sin '%s'" % shown)
            elif normalize(token) not in self.canonical_norm:
                missing.append("registro sin '%s'" % token)
        self.assertEqual(missing, [])

    def test_exp005_index_has_one_row_per_document(self):
        excluded = {"EXP-005-INDICE.md", "EXP-005-CIERRE.md"}
        documents = sorted(p.name for p in (ROOT / "Docs").glob("EXP-005-*.md") if p.name not in excluded)
        rows = re.findall(r"^\| `(EXP-005-[^`]+)` \|", INDEX.read_text(encoding="utf-8"), re.M)
        self.assertEqual(sorted(rows), documents)

    def test_governance_links_canonical_sources(self):
        text = GOVERNANCE.read_text(encoding="utf-8")
        for needle in ("optic_neuro_blender_acceptance_v1.json", "Docs/PATH_MAP.md",
                       "Docs/WORKSPACE.md", "EXP-005-CIERRE.md", "EXP-005-INDICE.md"):
            self.assertIn(needle, text)

    def test_readme_links_governance_and_closure(self):
        self.assertIn("Docs/GOVERNANCE.md", self.readme)
        self.assertIn("Docs/EXP-005-CIERRE.md", self.readme)

    def test_closure_document_states_closed(self):
        self.assertIn("CERRADA", CLOSURE.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
