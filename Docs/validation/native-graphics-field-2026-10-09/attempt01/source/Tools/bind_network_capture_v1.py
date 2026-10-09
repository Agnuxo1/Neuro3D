"""Resolve a neural binding contract against an existing captured Blender scene.

This software operation does not run Blender, optical propagation or training.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from Blender.blender_lab.scene_capture_v1 import digest, resolve_network, validate_capture, write_capture


def read_json(path: Path, cap: int):
    raw = path.read_bytes()
    if len(raw) > cap:
        raise ValueError("bounded JSON input exceeded")
    def unique_pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result
    value = json.loads(raw, object_pairs_hook=unique_pairs,
                       parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite JSON")))
    return value, hashlib.sha256(raw).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture", required=True, type=Path)
    parser.add_argument("--network", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    snapshot, capture_hash = read_json(args.capture, 128 * 2**20)
    network, network_hash = read_json(args.network, 2**20)
    validate_capture(snapshot)
    snapshot["state"]["network"] = resolve_network(network, snapshot["state"]["objects"])
    snapshot["state_sha256"] = digest(snapshot["state"])
    snapshot["provenance"].update(binding_resolution_mode="AFTER_CAPTURE_FROM_SNAPSHOT",
                                  unbound_capture_sha256=capture_hash, network_contract_sha256=network_hash)
    write_capture(args.output, snapshot)
    print(json.dumps({"state_sha256": snapshot["state_sha256"], "network_bound": True,
                      "optical_forward_executed": False, "training_executed": False}))


if __name__ == "__main__":
    main()
