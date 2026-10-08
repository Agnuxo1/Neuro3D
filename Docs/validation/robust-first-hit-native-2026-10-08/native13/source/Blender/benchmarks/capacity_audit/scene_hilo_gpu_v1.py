"""Blender 4.5 OpenGL integer transport and compensated geometric diagnostics.

No GPU imports, dispatch or native procedure resolution occurs on import.
Raw bytes enter through GPUUniformBuf (PyBUF_SIMPLE, no scalar conversion).
R32UI output read() selects GPU_DATA_UINT in this pinned Blender build. The
RGBA32UI Python upload/read draft was rejected before any native execution.
Only the guarded Blender worker may call these functions. The arithmetic scope
is differences of observed geometry/query values; it is not an intersection,
phase, wave, RT/BVH, performance or universal floating-point certificate.

Visibility: Blender commit 62c1db4208e8 adds TEXTURE_FETCH and IMAGE_ACCESS
barriers after compute dispatch, but GLTexture::read invokes glGetTextureImage
without TEXTURE_UPDATE. This new path supplies the required host barrier and a
bounded completion fence in the SAME current Windows OpenGL context.
Primary API contracts:
https://registry.khronos.org/OpenGL-Refpages/gl4/html/glMemoryBarrier.xhtml
https://registry.khronos.org/OpenGL-Refpages/gl4/html/glFenceSync.xhtml
https://registry.khronos.org/OpenGL-Refpages/gl4/html/glClientWaitSync.xhtml
https://learn.microsoft.com/windows/win32/api/wingdi/nf-wingdi-wglgetprocaddress
https://docs.blender.org/api/4.5/gpu.types.html
"""
import ctypes
import hashlib
import math
from pathlib import Path
import struct
import sys
import time

