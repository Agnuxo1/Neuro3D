"""Export the current trained Iris scene and its exact embedded assets, without rendering.
Run inside background Blender: --python this_file -- --output scene.blend --manifest manifest.json.
"""
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
import time

import bpy
import numpy as np


def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--source-commit", default="unrecorded")
    parser.add_argument("--sample", type=int, default=71)
    args = parser.parse_args(argv)
    if not bpy.app.background:
        raise RuntimeError("This exporter requires a fresh background Blender process")
    source_path = Path(__file__).with_name("neuro3d_iris_demo.py")
    source = source_path.read_text(encoding="utf-8")
    spec = importlib.util.spec_from_file_location("neuro3d_export_source", source_path)
    demo = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = demo
    spec.loader.exec_module(demo)
    started = time.perf_counter()
    state = demo.load_state()
    features, labels, _ = demo.load_iris()
    if not 0 <= args.sample < len(features):
        raise ValueError("Export sample is outside the dataset")
    demo.build_scene(np.asarray(state["theta"]).reshape(demo.K, demo.K), state["ref"], reset=True)
    demo.setup_render()
    pred, powers, fields_before, segments, casts = demo.classify(features[args.sample])
    _, outputs = demo.modes()
    if set(fields_before) != set(outputs):
        raise RuntimeError("Exporter did not observe all eight detector outputs")
    if not np.isfinite(list(fields_before.values())).all():
        raise RuntimeError("Non-finite export fields")
    demo.show(segments, powers, pred, truth=int(labels[args.sample]), x_row=features[args.sample])
    pred_after, powers_after, fields_after, _, casts_after = demo.classify(features[args.sample])
    decoration_error = max(abs(fields_before[name] - fields_after[name]) for name in outputs)
    if not math.isfinite(decoration_error) or decoration_error > demo.VERIFY_LIMITS["decoration_invariance_max"]:
        raise RuntimeError("Decoration altered the optical computation")
    bpy.context.scene["flower"] = args.sample
    text = bpy.data.texts.get("neuro3d_iris_demo.py") or bpy.data.texts.new("neuro3d_iris_demo.py")
    text.from_string(source)
    text.use_fake_user = True
    text.use_module = False
    demo.embed_assets()
    assets = {}
    for name, text_name in (
        ("neuro3d_iris_demo.py", "neuro3d_iris_demo.py"),
        ("iris.csv", "neuro3d.asset.iris.csv"),
        ("trained_lattice.json", "neuro3d.asset.trained_lattice.json"),
    ):
        block = bpy.data.texts[text_name]
        block.use_fake_user = True
        assets[name] = {"text_name": text_name, "sha256": digest(block.as_string())}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(args.output.resolve()), check_existing=False)
    manifest = {
        "schema": "neuro3d-iris-portable-v1",
        "bundle_version": 1,
        "source_commit": args.source_commit,
        "blender_version": bpy.app.version_string,
        "blend_sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
        "assets": assets,
        "export_sample": {
            "index": args.sample,
            "prediction": pred_after,
            "fields": {name: [fields_after[name].real, fields_after[name].imag] for name in outputs},
            "powers": {name: abs(fields_after[name]) ** 2 for name in outputs},
            "escape": demo.TRACE_INFO["escape"],
        },
        "export_decoration_invariance_max": decoration_error,
        "export_decoration_limit": demo.VERIFY_LIMITS["decoration_invariance_max"],
        "export_ray_casts": casts + casts_after,
        "export_seconds": time.perf_counter() - started,
        "render_executed": False,
        "training_executed": False,
        "inference_route": "Blender scene.ray_cast and Python complex sums",
    }
    args.manifest.write_text(json.dumps(manifest, indent=2, allow_nan=False), encoding="utf-8")
    print("IRIS_PORTABLE_EXPORTED", json.dumps({"blend": str(args.output), "sha256": manifest["blend_sha256"], "decoration_error": decoration_error}), flush=True)


if __name__ == "__main__":
    main(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
