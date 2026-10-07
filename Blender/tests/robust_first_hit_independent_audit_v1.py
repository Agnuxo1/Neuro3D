"""Independent standard-library audit for point-5 retained native first-hit readbacks.

No Blender, GPU module, selector implementation, shader or project arithmetic module is
imported. Geometry is decoded independently from the retained scene hi/lo wire and
evaluated with exact Fraction arithmetic.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import json
import math
import os
from pathlib import Path
import struct
import tempfile
import time
import traceback

POISON = 0x5A5A5A5A
MAGIC = 0x4E33484C
STATUS = {
    "SELECT": 1, "MISS": 2, "TRUE_TIE": 3, "BOUNDARY": 4,
    "CONTACT": 5, "COPLANAR": 6, "INVALID_GEOMETRY": 7,
    "NUMERIC_OVERFLOW": 8,
}
DEPARTURE = {None: 0, "mirror": 1, "t": 2, "r": 3}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def file_sha(path):
    return sha(Path(path).read_bytes())


def read_json(path, expected=None):
    raw = Path(path).read_bytes()
    need(len(raw) <= 32 * 1024 * 1024, "JSON cap")
    if expected is not None:
        need(sha(raw) == expected, "SHA mismatch: " + str(path))
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, "duplicate JSON key")
            result[key] = value
        return result
    def bad(value):
        raise ValueError("nonfinite JSON: " + value)
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=bad), raw


def atomic(path, value):
    path = Path(path)
    need(path.parent.is_dir() and not path.exists(), "fresh audit output required")
    raw = (json.dumps(value, indent=2, allow_nan=False, sort_keys=True) + "\n").encode()
    with tempfile.NamedTemporaryFile("wb", delete=False, dir=path.parent,
                                     prefix=path.name + ".", suffix=".tmp") as stream:
        temp = Path(stream.name)
        stream.write(raw); stream.flush(); os.fsync(stream.fileno())
    os.replace(temp, path)
    return raw


def word_fraction(word):
    need(type(word) is int and 0 <= word <= 0xFFFFFFFF, "uint32 word")
    sign = -1 if word >> 31 else 1
    exponent = (word >> 23) & 0xFF
    mantissa = word & 0x7FFFFF
    need(exponent != 0xFF and not (exponent == 0 and mantissa), "unsupported binary32")
    if exponent == 0:
        return F(0)
    significand = mantissa | 0x800000
    power = exponent - 127 - 23
    value = F(sign * significand)
    return value * (1 << power) if power >= 0 else value / (1 << -power)


def words(raw):
    need(len(raw) % 4 == 0, "word aligned")
    return list(struct.unpack("<%dI" % (len(raw) // 4), raw))


def signed512(limbs):
    need(len(limbs) == 16, "signed512 limbs")
    value = sum(int(word) << (32 * i) for i, word in enumerate(limbs))
    return value - (1 << 512) if value >> 511 else value


def packet_wire(packet):
    need(type(packet) is dict and packet.get("schema") == "neuro3d-scene-hilo-transport-v1",
         "point4 packet schema")
    raw = bytes.fromhex(packet["wire_hex"])
    need(sha(raw) == packet["manifest"]["wire_sha256"], "wire hash")
    return raw


def scalar(data, layout, index):
    need(type(index) is int and 0 <= index < layout["scalar_count"], "scalar index")
    base = layout["scalar_offset"] + index * layout["scalar_stride"]
    return word_fraction(data[base]) + word_fraction(data[base + 1])


def source(data, layout, index):
    base = layout["source_offset"] + index * layout["source_stride"]
    need(data[base] == index and data[base + 1] == 0xFFFFFFFF, "source identity")
    origin = tuple(scalar(data, layout, data[base + 2 + axis]) for axis in range(3))
    direction = tuple(scalar(data, layout, data[base + 5 + axis]) for axis in range(3))
    return origin, direction


def vertex(data, layout, index):
    base = layout["vertex_offset"] + index * layout["vertex_stride"]
    need(data[base] == index, "vertex identity")
    return tuple(scalar(data, layout, data[base + 3 + axis]) for axis in range(3))


def tri(data, layout, index):
    base = layout["triangle_offset"] + index * layout["triangle_stride"]
    need(data[base] == index, "triangle identity")
    return {
        "primitive_id": index, "object": data[base + 1],
        "vertices": tuple(data[base + 3:base + 6]),
    }


def sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def cross(a, b):
    return (a[1]*b[2]-a[2]*b[1],
            a[2]*b[0]-a[0]*b[2],
            a[0]*b[1]-a[1]*b[0])


def dot(a, b):
    return sum((x*y for x, y in zip(a, b)), F(0))


def zero(v):
    return all(x == 0 for x in v)


def candidate(data, layout, origin, direction, index):
    record = tri(data, layout, index)
    a, b, c = (vertex(data, layout, i) for i in record["vertices"])
    e1, e2 = sub(b, a), sub(c, a)
    normal = cross(e1, e2)
    if zero(normal):
        return dict(record, klass="degenerate")
    p = cross(direction, e2)
    determinant = dot(e1, p)
    rel = sub(origin, a)
    if determinant == 0:
        return dict(record, klass="coplanar" if dot(rel, normal) == 0 else "outside")
    q = cross(rel, e1)
    u = dot(rel, p)
    v = dot(direction, q)
    t = dot(e2, q)
    if determinant < 0:
        determinant, u, v, t = -determinant, -u, -v, -t
    uv = u + v
    if t < 0 or u < 0 or v < 0 or uv > determinant:
        return dict(record, klass="outside")
    common = dict(record, t=t/determinant, normal=normal)
    if t == 0:
        return dict(common, klass="contact")
    if u == 0 or v == 0 or uv == determinant:
        return dict(common, klass="boundary")
    return dict(common, klass="interior")


def parallel(a, b):
    return cross(a, b) == (F(0), F(0), F(0))


def independent_select(packet, source_index, previous, event):
    raw = packet_wire(packet)
    data = words(raw)
    layout = packet["manifest"]["abi"]
    need(data[:3] == [MAGIC, 1, 32] and data[3] == len(data), "wire ABI")
    need(0 <= source_index < layout["source_count"] and layout["triangle_count"] <= 64,
         "bounded query")
    origin, direction = source(data, layout, source_index)
    need(not zero(direction), "nonzero direction")
    if previous is None:
        need(event is None, "event without previous")
    else:
        need(type(previous) is int and 0 <= previous < layout["triangle_count"] and
             event in ("mirror", "t", "r"), "previous/event contract")
    positives = []
    contacts = []
    coplanars = []
    degenerates = []
    excluded = 0
    for index in range(layout["triangle_count"]):
        row = candidate(data, layout, origin, direction, index)
        if row["klass"] == "degenerate":
            degenerates.append(index)
        elif row["klass"] == "coplanar":
            coplanars.append(index)
        elif row["klass"] == "contact":
            if index == previous and event in ("mirror", "t", "r"):
                excluded += 1
            else:
                contacts.append(index)
        elif row["klass"] in ("boundary", "interior"):
            positives.append(row)
    common = {
        "excluded_previous_contacts": excluded,
        "contact_primitive_ids": contacts,
        "coplanar_primitive_ids": coplanars,
        "degenerate_primitive_ids": degenerates,
    }
    if degenerates:
        return dict(common, status="INVALID_GEOMETRY", status_code=7,
                    selected_primitive=None, selected_object=None, ties=[], equiv=False, t=None)
    if coplanars:
        return dict(common, status="COPLANAR", status_code=6,
                    selected_primitive=None, selected_object=None, ties=[], equiv=False, t=None)
    if contacts:
        return dict(common, status="CONTACT", status_code=5,
                    selected_primitive=None, selected_object=None, ties=sorted(contacts), equiv=False, t=None)
    if not positives:
        return dict(common, status="MISS", status_code=2,
                    selected_primitive=None, selected_object=None, ties=[], equiv=False, t=None)
    best_t = min(row["t"] for row in positives)
    tied = [row for row in positives if row["t"] == best_t]
    winner = min(tied, key=lambda row: row["primitive_id"])
    equivalent = len(tied) > 1 and all(
        row["object"] == winner["object"] and parallel(row["normal"], winner["normal"])
        for row in tied)
    if len(tied) > 1 and not equivalent:
        status, code = "TRUE_TIE", 3
    elif winner["klass"] == "boundary" and not equivalent:
        status, code = "BOUNDARY", 4
    else:
        status, code = "SELECT", 1
    return dict(common, status=status, status_code=code,
                selected_primitive=winner["primitive_id"], selected_object=winner["object"],
                ties=sorted(row["primitive_id"] for row in tied), equiv=equivalent, t=best_t)


def tie_mask(ids):
    lo = hi = 0
    for value in ids:
        if value < 32:
            lo |= 1 << value
        else:
            hi |= 1 << (value - 32)
    return lo, hi


def parse_gpu(raw, nonce):
    data = words(raw)
    need(len(data) == 64 and data[0] == 0x35484652 and data[1] == 1 and
         data[13] == nonce and data[14] == (nonce ^ 0xFFFFFFFF) and data[15] == 1,
         "native result header")
    return {
        "status_code": data[2], "source_index": data[3],
        "selected_primitive": None if data[4] == 0xFFFFFFFF else data[4],
        "selected_object": None if data[5] == 0xFFFFFFFF else data[5],
        "tie_count": data[6], "boundary": bool(data[7]),
        "excluded_previous_contacts": data[8], "contact_count": data[9],
        "coplanar_count": data[10], "degenerate_count": data[11],
        "triangle_count": data[12], "t_num": signed512(data[16:32]),
        "t_den": signed512(data[32:48]), "tie_mask_lo": data[48],
        "tie_mask_hi": data[49], "equivalent_surface_tie": bool(data[50]),
        "ambiguous_tie": bool(data[51]),
    }


def main():
    parser = argparse.ArgumentParser()
    for name in ("worker-report", "worker-sha256", "guard-receipt", "guard-sha256",
                 "input-manifest", "input-sha256", "repo", "out"):
        parser.add_argument("--" + name, required=True)
    args = parser.parse_args()
    repo = Path(args.repo).resolve()
    out = Path(args.out).resolve()
    started = time.perf_counter()
    report = {
        "schema": "neuro3d.robust_first_hit.independent_audit.cpu.v1",
        "status": "FAIL", "verification_passed": False,
        "auditor_gpu_executed": False, "auditor_blender_executed": False,
        "implementation_imports": 0, "cases": [],
    }
    try:
        worker, worker_raw = read_json(args.worker_report, args.worker_sha256)
        guard, guard_raw = read_json(args.guard_receipt, args.guard_sha256)
        manifest, manifest_raw = read_json(args.input_manifest, args.input_sha256)
        need(guard.get("status") == "PASS" and guard.get("GPU_job_admission") is True and
             guard.get("native_gpu_execution_verified") is True and
             guard.get("cleanup_confirmed") is True and guard.get("worker_exit_code") == 0,
             "guard did not pass")
        need(guard.get("worker_report_sha256") == sha(worker_raw), "guard/worker binding")
        need(worker.get("schema") == "neuro3d.robust_first_hit.native_report.v1" and
             worker.get("status") == "PASS" and worker.get("verification_passed") is True and
             worker.get("native_gpu_executed") is True and worker.get("completed_readbacks") == 20,
             "worker did not pass all readbacks")
        need(worker.get("gpu_readback_sha256") == guard.get("gpu_readback_sha256"),
             "guard/worker readback hash")
        need(manifest.get("schema") == "neuro3d.robust_first_hit.native_job.v1" and
             manifest.get("limits") == {"max_triangles": 64, "max_dispatches": 20},
             "frozen input profile")
        records = worker["gpu_readback_records"]
        need(len(records) == 20, "20 native readbacks")
        digest = hashlib.sha256()
        record_index = 0
        thin_gap_verified = []
        real_selects = 0
        for case in manifest["cases"]:
            packet_path = Path(case["packet_path"])
            if not packet_path.is_absolute():
                packet_path = repo / packet_path
            packet, packet_raw = read_json(packet_path, case["packet_sha256"])
            wire = packet_wire(packet)
            case_report = {"case_id": case["case_id"], "queries": []}
            report["cases"].append(case_report)
            for q_index, query in enumerate(case["queries"]):
                record = records[record_index]
                need(record["case_id"] == case["case_id"] and
                     record["query_index"] == q_index and
                     record["source_index"] == query["source_index"] and
                     record["previous_primitive"] == query["previous_primitive"] and
                     record["departure_event"] == query["departure_event"], "record ordering")
                echo = bytes.fromhex(record["input_echo_hex"])
                result_raw = bytes.fromhex(record["result_hex"])
                digest.update(echo); digest.update(result_raw)
                echo_words = words(echo)
                expected_echo = words(wire) + [POISON] * (len(echo_words) - len(wire)//4)
                need(echo_words == expected_echo, "bit-exact native packet echo")
                seed = (worker["job_id"] + "/" + case["case_id"] + "/" + str(q_index)).encode()
                nonce = int.from_bytes(hashlib.sha256(seed).digest()[:4], "little") & 0x7FFFFFFF
                native = parse_gpu(result_raw, nonce)
                oracle = independent_select(packet, query["source_index"],
                                            query["previous_primitive"], query["departure_event"])
                lo, hi = tie_mask(oracle["ties"])
                need(native["status_code"] == oracle["status_code"] and
                     native["selected_primitive"] == oracle["selected_primitive"] and
                     native["selected_object"] == oracle["selected_object"] and
                     native["tie_count"] == len(oracle["ties"]) and
                     native["tie_mask_lo"] == lo and native["tie_mask_hi"] == hi and
                     native["equivalent_surface_tie"] == oracle["equiv"] and
                     native["excluded_previous_contacts"] == oracle["excluded_previous_contacts"],
                     "native result differs from independent exact oracle")
                frozen = query["expected"]
                need(frozen["status"] == oracle["status"] and
                     frozen["status_code"] == oracle["status_code"] and
                     frozen["selected_primitive"] == oracle["selected_primitive"] and
                     frozen["selected_object"] == oracle["selected_object"] and
                     frozen["tie_primitive_ids"] == oracle["ties"] and
                     bool(frozen["equivalent_surface_tie"]) == oracle["equiv"] and
                     frozen["excluded_previous_contacts"] == oracle["excluded_previous_contacts"],
                     "frozen CPU expectation differs from independent oracle")
                if oracle["t"] is None:
                    need(native["t_num"] == native["t_den"] == 0 and frozen["t"] is None,
                         "STOP/miss t must be absent")
                else:
                    need(native["t_den"] > 0 and F(native["t_num"], native["t_den"]) == oracle["t"],
                         "native exact t fraction")
                    need(frozen["t"] is not None and F(frozen["t"][0], frozen["t"][1]) == oracle["t"],
                         "frozen t fraction")
                if case["case_id"].startswith("thin_gap_"):
                    need(oracle["status"] == "SELECT", "thin gap select")
                    thin_gap_verified.append(case["case_id"])
                if case["case_id"] in ("k3_real", "k4_real"):
                    need(oracle["status"] == "SELECT" and oracle["equiv"], "real triangulation surface select")
                    real_selects += 1
                case_report["queries"].append({
                    "query_index": q_index, "status": oracle["status"],
                    "selected_primitive": oracle["selected_primitive"],
                    "tie_primitive_ids": oracle["ties"],
                    "equivalent_surface_tie": oracle["equiv"],
                    "excluded_previous_contacts": oracle["excluded_previous_contacts"],
                    "t": None if oracle["t"] is None else
                         [oracle["t"].numerator, oracle["t"].denominator],
                })
                record_index += 1
        need(record_index == 20 and real_selects == 9 and
             sorted(thin_gap_verified) == ["thin_gap_2m53", "thin_gap_2m54", "thin_gap_2m60"],
             "full preregistered coverage")
        need(digest.hexdigest() == worker["gpu_readback_sha256"] == guard["gpu_readback_sha256"],
             "complete readback hash")
        report.update(
            status="PASS_CPU_INDEPENDENT_EXACT_AUDIT", verification_passed=True,
            retained_native_evidence_validated=True, total_queries=20,
            real_scene_selects=real_selects, thin_gap_cases=thin_gap_verified,
            readback_sha256=digest.hexdigest(),
            worker_sha256=sha(worker_raw), guard_sha256=sha(guard_raw),
            input_sha256=sha(manifest_raw),
        )
    except BaseException as exc:
        report["error"] = type(exc).__name__ + ": " + str(exc)
        report["traceback"] = traceback.format_exc()
    report["created_utc"] = datetime.now(timezone.utc).isoformat()
    report["audit_wall_seconds"] = time.perf_counter() - started
    raw = atomic(out, report)
    print(json.dumps({"status": report["status"], "path": str(out),
                      "sha256": sha(raw), "error": report.get("error")}, sort_keys=True))
    return 0 if report["verification_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
