// Exact observed-scene first-hit selector over the point-4 hi/lo ABI.
// The signed512 header is prepended by the host. No float/double geometry math.
const uint RFH_MAGIC = 0x35484652u; // RFH5
const uint RFH_VERSION = 1u;
const uint STATUS_SELECT = 1u;
const uint STATUS_MISS = 2u;
const uint STATUS_TRUE_TIE = 3u;
const uint STATUS_BOUNDARY = 4u;
const uint STATUS_CONTACT = 5u;
const uint STATUS_COPLANAR = 6u;
const uint STATUS_INVALID_GEOMETRY = 7u;
const uint STATUS_NUMERIC_OVERFLOW = 8u;

const int C_OUT = 0;
const int C_INTERIOR = 1;
const int C_BOUNDARY = 2;
const int C_CONTACT = 3;
const int C_COPLANAR = 4;
const int C_DEGENERATE = 5;
const int C_NUMERIC = 6;

struct Exp005V3I {
    Exp005I512 x;
    Exp005I512 y;
    Exp005I512 z;
};
Exp005V3I zero_vector512() {
    return Exp005V3I(exp005_zero512(), exp005_zero512(), exp005_zero512());
}

uint input_word(uint index) {
    uvec4 lane = input_packet.words[index >> 2u];
    return lane[int(index & 3u)];
}
ivec2 texel(uint index) { return ivec2(int(index & 63u), int(index >> 6u)); }
void put(uint index, uint value) {
    imageStore(result_words, texel(index), uvec4(value, 0u, 0u, 0u));
}
void put512(uint offset, Exp005I512 value) {
    for (uint i = 0u; i < 16u; ++i) put(offset + i, exp005_word512(value,int(i)));
}
bool zero512(Exp005I512 value) {
    uint anyv = 0u;
    for (int i = 0; i < 16; ++i) anyv |= exp005_word512(value,i);
    return anyv == 0u;
}
bool zero3(Exp005V3I value) {
    return zero512(value.x) && zero512(value.y) && zero512(value.z);
}
Exp005I512 negate512(Exp005I512 value) { return exp005_negmod512(value); }

bool add512(Exp005I512 a, Exp005I512 b, out Exp005I512 r) {
    return exp005_add512(a, b, r);
}
bool sub512(Exp005I512 a, Exp005I512 b, out Exp005I512 r) {
    return exp005_sub512(a, b, r);
}
bool mul512(Exp005I512 a, Exp005I512 b, out Exp005I512 r) {
    return exp005_mul512(a, b, r);
}

bool sub3(Exp005V3I a, Exp005V3I b, out Exp005V3I r) {
    return sub512(a.x,b.x,r.x) && sub512(a.y,b.y,r.y) && sub512(a.z,b.z,r.z);
}
bool cross3i(Exp005V3I a, Exp005V3I b, out Exp005V3I r) {
    Exp005I512 p, q;
    if (!mul512(a.y,b.z,p) || !mul512(a.z,b.y,q) || !sub512(p,q,r.x)) return false;
    if (!mul512(a.z,b.x,p) || !mul512(a.x,b.z,q) || !sub512(p,q,r.y)) return false;
    if (!mul512(a.x,b.y,p) || !mul512(a.y,b.x,q) || !sub512(p,q,r.z)) return false;
    return true;
}
bool dot3i(Exp005V3I a, Exp005V3I b, out Exp005I512 r) {
    Exp005I512 x,y,z,s;
    if (!mul512(a.x,b.x,x) || !mul512(a.y,b.y,y) || !mul512(a.z,b.z,z)) return false;
    if (!add512(x,y,s) || !add512(s,z,r)) return false;
    return true;
}

bool positive512(Exp005I512 value) { return !zero512(value) && !exp005_neg512(value); }
bool nonnegative512(Exp005I512 value) { return !exp005_neg512(value); }

