#version 430
// Experimental raw-path consumer. No intersection / RT / physical optics.
// FP64 distances, phase reduction, products and sums; FP32 sin/cos explicitly.
layout(local_size_x=8) in;
layout(std430,binding=0) readonly buffer Paths { double p[]; };
layout(std430,binding=1) readonly buffer Hits { double h[]; };
layout(std430,binding=2) writeonly buffer Fields { double out_field[]; };
uniform int path_count;
uniform int port_count;
uniform double wavelength_BU;
const double TAU = 6.2831853071795864769lf;
dvec2 mul(dvec2 a, dvec2 b) {
    return dvec2(a.x*b.x-a.y*b.y, a.x*b.y+a.y*b.x);
}
dvec2 rotate_field(dvec2 value, double phase) {
    double reduced = phase - TAU*floor(phase/TAU+0.5);
    float angle = float(reduced);
    return mul(value, dvec2(double(cos(angle)), double(sin(angle))));
}
void main() {
    int port = int(gl_GlobalInvocationID.x);
    if (port >= port_count) return;
    dvec2 sum_field = dvec2(0.0);
    // One deterministic work item per port, no atomics / nondeterministic sum.
    for (int path=0; path<path_count; ++path) {
        int b=path*8;
        if (int(p[b]) != port) continue;
        dvec2 value=dvec2(p[b+3],p[b+4]);
        int first=int(p[b+1]);
        for (int j=0; j<int(p[b+2]); ++j) {
            int e=(first+j)*4;
            value=rotate_field(value, TAU*h[e]/wavelength_BU);
            int code=int(h[e+2]);
            if (code==1) value*=0.7071067811865475244lf;
            if (code==2) value=mul(value,dvec2(0.0,0.7071067811865475244lf));
            if (code==3) value=-rotate_field(value,h[e+1]);
        }
        value=rotate_field(value,TAU*p[b+5]/wavelength_BU);
        sum_field+=value;
    }
    out_field[port*4]=sum_field.x;
    out_field[port*4+1]=sum_field.y;
    out_field[port*4+2]=dot(sum_field,sum_field);
    out_field[port*4+3]=0.0;
}
