"""Opt-in HOST staging only. No decoder/compiler imports, devices or GPU dispatch."""
import base64
import hashlib
import json
import struct
import zlib
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MODEL = "axial-SOURCE-compiled-buffer-prep-HOST-v1"
IG = "coordinacion/respuestas/AXIAL-SOURCE-ZERO-AWARE-INTEGER-GLSL-001-CODEX.json"
IG_SHA = "741e5c5830ead5eeaacf3572fbe6ce03aabb89f7fd2b760eee8ecd7da249245f"
SC = "coordinacion/respuestas/AXIAL-SOURCE-INTEGER-SHADERC-COMPILE-001-CODEX.json"
SC_SHA = "0806f8cf64a0fd2c233c818517642ccd9a7db3f3fb1c531bdb8ad13acc92ee10"
MODULE_SHA = "ab1b705012b020ed9cb0c6878f0de5af436c8e3c0350b61715c99636df0624f7"
WRAPPER_SHA = "b4ed47d1a24c6d4c75778d72debe76e2a8b83ad8b1bdedad1cfa408bcbf169b7"
SOURCE_SHA = "088c2b8716664494a6d4a8a6358279d017618f25ae03171608b95b1b8fb9242a"
SIGNED_SHA = "e1f2ff0ca905ee29e8afa0440e9abdaa4a4127be23fe20d29e29c25af68f236f"
OLD_CPU_SHA = "9f22f2c7709360b61a1d0765cf9776af47a2306efd8c1c61bfbd09a12077ef03"
ABI = "LE-uvec2-HIGH32-LOW32-to-uvec4-LOW64-HIGH64-valid-reserved"

def require(ok, message):
    if not ok:
        raise ValueError(message)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def digest(value):
    return sha(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode())

def unpack(value):
    data = zlib.decompress(base64.b64decode(value["zlib_base64"], validate=True))
    require(len(data) == value["bytes"] and sha(data) == value["sha256"], "packed artifact integrity")
    return data

def stdout(receipt):
    t = receipt["test_run"]
    require(t["rc"] == 0 and not t["timed_out"], "retained test status")
    text = t.get("stdout_zlib_base64") or "".join(t["stdout_zlib_base64_chunks"])
    data = zlib.decompress(base64.b64decode(text, validate=True))
    require(len(data) == t["stdout_bytes"] and sha(data) == t["stdout_sha256"], "retained stdout")
    return json.loads(data)

def load_retained():
    ig_raw, sc_raw = [(ROOT / p).read_bytes() for p in (IG, SC)]
    require(sha(ig_raw) == IG_SHA and sha(sc_raw) == SC_SHA, "two explicit receipts")
    ig, sc = json.loads(ig_raw), json.loads(sc_raw)
    pins = dict(ig["code_doc_sha256"])
    additions = [(IG, IG_SHA), (SC, SC_SHA)] + [(p["path"], p["sha256"]) for p in sc["pins"]]
    for path, h in additions:
        require(path not in pins or pins[path] == h, "conflicting dependency SHA")
        pins[path] = h
    for path, h in pins.items():
        require(sha((ROOT / path).read_bytes()) == h, "sealed dependency " + path)
    d, compiled = stdout(ig)["data"], stdout(sc)
    require(len(ig["proof_scope"]) == 38 and all(v is False for v in ig["proof_scope"].values()), "general STOP")
    row = compiled["compilations"][0]
    require(row["name"] == "vulkan_1_0_valid" and row["status"] == row["errors"] == row["warnings"] == 0,
            "specific retained compilation")
    require((row["target_env"], row["target_version"], row["shader_kind"], row["entry_point"]) ==
            (0, 4194304, 2, "main"), "not a target/backend alias")
    module = unpack(row["spirv"])
    require(sha(module) == MODULE_SHA, "specific SPIR-V")
    wrapper = unpack(compiled["wrapper"])
    require(sha(wrapper) == WRAPPER_SHA, "specific compile-only wrapper")
    header = (ROOT / "Blender/benchmarks/capacity_audit/axial_SOURCE_zero_aware_integer_v1.glsl").read_bytes()
    signed = (ROOT / "Blender/benchmarks/capacity_audit/axial_native_signed512_v1.glsl").read_bytes()
    require(unpack(row["source"]) == b"#version 450\n" + signed + b"\n" + header + b"\n" + wrapper,
            "module source assembly exact")
    return {"input": d["request"]["upstream_transport_INPUT"], "module": module,
            "pins": pins, "proof_scope": ig["proof_scope"]}

def selection():
    return {"compile_receipt_sha256": SC_SHA, "module_sha256": MODULE_SHA,
            "wrapper_sha256": WRAPPER_SHA, "SOURCE_header_sha256": SOURCE_SHA,
            "signed512_sha256": SIGNED_SHA, "target_env": 0, "target_version": 4194304,
            "entry_point": "main", "shader_kind": 2, "ABI": ABI}

