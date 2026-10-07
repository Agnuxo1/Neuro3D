"""New polynomial-box QA; does not replay retained triangle/contact producers."""
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
from Blender.benchmarks.capacity_audit import original_SOURCE_next_position_box_CPU_v1 as core

RECORDS = []


def qs(q):
    return [q.numerator, q.denominator]


def iv(lo, hi=None):
    return [qs(F(lo)), qs(F(lo if hi is None else hi))]


def vec(x, y=0, z=0):
    return [iv(x), iv(y), iv(z)]


def check_polynomial(test, row):
    """Independent Cartesian corners and Python binary64 RNE, no core math."""
    p = [[F(*q) for q in a] for a in row["point_box"]]
    d = [[F(*q) for q in a] for a in row["direction_box"]]
    ts = [F(*q) for q in row["parameter_interval"]]
    exact = [[F(*q) for q in a] for a in row["exact_ray_position_box_BU"]]
    modeled = [[F(*q) for q in a] for a in row["modeled_binary64_position_box_BU"]]
    values = [[] for _ in range(3)]
    rounded_values = [[] for _ in range(3)]
    for corner in itertools.product(*(p+d+[ts])):
        pp, dd, t = corner[:3], corner[3:6], corner[6]
        for j in range(3):
            q = pp[j]+t*dd[j]
            values[j].append(q)
            # Round the product then round the sum; explicitly NOT FMA.
            prod = F.from_float(float(t*dd[j]))
            result = F.from_float(float(pp[j]+prod))
            rounded_values[j].append(result)
            test.assertTrue(exact[j][0] <= q <= exact[j][1])
            test.assertTrue(modeled[j][0] <= result <= modeled[j][1])
    for j in range(3):
        test.assertEqual(exact[j], [min(values[j]), max(values[j])])
        test.assertLessEqual(modeled[j][0], exact[j][0])
        test.assertGreaterEqual(modeled[j][1], exact[j][1])
    test.assertIsNone(row["native_position_error_bound"])
    test.assertIsNone(row["length_reference_phase_bound"])
    for flag in ("native_precision_certified", "triangle_hit_certified", "nearest_hit_certified",
                 "launch_exclusion_allowed", "GPU_launch_allowed", "phase_certified",
                 "full_path_visibility_certified"):
        test.assertIs(row[flag], False)
    return 128


