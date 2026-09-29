"""Opt-in bounded RTX probe for the dormant Neuro3D compute shader.

Tests compilation, GPU dispatch and readback of the per-neuron update.
It does not establish parity with the MZ scene or graph-based CPU model.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import struct
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
SHADER = ROOT / "shaders" / "nebula_photonic_compute.glsl"


def f32(x):
    return struct.unpack("<f", struct.pack("<f", x))[0]


def state(i):
    return (f32(i / 10), 0., 0., .2, f32(.3 + .01 * i), f32(450 + i % 17),
            f32(.7 if i % 2 == 0 else .1), f32(.6), 1., .25, .5, 1.)


def reference(s):
    out = list(s)
    out[4] = f32(f32(s[4]) + f32(f32(s[5]) * f32(.01)))
    out[6] = f32(max(0., min(1., s[6])))
    out[7] = f32(max(0., min(1., f32(s[7] * f32(.98)))))
    if out[6] < .25:
        out[7] = f32(out[7] * f32(.98))
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--authorized-by-user", action="store_true")
    args = parser.parse_args()
    if not args.authorized_by_user:
        raise SystemExit("Explicit GPU authorization required")
    if args.report.exists() or not args.report.parent.is_dir():
        raise SystemExit("Report exists or parent directory missing")
    import glfw
    import moderngl
    if not glfw.init():
        raise RuntimeError("GLFW initialization failed")
    window = None
    ctx = None
    try:
        glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        window = glfw.create_window(64, 64, "Neuro3D GPU probe", None, None)
        if window is None:
            raise RuntimeError("OpenGL 4.3 context unavailable")
        glfw.make_context_current(window)
        ctx = moderngl.create_context(require=430)
        vendor = ctx.info.get("GL_VENDOR", "unknown")
        renderer = ctx.info.get("GL_RENDERER", "unknown")
        if "NVIDIA" not in (vendor + renderer).upper():
            raise RuntimeError("Context is not on NVIDIA GPU")
        shader = ctx.compute_shader(SHADER.read_text(encoding="utf-8"))
        shader["delta_seconds"].value = .01
        shader["activation_threshold"].value = .25
        cases = []
        for count in (64, 1024, 4096):
            states = [state(i) for i in range(count)]
            packed = struct.pack(f"<{12 * count}f", *(x for s in states for x in s))
            source = ctx.buffer(packed)
            target = ctx.buffer(reserve=len(packed))
            try:
                source.bind_to_storage_buffer(0)
                target.bind_to_storage_buffer(1)
                shader["neuron_count"].value = count
                started = time.perf_counter()
                shader.run(group_x=math.ceil(count / 64))
                ctx.memory_barrier()
                output = target.read()
                elapsed = (time.perf_counter() - started) * 1000
            finally:
                source.release()
                target.release()
            actual = struct.unpack(f"<{12 * count}f", output)
            if not all(math.isfinite(x) for x in actual):
                raise AssertionError("Non-finite GPU output")
            worst = max(abs(actual[12*i+j] - reference(s)[j])
                        for i, s in enumerate(states) for j in range(12))
            cases.append({"neurons": count, "worst_abs_diff": worst,
                          "dispatch_sync_readback_ms": round(elapsed, 3)})
            if worst > 1e-5:
                raise AssertionError(f"GPU local-rule mismatch: {worst}")
        sys.path.insert(0, str(ROOT / "core"))
        from photonic_model import Graph, NeuronState, step
        graph = Graph([NeuronState((0., 0., 0.), phase=.3, frequency=450.,
                                   intensity=.7, energy=.6, color=(1., .25, .5))], [])
        step(graph, .01)
        first = reference(state(0))
        graph_gap = max(abs(graph.neurons[0].phase - first[4]),
                        abs(graph.neurons[0].intensity - first[6]),
                        abs(graph.neurons[0].energy - first[7]))
        report = {"vendor": vendor, "renderer": renderer, "cases": cases,
                  "shader_local_rule_passes": True,
                  "cpu_graph_model_parity": graph_gap <= 1e-5,
                  "cpu_graph_model_worst_abs_diff": graph_gap,
                  "limitation": "Shader reads neither Blender geometry nor graph edges; no MZ/network parity."}
        args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(json.dumps(report), flush=True)
    finally:
        if ctx is not None:
            ctx.release()
        if window is not None:
            glfw.destroy_window(window)
        glfw.terminate()


if __name__ == "__main__":
    main()
