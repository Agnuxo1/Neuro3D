// Exact base-2^32 arithmetic in 4480 bytes of shared memory, one invocation.
// Scalar register IDs avoid large aggregate parameters/returns in the driver.
shared uint reg512[64][16];
shared uint wide1024[3][32];
uint arithmetic_failure=0u;
void clear512(int r) { for(int i=0;i<16;++i) reg512[r][i]=0u; }
void copy512(int a,int r) { for(int i=0;i<16;++i) reg512[r][i]=reg512[a][i]; }
bool neg512(int a) { return (reg512[a][15]&0x80000000u)!=0u; }
bool zero512(int a) { uint v=0u;for(int i=0;i<16;++i)v|=reg512[a][i];return v==0u; }
void negate512(int a,int r) {
    uint carry=1u;
    for(int i=0;i<16;++i) {
        uint v=~reg512[a][i],result=v+carry;
        reg512[r][i]=result;carry=uint(result<v);
    }
}
int compare512(int a,int b) {
    bool na=neg512(a),nb=neg512(b);
    if(na!=nb)return na?-1:1;
    for(int i=15;i>=0;--i) {
        if(reg512[a][i]<reg512[b][i])return -1;
        if(reg512[a][i]>reg512[b][i])return 1;
    }
    return 0;
}
bool add512(int a,int b,int r) {
    bool na=neg512(a),nb=neg512(b);uint carry=0u;
    for(int i=0;i<16;++i) {
        uint av=reg512[a][i],bv=reg512[b][i],low=av+bv;
        uint c1=uint(low<av),result=low+carry,c2=uint(result<low);
        reg512[r][i]=result;carry=c1|c2;
    }
    return na!=nb||neg512(r)==na;
}
bool sub512(int a,int b,int r) {
    bool na=neg512(a),nb=neg512(b);uint borrow=0u;
    for(int i=0;i<16;++i) {
        uint av=reg512[a][i],bv=reg512[b][i],low=av-bv;
        uint b1=uint(av<bv),result=low-borrow,b2=uint(low<borrow);
        reg512[r][i]=result;borrow=b1|b2;
    }
    return na==nb||neg512(r)==na;
}
bool accumulate1024(int slot,int start,uint value) {
    uint carry=value;
    for(int i=start;i<32;++i) {
        if(carry==0u)break;
        uint old=wide1024[slot][i],result=old+carry;
        wide1024[slot][i]=result;carry=uint(result<old);
    }
    return carry==0u;
}
bool multiply_unsigned1024(int a,int b,int slot) {
    for(int i=0;i<32;++i)wide1024[slot][i]=0u;
    for(int i=0;i<16;++i)for(int j=0;j<16;++j) {
        uint av=reg512[a][i],bv=reg512[b][j];
        if(av==0u||bv==0u)continue;
        uint hi,lo;umulExtended(av,bv,hi,lo);
        if(!accumulate1024(slot,i+j,lo))return false;
        if(!accumulate1024(slot,i+j+1,hi))return false;
    }
    return true;
}
bool multiply512(int a,int b,int r) {
    bool na=neg512(a),nb=neg512(b),negative=na!=nb;
    if(na)negate512(a,60);else copy512(a,60);
    if(nb)negate512(b,61);else copy512(b,61);
    if(!multiply_unsigned1024(60,61,0))return false;
    for(int i=16;i<32;++i)if(wide1024[0][i]!=0u){arithmetic_failure=100u+uint(i);return false;}
    bool lower=false;for(int i=0;i<15;++i)lower=lower||wide1024[0][i]!=0u;
    uint high=wide1024[0][15];
    if(high>=0x80000000u&&!(negative&&high==0x80000000u&&!lower)){
        arithmetic_failure=200u;return false;
    }
    for(int i=0;i<16;++i)reg512[r][i]=wide1024[0][i];
    if(negative)negate512(r,r);
    return true;
}
int compare1024(int a,int b) {
    for(int i=31;i>=0;--i) {
        if(wide1024[a][i]<wide1024[b][i])return -1;
        if(wide1024[a][i]>wide1024[b][i])return 1;
    }
    return 0;
}
int compare_fraction(int an,int ad,int bn,int bd,out bool ok) {
    ok=multiply_unsigned1024(an,bd,1)&&multiply_unsigned1024(bn,ad,2);
    return ok?compare1024(1,2):0;
}
bool signed_product(int a,int b,int slot,out bool negative) {
    negative=neg512(a)!=neg512(b);
    if(neg512(a))negate512(a,60);else copy512(a,60);
    if(neg512(b))negate512(b,61);else copy512(b,61);
    return multiply_unsigned1024(60,61,slot);
}
bool product_equal(int a,int b,int c,int d,out bool ok) {
    bool left_negative,right_negative;
    ok=signed_product(a,b,1,left_negative)&&signed_product(c,d,2,right_negative);
    if(!ok)return false;
    bool left_zero=true,right_zero=true;
    for(int i=0;i<32;++i){left_zero=left_zero&&wide1024[1][i]==0u;right_zero=right_zero&&wide1024[2][i]==0u;}
    return (left_zero&&right_zero)||(left_negative==right_negative&&compare1024(1,2)==0);
}
bool parallel3(int a,int b,out bool ok) {
    bool x=product_equal(a,b+1,a+1,b,ok);if(!ok)return false;
    bool y=product_equal(a,b+2,a+2,b,ok);if(!ok)return false;
    bool z=product_equal(a+1,b+2,a+2,b+1,ok);return ok&&x&&y&&z;
}
bool sub3(int a,int b,int r) {
    for(int i=0;i<3;++i)if(!sub512(a+i,b+i,r+i))return false;return true;
}
bool cross3(int a,int b,int r) {
    for(int i=0;i<3;++i) {
        int j=(i+1)%3,k=(i+2)%3;
        if(!multiply512(a+j,b+k,50))return false;
        if(!multiply512(a+k,b+j,51))return false;
        if(!sub512(50,51,r+i))return false;
    }
    return true;
}
bool dot3(int a,int b,int r) {
    for(int i=0;i<3;++i)if(!multiply512(a+i,b+i,50+i))return false;
    if(!add512(50,51,53))return false;return add512(53,52,r);
}
bool zero3(int a) { return zero512(a)&&zero512(a+1)&&zero512(a+2); }
bool decode32(uint word,int r) {
    clear512(r);uint exponent=(word>>23u)&255u,mantissa=word&0x7fffffu;
    if(exponent==255u||(exponent==0u&&mantissa!=0u))return false;
    if(exponent==0u)return true;
    uint sig=mantissa|0x800000u,shift=exponent-1u;
    int slot=int(shift/32u);uint offset=shift%32u;
    reg512[r][slot]=sig<<offset;
    if(offset!=0u)reg512[r][slot+1]=sig>>(32u-offset);
    if((word&0x80000000u)!=0u)negate512(r,r);
    return true;
}
bool decode_hilo(uvec2 pair,int r) {
    if(!decode32(pair.x,56))return false;
    if(!decode32(pair.y,57))return false;
    return add512(56,57,r);
}