def make_request(*, model):
    require(type(model) is str and model == MODEL, "explicit NEW HOST model")
    retained = load_retained()
    return {"model": MODEL, "intent": "HOST_PREPARATION_ONLY", "compiled_selection": selection(),
            "upstream_CPU_snapshot": deepcopy(retained["input"])}

def selected_word(word):
    require(type(word) is int and 0 <= word < (1 << 32), "strict uint32")
    e, m = (word >> 23) & 255, word & 0x7fffff
    require(e != 255 and (e != 0 or m == 0), "normal finite-or-zero limb")

def frame_payloads(snapshot):
    # ALL frames validated before any packing/emission. CPU tag stays CPU, never rewritten.
    require(type(snapshot) is dict and set(snapshot) == {"model", "program_INPUT", "decoder_INPUT", "frames"},
            "upstream CPU artifact shape")
    rows = snapshot["decoder_INPUT"]["SOURCE_limb_records"]
    frames = snapshot["frames"]
    require(type(rows) is list and type(frames) is list and len(rows) == len(frames) == 4, "complete four SOURCEs")
    require(snapshot["program_INPUT"]["decoder_selection"]["implementation_sha256"] == OLD_CPU_SHA,
            "upstream is old CPU artifact, NOT compiled program")
    require(snapshot["program_INPUT"]["decoder_INPUT_sha256"] == digest(snapshot["decoder_INPUT"]),
            "upstream complete decoder INPUT")
    staged = []
    seen = set()
    for row, frame in zip(rows, frames):
        require(type(frame) is dict and set(frame) == {"case_name", "source_id", "frame_base64"}, "closed frame metadata")
        identity = (row["case_name"], row["source_id"])
        require(identity not in seen and identity == (frame["case_name"], frame["source_id"]), "SOURCE identity/order")
        seen.add(identity)
        words = row["limb_uint32"]
        require(type(words) is list and len(words) == 4, "four SOURCE limbs")
        for word in words:
            selected_word(word)
        require(type(frame["frame_base64"]) is str, "base64 text")
        data = base64.b64decode(frame["frame_base64"], validate=True)
        require(len(data) == 120 and data[:8] == b"N3DZAD01", "old artifact frame120 magic")
        require(data[8:40].hex() == OLD_CPU_SHA, "old CPU implementation binding")
        require(data[40:72].hex() == row["context_sha256"] and data[72:104].hex() == digest(row),
                "context/SOURCE row binding")
        payload = data[104:]
        require(sha(payload) == row["hilo_le_sha256"] and
                payload == base64.b64decode(row["hilo_le_base64"], validate=True) and
                list(struct.unpack("<4I", payload)) == words, "lossless words/payload binding")
        staged.append((row, payload, sha(data)))
    return staged

