import unittest
from exp005_nearest_audit import audit


class NearestAuditTests(unittest.TestCase):
    def test_failed_runtime_rejected(self):
        with self.assertRaisesRegex(ValueError, 'runtime'):
            audit({'passed': False})

    def test_missing_dispatch_rejected(self):
        with self.assertRaisesRegex(ValueError, 'dispatches'):
            audit({'passed': True, 'raw_cases': [], 'legacy_CE3': [], 'real_cases': []})


if __name__ == '__main__': unittest.main()
