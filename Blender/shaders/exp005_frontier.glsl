// Raw scene -> DFS -> complex fields in native GPU ALUs. NO RT/BVH/CPU paths.
const double TAU=6.2831853071795864769lf;
const double BIAS=1.0e-6lf;
struct Ray { dvec3 o; dvec3 d; dvec2 a; double length; int depth; };
dvec4 raw4(sampler2D hi,sampler2D lo,int i) {
    return dvec4(texelFetch(hi,ivec2(i%64,i/64),0))+dvec4(texelFetch(lo,ivec2(i%64,i/64),0));
}
dvec2 product(dvec2 a,dvec2 b) { return dvec2(a.x*b.x-a.y*b.y,a.x*b.y+a.y*b.x); }
dvec2 rotated(dvec2 a,double phase) {
    float angle=float(phase-TAU*floor(phase/TAU+0.5));
    return product(a,dvec2(double(cos(angle)),double(sin(angle))));
}
void nearest(dvec3 origin,dvec3 d,out double best,out int object,out dvec3 normal,out bool ambiguous) {
    best=1.0e30lf; object=-1; normal=dvec3(0.0); ambiguous=false;
    dvec3 biased=origin+d*BIAS;
    for(int tri=0;tri<triangle_count;++tri) {
        dvec4 a=raw4(geometry_hi,geometry_lo,tri*3);
        dvec3 b=raw4(geometry_hi,geometry_lo,tri*3+1).xyz;
        dvec3 c=raw4(geometry_hi,geometry_lo,tri*3+2).xyz;
        dvec3 e1=b-a.xyz,e2=c-a.xyz,h=cross(d,e2);
        double det=dot(e1,h);
        if(abs(det)<=1.0e-14lf) continue;
        dvec3 rel=biased-a.xyz,q=cross(rel,e1);
        double u=dot(rel,h)/det,v=dot(d,q)/det;
        if(u<-1.0e-10lf || v<-1.0e-10lf || u+v>1.0lf+1.0e-10lf) continue;
        double t=dot(e2,q)/det;
        if(t<=1.0e-9lf) continue;
        dvec3 n=normalize(cross(e1,e2));
        if(t<best-1.0e-9lf) { best=t;object=int(a.w);normal=n;ambiguous=false; }
        else if(abs(t-best)<=1.0e-9lf && (int(a.w)!=object || abs(dot(n,normal))<1.0lf-1.0e-9lf)) ambiguous=true;
    }
    best+=BIAS; // Original ray origin distance, not shortened biased length.
}
void main() {
    int port=int(gl_GlobalInvocationID.x);
    if(port>=port_count) return;
    dvec2 sum_field=dvec2(0.0);
    int status=0,casts=0,paths=0,deepest=0;
    Ray stack[33];
    for(int source=0;source<source_count && status==0;++source) {
        dvec4 a=raw4(sources_hi,sources_lo,source*2),b=raw4(sources_hi,sources_lo,source*2+1);
        if(a.w==0.0lf && b.w==0.0lf) continue;
        stack[0]=Ray(a.xyz,normalize(b.xyz),dvec2(a.w,b.w),0.0lf,0);
        int top=1,source_casts=0;
        while(top>0 && status==0) {
            Ray ray=stack[--top];
            if(++source_casts>max_steps) { status=5;break; }
            if(ray.depth>=max_depth) { status=6;break; }
            ++casts; deepest=max(deepest,ray.depth+1);
            double distance; int object; dvec3 normal; bool ambiguous;
            nearest(ray.o,ray.d,distance,object,normal,ambiguous);
            if(object<0) { status=1;break; }
            if(ambiguous) { status=2;break; }
            dvec4 props=raw4(optics_hi,optics_lo,object*3);
            dvec3 point=ray.o+ray.d*distance;
            double length=ray.length+distance;
            int kind=int(props.x);
            if(kind==2 || kind==3) {
                dvec3 reference=raw4(optics_hi,optics_lo,object*3+1).xyz;
                dvec3 axis=normalize(raw4(optics_hi,optics_lo,object*3+2).xyz);
                if(dot(ray.d,axis)<1.0lf-1.0e-6lf) { status=3;break; }
                if(int(props.w)==port) {
                    if(paths>=128) { status=8;break; }
                    double effective=length+dot(ray.d,reference-point);
                    dvec2 field=rotated(ray.a,TAU*effective/(double(wavelength_hi)+double(wavelength_lo)));
                    imageStore(ledger_out,ivec2(paths,port),vec4(float(field.x),float(field.y),float(effective),float(source)));
                    sum_field+=field; ++paths;
                }
                continue;
            }
            dvec3 reflected=normalize(ray.d-2.0lf*dot(ray.d,normal)*normal);
            if(kind==1) {
                if(top>=33) { status=4;break; }
                stack[top++]=Ray(point,reflected,-rotated(ray.a,props.z),length,ray.depth+1);
            } else if(kind==0) {
                if(top+2>33) { status=4;break; }
                stack[top++]=Ray(point,ray.d,ray.a*sqrt(props.y),length,ray.depth+1);
                stack[top++]=Ray(point,reflected,product(ray.a,dvec2(0.0lf,sqrt(1.0lf-props.y))),length,ray.depth+1);
            } else { status=7;break; }
        }
    }
    // Invalid partial sums are not inference: clear and retain error status.
    if(status!=0) sum_field=dvec2(0.0);
    imageStore(fields_out,ivec2(port,0),vec4(float(sum_field.x),float(sum_field.y),float(dot(sum_field,sum_field)),float(status)));
    imageStore(stats_out,ivec2(port,0),vec4(float(casts),float(paths),float(deepest),float(status)));
}