bool full_mul_positive(Exp005I512 a, Exp005I512 b, out Exp005U1024 full) {
    if (exp005_neg512(a) || exp005_neg512(b)) return false;
    full=exp005_zero1024();
    for (int i=0;i<16;++i) for (int j=0;j<16;++j) {
        uint hi,lo; umulExtended(exp005_word512(a,i),exp005_word512(b,j),hi,lo);
        if (!exp005_acc1024(full,i+j,lo)) return false;
        if (!exp005_acc1024(full,i+j+1,hi)) return false;
    }
    return true;
}
int compare1024(Exp005U1024 a, Exp005U1024 b) {
    for (int i=31;i>=0;--i) {
        if (exp005_word1024(a,i) < exp005_word1024(b,i)) return -1;
        if (exp005_word1024(a,i) > exp005_word1024(b,i)) return 1;
    }
    return 0;
}
int compare_fraction(Exp005I512 an, Exp005I512 ad, Exp005I512 bn, Exp005I512 bd,
                     out bool ok) {
    Exp005U1024 left, right;
    ok = full_mul_positive(an,bd,left) && full_mul_positive(bn,ad,right);
    return ok ? compare1024(left,right) : 0;
}

bool signed_product_equal(Exp005I512 a, Exp005I512 b, Exp005I512 c, Exp005I512 d,
                          out bool ok) {
    bool sa=exp005_neg512(a), sb=exp005_neg512(b), sc=exp005_neg512(c), sd=exp005_neg512(d);
    Exp005I512 aa=sa?negate512(a):a, bb=sb?negate512(b):b;
    Exp005I512 cc=sc?negate512(c):c, dd=sd?negate512(d):d;
    Exp005U1024 left,right;
    ok=full_mul_positive(aa,bb,left)&&full_mul_positive(cc,dd,right);
    if(!ok) return false;
    bool zl=true,zr=true; for(int i=0;i<32;++i){zl=zl&&(exp005_word1024(left,i)==0u);zr=zr&&(exp005_word1024(right,i)==0u);}
    if(zl&&zr) return true;
    return (sa!=sb)==(sc!=sd) && compare1024(left,right)==0;
}
bool parallel3i(Exp005V3I a, Exp005V3I b, out bool ok) {
    bool q=true;
    bool e1=signed_product_equal(a.x,b.y,a.y,b.x,q); if(!q){ok=false;return false;}
    bool e2=signed_product_equal(a.x,b.z,a.z,b.x,q); if(!q){ok=false;return false;}
    bool e3=signed_product_equal(a.y,b.z,a.z,b.y,q); if(!q){ok=false;return false;}
    ok=true;return e1&&e2&&e3;
}

bool load_scalar(uint scalar_index, out Exp005I512 value) {
    uint scalar_count=input_word(4u), scalar_offset=input_word(5u), stride=input_word(6u);
    if (scalar_index>=scalar_count || stride!=8u) return false;
    uint base=scalar_offset+scalar_index*stride;
    return exp005_decode_hilo512(uvec2(input_word(base),input_word(base+1u)),value);
}
bool load_source(uint sid, out Exp005V3I origin, out Exp005V3I direction) {
    origin=zero_vector512(); direction=zero_vector512();
    uint count=input_word(7u), offset=input_word(8u), stride=input_word(9u);
    if (sid>=count || stride!=32u) return false;
    uint base=offset+sid*stride;
    if (input_word(base)!=sid || input_word(base+1u)!=0xffffffffu) return false;
    return load_scalar(input_word(base+2u),origin.x) &&
           load_scalar(input_word(base+3u),origin.y) &&
           load_scalar(input_word(base+4u),origin.z) &&
           load_scalar(input_word(base+5u),direction.x) &&
           load_scalar(input_word(base+6u),direction.y) &&
           load_scalar(input_word(base+7u),direction.z);
}
bool load_vertex(uint vid, out Exp005V3I value) {
    value=zero_vector512();
    uint count=input_word(10u), offset=input_word(11u), stride=input_word(12u);
    if (vid>=count || stride!=8u) return false;
    uint base=offset+vid*stride;
    if (input_word(base)!=vid) return false;
    return load_scalar(input_word(base+3u),value.x) &&
           load_scalar(input_word(base+4u),value.y) &&
           load_scalar(input_word(base+5u),value.z);
}
bool triangle_info(uint tri, out uint object_id, out uvec3 verts) {
    uint count=input_word(13u), offset=input_word(14u), stride=input_word(15u);
    if (tri>=count || stride!=8u) return false;
    uint base=offset+tri*stride;
    if (input_word(base)!=tri) return false;
    object_id=input_word(base+1u);
    verts=uvec3(input_word(base+3u),input_word(base+4u),input_word(base+5u));
    return true;
}

