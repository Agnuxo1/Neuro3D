"""Independently verify a copied, self-contained Iris scene in a fresh Blender process.

Run under the caller's bounded, single-threaded supervisor:
  blender -b --factory-startup --python-exit-code 1 --python verify_portable_blender.py \
    -- --blend COPIED.blend --manifest MANIFEST.json --report REPORT.json

Only the scene's embedded source is executed, as a module without __file__.
The verifier never builds, trains, renders, saves or rebuilds a Blender scene.
It performs exactly one classify call for each of the 150 Iris rows. Numerical
limits come from the hash-verified embedded source's existing VERIFY_LIMITS.
Decoration invariance is explicitly unmeasured by this verifier.
"""
from __future__ import annotations

import argparse
import builtins
import contextlib
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
import math
import os
from pathlib import Path
import re
import sys
import tempfile
import time
import traceback
import types

SCHEMA = "neuro3d-iris-portable-v1"
ASSET_TEXTS = {
    "neuro3d_iris_demo.py": "neuro3d_iris_demo.py",
    "iris.csv": "neuro3d.asset.iris.csv",
    "trained_lattice.json": "neuro3d.asset.trained_lattice.json",
}
OPTICAL_METRICS = (
    "scene_vs_model_max_power_diff",
    "outputs_complex_vs_model_max",
    "escape_max",
    "power_balance_max_err",
)
MODULE_NAME = "_neuro3d_iris_portable_verified"


def require(condition, message):
    """Reject missing evidence or an invalid contract without manufacturing a pass."""
    if not condition:
        raise RuntimeError(message)


def utc_now():
    """Return an unambiguous timestamp for retained verification evidence."""
    return datetime.now(timezone.utc).isoformat()


def finite_number(value, name, *, nonnegative=False):
    """Accept a real finite JSON number, excluding booleans."""
    require(type(value) in (int, float), name + " must be a real number")
    number = float(value)
    require(math.isfinite(number), name + " is not finite")
    require(not nonnegative or number >= 0, name + " is negative")
    return number


def unique_object(pairs):
    """Reject duplicate JSON keys before interpreting a manifest or saved state."""
    result = {}
    for key, value in pairs:
        require(key not in result, "Duplicate JSON key: " + key)
        result[key] = value
    return result


def parse_json(text):
    """Parse strict JSON: duplicate keys and non-finite constants are errors."""
    def invalid_constant(value):
        raise RuntimeError("Non-finite JSON constant: " + value)
    return json.loads(text, object_pairs_hook=unique_object,
                      parse_constant=invalid_constant)


def sha256_file(path):
    """Hash an input file without loading its entire binary payload into memory."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def valid_hash(value, name):
    """Require the manifest's SHA-256 to have a canonical hexadecimal form."""
    require(type(value) is str and re.fullmatch(r"[0-9a-f]{64}", value) is not None,
            name + " must be a lowercase SHA-256")
    return value


