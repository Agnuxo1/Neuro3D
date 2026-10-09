"""New chord norms on captured propagated boxes; no old position/trace replay."""
import copy
from fractions import Fraction as F
import itertools
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from Blender.benchmarks.capacity_audit import original_SOURCE_next_chord_length_CPU_v1 as core

RECORDS = []


def pair(q):
    q = F(q)
    return [q.numerator, q.denominator]


def iv(lo, hi=None):
    return [pair(lo), pair(lo if hi is None else hi)]


def point(x=0, y=0, z=0):
    return [iv(x), iv(y), iv(z)]


def check_norm(test, out):
    p = [[F(*q) for q in a] for a in out["point_box"]]
    q = [[F(*v) for v in a] for a in out["modeled_next_position_box_BU"]]
    components = []
    for a, b in zip(p, q):
        lo, hi = b[0]-a[1], b[1]-a[0]
        nearest = F(0) if a[0] <= b[1] and b[0] <= a[1] else min(abs(lo), abs(hi))
        farthest = max(abs(lo), abs(hi))
        components.append((nearest**2, farthest**2))
    sq = [sum((c[i] for c in components), F(0)) for i in range(2)]
    chord = out["chord"]
    test.assertEqual(chord["squared_BU2"], [pair(v) for v in sq])
    length = [F(*v) for v in chord["length_BU"]]
    test.assertTrue(0 <= length[0] <= length[1])
    test.assertLessEqual(length[0]**2, sq[0])
    test.assertGreaterEqual(length[1]**2, sq[1])
    for i, key in enumerate(("root_lower_certificate", "root_upper_certificate")):
        cert = chord[key]
        test.assertEqual(cert["fraction_bits"], 96)
        test.assertEqual(cert["squared"], pair(sq[i]))
        n, d = sq[i].numerator << 192, sq[i].denominator
        k = cert["floor_scaled_root"]
        test.assertLessEqual(k*k*d, n)
        test.assertLess(n, (k+1)*(k+1)*d)
        exact = k*k*d == n
        test.assertIs(cert["exact"], exact)
        test.assertEqual(cert["lower_BU"], pair(F(k, 2**96)))
        test.assertEqual(cert["upper_BU"], pair(F(k+int(not exact), 2**96)))
    for corner in itertools.product(*(p+q)):
        value = sum(((corner[j+3]-corner[j])**2 for j in range(3)), F(0))
        test.assertTrue(length[0]**2 <= value <= length[1]**2)
    test.assertEqual(out["costs"], dict(new_interval_segment_norms=1, new_integer_root_certificates=2))
    test.assertEqual(out["root_fraction_bits"], 96)
    test.assertIsNone(out["native_length_error_bound"])
    test.assertIsNone(out["length_reference_phase_bound"])
    for flag in ("native_precision_certified", "native_length_graph_certified", "length_accuracy_budget_admitted",
                 "nearest_hit_certified", "launch_exclusion_allowed", "GPU_launch_allowed", "phase_certified"):
        test.assertIs(out[flag], False)
    return 64