SHADER = Path(__file__).parents[2] / "shaders" / "scene_hilo_transport_v1.glsl"
MAGIC = 0x4E33484C
OUTPUT_MAGIC = 0x4E33484F
HEADER_WORDS = 32
ROW_WORDS = 24
POISON = 0x5A5A5A5A
INPUT_BUFFER_WORDS = 8192
INPUT_BUFFER_BYTES = INPUT_BUFFER_WORDS * 4
GL_MAX_UNIFORM_BLOCK_SIZE = 0x8A30
MAX_SOURCES = 5
MAX_TRIANGLES = 64
MAX_VERTICES = 192
MAX_OBJECTS = 64
MAX_SCALARS = 4096
MAX_WORDS = 65536
GL_TEXTURE_UPDATE_BARRIER_BIT = 0x00000100
GL_SHADER_IMAGE_ACCESS_BARRIER_BIT = 0x00000020
GL_SYNC_GPU_COMMANDS_COMPLETE = 0x9117
GL_SYNC_FLUSH_COMMANDS_BIT = 0x00000001
GL_ALREADY_SIGNALED = 0x911A
GL_TIMEOUT_EXPIRED = 0x911B
GL_CONDITION_SATISFIED = 0x911C
GL_WAIT_FAILED = 0x911D
BARRIER_MASK = GL_TEXTURE_UPDATE_BARRIER_BIT | GL_SHADER_IMAGE_ACCESS_BARRIER_BIT
FENCE_DEADLINE_SECONDS = 5.0
FENCE_POLL_NANOSECONDS = 50_000_000


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unpack_words(raw):
    require(type(raw) is bytes and len(raw) % 4 == 0, "uint32 byte stream required")
    return list(struct.unpack("<" + str(len(raw) // 4) + "I", raw))


def pack_words(words):
    require(all(type(word) is int and 0 <= word <= 0xFFFFFFFF for word in words),
            "readback must contain exact uint32 values")
    return struct.pack("<" + str(len(words)) + "I", *words)


def padded_word_count(count):
    return ((count + 63) // 64) * 64


def admitted_layout(wire):
    """Enforce the native pilot's smaller bounds after CPU packet admission."""
    require(type(wire) is bytes and 128 <= len(wire) <= INPUT_BUFFER_BYTES,
            "bounded native input bytes required")
    words = unpack_words(wire)
    require(words[:3] == [MAGIC, 1, HEADER_WORDS] and words[3] == len(words),
            "native ABI header mismatch")
    require(words[6] == 8 and words[9] == 32 and words[12] == 8 and words[15] == 8,
            "native ABI stride mismatch")
    scalars, sources, vertices, triangles, objects = (words[i] for i in (4, 7, 10, 13, 16))
    require(0 < scalars <= MAX_SCALARS and 0 < sources <= MAX_SOURCES and
            0 < vertices <= MAX_VERTICES and 0 < triangles <= MAX_TRIANGLES and
            0 < objects <= MAX_OBJECTS, "native geometry/query bounds exceeded")
    require(words[5] == 32 and words[8] == 32 + scalars * 8 and
            words[11] == words[8] + sources * 32 and
            words[14] == words[11] + vertices * 8 and
            len(words) == words[14] + triangles * 8 and
            words[17] < scalars and not any(words[18:32]),
            "native input sections/reserved words invalid")
    row_count = sources * vertices + sources + 2 * triangles
    output_count = HEADER_WORDS + ROW_WORDS * row_count
    require(output_count <= MAX_WORDS, "native output bound exceeded")
    return {"input_words": len(words), "output_words": output_count,
            "row_count": row_count, "scalar_count": scalars,
            "source_count": sources, "vertex_count": vertices,
            "triangle_count": triangles, "object_count": objects}


def device_profile(gpu):
    profile = {"backend": gpu.platform.backend_type_get(),
               "vendor": gpu.platform.vendor_get(),
               "renderer": gpu.platform.renderer_get(),
               "driver_version": gpu.platform.version_get()}
    require(sys.platform == "win32", "this native sync binding is Windows-only")
    require(profile["backend"] == "OPENGL", "explicit OpenGL backend required")
    require("NVIDIA" in profile["vendor"].upper() and
            "RTX 3090" in profile["renderer"].upper(),
            "the preregistered NVIDIA RTX 3090 context is required")
    return profile


class OpenGLReadbackSync:
    """Resolve only documented synchronization calls in a verified WGL context.

    Windows GL procedure pointers are context-dependent. No context creation,
    GL resource ownership, dispatch, pointer arithmetic or private Blender API
    is performed here. ctypes scalar/pointer widths match the Khronos C ABI.
    """

    def __init__(self):
        require(sys.platform == "win32", "Windows OpenGL synchronization required")
        self._dll = ctypes.WinDLL("opengl32.dll")
        self._current = self._dll.wglGetCurrentContext
        self._current.restype = ctypes.c_void_p
        self._current.argtypes = []
        self._get_proc = self._dll.wglGetProcAddress
        self._get_proc.restype = ctypes.c_void_p
        self._get_proc.argtypes = [ctypes.c_char_p]
        self._get_error = self._dll.glGetError
        self._get_error.restype = ctypes.c_uint32
        self._get_error.argtypes = []
        self._get_integer = self._dll.glGetIntegerv
        self._get_integer.restype = None
        self._get_integer.argtypes = [ctypes.c_uint32, ctypes.POINTER(ctypes.c_int32)]
        self.context = self._current()
        require(bool(self.context), "no current WGL context")
        self._barrier = self._resolve("glMemoryBarrier", None, ctypes.c_uint32)
        self._fence = self._resolve("glFenceSync", ctypes.c_void_p,
                                   ctypes.c_uint32, ctypes.c_uint32)
        self._wait = self._resolve("glClientWaitSync", ctypes.c_uint32,
                                  ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint64)
        self._delete = self._resolve("glDeleteSync", None, ctypes.c_void_p)

    def _resolve(self, name, result_type, *argument_types):
        pointer = self._get_proc(name.encode("ascii"))
        invalid = {None, 0, 1, 2, 3, ctypes.c_void_p(-1).value}
        require(pointer not in invalid, "missing valid OpenGL procedure: " + name)
        return ctypes.WINFUNCTYPE(result_type, *argument_types)(pointer)

    def assert_context(self):
        require(self._current() == self.context, "WGL context changed during dispatch/readback")

    def require_no_error(self, stage):
        self.assert_context()
        error = self._get_error()
        require(error == 0, stage + ": OpenGL error " + hex(error))

    def uniform_buffer_limit(self):
        self.assert_context()
        value = ctypes.c_int32()
        self._get_integer(GL_MAX_UNIFORM_BLOCK_SIZE, ctypes.byref(value))
        self.require_no_error("uniform buffer size capability query")
        require(value.value >= INPUT_BUFFER_BYTES, "driver uniform block limit below fixed 32 KiB profile")
        return value.value

    def wait_for_readback(self):
        self.require_no_error("before texture-update barrier")
        start = time.monotonic()
        self._barrier(BARRIER_MASK)
        self.require_no_error("texture-update barrier")
        fence = self._fence(GL_SYNC_GPU_COMMANDS_COMPLETE, 0)
        require(bool(fence), "glFenceSync returned a null fence")
        polls, final_status = 0, None
        try:
            self.require_no_error("fence creation")
            deadline = start + FENCE_DEADLINE_SECONDS
            while time.monotonic() < deadline:
                self.assert_context()
                remaining_ns = max(1, int((deadline - time.monotonic()) * 1_000_000_000))
                timeout_ns = min(FENCE_POLL_NANOSECONDS, remaining_ns)
                flags = GL_SYNC_FLUSH_COMMANDS_BIT if polls == 0 else 0
                final_status = self._wait(fence, flags, timeout_ns)
                polls += 1
                self.require_no_error("fence client wait")
                if final_status in (GL_ALREADY_SIGNALED, GL_CONDITION_SATISFIED):
                    return {"barrier_mask": BARRIER_MASK,
                            "barrier_names": ["GL_TEXTURE_UPDATE_BARRIER_BIT",
                                              "GL_SHADER_IMAGE_ACCESS_BARRIER_BIT"],
                            "fence_status": final_status, "fence_polls": polls,
                            "fence_deadline_seconds": FENCE_DEADLINE_SECONDS,
                            "fence_elapsed_ms": (time.monotonic() - start) * 1000.0,
                            "same_context_verified": True}
                require(final_status == GL_TIMEOUT_EXPIRED,
                        "glClientWaitSync failed or returned an unknown status")
            raise TimeoutError("native GPU readback fence exceeded five-second deadline")
        finally:
            self.assert_context()
            self._delete(fence)
            self.require_no_error("fence deletion")


def native_shader(gpu):
    """Compile the independently versioned consumer; leave frozen V2 unchanged."""
    info = gpu.types.GPUShaderCreateInfo()
    OpenGLReadbackSync().uniform_buffer_limit()
    info.typedef_source("struct HiloInputPacket { uvec4 words[2048]; };")
    info.uniform_buf(0, "HiloInputPacket", "input_packet")
    info.image(0, "R32UI", "UINT_2D", "echo_words", qualifiers={"WRITE"})
    info.image(1, "R32UI", "UINT_2D", "delta_words", qualifiers={"WRITE"})
    for name in ("input_word_count", "output_word_count", "zero_low", "dispatch_nonce"):
        info.push_constant("INT", name)
    info.local_group_size(1, 1, 1)
    info.compute_source(SHADER.read_text(encoding="utf-8"))
    return gpu.shader.create_from_info(info)


def _flatten(value):
    if isinstance(value, (list, tuple)):
        for element in value:
            yield from _flatten(element)
    else:
        yield value


def _read_texture(texture, expected_words):
    words = list(_flatten(texture.read().to_list()))
    require(len(words) == padded_word_count(expected_words), "complete texture readback required")
    require(all(type(value) is int and 0 <= value <= 0xFFFFFFFF for value in words),
            "GPU UINT texture was converted, truncated or non-integer")
    require(all(value == POISON for value in words[expected_words:]),
            "output padding changed or was not initialized to the declared poison")
    return words


def validate_readback(wire, echo_raw, computed_raw, *, zero_low, nonce):
    """Validate native identity/status and exact bits before numerical auditing."""
    layout = admitted_layout(wire)
    echo, computed = unpack_words(echo_raw), unpack_words(computed_raw)
    require(len(echo) == padded_word_count(layout["input_words"]) and
            len(computed) == padded_word_count(layout["output_words"]),
            "readback physical length mismatch")
    expected_echo = unpack_words(wire) + [POISON] * (len(echo) - len(wire) // 4)
    require(echo == expected_echo, "native integer echo is not bit-for-bit exact")
    expected_header = [
        OUTPUT_MAGIC, 1, HEADER_WORDS, layout["output_words"],
        layout["input_words"], layout["row_count"], layout["source_count"],
        layout["vertex_count"], layout["triangle_count"], layout["scalar_count"],
        layout["object_count"], zero_low, 0, 1, nonce, nonce ^ 0xFFFFFFFF,
    ] + [0] * 16
    require(computed[:32] == expected_header,
            "native result header, nonce, mode or completed status mismatch")
    require(all(word == POISON for word in computed[layout["output_words"]:]),
            "native result padding mismatch")
    for offset in range(HEADER_WORDS, layout["output_words"], ROW_WORDS):
        require(computed[offset + 22:offset + 24] == [0, 0], "result row reserved words changed")
    return layout


def dispatch(gpu, shader, wire, *, zero_low, nonce):
    """One bounded real compute dispatch, explicit visibility/fence, integer read."""
    require(type(zero_low) is int and zero_low in (0, 1), "declared low-zero mode required")
    require(type(nonce) is int and 0 < nonce < 0x80000000, "positive signed-int dispatch nonce required")
    device_profile(gpu)
    layout = admitted_layout(wire)
    sync = OpenGLReadbackSync()
    sync.require_no_error("before native allocation")
    uniform_block_limit = sync.uniform_buffer_limit()
    padded = padded_word_count(len(wire) // 4)
    upload_bytes = wire + bytes(INPUT_BUFFER_BYTES - len(wire))
    source = echo = computed = None
    allocation_started = time.perf_counter()
    try:
        source = gpu.types.GPUUniformBuf(upload_bytes)
        echo = gpu.types.GPUTexture((64, padded // 64), format="R32UI")
        computed = gpu.types.GPUTexture(
            (64, padded_word_count(layout["output_words"]) // 64), format="R32UI")
        for texture in (echo, computed):
            texture.clear(format="UINT", value=(POISON,))
        shader.uniform_block("input_packet", source)
        shader.image("echo_words", echo)
        shader.image("delta_words", computed)
        for name, value in (("input_word_count", layout["input_words"]),
                            ("output_word_count", layout["output_words"]),
                            ("zero_low", zero_low), ("dispatch_nonce", nonce)):
            shader.uniform_int(name, value)
        sync.require_no_error("before native dispatch")
        start = time.perf_counter()
        allocation_upload_bind_ms = (start - allocation_started) * 1000.0
        gpu.compute.dispatch(shader, 1, 1, 1)
        synchronization = sync.wait_for_readback()
        sync.assert_context()
        echo_words = _read_texture(echo, layout["input_words"])
        result_words = _read_texture(computed, layout["output_words"])
        sync.require_no_error("after integer readback")
        echo_raw, computed_raw = pack_words(echo_words), pack_words(result_words)
        validate_readback(wire, echo_raw, computed_raw, zero_low=zero_low, nonce=nonce)
        elapsed = (time.perf_counter() - start) * 1000.0
        require(math.isfinite(elapsed), "finite diagnostic elapsed time required")
        return {"zero_low": zero_low, "dispatch_nonce": nonce, "layout": layout,
                "input_echo_hex": echo_raw.hex(), "computed_rows_hex": computed_raw.hex(),
                "readback_sha256": hashlib.sha256(echo_raw + computed_raw).hexdigest(),
                "synchronization": synchronization,
                "dispatch_sync_readback_host_validation_ms": elapsed,
                "allocation_upload_bind_ms": allocation_upload_bind_ms,
                "gpu_resource_payload_bytes": {
                    "source_ubo": INPUT_BUFFER_BYTES, "echo": padded * 4,
                    "computed": padded_word_count(layout["output_words"]) * 4,
                    "total": INPUT_BUFFER_BYTES + (padded + padded_word_count(layout["output_words"])) * 4},
                "storage_profile": "input raw-byte std140 uvec4 UBO32KiB; outputs R32UI UINT words; physical row width64",
                "opengl_max_uniform_block_size": uniform_block_limit,
                "timing_scope": "CPU wall clock; allocation/upload/binding and combined dispatch/fence/readback/host validation; no isolated GPU timing",
                "scope": "one OpenGL scalar-ALU diagnostic invocation; no RT/BVH or timing advantage"}
    finally:
        # Release GPU Python owners before the Blender event-loop quit timer.
        source = echo = computed = None