def persist_report(path, report):
    """Atomically replace the report so interruption retains an explicit non-pass."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n",
                                         dir=path.parent, prefix=path.name + ".",
                                         suffix=".tmp", delete=False) as handle:
            temporary = Path(handle.name)
            json.dump(report, handle, indent=2, sort_keys=True, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


@contextlib.contextmanager
def deny_external_assets(directory, evidence):
    """Deny sidecar asset reads through open/io.open while leaving imports usable."""
    old_open, old_io_open, old_cwd = builtins.open, io.open, Path.cwd()
    blocked = {name.casefold() for name in ASSET_TEXTS}

    def guard(delegate):
        def checked(file, *args, **kwargs):
            try:
                name = os.path.basename(os.fsdecode(os.fspath(file))).casefold()
            except TypeError:
                name = ""  # File descriptors are unrelated to sidecar path lookup.
            if name in blocked:
                evidence.append({"asset": name, "operation": "external_open_denied"})
                raise PermissionError("External portable asset access denied: " + name)
            return delegate(file, *args, **kwargs)
        return checked

    os.chdir(directory)
    builtins.open, io.open = guard(old_open), guard(old_io_open)
    try:
        yield
    finally:
        builtins.open, io.open = old_open, old_io_open
        os.chdir(old_cwd)


def validate_manifest(manifest):
    """Validate names and hashes without accepting substitute embedded asset names."""
    require(type(manifest) is dict and manifest.get("schema") == SCHEMA,
            "Unsupported or missing manifest schema")
    assets = manifest.get("assets")
    require(type(assets) is dict and set(assets) == set(ASSET_TEXTS),
            "Manifest must declare exactly the source, CSV and trained state")
    for logical_name, text_name in ASSET_TEXTS.items():
        entry = assets[logical_name]
        require(type(entry) is dict and entry.get("text_name") == text_name,
                "Wrong embedded Text name for " + logical_name)
        valid_hash(entry.get("sha256"), logical_name)
    require(type(manifest.get("bundle_version")) is int and
            manifest["bundle_version"] == 1, "Manifest bundle_version must be 1")
    require(type(manifest.get("export_sample")) is dict,
            "Manifest lacks the measured export_sample needed for reopening parity")
    valid_hash(manifest.get("blend_sha256"), "blend_sha256")


def read_embedded_assets(bpy, manifest):
    """Read and hash Text payloads before allowing any embedded source execution."""
    contents, evidence = {}, {}
    require(bpy.context.scene.get("neuro3d_bundle_version") == 1,
            "Copied scene has no complete version-1 embedded asset bundle")
    for logical_name, text_name in ASSET_TEXTS.items():
        block = bpy.data.texts.get(text_name)
        require(block is not None, "Missing embedded asset: " + text_name)
        content = block.as_string()
        encoded = content.encode("utf-8")
        actual = hashlib.sha256(encoded).hexdigest()
        entry = manifest["assets"][logical_name]
        require(actual == entry["sha256"], "Embedded asset hash mismatch: " + text_name)
        if "bytes" in entry:
            require(type(entry["bytes"]) is int and entry["bytes"] == len(encoded),
                    "Embedded asset byte count mismatch: " + text_name)
        contents[logical_name] = content
        evidence[logical_name] = {
            "text_name": text_name, "sha256": actual, "utf8_bytes": len(encoded),
            "manifest_match": True,
        }
    return contents, evidence


def load_embedded_module(source, directory):
    """Execute the hash-checked Text without __file__ or the demo's command-line main."""
    require(MODULE_NAME not in sys.modules, "Verifier module already exists in this process")
    module = types.ModuleType(MODULE_NAME)
    module.__package__ = None
    sys.modules[MODULE_NAME] = module
    exec(compile(source, "<embedded:neuro3d_iris_demo.py>", "exec",
                 dont_inherit=True), module.__dict__)
    require("__file__" not in module.__dict__, "Embedded module unexpectedly defines __file__")
    module.HERE = str(directory)
    require(not module.LIVE.get("on", False), "Embedded module started live inference")
    return module


def register_panel(demo, bpy):
    """Register UI classes and inspect their RNA without invoking any operator."""
    demo.register()
    panel = bpy.types.Panel.bl_rna_get_subclass_py("NEURO3D_PT_panel")
    require(panel is demo.NEURO3D_PT_panel, "Portable Neuro3D panel did not register")
    require(panel.bl_space_type == "VIEW_3D" and panel.bl_region_type == "UI" and
            panel.bl_category == "Neuro3D", "Registered panel has the wrong UI location")
    operators, step_evidence = {}, {}
    for name in ("classify_flower", "build_trained", "live"):
        rna = getattr(bpy.ops.neuro3d, name).get_rna_type()
        operators[name] = rna.identifier
        if name == "classify_flower":
            step = rna.properties.get("step")
            require(step is not None and step.type == "INT" and step.default == 1,
                    "Classify operator did not register its step IntProperty(default=1)")
            step_evidence = {"type": step.type, "default": step.default}
    return {"panel": panel.__name__, "panel_registered": True,
            "operators_registered": operators, "operators_invoked": 0,
            "classify_step_property": step_evidence}


