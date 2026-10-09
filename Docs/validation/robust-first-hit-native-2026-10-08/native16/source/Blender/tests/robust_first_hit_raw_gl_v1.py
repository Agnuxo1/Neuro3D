"""Bounded core-OpenGL dispatch in Blender's verified private WGL context.

Only integer packet upload/readback occurs on CPU. Geometry stays in GLSL.
No independent oracle or frozen expected result is consumed here.
"""
import ctypes as c
import time

from Blender.benchmarks.capacity_audit import scene_hilo_gpu_v1 as base


class RawProgram:
    def __init__(self, handle):
        self.handle = handle
        self.sync = base.OpenGLReadbackSync()

    def entry(self, name, result, *arguments):
        # OpenGL 1.1 entry points are exported by opengl32.dll on Windows.
        try:
            function = getattr(self.sync._dll, name)
            function.restype, function.argtypes = result, arguments
            return function
        except AttributeError:
            return self.sync._resolve(name, result, *arguments)

    def close(self):
        if self.handle:
            self.entry("glDeleteProgram", None, c.c_uint32)(self.handle)
            self.handle = 0

    def dispatch(self, wire, constants, output_words=64):
        self.sync.uniform_buffer_limit()
        self.sync.require_no_error("before raw OpenGL allocation")
        U, I, P = c.c_uint32, c.c_int32, c.c_void_p
        gen_buffers = self.entry("glGenBuffers", None, I, c.POINTER(U))
        bind_buffer = self.entry("glBindBuffer", None, U, U)
        buffer_data = self.entry("glBufferData", None, U, c.c_ssize_t, P, U)
        bind_base = self.entry("glBindBufferBase", None, U, U, U)
        gen_textures = self.entry("glGenTextures", None, I, c.POINTER(U))
        bind_texture = self.entry("glBindTexture", None, U, U)
        storage = self.entry("glTexStorage2D", None, U, I, U, I, I)
        clear = self.entry("glClearTexImage", None, U, I, U, U, P)
        bind_image = self.entry("glBindImageTexture", None, U, U, I, c.c_ubyte, I, U, U)
        use = self.entry("glUseProgram", None, U)
        location = self.entry("glGetUniformLocation", I, U, c.c_char_p)
        uniform = self.entry("glUniform1i", None, I, I)
        compute = self.entry("glDispatchCompute", None, U, U, U)
        read = self.entry("glGetTexImage", None, U, I, U, U, P)
        delete_buffers = self.entry("glDeleteBuffers", None, I, c.POINTER(U))
        delete_textures = self.entry("glDeleteTextures", None, I, c.POINTER(U))
        get_index = self.entry("glGetIntegeri_v", None, U, U, c.POINTER(I))
        previous_program, previous_buffer, previous_texture, previous_base = I(), I(), I(), I()
        for token, value in ((0x8B8D, previous_program), (0x8A28, previous_buffer),
                             (0x8069, previous_texture)):
            self.sync._get_integer(token, c.byref(value))
        get_index(0x8A28, 0, c.byref(previous_base))
        source, textures = U(), (U * 2)()
        padded = base.padded_word_count(len(wire) // 4)
        started = time.perf_counter()
        try:
            gen_buffers(1, c.byref(source))
            bind_buffer(0x8A11, source.value)  # GL_UNIFORM_BUFFER
            upload = c.create_string_buffer(wire + bytes(base.INPUT_BUFFER_BYTES - len(wire)))
            buffer_data(0x8A11, base.INPUT_BUFFER_BYTES, upload, 0x88E4)  # STATIC_DRAW
            bind_base(0x8A11, 0, source.value)
            gen_textures(2, textures)
            poison = U(base.POISON)
            for index, count in enumerate((padded, output_words)):
                bind_texture(0x0DE1, textures[index])  # GL_TEXTURE_2D
                storage(0x0DE1, 1, 0x8236, 64, count // 64)  # R32UI
                clear(textures[index], 0, 0x8D94, 0x1405, c.byref(poison))
                bind_image(index, textures[index], 0, 0, 0, 0x88B9, 0x8236)
            use(self.handle)
            for name, value in constants.items():
                slot = location(self.handle, name.encode("ascii"))
                if slot < 0:
                    raise ValueError("missing raw shader uniform: " + name)
                uniform(slot, value)
            allocation_ms = (time.perf_counter() - started) * 1000
            self.sync.require_no_error("before raw exact first-hit dispatch")
            started = time.perf_counter()
            compute(1, 1, 1)
            synchronization = self.sync.wait_for_readback()
            arrays = []
            for index, count in enumerate((padded, output_words)):
                values = (U * count)()
                bind_texture(0x0DE1, textures[index])
                read(0x0DE1, 0, 0x8D94, 0x1405, values)
                arrays.append(list(values))
            self.sync.require_no_error("after raw exact first-hit readback")
            return {
                "echo": arrays[0], "result": arrays[1],
                "allocation_upload_bind_ms": allocation_ms,
                "dispatch_sync_readback_host_validation_ms":
                    (time.perf_counter() - started) * 1000,
                "synchronization": synchronization,
                "resource_payload_bytes": base.INPUT_BUFFER_BYTES + 4 * (padded + output_words),
            }
        finally:
            # Restore the GL state touched here before returning to Blender.
            for index in (0, 1):
                bind_image(index, 0, 0, 0, 0, 0x88B9, 0x8236)
            bind_base(0x8A11, 0, previous_base.value)
            bind_buffer(0x8A11, previous_buffer.value)
            bind_texture(0x0DE1, previous_texture.value)
            use(previous_program.value)
            if any(textures):
                delete_textures(2, textures)
            if source.value:
                delete_buffers(1, c.byref(source))
            self.sync.require_no_error("raw OpenGL cleanup")
