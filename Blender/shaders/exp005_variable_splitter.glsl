// V2: property-owned lossless splitter, no CPU-precomputed field coefficients.
const double TAU = 6.2831853071795864769lf;
dvec4 raw4(sampler2D hi, sampler2D lo, int index) {
    ivec2 at = ivec2(index%64,index/64);
    return dvec4(texelFetch(hi,at,0)) + dvec4(texelFetch(lo,at,0));
}
dvec2 product(dvec2 a,dvec2 b) {
    return dvec2(a.x*b.x-a.y*b.y,a.x*b.y+a.y*b.x);
}
dvec2 rotate_field(dvec2 value,double phase) {
    float angle=float(phase-TAU*floor(phase/TAU+0.5));
    return product(value,dvec2(double(cos(angle)),double(sin(angle))));
}
void main() {
    int port=int(gl_GlobalInvocationID.x);
    if(port>=port_count) return;
    dvec2 sum_field=dvec2(0.0);
    for(int path=0;path<path_count;++path) {
        dvec4 a=raw4(paths_hi,paths_lo,path*2);
        dvec4 b=raw4(paths_hi,paths_lo,path*2+1);
        if(int(a.x)!=port) continue;
        dvec2 value=dvec2(a.w,b.x);
        for(int j=0;j<int(a.z);++j) {
            dvec4 hit=raw4(hits_hi,hits_lo,int(a.y)+j);
            value=rotate_field(value,TAU*hit.x/(double(wavelength_hi)+double(wavelength_lo)));
            if(int(hit.z)==1) value*=0.7071067811865475244lf;
            if(int(hit.z)==2) value=product(value,dvec2(0.0,0.7071067811865475244lf));
            if(int(hit.z)==3) value=-rotate_field(value,hit.y);
            if(int(hit.z)==4) value*=sqrt(hit.w);
            if(int(hit.z)==5) value=product(value,dvec2(0.0,sqrt(1.0lf-hit.w)));
        }
        value=rotate_field(value,TAU*b.y/(double(wavelength_hi)+double(wavelength_lo)));
        sum_field+=value;
    }
    imageStore(fields_out,ivec2(port,0),vec4(float(sum_field.x),float(sum_field.y),float(dot(sum_field,sum_field)),0.0));
}
