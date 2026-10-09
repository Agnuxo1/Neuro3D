"""blender -b scene.blend --disable-autoexec --python THIS -- --output NEW.json."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from Blender.blender_lab.scene_capture_v1 import capture_scene, write_capture


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--network", type=Path, help="Optional explicit neural binding contract")
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    network = None
    if args.network:
        def unique_keys(items):
            result = {}
            for key, value in items:
                if key in result:
                    raise ValueError("duplicate network contract key")
                result[key] = value
            return result
        raw = args.network.read_bytes()
        if len(raw) > 2**20:
            raise ValueError("network contract exceeds 1 MiB bound")
        network = json.loads(raw, object_pairs_hook=unique_keys,
                             parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite JSON")))
    result = capture_scene(network=network)
    write_capture(args.output, result)
    print("BLENDER_LAB_CAPTURE " + json.dumps({"state_sha256": result["state_sha256"],
          "objects": len(result["state"]["objects"]), "instances": len(result["state"]["instances"]),
          "network_bound": network is not None, "optical_forward_executed": False}))


if __name__ == "__main__":
    main()
