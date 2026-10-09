"""Guarded native scene hi/lo v1 runtime; no import-time Blender/GPU work.

The job reopens three pinned saved scenes, admits their complete integer packets,
executes one actual compute invocation in each of two modes, and audits EVERY
geometric output against independent Fraction arithmetic on observed scene
values. The low-zero ablation and collapsed-double columns are explicit controls.

PASS establishes this bounded native diagnostic on the recorded device/build.
It does not establish intersections, phases, a full Iris GPU network, physical
uncertainty, hardware RT/BVH, speedup, or a universal GLSL numerical theorem.
Launch only through scene_hilo_gpu_guard_v1.py under its UUID gpuq lease.
"""
import argparse
from fractions import Fraction
import gc
import hashlib
import json
import math
import os
from pathlib import Path
import struct
import sys
import time
import traceback
import uuid

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from Blender.benchmarks.capacity_audit import scene_hilo_gpu_v1 as native
from Blender.benchmarks.capacity_audit import scene_hilo_transport_v1 as transport
from exp005_scene_readback import export_snapshot
from exp005_blender_gpu import schedule_exit

SCHEMA = "neuro3d.scene_hilo.native_job.v1"
REPORT_SCHEMA = "neuro3d.scene_hilo.native_report.v1"
CASE_CLASSES = [("k3_baseline", "real_reopened_baseline"),
                ("k4_baseline", "real_reopened_baseline"),
                ("controlled_numeric", "controlled_numeric_scene")]
LIMITS = {"max_sources": 5, "max_triangles": 64, "max_dispatches": 6}
MAX_JSON_BYTES = 16 * 1024 * 1024
ABSENT = 0xFFFFFFFF
SCOPE = {
    "native_arithmetic": "all source-by-vertex xyz differences, source direction widths, both triangle edges",
    "transport_only_fields": "raw directions, fields, wavelength, terminal modes and scalar/identity records",
    "material_parameters": "preserved exactly in original snapshot metadata, uniformly excluded from numeric ABI",
    "oracle": "Fraction from original observed scene binary64; no reuse of compensated GPU algorithm",
    "precision_claim": "empirical exactness of these finite outputs on this recorded native implementation",
    "physical_uncertainty_certified": False,
    "full_intersection_integration": False,
    "phase_certified": False,
    "full_Iris_GPU": False,
    "hardware_RT_or_BVH": False,
    "speed_advantage_claimed": False,
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)


def read_json(path):
    require(path.is_file() and path.stat().st_size <= MAX_JSON_BYTES,
            "bounded existing JSON required: " + str(path))
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "duplicate JSON key: " + str(key))
            result[key] = value
        return result
    def bad_constant(value):
        raise ValueError("nonfinite JSON constant: " + value)
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs,
                      parse_constant=bad_constant)