int exact_candidate(uint tri, Exp005V3I origin, Exp005V3I direction,
                    out Exp005I512 numerator, out Exp005I512 denominator,
                    out uint object_id, out Exp005V3I normal) {
    uvec3 ids; Exp005V3I a,b,c,e1,e2,p,rel,q;
    numerator=exp005_zero512(); denominator=exp005_zero512(); object_id=0xffffffffu;
    normal=zero_vector512();
    if (!triangle_info(tri,object_id,ids) || !load_vertex(ids.x,a) ||
        !load_vertex(ids.y,b) || !load_vertex(ids.z,c)) return C_NUMERIC;
    if (!sub3(b,a,e1) || !sub3(c,a,e2) || !cross3i(e1,e2,normal)) return C_NUMERIC;
    if (zero3(normal)) return C_DEGENERATE;
    if (!cross3i(direction,e2,p) || !dot3i(e1,p,denominator) || !sub3(origin,a,rel)) return C_NUMERIC;
    if (zero512(denominator)) {
        Exp005I512 plane;
        if (!dot3i(rel,normal,plane)) return C_NUMERIC;
        return zero512(plane) ? C_COPLANAR : C_OUT;
    }
    Exp005I512 u,v,uv;
    if (!cross3i(rel,e1,q) || !dot3i(rel,p,u) || !dot3i(direction,q,v) ||
        !dot3i(e2,q,numerator)) return C_NUMERIC;
    if (exp005_neg512(denominator)) {
        denominator=negate512(denominator); u=negate512(u); v=negate512(v); numerator=negate512(numerator);
    }
    if (!add512(u,v,uv)) return C_NUMERIC;
    if (!nonnegative512(numerator) || !nonnegative512(u) || !nonnegative512(v) ||
        exp005_cmp512(uv,denominator)>0) return C_OUT;
    if (zero512(numerator)) return C_CONTACT;
    if (zero512(u) || zero512(v) || exp005_cmp512(uv,denominator)==0) return C_BOUNDARY;
    return C_INTERIOR;
}

void add_mask(uint tri, inout uint lo, inout uint hi) {
    if (tri < 32u) lo |= (1u << tri);
    else if (tri < 64u) hi |= (1u << (tri-32u));
}

