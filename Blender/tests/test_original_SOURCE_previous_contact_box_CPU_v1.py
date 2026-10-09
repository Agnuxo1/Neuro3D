"""New direction-box contact condition; no old contact/geometry suite replay."""
import copy
from fractions import Fraction as F
import itertools
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from Blender.benchmarks.capacity_audit import original_SOURCE_previous_contact_box_CPU_v1 as core

RECORDS = []
FALSE = ("native_point_budget_authenticated", "native_direction_budget_authenticated",
         "native_precision_certified", "launch_exclusion_allowed", "nearest_hit_certified",
         "GPU_launch_allowed", "phase_certified")


def corners(box):
    return itertools.product(*[[F(*lo), F(*hi)] for lo, hi in box])


def det(a, b, c):
    return (a[0]*(b[1]*c[2]-b[2]*c[1]) - b[0]*(a[1]*c[2]-a[2]*c[1])
            + c[0]*(a[1]*b[2]-a[2]*b[1]))


class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packets = core.retained_packets()

    def safe(self, result):
        for key in FALSE:
            self.assertIs(result[key], False)
        self.assertIsNone(result["phase_error_bound"])
        self.assertEqual(result["ignored_primitive_ids"], [])
        self.assertIs(result["origin_offset_applied"], False)
        self.assertEqual(result["full_costs"], "UNKNOWN_NOT_ZERO")

    def test_original_SOURCE_boxes_and_independent_Cramer_corners(self):
        bindings = set()
        for packet in self.packets:
            out = core.evaluate_packet(packet, model=core.MODEL)
            slot = packet["slot"]
            self.assertEqual(out["status"], "CPU_STRICT_PREVIOUS_CONTACT_ALL_DECLARED_DIRECTIONS_ONLY")
            self.assertIs(out["CPU_strict_interior_contact_for_all_directions"], True)
            self.safe(out)
            self.assertEqual(out["slot"], slot)
            self.assertNotEqual(out["direction_box"][0][0], out["direction_box"][0][1])
            a, b, c = [[core.ar.decode(w) for w in vertex] for vertex in slot["saved_triangle_words"]]
            e1, e2 = [[x-y for x, y in zip(vertex, a)] for vertex in (b, c)]
            checks = 0
            for p, d in itertools.product(corners(out["point_box"]), corners(out["direction_box"])):
                rhs = [x-y for x, y in zip(p, a)]
                denominator = det(e1, e2, d)
                self.assertNotEqual(denominator, 0)
                u, v = det(rhs, e2, d)/denominator, det(e1, rhs, d)/denominator
                t = -det(e1, e2, rhs)/denominator
                self.assertEqual(t, 0)
                self.assertTrue(all(x > 0 for x in (u, v, 1-u-v)))
                for value, interval in zip((u, v, 1-u-v), out["barycentric_intervals"]):
                    self.assertLessEqual(F(*interval[0]), value)
                    self.assertLessEqual(value, F(*interval[1]))
                checks += 1
            self.assertEqual(checks, 64)  # Repeated corners kept, not unique samples.
            bindings.add(out["CPU_packet_binding_sha256"])
            RECORDS.append(dict(kind="ORIGINAL_CAPTURE", case=slot["case"], source_id=slot["source_id"],
                                independent_corner_combinations=checks, result=out))
        self.assertEqual(len(bindings), 12)

    def test_new_conditional_controls_preserve_zero_denominator_and_uncertainty(self):
        p = next(p for p in self.packets if p["slot"]["case"] == "oblique" and p["slot"]["source_id"] == "S0")
        s = p["slot"]
        for kind, wanted in (("direction_cross_zero", "STOP_DIRECTION_PLANE_DENOMINATOR_ZERO_POSSIBLE"),
                             ("parallel", "STOP_DIRECTION_PLANE_DENOMINATOR_ZERO_POSSIBLE"),
                             ("point_normal_uncertainty", "STOP_POINT_BOX_NOT_IDENTICALLY_ON_PREVIOUS_PLANE"),
                             ("thin_normal_shift", "STOP_POINT_BOX_NOT_IDENTICALLY_ON_PREVIOUS_PLANE"),
                             ("vertex", "STOP_PREVIOUS_TRIANGLE_NOT_STRICT_INTERIOR"),
                             ("outside", "STOP_PREVIOUS_TRIANGLE_NOT_STRICT_INTERIOR"),
                             ("degenerate", "STOP_DEGENERATE_PLANE"),
                             ("tiny_nonzero_direction", "CPU_STRICT_PREVIOUS_CONTACT_ALL_DECLARED_DIRECTIONS_ONLY"),
                             ("tangent_box", "CPU_STRICT_PREVIOUS_CONTACT_ALL_DECLARED_DIRECTIONS_ONLY")):
            point, direction, tri = [copy.deepcopy(s[k]) for k in
                                     ("saved_point_bounds", "saved_direction_bounds", "saved_triangle_words")]
            if kind == "direction_cross_zero":
                direction[0] = [[-1, 1], [1, 1]]
            elif kind == "parallel":
                direction[0] = [[0, 1], [0, 1]]
            elif kind == "point_normal_uncertainty":
                point[0] = [[2**59-1, 2**59], [2**59+1, 2**59]]
            elif kind == "thin_normal_shift":
                point[0] = [[2**60+1, 2**60], [2**60+1, 2**60]]
            elif kind == "vertex":
                point[1] = point[2] = [[0, 1], [0, 1]]
            elif kind == "outside":
                point[1] = [[4, 1], [4, 1]]
            elif kind == "degenerate":
                tri = [copy.deepcopy(tri[0]) for _ in range(3)]
            elif kind == "tiny_nonzero_direction":
                direction[0] = [[-1, 2**60], [-1, 2**60]]
            elif kind == "tangent_box":
                point[1] = [[3, 4], [5, 4]]
                point[2] = [[1, 8], [3, 8]]
            result = core.condition(point, direction, tri, model=core.MODEL)
            self.assertEqual(result["status"], wanted)
            self.safe(result)
            RECORDS.append(dict(kind="SYNTHETIC_NEW_CONTROL_NOT_ORIGINAL", control=kind,
                                point=point, direction=direction, triangle=tri, result=result))

    def test_malformed_domains_and_closed_selectors(self):
        s = self.packets[0]["slot"]
        for kind in ("bool_rational", "noncanonical", "reverse", "shape", "missing",
                     "negative_zero_word", "subnormal_word", "nonfinite_word", "wrong_model"):
            p, d, tri = [copy.deepcopy(s[k]) for k in
                         ("saved_point_bounds", "saved_direction_bounds", "saved_triangle_words")]
            model = core.MODEL
            if kind == "bool_rational": p[0][0][1] = True
            elif kind == "noncanonical": p[0][0] = [2, 2]
            elif kind == "reverse": d[0].reverse()
            elif kind == "shape": d.append([[0, 1], [0, 1]])
            elif kind == "missing": d = None
            elif kind == "negative_zero_word": tri[0][1] = 0x80000000
            elif kind == "subnormal_word": tri[0][1] = 1
            elif kind == "nonfinite_word": tri[0][1] = 0x7f800000
            else: model = "implicit_native"
            with self.assertRaises(ValueError):
                core.condition(p, d, tri, model=model)
            RECORDS.append(dict(kind="MALFORMED_NEGATIVE", control=kind, status="REJECT"))
        for case, source, model in (("unknown", "S0", core.MODEL), ("oblique", "S2", core.MODEL),
                                     ("oblique", "S0", "implicit_native")):
            with self.assertRaises(ValueError):
                core.run(case, source, model=model)
            RECORDS.append(dict(kind="SELECTOR_NEGATIVE", case=case, source_id=source, status="REJECT"))

    def test_fixed_run_and_output_copy_isolation(self):
        got = core.run("oblique", "S0", model=core.MODEL)
        self.assertEqual(got["scope"], "FIXED_CAPTURE_CPU_CONTENT_ONLY_NOT_NATIVE")
        self.assertEqual(got["parent_receipt_sha256"], core.PSHA)
        self.safe(got)
        original = copy.deepcopy(self.packets[0])
        result = core.evaluate_packet(self.packets[0], model=core.MODEL)
        result["slot"]["saved_point_bounds"][0][0][0] = -1
        result["direction_box"][0][0][0] = 999
        self.assertEqual(self.packets[0], original)
        RECORDS.append(dict(kind="FIXED_RUN_AND_COPY_ISOLATION", status="PASS"))
        changed = copy.deepcopy(original)
        changed["slot"]["scene_sha256"] = "0"*64
        changed["CPU_packet_binding_sha256"] = core.packing.binding(changed)
        caller = core.evaluate_packet(changed, model=core.MODEL)
        self.assertIsNone(caller["parent_receipt_sha256"])
        self.assertEqual(caller["scope"], "CALLER_CONDITIONAL_CPU_CONTENT_ONLY")
        self.assertIs(caller["scene_authenticated"], False)
        self.safe(caller)
        RECORDS.append(dict(kind="CALLER_RESEALED_NOT_FIXED_PARENT", result=caller))


if __name__ == "__main__":
    outcome = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    print(json.dumps(dict(id="PRECISION-ORIGINAL-SOURCE-PREVIOUS-CONTACT-BOX-CPU-001",
                         status="PASS" if outcome.wasSuccessful() else "FAIL", tests=outcome.testsRun,
                         records=RECORDS, GPU_launch_allowed=False, launch_exclusion_allowed=False,
                         native_precision_certified=False, phase_error_bound=None,
                         full_costs="UNKNOWN_NOT_ZERO", old_contact_evaluator_replays=0), sort_keys=True))
    raise SystemExit(0 if outcome.wasSuccessful() else 1)
