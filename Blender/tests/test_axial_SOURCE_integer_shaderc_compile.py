"""CPU-only shaderc compilation; never creates a Vulkan/OpenGL device or dispatches."""
from pathlib import Path
import base64
import ctypes as C
import hashlib
import json
import os
import struct
import time
import zlib

ROOT = Path(__file__).resolve().parents[2]
DLL = Path("D:/TOOLS/Blender/blender-4.5.14-windows-x64/blender.shared/shaderc_shared.dll")
DLL_SHA = "d62717becac57380539f099f844e38171a84dad544d86550fc1889224318ab6b"
PINS = {
    "Blender/benchmarks/capacity_audit/axial_native_signed512_v1.glsl":
    "e1f2ff0ca905ee29e8afa0440e9abdaa4a4127be23fe20d29e29c25af68f236f",
    "Blender/benchmarks/capacity_audit/axial_SOURCE_zero_aware_integer_v1.glsl":
    "088c2b8716664494a6d4a8a6358279d017618f25ae03171608b95b1b8fb9242a",
    "coordinacion/respuestas/AXIAL-SOURCE-ZERO-AWARE-INTEGER-GLSL-001-CODEX.json":
    "741e5c5830ead5eeaacf3572fbe6ce03aabb89f7fd2b760eee8ecd7da249245f",
}
WRAPPER = "Blender/benchmarks/capacity_audit/axial_SOURCE_integer_compile_probe_v1.comp"
MODEL = "axial-SOURCE-integer-shaderc-compile-only-v1"

def sha(data):
    return hashlib.sha256(data).hexdigest()

def packed(data):
    return {"bytes": len(data), "sha256": sha(data),
            "zlib_base64": base64.b64encode(zlib.compress(data, 9)).decode("ascii")}

def load_sources(model=MODEL):
    if model != MODEL:
        raise ValueError("explicit compile-only model required")
    sources = {}
    for path, expected in PINS.items():
        data = (ROOT / path).read_bytes()
        if sha(data) != expected:
            raise ValueError("frozen source/receipt hash mismatch: " + path)
        sources[path] = data
    data = DLL.read_bytes()
    if sha(data) != DLL_SHA:
        raise ValueError("existing shaderc DLL hash mismatch")
    wrapper = (ROOT / WRAPPER).read_bytes()
    return sources, wrapper, packed(data)["sha256"]

class Compiler:
    def __enter__(self):
        # Existing CPU compiler only; no Blender/Python module, graphics API or installation.
        self.directory = os.add_dll_directory(str(DLL.parent))
        try:
            self.lib = C.CDLL(str(DLL))
            def bind(name, ret, args):
                f = getattr(self.lib, name)
                f.restype, f.argtypes = ret, args
                return f
            pointer, size = C.c_void_p, C.c_size_t
            self.initialize = bind("shaderc_compiler_initialize", pointer, [])
            self.release = bind("shaderc_compiler_release", None, [pointer])
            self.options_init = bind("shaderc_compile_options_initialize", pointer, [])
            self.options_release = bind("shaderc_compile_options_release", None, [pointer])
            self.target = bind("shaderc_compile_options_set_target_env", None,
                               [pointer, C.c_int, C.c_uint])
            self.optimize = bind("shaderc_compile_options_set_optimization_level", None,
                                 [pointer, C.c_int])
            self.compile = bind("shaderc_compile_into_spv", pointer,
                [pointer, C.c_char_p, size, C.c_int, C.c_char_p, C.c_char_p, pointer])
            self.result_release = bind("shaderc_result_release", None, [pointer])
            self.status = bind("shaderc_result_get_compilation_status", C.c_int, [pointer])
            self.errors = bind("shaderc_result_get_num_errors", size, [pointer])
            self.warnings = bind("shaderc_result_get_num_warnings", size, [pointer])
            self.message = bind("shaderc_result_get_error_message", C.c_char_p, [pointer])
            self.length = bind("shaderc_result_get_length", size, [pointer])
            self.bytes = bind("shaderc_result_get_bytes", pointer, [pointer])
            self.handle = self.initialize()
            if not self.handle:
                raise RuntimeError("shaderc initialization failed")
        except BaseException:
            self.directory.close()
            raise
        return self

    def __exit__(self, *args):
        self.release(self.handle)
        self.directory.close()

    def run(self, source, target, version, name):
        options = self.options_init()
        if not options:
            raise RuntimeError("shaderc options allocation failed")
        result = None
        start = time.perf_counter()
        try:
            self.target(options, target, version)
            self.optimize(options, 0)
            result = self.compile(self.handle, source, len(source), 2,
                                  name.encode("ascii"), b"main", options)
            if not result:
                raise RuntimeError("shaderc null compilation result")
            data = C.string_at(self.bytes(result), self.length(result)) if self.length(result) else b""
            row = {"name": name, "target_env": target, "target_version": version,
                   "optimization": 0, "shader_kind": 2, "entry_point": "main",
                   "source": packed(source), "status": self.status(result),
                   "errors": self.errors(result), "warnings": self.warnings(result),
                   "diagnostics": (self.message(result) or b"").decode("utf-8", "replace"),
                   "spirv": packed(data), "compile_call_seconds": time.perf_counter() - start}
            return row, data
        finally:
            if result:
                self.result_release(result)
            self.options_release(options)

