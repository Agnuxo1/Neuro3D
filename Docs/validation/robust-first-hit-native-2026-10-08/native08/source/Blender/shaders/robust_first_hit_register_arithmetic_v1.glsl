// Same base-2^32 signed512 arithmetic, stored in vectors instead of local arrays.
// Exactly one invocation per workgroup; no shared state or floating geometry.
#ifndef RFH_REGISTER_ARITHMETIC_V1
#define RFH_REGISTER_ARITHMETIC_V1
struct Exp005I512 { uvec4 q0; uvec4 q1; uvec4 q2; uvec4 q3; };
struct Exp005U1024 {
    uvec4 q0; uvec4 q1; uvec4 q2; uvec4 q3;
    uvec4 q4; uvec4 q5; uvec4 q6; uvec4 q7;
};
uint exp005_word512(Exp005I512 a, int i) {
    int lane=i&3;
    switch(i>>2) {
        case 0: return a.q0[lane]; case 1: return a.q1[lane];
        case 2: return a.q2[lane]; default: return a.q3[lane];
    }
}
void exp005_set512(inout Exp005I512 a,int i,uint value) {
    int lane=i&3;
    switch(i>>2) {
        case 0: a.q0[lane]=value; break; case 1: a.q1[lane]=value; break;
        case 2: a.q2[lane]=value; break; default: a.q3[lane]=value; break;
    }
}
uint exp005_word1024(Exp005U1024 a,int i) {
    int lane=i&3;
    switch(i>>2) {
        case 0: return a.q0[lane]; case 1: return a.q1[lane];
        case 2: return a.q2[lane]; case 3: return a.q3[lane];
        case 4: return a.q4[lane]; case 5: return a.q5[lane];
        case 6: return a.q6[lane]; default: return a.q7[lane];
    }
}
void exp005_set1024(inout Exp005U1024 a,int i,uint value) {
    int lane=i&3;
    switch(i>>2) {
        case 0: a.q0[lane]=value; break; case 1: a.q1[lane]=value; break;
        case 2: a.q2[lane]=value; break; case 3: a.q3[lane]=value; break;
        case 4: a.q4[lane]=value; break; case 5: a.q5[lane]=value; break;
        case 6: a.q6[lane]=value; break; default: a.q7[lane]=value; break;
    }
}
Exp005I512 exp005_zero512() {
    return Exp005I512(uvec4(0u),uvec4(0u),uvec4(0u),uvec4(0u));
}
Exp005U1024 exp005_zero1024() {
    return Exp005U1024(uvec4(0u),uvec4(0u),uvec4(0u),uvec4(0u),
                     uvec4(0u),uvec4(0u),uvec4(0u),uvec4(0u));
}
bool exp005_neg512(Exp005I512 a) { return (a.q3.w&0x80000000u)!=0u; }
Exp005I512 exp005_negmod512(Exp005I512 a) {
    Exp005I512 r=exp005_zero512(); uint carry=1u;
    for(int i=0;i<16;++i) {
        uint v=~exp005_word512(a,i), result=v+carry;
        exp005_set512(r,i,result); carry=uint(result<v);
    }
    return r;
}
int exp005_cmp512(Exp005I512 a,Exp005I512 b) {
    bool na=exp005_neg512(a),nb=exp005_neg512(b);
    if(na!=nb) return na?-1:1;
    for(int i=15;i>=0;--i) {
        uint av=exp005_word512(a,i),bv=exp005_word512(b,i);
        if(av!=bv) return av<bv?-1:1;
    }
    return 0;
}
bool exp005_add512(Exp005I512 a,Exp005I512 b,out Exp005I512 r) {
    r=exp005_zero512(); uint carry=0u;
    for(int i=0;i<16;++i) {
        uint av=exp005_word512(a,i),bv=exp005_word512(b,i),low=av+bv;
        uint c1=uint(low<av),result=low+carry,c2=uint(result<low);
        exp005_set512(r,i,result); carry=c1|c2;
    }
    return exp005_neg512(a)!=exp005_neg512(b)||exp005_neg512(r)==exp005_neg512(a);
}
bool exp005_sub512(Exp005I512 a,Exp005I512 b,out Exp005I512 r) {
    r=exp005_zero512(); uint borrow=0u;
    for(int i=0;i<16;++i) {
        uint av=exp005_word512(a,i),bv=exp005_word512(b,i),low=av-bv;
        uint b1=uint(av<bv),result=low-borrow,b2=uint(low<borrow);
        exp005_set512(r,i,result); borrow=b1|b2;
    }
    return exp005_neg512(a)==exp005_neg512(b)||exp005_neg512(r)==exp005_neg512(a);
}
bool exp005_acc1024(inout Exp005U1024 full,int start,uint value) {
    uint carry=value;
    for(int k=start;k<32;++k) {
        if(carry==0u) break;
        uint old=exp005_word1024(full,k),result=old+carry;
        exp005_set1024(full,k,result); carry=uint(result<old);
    }
    return carry==0u;
}
bool exp005_mul512(Exp005I512 a,Exp005I512 b,out Exp005I512 r) {
    r=exp005_zero512();
    bool na=exp005_neg512(a),nb=exp005_neg512(b),neg=na!=nb;
    Exp005I512 ua=na?exp005_negmod512(a):a,ub=nb?exp005_negmod512(b):b;
    Exp005U1024 full=exp005_zero1024();
    for(int i=0;i<16;++i) for(int j=0;j<16;++j) {
        uint hi,lo; umulExtended(exp005_word512(ua,i),exp005_word512(ub,j),hi,lo);
        if(!exp005_acc1024(full,i+j,lo)||!exp005_acc1024(full,i+j+1,hi)) return false;
    }
    for(int i=16;i<32;++i) if(exp005_word1024(full,i)!=0u) return false;
    bool lower=false;
    for(int i=0;i<15;++i) if(exp005_word1024(full,i)!=0u) lower=true;
    uint high=exp005_word1024(full,15);
    if(high>=0x80000000u&&!(neg&&high==0x80000000u&&!lower)) return false;
    for(int i=0;i<16;++i) exp005_set512(r,i,exp005_word1024(full,i));
    if(neg) r=exp005_negmod512(r);
    return true;
}
bool exp005_decode32_scaled512(uint word,out Exp005I512 r) {
    uint exponent=(word>>23u)&255u,mantissa=word&0x7fffffu;
    r=exp005_zero512();
    if(exponent==255u||(exponent==0u&&mantissa!=0u)) return false;
    if(exponent==0u) return true;
    uint sig=mantissa|0x800000u,shift=exponent-1u;
    int slot=int(shift/32u); uint offset=shift%32u;
    exp005_set512(r,slot,sig<<offset);
    if(offset!=0u) exp005_set512(r,slot+1,sig>>(32u-offset));
    if((word&0x80000000u)!=0u) r=exp005_negmod512(r);
    return true;
}
bool exp005_decode_hilo512(uvec2 pair,out Exp005I512 r) {
    r=exp005_zero512(); Exp005I512 hi,lo;
    if(!exp005_decode32_scaled512(pair.x,hi)||!exp005_decode32_scaled512(pair.y,lo)) return false;
    return exp005_add512(hi,lo,r);
}
#endif
