"""Independent CPU audit of retained scene-hi/lo native outputs.

Only standard-library modules are imported. The host implementation, shader,
codec, Blender and GPU APIs are never imported or executed. Input hashes are
provided by the controller after the native job completes.
"""
import argparse
from fractions import Fraction as F
import hashlib
import json
import math
import os
from pathlib import Path
import struct
import time
import traceback
from datetime import datetime, timezone

AUDITOR_BYTES = Path(__file__).read_bytes() if "__file__" in globals() and Path(__file__).is_file() else None
AUDITOR_SOURCE = AUDITOR_BYTES.decode("utf-8") if AUDITOR_BYTES is not None else None
PREVIOUS_AUDITOR_SHA256 = "65e26c3c2724b4e16f908de871328f65386d8fd9f3f2dd0e83383a2d8b3f3d37"
EXPECTED_CODE_PATHS = {
    "Blender/tests/scene_hilo_native_runtime_v1.py",
    "Blender/benchmarks/capacity_audit/scene_hilo_gpu_v1.py",
    "Blender/shaders/scene_hilo_transport_v1.glsl",
    "Blender/benchmarks/capacity_audit/scene_hilo_transport_v1.py",
    "Blender/benchmarks/capacity_audit/oblique_exact_scalar_hilo32_CPU_v1.py",
    "Blender/tests/exp005_scene_readback.py",
    "Blender/tests/exp005_scene_properties.py",
    "Blender/tests/exp005_blender_gpu.py",
}

POISON = 0x5A5A5A5A
ABSENT = 0xFFFFFFFF
ROLE = {"origin":1,"raw_direction":2,"direction_bound":3,"field":4,
        "vertex":5,"mode_origin":8,"mode_direction":9,"wavelength":10}
KIND = {"bs":0,"mirror":1,"det":2,"escape":3}
ORDER = ["k3_baseline", "k4_baseline", "controlled_numeric"]


def need(value, message):
    if not value:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False, ensure_ascii=True)


def read_json(path, expected_sha=None):
    raw = Path(path).read_bytes()
    need(len(raw) <= 16 * 1024 * 1024, "JSON byte cap")
    if expected_sha is not None:
        need(sha(raw) == expected_sha, "SHA mismatch: " + str(path))
    def pairs(items):
        value = {}
        for key, item in items:
            need(key not in value, "duplicate JSON key")
            value[key] = item
        return value
    def bad_constant(value):
        raise ValueError("nonfinite JSON constant: " + value)
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=bad_constant), raw


def binary32(word):
    need(type(word) is int and 0 <= word <= 0xFFFFFFFF, "uint32 word required")
    value = struct.unpack("<f", struct.pack("<I", word))[0]
    need(math.isfinite(value), "nonfinite binary32")
    return F.from_float(value)


def binary64(words):
    """Integer IEEE decoder, exact even for subnormals; zero sign stays in raw words."""
    need(len(words) == 2 and all(type(w) is int and 0 <= w <= 0xFFFFFFFF for w in words),
         "two uint32 words required")
    word = words[0] | words[1] << 32
    exponent, mantissa = (word >> 52) & 0x7FF, word & ((1 << 52) - 1)
    need(exponent != 0x7FF, "nonfinite binary64 output")
    significand = mantissa if exponent == 0 else mantissa + (1 << 52)
    power = -1074 if exponent == 0 else exponent - 1075
    value = F(significand * (-1 if word >> 63 else 1))
    return value * (1 << power) if power >= 0 else value / (1 << -power)


def float32(value):
    result = struct.unpack("<f", struct.pack("<f", float(value)))[0]
    need(math.isfinite(result), "nonfinite reference high limb")
    return result


def observed(value, mode=0):
    need(type(value) in (float, int) and math.isfinite(value), "finite observed scalar required")
    return F.from_float(float32(value) if mode else float(value))


