"""Independent evidence check by Z separators, without importing matcher."""
import base64, hashlib, json, zlib
from fractions import Fraction as F
import os
from pathlib import Path
REPO_ROOT=Path(__file__).resolve().parents[2]
NEURO3D_COGNITION = Path(os.environ.get("NEURO3D_COGNITION_DIR", REPO_ROOT / ".cognition"))
r = json.loads(Path("coordinacion/respuestas/PRECISION-EXISTING-P03-SCENE-INVARIANTS-HOST-001-CODEX.json").read_bytes())
for path, pin in r["pins"].items():
    raw = Path(path).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == pin["sha256"] and len(raw) == pin["bytes"], path
cap = r["test_run"]
raw = zlib.decompress(base64.b64decode(cap["stdout_zlib_base64"]))
assert len(raw) == cap["stdout_bytes"] and hashlib.sha256(raw).hexdigest() == cap["stdout_sha256"]
qa = json.loads(raw)
assert qa["status"] == "PASS" and qa["tests"] == 5 and len(qa["records"]) == 431
l = json.loads(Path("coordinacion/respuestas/PRECISION-OBLIQUE-COMMON-DETECTOR-LENGTH-CPU-001-CODEX.json").read_bytes())
c = l["test_run"]
raw = zlib.decompress(base64.b64decode(c["stdout_zlib_base64"]))
assert len(raw) == c["stdout_bytes"] and hashlib.sha256(raw).hexdigest() == c["stdout_sha256"]
inputs = json.loads(raw)["data"]["inputs"]
manifest = json.loads((NEURO3D_COGNITION / "neuro3d/p0_scene_gpu/p03_manifest.json").read_bytes())
result = json.loads((NEURO3D_COGNITION / "neuro3d/p0_scene_gpu/p03_cuda_result.json").read_bytes())
assert len(manifest["scenes"]) == len(result["scene_results"]) == 104
rows = [x for x in qa["records"] if x["kind"] == "ARCHIVED_SCENE_COMPARISON"]
assert len(rows) == 416
summaries = [x for x in qa["records"] if x["kind"] == "CASE_SUMMARY"]
assert len(summaries) == 4
for case, summary in zip(("oblique","direction_scaled","shared_ref1000","tiny_gap_2m60"), summaries, strict=True):
    item = inputs[case]
    original_z = [F(*v[2]) for t in item["scene"]["triangles"] for v in t["vertices_BU"]]
    assert min(original_z) == 0 and max(original_z) == 3
    assert {F(*s["position_BU"][2]) for s in item["scene"]["sources"]} == {F(1,4)}
    # Verify original triangles are actual nondegenerate surfaces: yz-area !=0.
    for t in item["scene"]["triangles"]:
        a,b,c = [[F(*v) for v in point] for point in t["vertices_BU"]]
        assert (b[1]-a[1])*(c[2]-a[2]) != (b[2]-a[2])*(c[1]-a[1])
    lam_different = 0
    case_rows = [x for x in rows if x["case"] == case]
    for i, (snap, rr, row) in enumerate(zip(manifest["scenes"],result["scene_results"],case_rows,strict=True)):
        h = hashlib.sha256(json.dumps(snap, sort_keys=True).encode()).hexdigest()
        assert rr["index"] == row["index"] == i and rr["scene_sha256"] == row["snapshot_sha256"] == h
        points = [ob["vertices_world_BU"][j] for ob in snap["objects"].values() for face in ob["faces"] for j in face]
        # Even all face vertices lie inside this Z slab; no nondegenerate subset
        # can have original max Z=3. This proof does not depend on core bbox code.
        assert min(F(p[2]) for p in points) == F(-1,8)
        assert max(F(p[2]) for p in points) == F(1,8)
        assert {F(s["position_BU"][2]) for s in snap["sources"]} == {F(0)}
        different = F(snap["lambda_BU"]) != F(*item["request"]["lambda_BU"])
        lam_different += different
        assert row["invariant_equal"] == dict(surface_extent_BU=False, oriented_SOURCE_multiset=False, lambda_BU=not different)
        assert row["status"] == "DIFFERENT_DECLARED_SCENE_SAME_BU_FRAME"
        assert row["phase_bound_rad"] is None and row["equivalence_proved"] is False
    assert summary["case"] == case and summary["mismatches"] == dict(surface_extent_BU=104, oriented_SOURCE_multiset=104, lambda_BU=lam_different)
for row in qa["records"]:
    if "equivalence_proved" in row:
        assert not row["equivalence_proved"] and not row["current_GPU_admission"]
        assert not row["native_precision_certified"] and row["phase_bound_rad"] is None
m = json.loads(Path("coordinacion/respuestas/GPU-GUARD-OWNED-TREE-CONTAINMENT-CPU-001-CODEX.json").read_bytes())["pinned_manifest_capture"]
raw = zlib.decompress(base64.b64decode(m["stdout_zlib_base64"]))
assert hashlib.sha256(raw).hexdigest() == m["stdout_sha256"]
pins = json.loads(raw)["pins"]
assert len(pins) == 461
for path, h in pins.items():
    assert hashlib.sha256(Path(path).read_bytes()).hexdigest() == h, path
print(json.dumps(dict(status="PASS", comparisons=416, input_pins=len(r["pins"]), frozen_pins=461,
    independent_proof="original surfaces Z[0,3] outside archived Z[-1/8,1/8]; SOURCE Z1/4 vs0",
    summaries=summaries, native_equivalence=False, GPU_used=False)))
