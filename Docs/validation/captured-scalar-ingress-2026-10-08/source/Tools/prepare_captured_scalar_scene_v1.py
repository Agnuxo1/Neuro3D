"""Prepare scalar CPU inputs from a capture and explicit optical semantics."""
import argparse
from pathlib import Path
import sys
import json

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from Tools.bind_network_capture_v1 import read_json
from Blender.blender_lab.scene_capture_v1 import canonical_bytes, need
from Blender.blender_lab.scalar_scene_ingress_v1 import prepare_scalar_scene, rational_wire


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture", required=True, type=Path)
    parser.add_argument("--semantics", required=True, type=Path)
    parser.add_argument("--fields", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    capture, capture_sha = read_json(args.capture, 128 * 2**20)
    semantics, semantics_sha = read_json(args.semantics, 2**20)
    fields, fields_sha = read_json(args.fields, 2**20)
    scene = prepare_scalar_scene(capture, semantics, fields)
    scene["blender_lab_ingress"]["input_file_sha256"] = {
        "capture": capture_sha, "semantics": semantics_sha, "fields": fields_sha}
    raw = canonical_bytes(rational_wire(scene))
    need(len(raw) <= 8 * 2**20 and args.out.parent.is_dir(), "bounded output and existing parent required")
    with args.out.open("xb") as stream:
        stream.write(raw)
    print(json.dumps({"status": "STRUCTURALLY_ADMITTED", **scene["blender_lab_ingress"]["counts"],
                      "optical_forward_executed": False, "field_certified": False}))


if __name__ == "__main__":
    main()
