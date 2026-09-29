"""Self-contained CPU tests of the augmented scattering ledger."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exp004_coherent_balance import scattering_audit


def source(fields, escape=None):
    return {"fields": fields, "escape": escape or {}}


class CoherentBalanceTests(unittest.TestCase):
    def test_identity_has_zero_gram_and_superposition_error(self):
        data = {"a": source({"A": [1, 0], "B": [0, 0]}),
                "b": source({"A": [0, 0], "B": [1, 0]})}
        result = scattering_audit(data)
        self.assertLess(result["max_gram_error"], 1e-12)
        self.assertLess(result["max_superposition_balance_error"], 1e-12)

    def test_escape_must_combine_coherently_by_channel(self):
        s = 2 ** -.5
        data = {"a": source({"A": [s, 0]}, {"open": [s, 0]}),
                "b": source({"A": [s, 0]}, {"open": [-s, 0]})}
        result = scattering_audit(data)
        self.assertLess(result["max_gram_error"], 1e-12)
        data["b"]["escape"]["open"] = [s, 0]
        broken = scattering_audit(data)
        self.assertGreater(broken["max_gram_error"], .9)
        self.assertGreater(broken["max_superposition_balance_error"], .9)

    def test_missing_escape_and_invalid_field_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "Missing"):
            scattering_audit({"a": {"fields": {"A": [1, 0]}},
                              "b": source({"B": [1, 0]})})
        with self.assertRaisesRegex(ValueError, "Non-finite"):
            scattering_audit({"a": source({"A": [float("nan"), 0]}),
                              "b": source({"B": [1, 0]})})


if __name__ == "__main__":
    unittest.main()
