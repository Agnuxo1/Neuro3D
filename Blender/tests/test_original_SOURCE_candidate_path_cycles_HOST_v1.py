"""New geometric composition, captured next chord only; no trace/phase replay."""
import copy
import base64
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
from Blender.benchmarks.capacity_audit import original_SOURCE_candidate_path_cycles_HOST_v1 as core

RECORDS = []


def pair(q):
    q = F(q)
    return [q.numerator, q.denominator]


def iv(a, b=None):
    return [pair(a), pair(a if b is None else b)]


def check_cycles(t, out):
    l, r, w = [[F(*x) for x in out[k]] for k in ("length_BU", "reference_BU", "wavelength_BU")]
    lo, hi = [F(*x) for x in out["cycles_interval"]]
    values = [(a-b)/c for a, b, c in itertools.product(l, r, w)]
    t.assertEqual((lo, hi), (min(values), max(values)))
    t.assertEqual(out["cycles_width"], pair(hi-lo))
    t.assertEqual(out["length_minus_reference_BU"], [pair(l[0]-r[1]), pair(l[1]-r[0])])
    for f in core.FLAGS:
        t.assertIs(out[f], False)
    for k in ("phase_error_bound", "source_phase", "material_phase", "amplitude", "field", "power"):
        t.assertIsNone(out[k])
    t.assertIs(out["SOURCE_merged"], False)
    t.assertEqual(out["result_units"], "unwrapped_cycles_NOT_radians")
    return 8