class TestLength(unittest.TestCase):
    def test_fixed28_lengths_from_propagated_boxes(self):
        rows = core.run(model=core.MODEL)
        census = {}
        for out in rows:
            count = check_norm(self, out)
            state = out["upstream_triangle_status"]
            census[state] = census.get(state, 0)+1
            self.assertEqual(out["upstream_ledger_status"], "STOP_UNRESOLVED_ALL_PRIMITIVES")
            self.assertIsNone(out["conditional_first_id"])
            self.assertEqual(out["parent_receipt_sha256"], core.PSHA)
            if state.startswith("STOP_"):
                self.assertEqual(out["chord"]["length_BU"], iv(0))
            if state == "CONDITIONAL_TRIANGLE_INTERIOR_HIT":
                lo, hi = [F(*v) for v in out["chord"]["length_BU"]]
                self.assertTrue(0 < lo < hi)
            RECORDS.append(dict(kind="FIXED_LENGTH", corner_combinations=count, result=out))
        self.assertEqual(census, {"CONDITIONAL_TRIANGLE_INTERIOR_HIT": 12,
                                  "STOP_TRIANGLE_CONTACT_OR_BOUNDARY_UNRESOLVED": 12,
                                  "CONDITIONAL_TRIANGLE_MISS": 4})

    def test_new_norm_controls(self):
        uncertain = point(); uncertain[0] = iv(-1, 1)
        overlapping = point(); overlapping[0] = iv(0, 2)
        controls = [
            ("three_four_five_NOT_tau", point(), point(6, 8)),
            ("uncertain_same_contact_NO_correlation_credit", uncertain, uncertain),
            ("component_zero_crossing", point(), uncertain),
            ("negative_coordinates", point(-3, -4), point()),
            ("tiny_gap_2m60_norm", point(), point(F(1, 2**60), F(1, 2**60))),
            ("root_granularity_2m97_kept", point(), point(F(1, 2**97))),
            ("point_transport_low_bit", point(1), point(1+F(1, 2**53))),
            ("boxes_overlap_lower_zero", uncertain, overlapping),
        ]
        for label, p, q in controls:
            out = core.enclose(p, q, model=core.MODEL)
            count = check_norm(self, out)
            if label == "three_four_five_NOT_tau":
                self.assertEqual(out["chord"]["length_BU"], iv(10))
            if label == "uncertain_same_contact_NO_correlation_credit":
                self.assertEqual(out["chord"]["length_BU"], iv(0, 2))
            if label == "root_granularity_2m97_kept":
                self.assertEqual(out["chord"]["length_BU"], iv(0, F(1, 2**96)))
                self.assertFalse(out["chord"]["root_upper_certificate"]["exact"])
            RECORDS.append(dict(kind="CONTROL", label=label, corner_combinations=count, result=out))

    def test_caller_scope_copy_and_STOP_promotion_negatives(self):
        row = core.retained()[0]
        old = copy.deepcopy(row)
        out = core.compose(row, model=core.MODEL)
        check_norm(self, out)
        self.assertIsNone(out["parent_receipt_sha256"])
        out["point_box"][0][0][0] = 999
        self.assertEqual(row, old)
        RECORDS.append(dict(kind="CALLER_SCOPE_COPY", status="PASS"))
        controls = [("ledger", "upstream_ledger_status", "CONDITIONAL_UNIQUE_FIRST_ON_DECLARED_LEDGER"),
                    ("first_id", "conditional_first_id", 0), ("ignored", "ignored_primitive_ids", [1]),
                    ("offset", "origin_offset_applied", True), ("model", "model", "other"),
                    ("position_status", "status", "NATIVE_PASS"),
                    ("triangle_status", "upstream_triangle_status", "NATIVE_PASS"),
                    ("SOURCE", "source_id", "S2"), ("primitive_bool", "primitive_id", False),
                    ("previous_bool", "previous_primitive_id", True)]
        controls += [(flag, flag, True) for flag in
                     ("native_precision_certified", "triangle_hit_certified", "nearest_hit_certified",
                      "launch_exclusion_allowed", "GPU_launch_allowed", "full_path_visibility_certified", "phase_certified")]
        for label, key, value in controls:
            bad = copy.deepcopy(old); bad[key] = value
            with self.assertRaises(ValueError) as cm:
                core.compose(bad, model=core.MODEL)
            RECORDS.append(dict(kind="PROMOTION_NEG", label=label, error=str(cm.exception)))

    def test_input_and_unchanged_root_capacity_limits(self):
        cases = []
        for label, value in [("bool", [True, 1]), ("noncanonical", [2, 2]), ("zero_den", [1, 0]),
                             ("capacity128", [1, 2**128]), ("subnormal_2m149_outside128", [1, 2**149]),
                             ("domain", [1000001, 1])]:
            p = point(); p[0][0] = value; cases.append((label, p, point(), core.MODEL))
        p = point(); p[0] = iv(2, 1); cases.append(("reversed", p, point(), core.MODEL))
        cases.append(("shape", [], point(), core.MODEL))
        cases.append(("model", point(), point(), "other"))
        # Inputs fit existing 128-bit cap; squared sum exceeds fixed 512-bit root cap.
        cases.append(("root_capacity512_retained", point(),
                      point(F(1, 2**127-1), F(1, 2**107-1), F(1, 2**89-1)), core.MODEL))
        for label, p, q, model in cases:
            with self.assertRaises(ValueError) as cm:
                core.enclose(p, q, model=model)
            if label == "root_capacity512_retained":
                self.assertEqual(str(cm.exception), "root_capacity")
            RECORDS.append(dict(kind="INPUT_NEG", label=label, error=str(cm.exception)))


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestLength)
    result = unittest.TextTestRunner(stream=sys.stderr).run(suite)
    print(json.dumps(dict(id="PRECISION-ORIGINAL-SOURCE-NEXT-CHORD-LENGTH-CPU-001",
                          status="PASS" if result.wasSuccessful() else "FAIL", tests=result.testsRun,
                          records=RECORDS, old_position_evaluator_replays=0, old_length_producer_replays=0,
                          old_geometry_queries=0, old_roots_replayed=0, GPU_used=False,
                          JEV="LOCAL_NO_REMOTE_ENDORSEMENT"), sort_keys=True))
    sys.exit(0 if result.wasSuccessful() else 1)
