"""Actual archived104 snapshots vs four retained originals; no trace replay."""
import base64
import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest
import zlib

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/"Blender/benchmarks/capacity_audit"))
import scene_necessary_invariants_HOST_v1 as m

LITERAL = ROOT/"coordinacion/respuestas/PRECISION-OBLIQUE-COMMON-DETECTOR-LENGTH-CPU-001-CODEX.json"
LITERAL_SHA = "139cb34a315f476fa026bb346086a3a59d7c22241932ca3f4c291a501f4ca47e"
MANIFEST = Path("D:/PROJECTS/.cognition/neuro3d/p0_scene_gpu/p03_manifest.json")
MANIFEST_SHA = "3343fa298cef2286e6643026a7e8b23ac4a6db011b443ffdf8c9c625fa89fe5b"
RECORDS = []


def pinned(path, expected):
    raw = path.read_bytes()
    if len(raw) > 1048576 or hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError("input SHA mismatch: "+str(path))
    return json.loads(raw)


def control(item):
    # Explicit synthetic partial matching geometry, not a new native snapshot.
    scene = item["scene"]
    number = lambda v: float(m.rational(v))
    vec = lambda v: [number(x) for x in v]
    return dict(schema="exp005-readback-v2", lambda_BU=number(item["request"]["lambda_BU"]),
                sources=[dict(id=s["id"], position_BU=vec(s["position_BU"]),
                              direction=vec(s["direction"])) for s in scene["sources"]],
                objects={str(t["primitive_id"]):dict(vertices_world_BU=[vec(v) for v in t["vertices_BU"]],
                            faces=[[0, 1, 2]]) for t in scene["triangles"]})


class NecessaryInvariantsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        r = pinned(LITERAL, LITERAL_SHA)
        c = r["test_run"]
        z = zlib.decompressobj()
        raw = z.decompress(base64.b64decode(c["stdout_zlib_base64"], validate=True), 1048577)
        assert z.eof and not z.unused_data and not z.unconsumed_tail
        assert len(raw) <= 1048576 and len(raw) == c["stdout_bytes"]
        assert hashlib.sha256(raw).hexdigest() == c["stdout_sha256"]
        assert c["rc"] == 0 and c["timed_out"] is False
        cls.inputs = json.loads(raw)["data"]["inputs"]
        cls.snapshots = pinned(MANIFEST, MANIFEST_SHA)["scenes"]
        assert len(cls.snapshots) == 104

    def test_existing_all104_no_same_declared_scene(self):
        for case in ("oblique", "direction_scaled", "shared_ref1000", "tiny_gap_2m60"):
            item = self.inputs[case]
            counts = {key: 0 for key in ("surface_extent_BU", "oriented_SOURCE_multiset", "lambda_BU")}
            for i, snap in enumerate(self.snapshots):
                r = m.compare(item["scene"], item["request"], snap)
                self.assertEqual(r["status"], "DIFFERENT_DECLARED_SCENE_SAME_BU_FRAME")
                self.assertFalse(r["equivalence_proved"])
                for key, equal in r["invariant_equal"].items():
                    counts[key] += not equal
                RECORDS.append(dict(kind="ARCHIVED_SCENE_COMPARISON", case=case, index=i,
                                    snapshot_sha256=hashlib.sha256(json.dumps(snap, sort_keys=True).encode()).hexdigest(),
                                    **r))
            self.assertEqual(counts["surface_extent_BU"], 104)
            self.assertEqual(counts["oriented_SOURCE_multiset"], 104)
            RECORDS.append(dict(kind="CASE_SUMMARY", case=case, comparisons=104, mismatches=counts))

    def test_identifier_order_and_positive_scale_are_not_rejection(self):
        item = self.inputs["oblique"]
        snap = control(item)
        snap["sources"].reverse()
        for i, s in enumerate(snap["sources"]):
            s["id"] = "renamed"+str(i)
            s["direction"] = [v*8 for v in s["direction"]]
        snap["objects"] = {"renamed"+k:dict(v, faces=[[2, 1, 0]]) for k, v in reversed(list(snap["objects"].items()))}
        r = m.compare(item["scene"], item["request"], snap)
        self.assertEqual(r["status"], "STOP_EQUAL_NECESSARY_INVARIANTS_NOT_EQUIVALENCE")
        self.assertFalse(r["equivalence_proved"])
        RECORDS.append(dict(kind="SYNTHETIC_REORDER_SCALE_STILL_STOP", **r))

    def test_equal_bounds_do_not_prove_surface_identity(self):
        item = self.inputs["oblique"]
        snap = control(item)
        # Change triangular support inside unchanged bbox. No equivalence promotion.
        snap["objects"]["1"]["vertices_world_BU"][1][2] = 1.0
        r = m.compare(item["scene"], item["request"], snap)
        self.assertEqual(r["status"], "STOP_EQUAL_NECESSARY_INVARIANTS_NOT_EQUIVALENCE")
        self.assertTrue(all(r["invariant_equal"].values()))
        RECORDS.append(dict(kind="SYNTHETIC_EQUAL_BBOX_DIFFERENT_SURFACE_STOP", **r))

    def test_reversed_ray_and_channel_multiplicity(self):
        item = self.inputs["oblique"]
        for label in ("reverse", "duplicate_channel", "wavelength"):
            snap = control(item)
            if label == "reverse":
                snap["sources"][0]["direction"] = [-v for v in snap["sources"][0]["direction"]]
            elif label == "duplicate_channel":
                snap["sources"].append(copy.deepcopy(snap["sources"][0]))
            else:
                snap["lambda_BU"] = 0.25
            r = m.compare(item["scene"], item["request"], snap)
            self.assertEqual(r["status"], "DIFFERENT_DECLARED_SCENE_SAME_BU_FRAME")
            self.assertIn("lambda_BU" if label == "wavelength" else "oriented_SOURCE_multiset", r["reasons"])
            RECORDS.append(dict(kind="SYNTHETIC_NEGATIVE", label=label, **r))

    def test_invalid_input_stops(self):
        item = self.inputs["oblique"]
        for label in ("bool_scalar", "nan_scalar", "zero_direction", "bool_index", "bad_schema", "empty_surface"):
            snap = control(item)
            if label == "bool_scalar": snap["lambda_BU"] = True
            elif label == "nan_scalar": snap["lambda_BU"] = float("nan")
            elif label == "zero_direction": snap["sources"][0]["direction"] = [0, 0, 0]
            elif label == "bool_index": snap["objects"]["0"]["faces"] = [[True, 1, 2]]
            elif label == "bad_schema": snap["schema"] = "other"
            else:
                for obj in snap["objects"].values(): obj["faces"] = [[0, 0, 0]]
            r = m.compare(item["scene"], item["request"], snap)
            self.assertEqual(r["status"], "STOP_INPUT")
            self.assertFalse(r["current_GPU_admission"])
            RECORDS.append(dict(kind="INVALID_INPUT_STOP", label=label, **r))


if __name__ == "__main__":
    r = unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(NecessaryInvariantsTests))
    print(json.dumps(dict(status="PASS" if r.wasSuccessful() else "FAIL", tests=r.testsRun,
                         records=RECORDS, GPU_used=False, foreign_code_executed=False,
                         new_traces=0, pointwise_budget_certified=False)))
    raise SystemExit(0 if r.wasSuccessful() else 1)