def check_missing_embedded_assets(demo, bpy, denied):
    """Require explicit missing-Text failures, restoring each original asset in finally."""
    evidence = []
    for logical_name, loader in (("iris.csv", demo.load_raw),
                                 ("trained_lattice.json", demo.load_state)):
        original_name = ASSET_TEXTS[logical_name]
        block = bpy.data.texts.get(original_name)
        require(block is not None, "Missing original asset before negative control")
        original_content = block.as_string()
        temporary_name = "_portable_missing_" + str(os.getpid()) + "_" + logical_name
        require(bpy.data.texts.get(temporary_name) is None,
                "Temporary missing-asset Text name is already in use")
        denied_before = len(denied)
        message = None
        try:
            block.name = temporary_name
            require(bpy.data.texts.get(original_name) is None,
                    "Missing-asset control did not hide the canonical Text")
            try:
                loader()
            except RuntimeError as exc:
                message = str(exc)
                require(message == "Portable scene is missing embedded asset: " + logical_name,
                        "Unexpected error in missing embedded asset control: " + message)
            else:
                raise RuntimeError("Missing embedded asset was silently accepted: " + logical_name)
        finally:
            block.name = original_name
            restored = bpy.data.texts.get(original_name)
            require(restored is not None and restored.as_pointer() == block.as_pointer() and
                    block.as_string() == original_content,
                    "Failed to restore the original embedded asset: " + logical_name)
        require(len(denied) == denied_before,
                "Missing embedded asset attempted an external file fallback")
        evidence.append({"asset": logical_name, "exception_type": "RuntimeError",
                         "message": message, "original_text_restored": True,
                         "external_fallback_attempts": 0, "classify_calls": 0})
    return evidence


