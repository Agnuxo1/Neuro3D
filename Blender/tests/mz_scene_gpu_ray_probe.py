"""Opt-in GPU ray/phase probe from saved Blender object matrices.

Bounded to EXP-001 ideal optics. Traces source, mirrors and BS2 discs on GPU;
does not implement detector-first-hit, Gaussian overlap or general materials.
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

from mz_scene_gpu_probe import NAMES, pack_record, position

STRIDE = 64
OUT_STRIDE = 12
SHADER = """#version 430
layout(local_size_x=32) in;
layout(std430,binding=0) readonly buffer Input { double x[]; };
layout(std430,binding=1) writeonly buffer Output { double y[]; };
uniform int control_count;
dvec3 at(int b) { return dvec3(x[b],x[b+1],x[b+2]); }
dvec3 refl(dvec3 d,dvec3 n) { return d-2.0*dot(d,n)*n; }
double cos_near_pi(double phase) {
    // EXP-001 phases are in [-pi, pi]. FP64 Taylor avoids this driver's
    // inaccurate FP32 cos near the dark port.
    double squared=phase*phase;
    double term=1.0,total=1.0;
    for(int k=1;k<=12;k++) {
        term *= -squared/(double(2*k-1)*double(2*k));
        total += term;
    }
    return total;
}
bool disc(dvec3 o,dvec3 d,dvec3 c,dvec3 n,double rad,
          out dvec3 hit,out double t) {
    double den=dot(d,n);
    if(abs(den)<1e-12) return false;
    t=dot(c-o,n)/den;
    if(t<=1e-9) return false;
    hit=o+d*t;
    return length(hit-c)<=rad;
}
void main() {
    int i=int(gl_GlobalInvocationID.x);
    if(i>=control_count) return;
    int b=i*64;
    dvec3 bs1=at(b),m1=at(b+4),m2=at(b+8),bs2=at(b+12);
    dvec3 source=at(b+32),source_dir=normalize(at(b+35));
    dvec3 bs1_n=normalize(at(b+38)),m1_n=normalize(at(b+42));
    dvec3 m2_n=normalize(at(b+46)),bs2_n=normalize(at(b+50));
    dvec3 h0,h1,h2,z1,z2;
    double t0,t1,t2,u1,u2;
    bool first=disc(source,source_dir,bs1,bs1_n,x[b+41],h0,t0);
    dvec3 d1=source_dir,d2=refl(source_dir,bs1_n);
    dvec3 r1=dvec3(0.0),r2=dvec3(0.0);
    bool a1=false,a2=false;
    if(first) {
        if(disc(h0,d1,m1,m1_n,x[b+45],h1,t1)) {
            r1=refl(d1,m1_n);
            a1=disc(h1,r1,bs2,bs2_n,x[b+53],z1,u1);
        }
        if(disc(h0,d2,m2,m2_n,x[b+49],h2,t2)) {
            r2=refl(d2,m2_n);
            a2=disc(h2,r2,bs2,bs2_n,x[b+53],z2,u2);
        }
    }
    double fa=0.0,fb=0.0,fe=0.0,delta=0.0,length_delta=0.0;
    int status=4;
    if(first) {
        if(a1 && a2) {
            status=0;
            // Refer both phases to the SAME point on the BS2 surface.
            double l1=t0+t1+u1+dot(r1,bs2-z1);
            double l2=t0+t2+u2+dot(r2,bs2-z2);
            length_delta=l2-l1;
            delta=6.2831853071795864769*length_delta*x[b+18]/x[b+19]+x[b+17]-x[b+16];
            double gamma=x[b+20];
            fa=0.5*(1.0-gamma*cos_near_pi(delta));
            fb=1.0-fa;
        } else if(a1 || a2) {
            status=a1 ? 1 : 2;
            fa=0.25; fb=0.25; fe=0.5;
        } else {
            status=3; fe=1.0;
        }
    } else fe=1.0;
    for(int c=0;c<3;c++) {
        double p=x[b+21]*x[b+22+c];
        y[i*12+c]=p*fa; y[i*12+3+c]=p*fb; y[i*12+6+c]=p*fe;
    }
    y[i*12+9]=double(status);
    y[i*12+10]=delta;
    y[i*12+11]=length_delta;
}
"""


def normal(record, role):
    matrix = record["objects"][role]["matrix_world"]
    if len(matrix) != 16:
        raise ValueError("Malformed saved Blender matrix")
    return tuple(float(matrix[4*i+2]) for i in range(3))


def input_record(record):
    base = pack_record(record)
    extra = [0.] * 32
    for offset, role, kind in ((0, "mz_source", "position"),
                               (3, "mz_source", "normal"),
                               (6, "mz_bs1", "normal"),
                               (10, "mz_mirror1", "normal"),
                               (14, "mz_mirror2", "normal"),
                               (18, "mz_bs2", "normal")):
        extra[offset:offset+3] = position(record, role) if kind == "position" else normal(record, role)
    for offset, role in ((9, "mz_bs1"), (13, "mz_mirror1"),
                         (17, "mz_mirror2"), (21, "mz_bs2")):
        extra[offset] = float(record["optics"][role]["radius"])
    values = base + extra
    if len(values) != STRIDE or not all(math.isfinite(v) for v in values):
        raise ValueError("Malformed GPU scene input")
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
    records = [json.loads((args.readbacks/(n+".readback.json")).read_text(encoding="utf-8"))
               for n in NAMES]
    values = [v for record in records for v in input_record(record)]
    packed = struct.pack(f"<{len(values)}d", *values)
    if not glfw.init():
        raise RuntimeError("GLFW initialization failed")
    window = None
    ctx = None
    try:
        glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        window = glfw.create_window(64, 64, "Neuro3D GPU ray probe", None, None)
        if window is None:
            raise RuntimeError("OpenGL 4.3 context unavailable")
        glfw.make_context_current(window)
        ctx = moderngl.create_context(require=430)
        vendor = ctx.info.get("GL_VENDOR", "unknown")
        renderer = ctx.info.get("GL_RENDERER", "unknown")
        if "NVIDIA" not in (vendor+renderer).upper():
            raise RuntimeError("GPU context not NVIDIA")
        shader = ctx.compute_shader(SHADER)
        source = ctx.buffer(packed)
        target = ctx.buffer(reserve=len(NAMES)*OUT_STRIDE*8)
        try:
            source.bind_to_storage_buffer(0)
            target.bind_to_storage_buffer(1)
            shader["control_count"].value = len(NAMES)
            started = time.perf_counter()
            shader.run(group_x=1)
            ctx.memory_barrier()
            output = target.read()
            elapsed_ms = (time.perf_counter()-started)*1000
        finally:
            source.release()
            target.release()
        out = struct.unpack(f"<{len(NAMES)*OUT_STRIDE}d", output)
        if not all(math.isfinite(v) for v in out):
            raise AssertionError("Non-finite GPU output")
        cases=[]
        for i,(name,record) in enumerate(zip(NAMES,records)):
            sample=out[i*OUT_STRIDE:(i+1)*OUT_STRIDE]
            expected=record["result"]
            if abs(sample[10]) > math.pi + 1e-9:
                raise AssertionError(f"{name}: phase outside validated cosine range")
            ray_status=int(sample[9])
            expected_status=expected["status"]
            status_matches=((expected_status=="ok" and ray_status==0) or
                            (expected_status=="missed_bs2" and ray_status in (1,2)))
            target_rgb=(expected["optical_a"]+expected["optical_b"]+
                        expected["escape_rgb"])
            diff=max(abs(a-b) for a,b in zip(sample[:9],target_rgb))
            totals=(sum(sample[:3]),sum(sample[3:6]),sum(sample[6:9]))
            expected_totals=(sum(expected["optical_a"]),
                             sum(expected["optical_b"]),sum(expected["escape_rgb"]))
            total_diff=max(abs(a-b) for a,b in zip(totals,expected_totals))
            cases.append({"control":name,"gpu_a":sum(sample[:3]),
                          "gpu_b":sum(sample[3:6]),"gpu_escape":sum(sample[6:9]),
                          "ray_status_code":ray_status,"expected_status":expected_status,
                          "status_matches":status_matches,"delta_phase":sample[10],
                          "rgb_worst_abs_diff":diff,"total_worst_abs_diff":total_diff,
                          "within_1e-9":max(diff,total_diff)<=1e-9})
        report={"vendor":vendor,"renderer":renderer,
                "dispatch_sync_readback_ms":round(elapsed_ms,3),
                "scene_source":str(args.readbacks),"cases":cases,
                "seven_control_power_parity":all(c["within_1e-9"] for c in cases),
                "seven_control_status_parity":all(c["status_matches"] for c in cases),
                "general_model_parity":False,
                "limitation":"Ideal optics only; no detector-first-hit, Gaussian overlap, absorption, or physical EM model."}
        args.report.write_text(json.dumps(report,indent=2),encoding="utf-8")
        print(json.dumps(report),flush=True)
    finally:
        if ctx is not None:
            ctx.release()
        if window is not None:
            glfw.destroy_window(window)
        glfw.terminate()


if __name__=="__main__":
    main()
