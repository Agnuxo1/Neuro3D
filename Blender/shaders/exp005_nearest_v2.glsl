// Versioned two-pass global-minimum/tie selection. GPU ALUs, not hardware RT.
// Raw triangles only; unchanged BIAS and triangle tolerances from frozen V1.
bool candidate_hit(int tri,dvec3 biased,dvec3 d,out double t,out int obj,out dvec3 n) {
    dvec4 a=raw4(geometry_hi,geometry_lo,tri*3);
    dvec3 b=raw4(geometry_hi,geometry_lo,tri*3+1).xyz;
    dvec3 c=raw4(geometry_hi,geometry_lo,tri*3+2).xyz;
    dvec3 e1=b-a.xyz,e2=c-a.xyz,h=cross(d,e2);
    double det=dot(e1,h);
    if(abs(det)<=1.0e-14lf) return false;
    dvec3 rel=biased-a.xyz,q=cross(rel,e1);
    double u=dot(rel,h)/det,v=dot(d,q)/det;
    if(u<-1.0e-10lf || v<-1.0e-10lf || u+v>1.0lf+1.0e-10lf) return false;
    t=dot(e2,q)/det;
    if(t<=1.0e-9lf) return false;
    obj=int(a.w); n=normalize(cross(e1,e2));
    if(n.x<0.0lf || (n.x==0.0lf && n.y<0.0lf) ||
       (n.x==0.0lf && n.y==0.0lf && n.z<0.0lf)) n=-n;
    return true;
}
void nearest(dvec3 origin,dvec3 d,out double best,out int object,out dvec3 normal,out bool ambiguous) {
    best=1.0e30lf; object=-1; normal=dvec3(0.0); ambiguous=false;
    dvec3 biased=origin+d*BIAS;
    // Pass 1: exact minimum, NOT minimum minus a tolerance. No ambiguity reset.
    for(int tri=0;tri<triangle_count;++tri) {
        double t; int obj; dvec3 n;
        if(candidate_hit(tri,biased,d,t,obj,n)) {
            bool earlier_normal=n.x<normal.x || (n.x==normal.x && n.y<normal.y) ||
                                (n.x==normal.x && n.y==normal.y && n.z<normal.z);
            if(t<best || (t==best && earlier_normal)) {
                best=t;object=obj;normal=n;
            }
        }
    }
    // Pass 2: compare every candidate against the final global minimum.
    if(object>=0) {
        for(int tri=0;tri<triangle_count;++tri) {
            double t; int obj; dvec3 n;
            if(candidate_hit(tri,biased,d,t,obj,n) && abs(t-best)<=1.0e-9lf &&
               (obj!=object || abs(dot(n,normal))<1.0lf-1.0e-9lf)) ambiguous=true;
        }
    }
    best+=BIAS;
}
