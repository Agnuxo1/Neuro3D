"""Captured-only join tests; no prior producer/evaluator imports or execution."""
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
from Blender.benchmarks.capacity_audit import original_SOURCE_candidate_total_phase_HOST_v1 as core

RECORDS = []


def iv(a, b=None):
    return [[F(x).numerator, F(x).denominator] for x in (a, a if b is None else b)]


class TestTotalPhase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows, cls.geometry, cls.overlays = core.retained()

    def inputs(self, case="tiny_gap_2m60"):
        rows = [r for r in self.rows if r["case"] == case and r["cycles_interval"] is not None]
        rows.sort(key=lambda r: r["source_id"])
        return copy.deepcopy(rows), {k: copy.deepcopy(self.geometry[case][k]) for k in ("scene", "request")}, copy.deepcopy(self.overlays[case])

    def call(self, rows, literal, overlay, expected=None, model=core.MODEL):
        return core.evaluate(rows, literal, overlay, expected_row_sha256s=expected if expected is not None else
                             [core.digest(r) for r in rows], model=model)

    def scope(self, out):
        for f in ("native_promotion_allowed", "GPU_launch_allowed", "GPU_used", "phase_certified",
                  "material_authenticated", "SOURCE_merged", "old_ideal_relative_interval_used"):
            self.assertIs(out[f], False)
        for k in ("native_phase_error_bound", "amplitude", "field", "power"):
            self.assertIsNone(out[k])
        self.assertEqual(out["promotion"], "STOP")
        self.assertEqual(out["original_scene_phase_status"], "UNKNOWN_NOT_ZERO")

    def check_formula(self, rows, overlay, out):
        p = [[F(*v) for v in r["cycles_interval"]] for r in rows]
        g = [[F(*v) for v in s["phase_interval_cycles"]] for s in overlay["sources"]]
        m = [F(*v) for v in overlay["material"]["phase_interval_cycles"]]
        expected = [(p[j][0]+g[j][0]+m[0], p[j][1]+g[j][1]+m[1]) for j in range(2)]
        expected += [(p[0][0]-p[1][1]+g[0][0]-g[1][1], p[0][1]-p[1][0]+g[0][1]-g[1][0])]
        self.assertEqual(len(out["diagnostics"]), 3)
        for bounds, d in zip(expected, out["diagnostics"]):
            self.assertEqual([F(*v) for v in d["interval_cycles"]], list(bounds))
            self.assertEqual(F(*d["HOST_midpoint_cycles"]), sum(bounds)/2)
            self.assertEqual(F(*d["conditional_HOST_radius_bound_rad"]), 4*(bounds[1]-bounds[0]))
            self.assertEqual(d["fits"], 4*(bounds[1]-bounds[0]) <= F(*d["literal_cap_rad"]))
        for j in range(2):
            values = [a+b+c for a, b, c in itertools.product(p[j], g[j], m)]
            self.assertEqual((min(values), max(values)), expected[j])
        values = [a-b+c-d for a, b, c, d in itertools.product(*p, *g)]
        self.assertEqual((min(values), max(values)), expected[2])
        self.scope(out)

    def test_fixed_scene_join_and_original_UNKNOWN(self):
        data = core.run(model=core.MODEL)
        self.assertEqual(data["upstream_STOP_rows_preserved"], 20)
        self.assertEqual(data["root_evaluations"], 0)
        for run in data["runs"]:
            rows, literal, overlay = self.inputs(run["case"])
            out = run["result"]
            self.scope(out)
            if run["mode"] == "ORIGINAL_UNKNOWN":
                self.assertEqual(out["status"], "STOP_ORIGINAL_PHASE_UNKNOWN")
                self.assertEqual(out["diagnostics"], [])
                self.assertIsNone(out["source_phase"])
            else:
                self.check_formula(rows, overlay, out)
                status = "CONDITIONAL_HOST_OVERLAY_CAPS_ONLY" if run["case"] == "tiny_gap_2m60" else "STOP_ALL_SOURCE_DIAGNOSTIC_CAP"
                self.assertEqual(out["status"], status)
                self.assertEqual(len(out["rows"]), 3 if run["case"] == "tiny_gap_2m60" else 0)
            RECORDS.append(dict(kind="FIXED_JOIN", **run))

    def test_common_material_never_cancels_SOURCE_budgets(self):
        rows, lit, overlay = self.inputs()
        base = self.call(rows, lit, overlay)
        overlay["material"]["phase_interval_cycles"] = iv(0, 1)
        out = self.call(rows, lit, overlay)
        self.check_formula(rows, overlay, out)
        self.assertEqual(out["diagnostics"][2], base["diagnostics"][2])
        self.assertIs(out["diagnostics"][2]["fits"], True)
        self.assertEqual(out["status"], "STOP_ALL_SOURCE_DIAGNOSTIC_CAP")
        self.assertEqual(out["rows"], [])
        RECORDS.append(dict(kind="COMMON_MATERIAL_ALL_SOURCE_STOP", result=out))
        for j in range(2):
            rows, lit, overlay = self.inputs()
            overlay["sources"][j]["phase_interval_cycles"] = iv(0, F(1, 8))
            out = self.call(rows, lit, overlay)
            self.check_formula(rows, overlay, out)
            self.assertEqual(out["status"], "STOP_ALL_SOURCE_DIAGNOSTIC_CAP")
            self.assertIs(out["diagnostics"][1-j]["fits"], True)
            self.assertIs(out["diagnostics"][2]["fits"], False)
            RECORDS.append(dict(kind="SEPARATE_SOURCE_UNCERTAINTY", source_id="S"+str(j), result=out))

    def test_declared_offset_and_copy_not_encoded(self):
        rows, lit, overlay = self.inputs()
        overlay["sources"][1]["phase_interval_cycles"] = iv(F(1, 8))
        overlay["material"]["phase_interval_cycles"] = iv(1000)
        before = copy.deepcopy((rows, lit, overlay))
        out = self.call(rows, lit, overlay)
        self.check_formula(rows, overlay, out)
        self.assertEqual(out["status"], "CONDITIONAL_HOST_OVERLAY_CAPS_ONLY")
        self.assertGreater(F(*out["diagnostics"][0]["HOST_midpoint_cycles"]), 1000)
        out["source_phase"][0]["record_id"] = "MUTATED"
        out["rows"][0]["interval_cycles"][0][0] = 999
        self.assertEqual((rows, lit, overlay), before)
        self.assertNotEqual(out["rows"], out["diagnostics"])
        RECORDS.append(dict(kind="OFFSET_COPY_CONTROL", result=self.call(rows, lit, overlay)))

    def test_inclusive_SOURCE_boundary_relative_STOP_and_output_capacity(self):
        rows, lit, overlay = self.inputs()
        cap = F(*lit["request"]["source_width_caps_rad"][0])
        width = F(*rows[0]["cycles_width"])
        for s in overlay["sources"]:
            s["phase_interval_cycles"] = iv(0, cap/4-width)
        out = self.call(rows, lit, overlay)
        self.check_formula(rows, overlay, out)
        self.assertEqual(out["status"], "STOP_RELATIVE_DIAGNOSTIC_CAP")
        self.assertEqual(out["rows"], [])
        for d in out["diagnostics"][:2]:
            self.assertIs(d["fits"], True)
            self.assertEqual(d["conditional_HOST_radius_bound_rad"], d["literal_cap_rad"])
        RECORDS.append(dict(kind="INCLUSIVE_SOURCE_CAP_RELATIVE_STOP", result=out))
        rows, lit, overlay = self.inputs()
        for s in overlay["sources"]:
            s["phase_interval_cycles"] = iv(F(1, 2**255-19))
        overlay["material"]["phase_interval_cycles"] = iv(F(1, 2**251-9))
        out = self.call(rows, lit, overlay)
        self.assertEqual(out["status"], "STOP_INPUT")
        self.assertEqual(out["reason"], "output_capacity512")
        self.assertEqual(out["rows"], [])
        self.scope(out)
        RECORDS.append(dict(kind="OUTPUT_CAPACITY512_STOP", result=out))

    def test_missing_identity_flags_and_closed_overlay_NEG(self):
        rows, lit, overlay = self.inputs()
        mutations = []
        for key in ("original_scene_sha256", "literal_request_sha256", "parent_receipt_sha256"):
            q = copy.deepcopy(overlay); q[key] = "0"*64
            mutations.append((key, rows, lit, q, None))
        for label, apply in [
            ("missing_SOURCE", lambda q: q["sources"].pop()),
            ("reordered_SOURCE", lambda q: q["sources"].reverse()),
            ("missing_phase", lambda q: q["sources"][0].pop("phase_interval_cycles")),
            ("unknown_phase", lambda q: q["sources"][0].update(phase_interval_cycles=None)),
            ("unknown_material", lambda q: q.update(material=None)),
            ("implicit_material_sign", lambda q: q["material"].update(profile="IMPLICIT_MINUS")),
            ("bool_primitive", lambda q: q["material"].update(primitive_id=True)),
            ("material_object", lambda q: q["material"].update(object_id="other")),
            ("cap_override", lambda q: q.update(source_width_caps_rad=iv(1))),
            ("bool_rational", lambda q: q["sources"][0].update(phase_interval_cycles=[[True, 1], [1, 1]])),
            ("reversed", lambda q: q["sources"][0].update(phase_interval_cycles=iv(1, 0))),
            ("canonical", lambda q: q["sources"][0].update(phase_interval_cycles=[[2, 2], [1, 1]])),
            ("capacity256", lambda q: q["sources"][0].update(phase_interval_cycles=iv(F(1, 2**256)))),
            ("magnitude", lambda q: q["material"].update(phase_interval_cycles=iv(1000001))),
            ("radians", lambda q: q.update(units={"phase": "rad", "cap": "rad"})),
            ("physical_assertion", lambda q: q.update(authentication="PHYSICAL_AUTHENTICATED")),
        ]:
            q = copy.deepcopy(overlay); apply(q)
            mutations.append((label, rows, lit, q, None))
        for f in core.FLAGS:
            r = copy.deepcopy(rows); r[0][f] = True
            mutations.append(("resealed_"+f, r, lit, overlay, None))
        r = copy.deepcopy(rows); r[0]["cycles_interval"] = iv(0)
        mutations.append(("changed_captured_row", r, lit, overlay, [core.digest(x) for x in rows]))
        r = copy.deepcopy(rows); r.reverse()
        mutations.append(("reordered_candidate_SOURCE", r, lit, overlay, None))
        r = copy.deepcopy(rows); r[0]["cycles_width"] = [0, 1]
        mutations.append(("resealed_inconsistent_width", r, lit, overlay, None))
        for label, r, l, q, expected in mutations:
            out = self.call(r, l, q, expected)
            self.assertEqual(out["status"], "STOP_INPUT", label)
            self.assertEqual(out["rows"], [], label)
            self.scope(out)
            RECORDS.append(dict(kind="INPUT_NEG", label=label, result=out))
        # Same scene but a different literal reference is not equivalent.
        r, l, q = self.inputs("oblique")
        cross = {k: copy.deepcopy(self.geometry["shared_ref1000"][k]) for k in ("scene", "request")}
        out = self.call(r, cross, q)
        self.assertEqual(out["status"], "STOP_INPUT")
        RECORDS.append(dict(kind="INPUT_NEG", label="same_scene_wrong_query", result=out))
        out = self.call(rows, lit, overlay, model="other")
        self.assertEqual(out["status"], "STOP_INPUT")
        RECORDS.append(dict(kind="INPUT_NEG", label="wrong_model", result=out))

    def test_capture_fail_closed(self):
        raw = b'{"status":"PASS"}'
        good = dict(rc=0, before_deadline=True, timed_out=False, stdout_bytes=len(raw),
                    stdout_sha256=hashlib.sha256(raw).hexdigest(),
                    stdout_zlib_base64=base64.b64encode(zlib.compress(raw)).decode())
        for key, val in (("rc", False), ("before_deadline", False), ("timed_out", True),
                         ("stdout_bytes", True), ("stdout_sha256", "0"*64)):
            t = copy.deepcopy(good); t[key] = val
            with self.assertRaises(ValueError) as cm:
                core.capture(dict(test_run=t), require_deadline=True)
            RECORDS.append(dict(kind="CAPTURE_NEG", label=key, error=str(cm.exception)))


if __name__ == "__main__":
    result = unittest.TextTestRunner(stream=sys.stderr).run(unittest.defaultTestLoader.loadTestsFromTestCase(TestTotalPhase))
    print(json.dumps(dict(id=core.ID, status="PASS" if result.wasSuccessful() else "FAIL",
        tests=result.testsRun, records=RECORDS, GPU_used=False, Bpy_used=False, RT_used=False,
        frozen_producer_replays=0, old_ideal_relative_interval_used=False,
        geometry_queries=0, root_evaluations=0, JEV="LOCAL_SECURITY_BLOCKED_NO_RETRY"), sort_keys=True))
    sys.exit(0 if result.wasSuccessful() else 1)
