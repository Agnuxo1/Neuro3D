"""New detector-residual norms only; captured path geometry is not replayed."""
import base64
import copy
from fractions import Fraction as F
import hashlib
import itertools
import json
from pathlib import Path
import sys
import unittest
import zlib

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from Blender.benchmarks.capacity_audit import original_SOURCE_detector_connection_residual_HOST_v1 as core

RECORDS = []


def pair(q):
    q = F(q)
    return [q.numerator, q.denominator]


def iv(a, b=None):
    return [pair(a), pair(a if b is None else b)]


def box(x, y=0, z=0):
    return [iv(x), iv(y), iv(z)]


def point(x, y=0, z=0):
    return [pair(x), pair(y), pair(z)]


class TestResidual(unittest.TestCase):
    def scope(self, out):
        for f in (*core.FLAGS, "native_promotion_allowed", "SOURCE_merged", "GPU_used", "Bpy_used", "RT_used"):
            self.assertIs(out[f], False)
        for f in ("original_detector_connection_budget_BU", "native_detector_error_bound_BU",
                  "native_phase_error_bound_rad", "amplitude", "field", "power", "source_phase", "material_phase"):
            self.assertIsNone(out[f])
        self.assertEqual(out["promotion"], "STOP")

    def check_norm(self, out):
        q = [[F(*v) for v in axis] for axis in out["candidate_Q_box_BU"]]
        d = [F(*v) for v in out["literal_detector_point_BU"]]
        r = out["residual"]
        differences = [(a-v, b-v) for (a, b), v in zip(q, d)]
        low = sum((0 if a <= 0 <= b else min(a*a, b*b) for a, b in differences), F(0))
        high = sum((max(a*a, b*b) for a, b in differences), F(0))
        self.assertEqual([F(*v) for v in r["squared_BU2"]], [low, high])
        for k in ("root_lower_certificate", "root_upper_certificate"):
            c = r[k]; s = F(*c["squared"]); n = c["floor_scaled_root"]
            self.assertEqual(c["fraction_bits"], 96)
            self.assertTrue(n*n*s.denominator <= s.numerator << 192 < (n+1)**2*s.denominator)
            self.assertTrue(F(*c["lower_BU"])**2 <= s <= F(*c["upper_BU"])**2)
        lo, hi = [F(*v) for v in r["length_BU"]]
        for corner in itertools.product(*q):
            s = sum(((a-b)**2 for a, b in zip(corner, d)), F(0))
            self.assertTrue(lo*lo <= s <= hi*hi)
        witness = [F(*v) for v in out["max_distance_box_witness_Q_BU"]]
        self.assertEqual(sum(((a-b)**2 for a, b in zip(witness, d)), F(0)), high)
        self.assertEqual(F(*out["max_distance_box_witness_squared_BU2"]), high)
        self.assertEqual(F(*out["conditional_geometric_Q_replacement_allowance_BU"]), hi)
        wlow = F(*out["wavelength_BU"][0])
        self.assertEqual(F(*out["conditional_Q_replacement_allowance_cycles"]), hi/wlow)
        self.assertEqual(F(*out["conditional_Q_replacement_allowance_rad"]), 8*hi/wlow)
        self.assertEqual(out["costs"], dict(new_interval_segment_norms=1, new_integer_root_certificates=2))
        self.assertIs(out["actual_Q_replaced"], False)
        self.assertIs(out["cap_budget_admitted"], False)
        self.scope(out)

    def test_fixed_new_detector_residuals_and_upstream_STOP(self):
        outputs = core.run(model=core.MODEL)
        counts = {}
        for out in outputs:
            counts[out["status"]] = counts.get(out["status"], 0)+1
            self.scope(out)
            self.assertEqual(out["upstream_ledger_status"], "STOP_UNRESOLVED_ALL_PRIMITIVES")
            if out["status"] == "CONDITIONAL_DETECTOR_RESIDUAL_ONLY":
                self.check_norm(out)
                self.assertIs(out["detector_point_in_candidate_box"], True)
                self.assertIs(out["ALL_candidate_box_points_equal_literal_detector"], False)
                self.assertGreater(F(*out["conditional_geometric_Q_replacement_allowance_BU"]), 0)
            else:
                self.assertNotIn("residual", out)
                self.assertEqual(out["costs"]["new_integer_root_certificates"], 0)
            RECORDS.append(dict(kind="FIXED_RESIDUAL_OR_STOP", result=out))
        self.assertEqual(counts, {"CONDITIONAL_DETECTOR_RESIDUAL_ONLY": 8, "STOP_UPSTREAM_NO_DETECTOR_RESIDUAL": 20})
        # Reference changes query but not a distance in BU. No relative-phase credit.
        by = {(o["case"], o["source_id"]): o for o in outputs if "residual" in o}
        for sid in ("S0", "S1"):
            self.assertEqual(by[("oblique", sid)]["residual"], by[("shared_ref1000", sid)]["residual"])
            self.assertNotEqual(by[("oblique", sid)]["query_sha256"], by[("shared_ref1000", sid)]["query_sha256"])

    def test_contains_is_not_ALL_and_reverse_triangle_controls(self):
        cases = [
            ("exact_singleton", box(1, 2, 3), point(1, 2, 3), iv(1), True, True, iv(0)),
            ("contains_but_NOT_ALL", [iv(-1, 1), iv(0), iv(0)], point(0), iv(1), True, False, iv(0, 1)),
            ("outside_point", [iv(2, 3), iv(0), iv(0)], point(0), iv(1), False, False, iv(2, 3)),
            ("pythagorean", box(3, 4), point(0), iv(2), False, False, iv(5)),
            ("tiny_below_root_grid", box(F(1, 2**97)), point(0), iv(F(1, 8)), False, False, iv(0, F(1, 2**96))),
            ("positive_variable_lambda", box(1), point(0), iv(1, 2), False, False, iv(1)),
            ("large_reference_irrelevant_to_BU", box(1000), point(999), iv(1), False, False, iv(1)),
        ]
        for label, q, d, w, contains, all_equal, distance in cases:
            out = core.enclose(q, d, w, source_id="S1", units="BU", model=core.MODEL)
            self.check_norm(out)
            self.assertEqual(out["residual"]["length_BU"], distance)
            self.assertIs(out["detector_point_in_candidate_box"], contains)
            self.assertIs(out["ALL_candidate_box_points_equal_literal_detector"], all_equal)
            RECORDS.append(dict(kind="RESIDUAL_CONTROL", label=label, result=out))
        # Fixed 1D P, Q and D have rational exact lengths; check both signs.
        for p, q, d in ((-4, 3, 0), (4, 3, 0), (0, -3, 2), (3, 0, 3)):
            out = core.enclose(box(q), point(d), iv(F(1, 8)), source_id="S0", units="BU", model=core.MODEL)
            length_difference = abs(F(q-p))-abs(F(d-p))
            self.assertLessEqual(abs(length_difference), F(*out["conditional_geometric_Q_replacement_allowance_BU"]))
            self.assertLessEqual(8*abs(length_difference)/F(1, 8), F(*out["conditional_Q_replacement_allowance_rad"]))
            self.check_norm(out)
            RECORDS.append(dict(kind="REVERSE_TRIANGLE_CONTROL", P_BU=p, result=out))

    def test_invalid_units_domain_rationals_wavelength_and_copy(self):
        good = dict(candidate_Q_box_BU=box(1), literal_detector_point_BU=point(0), wavelength_BU=iv(1),
                    source_id="S0", units="BU", model=core.MODEL)
        bad = [("zero_lambda", "wavelength_BU", iv(0)), ("cross_lambda", "wavelength_BU", iv(-1, 1)),
               ("negative_lambda", "wavelength_BU", iv(-2, -1)), ("reversed_lambda", "wavelength_BU", iv(2, 1)),
               ("source", "source_id", "S2"), ("source_bool", "source_id", True), ("units", "units", "meters"),
               ("model", "model", "other"), ("box3", "candidate_Q_box_BU", [iv(1)]),
               ("point3", "literal_detector_point_BU", [[0, 1]]),
               ("coordinate_domain", "candidate_Q_box_BU", box(1000001))]
        for label, v in (("bool", [True, 1]), ("float", [1.0, 1]), ("den_zero", [1, 0]),
                         ("noncanonical", [2, 2]), ("capacity128", [1, 2**128])):
            bad.append((label, "literal_detector_point_BU", [v, [0, 1], [0, 1]]))
        for label, key, val in bad:
            q = copy.deepcopy(good); q[key] = val
            with self.assertRaises(ValueError) as cm:
                core.enclose(**q)
            RECORDS.append(dict(kind="INPUT_NEG", label=label, error=str(cm.exception)))
        original = copy.deepcopy(good)
        out = core.enclose(**good)
        out["candidate_Q_box_BU"][0][0][0] = 999
        out["literal_detector_point_BU"][0][0] = 999
        self.assertEqual(good, original)
        RECORDS.append(dict(kind="COPY_CONTROL", status="PASS"))

    def test_source_query_native_flags_and_missing_context_NEG(self):
        rows, literals = core.retained()
        original = next(r for r in rows if r["case"] == "oblique" and r["source_id"] == "S0" and r["cycles_interval"] is not None)
        expected = core.digest(original)
        r = copy.deepcopy(original); r["source_id"] = "S1"
        with self.assertRaises(ValueError) as cm:
            core.compose(r, literals["oblique"], expected_row_sha256=expected, model=core.MODEL)
        RECORDS.append(dict(kind="BINDING_NEG", label="changed_SOURCE_digest", error=str(cm.exception)))
        for f in core.FLAGS:
            r = copy.deepcopy(original); r[f] = True
            with self.assertRaises(ValueError) as cm:
                core.compose(r, literals["oblique"], expected_row_sha256=core.digest(r), model=core.MODEL)
            RECORDS.append(dict(kind="BINDING_NEG", label="resealed_"+f, error=str(cm.exception)))
        for label, literal in (("same_scene_wrong_query", literals["shared_ref1000"]), ("missing_context", None)):
            with self.assertRaises(ValueError) as cm:
                core.compose(original, literal, expected_row_sha256=expected, model=core.MODEL)
            RECORDS.append(dict(kind="BINDING_NEG", label=label, error=str(cm.exception)))
        for key, val in (("origin_offset_applied", True), ("ignored_primitive_ids", [1]),
                         ("conditional_first_id", 0), ("SOURCE_merged", True), ("previous_primitive_id", True),
                         ("units", "meters"), ("source_phase", [0, 1])):
            r = copy.deepcopy(original); r[key] = val
            with self.assertRaises(ValueError) as cm:
                core.compose(r, literals["oblique"], expected_row_sha256=core.digest(r), model=core.MODEL)
            RECORDS.append(dict(kind="BINDING_NEG", label="resealed_"+key, error=str(cm.exception)))

    def test_capture_FAIL_closed(self):
        raw = b'{"status":"PASS"}'
        good = dict(rc=0, before_deadline=True, stdout_bytes=len(raw), stdout_sha256=hashlib.sha256(raw).hexdigest(),
                    stdout_zlib_base64=base64.b64encode(zlib.compress(raw)).decode())
        for key, val in (("rc", False), ("before_deadline", False), ("timed_out", True),
                         ("stdout_bytes", True), ("stdout_sha256", "0"*64)):
            c = copy.deepcopy(good); c[key] = val
            with self.assertRaises(ValueError) as cm:
                core.capture(dict(test_run=c), require_deadline=True)
            RECORDS.append(dict(kind="CAPTURE_NEG", label=key, error=str(cm.exception)))


if __name__ == "__main__":
    result = unittest.TextTestRunner(stream=sys.stderr).run(unittest.defaultTestLoader.loadTestsFromTestCase(TestResidual))
    print(json.dumps(dict(id=core.ID, status="PASS" if result.wasSuccessful() else "FAIL", tests=result.testsRun,
        records=RECORDS, GPU_used=False, Bpy_used=False, RT_used=False, frozen_producer_replays=0,
        old_root_replays=0, native_detector_connection_certified=False, JEV="LOCAL_SECURITY_BLOCKED_NO_RETRY"), sort_keys=True))
    sys.exit(0 if result.wasSuccessful() else 1)