def reflect_layout(module):
    # Exact-module structural ABI reflection. NOT SPIRV-Tools validation or semantic proof.
    require(type(module) is bytes and sha(module) == MODULE_SHA, "exact selected module")
    require(len(module) % 4 == 0 and len(module) >= 20, "SPIR-V size")
    words = struct.unpack("<" + "I" * (len(module) // 4), module)
    require(words[0] == 0x07230203, "SPIR-V header")
    types, decorations, member_offsets, variables = {}, {}, {}, []
    pos = 5
    while pos < len(words):
        count, op = words[pos] >> 16, words[pos] & 65535
        require(count > 0 and pos + count <= len(words), "SPIR-V instruction size")
        a = words[pos+1:pos+count]
        if op in (21, 23, 29, 30, 32):
            types[a[0]] = (op, a[1:])
        elif op == 71:
            decorations.setdefault(a[0], {})[a[1]] = a[2:]
        elif op == 72 and a[2] == 35:
            member_offsets[(a[0], a[1])] = a[3:]
        elif op == 59:
            variables.append(a[:3])
        pos += count
    result = []
    for pointer, var, storage in variables:
        dec = decorations.get(var, {})
        if 33 not in dec:
            continue
        binding = dec[33][0]
        require(dec.get(34) == (0,) and binding in (0, 1), "selected descriptor set/binding")
        op, ptr = types[pointer]
        require(op == 32 and ptr[0] == storage, "variable pointer type")
        op, members = types[ptr[1]]
        require(op == 30 and len(members) == 1 and member_offsets[(ptr[1], 0)] == (0,), "one member at offset0")
        array = members[0]
        op, elem = types[array]
        require(op == 29 and len(elem) == 1, "runtime array")
        op, vec = types[elem[0]]
        require(op == 23 and vec[1] == (2 if binding == 0 else 4), "uvec2/uvec4")
        op, integer = types[vec[0]]
        require(op == 21 and integer == (32, 0), "uint32 component")
        stride = decorations[array][6][0]
        require(stride == (8 if binding == 0 else 16), "actual compiled ArrayStride")
        result.append({"set": 0, "binding": binding, "stride_bytes": stride,
                       "components_uint32": vec[1], "member_offset": 0})
    result.sort(key=lambda r: r["binding"])
    require(len(result) == 2 and [r["binding"] for r in result] == [0, 1], "both buffers exactly once")
    return result

def dispatch_contract(count, input_bytes, output_bytes, groups):
    require(all(type(v) is int for v in (count, input_bytes, output_bytes)), "strict HOST sizes")
    require(count == 8 and input_bytes == 64 and output_bytes == 128, "fixed complete pilot shape")
    require(type(groups) is list and len(groups) == 3 and all(type(v) is int for v in groups), "strict groups")
    require(groups == [count, 1, 1], "exact invocation coverage, NO padding/oversubscription")
    return True

def emit_plan(staged, module, layout, proof):
    # Sole observable packing/emission point, reached only after ALL validation above.
    payload = b"".join(item[1] for item in staged)
    mapping = []
    for source_index, (row, _, frame_sha) in enumerate(staged):
        for component_index, component in enumerate(("real", "imag")):
            i = 2 * source_index + component_index
            mapping.append({"scalar_index": i, "case_name": row["case_name"], "source_id": row["source_id"],
                            "component": component, "context_sha256": row["context_sha256"],
                            "SOURCE_row_sha256": digest(row), "upstream_CPU_frame_sha256": frame_sha,
                            "SOURCE_request_sha256": row["SOURCE_request_sha256"],
                            "GRID_INPUT_plan_sha256": row["GRID_INPUT_plan_sha256"],
                            "ORIGINAL_uint64": row["scalars"][component_index]["original_uint64"],
                            "input_byte_offset": 8 * i, "output_byte_offset": 16 * i,
                            "whole_box_guard_disproved": row["retained_whole_box_guard_admission_disproved"]})
    require(len(payload) == 64 and len(mapping) == 8, "complete packed shape")
    return {"model": MODEL, "status": "HOST_PREPARED_GPU_STOP", "compiled_selection": selection(),
            "input_buffer": {"set": 0, "binding": 0, "bytes": len(payload), "stride_bytes": 8,
                             "sha256": sha(payload), "base64": base64.b64encode(payload).decode()},
            "output_buffer": {"set": 0, "binding": 1, "planned_bytes": 128, "stride_bytes": 16,
                              "result_bytes": None, "status0_words_invalid": True},
            "module_sha256": sha(module), "module_bytes": len(module), "compiled_layout": layout,
            "scalar_mapping": mapping, "dispatch_plan_unexecuted": [8, 1, 1],
            "upstream_CPU_frame_bytes": 480, "upstream_header_bytes": 416,
            "old_frame_tags_unchanged": True, "old_CPU_tag_is_NOT_compiled_program_selection": True,
            "GROUP_field_evaluation": None, "GPU_job_admission": False, "GPU_executed": False,
            "general_proof_scope": deepcopy(proof), "group_admissions": 0, "phase_quota": None,
            "missing_cases": 17, "missing_sources": 19, "full_costs": "UNMEASURED_NOT_ZERO",
            "GPU_budget_preflight": "UNCOMPUTED: 64+128 host payload is NOT a conservative GPU job budget",
            "new_decoder_calls": 0, "new_compiler_calls": 0, "scene_authentication": False,
            "runtime_runner_integrated": False, "numerical_GPU_semantics_proved": False}

def prepare(request, *, model):
    require(type(model) is str and model == MODEL, "explicit NEW HOST model")
    require(type(request) is dict and set(request) ==
            {"model", "intent", "compiled_selection", "upstream_CPU_snapshot"}, "closed new HOST INPUT")
    require(request["model"] == MODEL and request["intent"] == "HOST_PREPARATION_ONLY", "HOST intent only")
    require(digest(request["compiled_selection"]) == digest(selection()), "exact compiled selector, NOT old CPU")
    retained = load_retained()
    require(digest(request["upstream_CPU_snapshot"]) == digest(retained["input"]), "complete retained scene/ORIGINAL/gauges snapshot")
    staged = frame_payloads(request["upstream_CPU_snapshot"])
    layout = reflect_layout(retained["module"])
    dispatch_contract(8, 64, 128, [8, 1, 1])
    plan = emit_plan(staged, retained["module"], layout, retained["proof_scope"])
    plan["pins_verified"] = len(retained["pins"])
    plan["request_sha256"] = digest(request)
    return plan
