// Opt-in header; requires caller GLSL >= 4.00. Not compiled or executed.
// Failure outputs MUST NOT be consumed. Caller propagates false fail-closed.
// No main(), binding, dispatch, admission, YZ/tree or inference in this header.
#ifndef EXP005_SIGNED512_V1
#define EXP005_SIGNED512_V1
struct Exp005I512 { uint w[16]; };
Exp005I512 exp005_zero512() {
    Exp005I512 r; for (int i=0;i<16;++i) r.w[i]=0u; return r;
}
bool exp005_neg512(Exp005I512 a) { return (a.w[15]&0x80000000u)!=0u; }
Exp005I512 exp005_negmod512(Exp005I512 a) {
    Exp005I512 r; uint carry=1u;
    for(int i=0;i<16;++i) { uint v=~a.w[i]; r.w[i]=v+carry; carry=uint(r.w[i]<v); }
    return r;
}
int exp005_cmp512(Exp005I512 a, Exp005I512 b) {
    bool na=exp005_neg512(a), nb=exp005_neg512(b);
    if(na!=nb) return na ? -1 : 1;
    for(int i=15;i>=0;--i) if(a.w[i]!=b.w[i]) return a.w[i]<b.w[i] ? -1 : 1;
    return 0;
}
bool exp005_add512(Exp005I512 a, Exp005I512 b, out Exp005I512 r) {
    uint carry=0u;
    for(int i=0;i<16;++i) {
        uint low=a.w[i]+b.w[i], c1=uint(low<a.w[i]);
        r.w[i]=low+carry; uint c2=uint(r.w[i]<low); carry=c1|c2;
    }
    return exp005_neg512(a)!=exp005_neg512(b) || exp005_neg512(r)==exp005_neg512(a);
}
bool exp005_sub512(Exp005I512 a, Exp005I512 b, out Exp005I512 r) {
    uint borrow=0u;
    for(int i=0;i<16;++i) {
        uint low=a.w[i]-b.w[i], b1=uint(a.w[i]<b.w[i]);
        r.w[i]=low-borrow; uint b2=uint(low<borrow); borrow=b1|b2;
    }
    return exp005_neg512(a)==exp005_neg512(b) || exp005_neg512(r)==exp005_neg512(a);
}
bool exp005_acc1024(inout uint full[32], int start, uint value) {
    uint carry=value;
    for(int k=start;k<32;++k) {
        if(carry==0u) break;
        uint old=full[k]; full[k]=old+carry; carry=uint(full[k]<old);
    }
    return carry==0u;
}
bool exp005_mul512(Exp005I512 a, Exp005I512 b, out Exp005I512 r) {
    bool na=exp005_neg512(a), nb=exp005_neg512(b), neg=na!=nb;
    Exp005I512 ua=a, ub=b;
    if(na) ua=exp005_negmod512(a); if(nb) ub=exp005_negmod512(b);
    uint full[32]; for(int i=0;i<32;++i) full[i]=0u;
    for(int i=0;i<16;++i) for(int j=0;j<16;++j) {
        uint hi,lo; umulExtended(ua.w[i],ub.w[j],hi,lo);
        if(!exp005_acc1024(full,i+j,lo)) return false;
        if(!exp005_acc1024(full,i+j+1,hi)) return false;
    }
    for(int i=16;i<32;++i) if(full[i]!=0u) return false;
    bool lower=false; for(int i=0;i<15;++i) if(full[i]!=0u) lower=true;
    if(full[15]>=0x80000000u && !(neg && full[15]==0x80000000u && !lower)) return false;
    for(int i=0;i<16;++i) r.w[i]=full[i];
    if(neg) r=exp005_negmod512(r);
    return true;
}
bool exp005_decode32_scaled512(uint word, out Exp005I512 r) {
    uint exponent=(word>>23u)&255u, mantissa=word&0x7fffffu;
    r=exp005_zero512();
    if(exponent==255u || (exponent==0u && mantissa!=0u)) return false;
    if(exponent==0u) return true;
    uint sig=mantissa|0x800000u, shift=exponent-1u;
    int slot=int(shift/32u); uint offset=shift%32u;
    r.w[slot]=sig<<offset;
    if(offset!=0u) r.w[slot+1]=sig>>(32u-offset);
    if((word&0x80000000u)!=0u) r=exp005_negmod512(r);
    return true;
}
bool exp005_decode_hilo512(uvec2 pair, out Exp005I512 r) {
    Exp005I512 hi,lo;
    if(!exp005_decode32_scaled512(pair.x,hi)) return false;
    if(!exp005_decode32_scaled512(pair.y,lo)) return false;
    return exp005_add512(hi,lo,r);
}
#endif
