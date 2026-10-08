"""Guarded native exact first-hit v1 runtime.

Consumes only frozen scene-hi/lo packets and query metadata. Geometry arithmetic
is performed by robust_first_hit_exact_v1.glsl using exact signed512 integer
operations. This worker never uses the CPU selector as an oracle.
"""
from __future__ import annotations

import argparse
import ctypes
import gc
import hashlib
import json
import math
import os
from pathlib import Path
import struct
import sys
import time
import traceback
import uuid

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from Blender.benchmarks.capacity_audit import scene_hilo_gpu_v1 as gpu_base
from Blender.benchmarks.capacity_audit import scene_hilo_transport_v1 as transport
from exp005_blender_gpu import schedule_exit

SCHEMA = "neuro3d.robust_first_hit.native_job.v1"
REPORT_SCHEMA = "neuro3d.robust_first_hit.native_report.v1"
MAX_JSON = 16 * 1024 * 1024
MAX_DISPATCHES = 32
OUTPUT_WORDS = 64
POISON = gpu_base.POISON
SHADER = ROOT / "Blender/shaders/robust_first_hit_exact_v1.glsl"
SIGNED512 = ROOT / "Blender/shaders/robust_first_hit_register_arithmetic_v1.glsl"
COMPILE_OPTIONS = "#pragma optimize(off)\n#pragma optionNV(unroll none)\n#pragma optionNV(inline 0)\n"
DEPARTURE = {None: 0, "mirror": 1, "t": 2, "r": 3}

SCOPE = {
    "numeric_domain": "exact signed512 Moller-Trumbore over admitted hi/lo scene packet",
    "fixed_origin_bias": False,
    "epsilon_hit_band": False,
    "previous_primitive_global_exclusion": False,
    "exact_zero_departure_exclusion": True,
    "same_surface_triangulation_equivalence": True,
    "phase_certified": False,
    "full_path_visibility_certified": False,
    "physical_uncertainty_certified": False,
    "hardware_RT_or_BVH": False,
    "speed_advantage_claimed": False,
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    path = Path(path)
    require(path.is_file() and path.stat().st_size <= MAX_JSON, "bounded JSON required")
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "duplicate JSON key: " + str(key))
            result[key] = value
        return result
    def bad(value):
        raise ValueError("nonfinite JSON constant: " + value)
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs,
                      parse_constant=bad)