class TestPosition(unittest.TestCase):
    def test_fixed28_new_position_compositions(self):
        rows = core.run(model=core.MODEL)
        census = {}
        for row in rows:
            corners = check_polynomial(self, row)
            state = row["upstream_triangle_status"]
            census[state] = census.get(state, 0)+1
            self.assertEqual(row["upstream_ledger_status"], "STOP_UNRESOLVED_ALL_PRIMITIVES")
            self.assertIsNone(row["conditional_first_id"])
            self.assertEqual(row["parent_receipts"], {p: core.PINS[p] for p in (core.QUERY, core.TRIANGLE, core.LEDGER)})
            if state.startswith("STOP_"):
                self.assertEqual(row["parameter_interval"], iv(0))
                self.assertEqual(row["exact_ray_position_box_BU"], row["point_box"])
            RECORDS.append(dict(kind="FIXED_POSITION", corner_combinations=corners, result=row))
        self.assertEqual(census, {"CONDITIONAL_TRIANGLE_INTERIOR_HIT": 12,
                                  "STOP_TRIANGLE_CONTACT_OR_BOUNDARY_UNRESOLVED": 12,
                                  "CONDITIONAL_TRIANGLE_MISS": 4})

    def test_new_polynomial_controls(self):
        p, d = vec(1, 2, F(1, 4)), vec(-1, 1)
        direction_box = copy.deepcopy(d)
        direction_box[0] = iv(-2, -1)
        point_box = copy.deepcopy(p)
        point_box[1] = iv(1, 3)
        controls = [
            ("separate_rounding_tie", vec(1), vec(1), iv(F(1, 2**53))),
            ("direction_width", p, direction_box, iv(1)),
            ("point_width", point_box, d, iv(1)),
            ("negative_parameter_NO_forward_hit", p, d, iv(-2, -1)),
            ("zero_parameter_KEEPS_contact", point_box, d, iv(0)),
            ("positive_subnormal_parameter", vec(0), vec(1), iv(F(1, 2**1074))),
            ("unnormalized_parameter_NOT_length", vec(0), vec(3, 4), iv(2)),
            ("parameter_width", p, d, iv(F(1, 2), F(3, 2))),
        ]
        for label, pp, dd, tt in controls:
            result = core.enclose(pp, dd, tt, model=core.MODEL)
            count = check_polynomial(self, result)
            if label == "separate_rounding_tie":
                self.assertEqual(result["exact_ray_position_box_BU"][0], iv(1+F(1, 2**53)))
                self.assertNotEqual(result["modeled_binary64_position_box_BU"][0],
                                    result["exact_ray_position_box_BU"][0])
                error = F.from_float(float(1+F(1, 2**53)))-(1+F(1, 2**53))
                self.assertEqual(error, -F(1, 2**53))
            if label == "unnormalized_parameter_NOT_length":
                self.assertEqual(result["exact_ray_position_box_BU"], vec(6, 8))
                # Squared displacement 100 != tau^2=4. No square-root invocation.
                self.assertNotEqual(F(6)**2+F(8)**2, F(2)**2)
            RECORDS.append(dict(kind="CONTROL", label=label, corner_combinations=count, result=result))

    def test_caller_scope_copy_and_crossbindings(self):
        packets, tri, ledger = core.retained()
        p, c = packets[0], tri["cases"][0]
        s, l = c["sources"][0], ledger["cases"][0]["sources"][0]["result"]
        r = s["rows"][0]
        originals = copy.deepcopy((p, c, s, r, l))
        result = core.compose(p, c, s, r, l, model=core.MODEL)
        self.assertIsNone(result["parent_receipts"])
        self.assertEqual(result["scope"], "CALLER_CONDITIONAL_CPU_CONTENT_ONLY")
        check_polynomial(self, result)
        result["point_box"][0][0][0] = 999
        self.assertEqual((p, c, s, r, l), originals)
        RECORDS.append(dict(kind="CALLER_SCOPE_COPY", status="PASS"))
        def mutate(label, action):
            # Keep the supplied row independent from its purported source row.
            # deepcopy(tuple) preserves aliases and would mutate BOTH operands.
            pp, cc, ss, rr, ll = [copy.deepcopy(x) for x in originals]
            action(pp, cc, ss, rr, ll)
            with self.assertRaises(ValueError) as cm:
                core.compose(pp, cc, ss, rr, ll, model=core.MODEL)
            RECORDS.append(dict(kind="BINDING_NEG", label=label, error=str(cm.exception)))
        for k in ("case", "input_sha256", "scene_sha256", "query_sha256"):
            mutate(k, lambda p, c, s, r, l, key=k: c.update({key: "wrong"}))
        mutate("SOURCE", lambda p, c, s, r, l: s.update(source_id="S1"))
        mutate("point", lambda p, c, s, r, l: s.update(point_interval=vec(0)))
        mutate("direction", lambda p, c, s, r, l: s.update(reflected_direction_interval=vec(1)))
        mutate("previous", lambda p, c, s, r, l: s.update(previous_primitive_id=0))
        mutate("bool_primitive", lambda p, c, s, r, l: r.update(primitive_id=False))
        mutate("row", lambda p, c, s, r, l: r.update(triangle_words=[[0]*3]*3))
        mutate("ledger_binding", lambda p, c, s, r, l: l.update(binding=["0"]*4))
        mutate("coverage", lambda p, c, s, r, l: l.update(expected_ids=[0]))
        mutate("first_id", lambda p, c, s, r, l: l.update(conditional_first_id=0))
        mutate("ignored_previous", lambda p, c, s, r, l: l.update(ignored_primitive_ids=[1]))
        mutate("ledger_promoted", lambda p, c, s, r, l: l.update(status="CONDITIONAL_UNIQUE_FIRST_ON_DECLARED_LEDGER"))
        # Both row locations must be altered, otherwise row-binding fails first.
        mutate("parameter_units", lambda p, c, s, r, l:
               (r["result"].update(parameter_units="BU_length"),
                s["rows"][0]["result"].update(parameter_units="BU_length")))
        mutate("row_status", lambda p, c, s, r, l:
               (r["result"].update(status="NATIVE_PASS"),
                s["rows"][0]["result"].update(status="NATIVE_PASS")))

    def test_malformed_boxes_and_captures(self):
        good = [vec(1), vec(-1), iv(1)]
        bads = []
        for label, q in [("bool", [True, 1]), ("zero_den", [1, 0]),
                         ("noncanonical", [2, 2]), ("capacity", [1, 2**4096]),
                         ("outside_domain", [1000001, 1]), ("nonbinary64", [1, 3])]:
            args = copy.deepcopy(good); args[0][0][0] = q; bads.append((label, args, core.MODEL))
        args = copy.deepcopy(good); args[2] = iv(2, 1); bads.append(("reversed", args, core.MODEL))
        args = copy.deepcopy(good); args[1] = []; bads.append(("shape", args, core.MODEL))
        bads.append(("model", good, "other"))
        for label, args, model in bads:
            with self.assertRaises(ValueError) as cm:
                core.enclose(*args, model=model)
            RECORDS.append(dict(kind="INPUT_NEG", label=label, error=str(cm.exception)))
        raw = b'{}'
        valid = dict(rc=0, timed_out=False, stdout_bytes=2,
                     stdout_sha256=hashlib.sha256(raw).hexdigest(),
                     stdout_zlib_base64=base64.b64encode(zlib.compress(raw)).decode())
        for label, change in [("rc", dict(rc=1)), ("timeout", dict(timed_out=True)),
                              ("SHA", dict(stdout_sha256="0"*64)),
                              ("trailing", dict(stdout_zlib_base64=base64.b64encode(zlib.compress(raw)+b'x').decode()))]:
            cap = dict(valid, **change)
            with self.assertRaises(ValueError) as cm:
                core.capture({"test_run": cap}, "test_run")
            RECORDS.append(dict(kind="CAPTURE_NEG", label=label, error=str(cm.exception)))


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestPosition)
    result = unittest.TextTestRunner(stream=sys.stderr).run(suite)
    print(json.dumps(dict(id="PRECISION-ORIGINAL-SOURCE-NEXT-POSITION-BOX-CPU-001",
                          status="PASS" if result.wasSuccessful() else "FAIL", tests=result.testsRun,
                          records=RECORDS, old_triangle_queries=0, old_contact_evaluators=0,
                          old_roots=0, GPU_used=False, JEV="LOCAL_NO_REMOTE_ENDORSEMENT"), sort_keys=True))
    sys.exit(0 if result.wasSuccessful() else 1)