def prepare_reference(demo, texts, bpy, np):
    """Independently check dataset/scaler/split, then use the declared optical model."""
    csv_rows = list(csv.reader(io.StringIO(texts["iris.csv"])))
    require(len(csv_rows) >= 2 and len(csv_rows[0]) == 5, "Invalid Iris CSV header")
    rows = [row for row in csv_rows[1:] if row]
    require(len(rows) == 150 and all(len(row) == 5 for row in rows),
            "Embedded Iris CSV must contain exactly 150 complete rows")
    raw = np.asarray([[float(value) for value in row[:4]] for row in rows], dtype=float)
    require(raw.shape == (150, 4) and np.isfinite(raw).all(), "Invalid raw Iris features")
    species = ["setosa", "versicolor", "virginica"]
    require(list(demo.SPECIES) == species, "Unexpected Iris class ordering")
    labels = np.asarray([species.index(row[4]) for row in rows], dtype=int)
    state = parse_json(texts["trained_lattice.json"])
    require(type(state) is dict, "Embedded trained state is not an object")
    needed = {"theta", "ref", "train_idx", "test_idx", "scaler_lo", "scaler_hi"}
    require(needed <= state.keys(), "Embedded state lacks parameters, split or saved scaler")

    def indices(key, count):
        values = state[key]
        require(type(values) is list and len(values) == count and
                all(type(value) is int and 0 <= value < 150 for value in values) and
                len(set(values)) == count, "Invalid " + key)
        return np.asarray(values, dtype=int)

    train, test = indices("train_idx", 120), indices("test_idx", 30)
    require(set(train.tolist()).isdisjoint(test.tolist()) and
            set(train.tolist() + test.tolist()) == set(range(150)), "Split is not a partition")
    declared_train, declared_test = demo.split()
    require(np.array_equal(train, declared_train) and np.array_equal(test, declared_test),
            "Saved split differs from the demo's fixed split")
    low = np.asarray(state["scaler_lo"], dtype=float)
    high = np.asarray(state["scaler_hi"], dtype=float)
    require(low.shape == high.shape == (4,) and np.isfinite(low).all() and
            np.isfinite(high).all() and (high > low).all(), "Invalid embedded scaler")
    require(np.array_equal(low, raw[train].min(axis=0)) and
            np.array_equal(high, raw[train].max(axis=0)), "Scaler is not fitted on train rows")
    expected_x = (raw - low) / (high - low)
    loaded_raw, loaded_labels = demo.load_raw()
    require(np.array_equal(loaded_raw, raw) and np.array_equal(loaded_labels, labels),
            "Demo raw data differ from the embedded CSV")
    require(demo.load_state() == state, "Demo state differs from the embedded weights")
    features, loaded_labels, scaler = demo.load_iris()
    require(features.shape == (150, 4) and np.isfinite(features).all() and
            np.array_equal(features, expected_x) and np.array_equal(loaded_labels, labels),
            "Demo preprocessing differs from the independently checked embedded data")
    require(np.array_equal(scaler[0], low) and np.array_equal(scaler[1], high),
            "Demo preprocessing used a different scaler")

    theta = np.asarray(state["theta"], dtype=float)
    require(theta.shape == (16,) and np.isfinite(theta).all(), "Invalid trained mirror delays")
    reference = finite_number(state["ref"], "trained reference amplitude")
    require(float(bpy.context.scene["ref"]) == reference, "Scene reference differs from weights")
    saved_theta = np.asarray(parse_json(bpy.context.scene["theta"]), dtype=float)
    require(saved_theta.shape == (4, 4) and
            np.array_equal(saved_theta, theta.reshape(4, 4)), "Scene theta differs from weights")
    inputs, outputs = demo.modes()
    require(len(inputs) == len(outputs) == 8 and len(set(outputs)) == 8 and
            set(demo.CLASS_DET) <= set(outputs), "Expected eight distinct optical outputs")
    matrix = np.asarray(demo.model_U(theta.reshape(4, 4) * demo.LAM / (4 * math.pi)))
    amplitudes = np.asarray(demo.encode(features, reference))
    require(matrix.shape == (8, 8) and amplitudes.shape == (150, 8) and
            np.isfinite(matrix).all() and np.isfinite(amplitudes).all(),
            "Optical model produced an invalid matrix or encoded input")
    model_fields = amplitudes @ matrix.T
    require(np.isfinite(model_fields).all(), "Non-finite reference model fields")
    class_indices = [outputs.index(name) for name in demo.CLASS_DET]
    model_predictions = (np.abs(model_fields[:, class_indices]) ** 2).argmax(axis=1)
    return features, labels, train, test, outputs, class_indices, model_fields, model_predictions


def check_export_sample(sample, outputs):
    """Require a complete, finite measured baseline for a single exported sample."""
    require(type(sample.get("index")) is int and 0 <= sample["index"] < 150,
            "Invalid export sample index")
    require(type(sample.get("prediction")) is int and 0 <= sample["prediction"] < 3,
            "Invalid export sample prediction")
    for key in ("fields", "powers"):
        require(type(sample.get(key)) is dict and set(sample[key]) == set(outputs),
                "Export sample must contain all eight " + key)
    fields = {}
    for name in outputs:
        value = sample["fields"][name]
        require(type(value) is list and len(value) == 2, "Invalid export complex field: " + name)
        fields[name] = complex(finite_number(value[0], name + ".real"),
                               finite_number(value[1], name + ".imag"))
        finite_number(sample["powers"][name], name + ".power", nonnegative=True)
    finite_number(sample.get("escape"), "export escape", nonnegative=True)
    return fields