class TestCycles(unittest.TestCase):
    def test_fixed_scene_candidate_PATH_composition_and_STOPs(self):
        outputs = core.run(model=core.MODEL)
        counts = {}
        for out in outputs:
            counts[out["status"]] = counts.get(out["status"], 0)+1
            self.assertEqual(out["upstream_ledger_status"], "STOP_UNRESOLVED_ALL_PRIMITIVES")
            self.assertIsNone(out["conditional_first_id"])
            self.assertEqual(out["parent_receipts_sha256"], core.PARENTS)
            if out["cycles_interval"] is not None:
                check_cycles(self, out)
                first = out["new_first_segment"]
                a, b = [[list(map(lambda v: F(*v), axis)) for axis in out[k]]
                        for k in ("source_origin_box_BU", "previous_point_box_BU")]
                flo, fhi = map(lambda v: F(*v), first["length_BU"])
                for corner in itertools.product(*(a+b)):
                    sq = sum(((corner[j+3]-corner[j])**2 for j in range(3)), F(0))
                    self.assertTrue(flo*flo <= sq <= fhi*fhi)
                for key in ("root_lower_certificate", "root_upper_certificate"):
                    c = first[key]; q = F(*c["squared"]); k = c["floor_scaled_root"]
                    self.assertTrue(k*k*q.denominator <= q.numerator << 192 < (k+1)**2*q.denominator)
                    self.assertEqual(c["fraction_bits"], 96)
                last = list(map(lambda v: F(*v), out["retained_next_segment_length_BU"]))
                self.assertEqual(out["length_BU"], [pair(flo+last[0]), pair(fhi+last[1])])
                self.assertGreater(F(*out["cycles_width"]), 0)
                self.assertEqual(out["costs"], dict(new_interval_segment_norms=1, new_integer_root_certificates=2))
                self.assertIs(out["old_ideal_lengths_used"], False)
                self.assertIs(out["first_leg_native_ALU_certified"], False)
                self.assertIs(out["detector_connection_certified"], False)
                if out["case"] == "shared_ref1000":
                    self.assertEqual(out["reference_BU"], iv(1000))
                    self.assertLess(F(*out["cycles_interval"][1]), 0)
            else:
                self.assertNotIn("new_first_segment", out)
            RECORDS.append(dict(kind="FIXED_PATH_OR_STOP", result=out))
        self.assertEqual(counts, {"CONDITIONAL_GEOMETRIC_PATH_CYCLES_ONLY": 8,
                                  "STOP_NO_CONDITIONAL_FORWARD_PATH": 16,
                                  "STOP_MISSING_LITERAL_REFERENCE_WAVELENGTH_CONTEXT": 4})
        # Same geometry, genuinely different request: preserve reference shift.
        by = {(x["case"], x["source_id"]): x for x in outputs if x["cycles_interval"] is not None}
        for sid in ("S0", "S1"):
            for i in range(2):
                self.assertEqual(F(*by[("oblique", sid)]["cycles_interval"][i])-
                                 F(*by[("shared_ref1000", sid)]["cycles_interval"][i]), 8000)
        self.assertNotEqual(by[("oblique", "S0")]["cycles_interval"], by[("oblique", "S1")]["cycles_interval"])

    def test_quotient_controls_sign_positive_wave_and_no_modulo(self):
        controls = [
            ("positive_delta_variable_wave", iv(10, 12), iv(1, 2), iv(2, 4), iv(2, F(11, 2))),
            ("negative_delta_variable_wave", iv(1, 2), iv(10, 12), iv(2, 4), iv(F(-11, 2), -2)),
            ("zero_crossing_delta", iv(1, 3), iv(2), iv(1, 2), iv(-1, 1)),
            ("large_reference_NO_modulo", iv(3), iv(1000), iv(F(1, 8)), iv(-7976)),
            ("tiny_gap_finite_resolution_kept", iv(0, F(1, 2**96)), iv(0), iv(F(1, 8)), iv(0, F(1, 2**93))),
            ("SOURCE_reference_budget_nonzero", iv(5, 6), iv(1, 3), iv(1), iv(2, 5)),
            ("distinct_SOURCE1_wavelength", iv(5, 6), iv(1, 3), iv(2), iv(1, F(5, 2))),
            ("zero_geometric_length", iv(0), iv(0), iv(F(1, 2**127)), iv(0)),
        ]
        for label, l, r, w, expected in controls:
            sid = "S1" if label == "distinct_SOURCE1_wavelength" else "S0"
            out = core.enclose(l, r, w, source_id=sid, units="BU",
                               reference_scope="GEOMETRIC_TWO_SEGMENT_PATH", model=core.MODEL)
            check_cycles(self, out)
            self.assertEqual(out["cycles_interval"], expected)
            self.assertIsNone(out["parent_receipts_sha256"])
            RECORDS.append(dict(kind="QUOTIENT_CONTROL", label=label, result=out))

    def test_binding_flags_and_root_corruption_rejected(self):
        rows, literals, endpoints = core.retained()
        original = next(r for r in rows if r["case"] == "oblique" and r["source_id"] == "S0" and r["primitive_id"] == 0)
        expected = {k: original[k] for k in core.CONTEXT}
        mutations = [("scene_only_cross_query", "literal", literals["shared_ref1000"]),
                     ("cross_SOURCE", "source_id", "S1"), ("wrong_input", "input_sha256", "0"*64),
                     ("scene", "scene_sha256", "0"*64), ("query", "query_sha256", "0"*64),
                     ("source_record", "source_record_sha256", "0"*64),
                     ("CPU_packet", "CPU_packet_binding_sha256", "0"*64),
                     ("ignored", "ignored_primitive_ids", [1]), ("offset", "origin_offset_applied", True),
                     ("first_id", "conditional_first_id", 0), ("merged", "SOURCE_merged", True),
                     ("ledger", "upstream_ledger_status", "PASS"), ("primitive_bool", "primitive_id", False),
                     ("units", "units", dict(displacement="meters", length="meters", squared="meters2")),
                     ("root96", "root_fraction_bits", 192), ("model", "model", "other")]
        mutations += [(f, f, True) for f in core.FLAGS]
        for label, key, val in mutations:
            r = copy.deepcopy(original); lit = copy.deepcopy(literals["oblique"])
            if key == "literal":
                lit = copy.deepcopy(val)
            else:
                r[key] = val
            with self.assertRaises(ValueError) as cm:
                core.compose(r, lit, endpoints["oblique"], expected_context=expected, model=core.MODEL)
            RECORDS.append(dict(kind="BINDING_NEG", label=label, error=str(cm.exception)))
        for label in ("captured_length", "captured_root_integer", "captured_squared"):
            r = copy.deepcopy(original)
            if label == "captured_length":
                r["chord"]["length_BU"][0] = [0, 1]
            elif label == "captured_root_integer":
                r["chord"]["root_lower_certificate"]["floor_scaled_root"] += 1
            else:
                r["chord"]["squared_BU2"][0] = [0, 1]
            with self.assertRaises(ValueError) as cm:
                core.compose(r, literals["oblique"], endpoints["oblique"], expected_context=expected, model=core.MODEL)
            RECORDS.append(dict(kind="BINDING_NEG", label=label, error=str(cm.exception)))

    def test_closed_units_reference_scope_and_rational_limits(self):
        good = dict(length_BU=iv(1), reference_BU=iv(0), wavelength_BU=iv(1), source_id="S0",
                    units="BU", reference_scope="GEOMETRIC_TWO_SEGMENT_PATH", model=core.MODEL)
        bad = [("zero_wave", "wavelength_BU", iv(0)), ("wave_crosses_zero", "wavelength_BU", iv(-1, 1)),
               ("negative_wave", "wavelength_BU", iv(-2, -1)), ("negative_length", "length_BU", iv(-1)),
               ("reversed", "reference_BU", iv(2, 1)), ("scope_chord", "reference_scope", "CHORD_LOCAL"),
               ("scope_optical", "reference_scope", "OPTICAL_PATH"), ("units", "units", "meters"),
               ("source", "source_id", "S2"), ("source_bool", "source_id", True), ("model", "model", "other")]
        for label, v in (("bool", [True, 1]), ("float", [1.0, 1]), ("noncanonical", [2, 2]),
                         ("den_zero", [1, 0]), ("cap128", [1, 2**128])):
            bad.append((label, "wavelength_BU", [v, [1, 1]]))
        for label, key, val in bad:
            q = copy.deepcopy(good); q[key] = val
            with self.assertRaises(ValueError) as cm:
                core.enclose(**q)
            RECORDS.append(dict(kind="INPUT_NEG", label=label, error=str(cm.exception)))
        # Each canonical input fits 128 bits; composing the final width may not
        # fit 512, even if each quotient endpoint does. Preserve that STOP.
        l = iv(F(1, 2**127-1), F(2, 2**107-1))
        r = iv(F(1, 2**89-1), F(2, 2**83-1))
        w = iv(F(2**79-1, 2**113-1), F(2**101-1, 2**109-1))
        with self.assertRaises(ValueError) as cm:
            core.enclose(l, r, w, source_id="S0", units="BU",
                         reference_scope="GEOMETRIC_TWO_SEGMENT_PATH", model=core.MODEL)
        self.assertEqual(str(cm.exception), "cycle_capacity512")
        RECORDS.append(dict(kind="INPUT_NEG", label="final_width_capacity512_retained", error=str(cm.exception)))

    def test_capture_fail_closed_and_caller_copy(self):
        raw = b'{"status":"PASS"}'
        good = dict(rc=0, before_deadline=True, stdout_bytes=len(raw),
                    stdout_sha256=hashlib.sha256(raw).hexdigest(),
                    stdout_zlib_base64=base64.b64encode(zlib.compress(raw)).decode())
        bads = [("late", "before_deadline", False), ("bool_rc", "rc", False),
                ("digest", "stdout_sha256", "0"*64), ("bytes", "stdout_bytes", 1),
                ("timeout_contradiction", "timed_out", True)]
        for label, key, val in bads:
            c = copy.deepcopy(good); c[key] = val
            with self.assertRaises(ValueError) as cm:
                core.capture(dict(test_run=c))
            RECORDS.append(dict(kind="CAPTURE_NEG", label=label, error=str(cm.exception)))
        length = iv(1, 2); reference = iv(0); wavelength = iv(1)
        snap = copy.deepcopy((length, reference, wavelength))
        out = core.enclose(length, reference, wavelength, source_id="S0", units="BU",
                           reference_scope="GEOMETRIC_TWO_SEGMENT_PATH", model=core.MODEL)
        out["length_BU"][0][0] = 999
        self.assertEqual((length, reference, wavelength), snap)
        self.assertIsNone(out["parent_receipts_sha256"])
        RECORDS.append(dict(kind="CALLER_COPY", status="PASS"))


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestCycles)
    result = unittest.TextTestRunner(stream=sys.stderr).run(suite)
    print(json.dumps(dict(id=core.ID, status="PASS" if result.wasSuccessful() else "FAIL",
                          tests=result.testsRun, records=RECORDS, GPU_used=False, Bpy_used=False, RT_used=False,
                          old_position_evaluator_replays=0, old_length_producer_replays=0, old_phase_producer_replays=0,
                          old_geometry_queries=0, JEV="LOCAL_SECURITY_BLOCKED_NO_RETRY"), sort_keys=True))
    sys.exit(0 if result.wasSuccessful() else 1)
