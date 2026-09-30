// Opt-in scalar phase probe only. NOT geometry/scene propagation or RT.
// GPUShaderCreateInfo declares samples_in, trace_out and sample_count.
const double TAU = 6.2831853071795864769lf;
const double MIN_NORMAL = 2.2250738585072014e-308lf;
bool normal_zero(double x) { return x == 0.0lf || abs(x) >= MIN_NORMAL; }
bool finite_value(double x) { return !isnan(x) && !isinf(x); }
void scalar_out(int column, int row, double value) {
    imageStore(trace_out, ivec2(column,row), uvec4(unpackDouble2x32(value),0u,0u));
}
void main() {
    int id = int(gl_GlobalInvocationID.x);
    if (id >= sample_count) return;
    for (int column=0;column<7;column++) imageStore(trace_out,ivec2(column,id),uvec4(0u));
    uvec4 words = texelFetch(samples_in,ivec2(id,0),0);
    double length = packDouble2x32(words.xy);
    double wavelength = packDouble2x32(words.zw);
    uint status = 0u;
    precise double quotient=0.0lf, residual=0.0lf, correction=0.0lf, reduced=0.0lf;
    if (!finite_value(length) || !finite_value(wavelength) || length<0.0lf || wavelength<=0.0lf
        || !normal_zero(length) || !normal_zero(wavelength)) status=1u;
    if (status==0u) {
        quotient=length/wavelength;
        if (!finite_value(quotient) || quotient>=4503599627370496.0lf
            || !normal_zero(quotient) || (length>0.0lf && quotient==0.0lf)) status=2u;
    }
    if (status==0u) {
        // Must remain a native FMA, never silently multiply then subtract.
        residual=fma(-quotient,wavelength,length);
        if (!finite_value(residual) || !normal_zero(residual)) status=3u;
    }
    if (status==0u) {
        correction=residual/wavelength;
        if (!finite_value(correction) || !normal_zero(correction) || abs(correction)>0.5lf) status=4u;
    }
    if (status==0u) {
        precise double cycles=(quotient-floor(quotient))+correction;
        reduced=cycles-floor(cycles+0.5lf);
        precise double product=TAU*reduced;
        float angle=float(product);
        scalar_out(0,id,quotient); scalar_out(1,id,residual);
        scalar_out(2,id,correction); scalar_out(3,id,reduced); scalar_out(4,id,double(angle));
        imageStore(trace_out,ivec2(5,id),uvec4(unpackDouble2x32(double(cos(angle))),
                                             unpackDouble2x32(double(sin(angle)))));
    }
    imageStore(trace_out,ivec2(6,id),uvec4(status,uint(id),0u,0u));
}