def write_new(path, value, job_id):
    path = Path(path)
    require(path.parent.is_dir() and not path.exists(), "fresh report required")
    raw = (json.dumps(value, indent=2, allow_nan=False) + "\n").encode()
    require(len(raw) <= MAX_JSON, "report cap")
    temp = path.with_name(path.name + "." + job_id + ".tmp")
    with temp.open("xb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    os.rename(temp, path)


def private_exit_settings(bpy):
    prefs = bpy.context.preferences
    prefs.use_preferences_save = False
    prefs.view.use_save_prompt = False
    prefs.filepaths.use_auto_save_temporary_files = False
    return {"save_user_preferences": False, "save_prompt": False,
            "temporary_autosave": False}


def i512(words):
    require(type(words) is list and len(words) == 16 and
            all(type(x) is int and 0 <= x <= 0xFFFFFFFF for x in words),
            "16 uint32 signed512 limbs")
    value = sum(word << (32 * i) for i, word in enumerate(words))
    if value >> 511:
        value -= 1 << 512
    return value


def tie_mask(ids):
    lo = hi = 0
    for primitive in ids:
        require(type(primitive) is int and 0 <= primitive < 64, "tie primitive ID")
        if primitive < 32:
            lo |= 1 << primitive
        else:
            hi |= 1 << (primitive - 32)
    return lo, hi


def parse_result(words, expected_nonce):
    require(len(words) == OUTPUT_WORDS, "complete fixed result")
    require(words[0] == 0x35484652 and words[1] == 1 and
            words[13] == expected_nonce and words[14] == (expected_nonce ^ 0xFFFFFFFF) and
            words[15] == 1, "result header/nonce/completion")
    return {
        "status_code": words[2],
        "source_index": words[3],
        "selected_primitive": None if words[4] == 0xFFFFFFFF else words[4],
        "selected_object": None if words[5] == 0xFFFFFFFF else words[5],
        "tie_count": words[6],
        "boundary": bool(words[7]),
        "excluded_previous_contacts": words[8],
        "contact_count": words[9],
        "coplanar_count": words[10],
        "degenerate_count": words[11],
        "triangle_count": words[12],
        "t_num": i512(words[16:32]),
        "t_den": i512(words[32:48]),
        "tie_mask_lo": words[48],
        "tie_mask_hi": words[49],
        "equivalent_surface_tie": bool(words[50]),
        "ambiguous_tie": bool(words[51]),
    }


def expected_query(row):
    require(type(row) is dict and set(row) == {
        "source_index", "previous_primitive", "departure_event", "expected"}, "closed query schema")
    require(type(row["source_index"]) is int and row["source_index"] >= 0, "source index")
    previous = row["previous_primitive"]
    require(previous is None or (type(previous) is int and previous >= 0), "previous primitive")
    require(row["departure_event"] in DEPARTURE, "departure event")
    require((previous is None) == (row["departure_event"] is None), "departure/previous pairing")
    e = row["expected"]
    require(type(e) is dict and set(e) == {
        "status", "status_code", "selected_primitive", "selected_object",
        "tie_primitive_ids", "equivalent_surface_tie", "excluded_previous_contacts", "t"},
        "closed expected result")
    require(type(e["status_code"]) is int and 1 <= e["status_code"] <= 8, "status code")
    require(type(e["tie_primitive_ids"]) is list and
            all(type(x) is int and 0 <= x < 64 for x in e["tie_primitive_ids"]), "tie ids")
    return row


def pinned_packet_path(case):
    """Resolve frozen portable paths relative to this checkout, never the CWD."""
    value = case["packet_path"]
    require(type(value) is str and value and "\0" not in value, "pinned packet path")
    path = Path(value)
    if not path.is_absolute():
        path = ROOT / path
    path = path.resolve()
    require(path.is_file() and path.suffix == ".json" and
            sha(path) == case["packet_sha256"], "pinned packet")
    return path


def validate_job(job):
    require(type(job) is dict and set(job) == {
        "schema", "expected_backend", "expected_renderer_contains", "limits", "cases"},
        "closed first-hit job schema")
    require(job["schema"] == SCHEMA and job["expected_backend"] == "OPENGL" and
            job["expected_renderer_contains"] == "RTX 3090", "fixed GPU profile")
    require(job["limits"] == {"max_triangles": 64, "max_dispatches": 20}, "fixed limits")
    require(type(job["cases"]) is list and 1 <= len(job["cases"]) <= 20, "bounded cases")
    ids = []
    dispatches = 0
    for case in job["cases"]:
        require(type(case) is dict and set(case) == {
            "case_id", "input_class", "packet_path", "packet_sha256", "queries"}, "closed case schema")
        require(type(case["case_id"]) is str and case["case_id"], "case ID")
        ids.append(case["case_id"])
        pinned_packet_path(case)
        require(type(case["queries"]) is list and case["queries"], "queries required")
        for query in case["queries"]:
            expected_query(query)
            dispatches += 1
    require(len(set(ids)) == len(ids), "unique case IDs")
    require(dispatches == job["limits"]["max_dispatches"], "exact preregistered dispatch coverage")
    return dispatches


def raw_compile_diagnostic():
    """Retain bounded full driver logs; Blender's log buffer hides later errors.

    Diagnostic compile/link only: no dispatch, buffers or result readback.
    The original Blender shader failure remains a failure regardless of this log.
    """
    sync = gpu_base.OpenGLReadbackSync()
    resolve = sync._resolve
    uint, integer = ctypes.c_uint32, ctypes.c_int32
    create_shader = resolve("glCreateShader", uint, uint)
    shader_source = resolve("glShaderSource", None, uint, integer,
                            ctypes.POINTER(ctypes.c_char_p), ctypes.POINTER(integer))
    compile_stage = resolve("glCompileShader", None, uint)
    get_shader = resolve("glGetShaderiv", None, uint, uint, ctypes.POINTER(integer))
    shader_log = resolve("glGetShaderInfoLog", None, uint, integer,
                         ctypes.POINTER(integer), ctypes.POINTER(ctypes.c_char))
    create_program = resolve("glCreateProgram", uint)
    attach = resolve("glAttachShader", None, uint, uint)
    link = resolve("glLinkProgram", None, uint)
    get_program = resolve("glGetProgramiv", None, uint, uint, ctypes.POINTER(integer))
    program_log = resolve("glGetProgramInfoLog", None, uint, integer,
                          ctypes.POINTER(integer), ctypes.POINTER(ctypes.c_char))
    delete_shader = resolve("glDeleteShader", None, uint)
    delete_program = resolve("glDeleteProgram", None, uint)
    prefix = """#version 450 core
layout(local_size_x=1,local_size_y=1,local_size_z=1) in;
struct HiloInputPacket { uvec4 words[2048]; };
layout(std140,binding=0) uniform PacketBlock { HiloInputPacket input_packet; };
layout(r32ui,binding=0) uniform writeonly uimage2D echo_words;
layout(r32ui,binding=1) uniform writeonly uimage2D result_words;
uniform int input_word_count,source_index,previous_primitive,departure_event,dispatch_nonce;
"""
    source = (prefix + COMPILE_OPTIONS + SIGNED512.read_text(encoding="utf-8") + "\n" +
              SHADER.read_text(encoding="utf-8")).encode()
    stage = program = 0
    report = {"dispatches": 0, "source_sha256": hashlib.sha256(source).hexdigest()}
    def log(handle, getter, reader):
        size = integer()
        getter(handle, 0x8B84, ctypes.byref(size))  # GL_INFO_LOG_LENGTH
        require(0 <= size.value <= 1024 * 1024, "bounded compile log")
        buffer = ctypes.create_string_buffer(max(1, size.value))
        written = integer()
        reader(handle, len(buffer), ctypes.byref(written), buffer)
        return buffer.raw[:written.value].decode("utf-8", errors="replace")
    try:
        stage = create_shader(0x91B9)  # GL_COMPUTE_SHADER
        require(stage != 0, "diagnostic shader allocation")
        pointers = (ctypes.c_char_p * 1)(source)
        length = integer(len(source))
        shader_source(stage, 1, pointers, ctypes.byref(length))
        compile_stage(stage)
        status = integer()
        get_shader(stage, 0x8B81, ctypes.byref(status))  # GL_COMPILE_STATUS
        report.update(stage_compiled=bool(status.value), stage_log=log(stage, get_shader, shader_log))
        if status.value:
            program = create_program()
            require(program != 0, "diagnostic program allocation")
            attach(program, stage)
            link(program)
            get_program(program, 0x8B82, ctypes.byref(status))  # GL_LINK_STATUS
            report.update(program_linked=bool(status.value),
                          program_log=log(program, get_program, program_log))
        return report
    finally:
        if program:
            delete_program(program)
        if stage:
            delete_shader(stage)


def compile_shader(gpu, report):
    sync = gpu_base.OpenGLReadbackSync()
    sync.uniform_buffer_limit()
    info = gpu.types.GPUShaderCreateInfo()
    info.typedef_source("struct HiloInputPacket { uvec4 words[2048]; };")
    info.uniform_buf(0, "HiloInputPacket", "input_packet")
    info.image(0, "R32UI", "UINT_2D", "echo_words", qualifiers={"WRITE"})
    info.image(1, "R32UI", "UINT_2D", "result_words", qualifiers={"WRITE"})
    for name in ("input_word_count", "source_index", "previous_primitive",
                 "departure_event", "dispatch_nonce"):
        info.push_constant("INT", name)
    info.local_group_size(1, 1, 1)
    report["compile_options"] = COMPILE_OPTIONS.splitlines()
    info.compute_source(COMPILE_OPTIONS + SIGNED512.read_text(encoding="utf-8") + "\n" +
                        SHADER.read_text(encoding="utf-8"))
    try:
        return gpu.shader.create_from_info(info)
    except Exception:
        try:
            report["compile_diagnostic"] = raw_compile_diagnostic()
        except Exception as diagnostic_error:
            report["compile_diagnostic"] = {"error": type(diagnostic_error).__name__ +
                                             ": " + str(diagnostic_error), "dispatches": 0}
        raise


def dispatch(gpu, shader, wire, query, nonce):
    require(len(wire) <= gpu_base.INPUT_BUFFER_BYTES and len(wire) % 4 == 0, "bounded input")
    layout = transport.admit_for_upload(
        {"schema": transport.SCHEMA,
         "manifest": query["_packet_manifest"],
         "wire_hex": wire.hex()},
        trusted_manifest=query["_packet_manifest"])
    del layout
    sync = gpu_base.OpenGLReadbackSync()
    sync.require_no_error("before exact first-hit allocation")
    input_words = len(wire) // 4
    padded = gpu_base.padded_word_count(input_words)
    source = echo = result = None
    allocation_started = time.perf_counter()
    try:
        source = gpu.types.GPUUniformBuf(wire + bytes(gpu_base.INPUT_BUFFER_BYTES - len(wire)))
        echo = gpu.types.GPUTexture((64, padded // 64), format="R32UI")
        result = gpu.types.GPUTexture((64, 1), format="R32UI")
        echo.clear(format="UINT", value=(POISON,))
        result.clear(format="UINT", value=(POISON,))
        shader.uniform_block("input_packet", source)
        shader.image("echo_words", echo)
        shader.image("result_words", result)
        previous = -1 if query["previous_primitive"] is None else query["previous_primitive"]
        constants = {
            "input_word_count": input_words,
            "source_index": query["source_index"],
            "previous_primitive": previous,
            "departure_event": DEPARTURE[query["departure_event"]],
            "dispatch_nonce": nonce,
        }
        for name, value in constants.items():
            shader.uniform_int(name, value)
        allocation_ms = (time.perf_counter() - allocation_started) * 1000
        sync.require_no_error("before exact first-hit dispatch")
        started = time.perf_counter()
        gpu.compute.dispatch(shader, 1, 1, 1)
        synchronization = sync.wait_for_readback()
        sync.assert_context()
        echo_words = gpu_base._read_texture(echo, input_words)
        result_words = gpu_base._read_texture(result, OUTPUT_WORDS)
        sync.require_no_error("after exact first-hit readback")
        input_expected = gpu_base.unpack_words(wire) + [POISON] * (len(echo_words) - input_words)
        require(echo_words == input_expected, "bit-exact packet echo")
        parsed = parse_result(result_words, nonce)
        elapsed_ms = (time.perf_counter() - started) * 1000
        return {
            "input_echo_hex": gpu_base.pack_words(echo_words).hex(),
            "result_hex": gpu_base.pack_words(result_words).hex(),
            "parsed": parsed,
            "synchronization": synchronization,
            "allocation_upload_bind_ms": allocation_ms,
            "dispatch_sync_readback_host_validation_ms": elapsed_ms,
            "resource_payload_bytes": gpu_base.INPUT_BUFFER_BYTES + len(echo_words) * 4 + OUTPUT_WORDS * 4,
        }
    finally:
        source = echo = result = None


def compare_expected(parsed, expected):
    lo, hi = tie_mask(expected["tie_primitive_ids"])
    t = expected["t"]
    pairs = {
        "status_code": expected["status_code"],
        "selected_primitive": expected["selected_primitive"],
        "selected_object": expected["selected_object"],
        "tie_count": len(expected["tie_primitive_ids"]),
        "tie_mask_lo": lo,
        "tie_mask_hi": hi,
        "equivalent_surface_tie": bool(expected["equivalent_surface_tie"]),
        "excluded_previous_contacts": expected["excluded_previous_contacts"],
        "t_num": 0 if t is None else t[0],
        "t_den": 0 if t is None else t[1],
    }
    mismatches = {key: {"actual": parsed[key], "expected": value}
                  for key, value in pairs.items() if parsed[key] != value}
    require(not mismatches, "GPU result differs from frozen CPU expectation: " + json.dumps(mismatches))
    return pairs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-manifest", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--job-id", required=True)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    require(str(uuid.UUID(args.job_id)) == args.job_id, "canonical job UUID")
    manifest_path, report_path = args.input_manifest.resolve(), args.report.resolve()
    report = {
        "schema": REPORT_SCHEMA, "status": "FAIL", "verification_passed": False,
        "job_id": args.job_id, "input_manifest_sha256": sha(manifest_path),
        "native_gpu_executed": False, "native_gpu_execution_attempted": False,
        "gpu_dispatch_count": 0, "completed_readbacks": 0,
        "gpu_readback_records": [], "gpu_readback_sha256": None,
        "scope": SCOPE, "cases": [],
    }
    hasher = hashlib.sha256()
    shader = None
    failure = None
    started = time.perf_counter()
    try:
        import bpy
        import gpu
        require(not bpy.app.background, "windowed private OpenGL context required")
        report.update(gpu_base.device_profile(gpu))
        report["background"] = bpy.app.background
        report["blender_version"] = bpy.app.version_string
        report["blender_build_hash"] = bpy.app.build_hash.decode("ascii")
        report["private_exit_settings"] = private_exit_settings(bpy)
        job = read_json(manifest_path)
        dispatch_count = validate_job(job)
        dependencies = [
            Path(__file__).resolve(), Path(gpu_base.__file__), gpu_base.SHADER,
            Path(transport.__file__), Path(transport.codec.__file__), SHADER, SIGNED512,
            Path(__file__).with_name("exp005_blender_gpu.py"),
        ]
        report["code_sha256"] = {str(path.relative_to(ROOT)): sha(path) for path in dependencies}
        shader = compile_shader(gpu, report)
        seen_nonces = set()
        for case in job["cases"]:
            packet_path = pinned_packet_path(case)
            packet = read_json(packet_path)
            require(packet.get("schema") == transport.SCHEMA and
                    sha(packet_path) == case["packet_sha256"], "packet identity")
            trusted = packet["manifest"]
            wire = transport.admit_for_upload(packet, trusted_manifest=trusted)
            require(trusted["abi"]["triangle_count"] <= 64, "triangle limit")
            case_report = {
                "case_id": case["case_id"], "input_class": case["input_class"],
                "packet_sha256": case["packet_sha256"], "wire_sha256": hashlib.sha256(wire).hexdigest(),
                "triangle_count": trusted["abi"]["triangle_count"], "queries": [],
            }
            report["cases"].append(case_report)
            for q_index, frozen in enumerate(case["queries"]):
                query = dict(frozen)
                query["_packet_manifest"] = trusted
                seed = (args.job_id + "/" + case["case_id"] + "/" + str(q_index)).encode()
                nonce = int.from_bytes(hashlib.sha256(seed).digest()[:4], "little") & 0x7FFFFFFF
                require(nonce and nonce not in seen_nonces, "unique nonce")
                seen_nonces.add(nonce)
                report["gpu_dispatch_count"] += 1
                report["native_gpu_execution_attempted"] = True
                result = dispatch(gpu, shader, wire, query, nonce)
                report["native_gpu_executed"] = True
                compare_expected(result["parsed"], frozen["expected"])
                raw_record = {
                    "case_id": case["case_id"], "query_index": q_index,
                    "source_index": frozen["source_index"],
                    "previous_primitive": frozen["previous_primitive"],
                    "departure_event": frozen["departure_event"],
                    "input_echo_hex": result["input_echo_hex"],
                    "result_hex": result["result_hex"],
                }
                report["gpu_readback_records"].append(raw_record)
                report["completed_readbacks"] = len(report["gpu_readback_records"])
                hasher.update(bytes.fromhex(raw_record["input_echo_hex"]))
                hasher.update(bytes.fromhex(raw_record["result_hex"]))
                report["gpu_readback_sha256"] = hasher.hexdigest()
                case_report["queries"].append({
                    "query_index": q_index, "frozen_expected": frozen["expected"],
                    "parsed": result["parsed"],
                    "synchronization": result["synchronization"],
                    "allocation_upload_bind_ms": result["allocation_upload_bind_ms"],
                    "dispatch_sync_readback_host_validation_ms":
                        result["dispatch_sync_readback_host_validation_ms"],
                    "resource_payload_bytes": result["resource_payload_bytes"],
                    "raw_record_index": len(report["gpu_readback_records"]) - 1,
                })
        require(report["gpu_dispatch_count"] == report["completed_readbacks"] == dispatch_count == 20,
                "exact 20 dispatch/readback coverage")
        validate_job(job)
        require(sha(manifest_path) == report["input_manifest_sha256"] and
                all(sha(ROOT / relative) == digest for relative, digest in report["code_sha256"].items()),
                "inputs/code changed during run")
        report["status"] = "PASS"
        report["verification_passed"] = True
    except BaseException as exc:
        failure = exc
        report["error"] = type(exc).__name__ + ": " + str(exc)
        report["traceback"] = traceback.format_exc()
    finally:
        shader = None
        gc.collect()
        report["total_seconds"] = time.perf_counter() - started
        write_new(report_path, report, args.job_id)
    if failure is not None:
        raise failure
    print("ROBUST_FIRST_HIT_NATIVE_PASS " + report["gpu_readback_sha256"], flush=True)
    schedule_exit(bpy)


if __name__ == "__main__":
    main()