void main() {
    if (any(notEqual(gl_GlobalInvocationID,uvec3(0u)))) return;
    for (uint i=0u;i<uint(input_word_count);++i)
        imageStore(echo_words,texel(i),uvec4(input_word(i),0u,0u,0u));
    for (uint i=0u;i<64u;++i) put(i,0u);

    uint final_status=STATUS_NUMERIC_OVERFLOW;
    uint selected=0xffffffffu, selected_object=0xffffffffu, tie_count=0u;
    uint tie_lo=0u,tie_hi=0u,contact_count=0u,coplanar_count=0u,degenerate_count=0u;
    uint excluded_previous=0u; bool best_boundary=false,have_best=false,numeric_error=false;
    Exp005I512 best_num=exp005_zero512(),best_den=exp005_zero512();
    Exp005V3I best_normal=zero_vector512(); bool ambiguous_tie=false,equivalent_surface_tie=false;

    bool header_ok=input_word_count>=32 && input_word(0u)==0x4e33484cu && input_word(1u)==1u &&
                   input_word(2u)==32u && input_word(3u)==uint(input_word_count) &&
                   input_word(13u)>0u && input_word(13u)<=64u &&
                   source_index>=0 && uint(source_index)<input_word(7u);
    Exp005V3I origin,direction;
    if (!header_ok || !load_source(uint(source_index),origin,direction) || zero3(direction)) {
        numeric_error=true;
    } else {
        uint triangle_count=input_word(13u);
        for (uint tri=0u;tri<triangle_count;++tri) {
            Exp005I512 n,d; uint object_id; Exp005V3I candidate_normal;
            int klass=exact_candidate(tri,origin,direction,n,d,object_id,candidate_normal);
            if (klass==C_NUMERIC) { numeric_error=true; break; }
            if (klass==C_DEGENERATE) { degenerate_count++; continue; }
            if (klass==C_COPLANAR) { coplanar_count++; continue; }
            if (klass==C_CONTACT) {
                if (previous_primitive>=0 && uint(previous_primitive)==tri &&
                    departure_event>=1 && departure_event<=3) excluded_previous++;
                else contact_count++;
                continue;
            }
            if (klass!=C_INTERIOR && klass!=C_BOUNDARY) continue;
            if (!have_best) {
                have_best=true;best_num=n;best_den=d;selected=tri;selected_object=object_id;
                best_normal=candidate_normal; ambiguous_tie=false; equivalent_surface_tie=false;
                best_boundary=(klass==C_BOUNDARY);tie_count=1u;tie_lo=0u;tie_hi=0u;add_mask(tri,tie_lo,tie_hi);
            } else {
                bool ok=false; int relation=compare_fraction(n,d,best_num,best_den,ok);
                if (!ok) { numeric_error=true; break; }
                if (relation<0) {
                    best_num=n;best_den=d;selected=tri;selected_object=object_id;
                    best_normal=candidate_normal; ambiguous_tie=false; equivalent_surface_tie=false;
                    best_boundary=(klass==C_BOUNDARY);tie_count=1u;tie_lo=0u;tie_hi=0u;add_mask(tri,tie_lo,tie_hi);
                } else if (relation==0) {
                    tie_count++;add_mask(tri,tie_lo,tie_hi);
                    bool parallel_ok=true;
                    bool same_surface=false;
                    if (object_id==selected_object)
                        same_surface=parallel3i(candidate_normal,best_normal,parallel_ok);
                    if(!parallel_ok){numeric_error=true;break;}
                    if(!same_surface) ambiguous_tie=true;
                    equivalent_surface_tie=!ambiguous_tie;
                }
            }
        }
    }

    if (numeric_error) final_status=STATUS_NUMERIC_OVERFLOW;
    else if (degenerate_count>0u) final_status=STATUS_INVALID_GEOMETRY;
    else if (coplanar_count>0u) final_status=STATUS_COPLANAR;
    else if (contact_count>0u) final_status=STATUS_CONTACT;
    else if (!have_best) final_status=STATUS_MISS;
    else if (ambiguous_tie) final_status=STATUS_TRUE_TIE;
    else if (best_boundary && !equivalent_surface_tie) final_status=STATUS_BOUNDARY;
    else final_status=STATUS_SELECT;

    put(0u,RFH_MAGIC); put(1u,RFH_VERSION); put(2u,final_status); put(3u,uint(source_index));
    put(4u,selected); put(5u,selected_object); put(6u,tie_count); put(7u,uint(best_boundary));
    put(8u,excluded_previous); put(9u,contact_count); put(10u,coplanar_count); put(11u,degenerate_count);
    put(12u,input_word(13u)); put(13u,uint(dispatch_nonce)); put(14u,~uint(dispatch_nonce)); put(15u,1u);
    put512(16u,best_num); put512(32u,best_den);
    put(48u,tie_lo); put(49u,tie_hi); put(50u,uint(equivalent_surface_tie)); put(51u,uint(ambiguous_tie));
}