def write_new_report(path, report, job_id):
    """Publish a complete JSON atomically; refuse any pre-existing destination."""
    require(not path.exists() and path.parent.is_dir(), "fresh report path required")
    raw = (json.dumps(report, indent=2, allow_nan=False) + "\n").encode("utf-8")
    require(len(raw) <= MAX_JSON_BYTES, "bounded native report required")
    temporary = path.with_name(path.name + "." + job_id + ".tmp")
    with temporary.open("xb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    # Windows rename is atomic within a volume and fails if the target exists.
    # This worker rejects non-Windows devices before native execution.
    if os.name == "nt":
        os.rename(temporary, path)
    else:
        os.link(temporary, path)
        temporary.unlink()


def validate_job(job):
    require(type(job) is dict and set(job) == {
        "schema", "cases", "limits", "expected_backend", "expected_renderer_contains"},
        "closed native job schema required")
    require(job["schema"] == SCHEMA and job["limits"] == LIMITS and
            job["expected_backend"] == "OPENGL" and
            job["expected_renderer_contains"] == "RTX 3090", "frozen native job profile changed")
    require(type(job["cases"]) is list and len(job["cases"]) == 3, "exactly three saved-scene cases required")
    paths = []
    for case, (case_id, input_class) in zip(job["cases"], CASE_CLASSES):
        require(type(case) is dict and set(case) == {
            "case_id", "input_class", "blend_path", "blend_sha256", "packet_path", "packet_sha256"},
            "closed scene case schema required")
        require(case["case_id"] == case_id and case["input_class"] == input_class,
                "case identity, input class or ordering changed")
        for name, suffix in (("blend", ".blend"), ("packet", ".json")):
            path = Path(case[name + "_path"])
            digest = case[name + "_sha256"]
            require(path.is_absolute() and path.suffix.lower() == suffix and path.is_file(),
                    "absolute saved input path required")
            require(type(digest) is str and len(digest) == 64 and
                    all(char in "0123456789abcdef" for char in digest) and sha(path) == digest,
                    "pinned input hash mismatch: " + str(path))
            paths.append(str(path.resolve()).casefold())
    require(len(set(paths)) == len(paths), "unique scene/packet files required")


def read_actual_case(bpy, case):
    blend = Path(case["blend_path"]).resolve()
    packet_path = Path(case["packet_path"]).resolve()
    retained = read_json(packet_path)
    require(type(retained) is dict and "manifest" in retained, "retained packet manifest required")
    trusted = retained["manifest"]
    transport.admit_for_upload(retained, trusted_manifest=trusted)
    bpy.ops.wm.open_mainfile(filepath=str(blend))
    bpy.context.view_layer.update()
    snapshot = export_snapshot(bpy.context.scene,
                               depsgraph=bpy.context.evaluated_depsgraph_get(),
                               view_layer=bpy.context.view_layer)
    provenance = {
        "input_class": case["input_class"], "blend_sha256": sha(blend),
        "blender_version": bpy.app.version_string, "scene_name": bpy.context.scene.name,
        "view_layer_name": bpy.context.view_layer.name,
    }
    if "blend_path" in trusted["provenance"]:
        require(Path(trusted["provenance"]["blend_path"]).resolve() == blend,
                "retained provenance blend path differs")
        provenance["blend_path"] = trusted["provenance"]["blend_path"]
    if transport.BOUNDS_PROPERTY in bpy.context.scene:
        raw_bounds = bpy.context.scene[transport.BOUNDS_PROPERTY]
        require(type(raw_bounds) is str, "persisted direction bounds JSON string required")
        bounds = transport._strict_bounds_json(raw_bounds)
        snapshot[transport.BOUNDS_PROPERTY] = bounds
        provenance["direction_bounds_property"] = transport.BOUNDS_PROPERTY
        provenance["direction_bounds_json"] = raw_bounds
    rebuilt = transport.build_packet(snapshot, provenance=provenance)
    wire = transport.admit_for_upload(rebuilt, trusted_manifest=trusted)
    require(canonical(rebuilt) == canonical(retained),
            "reopened evaluated scene or packet differs from pinned preparation")
    require(sha(blend) == case["blend_sha256"] and sha(packet_path) == case["packet_sha256"],
            "input files changed while reopening")
    layout = native.admitted_layout(wire)
    return {"case": case, "snapshot": snapshot, "wire": wire, "packet": rebuilt,
            "layout": layout}


def operand(value, zero_low):
    """Independent reference: original binary64, or its nearest float32 high limb."""
    observed = float(value)
    require(math.isfinite(observed), "finite observed reference required")
    if zero_low:
        observed = struct.unpack("<f", struct.pack("<f", observed))[0]
    return Fraction.from_float(observed)


def reference_rows(snapshot, zero_low):
    """Derive operations from source/mesh values, never from a CPU hit/t table."""
    vertices, triangles = [], []
    for object_id, name in enumerate(sorted(snapshot["objects"])):
        obj = snapshot["objects"][name]
        first = len(vertices)
        for point in obj["vertices_world_BU"]:
            vertices.append((object_id, point))
        for face in obj["faces"]:
            require(len(face) == 3, "actual triangle faces required by native profile")
            triangles.append((object_id, [first + index for index in face]))
    sources = snapshot["sources"]

    def record(identity, left, right):
        a = [operand(value, zero_low) for value in left]
        b = [operand(value, zero_low) for value in right]
        exact = [lhs - rhs for lhs, rhs in zip(a, b)]
        naive = [float(lhs) - float(rhs) for lhs, rhs in zip(a, b)]
        return identity, exact, naive

    for source_id, source in enumerate(sources):
        for vertex_id, (object_id, position) in enumerate(vertices):
            yield record([1, source_id, vertex_id, object_id],
                         position, source["position_BU"])
    bounds = snapshot.get(transport.BOUNDS_PROPERTY, {})
    for source_id, source in enumerate(sources):
        axes = bounds.get(source["id"], [[value, value] for value in source["direction"]])
        yield record([2, source_id, ABSENT, ABSENT],
                     [axis[1] for axis in axes], [axis[0] for axis in axes])
    for edge in (1, 2):
        for triangle_id, (object_id, indices) in enumerate(triangles):
            yield record([2 + edge, ABSENT, triangle_id, object_id],
                         vertices[indices[edge]][1], vertices[indices[0]][1])


def fraction_record(value):
    return [value.numerator, value.denominator]


def double_at(words):
    require(len(words) == 2, "two uint32 words per binary64 required")
    value = struct.unpack("<d", struct.pack("<II", *words))[0]
    require(math.isfinite(value), "nonfinite native binary64 output")
    return value


def audit_rows(snapshot, readback, *, zero_low):
    """Audit every identity and every exact component, returning bounded witnesses."""
    words = native.unpack_words(bytes.fromhex(readback["computed_rows_hex"]))
    references = list(reference_rows(snapshot, zero_low))
    require(words[5] == len(references) and words[3] == 32 + 24 * len(references),
            "native output coverage differs from independent scene traversal")
    exact_values, witnesses = [], []
    nonzero_lows = collapsed_losses = components = 0
    expected_hasher = hashlib.sha256()
    tiny_target = Fraction(1) - Fraction(1, 2 ** 60)
    four_term_target = Fraction(1) + Fraction(1, 2 ** 30) - Fraction(1, 2 ** 60) - Fraction(1, 2 ** 100)
    critical = {"one_minus_2pow_minus60": [], "four_term_direction_width": []}
    for row_index, (identity, expected, naive_reference) in enumerate(references):
        row = words[32 + row_index * 24:32 + (row_index + 1) * 24]
        require(row[:4] == identity and row[22:24] == [0, 0],
                "native row identity/order/reserved fields mismatch at " + str(row_index))
        expected_hasher.update((canonical([identity, [fraction_record(x) for x in expected]]) + "\n").encode())
        result_values = []
        for axis, target in enumerate(expected):
            high = double_at(row[4 + axis * 4:6 + axis * 4])
            low = double_at(row[6 + axis * 4:8 + axis * 4])
            naive_value = double_at(row[16 + axis * 2:18 + axis * 2])
            exact_native = Fraction.from_float(high) + Fraction.from_float(low)
            require(exact_native == target,
                    "exact Fraction mismatch at row " + str(row_index) + " axis " + str(axis))
            require(Fraction.from_float(naive_value) == Fraction.from_float(naive_reference[axis]),
                    "native collapsed-double control differs from binary64 reference")
            nonzero_lows += low != 0.0
            loss = Fraction.from_float(naive_value) != target
            collapsed_losses += loss
            components += 1
            result_values.append(exact_native)
            witness = {"row_index": row_index, "identity": identity, "axis": axis,
                       "exact_expected": fraction_record(target), "pair64": [high, low],
                       "pair64_words": row[4 + axis * 4:8 + axis * 4],
                       "naive_binary64": naive_value, "naive_lost_exact_value": loss}
            if (low != 0.0 or loss) and len(witnesses) < 12:
                witnesses.append(witness)
            if identity[0] == 1 and axis == 0 and target == tiny_target:
                critical["one_minus_2pow_minus60"].append(witness)
            if identity[0] == 2 and target == four_term_target:
                critical["four_term_direction_width"].append(witness)
        exact_values.append(result_values)
    result = {
        "status": "PASS", "all_rows_checked": len(references),
        "exact_components_checked": components, "zero_tolerance_exact_comparison": True,
        "nonzero_output_low_components": nonzero_lows,
        "collapsed_binary64_loss_components": collapsed_losses,
        "expected_rows_sha256": expected_hasher.hexdigest(),
        "witnesses": witnesses, "critical_witnesses": critical,
    }
    return result, exact_values


def private_exit_settings(bpy):
    prefs = bpy.context.preferences
    prefs.use_preferences_save = False
    prefs.view.use_save_prompt = False
    prefs.filepaths.use_auto_save_temporary_files = False
    require(not prefs.use_preferences_save and not prefs.view.use_save_prompt and
            not prefs.filepaths.use_auto_save_temporary_files,
            "private child must disable persistent preferences, autosave and quit prompts")
    return {"save_user_preferences": False, "save_prompt": False, "temporary_autosave": False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-manifest", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--job-id", required=True)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    require(str(uuid.UUID(args.job_id)) == args.job_id, "canonical guard job UUID required")
    manifest_path, report_path = args.input_manifest.resolve(), args.report.resolve()
    require(not report_path.exists() and report_path.parent.is_dir(), "fresh report required")
    report = {
        "schema": REPORT_SCHEMA, "status": "FAIL", "verification_passed": False,
        "job_id": args.job_id, "input_manifest_sha256": sha(manifest_path),
        "native_gpu_executed": False, "native_gpu_execution_attempted": False,
        "gpu_dispatch_count": 0, "completed_readbacks": 0,
        "execution_state_scope": "dispatch_count counts attempted native calls; executed is null until a first complete readback confirms execution, and true thereafter",
        "gpu_readback_records": [], "gpu_readback_sha256": None,
        "scope": SCOPE, "limits": LIMITS, "cases": [],
    }
    started = time.perf_counter()
    shader = None
    failure = None
    readback_hasher = hashlib.sha256()
    try:
        import bpy
        import gpu
        require(not bpy.app.background, "windowed private OpenGL context required")
        report.update(native.device_profile(gpu))
        report["background"] = bpy.app.background
        report["blender_version"] = bpy.app.version_string
        report["blender_build_hash"] = bpy.app.build_hash.decode("ascii")
        report["private_exit_settings"] = private_exit_settings(bpy)
        job = read_json(manifest_path)
        validate_job(job)
        dependencies = [
            Path(__file__).resolve(), Path(native.__file__), native.SHADER,
            Path(transport.__file__), Path(transport.codec.__file__),
            Path(__file__).with_name("exp005_scene_readback.py"),
            Path(__file__).with_name("exp005_scene_properties.py"),
            Path(__file__).with_name("exp005_blender_gpu.py"),
        ]
        code_hashes = {str(path.relative_to(ROOT)): sha(path) for path in dependencies}
        report["code_sha256"] = code_hashes
        # Admit all three real reopened scenes before any compute dispatch.
        prepared = [read_actual_case(bpy, case) for case in job["cases"]]
        report["all_saved_scenes_reopened_before_compute"] = True
        shader = native.native_shader(gpu)
        seen_nonces = set()
        for prepared_case in prepared:
            case = prepared_case["case"]
            case_id = case["case_id"]
            snapshot = prepared_case["snapshot"]
            wire = prepared_case["wire"]
            packet_manifest = prepared_case["packet"]["manifest"]
            case_report = {
                **case, "layout": prepared_case["layout"],
                "reopened_snapshot_equal": True, "snapshot": snapshot,
                "wire_sha256": hashlib.sha256(wire).hexdigest(),
                "native_input_nonzero_low_limbs": sum(
                    (record["lo_word"] & 0x7FFFFFFF) != 0 for record in packet_manifest["scalars"]),
                "material_binary64_metadata": packet_manifest["material_binary64_metadata"],
                "modes": [],
            }
            report["cases"].append(case_report)
            values_by_mode = {}
            for zero_low in (0, 1):
                seed = (args.job_id + "/" + case_id + "/" + str(zero_low)).encode()
                nonce = int.from_bytes(hashlib.sha256(seed).digest()[:4], "little") & 0x7FFFFFFF
                require(nonce != 0 and nonce not in seen_nonces, "fresh unique dispatch nonce required")
                seen_nonces.add(nonce)
                require(report["gpu_dispatch_count"] < LIMITS["max_dispatches"], "dispatch cap reached")
                report["gpu_dispatch_count"] += 1
                report["native_gpu_execution_attempted"] = True
                if report["native_gpu_executed"] is not True:
                    report["native_gpu_executed"] = None
                result = native.dispatch(gpu, shader, wire, zero_low=zero_low, nonce=nonce)
                report["native_gpu_executed"] = True
                raw_record = {
                    "case_id": case_id, "zero_low": zero_low,
                    "input_echo_hex": result["input_echo_hex"],
                    "computed_rows_hex": result["computed_rows_hex"],
                }
                report["gpu_readback_records"].append(raw_record)
                report["completed_readbacks"] = len(report["gpu_readback_records"])
                readback_hasher.update(bytes.fromhex(raw_record["input_echo_hex"]))
                readback_hasher.update(bytes.fromhex(raw_record["computed_rows_hex"]))
                report["gpu_readback_sha256"] = readback_hasher.hexdigest()
                audit, exact_values = audit_rows(snapshot, result, zero_low=zero_low)
                values_by_mode[zero_low] = exact_values
                case_report["modes"].append({
                    key: value for key, value in result.items()
                    if key not in ("input_echo_hex", "computed_rows_hex")
                } | {"audit": audit, "raw_record_index": len(report["gpu_readback_records"]) - 1})
            changed = sum(a != b for row_a, row_b in zip(values_by_mode[0], values_by_mode[1])
                          for a, b in zip(row_a, row_b))
            case_report["low_zero_ablation_changed_components"] = changed
            if case["input_class"] == "real_reopened_baseline":
                require(changed == 0, "baseline low-zero arithmetic sham unexpectedly changed")
            else:
                require(case_report["native_input_nonzero_low_limbs"] > 0 and changed > 0,
                        "controlled case must causally depend on nonzero input low limbs")
                full = case_report["modes"][0]["audit"]
                critical = full["critical_witnesses"]
                require(full["nonzero_output_low_components"] > 0 and
                        full["collapsed_binary64_loss_components"] > 0 and
                        critical["one_minus_2pow_minus60"] and
                        critical["four_term_direction_width"],
                        "controlled exact/collapsed/four-term witnesses missing")
                require(all(w["pair64"][1] != 0.0 and w["naive_lost_exact_value"]
                            for group in critical.values() for w in group),
                        "critical low components must survive while naive binary64 loses them")
        require(report["gpu_dispatch_count"] == 6 and len(report["gpu_readback_records"]) == 6,
                "exactly six bounded native readbacks required")
        validate_job(job)
        require(sha(manifest_path) == report["input_manifest_sha256"] and
                all(sha(ROOT / name) == digest for name, digest in code_hashes.items()),
                "pinned inputs or implementation changed during native execution")
        report["verification_passed"] = True
        report["status"] = "PASS"
    except BaseException as exc:
        failure = exc
        report["error"] = type(exc).__name__ + ": " + str(exc)
        report["traceback"] = traceback.format_exc()
    finally:
        shader = None
        gc.collect()
        report["total_seconds"] = time.perf_counter() - started
        write_new_report(report_path, report, args.job_id)
    if failure is not None:
        raise failure
    print("SCENE_HILO_NATIVE_PASS " + report["gpu_readback_sha256"], flush=True)
    schedule_exit(bpy)


if __name__ == "__main__":
    main()
