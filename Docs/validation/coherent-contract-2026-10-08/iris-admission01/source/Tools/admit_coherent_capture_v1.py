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


def main():
    parser = argparse.ArgumentParser()
    for name in ("capture", "semantics", "fields", "contract", "out"):
        parser.add_argument("--" + name, required=True, type=Path)
    args = parser.parse_args()
    paths = {name: getattr(args, name) for name in ("capture", "semantics", "fields", "contract")}
    inputs = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in paths.items()}
    pins = {name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in paths.items()}
    packet = prepare_coherent_scene(inputs["capture"], inputs["semantics"], inputs["fields"], inputs["contract"])
    packet["blender_lab_optical_contract"]["input_file_sha256"] = pins
    raw = json.dumps(rational_wire(packet), indent=2, allow_nan=False) + "\n"
    with args.out.open("x", encoding="utf-8", newline="\n") as output:
        output.write(raw)
    report = {"output": str(args.out), "bytes": args.out.stat().st_size,
              "sha256": hashlib.sha256(args.out.read_bytes()).hexdigest(),
              "optical_forward_executed": False, "field_certified": False,
              "counts": packet["blender_lab_ingress"]["counts"]}
    print(json.dumps(report))


if __name__ == "__main__":
    main()