def unpack(raw):
    need(type(raw) is bytes and len(raw) % 4 == 0, "word-aligned bytes required")
    return list(struct.unpack("<%dI" % (len(raw) // 4), raw))


def hex_bytes(value):
    need(type(value) is str and len(value) % 2 == 0 and
         all(c in "0123456789abcdef" for c in value), "canonical lowercase hex required")
    return bytes.fromhex(value)


def padded(count):
    return ((count + 63) // 64) * 64


def audit_packet(case):
    packet, packet_raw = read_json(case["packet_path"], case["packet_sha256"])
    blend = Path(case["blend_path"]).read_bytes()
    need(sha(blend) == case["blend_sha256"], "saved scene SHA mismatch")
    need(packet["schema"] == "neuro3d-scene-hilo-transport-v1", "packet schema")
    manifest, wire = packet["manifest"], hex_bytes(packet["wire_hex"])
    need(manifest["wire_sha256"] == sha(wire) and manifest["wire_bytes"] == len(wire), "packet wire binding")
    snapshot = manifest["snapshot"]
    need(manifest["snapshot_sha256"] == sha(canonical(snapshot).encode()), "snapshot canonical hash")
    need(manifest["provenance"]["blend_sha256"] == case["blend_sha256"] and
         manifest["provenance"]["input_class"] == case["input_class"], "scene provenance binding")
    objects, sources = snapshot["objects"], snapshot["sources"]
    names, bounds = sorted(objects), snapshot.get("neuro3d_direction_bounds", {})
    need(snapshot["evaluated_optics_checked"] is True and snapshot["evaluated_optical_ids"] == names and
         snapshot["undeclared_meshes"] == [], "evaluated complete geometry required")
    if bounds:
        raw_bounds = manifest["provenance"]["direction_bounds_json"]
        need(json.loads(raw_bounds) == bounds, "persisted interval values")
        need(sha(raw_bounds.encode()) == manifest["direction_bounds_provenance"]["stored_json_sha256"],
             "persisted interval hash")
    scalars, source_records, vertex_records, triangle_records = [], [], [], []
    for si, source in enumerate(sources):
        first = len(scalars)
        intervals = bounds.get(source["id"], [[x, x] for x in source["direction"]])
        for role, values, endpoint in (
            ("origin", source["position_BU"], 0), ("raw_direction", source["direction"], 0),
            ("direction_bound", [v[0] for v in intervals], 0),
            ("direction_bound", [v[1] for v in intervals], 1), ("field", source["field_reim"], 0)):
            for axis, value in enumerate(values):
                scalars.append((role, si, 0, axis, endpoint, float(value)))
        source_records.append([si, ABSENT] + list(range(first, first + 14)) + [0] * 16)
    for oi, name in enumerate(names):
        obj = objects[name]
        start_vertex = len(vertex_records)
        for vi, vertex in enumerate(obj["vertices_world_BU"]):
            indices = []
            for axis, value in enumerate(vertex):
                indices.append(len(scalars))
                scalars.append(("vertex", oi, vi, axis, 0, float(value)))
            vertex_records.append([len(vertex_records), oi, vi] + indices + [0, 0])
        for fi, face in enumerate(obj["faces"]):
            need(len(face) == 3 and len(set(face)) == 3 and
                 all(type(i) is int and 0 <= i < len(obj["vertices_world_BU"]) for i in face),
                 "actual triangle connectivity required")
            triangle_records.append([len(triangle_records), oi, fi] +
                                    [start_vertex + i for i in face] + [KIND[obj["kind"]], 0])
        if obj["kind"] in ("det", "escape"):
            for key, role in (("mode_origin_BU", "mode_origin"), ("mode_direction", "mode_direction")):
                for axis, value in enumerate(obj[key]):
                    scalars.append((role, oi, 0, axis, 0, float(value)))
        metadata = manifest["material_binary64_metadata"][oi]
        need(metadata["object_id"] == name and metadata["object_ordinal"] == oi, "material identity")
        for key in ("phase_rad", "power_transmittance"):
            if key in obj:
                words = list(struct.unpack("<II", struct.pack("<d", float(obj[key]))))
                need(metadata["parameters"][key] == {"binary64_words": words, "numeric_ABI": False},
                     "material raw64 metadata changed")
    scalars.append(("wavelength", ABSENT, 0, 0, 0, float(snapshot["lambda_BU"])))
    n, ns, nv, nt, no = len(scalars), len(sources), len(vertex_records), len(triangle_records), len(names)
    so, vo = 32 + 8 * n, 32 + 8 * n + 32 * ns
    to, total = vo + 8 * nv, vo + 8 * nv + 8 * nt
    header = [0x4E33484C,1,32,total,n,32,8,ns,so,32,nv,vo,8,nt,to,8,no,n-1,0]+[0]*13
    words = unpack(wire)
    need(words[:32] == header and len(words) == total, "independent full packet header")
    need(manifest["source_order"] == [s["id"] for s in sources] and manifest["object_order"] == names,
         "independent source/object ordering")
    need(manifest["source_records"] == source_records and manifest["vertex_records"] == vertex_records and
         manifest["triangle_records"] == triangle_records, "independent geometry/source tables")
    need(words[so:vo] == sum(source_records, []) and words[vo:to] == sum(vertex_records, []) and
         words[to:] == sum(triangle_records, []), "native table words")
    nonzero_lows = 0
    for i, (role, owner, element, component, endpoint, value) in enumerate(scalars):
        record = words[32 + i*8:40 + i*8]
        need(record[2:] == [ROLE[role], owner, element, component, endpoint, 0], "scalar metadata")
        expected = observed(value)
        need(binary32(record[0]) + binary32(record[1]) == expected, "exact scalar transport")
        hi_word = struct.unpack("<I", struct.pack("<f", value))[0]
        residual = expected - binary32(hi_word)
        need(F.from_float(float(residual)) == residual, "reference residual is not exactly binary64")
        lo_word = struct.unpack("<I", struct.pack("<f", float(residual)))[0]
        need(record[:2] == [hi_word, lo_word], "independent RN32 limbs")
        audit = manifest["scalars"][i]
        need(audit["observed_binary64_words"] == list(struct.unpack("<II", struct.pack("<d", value))) and
             F(*audit["exact_input"]) == expected and audit["residual_exact"] == [0,1],
             "scalar retained IEEE metadata")
        nonzero_lows += (record[1] & 0x7FFFFFFF) != 0
    need(len(manifest["scalars"]) == n, "complete scalar metadata")
    return {"snapshot":snapshot,"wire":wire,"input_words":total,"scalars":n,"sources":ns,
            "vertices":nv,"triangles":nt,"objects":no,"nonzero_lows":nonzero_lows,
            "rows":ns*nv+ns+2*nt,"packet_sha256":sha(packet_raw),
            "wire_sha256":sha(wire),"blend_sha256":sha(blend)}


def reference_rows(snapshot, mode):
    vertices, triangles = [], []
    for oi, name in enumerate(sorted(snapshot["objects"])):
        obj = snapshot["objects"][name]
        first = len(vertices)
        vertices.extend((oi, point) for point in obj["vertices_world_BU"])
        triangles.extend((oi, [first + x for x in face]) for face in obj["faces"])
    def row(identity, a, b):
        lhs, rhs = [observed(v, mode) for v in a], [observed(v, mode) for v in b]
        return identity, [x-y for x,y in zip(lhs,rhs)], [float(x)-float(y) for x,y in zip(lhs,rhs)]
    for si, source in enumerate(snapshot["sources"]):
        for vi, (oi, vertex) in enumerate(vertices):
            yield row([1,si,vi,oi], vertex, source["position_BU"])
    bounds = snapshot.get("neuro3d_direction_bounds", {})
    for si, source in enumerate(snapshot["sources"]):
        intervals = bounds.get(source["id"], [[v,v] for v in source["direction"]])
        yield row([2,si,ABSENT,ABSENT], [x[1] for x in intervals], [x[0] for x in intervals])
    for edge in (1,2):
        for ti, (oi, indices) in enumerate(triangles):
            yield row([2+edge,ABSENT,ti,oi], vertices[indices[edge]][1], vertices[indices[0]][1])


def audit_readback(data, record, mode_report, mode, nonce):
    echo, computed = hex_bytes(record["input_echo_hex"]), hex_bytes(record["computed_rows_hex"])
    ne, nc = padded(data["input_words"]), padded(32 + 24*data["rows"])
    need(echo == data["wire"] + struct.pack("<I", POISON)*(ne-data["input_words"]), "all input echo and padding")
    words = unpack(computed)
    need(len(words) == nc, "physical computed length")
    expected_header = [0x4E33484F,1,32,32+24*data["rows"],data["input_words"],data["rows"],
                       data["sources"],data["vertices"],data["triangles"],data["scalars"],
                       data["objects"],mode,0,1,nonce,nonce^0xFFFFFFFF]+[0]*16
    need(words[:32] == expected_header, "native header/status/nonce/coverage")
    need(words[32+24*data["rows"]:] == [POISON]*(nc-32-24*data["rows"]), "computed padding")
    need(mode_report["zero_low"] == mode and mode_report["dispatch_nonce"] == nonce and
         mode_report["readback_sha256"] == sha(echo+computed), "per-dispatch identity/hash")
    sync = mode_report["synchronization"]
    need(sync["barrier_mask"] == 0x120 and sync["same_context_verified"] is True and
         sync["fence_status"] in (0x911A,0x911C) and sync["fence_deadline_seconds"] == 5.0 and
         type(sync["fence_polls"]) is int and sync["fence_polls"] > 0, "readback synchronization record")
    payload = mode_report["gpu_resource_payload_bytes"]
    need(payload == {"source_ubo":32768,"echo":ne*4,"computed":nc*4,"total":32768+(ne+nc)*4},
         "native payload accounting")
    refs = list(reference_rows(data["snapshot"], mode))
    need(len(refs) == data["rows"], "independent complete row count")
    exact_values, witnesses = [], []
    nonzero_low = lost = checked = negative_zero_words = 0
    expected_hasher = hashlib.sha256()
    targets = {"one_minus_2pow_minus60": F(1)-F(1,2**60),
               "four_term_direction_width": F(1)+F(1,2**30)-F(1,2**60)-F(1,2**100)}
    critical = {name: [] for name in targets}
    for ri, (identity, expected, naive) in enumerate(refs):
        row = words[32+ri*24:56+ri*24]
        need(row[:4] == identity and row[22:] == [0,0], "row identity/order/reserved")
        expected_hasher.update((canonical([identity,[[x.numerator,x.denominator] for x in expected]])+"\n").encode())
        current = []
        for axis,target in enumerate(expected):
            pair_words = row[4+axis*4:8+axis*4]
            high, low = binary64(pair_words[:2]), binary64(pair_words[2:])
            naive_words = row[16+axis*2:18+axis*2]
            native_naive = binary64(naive_words)
            need(high+low == target, "exact output mismatch row=%d axis=%d"%(ri,axis))
            need(native_naive == F.from_float(naive[axis]), "naive binary64 diagnostic mismatch")
            checked += 1
            nonzero_low += low != 0
            lost_here = native_naive != target
            lost += lost_here
            for lo_word,hi_word in ((pair_words[0],pair_words[1]),(pair_words[2],pair_words[3])):
                negative_zero_words += lo_word == 0 and hi_word == 0x80000000
            current.append(high+low)
            witness = {"row":ri,"identity":identity,"axis":axis,
                       "exact":[target.numerator,target.denominator],"pair64_words":pair_words,
                       "naive_words":naive_words,"low_nonzero":low!=0,"naive_loss":lost_here}
            if (low != 0 or lost_here) and len(witnesses)<12:
                witnesses.append(witness)
            if identity[0] == 1 and axis == 0 and target == targets["one_minus_2pow_minus60"]:
                critical["one_minus_2pow_minus60"].append(witness)
            if identity[0] == 2 and target == targets["four_term_direction_width"]:
                critical["four_term_direction_width"].append(witness)
        exact_values.append(current)
    claimed = mode_report["audit"]
    need(claimed["status"] == "PASS" and claimed["all_rows_checked"] == len(refs) and
         claimed["exact_components_checked"] == checked and claimed["zero_tolerance_exact_comparison"] is True and
         claimed["nonzero_output_low_components"] == nonzero_low and
         claimed["collapsed_binary64_loss_components"] == lost and
         claimed["expected_rows_sha256"] == expected_hasher.hexdigest(), "worker audit summary disagreement")
    return {"mode":mode,"rows":len(refs),"components":checked,"nonzero_output_lows":nonzero_low,
            "naive_loss_components":lost,"negative_zero_output_words":negative_zero_words,
            "expected_rows_sha256":expected_hasher.hexdigest(),
            "native_readback_sha256":sha(echo+computed),"witnesses":witnesses,
            "critical":critical}, exact_values, echo+computed



def audit_guard_resources(guard):
    """Check retained supervisor facts independently, without polling the machine."""
    def integer(value, label, minimum=0, maximum=2**63-1):
        need(type(value) is int and minimum <= value <= maximum, label)
        return value
    def finite(value, label, minimum=0, maximum=float("inf")):
        need(type(value) in (int, float) and math.isfinite(value) and minimum <= value <= maximum, label)
        return value
    def utc(value):
        need(type(value) is str, "guard timestamp string required")
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        need(parsed.tzinfo is not None and parsed.utcoffset().total_seconds() == 0,
             "guard timestamp must be UTC")
        return parsed
    gib = 2**30
    need(guard["schema"] == "scene-hilo-gpu-guard-v1" and guard["synthetic_CPU_control"] is False,
         "real native guard contract required")
    need(type(guard["worker_exit_code"]) is int and guard["worker_exit_code"] == 0,
         "guard worker must exit rc0")
    closed = guard["accounting_after_close"]
    need(type(closed) is dict and type(closed["active_processes"]) is int and
         closed["active_processes"] == 0 and guard["cleanup_errors"] == [],
         "guard has active owned processes or cleanup errors")
    timeout = finite(guard["timeout_seconds"], "bounded guard work timeout", .05, 100)
    cleanup = finite(guard["cleanup_seconds"], "bounded guard cleanup timeout", 1, 10)
    elapsed = finite(guard["elapsed_seconds"], "finite guard elapsed")
    need(elapsed < timeout + cleanup, "guard exceeded work plus cleanup")
    host = integer(guard["host_budget_bytes"], "bounded host reserve", 256*2**20, 2*gib)
    device = integer(guard["device_budget_bytes"], "bounded device reserve", 16*2**20, 2*gib)
    need(guard["ram_floor_bytes"] == 4*gib and guard["vram_cap_bytes"] == 18*gib and
         guard["temperature_cap_c"] == 80 and
         guard["reserve_allowance_applies_during_runtime"] is True,
         "guard resource policy changed")
    started, finished, deadline = (utc(guard[key]) for key in
                                   ("started_utc", "finished_utc", "deadline_utc"))
    need(started <= finished < deadline, "guard UTC timing/deadline")
    samples = guard["samples"]
    need(type(samples) is list and len(samples) >= 3, "admission/running/post-exit samples required")
    need(samples[-1].get("stage") == "after_worker_exit_before_job_close",
         "last guard sample is not after worker exit")
    previous_time = started
    gpu_uuid = samples[0]["gpu_uuid"]
    need(type(gpu_uuid) is str and gpu_uuid.startswith("GPU-"), "recorded GPU UUID required")
    remaining_ram, projected_vram, temperatures = [], [], []
    for sample in samples:
        sampled = utc(sample["sampled_utc"])
        need(previous_time <= sampled <= finished, "guard sample chronology")
        previous_time = sampled
        need(integer(sample["gpu_count"], "single physical GPU", 1, 1) == 1 and
             sample["gpu_uuid"] == gpu_uuid and "RTX 3090" in sample["name"],
             "guard physical GPU identity changed")
        available = integer(sample["ram_available_bytes"], "RAM telemetry")
        used = integer(sample["device_used_bytes"], "used device telemetry")
        total = integer(sample["device_total_bytes"], "total device telemetry", 1)
        temperature = finite(sample["temperature_c"], "temperature telemetry", 0, 80)
        finite(sample["utilization_percent"], "utilization telemetry", 0, 100)
        need(available - host >= 4*gib, "sample RAM floor after host reserve")
        need(used + device <= 18*gib and used + device <= total,
             "sample VRAM cap after device reserve")
        remaining_ram.append(available-host)
        projected_vram.append(used+device)
        temperatures.append(temperature)
    age = (finished - previous_time).total_seconds()
    need(0 <= age <= 5, "final guard telemetry is stale at receipt finalization")
    return {"worker_exit_code":0, "active_owned_processes_after_close":0,
            "samples_checked":len(samples), "elapsed_seconds":elapsed,
            "work_timeout_seconds":timeout, "cleanup_seconds":cleanup,
            "min_ram_after_reserve_bytes":min(remaining_ram),
            "max_vram_after_reserve_bytes":max(projected_vram),
            "max_temperature_c":max(temperatures),
            "final_sample_stage":samples[-1]["stage"], "final_sample_age_seconds":age,
            "gpu_uuid":gpu_uuid}


def main():
    p=argparse.ArgumentParser()
    for name in ("worker-report","worker-sha256","guard-receipt","guard-sha256",
                 "input-manifest","input-sha256","repo","out"):
        p.add_argument("--"+name,required=True)
    args=p.parse_args()
    out=Path(args.out).resolve()
    need(out.parent.is_dir() and not out.exists(), "fresh audit output required")
    inputs=[Path(args.worker_report).resolve(),Path(args.guard_receipt).resolve(),Path(args.input_manifest).resolve()]
    need(out not in inputs, "audit output overlaps input")
    started=time.perf_counter()
    report={"schema":"neuro3d.scene_hilo.independent_native_readback_audit.cpu.v2",
            "status":"FAIL_CPU_AUDIT_OF_RETAINED_NATIVE_READBACK","verification_passed":False,
            "auditor_GPU_executed":False,"auditor_Blender_executed":False,
            "implementation_imports":0,"retained_native_evidence_validated":False,
            "physical_precision_certified":False,"phase_certified":False,"first_hit_certified":False,
            "native_original_transport_joins":0,"cases":[]}
    try:
        worker,worker_raw=read_json(inputs[0],args.worker_sha256)
        guard,guard_raw=read_json(inputs[1],args.guard_sha256)
        job,job_raw=read_json(inputs[2],args.input_sha256)
        report["artifacts"]={"worker":{"path":str(inputs[0]),"sha256":sha(worker_raw)},
                             "guard":{"path":str(inputs[1]),"sha256":sha(guard_raw)},
                             "input_manifest":{"path":str(inputs[2]),"sha256":sha(job_raw)}}
        need(guard["status"]=="PASS" and guard["cleanup_confirmed"] is True and
             guard["native_gpu_execution_verified"] is True and guard["GPU_job_admission"] is True,
             "native guard did not pass")
        need(guard["worker_report_sha256"]==sha(worker_raw) and
             guard["job_id"]==worker["job_id"], "guard/worker evidence binding")
        need(guard["pins_entry"]==guard["pins_exit"], "guard dependency closure changed")
        report["guard_independent_checks"]=audit_guard_resources(guard)
        for name in ("physical_precision_certified","native_precision_certified",
                     "global_machine_safety_certified","foreign_processes_terminated"):
            need(guard[name] is False, "guard scope inflation: "+name)
        need(worker["schema"]=="neuro3d.scene_hilo.native_report.v1" and worker["status"]=="PASS" and
             worker["verification_passed"] is True and worker["native_gpu_executed"] is True and
             worker["native_gpu_execution_attempted"] is True and
             type(worker["completed_readbacks"]) is int and worker["completed_readbacks"] == 6,
             "native worker did not complete all six attempted readbacks")
        need(worker["input_manifest_sha256"]==sha(job_raw) and
             worker["backend"]=="OPENGL" and worker["background"] is False and
             "NVIDIA" in worker["vendor"].upper() and "RTX 3090" in worker["renderer"].upper(),
             "native input/device binding")
        for name in ("physical_uncertainty_certified","full_intersection_integration","phase_certified",
                     "full_Iris_GPU","hardware_RT_or_BVH","speed_advantage_claimed"):
            need(worker["scope"][name] is False, "worker scope inflation: "+name)
        need(job["schema"]=="neuro3d.scene_hilo.native_job.v1" and
             job["limits"]=={"max_sources":5,"max_triangles":64,"max_dispatches":6} and
             [c["case_id"] for c in job["cases"]]==ORDER, "pinned native job profile")
        need([c["case_id"] for c in worker["cases"]]==ORDER, "case coverage/order")
        records=worker["gpu_readback_records"]
        need(worker["gpu_dispatch_count"]==guard["gpu_dispatch_count"]==len(records)==6,
             "six dispatch/readback records required")
        code_pins={}
        declared_code = worker["code_sha256"]
        need(type(declared_code) is dict and len(declared_code) == len(EXPECTED_CODE_PATHS) and
             all(type(relative) is str for relative in declared_code) and
             {relative.replace("\\", "/") for relative in declared_code} == EXPECTED_CODE_PATHS,
             "exact eight worker dependencies required")
        for relative,expected in declared_code.items():
            path=Path(args.repo)/relative
            actual=sha(path.read_bytes())
            need(actual==expected, "worker source changed after native run: "+relative)
            norm=os.path.normcase(str(path.resolve()))
            need(guard["pins_entry"].get(norm)==actual, "worker code is outside guard pins: "+relative)
            code_pins[relative]=actual
        report["code_pins"]=code_pins
        all_raw=hashlib.sha256(); total_components=total_rows=0; seen_nonces=set()
        for ci,(case,case_report) in enumerate(zip(job["cases"],worker["cases"])):
            data=audit_packet(case)
            need(canonical(case_report["snapshot"])==canonical(data["snapshot"]) and
                 case_report["reopened_snapshot_equal"] is True and
                 case_report["wire_sha256"]==data["wire_sha256"] and
                 case_report["native_input_nonzero_low_limbs"]==data["nonzero_lows"],
                 "case snapshot/transport summary")
            need(len(case_report["modes"])==2,"both modes required")
            audits=[]; values=[]
            for mode in (0,1):
                index=ci*2+mode; record=records[index]; mode_report=case_report["modes"][mode]
                need(record["case_id"]==case["case_id"] and type(record["zero_low"]) is int and
                     record["zero_low"]==mode and mode_report["raw_record_index"]==index,
                     "case/mode/raw-record order")
                seed=(worker["job_id"]+"/"+case["case_id"]+"/"+str(mode)).encode()
                nonce=int.from_bytes(hashlib.sha256(seed).digest()[:4],"little")&0x7FFFFFFF
                need(nonce and nonce not in seen_nonces,"fresh unique dispatch nonce")
                seen_nonces.add(nonce)
                audit,exact,raw=audit_readback(data,record,mode_report,mode,nonce)
                audits.append(audit); values.append(exact); all_raw.update(raw)
                total_rows+=audit["rows"]; total_components+=audit["components"]
            changed=sum(a!=b for r0,r1 in zip(values[0],values[1]) for a,b in zip(r0,r1))
            need(changed==case_report["low_zero_ablation_changed_components"],"ablation summary")
            if case["input_class"]=="real_reopened_baseline":
                need(data["nonzero_lows"]==0 and changed==0,"baseline low-zero sham")
            else:
                need(data["nonzero_lows"]>0 and changed>0,"controlled informative low limbs")
                need(all(audits[0]["critical"].values()),"both critical witnesses required")
                need(all(w["low_nonzero"] and w["naive_loss"] for group in audits[0]["critical"].values() for w in group),
                     "critical exact pair/naive-loss witness")
            report["cases"].append({"case_id":case["case_id"],"packet_sha256":data["packet_sha256"],
                                    "wire_sha256":data["wire_sha256"],"input_scalar_count":data["scalars"],
                                    "input_nonzero_lows":data["nonzero_lows"],"ablation_changed_components":changed,
                                    "modes":audits})
        need(total_rows==2342 and total_components==7026,"full preregistered output coverage")
        need(all_raw.hexdigest()==worker["gpu_readback_sha256"]==guard["gpu_readback_sha256"],
             "complete worker/guard readback hash")
        report.update(status="PASS_CPU_AUDIT_OF_RETAINED_NATIVE_READBACK",verification_passed=True,
                      retained_native_evidence_validated=True,total_rows=total_rows,total_components=total_components,
                      readback_sha256=all_raw.hexdigest(),job_id=worker["job_id"],guard_cleanup_verified=True)
        for path,expected in zip(inputs,(args.worker_sha256,args.guard_sha256,args.input_sha256)):
            need(sha(path.read_bytes())==expected,"audit input mutated during read")
    except BaseException as error:
        report.update(status="FAIL_CPU_AUDIT_OF_RETAINED_NATIVE_READBACK",verification_passed=False,
                      retained_native_evidence_validated=False,error=type(error).__name__+": "+str(error),
                      traceback=traceback.format_exc())
    report["created_utc"]=datetime.now(timezone.utc).isoformat()
    report["audit_wall_seconds"]=time.perf_counter()-started
    report["previous_auditor_sha256"]=PREVIOUS_AUDITOR_SHA256
    if AUDITOR_BYTES is not None:
        report["auditor_file_sha256"]=sha(AUDITOR_BYTES)
    if isinstance(AUDITOR_SOURCE, str):
        report["auditor_source_sha256"]=sha(AUDITOR_SOURCE.encode())
        report["auditor_source"]=AUDITOR_SOURCE
    raw=(json.dumps(report,indent=2,allow_nan=False)+"\n").encode()
    temporary=out.with_name(out.name+".tmp")
    with temporary.open("xb") as stream:
        stream.write(raw);stream.flush();os.fsync(stream.fileno())
    os.rename(temporary,out)
    print(json.dumps({"path":str(out),"sha256":sha(raw),"bytes":len(raw),
                      "status":report["status"],"components":report.get("total_components"),
                      "error":report.get("error")},sort_keys=True))
    return 0 if report["verification_passed"] else 1


if __name__=="__main__":
    raise SystemExit(main())