def inspect_spirv(data):
    # Structural inspection ONLY, not SPIRV-Tools validation or execution.
    if len(data) < 20 or len(data) % 4:
        raise ValueError("SPIR-V length")
    words = struct.unpack("<" + "I" * (len(data) // 4), data)
    if words[0] != 0x07230203 or words[4] != 0:
        raise ValueError("SPIR-V header")
    i, opcodes, entries, modes, caps = 5, [], [], [], []
    while i < len(words):
        count, opcode = words[i] >> 16, words[i] & 65535
        if count == 0 or i + count > len(words):
            raise ValueError("SPIR-V instruction length")
        operands = words[i+1:i+count]
        opcodes.append(opcode)
        if opcode == 15:
            entries.append(list(operands))
        if opcode == 16:
            modes.append(list(operands))
        if opcode == 17:
            caps.append(operands[0])
        i += count
    if 22 in opcodes:
        raise ValueError("OpTypeFloat present")
    if not any(e[0] == 5 and struct.pack("<I", e[2]) == b"main" for e in entries):
        raise ValueError("GLCompute main entry missing")
    if not any(m[1:] == [17, 1, 1, 1] for m in modes):
        raise ValueError("LocalSize(1,1,1) missing")
    return {"instructions": len(opcodes), "OpTypeFloat_count": 0,
            "GLCompute_main": True, "LocalSize": [1, 1, 1],
            "capabilities": caps, "spirv_tools_validated": False,
            "gpu_executed": False}

def main():
    sources, wrapper, dll_sha = load_sources()
    signed, integer = [sources[p] for p in list(PINS)[:2]]
    prefix = b"#version 450\n"
    full = prefix + signed + b"\n" + integer + b"\n" + wrapper
    controls = [
        ("vulkan_1_0_valid", full, 0, 1 << 22, True),
        ("opengl_4_5_valid", full, 1, 450, True),
        ("reserved_half_negative", full.replace(b"guardBit", b"half"), 0, 1 << 22, False),
        ("missing_signed512_negative", prefix + integer + wrapper, 0, 1 << 22, False),
        ("reversed_headers_negative", prefix + integer + signed + wrapper, 0, 1 << 22, False),
    ]
    records, failures = [], []
    with Compiler() as compiler:
        for name, source, env, version, expected in controls:
            row, binary = compiler.run(source, env, version, name)
            row["expected_compile_success"] = expected
            row["check_passed"] = (row["status"] == 0 and row["errors"] == 0) == expected
            if row["status"] == 0:
                try:
                    row["structural_inspection"] = inspect_spirv(binary)
                except ValueError as exc:
                    row["check_passed"] = False
                    row["inspection_failure"] = str(exc)
            elif expected:
                failures.append(name)
            if not row["check_passed"]:
                failures.append(name + ": expectation")
            records.append(row)
    model_rejects = 0
    for wrong in ("", None, "axial-SOURCE-zero-aware-integer-words-GLSL-v1"):
        try:
            load_sources(wrong)
        except ValueError:
            model_rejects += 1
    structural_rejects = 0
    good = zlib.decompress(base64.b64decode(records[0]["spirv"]["zlib_base64"]))
    for wrong in (b"", good[:-1], b"\0\0\0\0" + good[4:], good[:20] + b"\0\0\0\0"):
        try:
            inspect_spirv(wrong)
        except ValueError:
            structural_rejects += 1
    if model_rejects != 3 or structural_rejects != 4:
        failures.append("negative validators")
    result = {
        "ID": "AXIAL-SOURCE-INTEGER-SHADERC-COMPILE-001", "model": MODEL,
        "pins": PINS, "compiler": {"path": str(DLL), "sha256": dll_sha, "bytes": DLL.stat().st_size,
                                 "upstream_version": "UNKNOWN: local binary hash is identity"},
        "wrapper": {"path": WRAPPER, **packed(wrapper)}, "compilations": records,
        "model_rejects_before_load": model_rejects, "structural_rejects": structural_rejects,
        "status": "PASS" if not failures else "FAIL", "failures": failures,
        "scope": {"compile_only": True, "new_wrapper_not_runtime_runner": True,
                  "GLSL450_only_not_all_versions": True, "gpu_executed": False,
                  "blender_started": False, "scene_admission": False, "dispatches": 0,
                  "spirv_tools_validated": False, "numeric_semantics_proven": False,
                  "phase_quota": None, "groups_admitted": 0, "general_38_gates_pass": False,
                  "full_costs": "UNMEASURED_NOT_ZERO", "JEV": "LOCAL_FALLBACK_NO_RETRY"}
    }
    print(json.dumps(result, sort_keys=True))
    return 0 if not failures else 1

if __name__ == "__main__":
    raise SystemExit(main())