def run_verification(args, report):
    """Open the copied bundle and measure independent portability and optical gates."""
    import bpy
    import numpy as np

    blend = Path(args.blend).resolve(strict=True)
    manifest_path = Path(args.manifest).resolve(strict=True)
    report_path = Path(args.report).resolve()
    repository = Path(__file__).resolve().parents[2]
    require(blend.suffix.casefold() == ".blend", "Input is not a .blend file")
    require(not blend.is_relative_to(repository), "Portable copy must be outside the repository")
    require(report_path not in (blend, manifest_path), "Report cannot overwrite an input")
    require(bpy.app.background, "Run this verifier in a fresh background Blender process")
    manifest = parse_json(manifest_path.read_text(encoding="utf-8"))
    validate_manifest(manifest)
    actual_blend_hash = sha256_file(blend)
    require(actual_blend_hash == manifest["blend_sha256"], "Copied .blend hash mismatch")
    if "export_pid" in manifest:
        require(type(manifest["export_pid"]) is int and manifest["export_pid"] != os.getpid(),
                "Export and portable verification must use different processes")
    report.update({
        "blend": str(blend), "blend_sha256": actual_blend_hash,
        "blend_manifest_hash_verified": True,
        "manifest_sha256": sha256_file(manifest_path),
        "source_commit_declared_by_manifest": manifest.get("source_commit"),
        "blender_version": bpy.app.version_string, "pid": os.getpid(),
        "export_pid": manifest.get("export_pid"), "background": True,
        "outside_repository": True, "fresh_process_required_by_supervisor": True,
        "export_decoration_invariance_max_declared": manifest.get("export_decoration_invariance_max"),
    })
    bpy.ops.wm.open_mainfile(filepath=str(blend), load_ui=False, use_scripts=False)
    require(Path(bpy.data.filepath).resolve() == blend, "Blender opened a different file")
    texts, asset_evidence = read_embedded_assets(bpy, manifest)
    report["assets"] = asset_evidence
    denied = report["external_asset_access_denied"]
    with deny_external_assets(blend.parent, denied):
        demo = load_embedded_module(texts["neuro3d_iris_demo.py"], blend.parent)
        report["embedded_module_has_file"] = "__file__" in demo.__dict__
        report["isolated_here"] = demo.HERE
        report["panel_registration"] = register_panel(demo, bpy)
        report["missing_embedded_asset_controls"] = check_missing_embedded_assets(demo, bpy, denied)
        limits = dict(demo.VERIFY_LIMITS)
        for name in (*OPTICAL_METRICS, "save_reopen_max"):
            finite_number(limits.get(name), "VERIFY_LIMITS." + name, nonnegative=True)
        report["verification_limits"] = limits
        data = prepare_reference(demo, texts, bpy, np)
        features, labels, train, test, outputs, class_indices, model_fields, model_predictions = data
        baseline_fields = check_export_sample(manifest["export_sample"], outputs)
        baseline = manifest["export_sample"]
        report["data"] = {"rows": 150, "features": 4, "train_rows": 120,
                          "test_rows": 30, "scaler_fitted_on_train_only": True,
                          "source": "embedded Text assets only"}
        report["output_order"] = list(outputs)
        maxima = {name: 0.0 for name in OPTICAL_METRICS}
        predictions, disagreement_rows = [], []
        classified_wall = classified_cpu = 0.0
        casts_total = 0
        for index in range(150):
            report["classify_calls_attempted"] += 1
            wall, cpu = time.perf_counter(), time.process_time()
            prediction, returned_powers, detectors, _, casts = demo.classify(features[index])
            elapsed_wall = time.perf_counter() - wall
            elapsed_cpu = time.process_time() - cpu
            classified_wall += elapsed_wall
            classified_cpu += elapsed_cpu
            report["classify_calls_completed"] += 1
            require(type(prediction) is int and 0 <= prediction < 3, "Invalid scene prediction")
            require(type(casts) is int and casts > 0, "Invalid ray-cast counter")
            require(type(detectors) is dict and set(detectors) <= set(outputs),
                    "Unexpected detector identifier in copied scene")
            # A port with no traced contribution is zero by the tracer's declared semantics.
            # Its absence remains visible below and its value is checked against the model.
            fields = np.asarray([detectors.get(name, 0j) for name in outputs], dtype=complex)
            powers = np.abs(fields) ** 2
            class_powers = np.asarray(returned_powers, dtype=float)
            escape = finite_number(demo.TRACE_INFO.get("escape"), "scene escape", nonnegative=True)
            require(fields.shape == (8,) and np.isfinite(fields).all() and
                    np.isfinite(powers).all() and class_powers.shape == (3,) and
                    np.isfinite(class_powers).all() and (class_powers >= 0).all(),
                    "Non-finite or malformed scene output")
            consistency = float(np.max(np.abs(class_powers - powers[class_indices])))
            require(consistency <= limits["scene_vs_model_max_power_diff"],
                    "Returned class powers disagree with the actual detector fields")
            require(prediction == int(class_powers.argmax()), "Prediction is not the brightest class")
            reference_powers = np.abs(model_fields[index]) ** 2
            residuals = {
                "scene_vs_model_max_power_diff": float(np.max(np.abs(powers - reference_powers))),
                "outputs_complex_vs_model_max": float(np.max(np.abs(fields - model_fields[index]))),
                "escape_max": escape,
                "power_balance_max_err": abs(float(powers.sum()) + escape - 1.0),
            }
            for name, value in residuals.items():
                maxima[name] = max(maxima[name], finite_number(value, name, nonnegative=True))
            predictions.append(prediction)
            if prediction != int(model_predictions[index]):
                disagreement_rows.append(index)
            casts_total += casts
            row = {
                "index": index, "truth": int(labels[index]), "prediction": prediction,
                "model_prediction": int(model_predictions[index]), "ray_casts": casts,
                "fields": {name: [float(value.real), float(value.imag)]
                           for name, value in zip(outputs, fields)},
                "powers": {name: float(value) for name, value in zip(outputs, powers)},
                "model_fields": {name: [float(value.real), float(value.imag)]
                                 for name, value in zip(outputs, model_fields[index])},
                "escape": escape, "residuals": residuals,
                "ports_without_traced_contributions": sorted(set(outputs) - set(detectors)),
                "classify_wall_seconds": elapsed_wall, "classify_cpu_seconds": elapsed_cpu,
            }
            report["rows"].append(row)
            if index == baseline["index"]:
                field_diff = max(abs(fields[i] - baseline_fields[name])
                                 for i, name in enumerate(outputs))
                power_diff = max(abs(float(powers[i]) - baseline["powers"][name])
                                 for i, name in enumerate(outputs))
                report["save_reopen_max"] = float(field_diff)
                report["export_sample_comparison"] = {
                    "index": index, "field_max_diff": float(field_diff),
                    "power_max_diff": float(power_diff),
                    "escape_diff": abs(escape - baseline["escape"]),
                    "prediction_equal": prediction == baseline["prediction"],
                    "limit_name": "save_reopen_max",
                    "field_and_power_limit": limits["save_reopen_max"],
                    "scope": "one measured export sample reopened in this process",
                }
            report.update(maxima)
            report["ray_casts_total"] = casts_total
            report["classification_costs"] = {
                "wall_seconds": classified_wall, "cpu_seconds": classified_cpu,
                "wall_ms_per_completed_sample": 1000 * classified_wall / len(predictions),
                "scope": "classify calls only; no training, render or GPU-energy benchmark",
            }
            if (index + 1) % 10 == 0:
                persist_report(report_path, report)
                print("PORTABLE_IRIS_PROGRESS " + json.dumps({
                    "completed": index + 1, "rows": 150, "ray_casts": casts_total,
                    "classification_wall_seconds": classified_wall}), flush=True)

        require(report["classify_calls_attempted"] == report["classify_calls_completed"] == 150,
                "Verification did not classify exactly 150 rows once each")
        predicted = np.asarray(predictions, dtype=int)
        for name, subset in (("train", train), ("test", test)):
            correct = int((predicted[subset] == labels[subset]).sum())
            model_correct = int((model_predictions[subset] == labels[subset]).sum())
            report["accuracy"][name] = {
                "correct": correct, "total": len(subset), "accuracy": correct / len(subset),
                "model_correct": model_correct, "indices": subset.tolist(),
            }
        report["scene_train_acc"] = report["accuracy"]["train"]["accuracy"]
        report["scene_test_acc"] = report["accuracy"]["test"]["accuracy"]
        report["prediction_disagreements"] = disagreement_rows
        for name in OPTICAL_METRICS:
            if not 0 <= maxima[name] <= limits[name]:
                report["verification_failures"].append(name)
        if disagreement_rows:
            report["verification_failures"].append("scene_model_prediction_disagreement")
        comparison = report.get("export_sample_comparison")
        require(comparison is not None, "Export sample was not measured after reopening")
        for name in ("field_max_diff", "power_max_diff"):
            if not 0 <= comparison[name] <= limits["save_reopen_max"]:
                report["verification_failures"].append("export_sample_" + name)
        if not 0 <= comparison["escape_diff"] <= limits["escape_max"]:
            report["verification_failures"].append("export_sample_escape_diff")
        if not comparison["prediction_equal"]:
            report["verification_failures"].append("export_sample_prediction")
        require(not denied, "Embedded source attempted an external asset read")
        report["external_asset_guard_active_during_all_150_rows"] = True
        report["embedded_assets_rechecked_after_inference"] = read_embedded_assets(bpy, manifest)[1]
        report["metric_status"].update({name: "MEASURED_150_ROWS" for name in OPTICAL_METRICS})
        report["metric_status"]["save_reopen_max"] = "MEASURED_ONE_EXPORT_SAMPLE"
        report["verification_passed"] = not report["verification_failures"]


