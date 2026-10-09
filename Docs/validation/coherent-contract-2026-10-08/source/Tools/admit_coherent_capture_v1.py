"""Admit a captured own-network packet with an explicit coherent contract."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from Blender.blender_lab.coherent_contract_v1 import prepare_coherent_scene
from Blender.blender_lab.scalar_scene_ingress_v1 import rational_wire
from Blender.blender_lab.scene_capture_v1 import canonical_bytes, need
from Tools.bind_network_capture_v1 import read_json


def main():
    parser = argparse.ArgumentParser()
    for name in ("capture", "semantics", "fields", "contract", "out"):
        parser.add_argument("--" + name, required=True, type=Path)
    args = parser.parse_args()
    paths = {name: getattr(args, name) for name in ("capture", "semantics", "fields", "contract")}
    loaded = {name: read_json(path, (128 if name == "capture" else 2) * 2**20) for name, path in paths.items()}
    inputs = {name: value[0] for name, value in loaded.items()}
    pins = {name: value[1] for name, value in loaded.items()}
    packet = prepare_coherent_scene(inputs["capture"], inputs["semantics"], inputs["fields"], inputs["contract"])
    packet["blender_lab_ingress"]["input_file_sha256"] = {name: pins[name] for name in ("capture", "semantics", "fields")}
    packet["blender_lab_optical_contract"]["input_file_sha256"] = pins
    raw = canonical_bytes(rational_wire(packet))
    need(len(raw) <= 8 * 2**20 and args.out.parent.is_dir(), "bounded output and existing parent required")
    with args.out.open("xb") as output:
        output.write(raw)
    report = {"output": str(args.out), "bytes": args.out.stat().st_size,
              "sha256": hashlib.sha256(args.out.read_bytes()).hexdigest(),
              "optical_forward_executed": False, "field_certified": False,
              "counts": packet["blender_lab_ingress"]["counts"]}
    print(json.dumps(report))


if __name__ == "__main__":
    main()
