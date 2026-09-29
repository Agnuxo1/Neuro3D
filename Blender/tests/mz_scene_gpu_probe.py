"""Opt-in, bounded GPU phase probe from saved Blender MZ readback.

This is a deliberately limited equal-arm ideal combiner. It derives path
lengths from reopened object matrices on the GPU, but does not ray-trace
apertures, mode overlap or detector occlusion. D is a negative control.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import struct
import time

import glfw
import moderngl

NAMES = ("A", "B-geo", "B-mat", "C-A", "C-B-geo", "C-B-mat", "D")
STRIDE = 32
OUT_STRIDE = 8
SHADER = """#version 430
layout(local_size_x=32) in;
layout(std430,binding=0) readonly buffer Input { double x[]; };
layout(std430,binding=1) writeonly buffer Output { double y[]; };
uniform int control_count;
dvec3 at(int base) { return dvec3(x[base],x[base+1],x[base+2]); }
void main() {
    int i=int(gl_GlobalInvocationID.x);
    if(i>=control_count) return;
    int b=i*32;
    dvec3 bs1=at(b), m1=at(b+4), m2=at(b+8), bs2=at(b+12);
    double l1=length(m1-bs1)+length(bs2-m1);
    double l2=length(m2-bs1)+length(bs2-m2);
    double delta=6.2831853071795864769*(l2-l1)*x[b+18]/x[b+19]+x[b+17]-x[b+16];
    double gamma=x[b+20];
    // This OpenGL driver has no cos(double); phase geometry stays FP64,
    // while the final trigonometric evaluation is explicitly FP32.
    double fraction_a=0.5*(1.0-gamma*double(cos(float(delta))));
    double fraction_b=1.0-fraction_a;
    for(int c=0;c<3;c++) {
        double channel_power=x[b+21]*x[b+22+c];
        y[i*8+c]=channel_power*fraction_a;
        y[i*8+3+c]=channel_power*fraction_b;
    }
    y[i*8+6]=delta;
    y[i*8+7]=l2-l1;
}
"""


def position(record, role):
    values = record["objects"][role]["matrix_world"]
    if len(values) != 16:
        raise ValueError("Malformed saved Blender matrix")
    return tuple(float(values[4 * row + 3]) for row in range(3))


def pack_record(record):
    optics = record["optics"]
    src = optics["mz_source"]
    if (abs(optics["mz_bs1"]["transmission"] - .5) > 1e-12 or
        abs(optics["mz_bs2"]["transmission"] - .5) > 1e-12 or
        any(abs(v - 1.) > 1e-12 for role in ("mz_mirror1", "mz_mirror2")
            for v in optics[role]["reflectance_rgb"]) or
        abs(src["absorption_per_unit"]) > 1e-12):
        raise ValueError("Probe supports only the preregistered ideal optics")
    weights = tuple(float(v) for v in src["rgb"])
    norm = sum(weights)
    if norm <= 0:
        raise ValueError("Zero source RGB weight")
    values = [0.] * STRIDE
    for offset, role in ((0, "mz_bs1"), (4, "mz_mirror1"),
                         (8, "mz_mirror2"), (12, "mz_bs2")):
        values[offset:offset+3] = position(record, role)
    values[16] = float(optics["mz_mirror1"]["phase_shift"])
    values[17] = float(optics["mz_mirror2"]["phase_shift"])
    values[18] = float(src["frequency"])
    values[19] = float(src["propagation_speed"])
    values[20] = float(src["mutual_coherence"])
    values[21] = float(src["power"])
    values[22:25] = [v/norm for v in weights]
    if not all(math.isfinite(v) for v in values):
        raise ValueError("Non-finite scene input")
    return values


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--readbacks", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--authorized-by-user", action="store_true")
    args = parser.parse_args()
    if not args.authorized_by_user:
        raise SystemExit("Explicit GPU authorization required")
    if args.report.exists() or not args.report.parent.is_dir():
        raise SystemExit("Report exists or parent missing")
    records = [json.loads((args.readbacks / (name + ".readback.json")).read_text(encoding="utf-8"))
               for name in NAMES]
    inputs = [v for record in records for v in pack_record(record)]
    packed = struct.pack(f"<{len(inputs)}d", *inputs)
    if not glfw.init():
        raise RuntimeError("GLFW initialization failed")
    window = None
    ctx = None
    try:
        glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        window = glfw.create_window(64, 64, "Neuro3D scene GPU probe", None, None)
        if window is None:
            raise RuntimeError("OpenGL 4.3 context unavailable")
        glfw.make_context_current(window)
        ctx = moderngl.create_context(require=430)
        vendor = ctx.info.get("GL_VENDOR", "unknown")
        renderer = ctx.info.get("GL_RENDERER", "unknown")
        if "NVIDIA" not in (vendor + renderer).upper():
            raise RuntimeError("GPU context not NVIDIA")
        shader = ctx.compute_shader(SHADER)
        source = ctx.buffer(packed)
        target = ctx.buffer(reserve=len(NAMES) * OUT_STRIDE * 8)
        try:
            source.bind_to_storage_buffer(0)
            target.bind_to_storage_buffer(1)
            shader["control_count"].value = len(NAMES)
            started = time.perf_counter()
            shader.run(group_x=1)
            ctx.memory_barrier()
            output = target.read()
            elapsed_ms = (time.perf_counter() - started) * 1000
        finally:
            source.release()
            target.release()
        values = struct.unpack(f"<{len(NAMES)*OUT_STRIDE}d", output)
        if not all(math.isfinite(v) for v in values):
            raise AssertionError("Non-finite GPU scene output")
        cases = []
        for i, (name, record) in enumerate(zip(NAMES, records)):
            sample = values[i*OUT_STRIDE:(i+1)*OUT_STRIDE]
            expected = record["result"]
            difference = max(abs(a-b) for a,b in
                             zip(sample[:6], expected["optical_a"]+expected["optical_b"]))
            cases.append({"control": name, "gpu_a": sum(sample[:3]),
                          "gpu_b": sum(sample[3:6]), "delta_phase": sample[6],
                          "path_difference": sample[7], "rgb_worst_abs_diff": difference,
                          "within_1e-8": difference <= 1e-8})
        report = {"vendor": vendor, "renderer": renderer,
                  "dispatch_sync_readback_ms": round(elapsed_ms, 3),
                  "scene_source": str(args.readbacks), "cases": cases,
                  "ideal_controls_pass": all(c["within_1e-8"] for c in cases[:-1]),
                  "full_mz_parity": all(c["within_1e-8"] for c in cases),
                  "limitation": "GPU uses saved object centers and ideal combiner; no aperture/ray/detector gate or physical EM simulation."}
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
