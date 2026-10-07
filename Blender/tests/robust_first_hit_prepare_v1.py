"""Prepare the frozen point-5 exact first-hit GPU input manifest on CPU only."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from Blender.benchmarks.capacity_audit import robust_first_hit_exact_v1 as exact
from Blender.benchmarks.capacity_audit import scene_hilo_transport_v1 as transport

SCHEMA = "neuro3d.robust_first_hit.native_job.v1"
REAL_DIR = ROOT / "Docs/validation/scene-hilo-native-2026-10-06/inputs01"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def relative(path):
    return str(Path(path).resolve().relative_to(ROOT)).replace("\\", "/")


def write_json(path, value):
    raw = (json.dumps(value, indent=2, allow_nan=False) + "\n").encode()
    path.write_bytes(raw)
    return hashlib.sha256(raw).hexdigest()


def freeze(result):
    use_t = result["status"] in ("SELECT", "TRUE_TIE", "BOUNDARY")
    return {
        "status": result["status"],
        "status_code": result["status_code"],
        "selected_primitive": result["selected_primitive"],
        "selected_object": result["selected_object"],
        "tie_primitive_ids": result["tie_primitive_ids"],
        "equivalent_surface_tie": bool(result.get("equivalent_surface_tie", False)),
        "excluded_previous_contacts": result["excluded_previous_contacts"],
        "t": result["t"] if use_t else None,
    }


def query(packet, source_index=0, previous_primitive=None, departure_event=None):
    result = exact.select(packet, source_index, previous_primitive=previous_primitive,
                          departure_event=departure_event)
    return {
        "source_index": source_index,
        "previous_primitive": previous_primitive,
        "departure_event": departure_event,
        "expected": freeze(result),
    }


def plane(x, scale=4.0):
    return exact.mirror([(x, 0.0, 0.0), (x, scale, 0.0), (x, 0.0, scale)])


def synthetic(objects, *, position=(1.0, 1.0, 1.0), direction=(-1.0, 0.0, 0.0),
              case_id):
    snapshot = exact.make_snapshot(objects, [exact.source_row(position, direction)])
    return exact.synthetic_packet(snapshot, label=case_id)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    out = args.out_dir.resolve()
    if out.exists() and any(out.iterdir()):
        raise RuntimeError("fresh empty point-5 input directory required")
    out.mkdir(parents=True, exist_ok=True)
    cases = []

    for case_id, filename in (("k3_real", "k3_baseline.packet.json"),
                              ("k4_real", "k4_baseline.packet.json")):
        source = REAL_DIR / filename
        packet = json.loads(source.read_text(encoding="utf-8"))
        queries = [query(packet, index)
                   for index in range(packet["manifest"]["abi"]["source_count"])]
        cases.append({
            "case_id": case_id, "input_class": "real_reopened_baseline",
            "packet_path": relative(source), "packet_sha256": sha(source),
            "queries": queries,
        })

    generated = []
    for power in (53, 54, 60):
        delta = 2.0 ** -power
        generated.append((
            "thin_gap_2m" + str(power),
            synthetic({"a_far": plane(0.0), "z_near": plane(delta)},
                      case_id="thin-gap-" + str(power)),
            None, None,
        ))

    generated.append((
        "true_coincident_objects",
        synthetic({"a": plane(0.0), "b": plane(0.0)}, case_id="true-tie"),
        None, None,
    ))

    delta = 2.0 ** -60
    contact_packet = synthetic(
        {"near": plane(delta), "previous": plane(0.0)},
        position=(0.0, 1.0, 1.0), direction=(1.0, 0.0, 0.0), case_id="contact-gap")
    generated.append((
        "previous_exact_contact_then_2m60_gap", contact_packet,
        exact.object_primitive(contact_packet, "previous"), "mirror",
    ))

    return_packet = synthetic(
        {"previous": plane(0.0)}, position=(-1.0, 1.0, 1.0),
        direction=(1.0, 0.0, 0.0), case_id="later-return")
    generated.append((
        "legitimate_later_return_same_primitive", return_packet,
        exact.object_primitive(return_packet, "previous"), "r",
    ))

    generated.extend([
        ("outer_boundary", synthetic({"only": plane(0.0, 2.0)}, case_id="boundary"),
         None, None),
        ("coplanar", synthetic({"only": plane(0.0)}, position=(0.0, 0.5, 0.5),
                               direction=(0.0, 1.0, 0.0), case_id="coplanar"),
         None, None),
        ("degenerate", synthetic({"bad": exact.mirror([
             (0.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 2.0, 0.0)])},
             case_id="degenerate"), None, None),
        ("near_parallel_2m100", synthetic({"only": plane(0.0)},
             direction=(-(2.0 ** -100), 0.0, 0.0), case_id="near-parallel"),
         None, None),
        ("extreme_coordinate", synthetic({"only": plane(999999.0)},
             position=(1000000.0, 1.0, 1.0), direction=(-1.0, 0.0, 0.0),
             case_id="extreme"), None, None),
    ])

    for case_id, packet, previous, event in generated:
        packet_path = out / (case_id + ".packet.json")
        write_json(packet_path, packet)
        cases.append({
            "case_id": case_id, "input_class": "synthetic_adversarial",
            "packet_path": relative(packet_path), "packet_sha256": sha(packet_path),
            "queries": [query(packet, 0, previous, event)],
        })

    dispatches = sum(len(case["queries"]) for case in cases)
    if dispatches != 20 or len(cases) != 13:
        raise RuntimeError("expected 13 cases / 20 queries, got %d / %d" %
                           (len(cases), dispatches))
    manifest = {
        "schema": SCHEMA,
        "expected_backend": "OPENGL",
        "expected_renderer_contains": "RTX 3090",
        "limits": {"max_triangles": 64, "max_dispatches": 20},
        "cases": cases,
    }
    manifest_path = out / "input_manifest.json"
    digest = write_json(manifest_path, manifest)
    summary = {
        "schema": "neuro3d.robust_first_hit.preparation.v1",
        "status": "PASS_CPU_PREPARATION",
        "manifest": relative(manifest_path),
        "manifest_sha256": digest,
        "cases": len(cases), "queries": dispatches,
        "real_queries": 9, "synthetic_queries": 11,
        "thin_gap_powers": [53, 54, 60],
        "fixed_bias": False, "epsilon_tie_band": False,
        "source_module_sha256": sha(ROOT / "Blender/benchmarks/capacity_audit/robust_first_hit_exact_v1.py"),
    }
    write_json(out / "prepare_report.json", summary)
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
