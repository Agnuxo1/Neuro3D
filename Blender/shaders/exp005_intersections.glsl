// Exhaustive nearest triangle on GPU ALUs. No BVH, RT API or CPU hit input.
dvec4 raw4(sampler2D hi,sampler2D lo,int i) {
    ivec2 p=ivec2(i%64,i/64);
    return dvec4(texelFetch(hi,p,0))+dvec4(texelFetch(lo,p,0));
}
void main() {
    int id=int(gl_GlobalInvocationID.x);
    if(id>=query_count) return;
    dvec4 o=raw4(rays_hi,rays_lo,id*2);
    dvec3 d=normalize(raw4(rays_hi,rays_lo,id*2+1).xyz);
    dvec3 origin=o.xyz+d*o.w;
    double best=1.0e30lf;
    int object=-1,primitive=-1;
    bool ambiguous=false;
    dvec3 normal=dvec3(0.0);
    for(int tri=0;tri<triangle_count;++tri) {
        dvec4 a=raw4(geometry_hi,geometry_lo,tri*3);
        dvec3 b=raw4(geometry_hi,geometry_lo,tri*3+1).xyz;
        dvec3 c=raw4(geometry_hi,geometry_lo,tri*3+2).xyz;
        dvec3 e1=b-a.xyz,e2=c-a.xyz,h=cross(d,e2);
        double det=dot(e1,h);
        if(abs(det)<=1.0e-14lf) continue;
        dvec3 rel=origin-a.xyz,q=cross(rel,e1);
        double u=dot(rel,h)/det,v=dot(d,q)/det;
        if(u<-1.0e-10lf || v<-1.0e-10lf || u+v>1.0lf+1.0e-10lf) continue;
        double t=dot(e2,q)/det;
        if(t<=1.0e-9lf) continue;
        if(t<best-1.0e-9lf) {
            best=t;object=int(a.w);primitive=tri;normal=normalize(cross(e1,e2));ambiguous=false;
        } else if(abs(t-best)<=1.0e-9lf && int(a.w)!=object) ambiguous=true;
    }
    if(object<0) {
        imageStore(hits_out,ivec2(id,0),vec4(-1.0,-1.0,-1.0,0.0));
        imageStore(normals_out,ivec2(id,0),vec4(0.0));
    } else {
        imageStore(hits_out,ivec2(id,0),vec4(float(best+o.w),float(object),float(primitive),ambiguous?2.0:1.0));
        imageStore(normals_out,ivec2(id,0),vec4(vec3(normal),0.0));
    }
}