def main(argv=None):
    """Always retain an explicit failed/incomplete report before returning nonzero."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--blend", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--report", required=True)
    args = parser.parse_args(argv)
    report_path = Path(args.report).resolve()
    input_paths = (Path(args.blend).resolve(), Path(args.manifest).resolve())
    require(report_path not in input_paths, "Report path would overwrite an input")
    report = {
        "schema": SCHEMA + "-verification", "status": "RUNNING", "started_utc": utc_now(),
        "verification_passed": False, "verification_failures": [],
        "classify_calls_attempted": 0, "classify_calls_completed": 0, "rows": [],
        "accuracy": {}, "external_asset_access_denied": [],
        "decoration_invariance_max": None, "save_reopen_max": None,
        "metric_status": {"decoration_invariance_max": "NOT_MEASURED_BY_THIS_VERIFIER",
                          "save_reopen_max": "NOT_MEASURED"},
        "operations": {"build": False, "reset": False, "train": False,
                       "render": False, "save_blend": False, "gpu_workload_requested": False},
        "process_cost_scope": "CPU/wall time of this verification process; not an energy benchmark",
    }
    wall, cpu = time.perf_counter(), time.process_time()
    persist_report(report_path, report)
    try:
        run_verification(args, report)
        report["status"] = "PASS" if report["verification_passed"] else "FAIL"
    except BaseException as exc:
        report["status"] = "FAIL"
        report["verification_passed"] = False
        report["verification_failures"].append(type(exc).__name__ + ": " + str(exc))
        report["exception_traceback"] = traceback.format_exc()
    finally:
        report["finished_utc"] = utc_now()
        report["total_wall_seconds"] = time.perf_counter() - wall
        report["total_cpu_seconds"] = time.process_time() - cpu
        persist_report(report_path, report)
    print("PORTABLE_IRIS_RESULT " + json.dumps({
        "status": report["status"], "report": str(report_path),
        "classified": report["classify_calls_completed"],
        "failures": report["verification_failures"]}), flush=True)
    return 0 if report["verification_passed"] else 1


if __name__ == "__main__":
    arguments = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    raise SystemExit(main(arguments))
